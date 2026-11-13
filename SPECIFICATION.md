# Fingerworker device specification

Version 1.0 draft · 8 November 2026 · Product owner Jonas Hilti

Fingerworker is a compact, portable finger trainer for climbing. The user pulls a finger edge toward a fixed palm support against resistance, or anchors the device to an external support. The complete system measures force, counts full repetitions, guides training on an iPhone and retains a useful training history. It should feel comfortable, look simple and be easy to assemble, carry and use.

The product must support both repeated finger curls and sustained, light, time-based exercise. Its mechanical design must also retain the established isometric configuration. The focus is training; rehabilitation protocols and medical claims are outside this specification.

This draft consolidates the requested product behavior and the current engineering baseline. The mechanical reference is **Flat132 R15**. The software reference includes the repetition-training app, the 6 November end-stop feedback and the 7 November timed cARC mode. A working-load rating, measurement accuracy, endurance and battery runtime remain release decisions requiring physical evidence.

## 1 Requirement status and precedence

Four labels distinguish intent from implementation:

| Label | Meaning |
| --- | --- |
| Required | A user requirement or necessary behavior for the requested system. “Shall” states a requirement, not that it has passed testing. |
| Baseline | The selected or implemented solution at the date above. Dimensions are nominal unless explicitly measured. |
| Candidate | A proposed solution that has not been integrated or qualified for the complete current device. |
| Open | A parameter or scope decision that must be resolved before the relevant release claim. |

Latest explicit user decisions take precedence over earlier proposals. Revision-specific release records take precedence over historical passages in the general README and procurement documents. Supplier correspondence governs the purchased assembly scope. Software source and current protocol documents govern implemented behavior.

The following decisions are settled for the current prototype:

- Use a close, broad palm support integrated into the main frame, without a separate sleeve or palm mounting screws.
- Simplify shapes, reduce the number of parts and avoid small loose printed pieces where integration preserves function.
- Allow click-together positioning and unloaded assembly; retain screws needed to secure the loaded mechanism.
- Remove both the central preload adjuster and the rear return-stop adjusters. Fixed installation compression remains.
- Use PLA as the standard prototype printing material, without requiring TPU or a second material.
- Provide two 25 mm mounting straps through openings inside the baseplate on both sides.
- Provide the end-stop click through the iPhone.
- Preserve the request for approximately two-thirds of the resistance of the fitted DF2194 spring pair.
- Deliver the current mechanical print set on one H2D plate, without brims and with required supports retained.

Earlier cord eyelets, separate palm components, 86 mm isometric sleeves and adjustable preload assemblies are historical designs. The removal of electronics parts from the latest print job applies to that mechanical fit build; electronics remain part of the complete product. [S1–S5, T1–T5]

## 2 Intended use and system scope

**USE-01 — Portable training.** The device shall support seated, low-setup training away from a climbing wall, including stationary-car or passenger use. It shall not need a gym installation, suspended weights or mains power for ordinary mechanical exercise.

**USE-02 — Finger curl action.** The finger contact shall act as an edge or recess that the fingers pull toward the palm heel. The form shall support the intended climbing-related finger curl action and a comfortable thumb position. The user's actual hand is the primary fit reference for this prototype.

**USE-03 — Both hands.** The same device shall be usable with the left and right hand. The app shall track each hand separately and guide alternating work and recovery.

**USE-04 — External support.** The device shall accept mounting to a round object or the user's thigh using two straps. Where the external mounting replaces palm reaction, the load path and calibration shall be checked in that configuration.

**USE-05 — Standalone operation.** Mechanical exercise shall work without the phone. Force acquisition and the cumulative repetition counter shall operate on the qualified powered device without a live BLE connection. Phone guidance, audible feedback and detailed session storage belong to the connected experience in the current baseline.

**USE-06 — Simple and elegant form.** The product shall be as flat and compact as practical, minimizing protrusions, unnecessary adjustment hardware, excess material and awkward assembly steps. The intended experience is to select a resistance, pick up or attach the device and train.

The original ambition of “as standalone as possible” remains relevant. The present hardware does not provide a standalone display, onboard sound or durable offline session archive. Those features are not silently assumed to exist; their inclusion is an open product decision. The current device preserves counters and peaks across a radio interruption only while its relevant run and power state survive. [T6, T7, S7–S9]

## 3 Training modes

| Mode | Required physical behavior | Counting and app behavior |
| --- | --- | --- |
| Finger curls | Repeated travel against a matched spring pair; return after release. | A qualified full stroke can generate one repetition. Guide alternating hands, sets and independent recovery. |
| Timed cARC | Light, comfortable repetitive movement, including partial strokes that do not reach the end switch. | Progress by actual exercise time. Do not require or invent repetitions. Offer rhythm cues and optional valid force feedback. |
| Isometric measurement | Replace both springs with the matched rigid sleeve pair and take up the approach travel before loading. | Measure sustained force through the sensor. Do not require end-stop activation or dynamic repetition counting. |
| Free measurement | Display and record qualified force independently of a guided workout. | Show measurement status, chart, peak and recorded session. |

The curl protocol originated from the user's request for approximately **10–20 repetitions per hand, six sets and about three minutes of recovery per hand**. Current defaults are six sets of 15 repetitions per hand. These are configurable preferences, not a validated prescription.

“cARC” is the app's label for the requested timed, low-resistance mode. A timer, spring selection or force threshold does not establish an aerobic training zone. Isometric measurement is part of the mechanical and measurement baseline; a separate guided isometric workout program is not currently specified. [T8, T9, S9]

