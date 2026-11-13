# Flat132 R3 — palm 7 mm closer

The palm contact surface is **7 mm closer to the finger pocket**. The full round bolster becomes a wrist-facing half-round, with a matching TPU cap and two integral retaining returns. Only P02 and P03 change shape from [R2](../flat132-strengthened-2026-10-22/README.md). The mounting holes, locating keys, electronics enclosure and finger mechanism retain their positions.

**Nominal CAD validation passes, with zero failed or unresolved checks.** The 132 mm frame, 72 mm clear opening, 35 mm height, 28–30 mm travel, reinforced reaction portal and integral sensor stops are retained. 500 N remains a design target requiring physical qualification.

The wrist contact tangent changes from X−44.25 to X−37.25 mm. The loaded finger-pocket wall remains at X77 minus stroke, giving a nominal contact-plane span of 114.25 mm at neutral instead of 121.25 mm. That is a 7 mm reduction at every stroke setting. This measurement is between source-defined contact planes; the original hand scan remains an approximate visual reference.

The central half-round keeps the original curved radius and contact width. The cap's two small end returns wrap the rigid flat face to provide nominal radial capture. Print tolerance, flexible installation, axial retention and hand comfort require a prototype check. The rigid core remains connected to its support plate; its half-round core/plate bond width is smaller than R2, so nominal clearance evidence does not establish equal strength.

[Frozen Onshape R3](https://cad.onshape.com/documents/15316cc6370631845af136b2/v/9bf146edbc2e61a5c4144a35/e/d253eb87b70818ebde8215f0) · [Open the interactive R3 viewer](http://127.0.0.1:8771/viewer/viewer.html) · [Native neutral STEP](native/Flat132_R3_final_AP214.step) · [CAD and full print set](deliverables/Flat132_R3_Palm_Fit.zip)

The full print set has 14 Pxx parts in millimetres and neutral assembly coordinates. For an existing R2 assembly, replace P02 and P03 together. This is a matched 132 mm revision; older 158 mm Rev D print sets remain separate. Read [print and assembly notes](PRINT_NOTES.md).

[Validation evidence](validation/validation-summary.md) covers all 105 native solids, the unchanged genuine manufacturer sensor, neutral/MAX28-p2/ISO13-p2 configurations, the complete legal motion domain, revised palm geometry and retained service paths. Exact STEP core/cap overlap and sensor symmetric difference are both zero. The cap/core STL facet artifact is bounded separately and does not replace the exact STEP check.

The current firmware still blocks qualified force/peak readings when the NC end switch opens. Reset H10 manually by minus the preload change after any preload adjustment. This CAD revision contains no firmware changes.

Source: [fingerworker_flat132_palm_fit.fs](fingerworker_flat132_palm_fit.fs), SHA256 `4665c3ec4e983e478d34c6cfe923b3b60e6c8848f36b7c54b55b1989eaab6326`. [Final specification](final-specification.json) records the native files, version and limits. R2 and earlier saved versions remain preserved.
