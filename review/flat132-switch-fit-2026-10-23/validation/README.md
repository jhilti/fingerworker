# R4 switch fit: native CAD validation

Final status: **NOMINAL_GEOMETRY_CHECKS_PASS**, with **zero failed and zero unresolved checks**, bound to [immutable Onshape R4](https://cad.onshape.com/documents/15316cc6370631845af136b2/v/1a51bc54c29fb727dcb77016/e/d253eb87b70818ebde8215f0). Source SHA256: `b150ff3a76cfaaaaa65ee1ea09e144b7c7d64e45459a925163e56918f48bb3c5`.

These scripts check the separate R4 manufacturer-drawing switch study against frozen R3. They do not create, repair or regenerate the native model. Final status is in `validation-summary.json`; an absent native input, required pose, invalid solid, ambiguous STEP association, unexpected geometry change or unresolved continuous path prevents a complete pass.

Only P01/P04/H09/H09a/H09b/H10 may change shape. The complete P05 reaction web and integral stops, the R3 half-round palm fit, force sensor, electronics and all remaining native geometry are retained. Facet reordering is accepted only when canonical triangle coordinates match exactly without geometric rounding. A separate exact STEP audit independently reconstructs the six CSG changes and compares all99 untouched BReps with R3.

The new switch checks cover its raised pedestal, joined tab/lug envelopes, Ø5.8 head recess, retained1.3mm guide roof web, pilot bores, three terminal separation slabs over full preload, nominal M3x8/L4 insert overlap and a partial diameter4mm driver-shank corridor. Terminal/lug profiles are conservative manufacturer-drawing envelopes, and the fixed-length lever motion is illustrative. They do not qualify real solder/wire routing or actual switch travel. The head socket and complete driver handle are not modeled.

The operating polygon remains stroke≥0, preload0–2mm, stroke+preload≤30mm. The source shows the manually configured cam setting after each preload change, not an automatic linkage. Continuous rigid and actuator certificates, native MAX/ISO pose congruence, spring envelopes, finite service paths and selected retained dimensions/probes remain strict. Exact native STEP checks require105 valid positive uniquely associated solids, the genuine unchanged sensor and zero P02/P03 material intersection.

500N remains a design target, not a qualified printed load rating. Actual switch OP/total travel and cam locking, screw/head/washer/insert stock, printed fit, wiring, comfort and strength require physical checks.

## Reproduce

Runtime: `/tmp/fingerworker-sensor-cad-20261022/bin/python`; dependencies are in `requirements.txt`. From the repository root:

```bash
PY=/tmp/fingerworker-sensor-cad-20261022/bin/python
$PY review/flat132-switch-fit-2026-10-23/validation/prepare_manifest.py \
  --neutral review/flat132-switch-fit-2026-10-23/native/Flat132_R4_neutral_final.zip \
  --step review/flat132-switch-fit-2026-10-23/native/Flat132_R4_final_AP214.step \
  --workspace 'https://cad.onshape.com/documents/15316cc6370631845af136b2/w/3ee26cf6386f889ca7ae9519/e/d253eb87b70818ebde8215f0' \
  --native-pose dynamic 28 2 review/flat132-switch-fit-2026-10-23/native/Flat132_R4_max28_p2_heavy_final.zip \
  --native-pose isometric 13 2 review/flat132-switch-fit-2026-10-23/native/Flat132_R4_isometric13_p2_final.zip
$PY review/flat132-switch-fit-2026-10-23/validation/validate_finished.py \
  review/flat132-switch-fit-2026-10-23/validation/manifest.json
$PY review/flat132-switch-fit-2026-10-23/validation/audit_native_step.py
$PY review/flat132-switch-fit-2026-10-23/validation/audit_switch_fit.py
$PY review/flat132-switch-fit-2026-10-23/validation/certify_source_fit.py
$PY review/flat132-switch-fit-2026-10-23/validation/check_r2_domain.py
$PY review/flat132-switch-fit-2026-10-23/validation/summarize_validation.py
```

After root verifies the immutable native checkpoint, `bind_version.py` records that provenance without recomputing geometry; rerun `certify_source_fit.py` and `summarize_validation.py` to bind the evidence index. Source/export association remains operator declared and hash-bound.
