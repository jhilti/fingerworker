# Flat132 R7 — print and assembly

R7 uses two captive screw-adjusted return shoes instead of the fixed rear extensions. The rear frame, cap interfaces and guide-rod ends are shortened together by 5 mm; use the coordinated R7 parts as a set. The existing one-piece rigid P02 palm remains, without a TPU palm sleeve. The four P07 contact pads remain flexible and now attach to the P120/P121 shoe faces. They retain their 1.5 mm flat geometry; no new snap fit or mechanical pad interlock is modeled. Secure the flat pads to the shoe shoulders, for example with an adhesive compatible with the selected TPU and rigid print. The pads carry compressive return contact; attachment retains them during unloading. Material compatibility, attachment and retention require a physical check.

For mounted setup, unload the springs, loosen each jam nut and set both return shoes to equal caliper-measured positions. Use a FACOM 97.6X7 through-box spanner at its 7 mm end (OD10.70 mm, manufacturer-stated full opening, length110 mm) with a long 2 mm hex key of at least125 mm useful reach through the bore to counterhold the adjuster. Hold the hex key stationary and turn the tube’s outer hex with a wrench to lock the jam nut. Check that the actual tools reach and turn freely before using this route. The nominal M4×0.7 thread advances 0.7 mm per turn; match the two measured shoe positions and verify the actual screw pitch. The qualified CAD setting is 0–2 mm; the pin/slot has nominal clearance permitting about −0.1…2.1 mm physical movement. Do not force the screws past the stops: overdriving can damage the printed capture slots. There is no automatic equalization or preload linkage. Unequal adjustment can twist or bind the carriage and must be checked physically.

Use `a` for additional rear rest adjustment and `p` for sensor preload. Keep `a≥0`, `p≥0` and `a+p≤2 mm` to preserve the approved 28–30 mm dynamic stroke. Actual carriage displacement is `q=5+a+u`, with user stroke `u≤30−a−p`. The spring working length is `96−a−p−u mm`, so the nominal fully pressed minimum remains 66 mm. The return contacts carry the initial/rest reaction; the integral P05 stops preserve the sensing end-force path. Initial hand force unloads the return reaction before motion, creating the existing measurement dead zone.

Retain both matched 81 mm steel isometric sleeves, nominal Ø16/Ø8 mm, in place of the springs. These are metal hardware, not printed parts. Their absolute seating position stays `q=20−p`; measured from the adjusted rest it is `u=15−p−a`.

P11 cam setting remains manual: calibrate trim `e`, set its offset to `e−p`, then clamp with H10. A rear rest change does not change the fixed sensor endpoint; a sensor preload change still requires cam reset. Real switch trip, release and overtravel remain physical calibration tasks. The Omron SS-01GL2 is represented from the manufacturer drawing, with illustrative actuator motion, not factory STEP.

Heat-set insert stock dimensions are still unknown. Match the nominal seats to actual insert OD, length and recommended pilot before printing; keep steel force-path nuts and keepers. Filament, layer direction, perimeters, infill, printed threaded interfaces and all load-bearing joints need physical qualification. A closed solid palm CAD block does not specify slicer infill or establish 500 N capacity. Service only with the device unloaded and stored spring energy restrained or removed.

The verified native set contains 123 solids: 70 device bodies and 53 electronics references. The 16 print pieces are P01, P02, P04, P05, P060/P061, P070a/P070b/P071a/P071b, P08/P09/P10/P11 and the two new P120/P121 shoes. All four exported whole poses and native counts pass independent nominal validation. STL files remain unsliced native millimetre geometry in original assembly coordinates, without remeshing, scaling or recentering.


The rear hardware is specified at nominal catalogue dimensions. Check purchased hardware against the modeled envelopes:

| Quantity | Ref | Hardware |
|---:|---|---|
| 2 | H260 / H261 | M4×10 ISO4026 flat-point set screw, nominal 0.7 mm pitch, 2 mm hex |
| 2 | H270 / H271 | M4 DIN562 thin square main nut, 7×7×2.2 mm |
| 2 | H310 / H311 | Steel M4 DIN9021 reaction washer, OD12 / ID4.3 / thickness1 mm |
| 2 | H320 / H321 | M4 DIN439 jam nut, AF7 / thickness2.2 mm |
| 2 | H280 / H281 | M2×8 socket-cap capture screw |
| 2 | H290 / H291 | M2 DIN562 square capture nut, 4×4×1.2 mm |
| 4 | H300a / H300b / H301a / H301b | M3×8 socket-cap rear mounting screw; 5.5×3 mm head envelope |
| 2 | H040 / H041 | Ø6×141 mm steel guide rod; replaces the 146 mm R6 length |

Load each main nut and reaction washer before closing the P06 retainer onto P01. The P01 seat closes the main-nut trap; support and retain loose nuts/washers when the cap is off the base. The printed shoulder, washer and main nut carry the rest reaction; the accessible jam nut locks the setting. The Ø11 mm CAD tool well admits the specified OD10.70 mm FACOM end with 0.15 mm nominal radial clearance; actual tool shape, print tolerance and usable hex-key reach still require fitting. An ordinary closed 7 mm driver can block simultaneous counterholding. As a fallback, unload and remove both P06 cap assemblies, set equal shoe positions on the bench, counterhold with a 2 mm hex driver and lock with an ordinary 7 mm wrench, then remount. Fit the two M2 capture screws and captive steel nuts before applying spring load. Keep those capture screws installed during normal adjustment. No locking torque or cyclic-retention rating is established.

The base length is 151 mm, 5 mm shorter than R6, and the rod ends move forward 5 mm. The modeled physical-device X envelope at a=0 is 176.5 mm versus 180.1 mm in R6: the adjustment hardware leaves a verified net 3.6 mm reduction. At a=2 the fixed capture bosses set the physical X span to175.6 mm. This is distinct from the unchanged 132 mm width.


The mounted setup tool is specified by its actual envelope, not by AF7 alone: [FACOM 97.6X7](https://www.facom.com/product/976x7/double-socket-wrench-97-6-points-passage-hole-6x7-mm), [manufacturer dimensional sheet](https://docs.rs-online.com/02fa/A700000008417796.pdf). An equivalent tool must match the usable end OD, verified axial key clearance and reach. The manufacturer’s “full opening” supports the through-tool route, but a minimum axial bore is not dimensionally established here. Gauge-check at least2.4 mm axial clearance for the 2 mm hex key (2.31 mm across corners). A nominal long-key example is [Wiha 33442, 2.0×150 mm](https://www.wihatools.com/products/soft-grip-dual-drive-hex-t-handle-2-0mm); verify at least125 mm useful reach with the actual tool. The 0.15 mm nominal radial clearance is not a physical fit guarantee.

The native STEP also includes electronics references, including USB-approach and side-button travel volumes extending outside the physical housing. These REF E06/E08 clearance envelopes do not define the physical-device footprint. All native solids remain in the STEP inventory; the printable/device STL sets contain P/H parts only.


For rear-unit service, unload the springs and positively restrain the carriage at rest. Remove all four H300a/H300b/H301a/H301b cap screws. Keep each cap, shoe, capture pin, adjuster, nuts and washer together while pulling both rear units straight in +X by15 mm to disengage the shortened rods; support the loose hardware before lifting it off the base. The M2 capture pins stay fitted for ordinary adjustment and are removed only for unloaded shoe service. The final service audit records these prerequisites and the checked paths.
