# Fingerworker iPhone prototype

Stand 11 October 2026. Open `Fingerworker.xcodeproj`, choose the Fingerworker scheme and run in an iPhone simulator. Simulator starts labelled simulation automatically. For a real iPhone select your Apple development team, install the app, allow Bluetooth, then Gerät suchen → Fingerworker.

## Guided training

### Timed cARC mode — 7 November 2026

Open **Training → Einstellungen → Trainingsart → cARC · nach Zeit**, or use the **cARC · 5 min pro Hand** template. The template is a configurable starting point, not a validated training prescription. Choose a very light resistance and a comfortable short stroke; reaching the end switch is unnecessary.

- Each hand completes a timed block, with configurable blocks per hand (1–12), block duration (1–60 minutes), hand-change preparation, and independent recovery. The template uses one 5-minute block per hand and zero additional recovery.
- The countdown and exercise-time progress replace repetitions. Squeeze/release cues are always visible in cARC; rhythm, sounds and haptics are configurable. Cadence cues and device counts never create cARC repetitions. End-stop click feedback is temporarily suppressed during a cARC workout without changing its saved preferences.
- The timer works without a connected or calibrated device and continues after a connection loss. Optional force feedback becomes unavailable when data is missing, invalid, or from isometric mode. Its adjustable reminder uses the displayed force after tare; it is not an automatically determined aerobic threshold or a percentage of maximum strength. Return-stop preload can obscure initial hand force.
- Pause/resume freezes block time and cadence. Moving the app to the background pauses the workout. A delayed timer callback finishes only the current block and starts the next hand from the current time; it does not claim unseen exercise for that hand.
- The log retains actual exercise time, completed and partial blocks, original settings, interruptions, notes and exertion. A partial timed block is retained even with zero counted movements. Missing force measurements appear as unavailable, not a measured zero.
- Settings and older curl workouts remain readable. CSV schema 2 adds `training_mode`, `block_duration_seconds`, `work_seconds`, `force_feedback_enabled`, `force_ceiling_newtons` and `force_sample_count`. cARC repetition fields are empty. Work time excludes preparation, recovery and interruptions; existing `active_seconds` remains total unpaused session time. Connected sessions can retain linked raw recordings as before.

### End-stop feedback — 6 November 2026

**Training** and **Messung** both expose **Rückmeldung bei Endlage**: a short click
(enabled by default), optional light haptics (off by default), and **Rückmeldung testen**.
Both switches persist across launches, apply immediately, and are independent of
the workout's cadence/transition cues. Feedback also works without an active workout
or recording, including the labelled simulation.

A freshly observed dynamic end-stop activation produces one cue after at least
10 ms of observed release. Holding the switch does not repeat. Feedback resets on
disconnect, stale/invalid telemetry, device reboot, packet gaps, and leaving the
foreground; cumulative device counts never cause catch-up sounds. Isometry and
other fault states suppress cues. An open end-stop cable is electrically
indistinguishable from activation and can also produce a cue.

Feedback runs only while the app is active. Sound uses the bundled original
35 ms mono PCM WAV (`python3 ios/make_click.py` regenerates it), registered through
System Sound Services, and respects iPhone silent mode and system volume. Haptics,
audibility, Bluetooth latency and operation on the physical iPhone/device still
require hardware checks. App-side cues are subject to BLE notification timing.

### Training behavior

The app now opens on **Training**. On a real iPhone, choose **Gerät suchen**, connect the Fingerworker, then tap **Training starten**. Automatic counting is the default; the simulator uses clearly labelled test data.

- Defaults: **6 × 15 pulls per hand, 3 minutes rest per hand**, left hand first and a 5-second preparation/hand-change countdown.
- Settings change repetitions (1–50), sets per hand (1–12), rest (0–15 minutes in 15-second steps), starting hand and preparation time (0–15 seconds). Settings persist across launches. A running workout keeps its original settings.
- Automatic counting uses the connected Fingerworker's cumulative repetition counter (v2/v3). Missed notifications are included; historical device counts are discarded at start/resume. Counts during preparation, rest or pause do not advance a set. A batch cannot overflow into the next hand. Legacy v1 counts observed end-stop edges and discards uncertain edges across packet gaps.
- Left and right alternate. Each hand's rest begins at **its own set end** and runs while the other hand exercises. For example, if left ends at 0:20 and right ends at 0:45, left is eligible at 3:20, so only 2:35 of shared waiting remains. There is no final rest after the last set.
- An optional cadence cue defaults to 1 second pulling / 1 second releasing, adjustable from 0.5–5 seconds each, with optional sound and haptics. Cadence never creates a repetition. Manual counting is an optional fallback.
- Pause/resume freezes workout time and countdowns. Device loss, stale data, reboot, invalid state or switching away from dynamic mode pauses automatic training. Resume requires a ready device and resets the counter baseline. Moving the app into the background pauses the guided workout because iOS does not guarantee background timers. Raw BLE recording may continue independently.
- Workouts are checkpointed locally about once a second and on transitions. After relaunch, an unfinished workout is offered paused. **Log** retains the original protocol, per-hand sets, pulls, active duration and received-sample peak force. Partial sets are preserved on early stop.
- Connected workouts also start the existing raw measurement archive automatically, link it to the workout UUID and stop it when the workout ends. **Messung** retains the live chart, recorded device peak and CSV export. Raw recording controls are locked while a workout is active.

