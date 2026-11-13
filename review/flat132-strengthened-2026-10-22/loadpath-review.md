# Printed reaction portal: load path and comparative sections

**22 October 2026 — engineering review; 500 N is a design target, not an established working-load rating.**

The red outline identifies the teal P01 reaction wall and its sensor-cassette guides. It is part of the main force path. The original wall is 6 mm deep (X−22..−16), 48 mm wide and rises to Z29. Its guides and lower closed slot ends already act as ribs, so describing the baseline as a bare unsupported 6 mm plate would be inaccurate.

The retained force path is P04 → spring seats and springs (or isometric sleeves) → P05 → H02 → genuine H01 sensor → H12 → H13 M6 adjuster → H11 nut → H15 keeper → H16/H17 fasteners → P01 → base and palm attachment. H11 sits in a through pocket; H15 and its two M3 fasteners therefore carry the reaction, rather than serving only as unloaded retention.

At 30 mm travel and 2 mm additional preload the heavy pair compresses by 36 mm including its original 4 mm compression: 2 × 3.709 × 36 = **267.048 N nominal**. The light pair reaches 218.262 N. Isometric user force is independent of the spring rate. The user requested a **500 N target**, including isometric use. This produces 7,000 Nmm about the base top (Z4) or 10,000 Nmm about the bottom (Z−2), with the sensor axis at Z18. A 1,000 N case is recorded only as an engineering sensitivity; it is not a prescribed or performed proof test.

The frozen printed candidate thickens the wall to 6.75 mm, broadens the guide ribs from 3 to 5 mm, adds upper flanking gussets, and closes the top with a bridge at Z30..33. The wider rib slots retain the existing hardware envelope; the positive-Y gusset has an open lead window. The 132 mm frame, 72 mm finger opening and original force datums stay fixed. No new steel bracket, new hardware or sensor reshaping is proposed.

The table compares exact local horizontal sections of the native R1 and final R2 STEP solids using OCCT. The previously reconstructed analytic candidate agrees with these final native section properties to numerical precision. These are geometry comparisons, not a stress analysis. The root section includes the existing guide ribs.

| Z (mm) | Baseline area (mm²) | Candidate area (mm²) | Baseline Iy (mm⁴) | Candidate Iy (mm⁴) | Iy ratio | Front modulus ratio |
|---:|---:|---:|---:|---:|---:|---:|
| 4.1 | 345.0 | 437.9 | 4150.6 | 6927.3 | 1.669× | 1.685× |
| 8.5 | 309.0 | 377.9 | 2634.2 | 4398.5 | 1.670× | 1.652× |
| 11.8 | 270.0 | 401.5 | 2572.1 | 5823.1 | 2.264× | 2.442× |
| 18.0 | 233.0 | 353.3 | 2012.9 | 4591.5 | 2.281× | 2.545× |
| 24.0 | 193.8 | 309.4 | 2143.0 | 4364.7 | 2.037× | 2.260× |
| 27.0 | 277.0 | 388.3 | 2589.6 | 4819.1 | 1.861× | 2.012× |
| 30.5 | 0 | 496.8 | — | 4602.3 | New roof | — |

At the root, Iy increases by 66.9% and the front section modulus by 68.5%. At the sensor-axis height, local Iy increases by 128.1%. This substantiates a geometric reinforcement; it does not establish the same percentage increase in whole-device strength or stiffness.

The keeper fasteners remain above the sensor axis: Z24 versus Z18 gives a 3,000 Nmm local eccentric moment at 500 N. Plate flexibility, prying and contact determine their actual loads, which can exceed F/2 per bolt. More printed wall material alone does not qualify that interface. The main base, palm attachment and other load-bearing pieces also require the same load case.

Required qualification remains tied to the actual polymer, print orientation, perimeter/infill strategy, layer bonding and conditioning. It must cover deformation and sensor alignment under load, eccentric loading, sustained-load creep, cyclic loading, fastener fit and the complete force path. The current review supplies no polymer allowable and no 500 N rating.

