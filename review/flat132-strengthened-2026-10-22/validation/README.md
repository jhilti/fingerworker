# R2 printed reinforcement: native CAD audit

Final status: **NOMINAL_GEOMETRY_CHECKS_PASS**, bound to [immutable Onshape version9bdcf9c3](https://cad.onshape.com/documents/15316cc6370631845af136b2/v/9bdcf9c3c67638228b40378b/e/d253eb87b70818ebde8215f0), with **zero failed and zero unresolved checks**. Neutral, native maximum28/preload2 and native isometric13/preload2 all pass. The compact [validation-summary.md](validation-summary.md) indexes the full evidence. The 500 N maximum hand force is a design target, not a verified working-load rating. This audit addresses nominal geometry, source motion and declared service paths. It does not calculate printed material strength, fatigue, creep or layer adhesion.

Final R2 source SHA256: `d5eca2f3d87bf4b9a47c1987ee91ba1d56e8c87003eca101677a148a2e605654`. The earlier candidates are superseded by this integral printed stop design and final UI roundoff guard. Both neutral exports retain source6c provenance; the independently checked guard-only certificate binds their unchanged legal-domain geometry to final sourced5.

Only printed P01 and P05 change shape. The four M4 stop screw/nut previews H070, H071, H080 and H081 are intentionally removed because broad integral P05 stop faces now carry the end load through the floating yoke and sensor. The baseline comparison requires every remaining neutral native STL member, including the actual manufacturer sensor and hardware, to remain byte-identical to R1. H15 and P04 have reordered facets in the new native export; for those two only, exact native triangle-coordinate set hashes must match, with no rounding, scaling or geometric tolerance. Both intended changed parts must actually change. Missing, extra, invalid or disconnected parts remain failures.

The retained R1 audit covers all native solid pairs in neutral, maximum stroke/preload, and isometric native configurations. The exact legal operating polygon is stroke ≥0, preload 0–2 mm and stroke+preload ≤30 mm. Maximum stroke therefore changes from 30 mm at preload0 to 28 mm at preload2. Linear relative-X extrema are evaluated at all four polygon vertices. The switch follows q=stroke+preload: the lower-q stationary lever polygon reduces to an exact axial interval; the active q24.2–30 / preload0–2 region is a legal rectangle certified by the adaptive rotation bound. **H10 must be manually reset by −preload after every preload change**; the model represents that setup and does not claim an automatic coupling. This preserves the source 1 mm trip margin before the printed stops. Native pose geometry independently checks those kinematics. Spring-envelope checks remain conservative over the complete polygon. Exact STEP checks compare the genuine sensor to its canonical manufacturer BRep and require zero real sleeve/core overlap. The complete neutral STEP is checked for 105 valid positive solids, unique correspondence to all 52 device and 53 electronics reference STL bodies, and no missing bodies.

R2 adds selected local probes for the 6.75 mm reaction wall, 5 mm cassette guides, 3 mm upper bridge, 6.2 mm driver-access opening, buttress stock, widened lead passage and retained 35 mm frame height. Each integral printed stop has a 14×22 mm broad bearing face and a 10×22 mm axial arm section, checked by local rays and inclusion probes. These measurements do not establish a global minimum wall or a strength margin. The P04/P05 endpoint certificate partitions both native solids into five complete transverse Y slabs; each uses the strict continuous relative-X proof, including exact exterior stop-face tangency. No positive overlap is waived.

The complete sensor/yoke/pusher cassette must first translate forward **3.5 mm**, with no initial lift, before it can lift 40 mm past the new bridge. The declared prerequisites include removing the palm/electronics module, safely unloading and removing the springs, rear retainers/bumpers and rods, removing both H18/H19 cassette retainers, and setting preload to zero. This is an audit of the stated sequence, not a general disassembly planner. H15 keeper release also changes to a **2 mm wristward translation before lift** because the reaction wall has grown rearward.

## Reproduce

Use the recorded dependency versions in `requirements.txt` with Python 3.12. The existing runtime is `/tmp/fingerworker-sensor-cad-20261022/bin/python`.

```bash
PY=/tmp/fingerworker-sensor-cad-20261022/bin/python
$PY review/flat132-strengthened-2026-10-22/validation/prepare_manifest.py \
  --source review/flat132-strengthened-2026-10-22/fingerworker_flat132_strengthened.fs \
  --neutral /absolute/path/R2-neutral.zip \
  --step /absolute/path/R2-neutral.step \
  --workspace 'https://cad.onshape.com/documents/.../w/.../e/...' \
  --native-pose dynamic 28 2 /absolute/path/R2-maximum.zip \
  --native-pose isometric 13 2 /absolute/path/R2-isometric.zip
$PY review/flat132-strengthened-2026-10-22/validation/validate_finished.py \
  review/flat132-strengthened-2026-10-22/validation/manifest.json
$PY review/flat132-strengthened-2026-10-22/validation/audit_native_step.py
$PY review/flat132-strengthened-2026-10-22/validation/certify_source_fit.py
```

The archive, each native STL member, FeatureScript, manifest and validator are hash-bound in the report. Native export/source association is operator supplied; the Python script does not regenerate Onshape. Exact STEP tests must finish before an overall geometry pass. An absent native input, missing required native pose, unresolved continuous sweep or invalid volume prevents a complete pass. `--static-only` is diagnostic only.

The inherited explicit contact models remain narrow: spherical load-button contact, flat sensor rear support, bounded nominal M2/M3 thread envelopes, the purchased lever/roller axle joint, and one electronic button travel envelope. Coincident sleeve/core mesh facets require a separate exact BRep check. No new positive material interference is waived for reinforcement.

Only the actual native exports are used for final evidence; local CAD mock approximations are not substituted for them. R1 audit machinery diagnostics remain archived in their original directory; they were not reclassified as R2 evidence. `r2-domain-adapter-check.json` records eleven passing mathematical diagnostics for the changed domain/arc adapter; it is not native device evidence.
