import Foundation

enum TrainingEventKind: String, Codable {
    case started, preparationStarted, setStarted, repetitionsAdded, repetitionRemoved
    case setFinished, restStarted, paused, resumed, completed, cancelled

    var title: String {
        switch self {
        case .started: return "Training gestartet"
        case .preparationStarted: return "Vorlauf / Handwechsel"
        case .setStarted: return "Satz gestartet"
        case .repetitionsAdded: return "Züge erfasst"
        case .repetitionRemoved: return "Zug zurückgenommen"
        case .setFinished: return "Satz beendet"
        case .restStarted: return "Erholung"
        case .paused: return "Training pausiert"
        case .resumed: return "Training fortgesetzt"
        case .completed: return "Training abgeschlossen"
        case .cancelled: return "Training vorzeitig beendet"
        }
    }
    var symbol: String {
        switch self {
        case .started, .resumed, .setStarted: return "play.circle"
        case .repetitionsAdded: return "plus.circle"
        case .repetitionRemoved: return "minus.circle"
        case .preparationStarted, .restStarted: return "hourglass"
        case .setFinished, .completed: return "checkmark.circle"
        case .paused: return "pause.circle"
        case .cancelled: return "stop.circle"
        }
    }
}

/// A receipt timestamp, not a reconstruction of movement between BLE packets.
/// A cumulative device count may produce one event for several repetitions.
struct TrainingEvent: Codable, Identifiable {
    var id = UUID()
    var date: Date
    var kind: TrainingEventKind
    var hand: TrainingHand?
    var setNumber: Int?
    var repetitions: Int?
    var delta: Int?
    var durationSeconds: TimeInterval?
    var reason: String?
}

struct TrainingLog: Codable {
    var events: [TrainingEvent] = []
    var notes = ""
    var perceivedExertion: Int?
    var hasCompleteTimeline: Bool { events.first?.kind == .started }

    func interruptionSeconds(from start: Date, to end: Date) -> TimeInterval {
        var pausedAt: Date?
        var total: TimeInterval = 0
        for event in events {
            if event.kind == .paused { pausedAt = event.date }
            if event.kind == .resumed || event.kind == .cancelled || event.kind == .completed,
               let pause = pausedAt {
                total += max(0, min(end, event.date).timeIntervalSince(max(start, pause)))
                pausedAt = nil
            }
        }
        if let pause = pausedAt { total += max(0, end.timeIntervalSince(max(start, pause))) }
        return total
    }
}

/// A rectangular CSV: session rows contain the original settings and totals;
/// set and event rows link to that session by workout_id. Dates are UTC ISO 8601.
enum TrainingLogCSV {
    static let columns = [
        "schema_version", "row_type", "workout_id", "timestamp", "started_at", "ended_at", "source", "phase",
        "repetitions_per_set", "sets_per_hand", "rest_seconds", "starting_hand", "counting_mode", "preparation_seconds",
        "cadence_enabled", "pull_seconds", "release_seconds", "sound_enabled", "haptics_enabled",
        "total_repetitions", "completed_sets", "active_seconds", "interruption_seconds", "peak_newtons",
        "perceived_exertion_1_to_10", "notes", "complete_timeline", "event_id", "event_type", "hand", "set_number",
        "repetitions", "delta", "set_completed", "duration_seconds", "rest_before_seconds", "reason",
        "training_mode", "block_duration_seconds", "work_seconds", "force_feedback_enabled", "force_ceiling_newtons", "force_sample_count"
    ]