## 4 Mechanical form and ergonomics

**MEC-01 — Motion.** The mechanism shall provide a nominal **30 mm usable finger-carriage stroke** in the fixed R15 configuration. The carriage shall move and return without binding, lifting off its guide, rotating excessively or contacting the user's hand in an unintended place.

**MEC-02 — Guidance.** A central sliding guide shall control carriage alignment and resist rotation. The two actual steel rods shall guide the spring assemblies. Real off-center finger loading shall be included in validation; a centered CAD motion check is insufficient.

**MEC-03 — Palm contact.** The palm support shall form one continuous part with P01. It shall retain the short reach established by the user's physical fit feedback, spread pressure over a smooth surface and avoid an exposed narrow sensor-support edge.

**MEC-04 — Finger contact.** Contact surfaces shall be smooth and free of support scars or sharp edges. Print orientation shall keep supports off the working finger surfaces. The original request specified a **10 mm climbing edge with rounded corners**. The current recess envelope below does not establish that effective edge depth; it shall be checked against the intended finger contact. The actual grip shall be checked for both hands throughout the stroke.

**MEC-05 — Assembly access.** The carriage, rods and sensor stack shall have real insertion and removal paths. Assembly shall not require forcing parts past a permanent obstruction or tightening screws to straighten a binding guide.

**MEC-06 — Current dimensions.** The following values define the R15 nominal baseline, rather than population-wide ergonomic claims:

| Feature | R15 baseline |
| --- | --- |
| Main baseplate width | 132 mm |
| P01 width including catch bosses | 132.4 mm |
| Complete assembly maximum width at rear latch arms | 135.2 mm |
| Base floor thickness | 6 mm |
| Nominal longitudinal base rectangle | 151 mm |
| Finger recess | 72 mm clear width × 34 mm front-to-back × 20 mm depth |
| User stroke | 30 mm |
| Palm contact size | 76 mm across the hand × 18 mm in the pull direction |
| Palm crown height | Z33 mm in the R15 CAD coordinate system |
| Palm rounding | 14 mm wrist-side radius; 3 mm sensor-side radius; 2 mm end radius |
| Preload and rear-stop settings | Fixed at p = a = 0 |
| Remaining switch-cam trim | −0.8 to +0.8 mm |

The original contact-to-contact reach of approximately 100 mm open and 70 mm pulled established the 30 mm stroke. Later requests to bring the palm support closer supersede those absolute reach dimensions. The final complete length, height and assembled mass shall be taken from the released configuration and measured prototype. Older overall-envelope comments shall not be reused as an R15 certification. The hand scan is an approximate geometry aid; comfortable reach and contact require the user's physical fit check. [S1–S3, T10]

## 5 Resistance and isometric conversion

**RES-01 — Selectable resistance.** Resistance shall be changed through clearly identified, matched configurations. The original request envisaged roughly **three to eight levels**. The present solution provides interchangeable spring pairs; it does not yet provide a qualified three-to-eight-level range. That range remains an open completion item rather than a reason to restore the removed preload knobs.

**RES-02 — Symmetric pairs.** Both springs shall be the same specified type. A spring shall not be mixed with an isometric sleeve. Spring changes shall be performed with stored force controlled and the mechanism unloaded.

**RES-03 — Fixed geometry.** In R15, original springs occupy **96 mm at rest**, reducing to 66 mm after 30 mm travel. Removing adjustment does not remove spring preload: the DF2194 pair starts with 6 mm compression per spring, and DF2185 with 9 mm.

For a linear spring pair, the nominal relationship is `F(u) = 2 × k × (L0 − Lrest + u)`. This describes spring reaction, excluding friction, tolerances and force taken by other contacts. It is not a calibration of finger force.

| Configuration | Rate per spring | Free length | Nominal pair force at 0 / 10 / 20 / 30 mm user travel | Status |
| --- | --- | --- | --- | --- |
| Two Febrotec 0X-DF2194 | 3.307 N/mm | 102 mm | 39.68 / 105.82 / 171.96 / 238.10 N | Native R15 option; fitted pair was reported by the user. |
| Two Febrotec 0X-DF2185 | 3.709 N/mm | 105 mm | 66.76 / 140.94 / 215.12 / 289.30 N | Native R15 stronger option. |
| Two Febrotec 0X-RDF2127 with matched spacers | 2.212 N/mm | 80 mm | 26.54 / 70.78 / 115.02 / 159.26 N | Candidate softer conversion; current-revision integration and physical qualification pending. |

**RES-04 — Softer curl option.** The requested lighter configuration shall aim for approximately **two-thirds of the fitted DF2194 resistance** over the useful stroke. The current candidate predicts 66.9% using two RDF2127 springs and two spacers with **22 mm effective axial length**. Each spacer is 24 mm overall including its 2 mm centering pilot. Its shoulder, not the pilot tip, sets the spring spacing.

The conversion was geometrically checked against frozen R9 and has not become the native R15 spring selection. Before use, reconcile it with R15, confirm coil guidance and full travel, and measure the installed force curve. Remove these spacers together with the shorter springs when reverting to original springs or isometric sleeves.

**RES-05 — Light timed exercise.** A cARC resistance configuration shall permit comfortable light partial strokes and release. The two-thirds curl conversion must not automatically be declared sufficiently light for cARC. Even its nominal rest force is about 26.5 N. The needed minimum resistance and usable low-force measurement region remain open.

