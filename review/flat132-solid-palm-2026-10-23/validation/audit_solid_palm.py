#!/usr/bin/env python3
"""Focused R6 native audit with exact unchanged-body/source reuse of frozen R5.

This program reads production exports; it does not edit or repair them.
Run with /tmp/fingerworker-sensor-cad-20261022/bin/python.
"""
from __future__ import annotations
import argparse
import copy
import hashlib
import importlib.metadata
import json
from pathlib import Path
import sys
import zipfile
import numpy as np

from OCP.STEPControl import STEPControl_Reader
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_SOLID, TopAbs_SHELL, TopAbs_EDGE
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepBndLib import BRepBndLib
from OCP.Bnd import Bnd_Box
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut, BRepAlgoAPI_Fuse, BRepAlgoAPI_Common
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder
from OCP.BRepFilletAPI import BRepFilletAPI_MakeFillet
from OCP.BRepAdaptor import BRepAdaptor_Curve
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
from OCP.GeomAbs import GeomAbs_Circle
from OCP.TopoDS import TopoDS
from OCP.gp import gp_Pnt, gp_Dir, gp_Ax2

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
PROJECT = STUDY.parents[1]
BASE = PROJECT / 'review/flat132-reach-fit-2026-10-23'
sys.path.insert(0, str(BASE / 'validation'))
import validate_finished as v
from certify_source_scope import main as certify_source

KERNEL_VOLUME_TOL = 1e-6

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def write(path, value):
    v.write(path, value)

def volume(shape):
    props = GProp_GProps()
    BRepGProp.VolumeProperties_s(shape, props)
    return abs(float(props.Mass()))

def count(shape, kind):
    ex = TopExp_Explorer(shape, kind)
    n = 0
    while ex.More():
        n += 1
        ex.Next()
    return n

def bounds(shape):
    box = Bnd_Box()
    BRepBndLib.AddOptimal_s(shape, box, False)
    return np.array([box.CornerMin().Coord(), box.CornerMax().Coord()])

def cut(a, b):
    operation = BRepAlgoAPI_Cut(a, b)
    assert operation.IsDone(), 'BRep cut failed'
    return operation.Shape()

def common(a, b):
    operation = BRepAlgoAPI_Common(a, b)
    assert operation.IsDone(), 'BRep common failed'
    return operation.Shape()

def fuse(a, b):
    operation = BRepAlgoAPI_Fuse(a, b)
    assert operation.IsDone(), 'BRep fuse failed'
    return operation.Shape()

def xor_volume(a, b):
    return volume(cut(a, b)) + volume(cut(b, a))

def box(low, high):
    return BRepPrimAPI_MakeBox(gp_Pnt(*low), gp_Pnt(*high)).Shape()

def gap(a, b):
    distance = BRepExtrema_DistShapeShape(a, b)
    distance.Perform()
    assert distance.IsDone(), 'BRep distance failed'
    return float(distance.Value())

def read_step(path):
    reader = STEPControl_Reader()
    status = str(reader.ReadFile(str(path)))
    assert status.endswith('RetDone'), status
    roots = reader.TransferRoots()
    ex = TopExp_Explorer(reader.OneShape(), TopAbs_SOLID)
    shapes, inventory = [], []
    while ex.More():
        shape = ex.Current()
        inventory.append({'index': len(shapes), 'valid': bool(BRepCheck_Analyzer(shape).IsValid()),
                          'volume_mm3': volume(shape), 'bounds_mm': bounds(shape).tolist(),
                          'shell_count': count(shape, TopAbs_SHELL)})
        shapes.append(shape)
        ex.Next()
    return shapes, inventory, roots

