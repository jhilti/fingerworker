import SwiftUI

struct TrainingHomeView: View {
    @ObservedObject var training: TrainingStore
    @ObservedObject var device: DeviceStore
    @State private var showingSettings = false
    @State private var confirmingStop = false

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 20) {
                    connectionCard
                    if let workout = training.workout {
                        if workout.phase.isFinished {
                            TrainingSummaryView(workout: workout, now: training.now)
                            NavigationLink {
                                TrainingLogDetailView(training: training, workoutID: workout.id)
                            } label: {
                                Label("Eintrag im Log", systemImage: "list.bullet.rectangle")
                                    .frame(maxWidth: .infinity).padding(.vertical, 9)
                            }.buttonStyle(.bordered).accessibilityIdentifier("training.openLog")
                            Button { training.newWorkout() } label: {
                                Label("Neues Training", systemImage: "arrow.clockwise")
                                    .frame(maxWidth: .infinity).padding(.vertical, 9)
                            }.buttonStyle(.borderedProminent)
                        } else {
                            workoutCard(workout)
                            handsCard(workout)
                            workoutControls(workout)
                        }
                    } else {
                        planCard
                        Button { training.start() } label: {
                            Label("Training starten", systemImage: "play.fill")
                                .font(.headline).frame(maxWidth: .infinity).padding(.vertical, 10)
                        }.buttonStyle(.borderedProminent).disabled(!training.canStart)
                            .accessibilityIdentifier("training.start")
                        if let hint = training.startHint {
                            Text(hint).font(.subheadline).foregroundStyle(.secondary)
                        }
                    }
                    if let error = training.storageError {
                        Label(error, systemImage: "exclamationmark.triangle.fill").foregroundStyle(.red)
                    }
                }.padding(20)
            }.background(Color(.systemGroupedBackground))
                .navigationTitle("Fingerworker")
                .toolbar {
                    ToolbarItem(placement: .topBarTrailing) {
                        Button { showingSettings = true } label: { Image(systemName: "slider.horizontal.3") }
                            .accessibilityLabel("Trainingseinstellungen")
                            .accessibilityIdentifier("training.settings")
                    }
                }
                .sheet(isPresented: $showingSettings) {
                    TrainingSettingsView(training: training)
                }
                .confirmationDialog("Training beenden?", isPresented: $confirmingStop, titleVisibility: .visible) {
                    Button("Training beenden", role: .destructive) { training.cancel() }
                } message: { Text("Dein bisheriges Training wird im Log gespeichert.") }
        }
    }

    private var connectionCard: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack(spacing: 10) {
                Image(systemName: device.demo ? "waveform" : "antenna.radiowaves.left.and.right")
                    .foregroundStyle(device.demo ? Color.orange : device.canRecord ? Color.teal : Color.secondary)
                VStack(alignment: .leading, spacing: 3) {
                    Text(device.demo ? "Simulation aktiv" : device.canRecord ? "Fingerworker verbunden" : "Fingerworker verbinden")
                        .font(.subheadline.weight(.semibold))
                    Text(device.demo ? "Testdaten · kein Gerät verbunden" : device.connectionDescription)
                        .font(.caption).foregroundStyle(.secondary)
                }
                Spacer(minLength: 4)
                if let sample = device.latest {
                    Text(String(format: "%.2f V", Double(sample.batteryMillivolts) / 1000))
                        .font(.caption).monospacedDigit().foregroundStyle(.secondary)
                }
            }
            if !device.canRecord {
                Button("Gerät suchen", systemImage: "magnifyingglass") { device.scan() }
                    .buttonStyle(.bordered).disabled(training.workout?.isRunning == true)
                ForEach(device.devices, id: \.identifier) { peripheral in
                    Button { device.connect(peripheral) } label: {
                        Label(peripheral.name ?? "Fingerworker", systemImage: "sensor.fill")
                    }.buttonStyle(.borderedProminent)
                }
            }
            Divider()
            if (training.workout?.settings ?? training.settings).isCARC {
                Text("cARC läuft nach Zeit, auch ohne Verbindung. Der Endanschlag muss nicht erreicht werden.")
                    .font(.footnote).foregroundStyle(.secondary)
            } else { EndstopFeedbackControls(device: device) }
        }.trainingCard()
    }

    private var planCard: some View {
        let settings = training.settings
        return VStack(alignment: .leading, spacing: 20) {
            VStack(alignment: .leading, spacing: 6) {
                Text("DEIN PROTOKOLL").font(.caption.weight(.semibold)).foregroundStyle(.teal)
                Text(settings.mode.title).font(.title2.bold())
                Text("Abwechselnd links und rechts trainieren.")
                    .font(.subheadline).foregroundStyle(.secondary)
            }
            HStack(alignment: .top, spacing: 20) {
                TrainingMetric(title: settings.isCARC ? "Blöcke / Hand" : "Sätze / Hand", value: "\(settings.setsPerHand)")
                Spacer(minLength: 0)
                TrainingMetric(title: settings.isCARC ? "Zeit / Block" : "Züge / Satz",
                               value: settings.carc.map { TrainingSettings.clock(TimeInterval($0.durationSeconds)) } ?? "\(settings.repetitionsPerSet)")
                Spacer(minLength: 0)
                TrainingMetric(title: "Pause / Hand", value: settings.restLabel)
            }
            Divider()
            VStack(alignment: .leading, spacing: 10) {
                Label("Start mit \(settings.startingHand.title.lowercased())", systemImage: "hand.draw")
                Label(settings.isCARC ? "Zeitgesteuert · ohne Zugzählung" : settings.countingMode.title,
                      systemImage: settings.isCARC ? "timer" : settings.countingMode == .device ? "sensor.fill" : "hand.tap")
                if settings.usesCadence {
                    Label("\(seconds(settings.pullSeconds)) s \(settings.isCARC ? "leicht drücken" : "ziehen") · \(seconds(settings.releaseSeconds)) s lösen", systemImage: "metronome")
                }
            }.font(.subheadline)
            Text(settings.isCARC && settings.restSeconds == 0 ? "Nach jedem Block folgt der Handwechsel."
                 : "Jede Hand erholt sich \(settings.restLabel) min ab ihrem \(settings.isCARC ? "Blockende" : "Satzende"). Während die andere Hand trainiert, läuft diese Erholung weiter.")
                .font(.footnote).foregroundStyle(.secondary)
                .fixedSize(horizontal: false, vertical: true)
            if settings.isCARC {
                Text("Sehr leichter Widerstand, locker drücken und vollständig lösen. Kleine Bewegungen reichen. Bei zunehmendem Pump Widerstand oder Hub reduzieren.")
                    .font(.footnote).foregroundStyle(.secondary)
                if settings.carc?.showForce == true {
                    Label("Kraftanzeige mit Erinnerung bei \(seconds(settings.carc!.forceCeilingNewtons)) N", systemImage: "waveform.path")
                        .font(.footnote).foregroundStyle(.secondary)
                }
            } else if settings.countingMode == .device {
                Text("Ein Zug zählt, wenn der Geräte-Endanschlag erreicht wird. Der Taktgeber gibt nur den Rhythmus vor.")
                    .font(.footnote).foregroundStyle(.secondary)
            }
        }.trainingCard()
    }

    private func workoutCard(_ workout: TrainingSession) -> some View {
        let phase = workout.phase == .paused ? workout.pausedPhase ?? .working : workout.phase
        return VStack(spacing: 18) {
            HStack {
                Label(workout.phase == .paused ? "Pausiert" : phase == .resting ? "Erholung" : phase == .preparing ? "Handwechsel / Start" : "Am Zug",
                      systemImage: workout.phase == .paused ? "pause.circle.fill" : phase == .resting ? "hourglass" : "hand.draw.fill")
                    .font(.subheadline.weight(.semibold)).foregroundStyle(.teal)
                Spacer()
                Text("\(workout.settings.isCARC ? "Block" : "Satz") \(workout.currentSetNumber) / \(workout.settings.setsPerHand)")
                    .font(.subheadline).foregroundStyle(.secondary)
            }
            VStack(spacing: 4) {
                Text(workout.activeHand.handTitle).font(.title2.bold())
                    .accessibilityIdentifier("training.hand")
                if phase == .working {
                    if workout.settings.isCARC {
                        Text(TrainingSettings.clock(workout.remaining(at: training.now)))
                            .font(.system(size: 68, weight: .semibold, design: .rounded)).monospacedDigit()
                            .accessibilityIdentifier("training.carcCountdown")
                        Text("Verbleibende Blockzeit").font(.subheadline).foregroundStyle(.secondary)
                    } else {
                    HStack(alignment: .firstTextBaseline, spacing: 8) {
                        Text("\(workout.currentRepetitions)")
                            .font(.system(size: 80, weight: .semibold, design: .rounded)).monospacedDigit()
                            .accessibilityIdentifier("training.count")
                        Text("/ \(workout.settings.repetitionsPerSet)")
                            .font(.title2).foregroundStyle(.secondary).monospacedDigit()
                    }.accessibilityElement(children: .combine)
                        .accessibilityLabel("\(workout.currentRepetitions) von \(workout.settings.repetitionsPerSet) Zügen")
                    }
                    if workout.settings.usesCadence, workout.phase != .paused {
                        Label(workout.isPulling(at: training.now) ? (workout.settings.isCARC ? "Leicht drücken" : "Ziehen") : "Vollständig lösen",
                              systemImage: workout.isPulling(at: training.now) ? "arrow.down" : "arrow.up")
                            .font(.headline).foregroundStyle(workout.isPulling(at: training.now) ? Color.teal : Color.secondary)
                    } else {
                        Text(workout.phase == .paused ? "\(workout.settings.isCARC ? "Timer" : "Zählung") angehalten" : "\(workout.settings.countingMode == .device ? "Züge werden am Gerät gezählt" : "Züge manuell bestätigen")")
                            .font(.subheadline).foregroundStyle(.secondary)
                    }
                } else {
                    Text(TrainingSettings.clock(workout.remaining(at: training.now)))
                        .font(.system(size: 68, weight: .semibold, design: .rounded)).monospacedDigit()
                        .accessibilityIdentifier("training.countdown")
                    Text(phase == .resting ? "Bis diese Hand wieder bereit ist" : "Fingerworker in die \(workout.activeHand.adjective) Hand nehmen")
                        .font(.subheadline).foregroundStyle(.secondary).multilineTextAlignment(.center)
                }
            }.frame(maxWidth: .infinity).padding(.vertical, 6)
            if let reason = workout.pauseReason {
                Label(reason, systemImage: "info.circle").font(.subheadline).foregroundStyle(.secondary)
            }
            ProgressView(value: workout.progress(at: training.now)).tint(.teal)
                .accessibilityLabel("Trainingsfortschritt")
            HStack {
                Text(workout.settings.isCARC
                     ? "\(trainingDuration(workout.workSeconds(at: training.now))) / \(trainingDuration(workout.settings.totalWorkSeconds)) Übungszeit"
                     : "\(workout.totalRepetitions) / \(workout.settings.totalRepetitions) Züge gesamt")
                Spacer()
                Text(TrainingSettings.clock(workout.elapsed(at: training.now)))
            }.font(.caption).foregroundStyle(.secondary).monospacedDigit()
            if let carc = workout.settings.carc {
                if carc.showForce {
                    if let force = carc.displayedForce(from: device.canRecord ? device.latest : nil) {
                        HStack {
                            Label("Kraft nach Tara", systemImage: "waveform.path")
                            Spacer()
                            Text(String(format: "%.1f N", force)).fontWeight(.semibold).monospacedDigit()
                        }.font(.subheadline)
                        if workout.phase == .working, force > carc.forceCeilingNewtons {
                            Label("Leichter drücken · über deinem Richtwert", systemImage: "arrow.down.circle")
                                .font(.subheadline).foregroundStyle(.orange)
                                .accessibilityIdentifier("training.carcForceReminder")
                        }
                    } else {
                        Text("Kraftanzeige nicht verfügbar. Der Timer läuft unabhängig davon.")
                            .font(.footnote).foregroundStyle(.secondary)
                    }
                }
            } else if let sample = device.latest, sample.valid {
                HStack {
                    Label("Kraft jetzt", systemImage: "waveform.path")
                    Spacer()
                    Text(String(format: "%.1f N", sample.force)).fontWeight(.semibold).monospacedDigit()
                }.font(.subheadline)
            }
        }.trainingCard()
    }

    private func handsCard(_ workout: TrainingSession) -> some View {
        VStack(spacing: 16) {
            ForEach(TrainingHand.allCases) { hand in
                HStack(spacing: 14) {
                    Image(systemName: hand == workout.activeHand ? "hand.draw.fill" : "hand.draw")
                        .font(.title3).foregroundStyle(hand == workout.activeHand ? Color.teal : Color.secondary)
                    VStack(alignment: .leading, spacing: 5) {
                        Text(hand.title).font(.subheadline.bold())
                        HStack(spacing: 5) {
                            ForEach(0..<workout.settings.setsPerHand, id: \.self) { index in
                                Capsule().fill(index < workout.completedSets(for: hand) ? Color.teal : Color.secondary.opacity(0.15))
                                    .frame(height: 5)
                            }
                        }.frame(maxWidth: 150).accessibilityHidden(true)
                    }
                    Spacer()
                    VStack(alignment: .trailing, spacing: 3) {
                        Text("\(workout.completedSets(for: hand)) / \(workout.settings.setsPerHand) \(workout.settings.isCARC ? "Blöcke" : "Sätze")")
                            .font(.subheadline).monospacedDigit()
                        if let ready = workout.readyAt(for: hand), workout.completedSets(for: hand) < workout.settings.setsPerHand {
                            let date = workout.phase == .paused ? workout.pausedAt ?? training.now : training.now
                            Text(ready > date ? "Erholung \(TrainingSettings.clock(ready.timeIntervalSince(date)))" : "Bereit")
                                .font(.caption).foregroundStyle(.secondary).monospacedDigit()
                        }
                    }
                }
            }
        }.trainingCard()
    }

    private func workoutControls(_ workout: TrainingSession) -> some View {
        VStack(spacing: 12) {
            if !workout.settings.isCARC, workout.settings.countingMode == .manual, workout.phase == .working {
                HStack {
                    Button { training.undoManualRepetition() } label: { Image(systemName: "minus") }
                        .buttonStyle(.bordered).disabled(workout.currentRepetitions == 0)
                        .accessibilityLabel("Letzten Zug zurücknehmen")
                    Button { training.addManualRepetition() } label: {
                        Label("Zug zählen", systemImage: "plus").frame(maxWidth: .infinity).padding(.vertical, 7)
                    }.buttonStyle(.borderedProminent).accessibilityIdentifier("training.manualCount")
                }
            }
            Button { workout.phase == .paused ? training.resume() : training.pause() } label: {
                Label(workout.phase == .paused ? "Fortsetzen" : "Pausieren", systemImage: workout.phase == .paused ? "play.fill" : "pause.fill")
                    .font(.headline).frame(maxWidth: .infinity).padding(.vertical, 9)
            }.buttonStyle(.borderedProminent)
                .disabled(workout.phase == .paused && !training.canResume)
                .accessibilityIdentifier("training.pauseResume")
            if workout.phase == .paused && !training.canResume {
                Text("Zum Fortsetzen muss der Fingerworker verbunden und im dynamischen Modus bereit sein.")
                    .font(.footnote).foregroundStyle(.secondary)
            }
            Button("Training beenden", role: .destructive) { confirmingStop = true }
                .buttonStyle(.bordered).tint(.red).accessibilityIdentifier("training.stop")
        }
    }
    private func seconds(_ value: Double) -> String { value.formatted(.number.precision(.fractionLength(0...1))) }
}

