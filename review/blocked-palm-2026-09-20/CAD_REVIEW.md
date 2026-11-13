# Fingerworker — 30 mm printable prototype

Revision: 5 September 2026. [Editable Onshape model](https://cad.onshape.com/documents/15316cc6370631845af136b2/w/664d0779b5d992870442f997/e/d253eb87b70818ebde8215f0). FeatureScript: `fingerworker_mvp.fs`.

The springs now sit beside the finger pocket. Integral printed dovetails replace the MGN12 rails and bearing blocks; the switch lies flat on the base. Custom structural parts are separate printable solids. The previous 59.5 mm open-palm design is archived in `review/tall-open-palm-2026-09-05/`.

| Property | Current design |
|---|---:|
| Overall device envelope, excluding reference hand | 216 × 210 × 30 mm |
| Height reduction from 59.5 mm | 49.6% |
| Base | 216 × 210 × 6 mm |
| Finger recess | 94 × 34 × 20 mm, R8 plan corners, R4 contact edges |
| Pocket floor / underside | Z10 / Z7 mm; 3 mm floor |
| Palm crown / frame crown | Z30 / Z30 mm |
| Palm reaction / loaded pocket wall | X37 / X137 mm at rest |
| Datum spacing / pull travel | 100 to 70 mm / 30 mm |
| Printed dovetail spacing / engagement | 188 / 68 mm |
| Dovetail roof / normal flank clearance | 0.30 / 0.318 mm nominal |
| Rod / spring axes | Y±75 mm, Z18 mm |
| Springs | 2 × OD16 / ID8 / free length 102 mm |
| Spring seat spacing | 101 mm at rest; 71 mm at full pull |

The widened base fits within a nominal 220 × 220 mm printable area without a brim; a larger usable bed is preferable for adhesion aids. The round palm support retains a replaceable 2.5 mm TPU C-sleeve. Its reinforced yoke clears the rigid palm plate and sleeve envelope by 1 mm. The M4 travel stops and M3 screw used as the switch cam are separately adjustable. The switch is nominally set to operate 1 mm before full travel.

## Printing and assembly

There are 11 printed device solids: base, rigid palm bolster, soft sleeve, climbing carriage, floating yoke, two rear retainers and four return bumpers. Removing the rear retainers releases the rods and lets the carriage slide onto the printed tracks. Springs, rods, spring seats, sensor, switch, pusher and fasteners remain metal/electronic hardware. Electronics are external.

Use **Preview displacement = 0 mm** and **Show hand reference = off** for normal viewing and export. Printed bodies are named `P… PRINT`; hardware is named `H…`. The hand is a single optional reference solid, excluded from the BOM.

See `PRINTING.md` for orientations, fit coupons and finishing, and `EINKAUFSTEILE.md` for hardware. Guide-coupon STL files and their generator are in `print/` and `review/make_guide_coupon.py`.

## Verification scope

The exact-solid Onshape audit examines 20 selected pairs at each saved 0, 15 and 30 mm pose, including the illustrative hand. Raw results: `review/onshape-low-profile-audit-*mm.txt`. Boundary contacts at spring seats, mounts, return pads and the stop/click endpoints remain explicit contact records. Run `python3 review/check_low_profile.py` to check the independent dimensional ledger and all saved logs.

All three saved poses report **zero solid interference** in the 20 tested pairs, with all hand queries present and clear. The eleven exported device meshes also passed closed-edge and positive-volume checks; dimensions and file hashes are in `review/low-profile-print-validation.json`. The oriented STL package is `print/Fingerworker_30mm_print_pack.zip`.

The ledger also checks 61 motion positions for spring compression, guide overlap and contact datums. The hand retains the previous fixed-length finger construction, translated down 29.5 mm. It illustrates the pose; it is not population hand-fit data. The switch hinge and spring turns are nominal visual envelopes.

The two springs yield a nominal 15.6 to 483.6 N from the catalogue rate calculation. **This is not a load rating for the printed assembly.** Strength, creep, wear, sliding friction and comfort require a manufactured prototype and testing. These checks establish nominal geometry and assembly fit, not fatigue performance.
