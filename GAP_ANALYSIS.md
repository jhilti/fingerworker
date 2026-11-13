# Fingerworker specification comparison and prioritized work

8 November 2026 · Compared against [SPECIFICATION.md](SPECIFICATION.md), version 1.0 draft

**The core mechanical design, electronics design, firmware and training app are substantially implemented. The largest remaining gap is a physically qualified, calibrated, complete device.** There are also specific unfinished design and software tasks: current manufacturing drawings for the sensor support, R15 integration of the softer springs, an appropriate cARC resistance configuration, peak-state persistence, and complete linked raw recording/export behavior.

An earlier physical prototype exists: the user reported fitting the DF2194 springs and provided print/hand-fit feedback. R15 has nominal CAD, motion, service and print checks. The latest print-preparation record says no job was started by that preparation; it does not establish whether the user subsequently printed it. This comparison therefore distinguishes **missing implementation** from **missing physical evidence** and **open performance targets**. It does not assume that an undocumented component is absent or that a previously identified electrical risk is a confirmed fault.

## 1 What is already in place

| Area | Current evidence | Remaining limitation |
| --- | --- | --- |
| R15 form and movement | Integrated close palm support, 30 mm stroke, fixed preload geometry, click assembly, inboard strap slots and service paths have revision-specific nominal checks. | Actual fit, friction, loaded behavior and strap stability need current-prototype evidence. |
| Printing | H2D PLA project, one mechanical plate, no brims, required supports and finger-surface orientation are prepared and checked. | This is a mechanical fit set; P08/P09 and the real sensor/load hardware are not supplied by that six-piece print. |
| Electronics | Native PCB/schematic and manufacturing package exist; later assembly clarifications are recorded. | Actual supplied-board state, power behavior, battery behavior and installed fit need verification. |
| Firmware | Acquisition, status gating, calibration storage, tare, repetition debounce, peak accumulation, BLE v3 and power policy exist. Both normal and bench artifacts match their recorded source/artifact hashes. | `HARDWARE_QUALIFIED=false` intentionally remains. Hardware-specific measured parameters and calibration are not evidenced as complete. |
| Training app | Configurable curls, per-hand rest, timed cARC, click/haptics, local workout history, notes and workout CSV are implemented. | Real board/iPhone acceptance remains; several raw-session and peak-state paths need code changes. |
| Software checks | The existing `firmware/tools/test.sh` suite passed during this review. Normal and bench firmware manifests passed 14 source/artifact hash comparisons. | These tests cover domain logic, not every CoreBluetooth/UI/store lifecycle path and not physical hardware. |

Do not restart completed design work or remove qualification gates to make the device appear ready. Preserve the R15 form and the existing app behavior unless physical results identify a specific reason to change them.

## 2 Priority definitions

- **P0 — Establish a trustworthy measured prototype.** Close these before relying on loaded instrumented operation in a declared initial range.
- **P1 — Complete the requested everyday training experience.** Close the relevant items before claiming those modes, mounting configurations and recorded results are ready.
- **P2 — Complete the original resistance envelope.** This remains part of the original ambition but need not hold up a deliberately limited first working prototype.
- **P3 — Resolve optional extensions.** These are product decisions, not missing implementations of the current baseline.

Priority is not a strictly serial schedule. CAD/documentation work, software fixes and bench preparation can proceed in parallel. Calibration depends on the final physical configuration; high-force tests depend on an appropriately designed test setup and defined limits.

## 3 Prioritized backlog

### G01 P0 Establish the complete current build and release its manufacturing information

**Gap type:** Incomplete manufacturing definition and unconfirmed current assembly state.

The current print contains P01/P04/P05/P06/P11 and Q01. The complete device additionally needs the real sensor stack, rods, spring seats, selected springs or sleeves, functional fasteners, electronics and enclosure. Q01 must be removed for the working build. Verify existing parts against R15 rather than automatically replacing them.

A concrete documentation gap remains around the corrected H12 sensor backing/support and H23/H24/H25 keeper assembly. The October sensor-integration notes explicitly supersede the old H12 drawing and leave manufacturing tolerances, flatness, finish, finished threads and material/process details unassigned. Later R15 geometry is present, but the old October 11 manufacturing package cannot simply be treated as a current fabrication release.