struct TrainingSettingsView: View {
    @ObservedObject var training: TrainingStore
    @Environment(\.dismiss) private var dismiss
    @State private var draft: TrainingSettings
    init(training: TrainingStore) {
        self.training = training
        _draft = State(initialValue: training.settings)
    }
    var body: some View {
        NavigationStack {
            Form {
                if training.isOngoing {
                    Section { Text("Änderungen gelten für dein nächstes Training. Das laufende Protokoll bleibt bestehen.") }
                }
                Section("Protokoll") {
                    Picker("Trainingsart", selection: $draft.mode) {
                        ForEach(TrainingMode.allCases) { Text($0.title).tag($0) }
                    }.accessibilityIdentifier("settings.mode")
                    if draft.isCARC {
                        Stepper(value: Binding(get: { draft.carc!.durationSeconds }, set: { draft.carc?.durationSeconds = $0 }), in: 60...3600, step: 60) {
                            setting("Zeit pro Block", TrainingSettings.clock(TimeInterval(draft.carc!.durationSeconds)))
                        }.accessibilityIdentifier("settings.carcDuration")
                    } else {
                    Stepper(value: $draft.repetitionsPerSet, in: 1...50) {
                        setting("Züge pro Satz", "\(draft.repetitionsPerSet)")
                    }.accessibilityIdentifier("settings.repetitions")
                    }
                    Stepper(value: $draft.setsPerHand, in: 1...12) {
                        setting(draft.isCARC ? "Blöcke pro Hand" : "Sätze pro Hand", "\(draft.setsPerHand)")
                    }.accessibilityIdentifier("settings.sets")
                    Stepper(value: $draft.restSeconds, in: 0...900, step: 15) {
                        setting("Pause pro Hand", draft.restLabel)
                    }.accessibilityIdentifier("settings.rest")
                    Picker("Start-Hand", selection: $draft.startingHand) {
                        ForEach(TrainingHand.allCases) { Text($0.title).tag($0) }
                    }.accessibilityIdentifier("settings.hand")
                }
                Section {
                    if !draft.isCARC {
                    Picker("Züge zählen", selection: $draft.countingMode) {
                        ForEach(TrainingCountingMode.allCases) { Text($0.title).tag($0) }
                    }
                    }
                    Stepper(value: $draft.preparationSeconds, in: 0...15) {
                        setting("Vorlauf / Handwechsel", "\(draft.preparationSeconds) s")
                    }.accessibilityIdentifier("settings.preparation")
                } header: { Text("Ablauf") } footer: {
                    Text(draft.isCARC
                         ? "Die Blockzeit läuft unabhängig vom Gerät. Kleine Bewegungen reichen; der Endanschlag muss nicht erreicht werden. Beim Sperren oder Verlassen der App pausiert der Timer."
                         : "Automatisch: Der Fingerworker zählt volle Züge am Endanschlag. Die Pause läuft separat für jede Hand. Nach einer Erholung beginnt der nächste Satz direkt.")
                }
                Section {
                    if !draft.isCARC {
                    Toggle("Taktgeber", isOn: $draft.cadenceEnabled)
                        .accessibilityIdentifier("settings.cadence")
                    }
                    if draft.usesCadence {
                        Stepper(value: $draft.pullSeconds, in: 0.5...5, step: 0.5) {
                            setting(draft.isCARC ? "Leicht drücken" : "Ziehen", "\(draft.pullSeconds.formatted(.number.precision(.fractionLength(0...1)))) s")
                        }
                        Stepper(value: $draft.releaseSeconds, in: 0.5...5, step: 0.5) {
                            setting("Lösen", "\(draft.releaseSeconds.formatted(.number.precision(.fractionLength(0...1)))) s")
                        }
                    }
                    Toggle("Töne", isOn: $draft.soundEnabled)
                    Toggle("Haptisches Feedback", isOn: $draft.hapticsEnabled)
                } header: { Text("Rhythmus & Feedback") } footer: {
                    Text(draft.isCARC ? "Der Rhythmus ist eine Orientierung. Es werden keine Wiederholungen gezählt. Sehr leicht trainieren und bei zunehmendem Pump Widerstand oder Hub reduzieren."
                         : "Der Taktgeber zeigt Ziehen und Lösen an. Gezählt werden weiterhin nur die tatsächlichen Züge.")
                }
                if draft.isCARC {
                    Section {
                        Toggle("Kraftfeedback anzeigen", isOn: Binding(get: { draft.carc!.showForce }, set: { draft.carc?.showForce = $0 }))
                            .accessibilityIdentifier("settings.carcForce")
                        if draft.carc?.showForce == true {
                            Stepper(value: Binding(get: { draft.carc!.forceCeilingNewtons }, set: { draft.carc?.forceCeilingNewtons = $0 }), in: 5...500, step: 5) {
                                setting("Erinnerung über", "\(draft.carc!.forceCeilingNewtons.formatted()) N")
                            }
                        }
                    } header: { Text("Optionales Kraftfeedback") } footer: {
                        Text("Nur mit gültiger, kalibrierter Messung im dynamischen Modus. Die Anzeige berücksichtigt die Tara. Der Wert ist deine eigene Erinnerung, keine ermittelte Trainingsschwelle. Am Rücklaufanschlag ist die Handkraft nicht vollständig messbar.")
                    }
                }
                Section("Vorlagen") {
                    Button("cARC · 5 min pro Hand") {
                        draft.mode = .carc; draft.carc = CARCSettings()
                        draft.setsPerHand = 1; draft.restSeconds = 0
                        draft.preparationSeconds = 5; draft.pullSeconds = 1; draft.releaseSeconds = 1
                    }.accessibilityIdentifier("settings.carcPreset")
                    Button("6 × 15 · 3 min pro Hand") {
                        draft.mode = .curls
                        draft.repetitionsPerSet = 15; draft.setsPerHand = 6; draft.restSeconds = 180
                    }
                    Button("6 × 20 · 3 min pro Hand") {
                        draft.mode = .curls
                        draft.repetitionsPerSet = 20; draft.setsPerHand = 6; draft.restSeconds = 180
                    }
                }
            }.navigationTitle("Einstellungen").navigationBarTitleDisplayMode(.inline)
                .toolbar {
                    ToolbarItem(placement: .cancellationAction) { Button("Abbrechen") { dismiss() } }
                    ToolbarItem(placement: .confirmationAction) {
                        Button("Fertig") { training.updateSettings(draft); dismiss() }
                            .fontWeight(.semibold).accessibilityIdentifier("settings.save")
                    }
                }
        }.tint(.teal)
    }
    private func setting(_ title: String, _ value: String) -> some View {
        HStack { Text(title); Spacer(); Text(value).monospacedDigit().foregroundStyle(.secondary) }
    }
}

