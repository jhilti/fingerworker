import Foundation

enum TrainingHand: String, Codable, CaseIterable, Identifiable {
    case left, right
    var id: String { rawValue }
    var title: String { self == .left ? "Links" : "Rechts" }
    var handTitle: String { self == .left ? "Linke Hand" : "Rechte Hand" }
    var adjective: String { self == .left ? "linke" : "rechte" }
    var other: TrainingHand { self == .left ? .right : .left }
}

enum TrainingCountingMode: String, Codable, CaseIterable, Identifiable {
    case device, manual
    var id: String { rawValue }
    var title: String { self == .device ? "Automatisch am Gerät" : "Manuell" }
}

enum TrainingMode: String, CaseIterable, Identifiable {
    case curls, carc
    var id: String { rawValue }
    var title: String { self == .carc ? "cARC · nach Zeit" : "Finger Curls" }
}

struct CARCSettings: Codable, Equatable {
    var durationSeconds = 300
    var showForce = false
    // A user-chosen reminder, not a physiological threshold or a prescription.
    var forceCeilingNewtons = 50.0
    func displayedForce(from sample: Measurement?) -> Double? {
        guard showForce, let sample, sample.valid, sample.mode == 0, sample.force.isFinite else { return nil }
        return sample.force
    }
    var normalized: CARCSettings {
        var result = self
        result.durationSeconds = min(3600, max(60, durationSeconds))
        result.forceCeilingNewtons = forceCeilingNewtons.isFinite ? min(500, max(5, forceCeilingNewtons)) : 50
        return result
    }
}

struct TrainingSettings: Codable, Equatable {
    var repetitionsPerSet = 15
    var setsPerHand = 6
    var restSeconds = 180
    var startingHand: TrainingHand = .left
    var countingMode: TrainingCountingMode = .device
    var preparationSeconds = 5
    var cadenceEnabled = false
    var pullSeconds = 1.0
    var releaseSeconds = 1.0
    var soundEnabled = false
    var hapticsEnabled = true
    // Optional so existing settings and archives continue to decode as curls.
    var carc: CARCSettings?
    var isCARC: Bool { carc != nil }
    var mode: TrainingMode {
        get { isCARC ? .carc : .curls }
        set {
            guard newValue != mode else { return }
            carc = newValue == .carc ? CARCSettings() : nil
            if newValue == .carc { setsPerHand = 1; restSeconds = 0; cadenceEnabled = true }
        }
    }
    var usesDeviceCounter: Bool { !isCARC && countingMode == .device }
    var usesCadence: Bool { isCARC || cadenceEnabled }
    var protocolDescription: String {
        isCARC ? "cARC · \(setsPerHand) × \(Self.clock(TimeInterval(carc!.durationSeconds))) pro Hand"
            : "\(setsPerHand) × \(repetitionsPerSet) pro Hand"
    }

    var normalized: TrainingSettings {
        var result = self
        result.repetitionsPerSet = min(50, max(1, repetitionsPerSet))
        result.setsPerHand = min(12, max(1, setsPerHand))
        result.restSeconds = min(900, max(0, restSeconds))
        result.preparationSeconds = min(15, max(0, preparationSeconds))
        result.pullSeconds = pullSeconds.isFinite ? min(5, max(0.5, pullSeconds)) : 1
        result.releaseSeconds = releaseSeconds.isFinite ? min(5, max(0.5, releaseSeconds)) : 1
        result.carc = carc?.normalized
        return result
    }
    var totalSets: Int { setsPerHand * 2 }
    var totalRepetitions: Int { isCARC ? 0 : totalSets * repetitionsPerSet }
    var totalWorkSeconds: TimeInterval { TimeInterval(totalSets * (carc?.durationSeconds ?? 0)) }
    var restLabel: String { Self.clock(TimeInterval(restSeconds)) }
    static func clock(_ seconds: TimeInterval) -> String {
        let value = max(0, Int(ceil(seconds.isFinite ? seconds : 0)))
        return String(format: "%d:%02d", value / 60, value % 60)
    }
}

enum TrainingPhase: String, Codable {
    case preparing, working, resting, paused, completed, cancelled
    var isFinished: Bool { self == .completed || self == .cancelled }
}

