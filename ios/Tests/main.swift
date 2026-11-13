import Foundation
func packet(sequence: UInt32 = 42, raw: Int32 = -123, status: UInt16 = 0) -> Data {
    var result = Data([1, 0])
    func append<T: FixedWidthInteger>(_ value: T) { var v = value.littleEndian; withUnsafeBytes(of: &v) { result.append(contentsOf: $0) } }
    append(sequence); append(UInt32(1000)); append(raw); append(Int32(125_000)); append(Int32(5_000)); append(UInt16(3950)); append(status)
    return result
}
let valid = Measurement.decode(packet())!
precondition(valid.id == 42 && valid.raw == -123 && valid.force == 120 && valid.valid)
precondition(Measurement.decode(packet(status: 32))!.valid == false)
precondition(Measurement.decode(packet(status: 0x8000))!.valid == false)
precondition(Measurement.decode(packet(raw: 8_388_608)) == nil)
precondition(Measurement.decode(packet().dropLast()) == nil)
var wrongVersion = packet(); wrongVersion[0] = 2
precondition(Measurement.decode(wrongVersion) == nil)
precondition(Measurement.decode(packet(sequence: UInt32.max))!.id == UInt32.max)
print("Packet checks passed: signed raw values, units, status flags, length, version, sequence range")
var counter = RepetitionCounter()
func sample(_ ms: UInt32, _ status: UInt16 = 0, mode: UInt8 = 0) -> Measurement {
    Measurement(id: ms, milliseconds: ms, raw: 0, absoluteNewtons: 0, tareNewtons: 0, batteryMillivolts: 3900, status: status, mode: mode)
}
counter.receive(sample(0, 32)); precondition(counter.count == 0)
counter.receive(sample(40)); counter.receive(sample(80)); counter.receive(sample(120, 32))
counter.receive(sample(160, 32)); precondition(counter.count == 1)
counter.receive(sample(200)); counter.receive(sample(205, 32)); precondition(counter.count == 1)
counter.receive(sample(240)); counter.receive(sample(280)); counter.receive(sample(320, 32)); precondition(counter.count == 2)
counter.receive(sample(360)); counter.receive(sample(400)); counter.invalidate(); counter.receive(sample(440, 32)); precondition(counter.count == 2)
counter.receive(sample(480)); counter.receive(sample(520)); counter.receive(sample(560, 36)); precondition(counter.count == 2)
counter.receive(sample(600, mode: 1)); counter.receive(sample(640, 32, mode: 1)); precondition(counter.count == 2)
counter.reset(); precondition(counter.count == 0)
print("Counter checks passed: held switch, release debounce, gaps, faults, isometric mode, reset")
// Feedback observes live switch edges, never historical cumulative count deltas.
var clickTracker = EndstopFeedbackTracker()
func clickSample(_ sequence: UInt32, _ status: UInt16 = 0, boot: UInt32? = 1,
                 mode: UInt8 = 0, milliseconds: UInt32? = nil, total: UInt32 = 100) -> Measurement {
    var value = sample(milliseconds ?? sequence &* 40, status, mode: mode)
    value = Measurement(id: sequence, milliseconds: value.milliseconds, raw: value.raw,
        absoluteNewtons: value.absoluteNewtons, tareNewtons: value.tareNewtons,
        batteryMillivolts: value.batteryMillivolts, status: status, mode: mode)
    value.bootID = boot; value.deviceRepetitions = total
    return value
}
precondition(!clickTracker.receive(clickSample(0, 32))) // Connected while held.
precondition(!clickTracker.receive(clickSample(1)))
precondition(!clickTracker.receive(clickSample(2)))
precondition(clickTracker.receive(clickSample(3, 32)))
precondition(!clickTracker.receive(clickSample(3, 32))) // Duplicate.
precondition(!clickTracker.receive(clickSample(2))) // Out of order cannot rearm.
precondition(!clickTracker.receive(clickSample(4, 32))) // Held.
precondition(!clickTracker.receive(clickSample(5)))
precondition(!clickTracker.receive(clickSample(6, 32, milliseconds: 205))) // Short release/bounce.
precondition(!clickTracker.receive(clickSample(7)))
precondition(!clickTracker.receive(clickSample(8)))
precondition(!clickTracker.receive(clickSample(10, 32, total: 105))) // Gap: no catch-up clicks.
precondition(!clickTracker.receive(clickSample(11)))
precondition(!clickTracker.receive(clickSample(12)))
precondition(!clickTracker.receive(clickSample(13, 36))) // ADC fault disarms.
precondition(!clickTracker.receive(clickSample(14, 32)))
precondition(!clickTracker.receive(clickSample(15)))
precondition(!clickTracker.receive(clickSample(16)))
precondition(!clickTracker.receive(clickSample(17, 32, mode: 1))) // Isometry disarms.
precondition(!clickTracker.receive(clickSample(18, 32)))
precondition(!clickTracker.receive(clickSample(19)))
precondition(!clickTracker.receive(clickSample(20)))
precondition(!clickTracker.receive(clickSample(0, 32, boot: 2))) // Reboot while held.
precondition(!clickTracker.receive(clickSample(1, boot: 2)))
precondition(!clickTracker.receive(clickSample(2, boot: 2)))
clickTracker.clear() // Disconnect, stale/invalid data, or app becomes inactive.
precondition(!clickTracker.receive(clickSample(3, 32, boot: 2)))
precondition(!clickTracker.receive(clickSample(4, boot: 2)))
precondition(!clickTracker.receive(clickSample(5, boot: 2)))
precondition(clickTracker.receive(clickSample(6, 32, boot: 2)))
clickTracker.clear()
precondition(!clickTracker.receive(clickSample(UInt32.max - 1, boot: nil)))
precondition(!clickTracker.receive(clickSample(UInt32.max, boot: nil)))
precondition(clickTracker.receive(clickSample(0, 32, boot: nil))) // Legacy + sequence/time wrap.
print("End-stop feedback checks passed: one click per live edge, debounce, gaps, duplicates, faults, isometry, reboot, reset and wrap")
let firmwarePacket = try! Data(contentsOf: URL(fileURLWithPath: "/tmp/fingerworker-v2-packet.bin"))
let firmwareSample = Measurement.decode(firmwarePacket)!
precondition(firmwareSample.id == 42 && firmwareSample.raw == -123 && firmwareSample.force == 120)
precondition(firmwareSample.deviceRepetitions == 17 && firmwareSample.bootID == 0x12345678 && !firmwareSample.valid)
var deviceCounter = DeviceCounterTracker()
deviceCounter.receive(total: 10, bootID: 1); precondition(deviceCounter.displayed == 10)
deviceCounter.resetDisplay(); deviceCounter.receive(total: 13, bootID: 1); precondition(deviceCounter.displayed == 3)
deviceCounter.receive(total: 13, bootID: 1); precondition(deviceCounter.displayed == 3)
deviceCounter.receive(total: 12, bootID: 1); precondition(deviceCounter.displayed == 3)
deviceCounter.receive(total: 20, bootID: 1); precondition(deviceCounter.displayed == 10)
deviceCounter.receive(total: 0, bootID: 2); precondition(deviceCounter.displayed == 0)
deviceCounter.receive(total: 2, bootID: 2); precondition(deviceCounter.displayed == 2)
var wrapCounter = DeviceCounterTracker(); wrapCounter.receive(total: UInt32.max, bootID: 3); wrapCounter.resetDisplay(); wrapCounter.receive(total: 1, bootID: 3); precondition(wrapCounter.displayed == 2)
print("Firmware-to-app checks passed: v2 packet, missed packets/reconnect, app reset, device reboot, counter rollover")
let v3 = try! Data(contentsOf: URL(fileURLWithPath: "/tmp/fingerworker-v3-packet.bin"))
let peakSample = Measurement.decode(v3)!
precondition(peakSample.devicePeakMilliNewtons == 240000 && peakSample.peakEpoch == 789 && !peakSample.valid)
var peakTracker = DevicePeakTracker(); peakTracker.begin(789)
var oldPeak = peakSample; oldPeak.peakEpoch = 788; oldPeak.devicePeakMilliNewtons = 900000
precondition(!peakTracker.receive(oldPeak) && peakTracker.maximum == 0)
precondition(peakTracker.receive(peakSample) && peakTracker.maximum == 240)
var afterGap = peakSample; afterGap.devicePeakMilliNewtons = 300000
precondition(peakTracker.receive(afterGap) && peakTracker.maximum == 300)
precondition(peakTracker.receive(peakSample) && peakTracker.maximum == 300)
var reboot = peakSample; reboot.bootID = 99; reboot.peakEpoch = 0
precondition(!peakTracker.receive(reboot) && !peakTracker.acknowledged && peakTracker.maximum == 300)
peakTracker.begin(790); precondition(peakTracker.maximum == 0 && !peakTracker.receive(peakSample))
var badPeakFlags = v3; badPeakFlags[42] = 2
precondition(Measurement.decode(badPeakFlags) == nil)
var noPeak = v3; noPeak[42] = 0
precondition(Measurement.decode(noPeak)!.devicePeakMilliNewtons == nil)
precondition(Measurement.decode(v3.dropLast()) == nil)
let archiveURL = FileManager.default.temporaryDirectory.appendingPathComponent("fingerworker-session-tests-" + UUID().uuidString)
let archive = SessionArchive(directory: archiveURL)
var saved = RecordedSession(source: "device", samples: [peakSample], repetitions: [7], peak: 240, interrupted: true)
try! archive.save(saved)
let restored = try! archive.load()[0]
precondition(restored.id == saved.id && restored.samples[0].peakEpoch == 789 && restored.peak == 240 && restored.interrupted)
precondition(restored.csv.contains("240000,789"))
saved.samples.append(valid); saved.repetitions.append(8); try! archive.save(saved)
precondition(try! archive.load().count == 1)
precondition(try! archive.load()[0].samples.count == 2)
saved.repetitions = []
do { try archive.save(saved); preconditionFailure("Mismatched session accepted") } catch {}
try! FileManager.default.removeItem(at: archiveURL)
print("V3 peak and persistence checks passed: cumulative peak, epoch, flags, atomic save/load/update and CSV")

