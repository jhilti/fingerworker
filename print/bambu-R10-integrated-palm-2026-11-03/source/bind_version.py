"""Bind the unchanged native export to its subsequently frozen Onshape version."""
from pathlib import Path
from hashlib import sha256
import argparse,json
OUT=Path(__file__).resolve().parents[1];ROOT=OUT.parents[1]
p=argparse.ArgumentParser();p.add_argument('version');p.add_argument('--url',required=True);a=p.parse_args()
assert len(a.version)==24 and all(c in '0123456789abcdef' for c in a.version)
layout=json.loads((OUT/'plate-layout.json').read_text())
assert sha256((ROOT/layout['CAD_source_path']).read_bytes()).hexdigest()==layout['CAD_source_sha256']
for r in layout['placements']:assert sha256((ROOT/r['source_path']).read_bytes()).hexdigest()==r['source_sha256']
layout.update(native_R10_version=a.version,native_R10_version_url=a.url)
(OUT/'plate-layout.json').write_text(json.dumps(layout,indent=2)+'\n')
print('PASS: unchanged native mesh/source hashes bound to immutable Onshape version',a.version)
