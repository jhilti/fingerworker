# R6 fixed solid-palm audit

This audit reads the actual native R6 exports and changes no production geometry. It checks the single modified P02 body and preserves the existing R5 evidence for unaffected geometry through an exact source-scope certificate and direct native STEP comparisons. P03 is removed; the four separate P07 return bumpers remain.

The former R10.25 mm half-round contact stock is independently constructed in OpenCascade, with its R1.2 mm end fillets, then fused to the original native R5 P02. Exact Boolean symmetric difference with the R6 native P02 checks the filled block. One valid solid with one boundary shell checks that no enclosed sleeve cavity remains. The original mounting and insert-pilot regions are compared directly, as are the wrist-facing contact bound and the nominal 0.6 mm lid gap.

All 105 native STEP solids must be valid, have positive volume and associate uniquely with the 105 neutral native STL bodies. The 104 surviving bodies other than P02 must preserve their exact STEP geometry at their original coordinates. The independent source certificate reconstructs every byte of R6 from frozen R5 through the reviewed palm-only changes. It preserves the complete correlated R5 travel/preload/trim domain, 28–30 mm usable dynamic stroke and 81 mm steel isometric sleeves. The prior exports retain their R5 provenance.

The changed palm is checked against all other native bodies for exact STEP material overlap. Only its own full-domain interactions, conservative spring occupancy and related declared service paths are rerun. Native MAX and ISO exports are compared with the same R6 fixed palm and the corresponding R5 pose for all unchanged bodies, with exact triangle coordinates and facet/vertex ordering ignored. Unchanged R5 pair checks are not relabeled as newly run R6 checks.

Kernel volume tolerances are numerical acceptance thresholds, not permitted material penetrations or physical manufacturing clearances. The scripts do not establish a printed strength rating, slicer infill, fatigue life, comfort, switch calibration, spring fatigue or actual insert compatibility. The previously discussed electronics-cover extension is not part of R6.

## Reproduction

Use `/tmp/fingerworker-sensor-cad-20261022/bin/python` with the dependencies listed in `requirements.txt`. From the repository root:

```bash
/tmp/fingerworker-sensor-cad-20261022/bin/python review/flat132-solid-palm-2026-10-23/validation/certify_source_scope.py
/tmp/fingerworker-sensor-cad-20261022/bin/python review/flat132-solid-palm-2026-10-23/validation/audit_solid_palm.py --neutral review/flat132-solid-palm-2026-10-23/native/Flat132_R6_neutral_final.zip --step review/flat132-solid-palm-2026-10-23/native/Flat132_R6_final_AP214.step --max review/flat132-solid-palm-2026-10-23/native/Flat132_R6_max28_p2_heavy_final.zip --iso review/flat132-solid-palm-2026-10-23/native/Flat132_R6_isometric13_p2_81_final.zip --workspace https://cad.onshape.com/documents/15316cc6370631845af136b2/w/6c1e8b296c3ce433e6d4783f/e/d253eb87b70818ebde8215f0
```

`manifest.json` records the hashes and operator-declared native source association. `validation-summary.json` is the final machine gate. `validation.json` carries the same final gate fields for the viewer/package builder. Immutable version binding is provenance metadata and does not recompute geometry.
