# Printing the 30 mm Fingerworker prototype

Revision 20 September 2026, exterior palm: use the new base, palm bracket and forward-pocket carriage together. Previous printed revisions are not a matching set. The assembled length is238.25 mm; the separate base remains216 ×210 mm.

Print only the 11 bodies named `P… PRINT` in Onshape. Hardware (`H…`) and the optional hand are reference geometry. Export in millimetres at 100% scale, preview displacement 0 mm, hand off.

The ready-to-use archive is `print/Fingerworker_30mm_print_pack.zip`. It contains all eleven device STL files, two fit coupons and these notes. Device meshes were exported from Onshape at Fine resolution, checked as closed, and moved to Z0. The sleeve and pads have also been rotated into the orientations below. No scaling or shape changes were applied. Arrange the separate parts in your slicer and assign rigid material or TPU as indicated by their filenames. The unchanged Onshape download is retained as `print/Fingerworker_30mm_Onshape_original.zip`.

## Fit first

Print `print/guide_coupon_male.stl` and `print/guide_coupon_female.stl` separately, flat bottoms down. These 30-mm-long coupons reproduce the model's 45° guide faces, 0.30 mm roof gap and 0.45 mm horizontal flank offset. Slide the female over the male from an end; in an assembled preview its bottom would be 4 mm above the male's bottom. Both files are checked as closed, consistently oriented meshes.

Remove strings and elephant-foot edges before judging fit. The pair should slide smoothly without obvious rocking. Adjust guide dimensions or printer compensation from this result before printing the base and carriage. These are separate prints, not a print-in-place pair.

## Orientation

| Part | Initial material / orientation | Supports and finishing |
|---|---|---|
| Base | PETG prototype; broad underside down | Male guides have 45° flanks. Horizontal sockets and sensor relief may need accessible local supports. |
| Carriage | PETG prototype; underside down, pocket up | Guide roofs span 13.5 mm. Use a calibrated bridge or removable local supports, cleared through open channel ends. Ream Ø6.6 rod passages as needed. |
| Floating yoke | PETG prototype; assembled bottom down | Supports under raised rear rib and sensor/cable relief are accessible. Ream Ø6.6 rod holes; preserve centred sensor contact face. |
| Palm bolster | PETG prototype; flat plate and ears down | Local support under round core overhang. Four M4 access wells sit on the mounting ears; keep them clear. Test ear strength and bracket deflection. |
| Rear retainers | PETG prototype; flat bottom down | Small blind sockets may need supports and reaming to Ø6.2. |
| Palm sleeve | TPU, about 95A starting point; stand on one end | Seam away from palm contact; tune hardness and fit physically. |
| Return pads | TPU; broad 4.5 × 6 mm face down | Print 1.5 mm thick; secure with thin compatible adhesive film. |

The base needs **216 × 210 mm of usable bed area**. It fits a 220 × 220 mm area with little margin; a brim may need a larger bed or local adhesion tabs. The carriage is approximately119 ×204 mm. Its rounded rear through-window provides switch clearance; keep it open. Do not scale the assembly to fit a smaller bed, because hardware interfaces would change.

PETG is a practical mechanical-prototype material, but bridging needs attention. See [Prusa's PETG guide](https://help.prusa3d.com/article/petg_2059?product=mini) and [bridge guidance](https://help.prusa3d.com/article/poor-bridging_1802?product=mk3-5). Material selection alone does not establish load capacity.

A starting slicer setup is a 0.4 or 0.6 mm nozzle, 0.2 mm layers, enough perimeters for roughly 3 mm walls, and substantial top/bottom thickness. Use solid local modifiers at the yoke, stop lugs and insert bosses. Review sliced toolpaths and support-removal routes. These are prototype settings, not a qualified process or guaranteed 500-N recipe.

Smooth the R4 finger lip and pocket transitions by hand. Remove seam ridges on the pulling surface. Check pocket and sleeve feel before installing springs, and keep abrasive fibre-filled surfaces away from skin. The screw cam permits click timing adjustment separately from the travel stops.

If using the bench-mount holes, use flush countersunk screws and countersink the printed Ø5.5 mm pilot holes to the actual heads after printing. Their tops must stay at or below the Z6 base surface, especially at the rear holes beside the carriage. Ordinary raised screw heads can obstruct its return. Clamps on the exposed base are another mounting option.

## Physical validation

Printed guides need fit calibration and wear testing. The exterior palm bracket is cantilevered and the carriage is longer; specifically test bracket ears, fastener retention and carriage deflection. Sensor readings and spring-rate calculations are not proof of structural strength. Start with unloaded fit/return checks and establish a tested working load for the actual material, print orientation and machine before training against it.

The source and previous design are retained so clearance, thickness and wear surfaces can be revised after a physical test.
