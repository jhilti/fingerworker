# Broad integral printed sensing stops

The two full-pull stops are now part of the floating P05 sensor yoke. The former P01 fixed stop blocks, two M4 screws H070/H071 and their square nuts H080/H081 are removed. Each integral printed arm has a 10 ×22 mm axial root and a broad 14 ×22 mm flat stop face at X35 before preload. Both arms remain one connected P05 body.

At the pull limit, P04 transfers its stop reaction directly to P05. Spring force also returns to P05 through the fixed spring seats, so the two reactions combine before the retained pusher and genuine sensor. The fixed P01 full-pull stop bypass is removed. This describes the nominal axial load path; friction, acceleration, tolerances and deflection still affect a physical measurement.

The 14 ×22 mm nominal face area is 308 mm² per side. It avoids concentrating the end load into the former Ø4 mm screw tips. A 500 N total load shared equally gives a nominal mean face pressure of 0.812 MPa; 500 N on one face gives 1.623 MPa. These are geometric averages, not print strength allowables or a working-load rating. Actual face contact, print anisotropy, bending, single-sided loading, creep and fatigue require qualification.

| Geometry | Coordinates in mm |
| --- | --- |
| Arm root | X8.5…25, absolute Y19…29, Z7…29 |
| Broad terminal face | X24.7…35, absolute Y17…31, Z7…29 |
| Nominal face | X35, area14 ×22 =308 mm² per side |
| Fixed-base clearance | Arm undersideZ7 versus floorZ4:3 mm |
| Fixed switchcase clearance | Broad boss beginsX24.7, switchcase endsX24.2:0.5 mm |

The stop faces translate with synchronized preload. Therefore the frame travel limit is **30 mm minus preload**: 30 mm at zero extra preload, 28 mm at 2 mm extra preload. The source rejects an invalid greater travel value, with a 1 nm numerical guard tolerance so the exact 28 mm endpoint is accepted at 2 mm preload despite binary arithmetic roundoff. Geometry and the exact validation domain are unchanged. No automatic screw compensation is modeled. The isometric setting remains frame stroke15 mm minus preload, keeping the existing 86 mm compression sleeves.

After changing preload, the existing adjustable M3 click cam must be **manually backed out by the same axial amount as the added preload**, then checked and secured. The source displays this required configured setting: its face isX60−preload before carriage travel. The switch lever then follows combined travel plus preload, retaining the existing nominal 1 mm click margin before the hard stop. The CAD does not provide an automatic physical linkage, and switch/firmware behaviour still needs physical qualification.

The reinforced P01 portal service sequence is retained: H15 first moves wristward2 mm before lifting; the complete sensor/yoke stack first moves forward3.5 mm before lifting after the specified disassembly. The new broad arms leave this finite service path clear.

The frozen source SHA256 is `d5eca2f3d87bf4b9a47c1987ee91ba1d56e8c87003eca101677a148a2e605654`. Local mesh hypotheses find one connected P01 and one connected P05, no new positive interference at15 legal stroke/preload configurations and exterior stop contact at every tested preload endpoint. The four critical finite service motions pass546 continuous moving/fixed part-pair checks. These preliminary checks do not replace native regeneration, native export validation or physical loaded testing.
