import SwiftUI
import Charts
import UniformTypeIdentifiers

@main
struct FingerworkerApp: App {
    var body: some Scene { WindowGroup { Dashboard() } }
}
struct CSVDocument: FileDocument {
    static var readableContentTypes: [UTType] { [.commaSeparatedText] }
    var text: String
    init(text: String) { self.text = text }
    init(configuration: ReadConfiguration) throws { text = String(decoding: configuration.file.regularFileContents ?? Data(), as: UTF8.self) }
    func fileWrapper(configuration: WriteConfiguration) throws -> FileWrapper { FileWrapper(regularFileWithContents: Data(text.utf8)) }
}
private final class FingerworkerModel: ObservableObject {
    let device: DeviceStore
    let training: TrainingStore
    init() {
        let device = DeviceStore()
        self.device = device
        training = TrainingStore(device: device)
    }
}
struct Dashboard: View {
    @Environment(\.scenePhase) private var scenePhase
    // Construct the shared BLE/training stores once, including when SwiftUI
    // recreates the root view during a scene transition.
    @StateObject private var model = FingerworkerModel()
    private var device: DeviceStore { model.device }
    private var training: TrainingStore { model.training }
    var body: some View {
        TabView {
            TrainingHomeView(training: training, device: device)
                .tabItem { Label("Training", systemImage: "hand.draw.fill") }
            MeasurementDashboard(device: device, training: training)
                .tabItem { Label("Messung", systemImage: "waveform.path.ecg") }
            TrainingHistoryView(training: training)
                .tabItem { Label("Log", systemImage: "list.bullet.rectangle") }
        }.tint(.teal)
            .onChange(of: scenePhase) { _, phase in
                if phase == .background { training.saveForBackground() }
                if phase != .active { device.suspendEndstopFeedback(); device.saveForBackground() }
            }
    }
}
struct MeasurementDashboard: View {
    @ObservedObject var device: DeviceStore
    @ObservedObject var training: TrainingStore
    @State private var exporting = false
    @State private var exportDocument = CSVDocument(text: "")
    @State private var exportError: String?
    var body: some View {
        let segments = chartSegments
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 24) {
                    HStack {
                        Label(device.connectionDescription, systemImage: device.demo ? "waveform" : "antenna.radiowaves.left.and.right")
                        Spacer()
                        if let sample = device.latest { Text(String(format: "%.2f V", Double(sample.batteryMillivolts) / 1000)).monospacedDigit() }
                    }.font(.subheadline).foregroundStyle(.secondary)
                    if device.demo { Text("SIMULATION · TESTDATEN").font(.caption.bold()).foregroundStyle(.orange) }
                    VStack(alignment: .leading, spacing: 8) {
                        Text("KRAFT JETZT").font(.caption.bold()).foregroundStyle(.secondary)
                        HStack(alignment: .firstTextBaseline) {
                            Text(device.latest?.valid == true ? String(format: "%.1f", device.latest!.force) : "—")
                                .font(.system(size: 72, weight: .semibold, design: .rounded)).monospacedDigit()
                            Text("N").font(.title).foregroundStyle(.secondary)
                        }
                        if let sample = device.latest, !sample.valid { Label(sample.problem, systemImage: "exclamationmark.triangle.fill").foregroundStyle(.orange) }
                        else { Text("Kraft am Sensor").foregroundStyle(.secondary) }
                    }
                    Chart(device.points) { point in
                        if point.valid {
                            LineMark(x: .value("Time", Double(point.milliseconds) / 1000), y: .value("Force", point.force), series: .value("Segment", segments[point.id] ?? 0))
                                .foregroundStyle(Color.teal).lineStyle(StrokeStyle(lineWidth: 3))
                        }
                    }.chartXAxisLabel("Gerätezeit (s)").chartYAxisLabel("N").frame(height: 200)
                    HStack {
                        metric(device.peakFromDevice ? "Spitzenkraft · Gerät" : "Spitzenkraft · empfangen", String(format: "%.1f N", device.peak))
                        Spacer()
                        metric("Fehlende Pakete", "\(device.lostPackets)")
                    }
                    HStack {
                        metric(device.counterFromDevice ? "Züge · Gerät" : "Züge · App", "\(device.repetitions)")
                        Spacer()
                        Button("Zähler zurücksetzen", systemImage: "arrow.counterclockwise") { device.resetRepetitions() }
                            .disabled(training.isOngoing)
                    }
                    Text("Gezählt wird der Endanschlag. Ein Kabelbruch kann ebenfalls auslösen. Im isometrischen Modus werden keine Züge gezählt.")
                        .font(.caption).foregroundStyle(.secondary)
                    EndstopFeedbackControls(device: device)
                    if training.isOngoing {
                        Label("Die Messung gehört zum laufenden Training.", systemImage: "hand.draw.fill")
                            .font(.subheadline).foregroundStyle(.teal)
                    }
                    Button(device.stopping ? "Letzten Spitzenwert speichern…" : device.recording ? "Aufnahme beenden" : "Messung aufnehmen", systemImage: device.recording ? "stop.circle.fill" : "record.circle") { device.toggleRecording() }
                        .buttonStyle(.borderedProminent).tint(device.recording ? .red : .teal).disabled(training.isOngoing || device.stopping || (!device.recording && !device.canRecord)).frame(maxWidth: .infinity)
                    HStack {
                        Button("Gerät suchen", systemImage: "magnifyingglass") { device.scan() }
                        Spacer()
                        Button(device.demo ? "Simulation beenden" : "Simulation testen") { if device.demo { device.disconnect() } else { device.startDemo() } }
                    }.buttonStyle(.bordered)
                    ForEach(device.devices, id: \.identifier) { peripheral in
                        Button { device.connect(peripheral) } label: { Label(peripheral.name ?? "Fingerworker", systemImage: "sensor.fill") }
                    }
                    if device.canRecord && !device.demo { Button("Verbindung trennen") { device.disconnect() } }
                    Button("Aufnahme als CSV exportieren", systemImage: "square.and.arrow.up") {
                        // Build a fixed snapshot only on export, not on every
                        // live sample while this tab exists.
                        exportDocument = CSVDocument(text: device.csv); exporting = true
                    }.disabled(!device.hasSession || device.recording)
                    if let error = device.storageError { Text(error).foregroundStyle(.red) }
                    if !device.savedSessions.isEmpty {
                        Text("Gespeicherte Messungen").font(.headline)
                        ForEach(device.savedSessions) { session in
                            Button { device.selectSession(session) } label: {
                                VStack(alignment: .leading) {
                                    Text(trainingDate(session.startedAt, includeSeconds: true))
                                    Text("\(session.source == "simulation" ? "Simulation" : "Gerät")\(session.workoutID == nil ? "" : " · Training") · \(session.samples.count) Messwerte\(session.completed ? "" : " · unvollständig")\(session.interrupted ? " · unterbrochen" : "")").font(.caption)
                                }
                            }.disabled(device.recording)
                        }
                    }
                    if let exportError { Text(exportError).foregroundStyle(.red) }
                }.padding(24)
            }.navigationTitle("Messung").background(Color(.systemGroupedBackground))
        }.fileExporter(isPresented: $exporting, document: exportDocument, contentType: .commaSeparatedText, defaultFilename: "Fingerworker-session") { result in
            if case .failure(let error) = result { exportError = error.localizedDescription }
        }
    }
    private func metric(_ title: String, _ value: String) -> some View { VStack(alignment: .leading) { Text(title).font(.caption).foregroundStyle(.secondary); Text(value).font(.title3.bold()).monospacedDigit() } }
    private var chartSegments: [UInt32: Int] {
        var segments: [UInt32: Int] = [:]
        var segment = 0
        var previous: UInt32?
        for sample in device.points {
            if let previous, sample.id &- previous != 1 { segment += 1 }
            if !sample.valid { segment += 1 }
            segments[sample.id] = segment
            previous = sample.id
        }
        return segments
    }
}

struct EndstopFeedbackControls: View {
    @ObservedObject var device: DeviceStore
    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text("Rückmeldung bei Endlage").font(.subheadline.weight(.semibold))
            Toggle("Klickton", isOn: $device.endstopSoundEnabled)
                .accessibilityIdentifier("endstop.sound")
            Toggle("Vibrieren", isOn: $device.endstopHapticsEnabled)
                .accessibilityIdentifier("endstop.haptics")
            Button("Rückmeldung testen", systemImage: "speaker.wave.2") { device.previewEndstopFeedback() }
                .disabled(!device.endstopSoundEnabled && !device.endstopHapticsEnabled)
                .accessibilityIdentifier("endstop.preview")
            Text("Einmal pro Betätigung bei geöffneter App. Der Klickton folgt dem Stummmodus und der Lautstärke des iPhones.")
                .font(.caption).foregroundStyle(.secondary)
        }
    }
}