**RES-06 — Isometry.** Isometric conversion shall use **two steel sleeves, OD16 / ID8 × 81 mm**, with flat, deburred ends and pair lengths matched within 0.05 mm. The R15 approach travel is **15 mm** before they seat. Force shall continue through the floating yoke and sensor. The app/firmware shall use the isometric calibration slot; dynamic counting shall be disabled. [S1, S4]

**RES-07 — Upper resistance objective.** The original maximum was approximately **50 kg-force total resistance**, equivalent to about **490 N**, commonly rounded to a 500 N design objective. This is the total device resistance, not the force of each spring. The current native pairs reach approximately 238 N and 289 N at full stroke, so they do not fulfill that original upper dynamic-resistance objective. The request for a softer option adds a lower range; it does not itself confirm cancellation of the upper objective. Retaining or revising that objective is an explicit release decision, separate from establishing a safe structural rating. [T10, T11]

## 6 Load path and force measurement

**FOR-01 — Intended load path.** Exercise reaction shall pass from P04 through the matched springs or isometric sleeves, into the floating P05 yoke, through the real H02 pusher, H01 sensor and H12 support, and into the fixed P01 reaction structure. Relevant P05 travel-stop contact must also remain in the intended sensor-bearing arrangement. P05 shall not be fixed directly to P01.

**FOR-02 — Sensor fit.** Use the actual **TE FX1901-0001-0200-L** geometry. The baseline is the 200 lbf compression variant, with an unscaled manufacturer model, approximately 25 mm body diameter and 7.95 mm axial thickness. Sensor support, cable clearance and pusher alignment shall match that geometry.

**FOR-03 — Avoid load bypass.** Guides, retainers, palm contact, mounting straps, printed fixtures and hard stops shall not create an unrecognized parallel measurement path. Guide friction and unequal finger loading shall be included in complete-device calibration and error assessment.

**FOR-04 — Qualified measurement region.** Only readings inside the qualified mechanical and calibrated electrical region shall be reported as valid. R15's full-travel stop faces belong to the floating P05 yoke and are designed to transmit endpoint force through the sensor; they are not the old fixed-frame bypass arrangement. The current firmware nevertheless invalidates force whenever the end-stop input is LOW. Retain that behavior until the complete endpoint measurement is deliberately qualified and the firmware contract changed. Unintended frame contact under load remains a condition to exclude in physical tests.

**FOR-05 — Low-force limitation.** Fixed spring preload and the return-stop reaction can obscure the initial hand-force region. The displayed value after tare is not automatically the full absolute finger force at rest or in a short initial movement. This is particularly relevant to cARC feedback.

**FOR-06 — Calibration.** Calibrate the complete functional assembly using known external loads. Use separate dynamic and isometric calibration slots, each with 2–8 actual load points. Test increasing and decreasing loads and centered and off-center pulls. Do not derive the calibration solely from spring catalogue rates.

**FOR-07 — Calibration integrity.** Interpolate only within the calibrated range; do not extrapolate. Preserve calibration version and integrity checks in nonvolatile memory. An invalid, missing, truncated or out-of-range calibration shall prevent valid-force output. Recheck calibration after changes to the sensor support, spring configuration, guide, print structure or mounting arrangement that affect the force path.

**FOR-08 — Tare.** Tare shall change the displayed offset while retaining absolute calibrated force and signed ADC data. Tare shall not conceal an absolute overload or convert a fault into a valid measurement. The current device has no qualified software overload limit; any future overload indication must use the established working limit independently of tare.

**FOR-09 — Peak provenance.** Device peaks shall accumulate from every freshly acquired valid ADC sample before BLE publication. The app shall distinguish a device-sampled peak from a peak calculated only from received notifications. Invalid samples shall not update the peak.

**FOR-10 — Structural capacity.** The complete assembled device shall carry its declared working load in every released use configuration, including the specified off-center and repeated loading cases. The original approximately **490–500 N total-resistance objective is not a qualified working-load rating**. Neither the sensor's capacity, nominal spring force, 24-bit ADC nor a passed CAD check establishes device strength or measurement accuracy. Maximum working force, proof conditions, accuracy, repeatability, drift and life require explicit release values and tests. [S1, S6–S8, T10]

## 7 Mounting straps and service

**STR-01 — Two mounting positions.** Provide four rounded inboard slots for two 25 mm straps. Each strap shall wrap beneath the chosen object and anchor to both sides of the baseplate at its own longitudinal station.

| Feature | Baseline |
| --- | --- |
| Slot size | 27 × 4 mm |
| Longitudinal stations | X28 and X65 mm; 37 mm apart |
| Lateral centers | Y−57.5 and Y+57.5 mm |
| Strap thickness through a slot | Maximum 2 mm single layer |
| Slot ends / upper edge | R2 / R0.8 mm |
| Lower edge treatment | 0.8 mm chamfer at 45° |
| Nominal outer ligament | 6.5 mm; minimum 4.2 mm at the top surface |
| Nominal inner remaining section | 17.5 mm |

**STR-02 — Routing.** Each strap end shall rise through its slot, turn over the outer bearing strip, descend outside the frame and fasten securely back onto its own strap. Doubled material shall remain outside the frame. No strap shall cross above the grip or springs.

