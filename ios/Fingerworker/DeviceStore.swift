import Foundation
import CoreBluetooth
import Combine
import UIKit

final class DeviceStore: NSObject, ObservableObject, CBCentralManagerDelegate, CBPeripheralDelegate {
    static let service = CBUUID(string: "C37A0001-7B4D-4A26-9C36-2C17F770A001")
    static let peakReset = CBUUID(string: "C37A0003-7B4D-4A26-9C36-2C17F770A001")
    static let telemetry = CBUUID(string: "C37A0002-7B4D-4A26-9C36-2C17F770A001")
    @Published var connection = "Disconnected"
    @Published var devices: [CBPeripheral] = []
    @Published var latest: Measurement?
    @Published var points: [Measurement] = []
    @Published var recording = false
    @Published var demo = false
    @Published var lostPackets: UInt64 = 0
    @Published var peak = 0.0
    @Published var repetitions: UInt64 = 0
    @Published var counterFromDevice = false
    @Published var endstopSoundEnabled = UserDefaults.standard.object(forKey: "endstopSoundEnabled") as? Bool ?? true {
        didSet { UserDefaults.standard.set(endstopSoundEnabled, forKey: "endstopSoundEnabled") }
    }
    @Published var endstopHapticsEnabled = UserDefaults.standard.bool(forKey: "endstopHapticsEnabled") {
        didSet { UserDefaults.standard.set(endstopHapticsEnabled, forKey: "endstopHapticsEnabled") }
    }
    private var endstopTracker = EndstopFeedbackTracker()
    var endstopFeedbackSuppressed = false {
        didSet { suspendEndstopFeedback() }
    }
    private let endstopFeedback = EndstopFeedback()
    private var deviceCounter = DeviceCounterTracker()
    private var demoCounter = RepetitionCounter()
    private var counter = RepetitionCounter()
    private var sessionCounts: [UInt64] = []
    @Published var savedSessions: [RecordedSession] = []
    @Published var storageError: String?
    @Published var peakFromDevice = false
    @Published var stopping = false
    private var stopTimer: Timer?
    private let archive = SessionArchive(directory: FileManager.default.urls(for: .applicationSupportDirectory, in: .userDomainMask)[0].appendingPathComponent("FingerworkerSessions", isDirectory: true))
    private var activeSession: RecordedSession?
    private var peakCommand: CBCharacteristic?
    private var peakToken: UInt32 = 0
    private var peakTracker = DevicePeakTracker()
    private var peakAckBoot: UInt32?
    private var lastPeakRequest = Date.distantPast
    private var lastSave = Date.distantPast
    private var wantedPeripheral: CBPeripheral?
    private var reconnectTimer: Timer?
    private var central: CBCentralManager!
    private var peripheral: CBPeripheral?
    private var timer: Timer?
    private var lastSequence: UInt32?
    private var lastBootID: UInt32?
    private var session: [Measurement] = []
    private var sessionSource = "device"
    private var demoTick: UInt32 = 0
    private var freshness: Timer?

