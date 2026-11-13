# R12 review: enclosure and printable part count

Date: 2026-11-03. Read-only review of released R11 plus a separate local candidate. No canonical source, Onshape document, released print package, or HTML was changed by this review.

**Selected R12 direction:** retain the separate P09 lid and all R11 enclosure clips. Reject the integrated ceiling because the actual slice moves support onto fit-critical electronics contact faces. Only the two obsolete P10 screw-pilot holes in P08 are removed; the main part-count reduction comes from the separately reviewed rear assembly.

## Existing count and useful consolidation

R11 contains **10 device print bodies**: P01, P04, P05, P060, P061, P08, P09, P11, P120, P121. Its **13-piece print package** additionally contains the two H040/H041 rod proxies and the Q01 unloaded alignment fixture. Those three are test aids, not three additional functional plastic device components.

| Part/group | Review conclusion |
|---|---|
| P01 frame and palm | Already one solid. Keep load path, guide clearance, sensor service and enclosure release space. A ceiling merge is feasible geometrically but has the print-quality tradeoff below. |
| P04 finger carriage | Must move relative to P01 and P05; merging would remove its function. Its R11 front-down orientation already moves support away from the finger-contact wall. |
| P05 spring/sensing yoke | Must remain floating so force passes through the pusher and sensor. A frame clip or frame fusion would bypass the sensor. |
| P060/P061 + P120/P121 | The largest remaining count/shape opportunity. If the rear adjustment is intentionally removed, a fixed return face and rod socket can be one cap per side; a common rear gate may reduce two caps to one if rod insertion, switch/wiring access, and release are proven. This is the separate rear-design workstream. |
| P08 tray | Existing base, PCB edge supports, battery rails, USB/button/lead apertures, two palm clips and optional M2 mounts each have a function. Keep P08 detachable; permanently fusing it to P01 would make electronics loading/service difficult. |
| P09 lid | Already includes the former P10 wire clamp. Existing support-free outer-face-down print gives clean PCB/battery/wire contact features. A permanent P01 ceiling can remove it, subject to the tradeoff below. |
| P11 switch shoe | Small but functionally independent: its position compensates switch tolerance and the retained central sensor-preload setting. Do not fuse solely because the rear adjustment is removed; evaluate switch adjustment separately. |
| P07 / P10 | Already eliminated as loose pieces in R11. Do not count their prior elimination again as an R12 reduction. |

## Enclosure details to retain

The existing P08/P09 forms are mostly functional primitives rather than ornament. The PCB rails carry the board from below. The narrow lid rib at Y−27…−25 holds the PCB over its free corridor; it ends at Z2.15 while the nominal PCB top is Z2.10. The battery ceiling rail is deliberately loose rather than clamping a LiPo. The integral wire clamp does not replace a cell strap. The two short original P10 screw posts still define the wire-clamp support plane; their now-unused pilot bores can be removed, but deleting the entire posts changes the wire channel and clamp geometry.

With an unchanged separate lid, the three M1.6 lid screw posts/holes preserve the optional screw reinforcement explicitly requested earlier. Removing them merely cleans a small amount of geometry and loses that option. The two M2 tray-to-frame mounts should likewise remain available alongside the palm clips.

The long 1.2 mm clip arms and their root/lead-in geometry are functional. Replacing them with short rigid nubs would change PLA strain and assembly force. Current release distances are ±Y0.6 mm for the palm clips; detached P09 releases outward −X0.9 mm before +Z15 mm.

## Rejected local candidate: fixed P01 electronics ceiling

Candidate implementation and evidence are in [enclosure-candidate](enclosure-candidate/). The design merges the rigid P09 skin, PCB keeper, loose battery rail and integral wire clamp into P01. A 0.7 mm connecting layer bridges the previous 0.6 mm nominal palm/lid gap. P08 keeps its original two palm clips and optional M2 mounts. Its two lid catches, three now-obsolete lid screw posts and the two old P10 screw pilot holes are omitted. The short wire-support posts remain. P09 and its two lid clip arms no longer exist as a separate body.

The ceiling is created **unconditionally** at final fusion, after the existing region audits. `showElectronics=false` therefore still generates the complete structural P01. P08/electronics display remains conditional. A final native validator must test the added ceiling because the legacy region audit deliberately executes before that fusion.

The H15 keeper service notch is explicitly preserved in the connecting layer: X−25.5…−23.1, Y±16.5, Z8.9…14.7. This leaves the original 0.8 mm ceiling skin, whose top Z8.9 lies below H15's bottom Z9. Without this notch the merge would block keeper withdrawal.

Nominal OCP result: **137 checks pass**. P01 and P08 are each one valid solid. Complete conservative electronics/battery/PCB envelopes clear the downward 20 mm tray service route. The whole tray with spread palm hooks clears 81 sampled poses; this sampled tray check is not a continuous trajectory certificate. H15−X2/+Z35, H13+X12/+Z40, H11+X9/+Z40 and H01/H12/H23+X3.2/+Z40 clear both sampled exact shapes and conservative continuous envelopes against the new ceiling. H13 uses separate shaft/wheel bounding boxes, verified to cover the full native body: a single full-body box would falsely fill empty space below the small M6 shaft.

