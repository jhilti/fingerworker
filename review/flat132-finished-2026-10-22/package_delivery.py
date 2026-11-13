#!/usr/bin/env python3
"""Package the frozen final CAD and its evidence; never include hand-scan files."""
from pathlib import Path
import hashlib,json,zipfile
HERE=Path(__file__).resolve().parent
DEST=HERE/'deliverables'; DEST.mkdir(exist_ok=True)
report=json.loads((HERE/'validation/validation.json').read_text())
assert report['status']=='NOMINAL_GEOMETRY_CHECKS_PASS'
assert report['step_roundtrip_status']=='COMPLETE'
assert not report['failed_checks'] and not report['unresolved_checks']
expected={
'fingerworker_flat132_finished.fs':'041056629440056626b2f2f88a0db216693e48fff178687174478cb1f34227ef',
'native/Flat132_R1_neutral_final.zip':'f22ebe6f8d2852a31c4345dff9062adc557274f2d94152d9459822a2bdd1683e',
'native/Flat132_R1_max30_p2_heavy_final.zip':'03b3d0c480ffb23aca9a590235d8c9a419d10b51bebcbeb72ef6683e8219ec40',
'native/Flat132_R1_isometric13_p2_final.zip':'6539c0800dffa49279cd5eee74d8d6781ab63f18b6f837fa4b78c0e0a762f37f',
'native/Flat132_R1_final_AP214.step':'6de4383e6423fd1f57bd353d8f42953ecdae841bee1e36b853fb312c679fd7ef'}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
for name,digest in expected.items(): assert sha(HERE/name)==digest,name
files=[HERE/name for name in [*expected,'README.md','finalization-notes.md','final-specification.json','onshape-build.json','source-build.json','native-mount-audit.json','native-mount-audit.md','native-neutral-inventory.json','preserved-baselines.json']]
for sub in ['validation','print-mm','sensor','machining-step','proof']:
    for p in sorted((HERE/sub).rglob('*')):
        if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc': files.append(p)
assert len(list((HERE/'print-mm').glob('*.stl')))==14
assert (HERE/'machining-step/manifest.json').is_file(),'individual STEP extraction not ready'
files=sorted(set(files))
assert all('viewer' not in p.parts and not p.name.startswith('hand') for p in files)
manifest=dict(revision='Flat132 R1',date='2026-10-22',scope='Nominal CAD prototype, not a manufacturing or load qualification',onshape_version_url='https://cad.onshape.com/documents/15316cc6370631845af136b2/v/4c39034c17201905fdfbb1d6/e/d253eb87b70818ebde8215f0',validation_status=report['status'],step_roundtrip_status=report['step_roundtrip_status'],hand_scan_included=False,viewer_included=False,files=[dict(path=str(p.relative_to(HERE)),bytes=p.stat().st_size,sha256=sha(p)) for p in files])
(DEST/'delivery-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
checksum=''.join(f"{x['sha256']}  {x['path']}\n" for x in manifest['files'])
archive=DEST/'Flat132_R1_CAD_Prototype.zip'
with zipfile.ZipFile(archive,'w') as z:
    for p in files:
        z.write(p,str(p.relative_to(HERE)),compress_type=zipfile.ZIP_STORED if p.suffix=='.zip' else zipfile.ZIP_DEFLATED,compresslevel=6)
    z.writestr('delivery-manifest.json',json.dumps(manifest,indent=2)+'\n',compress_type=zipfile.ZIP_DEFLATED)
    z.writestr('SHA256SUMS.txt',checksum,compress_type=zipfile.ZIP_DEFLATED)
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    for item in manifest['files']:
        assert hashlib.sha256(z.read(item['path'])).hexdigest()==item['sha256'],item['path']
result=dict(path=str(archive.relative_to(HERE)),bytes=archive.stat().st_size,sha256=sha(archive),files=len(manifest['files'])+2,crc_and_member_hashes='PASS')
(DEST/'package.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
