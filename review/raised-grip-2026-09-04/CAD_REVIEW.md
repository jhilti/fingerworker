# Fingerworker CAD review — 4 September 2026

The revised model is saved in [Onshape](https://cad.onshape.com/documents/15316cc6370631845af136b2/w/664d0779b5d992870442f997/e/d253eb87b70818ebde8215f0). Its source is `fingerworker_mvp.fs`; the previous source is preserved in `review/fingerworker_mvp_before_2026-09-04.fs`.

## What changed

- Removed solid material from the spring paths in the carriage: Ø17.2 mm tunnels around Ø16 mm spring envelopes.
- Extended the Ø6.6 mm guide passages through the entire carriage. The old blind bores could stop travel after roughly 1 mm.
- Raised the removable palm saddle by 12 mm and lowered the reaction wall, removing their overlap. Shortened the palm feet to clear the sensor connector.
- Added a separate 2.5 mm soft palm strip, elevated the finger bar to Z=78 mm, rounded its edges to R4, and added tapered support ribs. The contact strip leaves mounting screws accessible.
- Enlarged the finger opening, moved the cover bosses away from it, and extended the moving cover to overlap the fixed cover at rest.
- Added four fixed return cheeks and four 1 mm elastomer faces; relieved the moving rear cover around those stops.
- Moved the switch mounting screws beside its body onto a larger foot.
- Applied warm sand covers, dark olive contact surfaces, and a tinted inspection window.
- Added a separate, optional hand reference. Its fingers articulate as the grip moves; the hand is excluded from the BOM.

The existing Onshape feature instance contained **24 mm travel and 140 mm guide spacing**, despite different local defaults. These are now explicitly set to **30 mm and 130 mm** in Onshape.

## Key dimensions

| Item | Revised nominal value |
|---|---:|
| Open / closed X datum span | 100 / 70 mm |
| Working travel | 30 mm |
| Guide spacing | 130 mm |
| Finger bar section | 10 × 20 mm, R4 |
| Bar center height above base datum | 78 mm |
| Clear width between grip supports | 110 mm |
| Soft palm contact strip | 19 × 86 × 2.5 mm |
| Cover overlap at rest | 9 mm envelope; 1 mm full-height roof overlap |

The span is measured between the original X datum faces. It is not an anthropometric measurement of the illustrated hand or the new upper cushion surface. Elastomer compression and assembly tolerances affect the physical return position.

## Verification

Onshape regenerated the revised geometry at **0, 15 and 30 mm displacement**, with **40 parts including the one hand reference**. It reports zero solid interferences in the seven inspected pairs at each pose. These are targeted checks, not an exhaustive assembly, FEA, or tolerance analysis.

| Exact-solid pair | Minimum separation in all three poses | Result |
|---|---:|---|
| Carriage / guide rods | 0.30 mm | Clear |
| Carriage / spring sweeps | 0.60 mm | Clear |
| Fixed / moving cover | 1.00 mm | Clear |
| Hand / bar and carriage | 0.10 mm | Clear |
| Hand / remaining device, excluding cushion | 2.50 mm | Clear |
| Palm saddle / integrated base | 0 mm | Boundary contacts; see below |
| Hand / cushion | 0 mm | Boundary contact; see below |

Onshape classifies 24 saddle/base records and one hand/cushion record as unclassified abutments, not solid interference. These correspond to intended mounting/support contacts: the saddle underside and foot tops share Z=45 mm; the hand heel and cushion top share Z=63.5 mm. The raw classifications remain visible in the saved logs rather than being silently relabeled as a pass.

Evidence is retained in `review/onshape-audit-0mm.txt`, `review/onshape-audit-15mm.txt`, and `review/onshape-audit-30mm.txt`. The read-only diagnostic uses Onshape's [evCollision and evDistance APIs](https://cad.onshape.com/FsDoc/library.html#evCollision-Context-map). It runs with each feature regeneration and prints its results in FeatureScript notices.

The independent nominal geometry ledger (`python3 review/check_geometry.py`) also passes. It checks the identified former overlaps, intended span, guide and cover gaps, and return-stop reliefs at several points through travel. The hand is an illustrative pose, not population anthropometry or proof of hand fit.

## Using the model

Double-click **FingerworkerMVP**. Enable **Show hand reference** and set **Preview displacement** between 0 and 30 mm to inspect the grip. Springs, carriage, seats, cover, and fingers follow the same displacement. The final working configuration is 0 mm with the hand disabled, giving 39 device parts.

The saved pressing view is `assets/onshape-pressed-hand-30mm.png`; the product view is `assets/onshape-product-open.png`.

For manufacturing, use 0 mm with the hand disabled. The taller integrated grip requires print supports under the bar. The revised cushion and return bumpers require suitable retention; their hardness, finish, grip comfort, and load-bearing performance still need physical prototype testing. Updated fabrication notes and added soft parts are in `EINKAUFSTEILE.md`.