struct TrainingSetResult: Codable, Identifiable {
    var id = UUID()
    var hand: TrainingHand
    var number: Int
    var repetitions: Int
    var peakNewtons: Double
    var durationSeconds: TimeInterval
    var endedAt: Date
    var completed = true
    var restBeforeSeconds: TimeInterval?
    var forceSampleCount: Int?
}

/// A two-hand workout. Rest is measured independently from each hand's last set.
/// The settings are a snapshot: editing the next workout never changes a running one.
struct TrainingSession: Codable, Identifiable {
    var id = UUID()
    var settings: TrainingSettings
    var source: String
    var startedAt: Date
    var endedAt: Date?
    var updatedAt: Date
    var phase: TrainingPhase
    var activeHand: TrainingHand
    var phaseStartedAt: Date
    var deadline: Date?
    var currentRepetitions = 0
    var currentPeakNewtons = 0.0
    var currentForceSampleCount: Int?
    var setStartedAt: Date?
    var leftReadyAt: Date?
    var rightReadyAt: Date?
    var results: [TrainingSetResult] = []
    var pausedPhase: TrainingPhase?
    var pausedAt: Date?
    var pauseReason: String?
    var pausedSeconds: TimeInterval = 0
    // Optional for compatibility with workouts saved before detailed logging.
    var log: TrainingLog?

    init(settings: TrainingSettings, source: String, now: Date) {
        self.settings = settings.normalized
        self.source = source
        startedAt = now; updatedAt = now; phaseStartedAt = now
        activeHand = settings.startingHand
        phase = .preparing
        deadline = now.addingTimeInterval(TimeInterval(self.settings.preparationSeconds))
        log = TrainingLog()
        currentForceSampleCount = 0
        appendEvent(.started, at: now, includeSet: false)
        if self.settings.preparationSeconds > 0 {
            appendEvent(.preparationStarted, at: now, duration: TimeInterval(self.settings.preparationSeconds))
        }
        tick(at: now)
    }

    var isRunning: Bool { !phase.isFinished && phase != .paused }
    var isOngoing: Bool { !phase.isFinished }
    var totalRepetitions: Int { results.reduce(0) { $0 + $1.repetitions } + (isOngoing ? currentRepetitions : 0) }
    var completedSets: Int { results.filter(\.completed).count }
    var peakNewtons: Double { max(currentPeakNewtons, results.map(\.peakNewtons).max() ?? 0) }
    var hasForceSamples: Bool {
        (currentForceSampleCount ?? 0) > 0 || results.contains { ($0.forceSampleCount ?? (settings.isCARC ? 0 : 1)) > 0 }
    }
    var progress: Double { progress(at: updatedAt) }
    func workSeconds(at now: Date) -> TimeInterval {
        let end = endedAt ?? (phase == .paused ? pausedAt : nil) ?? now
        let current = isOngoing ? max(0, end.timeIntervalSince(setStartedAt ?? end)) : 0
        return results.reduce(0) { $0 + $1.durationSeconds } + min(TimeInterval(settings.carc?.durationSeconds ?? Int.max), current)
    }
    func progress(at now: Date) -> Double {
        if settings.isCARC { return min(1, workSeconds(at: now) / settings.totalWorkSeconds) }
        return min(1, Double(totalRepetitions) / Double(settings.totalRepetitions))
    }
    func completedSets(for hand: TrainingHand) -> Int { results.filter { $0.hand == hand && $0.completed }.count }
    var currentSetNumber: Int { completedSets(for: activeHand) + 1 }
    func readyAt(for hand: TrainingHand) -> Date? { hand == .left ? leftReadyAt : rightReadyAt }
    func remaining(at now: Date) -> TimeInterval {
        guard let deadline else { return 0 }
        return max(0, deadline.timeIntervalSince(phase == .paused ? pausedAt ?? now : now))
    }
    func elapsed(at now: Date) -> TimeInterval {
        max(0, (endedAt ?? (phase == .paused ? pausedAt : nil) ?? now).timeIntervalSince(startedAt) - pausedSeconds)
    }
    func isPulling(at now: Date) -> Bool {
        let elapsed = max(0, (phase == .paused ? pausedAt ?? now : now).timeIntervalSince(phaseStartedAt))
        return elapsed.truncatingRemainder(dividingBy: settings.pullSeconds + settings.releaseSeconds) < settings.pullSeconds
    }