**STR-03 — Clearance.** With the actual straps installed, the full 30 mm stroke shall remain free. R15 nominal checks give 2.26 mm minimum strap clearance to moving spring seats and 3.5 mm to the rear grip bridge. Physical strap thickness, fold shape and frame deflection shall be checked.

**STR-04 — Stability.** The assembly shall stay securely positioned during the intended exercise without strap slip, rotation, edge damage or harmful pressure concentration on the thigh. The close 37 mm spacing makes a real rotational-stability check necessary. Strap length shall suit the intended object plus both secure folds; a universal fixed length is not specified.

**SER-01 — Reversible assembly.** The rear gate, rods, carriage, sensor and electronics shall be serviceable without cutting the main frame. Remove straps before disassembly or electronics service.

**SER-02 — Retained sensor.** The sensor shall remain supported during spring replacement. Its retaining parts shall not bypass measurement load.

**SER-03 — Fixture removal.** Q01 is only a spring-free substitute used to assess fit. It shall be completely removed before fitting the real sensor stack, springs, spring seats or isometric sleeves. Printed rod or metal-part replicas shall not be substituted for functional hardware in a loaded build.

Detailed removal movements and fastener instructions remain in the R15 assembly guide. [S1–S3]

## 8 Parts and manufacturing

**MFG-01 — Printed device parts.** The complete R15 design contains seven printed device bodies:

| Part | Function |
| --- | --- |
| P01 | Main frame, integrated palm support and strap slots |
| P04 | Moving finger carriage |
| P05 | Floating force-transfer yoke |
| P06 | Single rear gate retaining both rods |
| P08 | Removable electronics tray |
| P09 | Electronics lid with integrated cable features |
| P11 | Adjustable switch cam |

**MFG-02 — Click assembly.** Click features shall locate and retain parts for unloaded assembly and fit assessment. Loaded spring operation shall retain the four specified H30 M3×8 gate screws and suitable inserts. Functional switch and sensor hardware shall remain where required. Easy assembly does not imply that every joint is screw-free under load.

**MFG-03 — Prototype process.** Use Bambu H2D, a 0.4 mm standard nozzle and PLA. The present mechanical package generally uses 0.2 mm layers, four walls and 20% Gyroid infill. P11 uses 0.1 mm layers; P11 and Q01 use 100% infill. The four strap-bearing regions also receive local 100% infill. Qualified strength shall be tied to the actual filament, orientation and process used.

**MFG-04 — Surface and cleanup.** All six objects in the current mechanical print job shall have no brim. Necessary supports shall remain accessible for removal, and working finger surfaces shall have no support contact. Small functional P11 remains a justified exception to the preference against tiny parts; its first-layer adhesion requires inspection.

**MFG-05 — Current print scope.** The one-plate set contains P01, P04, P05, P06, P11 and the unloaded Q01 fixture. Use the already available real rods. P08 and P09 are excluded from this print job, not from the complete device. The saved PLA Basic project estimates about **10 h 49 min and 234 g**; this is a slicer estimate, not assembled product mass or a requirement for all later revisions.

**MFG-06 — Metal and purchased components.** Keep real steel rods, force sensor, pusher, springs or isometric sleeves, functional seats, screws, inserts and other load hardware until a replacement is explicitly qualified. The user's preference for extensive 3D printing permits further simplification; it does not establish that present PLA replicas can carry the operating load.

**MFG-07 — Release consistency.** Each build package shall identify its revision, source model, compatible parts, print profile and assembly guide. Replacing a single part shall state whether old parts remain compatible. CAD, STEP, STL, 3MF and bill of materials shall agree. [S1–S5]

## 9 Electronics and power

The current electronics baseline is:

| Function | Selected implementation |
| --- | --- |
| Controller and BLE | Seeed XIAO nRF52840 102010448, original non-Sense/non-Plus, without headers |
| Force conversion | TI ADS1220IPWR, 24-bit differential ADC, gain 8 |
| Sensor | TE FX1901-0001-0200-L |
| End switch | Omron SS-01GL2, NC/COM wiring |
| Digital supply | 3.3 V |
| Analog supply | 5 V bridge excitation, ADC analog supply and ratiometric reference |
| Boost and regulation | TPS61041DBVR followed by TPS7A2050PDBVR |
| Battery | Protected 1S 100 mAh LiPo; current prototype selection Adafruit 1570 |
| Charge system | XIAO charger, nominal 50 mA configuration |
| User button | Panasonic EVQPUC02K |
| Carrier PCB | 19.5 × 68.5 × 0.8 mm, four copper layers |

**ELE-01 — Integrated packaging.** PCB, battery, switch wiring and sensor wiring shall fit the intended enclosure with insulation, strain relief, connector access and space for cables. No fastener, clip or moving part shall press into the cell. USB access and button operation shall remain usable after assembly.

**ELE-02 — Charging and supply.** The device shall support battery-powered operation and the designed USB operation without a battery. Confirm charger current, charge voltage, temperature and actual battery-harness polarity on the assembled hardware.

**ELE-03 — Assembly interfaces.** Solder both XIAO underside battery contacts, U1.19 BAT+/VBAT and U1.20 BAT−/GND, to the carrier's top-side landing pads in addition to its castellations. Continuity and function shall be checked during bring-up. Extra supplier X-ray or custom electrical-test services are not part of the latest requested purchase scope.