**Work:** Record the actual printed/assembled revision and available components; reconcile a complete R15 bill of materials; issue the current sensor-stack drawings and inspection criteria; finish or inspect the functional hardware; fit P08/P09 with the actual PCB, battery, connectors and cable loops. Carry the R15 service sequence and stop geometry into the commissioning documents, replacing obsolete preload/cord instructions.

**Done when:** One identified assembly has a current parts list, correct functional hardware, inspectable manufacturing requirements, supported sensor retention, usable USB/button access and strain relief. No Q01 or printed metal-form substitute remains in its loaded force path. Supplier/order status is recorded if it still affects availability.

**Requirements:** MFG-01/02/05/06/07, SER-01–03, FOR-01–03, ELE-01/03. **Acceptance:** A02/A07. **Dependency:** None; starts now.

Evidence: [R15 assembly](review/inboard-straps-2026-11-08/MONTAGE.md), [print scope](print/bambu-R15-inboard-straps-2026-11-08/README.md), [superseded H12 drawing and unfinished manufacturing definition](review/flat132-finished-2026-10-22/finalization-notes.md), current [FeatureScript](fingerworker_mvp.fs).

### G02 P0 Confirm current hand fit and resolve the effective edge depth

**Gap type:** Physical acceptance plus an unresolved geometry requirement.

The closer integrated palm follows the user's feedback, but that feedback does not qualify the exact R15 print for both hands. The original 10 mm edge requirement is also not proven by the current 72 × 34 × 20 mm recess envelope.

**Work:** Check an unloaded current assembly with both hands over the full 30 mm stroke. Measure the actual finger-bearing depth and confirm that it gives the intended rounded climbing-edge contact. Inspect palm comfort, thumb space, finger-surface finish, guide play and off-center binding. Measure complete dimensions and assembled mass. Make localized changes only where the trial identifies a problem.

**Done when:** Both hands can perform the intended movement with comfortable, accessible contacts, no binding or interference, and an explicitly accepted effective edge depth. Record any deliberate change from 10 mm.

**Requirements:** USE-01–03/06, MEC-01–06, MFG-03/04. **Acceptance:** A01/A02. **Dependency:** Current unloaded fit assembly from G01; electronics can be qualified in parallel.

Evidence: [R15 geometry/status](review/inboard-straps-2026-11-08/final-specification.json), [print surface/process](print/bambu-R15-inboard-straps-2026-11-08/README.md), specification MEC-04/06.

### G03 P0 Commission and qualify the actual electronics

**Gap type:** Missing physical commissioning evidence; hardware changes depend on measured results.

The firmware is implemented and the existing binaries match the source. Valid force and device counts remain intentionally gated by `HARDWARE_QUALIFIED=false`. Turning that flag on is not the commissioning task.

**Work:** Confirm the real PCBA revision and assembly, battery-contact soldering and harness polarity. Upload the bench build and follow first-power checks: current-limited start, XIAO/core/bootloader pin behavior, analog rails and ramps, ripple, settling, sensor common mode, ADC register readback and DRDY. Test USB source changes. Measure initial charging behavior before relying on battery operation. Correct any hardware failures before qualifying the configuration.

**Done when:** The actual board and sensor have a recorded electrical test report, the build is verified on the board, provisional parameters are supported or replaced by measurements, and the qualification flag can be changed on evidence.

**Requirements:** ELE-02–05, FW-01–03. **Acceptance:** A07. **Dependency:** Actual PCBA and sensor availability; independent of much of the mechanical fit work.

Evidence: [qualification gate](firmware/Fingerworker/Config.h), [first power](electronics/procurement/FIRST_POWER.md), [firmware instructions](firmware/README.md), [latest local DFM record](electronics/jlc-review-2026-11-04/placement-review.json).

### G04 P0 Establish an initial mechanical working range and switch behavior

**Gap type:** Open acceptance limits and missing physical load evidence.

There is no qualified device working-load rating. A nominal spring force or sensor rating cannot provide one. The R15 travel stops are on the floating P05 yoke and preserve the intended sensor path; old descriptions of fixed-frame full-travel bypass stops do not describe this revision.