Workout files live in Application Support/FingerworkerWorkouts; settings use UserDefaults. A sudden process termination may lose changes since the most recent checkpoint. All data remains local to this installation.

## Training log

Every newly started workout records a timestamped timeline: start, preparation/hand changes, set starts, accepted pulls, manual count corrections, set finishes, remaining shared rest, pauses with reasons, resumes and completion/early stop. A batch of device counts is one receipt event; individual movement timestamps between notifications are not reconstructed. Counts ignored outside a working phase or beyond a completed set do not enter the log.

Open **Log → a workout** to see its original settings, per-hand sets, received-sample peak, set duration and actual recovery before later sets. Recovery includes exercising the other hand and shared waiting, but excludes workout interruptions. The first set of each hand has no previous-set recovery value. Expand **Ablauf** for the timeline. Add optional notes (for example resistance or grip position) and perceived exertion from 1–10 through **Bearbeiten**. Editing notes during a workout preserves newly received counts and events.

Export a single workout from its detail page or all saved workouts from the Log toolbar. The CSV uses session, set and event rows linked by `workout_id`; session rows hold every original setting, source, totals, interruption duration, notes and exertion. Dates are UTC ISO 8601, numeric decimals use a dot, and text containing quotes/newlines is escaped. Notes and reasons beginning with formula characters are exported as literal spreadsheet text. Raw sample CSV remains available under **Messung** and links back using the same workout UUID.

Older workout JSON files still load. They retain their original settings and results, but show no fabricated event timeline or recovery values. Their notes can be edited and their existing data exported. `complete_timeline` identifies this difference in exported CSV. There is no cloud upload.

## Implemented

- BLE discovery, connection, notifications and automatic reconnect to the selected device after an unexpected connection loss. Explicit Disconnect, Find device and simulation cancel reconnect.
- Signed ADC raw values, validity/status display, battery voltage, chart, repetitions and CSV.
- V3 cumulative device peak over every freshly acquired valid ADC sample; session-specific reset token and acknowledgement. Legacy v1/v2 and simulation use received-sample peaks.
- Atomic local JSON autosave approximately once per second while packets arrive, plus stop/disconnect/background save. Saved sessions can be selected and exported after app restart. CSV includes raw values, status, device count/boot and peak/epoch.
- Stop waits for one final cumulative-peak notification (up to one second); interruption/timeout is recorded. Recording stays open during reconnect; missing raw samples are not reconstructed.

Sessions are stored in Application Support/FingerworkerSessions with one UUID-named file per session. A sudden process termination may lose data since the last successful autosave. Storage failures are shown. Sessions remain local to this app installation; deleting the app removes them. Saved-session selection does not resume acquisition. No cloud sync or full 330-SPS archive is implemented.

The app declares Bluetooth central background mode so connected BLE notifications may continue while backgrounded. Actual iOS scheduling, lock-screen reception and device interoperability need physical testing. App termination/force quit is not continuous recording. A background save preserves the most recent foreground state even when further packets do not arrive.

## Hardware dependency

The matching firmware is under `../firmware/`. `HARDWARE_QUALIFIED=false` intentionally blocks valid force and counts until bench qualification. Calibration must come from known loads in the final assembled mechanism. Real MTU negotiation (v3 requires ≥46), notifications, reset acknowledgement and reconnect remain physical acceptance items.

USB serial controls calibration, tare, power and operating mode. BLE exposes only the peak-reset write, not remote power/calibration commands. Full protocol: [BLE_PROTOCOL.md](BLE_PROTOCOL.md).

## Verification

The test script also checks the workout state machine with deterministic timestamps: hand-specific rest, preparation, pause/resume, batch counts, reboot/fault/gap handling, completion, partial sets, settings bounds and archive compatibility. Log tests cover accepted-count events, interrupted recovery timing, corrections, notes/exertion persistence, old workout loading and single/all-workout CSV shape and quoting.

The training feature's build and simulator results are recorded in [TRAINING_VERIFICATION.md](TRAINING_VERIFICATION.md).

Run `bash firmware/tools/test.sh` for sanitizer-enabled C++ logic tests, C++→Swift v2/v3 packet checks and atomic session save/load/update/CSV tests. Build:

```sh
xcodebuild -project ios/Fingerworker.xcodeproj -scheme Fingerworker -sdk iphonesimulator -configuration Debug -derivedDataPath /tmp/fingerworker-review-build CODE_SIGNING_ALLOWED=NO build
```

A simulator build checks compilation, not Bluetooth operation. Fresh build results are recorded in `../review/software-2026-10-11/STATUS.md`.
