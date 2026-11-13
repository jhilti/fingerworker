# Training verification — 11 October 2026

## End-stop feedback — 6 November 2026

- `bash firmware/tools/test.sh` passes, including new live-feedback checks for
  initial held state, one cue per activation, held switch, release debounce,
  duplicate/out-of-order packets, packet gaps without cumulative catch-up,
  ADC faults, isometry, reboot, lifecycle reset, legacy packets and counter wrap.
- The generic iOS Simulator Debug build succeeds with signing disabled using
  `/tmp/fingerworker-endstop-build`. The original 35 ms mono/16-bit/44.1 kHz WAV
  is copied into the app bundle and the feedback source compiles for arm64/x86_64.
- No Swift source warnings/errors. The existing unused AppIntents metadata
  warning and sandbox CoreSimulator service diagnostics do not prevent the build.
- No running-simulator UI/audio check was performed in this change. Physical
  acceptance remains: click and haptics, saved switches in Training/Messung,
  silent mode/system volume, foreground/background transitions, held switch,
  real BLE timing and disconnect/reconnect. This change does not install the app
  on an iPhone.

## Builds

Both the iOS Simulator and physical iPhone SDK builds succeeded with code signing disabled. Minimum supported iOS remains 17.0. There were no Swift source warnings/errors. Xcode's sandboxed simulator service diagnostics and the unused AppIntents metadata warning did not prevent either build.

Use the Fingerworker scheme in Fingerworker.xcodeproj. A physical iPhone installation needs the user's Apple development team selected in Xcode.

## Automated checks

The existing firmware/tools/test.sh passes, including sanitizer-enabled firmware tests, C++ to Swift packet compatibility, device counter/peak handling and recording persistence/CSV.

New deterministic workout checks cover:

- Preparation and hand changes, including right-hand start and zero rest.
- Rest measured separately from each hand's last set, including time spent exercising the other hand.
- Multiple device counts received together, with no spill into another hand/set.
- Ignoring movements outside a working phase and stopping immediately after the final set.
- Pause/resume, frozen rest, active duration and partial sets on early stop.
- Device cumulative counts, missed notifications, duplicates, counter wrap, reboot, faults and counter rebasing.
- Legacy v1 end-stop edges and uncertain edges across packet gaps.
- Bounds on settings, atomic save/update/restore, invalid archive rejection, persisted settings and old recording compatibility.

## Simulator checks

Native UI checks used iPhone 17 / iOS 26.5 with the app's explicitly labelled 25 Hz simulation feed. The feed sends the same Measurement model, end-stop status and cumulative repetition counter used by connected-device training.

1. Changed and saved repetitions, sets, rest, preparation and cadence. Settings survived replacing/relaunching the simulator build.
2. Ran 2 × 1 pull per hand, 15-second rest and 2-second preparation. Automatic hand changes/rest completed with four total pulls and two completed sets for each hand. No final rest was added.
3. Inspected the saved JSON: one linked raw recording with 759 samples, matching count/sample arrays and completed state. The last counted end-stop sample was included.
4. Paused a 2 × 3 workout. The countdown and workout count stayed frozen while device telemetry continued.
5. Ended the data stream through Messung. Training automatically paused at two pulls, explained the interruption and disabled resume.
6. Restarted the data stream. Resume was enabled; historical/paused movements did not count. Exactly three pulls completed the left-hand set.
7. Moved the app to the home screen. On return it remained paused at the right-hand start, with the background reason and saved checkpoint intact.
8. Resumed and ended the workout early. The summary and history retained five pulls: one completed left set (three) and one partial right set (two).
9. Verified both completed and ended workouts in Verlauf, and raw recording controls were disabled while training was ongoing.

## Physical acceptance still required

Simulator tests do not establish real Bluetooth interoperability, RF reliability, end-stop/cable behaviour, calibration accuracy or iPhone background reception. Test with the actual qualified Fingerworker hardware and matching firmware before relying on the measurements. Existing firmware qualification requirements are described in README.md and BLE_PROTOCOL.md.

## Training log extension — 11 October 2026