**Work:** Define the initial supported spring configuration, maximum working force, centered/off-center cases and pass/fail deformation limits. Test the actual print process, rear-gate screws/inserts, guide, yoke, pusher and sensor support using a controlled external setup. Verify that the switch activates before P05 stop contact, remains physically perceptible, and gives the specified held/release/wake/open-wire behavior. Check for unintended frame contact under deflection. Retain current LOW-state force inhibition.

**Done when:** A named assembly has a documented initial operating range and correct switch timing/fault behavior. Any failure results in a specific correction and retest, not an unsupported 500 N claim.

**Requirements:** MEC-01/02, FOR-01–04/10, RES-02/03, FW-04–08. **Acceptance:** A06/A09. **Dependency:** G01/G02; electrical fault tests also need G03.

### G05 P0 Calibrate the complete device in its initial operating configuration

**Gap type:** Missing assembled-device calibration/performance evidence and numerical measurement targets.

The firmware supports bounded multipoint calibration, separate mode slots and tare. The missing part is measured accuracy through the complete mechanism, including friction and return-stop preload effects.

**Work:** Set valid force range, maximum permitted error, repeatability and drift limits. Apply known loads upward and downward, centrally and off-center. Determine the usable low-force region, save/reload calibration, verify tare preserves absolute/raw values, and compare recorded peaks with the applied signal. Use at least the implemented two points and additional points where needed to characterize behavior. Repeat for each subsequently released mode or mounting arrangement.

**Done when:** Actual force readings meet the declared limits across the initial released range and reproduce after restart. Values outside the calibrated range remain invalid. Initial hand force obscured by preload is described rather than claimed to be recovered by calibration.

**Requirements:** FOR-03–09, FW-02/09. **Acceptance:** A08/A10. **Dependency:** G03/G04 and a fixed physical resistance/support configuration. A later spring/support change may require a recheck.

### G06 P1 Correct peak availability and provenance in the app

**Gap type:** Confirmed implementation defect; can be fixed without hardware.

The measurement screen always formats the numeric peak, initially zero. `RecordedSession` saves a numeric peak but not its availability/provenance. Selecting a saved session restores the number without restoring the source flag, so the source label can reflect another session. An acknowledged reset epoch with no valid peak can also retain the initialized zero.

**Work:** Represent unavailable/pending/valid peak states explicitly, retain whether a valid peak came from the acknowledged device epoch or received samples, and persist/restore that information. Preserve a real measured zero as distinct from unavailable. Load legacy sessions without inventing provenance.

**Done when:** No valid peak yet displays “—”; valid historical peaks survive later current-force faults; reopened sessions show their own accurate peak/source state. Add tests around store/session selection and archive compatibility, not just packet parsing.

**Requirements:** FOR-09, FW-02, BLE-02/03, APP-12, DAT-01/06/07. **Acceptance:** A10/A14. **Dependency:** None; complete before relying on reported peak results in G09.

Evidence: [always-numeric peak UI](ios/Fingerworker/FingerworkerApp.swift), [peak model/tracker](ios/Fingerworker/Measurement.swift), [save/select/accept behavior](ios/Fingerworker/DeviceStore.swift).

### G07 P1 Integrate and verify the requested softer spring option

**Gap type:** Candidate solution not released against current CAD.

The RDF2127 pair with 22 mm effective spacers predicts 66.9% of DF2194 resistance, matching the requested reduction. Its checks are against frozen R9; native R15 still offers the original pairs.

**Work:** Integrate the candidate as an identified R15-compatible configuration, update the model/BOM/assembly instructions and repeat current-geometry clearance checks. Confirm the actual spacers, coil guidance, full travel and physical loading/unloading curve. Inspect spacer deformation and creep; recheck force calibration as needed.

**Done when:** The softer configuration is buildable from one consistent release and delivers the accepted approximately two-thirds curve with reliable movement and return. It is not automatically labeled suitable for cARC.

**Requirements:** RES-01–04, MFG-07, FOR-06/07. **Acceptance:** A03/A08. **Dependency:** Digital work can start now; physical completion needs G01/G04/G05 as applicable.

Evidence: [softer spring candidate and R9 scope](review/flat132-softer-springs-2026-10-26/README.md).

### G08 P1 Establish a genuinely usable light cARC configuration

**Gap type:** Mechanical performance unresolved; app timer already implemented.

