#!/usr/bin/env python3
"""Package R9 native parts only after nominal checks and version binding pass.

Large whole-pose STL ZIPs remain hash-bound project audit inputs and are omitted
from this compact CAD handoff. This does not relabel or synthesize native poses.
"""
from pathlib import Path
from hashlib import sha256
import argparse
import json
import re
import zipfile

R = Path(__file__).resolve().parent
ROOT = R.parents[1]
SOURCE = 'fingerworker_flat132_palm_bracing.fs'
BUILDER = 'build_palm_bracing.py'
SOURCE_SHA = '16972ba9341f4cdf763a5570dad82a4fbd601f0935d0a7657be85813f97ff2b1'
NEUTRAL = 'Flat132_R9_neutral_final.zip'
ISO = 'Flat132_R9_isometric13_p2_81_final.zip'
STEP = 'Flat132_R9_final_AP214.step'
PACKAGE = 'deliverables/Flat132_R9_Palm_Bracing.zip'


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def release_inputs():
    assert digest(R / SOURCE) == SOURCE_SHA
    build = json.loads((R / 'onshape-build.json').read_text())
    assert build['source_sha256'] == SOURCE_SHA
    assert build['native_source_exact_readback_matches'] is True
    assert build['native_regeneration'] == 'PASS'
    assert build['native_parts'] == 123 and build['device_parts'] == 70
    version = build.get('immutable_version_id')
    assert version, 'Await frozen R9 Onshape version.'
    assert build.get('immutable_source_readback_sha256') == SOURCE_SHA, 'Await immutable source readback binding.'
    report_path = R / 'validation/validation.json'
    summary_path = R / 'validation/validation-summary.json'
    report = json.loads(report_path.read_text())
    summary = json.loads(summary_path.read_text())
    for evidence in [report, summary]:
        assert evidence['status'] == 'NOMINAL_GEOMETRY_CHECKS_PASS'
        assert evidence['source_sha256'] == SOURCE_SHA
        assert evidence['failed_checks'] == evidence['unresolved_checks'] == 0
        assert evidence['step_roundtrip_status'] == 'COMPLETE'
        assert evidence['native_provenance']['immutable_version_id'] == version
    for name, expected in summary['evidence_files'].items():
        assert digest(R / 'validation' / name) == expected, name
    assert len(build['native_exports']) == 5
    for name, record in build['native_exports'].items():
        assert digest(R / 'native' / name) == record['sha256'], name
        assert record['export_source_sha256'] == SOURCE_SHA
    portable = json.loads((R / 'portable-build-check.json').read_text())
    assert portable['status'] == 'PASS' and portable['source_sha256'] == SOURCE_SHA
    assert portable['builder_sha256'] == digest(R / BUILDER)
    assert portable['source_build_sha256'] == digest(R / 'source-build.json')
    return build, report, summary


def native_members(filename, build):
    path = R / 'native' / filename
    assert digest(path) == build['native_exports'][filename]['sha256']
    members = {}
    with zipfile.ZipFile(path) as archive:
        assert archive.testzip() is None and len(archive.infolist()) == 123
        for item in archive.infolist():
            match = re.search(r'(?:^| - )([PH]\d+[ab]?)\b', item.filename)
            if not match:
                continue
            ref = match.group(1)
            assert item.filename.lower().endswith('.stl') and ref not in members
            members[ref] = (item.filename, archive.read(item))
    assert len(members) == 70 and 'P03' not in members
    return members


