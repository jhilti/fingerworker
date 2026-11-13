# P03 adjuster clearance and P04 rear roof patch

The exact replacement manifest is [comfort-roof-patch.json](comfort-roof-patch.json). It contains two independent, uniquely matched changes against the preserved [V6 source](../onshape-flat132-2026-10-19/fingerworker_flat132.fs). Apply them to the new final-study source, not the preserved source. These additions have **not** been compiled in Onshape by this audit agent.

## P03 local shaft opening

The offending H13 feature is the Ø6 M6-shaft rear end at X−24 / Y0 / Z18 at zero preload. The Ø22 thumbwheel is farther forward, X−15.8…−13, and is not the source of the sleeve overlap. The original P03/H13 volume intersection is 3.085995 mm³.

Subtract a cylinder from **P03 only**, X−24.5…−21.3, centred Y0/Z18, radius 3.5 mm. This provides 0.5 mm nominal radial clearance around the shaft and at least 0.5 mm axial extension behind its zero-preload rear end. Preload moves the shaft forward by 0…2 mm; the sleeve ends at X−23.7503, so the relief covers all shaft positions close to the sleeve. It does not change H13 length, M6 engagement, the palm core or the principal wrist contact surface.

In the local STL hypothesis, 18.36685 mm³ of soft sleeve material is removed. The result remains a watertight volume. At 21 checked preload values from 0 to 2 mm, there is zero sleeve/adjuster volume overlap, and minimum measured gap is 0.499983 mm. This rounding difference is from tessellation. The opening is a shaft-clearance relief rather than a hand-fit alteration.

## P04 roof restoration

The old local roof issue at X114 / |Y|42 is caused by **`deckTopRound`**, not `armTopRound`: the arm boxes start at X116 and therefore do not exist at the measured X114 section. `deckTopRound` selects the front upper edge at X65 but uses `tangentPropagation:true`; it follows the R5 plan-corner perimeter onto the Y±42 upper side edges. This reduces local top Z30 to Z29. Above the R12 seat clearance, the retained roof approaches 3.063 mm.

After the pocket/lip operations, and **before** the existing R12 seat-relief cuts, add and union two shallow rounded caps:

| Dimension | Value |
| --- | --- |
| X | 111.5…116.5 mm |
| Y | −42…−40.5 and +40.5…+42 mm |
| Z | 28.5…30 mm |
| Plan-corner rounding | R0.35 on vertical edges |

The caps overlap the existing carriage body by finite volume and extend 0.5 mm beyond both ends of the audited X112…116 relief region, so neither end is a coincident-only attachment. The rounded plan ends avoid projecting square plan corners. They stay within the existing 84 mm deck width and top Z30. The top at the throat remains flat at Z30; adding the old R1 upper rounding again would recreate the defect.

The outer limit is deliberately **|Y|42 rather than 43**. At Y43 the unchanged R12 void reaches about Z26.944, leaving only about 3.056 mm below Z30. Extending to 43 would introduce a new outer ledge and would not improve the intended roof screen. The 40.5 inner limit keeps the additions outside the nominal 72 mm pocket and its maximum 4 mm lateral lip rounding. The actual pocket topology must still be checked after native regeneration.

The unchanged R12 cuts occur *after* cap union, so the added material cannot fill the steel-seat clearance. Steel seat OD22, its X116 reaction datum, spring length, the 72 mm finger opening and travel/preload datums remain unchanged. In the local STL hypothesis, added volume is 2.04822 mm³ total. Both modified parts remain watertight. At X114 and |Y|41.9 / 41.99 / 41.999 / 41.9999, the smallest measured roof is 4.062864 mm. New cap material has zero volume intersection with both bought-spring reference meshes, both moving seats and both rods at the neutral pose.

These local results are reproducible with [comfort-roof-mock.py](comfort-roof-mock.py); complete values, inputs and hashes are in [comfort-roof-mock.json](comfort-roof-mock.json). The mock applies equivalent nominal primitives to the exact old native STL. It does not prove the FeatureScript has compiled, replace a fresh native export, establish a global minimum ligament or qualify strength.

## Native acceptance still required

1. Apply the two exact replacements once in the new source. Regenerate the native Part Studio and inspect cap joins/fillets and the sleeve opening.
2. Export final native P03/P04; confirm valid single closed solids. Recompute P03/H13 gap through preload and the rear roof samples on those actual outputs.
3. Run the final assembly's full travel, spring/seat, electronics and assembly/service clearance checks. Existing source-specific preservation tests must be updated to permit only these declared changes.
4. Keep the hand scan and its registration unchanged. These two patches do not resolve the uncertain physical grip posture or qualify the new palm joint and printed load path.
