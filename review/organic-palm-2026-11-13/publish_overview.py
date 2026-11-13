#!/usr/bin/env python3
"""Publish the already verified staged R18 offline overview after explicit release GO."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];STAGE=HERE/'overview-staging';OUT=ROOT/'overview'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text())
spec=read(HERE/'final-specification.json');assert spec['status'].startswith('PASS')
assert sha(ROOT/'fingerworker_mvp.fs')==spec['source_sha256']
assert read(STAGE/'static-validation.json')['status']=='PASS_STATIC_OVERVIEW'
assert read(STAGE/'model/validation.json')['status']=='PASS_STATIC_GEOMETRY_AND_EMBEDDING'
assert read(STAGE/'model/manifest.json')['binding_status']=='BOUND_TO_RELEASED_R18'
for folder,names in [('', ['build_overview.py','template.html','style.css','app.js','content.json','validate_static.py']),('model',['build_model.py','assemble_component.py','validate_model.py','component-template.html','viewer.js','viewer.css','model-data.b64','manifest.json','component.html','test.html'])]:
 for name in names:
  p=STAGE/folder/name
  if p.is_file():shutil.copyfile(p,OUT/folder/name)
for script in [OUT/'model/validate_model.py',OUT/'build_overview.py',OUT/'validate_static.py']:
 subprocess.run([sys.executable,str(script)],check=True,cwd=ROOT)
result=dict(status='PASS_PUBLISHED_R18_OVERVIEW',source_sha256=spec['source_sha256'],onshape_version=spec['onshape_version'],html_sha256=sha(ROOT/'Uebersicht.html'),model_manifest_sha256=sha(OUT/'model/manifest.json'),static_validation_sha256=sha(OUT/'static-validation.json'),source_file_sha256=sha(__file__))
(HERE/'overview-published.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