def prepare_parts(build):
    members = native_members(NEUTRAL, build)
    refs = sorted(ref for ref in members if ref.startswith('P'))
    assert len(refs) == 16
    mapping = {}
    for ref, (member, payload) in sorted(members.items()):
        path = R / 'assembly-mm' / (ref + '.stl')
        path.parent.mkdir(exist_ok=True)
        path.write_bytes(payload)
        mapping[ref] = {'native_member': member, 'output': str(path.relative_to(R)),
                        'sha256': digest(path), 'bytes': len(payload)}
        if ref in refs:
            printed = R / 'print-mm' / path.name
            printed.parent.mkdir(exist_ok=True)
            printed.write_bytes(payload)
    common = {'source_sha256': SOURCE_SHA, 'native_zip': 'native/' + NEUTRAL,
              'native_zip_sha256': build['native_exports'][NEUTRAL]['sha256'],
              'units': 'mm', 'orientation': 'Original native assembly coordinates; no rescaling, repair, remeshing or slicing.',
              'identity': 'Each STL is byte-identical to its named fresh whole R9 native ZIP member.'}
    (R / 'assembly-mm/part-manifest.json').write_text(json.dumps(dict(common, count=70, parts=mapping), indent=2) + '\n')
    printed = {ref: dict(mapping[ref], output='print-mm/' + ref + '.stl') for ref in refs}
    (R / 'print-mm/part-manifest.json').write_text(json.dumps(dict(
        common, count=16, changed_since_R8=['P02'], added_since_R8=[],
        flexible_refs=['P070a', 'P070b', 'P071a', 'P071b'], parts=printed), indent=2) + '\n')
    sleeves = {}
    for ref, (member, payload) in native_members(ISO, build).items():
        if ref not in {'H140', 'H141'}:
            continue
        path = R / 'hardware-mm' / (ref + '.stl')
        path.parent.mkdir(exist_ok=True)
        path.write_bytes(payload)
        sleeves[ref] = {'native_member': member, 'output': str(path.relative_to(R)),
                        'sha256': digest(path), 'bytes': len(payload)}
    assert set(sleeves) == {'H140', 'H141'}
    (R / 'hardware-mm/part-manifest.json').write_text(json.dumps({
        'source_sha256': SOURCE_SHA, 'native_zip': 'native/' + ISO,
        'native_zip_sha256': build['native_exports'][ISO]['sha256'],
        'units': 'mm', 'material_intent': 'Purchased steel ISO sleeves, not print parts.',
        'dimensions_mm': {'OD': 16, 'ID': 8, 'length': 81}, 'count': 2, 'parts': sleeves,
    }, indent=2) + '\n')
    return refs


def prepare_reference():
    baseline = ROOT / 'review/flat132-palm-cover-2026-10-23'
    copies = {
        'reference/baseline/fingerworker_flat132_palm_cover.fs': baseline / 'fingerworker_flat132_palm_cover.fs',
        'reference/baseline/Flat132_R8_final_AP214.step': baseline / 'native/Flat132_R8_final_AP214.step',
        'reference/baseline/R8-PRINT_NOTES.md': baseline / 'PRINT_NOTES.md',
        'reference/baseline/R8-final-specification.json': baseline / 'final-specification.json',
        'reference/baseline/validation/validation-summary.json': baseline / 'validation/validation-summary.json',
        'reference/baseline/validation/native-step-inventory.json': baseline / 'validation/native-step-inventory.json',
    }
    records = {}
    for name, source in copies.items():
        target = R / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(source.read_bytes())
        records[name] = {'source_project_path': str(source), 'sha256': digest(target), 'bytes': target.stat().st_size}
    (R / 'reference/reference-manifest.json').write_text(json.dumps({
        'meaning': 'Exact immutable historical R8 reference copies, not new R9 validation.', 'files': records,
    }, indent=2) + '\n')