| Connection | Required baseline mapping |
| --- | --- |
| J1 battery | Pin 1 positive/VBAT; pin 2 GND; verify the real cable |
| J2 sensor | 1 EXC+ red; 2 SIG+ yellow; 3 SIG− white; 4 EXC− black |
| J2 reference sense | 5 and 6 are internal sense connections to 1 and 4; no extra sensor wires |
| J3 switch | NC to pin 1; COM to pin 2/GND; insulate NO |

**ELE-04 — Analog integrity.** Qualify actual supply ramps, settling, ripple, sensor common mode, reference stability and ADC operation. Check startup, wake, USB transitions and BLE activity. Firmware delays alone shall not be treated as repair for an invalid electrical ramp.

**ELE-05 — Power states.** A short valid button press shall tare; a 1.5 s long press shall toggle analog standby. User-selected standby shall remain selected across USB changes and battery recovery. Low-voltage shutdown and user standby shall be distinct states.

**ELE-06 — Runtime.** The final device shall have measured active runtime, standby current and charging time under a defined usage profile. The historical 4–8 h active estimate and below-100 µA standby goal are planning values. Current standby leaves BLE/USB running and does not establish that low-current goal. [S7, S8, S10]

## 10 Firmware and end-stop behavior

**FW-01 — Acquisition.** The current implementation shall read signed ADC data correctly and check ADC configuration and readiness. Baseline: SPI Mode 1 at 1 MHz; continuous nominal 330 samples/s; discard the first eight conversions. Nominal conversion rate is not a promise of a lossless 330 samples/s archive.

**FW-02 — Validity.** Current force is valid only with qualified stable supplies, a ready ADC, valid in-range calibration and no applicable timeout, saturation, end-stop, battery or standby fault. Invalid or missing force shall appear unavailable, not as a plausible measured zero.

**FW-03 — Qualification gate.** `HARDWARE_QUALIFIED=false` shall remain until actual electrical qualification. The first-power bench build shall start with the analog branch off and require deliberate wake. Production measurement claims shall identify the qualified hardware and firmware combination.

**FW-04 — End-stop polarity.** In the current circuit an intact, unactuated NC path produces HIGH. Switch activation or an open wire produces LOW. Rail-off or ramping states are not usable switch observations.

**FW-05 — Force inhibition.** LOW shall immediately inhibit valid current-force output and new peak updates. Releasing the switch shall require at least 10 ms stable HIGH, along with all other validity conditions, before force becomes valid again.

**FW-06 — Repetition event.** Dynamic counting shall require a qualified sequence of at least 10 ms HIGH followed by 10 ms LOW. A held switch shall count once. A device waking with LOW shall not count until it has observed a valid release and new activation. Counting requires qualified power/ADC but need not require force calibration.

**FW-07 — Physical switch position and feedback.** The real switch shall operate before contact with the P05 full-travel stops under manufacturing tolerances and load. Those stops preserve the intended sensor path; LOW still invalidates current force under the current firmware contract. The original request also called for a physically perceptible endpoint. Confirm the mechanical endpoint feel on the real assembly; the later phone-click requirement does not prove that physical feel. The cam permits real switch-point adjustment. The nominal lead is only a starting point until measured on the assembled mechanism.

**FW-08 — Fault interpretation.** The app shall not describe this single input as a fault-discriminating safety channel. A wire opening can resemble one repetition or click; a short-to-ground in this circuit is not reliably detected. In isometric mode, LOW remains a fault and does not count a repetition.

**FW-09 — Persistent data.** Calibration shall survive restart. Current cumulative counts and device peaks shall survive BLE loss in the running device; reboot shall start a recognizable new boot/run context. Full offline recording across power loss is not provided by the present implementation.

Current settling delays and battery cutoffs are provisional engineering parameters. Qualify them before freezing a production configuration. [S7, S8]

## 11 Bluetooth interface

**BLE-01 — Discovery.** Advertise as **Fingerworker** and allow the iPhone to discover, select, connect and reconnect to the intended device.

| Interface | Baseline |
| --- | --- |
| Service | C37A0001-7B4D-4A26-9C36-2C17F770A001 |
| Telemetry read and notify | C37A0002-7B4D-4A26-9C36-2C17F770A001 |
| Peak reset write with response | C37A0003-7B4D-4A26-9C36-2C17F770A001 |
| Current packet | Version 3; 43 bytes; little endian |
| Publication cadence | Nominal 25 Hz |
| Required ATT MTU | At least 46; current requested value 64 |

**BLE-02 — Telemetry content.** Convey protocol version, operating mode, sequence, acquisition timestamp, signed raw ADC, absolute force, tare, battery voltage, validity/status, cumulative repetitions, boot identity, cumulative peak, independent peak-valid state and peak epoch. A later current-force fault shall not invalidate an earlier valid historical peak. Force uses millinewtons in the packet; battery uses millivolts.

**BLE-03 — Session peaks.** Starting an app recording shall establish a nonzero reset token. A repeated token shall be idempotent. The app shall attribute a device peak to the session only after acknowledgement of the matching epoch.

**BLE-04 — Gaps and restart.** Detect sequence gaps, stale data and boot changes. Reconnection may recover a cumulative total or retained peak; it shall not fabricate missing raw samples, individual repetition times or a continuous force trace.

**BLE-05 — Control scope.** Current BLE writes provide peak reset only. Calibration, operating-mode selection, remote tare and power control are not current BLE functions; device-button and USB serial behavior remain as documented. Do not advertise phone controls that the firmware cannot perform.

Keep the detailed byte layout and compatibility contract in `ios/BLE_PROTOCOL.md`. [S8, S9]

