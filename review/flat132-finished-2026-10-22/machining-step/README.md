# Individual H12 / H23 STEP helpers

These two files are direct STEP exports of uniquely identified solids from the **final native Onshape assembly**. The geometric authority remains the [complete final native STEP](../native/Flat132_R1_final_AP214.step), SHA256 `6de4383e6423fd1f57bd353d8f42953ecdae841bee1e36b853fb312c679fd7ef`. They use the final source `041056629440056626b2f2f88a0db216693e48fff178687174478cb1f34227ef`.

| Reference | Individual STEP | Quantity | Source material/callout |
| --- | --- | ---: | --- |
| H12 | [Sensor backing plate](H12_sensor_backing_S355.step) | 1 | S355 steel; 30 × 30 × 2.15 mm main plate plus collar and side ears |
| H23 | [Loose sensor keeper](H23_loose_sensor_keeper_stainless.step) | 1 | 0.5 mm stainless sheet; grade not assigned; cut profile and deburr |

Each file retains its native neutral **assembly coordinates in millimetres**, scale 1. No origin centring, reorientation, reshaping, separate healing or scaling was performed. A direct `STEPControl_AsIs` transfer wrote each selected native solid. The [extractor](extract_native_solids.py) and [manifest](manifest.json) record the source association and output hashes. Other metal components, spacers, nuts and adjuster references remain available in the complete native assembly.

## Roundtrip check and its limit

Both files reimport as **one valid solid**, with unchanged face count, zero recorded bounds difference, zero minimum shape distance, and volume/area differences below 8 × 10⁻¹¹ in mm³/mm². H12 has 47 faces and H23 has 27. Native-solid association was unique in all six bounds and volume against the final native STL.

**The coincident Boolean equivalence check is unresolved for these helpers.** OCCT's two-way Cut returned inconsistent results despite matching bounds, volumes, areas and valid roundtrips. For H23, one reported difference even exceeds the part's entire volume. These results are recorded in the manifest; they are not presented as a proved zero symmetric difference. Use the complete final native STEP as the authority if exact individual-export equivalence is required. The helper exports do not replace the independently checked full assembly or its mechanical contact audit.

## Threads and fabrication details

H12's Ø2.5 pilot requires the finished **M3 × 0.5** retention thread, with 2 mm usable engagement, a flat-bottom blind detail and 1.1 mm runout corridor to the stated bore limit. Its M2 holes are nominal Ø1.7 envelopes; specify the finished M2 thread and chosen tap-drill process explicitly. Thread helices are not modelled. Smooth STEP holes and the nut/shaft envelopes elsewhere in the assembly are not substitutes for finished-thread drawing callouts.

These are **prototype CAD references**, not released machining drawings. Material grades beyond the source callouts, tolerances, surface finish, flatness, coatings, thread classes and torque values are not assigned here. Roundtrip numerical thresholds are identity checks, not manufacturing tolerances. The [finalization notes](../finalization-notes.md) describe assembly interfaces and remaining physical qualifications.

Preserve H12's planar sensor-bearing surface and the loose keeper's clearance. H23 clamps through four steel spacers and must remain clear of the sensor housing; shortening spacers or bending the keeper against the housing changes the force path. Physical strength, tolerance, friction and calibration qualification remain outstanding.
