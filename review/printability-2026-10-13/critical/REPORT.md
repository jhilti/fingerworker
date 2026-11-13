# Printability review: P01, P04, P05

Reviewed the Rev E H2D / 0.4 mm / PETG project and the corresponding Rev D STLs. Four isolated orientation alternatives were sliced with the official Bambu Studio 02.08.02.61 CLI; all four returned success. These are geometry and slicer checks, not a physical print or a strength qualification.

| Part | Recommendation | Reason / cleanup |
|---|---|---|
| P01 base | Keep the flat underside on the bed. Add a 5 mm outer brim. Keep build-plate-only automatic supports. | The male rail grows at approximately 45 degrees and has no wide ceiling. The plate windows are through-open. Existing support under bottom edge rounding is accessible. Horizontal socket and screw holes are at most 6.4 mm diameter; inspect and deburr only if needed. The 156 × 180 mm PETG footprint can lift at corners; the brim increases adhesion. |
| P04 carriage | Rotate **+90 degrees about Y**, then translate bounding-box minimum to zero: rear X-max face on the bed. Use automatic supports **on the model as well** and a 5 mm brim. | The old downward female guide has a 33.5 mm roof and a 36 mm-wide relief roof, supported at only about 2 mm above the bed. That arrangement scars sliding surfaces. Upright printing makes the sliding faces vertical, and both rod bores vertical. The finger pocket needs supports, removable through its open side. Small supports at the guide relief transition remain accessible through the shallow open underside; remove them before assembly. |
| P05 yoke | Rotate **+90 degrees about Y**, then translate bounding-box minimum to zero: thick rear rib X-max face on the bed. Use **build-plate-only** automatic supports and a 5 mm brim. | The sensor recess opens upward and the rod / pusher holes become vertical. The back-side shoulders start 6.5 mm above the bed and need broad, accessible supports. This puts their support-contact marks on the rear side rather than the sensor shoulder. The small nuttrap ceiling bridges its 5.7 mm lateral opening; plate-only support keeps the pusher hole clear. |

The recommended transformations preserve all nominal geometry; no hole sizes, guide fit or assembly interfaces change. Generated candidate STLs are in this directory. The positive Y rotation maps original STL coordinates `(x, y, z)` to `(z, y, Xmax-x)` after normalization.

## Comparison evidence

| Alternative | Contact section at 0.1 mm | Official slicer estimate |
|---|---:|---:|
| P04 rear face on bed | 4,006.97 mm² | 93.36 g, 3 h 11 min |
| P04 front face on bed | 66.15 mm² | 110.32 g, 3 h 44 min |
| P05 rear rib on bed | 1,026.00 mm² | 45.55 g, 1 h 40 min |
| P05 front face on bed | 2,946.44 mm² | 42.20 g, 1 h 33 min |

P04 front-on-bed is rejected: the projecting cam becomes the first small contact patch and much of the body initially floats. P05 front-on-bed closes the 20.4 mm-diameter blind sensor recess over support; it is slightly cheaper but worsens the sensor shoulder surface.

The former flat P04's actual Rev E G-code contains support interface at print Z 1.492–2.15 mm beneath the guide. The upright P04 still has small support interface regions beside the relief transition at print Z about 14.4 and 44.75 mm; these contact the transverse relief step, not the longitudinal sliding plane. There are no Bridge-tagged extrusion segments inside the guide cavity for the upright experiment.

The upright P04 has zero Support / Support interface paths inside both 8 mm guide bores and the 3.4 mm cam passage. They print vertically. The finger pocket is side-open across its approximately 94 × 34 mm mouth, and the guide relief remains open along the shallow underside. These accesses permit removal of the generated supports without entering a closed cavity.

A targeted P05 comparison found that support-on-model produced 24 tiny support / interface paths in the pusher bore at the side-open nuttrap. Changing to **build-plate-only** removes all 24 while retaining the same broad shoulder support: 82 left-wing and 80 right-wing interface segments under the 6.5 mm-high shoulders. Both 6.6 mm guide bores also remain clear. The nuttrap's printed horizontal bridge spans 5.7 mm; the 2 mm trap thickness is its vertical interruption in this orientation. Its longest Bridge-tagged line is 8.768 mm including anchored ends. An explicit support-blocker experiment gave the same result and is unnecessary. See `P05-plate-only-validation.json`.

The reported generic Bridge path counts should **not** be read as unsupported-air distances: Bambu also labels solid infill printed over sparse infill and over supports as Bridge. Wide internal infill segments in P01 are therefore not evidence of a wide empty bridge. The geometry spans and support accessibility above are the basis of this assessment.

## Limits

Use these orientations for the existing spring-free form / assembly prototype. P04's upright layers are perpendicular to the X loading direction; its later loaded version needs a separate mechanical strength decision. Surface cleanup, hole fit, PETG adhesion and support separation still need confirmation on the user's printer. The female fit coupon cannot certify the full carriage when printed in a different orientation; check the full guide after cleanup.

Artifacts: `orientation_study.py`, `orientation-study.3mf`, `orientation-study.gcode.3mf`, `orientation-study-slice.log`, transformed STLs, native plate thumbnails and `critical-validation.json`.
