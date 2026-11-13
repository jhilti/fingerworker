# Fixed front support: printability review

Date: 2026-11-03. Design review for the user-confirmed removal of the central preload mechanism. The earlier adjustable R12 exports are superseded. This note is not a final native/slice release.

The former H11 nut pocket has a 12.4 mm square opening, and H15 adds a broad rear recess, two small horizontal driver bores and a vertical locking access. Omitting these features makes the reaction portal a simpler continuous wall in the existing upright P01 orientation. Removing the hardware also removes the reason for the narrow H15 palm service notch. The separate P09 electronics lid should remain: its PCB keeper, battery rail and wire clamp stay support-free in their existing print orientation.

The mechanics proposal grows the fixed support from the base rather than hanging a new shelf from the portal. It spans X−16.2…−12, with the YZ profile:

`(−9,3.8), (9,3.8), (9,9.5), (11,11.5), (11,26), (−11,26), (−11,11.5), (−9,9.5)`.

This profile has a continuous lower pillar, two 45° widening shoulders and a vertical front contact face at X−12. It overlaps the base and existing portal by0.2 mm. The lower |Y|≤9 pillar leaves0.5 mm to the nearest nominal lower H25 screw-tip envelope at |Y|9.5. Its Z26 top lies1.5 mm below the upper screw-tip envelope at Z27.5. Therefore no tiny screw-tip pockets or added contact-surface supports should be necessary; final native clearance and actual slicing must verify this.

The old reactionTopBridge spans X−16.2…−12.5 and Z30…33, leaving a3.5 mm forward projection above the fixed support. Its underside would become an unnecessary internal overhang, and the new pillar could prevent bed-only supports from reaching it. **The mechanics candidate removes this obsolete bridge**, retaining the solid portal wall and both side buttresses. The free removed stock is X−16…−12.5, Y±20.3, Z30…33; its overlap in the wall/buttresses stays intact. This leaves the top of the new support open and removes the roof-support cleanup problem.

Final printing checks should bind the complete R12 STEP/STLs to the sliced archive, confirm the new support contact face has no support, verify the two widening shoulders print continuously from the base, inspect any residual roof bridge, and re-run the rear-gate and enclosure tests in `validation/check_print_features.py`. Nominal geometry and slice checks do not establish real PLA strength, fit or durability.

## Final native and slice result

The final fixed-front source and corrected P06 gate were exported and sliced. `print/bambu-R12-simplified-2026-11-03/validation/print-feature-check.json` reports **65 passed checks** for actual H2D 0.4 mm PLA paths. It binds native STEP `b2c076642b22f99a251b8e2a6ac20da9f251696e892448a2651ee8b636f32021` and sliced archive `4944d6e090a8048ba8639c9e7c04fd672f24312208422febea1680ba05681e4e`.

The fixed P01 pillar grows continuously from the base. Its vertical sensor contact face and both 45° shoulders have no support paths; the obsolete reaction roof and trapped roof supports are absent. The rear frame catches also require no local support in this slice. Native checks separately account for the inherited sensor-floor cut that intersects the bottom of the support; contact-area calculations therefore use the actual final solid rather than the uncut candidate prism.

P06 is support-free. Both long PLA beams print on the bed, both hooks reach their final height, flexure gaps and functional rod passages stay open, and all four optional M3 holes are empty in exact native CAD and actual toolpaths. The previous Boolean-order defect that refilled the two inner holes was corrected before this final slice. At the teardrop apex, bridge-tagged paths up to4.636 mm include their supported anchors: subtracting actual prior-layer bead footprints leaves only0.36801 mm of unsupported centerline on each side.

The new Q01 fixture also prints without support or bridge tags. Its broad12×22.3 mm reaction face faces down; the measured first-layer footprint is11.70×22.00 mm, exactly matching the actual0.15 mm elephant-foot compensation per edge. The P05 shoulder faces upward. P08/P09 retained clip, gap, hook and support-region checks pass. These are nominal CAD and slicer checks; physical PLA fit, snap force, support cleanup and load capacity remain print-test questions.
