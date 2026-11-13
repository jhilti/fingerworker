# Device upgrades — local CAD development revision

The three additions are implemented in `fingerworker_mvp.fs` and committed to the live Onshape Feature Studio. The full review on 21 September supersedes those sampled checks; see `FULL_REVIEW.md` and `review/onshape-full-review.json`. This remains a development revision, not a released print revision. Existing STL/ZIP exports have not been updated. Source and notes before this change are saved in `review/pre-adjustment-2026-09-20/`.

## Interchangeable lighter pair

`lightSprings = true` selects the new default pair. Procurement target per spring: **2 N/mm**, free length **102 mm**, outside diameter **16 mm maximum**, bore **8 mm minimum**, closed/ground ends and permissible working compression at least **33 mm**. Specify pair matching within 5% at the working lengths and require supplier fatigue/stress approval at 69 mm installed length. Replace both springs together through the existing removable rear retainers; keep the Ø6 rods and steel seats. The blue 30-turn, Ø2-wire coil is an illustrative envelope, not a released winding specification. No catalog part has yet been qualified for this target.

The existing 7.8 N/mm pair remains selectable with `lightSprings = false`. Its catalog identifies 31 mm as S2 and 41 mm as maximum deflection; added preload exceeds S2 at full travel and needs duty-cycle qualification. [norelem manufacturer model data](https://norelem.partcommunity.com/3d-cad-models/26000-compression-springs-ISO-10243-light-load-norelem?info=norelem%2Fsysteme_u_komponenten_fuer_den_maschinenbau%2Fgruppe_26000%2Fdruckfedern%2F26000.prj).

| Pair | Extra preload | Open force | Force at 30 mm travel |
|---|---:|---:|---:|
| Light target, 2 × 2 N/mm | 0 mm | 4 N | 124 N |
| Light target, 2 × 2 N/mm | 2 mm | 12 N | 132 N |
| Existing, 2 × 7.8 N/mm | 0 mm | 15.6 N | 483.6 N |
| Existing, 2 × 7.8 N/mm | 2 mm | 46.8 N | 514.8 N |

These are nominal spring calculations, not device load ratings. General relation: F = 2k(1 + p + x), with p the additional preload in mm and x the pull travel in mm. Installed spring length is 101 − p − x mm.

## Synchronized preload

`preloadAdjustment` allows **0–2 mm additional compression**, giving 1–3 mm total initial spring compression. A single **M6×1 thumbwheel screw** pushes a steel backing cassette, the sensor, its central pusher, the floating yoke and both fixed seats forward together. One turn adds 1 mm to both sides. No separate left/right adjusters are needed.

The original integral sensor wall becomes a fixed nut support and two cassette guide cheeks. New metal bodies:

- H11: custom 12 × 12 × 5 mm square steel nut, M6×1, with a radial M3 setting-lock thread.
- H12: 4 mm thick steel backing cassette, 27 × 21 mm, with two machined retention ears; preserve the sensor's Ø15 × 1.6 mm rear-centre relief and outer-ring support.
- H13: nominal Ø6 × 12 mm threaded adjuster with Ø22 × 2.8 mm thumbwheel and flat tip. Thread is represented by a smooth cylinder.
- H15: 2 mm S355 steel rear nut keeper, 32 × 19 mm, recessed 1 mm into the printed wall; two 90° countersunk M3×8 screws at Y±11/Z24, maximum head diameter 6 mm, through-bolted into captive 5.5 × 5.5 × 1.8 mm steel square nuts. Screw heads finish at X−23. Supplier head dimensions and countersink depth must match.

The screw/cassette contact transmits compression. The cassette is now retained by two M3×8 screws and Ø4/Ø3.2×4 mm steel shoulder spacers in slotted guide cheeks. The nominal pin-center limits are X−13 and X−11, giving 0/2-mm adjustment stops. The bolts tighten onto the steel ears/spacers, not the printed guide faces. A recessed M3×4 screw through H11 presses a Ø2.5×1 mm brass pad against the M6 thread to lock the setting. The stops are position limits, not torque limiters: stop at first contact. The pusher now has a Ø8×1 mm shoulder, Ø4×1.9 mm contact tip and M3×6.5 mm tail retained by a square nut in the yoke. The sensor itself still requires support when the springs are removed; its final unloaded capture is an open mechanical issue. The main nut must be held during disassembly of the setting lock/keeper. The thumbwheel is adjusted unloaded; access beneath the palm and cable slack through the full 2 mm shift need physical verification. The narrowest nominal wheel/wall clearance is 0.2 mm and keeper/palm clearance 0.25 mm, so manufacturing tolerances matter.

## Sensor-compatible isometric lock

`isometricLock = true` **replaces both springs** with two matched **steel sleeves Ø16 / Ø8 × 86 mm**, H140/H141. They slide over the existing rods between the existing steel seats. This is a removable compression lock, not a lever-operated latch and not a bidirectional brake. Sleeves must be square-ended, deburred and matched in length within 0.05 mm; differential length and end parallelism need checking under load.

The load path is:

**Finger carriage → moving steel seats → two rigid sleeves → fixed steel seats → floating yoke → central pusher → FX1901 → backing cassette → adjuster/nut/keeper → base.**

A carriage-to-base pin would bypass the sensor; these sleeves do not introduce that bypass. Guide friction can still cause measurement error, and compliance means “isometric” is not literally zero displacement.

The selected seated travel is **15 − p mm** (15 mm at minimum adjustment, 13 mm at maximum). CAD ignores `previewTravel` in this mode and reports actual travel. Contact spacing is 106.25–108.25 mm. There are no return springs in this mode: the user takes up free travel until both sleeves seat, then pulls against the rigid stack. This fixes the working position only in the pulling direction. The normal 30 mm endstop remains clear and the full-stroke switch does not detect the isometric hold. Software must not gate force measurement on that switch; isometric timing/control remains a firmware task.

Remove hand load, support the loose sensor stack, release preload and remove the rear retainers before exchanging both springs for both sleeves. Refit rods and retainers before applying load. Never use one spring and one sleeve. Do not change mode under load. Recheck calibration after reassembly; preserve a raw force reading and separate the user tare from any overload threshold.

## Verification and release work

`review/check_device_upgrades.py` checks both force profiles over 61 travel positions × 21 preload settings, lock seating dimensions, working clearances and source options. It does **not** compile FeatureScript, validate exact solids, establish strength or qualify a spring supplier.

Current source verification is recorded in `review/onshape-full-review.json`: 43 selected pair groups per configuration, with boundary/intermediate preload and travel plus the existing springs and isometric sleeves. Actual hardware geometry is included. Zero-volume contact findings remain REVIEW rather than being silently called clear. See `FULL_REVIEW.md` for the exact results and unresolved prototype tests.

The older `onshape-upgrades-validation.json` refers to the previous geometry. It cannot validate the new retention hardware. The physical handscan conflict, force rating, spring qualification, final electronics mounting, cable path and sensor capture remain release blockers. Do not mix old and new P01/P05 parts.
