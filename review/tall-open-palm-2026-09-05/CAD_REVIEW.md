# Fingerworker — open mechanism and palm reaction

CAD revision: 4 September 2026. Saved in [Onshape](https://cad.onshape.com/documents/15316cc6370631845af136b2/w/664d0779b5d992870442f997/e/d253eb87b70818ebde8215f0). Editable source: `fingerworker_mvp.fs`. The previous covered climbing version is preserved in `review/covered-climbing-2026-09-04/`.

## Requested changes

The fixed palm support is now a transverse rounded bolster designed to oppose the finger pull. A 2.5 mm soft C-shaped sleeve covers its front and crown. The finished crown is at **Z59.5 mm**, level with the climbing-edge frame. Its forward reaction face remains **X37 mm**, preserving the **100 mm open / 70 mm pulled** datum spacing and **30 mm travel**.

The lower tray, fixed hood, inspection window, moving hood and associated mounting features have been removed. The structural base, linear guides, springs, sensor, switch and mechanical stops remain exposed. The base's outer edges now have R3 rounding.

| Dimension | Nominal value |
|---|---:|
| Palm bolster centre X / Z | 26.75 / 49.25 mm |
| Finished outer radius / rigid core radius | 10.25 / 7.75 mm |
| Soft sleeve width / thickness | 86 / 2.5 mm |
| Palm crown / climbing frame top | 59.5 / 59.5 mm |
| Mounting plate bottom / top | 39 / 44 mm |
| Sleeve underside / plate clearance | 44.1 / 0.1 mm |
| Climbing pocket | 94 × 34 × 20 mm, R4 lip |
| Device height without hand | 59.5 mm |

The cylindrical core overlaps the mounting plate by 2.5 mm, with an approximately 11.4 mm joining chord. Four M4 counterbore seats remain at Z43 mm, preserving 4 mm of material below the heads and roughly 6 mm nominal engagement with M4×10 screws. Access wells extend through the curved core, outside the sleeve ends.

## Hand reference

The optional illustrative hand now braces its heel against the forward curved palm surface, instead of resting on the old low pad. Its nominal heel/sleeve gap is 0.1 mm. The heel stays 1.25 mm above the spring anchor. A raised wrist clears the bolster crown; four fingers retain fixed link lengths while pulling the same pocket through 0–30 mm.

`review/check_palm_brace_hand.py` checks 311,040 sampled surface points at each 0/15/30 mm pose against conservative open-mechanism envelopes and checks 61 inverse-kinematic positions. `review/check_geometry.py` checks the rounded palm dimensions, fastening stack and mechanical clearances. Both pass. These are nominal geometry checks, not population hand-fit data or proof of load capacity.

## Verification and use

The regenerated CAD audit reports zero solid interference in 12 targeted solid pairs at 0, 15 and 30 mm; records are saved as `review/onshape-palm-open-audit-*mm.txt`. The palm plate/base interface has 22 unclassified boundary-contact records, and the fitted sleeve/core interface has five. At full pull the switch roller also meets the carriage. These intended mounting and actuation contacts remain explicit in the raw logs; they are distinct from solid interference.

For the normal product view and manufacturing exports, use **Preview displacement = 0 mm** and **Show hand reference = off**. The open model has 35 device parts; the optional hand adds one reference body excluded from the BOM.

Grip friction, sleeve retention, comfort and structural performance need to be checked on the manufactured prototype. The switch's operating datum follows the supplier drawing; its hinge motion remains an illustrative contact preview.

Updated purchasing and fabrication notes are in `EINKAUFSTEILE.md`. Final views: `assets/onshape-palm-open-product.png` and `assets/onshape-palm-brace-hand-30mm.png`.