// Rest must include the other hand's work time, rather than adding a full rest
// after both hands. Run the workout at deterministic timestamps.
let start = Date(timeIntervalSince1970: 1_700_000_000)
var trainingSettings = TrainingSettings()
precondition(trainingSettings.countingMode == .device && trainingSettings.setsPerHand == 6)
trainingSettings.repetitionsPerSet = 2
trainingSettings.setsPerHand = 2
trainingSettings.preparationSeconds = 5
var workout = TrainingSession(settings: trainingSettings, source: "device", now: start)
precondition(workout.phase == .preparing && workout.activeHand == .left)
workout.addRepetitions(20, at: start.addingTimeInterval(4))
precondition(workout.currentRepetitions == 0)
workout.tick(at: start.addingTimeInterval(5))
workout.record(force: 100)
workout.record(force: .nan)
workout.addRepetitions(at: start.addingTimeInterval(6))
precondition(workout.currentRepetitions == 1 && workout.results.isEmpty)
workout.addRepetitions(7, at: start.addingTimeInterval(7))
precondition(workout.results.count == 1 && workout.results[0].repetitions == 2 && workout.results[0].peakNewtons == 100)
precondition(workout.phase == .preparing && workout.activeHand == .right && workout.currentRepetitions == 0)
precondition(workout.leftReadyAt == start.addingTimeInterval(187))
workout.tick(at: start.addingTimeInterval(12))
workout.addRepetitions(2, at: start.addingTimeInterval(14))
precondition(workout.phase == .resting && workout.activeHand == .left)
precondition(workout.remaining(at: start.addingTimeInterval(14)) == 173)
workout.addRepetitions(20, at: start.addingTimeInterval(50))
workout.tick(at: start.addingTimeInterval(186))
precondition(workout.phase == .resting && workout.currentRepetitions == 0)
workout.tick(at: start.addingTimeInterval(187))
precondition(workout.phase == .working && workout.currentSetNumber == 2)
workout.addRepetitions(2, at: start.addingTimeInterval(189))
precondition(workout.activeHand == .right && workout.remaining(at: start.addingTimeInterval(189)) == 5)
workout.tick(at: start.addingTimeInterval(194))
workout.addRepetitions(2, at: start.addingTimeInterval(196))
precondition(workout.phase == .completed && workout.totalRepetitions == 8 && workout.progress == 1)
precondition(workout.completedSets(for: .left) == 2 && workout.completedSets(for: .right) == 2)
precondition(workout.deadline == nil && workout.elapsed(at: start.addingTimeInterval(400)) == 196)
workout.addRepetitions(at: start.addingTimeInterval(200))
precondition(workout.totalRepetitions == 8)
print("Training sequence checks passed: preparation, hand changes, independent rest, batch overflow and completion without final rest")

