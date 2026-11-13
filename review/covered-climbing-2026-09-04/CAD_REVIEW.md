# Fingerworker climbing-pocket review — 4 September 2026

The model is saved in [Onshape](https://cad.onshape.com/documents/15316cc6370631845af136b2/w/664d0779b5d992870442f997/e/d253eb87b70818ebde8215f0), with editable source in `fingerworker_mvp.fs`. The previous raised-grip revision and its evidence are preserved in `review/raised-grip-2026-09-04/`.

## Shape and contact surfaces

The raised bar and its uprights are replaced by a recessed four-finger climbing pocket inspired by the user's hangboard reference. The pocket has rounded plan corners, a continuous R4 loaded lip, and a warm brown finish. Its deck is flush with the moving enclosure. A 0.6 mm nominal assembly seam and small R1 outer top edge keep the surfaces visually tidy.

| Item | Revised nominal value |
|---|---:|
| Pocket width × fore/aft opening | 94 × 34 mm |
| Pocket depth | 20 mm |
| Pocket plan corner / contact lip radius | R8 / R4 mm |
| Front lip wall thickness | 12 mm |
| Pocket floor / deck top Z | 39.5 / 59.5 mm |
| Overall device height, including lower tray | 63.5 mm |
| Previous overall height | 92 mm |
| Height reduction | 28.5 mm, approximately 31% |
| Open / fully pulled X datum span | 100 / 70 mm |
| Working travel / guide spacing | 30 / 130 mm |
| Palm pad underside / top / cushion top Z | 39 / 47 / 49.5 mm |

The loaded inner wall stays at X137 at rest, measured from the palm-pad end at X37. The rounded edges and elastomer compression affect actual skin contact; the 100/70 mm values are CAD datum dimensions.

## Mechanical changes

- Lowered the spring and load-cell axes by 6 mm to Z25. Added lower reaction pads to support the complete moving spring-seat washers.
- Retained the Ø17.2 mm spring tunnels and Ø6.6 mm through guide bores from the earlier clearance repair.
- Lowered the palm support and switch bracket. The pocket floor retains 3.3 mm above the spring-seat recess envelope and 5.9 mm above spring tunnels.
- Shortened the fixed hood and inspection window; extended the moving hood forward to preserve its overlap. The fixed cover and deck stay separated at full travel.
- Added underside reliefs around the fixed hard-stop brackets, with 0.6 mm side clearance. Re-cut the steel strike-plate pockets after joining the deck; shortened the plates to 8 × 13.5 × 2 mm so they remain below the pocket floor.
- Preserved screwdriver access through the deck to the inner MGN12H screws. Moved enclosure bosses to X146/188, Y±72, clear of these mounting ports.
- Corrected the switch mounting datum from the supplier drawing, seated its case at Z12, and relieved the bracket around the case and hinge. The nominal operating position is 1 mm before the hard stop; the slots allow final click calibration. The roller now follows the carriage after initial contact. Its operating datum is manufacturer-dimensioned; the hinge position and motion are illustrative approximations of the drawing, not a force/deflection model.
- Updated screw lengths and fabrication notes in `EINKAUFSTEILE.md`: palm M4×10, moving hood M4×18, rail M3×8. Remove the moving hood for rail-carriage mounting access.

## Hand reference

The optional single hand body curls its fingers into the recess as the carriage moves. The heel stays at the palm cushion and the thumb clears the moving enclosure. It is excluded from the BOM and fitted specifically to the 20 mm pocket; the feature asks for it to be hidden if another pocket depth is selected.

`review/check_climbing_hand.py` samples 303,264 hand-surface points per pose at 0/15/30 mm against conservative pocket/deck/hood envelopes. It also checks fixed-length inverse kinematics at 61 travel positions. These checks pass, but the stylized hand is an illustrative fit reference, not population anthropometry.

## Verification evidence

The final revision is checked at 0, 15 and 30 mm displacement, with 40 parts including the hand. The diagnostic inspects 14 targeted solid pairs and reports zero solid interference in all three poses. This is not an exhaustive assembly or tolerance analysis.

| Pair / condition | Smallest checked separation |
|---|---:|
| Carriage / guide rods | 0.30 mm |
| Carriage / spring sweeps | 0.60 mm |
| Carriage / strike plates | 0.20 mm |
| Carriage / integrated base | 0.50 mm |
| Carriage / fixed hood | 3.26 mm |
| Fixed hood / moving hood | 12.50 mm |
| Switch actuator / case and bracket | 0.78 mm |
| Hand / climbing pocket | 0.10 mm |
| Hand / other device parts excluding cushion and carriage | 0.67 mm |

Onshape retains unclassified boundary-contact records for the four hood mounting bosses (20 records), palm-pad mounts (24), and hand/cushion contact (1). At full stroke, it also reports three boundary-contact records where the switch roller meets the carriage. These are expected mounting or actuation contacts; they are not silently relabeled as generic clearance passes. The raw records distinguish them from solid interference.

Final exact-solid results are recorded in the associated `review/onshape-flat-audit-*mm.txt` files. The diagnostic uses Onshape's [evCollision and evDistance APIs](https://cad.onshape.com/FsDoc/library.html#evCollision-Context-map). The independent `review/check_geometry.py` ledger checks nominal dimensions, lowered internal stack and stop-relief coverage at 61 stroke positions.

The CAD and numerical checks do not establish physical grip feel, friction, fatigue life, print strength or load capacity. Those require a finished prototype and appropriate mechanical testing. The revised integrated grip avoids the earlier elevated-bar overhang, but print orientation and supports around internal tunnels/recesses still need to be chosen for the intended material and process.

## Using the model

Double-click **FingerworkerMVP**, enable **Show hand reference**, and set **Preview displacement** from 0 to 30 mm. The fingers, carriage, seats, springs and moving cover follow the same displacement. For manufacturing exports, use 0 mm and hide the hand; this gives 39 device parts.

Saved views: `assets/onshape-climbing-product-open.png` and
`assets/onshape-climbing-hand-30mm.png`. The final working configuration
is open (0 mm displacement), with the hand hidden and 39 device parts.
