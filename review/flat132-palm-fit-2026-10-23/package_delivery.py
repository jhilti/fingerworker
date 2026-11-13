#!/usr/bin/env python3
"""Build the complete R3 palm fit print set from verified native geometry."""
from pathlib import Path
import json,hashlib,zipfile
R=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report=json.loads((R/'validation/validation.json').read_text())
assert report.get('status')=='NOMINAL_GEOMETRY_CHECKS_PASS', report.get('status')
files=[R/x for x in ['README.md','PRINT_NOTES.md','PACKAGE_CONTENTS.txt','final-specification.json','fingerworker_flat132_palm_fit.fs','source-build.json','onshape-build.json','native/Flat132_R3_final_AP214.step','package_delivery.py']]
for sub in ['print-mm','sensor','validation','proof']:
 files += [p for p in (R/sub).rglob('*') if p.is_file() and '__pycache__' not in p.parts]
assert all(p.is_file() for p in files)
files=sorted(set(files))
manifest={'revision':'Flat132 R3','purpose':'Full 14-part print set; P02/P03 half-round palm update; unsliced CAD prototype','source_sha256':sha(R/'fingerworker_flat132_palm_fit.fs'),'native_step_sha256':sha(R/'native/Flat132_R3_final_AP214.step'),'nominal_validation':'PASS','physical_500N_qualification':'PENDING','files':{str(p.relative_to(R)):sha(p) for p in files}}
D=R/'deliverables';D.mkdir(exist_ok=True)
M=D/'package-manifest.json';M.write_text(json.dumps(manifest,indent=2)+'\n')
Z=D/'Flat132_R3_Palm_Fit.zip'
with zipfile.ZipFile(Z,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for p in files:z.write(p,str(p.relative_to(R)))
 z.write(M,'package-manifest.json')
with zipfile.ZipFile(Z) as z:
 assert z.testzip() is None
 for n,h in manifest['files'].items():assert hashlib.sha256(z.read(n)).hexdigest()==h,n
assert len([p for p in files if str(p.relative_to(R)).startswith('print-mm/') and p.suffix=='.stl'])==14
record={'path':str(Z.relative_to(R)),'sha256':sha(Z),'bytes':Z.stat().st_size,'members':len(files)+1,'crc_check':'PASS','member_sha256_checks':'PASS'}
(D/'delivery-check.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record,indent=2))
