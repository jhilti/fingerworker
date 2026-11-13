#!/usr/bin/env python3
"""Hash explicit whole R9 native exports and optional finished validation.

The operator must confirm that the exports were regenerated from this exact
source. File existence alone is not evidence of native provenance.
"""
from pathlib import Path
from hashlib import sha256
import argparse
import json

D = Path(__file__).resolve().parent
P = D.parent


def digest(p):
    return sha256(p.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native-confirmed', action='store_true',
                        help='Operator confirms files were exported from the exact R9 source.')
    parser.add_argument('--version-id')
    parser.add_argument('--validation-ready', action='store_true')
    parser.add_argument('--package-ready', action='store_true')
    args = parser.parse_args()
    c = json.loads((D / 'poses-input.json').read_text())
    source = P / c['feature_source']
    assert digest(source) == c['source_sha256']
    assert args.native_confirmed, 'Explicit native/source export confirmation is required.'
    available = []
    for pose in c['poses']:
        archive = P / pose['archive']
        pose['sha256'] = digest(archive) if archive.is_file() else None
        pose['native_export_source_sha256'] = c['source_sha256']
        if pose['sha256']:
            available.append(pose['id'])
    assert available and available[0] == 'neutral', 'Fresh whole R9 neutral native export required.'
    step = P / c['step']['path']
    c['step']['sha256'] = digest(step) if step.is_file() else None
    c['step']['native_export_source_sha256'] = c['source_sha256']
    c['geometry_origin'] = 'NATIVE_ONSHAPE_REGEN'
    c['geometry_provenance']['native_export_status'] = 'R9_NATIVE_EXPORTED_VALIDATION_PENDING'
    c['geometry_provenance']['native_source_export_association_confirmed_by_operator'] = True
    c['include_available_poses_only'] = len(available) != len(c['poses'])
    if args.version_id:
        c['frozen_version_url'] = ('https://cad.onshape.com/documents/15316cc6370631845af136b2/v/'
                                   + args.version_id + '/e/d253eb87b70818ebde8215f0')
        c['geometry_provenance']['immutable_version_id'] = args.version_id
    if args.validation_ready:
        summary_path = P / 'validation/validation-summary.json'
        report_path = P / 'validation/validation.json'
        summary = json.loads(summary_path.read_text())
        report = json.loads(report_path.read_text())
        for item in [summary, report]:
            assert item['status'] == 'NOMINAL_GEOMETRY_CHECKS_PASS'
            assert item['source_sha256'] == c['source_sha256']
            assert item['failed_checks'] == item['unresolved_checks'] == 0
            assert item['step_roundtrip_status'] == 'COMPLETE'
        assert len(available) == 4 and c['step']['sha256']
        c['validation_sha256'] = digest(report_path)
        c['validation_summary'] = {'path': 'validation/validation-summary.json',
                                   'sha256': digest(summary_path)}
        c['geometry_provenance']['native_export_status'] = 'FINAL_R9_NOMINAL_GEOMETRY_PASS'
        c['palm_bracing']['native_geometry_validation_status'] = 'NOMINAL_GEOMETRY_CHECKS_PASS'
        c['palm_cover']['curved_contact_geometry'] = 'PASS_EXACT_NATIVE_CONTACT_SCOPE_UNCHANGED'
        c['palm_cover']['electronics_cover_service']['status'] = 'PASS_DECLARED_UNLOADED_MODULE_REMOVAL_CASE_DETACH_LID_REMOVAL_PATHS'
        (D / 'review-state.json').write_text(json.dumps({
            'nominal_status': 'NOMINAL_GEOMETRY_CHECKS_PASS',
            'message': 'R9 native bearing, clearance, motion and unloaded removal checks pass. Physical contact fit, stiffness and the 500 N design target remain unqualified.',
        }, indent=2) + '\n')
    if args.package_ready:
        package = P / c['prototype_package']['path']
        assert package.is_file()
        c['prototype_package']['sha256'] = digest(package)
        c['prototype_package']['bytes'] = package.stat().st_size
    (D / 'poses-input.json').write_text(json.dumps(c, indent=2) + '\n')
    print(json.dumps({'available_native_poses': available,
                      'step_present': c['step']['sha256'] is not None,
                      'native_source_sha256': c['source_sha256'],
                      'validation_ready': args.validation_ready}, indent=2))


if __name__ == '__main__':
    main()
