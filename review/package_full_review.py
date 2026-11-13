#!/usr/bin/env python3
"""Package current reviewed design; leave historical artifacts intact."""
from pathlib import Path
import hashlib,json,zipfile,shutil
R=Path(__file__).resolve().parents[1];K=R/'electronics/kicad'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
verification=json.loads((K/'reports/verification-summary.json').read_text())
assert verification['status'].startswith('PASS')
for n,h in verification['input_sha256'].items():assert sha(K/n)==h,('changed since KiCad check',n)
for n,h in verification['report_sha256'].items():assert sha(K/'reports'/n)==h,('changed report',n)
cad=json.loads((R/'review/onshape-full-review.json').read_text());assert cad['cad_source_sha256']==sha(R/'fingerworker_mvp.fs')
mesh=json.loads((R/'review/full-review-print-validation.json').read_text());assert mesh['cad_source_sha256']==cad['cad_source_sha256']
for part in mesh['parts']:assert sha(R/'print/review-2026-09-21/parts'/part['file'])==part['sha256']
files=set()
for n in ['README.md','FULL_REVIEW.md','fingerworker_mvp.fs','DEVICE_UPGRADES.md','ELECTRONICS_PACKAGING.md','PRINTING.md','EINKAUFSTEILE.md','CAD_REVIEW.md','BLUETOOTH.md'] :files.add(R/n)
for pattern in ['*.kicad_pro','*.kicad_sch','*.kicad_pcb','*.kicad_sym','*.kicad_dru','*.pretty/*.kicad_mod','preview/*.svg','preview/*.png']:
 files.update(K.glob(pattern))
for n in ['sym-lib-table','fp-lib-table','README.md','native_design.json','mechanical-envelopes.json','Fingerworker_RevA.xml','verify_project.py','review_packaging.py'] :files.add(K/n)
for n in ['verification-summary.json','verification-commands.json','erc-full-review.json','drc-full-review.json','full-review-netlist.xml','mechanical-fit-local.json']:files.add(K/'reports'/n)
for n in ['README.md','FIRMWARE_CONTRACT.md','design.json','bom.csv','connections.csv','connectivity.xml','validation.json']:files.add(R/'electronics'/n)
for n in ['onshape-full-review.json','electronics-packaging-validation.json','device-upgrades-validation.json','full-review-print-validation.json','check_electronics_packaging.py','check_device_upgrades.py','check_current_handscan.py','package_review_parts.py','package_full_review.py']:files.add(R/'review'/n)
files.update((R/'review/full-review-2026-09-21').glob('*'))
files.update((R/'print/review-2026-09-21').rglob('*'))
files.update((R/'print').glob('guide_coupon_*.stl'));files.add(R/'print/REVISION_STATUS.md')
files={p for p in files if p.is_file()}
manifest={str(p.relative_to(K)):sha(p) for p in sorted(files) if p.is_relative_to(K)}
(K/'artifact-sha256.json').write_text(json.dumps(manifest,indent=2)+'\n');files.add(K/'artifact-sha256.json')
archive=R/'Fingerworker_FullReview_2026-09-21.zip'
allhash={str(p.relative_to(R)):sha(p) for p in sorted(files)}
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
 for p in sorted(files):z.write(p,str(p.relative_to(R)))
 z.writestr('package-sha256.json',json.dumps(allhash,indent=2)+'\n')
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None
 for n,h in allhash.items():assert hashlib.sha256(z.read(n)).hexdigest()==h,n
print(json.dumps({'archive':str(archive),'entries':len(allhash)+1,'bytes':archive.stat().st_size,'sha256':sha(archive)},indent=2))