## 12 iPhone experience

**APP-01 — Main workflow.** The app shall open on Training and provide Training, Measurement and Log. It shall support a real device and clearly labeled simulation. The native baseline requires iOS 17 or later.

**APP-02 — Configurable curl workouts.** The current configuration is:

| Setting | Default | Available range |
| --- | --- | --- |
| Repetitions per set | 15 | 1–50 |
| Sets per hand | 6 | 1–12 |
| Recovery per hand | 3 minutes | 0–15 minutes, in 15 s UI steps |
| Starting hand | Left | Left or right |
| Preparation and hand change | 5 seconds | 0–15 seconds |
| Counting | Automatic | Automatic or manual fallback |
| Optional cadence | 1 s pull / 1 s release | 0.5–5 s for each phase |

Settings shall persist. A running session shall retain its starting configuration even if later defaults are edited.

**APP-03 — Independent recovery.** Hands shall alternate. Each hand's recovery shall begin when its own set ends and run while the other hand works. Example: if left finishes at 0:20 and right at 0:45, a three-minute left recovery ends at 3:20, leaving 2:35 of shared waiting. Do not add an unnecessary final rest after the final set.

**APP-04 — Counting boundaries.** Accept device repetitions only during the active hand's work phase. Reset the counter baseline at start/resume. Ignore historical counts and counts during preparation, recovery or pause. A received batch shall not spill excess counts into the next hand's set. Cadence cues shall never manufacture repetitions.

**APP-05 — Curl interruptions.** Device loss, stale telemetry, reboot, wrong operating mode and faults other than the expected end-stop-only state shall pause automatic curl training. End-stop-only status invalidates current force while remaining countable. Resume shall require a ready device and a new count baseline. The current app also requires calibration for automatic-training readiness, although the firmware's device repetition counter does not. Manual fallback shall be explicit.

**APP-06 — Timed cARC.** Provide 1–12 blocks per hand and 1–60 minutes per block, with hand-change preparation and independent recovery. The current template is one five-minute block per hand and zero extra recovery. Use exercise-time progress rather than repetition targets. Preserve a partially completed block even when there were no counted end-stop movements.

**APP-07 — cARC independence.** The timed exercise shall work without a connected or calibrated device and continue through BLE loss. Optional force feedback shall become unavailable when measurements are missing, invalid or isometric. The force reminder shall be described as a user-set threshold on displayed force after tare, not a measured aerobic threshold or percentage of maximum force.

**APP-08 — Pause and background.** Pausing shall freeze workout time and cadence. In the present baseline, moving the app to the background pauses guided training. A delayed callback may finish the current block but shall not claim exercise time for a subsequent unseen hand. Lock-screen continuous guidance is not an established capability.

**APP-09 — End-stop click.** Provide a short click, enabled by default, and optional light haptics, disabled by default. Preferences shall persist, apply immediately and include a test action. Feedback shall work during free use as well as a workout or measurement recording.

**APP-10 — Click timing.** Produce one cue for a freshly observed qualified dynamic activation after release. Do not repeat while held or play catch-up sounds after gaps, reconnection, reboot or returning to the foreground. Suppress feedback for isometry, other fault states and timed cARC. Preserve saved click preferences during cARC suppression.

**APP-11 — Phone limits.** Current sound shall respect silent mode and system volume and operate while the app is active. Physical audibility, haptics and BLE-to-sound latency shall be tested on the user's iPhone. Brief switch events missed between notifications do not justify replaying historical counter increments as clicks.

**APP-12 — Free measurement.** Display valid force, status, battery voltage, chart and peak provenance. Do not draw a continuous chart line across known gaps. Starting a recording shall establish its device-peak epoch; stopping may wait up to one second for a final peak packet, then shall mark a timeout or interruption accurately. [S9, T4, T8, T9]

## 13 Training history and data

**DAT-01 — Local persistence.** Store workouts and measurement sessions locally without an account or cloud dependency. Checkpoint approximately once per second and at meaningful transitions. An unfinished workout shall reopen paused. Storage failures shall be visible.

**DAT-02 — Workout record.** Preserve session identity, date, original protocol, starting hand, source/mode, per-hand results, completed and partial sets or blocks, actual exercise time, recovery, interruptions, notes and perceived exertion on a 1–10 scale.

**DAT-03 — Event history.** Retain preparation, hand changes, starts, accepted count batches, manual corrections, set/block completion, pauses, resumes and early stop. A batch received after a gap shall remain a batch; individual timestamps shall not be invented.

**DAT-04 — Linked raw data.** Connected workouts shall link to their raw measurement session through a shared workout identifier. Raw recording controls shall not conflict with an active guided workout.

**DAT-05 — Export.** Export an individual workout, the workout library and raw measurements as CSV. Workout exports shall preserve original settings, results and interruptions, use UTC ISO 8601 for dates/events and escape text correctly. Timed cARC repetition fields shall remain empty; missing force in user-facing summaries shall be unavailable, not zero. Raw measurement exports shall retain diagnostic values with their status/validity, device milliseconds, boot identity and peak provenance. Device milliseconds are a wrapping acquisition clock, not UTC; invalid diagnostic numeric fields shall not be interpreted as valid measured force.

Raw session JSON retains session metadata, but current raw CSV does not export all session-level interruption/completion/start metadata or the workout link. Adding that context to raw exports is a remaining implementation requirement for fully self-describing exports; the CSV shall not be described as already carrying it.

