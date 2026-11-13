# Flat132 R1 — actual-sensor CAD prototype

This revision completes the nominal mechanical CAD around the original TE FX1901-0001-0200-L revision F manufacturer solid. Final source: [fingerworker_flat132_finished.fs](fingerworker_flat132_finished.fs). The original Rev D, the earlier 132 mm proxy study and the pre-redesign checkpoint are preserved.

**Nominal CAD checks pass**, including native solids, continuous motion, service paths and both exact STEP roundtrip comparisons. The report status is `NOMINAL_GEOMETRY_CHECKS_PASS`, with zero failed or unresolved checks. Intended bearing, thread and actuator interfaces are identified explicitly in the report. This is a CAD prototype revision; manufacturing tolerances and physical qualification remain separate.

[Final immutable Onshape version](https://cad.onshape.com/documents/15316cc6370631845af136b2/v/4c39034c17201905fdfbb1d6/e/d253eb87b70818ebde8215f0) · [Editable study branch](https://cad.onshape.com/documents/15316cc6370631845af136b2/w/3ee26cf6386f889ca7ae9519/e/d253eb87b70818ebde8215f0) · [Interactive exact native configurations](viewer/viewer.html)

[Final neutral AP214 STEP assembly](native/Flat132_R1_final_AP214.step) · [CAD prototype delivery package](deliverables/Flat132_R1_CAD_Prototype.zip)

[Current dimensions and BOM specification](final-specification.json) · [Printed-part subset and handling notes](print-mm/README.txt) · [Printed-part identity manifest](print-mm/part-manifest.json)

[Individual H12/H23 STEP convenience helpers](machining-step/README.md) provide valid single-solid roundtrips. Their separate coincident Boolean equivalence check is inconclusive, as documented; the full final native STEP remains the geometry authority.

The print subset contains 14 native P-prefixed STLs: nine rigid parts and five TPU parts. They retain millimetres and assembly coordinates. They are unsliced; print orientation, process settings and physical performance still require qualification. The manufacturing package excludes the hand scan and viewer.

## Files and recorded checks

The integrated final FeatureScript has SHA-256 `041056629440056626b2f2f88a0db216693e48fff178687174478cb1f34227ef`. It was committed in Onshape after exact editor readback. These are the three final native STL exports from that source:

| Native configuration | Archive | SHA-256 |
| --- | --- | --- |
| Neutral: 0 mm stroke, 0 mm preload, light springs | [Neutral](native/Flat132_R1_neutral_final.zip) | `f22ebe6f8d2852a31c4345dff9062adc557274f2d94152d9459822a2bdd1683e` |
| Maximum: 30 mm stroke, 2 mm preload, heavy springs | [Maximum](native/Flat132_R1_max30_p2_heavy_final.zip) | `03b3d0c480ffb23aca9a590235d8c9a419d10b51bebcbeb72ef6683e8219ec40` |
| Isometric: 13 mm setting, 2 mm preload, lock sleeves | [Isometric](native/Flat132_R1_isometric13_p2_final.zip) | `6539c0800dffa49279cd5eee74d8d6781ab63f18b6f837fa4b78c0e0a762f37f` |

Each archive contains 109 solids: 56 device parts and 53 electronics references. They retain millimetres and assembly coordinates. H-prefixed purchased or metal parts and REF electronics/envelopes are reference geometry, not print instructions. Use the neutral configuration as the assembly reference; the other archives record actual regenerated mechanisms.

The [validation report](validation/validation.json), [method and reproduction instructions](validation/README.md) and [independent mount audit](native-mount-audit.md) record valid solids, static pairs, both native end configurations, continuous travel/preload sweeps, isometric sleeves and 974 finite service-pair sweeps. The continuous checks cover the independent 0–30 mm travel and 0–2 mm preload ranges; they are more than three static-pose checks.

The final neutral AP214 STEP has SHA-256 `6de4383e6423fd1f57bd353d8f42953ecdae841bee1e36b853fb312c679fd7ef` and contains 109 solids. Exact kernel comparison found zero symmetric-difference volume between its valid H01 solid and the unmodified, rigidly placed manufacturer sensor. The P02/P03 palm-core/TPU STEP pair has zero positive BRep intersection volume. Both roundtrip checks pass. Immutable Onshape version `4c39034c17201905fdfbb1d6` records the same final source and 109-part neutral model; the obsolete suppressed proxy-deletion feature has been removed.

## Revised geometry

The frame remains 132 mm wide with a 72 mm clear finger opening, 30 mm travel and 0–2 mm synchronized preload. The actual maximum height is 35 mm, from base Z−2 to the sensor backplate at Z33. No manufacturer sensor surface is scaled, cut or reshaped. Its apex remains at X−1.9/Y0/Z18 in the neutral setting; the complete sensor and cassette translate with preload.

- P01: wider cassette-guide spacing, real lead exit, shallow sensor-floor pocket and reinforced closed slot ends. The slot end wall is now 2.3 mm; the pocket retains 4.7 mm of frame floor.
- P05: a cavity for the true sensor and independent keeper, corner screw clearance and low guide-cap relief. The central X1–9 pusher reaction web remains intact.
- H12: S355 planar steel backplate, 30×30×2.15 mm with a shallow locating collar and generous lead-base notch. The flat rear of the circular sensor housing is supported; the previous central relief is removed.
- H23 / H240–243 / H250–253: a removable 0.5 mm stainless loose keeper, four OD4/ID2.2×8.45 mm steel spacers and four M2×12 panhead screws. The keeper has a 0.5 mm unloaded axial housing gap and does not form a parallel reaction path around the sensor.
- H18 / H19: retained M3×8 capture screws, relocated capture axes and revised OD4/ID3.2×6 mm spacers. H12 uses Ø2.5 mm flat-bottom pilots **tapped M3×0.5**, with 2 mm nominal engagement and 1.1 mm bottoming-tap runout. These are light cassette retainers, separate from the operating force path.
- P03: a local 0–2 mm preload sweep relief removes the legacy contact with the adjuster shaft while preserving the principal wrist contact surface.
- P04: local top caps restore the rear spring-seat roof while retaining the 72 mm pocket and R12 seat clearances.

The physical force path remains spring/sleeve → yoke → retained pusher → sensor button → supported sensor rear → steel cassette → preload screw/nut/keeper → fixed frame. The front sensor keeper is a loose retention feature.

## Assembly and service

Release external operating load and spring energy before service. The [fabrication and BOM notes](finalization-notes.md) describe the sequence and the validation manifest records the exact removed parts. Remove the palm/case module, springs or lock sleeves, rear caps/bumpers, both rods and H18/H19 retention hardware. With preload at zero, keep the complete sensor/cassette/yoke/pusher stack together, translate it forward **+X 2.1 mm**, then lift **+Z 40 mm**. There is **no initial lift**; lifting first can obstruct the radial lead. Separate the yoke/pusher from the sensor keeper axially on the bench. Reinstall the palm/case module before operation.

STEP screw/nut bodies use simplified nominal thread representations; fabricated tapped holes require the stated finished threads. H12 contains nominal Ø1.7 mm M2 and Ø2.5 mm M3 pilot envelopes. Vendor springs, switch actuator, cable and connector representations have their documented limits.

## Qualification scope

The CAD provides nominal part geometry, assembly interfaces and motion/service clearance evidence. Printed strength, backing stiffness, fatigue, creep, actual fastener/insert fit, tolerance stacks, full cable routing and strain relief, sensor calibration and loaded behaviour still require prototype qualification. No new working-load rating is asserted.

The user confirmed that the hand scan is an approximate visual reference and the 72 mm opening should remain. The original scan and earlier manual registration are retained, with at least ±5 mm translation uncertainty and unknown rotation error. No scan is rescaled, articulated or shifted to manufacture a fit result. Physical hand fit and comfort need a spring-free fit prototype.