var shortSettings = trainingSettings
shortSettings.startingHand = .right; shortSettings.preparationSeconds = 0; shortSettings.restSeconds = 0
shortSettings.setsPerHand = 1; shortSettings.repetitionsPerSet = 3
var pausedWorkout = TrainingSession(settings: shortSettings, source: "device", now: start)
precondition(pausedWorkout.phase == .working && pausedWorkout.activeHand == .right)
pausedWorkout.addRepetitions(at: start.addingTimeInterval(1))
pausedWorkout.pause(at: start.addingTimeInterval(2), reason: "Lost connection")
pausedWorkout.addRepetitions(2, at: start.addingTimeInterval(20))
pausedWorkout.tick(at: start.addingTimeInterval(20))
precondition(pausedWorkout.phase == .paused && pausedWorkout.currentRepetitions == 1)
precondition(pausedWorkout.elapsed(at: start.addingTimeInterval(40)) == 2)
pausedWorkout.resume(at: start.addingTimeInterval(102))
pausedWorkout.addRepetitions(2, at: start.addingTimeInterval(103))
precondition(pausedWorkout.phase == .working && pausedWorkout.activeHand == .left)
precondition(pausedWorkout.results[0].durationSeconds == 3)
pausedWorkout.addRepetitions(at: start.addingTimeInterval(104))
pausedWorkout.undoRepetition(at: start.addingTimeInterval(105))
precondition(pausedWorkout.currentRepetitions == 0)
pausedWorkout.addRepetitions(2, at: start.addingTimeInterval(106))
pausedWorkout.pause(at: start.addingTimeInterval(107))
pausedWorkout.cancel(at: start.addingTimeInterval(207))
precondition(pausedWorkout.phase == .cancelled && pausedWorkout.totalRepetitions == 5)
precondition(pausedWorkout.results.count == 2 && !pausedWorkout.results[1].completed)
precondition(pausedWorkout.elapsed(at: start.addingTimeInterval(300)) == 7)