def associate(shapes, inventory, parts):
    result = {}
    for ref, part in sorted(parts.items()):
        mesh = part['mesh']
        candidates = []
        for item, shape in zip(inventory, shapes):
            err = float(np.max(np.abs(mesh.bounds - np.array(item['bounds_mm']))))
            if err > .05:
                continue
            verr = abs(mesh.volume - item['volume_mm3'])
            if verr > max(.1, abs(mesh.volume) * .002):
                props = GProp_GProps()
                error = float(BRepGProp.VolumePropertiesGK_s(shape, props, 1e-7, True, True, False, False))
                refined = abs(float(props.Mass()))
                if error >= 0 and np.isfinite(refined) and refined > 0:
                    item.update(volume_mm3=refined, adaptive_integration_error=error)
                    verr = abs(mesh.volume - refined)
            if verr <= max(.1, abs(mesh.volume) * .002):
                candidates.append({'solid_index': item['index'], 'maximum_bound_error_mm': err,
                                   'volume_error_mm3': float(verr), 'native_brep_valid': item['valid']})
        result[ref] = {'native_stl_member': part['member'], 'native_stl_sha256': part['sha256'],
                       'candidates': candidates,
                       'status': 'PASS' if len(candidates) == 1 and candidates[0]['native_brep_valid'] else 'FAIL'}
    return result