P01 gains 3850.816 mm³; the candidate tray volume is 4887.117 mm³. Overall P01 dimensions stay 175.1×132×35 mm. Selecting this candidate removes **one actual printed body**: 10→9 device parts, or 13→12 pieces in the unchanged fit package before any rear consolidation. It requires reprinting P01.

## Actual H2D slice tradeoff

The local candidate was sliced with the existing H2D 0.4 mm PLA profile, normal bed-only P01 supports, 0.25 mm support top gap, unchanged upright frame orientation. No printer job was sent.

| P01 only | R11 | Integrated-ceiling candidate |
|---|---:|---:|
| Predicted duration | 29,786 s | 30,615 s |
| Predicted PLA | 131.35 g | 133.81 g |

These are P01-only figures; the candidate additionally eliminates the separate P09 print, so they are not a whole-package penalty calculation.

The added underside remains open downward and toward the wrist; it does not create a sealed support pocket. However, the actual slice puts support on **three formerly clean, support-free P09 contact features**:

| Contact region | Actual support-interface segments | Chord path in the region |
|---|---:|---:|
| PCB keeper | 46 | 265.408 mm |
| Battery ceiling rail | 28 | 161.112 mm |
| Wire clamp | 8 | 115.428 mm |

The roof skin has a further 226 interface segments and 120 transition segments in the inspected region. These counts localize actual toolpaths; they are not a material-strength or physical support-removal test.

**Decision:** keep the two-piece P08/P09 enclosure. The ceiling merge is a real one-part reduction with intact nominal service paths, but it moves support cleanup onto a PCB keeper with only 0.05 mm nominal board clearance. The rear adjustable mechanism offers a larger reduction without moving electronics-contact features onto supports. The fixed-ceiling files remain explicitly rejected local study files and must not enter the R12 delivery.

The candidate local STL contained eight collapsed, zero-area tessellation facets at tangent seams. Only those degenerate facets were removed for the exploratory slice, with exactly zero mesh-volume change. No holes were filled and no surface was remeshed. This is documented in `local-tessellation.json`; it is not an authorization to repair or replace native release meshes silently.

## Reusable entry points

- **Selected cleanup:** `enclosure_cleanup.py` exposes `expected_cleanup(old)` and `source_cleanup_patch(source)`. It fills the two former P10 pilot bores, radius0.625 mm, Z1.2…3.4 at X−26.5/Y24 and31, and omits the matching operations21/23 in FeatureScript. Total nominal fill is5.3996 mm³. All existing outer geometry, support posts, rails, three optional lid screw posts, both optional M2 mounts and all four enclosure clip arms remain. `enclosure-cleanup-check.json` checks this limited change against the R11 part geometry.
- `enclosure-candidate/build_candidate.py`: `expected(old)` returns candidate P01/P08 and `source_patch(source)` patches R11 or a rear-only derivative. `make(old)` can consume an already-modified P01, so localized rear changes can compose. The patch uses its own final-fusion helper rather than conditional electronics generation.
- `enclosure-candidate/geometry-service-check.json`: local nominal/service results. Independent final native identity checks remain required.
- `enclosure-candidate/slice_candidate.py`, `slice-result.json`, `support-review.json`: official local Bambu slice and actual support-localization evidence. The seed retains inherited R11 descriptions and is explicitly marked a local, unreleased candidate in its manifest.
- `review/flat132-click-assembly-2026-11-03/enclosure/build_enclosure.py`: exact R11 clip primitive stocks, R10 native loader and baseline geometry utilities.
- `review/flat132-click-assembly-2026-11-03/enclosure/audit_motion.py`: conservative full operating-domain envelope method for any altered enclosure stock.
- `review/flat132-click-assembly-2026-11-03/enclosure/check_final_toolpaths.py`: final native P08/P09 support/clip checks and a reusable G-code parser.
- `review/flat132-integrated-palm-2026-11-03/validation/audit_service.py`: retained sensor, H15, H13, H11 and tool access paths. The obsolete removable-lid path must be removed only if the fixed-ceiling variant is actually selected.

No fatigue, print fit, wiring strain relief, battery swelling allowance beyond the nominal existing envelope, or load qualification is inferred from the geometric passes.

## Final R12 selection

R12 retains P09 as a separate support-free lid and changes P08 only by filling the two obsolete P10 pilot holes. The final ten-piece fit package contains seven device prints and three unloaded fit aids. The final actual-path report `print/bambu-R12-simplified-2026-11-03/validation/print-feature-check.json` passes all65 checks, including the retained palm hooks, bed-connected long beams, open enclosure flexure gaps, both flat P09 latch leaves, integral wire clamp, and accessible P08 USB-roof supports. The rejected integrated ceiling is excluded from the delivery.