The existing lighter pair starts at about 39.7 N nominal spring reaction; the proposed softer pair still starts around 26.5 N. Neither figure establishes comfortable prolonged light partial-stroke exercise. Preload can also obscure initial hand-force measurement.

**Work:** Determine the useful resistance and movement range from actual use. Select or develop a sufficiently light matched configuration while preserving reliable return and guidance. Check measured low-force behavior separately from the timer. Validate any optional force reminder only in the usable calibrated region.

**Done when:** The user can perform the intended light timed movement comfortably without reaching the end switch, and any force feedback is meaningful in that region. A disconnected timer can remain usable even when force feedback is unavailable.

**Requirements:** RES-05, FOR-05, APP-06/07. **Acceptance:** A03/A08/A12. **Dependency:** G02 and measured mechanism behavior; G07 may help but is not assumed sufficient.

### G09 P1 Complete a real iPhone and device acceptance session

**Gap type:** Physical integration acceptance, not missing core app features.

**Work:** Install the current app on the user's iPhone and test against the qualified device: discovery, MTU, live values, independent hand recovery, counts, peak reset/acknowledgement, short acquired peaks, stale data, disconnect/reconnect and reboot. Verify click/haptics, silent mode, held-switch behavior and cARC suppression. Finish a curl workout and timed workout, reopen their logs, export them and verify interruptions. Observe background/lock-screen behavior against the specified foreground-guidance limits.

**Done when:** One end-to-end recorded test demonstrates the complete user workflow on real hardware with the expected counts, valid force, cues and recoverable records. No simulator result is used as evidence of RF or physical cue performance.

**Requirements:** BLE-01–05, APP-01–12, DAT-01–07, USE-03/05. **Acceptance:** A10–A14. **Dependency:** G03–G06; resistance-specific use also needs the relevant mechanical configuration. G11 changes should be included in final logging acceptance.

Evidence: [implemented app behavior](ios/README.md), [existing verification and physical gaps](ios/TRAINING_VERIFICATION.md).

### G10 P1 Qualify isometric and externally mounted operation

**Gap type:** Physical mode-specific acceptance.

The 81 mm sleeve pair, 15 mm approach, floating load path and two inboard strap positions are designed. They still need actual sleeve matching, support/load checks and installed-strap stability evidence.

**Work:** Inspect and test both matched steel sleeves and the isometric calibration slot. Test the actual 25 mm straps on the intended thigh/round support, including slip, rotation, folded ends, loaded deflection and full motion. Check force readings when external anchoring replaces palm reaction. Inspect the sensor keeper during mode changes.

**Done when:** Each claimed mode has correct operation, supported load limits and valid calibration. Dynamic counting stays off in isometry; strap routing stays clear of movement; the sensor remains retained without a load bypass during service.

**Requirements:** USE-04, RES-06, FOR-01–08/10, STR-01–04, SER-01–03. **Acceptance:** A02/A04/A05/A08. **Dependency:** G01–G05; this extends the initial dynamic release rather than replacing its tests.

### G11 P1 Complete linked raw recording and raw CSV context

**Gap type:** Confirmed implementation gaps; can be fixed without hardware.

Two boundaries remain. First, raw recording is started only at workout start/resume. A cARC or manual workout that starts offline and connects later can receive force summaries without starting a linked raw archive. Explicit disconnect/reconnect can leave the same gap because timed cARC keeps running. Second, raw CSV omits session UUID, workout UUID, start time and completion/interruption metadata that are already present in JSON. The README currently overstates the raw CSV workout link.

**Work:** Start an appropriately linked recording segment when a continuing workout gains a connection; preserve earlier gaps and avoid duplicate/conflicting recordings. Extend raw export with versioned session context and accurate peak metadata. Update the documentation. Keep raw device milliseconds distinct from UTC session time.

**Done when:** Offline-start→connect, radio loss/reconnect and explicit disconnect/reconnect preserve the workout and identify its recorded intervals. Exported raw data can be associated with its workout and interruption/completion state without needing an unrelated JSON file. Existing archives remain readable.

**Requirements:** DAT-01/04/05/07, APP-07/12, BLE-04. **Acceptance:** A12/A14. **Dependency:** Can start now; coordinate archive schema with G06.

