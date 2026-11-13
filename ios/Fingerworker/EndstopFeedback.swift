import AudioToolbox
import UIKit

/// Uses our bundled click rather than an undocumented system sound number.
final class EndstopFeedback {
    private var click: SystemSoundID = 0
    private let impact = UIImpactFeedbackGenerator(style: .light)

    init() {
        if let url = Bundle.main.url(forResource: "endstop-click", withExtension: "wav") {
            AudioServicesCreateSystemSoundID(url as CFURL, &click)
        }
    }
    deinit {
        if click != 0 { AudioServicesDisposeSystemSoundID(click) }
    }
    func play(sound: Bool, haptics: Bool) {
        guard UIApplication.shared.applicationState == .active else { return }
        if sound, click != 0 { AudioServicesPlaySystemSound(click) }
        if haptics { impact.impactOccurred(); impact.prepare() }
    }
}
