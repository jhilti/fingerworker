# R4 reach and stop-arm study

A **5 mm closer rest position with the full 28–30 mm free stroke is a plausible CAD candidate only with a redesigned cam, return stops and P05 stop ends**. The proposed axial M3 cam cannot simply follow the carriage farther forward. A top-clamped, calibrated stepped shoe can avoid its screw projecting into the finger pocket. A short, wider front relief admits the existing illustrative switch lever.

This is a read-only, local CSG feasibility check against the frozen R4 native meshes and source. It is not native R5 regeneration, a full continuous collision certificate, a verified load rating or a physical switch/spring qualification. R4 remains unchanged. The companion [JSON](reach-clearance.json) records source hashes, numerical witnesses and limitations.

## What shortening the arms changes

Let `s` be user stroke, `p` the existing 0–2 mm sensor-yoke preload, `δ` a constant closer carriage rest shift and `a` the setback of the P05 stop ends. Physical carriage shift is `s+δ`; effective spring compression is `q=s+p+δ`.

| Relation | Expression |
|---|---|
| Finger wall | `X=77−s−δ` |
| Palm contact datum | `X=−37.25` |
| Reach between those landmarks | `114.25−s−δ mm` |
| P04 contact face | `X=65−s−δ` |
| P05 stop end | `X=35−a+p` |
| Contact condition | `s+p+δ=30+a` |
| Available free stroke | `30+a−p−δ mm` |

Cutting P05 ends alone does not move the unpressed carriage. Springs still push it against its original return bumpers. A closer rest therefore needs a new return-stop position. Moving that rest without shortening the sensing stops sacrifices exactly the same amount of free stroke. The user has retained 28–30 mm travel, so a full-travel candidate requires `a=δ` and reaches the new maximum compression `q=30+δ`.

## Limits measured on R4 geometry

Native closed STL meshes were checked with manifold Booleans. Contact thresholds are nominal; the bisection interval was under 0.0001 mm and the positive-volume threshold was 0.000001 mm³.

| Pair or feature | First nominal contact |
|---|---:|
| Original P05 sensing stops / P04 | `q=30 mm` |
| Existing illustrative roller / switch housing | about `q=31.00 mm` |
| Unchanged axial H10 cam / switch housing | `q=35.80 mm` |
| P04 / fixed P01 pedestal | physical carriage shift `36.00 mm` |
| P04 / switch housing | physical carriage shift `36.80 mm` |
| P04 / retained P05 force web, distal arms removed only in memory | `q=49.50 mm` |

The force web is not the first practical limitation. Keeping full original travel with `δ=6` reaches the P01 contact boundary at zero preload, leaving no local pedestal clearance. A 7 mm shift exceeds that boundary with the current pedestal and carriage. The illustrative roller contact is a warning about the existing model's geometry; it does not define the real switch's allowable overtravel. Real actuation and total travel remain unqualified.

An independent finger-pocket shift would avoid extra carriage travel, but it thins the original 12 mm front wall to `12−δ` and moves the wall toward the existing M3 cam tip at X75. The nominal wall/tip gap is only `2−δ mm`; the current through-bore ends at X76.5. That also requires a cam and load-bearing carriage redesign for a 5–7 mm gain.

## Five-millimetre sliding-shoe candidate

The parent candidate puts the carriage 5 mm closer at rest, moves its rear return-stop contact accordingly and shortens the two P05 ends from X35 to X30. The 72 mm finger width and P05 force web remain. Both 14 × 22 mm bearing faces remain: 308 mm² each, 616 mm² total. A native mesh witness gives zero overlap at `q=35` and 6.16 mm³ after 0.01 mm penetration, consistent with that full contact area. No retained force-web material is removed by the distal trim.

The active refined candidate replaces the original cam with a manually adjusted stepped P11 shoe. Calibration `e` is ±0.8 mm and the shoe/screw translate by `e−preload` along X in carriage coordinates.

