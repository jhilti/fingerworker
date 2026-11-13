# Flat132 R6 — one-piece rigid printed palm

R6 replaces the R5 rigid palm core and separate TPU half-shell with **one rigid printed P02 block**. Its outer half-round contact envelope, flat back, mounting interfaces and palm-to-finger position stay the same. **There is no P03 sleeve to print or fit.** The four small P07 return bumpers remain flexible parts.

**Native regeneration and independent nominal geometry validation pass with zero failed or unresolved checks.** The 105-solid neutral STEP, all three native pose exports, one-piece P02 construction and exact preservation of 104 other solids are verified. The 500 N design target, printed strength, deformation, creep, fatigue and hard-palm comfort require physical qualification. The former optional 9 mm electronics-cover extension is not part of this revision; the existing electronics enclosure and lid remain.

The R5 closer-grip mechanism is retained: **132 mm frame width, 72 mm finger opening, 28–30 mm dynamic travel and two 81 mm steel isometric sleeves**. The one-piece palm has a 10.25 mm outer radius, axis X−27 / Z19.75 mm and wrist contact X−37.25 mm. The existing keyed mounts and electronics mounting pilots remain.

The new palm receives a focused exact-geometry, motion and service audit. Other checks are inherited from frozen R5 only through exact source preservation and 104 unchanged native body identities.

Read [print and assembly notes](PRINT_NOTES.md), [finalization notes](finalization-notes.md), [final specification](final-specification.json) and [validation](validation/validation-summary.md). The native-derived sets contain **14 print STLs**, **52 device assembly STLs** and **two 81 mm sleeve STLs** in `hardware-mm`, in millimetres and original assembly coordinates. A closed solid CAD block does not prescribe slicer infill; material and print settings still need selection and testing.

The R5 spring pretension remains: about **40–53 N initial force for the light pair**, or **67–82 N for the stronger pair**, over 0–2 mm preload. While the carriage stays against its return pads, hand force first unloads that reaction; the additional sensor reading alone does not establish total hand force in this initial interval. P11 cam setting remains manual (`camTrim − preload`), with physical switch calibration and clamp checks required. Firmware is unchanged, including the NC-open force/peak block.

[Frozen R5 baseline](https://cad.onshape.com/documents/15316cc6370631845af136b2/v/ef00e6d9683bc3bffae42912/e/d253eb87b70818ebde8215f0) · [R6 interactive viewer](http://127.0.0.1:8774/viewer/viewer.html)

Source: [fingerworker_flat132_solid_palm.fs](fingerworker_flat132_solid_palm.fs), SHA256 `62fabee79cf36d0e0b6d4cd8430700519dbc529a5ea08f70018b14b0c3f2271f`. [Builder](build_solid_palm.py) and [change record](source-build.json) preserve a reversible ledger against frozen R5. Run `python3 build_solid_palm.py` to reproduce the source text; the compact package includes the exact baseline fallback.

[Frozen Onshape R6](https://cad.onshape.com/documents/15316cc6370631845af136b2/v/342570da84b0f424f988575d/e/d253eb87b70818ebde8215f0) · [Native neutral STEP](native/Flat132_R6_final_AP214.step)
