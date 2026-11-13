import Foundation
import Combine
import UIKit
import AudioToolbox

final class TrainingStore: ObservableObject {
    @Published private(set) var settings: TrainingSettings
    @Published private(set) var workout: TrainingSession?
    @Published private(set) var history: [TrainingSession] = []
    @Published private(set) var now = Date()
    @Published private(set) var storageError: String?
    private let device: DeviceStore
    private let defaults: UserDefaults
    private let archive: TrainingArchive
    private var subscriptions: Set<AnyCancellable> = []
    private var repetitionTracker = TrainingRepetitionTracker()
    private var timer: Timer?
    private var lastSavedAt = Date.distantPast
    private var cadenceBeat: Int?
    private var ownsRecording = false
    private static let settingsKey = "Fingerworker.trainingSettings.v1"

    init(device: DeviceStore, defaults: UserDefaults = .standard) {
        self.device = device; self.defaults = defaults
        archive = TrainingArchive(directory: FileManager.default.urls(for: .applicationSupportDirectory, in: .userDomainMask)[0]
            .appendingPathComponent("FingerworkerWorkouts", isDirectory: true))
        if let data = defaults.data(forKey: Self.settingsKey), let saved = try? JSONDecoder().decode(TrainingSettings.self, from: data) {
            settings = saved.normalized
        } else { settings = TrainingSettings() }
        do {
            history = try archive.load()
            if var unfinished = history.first(where: \.isOngoing) {
                // Restore the last checkpoint as paused, never advance a timer or
                // count movement that happened while the app was not running.
                unfinished.pause(at: unfinished.updatedAt, reason: "Das letzte Training wurde wiederhergestellt.")
                if unfinished.pauseReason == nil { unfinished.pauseReason = "Das letzte Training wurde wiederhergestellt." }
                workout = unfinished
            }
        } catch { storageError = "Trainings konnten nicht geladen werden: \(error.localizedDescription)" }
        device.endstopFeedbackSuppressed = workout?.settings.isCARC == true && isOngoing
        device.$latest.sink { [weak self] sample in self?.receive(sample) }.store(in: &subscriptions)
        let clock = Timer(timeInterval: 0.1, repeats: true) { [weak self] _ in self?.tick() }
        RunLoop.main.add(clock, forMode: .common)
        timer = clock
        if workout != nil { persist() }
    }
    deinit { timer?.invalidate() }