var restPause = TrainingSession(settings: trainingSettings, source: "device", now: start)
restPause.tick(at: start.addingTimeInterval(5)); restPause.addRepetitions(2, at: start.addingTimeInterval(7))
restPause.tick(at: start.addingTimeInterval(12)); restPause.addRepetitions(2, at: start.addingTimeInterval(14))
restPause.pause(at: start.addingTimeInterval(20))
precondition(restPause.remaining(at: start.addingTimeInterval(100)) == 167)
restPause.resume(at: start.addingTimeInterval(120))
precondition(restPause.remaining(at: start.addingTimeInterval(120)) == 167)
restPause.tick(at: start.addingTimeInterval(286)); precondition(restPause.phase == .resting)
restPause.tick(at: start.addingTimeInterval(287)); precondition(restPause.phase == .working)
print("Training interruption checks passed: pause ignores movements, frozen rest, resumed set duration, right-hand start and partial-set archive")

func trainingSample(sequence: UInt32 = 1, milliseconds: UInt32 = 0, total: UInt32? = nil, boot: UInt32? = nil, status: UInt16 = 0, mode: UInt8 = 0) -> Measurement {
    Measurement(id: sequence, milliseconds: milliseconds, raw: 0, absoluteNewtons: 80, tareNewtons: 0,
                batteryMillivolts: 3900, status: status, mode: mode, deviceRepetitions: total, bootID: boot)
}
var trainingCounter = TrainingRepetitionTracker()
precondition(trainingCounter.receive(trainingSample(total: 100, boot: 1)) == 0)
precondition(trainingCounter.receive(trainingSample(sequence: 3, total: 103, boot: 1, status: 32)) == 3)
precondition(trainingCounter.receive(trainingSample(sequence: 4, total: 103, boot: 1)) == 0)
precondition(trainingCounter.receive(trainingSample(sequence: 5, total: 102, boot: 1)) == 0)
precondition(trainingCounter.receive(trainingSample(sequence: 6, total: 104, boot: 1)) == 1)
precondition(trainingCounter.receive(trainingSample(sequence: 1, total: 0, boot: 2)) == 0 && trainingCounter.rebooted)
precondition(trainingCounter.receive(trainingSample(sequence: 2, total: 1, boot: 2)) == 1 && !trainingCounter.rebooted)
precondition(trainingCounter.receive(trainingSample(sequence: 3, total: 2, boot: 2, status: 4)) == 0)
precondition(trainingCounter.receive(trainingSample(sequence: 4, total: 3, boot: 2)) == 0)
trainingCounter.clear()
precondition(trainingCounter.receive(trainingSample(total: 900, boot: 2)) == 0)
precondition(trainingCounter.receive(trainingSample(sequence: 2, total: 901, boot: 2)) == 1)
trainingCounter.clear()
precondition(trainingCounter.receive(trainingSample(total: UInt32.max, boot: 3)) == 0)
precondition(trainingCounter.receive(trainingSample(sequence: 2, total: 1, boot: 3)) == 2)
trainingCounter.clear()
precondition(trainingCounter.receive(trainingSample(sequence: 1, milliseconds: 0, status: 32)) == 0)
precondition(trainingCounter.receive(trainingSample(sequence: 2, milliseconds: 40)) == 0)
precondition(trainingCounter.receive(trainingSample(sequence: 3, milliseconds: 80)) == 0)
precondition(trainingCounter.receive(trainingSample(sequence: 4, milliseconds: 120, status: 32)) == 1)
precondition(trainingCounter.receive(trainingSample(sequence: 5, milliseconds: 160)) == 0)
precondition(trainingCounter.receive(trainingSample(sequence: 6, milliseconds: 200)) == 0)
precondition(trainingCounter.receive(trainingSample(sequence: 8, milliseconds: 280, status: 32)) == 0)
precondition(trainingCounter.receive(trainingSample(sequence: 9, milliseconds: 320)) == 0)
precondition(trainingCounter.receive(trainingSample(sequence: 10, milliseconds: 360)) == 0)
precondition(trainingCounter.receive(trainingSample(sequence: 10, milliseconds: 360, status: 32)) == 0)
precondition(trainingCounter.receive(trainingSample(sequence: 11, milliseconds: 400, status: 32)) == 1)
precondition(trainingCounter.receive(trainingSample(sequence: 12, milliseconds: 440, status: 32, mode: 1)) == 0)
print("Training BLE counter checks passed: cumulative counts, missed packets, duplicates, reboot, faults, rebase, rollover and legacy edge gaps")

