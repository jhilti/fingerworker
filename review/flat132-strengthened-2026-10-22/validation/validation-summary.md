# R2 nominal native CAD validation

Status: **NOMINAL_GEOMETRY_CHECKS_PASS**. Failed checks: **0**. Unresolved checks: **0**.

This is nominal geometry evidence. **500 N remains a design target, not a verified working-load rating for the print.** Material, print orientation, layer adhesion, tolerances, creep, fatigue and loaded prototype behavior require physical qualification.

Source SHA256: `d5eca2f3d87bf4b9a47c1987ee91ba1d56e8c87003eca101677a148a2e605654`.

Immutable checkpoint: [9bdcf9c3c67638228b40378b](https://cad.onshape.com/documents/15316cc6370631845af136b2/v/9bdcf9c3c67638228b40378b/e/d253eb87b70818ebde8215f0). Neutral ZIP and STEP retain source6c export provenance; an independently checked exact single UI-guard replacement binds their unchanged geometry to final sourced5. Maximum and isometric ZIP exports were generated from final sourced5.

Native model: **52 device solids +53 electronics reference solids =105**. Neutral and both regenerated maximum28/preload2 and isometric13/preload2 configurations are included. The declared legal domain is stroke≥0, preload0–2 mm, stroke+preload≤30 mm. Maximum frame stroke is 30 mm at preload0 and 28 mm at preload2. The complete continuous domain is certified rather than inferred from those native endpoint snapshots.

**Manual setup:** reset the H10 click cam by −preload after each preload change, verify switch operation, and relock. The native source includes this required configured position; it does not create an automatic coupling.

Only P01 and P05 change shape from R1. Four old M4 stop screw/nut previews are removed. All remaining neutral native STL bodies must remain byte-identical to R1, with H15/P04 facet ordering permitted only after exact native triangle-coordinate set identity (no rounding or tolerance) is proved. Integral printed P05 stop faces now return end force through the yoke and sensor. Selected probes measure 14×22 mm broad stop faces, 10×22 mm arm sections, a 6.75 mm reaction wall, 5 mm guides, a 3 mm upper bridge, the driver-access and lead clearances, and the retained 35 mm frame height.

The exact native sensor BRep is checked against the canonical manufacturer STEP. The exact native P02/P03 BRep pair is checked for zero positive overlap. All105 native STEP solids must be valid positive volumes and uniquely correspond to the final neutral STL inventory.

Declared service changes: after the listed removals at preload0, translate the assembled sensor/yoke/pusher stack **forward3.5 mm before lifting40 mm**, with no initial lift. H15 keeper removal requires a **2 mm wristward translation before lift**. The complete prerequisites and all finite pair paths are recorded in the manifest/report.

Full machine-readable evidence: [validation.json](validation.json), [native-step-inventory.json](native-step-inventory.json), [source-fit-certificate.json](source-fit-certificate.json) and the compact [validation-summary.json](validation-summary.json). R2 domain-adapter diagnostics check the new mapping mathematics independently; they are not physical strength evidence.
