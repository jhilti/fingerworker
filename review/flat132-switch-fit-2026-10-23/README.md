# Flat132 R4 — switch fit from manufacturer drawing

R4 moves the Omron **SS-01GL2** switch **+4 mm X, +1 mm Y and +1.5 mm Z** to clear its solder terminals from the moving sensor yoke. It updates the frame's switch pedestal and carriage's recessed cam mount, and replaces H10 with an **M3×8** screw. P05's reinforced force web and integral stops remain intact. The R3 palm contact remains 7 mm closer to the fingers.

**Nominal CAD validation passes with zero failed or unresolved checks.** The full neutral STEP has 105 valid solids; native MAX28-p2 and ISO13-p2 configurations, continuous motion and service checks pass. The six intended geometry changes are verified; the other 99 solids retain their geometry. This is a CAD prototype. No verified load rating is claimed; 500 N remains a physical qualification target.

The exact switch model is SS-01GL2 without a suffix: hinge roller lever, SPDT, solder terminals. Its main housing is nominally **19.8 × 10.2 × 6.4 mm**. H09 combines that housing with three solder-tab boxes and a conservative lower-lug strip based on the [Omron drawing](https://omronfs.omron.com/en_US/ecb/products/pdf/en-ss.pdf). It is labeled **DRAWING REF**, and H09a/H09b retain approximate actuator motion. No factory switch STEP is used. The genuine TE FX1901 sensor remains the unmodified manufacturer solid.

The missing terminal envelopes overlapped R3's yoke at 2 mm preload. R4 provides a nominal **3.1 mm terminal-to-yoke gap** there. The switch body has a 1 mm lateral gap to the negative sensing stop; the raised pedestal has a 0.5 mm gap. Solder, insulated wires, actual inserts and switch calibration require physical checks.

The frame remains **132 mm wide**, with a **72 mm clear finger opening**, **35 mm height**, 0–2 mm preload and **30 − preload mm** dynamic travel. Isometric seating remains **15 − preload mm**. Reset H10 manually by minus the preload change after each preload adjustment. Current firmware continues to block qualified force/peak readings when the NC switch opens; this revision contains no firmware changes.

Read [print and assembly notes](PRINT_NOTES.md) and [finalization notes](finalization-notes.md). The prepared sets contain **14 print STLs** and **52 device assembly STLs**, copied unchanged from the neutral native export in millimetres and assembly coordinates. For an existing R3 assembly, replace **P01 and P04 together**, reposition the switch and use the revised H10 hardware. P02/P03 and P05 are retained.

[Frozen Onshape R4](https://cad.onshape.com/documents/15316cc6370631845af136b2/v/1a51bc54c29fb727dcb77016/e/d253eb87b70818ebde8215f0) · [Interactive R4 viewer](http://127.0.0.1:8772/viewer/viewer.html) · [Native neutral STEP](native/Flat132_R4_final_AP214.step) · [CAD and full print set](deliverables/Flat132_R4_Switch_Fit.zip)

[Validation evidence](validation/validation-summary.md) includes all 105 native STEP solids, exact switch geometry checks, the native maximum/isometric poses and retained sensor/palm geometry. The switch remains a manufacturer-drawing clearance reference throughout these checks.

Source: [fingerworker_flat132_switch_fit.fs](fingerworker_flat132_switch_fit.fs), SHA256 `b150ff3a76cfaaaaa65ee1ea09e144b7c7d64e45459a925163e56918f48bb3c5`. [Final specification](final-specification.json) records the exports, immutable version and validation limits. [R3](../flat132-palm-fit-2026-10-23/README.md) and older immutable revisions remain preserved. The delivery script requires final nominal PASS and checks archive hashes.
