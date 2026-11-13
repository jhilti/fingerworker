# Heat-set insert audit — R3 palm-fit prototype

**Status: ACTUAL_STOCK_DIMENSIONS_REQUIRED.** The current CAD already reserves **11 insert locations**: 2 M4, 5 M3 and 4 M2. It contains **zero separate insert solids**. The holes are nominal pilots, not a match to the user's unidentified inserts. No R3 source or geometry was changed.

Source: [frozen R3 FeatureScript](../flat132-palm-fit-2026-10-23/fingerworker_flat132_palm_fit.fs), SHA256 `4665c3ec4e983e478d34c6cfe923b3b60e6c8848f36b7c54b55b1989eaab6326`. Coordinates are mm in the assembly frame. This source audit expands the loops; it is not a thermal-tool or native BRep clearance certificate.

| Interface / host | Count | Entry centres (X,Y,Z) | Existing pilot / actual depth in plastic | Intended insert length | Insertion / access | Screw and nominal engagement |
|---|---:|---|---|---:|---|---|
| Palm joint / P01 feet | 2 M4 | (−16, ±31.5, 6.5) | Ø5.2 ×6.3 blind | 6 | From above, −Z; P02 removed | M4×10, underhead Z10.5, tip Z0.5: **6 mm** engagement |
| Rear retainers / P01 feet | 4 M3 | (129.5, −59/−43/43/59, 4.5) | Ø4.2 ×4 blind | 4 | From above, −Z; rear blocks removed | M3×8, underhead Z10, tip Z2: **2.5 mm** engagement |
| Click cam / P04 | 1 M3 | (64, 2.5, 10) | Ø4.2 ×5; Ø3.4 passage continues | 4 | From wrist/front, +X; carriage removed | H10 M3×12: **4 mm** throughout preload0–2 |
| Switch / P01 pedestal | 2 M2 | (16.5, −11.9/−2.4, 6) | Ø3.2 ×4 blind | 3 | From above, −Z; switch removed | M2×10 + thin washer: **3 mm if washer ≤0.6 mm** |
| Case attachment / P02 underside | 2 M2 | (−26.5, ±59, 9.5) | Ø3.2 ×4 blind | 4 | From below, +Z; tray detached | M2×6, underhead Z7, tip Z13: **3.5 mm** engagement |

The raw cutting tools extend outside their host to ensure an open hole: palm Z0.2…7.5, rear Z0.5…4.6, cam X63.8…69, switch Z2…6.2, case Z9.4…13.5. Their lengths **7.3/4.1/5.2/4.2/4.1 mm are not the physical blind depths**. The table uses actual entry surfaces. Nominal insert length is taken from existing purchasing/manufacturing notes, except the reduced current palm count comes from the R3 loop. The historical purchasing list still says four palm fasteners; R3 has two.

With inserts flush to their stated entries, palm pilots leave0.3 mm beyond the nominal L6 insert, rear L4 and case L4 leave **zero axial excess**, cam L4 leaves1 mm and switch L3 leaves1 mm. The respective remaining blind floors are palm2.2 mm above the base bottom, rear2.5 mm, switch4 mm, and case1 mm to P02's upper plate surface. The cam's larger pocket ends atX69 while the smaller screw passage continues toX76.5. Real insert dimensions, taper, flange, knurl pattern and melt-displacement allowance can require different holes.

Only H10 is modeled as a screw solid among these interfaces; the other ten screws and all eleven inserts are not separate CAD bodies. Adding eleven insert solids later would change the assembly body inventory and require that validation to be updated. A smooth reference body may represent purchased stock; its outer knurl envelope must not be inferred from the pilot diameter.

Five other fastening points are **M1.6 tapped-plastic pilots**, not heat-set pockets: three P09 lid screws and two P10 wire-clamp screws into P08. Existing pilots are Ø1.25 in Ø3.2 bosses, leaving0.975 mm radial plastic before any conversion. Lid bosses have4.3 mm blind depth; clamp bosses2.2 mm. Existing nominal screw calculations leave only0.1/0.2 mm tip-to-floor gaps respectively. These require stock-specific boss/pocket and electronics-clearance redesign if converted; simply widening the bores is not an established solution. The enclosure instructions specify hand-tapping M1.6×0.35.

The concrete integration plan is to match the available inserts to these eleven existing locations, starting with the case attachment interface. Obtain thread, maximum OD, overall length and manufacturer/part number or drawing, including flange/taper dimensions. Then set pocket size/depth, allowance and insertion orientation to that stock and recheck walls, screw engagement and assembly access. Install inserts before sensitive electronics and mating parts are fitted; an iron-tip envelope has not been defined or checked.

**Preserve the existing steel force path:** H11 M6×1 nut, H15 keeper, its through screws and H170/H171 captive steel nuts, H20 pusher nut, and H12's machined M2/M3 threads. These are not plastic insert candidates. Do not alter the R2 reinforced portal, integral P05 sensing stops, manual cam reset or firmware failsafe. The two-M4 palm joint and all physical retention/strength, including the500 N target, remain unqualified.

Detailed locations, conditional washer calculation, source line references and source hashes are in [insert-audit.json](insert-audit.json). Existing hardware intent is supported by [EINKAUFSTEILE.md](../../EINKAUFSTEILE.md) and [enclosure manufacturing notes](../../mechanical/manufacturing-2026-10-11/README.md); their historical counts and older mechanical geometry do not supersede R3.
