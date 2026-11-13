#!/usr/bin/env python3
"""Validate the final embedded display payload; no browser or network required."""
from pathlib import Path
import base64,gzip,hashlib,json,re,struct,zipfile

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((HERE/'manifest.json').read_text())
spec=json.loads((ROOT/'review/inboard-straps-2026-11-08/final-specification.json').read_text())
assert m['revision']=='R15' and m['source_sha256']==spec['source_sha256']
archive=ROOT/m['source'];assert sha(archive)==m['native_zip_sha256']
packed=base64.b64decode((HERE/'model-data.b64').read_text())
assert hashlib.sha256(packed).hexdigest()==m['data_sha256']
parts=json.loads(gzip.decompress(packed));ids=[p['id'] for p in parts]
assert len(ids)==len(set(ids))==spec['native_solids']==93
manifest={p['id']:p for p in m['parts']};checks=[]
with zipfile.ZipFile(archive) as z:
 for p in parts:
  native=manifest[p['id']]
  assert hashlib.sha256(z.read(native['native_member'])).hexdigest()==native['native_stl_sha256']
  vertices=base64.b64decode(p['v']);normals=base64.b64decode(p['n']);indices=base64.b64decode(p['f'])
  assert len(vertices)%6==0 and len(normals)==len(vertices)//2 and len(indices)%6==0
  nv=len(vertices)//6;nf=len(indices)//6;ii=struct.unpack('<'+'H'*(len(indices)//2),indices)
  assert min(ii)>=0 and max(ii)<nv and p['count']==len(ii)
  assert nv==native['display_vertices'] and nf==native['display_triangles']
  checks.append(dict(id=p['id'],vertices=nv,triangles=nf,indices_in_range=True,native_hash_verified=True))
counts={g:sum(p['group']==g for p in parts) for g in ['print','metal','buy','electronics']}
assert counts==m['counts'] and counts['print']==7 and counts['buy']==6 and counts['electronics']==53 and counts['metal']==27
component=(HERE/'component.html').read_text()
assert (HERE/'model-data.b64').read_text() in component
assert not re.search(r'%%[A-Z_]+%%',component)
assert not re.search(r'<(?:script|link)[^>]+(?:src|href)=["\']https?://',component)
result=dict(status='PASS_STATIC_GEOMETRY_AND_EMBEDDING',revision='R15',unique_bodies=len(parts),counts=counts,
 native_triangles=m['native_triangle_count'],display_triangles=m['display_triangle_count'],component_bytes=len(component.encode()),
 component_sha256=sha(HERE/'component.html'),all_assets_inline=True,external_runtime_assets=0,
 browser_visual_QA='Pending final HTML browser review',checks=checks)
(HERE/'validation.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:result[k] for k in ['status','unique_bodies','counts','component_bytes']},indent=2))