    mutating func tick(at now: Date) {
        if phase == .working, settings.isCARC, let deadline, now >= deadline {
            // Credit only this block. A delayed timer must never run the next
            // hand retroactively, even with zero preparation or rest.
            finishSet(at: deadline, nextStartAt: now)
            return
        }
        guard (phase == .preparing || phase == .resting), let deadline, now >= deadline else { return }
        phase = .working; phaseStartedAt = now
        self.deadline = settings.carc.map { now.addingTimeInterval(TimeInterval($0.durationSeconds)) }
        setStartedAt = now; updatedAt = now
        var rest: TimeInterval?
        if log?.hasCompleteTimeline == true,
           let previous = results.last(where: { $0.hand == activeHand && $0.completed }) {
            rest = max(0, now.timeIntervalSince(previous.endedAt) - (log?.interruptionSeconds(from: previous.endedAt, to: now) ?? 0))
        }
        appendEvent(.setStarted, at: now, duration: rest)
    }
    mutating func record(force: Double) {
        guard phase == .working, force.isFinite else { return }
        currentPeakNewtons = max(currentPeakNewtons, force)
        currentForceSampleCount = (currentForceSampleCount ?? 0) + 1
    }
    mutating func addRepetitions(_ count: Int = 1, at now: Date) {
        guard phase == .working, !settings.isCARC, count > 0 else { return }
        // Missed BLE notifications may contain several counts. Overflow belongs to
        // neither the next hand nor the next set and must never spill into it.
        let accepted = min(count, settings.repetitionsPerSet - currentRepetitions)
        currentRepetitions += accepted
        appendEvent(.repetitionsAdded, at: now, delta: accepted)
        updatedAt = now
        if currentRepetitions == settings.repetitionsPerSet { finishSet(at: now) }
    }
    mutating func undoRepetition(at now: Date) {
        guard phase == .working, !settings.isCARC, currentRepetitions > 0 else { return }
        currentRepetitions -= 1; updatedAt = now
        appendEvent(.repetitionRemoved, at: now, delta: -1)
    }
    private mutating func finishSet(at now: Date, nextStartAt: Date? = nil) {
        results.append(TrainingSetResult(hand: activeHand, number: currentSetNumber,
            repetitions: currentRepetitions, peakNewtons: currentPeakNewtons,
            durationSeconds: max(0, now.timeIntervalSince(setStartedAt ?? now)), endedAt: now,
            restBeforeSeconds: currentSetRest, forceSampleCount: currentForceSampleCount))
        appendEvent(.setFinished, at: now, duration: results.last?.durationSeconds)
        if activeHand == .left { leftReadyAt = now.addingTimeInterval(TimeInterval(settings.restSeconds)) }
        else { rightReadyAt = now.addingTimeInterval(TimeInterval(settings.restSeconds)) }
        currentRepetitions = 0; currentPeakNewtons = 0; setStartedAt = nil
        currentForceSampleCount = 0
        if completedSets == settings.totalSets {
            phase = .completed; endedAt = now; deadline = nil; updatedAt = now
            appendEvent(.completed, at: now, includeSet: false)
            return
        }
        activeHand = activeHand.other
        let next = nextStartAt ?? now
        phaseStartedAt = next
        if let ready = readyAt(for: activeHand), ready > next {
            phase = .resting; deadline = ready
            appendEvent(.restStarted, at: next, duration: ready.timeIntervalSince(next))
        } else {
            phase = .preparing; deadline = next.addingTimeInterval(TimeInterval(settings.preparationSeconds))
            if settings.preparationSeconds > 0 {
                appendEvent(.preparationStarted, at: next, duration: TimeInterval(settings.preparationSeconds))
            }
        }
        updatedAt = next
        tick(at: next)
    }
    mutating func pause(at now: Date, reason: String? = nil) {
        tick(at: now)
        guard isRunning else { return }
        pausedPhase = phase; pausedAt = now; pauseReason = reason; phase = .paused; updatedAt = now
        appendEvent(.paused, at: now, reason: reason)
    }
    mutating func resume(at now: Date) {
        guard phase == .paused, let previous = pausedPhase, let pausedAt else { return }
        let duration = max(0, now.timeIntervalSince(pausedAt))
        pausedSeconds += duration
        phaseStartedAt = phaseStartedAt.addingTimeInterval(duration)
        deadline = deadline?.addingTimeInterval(duration)
        setStartedAt = setStartedAt?.addingTimeInterval(duration)
        leftReadyAt = leftReadyAt?.addingTimeInterval(duration)
        rightReadyAt = rightReadyAt?.addingTimeInterval(duration)
        phase = previous; self.pausedAt = nil; pausedPhase = nil; pauseReason = nil; updatedAt = now
        appendEvent(.resumed, at: now, duration: duration)
    }
    mutating func cancel(at now: Date) {
        tick(at: now)
        guard isOngoing else { return }
        if phase == .paused, let pausedAt {
            // Closing a paused workout must not claim that training resumed.
            let duration = max(0, now.timeIntervalSince(pausedAt))
            pausedSeconds += duration
            setStartedAt = setStartedAt?.addingTimeInterval(duration)
            self.pausedAt = nil; pausedPhase = nil; pauseReason = nil
        }
        if currentRepetitions > 0 || (settings.isCARC && setStartedAt != nil) {
            results.append(TrainingSetResult(hand: activeHand, number: currentSetNumber,
                repetitions: currentRepetitions, peakNewtons: currentPeakNewtons,
                durationSeconds: max(0, now.timeIntervalSince(setStartedAt ?? now)), endedAt: now, completed: false,
                restBeforeSeconds: currentSetRest, forceSampleCount: currentForceSampleCount))
            appendEvent(.setFinished, at: now, duration: results.last?.durationSeconds, reason: settings.isCARC ? "Teil-Block" : "Teil-Satz")
        }
        currentRepetitions = 0; currentForceSampleCount = 0
        phase = .cancelled; endedAt = now; deadline = nil; updatedAt = now
        appendEvent(.cancelled, at: now, includeSet: false)
    }