struct TrainingHistoryView: View {
    @ObservedObject var training: TrainingStore
    @State private var exporting = false
    @State private var exportDocument = CSVDocument(text: "")
    @State private var exportError: String?
    var body: some View {
        NavigationStack {
            Group {
                if training.history.isEmpty {
                    ContentUnavailableView("Dein erstes Training wartet", systemImage: "hand.draw",
                                           description: Text("Jede Einheit wird automatisch gespeichert – mit Sätzen, Zügen, Pausen und deinen Notizen."))
                } else {
                    List(training.history) { workout in
                        NavigationLink {
                            TrainingLogDetailView(training: training, workoutID: workout.id)
                        } label: {
                            VStack(alignment: .leading, spacing: 7) {
                                HStack {
                                    Text(trainingDate(workout.startedAt)).font(.headline)
                                    Spacer()
                                    Image(systemName: workout.phase == .completed ? "checkmark.circle.fill" : workout.phase == .cancelled ? "stop.circle" : "pause.circle")
                                        .foregroundStyle(workout.phase == .completed ? Color.teal : Color.secondary)
                                }
                                Text(workout.settings.protocolDescription + (workout.settings.isCARC
                                     ? " · \(trainingDuration(workout.workSeconds(at: training.now))) Übungszeit"
                                     : " · \(workout.totalRepetitions) Züge"))
                                    .font(.subheadline).foregroundStyle(.secondary)
                                Text(workout.statusTitle + (workout.source == "simulation" ? " · Simulation" : ""))
                                    .font(.caption).foregroundStyle(workout.source == "simulation" ? Color.orange : Color.secondary)
                                if let effort = workout.log?.perceivedExertion {
                                    Text("Anstrengung \(effort)/10").font(.caption).foregroundStyle(.secondary)
                                }
                                if let notes = workout.log?.notes, !notes.isEmpty {
                                    Text(notes).font(.caption).foregroundStyle(.secondary).lineLimit(2)
                                }
                            }.padding(.vertical, 5)
                        }
                    }
                }
            }.navigationTitle("Trainingslog")
                .safeAreaInset(edge: .bottom) {
                    if let error = training.storageError {
                        Text(error).font(.footnote).foregroundStyle(.red).padding().frame(maxWidth: .infinity)
                            .background(Color(.systemGroupedBackground))
                    }
                }
                .toolbar {
                    ToolbarItem(placement: .topBarTrailing) {
                        Button("Alle Einheiten exportieren", systemImage: "square.and.arrow.up") {
                            exportDocument = CSVDocument(text: TrainingLogCSV.make(sessions: training.history, now: Date()))
                            exporting = true
                        }.disabled(training.history.isEmpty).accessibilityIdentifier("log.exportAll")
                    }
                }
                .fileExporter(isPresented: $exporting, document: exportDocument, contentType: .commaSeparatedText,
                              defaultFilename: "fingerworker-trainingslog") { result in
                    if case .failure(let error) = result { exportError = error.localizedDescription }
                }
                .alert("Export fehlgeschlagen", isPresented: Binding(get: { exportError != nil }, set: { if !$0 { exportError = nil } })) {
                    Button("OK") { exportError = nil }
                } message: { Text(exportError ?? "") }
        }
    }
}

