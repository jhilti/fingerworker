# Focused print/assembly review — R9 fit prototype

The print sources are the frozen R9 native STLs from Onshape version `e8f782e27bfe45394bf4038b` (FeatureScript SHA256 `16972ba9341f4cdf763a5570dad82a4fbd601f0935d0a7657be85813f97ff2b1`). Q01 is a separate local, unthreaded fixture. The project applies rigid rotations/translations at scale 1; it does not modify product CAD. Unchanged R8 design evidence is retained through the focused R9 native identity audit; the new P02 bearings are checked separately. CAD evidence is not a physical print qualification.

| Piece | Orientation and relevant constraint |
|---|---|
| P01 | Underside down, 35 mm high; broad bed contact. Insert pilots remain vertical and blind floors must remain intact. |
| P02 | Wrist ledge X−46.1 down, 36.6 mm high. The initial flat contact is 186 mm², with a 5 mm brim/supports. Both new X−22.75 compression bearings face upward; each has 33 actual top-surface segments and no adjacent support in the scoped comparison slice. The critical Z9.5 lid-gap face remains vertical. Curved wrist skin support marks need gentle comfort cleanup. |
| P04 | Rear X119 down, 59 mm high. Central dovetail and rod axes print vertically. Supports in the open finger cavity and cam recess are accessible before assembly. |
| P05 | Native Z up, 22 mm high. Integral stop undersides sit on the bed; support beneath the exposed rear rib is accessible. Horizontal rod bores use short bridges. This retains the X direction of the stop arms within the layers, without establishing load capacity. |
| P060/P061 | Native Z up, 26 mm high; deep M3 head bores stay open. The 6.6 mm tongue-guide roof bridges. Buildplate-only support under the rear roof extension is external to the main body (X>128.5), accessible before assembly. |
| P120/P121 | Front X119.2 down, 9.4 mm high. Early fork/connector islands receive accessible bed support; rod and thrust-shaft bores print vertically. Keep the 1.2 mm lower thrust plate and M2 slot intact. |
| P08 | Tray bottom down. USB roof receives support removable through the open tray/USB port. Preserve the small PCB locating ledges. |
| P09 | Smooth outer lid down, ribs upward; clean the countersinks and keep fitted heads flush. |
| P11 | Top Z19 down. The Ø4.2 blind insert pilot ends with a short bridge. Remove elephant foot from its open entry without drilling through the floor. |
| P07 proxies | Large 4.5×6 mm faces down, local 0.1 mm layers; actual last model path must be at 1.50 mm. Hard PLA plus adhesive differs from TPU and must not be used for load/return cushioning tests. |
| H040/H041 proxies | Ø6×141 mm native geometry, horizontal print. Roundness, seam and support cleanup affect friction; actual steel rods can replace these for the same unloaded fit trial. |
| Q01 | Square locating end down, 28 mm high. Bed support beneath the Ø18 flange and on-model support beneath the Ø8 shoulder are removable. Preserve the 17 mm axial datum spacing and plain Ø3 tail. |

Relevant nominal sections remain product geometry: P04's 1.3 mm local guide roof, P05's 10×22 mm stop roots / 14×22 mm contact faces, P12's 1.2 mm thrust plate, and the 0.6 mm lid-to-palm gap. These small clearances/sections require physical cleanup and fit checks. First/last actual extrusion paths and localized supports are checked separately in `qa-toolpaths.json`; neither the section dimensions nor slicer infill establish a 500 N rating.

The unchanged Q01 inherits its frozen R8 independent exact STEP review, which checks one connected solid; literal CSG identity; proper rigid print transform; zero overlap with all sixteen printed product bodies and both rod proxies; positive portal/yoke bearing contacts; continuous front insertion and yoke-over-tail assembly; and the complete p=0, a=0…2, u=0…30−a motion domain. Q01 has radial location only, with no axial latch. It replaces the whole sensor/preload stack solely for supported, gentle hand fit. Springs, isometric sleeves, force tests and powered measurement are outside this trial.

R9 P02 bearing faces have 91 mm² nominal area each and are deliberate boundary contacts with fixed P01. The wrist-down 0.2 mm slice places their top skin at approximately X−22.700 rather than nominal −22.750 mm (0.05 mm layer rounding). This is not a prescribed press fit: check simultaneous gentle contact and real frame dimensions before tightening. Never preload the portal by forcing the palm screws. Added brace stock remains at X≤−22.75, while Q01 starts X−20.5; their complete axial envelopes have at least 2.25 mm nominal separation. No springs/load or measurement test is valid with Q01.
