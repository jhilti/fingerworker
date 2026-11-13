# Corrected 132 mm prototype — manufacturing and BOM change notes

**CAD prototype notes, 22 October 2026 — nominal native geometry, continuous motion, service and exact STEP roundtrip checks pass.** This document records the matched parts, assembly and service procedure for the genuine TE FX1901 sensor revision. The overall digital report is `NOMINAL_GEOMETRY_CHECKS_PASS`, with zero failed or unresolved checks. Manufacturing drawings still need tolerances and process callouts; physical load and hand-fit qualification remain outstanding.

The dimensional authority is the [integrated final-study source](fingerworker_flat132_finished.fs), SHA-256 `041056629440056626b2f2f88a0db216693e48fff178687174478cb1f34227ef`, compiled in Onshape after exact source readback. It includes the genuine manufacturer solid query, the [sleeve/roof patch](comfort-roof-patch.json), strengthened low guide caps and corrected Ø2.5 M3 tap pilots. The three source-bound final native exports and their hashes are listed in the [revision README](README.md). The [final AP214 STEP](native/Flat132_R1_final_AP214.step), SHA-256 `6de4383e6423fd1f57bd353d8f42953ecdae841bee1e36b853fb312c679fd7ef`, provides the neutral assembly's exact geometry. The [CAD prototype package](deliverables/Flat132_R1_CAD_Prototype.zip) consolidates the delivery files. The underlying V3 [mount proposal](mount-proposal.json) and [proposal source](mount-proposal.fs), SHA-256 `ebc9b31fa760c11fdcf182fd88e378abae6babac2ca214b169f0bf072b6f8d50`, are development provenance; the integrated source's later pilot/guide values supersede them. The preserved V6 and older manufacturing drawings remain historical references.