struct TrainingLogDetailView: View {
    @ObservedObject var training: TrainingStore
    let workoutID: UUID
    @State private var editing = false
    @State private var showTimeline = false
    @State private var exporting = false
    @State private var exportDocument = CSVDocument(text: "")
    @State private var exportError: String?
    private var workout: TrainingSession? {
        training.workout?.id == workoutID ? training.workout : training.history.first(where: { $0.id == workoutID })
    }
    var body: some View {
        ScrollView {
            if let workout {
                LazyVStack(alignment: .leading, spacing: 18) {
                    TrainingSummaryView(workout: workout, now: training.now).trainingCard()
                    protocolCard(workout)
                    VStack(alignment: .leading, spacing: 12) {
                        HStack {
                            Text("Dein Eintrag").font(.headline)
                            Spacer()
                            Button("Bearbeiten", systemImage: "pencil") { editing = true }
                                .accessibilityIdentifier("log.edit")
                        }
                        if let effort = workout.log?.perceivedExertion {
                            Text("Anstrengung: \(effort)/10").font(.subheadline)
                        }
                        Text(workout.log?.notes.isEmpty == false ? workout.log!.notes : "Wie lief die Einheit? Ergänze Anstrengung und Notizen, zum Beispiel Widerstand oder Griffposition.")
                            .font(.subheadline).foregroundStyle(.secondary).textSelection(.enabled)
                    }.trainingCard()
                    if let error = training.storageError {
                        Text(error).font(.footnote).foregroundStyle(.red)
                    }
                    VStack(alignment: .leading, spacing: 12) {
                        DisclosureGroup(isExpanded: $showTimeline) {
                            if workout.log?.hasCompleteTimeline != true {
                                Text("Für diese ältere Einheit ist der Ablauf nicht vollständig aufgezeichnet. Vorhandene Satzdaten bleiben erhalten.")
                                    .font(.footnote).foregroundStyle(.secondary).padding(.vertical, 8)
                            }
                            LazyVStack(alignment: .leading, spacing: 16) {
                                ForEach(workout.log?.events ?? []) { event in
                                    eventRow(event)
                                }
                            }.padding(.top, 10)
                        } label: {
                            Text("Ablauf · \(workout.log?.events.count ?? 0) Einträge").font(.headline)
                        }.accessibilityIdentifier("log.timeline")
                        Text(workout.settings.isCARC
                             ? "Blockzeiten enthalten keine Unterbrechungen. Der Taktgeber bestätigt keine tatsächlich ausgeführten Bewegungen."
                             : "Zeitpunkte zeigen die Erfassung in der App. Mehrere nachträglich empfangene Gerätezüge werden gemeinsam eingetragen. Satzzeiten und Erholung enthalten keine Unterbrechungen.")
                            .font(.caption).foregroundStyle(.secondary)
                    }.trainingCard()
                }.padding(20)
            }
        }.background(Color(.systemGroupedBackground))
            .navigationTitle("Trainingseintrag").navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button("Einheit exportieren", systemImage: "square.and.arrow.up") {
                        guard let workout else { return }
                        exportDocument = CSVDocument(text: TrainingLogCSV.make(sessions: [workout], now: Date()))
                        exporting = true
                    }.accessibilityIdentifier("log.export")
                }
            }
            .sheet(isPresented: $editing) {
                if let workout { TrainingLogEditor(training: training, workout: workout) }
            }
            .fileExporter(isPresented: $exporting, document: exportDocument, contentType: .commaSeparatedText,
                          defaultFilename: "fingerworker-training-\(workoutID.uuidString.prefix(8))") { result in
                if case .failure(let error) = result { exportError = error.localizedDescription }
            }
            .alert("Export fehlgeschlagen", isPresented: Binding(get: { exportError != nil }, set: { if !$0 { exportError = nil } })) {
                Button("OK") { exportError = nil }
            } message: { Text(exportError ?? "") }
    }
    private func protocolCard(_ workout: TrainingSession) -> some View {
        let settings = workout.settings
        return VStack(alignment: .leading, spacing: 10) {
            Text("Protokoll dieser Einheit").font(.headline)
            LabeledContent("Trainingsart", value: settings.mode.title)
            LabeledContent("Pro Hand", value: settings.isCARC
                           ? "\(settings.setsPerHand) × \(TrainingSettings.clock(TimeInterval(settings.carc!.durationSeconds))) min"
                           : "\(settings.setsPerHand) × \(settings.repetitionsPerSet) \(settings.repetitionsPerSet == 1 ? "Zug" : "Züge")")
            LabeledContent("Erholung pro Hand", value: settings.restLabel)
            LabeledContent("Start-Hand", value: settings.startingHand.title)
            LabeledContent("Steuerung", value: settings.isCARC ? "Zeit · keine Zugzählung" : settings.countingMode.title)
            LabeledContent("Vorlauf / Handwechsel", value: "\(settings.preparationSeconds) s")
            if settings.usesCadence {
                LabeledContent("Takt Ziehen / Lösen", value: "\(settings.pullSeconds.formatted()) / \(settings.releaseSeconds.formatted()) s")
            } else { LabeledContent("Taktgeber", value: "Aus") }
            LabeledContent("Unterbrechungen", value: trainingDuration(workout.pausedSeconds))
            if let carc = settings.carc {
                LabeledContent("Kraftfeedback", value: carc.showForce ? "Erinnerung über \(carc.forceCeilingNewtons.formatted()) N" : "Aus")
            }
        }.font(.subheadline).trainingCard()
    }
    private func eventRow(_ event: TrainingEvent) -> some View {
        HStack(alignment: .top, spacing: 12) {
            Image(systemName: event.kind.symbol).foregroundStyle(.teal).frame(width: 22)
            VStack(alignment: .leading, spacing: 4) {
                HStack(alignment: .firstTextBaseline) {
                    Text(workout?.settings.isCARC == true ? event.kind.title.replacingOccurrences(of: "Satz", with: "Block") : event.kind.title)
                        .font(.subheadline.weight(.medium))
                    Spacer()
                    Text(event.date.formatted(Date.FormatStyle().hour().minute().second().locale(Locale(identifier: "de_LI"))))
                        .font(.caption).foregroundStyle(.secondary).monospacedDigit()
                }
                if let hand = event.hand, let number = event.setNumber {
                    Text("\(hand.title) · \(workout?.settings.isCARC == true ? "Block" : "Satz") \(number)" + (event.repetitions.map { " · \($0) \($0 == 1 ? "Zug" : "Züge")" } ?? ""))
                        .font(.caption).foregroundStyle(.secondary)
                }
                if let delta = event.delta, delta > 1 {
                    Text("\(delta) Züge gemeinsam erfasst").font(.caption).foregroundStyle(.secondary)
                }
                if let duration = event.durationSeconds {
                    Text((event.kind == .setStarted ? "Erholung davor: " : event.kind == .resumed ? "Unterbrechung: " : "Dauer: ") + trainingDuration(duration))
                        .font(.caption).foregroundStyle(.secondary)
                }
                if let reason = event.reason { Text(reason).font(.caption).foregroundStyle(.secondary) }
            }
        }
    }
}

