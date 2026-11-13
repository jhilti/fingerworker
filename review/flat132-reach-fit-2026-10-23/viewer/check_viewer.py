#!/usr/bin/env python3
"""Check viewer syntax and supplied-source binding; no CAD or browser QA claim."""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

D = Path(__file__).resolve().parent
P = D.parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--template-only', action='store_true')
    args = parser.parse_args()
    tree = ast.parse((D / 'build_viewer.py').read_text())
    template = next(n.value.value for n in tree.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'TEMPLATE' for t in n.targets))
    if args.template_only:
        html = template.replace('__DATA__', '[]').replace('__META__', '{}')
        report = {'status': 'TEMPLATE_SYNTAX_ONLY_INPUTS_PENDING', 'cad_qa': 'NOT_PERFORMED', 'browser_qa': 'NOT_PERFORMED'}
    else:
        html = (D / 'viewer.html').read_text()
        config = json.loads((D / 'poses-input.json').read_text())
        manifest = json.loads((D / 'viewer-build.json').read_text())
        assert manifest['viewer_sha256'] == sha(D / 'viewer.html')
        assert manifest['source_sha256'] == config['source_sha256'] == sha(P / config['feature_source'])
        for pose in manifest['poses']:
            assert sha(P / pose['archive']) == pose['sha256']
            assert len([r for r in pose['rows'] if r['group'] != 'hand']) == config['native_device_parts']
        assert manifest['switch_fit']['part_number'] == 'SS-01GL2'
        assert 'not factory STEP' in manifest['switch_fit']['source']
        assert manifest['switch_fit']['actual_TE_force_sensor_retained'] is True
        if manifest['geometry_origin'] == 'LOCAL_CSG_STUDY_NOT_NATIVE_REGEN':
            assert manifest['review_state']['nominal_status'] != 'NOMINAL_GEOMETRY_CHECKS_PASS'
            assert manifest['validation'] is None
            assert manifest['frozen_onshape_version'] is None
            assert 'Local CSG study' in html and 'Onshape regeneration pending' in html
        report = {'status': 'STATIC_SYNTAX_AND_SOURCE_BINDING_PASS', 'viewer_sha256': manifest['viewer_sha256'], 'source_sha256': manifest['source_sha256'], 'geometry_origin': manifest['geometry_origin'], 'poses': [{'id': p['id'], 'archive_sha256': p['sha256'], 'device_parts': len(p['rows']) - 1} for p in manifest['poses']], 'cad_qa': manifest['review_state'], 'browser_qa': 'PENDING_PARENT_UI_QA', 'switch_geometry': manifest['switch_fit'], 'step': manifest['step'], 'package_ready': manifest['package_ready']}
    script = html.rsplit('<script>', 1)[1].split('</script>', 1)[0]
    node = shutil.which('node')
    if not node:
        raise RuntimeError('Node is required for an actual JavaScript syntax check')
    with tempfile.TemporaryDirectory(prefix='flat132-r5-viewer-check-') as temp:
        path = Path(temp) / 'viewer.js'
        path.write_text(script)
        subprocess.run([node, '--check', str(path)], check=True, capture_output=True, text=True)
    report['javascript_syntax'] = 'NODE_CHECK_PASS'
    (D / 'viewer-static-validation.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
