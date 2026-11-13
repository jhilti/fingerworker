# R12 fixed front sensor support

This supersedes the earlier rear-only proposal: the user subsequently requested removal of **both** rear adjustment and central sensor preload adjustment. Both CAD parameters are fixed at zero and removed from the feature UI.

## Geometry and parts

The printed P01 reaction portal is solid again: no M6 nut pocket, central screw bore, H15 recess, M3 keeper bores, preload locking bore or upper driver access. The obsolete H15 service notch in the palm is restored to its original solid stock. The old projecting top bridge above the adjustable support is removed; the side buttresses stay.

A single integral support prism reaches the unchanged H12 rear face at **X−12 mm**. It rises from the base at Z3.8 with a0.2mm overlap, and overlaps the portal by0.2mm. Its YZ profile is:

`(−9,3.8),(9,3.8),(9,9.5),(11,11.5),(11,26),(−11,26),(−11,11.5),(−9,9.5)`

The inherited sensor-floor pocket trims the front0.3mm of the lowest0.4mm of this profile; its actual front contact starts atZ4.2. This gives a **454.4 mm² planar reaction face**, a lower narrow pillar and45° shoulders. It clears the rear-projecting H12 side ears and all four H25 screw tips. It creates no new unsupported horizontal shelf above the base.

Removed hardware: **H11,H13,H15,H160,H161,H170,H171,H21,H22** — nine bodies. H12, actual H01 sensor, H02 pusher, H20 pusher nut, H23 keeper and H24/H25 keeper hardware retain their exact geometry.

H18/H19 remain as cassette retainers. Their former printed travel slots become **Ø4.4 mm circular bores**, centred X−12.8,Z8.5, preserving0.2mm radial clearance around the OD4 steel spacers. The6mm spacers retain the established0.5mm guide-side clearance, so tightening the screws does not clamp the printed guide. These are retention screws, not adjustment controls.

Together with the one-piece rear gate: **7 printed device bodies**, **10 fit-test pieces** with revised Q01 and two rod proxies, **93 native bodies** including53 electronics references. The old Q01 is incompatible with the filled nut pocket and is replaced separately.

## Function and service

Force remains P04→springs/P05→H02→H01→H12→fixed P01 support. P05 is still floating and has no fixed frame connection. New support stock is separated from H01, H02, P05 and the front keeper; it cannot create a parallel load path around the sensor.

The user stroke is fixed at0…30mm and the selected81mm isometric sleeve approach is15mm. The existing spring seats retain their baseline rest compression (DF2194:6mm; DF2185:9mm); no adjustable preload remains. P11 still provides ±0.8mm physical switch calibration and is not a spring preload part.

After unloading/removing springs, guide rods and rear gate, undo H18 and withdraw H18/H19 outward through the existing side access. Move the assembled sensor/keeper/pusher/yoke stack **+X3.2mm**, then **+Z40mm**. H12 remains removable. There is no H13/H15/H11 disassembly sequence anymore.

## Verification scope

`front_fixed.py` exposes `expected(old)` and `patch_source(source)`. Compose its P01 result after the rear-gate frame result. Local candidate STEP/STL are study geometry; final manufacturing files must come from native CAD.

`preflight.json` checks a valid single P01 solid, overlap of the actual added stocks after circular bore cutting against retained parts, nominal sensor reaction contact, no sensor bypass,58 sensor-stack service poses, and56 outward poses for each H18/H19 part. OCC drops purely tangent faces from a solid-common operation; reaction area is therefore checked using two translated-copy thin overlap probes (0.001 and0.01mm), divided by their depth. The nominal geometry has zero penetration and zero reaction gap.

The final native export is independently checked in `../validation/native-motion.json`: all 77 checks pass. This binds source `730cd21ea3aafbe43bf8eb38007b20d9cd0272659430d8a2b3b6245f33f62455` and STEP `b2c076642b22f99a251b8e2a6ac20da9f251696e892448a2651ee8b636f32021`. The checks include the complete initial H12 release from 0 to 0.001 mm, actual 454.4 mm² H12 reaction contact, no sensor bypass, both catch restraints, the complete staged rear-gate release (outward flex, then 12 mm axial withdrawal), and 60 continuous moving/fixed pair checks over the complete 30 mm stroke including ±0.8 mm physical cam trim. The subsequent sensor-stack service route is checked separately by the final native service audit. Compressing springs and the moving switch actuator retain the earlier verified geometry; they are not falsely treated as rigid stationary bodies in these translational checks.

These checks do not establish PLA load rating, creep resistance, sensor calibration or physical fit. The existing hardware-dependent load and first-power checks remain necessary.
