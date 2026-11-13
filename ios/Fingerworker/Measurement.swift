import Foundation

struct Measurement: Identifiable, Codable {
    let id: UInt32
    let milliseconds: UInt32
    let raw: Int32
    let absoluteNewtons: Double
    let tareNewtons: Double
    let batteryMillivolts: UInt16
    let status: UInt16
    let mode: UInt8
    var deviceRepetitions: UInt32? = nil
    var bootID: UInt32? = nil
    var devicePeakMilliNewtons: Int32? = nil
    var peakEpoch: UInt32? = nil
    var valid: Bool { status == 0 }
    var force: Double { absoluteNewtons - tareNewtons }
    var problem: String {
        let names = ["Stromversorgung nicht freigegeben", "ADC nicht bereit", "ADC-Zeitüberschreitung", "ADC gesättigt", "Kalibrierung fehlt", "Endanschlag oder Kabel offen", "Batterie schwach", "Standby"]
        let reasons = names.enumerated().compactMap { status & (1 << $0.offset) != 0 ? $0.element : nil }
        return reasons.isEmpty ? "Unbekannter Gerätestatus" : reasons.joined(separator: ", ")
    }
    // v1: 26 bytes; v2: 34 bytes including device counter and boot ID. Integer force units: millinewtons.
    static func decode(_ data: Data) -> Measurement? {
        let b = Array(data)
        guard b.count >= 2, ((b[0] == 1 && b.count == 26) || (b[0] == 2 && b.count == 34) || (b[0] == 3 && b.count == 43)), b[1] <= 1 else { return nil }
        func u16(_ i: Int) -> UInt16 { UInt16(b[i]) | UInt16(b[i+1]) << 8 }
        func u32(_ i: Int) -> UInt32 { UInt32(b[i]) | UInt32(b[i+1]) << 8 | UInt32(b[i+2]) << 16 | UInt32(b[i+3]) << 24 }
        let raw = Int32(bitPattern: u32(10))
        guard (-8_388_608...8_388_607).contains(raw) else { return nil }
        var sample = Measurement(id: u32(2), milliseconds: u32(6), raw: raw,
                           absoluteNewtons: Double(Int32(bitPattern: u32(14))) / 1000,
                           tareNewtons: Double(Int32(bitPattern: u32(18))) / 1000,
                           batteryMillivolts: u16(22), status: u16(24), mode: b[1])
        if b[0] >= 2 { sample.deviceRepetitions = u32(26); sample.bootID = u32(30) }
        if b[0] == 3 {
            guard b[42] <= 1 else { return nil }
            sample.peakEpoch = u32(38)
            if b[42] == 1 { sample.devicePeakMilliNewtons = Int32(bitPattern: u32(34)) }
        }
        return sample
    }
}

struct RecordedSession: Codable, Identifiable {
    var id: UUID = UUID()
    var startedAt: Date = Date()
    var source: String
    var samples: [Measurement] = []
    var repetitions: [UInt64] = []
    var peak: Double = 0
    var interrupted: Bool = false
    var completed: Bool = false
    var workoutID: UUID? = nil
    var csv: String {
        "source,sequence,device_ms,raw,absolute_N,tare_N,display_N,battery_mV,status,mode,valid,repetitions,device_repetitions,boot_id,device_peak_mN,peak_epoch\n" + samples.enumerated().map { index, sample in
            "\(source),\(sample.id),\(sample.milliseconds),\(sample.raw),\(sample.absoluteNewtons),\(sample.tareNewtons),\(sample.force),\(sample.batteryMillivolts),\(sample.status),\(sample.mode),\(sample.valid),\(repetitions[index]),\(sample.deviceRepetitions.map(String.init) ?? ""),\(sample.bootID.map(String.init) ?? ""),\(sample.devicePeakMilliNewtons.map(String.init) ?? ""),\(sample.peakEpoch.map(String.init) ?? "")"
        }.joined(separator: "\n")
    }
}

struct DevicePeakTracker {
    var token: UInt32 = 0
    private(set) var acknowledged = false
    private(set) var maximum: Double = 0
    mutating func begin(_ token: UInt32) { self.token = token; acknowledged = false; maximum = 0 }
    mutating func receive(_ sample: Measurement) -> Bool {
        guard token != 0, sample.peakEpoch == token else { acknowledged = false; return false }
        acknowledged = true
        if let peak = sample.devicePeakMilliNewtons { maximum = max(maximum, Double(peak) / 1000) }
        return true
    }
}

struct SessionArchive {
    let directory: URL
    func save(_ session: RecordedSession) throws {
        guard session.samples.count == session.repetitions.count else { throw CocoaError(.fileWriteUnknown) }
        try FileManager.default.createDirectory(at: directory, withIntermediateDirectories: true)
        try JSONEncoder().encode(session).write(to: directory.appendingPathComponent(session.id.uuidString + ".json"), options: .atomic)
    }
    func load() throws -> [RecordedSession] {
        guard FileManager.default.fileExists(atPath: directory.path) else { return [] }
        return try FileManager.default.contentsOfDirectory(at: directory, includingPropertiesForKeys: nil)
            .filter { $0.pathExtension == "json" }.map { url in
                let session = try JSONDecoder().decode(RecordedSession.self, from: Data(contentsOf: url))
                guard session.samples.count == session.repetitions.count else { throw CocoaError(.fileReadCorruptFile) }
                return session
            }.sorted { $0.startedAt > $1.startedAt }
    }
}

/// Counts observed end-stop edges; ENDSTOP_OR_OPEN cannot distinguish a cable break.
struct RepetitionCounter {
    private(set) var count = 0
    private var releasedAt: UInt32?
    private var armed = false

    mutating func invalidate() { releasedAt = nil; armed = false }
    mutating func reset() { count = 0; invalidate() }
    mutating func receive(_ sample: Measurement) {
        guard sample.mode == 0, sample.status & ~UInt16(1 << 5) == 0 else { invalidate(); return }
        if sample.status & (1 << 5) != 0 {
            if armed { count += 1 }
            invalidate()
        } else {
            if releasedAt == nil { releasedAt = sample.milliseconds }
            if sample.milliseconds &- releasedAt! >= 10 { armed = true }
        }
    }
}


/// Live feedback only: never replay cumulative counts after a gap or reconnect.
struct EndstopFeedbackTracker {
    private var sequence: UInt32?
    private var bootID: UInt32?
    private var counter = RepetitionCounter()

    mutating func clear() { self = EndstopFeedbackTracker() }
    mutating func receive(_ sample: Measurement) -> Bool {
        if sample.bootID != bootID {
            clear(); bootID = sample.bootID
        }
        if let sequence {
            let delta = sample.id &- sequence
            guard delta > 0, delta < 0x80000000 else { return false }
            if delta > 1 { counter.invalidate() }
        }
        sequence = sample.id
        let previous = counter.count
        counter.receive(sample)
        return counter.count > previous
    }
}

/// Tracks cumulative device counts, including missed notifications and reconnects.
struct DeviceCounterTracker {
    private(set) var displayed: UInt64 = 0
    private var boot: UInt32?
    private var previous: UInt32?
    mutating func receive(total: UInt32, bootID: UInt32) {
        guard boot == bootID, let last = previous else {
            boot = bootID; previous = total; displayed = UInt64(total); return
        }
        let delta = total &- last
        guard delta < 0x80000000 else { return }
        displayed += UInt64(delta); previous = total
    }
    mutating func resetDisplay() { displayed = 0 }
    mutating func clear() { self = DeviceCounterTracker() }
}
