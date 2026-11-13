#!/usr/bin/env python3
"""Bind R20 native source,94-body exports and focused locating-fit evidence."""
from pathlib import Path
import importlib.util,json,argparse,re,zipfile,shutil
HERE=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('r20fit',HERE/'audit_locating_pegs.py');v=importlib.util.module_from_spec(s);s.loader.exec_module(v);b=v.b;sha=v.sha

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--native-step',type=Path,required=True);ap.add_argument('--native-archive',type=Path,required=True);args=ap.parse_args()
 source=v.STUDY/'fingerworker_R20_rear_locating_pegs.fs';verpath=v.STUDY/'onshape-version.json';ver=json.loads(verpath.read_text());sourcehash=sha(source);assert sourcehash==ver['source_sha256'] and ver['source_readback_exact'];inputs=[sha(args.native_step),sha(args.native_archive)]
 old,release=v.baseline();gsha=sha(v.STUDY/'mechanics/rear_pegs.py')
 local=json.loads((HERE/'local-locating-fit.json').read_text());assert local['status']=='PASS_LOCAL_R20_LOCATING_FIT' and local['source_sha256']==sourcehash and local['generator_sha256']==gsha and local['validator_sha256']==sha(HERE/'audit_locating_pegs.py')
 with zipfile.ZipFile(args.native_archive) as z:
  overrides={n:'P06'+match[1] for n in z.namelist() if (match:=re.search(r'\bP06([LR])(?=[ _.-])',n))}
 meshes,ignored=v.r.v.load(args.native_archive,{'member_ref_overrides':overrides});assert not ignored,ignored
 shapes,inventory,_=b.read_step(args.native_step);assoc=b.associate(shapes,inventory,meshes);assert all(q['status']=='PASS' for q in assoc.values()),[k for k,q in assoc.items() if q['status']!='PASS']
 parts={ref:shapes[q['candidates'][0]['solid_index']] for ref,q in assoc.items()};assert len(shapes)==len(parts)==94 and set(parts)==set(old)
 oldmeshes,_=v.r.v.load(v.BASE/'native/Flat132_R19_neutral_final.zip',{'member_ref_overrides':{n:'P06'+match[1] for n in zipfile.ZipFile(v.BASE/'native/Flat132_R19_neutral_final.zip').namelist() if (match:=re.search(r'\bP06([LR])(?=[ _.-])',n))}})
 identities=[]
 for ref in sorted(set(parts)-{'P01','P06L','P06R'}):
  comp=v.r.comparison(parts[ref],old[ref]);samebytes=meshes[ref]['sha256']==oldmeshes[ref]['sha256'];sametri=samebytes or v.r.v.canonical_triangle_sha256(meshes[ref]['mesh'])==v.r.v.canonical_triangle_sha256(oldmeshes[ref]['mesh'])
  identities.append(dict(ref=ref,status='PASS' if comp['empty'] and sametri else 'FAIL',stl_byte_identical=samebytes,exact_stl_triangle_identity=sametri,**comp))
 print('UNCHANGED',sum(q['status']=='PASS' for q in identities),len(identities),flush=True)
 fit_path=HERE/'native-fit-step.json';fit=json.loads(fit_path.read_text())
 assert fit['status']=='PASS_NATIVE_R20_STEP_FIT' and fit['source_sha256']==sourcehash and fit['native_step_sha256']==inputs[0]
 assert fit['generator_sha256']==gsha and fit['focused_validator_sha256']==sha(HERE/'audit_locating_pegs.py') and fit['validator_sha256']==sha(HERE/'prepare_native_fit.py')
 assert all(assoc[ref]['candidates'][0]['solid_index']==index for ref,index in fit['native_changed_part_indices'].items())
 rows=fit['checks']
 def ck(name,ok,**details):rows.append(dict(name=name,status='PASS' if bool(ok) else 'FAIL',**details))
 for ref in ['P01','P06L','P06R']:
  mesh=meshes[ref]['mesh'];ck('Native changed-part mesh is one closed positive volume '+ref,mesh.is_watertight and mesh.is_volume and meshes[ref].get('connected_solid_count')==1,native_stl_sha256=meshes[ref]['sha256'],triangle_count=len(mesh.faces),components=meshes[ref].get('connected_solid_count'),mesh_error=meshes[ref].get('error'))
 assert sourcehash==sha(source) and gsha==sha(v.STUDY/'mechanics/rear_pegs.py') and inputs==[sha(args.native_step),sha(args.native_archive)]
 failed=[q for q in rows+identities if q['status']!='PASS']
 inv=dict(native_step=str(args.native_step.resolve()),native_step_sha256=inputs[0],native_part_correspondence=assoc,solid_inventory=inventory);(HERE/'native-step-inventory.json').write_text(json.dumps(inv,indent=2)+'\n')
 report=dict(status='PASS_NATIVE_R20_LOCATING_FIT' if not failed else 'FAIL_NATIVE_R20_LOCATING_FIT',source_sha256=sourcehash,version_id=ver['version_id'],native_step_sha256=inputs[0],native_zip_sha256=inputs[1],baseline_native_step_sha256=release['native_step_sha256'],baseline_release_binding_sha256=sha(v.BASE/'validation/native-release-binding.json'),generator_sha256=gsha,validator_sha256=sha(__file__),focused_validator_sha256=sha(HERE/'audit_locating_pegs.py'),local_fit_report_sha256=sha(HERE/'local-locating-fit.json'),native_step_fit_report_sha256=sha(fit_path),native_parts=94,checks=rows,unchanged_native_bodies=identities,failures=failed,print_setup_status='PRINT_SETUP_DEFERRED_BY_USER',limitations=['Clearance-fit locator geometry only; physical PLA tolerances, strength and durability remain unqualified.','The rear-open slots do not positively retain the blocks rearward. Screwless fitting requires springs removed/unloaded; all four M3 screws are required before spring preload or any external loading.','Current print orientations and Bambu projects are unchanged. The new underside pegs require orientation review when printing is requested.'])
 (HERE/'native-locating-fit.json').write_text(json.dumps(report,indent=2)+'\n')
 if failed:
  print(json.dumps(dict(status=report['status'],checks=len(rows),unchanged=len(identities),failures=failed),indent=2));return 1
 assert len(identities)==91 and ver['native_parts']==94 and ver['step_sha256']==inputs[0] and ver['stl_zip_sha256']==inputs[1]
 ver['status']='PASS_NATIVE_REGENERATION_AND_EXPORT_AUDITS';verpath.write_text(json.dumps(ver,indent=2)+'\n');snapshot=HERE/'onshape-version-at-validation.json';shutil.copyfile(verpath,snapshot)
 reports={}
 for name in ['native-locating-fit.json','native-fit-step.json','local-locating-fit.json']:
  path=HERE/name;d=json.loads(path.read_text());reports[name]=dict(path=str(path),status=d['status'],sha256=sha(path))
 stls={ref:dict(member=meshes[ref]['member'],sha256=meshes[ref]['sha256']) for ref in ['P01','P06L','P06R']}
 binding=dict(status='PASS_NATIVE_R20_SOURCE_EXPORT_REPORT_BINDING',version_id=ver['version_id'],version_url=ver['url'],source_sha256=sourcehash,native_step_sha256=inputs[0],native_zip_sha256=inputs[1],native_P01_stl_sha256=stls['P01']['sha256'],native_changed_stls=stls,native_parts=94,unchanged_native_bodies=91,source_readback_exact=True,native_version_snapshot=dict(path=str(snapshot),sha256=sha(snapshot)),reports=reports,native_inventory_sha256=sha(HERE/'native-step-inventory.json'),baseline_native_release_binding_sha256=sha(v.BASE/'validation/native-release-binding.json'),validator_sha256=sha(__file__),print_setup_status='PRINT_SETUP_DEFERRED_BY_USER',scope='Native CAD/source/export and nominal assembly proof only. No print setup, slicing or machine readiness is claimed. Rear-open locators preserve rod assembly but do not replace mandatory screws for spring-loaded operation.')
 (HERE/'native-release-binding.json').write_text(json.dumps(binding,indent=2)+'\n');print(json.dumps(dict(status=report['status'],checks=len(rows),unchanged=len(identities),binding_sha256=sha(HERE/'native-release-binding.json')),indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
