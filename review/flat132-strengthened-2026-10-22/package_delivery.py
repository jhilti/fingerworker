#!/usr/bin/env python3
"""Build the compact R2 print update from verified native geometry."""
from pathlib import Path
import json,hashlib,zipfile
R=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report=json.loads((R/'validation/validation.json').read_text())
assert report.get('status')=='NOMINAL_GEOMETRY_CHECKS_PASS', report.get('status')
files=[R/x for x in ['README.md','PRINT_NOTES.md','PACKAGE_CONTENTS.txt','final-specification.json','fingerworker_flat132_strengthened.fs','source-build.json','onshape-build.json','source-ui-guard-only-certificate.json','loadpath-review.md','loadpath-review.json','native/Flat132_R2_final_AP214.step','package_delivery.py']]
for sub in ['print-mm','sensor','validation','proof']:
 files += [p for p in (R/sub).rglob('*') if p.is_file() and '__pycache__' not in p.parts]
assert all(p.is_file() for p in files)
files=sorted(set(files))
manifest={'revision':'Flat132 R2','purpose':'Matched P01/P05 printed reinforcement update; unsliced CAD prototype','source_sha256':sha(R/'fingerworker_flat132_strengthened.fs'),'native_step_sha256':sha(R/'native/Flat132_R2_final_AP214.step'),'nominal_validation':'PASS','physical_500N_qualification':'PENDING','files':{str(p.relative_to(R)):sha(p) for p in files}}
D=R/'deliverables';D.mkdir(exist_ok=True)
M=D/'package-manifest.json';M.write_text(json.dumps(manifest,indent=2)+'\n')
Z=D/'Flat132_R2_Printed_Reinforcement.zip'
with zipfile.ZipFile(Z,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for p in files:z.write(p,str(p.relative_to(R)))
 z.write(M,'package-manifest.json')
with zipfile.ZipFile(Z) as z:
 assert z.testzip() is None
 for n,h in manifest['files'].items():assert hashlib.sha256(z.read(n)).hexdigest()==h,n
assert len([p for p in files if str(p.relative_to(R)).startswith('print-mm/') and p.suffix=='.stl'])==2
record={'path':str(Z.relative_to(R)),'sha256':sha(Z),'bytes':Z.stat().st_size,'members':len(files)+1,'crc_check':'PASS','member_sha256_checks':'PASS'}
(D/'delivery-check.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record,indent=2))