    static func make(sessions: [TrainingSession], now: Date) -> String {
        let date = ISO8601DateFormatter()
        date.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
        var rows = [columns.joined(separator: ",")]
        func number(_ value: Double) -> String {
            String(format: "%.3f", locale: Locale(identifier: "en_US_POSIX"), value)
        }
        func append(_ fields: [String: String], session: TrainingSession, type: String) {
            var row = fields
            row["schema_version"] = "2"; row["row_type"] = type; row["workout_id"] = session.id.uuidString
            rows.append(columns.map { column in
                var value = row[column] ?? ""
                // Notes and reasons stay text when opened in a spreadsheet.
                if (column == "notes" || column == "reason"), let first = value.first, "=+-@".contains(first) {
                    value = "'" + value
                }
                return "\"" + value.replacingOccurrences(of: "\"", with: "\"\"") + "\""
            }.joined(separator: ","))
        }
        for session in sessions.sorted(by: { $0.startedAt > $1.startedAt }) {
            let s = session.settings
            let end = session.endedAt ?? (session.phase == .paused ? session.pausedAt : nil) ?? now
            let interruptions = session.pausedSeconds + (session.phase == .paused ? max(0, now.timeIntervalSince(session.pausedAt ?? now)) : 0)
            append([
                "timestamp": date.string(from: session.startedAt), "started_at": date.string(from: session.startedAt),
                "ended_at": session.endedAt.map(date.string(from:)) ?? "", "source": session.source, "phase": session.phase.rawValue,
                "repetitions_per_set": s.isCARC ? "" : String(s.repetitionsPerSet), "sets_per_hand": String(s.setsPerHand),
                "rest_seconds": String(s.restSeconds), "starting_hand": s.startingHand.rawValue, "counting_mode": s.isCARC ? "timer" : s.countingMode.rawValue,
                "preparation_seconds": String(s.preparationSeconds), "cadence_enabled": String(s.usesCadence),
                "pull_seconds": number(s.pullSeconds), "release_seconds": number(s.releaseSeconds),
                "sound_enabled": String(s.soundEnabled), "haptics_enabled": String(s.hapticsEnabled),
                "total_repetitions": s.isCARC ? "" : String(session.totalRepetitions), "completed_sets": String(session.completedSets),
                "active_seconds": number(session.elapsed(at: end)), "interruption_seconds": number(interruptions),
                "peak_newtons": session.hasForceSamples ? number(session.peakNewtons) : "", "perceived_exertion_1_to_10": session.log?.perceivedExertion.map(String.init) ?? "",
                "notes": session.log?.notes ?? "", "complete_timeline": String(session.log?.hasCompleteTimeline == true),
                "training_mode": s.mode.rawValue,
                "block_duration_seconds": s.carc.map { String($0.durationSeconds) } ?? "",
                "work_seconds": number(session.workSeconds(at: end)),
                "force_feedback_enabled": String(s.carc?.showForce == true),
                "force_ceiling_newtons": s.carc?.showForce == true ? number(s.carc!.forceCeilingNewtons) : "",
                "force_sample_count": session.currentForceSampleCount.map { String($0 + session.results.reduce(0) { $0 + ($1.forceSampleCount ?? 0) }) } ?? ""
            ], session: session, type: "session")
            for set in session.results {
                append([
                    "timestamp": date.string(from: set.endedAt), "hand": set.hand.rawValue, "set_number": String(set.number),
                    "repetitions": s.isCARC ? "" : String(set.repetitions), "set_completed": String(set.completed),
                    "duration_seconds": number(set.durationSeconds), "rest_before_seconds": set.restBeforeSeconds.map(number) ?? "",
                    "peak_newtons": set.forceSampleCount == 0 ? "" : number(set.peakNewtons),
                    "force_sample_count": set.forceSampleCount.map(String.init) ?? ""
                ], session: session, type: "set")
            }
            for event in session.log?.events ?? [] {
                append([
                    "timestamp": date.string(from: event.date), "event_id": event.id.uuidString, "event_type": event.kind.rawValue,
                    "hand": event.hand?.rawValue ?? "", "set_number": event.setNumber.map(String.init) ?? "",
                    "repetitions": event.repetitions.map(String.init) ?? "", "delta": event.delta.map(String.init) ?? "",
                    "duration_seconds": event.durationSeconds.map(number) ?? "", "reason": event.reason ?? ""
                ], session: session, type: "event")
            }
        }
        return rows.joined(separator: "\r\n") + "\r\n"
    }
}
