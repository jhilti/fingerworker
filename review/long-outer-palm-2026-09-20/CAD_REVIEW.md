# Fingerworker — external palm roller, 30 mm high

Revision: 20 September 2026, exterior palm. [Editable Onshape model](https://cad.onshape.com/documents/15316cc6370631845af136b2/w/664d0779b5d992870442f997/e/d253eb87b70818ebde8215f0). Source: `fingerworker_mvp.fs`.

The whole soft palm roller now sits outside the wrist end of the frame. Two mounting ears attach its rigid support to the base, beside the sensor wall and clear of the floating yoke. The hand approaches from outside; the wrist-facing curved surface supplies the opposing reaction to finger pull. The roller is a fixed bolster with a removable TPU sleeve, not a rotating bearing assembly.

The finger pocket advances 60 mm to keep the external palm support reachable. Its carriage retains the original outboard spring arms and guide engagement. A rounded through-window behind the pocket removes excess material and keeps the relocated switch accessible. The switch and its adjustable cam move together by 54 mm; hard stops move outward to the guide axes. The previous inboard-palm revision is archived in `review/inboard-palm-2026-09-20/`.

| Property | Current design |
|---|---:|
| Overall assembled device, excluding reference hand | 238.25 × 210 × 30 mm |
| Base, printed separately | 216 × 210 × 6 mm, with integral features above it |
| Roller center / radius | X−34, Z19.75 / 10.25 mm |
| Wrist-facing contact / nearest frame edge | X−44.25 / X−22 mm |
| Whole sleeve clearance from frame in X | 1.75 mm |
| Palm crown / frame crown | Z30 / Z30 mm |
| Finger pocket | 94 × 34 × 20 mm, R8 plan corners, R4 contact edges |
| Loaded pocket wall, rest to full pull | X77 to X47 mm |
| Contact datum spacing, rest to full pull | 121.25 to 91.25 mm |
| Travel / minimum guide engagement | 30 / 68 mm |
| Dovetail roof / normal flank clearance | 0.30 / 0.318 mm nominal |
| Rod / spring axes | Y±75, Z18 mm |
| Hard-stop axes | Y±94, Z18 mm; tip X86 |
| Spring seat spacing | 101 mm at rest; 71 mm at full pull |
| Switch case | X118–128.2 mm, flat on base |
| Rear through-window | X117–166 mm at rest, Y±47 mm, R5 corners |

There are eleven printable device solids. The largest base still fits within a nominal 220 × 220 mm bed without a brim; the roller support is a separate print. Its four M4 fasteners are at X−15, Y−56/−45/+45/+56 mm. The support ears clear the moving yoke by 1 mm in X and the front rod blocks by 2 mm in Y. The front bench holes move to Y±98 mm. Use the new base, palm bracket and carriage together; previous printed versions are not an interchangeable set.

## Hand and motion checks

The reference heel is wholly outside the frame, nominally 0.1 mm from the roller. The palm spans above the sensor support and yoke. Four fixed-length finger linkages follow the pocket through the stroke. This is an illustrative hand, not a fit guarantee for all hand sizes or a comfort measurement.

The exact Onshape audit checks 21 selected solid pairs at 0, 15 and 30 mm, including hand versus pocket, sleeve and remaining mechanism. Results are saved in `review/onshape-outer-palm-audit-*mm.txt`. All three positions have zero reported solid interference in the tested pairs. Intentional boundary contacts at seats, fitted sleeve, mounts, return pads, switch cam and hard stops remain explicit unclassified-contact records rather than being relabeled as clear.

`review/check_low_profile.py` checks the independent dimensions, switch corridor and spring/guide datums at 61 travel positions. `review/check_palm_brace_hand.py` checks fixed-length finger feasibility and the saved hand collision reports. These do not establish continuous swept-solid clearance between the three exact CAD poses.

## Printing and remaining validation

The updated eleven-part STL package is `print/Fingerworker_30mm_print_pack.zip`; mesh dimensions and hashes are in `review/low-profile-print-validation.json`. Read `PRINTING.md` and `EINKAUFSTEILE.md` before assembly. Use preview displacement zero and the hand disabled for exports.

The nominal spring-force calculation remains 15.6–483.6 N. It is not a load rating for the printed device. The projecting palm bracket and longer carriage require physical strength, creep and deflection testing, alongside guide fit and hand comfort. Supports and print orientation affect the result.

Electronics are not integrated into this CAD revision. The researched Bluetooth acquisition proposal is in `BLUETOOTH.md`.