def source_stock():
    # Independent OpenCascade construction of the declared, filled former-cap
    # outer stock. This is not a modification of the exported production body.
    cylinder = BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(-27, -43, 19.75), gp_Dir(0, 1, 0)), 10.25, 86).Shape()
    fillet = BRepFilletAPI_MakeFillet(cylinder)
    ex = TopExp_Explorer(cylinder, TopAbs_EDGE)
    while ex.More():
        edge = TopoDS.Edge(ex.Current())
        if BRepAdaptor_Curve(edge).GetType() == GeomAbs_Circle:
            fillet.Add(1.2, edge)
        ex.Next()
    fillet.Build()
    assert fillet.IsDone(), 'Independent stock end fillet failed'
    return cut(fillet.Shape(), box([-27, -45, 0], [0, 45, 40]))

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--neutral', type=Path, required=True)
    parser.add_argument('--step', type=Path, required=True)
    parser.add_argument('--workspace', required=True)
    parser.add_argument('--max', dest='maximum', type=Path)
    parser.add_argument('--iso', type=Path)
    args = parser.parse_args()
    certify_source()
    certificate_path = HERE / 'source-scope-certificate.json'
    certificate = json.loads(certificate_path.read_text())
    source_sha = certificate['source_sha256']
    m = json.loads((BASE / 'validation/manifest.json').read_text())
    baseline_manifest = copy.deepcopy(m)
    expected = set(m['expected_device_refs']) - {'P03'}
    m['expected_device_refs'] = sorted(expected)
    m['contacts'] = [x for x in m['contacts'] if 'P03' not in x['pair']]
    m['service_sweeps'] = [dict(x, moving_refs=[r for r in x['moving_refs'] if r != 'P03'],
                                **({'fixed_refs': [r for r in x['fixed_refs'] if r != 'P03']} if 'fixed_refs' in x else {}))
                           for x in m['service_sweeps']]
    manifest = {'status': 'ACTUAL_NATIVE_R6_INPUT_MANIFEST',
                'feature_source': str(STUDY / 'fingerworker_flat132_solid_palm.fs'),
                'native_provenance': {'workspace_url': args.workspace, 'feature_source_sha256': source_sha,
                                      'association': 'Root operator verified exact R6 FeatureScript source and regenerated105 parts before these exports. This audit does not regenerate Onshape.'},
                'assembly': str(args.neutral.resolve()), 'native_step': str(args.step.resolve()),
                'expected_device_refs': sorted(expected), 'expected_electronics_count': 53,
                'expected_print_part_count': 14,
                'native_export_files_sha256': {str(p.resolve()): sha(p) for p in (args.neutral, args.step, args.maximum, args.iso) if p},
                'source_scope_certificate': str(certificate_path), 'source_scope_certificate_sha256': sha(certificate_path),
                'baseline_validation_summary': certificate['baseline_validation_summary'],
                'baseline_validation_summary_sha256': certificate['baseline_validation_summary_sha256']}
    if (HERE / 'manifest.json').is_file():
        prior = json.loads((HERE / 'manifest.json').read_text())
        for key in ('immutable_version_id', 'immutable_version_url', 'version_binding_note'):
            if key in prior.get('native_provenance', {}):
                manifest['native_provenance'][key] = prior['native_provenance'][key]
    write(HERE / 'manifest.json', manifest)
    parts, ignored = v.load(args.neutral, m)
    assert not ignored, ignored
    assert set(parts) == expected | {r for r in parts if r.startswith(('E', 'PCB_'))}
    assert len(parts) == 105 and sum(r.startswith(('E', 'PCB_')) for r in parts) == 53
    assert sum(r.startswith('P') and not r.startswith('PCB_') for r in parts) == 14
    invalid = {r: x['error'] for r, x in parts.items() if 'error' in x and r not in v.SPRINGS}
    assert not invalid, invalid
    shapes, inventory, roots = read_step(args.step)
    correspondence = associate(shapes, inventory, parts)
    matches = [x['candidates'][0]['solid_index'] for x in correspondence.values() if x['status'] == 'PASS']
    assert len(shapes) == 105 and len(matches) == len(set(matches)) == 105
    assert all(x['valid'] and x['volume_mm3'] > 0 for x in inventory)
    native = {ref: shapes[item['candidates'][0]['solid_index']] for ref, item in correspondence.items()}
    step_report = {'status': 'PASS', 'scope': 'Complete native STEP validity and unique native-STL bounds/volume association; exact BRep preservation checked separately.',
                   'source_sha256': source_sha, 'native_step': str(args.step.resolve()), 'native_step_sha256': sha(args.step),
                   'native_stl_archive': str(args.neutral.resolve()), 'native_stl_archive_sha256': sha(args.neutral),
                   'transferred_roots': roots, 'native_step_solids': 105, 'native_stl_parts': 105,
                   'expected_device_solids': 52, 'expected_electronics_reference_solids': 53,
                   'valid_positive_solids': 105, 'solid_inventory': inventory,
                   'native_part_correspondence': correspondence}
    write(HERE / 'native-step-inventory.json', step_report)
    print('R6 native STEP/STL inventory:105 valid, uniquely associated', flush=True)
    old_inventory = json.loads((BASE / 'validation/native-step-inventory.json').read_text())
    assert sha(old_inventory['native_step']) == old_inventory['native_step_sha256']
    old_shapes, _, _ = read_step(Path(old_inventory['native_step']))
    old = {r: old_shapes[item['candidates'][0]['solid_index']]
           for r, item in old_inventory['native_part_correspondence'].items()}
    assert set(old) - set(native) == {'P03'} and not set(native) - set(old)
    identity = []
    for ref in sorted(set(native) - {'P02'}):
        error = xor_volume(native[ref], old[ref])
        identity.append({'ref': ref, 'symmetric_difference_mm3': error,
                         'status': 'PASS' if error <= KERNEL_VOLUME_TOL else 'FAIL'})
    write(HERE / 'unchanged-native-breps.json', {'status': 'PASS' if all(x['status'] == 'PASS' for x in identity) else 'FAIL',
          'criterion': 'Exact Boolean symmetric difference of unchanged-coordinate native STEP solids; numerical volume threshold1e-6 mm3. No scaling, translation or shape correction.',
          'baseline_step_sha256': old_inventory['native_step_sha256'], 'native_step_sha256': sha(args.step),
          'expected_unchanged_count': 104, 'checks': identity})
    print('R6 unchanged native BRep checks:', len(identity), flush=True)
    palm = native['P02']
    stock = source_stock()
    expected_palm = fuse(old['P02'], stock)
    difference = xor_volume(palm, expected_palm)
    palm_checks = [
        {'name': 'One valid connected palm solid with one boundary shell', 'status': 'PASS' if count(palm, TopAbs_SOLID) == 1 and count(palm, TopAbs_SHELL) == 1 and BRepCheck_Analyzer(palm).IsValid() else 'FAIL',
         'solid_count': count(palm, TopAbs_SOLID), 'shell_count': count(palm, TopAbs_SHELL), 'meaning': 'One outer boundary shell; no enclosed internal sleeve cavity.'},
        {'name': 'Independent filled-half-cylinder plus original P02 exact CSG', 'symmetric_difference_mm3': difference,
         'status': 'PASS' if difference <= KERNEL_VOLUME_TOL else 'FAIL'},
        {'name': 'Original P02 material and mount structure retained', 'missing_old_palm_volume_mm3': volume(cut(old['P02'], palm)),
         'status': 'PASS' if volume(cut(old['P02'], palm)) <= KERNEL_VOLUME_TOL else 'FAIL'},
        {'name': 'Outer wrist contact and height retained', 'bounds_mm': bounds(palm).tolist(),
         'status': 'PASS' if abs(bounds(palm)[0, 0] + 37.25) <= 1e-5 and abs(bounds(palm)[1, 2] - 30) <= 1e-5 else 'FAIL'},
        {'name': 'Electronics lid nominal gap retained', 'pair': ['P02', 'P09'], 'minimum_gap_mm': gap(palm, native['P09']),
         'status': 'PASS' if abs(gap(palm, native['P09']) - .6) <= 1e-5 else 'FAIL'}]
    # Exact local comparison around existing M4 screw/key and M2 enclosure
    # mounting regions proves the added stock has not plugged their openings.
    regions = [('left M4 and locating key', [-24, -38, 6], [-9, -25, 32]),
               ('right M4 and locating key', [-24, 25, 6], [-9, 38, 32]),
               ('left enclosure insert pilot', [-30, -62, 9], [-23, -56, 15]),
               ('right enclosure insert pilot', [-30, 56, 9], [-23, 62, 15])]
    for name, low, high in regions:
        region = box(low, high)
        err = xor_volume(common(palm, region), common(old['P02'], region))
        palm_checks.append({'name': name + ' exact unchanged local geometry', 'symmetric_difference_mm3': err,
                            'status': 'PASS' if err <= KERNEL_VOLUME_TOL else 'FAIL'})
    for side in (-1, 1):
        low_y, high_y = (-43, -39) if side < 0 else (39, 43)
        probe = box([-26.9, low_y, 14.6], [-24.5, high_y, 30])
        occupied = volume(common(palm, probe))
        palm_checks.append({'name': f'Obsolete front retention return removed, side{side}',
                            'remaining_probe_material_mm3': occupied,
                            'status': 'PASS' if occupied <= KERNEL_VOLUME_TOL else 'FAIL'})
    # Exact STEP pair check for all changed-body interactions, including the
    # designed mount contact. Surface contact is allowed; volume overlap is not.
    exact_pairs = []
    for ref, other in sorted(native.items()):
        if ref == 'P02':
            continue
        if v.separated(bounds(palm), bounds(other)):
            occupied = 0.
        else:
            occupied = volume(common(palm, other))
        exact_pairs.append({'pair': ['P02', ref], 'intersection_volume_mm3': occupied,
                            'status': 'PASS' if occupied <= KERNEL_VOLUME_TOL else 'FAIL'})
    write(HERE / 'palm-exact-audit.json', {'status': 'PASS' if all(x['status'] == 'PASS' for x in palm_checks + exact_pairs) else 'FAIL',
          'source_sha256': source_sha, 'native_step_sha256': sha(args.step),
          'original_palm_volume_mm3': volume(old['P02']), 'new_palm_volume_mm3': volume(palm),
          'checks': palm_checks, 'changed_body_static_pairs': exact_pairs})
    print('R6 exact changed-palm construction, mounts and104 pair checks complete', flush=True)
    # Rerun only changed-palm interactions over the inherited exact R5 domain.
    # Every unaffected interaction is reused by source and104-body identity.
    continuous = []
    for ref in sorted(parts):
        if ref in {'P02'} | v.SPRINGS:
            continue
        rows = v.all_pairs({'P02': parts['P02'], ref: parts[ref]}, m, sweeps=True)
        assert len(rows) == 1
        continuous += rows
    spring_envelopes = v.spring_envelopes({'P02': parts['P02']}, m)
    focused_service = []
    for spec in m['service_sweeps']:
        if 'P02' in spec['moving_refs']:
            focused_service.append(dict(spec, moving_refs=['P02']))
        elif 'P02' in spec.get('fixed_refs', []):
            focused_service.append(dict(spec, fixed_refs=['P02']))
    service = v.service_sweeps(parts, dict(m, service_sweeps=focused_service))
    paths = {'continuous_palm_pairs': continuous, 'continuous_palm_spring_envelopes': spring_envelopes,
             'palm_related_service_paths': service}
    bad_status = {'INTERFERENCE', 'UNCHECKED', 'UNRESOLVED_NEAR_CONTACT', 'FAIL'}
    bad_paths = [x for group in paths.values() for x in group if x['status'] in bad_status]
    write(HERE / 'palm-path-audit.json', {'status': 'PASS' if not bad_paths else 'FAIL',
          'scope': 'Only changed P02 versus unchanged mechanism over full correlated R5 u/p/e domain, conservative spring occupancy and declared service paths. No broad unaffected R5 rerun.',
          'source_sha256': source_sha, 'native_stl_sha256': sha(args.neutral), **paths,
          'failed_or_unresolved_rows': bad_paths})
    print('R6 changed-palm full-domain/service paths complete', flush=True)
    pose_results = []
    neutral_palm_triangle_sha = v.canonical_triangle_sha256(parts['P02']['mesh'])
    for key, path, old_path in [('dynamic28_p2_heavy', args.maximum, BASE / 'native/Flat132_R5_max28_p2_heavy_final.zip'),
                                ('isometric13_p2_81', args.iso, BASE / 'native/Flat132_R5_isometric13_p2_81_final.zip')]:
        if path is None:
            pose_results.append({'pose': key, 'status': 'NOT_PROVIDED', 'scope': 'Final source unchanged-motion certificate remains applicable; no new whole native pose claimed.'})
            continue
        posed, ignored_pose = v.load(path, m)
        old_posed, ignored_old = v.load(old_path, baseline_manifest)
        assert not ignored_pose and not ignored_old
        checks = []
        for ref in sorted(posed):
            first = v.canonical_triangle_sha256(posed[ref]['mesh'])
            second = neutral_palm_triangle_sha if ref == 'P02' else v.canonical_triangle_sha256(old_posed[ref]['mesh'])
            checks.append({'ref': ref, 'canonical_triangle_sha256': first,
                           'comparison_triangle_sha256': second, 'status': 'PASS' if first == second else 'FAIL'})
        sleeve_checks = []
        if key == 'isometric13_p2_81':
            for ref, side in [('H140', -1), ('H141', 1)]:
                mb = posed[ref]['mesh'].bounds
                length = float(mb[1, 0] - mb[0, 0])
                center = mb.mean(axis=0)
                good = (abs(length - 81) <= 1e-5 and abs(mb[0, 0] - 14) <= 1e-5 and
                        abs(mb[1, 0] - 95) <= 1e-5 and abs(center[1] - 51 * side) <= 1e-5 and
                        abs(center[2] - 18) <= 1e-5)
                sleeve_checks.append({'ref': ref, 'description': 'Retained steel isometric sleeve, distinct from removed P03 TPU palm cap',
                                      'length_mm': length, 'bounds_mm': mb.tolist(),
                                      'status': 'PASS' if good else 'FAIL'})
        pose_results.append({'pose': key, 'archive': str(path.resolve()), 'sha256': sha(path),
                             'status': 'PASS' if len(posed) == 105 and 'P03' not in posed and all(x['status'] == 'PASS' for x in checks) else 'FAIL',
                             'part_count': len(posed), 'checks': checks, 'steel_isometric_sleeve_checks': sleeve_checks,
                             'scope': 'Exact native triangle coordinates (only facet/vertex order ignored): changed fixed P02 matches R6 neutral;104 unchanged bodies match equivalent frozen R5 pose. No archive relabeling.'})
        if any(x['status'] != 'PASS' for x in sleeve_checks):
            pose_results[-1]['status'] = 'FAIL'
    write(HERE / 'native-pose-audit.json', {'source_sha256': source_sha, 'poses': pose_results})
    failures = [x for x in identity + palm_checks + exact_pairs if x['status'] != 'PASS'] + bad_paths + [x for x in pose_results if x['status'] == 'FAIL']
    unresolved = [x for x in pose_results if x['status'] == 'NOT_PROVIDED']
    evidence_names = ['manifest.json', 'source-scope-certificate.json', 'native-step-inventory.json',
                      'unchanged-native-breps.json', 'palm-exact-audit.json', 'palm-path-audit.json', 'native-pose-audit.json']
    summary = {'status': 'NOMINAL_GEOMETRY_CHECKS_PASS' if not failures and not unresolved else 'INCOMPLETE_OR_FAILED',
               'scope': 'R6 fixed solid-palm change: exact native body/source comparison and focused construction, clearance, full-domain and service checks; inherited unchanged R5 evidence remains hash-bound.',
               'source_sha256': source_sha, 'native_provenance': manifest['native_provenance'],
               'failed_checks': len(failures), 'unresolved_checks': len(unresolved),
               'native_inventory': {'whole': 105, 'device': 52, 'electronics_reference': 53, 'printed': 14},
               'changed_ref': 'P02', 'removed_ref': 'P03', 'unchanged_exact_brep_count': 104,
               'retained_hardware': 'Both H140/H141 steel16x8x81 mm isometric sleeves remain; these replace springs in ISO mode and are distinct from the removed P03 TPU palm cap.',
               'new_palm_volume_mm3': volume(palm), 'palm_checks': palm_checks,
               'focused_check_counts': {**{k: len(x) for k, x in paths.items()}, 'exact_palm_pairs': len(exact_pairs)},
               'native_poses': [{k: x[k] for k in x if k != 'checks'} for x in pose_results],
               'baseline_reuse': {'source_scope_certificate': str(certificate_path), 'sha256': sha(certificate_path),
                                 'baseline_summary_sha256': certificate['baseline_validation_summary_sha256'],
                                 'meaning': 'Unchanged R5 body pairs,81 mm isometric sleeves and full28–30 mm travel retain prior validation through exact source expressions and104 native BRep identities; P02 checks are newly run.'},
               'evidence_files': {name: sha(HERE / name) for name in evidence_names},
               'failures': failures, 'unresolved': unresolved,
               'limitations': ['500 N remains a design target, not a verified printed working-load rating.',
                   'Solid CAD stock removes the hollow sleeve, but does not prescribe slicer infill or qualify material, print orientation, creep/fatigue or comfort.',
                   'Rigid palm contact loses the previous TPU cap compliance; physical comfort remains unqualified.',
                   'The electronics enclosure/lid, USB/button access and existing insert pilots are retained; the previously discussed9 mm cover extension is not included.',
                   'Heat-set insert stock, actual fasteners, purchased switch calibration/total travel, spring fatigue and final hand fit remain physical prototype checks.',
                   'Native export/source association is root-operator declared and hash-bound; this independent script does not regenerate Onshape.']}
    summary['step_roundtrip_status'] = 'COMPLETE'
    write(HERE / 'validation.json', summary)
    write(HERE / 'validation-summary.json', summary)
    lines = ['# R6 solid-palm validation', '', '**' + summary['status'] + '**', '',
             f'Source `{source_sha}`. Failed checks: {len(failures)}; unresolved checks: {len(unresolved)}.', '',
             'Native inventory:105 valid STEP solids,52 device bodies plus53 electronics references;14 print bodies. P02 is one filled rigid palm, P03 removed.104 surviving bodies are compared directly with the frozen R5 exact STEP.', '',
             'The filled half-cylinder is independently rebuilt and fused to the original P02 for exact Boolean comparison. Existing mount regions, electronics pilots, outer contact position,0.6 mm lid gap, dynamic domain and declared service paths are checked. Unchanged R5 pair checks are reused through the exact source scope certificate rather than relabeled as new native checks.', '',
             '## Limits', '', *['- ' + x for x in summary['limitations']], '']
    (HERE / 'validation-summary.md').write_text('\n'.join(lines))
    print(json.dumps({k: summary[k] for k in ('status', 'failed_checks', 'unresolved_checks', 'unchanged_exact_brep_count')}, indent=2), flush=True)

if __name__ == '__main__':
    main()