Evidence: [recording start hooks](ios/Fingerworker/TrainingStore.swift), [disconnect/recording lifecycle](ios/Fingerworker/DeviceStore.swift), [raw CSV fields](ios/Fingerworker/Measurement.swift).

### G12 P1 Establish everyday reliability and power performance

**Gap type:** Open numerical targets and physical qualification.

**Work:** Set the intended cycle count/load profile, permissible wear/creep, storage/use temperature and moisture expectations, minimum active runtime and standby expectation. Measure repeated and sustained loading, straps and latch durability, post-test force drift, actual battery current/runtime, low-voltage shutdown/recovery, charging time/temperature and standby persistence. Validate the PLA process under the agreed storage conditions, including the intended car context. Optimize power or change material only where the results require it.

**Done when:** Declared everyday-use claims have recorded evidence for the actual configuration. The 4–8 h budget estimate and below-100 µA standby goal are not presented as achieved. Repeat relevant calibration/functional checks after endurance testing.

**Requirements:** FOR-07/10, STR-04, MFG-02/03/06, ELE-02/05/06, FW-03/09, USE-01. **Acceptance:** A06/A08/A15. **Dependency:** Qualified initial prototype; targets fixed before pass/fail testing. Detailed endurance need not block an unloaded fit trial.

### G13 P2 Resolve and complete the original resistance range

**Gap type:** Unfulfilled original performance objective and scope decision.

There are two native spring choices, with nominal endpoints around 238 N and 289 N, plus the softer candidate. That is not a released three-to-eight-level range and does not meet the original approximately 490–500 N total-resistance objective.

**Work:** Explicitly retain or revise the upper target and define the useful resistance levels. If retained, develop a matched high-range configuration and assess every affected structural/measurement component, rather than simply fitting stronger springs. Release identified configurations with measured force curves and load/endurance results. Do not restore removed preload knobs by default.

**Done when:** The agreed range and level count are met, documented and physically qualified, or the owner deliberately revises the specification. Lower-force prototype operation may be released earlier with a clearly limited range.

**Requirements:** RES-01/07, FOR-10, MFG-07. **Acceptance:** A03/A06/A08. **Dependency:** Initial mechanism performance and target decision; high-force validation follows engineering work.

### G14 P3 Decide whether to extend the current product scope

Durable device-offline sessions, an onboard display/sound, BLE remote mode/tare/power, cloud sync and continuous locked-screen guidance are not implemented current-baseline requirements. Additional substitution of metal load parts with printed parts is also a development option requiring validation.

**Work:** Decide which, if any, belong in the next release, with explicit benefit and acceptance criteria. Retain existing mechanical standalone use, running-device totals and phone-based guidance as the present baseline.

**Done when:** Optional extensions are either deferred explicitly or added as separately scoped requirements. Their absence is not counted as a failed current requirement.

**Requirements:** USE-05/06 and specification section 15. **Dependency:** Product decision; not a prerequisite for G01–G13.

## 4 Requirement coverage

“Implemented” here means present in CAD/code, not physically qualified. This grouped matrix covers all 82 numbered requirements without assigning a misleading completion percentage.