**DAT-06 — Data limits.** Raw session data is the received nominal 25 Hz stream, not the full ADC conversion stream. Force quit does not imply continuing recording. A sudden process termination may lose changes since the most recent save. Local app deletion can remove stored sessions; export is the current transfer mechanism.

**DAT-07 — Compatibility.** Existing workout archives shall remain readable. Older records shall not gain fabricated event timelines, force data or recovery values. [S8, S9]

## 14 Verification and release criteria

A functional release requires a real assembled device, a named configuration and recorded results. Each test shall identify the CAD/print revision, material/process, spring or sleeve set, electronics revision, firmware build, app build and calibration. Numerical limits listed as open in section 15 shall be fixed before claiming the corresponding performance.

| Test | Requirements covered | Pass condition |
| --- | --- | --- |
| A01 Hand fit and travel | USE-02/03, MEC-01–04 | Both hands achieve the intended grip and complete stroke without binding, unintended contact or unacceptable pressure concentration. |
| A02 Assembly and service | MEC-05, SER-01–03, MFG-02 | Actual parts assemble and disassemble through documented paths; clips recover; loaded retainers fit; Q01 cannot remain in the functional build. |
| A03 Resistance | RES-01–05 | Measured loading/unloading curves match the selected target within the agreed tolerance; correct return and no coil interference throughout travel. |
| A04 Isometry | RES-06, FOR-01–03 | Matched sleeves seat after the intended approach; force follows the sensor path; no dynamic counts or unintended moving contact. |
| A05 Mounted operation | STR-01–04, USE-04 | Actual straps remain secure on the intended object/thigh; no interference, slip or unacceptable rotation under the released load profile. |
| A06 Strength and endurance | MEC-01/02, FOR-10, MFG-06 | Centered, off-center, repeated and sustained loading satisfy the agreed working/proof/life criteria without failure or unacceptable permanent change. |
| A07 Electrical bring-up | ELE-01–04, FW-01–03 | Correct wiring/polarity, valid supply ramps, stable analog operation, safe cell installation and documented charging/temperature results. |
| A08 Calibration | FOR-03–08 | Known-load results in each supported mode meet the agreed accuracy, repeatability, hysteresis and drift limits, including relevant mounting configurations. |
| A09 End stop and faults | FW-04–08 | Switch precedes P05 stop contact under load; sensor path remains intact; held/wake-held/open-wire/ADC-fault cases invalidate force and do not repeatedly count. |
| A10 BLE and peaks | FOR-09, BLE-01–05 | Real iPhone negotiates MTU, receives telemetry and handles gaps/reboots; reset token/acknowledgement and retained peaks behave as specified. |
| A11 Guided curls | APP-02–05 | A real alternating workout observes per-hand recovery, counts only in work phases, pauses correctly and preserves partial results. |
| A12 Timed cARC | APP-06–08 | Partial strokes need no end-stop hits; timer works disconnected; pause/background and incomplete blocks are logged correctly. |
| A13 Phone feedback | APP-09–11 | Real click/haptic, held-switch, gap, silent-mode and cARC suppression tests behave as specified. |
| A14 Storage and export | DAT-01–07, APP-12 | Workouts and raw sessions survive restart as intended; linked exports reproduce recorded values and interruptions without invented data. |
| A15 Runtime and environment | ELE-05/06 | Active use, standby, charging and the agreed environmental conditions meet declared limits on the actual assembly. |

Nominal R15 CAD and print checks have passed within their recorded scope. Existing firmware logic tests and iOS builds support software development. They do not close physical acceptance items. The qualification flag, valid-force behavior and product claims shall follow the hardware evidence. [S1, S6–S10]

## 15 Open release parameters and remaining product decisions

| Decision | Current position | Required resolution |
| --- | --- | --- |
| Upper resistance and working force | Original approximately 50 kg-force total resistance objective; current spring pairs remain below it and no device rating is qualified. | Retain or revise the upper resistance objective; separately set working/proof/overload forces and test the final assembly. |
| Resistance range | Original goal roughly 3–8 levels; two native pairs plus one softer candidate. | Define useful levels and their measured force-versus-travel ranges; integrate the softer option into current CAD. |
| Very light cARC resistance | Timed app mode implemented; suitability of current spring forces unproven. | Establish comfortable minimum resistance and confirm return, partial-stroke behavior and low-force measurement limits. |
| Measurement performance | Sensor and ADC selected; complete-device accuracy not established. | Specify valid force range, maximum error, repeatability, hysteresis, drift and useful resolution. |
| Mechanical life | PLA prototype and nominal checks available. | Specify cycle count, load profile, sustained-load/creep exposure and allowable wear or deformation. |
| Environment | No released temperature, moisture, sweat or impact rating. | Define storage/use conditions, especially if carried in a car, and validate the chosen material and electronics. |
| Runtime and charging | 100 mAh cell; estimates only. | Set minimum active runtime, storage/standby expectation and acceptable recharge behavior; measure them. |
| Portable size and mass | Current width defined; no final complete mass or fully reconciled overall envelope. | Record final length, width, height and assembled mass and confirm practical portability. |
| Effective climbing-edge depth | Original request 10 mm with rounded corners; current recess dimensions describe a different geometric envelope. | Confirm the actual finger-bearing depth and contact shape in the latest grip; preserve the intended edge feel or record an intentional change. |
| Fully standalone experience | Mechanical use and running-device totals/peak available; phone supplies UI/history. | Decide whether durable offline sessions, local display or onboard feedback are required in a later revision. |
| Phone control and lock screen | USB/button control and foreground guided training are current limits. | Decide whether BLE mode/tare control or continuous locked-screen guidance belongs to the next release. |
| Raw CSV session context | Diagnostic rows exported; complete session metadata and workout link remain in JSON. | Include session identity, workout link, start and completion/interruption context in a versioned raw export. |
| Fully printed load structure | Strong user preference to simplify and print more parts. | Identify which remaining metal parts can be replaced and qualify each changed load path. |
| Product cost | No current complete cost ceiling established. | Set prototype and later-unit cost targets if needed for component/process choices. |

