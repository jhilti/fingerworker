# R4 switch-fit finalization notes

Status: **NOMINAL_GEOMETRY_CHECKS_PASS**, with zero failed or unresolved checks. [Immutable Onshape R4](https://cad.onshape.com/documents/15316cc6370631845af136b2/v/1a51bc54c29fb727dcb77016/e/d253eb87b70818ebde8215f0) binds the final source and neutral setup. All 105 neutral STEP solids are valid; native maximum and isometric poses pass. The delivery script refuses a non-passing final report. These notes do not establish mechanical strength or real switch performance.

## Scope and source

R4 is derived from frozen R3 source SHA256 `4665c3ec4e983e478d34c6cfe923b3b60e6c8848f36b7c54b55b1989eaab6326`. The final R4 source is [fingerworker_flat132_switch_fit.fs](fingerworker_flat132_switch_fit.fs), SHA256 `b150ff3a76cfaaaaa65ee1ea09e144b7c7d64e45459a925163e56918f48bb3c5`. The reproducible [builder](build_switch_fit.py) records exact changes and source-preservation assertions in [source-build.json](source-build.json).

Only P01, P04, H09, H09a, H09b and H10 change geometry from R3. P05's central reaction web and integral sensing stops retain their geometry. The source asserts the central web byte-for-byte and the stops exactly after removing comment-only lines. The stale R2 stop-clearance comment was corrected. R3 palm geometry and mounts remain byte-for-byte unchanged in source. Native comparison confirms exactly the six intended geometry changes. The other 99 STL files are byte-identical to R3 and their BRep symmetric differences are zero. Each of the six modified BReps also matches its independently reconstructed drawing/source geometry with zero symmetric-difference volume.

## Switch reference

SS-01GL2 is the plain solder-terminal, SPDT, hinge-roller model. The [manufacturer drawing](https://omronfs.omron.com/en_US/ecb/products/pdf/en-ss.pdf), pages 4/6, gives the major 19.8 × 10.2 × 6.4 mm housing, 9.5 ± 0.1 mm mount spacing, Ø2.35 mounting holes and Ø4.8 × 3.2 mm roller. Drawing tolerances and real geometry remain relevant.

H09 joins the housing to three rectangular terminal envelopes and a conservative full-width 0.4 mm lug strip. Terminal holes/corners and the precise lug profile are unspecified. The strip assumes lug thickness stays within the stated 6.4 mm housing thickness. It is explicitly **DRAWING REF**, not a downloaded factory STEP. H09a's cylindrical lever and H09b's configured motion remain illustrative. The unmodified official TE force-sensor solid is retained separately.

The earlier proxy omitted the tabs. Independent R3 envelope checks found 4.32 mm³ total overlap with P05 at 2 mm preload. R4 translates the switch +4/+1/+1.5 mm and models the missing clearance envelopes. At 2 mm preload the nominal tab-to-web axial gap is 3.1 mm. The case-to-negative-stop lateral gap is 1 mm, pedestal-to-stop gap 0.5 mm. These are nominal CAD gaps before tolerances, solder, wiring and deflection.

## Mount and hardware changes

The pedestal extends from Z3.8 to Z7.5 and remains joined to the base. Its trimmed Y−16.5 edge avoids the negative integral stop; translating the whole pedestal upward would disconnect it. Two M2 pilot floors move to Z3.5, preserving 4 mm blind depth. Existing M2×10/washer nominal engagement remains `min(3, 3.6 − washer thickness)` mm, reaching 3 mm when the washer is no thicker than 0.6 mm. Actual stock remains unconfirmed. Omron's M2.3 mounting instruction is not a torque qualification for the current M2/printed arrangement.

H10 becomes M3×8 with its axis at Y3.5/Z11.5. The Ø5.8 recess gives 0.15 mm nominal radial clearance around the Ø5.5 head and leaves 1.3 mm above the female guide roof. The intended L4 insert spans X68…72; its pilot ends at X73. Nominal screw engagement remains 4 mm throughout 0–2 mm preload. Thread helices, actual inserts and the setting lock are not qualified by smooth CAD hardware. No steel sensor nut/keeper interface is replaced by a heat-set insert.

## Retained function and limits

The 132 mm frame, 72 mm opening, 35 mm height, R3 palm surface 7 mm closer, reinforced portal, sensor force datum and P05 stop load path are preserved. Dynamic travel stays `30 − preload`, isometric seating `15 − preload`. H10 resets manually by minus the preload change; it is not automatically coupled.

The shifted OP surface is X35 ± 0.8 mm. The cam face reaches X34 at the mechanical stop, giving 1 mm nominal trip lead. Physical calibration must address OP tolerance, allowable total travel, release and locking. Solder and wire bend/insulation/strain relief require physical fitting. Firmware is unchanged and retains the NC force/peak block. The 500 N target, print process, palm joint, fatigue, off-axis loading and retention remain physically unqualified.

[Final specification](final-specification.json) binds the immutable version, STEP, all three native pose exports and final reports. Final validation covers 5,253 static pairs, 5,253 continuous pairs, 55 dimensions, 44 material/clearance probes, 120 spring-envelope checks and 826 service pairs. The separate exact switch audit passes 14 checks. Final native evidence supersedes the earlier local contact-region study; physical qualifications remain open.
