# Flat132 R9 — palm bracing on the fixed frame

R9 adds **two broad integral compression pads to P02**, bearing on the fixed P01 portal at X−22.75 mm. Each nominal bearing face is **7 × 13 mm (91 mm²)**, at Y−25…−18 and Y18…25 / Z14…27 mm. The pads overlap the old palm root by 2 mm and have explicit R1.2 side and upper root blends. They leave the central keeper/adjuster clear and do not touch the floating P05 yoke, sensor stack or electronics lid.

**Reprint P02 only** for an existing R8 device. The curved wrist contact, keyed mounts, cover, 0.6 mm nominal lid gap, 72 mm finger opening, 28–30 mm stroke and 81 mm steel ISO sleeves remain. Default physical dimensions remain 176.5 × 132 × 35 mm. The two bearing faces share the reaction with the existing palm mounts; actual load sharing depends on printed contact fit and assembly.

**Native regeneration and independent nominal geometry checks pass, with zero failed or unresolved checks.** The STEP contains 123 valid solids: 70 device bodies and 53 electronics references. All 122 other native BReps are exactly unchanged from R8. Independent construction/contact, full-domain dynamic/isometric clearance and unloaded removal checks cover the changed palm. All four whole native pose witnesses are separately exported and source bound. These are CAD geometry checks; printed stiffness, tolerances, creep/fatigue and the 500 N design target remain physically unqualified.

Fit both printed bearing faces without forcing the portal or palm into preload when tightening the two M4 mounting screws. Check full contact, free sensor adjustment and unloaded motion. Keep the existing electronics-lid gap clear. Removal remains vertical after unloading/restraining stored spring energy and removing both M4 palm screws.

The compact package contains 16 raw print STLs, 70 neutral device STLs, two purchased steel-sleeve reference STLs, the native STEP, FeatureScript/builder, provenance, validation records and proof images. Raw STLs retain original assembly coordinates in millimetres; they are not slicer-oriented. Whole native pose ZIPs remain hash-bound project audit inputs and are omitted. The source builder can run from the bundled frozen R8 source; complete independent audit reruns also need the historical source-project dependency chain described in the evidence.

Read [print and assembly notes](PRINT_NOTES.md), [specification](final-specification.json) and [validation](validation/validation-summary.md).

[Interactive viewer](http://127.0.0.1:8777/viewer/viewer.html) · [Frozen R9 Onshape](https://cad.onshape.com/documents/15316cc6370631845af136b2/v/e8f782e27bfe45394bf4038b/e/d253eb87b70818ebde8215f0) · [Native STEP](native/Flat132_R9_final_AP214.step)

Source SHA-256: `16972ba9341f4cdf763a5570dad82a4fbd601f0935d0a7657be85813f97ff2b1`. Frozen R8 and earlier revisions remain unchanged.