var invalidSettings = TrainingSettings()
invalidSettings.repetitionsPerSet = -3; invalidSettings.setsPerHand = 99; invalidSettings.restSeconds = -15
invalidSettings.preparationSeconds = 999; invalidSettings.pullSeconds = .infinity; invalidSettings.releaseSeconds = -1
let normalized = invalidSettings.normalized
precondition(normalized.repetitionsPerSet == 1 && normalized.setsPerHand == 12 && normalized.restSeconds == 0)
precondition(normalized.preparationSeconds == 15 && normalized.pullSeconds == 1 && normalized.releaseSeconds == 0.5)
precondition(TrainingSettings.clock(179.1) == "3:00" && TrainingSettings.clock(-1) == "0:00")
let trainingArchiveURL = FileManager.default.temporaryDirectory.appendingPathComponent("fingerworker-training-tests-" + UUID().uuidString)
let trainingArchive = TrainingArchive(directory: trainingArchiveURL)
try! trainingArchive.save(workout); try! trainingArchive.save(pausedWorkout); try! trainingArchive.save(restPause)
let restoredWorkouts = try! trainingArchive.load()
precondition(restoredWorkouts.count == 3)
precondition(restoredWorkouts.first(where: { $0.id == workout.id })!.totalRepetitions == 8)
var recovered = restoredWorkouts.first(where: { $0.id == restPause.id })!
recovered.pause(at: recovered.updatedAt, reason: "Restored")
precondition(recovered.phase == .paused && recovered.activeHand == .left && recovered.settings.restSeconds == 180)
try! trainingArchive.save(recovered)
precondition(try! trainingArchive.load().count == 3)
recovered.settings.repetitionsPerSet = 0
do { try trainingArchive.save(recovered); preconditionFailure("Invalid training settings accepted") } catch {}
var duplicateSet = workout; duplicateSet.results[1] = duplicateSet.results[0]
do { try trainingArchive.save(duplicateSet); preconditionFailure("Duplicate training set accepted") } catch {}
let defaults = UserDefaults(suiteName: "fingerworker-settings-test-" + UUID().uuidString)!
defaults.set(try! JSONEncoder().encode(trainingSettings), forKey: "settings")
precondition(try! JSONDecoder().decode(TrainingSettings.self, from: defaults.data(forKey: "settings")!) == trainingSettings)
defaults.removeObject(forKey: "settings")
var legacySessionJSON = try! JSONSerialization.jsonObject(with: JSONEncoder().encode(restored)) as! [String: Any]
legacySessionJSON.removeValue(forKey: "workoutID")
let legacySession = try! JSONDecoder().decode(RecordedSession.self, from: JSONSerialization.data(withJSONObject: legacySessionJSON))
precondition(legacySession.workoutID == nil && legacySession.samples.count == 1)
let linkedSession = RecordedSession(source: "device", workoutID: workout.id)
precondition(try! JSONDecoder().decode(RecordedSession.self, from: JSONEncoder().encode(linkedSession)).workoutID == workout.id)
try! FileManager.default.removeItem(at: trainingArchiveURL)
print("Training persistence checks passed: settings bounds, autosave/update/restore, corrupt state rejection and legacy recording compatibility")

// The log records accepted counts at receipt time; it must not invent timing
// for the seven device counts of which only one still fitted the first set.
let workoutEvents = workout.log!.events
precondition(workout.log!.hasCompleteTimeline && workoutEvents.first!.kind == .started)
precondition(workoutEvents.last!.kind == .completed)
let countEvents = workoutEvents.filter { $0.kind == .repetitionsAdded }
precondition(countEvents.compactMap(\.delta) == [1, 1, 2, 2, 2])
precondition(countEvents[1].date == start.addingTimeInterval(7) && countEvents[1].repetitions == 2)
precondition(workoutEvents.filter { $0.kind == .setFinished }.compactMap(\.setNumber) == [1, 1, 2, 2])
precondition(workoutEvents.filter { $0.kind == .restStarted }.compactMap(\.durationSeconds) == [173, 5])
precondition(workout.results[0].restBeforeSeconds == nil && workout.results[1].restBeforeSeconds == nil)
precondition(workout.results[2].restBeforeSeconds == 180 && workout.results[3].restBeforeSeconds == 180)
precondition(restPause.log!.events.last!.kind == .setStarted && restPause.log!.events.last!.durationSeconds == 180)
let pausedEvents = pausedWorkout.log!.events
precondition(pausedEvents.filter { $0.kind == .paused }.count == 2)
precondition(pausedEvents.filter { $0.kind == .resumed }.count == 1)
precondition(pausedEvents.first(where: { $0.kind == .paused })!.reason == "Lost connection")
precondition(pausedEvents.last!.kind == .cancelled && pausedWorkout.pausedSeconds == 200)
precondition(pausedWorkout.log!.interruptionSeconds(from: start, to: start.addingTimeInterval(207)) == 200)
precondition(pausedEvents.compactMap(\.delta).reduce(0, +) == pausedWorkout.totalRepetitions)

