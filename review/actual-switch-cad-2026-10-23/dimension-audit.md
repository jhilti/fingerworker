# Exact switch dimension audit — SS-01GL2

**The BOM specifies Omron SS-01GL2, with no extra suffix: SPDT, hinge roller lever, solder terminals.** The current R3 box and two fastener axes match its major nominal dimensions. It is still a simplified switch representation: terminals, mounting-lug details and real lever/hinge profiles are missing. R3 has not been edited.

The primary [Omron SS datasheet](https://omronfs.omron.com/en_US/ecb/products/pdf/en-ss.pdf), locally [SS_datasheet.pdf](../../vendor/omron_ss5gl2/SS_datasheet.pdf), was visually inspected: page4 solder terminals and mounts, page6 hinge-roller drawing and operating table, page7 mounting instructions. Local PDF SHA256 `b7c3cc9e838c1049d58772242b56cd06af3526ac422907769acd892668ba1a09`. The folder nameSS5GL2 does not change the exact BOM identity. Audited [R3 source](../flat132-palm-fit-2026-10-23/fingerworker_flat132_palm_fit.fs) SHA256 `4665c3ec4e983e478d34c6cfe923b3b60e6c8848f36b7c54b55b1989eaab6326`.

| Feature | Manufacturer nominal / current comparison |
|---|---|
| Main housing |19.8 long ×10.2 high ×6.4 thick; current box X14…24.2/Y−17…2.8/Z6…12.4 matches the major dimensions |
| Mounts |9.5±0.1 spacing, first axis5.1 from long end,2.5 above main housing bottom; current axes X16.5/Y−11.9 and−2.4 match |
| Mount holes |Ø2.35 +0.075/−0.05; CAD Ø2.35 is nominal. Extra middle Ø2.5±0.07 hole is absent |
| Lower lug projection |Mount line2.9 above lug bottom versus2.5 above main bottom:0.4 projection reaches X13.6; box startsX14 |
| Roller |Ø4.8 ×3.2 wide, polyacetal; current size and Z7.6…10.8 agree |
| Lever |Manufacturer0.3mm formed stainless strip; CAD Ø0.9 cylinder and inferred pivot are illustrative |
| Solder tabs |Three; nominal tips X10.1, centresY−15.4/−6.6/+0.7, Z7.6…10.8, thickness0.5 alongY; absent from current CAD |

The drawing's operation directionA maps to−X. **OP14.5±0.8 is measured from the mounting-axis lineX16.5**, so the roller contact surface operates nominally atX31.0, range30.2…31.8. This is consistent with the source's nominal1mm trip lead: cam face`60−preload−stroke` reachesX30 at the integral stop. The OP tolerance alone expands the lead/post-trip motion to0.2…1.8mm. The source uses the maximum free positionFP19.3 as an exact rest state and an inferred fixed-length lever; neither is a qualified motion model. SS-01GL2 has minimum overtravel1.2mm and maximum differential0.8mm; minimum overtravel does not specify a maximum allowable endpoint. Check actual switching, full travel and cam locking physically.

**Potential omitted-geometry conflict:** terminal tips are6.4mm below the mounting-axis line, givingX16.5−6.4=10.1. P05's central reaction web extends toX9+preload at these low heights. The drawing envelopes therefore have axial clearance`1.1−preload`:1.1mm at zero and **0.9mm overlap at2mm preload**. This is an analytical bounding-envelope finding, not an exact factory-STEP collision certificate. The [independent native-mesh audit](terminal-clearance.json) confirms the envelope overlap continuously over preload0–2mm, with independent MAX and ISO native exports as endpoint witnesses:4.32mm³ total at preload2mm (1.44mm³ per terminal box). [Section view](terminal-clearance.png). Terminal corner/hole profiles are not fully dimensioned in the PDF; solder and wires require additional clearance. The unconnectedNOtab still exists. Old switch-proxy collision passes do not cover these features.

Manufacturer mounting guidance uses M2.3 screws and washers on a flat support. Existing CAD/purchasing intent uses M2×10 plus thin washers into M2 inserts. This is a design difference requiring fastener/washer/clamping confirmation; the datasheet's0.23…0.26N·m torque for its specified M2.3 arrangement must not be transferred to the M2/printed joint. Unspecified drawing dimensions generally carry±0.4mm tolerance.

Use exact SS-01GL2 manufacturer CAD if available, aligned to its two mounting axes and broad mounting face. Preserve the original solid; do not silently use the differentD/Tterminal orSS-5rating variant. Test the real tabs/lugs against the full native assembly at both preload endpoints, then check motion and service paths. A static downloaded actuator state still needs a separate, clearly labeled operating envelope. Preserve manual cam reset and firmware failsafe; this audit does not establish electrical state or force-display permission.

See [dimension-audit.json](dimension-audit.json) for exact coordinate mappings, source line references, envelope bounds and operating-point calculations. Status: **DIMENSION_AUDIT_COMPLETE_FACTORY_CAD_PENDING**.


**STEP download status:** Exact plain SS-01GL2 CAD is listed by the manufacturer and its linked CAD providers. The live exact-selected TraceParts page offers STEP AP214, but Download leads to sign-in. No factory STEP has been downloaded or imported. No account or CAD licence agreement was accepted. The source and selection history are recorded in [step-provenance.json](step-provenance.json).

**Corrective proposal:** [A coordinated +4X/+1Y/+1.5Z switch relocation](switch-fit-proposal.md), with a raised pedestal and shorter M3×8 manual cam, clears the drawing terminal envelopes locally while keeping P05 intact.62 local contact-region checks pass. This has not been applied to FeatureScript or native CAD; factory geometry, complete native regeneration and motion/service validation remain pending.
