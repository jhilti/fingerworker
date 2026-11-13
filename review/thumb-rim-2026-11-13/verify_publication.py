#!/usr/bin/env python3
"""Final bounded R19 entrypoint/hash check after publication."""
from pathlib import Path
import json,hashlib
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text())
s=read(HERE/'final-specification.json');d=read(HERE/'documentation-ready.json')
assert sha(ROOT/'fingerworker_mvp.fs')==s['source_sha256']==d['source_sha256']
for owner in [s,d]:
 for p,h in owner['files_sha256'].items():assert sha(ROOT/p)==h,p
rows=[]
for name in ['README.md','PRINTING.md','EINKAUFSTEILE.md','DEVICE_UPGRADES.md','print/REVISION_STATUS.md']:
 p=ROOT/name;text=p.read_text();a=text.index('<!-- CURRENT_FLAT132_R19_START -->');b=text.index('<!-- CURRENT_FLAT132_R19_END -->')
 assert a<b and 'P06L' in text[a:b] and 'P06R' in text[a:b]
 if '<!-- CONNECTED_R15_READY_START -->' in text:assert a<text.index('<!-- CONNECTED_R15_READY_START -->')
 if 'Historischer Stand R15' in text:assert 'Historischer Stand R15 – für R19 den CAD-Stand oben beachten; Druckvorbereitung zurückgestellt' in text
 rows.append(dict(file=name,sha256=sha(p),current_marker_first=True))
static=read(ROOT/'overview/static-validation.json');model=read(ROOT/'overview/model/validation.json');manifest=read(ROOT/'overview/model/manifest.json')
assert static['status']=='PASS_STATIC_OVERVIEW' and static['revision']=='R19' and static['html_sha256']==sha(ROOT/'Uebersicht.html')
assert model['status']=='PASS_STATIC_GEOMETRY_AND_EMBEDDING' and model['unique_bodies']==94
assert manifest['source_sha256']==s['source_sha256'] and manifest['binding_status']=='BOUND_TO_RELEASED_R19'
result=dict(status='PASS_PUBLISHED_R19_ENTRYPOINTS',source_sha256=s['source_sha256'],onshape_version=s['onshape_version'],root_source_sha256=sha(ROOT/'fingerworker_mvp.fs'),html_sha256=sha(ROOT/'Uebersicht.html'),final_specification_sha256=sha(HERE/'final-specification.json'),documentation_binding_sha256=sha(HERE/'documentation-ready.json'),model_manifest_sha256=sha(ROOT/'overview/model/manifest.json'),static_validation_sha256=sha(ROOT/'overview/static-validation.json'),root_documents=rows,all_release_file_hashes_valid=True,native_display_bodies=94,gui_verified=s['gui_verified'],gui_status=s['gui_status'])
(HERE/'published-entrypoints-check.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