var annotated = workout
annotated.log!.notes = "Widerstand: mittel, Griff \"offen\"\nNoch Reserven – links besser."
annotated.log!.perceivedExertion = 7
let logArchiveURL = FileManager.default.temporaryDirectory.appendingPathComponent("fingerworker-log-tests-" + UUID().uuidString)
let logArchive = TrainingArchive(directory: logArchiveURL)
try! logArchive.save(annotated)
let restoredLog = try! logArchive.load()[0]
precondition(restoredLog.log!.notes == annotated.log!.notes && restoredLog.log!.perceivedExertion == 7)
precondition(restoredLog.log!.events.map(\.id) == annotated.log!.events.map(\.id))
precondition(restoredLog.results[2].restBeforeSeconds == 180)
var badLog = annotated; badLog.log!.perceivedExertion = 11
do { try logArchive.save(badLog); preconditionFailure("Invalid exertion accepted") } catch {}
badLog = annotated; badLog.log!.events.append(badLog.log!.events[0])
do { try logArchive.save(badLog); preconditionFailure("Duplicate log event accepted") } catch {}
badLog = annotated; badLog.log!.events[0].durationSeconds = -1
do { try logArchive.save(badLog); preconditionFailure("Invalid log duration accepted") } catch {}

var legacyWorkoutJSON = try! JSONSerialization.jsonObject(with: JSONEncoder().encode(annotated)) as! [String: Any]
legacyWorkoutJSON.removeValue(forKey: "log")
legacyWorkoutJSON["results"] = (legacyWorkoutJSON["results"] as! [[String: Any]]).map { result in
    var legacy = result; legacy.removeValue(forKey: "restBeforeSeconds"); return legacy
}
let legacyWorkout = try! JSONDecoder().decode(TrainingSession.self, from: JSONSerialization.data(withJSONObject: legacyWorkoutJSON))
precondition(legacyWorkout.log == nil && legacyWorkout.totalRepetitions == 8 && legacyWorkout.results[2].restBeforeSeconds == nil)
try! logArchive.save(legacyWorkout)
precondition(try! logArchive.load()[0].log == nil)

// Parse the exported file independently, including escaped quotes and embedded
// newlines, to check both one-workout and complete-history export shapes.
func csvRows(_ csv: String) -> [[String]] {
    let characters = Array(csv)
    var result: [[String]] = [], row: [String] = [], cell = "", quoted = false, index = 0
    while index < characters.count {
        let character = characters[index]
        if character == "\"" {
            if quoted && index + 1 < characters.count && characters[index + 1] == "\"" { cell.append("\""); index += 1 }
            else { quoted.toggle() }
        } else if character == "," && !quoted { row.append(cell); cell = "" }
        else if (character == "\r" || character == "\r\n") && !quoted {
            row.append(cell); result.append(row); row = []; cell = ""
            if index + 1 < characters.count && characters[index + 1] == "\n" { index += 1 }
        } else { cell.append(character) }
        index += 1
    }
    precondition(!quoted && row.isEmpty && cell.isEmpty)
    return result
}
let csv = TrainingLogCSV.make(sessions: [annotated], now: start.addingTimeInterval(500))
let rows = csvRows(csv)
precondition(rows[0] == TrainingLogCSV.columns && rows.allSatisfy { $0.count == rows[0].count })
func column(_ name: String) -> Int { TrainingLogCSV.columns.firstIndex(of: name)! }
precondition(rows[1][column("notes")] == annotated.log!.notes && rows[1][column("perceived_exertion_1_to_10")] == "7")
precondition(rows[1][column("started_at")] == "2023-11-14T22:13:20.000Z")
precondition(rows[1][column("rest_seconds")] == "180" && rows[1][column("active_seconds")] == "196.000")
precondition(rows.filter { $0[column("row_type")] == "set" }.count == 4)
precondition(rows.filter { $0[column("row_type")] == "event" }.count == workoutEvents.count)
precondition(rows.dropFirst().allSatisfy { $0[column("workout_id")] == annotated.id.uuidString })
let allRows = csvRows(TrainingLogCSV.make(sessions: [annotated, pausedWorkout], now: start.addingTimeInterval(500)))
precondition(allRows.filter { $0[column("row_type")] == "session" }.count == 2)
let stoppedRow = allRows.first { $0[column("row_type")] == "session" && $0[column("workout_id")] == pausedWorkout.id.uuidString }!
precondition(stoppedRow[column("active_seconds")] == "7.000" && stoppedRow[column("interruption_seconds")] == "200.000")
var formulaNote = annotated; formulaNote.log!.notes = "=1+1"
precondition(csvRows(TrainingLogCSV.make(sessions: [formulaNote], now: start))[1][column("notes")] == "'=1+1")
let legacyRows = csvRows(TrainingLogCSV.make(sessions: [legacyWorkout], now: start))
precondition(legacyRows[1][column("complete_timeline")] == "false" && legacyRows.count == 6)
try! FileManager.default.removeItem(at: logArchiveURL)
print("Training log checks passed: receipt batches, set/rest timing, interruptions, undo, notes/exertion, persistence, legacy workouts and rectangular CSV export")

