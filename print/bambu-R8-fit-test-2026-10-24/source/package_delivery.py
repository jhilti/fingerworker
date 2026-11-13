"""Package only the final editable PLA project, useful STLs, instructions and evidence."""
from pathlib import Path
from hashlib import sha256
import json,zipfile
OUT=Path(__file__).resolve().parents[1]
def sha(p):return sha256(p.read_bytes()).hexdigest()
qa=json.loads((OUT/'validation/qa-summary.json').read_text())
provenance={'scope':'R8 full-scale unloaded fit-test print project','material_user_confirmed':'PLA','printer':'Bambu H2D','nozzle_mm':0.4,'plate_count':1,'pieces':19,'frozen_R8_FeatureScript_sha256':'6099df42e341ff9f5c3439709a23107325d10ef922f616bdcda6fa6ef64d41c1','frozen_R8_Onshape_version':'6965afcca3af7c58ef3ac73f','native_project_sha256':sha(OUT/'Fingerworker_R8_H2D_04mm_PLA_Fit_Test.3mf'),'independent_QA_summary_sha256':sha(OUT/'validation/qa-summary.json'),'slicer':'Official Bambu Studio02.08.02.61','official_DMG_sha256':'cf648a95858fb630e1353c4987038df60d6caab693f18411fb95fb809f2d6926','official_download':'https://github.com/bambulab/BambuStudio/releases/download/v02.08.02.61/Bambu_Studio_mac-v02.08.02.61-20260820225108.dmg','official_release':'https://github.com/bambulab/BambuStudio/releases/tag/v02.08.02.61','stock_machine_macros_preserved':True,'local_official_slice_exit_code':0,'internal_slice_sha256':sha(OUT/'validation/Fingerworker_R8_slice_verification.gcode.3mf'),'estimated_seconds':65001,'estimated_grams':268.96,'no_printer_transmission':True,'no_scaling_remeshing_or_geometry_repair':True,'separate_STL_intent':'STL-print-oriented are rigid transforms only; source-mm retain exact original native STL bytes','limits':'Unloaded fit study; hard PLA P07/rod proxies and Q01 do not qualify functional force measurement or strength.'}
(OUT/'provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
files=[OUT/n for n in ['README.md','FIT_TEST_README.md','ASSEMBLY_DETAILS.md','PRINT_QA_NOTES.md','Fingerworker_R8_H2D_04mm_PLA_Fit_Test.3mf','plate-layout.json','Druckliste.json','provenance.json']]
for d in ['STL-print-oriented','source-mm','fixture','profiles','source','preview']:
 files.extend(p for p in (OUT/d).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
files.extend(OUT/'validation'/n for n in ['native-project-check.json','qa-summary.json','qa-summary.md','qa-project.json','qa-toolpaths.json','qa-q01-fixture.json'])
files=sorted(set(files))
assert len(list((OUT/'STL-print-oriented').glob('*.stl')))==19
assert all('PETG' not in p.name and '.gcode' not in p.name for p in files)
manifest={str(p.relative_to(OUT)):{'bytes':p.stat().st_size,'sha256':sha(p)} for p in files}
(OUT/'package-manifest.json').write_text(json.dumps({'files':manifest,'scope':'Final PLA one-plate deliverable only; local slice and runtime are excluded'},indent=2)+'\n');files.append(OUT/'package-manifest.json')
dest=OUT/'Fingerworker_R8_H2D_04mm_PLA_Fit_Test_Package.zip'
with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED) as z:
 for p in files:z.write(p,str(p.relative_to(OUT)))
with zipfile.ZipFile(dest) as z:
 assert z.testzip() is None
 for name,r in manifest.items():assert sha256(z.read(name)).hexdigest()==r['sha256']
check={'status':'FINAL_PLA_PACKAGE_PASS','zip':dest.name,'sha256':sha(dest),'bytes':dest.stat().st_size,'members':len(files),'crc':'PASS','all_member_sha256':'PASS','print_oriented_STLs':19,'raw_source_STLs':19,'editable_native_project_sha256':provenance['native_project_sha256'],'independent_QA_summary_sha256':provenance['independent_QA_summary_sha256'],'excluded':['PETG diagnostic artifacts','local verification Gcode','temporary runtime app/DMG','CLI logs'],'no_printer_transmission':True}
(OUT/'package-check.json').write_text(json.dumps(check,indent=2)+'\n');print(json.dumps(check,indent=2))