private struct TrainingLogEditor: View {
    @ObservedObject var training: TrainingStore
    let workoutID: UUID
    @Environment(\.dismiss) private var dismiss
    @State private var notes: String
    @State private var effort: Int
    init(training: TrainingStore, workout: TrainingSession) {
        self.training = training; workoutID = workout.id
        _notes = State(initialValue: workout.log?.notes ?? "")
        _effort = State(initialValue: workout.log?.perceivedExertion ?? 0)
    }
    var body: some View {
        NavigationStack {
            Form {
                Section {
                    Picker("Anstrengung", selection: $effort) {
                        Text("Nicht angegeben").tag(0)
                        ForEach(1...10, id: \.self) { Text("\($0) / 10").tag($0) }
                    }.accessibilityIdentifier("log.effort")
                } footer: { Text("1 = sehr leicht · 10 = maximal anstrengend") }
                Section("Notizen") {
                    TextEditor(text: $notes).frame(minHeight: 150)
                        .accessibilityLabel("Trainingsnotizen").accessibilityIdentifier("log.notes")
                }
                if let error = training.storageError { Section { Text(error).foregroundStyle(.red) } }
            }.navigationTitle("Trainingseintrag").navigationBarTitleDisplayMode(.inline)
                .toolbar {
                    ToolbarItem(placement: .cancellationAction) { Button("Abbrechen") { dismiss() } }
                    ToolbarItem(placement: .confirmationAction) {
                        Button("Speichern") {
                            if training.updateLog(for: workoutID, notes: notes, perceivedExertion: effort == 0 ? nil : effort) { dismiss() }
                        }.fontWeight(.semibold).accessibilityIdentifier("log.save")
                    }
                }
        }.tint(.teal)
    }
}