The [final immutable Onshape version](https://cad.onshape.com/documents/15316cc6370631845af136b2/v/4c39034c17201905fdfbb1d6/e/d253eb87b70818ebde8215f0), `4c39034c17201905fdfbb1d6`, preserves the 109-part neutral model with the final source. The [separate editable study branch](https://cad.onshape.com/documents/15316cc6370631845af136b2/w/3ee26cf6386f889ca7ae9519/e/d253eb87b70818ebde8215f0) remains available for subsequent revisions.

[Individual H12/H23 STEP convenience helpers](machining-step/README.md) are available for handling the two custom metal parts. Both reimport as one valid solid; their separate coincident Boolean equivalence comparison is inconclusive and documented in the helper manifest. The complete final native assembly STEP remains the geometry authority.

## Retained functional datums

| Item | Corrected prototype |
| --- | --- |
| Frame width | 132 mm |
| Clear finger opening / outside deck width | 72 / 84 mm |
| Dynamic stroke | 0–30 mm |
| Additional preload | 0–2 mm |
| Rod/spring axes | Y±51 / Z18 mm; Ø6 mm rods |
| Spring installed length | `101 − preload − stroke` mm |
| Isometric sleeves / seated stroke | 86 mm / `15 − preload` mm |
| Sensor | Genuine FX1901-0001-0200-L manufacturer STEP, scale 1 |
| Spherical contact apex at zero preload | X−1.9 / Y0 / Z18 mm |
| Sensor-bearing backing face | X−9.85 mm |
| Complete vertical envelope | **35 mm**, from base Z−2 to backing plate Z33 |

The larger vertical envelope is a real dimensional change from the old nominal 32 mm device. The genuine sensor alone reaches Z30.5; the retaining assembly reaches Z33. Neither the sensor nor the hand scan is rescaled to retain an old envelope claim.

## BOM delta for one prototype

| Reference | Quantity | Specification / change | Status |
| --- | ---: | --- | --- |
| H01 | 1 | Actual TE FX1901-0001-0200-L replaces the five smaller sensor/cable/connector proxy bodies | Purchased sensor retained; STEP is a reference, not a part to print |
| H12 | 1 | S355 steel cassette: 30 × 30 × 2.15 mm planar backing plate, locating collar and side retention ears; detailed profile from final STEP | **New machined part; old H12 geometry/drawing superseded for this prototype** |
| H23 | 1 | 0.5 mm stainless sheet keeper; Ø27 ring, Ø20 central opening, four 8 × 8 mm pads, four Ø2.2 clearance holes | New laser-cut and deburred part; loose capture only |
| H240–H243 | 4 | Steel spacers Ø4 outside / Ø2.2 inside × 8.45 mm long, square faced ends | New parts |
| H250–H253 | 4 | M2 × 12 panhead screws; head **maximum Ø4 × 1.6 mm high** | New standard fasteners; verify actual supplied head envelope |
| H190/H191 | 2 | Steel cassette-retention spacers Ø4 outside / Ø3.2 inside × **6 mm** | Changed from 4 mm; intermediate 5 mm spacers are superseded |
| H180/H181 | 2 | Existing M3 × 8 socket-head cassette-retention screws | Length retained; 2 mm nominal usable engagement plus 1.1 mm runout corridor in the revised flat-bottom blind hole |
| P01 | 1 | Revised printed frame: real-sensor floor pocket, relocated cassette guides/slots and +Y lead exit | Replace together with matching H12/P05 |
| P03 | 1 | Local Ø7 shaft-clearance opening through the soft sleeve near the adjuster rear end | Revised sleeve; do not alter the palm core or principal wrist contact |
| P04 | 1 | Two small rear roof caps within existing deck width, cut by the unchanged R12 seat relief | Revised printed grip; 72 mm pocket and seat datum retained |
| P05 | 1 | Larger genuine-sensor/keeper recess, lead exit and four screw-head pockets, with central reaction web retained | Revised printed yoke |

The keeper's ring and pads have a **29 × 29 mm nominal overall profile**; a 30 × 30 mm sheet blank is stock allowance. Fabricate the final cut profile.

The rods, paired springs, isometric sleeves, pusher, adjuster and remaining unchanged hardware may be retained only where the final source-specific BOM and geometry comparison confirm their identities. This mechanical revision requires no PCB, JLC production-package or electronics-order change. No order is placed by these notes.

## H12 bearing and collar details

At zero preload, the main backing plate occupies X−12…−9.85 / Y−15…+15 / Z3…33 mm. The planar **sensor-bearing face is X−9.85**. The genuine sensor's rear plane bears here. The final design removes the old central relief derived from the smaller placeholder; do not copy that relief from the previous H12 drawing.

The shallow locating collar occupies X−9.85…−8.65, ID25.5 / OD27 mm. Its nominal radial housing clearance is 0.25 mm. Its +Y lead-notch tool spans X−10…−8.5 / Y10…29 / Z10.5…25.5 mm; this wider opening admits the genuine sensor's flared lead base. The notch and four spacer scallops are part of the final profile, not optional omissions. The collar locates the housing; it must not pinch the wire stub or force the sensor out of its intended bearing plane.

Four M2 axes run parallel to X, at the combinations Y±10.5 / Z7.5 and Z28.5. The nominal model contains Ø1.7 thread/drill envelopes, with 2.15 mm plate engagement and 4.5 mm minimum centre-to-plate-edge distance. Specify finished **M2 threads** and tolerances on the machining drawing. M2 screw tips project 0.9 mm behind the plate; preserve that keepout.

Keep the bearing surface flat and free of burrs. Surface finish, flatness, dimensional tolerances, material certification and any coating are **not assigned by this note**. They require explicit final drawing values and agreement with the chosen fabrication method. The matching FX1901 loading/support instructions and actual sensor should be checked before machining the load-bearing support.

## Loose sensor capture — H23/H24/H25

H23 occupies X−1.4…−0.9. Its rear face is therefore nominally **0.5 mm ahead of the sensor rim at X−1.9**. The Ø20 central opening clears the force button/pusher. H240–H243 span X−9.85…−1.4 and set that keeper position. Four M2 screws fasten keeper and spacers to H12.

The screw heads extend to X+0.7 in the nominal model. The yoke's matching head pockets extend to X+1.4, giving 0.7 mm axial model clearance. The spacer-to-housing radial margin is approximately 0.349 mm. These are nominal CAD gaps before manufacturing variation and sensor/mechanism deflection.

The keeper prevents the housing falling out when the springs are removed. It is **not an operating reaction surface**. The rim gap must remain positive over the real part/tolerance/deflection stack; tightening these screws must clamp the spacers, not the sensor. Do not bend H23 into contact with the housing, omit the spacers or use shorter spacers to remove the gap. Deburr the cut profile and hole edges before bringing it near the sensor leads.

## H18/H19 cassette retention and blind-hole machining

The revised capture axes are X−12.8 / Z8.5. Each 6 mm H19 spacer spans |Y|15…21; the screw head spans |Y|21…24. The M3 × 8 screw tip ends at |Y|13, providing **2.0 mm nominal steel engagement** into the ear from |Y|15, approximately four M3 × 0.5 turns. This is light, non-primary cassette retention; it is not credited as a high-force stop.

The **Ø2.5 flat-bottom blind pilot must be tapped M3 × 0.5**. Its nominal bottom is |Y|11.9, leaving a **1.1 mm runout corridor beyond the screw tip**. Use a bottoming tap and inspect at least the full usable finished thread from |Y|13…15. The nearest M2 screw corridor is nominally 1.5 mm from the M3 screw tip. The nominal CAD omits helical thread form; verify actual fastener length, usable full threads and the stated bore limit during fabrication. Do not deepen the bore informally into the adjacent M2 corridor. The revised stack supplies runout space rather than relying on a nearly bottomed screw.

The ear's rear X limit is −15.5, leaving 0.5 mm nominal clearance to the fixed wall. Remaining steel ligaments around the Ø2.5 pilot are approximately 1.45 mm behind it and 1.25 mm above it. Screw heads retain 2 mm nominal clearance to the palm feet. These features retain the unloaded cassette; they are not credited as the main operating load path. The H19 steel tubes must span the printed guide, so tightening the screws cannot clamp the printed sliding surfaces. Substituting the old 4 mm or intermediate 5 mm tubes defeats the revised stack.

## Printed parts and assembly notes

P01's new floor pocket has a Z2.7 floor, leaving 4.7 mm above the base bottom. Low guide caps span X−8.1…−6.5 / Z3.8…11.7 and reinforce the closed slot's front wall to **2.3 mm nominal thickness**. P05 retains 0.5 mm nominal clearance to those caps. Both P01's positive-side guide lead notch and P05's lead relief span Z12…24; the web between the guide slot and lead notch is 1.3 mm. These are geometry dimensions, not a qualified overtravel-stop capacity. P05 retains its central reaction web at X1…9 while admitting the larger sensor/keeper and screw-head envelopes.

The P03 relief and P04 caps are defined in the exact patch and rationale and included in the final native exports. Source-bound whole-assembly static and continuous motion checks pass, including the adjuster/sleeve relief. The local roof probe measures approximately 4.075 mm at its recorded location. It does not establish a global wall minimum or material strength. The exact P02/P03 STEP comparison confirms zero positive BRep intersection, independently of the passing source separation certificate and native mesh checks.

For assembly, keep the final revision identity with the parts. Fit the backing, actual sensor and loose capture as one matched stack. Tighten keeper screws against the steel spacers while preserving the 0.5 mm housing gap. Route the supplied lead through the relief without clamping it. Confirm free 0–2 mm cassette adjustment before installing springs. Install either a matched spring pair or both isometric sleeves; confirm the appropriate stroke and switch adjustment. The final native isometric check uses 2 mm preload and a 13 mm seated setting, consistent with `15 − preload`.

## Verified service sequence

The [validation manifest](validation/manifest.json) and [report](validation/validation.json) record 974 finite pair sweeps, including the following nominal paths and their required removals:

1. Remove external operating load and safely restrain or remove spring energy. For palm/case removal, release H21, set 2 mm preload and remove both palm M4 fasteners. The complete palm/electronics module lifts +Z 40 mm. Its electronics move with the module.
2. For sensor-stack removal, remove the palm/case module, both springs or isometric sleeves, rear caps and bumpers, both guide rods and H180/H181 screws with H190/H191 spacers. Set preload to zero. Keep H01, H02, H12, H20, H23, all four H24/H25 pairs, P05 and its fixed seats together.
3. Move that complete stack **forward +X 2.1 mm with no initial lift** to release the radial lead through the guide window. Then lift **+Z 40 mm** from that translated position.
4. On the bench, move the yoke/pusher assembly axially +X to separate it from the sensor and loose keeper. The recorded local separation path is 30 mm. Reassemble with the matched spacers and restore the palm/case module before operation.

For separate H15 keeper removal, first remove the palm/case module, H160/H161 keeper screws and H13 adjuster. Shift H15 wristward −X 1.4 mm, then lift +Z 35 mm. The verified path depends on those removals; it does not establish access with the loaded mechanism assembled.

The official STEP contains only a short wire stub. It does not supply the complete flexible cable, connector, service loop or bend-radius specification. Final cable routing and strain relief must account for the actual supplied lead. Do not fabricate a fictitious rigid connector into the force path merely to make the model look complete.

## Recorded digital QA

The final neutral, maximum and isometric native exports each contain 109 valid closed solids: 56 device parts and 53 electronics references. The report has no failed geometry checks. Static pair checks, continuous 0–30 mm travel × 0–2 mm preload coverage, spring envelopes, articulated actuator motion, isometric geometry and the 974 service-pair sweeps pass with explicitly identified nominal thread/joint/contact models.

Both exact STEP roundtrip comparisons pass. The native H01 is a valid solid matching the original contact-aligned manufacturer BRep, with zero kernel symmetric-difference volume under identity placement. P02 and P03 have zero positive BRep intersection volume at their nominal fitted interface. The final report is `NOMINAL_GEOMETRY_CHECKS_PASS`, with zero failed or unresolved checks. An appropriate description is:

> The corrected 132 mm prototype CAD uses the genuine sensor geometry and preserves the 72 mm opening, 30 mm travel and 0–2 mm preload. The recorded nominal CAD configurations and movement/assembly paths have been checked. Its load capacity and physical hand fit remain unqualified.

Use only the configurations and paths covered by the report. STEP, STLs, BOM, metal drawings and assembly instructions must identify this same final revision. The native archives include metal/purchased parts and reference envelopes; their presence in an STL ZIP does not make them printable parts.

## Material and strength statements that the evidence supports

It is accurate to say **“H12 is specified as S355 steel,” “H23 is specified as 0.5 mm stainless sheet,”** and **“H24/H19 are steel spacers.”** These are material/design specifications. They do not establish stiffness, yield margin, fatigue life or permissible load. The stainless grade remains to be specified on the final drawing; do not silently substitute a grade or infer properties from the word “stainless.”

The earlier PETG print settings describe a different revision. They can provide a starting point for a spring-free fit prototype, but cannot qualify the new two-M4 palm joint, thin retention details, enlarged yoke recess or backing-plate stiffness. The soft P03 model also must not be treated as a load-bearing rigid PETG surrogate merely because an earlier visualization set used rigid sample parts.

No supported statement is available that this design is “strong enough,” “safe to 200 lbf,” “equivalent in strength,” or “ready for loaded use.” The 200 lbf sensor capacity is not a device load rating. The nominal spring-pair calculation up to 267.048 N is not a tested permissible hand force. Without a defined target force, actual material/process, justified load cases and structural evidence, no factor of safety should be invented.

The physical acceptance work is specific: confirm the true support/contact interface, inspect the manufactured stacks and gaps, establish the print process and load target, test central and eccentric loading, assess stiffness/creep/fatigue, complete cable routing and strain relief, and calibrate the complete mechanism including guide friction and hard-stop measurement bypass. The user confirmed the hand scan is an approximate reference and the 72 mm opening should remain. Its uncertain registration and missing contact surfaces require palm seating and finger posture checks with a spring-free fit prototype. These items remain separate from completion of a nominal prototype CAD revision.
