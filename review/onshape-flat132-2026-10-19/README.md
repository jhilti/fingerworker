# Flat 132 mm / 72 mm pocket — separate Onshape study

The V6 variant is built and regenerated in the separate [Study 132mm flat - 72mm grip workspace](https://cad.onshape.com/documents/15316cc6370631845af136b2/w/2aac8d39cfa101ed4326a108/e/d253eb87b70818ebde8215f0). The retained Rev D baseline is version `ab85d861449a697613ca7ef3`. Main CAD, manufacturing files and the electronics order are unchanged.

**Result: geometric packaging passes; physical function and strength remain unqualified.** The overall report is `CONDITIONAL_LIGAMENT_TARGET_NOT_MET`: two local roof measurements miss a provisional screening target. The inherited sleeve/adjuster contact also remains visible below.

## Dimensions and retained functions

| Item | Native V6 result / retained function |
| --- | --- |
| Frame width / total height | 132 mm / 32 mm; 26 mm narrower than the 158 mm baseline |
| Finger pocket / deck | 72 mm clear / 84 mm outside width; 20 mm pocket depth |
| Travel / preload | 30 mm travel; 0–2 mm preload |
| Rod/spring axes | Y±51 mm, Z18 mm |
| Retained hardware | Ø6 mm rods, Ø22 mm seats, 24 mm rod supports, existing spring pairs |
| Palm / case | 128 mm main palm body and 124 mm electronics enclosure retained |
| Force path | Spring–yoke–pusher–sensor reaction path retained |
| Isometric mode | 86 mm sleeves; actual lock pose at 13 mm stroke with 2 mm preload |

P01/P02 use a new detachable, keyed palm joint with two M4 screws. The switch/cam and sensor cable route are relocated to fit the narrower frame. No additional PCB or electronics purchase is part of this study. The 72 mm opening is the accepted design input; this iteration does not validate an earlier hand-scan pose or comfort.

## Palm mounting and service

The 11 mm palm wings occupy Y±[26,37], with M4 centres at X−16, Y±31.5. Rearward keys locate the joint. The forward clamp step sits at Z6.5, while the upper root stays above the unchanged case. Geometry checks verify the step, keys, pilot floor, fastener envelopes and the stated access paths; the new two-screw joint replaces four original M4 mounts and has unqualified stiffness, strength and fatigue life.

The checks assume **two M4×10 socket-head cap screws, ISO 4762 / DIN 912, with Ø7 mm × 4 mm heads and a 3 mm hex drive**. [Bossard's M4 specifications](https://nederland.bossard.com/en-us/912000a20040025) support these head/drive dimensions; the linked article has a different shaft length, while this design retains 10 mm. The local purchasing list is generic, so actual supplied fasteners must match this head envelope. Nominal insert engagement is 6 mm, screw-tip gap 0.3 mm and pilot bottom wall 2.2 mm.

**Service requires 2 mm preload.** Remove external operating load, set preload to 2 mm, remove both M4 palm screws, then lift the palm and attached case vertically as one module. Service the keeper/cassette or capture hardware with that module removed; refit and fasten it before operation. At zero preload, the H13 rear shaft obstructs this lift. The access proof covers its recorded finite paths and tool envelopes.

## Evidence and remaining conditions

[validation132.json](validation132.json) checks the full-resolution native neutral export: **51 valid closed device solids**, 344 operating-motion certificates, 140 rear-insertion certificates and 11 access-motion certificates; 39 access checks total. It reports **zero failed packaging checks and zero unresolved checks**. Native regenerated [maximum travel / heavy springs](pose-max30-preload2-heavy.json) and [isometric](pose-isometric-preload2.json) checks also pass. Native views: [neutral](onshape-flat132-final-neutral.jpg), [30 mm travel / 2 mm preload](onshape-flat132-max30-preload2-heavy.jpg), [isometric](onshape-flat132-isometric-preload2.jpg), [separate branch history](onshape-flat132-branch-history.jpg).

The two roof-screen failures remain explicit: at X114, local rays near the rounded rear edge give approximately **3.215 mm**, approaching **3.063 mm** near |Y|42. This is below the provisional 4 mm roof screen. These local samples are not a global minimum search or a validated material-strength limit. Loaded strength and print behaviour require physical validation.

P03's soft sleeve overlaps the H13 adjuster-shaft end by **3.085995 mm³ at zero preload**, identical to the baseline; it clears at 2 mm preload. This contact is separate from the intended sleeve/core fit. TPU deformation, adjustment friction and loaded effects remain unverified; see [the neutral contact diagnostic](pose-neutral-legacy-contact.json).

The native neutral archive contains **104 STL members: 51 device parts and 53 electronics/reference envelopes**. All three native pose ZIPs have clean CRC checks. Exact source/export/screenshot/report hashes and per-member inventory are in [review-provenance.json](review-provenance.json); branch identities are in [onshape-branch.json](onshape-branch.json). Selected source: [fingerworker_flat132.fs](fingerworker_flat132.fs). Earlier V1/V4/V5 files are intermediate evidence. The final source SHA-256 is `3e5de8f56211cf2ed063b6b4294da5f77fea4c3fb881fa0c13b1288eca7932cc`.
