# R3 half-round palm: nominal native CAD validation

Status: **NOMINAL_GEOMETRY_CHECKS_PASS**. Failed checks: **0**. Unresolved checks: **0**.

Immutable checkpoint: [Onshape R3](https://cad.onshape.com/documents/15316cc6370631845af136b2/v/9bf146edbc2e61a5c4144a35/e/d253eb87b70818ebde8215f0).

Source SHA256: `4665c3ec4e983e478d34c6cfe923b3b60e6c8848f36b7c54b55b1989eaab6326`.

The nominal palm wrist tangent moves exactly **7 mm** toward the finger grip, from X−44.25 to X−37.25. The new axis is X−27/Z19.75. P02 retains the wrist-facing half of the radius 7.75 mm rigid core, and P03 uses the corresponding radius 10.25 mm TPU cap. Two 4 mm wide, 2.5 mm deep outboard return bands provide nominal capture around the core flat. Real fit, assembly flex, pull-off force, wear and creep remain prototype checks.

Only P02 and P03 change shape from R2. All remaining frame, mechanism, electronics and hardware bodies retain identical native geometry. Any raw facet-order change requires exact canonical triangle-coordinate identity without rounding or geometric tolerance. There are no added or removed hardware parts. Direct comparisons against the native R2 palm bounds check the 7 mm change.

The native model retains **52 device solids + 53 electronics reference solids = 105**. Neutral, maximum stroke 28 mm/preload 2 mm and isometric stroke 13 mm/preload 2 mm exports are checked. The complete continuous legal domain remains stroke ≥0, preload 0–2 mm, stroke+preload ≤30 mm. The 72 mm finger opening and all R2 reinforcement/stop geometry remain unchanged.

The H10 click cam still requires manual resetting by −preload after each preload change, followed by switch verification and relocking. The source models this configured position; it creates no automatic linkage.

Exact native STEP checks verify the genuine manufacturer sensor remains unchanged, the P02/P03 intersection has zero positive volume, and all 105 STEP solids are valid positive volumes uniquely matched to the native neutral STL inventory. A separate source certificate proves curved-surface and return-band-plane separation. Selected local probes cover the revised contact profile, half-core front, bands, mounting plate and clearances. The inherited configured motion, spring envelopes and finite service paths remain strict.

The evidence is nominal CAD geometry, not a physical load or comfort qualification. **500 N remains a design target rather than a verified working-load rating for the print.**

Full evidence: [validation.json](validation.json), [native-step-inventory.json](native-step-inventory.json), [source-fit-certificate.json](source-fit-certificate.json), and [validation-summary.json](validation-summary.json). The conservative in-memory candidate diagnostic is separate from the final native evidence.