| Specification requirements | Comparison | Remaining work |
| --- | --- | --- |
| USE-01–06 | Portable form, alternating-hand app, straps and limited standalone operation exist in design/code. Full real-use evidence incomplete; optional standalone expansion remains a decision. | G02/G09/G10/G12/G14 |
| MEC-01–06 | R15 nominal geometry and service checks pass. Both-hand fit, physical movement, dimensions/mass and effective 10 mm edge need confirmation. | G01/G02/G04 |
| RES-01/07 | Original range/level count and approximately 490–500 N endpoint unmet by current native options. | G13 |
| RES-02/03 | Matched-pair/fixed-geometry baseline defined; actual setup and force curve need inspection. | G01/G04/G05 |
| RES-04 | Two-thirds candidate designed and checked against R9, not integrated into current native R15. | G07 |
| RES-05 | cARC app exists; suitable low-resistance mechanics and useful low-force sensing unresolved. | G08 |
| RES-06 | Isometric geometry/calibration capability exists; physical mode acceptance missing. | G10 |
| FOR-01–05 | Correct sensor-bearing R15 geometry and validity policy exist; actual parasitic loads, deflection and low-force behavior need measurement. | G01/G04/G05/G08/G10 |
| FOR-06–08 | Calibration/tare code exists; complete-device calibration and numerical criteria need evidence. | G05/G10/G12 |
| FOR-09 | Firmware peak accumulation/protocol implemented; app availability/provenance defects and hardware peak tests remain. | G06/G09 |
| FOR-10 | No declared, physically qualified working-load/life envelope. | G04/G12/G13 |
| STR-01–04 | Slots/routing digitally checked; actual strap fit, rotation/slip and loaded durability need acceptance. | G10/G12 |
| SER-01–03 | R15 service paths and Q01 separation documented; real-part service demonstration needed. | G01/G02/G10 |
| MFG-01–06 | Parts and mechanical PLA job defined; complete functional kit, real fits and load qualification need closure. | G01/G02/G04/G12 |
| MFG-07 | R15 print assets are revision-bound; full manufacturing/commissioning sources still include superseded material. | G01/G07/G13 |
| ELE-01–05 | Circuit, packaging and power policy designed/implemented; actual fit, supply, charge and button evidence incomplete. | G01/G03/G12 |
| ELE-06 | Runtime/standby/recharge performance is estimated, not established. | G12 |
| FW-01–03 | Implemented; current artifacts verified; hardware qualification gate intentionally false. | G03/G05 |
| FW-04–08 | Logic implemented; actual switch position, feel and combined fault behavior need verification. | G04/G09 |
| FW-09 | Runtime counter/peak and calibration persistence implemented; real restart/reconnect acceptance remains. | G05/G09/G12 |
| BLE-01–05 | Current contract implemented; real-device MTU, timing, gaps, epochs and restart handling need acceptance. | G09 |
| APP-01–08 | Guided curls/cARC and interruption rules implemented and domain-tested; real use remains. Background pause is intentional. | G08/G09 |
| APP-09–11 | Click/haptics and suppression implemented; physical audibility/latency/lifecycle acceptance remains. | G09 |
| APP-12 | Free measurement exists; peak-state defect and real acquisition/stop tests remain. | G06/G09 |
| DAT-01–03 | Local persistence, workout results and timeline implemented; end-to-end restart verification remains. | G06/G09 |
| DAT-04/05 | Ordinary linked workouts/workout CSV exist; late connection recording and raw export context are incomplete. | G11 |
| DAT-06/07 | Raw-stream/termination limits recognized and old archives load; peak metadata changes need conservative migration. | G06/G09/G11 |

## 5 Recommended execution sequence

Start three parallel tracks: **G01/G02** for the actual mechanical build, **G03** for the board, and **G06/G11** for the confirmed app defects. Integrate the softer candidate through **G07** while current manufacturing information is reconciled.

Converge on **G04 → G05 → G09**: establish the initial working range, calibrate it, and demonstrate the complete real-phone workflow. Add the desired light cARC behavior through **G08** and separately qualify straps/isometry through **G10**. Close everyday-use reliability in **G12**. Resolve the full resistance range in **G13** without treating the original upper target as silently canceled.

The next milestone is one identified, complete device that moves comfortably, produces trustworthy force/counts in a declared range, finishes a real guided workout and reopens an accurate saved result. The existing CAD and app provide most of the design foundation for that milestone.

## 6 Review evidence and limits

This was a source/report comparison with one fresh run of the existing software test suite and read-only firmware artifact hash verification. No hardware was flashed, printed, powered, calibrated or load-tested during this review. No software or CAD fixes were applied.

Primary records: [R15 release](review/inboard-straps-2026-11-08/final-specification.json), [connected print preparation](print/bambu-R15-inboard-straps-2026-11-08/connected-ready-delivery.json), [softer spring conversion](review/flat132-softer-springs-2026-10-26/README.md), [sensor manufacturing notes](review/flat132-finished-2026-10-22/finalization-notes.md), [first power](electronics/procurement/FIRST_POWER.md), [firmware](firmware/README.md), [app implementation and limitations](ios/README.md), and [recorded software verification](ios/TRAINING_VERIFICATION.md).

The older acceptance document remains a useful checklist, but its preload, cord, sleeve and stop descriptions must be reconciled with R15 before it is used as a commissioning procedure. Supplier snapshots similarly describe their recorded dates and are not proof of current delivery status.
