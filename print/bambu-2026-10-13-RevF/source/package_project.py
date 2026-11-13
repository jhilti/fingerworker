"""Make the self-contained H2D delivery ZIP after native-project validation."""
from pathlib import Path
import json,hashlib,zipfile
ROOT=Path(__file__).resolve().parents[3]
PACKAGE=ROOT/'print/Fingerworker_H2D_PETG_RevF_2026-10-13'
ARCHIVE=PACKAGE.with_suffix('.zip')
report=json.loads((PACKAGE/'validation.json').read_text())
assert report['status']=='PASS'
assert hashlib.sha256((PACKAGE/report['native_project']).read_bytes()).hexdigest()==report['native_sha256']
rows=json.loads((PACKAGE/'Druckliste.json').read_text())
assert len(rows)==25 and sum(r['quantity'] for r in rows)==30
assert len(list((PACKAGE/'PETG').glob('*.stl')))==25
for r in rows:
    assert r['material']=='PETG'
    assert hashlib.sha256((PACKAGE/r['file']).read_bytes()).hexdigest()==r['sha256']
for name in ['guide_coupon_male.stl','guide_coupon_female.stl']:
    assert (PACKAGE/name).read_bytes()==(ROOT/'print'/name).read_bytes()
manifest={str(p.relative_to(PACKAGE)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(PACKAGE.rglob('*')) if p.is_file() and p.name!='SHA256.json'}
(PACKAGE/'SHA256.json').write_text(json.dumps(manifest,indent=2)+'\n')
with zipfile.ZipFile(ARCHIVE,'w',zipfile.ZIP_DEFLATED) as z:
    for p in sorted(PACKAGE.rglob('*')):
        if p.is_file():z.write(p,Path(PACKAGE.name)/p.relative_to(PACKAGE))
with zipfile.ZipFile(ARCHIVE) as z:
    assert z.testzip() is None
    assert len([n for n in z.namelist() if n.endswith('.3mf')])==1
    assert len([n for n in z.namelist() if n.endswith('.stl')])==27
print('PASS: self-contained ZIP, 1 native 3MF, 25 device STL types + 2 coupons, instructions and verified SHA-256 manifest')
print(ARCHIVE)
