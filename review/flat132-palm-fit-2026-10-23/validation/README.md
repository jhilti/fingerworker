# R3 half-round palm: native CAD validation

Final status: **NOMINAL_GEOMETRY_CHECKS_PASS**, with **zero failed and zero unresolved checks**, bound to [immutable Onshape R3](https://cad.onshape.com/documents/15316cc6370631845af136b2/v/9bf146edbc2e61a5c4144a35/e/d253eb87b70818ebde8215f0). The final R3 source is `4665c3ec4e983e478d34c6cfe923b3b60e6c8848f36b7c54b55b1989eaab6326`.

Only P02 (rigid palm) and P03 (TPU cap) may change shape from the R2 baseline. The native inventory remains 52 device solids and 53 electronics reference solids, 105 total. The preserved R2 neutral archive is required for comparison. Every remaining body must retain its exact native boundary geometry. Raw facet reordering is accepted only when the complete canonical triangle-coordinate set is exactly identical, with no rounding, scaling or geometric tolerance. There are no added or removed hardware parts.

The nominal wrist tangent moves from X−44.25 to X−37.25, reducing the palm/finger contact span by exactly 7 mm while retaining the 72 mm finger opening. The palm axis changes to X−27/Z19.75. The rigid radius 7.75 mm core and radius 10.25 mm TPU surface retain only the wrist-facing half. Two TPU front return bands at Y[−43,−39] and [39,43], X[−27,−24.5], Z[14.6,30] provide nominal capture around the core flat. Printed fit, assembly flex, pull-off force and durability remain physical prototype checks.

The unchanged R2 operating polygon is stroke ≥0, preload 0–2 mm and stroke+preload≤30 mm: 30 mm stroke at preload 0, 28 mm at preload 2. H10 still requires manual resetting by −preload whenever preload changes. All configured motion, switch-arc, spring-envelope, finite service-path and inherited strength-geometry checks remain strict. The 500 N value remains a design target rather than a qualified printed working-load rating.

R3 adds direct comparisons to the actual R2 palm bounds for the 7 mm change, plus half-core depth/front-plane, central cap clearance, band width/depth and local material probes. Exact native STEP checks require the unmodified genuine sensor, zero P02/P03 material overlap, and 105 valid positive solids uniquely matching all native neutral STL bodies.

The source fit proof partitions the interface. P02 plate/ears remain at Z≤14.5, below all TPU at Z≥14.6. Above the plate, the rigid core lies inside radius 7.75 and at X≤−27. The annular TPU excludes that radius; the only front return material lies at X≥−27. Shared curved/planar boundaries are permitted; positive volume overlap is not.

`halfrod-candidate-audit.json` records 202 passing affected-part continuous feasibility checks against actual R2 parts, using conservative unfilleted in-memory outer geometry including both return bands. It is a feasibility diagnostic, not a substitute for the native R3 exports. The final report independently passes all native parts and configurations; see [validation-summary.md](validation-summary.md) for the compact evidence index.

## Reproduce

Use Python 3.12 and `requirements.txt`. The current runtime is `/tmp/fingerworker-sensor-cad-20261022/bin/python`.

```bash
PY=/tmp/fingerworker-sensor-cad-20261022/bin/python
$PY review/flat132-palm-fit-2026-10-23/validation/prepare_manifest.py \
  --neutral /absolute/path/R3-neutral.zip \
  --step /absolute/path/R3-neutral.step \
  --baseline /absolute/path/R2-neutral.zip \
  --workspace 'https://cad.onshape.com/documents/.../w/.../e/...' \
  --native-pose dynamic 28 2 /absolute/path/R3-maximum.zip \
  --native-pose isometric 13 2 /absolute/path/R3-isometric.zip
$PY review/flat132-palm-fit-2026-10-23/validation/validate_finished.py \
  review/flat132-palm-fit-2026-10-23/validation/manifest.json
$PY review/flat132-palm-fit-2026-10-23/validation/audit_native_step.py
$PY review/flat132-palm-fit-2026-10-23/validation/certify_source_fit.py
```

Native association is operator declared and hash-bound; these scripts do not regenerate Onshape. A missing native input, required pose, invalid body, ambiguous STEP correspondence, unresolved continuous path or unexpected shape change prevents a complete pass. Geometry validation does not establish hand comfort, material strength, print tolerance, creep or fatigue performance.
