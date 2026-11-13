# R5 closer-grip mechanism proposal

The selected CAD candidate moves the carriage rest **5 mm toward the palm**, shortens the two distal P05 sensing-stop faces by the same 5 mm, and preserves the requested **30 mm travel at zero preload / 28 mm at 2 mm preload**. A new top-clamped P11 cam shoe replaces the horizontal M3 cam screw. This is a prototype candidate; native regeneration, motion verification and physical qualification remain separate requirements. Frozen R4 is unchanged.

The local source is [fingerworker_flat132_reach_fit.fs](../flat132-reach-fit-2026-10-23/fingerworker_flat132_reach_fit.fs), SHA256 `61885fd717b30eaf1dfc39a1f7f65f017bfc1b4ac077c3e3493399ef3373a9a3`. Its deterministic [builder and change record](../flat132-reach-fit-2026-10-23/source-build.json) verify the frozen R4 source hash and preserve the central P05 force web and palm source exactly. The expected inventory is 53 device solids, 106 including electronics, and 15 printed parts.

## Why the changes must be coordinated

Shortening P05 alone changes the closed stop and does not move the unpressed carriage: the springs still return it to the existing bumpers. Moving only the return bumpers inward by 5 mm would reduce free travel to 25/23 mm. The retained travel therefore requires both the closer rest and a stop 5 mm farther forward. The resulting extra spring compression also requires the switch cam to be retimed.

Let `u` be user travel measured from the new closer rest, `p` the existing 0–2 mm adjustment, and `q` absolute carriage displacement from the R4 rest:

| Quantity | R5 relation |
|---|---|
| Absolute carriage displacement | `q=5+u` |
| Dynamic travel domain | `0≤p≤2`, `0≤u≤30−p` |
| P04 stop-contact face | `X=65−q` |
| P05 stop-contact face | `X=30+p` |
| End contact | `q+p=35`, hence `u+p=30` |
| Spring installed length | `L=101−p−q=96−p−u` |
| Loaded finger-wall datum | `X=77−q=72−u` |
| Fixed wrist-facing palm tangent | `X=−37.25` |
| Reach between those landmarks | `109.25−u mm` |

Thus the nominal dynamic grip is 5 mm closer at every user travel setting. Reach is 109.25 mm at rest, 79.25 mm at u30/p0, and 81.25 mm at u28/p2. These are CAD landmarks; hand comfort and soft-tissue contact require a prototype.

## Concrete geometry

- **P05:** distal stop fronts X35→30. Both 14×22 mm contact faces and the 10×22 mm arm roots remain; the sensor/yoke central web is unchanged. The force path remains P04→P05→H02→actual H01→H12→H13/H11/H15→P01. No fixed stop bypasses the sensor.
- **P06 retainers and P07 bumpers:** four rigid bosses extend to X120.5 from the existing X125.5 retainers, with 0.1 mm union overlap. Their Y footprints remain at the four original bumper positions and Z14…20. The existing 1.5 mm TPU pads move from X124…125.5 to X119…120.5. Rear screws, rod lengths and mounting locations remain.
- **P01 guide:** front of the central rail extends X34→29 to retain the full 14 mm front bearing land at absolute q35. The profile, channel clearances and track rear end remain.
- **P04:** the entire old horizontal cam bore/recess is omitted. A main well X64…74.8/Y−1…8/Z8.6…19 and short front lever relief X64…67.2/Y−14…8/Z8.6…19 replace it. The guide roof remains Z7.3, leaving a nominal 1.3 mm local ligament. The rear well wall is 2.2 mm before the vertical pocket wall at X77.
- **P11:** lower shoe X69…73.5/Y−0.7…7.7/Z9…19; upper forward boss X67.5…69/Z13.2…19. The upper boss clears the illustrated roller top Z12.3 by 0.9 mm. Nominal well clearances are 0.3 mm per Y side, 0.4 mm below and 0.5 mm behind at the extreme forward setting.
- **H10:** vertical M3×10 with Ø5.5×3 mm head at Z25…28, shank tip Z15 and a nominal L4 M3 insert ending at Z15. The Ø4.2 pilot enters Z19 and ends Z14.5. Actual insert stock dimensions must be confirmed before manufacture. The minimum axial pilot wall is 0.9 mm; installation and clamp durability are unqualified.

P11 and H10 translate relative to P04 by `k=e−p`, where public `camTrim=e` is bounded −0.8…+0.8 mm and defaults to zero. The roof slot has centre range X67.7…71.3 and radius1.7; its recessed head slot has radius3. The shoe contact face is `X=69+e−p−q=64+e−p−u`, preserving the previous nominal timing at e0. Changing preload still requires a **manual shoe reset and clamp check**. The parameter represents the physical setting; it does not add automatic coupling. The shoe carries switch actuation, outside the main force path. Real opening point, overtravel, wiring and clamp stability require calibration on actual hardware.

## Spring and ISO consequences

The independent [spring study](spring-tradeoff.md) freshly checks both official Febrotec products. With the selected full-travel offset, minimum nominal installed length is 66 mm. This exceeds catalogue L1 by 7.41 mm for 0X-DF2194 and 9.86 mm for 0X-DF2185. The catalogue margins do not qualify fatigue, buckling, spring tolerances or printed strength.

| Spring pair | Starting force p0…p2 | Nominal end force |
|---|---:|---:|
| Light DF2194 | 39.68…52.91 N | 238.10 N |
| Strong DF2185 | 66.76…81.60 N | 289.30 N |

The current candidate retains the existing **86 mm ISO sleeves**. They stop at the same absolute q15−p as R4, so their absolute grip position is unchanged; approach from the new rest is only u10−p, or 10/8 mm. An 81 mm sleeve would instead move ISO grip 5 mm closer and preserve 15/13 mm approach. That alternative is not selected in this source and must be coordinated if requested.

## Alternatives and practical limit

A 7–10 mm offset is not a small continuation of this arrangement. At 7 mm the P04 front reaches X28 at maximum zero-preload travel and overlaps the unchanged pedestal ending X29 and switch body ending X28.2. The old horizontal H10 cannot simply move forward 5 mm: its tip X75 would enter the pocket wall at X77, while moving the switch backward would consume its 3.1 mm bare-terminal clearance at maximum preload. The stepped shoe solves the timing issue with a local low-load part and leaves the fixed switch in its R4 location.

The independent [local clearance study](reach-clearance.md) supports this 5 mm candidate with nominal mesh witnesses and sampled trim/preload/travel checks. Those studies precede native R5 regeneration and do not certify the full continuous three-parameter domain. The switch lever remains an approximate manufacturer-drawing reference. The 500 N target remains physically unqualified, including the modified P04 guide roof, printed stops, return bosses, bumpers, keeper joints, creep, fatigue and one-sided loading. Firmware NC-LOW remains fail-safe and still blocks qualified endpoint force/peak reporting; this CAD study makes no firmware changes.
