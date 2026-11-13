# Switch-fit corrective proposal

**Status: PENDING_FACTORY_STEP_NATIVE_REGEN_AND_VALIDATION.** A separate R4 candidate is feasible using switch translation **+4mm X, +1mm Y, +1.5mm Z** and the coordinated cam/support edits below. Local nominal mesh checks found no additional positive-volume conflict. **No R3 FeatureScript or native CAD was edited; P05 remains intact.** This is a proposal, not a released or physically qualified design.

The R3 solder-tab-envelope conflict is independently confirmed: at2mm preload three tab envelopes each overlap P05 by1.44mm³,4.32mm³ total. This omitted geometry requires correction before claiming the actual switch fits. The exact SS-01GL2 STEP still requires authenticated access; proposed terminal/lug bodies must be labeled **datasheet envelopes**, without a factory-CAD claim.

| Item | Preferred coordinates / change |
|---|---|
| H09 main body |X18…28.2, Y−16…3.8, Z7.5…13.9 |
| Mount axes |X20.5, Y−10.9 and−1.4; through toolsZ6.5…14.5, nominalØ2.35 |
| P01 pedestal |X17…29, Y−16.5…5, Z3.8…7.5 |
| M2 insert pilots |Same axes, Ø3.2, toolsZ3.5…7.7; actual4mm depth fromZ7.5 |
| H10 cam |M3×8, headX64…67, shankX67…75, centreY3.5/Z11.5; backs out by preload and moves with stroke |
| H10 recess |Ø5.8, X63.8…68; insert pilotØ4.2, X67.8…73; entryX68, nominalL4 endsX72 |
| H10 through bore |Ø3.4, X63…76.5; cam nub frontX65 |
| Tab reference boxes |X14.1…18, centresY−14.4/−5.6/+1.7, thickness0.5Y, Z9.1…12.3 |

Keep the pedestal's bottom atZ3.8 and **extend its top**; translating the entire pedestal upward would detach it from the base. Trim its shifted lower-Y edge to−16.5. An untrimmed raised pedestal overlaps the negative sensing-stop arm. Preferred +Y1 gives **1mm nominal body-to-stop gap**,0.5mm pedestal-to-stop gap and0.5mm pedestal support beyond the body edge. The earlier +Y0.5 option also passed local checks, but left only0.5mm body gap and no nominal edge support margin. These gaps remain subject to switch±0.4mm general dimensional tolerance, printing variation and deflection.

The tabs gain **3.1mm nominal axial clearance from P05 at2mm preload**, plus1.6mm above the new pedestal. This is raw space: solder and wire insulation/bends remain to be defined. To retain1mm axial margin, any joint projection toward the yoke must stay within2.1mm beyond the tab tip. Route and inspect real wires without cutting P05's force-transmitting web. The nominal lug reference reachesX17.6; its exact profile and thickness-axis extent remain unresolved without factory geometry.

Raising H10 toZ11.5 keeps the Ø5.8 head recess1.3mm above the female guide roofZ7.3. The modeled Ø5.5 head has0.15mm nominal radial clearance. M3×8 retains4mm nominal engagement in the assumed L4 insert across preload0…2; it keeps the old distal screw-tip/bore limit and avoids extending the screw toward the finger pocket. Actual insert dimensions and screw-head tolerances still need checking.

The switch remains6.4mm thick, so existing M2×10/washer nominal engagement is preserved: **min(3,3.6−w)mm**, full3mm for washer thicknessw≤0.6mm. Pilot floor isZ3.5 and screw tipZ3.9+w, leaving0.4+w nominal tip clearance. The manufacturer's M2.3 mounting recommendation remains a difference; do not apply its torque directly to the M2/printed joint.

Preferred local study: 62 contact-region checks, **zero positive-volume conflicts**, using source-equivalent local CSG on R3 native meshes. Cases include preload0/2; neutral, isometric15−p and dynamic30−p; body/pedestal/tab/lug to fixed and moving parts; recessed cam fit; and intended H10/roller contact. The changed P01/P04/H10 mesh constructs are valid Manifold solids. This does not replace native regeneration, all-pairs/continuous-motion validation, or exact STEP verification.

A representative radius1.5mm L-key envelope with20mm short leg clears the nearby proxy geometry at neutral/unloaded2mm preload; minimum roller gap is about0.96mm. It is an external tool-access study, not a modeled hex-socket engagement or approved purchased tool. Cam adjustment remains manual; a physical locking method is not established by the smooth CAD hardware.

The operating datum moves toX35±0.8. The cam face reachesX34 at the existing30−preload stop, preserving **1mm nominal trip lead**, with0.2…1.8mm from OP tolerance alone. Calibrate the real switch and check allowed overtravel, manual reset and locking. Preserve NC fail-safe behavior; no firmware changes or Newton-display enablement follow from this proposal. R3 palm,132/72/35 geometry, travel, sensor and reinforced P05 remain unchanged.

[Detailed proposal and local checks](switch-fit-proposal.json). Baseline source SHA256 `4665c3ec4e983e478d34c6cfe923b3b60e6c8848f36b7c54b55b1989eaab6326`.
