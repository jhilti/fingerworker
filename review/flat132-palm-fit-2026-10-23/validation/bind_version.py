#!/usr/bin/env python3
"""Record the operator-verified immutable Onshape checkpoint after a passed audit.

This updates provenance only; it does not claim to regenerate or query Onshape.
The root operator must verify that the native checkpoint contains this source
and the exported geometry. Geometry evidence is not recomputed or altered.
"""
import argparse
import json
import re
from pathlib import Path
import validate_finished as v

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--version-id',required=True)
p.add_argument('--version-url',required=True)
p.add_argument('--note',required=True)
a=p.parse_args()
assert re.fullmatch('[0-9a-f]{24}',a.version_id)
assert f'/v/{a.version_id}/' in a.version_url
manifest_path=v.HERE/'manifest.json';report_path=v.HERE/'validation.json'
m=json.loads(manifest_path.read_text());r=json.loads(report_path.read_text())
assert r['status']=='NOMINAL_GEOMETRY_CHECKS_PASS' and r['failed_checks']==r['unresolved_checks']==0
assert r['manifest_sha256']==v.sha(manifest_path)
assert v.sha(m['feature_source'])==m['native_provenance']['feature_source_sha256']
m['native_provenance'].update(immutable_version_id=a.version_id,immutable_version_url=a.version_url,version_binding_note=a.note)
v.write(manifest_path,m)
r['manifest']=m;r['manifest_sha256']=v.sha(manifest_path)
r['provenance_metadata_update']='Immutable checkpoint association recorded after unchanged geometry/source audit, based on the root operator native UI verification; no new geometry result inferred.'
v.write(report_path,r)
inventory_path=v.HERE/'native-step-inventory.json';inventory=json.loads(inventory_path.read_text())
assert inventory['status']=='PASS' and inventory['source_sha256']==m['native_provenance']['feature_source_sha256']
inventory['native_provenance']=m['native_provenance'];v.write(inventory_path,inventory)
print(a.version_url)
