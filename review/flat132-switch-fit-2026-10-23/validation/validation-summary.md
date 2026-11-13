# R4 drawing-based switch fit: nominal native validation

Status: **NOMINAL_GEOMETRY_CHECKS_PASS**. Failed checks: **0**. Unresolved checks: **0**.

Immutable checkpoint: [Onshape R4](https://cad.onshape.com/documents/15316cc6370631845af136b2/v/1a51bc54c29fb727dcb77016/e/d253eb87b70818ebde8215f0).

Source SHA256: `b150ff3a76cfaaaaa65ee1ea09e144b7c7d64e45459a925163e56918f48bb3c5`.

The SS-01GL2 reference moves +4X/+1Y/+1.5Zmm. H09 includes three solder-tab boxes and a conservative lower-lug strip based on the manufacturer drawing; it is not factory CAD. The fixed-length H09a/H09b lever/roller preview remains an approximate mechanism. The cam uses a nominal M3x8 screw and recessed head with a diameter5.8mm relief. Selected native measurements check the1.3mm guide roof web, raised pedestal, pilot diameters, tabs/lug and other preserved local sections.

Only P01/P04/H09/H09a/H09b/H10 may change from frozen R3. Exact coordinate-set comparison permits facet-order changes without geometric rounding. An independent exact STEP audit reconstructs the six changes by CSG and compares every remaining native BRep with frozen R3. It separately checks three terminal slabs against the intact P05 through full preload, nominal L4 insert engagement and a partial diameter4mm driver-shank corridor. A full screwdriver handle and head socket are not modeled.

All105 native STEP solids must be valid positive volumes and uniquely associated with the52 device and53 electronics reference bodies. The actual TE sensor remains exact and unscaled. Exact P02/P03 intersection is zero; their shared nominal curved/flat interface is supported by a separate source containment proof. The R3 half-round palm fit and complete P05 force path/stops remain unchanged.

Neutral,28mm/preload2mm maximum and13mm/preload2mm isometric exports are checked against declared source motion. Continuous certificates cover stroke≥0, preload0–2mm and stroke+preload≤30mm; all affected static, spring-envelope and finite service paths remain strict. H10 requires manual resetting by−preload after every preload change, actual switch calibration and relocking. The one-mm nominal trip lead is not a guaranteed margin under operating-position tolerance or unknown total travel.

This evidence qualifies nominal CAD geometry only. Actual switch/insert/screw stock, soldering/wire bends/insulation/strain relief, printed fit and durability, hand comfort and force calibration require prototype checks. **500N remains a design target, not a verified printed working-load rating.**

Full evidence: [validation.json](validation.json), [native-step-inventory.json](native-step-inventory.json), [switch-fit-audit.json](switch-fit-audit.json), [source-fit-certificate.json](source-fit-certificate.json), and [validation-summary.json](validation-summary.json).