    private var currentSetRest: TimeInterval? {
        log?.events.last(where: { $0.kind == .setStarted && $0.hand == activeHand && $0.setNumber == currentSetNumber })?.durationSeconds
    }
    private mutating func appendEvent(_ kind: TrainingEventKind, at date: Date, delta: Int? = nil,
                                     duration: TimeInterval? = nil, reason: String? = nil, includeSet: Bool = true) {
        guard log != nil else { return }
        // setFinished follows result insertion, so its number is the stored one.
        let number = kind == .setFinished ? results.last?.number : currentSetNumber
        log?.events.append(TrainingEvent(date: date, kind: kind, hand: includeSet ? activeHand : nil,
            setNumber: includeSet ? number : nil, repetitions: includeSet && !settings.isCARC ? currentRepetitions : nil,
            delta: delta, durationSeconds: duration, reason: reason))
    }
}

/// Uses the firmware's cumulative counter when present and falls back to switch
/// edges for v1. Always observes idle/rest packets so they cannot enter a set.
struct TrainingRepetitionTracker {
    private var bootID: UInt32?
    private var total: UInt32?
    private var sequence: UInt32?
    private var counter = RepetitionCounter()
    private(set) var rebooted = false

    mutating func clear() { self = TrainingRepetitionTracker() }
    mutating func receive(_ sample: Measurement) -> Int {
        rebooted = false
        guard sample.mode == 0, sample.status & ~UInt16(1 << 5) == 0 else {
            total = nil; bootID = nil; sequence = nil; counter.invalidate(); return 0
        }
        if let next = sample.deviceRepetitions, let boot = sample.bootID {
            guard let previous = total, bootID == boot else {
                rebooted = bootID != nil && bootID != boot
                bootID = boot; total = next; sequence = sample.id; return 0
            }
            let delta = next &- previous
            guard delta < 0x80000000 else { return 0 }
            total = next; sequence = sample.id; return Int(delta)
        }
        if total != nil { total = nil; bootID = nil; sequence = nil; counter.invalidate() }
        if let sequence {
            let difference = sample.id &- sequence
            guard difference > 0, difference < 0x80000000 else { return 0 }
            if difference > 1 { counter.invalidate() }
        }
        sequence = sample.id
        let previous = counter.count
        counter.receive(sample)
        return counter.count - previous
    }
}

