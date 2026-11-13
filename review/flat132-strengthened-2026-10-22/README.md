# Flat132 R2 — printed reinforcement and sensed stops

**Nominal geometry checks pass for the R2 CAD prototype.** Open the [immutable R2 Onshape version](https://cad.onshape.com/documents/15316cc6370631845af136b2/v/9bdcf9c3c67638228b40378b/e/d253eb87b70818ebde8215f0). The 500 N requirement remains a design target, not an established working-load rating. This revision changes the printed P01 frame and P05 sensor pressbar/yoke; R1 remains preserved at its [immutable version](https://cad.onshape.com/documents/15316cc6370631845af136b2/v/4c39034c17201905fdfbb1d6/e/d253eb87b70818ebde8215f0).

P01's reaction wall grows from 6 to 6.75 mm, its cassette guides from 3 to 5 mm, with upper gussets and a continuous roof bridge. The frame remains 132 mm wide and 35 mm high, with the 72 mm finger opening retained. The [comparative section review](loadpath-review.md) gives +66.9% root Iy and +68.5% front section modulus for the geometric reinforcement hypothesis. These are local section changes, not whole-device strength gains or proof of 500 N capacity.

P05 is one printed solid with both broad stop arms. Each endpoint face is 14 × 22 mm (308 mm²), centred at Y±24 and nominal X35 before preload translation. The old fixed stop blocks and H070/H071/H080/H081 hardware are removed. Endpoint reaction now follows **P04 → integral P05 stops → H02 → genuine H01 sensor → H12 → H13/H11/H15 → P01**. This revision adds no metal bracket. The keeper joint and the complete force path still require physical qualification, including one-sided loading.

The user-confirmed dynamic travel is **30 mm minus preload**, giving the simple **28–30 mm range** over the permitted preload settings. The existing H10 click cam must be reset manually after a preload change; its configured offset is −preload relative to the zero-preload setting. There is no automatic coupling or new cam lock.

| Additional preload | Maximum frame travel | Nominal switch trip | H10 offset from zero-preload setting |
| ---: | ---: | ---: | ---: |
| 0 mm | 30 mm | 29 mm | 0 mm |
| 1 mm | 29 mm | 28 mm | −1 mm |
| 2 mm | 28 mm | 27 mm | −2 mm |

Isometric sleeves retain the seated position `15 mm − preload`. The switch remains nominally 1 mm before the mechanical stop. Current firmware/app behavior at NC LOW still blocks qualified force and peak updates. This CAD revision does **not** enable an endpoint Newton display; firmware and its fail-closed behavior remain unchanged.

Replace **P01 and P05 as a matched pair**. Native comparison confirms that the other 12 printed parts retain their R1 geometry; P04 differs only in triangle ordering. The native inventory contains 52 device solids plus 53 electronics references, 105 valid, uniquely associated solids total. The source is [fingerworker_flat132_strengthened.fs](fingerworker_flat132_strengthened.fs), SHA256 `d5eca2f3d87bf4b9a47c1987ee91ba1d56e8c87003eca101677a148a2e605654`.

[Print and assembly notes](PRINT_NOTES.md) cover the verified nominal unloaded service paths and manual cam setup. The [validation report](validation/validation.json) records zero failed or unresolved checks, including the maximum dynamic pose at 28 mm travel / 2 mm preload and isometric pose at 13 mm / 2 mm. The genuine sensor has zero exact BRep geometry difference. The [native STEP inventory](validation/native-step-inventory.json) records all 105 valid solids. See [final-specification.json](final-specification.json) for file hashes and scope.

The compact bundle path is `deliverables/Flat132_R2_Printed_Reinforcement.zip`: matched P01/P05 prints, full native STEP, source, proofs and reports. The three large native pose ZIPs remain local provenance witnesses. Open the [interactive R2 viewer](http://127.0.0.1:8770/viewer/viewer.html) or [full native STEP](native/Flat132_R2_final_AP214.step).

Actual material, printing process, deformation, creep, fatigue, fastener/keeper behavior, calibration and asymmetric loading remain to be qualified. The hand scan is an approximate visual reference and does not establish physical hand fit.