Geometry and service checks must separately verify every preload/travel configuration, lead exit, keeper driver path and the unloaded removal sequence. The hand scan is an approximate visual reference; no hand-fit conclusion follows from this reinforcement.

Final native source bindings:

- Final FeatureScript SHA-256: `d5eca2f3d87bf4b9a47c1987ee91ba1d56e8c87003eca101677a148a2e605654`.
- Native R2 STEP SHA-256: `31b4df767555af39219028c5363b12f277e60b7a0c0d784b868e4bb20dc47859`. Its export used source `6c877ec401051cdf840a93bb28dfeb9c3fb5a13f5324c93b567c8f87e0dfa2ad`; the [guard-only certificate](source-ui-guard-only-certificate.json) proves the final source changes only the numerical UI validation guard and no geometry expression.
- Baseline native R1 STEP SHA-256: `6de4383e6423fd1f57bd353d8f42953ecdae841bee1e36b853fb312c679fd7ef`.
- Full native section values, STEP solid indices, exact stop-contact results and historical analytic cross-check: [loadpath-review.json](loadpath-review.json).

## Broad printed stops through the sensing yoke

The current stop candidate replaces H070/H071/H080/H081 with two broad, integral P05 faces. P04 presses those faces, so the intended endpoint reaction goes through P05, H02 and H01 before reaching the reinforced rear portal. The old P01-mounted hard-stop bypass is removed. Guide friction, eccentric loading, side contacts and loaded deformation still affect how accurately the sensor represents hand force. This is a principal force-path change, not a metrology guarantee.

The 10 × 22 mm arm roots are centred on Z18 and carry predominantly axial compression. Their 220 mm² gross area gives 1.136 MPa nominal at 250 N per arm or 2.273 MPa at 500 N on one arm. Exact native STEP face intersections confirm **308.000 mm² of shared P05/P04 contact per side, 616.000 mm² total**, after moving neutral P04 −30 mm relative to P05. The solid intersection volume is **0.000 mm³**. Both contact centroids are at X35, Z18 and Y±24. This represents both 30 mm travel / zero preload and 28 mm travel / 2 mm preload after subtracting their common translation. Nominal contact pressure is 0.812 MPa at 250 N per face and 1.623 MPa at 500 N on one face, compared with the much smaller contact area of the removed M4 tips. These calculations assign no print allowable. A one-sided 500 N stop load also produces 12,000 Nmm about the central sensor axis; the yoke and guides must resolve it, and guide friction can divert some force from H01.

The fixed printed faces move with preload. Contact occurs when `stroke + preload = 30 mm`: maximum frame travel is 30 mm at zero preload and 28 mm at 2 mm preload. The nominal spring load at that endpoint is therefore 252.212 N for the heavy pair or 205.034 N for the light pair. Under an ideal balanced 500 N endpoint hand load with heavy springs, the additional stop load is 247.788 N total, or 123.894 N per face. The 250 N / 500 N arm screening cases conservatively consider the stop members separately; they are not added to spring force and then described as a 500 N total hand load.

H10 must be adjusted manually after every preload change. Backing its M3×12 screw out by the preload distance places the cam face at `X60 − preload − stroke`. This preserves a nominal one-millimetre switch lead: trip at `29 − preload`, stop at `30 − preload`. There is no automatic physical linkage. For the 0–2 mm reset, the screw tip remains at X73..75 and still covers the complete nominal insert region X63.8..69; head-back clearance to P04 is 1..3 mm. A further ±1 mm fine adjustment is nominally possible, with a 0.5 mm minimum tip gap at maximum advance. Real insert/thread dimensions, a specified setting-retention method and unloaded switch checks remain required; no positive H10 lock is modeled.

Current firmware and app behavior remains fail closed at NC LOW or an open cable. Endstop status bit32 blocks qualified force and peak updates (`status == 0` is required), although raw ADC data continues. Changing the CAD does not itself make end-stop force display valid. The current `HARDWARE_QUALIFIED = false` default and NC/open-line fault are preserved. Any future qualified endpoint measurement mode needs an explicit coordinated firmware/protocol/app change; simply suppressing the NC fault is not an acceptable substitute.