struct TrainingArchive {
    let directory: URL
    func save(_ session: TrainingSession) throws {
        try validate(session)
        try FileManager.default.createDirectory(at: directory, withIntermediateDirectories: true)
        try JSONEncoder().encode(session).write(to: directory.appendingPathComponent(session.id.uuidString + ".json"), options: .atomic)
    }
    func load() throws -> [TrainingSession] {
        guard FileManager.default.fileExists(atPath: directory.path) else { return [] }
        return try FileManager.default.contentsOfDirectory(at: directory, includingPropertiesForKeys: nil)
            .filter { $0.pathExtension == "json" }.map { url in
                let session = try JSONDecoder().decode(TrainingSession.self, from: Data(contentsOf: url))
                try validate(session)
                return session
            }.sorted { $0.startedAt > $1.startedAt }
    }
    private func validate(_ session: TrainingSession) throws {
        guard session.settings == session.settings.normalized,
              (0...session.settings.repetitionsPerSet).contains(session.currentRepetitions),
              session.currentPeakNewtons.isFinite && session.currentPeakNewtons >= 0,
              session.currentForceSampleCount == nil || session.currentForceSampleCount! >= 0,
              session.pausedSeconds.isFinite && session.pausedSeconds >= 0,
              session.results.count <= session.settings.totalSets,
              session.results.allSatisfy({ (1...session.settings.setsPerHand).contains($0.number)
                  && (session.settings.isCARC ? $0.repetitions == 0 : (1...session.settings.repetitionsPerSet).contains($0.repetitions))
                  && $0.peakNewtons.isFinite && $0.peakNewtons >= 0
                  && ($0.forceSampleCount == nil || $0.forceSampleCount! >= 0)
                  && $0.durationSeconds.isFinite && $0.durationSeconds >= 0
                  && ($0.restBeforeSeconds == nil || ($0.restBeforeSeconds!.isFinite && $0.restBeforeSeconds! >= 0))
                  && (session.settings.isCARC
                      ? ($0.durationSeconds <= TimeInterval(session.settings.carc!.durationSeconds)
                          && (!$0.completed || $0.durationSeconds == TimeInterval(session.settings.carc!.durationSeconds)))
                      : (!$0.completed || $0.repetitions == session.settings.repetitionsPerSet)) }),
              !session.settings.isCARC || session.currentRepetitions == 0,
              !session.settings.isCARC || (session.phase != .working && session.pausedPhase != .working) || session.deadline != nil,
              Set(session.results.map { "\($0.hand.rawValue)-\($0.number)" }).count == session.results.count,
              session.phase != .paused || (session.pausedAt != nil && session.pausedPhase != nil
                  && session.pausedPhase != .paused && session.pausedPhase?.isFinished == false),
              session.phase != .completed || session.completedSets == session.settings.totalSets else {
            throw CocoaError(.fileReadCorruptFile)
        }
        if let log = session.log {
            guard log.perceivedExertion == nil || (1...10).contains(log.perceivedExertion!),
                  Set(log.events.map(\.id)).count == log.events.count,
                  log.events.allSatisfy({ event in
                      (event.setNumber == nil || (1...session.settings.setsPerHand).contains(event.setNumber!))
                      && (event.repetitions == nil || (0...session.settings.repetitionsPerSet).contains(event.repetitions!))
                      && (event.durationSeconds == nil || (event.durationSeconds!.isFinite && event.durationSeconds! >= 0))
                      && (event.delta == nil || (event.kind == .repetitionRemoved ? event.delta == -1 : (1...session.settings.repetitionsPerSet).contains(event.delta!)))
                  }) else { throw CocoaError(.fileReadCorruptFile) }
        }
    }
}
