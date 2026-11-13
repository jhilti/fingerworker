# Actual TE FX1901 CAD reference

The unchanged manufacturer STEP is `TE_FX1901_official_original.step` (identical to `vendor/te_fx1901/c-fx1901-0001-0200-l-f-3d.stp`, SHA256 `fe4aee5f64f19f4859d2cfdbf73cb24d3cd91b0987949a6fcf28ada22e46cac3`). It identifies TE Connectivity, product C-FX1901-0001-0200-L, Creo, 15 February 2018, millimetres. Its valid single solid has 107 faces and volume 3933.719319616 mm³.

Use `TE_FX1901_actual_apex_aligned_132_mm.step` and the same-name STL for the 132 mm reference study. These apply only a rigid rotation and translation. The native central spherical contact apex `(0,0,0)` maps to the existing force-pusher tip `(-1.9,0,18)`; the radial lead points toward +Y. Full transform and source hashes are in `sensor-geometry-audit.json`. This registration requires confirmation against the matching FX1901 drawing and actual part before machining.

The actual STEP housing is **Ø25 × 7.95 mm**, with its short four-wire stub extending to native X27. The prior H01 model used Ø19.75 × 5.45 mm plus a separate boss. The stored May 2020 FX1901 PDF dimensions illustrations are labeled **FX1900-XXX1 / FX1900-0000** and show those smaller dimensions; they do not match the actual FX1901 STEP.

At the preserved force-contact datum, the real rear face lies at X−9.85, 1.85 mm behind the old proxy rear face X−8. Nominal mesh intersections with unchanged 132 mm parts are:

| Part | Intersection | Viewer overlay |
| --- | ---: | --- |
| H12 backing cassette | 582.55 mm³ | `conflict-H12.stl` |
| P01 frame | 54.10 mm³ | `conflict-P01.stl` |
| P05 floating yoke | 733.72 mm³ | `conflict-P05.stl` |
| H02 force pusher | 0 mm³ | Contact apex aligned |
| H13 preload adjuster | 0 mm³ | Clear in this pose |

**The actual sensor does not fit the unchanged mount.** No mechanism geometry, source, manufacturing package, or load rating was changed by this reference study. Prior checks made with the smaller sensor proxy do not establish real-sensor fit.

The manufacturer STEP includes only a short wire stub, with no full flexible cable or connector. H01c/H01d remain routing approximations if shown elsewhere.

The STL uses 0.01 mm linear deflection / 0.08 rad angular deflection. Two zero-area tessellator pole triangles were discarded after identical boundary vertices were merged; no holes were filled and no surface was remeshed. Both STEP exports reimport as valid solids; the final STL and three conflict meshes reload as closed volumes. See `export-roundtrip-validation.json` for evidence.

`TE_FX1901_actual_contact_aligned_132_mm.*` is a rejected intermediate that aligned the flat disk under the actual spherical button. It causes 0.51 mm pusher penetration and must not be used. The final file uses **apex_aligned** in its name.

Reproduce the measured geometry and mesh audit with `inspect_sensor.py` using `/tmp/fingerworker-sensor-cad-20261022/bin/python` (cadquery-ocp 8.0.1.1, trimesh 5.1.1, manifold3d 3.5.4).