| Feature | Envelope or position |
|---|---|
| Lower P11 shoe | X69…73.5, Y−0.7…7.7, Z9…19 mm |
| Upper P11 boss | X67.5…69, Y−0.7…7.7, Z13.2…19 mm |
| Shoe/screw axis | X70.5+e−preload, Y3.5 mm |
| Insert pilot | Radius2.1, entryZ19, floorZ14.5 mm; L4 insert endsZ15 |
| Main well | X64…74.8, Y−1…8, Z8.6…19 mm |
| Short lever relief | X64…67.2, Y−14…8, Z8.6…19 mm |
| Through-slot | capsule centresX67.7…71.3, radius1.7, Z19…25 mm |
| Head counterbore | same centres, radius3, Z25…30 mm |
| M3x10 clamp envelope | shaftZ15…25; Ø5.5 headZ25…28 mm |

The lower shoe face becomes `69+e−(s+5)−p =64+e−s−p`. At zero calibration this preserves the previous nominal switch timing. It avoids an axial screw entering the finger pocket. Preload resets remain manual; calibration accounts for the real switch opening point and requires physical setting/locking.

The first proposal with only a Y−1…8 well intersected the illustrative lever by 5.183 mm³ at s30/p0. A wide relief is essential, but it only needs to extend to X67.2; the rest of the well can remain narrow. The refined upper boss starts at Z13.2, giving 0.9 mm nominal clearance over the roller's Z12.3 top.

The refined candidate passed **3,159 configurations** sampled at 0.25 mm stroke/preload increments and `e=−0.8,0,+0.8`. No tested intersection exceeded 0.000001 mm³ for P04 versus frame, case, lever and roller; shoe versus carriage, case, lever and roller; and screw versus carriage, lever and roller. The diagnostic roller followed `X=min(37.4,61.6+e−(s+p))` with the source fixed-pivot approximation. These calibration-correlated illustrative poses do not qualify the real actuator.

At the endpoints, local pedestal clearance is **1 mm at s30/p0** and **3 mm at s28/p2**. The existing guide determines the smaller global frame/carriage gap of about 0.300 mm. Both original 308 mm² P05 stop faces and the uncut force web are retained by the 5 mm distal trim.

At every relative stroke the reach decreases by 5 mm. Neutral spacing becomes 109.25 mm; end spacing is 79.25 mm at zero preload or 81.25 mm at 2 mm preload. Those are source landmark dimensions, not a hand-fit result.

## Issues to resolve before accepting this candidate

- The guide ceiling is Z7.3; the refined well floor Z8.6 leaves **1.3 mm** of local guide roof. The wider front relief changes P04 stiffness and guide retention. Clearance does not establish strength.
- The stepped P11 keeps **0.9 mm minimum axial pilot walls**, 2.1 mm transverse pilot walls and a 1.3 mm bottom ligament under the pilot in the upper boss. Insert installation, retention and locking remain unqualified.
- The M3 head has at least **6.346 mm²** of nominal bearing support at the counterbore floor. At the extreme axisX67.7 the counterbore opens 0.3 mm beyond the carriage front and the head extends about0.05 mm. Ideal floor loss is0.0343 mm² there; the larger minimum-area case remains fully supported. Head height endsZ28, below the rounded upper lip, but access/comfort still need review.
- The main well has 0.3 mm nominal Y-side clearance per side, 0.5 mm rear clearance and0.4 mm bottom clearance around the shoe. Its intended rear wall is2.2 mm. **Native R5 must omit the old horizontal cam bores:** subtracting the new well from R4 without restoring that material leaves a tunnel endingX76.5 and only0.5 mm local wall.
- The new rest adds **5 mm spring compression everywhere**. Installed length becomes `96−preload mm` at rest and **66 mm at the end stop**. The spring audit must establish allowable deflection, solid-height margin and force. A clear clamp/carriage alone does not establish feasibility.
- Quarter-millimetre stroke/preload sampling at three calibration values does not certify the continuous three-parameter domain. Native regeneration, exact STEP checks, continuous motion/service sweeps, tolerances and real switch/wire envelopes remain necessary. The switch lever is a drawing-based illustration, not manufacturer STEP geometry.

The useful next candidate is the refined **δ5 calibrated sliding-shoe** arrangement, subject to spring and P04 guide-roof checks. Shortening the original arms alone does not satisfy the retained travel requirement.