struct TrainingSummaryView: View {
    let workout: TrainingSession
    let now: Date
    var body: some View {
        VStack(alignment: .leading, spacing: 22) {
            VStack(alignment: .leading, spacing: 6) {
                Image(systemName: workout.phase == .completed ? "checkmark.circle.fill" : "hand.draw.fill")
                    .font(.largeTitle).foregroundStyle(.teal)
                Text(workout.statusTitle).font(.title2.bold())
                if workout.settings.isCARC { Text("cARC · nach Zeit").font(.headline).foregroundStyle(.teal) }
                Text(trainingDate(workout.startedAt))
                    .font(.subheadline).foregroundStyle(.secondary)
                if workout.source == "simulation" {
                    Label("Simulation · Testdaten", systemImage: "waveform").font(.caption).foregroundStyle(.orange)
                }
            }
            HStack(alignment: .top) {
                TrainingMetric(title: workout.settings.isCARC ? "Übungszeit" : "Züge",
                               value: workout.settings.isCARC ? trainingDuration(workout.workSeconds(at: now)) : "\(workout.totalRepetitions)")
                Spacer()
                TrainingMetric(title: "Dauer", value: trainingDuration(workout.elapsed(at: now)))
                Spacer()
                TrainingMetric(title: "Peak¹", value: workout.hasForceSamples ? String(format: "%.1f N", workout.peakNewtons) : "—")
            }
            Divider()
            ForEach(TrainingHand.allCases) { hand in
                VStack(alignment: .leading, spacing: 10) {
                    HStack {
                        Text(hand.title).font(.headline)
                        Spacer()
                        Text("\(workout.completedSets(for: hand)) / \(workout.settings.setsPerHand) \(workout.settings.isCARC ? "Blöcke" : "Sätze")")
                            .font(.subheadline).foregroundStyle(.secondary)
                    }
                    ForEach(workout.results.filter { $0.hand == hand }) { result in
                        VStack(alignment: .leading, spacing: 4) {
                            HStack {
                                Text("\(workout.settings.isCARC ? "Block" : "Satz") \(result.number)")
                                Spacer()
                                Text((workout.settings.isCARC ? trainingDuration(result.durationSeconds) : "\(result.repetitions) \(result.repetitions == 1 ? "Zug" : "Züge")")
                                     + (result.completed ? "" : " · Teil"))
                                Text(result.forceSampleCount == 0 ? "—" : String(format: "%.1f N", result.peakNewtons)).foregroundStyle(.secondary)
                            }.font(.subheadline).monospacedDigit()
                            Text("\(workout.settings.isCARC ? "Blockzeit" : "Satzzeit") \(trainingDuration(result.durationSeconds))" + (result.restBeforeSeconds.map { " · Erholung davor \(trainingDuration($0))" } ?? ""))
                                .font(.caption).foregroundStyle(.secondary).monospacedDigit()
                        }
                    }
                }
            }
            Text("¹ Spitzenkraft aus den empfangenen gültigen Messwerten während der Sätze. Gespeicherte Geräte-Messungen kannst du unter Messung auswählen und als CSV exportieren.")
                .font(.footnote).foregroundStyle(.secondary)
        }.trainingCard()
    }
}