// Timed cARC never uses end-stop counts or interprets cadence as movement.
var carcSettings = TrainingSettings()
carcSettings.mode = .carc
precondition(carcSettings.isCARC && !carcSettings.usesDeviceCounter && carcSettings.usesCadence)
precondition(carcSettings.setsPerHand == 1 && carcSettings.restSeconds == 0)
carcSettings.carc!.durationSeconds = 60
carcSettings.preparationSeconds = 5
var carcWorkout = TrainingSession(settings: carcSettings, source: "timer", now: start)
carcWorkout.tick(at: start.addingTimeInterval(5))
carcWorkout.addRepetitions(50, at: start.addingTimeInterval(10))
precondition(carcWorkout.currentRepetitions == 0 && carcWorkout.results.isEmpty)
precondition(carcWorkout.remaining(at: start.addingTimeInterval(15)) == 50)
precondition(carcWorkout.workSeconds(at: start.addingTimeInterval(15)) == 10)
precondition(carcWorkout.progress(at: start.addingTimeInterval(15)) == 10.0 / 120)
carcWorkout.pause(at: start.addingTimeInterval(15), reason: "Background")
precondition(carcWorkout.remaining(at: start.addingTimeInterval(100)) == 50)
precondition(carcWorkout.workSeconds(at: start.addingTimeInterval(100)) == 10)
precondition(carcWorkout.isPulling(at: start.addingTimeInterval(100)) == carcWorkout.isPulling(at: start.addingTimeInterval(15)))
carcWorkout.resume(at: start.addingTimeInterval(115))
carcWorkout.tick(at: start.addingTimeInterval(164))
precondition(carcWorkout.phase == .working && carcWorkout.activeHand == .left)
carcWorkout.tick(at: start.addingTimeInterval(165))
precondition(carcWorkout.results[0].durationSeconds == 60 && carcWorkout.results[0].repetitions == 0)
precondition(carcWorkout.activeHand == .right && carcWorkout.phase == .preparing)
carcWorkout.tick(at: start.addingTimeInterval(170))
carcWorkout.tick(at: start.addingTimeInterval(230))
precondition(carcWorkout.phase == .completed && carcWorkout.totalRepetitions == 0)
precondition(carcWorkout.workSeconds(at: start.addingTimeInterval(1000)) == 120 && carcWorkout.progress == 1)
precondition(!carcWorkout.hasForceSamples && carcWorkout.elapsed(at: start) == 130)
precondition(carcWorkout.log!.events.allSatisfy { $0.repetitions == nil && $0.delta == nil })

// A delayed tick credits only the current block; no unseen work for the other hand.
var immediateCARC = carcSettings
immediateCARC.preparationSeconds = 0
var lateCARC = TrainingSession(settings: immediateCARC, source: "timer", now: start)
lateCARC.tick(at: start.addingTimeInterval(500))
precondition(lateCARC.results.count == 1 && lateCARC.results[0].durationSeconds == 60)
precondition(lateCARC.phase == .working && lateCARC.activeHand == .right)
precondition(lateCARC.remaining(at: start.addingTimeInterval(500)) == 60)
precondition(lateCARC.workSeconds(at: start.addingTimeInterval(500)) == 60)
lateCARC.tick(at: start.addingTimeInterval(560))
precondition(lateCARC.phase == .completed)

