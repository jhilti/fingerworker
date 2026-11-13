# Softer spring conversion for the R9 prototype

The user has fitted the lighter **0X-DF2194** pair and requested **two thirds of the current force** on 26 October 2026. This is a 33% reduction. The target retains the closer grip and the existing 28–30 mm travel.

The proposed conversion uses **two Febrotec 0X-RDF2127 springs** and **two identical 22 mm axial spacers** on the fixed/yoke steel spring seats. No main printed part is changed. This accessory is local CAD; the frozen R9 Onshape version and its original print files remain as recorded.

## Catalogue match and force calculation

The [manufacturer product page](https://www.febrotec.de/de-DE/druckfedern/schraubendruckfedern/0x-rdf2127/), checked live on 26 October 2026, specifies:

| Property | 0X-RDF2127 |
|---|---:|
| Rate, each | 2.212 N/mm |
| Free length | 80 mm |
| Outer / inner diameter | 16 / 12.4 mm |
| Wire diameter | 1.8 mm |
| Material / ends | 1.4310 stainless / ground |
| Catalogue test length L1 | 34.75 mm |
| Force at L1 | 100.09 N |
| Approximate solid length | 29.92 mm |

The 22 mm spacers compensate for the 22 mm shorter free spring length. The spring bearing shoulder, not the pilot tip, sets this dimension. The resulting nominal force ratio is **2.212 / 3.307 = 0.668884**, or **66.9% of the original force**, throughout the legal dynamic travel at the same adjustment settings.

| Squeeze from rest, zero extra adjustment | Original pair | New pair |
|---|---:|---:|
| 0 mm | 39.68 N | 26.54 N |
| 10 mm | 105.82 N | 70.78 N |
| 20 mm | 171.96 N | 115.02 N |
| 30 mm | 238.10 N | 159.26 N |

With the combined adjustment a+p=2 mm, resting force is 35.39 N, travel is 28 mm, and the same 159.26 N endpoint applies. The minimum spring length becomes **44 mm**, 9.25 mm longer than the catalogue L1, and the maximum calculated force is 79.632 N per spring. These are nominal linear calculations excluding tolerances and friction. The catalogue selector describes L1 as a minimum operating length but does not assess fatigue, buckling or installed guidance; physical behaviour must be checked on the prototype.

## Adapter and assembly

Print **two** copies of `print/S01_spring_spacer_22mm.stl`, at 100% scale. Its body is Ø16 × 22 mm with a Ø6.6 mm through-bore and a Ø11.4 × 2 mm spring-centering pilot. Overall height is **24 mm**, while the effective spring spacing is **22 mm**. The nominal spring-to-pilot radial clearance is 0.5 mm. The ground spring end must sit flat on the annular shoulder, not on the tip of the pilot.

Unload and restrain the mechanism before changing springs. Keep the existing steel seats and both Ø6 mm steel guide rods. On each side, assemble from the sensor yoke toward the finger carriage:

1. Existing fixed steel spring seat.
2. New spacer, broad flat root on the steel seat and pilot facing the spring.
3. New 0X-RDF2127 spring around the pilot and guide rod.
4. Existing moving steel spring seat and finger carriage.

The order is the same on both sides. Use the same adjustment on both sides, starting at a=p=0. Remove the 22 mm spacers together with these springs if reverting to the original 102 mm springs or the existing isometric sleeves. The spacers are not an isometric locking part.

The STL is oriented with the broad root on the build plate. Use the separately supplied H2D / 0.4 mm / PLA project for the two adapters. A finished pilot must slide freely into the real spring, both spring ends must seat flat, and both rods must move without binding. Verify actual coil clearance and complete travel before increasing force. PLA adapter strength, creep and cycle life have not been qualified; this conversion does not establish the device's 500 N rating.

The local part checks and exact force data are in `spring-change.json`. The independent geometric integration audit in `validation/adapter-native-audit.json` passed **503 checks with zero failures** against the exact frozen R9 STEP. It checks conservative continuous motion envelopes over the full adjustment/travel domain. The minimum nominal spacer/carriage clearance is 1.083 mm and the nominal new coil/carriage clearance is 1.0 mm. This is local accessory verification, not native Onshape regeneration. No spring order or printer transmission was made.
