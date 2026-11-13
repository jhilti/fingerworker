# Fingerworker R8 — one plate PLA fit test

Open **Fingerworker_R8_H2D_04mm_PLA_Fit_Test.3mf** in Bambu Studio. It is an editable **one-plate project with 19 full-size pieces**, prepared for **Bambu H2D, 0.4 mm nozzle, Generic PLA, textured PEI**. Keep scale at **100%** and keep the saved orientations and individual support settings.

Estimated print: **18 h 3 min · 269 g PLA**, including supports/brims. Stock profile temperatures are **220 °C nozzle / 55 °C bed**. Main settings: **0.20 mm layers, 4 walls, 30% gyroid**; the four thin P07 proxies and P11 use **0.10 mm** layers, and selected small parts use full infill. Check your actual filament requirements before slicing on your own machine.

The plate contains 12 rigid R8 parts, four **hard PLA P07 shape proxies**, two **printed rod proxies**, and the separate **Q01 unloaded fixture**. Use it to check fit, reach, enclosure clearance and supported manual travel. **Do not load, squeeze against stops, fit springs or measure force with the printed rods/Q01.**

Follow [the fit-test steps](FIT_TEST_README.md), with [hardware and assembly details](ASSEMBLY_DETAILS.md). The force sensor, electronics, springs, real fasteners and heat-set inserts are not included in the print job.

- **STL-print-oriented/**: the 19 pieces already rotated to the saved print orientations, in millimetres, ready for individual reprints at 100%. These files need supports/settings as in the project.
- **source-mm/**: the exact source STLs retained for provenance; their original coordinates/orientations are not the print layout.
- **fixture/**: Q01 source, geometry and assembly note. Q01 is a test aid, not a production part.
- **profiles/** and **source/**: pinned official profile inputs and authoring/check scripts. Authoring scripts reference the original repository/R8 baseline; the 3MF is self-contained.
- **preview/**: native Bambu model preview. **PRINT_QA_NOTES.md** describes the actual sliced support/bridge checks.

The official Bambu 02.08.02.61 slice and independent geometry/toolpath checks passed **759 checks, zero failures/unresolved items**. Actual P07 model deposition reaches **1.50 mm**. The local slice is retained as internal verification; the delivered primary file is editable and contains no Gcode. No job was sent to a printer. Physical fit and strength remain to be tested.