def write_docs(build, report, summary, print_refs):
    version = build['immutable_version_id']
    url = 'https://cad.onshape.com/documents/15316cc6370631845af136b2/v/' + version + '/e/d253eb87b70818ebde8215f0'
    proof = {str(p.relative_to(R)): digest(p) for p in sorted((R / 'proof').rglob('*')) if p.is_file()}
    assert proof, 'Await CAD/viewer proof image(s).'
    spec = {
        'revision': 'Flat132 R9 fixed-frame palm bracing',
        'status': 'CAD_PROTOTYPE_NOMINAL_GEOMETRY_CHECKS_PASS',
        'source': {'file': SOURCE, 'sha256': SOURCE_SHA, 'builder': BUILDER, 'builder_sha256': digest(R / BUILDER)},
        'baseline': {'revision': 'R8', 'immutable_version_id': '6965afcca3af7c58ef3ac73f',
                     'source_sha256': '6099df42e341ff9f5c3439709a23107325d10ef922f616bdcda6fa6ef64d41c1'},
        'onshape': {'immutable_version_id': version, 'immutable_version_url': url,
                    'workspace_id': build['workspace_id'], 'document_id': build['document_id']},
        'native_exports': build['native_exports'],
        'assembly_set': {'full_native_solid_count': 123, 'device_STL_count': 70,
                         'electronics_reference_count': 53, 'source_native_zip': NEUTRAL,
                         'source_native_step': 'native/' + STEP},
        'print_set': {'count': 16, 'refs': print_refs, 'changed_since_R8': ['P02'], 'added_since_R8': [],
                      'flexible_refs': ['P070a', 'P070b', 'P071a', 'P071b'], 'rigid_palm_ref': 'P02'},
        'bracing': {'intended_contact': ['P02', 'P01'], 'support_fixed': True,
                     'contact_plane_x_mm': -22.75, 'each_face_mm': [7, 13], 'each_face_area_mm2': 91,
                     'y_intervals_mm': [[-25, -18], [18, 25]], 'z_interval_mm': [14, 27],
                     'root_overlap_mm': 2, 'root_round_radius_mm': 1.2,
                     'added_material_mm3': json.loads((R / 'local-candidate-geometry-check.json').read_text())['added_material_mm3'],
                     'physical_contact_fit_load_sharing_stiffness': 'UNQUALIFIED'},
        'retained': {'width_mm': 132, 'clear_finger_opening_mm': 72,
                     'default_physical_device_XYZ_mm': [176.5, 132, 35],
                     'curved_palm_contact_x_mm': -37.25, 'cover_lid_gap_mm': .6,
                     'dynamic_travel_mm': [28, 30], 'setting_limit': 'a+p<=2',
                     'dynamic_limit': 'u+a+p<=30', 'steel_iso_sleeve_mm': 81,
                     'all_122_other_native_BReps': 'EXACT_UNCHANGED_FROM_R8'},
        'validation': {'binding_status': 'FINAL_BOUND', 'report_sha256': digest(R / 'validation/validation.json'),
                       'summary_sha256': digest(R / 'validation/validation-summary.json'),
                       'failed_checks': 0, 'unresolved_checks': 0, 'scope': summary['scope']},
        'portable_source_reconstruction_sha256': digest(R / 'portable-build-check.json'),
        'proof_files': proof, 'package': PACKAGE,
        'physical_500N_qualification': 'PENDING',
        'package_limits': 'Whole native pose ZIPs and complete historical project dependency chain omitted. They remain hash-bound audit inputs in the source project. Source construction builder is portable; complete independent audit reruns require those project dependencies.',
    }
    (R / 'final-specification.json').write_text(json.dumps(spec, indent=2, ensure_ascii=False) + '\n')
    (R / 'README.md').write_text(f'''# Flat132 R9 — palm bracing on the fixed frame

R9 adds **two broad integral compression pads to P02**, bearing on the fixed P01 portal at X−22.75 mm. Each nominal bearing face is **7 × 13 mm (91 mm²)**, at Y−25…−18 and Y18…25 / Z14…27 mm. The pads overlap the old palm root by 2 mm and have explicit R1.2 side and upper root blends. They leave the central keeper/adjuster clear and do not touch the floating P05 yoke, sensor stack or electronics lid.

**Reprint P02 only** for an existing R8 device. The curved wrist contact, keyed mounts, cover, 0.6 mm nominal lid gap, 72 mm finger opening, 28–30 mm stroke and 81 mm steel ISO sleeves remain. Default physical dimensions remain 176.5 × 132 × 35 mm. The two bearing faces share the reaction with the existing palm mounts; actual load sharing depends on printed contact fit and assembly.

**Native regeneration and independent nominal geometry checks pass, with zero failed or unresolved checks.** The STEP contains 123 valid solids: 70 device bodies and 53 electronics references. All 122 other native BReps are exactly unchanged from R8. Independent construction/contact, full-domain dynamic/isometric clearance and unloaded removal checks cover the changed palm. All four whole native pose witnesses are separately exported and source bound. These are CAD geometry checks; printed stiffness, tolerances, creep/fatigue and the 500 N design target remain physically unqualified.

Fit both printed bearing faces without forcing the portal or palm into preload when tightening the two M4 mounting screws. Check full contact, free sensor adjustment and unloaded motion. Keep the existing electronics-lid gap clear. Removal remains vertical after unloading/restraining stored spring energy and removing both M4 palm screws.

The compact package contains 16 raw print STLs, 70 neutral device STLs, two purchased steel-sleeve reference STLs, the native STEP, FeatureScript/builder, provenance, validation records and proof images. Raw STLs retain original assembly coordinates in millimetres; they are not slicer-oriented. Whole native pose ZIPs remain hash-bound project audit inputs and are omitted. The source builder can run from the bundled frozen R8 source; complete independent audit reruns also need the historical source-project dependency chain described in the evidence.

Read [print and assembly notes](PRINT_NOTES.md), [specification](final-specification.json) and [validation](validation/validation-summary.md).

[Interactive viewer](http://127.0.0.1:8777/viewer/viewer.html) · [Frozen R9 Onshape]({url}) · [Native STEP](native/{STEP})

Source SHA-256: `{SOURCE_SHA}`. Frozen R8 and earlier revisions remain unchanged.
''')
    (R / 'PRINT_NOTES.md').write_text('''# R9 print and assembly notes

For an existing R8 device, replace **P02 only**. P02 is a single rigid printable half-round palm, including the electronics-cover ledge and the two new frame-bearing pads. No TPU palm sleeve, added hardware or extra print part is introduced. P070a/P070b/P071a/P071b remain the four separate flexible rear-return pads; the raw CAD package does not prescribe a filament process or infill percentage.

The new flat bearing faces are at X−22.75 mm, Y−25…−18 / Y18…25, Z14…27 mm. They contact **fixed P01**. Keep them flat and free of support scars, seams and debris. Fit the P02 keys and mounts first, then verify that both bearing faces meet the fixed wall without pulling a visibly gapped face into contact by screw force. Adjust printed fit locally if necessary; do not remove the bearing function, force an interference fit or bend the fixed portal. Actual tolerances, insert stock dimensions, screw retention and load sharing require a physical check. No tightening torque or 500 N rating is established.

Keep the central steel keeper, M6 preload wheel/lock and their access clear. The blue P05 floating yoke and sensor/cassette are not palm supports. Keep the nominal 0.6 mm P02-to-P09 electronics-lid gap clear; do not transfer hand load into the lid, PCB, battery or connectors. The curved wrist contact at X−37.25 mm, palm mounts and cover footprint are unchanged.

Retain the R8/R7 manual setup: rear rest adjustment a=0…2 mm and sensor preload p=0…2 mm share a+p≤2 mm; dynamic stroke is 30−a−p mm, retaining 28–30 mm. Measure both rear shoes equally and counterhold the adjusters while locking the jam nuts. Reset the P11 shoe manually to calibration e minus preload after a preload change. The 81 mm Ø16/Ø8 ISO sleeves are purchased steel hardware and must not be printed as load-bearing substitutes.

For palm/case removal, first unload or safely restrain spring energy and positively restrain the carriage. The checked nominal service setup is a=0/p=2. Remove both palm M4 screws and lift the entire palm/case unit vertically by 40 mm; the bearings slide along the fixed wall and have no hooks. On the bench, remove the two enclosure-to-palm M2 screws from below at X−26.5/Y±59 mm, then lower the case/electronics 20 mm. Remove the three lid screws and lift P09 by 15 mm with P02 absent. Disconnect or secure actual wiring before moving modules; cable flexibility, slack and strain relief are not modeled.

The separate H2D/0.4 mm/PLA print job is an **unloaded fit and movement test**. Its printed guide rods, hard pad proxies and Q01 yoke datum fixture are test stand-ins. Do not install springs, apply force or use it to qualify 500 N, preload calibration, switch timing or flexible-pad behavior. Its assembly/checklist and slicer support-removal notes govern that job. The revised P02 is printed wrist-side down to keep its new bearing faces and lid-gap underside away from support interfaces; clean guide, pilot and mounting surfaces before fitting.

Nominal source/native checks do not establish printed stiffness, layer adhesion, creep, fatigue, heat resistance, comfort, sensor calibration or real hardware fits. Raw print STLs use original assembly coordinates; use the Bambu project for the prepared test orientation and settings.
''')
    (R / 'finalization-notes.md').write_text(f'''# R9 evidence and handoff

Immutable Onshape version: `{version}`; source SHA-256 `{SOURCE_SHA}`. The operator-bound native export/provenance record is `onshape-build.json`. The independent `validation/validation-summary.json` and `validation/validation.json` are final bound PASS records with zero failed/unresolved checks.

R9 changes only P02. The exact native symmetric difference for every other one of the 122 solids is zero. The changed whole palm matches the independently constructed union of frozen R8 P02 and eight explicit CSG stocks. Two complete 91 mm² boundary contacts are on fixed P01; dynamic/isometric motion, upward palm removal and case/lid separation are checked over the declared nominal domains. Historical R8 checks are retained by exact scope and are not relabeled as newly executed.

The compact CAD package includes proof images and exact raw native-derived part files. It omits the large complete pose ZIPs; their hashes, export settings and source association remain recorded. The standalone source-builder reconstruction is tested; independent audit replay requires the recorded source-project historical dependencies and original native pose ZIPs. The interactive viewer remains in the source project and displays those whole native configurations without generated/interpolated CAD motion.

No tested force rating or fit guarantee is assigned. In particular, the separate PLA prototype job is unloaded only. Frozen R8 and all earlier production/study records remain unchanged.
''')
    return spec