var partialCARC = TrainingSession(settings: immediateCARC, source: "timer", now: start)
partialCARC.record(force: 35)
partialCARC.pause(at: start.addingTimeInterval(12))
partialCARC.cancel(at: start.addingTimeInterval(112))
precondition(partialCARC.results.count == 1 && !partialCARC.results[0].completed)
precondition(partialCARC.results[0].durationSeconds == 12 && partialCARC.results[0].repetitions == 0)
precondition(partialCARC.results[0].forceSampleCount == 1 && partialCARC.hasForceSamples)
precondition(partialCARC.workSeconds(at: start.addingTimeInterval(1000)) == 12)
precondition(partialCARC.elapsed(at: start) == 12 && partialCARC.pausedSeconds == 100)

var forceSettings = CARCSettings()
precondition(forceSettings.displayedForce(from: trainingSample()) == nil)
forceSettings.showForce = true
precondition(forceSettings.displayedForce(from: trainingSample()) == 80)
for flag: UInt16 in [1, 4, 16, 32, 128] {
    precondition(forceSettings.displayedForce(from: trainingSample(status: flag)) == nil)
}
precondition(forceSettings.displayedForce(from: nil) == nil)
precondition(forceSettings.displayedForce(from: trainingSample(mode: 1)) == nil)
forceSettings.durationSeconds = -1; forceSettings.forceCeilingNewtons = .nan
precondition(forceSettings.normalized.durationSeconds == 60 && forceSettings.normalized.forceCeilingNewtons == 50)

let carcArchiveURL = FileManager.default.temporaryDirectory.appendingPathComponent("fingerworker-carc-tests-" + UUID().uuidString)
let carcArchive = TrainingArchive(directory: carcArchiveURL)
try! carcArchive.save(carcWorkout); try! carcArchive.save(partialCARC)
let savedCARC = try! carcArchive.load()
precondition(savedCARC.count == 2 && savedCARC.allSatisfy { $0.settings.isCARC })
precondition(savedCARC.first(where: { $0.id == partialCARC.id })!.results[0].durationSeconds == 12)
var corruptCARC = carcWorkout
corruptCARC.results[0].durationSeconds = 59
do { try carcArchive.save(corruptCARC); preconditionFailure("Incomplete cARC block marked complete") } catch {}
corruptCARC = carcWorkout; corruptCARC.currentRepetitions = 1
do { try carcArchive.save(corruptCARC); preconditionFailure("Invented cARC repetitions accepted") } catch {}
var legacySettingsJSON = try! JSONSerialization.jsonObject(with: JSONEncoder().encode(trainingSettings)) as! [String: Any]
legacySettingsJSON.removeValue(forKey: "carc")
let legacySettings = try! JSONDecoder().decode(TrainingSettings.self, from: JSONSerialization.data(withJSONObject: legacySettingsJSON))
precondition(!legacySettings.isCARC && legacySettings == trainingSettings)
let carcRows = csvRows(TrainingLogCSV.make(sessions: [carcWorkout, partialCARC], now: start))
precondition(carcRows.allSatisfy { $0.count == TrainingLogCSV.columns.count })
let completeCARCRow = carcRows.first { $0[column("row_type")] == "session" && $0[column("workout_id")] == carcWorkout.id.uuidString }!
precondition(completeCARCRow[column("training_mode")] == "carc" && completeCARCRow[column("counting_mode")] == "timer")
precondition(completeCARCRow[column("work_seconds")] == "120.000" && completeCARCRow[column("total_repetitions")].isEmpty)
precondition(completeCARCRow[column("peak_newtons")].isEmpty)
let partialCARCRow = carcRows.first { $0[column("row_type")] == "session" && $0[column("workout_id")] == partialCARC.id.uuidString }!
precondition(partialCARCRow[column("work_seconds")] == "12.000" && partialCARCRow[column("force_sample_count")] == "1")
try! FileManager.default.removeItem(at: carcArchiveURL)
print("cARC checks passed: timed blocks, no invented counts, pause/resume, delayed ticks, partial sessions, force validity, legacy settings, archive validation and CSV")

// Relaunch recovery must preserve the current block, not consume wall-clock downtime.
var recoverCARC = TrainingSession(settings: immediateCARC, source: "timer", now: start)
recoverCARC.tick(at: start.addingTimeInterval(20))
recoverCARC.pause(at: start.addingTimeInterval(20), reason: "Restored")
recoverCARC = try! JSONDecoder().decode(TrainingSession.self, from: JSONEncoder().encode(recoverCARC))
recoverCARC.resume(at: start.addingTimeInterval(86420))
precondition(recoverCARC.remaining(at: start.addingTimeInterval(86420)) == 40)
recoverCARC.tick(at: start.addingTimeInterval(86460))
precondition(recoverCARC.results[0].durationSeconds == 60 && recoverCARC.activeHand == .right)
recoverCARC.pause(at: start.addingTimeInterval(86520))
precondition(recoverCARC.phase == .completed && recoverCARC.workSeconds(at: start) == 120)
print("cARC recovery checks passed: Codable checkpoint, overnight resume and completion at pause boundary")