The Simulator and iPhone SDK builds succeeded again after adding the log. `bash firmware/tools/test.sh` passes, including the new log checks:

- Timestamped accepted counts, including cumulative batches clamped to the active set.
- Set numbers, hand changes, actual per-hand recovery and exclusion of interruptions from recovery.
- Pause reasons, resume durations, corrections and early cancellation without a false resume event.
- Atomic persistence of event IDs, notes, perceived exertion and recovery values; invalid log values rejected.
- Older workout files without a log or recovery fields still load and export with an incomplete-timeline flag.
- Rectangular single/all-workout CSV, UUID linkage, UTC dates, numeric format, escaped quotes/newlines and literal spreadsheet text.

Native UI checks on the existing iPhone 17 simulator confirmed:

1. Existing completed and partial workouts load under **Log**; older workouts show the missing-timeline explanation.
2. Notes entered through ordinary keyboard input and an exertion score of 7/10 save and appear immediately in the detail page. The saved JSON retains them and the original partial-set results.
3. Single-workout CSV opens the iOS file exporter and saves locally under **Auf meinem iPhone**. CSV contents and all-workout export are independently verified by the domain tests.
4. A new automatic 2 × 1 workout per hand with 15-second rest and 2-second preparation completes with four pulls, four completed sets and 18 timestamped events. Both later sets record between 15.0 and 15.2 seconds of actual per-hand recovery. The new timeline is visible in the detail page.
5. The matching raw measurement archive remains completed and linked by the workout UUID.
6. Simulator settings were restored to 6 × 15 per hand, 180-second rest, 5-second preparation and cadence disabled; existing test workouts remain labelled Simulation.

The native accessibility API can visually set a TextEditor value without updating its SwiftUI binding. Notes were therefore verified with ordinary keyboard input and by reading the saved archive. No clipboard access permission was granted for this test. Logged duration labels round to the nearest second; countdowns still round up and CSV keeps three decimal places.

## Timed cARC mode — 7 November 2026

The full `bash firmware/tools/test.sh` suite passes, including the existing firmware, BLE, curl-workout and export regressions. New deterministic cARC checks cover:

- Timed preparation, per-hand blocks, hand changes and completion without end-stop counts.
- Exercise-time progress, frozen pause/cadence, resumed deadlines and exclusion of interruptions.
- Delayed timer callbacks crediting only the current block, without retroactive work for the other hand.
- Early stopping with a partial block and no movements; measured force sample counts remain accurate.
- Optional force display rejecting absent, invalid and isometric data; normalized settings bounds.
- Completed/partial archive round trips, invalid block rejection, settings from before cARC, and CSV schema 2 with empty cARC repetition fields.
- Codable checkpoint recovery after overnight downtime and completion when pause coincides with the final deadline.

Both Simulator and iPhone SDK builds pass with code signing disabled. No Swift source warnings/errors were reported. Xcode emitted local CoreSimulator service diagnostics and the existing unused AppIntents metadata warning; these did not prevent either build.

Native UI checks used an isolated `com.fingerworker.carcqa` installation on the booted iPhone 17 / iOS 26.5 simulator, preserving the existing app's workout data:

- Selected the cARC template, changed block duration to one minute, enabled optional force feedback and saved. The plan showed one timed block per hand, zero extra recovery and squeeze/release cadence.
- Started the workout and observed the block countdown, exercise-time progress, alternating movement cues and a visual force reminder using labelled simulated measurements.
- Paused and confirmed countdown/progress stayed frozen; resumed from the remaining time.
- Observed automatic change from left to right after a full 60-second block. Saved JSON recorded zero repetitions and no count events despite the simulation's end-stop activations.
- Stopped the simulation during the right-hand block. The cARC timer continued and the force display changed to unavailable.
- Completed both blocks and reopened the saved log. The summary showed 2:00 exercise time, two 60-second blocks and zero repetition events; the separate 2:10 session duration included the two preparation periods and excluded the pause. The protocol retained the force reminder and interruption time.

The five-minute template and force reminder are configurable product defaults, not validated physiological prescriptions. Physical Bluetooth behavior, sound/haptics on the phone, and force calibration remain hardware acceptance items.
