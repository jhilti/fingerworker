# Native geometry validation

Final R1 result: **NOMINAL_GEOMETRY_CHECKS_PASS**, with zero failed or
unresolved checks, bound to [immutable Onshape version 4c39034c](https://cad.onshape.com/documents/15316cc6370631845af136b2/v/4c39034c17201905fdfbb1d6/e/d253eb87b70818ebde8215f0)
and source SHA256 `041056629440056626b2f2f88a0db216693e48fff178687174478cb1f34227ef`.
The genuine sensor has zero Boolean symmetric difference from the canonical
manufacturer geometry at CAD kernel tolerance. The exact native sleeve/core
intersection is zero. `native-step-inventory.json` independently confirms all
109 STEP solids are valid positive volumes and uniquely correspond to the
56 device and 53 electronics reference bodies in the final native STL export.

`validate_finished.py` reads actual Onshape exports. It does not manufacture,
remesh, repair or alter the design. `manifest.template.json` contains deliberately
missing inputs and cannot produce a validation pass.

Runtime:

```bash
PY=/tmp/fingerworker-sensor-cad-20261022/bin/python
```

The exact dependency versions are recorded in `requirements.txt` and each
report. If the temporary runtime is no longer available, create a Python 3.12
virtual environment and install that requirements file.

After exporting **all parts as separate high-resolution STL files in one ZIP**
from the assembled neutral configuration, plus the complete neutral STEP:

```bash
$PY review/flat132-finished-2026-10-22/validation/prepare_manifest.py \
  --neutral /absolute/path/neutral.zip \
  --step /absolute/path/neutral.step \
  --workspace 'https://cad.onshape.com/documents/.../w/.../e/...' \
  --native-pose dynamic 30 2 /absolute/path/max30-preload2.zip \
  --native-pose isometric 13 2 /absolute/path/isometric-preload2.zip

$PY review/flat132-finished-2026-10-22/validation/validate_finished.py \
  review/flat132-finished-2026-10-22/validation/manifest.json

$PY review/flat132-finished-2026-10-22/validation/audit_native_step.py
```

`--native-pose` can be repeated to check additional regenerated configurations.
The minimum required regenerated configurations are dynamic stroke30/preload2
and isometric stroke13/preload2, in addition to neutral. Native stroke25/27 and
preload0 configurations are useful independent checks if available. The script
checks each pose's source motion against the neutral native meshes and checks
every pair in each pose. The source hash and all input member hashes are kept.

The model currently contains56 device parts: the47 retained device bodies,
without H01a..d proxies, plus H23, H240..243 and H250..253. It also contains53
electronics reference solids when those references are enabled. Unexpected or
missing bodies, duplicate reference names, invalid/negative solids and
disconnected bodies remain failures; they are not silently discarded. The two
illustrative coil meshes are excluded from physical-material collision tests
and are replaced by conservative axial spring envelopes.

## What is proved

* Every device/electronics solid pair is checked at neutral and every supplied
  native pose, using the full native triangles and closed Manifold solids.
* The official sensor must be found unchanged in the native assembly STEP.
  OCCT checks its validity and the symmetric difference from the original
  contact-aligned manufacturer BRep. Only a proper rigid unit-scale transform
  can be specified; the default is the identity. A missing STEP or ambiguous
  correspondence cannot pass.
* Source rigid movement is axial. The difference of each body's stroke/preload
  coefficients maps the full independent rectangle stroke0..30 × preload0..2
  onto one exact relative-X interval. Adaptive gap certificates cover that
  complete interval, not only the endpoint configurations. Bounds separation,
  exact transverse slab clipping and the 1-Lipschitz minimum-gap bound certify
  clearance; unresolved near-contact intervals remain unresolved.
  A convex hull of the two endpoint solids is a conservative complete swept
  envelope. If its Boolean intersection is below the numerical volume
  tolerance, every intermediate pose is bounded by that same volume. The
  report records this upper bound separately, including tiny tessellation
  residues at the intended spacer/slot endpoint contacts.
* The switch actuator follows the exact source fixed-length path around
  pivot(25.5,−14.1,9.2). Exact extrema of the rotating mesh vertices bound every
  rotation arc. Adaptive source-arc/preload rectangles use a conservative
  point-displacement bound. The roller/cam contact has an analytic separating
  X plane: roller maxX≤min(35.8,60−stroke), cam minX=60−stroke. Native regenerated
  actuator positions and shape congruence are independently checked.
* Isometric sleeves replace the springs and must have their native86mm length,
  expected seat endpoints and source-imposed stroke15−preload. Every sleeve
  collision is included in the native all-pair checks.
* Local wall rays, air/material probes and declared finite service paths cover
  the changed sensor backing, keeper, mounting hardware, floor, rear carriage
  roof, sleeve relief and selected service operations. Each records its exact
  location, assumed path and prerequisites.

## Contacts are explicit

Exterior-contact annotations never waive positive material overlap. Numerical
volume tolerance0.01mm³ is a reporting tolerance, not an assembly allowance.
The only default positive-overlap classifications are explicit nominal models:

* The unchanged lever/roller previews join at the axle of one purchased Omron
  actuator. Their internal preview overlap is bounded analytically and is not
  an independent-device collision.
* M2 full-cylinder screw envelopes occupy their tap-drill envelopes in H12.
  The analytic annulus bounds the expected nominal thread engagement. Threads
  are not actually modeled as helices.
  The two M3 cassette retention screws likewise engage their diameter 2.5 mm
  tap-drill envelopes; their finished M3×0.5 threads are explicit drawing
  callouts. Each has 2 mm nominal engagement, bounded by 4.35 mm³ of preview
  thread-envelope intersection.
* Separately triangulated nominal R7.75 sleeve/core surfaces overlap slightly.
  The native STEP pair must independently show zero real BRep intersection.
  Its result and unique solid correspondence are included in the report.
* Electronics reference E08 is a button actuator *travel envelope*. It
  deliberately reaches the SW2 courtyard/height envelope. That exact functional
  pair is labelled explicitly; it is not two physical solids occupying space.

Any larger or different intersection fails. No inherited adjuster/TPU collision
is accepted; the explicit new relief has to clear the full adjustment sweep.

## Interpretation

`NOMINAL_GEOMETRY_CHECKS_PASS` is limited to the recorded nominal CAD checks.
It is not a load rating, fatigue/print/fit certification or fabrication release.
The local retention lips, backing stiffness, actual screw/tap runout and
material tolerances need the associated manufacturing drawings and prototype
qualification. Local ray measurements do not establish a global minimum wall.
The final fixed-guide end wall is reinforced to 2.3 mm; the cassette ear roof
is a 1.25 mm local, non-primary retention feature, with a 1.45 mm rear ligament.
The open hand scan's provisional registration does not establish a complete
hand volume, comfort or motion clearance, so this script makes no such claim.

`--static-only` is a diagnostic option and always prevents a complete pass.

`nominal_native_mesh_status` reports the solid/motion/probe/service checks with
the explicit contact models. `step_roundtrip_status` separately reports the
manufacturer-sensor and native sleeve/core BRep comparisons. The overall status
remains `INCOMPLETE` while those exact roundtrip checks are pending; successful
mesh checks do not silently stand in for an unperformed STEP comparison.

`certify_source_fit.py` adds an independent exact source-level sleeve/core
separation certificate for the frozen final source revision. Its proof uses
the nonoverlapping plate/sleeve Z intervals and the identical nominal radius
of the core and full through-cut inner sleeve tool. Native final mesh bounds
corroborate the reviewed construction. `source-fit-certificate.json` explicitly
distinguishes this mathematical source proof from the independent STEP roundtrip.

## Validator checks, separate from the revised device

`check_validator_math.py` checks analytic solids, end-stop tangency, hidden
mid-sweep crossing, the two-parameter interval mapping and rotating-vertex
bounds. `validator-math-checks.json` records eight passing checks. The archived
V6 actuator diagnostic covers87 continuous pairs, and the archived native
maximum-pose diagnostic checks51 retained source motion/datum correspondences.
The canonical BRep reader check compares the manufacturer sensor to itself.
These validate the audit machinery; none is evidence that the revised export
has already passed. The files with `old-` prefixes are explicitly archival
diagnostics, including the old proxy model's reported collisions.