private struct TrainingMetric: View {
    let title: String
    let value: String
    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(title).font(.caption).foregroundStyle(.secondary)
            Text(value).font(.title2.weight(.semibold)).monospacedDigit().minimumScaleFactor(0.7)
        }
    }
}

func trainingDate(_ date: Date, includeSeconds: Bool = false) -> String {
    date.formatted(Date.FormatStyle(date: .abbreviated, time: includeSeconds ? .standard : .shortened)
        .locale(Locale(identifier: "de_LI")))
}

// Logged durations round to the nearest second; countdowns still round up.
private func trainingDuration(_ seconds: TimeInterval) -> String {
    TrainingSettings.clock(seconds.rounded())
}

private extension View {
    func trainingCard() -> some View {
        padding(20).frame(maxWidth: .infinity, alignment: .leading)
            .background(Color(.secondarySystemGroupedBackground), in: RoundedRectangle(cornerRadius: 22))
    }
}

private extension TrainingSession {
    var statusTitle: String {
        switch phase {
        case .completed: return "Training abgeschlossen"
        case .cancelled: return "Training beendet"
        case .paused: return "Training pausiert"
        default: return "Training läuft"
        }
    }
}

extension DeviceStore {
    var connectionDescription: String {
        switch connection {
        case "Connected": return "Live-Daten vom Gerät"
        case "Disconnected": return "Noch kein Gerät verbunden"
        case "Ready to scan": return "Bereit für die Gerätesuche"
        case "Scanning…": return "Suche nach deinem Fingerworker…"
        case "Choose a device": return "Wähle deinen Fingerworker"
        case "No compatible device found": return "Kein Fingerworker gefunden"
        case "Connecting…": return "Verbindung wird aufgebaut…"
        case "Discovering service…": return "Gerät wird vorbereitet…"
        case "Turn on Bluetooth": return "Bluetooth einschalten"
        case "Allow Bluetooth in Settings": return "Bluetooth in den iOS-Einstellungen erlauben"
        case "Bluetooth unavailable": return "Bluetooth nicht verfügbar"
        case "Bluetooth starting": return "Bluetooth startet…"
        case "Connected · waiting for data": return "Verbunden · warte auf Daten"
        case "Connection failed": return "Verbindung fehlgeschlagen"
        case "Service unavailable": return "Gerätedienst nicht verfügbar"
        case "Telemetry unavailable": return "Messdaten nicht verfügbar"
        case "Subscription failed": return "Live-Daten konnten nicht abonniert werden"
        case "Invalid telemetry packet": return "Ungültige Messdaten empfangen"
        case "Simulation": return "Simulation"
        default: return connection
        }
    }
}