def build_package(spec):
    primary = ['README.md', 'PRINT_NOTES.md', 'finalization-notes.md', 'final-specification.json',
               SOURCE, BUILDER, 'source-build.json', 'source_brace_geometry.py',
               'local-candidate-geometry-check.json', 'portable-build-check.json',
               'onshape-build.json', 'package_delivery.py', 'native/' + STEP]
    entries = {name: R / name for name in primary}
    for sub in ['print-mm', 'assembly-mm', 'hardware-mm', 'reference', 'validation', 'proof']:
        for path in (R / sub).rglob('*'):
            if path.is_file() and '__pycache__' not in path.parts and path.suffix.lower() != '.zip':
                entries[str(path.relative_to(R))] = path
    assert all(path.is_file() for path in entries.values())
    assert sum(name.startswith('print-mm/') and name.endswith('.stl') for name in entries) == 16
    assert sum(name.startswith('assembly-mm/') and name.endswith('.stl') for name in entries) == 70
    assert sum(name.startswith('hardware-mm/') and name.endswith('.stl') for name in entries) == 2
    assert not any(Path(name).name == 'P03.stl' for name in entries)
    manifest = {'revision': spec['revision'], 'immutable_version_id': spec['onshape']['immutable_version_id'],
                'source_sha256': SOURCE_SHA, 'nominal_validation': 'PASS', 'physical_500N_qualification': 'PENDING',
                'print_STLs': 16, 'device_STLs': 70, 'purchased_ISO_sleeve_reference_STLs': 2,
                'large_pose_ZIPs': 'Omitted; source-bound audit inputs retained in the project.',
                'files': {name: digest(path) for name, path in sorted(entries.items())}}
    delivery = R / 'deliverables'
    delivery.mkdir(exist_ok=True)
    manifest_path = delivery / 'package-manifest.json'
    manifest_path.write_text(json.dumps(manifest, indent=2) + '\n')
    package = R / PACKAGE
    with zipfile.ZipFile(package, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, path in sorted(entries.items()):
            archive.write(path, name)
        archive.write(manifest_path, 'package-manifest.json')
    with zipfile.ZipFile(package) as archive:
        assert archive.testzip() is None
        for name, expected in manifest['files'].items():
            assert sha256(archive.read(name)).hexdigest() == expected, name
    check = {'path': PACKAGE, 'sha256': digest(package), 'bytes': package.stat().st_size,
             'members': len(entries) + 1, 'CRC': 'PASS', 'all_member_SHA256': 'PASS',
             'print_STLs': 16, 'device_STLs': 70, 'ISO_sleeve_reference_STLs': 2}
    (delivery / 'delivery-check.json').write_text(json.dumps(check, indent=2) + '\n')
    return check


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--docs-only', action='store_true')
    args = parser.parse_args()
    build, report, summary = release_inputs()
    refs = prepare_parts(build)
    prepare_reference()
    spec = write_docs(build, report, summary, refs)
    print(json.dumps({'status': 'FINAL_BOUND_DOCS_PREPARED'} if args.docs_only else build_package(spec), indent=2))
