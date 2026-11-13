"""Package the final R9 editable PLA projects, useful STLs, instructions and bound evidence."""
from pathlib import Path
from hashlib import sha256
import json,zipfile
OUT=Path(__file__).resolve().parents[1];ROOT=OUT.parents[1]
def sha(p):return sha256(p.read_bytes()).hexdigest()
layout=json.loads((OUT/'plate-layout.json').read_text());assert not layout['native_R9_version'].startswith('PENDING')
qa=json.loads((OUT/'validation/qa-summary.json').read_text())
assert qa['status'].startswith('PASS') and qa['failed_checks']==qa['unresolved_checks']==0
assert qa['source_sha256']==layout['CAD_source_sha256'] and qa['immutable_version_id']==layout['native_R9_version']
local=json.loads((OUT/'validation/native-project-check.json').read_text());palm=json.loads((OUT/'validation/palm-only-check.json').read_text())
project=OUT/'Fingerworker_R9_H2D_04mm_PLA_Fit_Test.3mf';reprint=OUT/'Fingerworker_R9_P02_wrist_down_H2D_04mm_PLA.3mf'
assert local['native_sha256']==sha(project) and palm['native_project_sha256']==sha(reprint) and palm['full_project_sha256']==sha(project)
cad=json.loads((ROOT/'review/flat132-palm-bracing-2026-10-25/onshape-build.json').read_text())
assert cad['source_sha256']==layout['CAD_source_sha256'] and cad['immutable_version_id']==layout['native_R9_version']
provenance={'scope':'R9 full-scale unloaded fit-test print projects; P02 palm only design change','material_user_confirmed':'PLA','printer':'Bambu H2D','nozzle_mm':0.4,'plate_count':1,'pieces':19,'R9_FeatureScript_sha256':layout['CAD_source_sha256'],'R9_Onshape_version':layout['native_R9_version'],'native_CAD_neutral_export':cad['native_exports']['Flat132_R9_neutral_final.zip'],'native_project_sha256':sha(project),'P02_only_reprint_project_sha256':sha(reprint),'P02_print_orientation':'Native Xmin wrist ledge down; new fixed-frame bearing faces upward','independent_QA_summary_sha256':sha(OUT/'validation/qa-summary.json'),'slicer':'Official Bambu Studio02.08.02.61','official_DMG_sha256':'cf648a95858fb630e1353c4987038df60d6caab693f18411fb95fb809f2d6926','official_download':'https://github.com/bambulab/BambuStudio/releases/download/v02.08.02.61/Bambu_Studio_mac-v02.08.02.61-20260820225108.dmg','official_release':'https://github.com/bambulab/BambuStudio/releases/tag/v02.08.02.61','stock_machine_macros_preserved':True,'local_official_slice_exit_code':0,'internal_full_slice_sha256':local['sliced_internal_evidence_sha256'],'internal_P02_only_slice_sha256':palm['slice_sha256'],'full_estimated_seconds':local['estimated_seconds'],'full_estimated_grams':local['estimated_grams'],'P02_only_estimated_seconds':palm['estimated_seconds'],'P02_only_estimated_grams':palm['estimated_grams'],'no_printer_transmission':True,'no_scaling_remeshing_or_geometry_repair':True,'separate_STL_intent':'STL-print-oriented are rigid transforms only; source-mm retain exact original native STL bytes','limits':'Unloaded fit study; hard PLA P07/rod proxies and Q01 do not qualify functional force measurement or strength.'}
(OUT/'provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
files=[OUT/n for n in ['README.md','FIT_TEST_README.md','ASSEMBLY_DETAILS.md','PRINT_QA_NOTES.md',project.name,reprint.name,'plate-layout.json','Druckliste.json','provenance.json']]
for d in ['STL-print-oriented','source-mm','fixture','profiles','source']:
 files.extend(p for p in (OUT/d).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='build_palm_wrist_down.py')
files.extend(OUT/'preview'/n for n in ['plate_1.png','top_1.png','P02-wrist-down.png'])
files.extend(p for p in (OUT/'validation').glob('*') if p.is_file() and p.suffix in {'.json','.md'} and not p.name.startswith('diagnostic'))
files=sorted(set(files));assert len(list((OUT/'STL-print-oriented').glob('*.stl')))==19
assert all('PETG' not in p.name and '.gcode' not in p.name for p in files)
manifest={str(p.relative_to(OUT)):{'bytes':p.stat().st_size,'sha256':sha(p)} for p in files}
(OUT/'package-manifest.json').write_text(json.dumps({'files':manifest,'scope':'Final wrist-down PLA one-plate and P02-only deliverables; comparison Gcode and runtime are excluded'},indent=2)+'\n');files.append(OUT/'package-manifest.json')
dest=OUT/'Fingerworker_R9_H2D_04mm_PLA_Fit_Test_Package.zip'
with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED) as z:
 for p in files:z.write(p,str(p.relative_to(OUT)))
with zipfile.ZipFile(dest) as z:
 assert z.testzip() is None
 for name,r in manifest.items():assert sha256(z.read(name)).hexdigest()==r['sha256']
check={'status':'FINAL_R9_PLA_PACKAGE_PASS','zip':dest.name,'sha256':sha(dest),'bytes':dest.stat().st_size,'members':len(files),'crc':'PASS','all_member_sha256':'PASS','print_oriented_STLs':19,'raw_source_STLs':19,'editable_full_native_project_sha256':sha(project),'editable_P02_only_project_sha256':sha(reprint),'independent_QA_summary_sha256':provenance['independent_QA_summary_sha256'],'excluded':['Initial orientation diagnostic projects','Local verification Gcode','Temporary runtime app/DMG','CLI logs'],'no_printer_transmission':True}
(OUT/'package-check.json').write_text(json.dumps(check,indent=2)+'\n');print(json.dumps(check,indent=2))
