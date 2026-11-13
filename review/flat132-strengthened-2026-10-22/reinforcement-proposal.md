# Print-only reaction portal proposal

This candidate reinforces the circled P01 fixed reaction structure. The existing M6 adjuster, square nut, keeper, sensor cassette and manufacturer sensor remain unchanged. No new metal bracket or hardware is introduced. The 132 mm frame, 72 mm finger opening, 30 mm travel, synchronized 0–2 mm preload and 35 mm overall height are retained.

The primary changes are 5 mm thick cassette guides (formerly 3 mm), a 6.75 mm deep rear reaction wall (formerly 6 mm), a wider 50.8 mm reaction wall and a continuous upper bridge. The bridge closes the rear structure into a deeper portal around the cassette rather than relying on two thin exposed wall ends. It is above the adjustment wheel and behind the unmodified cassette. Upper side buttresses distribute the reaction into the widened guides while staying above the M3 retention heads. Their positive-Y window opens fully through the forward edge to clear the genuine radial lead base.

| Region | Candidate coordinates in mm | Reason |
| --- | --- | --- |
| Main wall | X−22.75…−16, Y±25.4, Z3.8…33 | More rear depth, width and an upper cross tie |
| Each fixed guide | absolute Y15.5…20.5 | 5 mm continuous root instead of 3 mm |
| Upper side buttress | absolute Y20.3…25.4, bottom Z11.75 | 0.2 mm union overlap with guide; at least 0.5 mm above retained M3 heads |
| Buttress forward edge | X−7.6 at Z13, sloping to X−12.5 at Z33 | Deep section with yoke clearance |
| Upper bridge | X−22.75…−12.5, Y±25.4, Z30…33 | 1 mm above wheel, 0.5 mm behind H12 rear plate |
| M3 lock driver access | P01-only R3.1, Z29.2…34 | Preserves original H15 hardware notch and old lower counterbore |
| Positive-Y lead window | X−10.35…−7.4, Y20.1…27.5, Z11.5…24.5 | No residual forward lip trapping the lead |

The widened guides require matching wider slot cutters and the P05 lower guide-cap reliefs. These are included in the full FeatureScript candidate. The local rear-wall keeper recess begins at X−23.1 to clear the original H15 rear plate after the wall is thickened rearwards. No H15 surface is altered.

The local Boolean hypothesis uses R1 native meshes and explicit new source geometry. It results in one connected P01 solid, adds 4471.236 mm³ of material and removes 65.070 mm³ for clearances. There is no new positive overlap with the 56 device parts at five preload positions. Measured gaps to added material include P02 0.5 mm, P03 1.0002 mm, H12 0.5 mm, P05 at least 0.5 mm and H18 at least 0.45 mm. Existing intentional H19 travel-stop contacts remain. This local calculation is preliminary evidence; final native regeneration and the full native motion/service audit remain required.

The new bridge changes two service motions. After removal of the palm/case module, keeper screws and adjuster, move H15 wristward 2.0 mm before lifting it. After the previously required disassembly, translate the complete sensor/yoke stack forward 3.5 mm before lifting it; the former 2.1 mm motion would bring the cassette's rear ears into the new bridge. The shallow floor pocket also extends forward to X2.9, providing 0.3 mm beyond the translated keeper while retaining the existing Z2.7 floor level and 4.7 mm frame thickness. The stack stays assembled until it is on the bench. A local continuous audit of these four finite service motions passes all 674 moving/fixed part pairs; the result remains preliminary to native export validation.

The user's 500 N force is a design target. Printed material, orientation, layer adhesion, creep, fatigue, nut-pocket bearing, mounting and actual tolerances have not been physically qualified. A larger section and a clear force path do not establish a 500 N working-load rating. The main force path remains sensor rear → H12 → M6 adjuster/nut → H15 and its retained fasteners → fixed frame. The front sensor keeper remains loose; reinforcement must not create an alternate path bypassing the sensor.

Files are a frozen full candidate source, a reproducible exact source-replacement builder (final candidate SHA256 `64b844211e5e562e5350327e8f9b6902fd8cb77e152984461e4020b42a2d451d`), its replacement/dimension manifest, local mesh hypotheses and local checks. R1 is preserved separately. No manufacturing approval is implied by this proposal.
