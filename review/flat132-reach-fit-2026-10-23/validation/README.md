# R5 reach fit and81mm isometric sleeve validation

Final machine status, hashes, counts and immutable native checkpoint are in `validation-summary.json` and `validation-summary.md`. An absent input, invalid solid, source/provenance mismatch, unexpected geometry change, positive interference or unresolved continuous path prevents a complete pass. This folder contains independent geometry checks; it does not regenerate Onshape or establish a printed load rating.

The exact domain is user travel u≥0, preload0–2mm, u+preload≤30mm and calibration trim−0.8…+0.8mm. Absolute carriage displacement is5+u. The actuator variable is Q=u+preload−trim. Certificates preserve the correlation Q+trim≤30; the illegal independent Q30.8/trim+0.8 corner is excluded. The inactive source actuator is checked over its clipped polytope and the moving arc over its exact trapezoid times preload. Finite service paths retain specified prerequisites.

Neutral/dynamic native exports originated from the prior61885 source. `dynamic-mode-equivalence.json` independently reverses all five ISO81 source replacements and restores that complete source exactly. Only the isometric conditional branch changes coordinates. Reuse is restricted to isometricLock=false; the81mm isometric native export comes from finald7f476. Original source associations remain recorded per native file. The superseded86mm ISO export is not a required final input.

P05 primary web/root, sensor, half-round palm and electronics are retained. The independent exact STEP audit reconstructs P01/P04/P05/P060/P061/P11/H10 and compares97 preserved rigid BReps. Six seats/return pads shift exactly5mm. Four pad STLs exhibit one float32 ULP bound differences after translation; their exact STEP symmetric differences are zero, and each native mesh must be an8-vertex rectangular box matching its own STEP bounds within one coordinate float32 ULP. This does not alter the global collision tolerance.

The clamp/carriage contact is certified using two conservative convex cylinders that contain every native clamp triangle and full solid; each full swept hull is checked. The complete shoe uses its exact well-relative frame. There is no material erosion or broad contact waiver. The illustrative roller/P11 interface has an exact separating plane after clipping the shoe to the roller's Z slab. The unchanged illustrative lever/roller axle joint retains its specific source-derived internal overlap bound.

The genuine TE sensor must match its unscaled STEP. The native assembly must contain106 valid positive uniquely associated solids. P02/P03 zero exact STEP overlap is supplemented by a source separation proof; shared-surface STL facets remain a numerical approximation. Selected wall probes do not establish a global minimum wall or strength.

500N is a design target. Actual spring fatigue, switch operating/total travel, cam clamping and insert installation, guide friction, wire routing, printed creep/fatigue and hand comfort remain physically unqualified. Set P11 manually to trim−preload and calibrate/relock after preload changes. Driver clearance covers a partial diameter4mm shaft, not a complete tool handle or socket.

## Reproduction

Use `/tmp/fingerworker-sensor-cad-20261022/bin/python` and the dependencies in `requirements.txt`, from the repository root. The saved manifest has all absolute native paths and poses.

```bash
PY=/tmp/fingerworker-sensor-cad-20261022/bin/python
$PY review/flat132-reach-fit-2026-10-23/validation/certify_dynamic_mode_equivalence.py
$PY review/flat132-reach-fit-2026-10-23/validation/audit_native_step.py
$PY review/flat132-reach-fit-2026-10-23/validation/check_r5_domain.py
$PY review/flat132-reach-fit-2026-10-23/validation/validate_finished.py review/flat132-reach-fit-2026-10-23/validation/manifest.json
$PY review/flat132-reach-fit-2026-10-23/validation/audit_reach_fit.py
$PY review/flat132-reach-fit-2026-10-23/validation/certify_source_fit.py
$PY review/flat132-reach-fit-2026-10-23/validation/summarize_validation.py
```

`prepare_manifest.py` can rebuild the intent manifest using `--neutral`, `--step`, `--workspace` and four `--native-pose MODE USER_U PRELOAD TRIM ZIP` records: dynamic28/2/0, isometric13/2/0, dynamic28/2/−0.8, dynamic30/0/+0.8. Rebinding requires a fresh full audit, then `bind_version.py` may record the verified immutable native checkpoint. Rerun the source-fit certificate and summary after binding. This is provenance metadata, not a geometry recomputation.