    var isOngoing: Bool { workout?.isOngoing == true }
    var canCountAutomatically: Bool {
        guard device.canRecord, let sample = device.latest else { return false }
        return sample.mode == 0 && sample.status & ~UInt16(1 << 5) == 0
    }
    var canStart: Bool { !isOngoing && !device.recording && (!settings.usesDeviceCounter || canCountAutomatically) }
    var canResume: Bool { workout?.phase == .paused && (workout?.settings.usesDeviceCounter == false || canCountAutomatically) }
    var startHint: String? {
        if device.recording && !isOngoing { return "Beende zuerst die laufende Messaufnahme." }
        if settings.usesDeviceCounter && !canCountAutomatically {
            if device.latest?.mode == 1 { return "Automatisches Zählen braucht den dynamischen Gerätemodus." }
            if let sample = device.latest, sample.status & ~UInt16(1 << 5) != 0 {
                return "Gerät meldet: \(sample.problem). Prüfe die Messansicht."
            }
            if device.canRecord { return "Warte auf aktuelle Messdaten vom Fingerworker." }
            return "Verbinde deinen Fingerworker oder wähle manuelles Zählen in den Einstellungen."
        }
        return nil
    }
    func updateSettings(_ settings: TrainingSettings) {
        self.settings = settings.normalized
        if let data = try? JSONEncoder().encode(self.settings) { defaults.set(data, forKey: Self.settingsKey) }
    }
    func start() {
        guard canStart else { return }
        let date = Date(); now = date
        workout = TrainingSession(settings: settings,
            source: device.demo ? "simulation" : settings.isCARC ? "timer" : settings.countingMode == .manual ? "manual" : "device", now: date)
        cadenceBeat = nil
        device.endstopFeedbackSuppressed = settings.isCARC
        rebaseCounter()
        startRecordingIfAvailable()
        feedback()
        UIApplication.shared.isIdleTimerDisabled = true
        persist()
    }
    func pause(reason: String? = nil) {
        guard workout?.isRunning == true else { return }
        now = Date(); workout?.pause(at: now, reason: reason)
        if workout?.phase.isFinished == true { finish(); return }
        UIApplication.shared.isIdleTimerDisabled = false
        feedback()
        persist()
    }
    func resume() {
        guard canResume else { return }
        now = Date(); workout?.resume(at: now); cadenceBeat = nil
        // A workout that ever continues with simulated data stays labelled as
        // simulation, even if it originally began on physical hardware.
        if device.demo { workout?.source = "simulation" }
        rebaseCounter(); startRecordingIfAvailable()
        UIApplication.shared.isIdleTimerDisabled = true
        feedback(); persist()
    }
    func cancel() {
        guard isOngoing else { return }
        now = Date(); workout?.cancel(at: now); finish()
    }
    func newWorkout() {
        guard !isOngoing else { return }
        workout = nil; cadenceBeat = nil
    }
    @discardableResult
    func updateLog(for id: UUID, notes: String, perceivedExertion: Int?) -> Bool {
        // Read the current snapshot when saving: editing a note must never
        // replace repetitions or events received while the editor was open.
        guard var saved = workout?.id == id ? workout : history.first(where: { $0.id == id }) else { return false }
        if saved.log == nil { saved.log = TrainingLog() }
        saved.log?.notes = notes
        saved.log?.perceivedExertion = perceivedExertion
        do {
            try archive.save(saved)
            if workout?.id == id { workout = saved }
            if let index = history.firstIndex(where: { $0.id == id }) { history[index] = saved }
            storageError = nil
            return true
        } catch {
            storageError = "Log konnte nicht gespeichert werden: \(error.localizedDescription)"
            return false
        }
    }
    func addManualRepetition() {
        guard workout?.settings.isCARC == false, workout?.settings.countingMode == .manual, workout?.phase == .working else { return }
        let oldPhase = workout?.phase, oldHand = workout?.activeHand
        now = Date(); workout?.addRepetitions(at: now)
        handleTransition(from: oldPhase, hand: oldHand)
        persist()
    }
    func undoManualRepetition() {
        guard workout?.settings.isCARC == false, workout?.settings.countingMode == .manual else { return }
        now = Date(); workout?.undoRepetition(at: now); persist()
    }
    func saveForBackground() {
        // iOS does not guarantee background timers. Freeze the guided workout and
        // require explicit resume; the separate BLE recording can still autosave.
        pause(reason: "Training pausiert, während die App im Hintergrund ist.")
        persist()
    }
    private func tick() {
        guard workout?.isRunning == true else { return }
        now = Date()
        let oldPhase = workout?.phase, oldHand = workout?.activeHand
        workout?.tick(at: now)
        handleTransition(from: oldPhase, hand: oldHand)
        if let workout, workout.phase == .working, workout.settings.usesCadence {
            let elapsed = max(0, now.timeIntervalSince(workout.phaseStartedAt))
            let cycle = workout.settings.pullSeconds + workout.settings.releaseSeconds
            let beat = Int(elapsed / cycle) * 2 + (workout.isPulling(at: now) ? 0 : 1)
            if beat != cadenceBeat { cadenceBeat = beat; feedback(cadence: true, releasing: !workout.isPulling(at: now)) }
        }
        if Date().timeIntervalSince(lastSavedAt) >= 1 { persist() }
    }
    private func receive(_ sample: Measurement?) {
        guard let sample else {
            repetitionTracker.clear()
            if workout?.settings.usesDeviceCounter == true { pause(reason: "Verbindung unterbrochen. Prüfe das Gerät und setze dann fort.") }
            return
        }
        let delta = repetitionTracker.receive(sample)
        guard workout?.isRunning == true else { return }
        if sample.valid, workout?.settings.isCARC != true || sample.mode == 0 {
            workout?.record(force: sample.force)
        }
        guard workout?.settings.usesDeviceCounter == true else { return }
        if repetitionTracker.rebooted {
            pause(reason: "Der Fingerworker wurde neu gestartet. Prüfe den Zähler und setze dann fort.")
            return
        }
        guard sample.mode == 0, sample.status & ~UInt16(1 << 5) == 0 else {
            pause(reason: "Das Gerät kann gerade keine Züge zählen. Prüfe die Messansicht.")
            return
        }
        let oldPhase = workout?.phase, oldHand = workout?.activeHand
        now = Date(); workout?.addRepetitions(delta, at: now)
        handleTransition(from: oldPhase, hand: oldHand)
    }
    private func rebaseCounter() {
        repetitionTracker.clear()
        if let sample = device.latest { _ = repetitionTracker.receive(sample) }
    }
    private func handleTransition(from phase: TrainingPhase?, hand: TrainingHand?) {
        guard phase != workout?.phase || hand != workout?.activeHand else { return }
        cadenceBeat = nil
        feedback()
        if workout?.phase.isFinished == true { finish() }
        else { persist() }
    }
    private func startRecordingIfAvailable() {
        guard !device.recording, device.canRecord, let id = workout?.id else { return }
        ownsRecording = device.startRecording(workoutID: id) != nil
    }
    private func finish() {
        UIApplication.shared.isIdleTimerDisabled = false
        device.endstopFeedbackSuppressed = false
        if ownsRecording, device.recording { device.toggleRecording() }
        ownsRecording = false
        persist()
    }
    private func persist() {
        guard var saved = workout else { return }
        // Keep the paused checkpoint at the instant the timer was frozen.
        if saved.phase != .paused { saved.updatedAt = Date() }
        workout = saved
        do {
            try archive.save(saved); storageError = nil; lastSavedAt = Date()
            if let index = history.firstIndex(where: { $0.id == saved.id }) { history[index] = saved }
            else { history.insert(saved, at: 0) }
        } catch { storageError = "Training konnte nicht gespeichert werden: \(error.localizedDescription)" }
    }
    private func feedback(cadence: Bool = false, releasing: Bool = false) {
        guard let settings = workout?.settings else { return }
        if settings.soundEnabled { AudioServicesPlaySystemSound(cadence ? (releasing ? 1105 : 1104) : 1057) }
        if settings.hapticsEnabled {
            if cadence { UISelectionFeedbackGenerator().selectionChanged() }
            else { UINotificationFeedbackGenerator().notificationOccurred(.success) }
        }
    }
}
