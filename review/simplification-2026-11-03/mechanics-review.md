# R12 mechanics review — fixed rear gate proposal

> **Superseded central-preload scope:** after this rear-only review, the user also requested removal of central H13 preload. The final fixed-front design is documented in [front/README.md](front/README.md); it removes9 additional hardware bodies and fixes p=0. References below to retaining central preload describe the earlier review stage.

Read-only baseline: R11 `fingerworker_mvp.fs`, source SHA `c8ec18f08149553001ccf8173f35fe57eee6a16be0294be2d7f88577f658cf5e`, native STEP SHA `4c7b412eb5700e6ff8dc985c7ab8182e5acc7003a645ecac3291e88fe455d6e7`.

## Identification of the circled screw

The illustrated low axial screw at the outer guide-rod holder is **H260/H261**, M4×10 ISO4026, 2-mm hex, axis `Y=±51,Z=7`, extending `X120.4…130.4`. It pushes P120/P121 forward, changing the **return/rest position** by `a=0…2 mm`. Thus it also adds spring precompression and consumes the same amount of useful travel. It is not the central H13 M6 sensor preload thumbwheel (`Y=0,Z=18,X−24…−12`). These are separate mechanisms.

At R11 rest, the P04 rear face is `X=119−a`, matching the P12 lands. Deleting the outer adjusters is functionally coherent when fixing `a=0`: return datum remains X119, P04 moves toward −X during use, travel remains `30−p` mm, and the central sensor force path and cam calibration remain available. The optional isometric sleeves still seat after `15−p` mm.

Source locations in R11: rear parameters lines861–902; construction lines1494–1616; return-pad datum119 at lines1605–1611. Central preload is a different block around1266–1431.

## Proposed consolidation: four printed pieces become one

A single **P06 rear gate** replaces P060, P061, P120, P121. Each end is a plain block `X119…129,Y±51±14,Z4.5…28`, joined by a bridge `X125…129,Y−51…51,Z4.5…10`. The bridge starts 1 mm beyond the central rail end X124. The X119 front face is the fixed return datum.

Retain the two Ø6.2 blind guide sockets ending X126.2 and all four H30 M3×8 holes, counterbores and exact screw geometry. Add a 45° tangent teardrop roof over each rod hole to reduce support needs while keeping its round Ø6.2 functional clearance. Delete the adjuster tool wells, nut/washer recesses, moving shoe fork/tongue, M2 capture roof and capture slot. The P01 obsolete rear adjuster pockets are filled to its original 6-mm base and raised foot shape; existing insert pilots stay.

The whole gate still installs **axially toward −X over the rod ends**, after P05/P04 and rods have been placed. It must remain removable: fusing these caps into P01 would block the established rear-loading assembly. A +X12-mm withdrawal clears both rods. Do not turn the blind sockets into lateral or top clips that let rods escape under return load.

The two long integral side latch arms are outside the slider (`|Y|66.4…67.6` vs P04 `|Y|≤63`), flat with the gate bottom (`Z4.5…7.5`) and rooted through an R0.6 concave blend starting X126 (rigid stock starts X126.6). Their hooks engage small P01 posts at `X108.2…110.5,|Y|64.2…66.2,Z3…7.8`. Release both outward by0.9mm then withdraw +X; remove H30 first if fitted. Nominal axial hook clearance is0.2mm. Four existing M3 screws remain available for functional securing. The latch design is for convenient assembly; no new load/creep/cycle qualification is implied.

This reduces the device print count **10→7** and the complete fit-test set **13→10** without inventing printed screw/nut substitutes. It removes **12 real hardware pieces**: two each H26, H27, H28, H29, H31, H32. H30×4 remain. No spring, rod, steel seat or sensor hardware is removed.

## Other parts and constraints

- **P01:** already one piece with palm. Keep the central guide, sensor portal, palm braces and electronics-service opening. Their shape has a purpose. The rear adjustment pockets become unnecessary; fill them while preserving 6-mm nominal floor, rail and screw pilots. New small latch posts are clear of the moving grip and do not bridge the force sensor.
- **P04:** keep separate and sliding. Its rounded finger contact and central guide determine comfort and movement; flattening the finger profile would lose useful contact geometry. Keep the existing improved print orientation unless a new toolpath demonstrates a better exposed surface. Rear gate changes do not alter its pose.
- **P05:** must float axially on the guides and transmit reaction to the pusher/sensor. Do not fuse or click it rigidly into P01; this would create a parallel load path around the sensor.
- **P08/P09:** retain serviceable enclosure clips and their broad electronics/wire supports. Merge into the frame would make battery/PCB/USB service and lid release harder. Separate enclosure agent reviews shape simplification.
- **P11:** retain a separate adjustable cam while sensor preload `p` and switch trim remain. Its required position is `camTrim−p`; a fixed fused cam would lose calibration. A larger simple keyed sliding cam could be reviewed separately but not silently replaced with an unadjustable nose.
- **Printed rods/Q01:** are only assembly proxies, not load-qualified functional pieces. Their count should not be mixed with the seven actual printed device bodies. Optional S01 spring spacers are a separate selected spring-conversion set.

## Function after removing the rear adjusters

Fixed rest offset5mm; user stroke `u∈[0,30−p]`, central preload `p∈[0,2]`. P04 rear X119−u is always ≤ the gate return face119. At rest this is an intentional exterior contact; the old collision audit named “Carriage / rear caps” must be changed to allow the fixed return contact. At increasing u every main cap/bridge surface moves farther from P04. The latch arms remain laterally outside its whole travel envelope.

The gate is a return retainer, not a sensor-end-stop replacement. The working force path still passes P04→P05→H02→H01. The front P05 sensing stops and cam/switch must not be removed under the premise that they are part of the rear adjusters.

## Deliverables and required final checks

`rear_gate.py` exposes `load()`, `expected(old)` and `patch_source(source)`. Its implementation and local STEP/STL candidates are in `mechanics/`. `preflight.json` records the literal CSG validity, seated overlaps, +X12-mm released assembly path, latch retention and calculated strain. These are **local proposal geometry**, not native Onshape manufacturing exports.

Final integration must regenerate native CAD, compare native exports to literal CSG, validate slider/spring/sensor and gate service motion, and slice the native gate. Native bottom down is intended so latch bending occurs within printed layers. Confirm first-layer contact and no trapped supports in the rod sockets. Actual PLA fit, release force, repeated cycling, unloaded grip return and loaded securing remain physical checks.

## In-memory frame scope result

Fresh in-memory R11 P01 minus the proposed P01 has a **valid Boolean result with zero removed volume**. Added material is confined to X108.2…129.0000001, Y±66.2, Z0.8…7.8. Both solids are valid and forward oriented. The front/palm/sensor geometry is therefore preserved in this local construction. See `mechanics/in-memory-frame-scope.json`. Re-reading the locally serialized P01 STEP produces invalid OCC difference results on old coincident B-spline faces; those numbers are rejected and are not evidence of geometry change. Final native verification must compare the actual Onshape export to fresh in-memory expected geometry, with validity checks on the Boolean result.