    override init() {
        super.init()
        do { savedSessions = try archive.load() } catch { storageError = "Cannot load sessions: \(error.localizedDescription)" }
        if let restored = savedSessions.first {
            activeSession = restored; session = restored.samples; sessionCounts = restored.repetitions
            sessionSource = restored.source; peak = restored.peak
        }
        central = CBCentralManager(delegate: self, queue: .main)
        #if targetEnvironment(simulator)
        DispatchQueue.main.async { [weak self] in self?.startDemo() }
        #endif
        let freshnessTimer = Timer(timeInterval: 1, repeats: true) { [weak self] _ in
            guard let self, !self.demo, let received = self.receivedAt,
                  Date().timeIntervalSince(received) > 2 else { return }
            self.latest = nil; self.counter.invalidate(); self.suspendEndstopFeedback()
            if self.peripheral != nil { self.connection = "Connected · waiting for data" }
        }
        RunLoop.main.add(freshnessTimer, forMode: .common); freshness = freshnessTimer
    }
    private var receivedAt: Date?
    var canRecord: Bool { demo || peripheral?.state == .connected && connection == "Connected" }
    func centralManagerDidUpdateState(_ central: CBCentralManager) {
        guard !demo else { return }
        switch central.state {
        case .poweredOn: connection = "Ready to scan"; if let wantedPeripheral { connect(wantedPeripheral) }
        case .poweredOff: connection = "Turn on Bluetooth"
        case .unauthorized: connection = "Allow Bluetooth in Settings"
        case .unsupported: connection = "Bluetooth unavailable"
        default: connection = "Bluetooth starting"
        }
    }
    func scan() {
        disconnect()
        guard central.state == .poweredOn else { centralManagerDidUpdateState(central); return }
        devices = []; connection = "Scanning…"
        central.scanForPeripherals(withServices: [Self.service])
        DispatchQueue.main.asyncAfter(deadline: .now() + 10) { [weak self] in
            guard let self, self.connection == "Scanning…" else { return }
            self.central.stopScan(); self.connection = self.devices.isEmpty ? "No compatible device found" : "Choose a device"
        }
    }
    func centralManager(_ central: CBCentralManager, didDiscover peripheral: CBPeripheral, advertisementData: [String: Any], rssi RSSI: NSNumber) {
        if !devices.contains(where: { $0.identifier == peripheral.identifier }) { devices.append(peripheral) }
    }
    func connect(_ device: CBPeripheral) {
        reconnectTimer?.invalidate(); reconnectTimer = nil
        central.stopScan(); wantedPeripheral = device; peripheral = device; device.delegate = self
        connection = "Connecting…"; central.connect(device)
    }
    func centralManager(_ central: CBCentralManager, didConnect peripheral: CBPeripheral) {
        connection = "Discovering service…"; peripheral.discoverServices([Self.service])
    }
    func centralManager(_ central: CBCentralManager, didFailToConnect peripheral: CBPeripheral, error: Error?) {
        guard self.peripheral?.identifier == peripheral.identifier else { return }
        self.peripheral = nil; connection = "Connection failed"; scheduleReconnect()
    }
    func centralManager(_ central: CBCentralManager, didDisconnectPeripheral peripheral: CBPeripheral, error: Error?) {
        guard self.peripheral?.identifier == peripheral.identifier else { return }
        self.peripheral = nil; peakCommand = nil; latest = nil; counter.invalidate(); suspendEndstopFeedback(); lastSequence = nil; connection = "Disconnected"
        if recording { activeSession?.interrupted = true; saveSession() }; scheduleReconnect()
    }
    func peripheral(_ peripheral: CBPeripheral, didDiscoverServices error: Error?) {
        guard error == nil, let service = peripheral.services?.first(where: { $0.uuid == Self.service }) else { connection = "Service unavailable"; return }
        peripheral.discoverCharacteristics([Self.telemetry, Self.peakReset], for: service)
    }
    func peripheral(_ peripheral: CBPeripheral, didDiscoverCharacteristicsFor service: CBService, error: Error?) {
        guard error == nil, let c = service.characteristics?.first(where: { $0.uuid == Self.telemetry }), c.properties.contains(.notify) else { connection = "Telemetry unavailable"; return }
        peakCommand = service.characteristics?.first(where: { $0.uuid == Self.peakReset && $0.properties.contains(.write) })
        peripheral.setNotifyValue(true, for: c)
    }
    func peripheral(_ peripheral: CBPeripheral, didUpdateNotificationStateFor characteristic: CBCharacteristic, error: Error?) {
        connection = error == nil && characteristic.isNotifying ? "Connected" : "Subscription failed"
    }
    func peripheral(_ peripheral: CBPeripheral, didUpdateValueFor characteristic: CBCharacteristic, error: Error?) {
        guard peripheral.identifier == self.peripheral?.identifier, characteristic.uuid == Self.telemetry else { return }
        guard error == nil, let data = characteristic.value, let sample = Measurement.decode(data) else { latest = nil; counter.invalidate(); suspendEndstopFeedback(); connection = "Invalid telemetry packet"; return }
        connection = "Connected"; accept(sample)
    }
    private func scheduleReconnect() {
        guard wantedPeripheral != nil, !demo else { return }
        reconnectTimer?.invalidate()
        reconnectTimer = Timer.scheduledTimer(withTimeInterval: 3, repeats: false) { [weak self] _ in
            guard let self, self.central.state == .poweredOn, let target = self.wantedPeripheral else { return }
            self.connect(target)
        }
    }
    private func requestPeakReset() {
        guard recording, peakToken != 0, let peripheral, peripheral.state == .connected, let peakCommand,
              Date().timeIntervalSince(lastPeakRequest) >= 1 else { return }
        var token = peakToken.littleEndian
        peripheral.writeValue(withUnsafeBytes(of: &token) { Data($0) }, for: peakCommand, type: .withResponse)
        lastPeakRequest = Date()
    }
    private func saveSession() {
        guard var saved = activeSession, !session.isEmpty else { return }
        saved.samples = session; saved.repetitions = sessionCounts; saved.peak = peak
        activeSession = saved
        do {
            try archive.save(saved); storageError = nil; lastSave = Date()
            if let index = savedSessions.firstIndex(where: { $0.id == saved.id }) { savedSessions[index] = saved }
            else { savedSessions.insert(saved, at: 0) }
        } catch { storageError = "Recording could not be saved: \(error.localizedDescription)" }
    }
    func saveForBackground() {
        saveSession()
    }
    func suspendEndstopFeedback() { endstopTracker.clear() }
    func previewEndstopFeedback() {
        endstopFeedback.play(sound: endstopSoundEnabled, haptics: endstopHapticsEnabled)
    }
    func selectSession(_ saved: RecordedSession) {
        guard !recording else { return }
        activeSession = saved; session = saved.samples; sessionCounts = saved.repetitions
        sessionSource = saved.source; peak = saved.peak
    }
    private func accept(_ sample: Measurement) {
        // Rebase on long stalls even before the periodic freshness timer fires.
        if let receivedAt, Date().timeIntervalSince(receivedAt) > 2 { suspendEndstopFeedback() }
        if let boot = sample.bootID, boot != lastBootID {
            if recording && lastBootID != nil { activeSession?.interrupted = true }
            lastSequence = nil; points = []; lastBootID = boot
        }
        if let last = lastSequence {
            let delta = sample.id &- last
            guard delta > 0, delta < 0x80000000 else { return }
            lostPackets += UInt64(delta - 1)
            if delta > 1 { counter.invalidate() }
        }
        if let total = sample.deviceRepetitions, let bootID = sample.bootID {
            deviceCounter.receive(total: total, bootID: bootID); repetitions = deviceCounter.displayed; counterFromDevice = true
        } else {
            counter.receive(sample); repetitions = UInt64(counter.count); counterFromDevice = false
        }
        lastSequence = sample.id; receivedAt = Date()
        if UIApplication.shared.applicationState == .active && !endstopFeedbackSuppressed {
            if endstopTracker.receive(sample) { previewEndstopFeedback() }
        } else { suspendEndstopFeedback() }
        points.append(sample); if points.count > 250 { points.removeFirst(points.count - 250) }
        if recording {
            session.append(sample); sessionCounts.append(repetitions)
            if sample.peakEpoch != nil && peakCommand != nil {
                if peakTracker.receive(sample) {
                    peakFromDevice = true; peakAckBoot = sample.bootID
                    peak = max(peak, peakTracker.maximum)
                } else { requestPeakReset() }
                if sample.bootID != peakAckBoot { requestPeakReset() }
            } else {
                peakFromDevice = false
                if sample.valid { peak = max(peak, sample.force) }
            }
            if Date().timeIntervalSince(lastSave) >= 1 { saveSession() }
            if stopping { finishRecording() }
        }
        // Publish after archiving this sample. A training observer may finish the
        // recording when its final repetition arrives.
        latest = sample
    }
    func disconnect() {
        if recording { activeSession?.interrupted = true; finishRecording() }
        saveSession(); wantedPeripheral = nil; reconnectTimer?.invalidate(); reconnectTimer = nil; peakCommand = nil
        timer?.invalidate(); timer = nil; demo = false; if central.state == .poweredOn { central.stopScan() }; counter.invalidate()
        if let peripheral { central.cancelPeripheralConnection(peripheral) }
        peripheral = nil; latest = nil; points = []; lastSequence = nil; receivedAt = nil; recording = false; suspendEndstopFeedback()
        connection = "Disconnected"
    }
    func startDemo() {
        disconnect(); points = []; lostPackets = 0; demoTick = 0; deviceCounter.clear(); demoCounter.reset(); resetRepetitions(); demo = true; connection = "Simulation"
        let demoTimer = Timer(timeInterval: 0.04, repeats: true) { [weak self] _ in
            guard let self else { return }; self.demoTick &+= 1
            let t = Double(self.demoTick) * 0.04
            let force = max(0, 90 * sin(t * 0.8))
            if self.demoTick == 1 { print("Fingerworker simulation is streaming force measurements at 25 Hz") }
            var sample = Measurement(id: self.demoTick, milliseconds: self.demoTick &* 40, raw: Int32(force * 1000), absoluteNewtons: force, tareNewtons: 0, batteryMillivolts: 3950, status: sin(t * 0.8) > 0.96 ? 32 : 0, mode: 0)
            self.demoCounter.receive(sample)
            sample.deviceRepetitions = UInt32(self.demoCounter.count); sample.bootID = 0x53494d31
            self.accept(sample)
        }
        RunLoop.main.add(demoTimer, forMode: .common); timer = demoTimer
    }
    func toggleRecording() {
        if recording {
            guard !stopping else { return }
            if !demo && peakCommand != nil && peripheral?.state == .connected {
                // Include the next cumulative peak notification before final save.
                stopping = true
                stopTimer = Timer.scheduledTimer(withTimeInterval: 1, repeats: false) { [weak self] _ in
                    self?.activeSession?.interrupted = true; self?.finishRecording()
                }
            } else { finishRecording() }
        }
        else { startRecording() }
    }
    @discardableResult
    func startRecording(workoutID: UUID? = nil) -> UUID? {
        guard canRecord, !recording else { return nil }
        session = []; sessionCounts = []; resetRepetitions(); sessionSource = demo ? "simulation" : "device"
        peak = 0; peakFromDevice = false; recording = true
        activeSession = RecordedSession(source: sessionSource, workoutID: workoutID)
        peakToken = UInt32.random(in: 1...UInt32.max); peakAckBoot = nil; lastPeakRequest = .distantPast
        peakTracker.begin(peakToken)
        requestPeakReset()
        return activeSession?.id
    }
    private func finishRecording() {
        stopTimer?.invalidate(); stopTimer = nil; stopping = false; recording = false
        activeSession?.completed = true; saveSession()
    }
    func resetRepetitions() { counter.reset(); deviceCounter.resetDisplay(); repetitions = 0 }
    var csv: String {
        var saved = activeSession ?? RecordedSession(source: sessionSource)
        saved.samples = session; saved.repetitions = sessionCounts
        return saved.csv
    }
    var hasSession: Bool { !session.isEmpty }
}