These items do not require reopening settled choices such as the close integrated palm, removal of preload adjusters, PLA fit builds or inboard strap routing. They define what is still needed to turn the prototype into a specified and measured training device.

## 16 Reference documents and decision trace

The following sources provide the detailed implementation and the decisions behind this baseline.

| Ref | Source | What it governs |
| --- | --- | --- |
| S1 | [R15 release specification](review/inboard-straps-2026-11-08/final-specification.json) | Current geometry, parts, fixed travel, print scope and qualification status. |
| S2 | [R15 assembly guide](review/inboard-straps-2026-11-08/MONTAGE.md) | Real-part assembly, sensor path, Q01 exclusion, straps and service movements. |
| S3 | [R15 design parameters](review/inboard-straps-2026-11-08/mechanics/design-specification.json) and [FeatureScript](fingerworker_mvp.fs) | Palm, strap geometry and current parametric mechanism. |
| S4 | [Softer spring conversion](review/flat132-softer-springs-2026-10-26/README.md) | Two-thirds force request, RDF2127 candidate and R9-only validation scope. |
| S5 | [R15 print instructions](print/bambu-R15-inboard-straps-2026-11-08/README.md) | H2D PLA process, plate scope and file variants. |
| S6 | [Physical acceptance framework](review/software-2026-10-11/ABNAHME.md) | Test methodology; older mechanical settings must be replaced by this R15 baseline. |
| S7 | [Firmware guide](firmware/README.md) and [firmware contract](electronics/FIRMWARE_CONTRACT.md) | Acquisition, qualification, calibration, end-stop and power behavior. |
| S8 | [BLE protocol](ios/BLE_PROTOCOL.md) and [firmware configuration](firmware/Fingerworker/Config.h) | Packet contract and current engineering parameters. |
| S9 | [iPhone app guide](ios/README.md) and [training verification](ios/TRAINING_VERIFICATION.md) | Curl/cARC behavior, feedback, history, export and known platform limits. |
| S10 | [Electronics](electronics/README.md), [KiCad guide](electronics/kicad/README.md) and [first power](electronics/procurement/FIRST_POWER.md) | Selected circuit, physical assembly and bench qualification. |

| Ref | Chat title and identifier | Relevant decisions |
| --- | --- | --- |
| T1 | Device-Readiness-Review erstellen — 01a12a68-84fe-7c33-b799-8512cdf2b49a | Integrated close palm, fewer parts, PLA, all preload adjustment removed, two 25 mm straps, inboard slots on both sides, one plate and no brims. |
| T2 | Clarify STL sensor obstruction — 01a179a2-e95b-7423-872a-fe962b8748f9 | Q01 is a fit fixture and cannot occupy the sensor path in a working device. |
| T3 | KiCad-MCP für Review bewerten (2) — 01a1555f-1af9-7ca3-a862-28a66977421b | XIAO battery-pad assembly and revised supplier scope. |
| T4 | Click-Sound am Endschalter ergänzen — 01a1b0f2-a061-72e1-b63d-4fe220ae5498 | End-stop sound through the phone. |
| T5 | Entwicklungsprozess zusammenfassen — 01a1a306-f381-73f2-9b2d-3a9dbc36495f | Development context and the need to separate proposals from completed work. |
| T6 | Erforsche Gerät für Fingertraining — 01a03557-6e81-7d22-b3ea-5eb9bd0b586a | Portable climbing finger curls, force/cycle measurement, resistance levels, simple setup, standalone ambition and BLE/app tracking. |
| T7 | Optimize Onshape CAD model — 01a06e1d-4314-7a82-8642-2577d69b76a0 | External attachment and exercise without palm reaction; earlier cord solution later removed. |
| T8 | Reha-Protokoll für Kletterfinger — 01a12aec-2ab3-7fe1-a380-ebcd9c79da75 | Explicit change to training rather than rehabilitation; adjustable per-hand curl program and a training log. |
| T9 | Research ARC and cARC training — 01a196d3-5ced-7730-842b-7626d76892a0 | User request to implement the proposed time-based cARC app mode. |
| T10 | Finde kostenlose CAD-Browsertools — 01a051c1-e9bf-7882-9fc6-730f537161a9 | Approximately 50 kg-force total resistance, 10 mm rounded edge, original 100-to-70 mm reach, perceptible end stop and a printable MVP. |
| T11 | Add device spring and lock upgrades — 01a0c0b9-2d47-73d0-a725-420bc71874f0 | Lighter interchangeable springs and sensor-compatible isometric locking; requested preload adjustment later explicitly removed. |

The older general documents remain useful historical records. Their adjustable-preload geometry, cord attachments, separate palm pieces and earlier spring-force tables shall not be mixed into a new R15 build.
