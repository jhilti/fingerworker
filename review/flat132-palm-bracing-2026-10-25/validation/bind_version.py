#!/usr/bin/env python3
"""Bind a root-operator verified immutable Onshape checkpoint; no new geometry claim."""
import argparse
import hashlib
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def write(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--version', required=True)
p.add_argument('--note', required=True)
a = p.parse_args()
assert re.fullmatch('[a-f0-9]{24}', a.version), 'Expected Onshape version ID'
m = json.loads((HERE / 'manifest.json').read_text())
s = json.loads((HERE / 'validation-summary.json').read_text())
assert s['status'] == 'NOMINAL_GEOMETRY_CHECKS_PASS'
assert s['failed_checks'] == s['unresolved_checks'] == 0
assert sha(m['feature_source']) == m['native_provenance']['feature_source_sha256'] == s['source_sha256']
for path, digest in m['native_export_files_sha256'].items():
    assert sha(path) == digest, path
version_url = 'https://cad.onshape.com/documents/15316cc6370631845af136b2/v/' + a.version + '/e/d253eb87b70818ebde8215f0'
provenance = m['native_provenance']
provenance.update(immutable_version_id=a.version, immutable_version_url=version_url, version_binding_note=a.note)
write(HERE / 'manifest.json', m)
s['native_provenance'] = provenance
s['evidence_files']['manifest.json'] = sha(HERE / 'manifest.json')
write(HERE / 'validation.json', s)
write(HERE / 'validation-summary.json', s)
print(json.dumps({'status': s['status'], 'immutable_version_url': version_url,
                  'validation_summary_sha256': sha(HERE / 'validation-summary.json')}))
