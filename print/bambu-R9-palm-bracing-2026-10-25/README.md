# Fingerworker R9 — braced palm print projects

**Only P02 changed from R8.** If the other pieces are already printed, use **Fingerworker_R9_P02_wrist_down_H2D_04mm_PLA.3mf** to reprint the palm alone: approximately **1 h 55 min / 28 g PLA**.

For the complete unloaded fit set, open **Fingerworker_R9_H2D_04mm_PLA_Fit_Test.3mf**: **19 full-size pieces on one plate**, approximately **17 h 58 min / 265 g PLA**, including supports and brims.

Both projects use **Bambu H2D · 0.4 mm · Generic PLA · textured PEI · 100% scale**. Keep the saved orientations and individual support settings. The stock filament profile uses **220 °C nozzle / 55 °C bed**. Main settings are **0.20 mm layers, 4 walls and 30% gyroid**; the thin P07 proxies and P11 use **0.10 mm** layers, with selected small parts at full infill.

P02 is printed **wrist ledge down**, so its two new fixed-frame bearing faces finish upward without support contact. Remove support remnants gently from the curved wrist surface. During assembly, both bearings should seat gently against the fixed frame; do not force interference or use the mounting screws to pull a poor fit into place.

Follow [the fit-test steps](FIT_TEST_README.md) and [hardware/assembly details](ASSEMBLY_DETAILS.md). The full set includes four **hard PLA pad proxies**, two **printed rod proxies** and **Q01, an unloaded fixture**. These check fit and supported manual travel; they do not reproduce TPU cushioning or qualify a force-bearing assembly. No sensor, electronics, springs, fasteners or heat-set inserts are included.

- **STL-print-oriented/**: 19 millimetre STLs in the saved print orientations, for individual reprints at 100%.
- **source-mm/**: exact native source files retained for provenance; their assembly coordinates are not the print layout.
- **fixture/**: Q01 geometry, source and instructions.
- **profiles/** and **source/**: pinned profiles and authoring/check scripts. Rebuilding references the original repository/R9 CAD export; the delivered 3MF files are self-contained.
- **preview/** and **validation/**: native previews and bound geometry/toolpath evidence; see [print QA notes](PRINT_QA_NOTES.md).

Both editable projects were sliced locally with official Bambu Studio 02.08.02.61 and checked independently. Actual P07 deposition reaches **1.50 mm**. Verification Gcode is kept outside this package. **No job was sent to a printer.** Physical fit and strength remain unqualified; do not load Q01 or the printed rod proxies.
