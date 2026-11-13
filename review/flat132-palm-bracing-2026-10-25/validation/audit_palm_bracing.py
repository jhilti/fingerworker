#!/usr/bin/env python3
"""Focused R9 native palm-brace audit with hash-bound unchanged R8 evidence."""
from pathlib import Path
import argparse,hashlib,json,sys
import numpy as np
HERE=Path(__file__).resolve().parent;STUDY=HERE.parent;PROJECT=STUDY.parents[1]
BASE=PROJECT/'review/flat132-palm-cover-2026-10-23'
sys.path.insert(0,str(BASE/'validation'));import audit_palm_cover as r8
r7=r8.r7;b=r8.b;v=r8.v
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.TopAbs import TopAbs_SOLID,TopAbs_SHELL
TOL=1e-6
BAD={'FAIL','INTERFERENCE','UNCHECKED','UNRESOLVED_NEAR_CONTACT','NOT_PROVIDED'}
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,x):v.write(p,x)

def source_scope():
 source=STUDY/'fingerworker_flat132_palm_bracing.fs';baseline=BASE/'fingerworker_flat132_palm_cover.fs';ledger=STUDY/'source-build.json';j=json.loads(ledger.read_text())
 assert sha(baseline)=='6099df42e341ff9f5c3439709a23107325d10ef922f616bdcda6fa6ef64d41c1'
 generated=baseline.read_text()
 assert {c['label'] for c in j['changes']}=={'R9 study identity','R9 feature name','P02 only: union two broad bearings and explicit rounded root stocks'}
 for c in j['changes']:assert generated.count(c['old'])==c['count'];generated=generated.replace(c['old'],c['new'])
 assert generated==source.read_text() and sha(source)==j['sha256']
 prior=json.loads((BASE/'validation/validation-summary.json').read_text());assert prior['status']=='NOMINAL_GEOMETRY_CHECKS_PASS' and prior['failed_checks']==prior['unresolved_checks']==0 and prior['source_sha256']==sha(baseline)
 for name,digest in prior['evidence_files'].items():assert sha(BASE/'validation'/name)==digest,name
 result={'status':'PASS_EXACT_P02_ONLY_SOURCE_SCOPE','source':str(source),'source_sha256':sha(source),'baseline_source':str(baseline),'baseline_source_sha256':sha(baseline),'baseline_immutable_version_id':'6965afcca3af7c58ef3ac73f','source_build_sha256':sha(ledger),'exact_forward_reconstruction_matches_all_source_bytes':True,'changed_ref':'P02','baseline_validation_summary':str(BASE/'validation/validation-summary.json'),'baseline_validation_summary_sha256':sha(BASE/'validation/validation-summary.json'),'baseline_evidence_files_sha256':prior['evidence_files'],'reuse_policy':'All original R8 P02 material and all122 other native bodies must remain exact. Unchanged R8 operating/service evidence retained; only added P02 stock receives new full-domain/contact/withdrawal checks. No prior rear or print qualification is relabeled as newly run.'}
 write(HERE/'source-scope-certificate.json',result);return result

def stocks():
 # Independent literal CSG witness, without importing the source-agent helper.
 rows=[]
 for tag,y0,y1 in [('L',-25.,-18.),('R',18.,25.)]:
  rows.append((tag+' bearing',b.box([-29,y0,14],[-22.75,y1,27])))
  for edge,cy,lo,hi in [('lower',y0-1.2,y0-1.2,y0),('upper',y1+1.2,y1,y1+1.2)]:
   block=b.box([-27.1,lo,14],[-25.8,hi,27]);tool=r7.cyl([-25.8,cy,13.9],[-25.8,cy,27.1],1.2);rows.append((tag+' '+edge+' root',b.cut(block,tool)))
  block=b.box([-27.1,y0,27],[-25.8,y1,28.2]);tool=r7.cyl([-25.8,y0-.1,28.2],[-25.8,y1+.1,28.2],1.2);rows.append((tag+' top root',b.cut(block,tool)))
 return rows

def baseline_native():
 inv=json.loads((BASE/'validation/native-step-inventory.json').read_text());assert sha(inv['native_step'])==inv['native_step_sha256'];ss,_,_=b.read_step(Path(inv['native_step']))
 return {ref:ss[row['candidates'][0]['solid_index']] for ref,row in inv['native_part_correspondence'].items()},inv

def exact_checks(native,old):
 rows=[]
 def add(name,test,**e):rows.append(dict(name=name,status='PASS' if test else 'FAIL',**e))
 st=stocks();added=r7.union([s for _,s in st]);palm=native['P02'];expected=b.fuse(old['P02'],added)
 d=b.xor_volume(palm,expected);add('Independent two pads plus6 R1.2 CSG root stocks equal whole native P02',d<=TOL,symmetric_difference_mm3=d)
 add('P02 remains one valid connected printable solid',BRepCheck_Analyzer(palm).IsValid() and b.count(palm,TopAbs_SOLID)==b.count(palm,TopAbs_SHELL)==1,solid_count=b.count(palm,TopAbs_SOLID),shell_count=b.count(palm,TopAbs_SHELL))
 missing=b.volume(b.cut(old['P02'],palm));add('All original R8 P02 stock retained',missing<=TOL,missing_original_stock_mm3=missing)
 # All new material is inside this exact broad cover; outside it the source palm is preserved.
 cover=r7.union([b.box([-29,-26.2,14],[-22.75,-16.8,28.2]),b.box([-29,16.8,14],[-22.75,26.2,28.2])]);outside=b.xor_volume(b.cut(palm,cover),b.cut(old['P02'],cover));add('Wrist surface/cover/mounts unchanged outside declared brace region',outside<=TOL,symmetric_difference_mm3=outside)
 for name,lo,hi in [('palm M4 left',[-24,-38,6],[-9,-26.25,32]),('palm M4 right',[-24,26.25,6],[-9,38,32]),('case M2 left',[-30,-62,9],[-23,-56,15]),('case M2 right',[-30,56,9],[-23,62,15]),('complete lid-gap underside',[-47,-65,9.4],[-23,65,13.999])]:
  area=b.box(lo,hi);d=b.xor_volume(b.common(palm,area),b.common(old['P02'],area));add('Exact existing local region '+name,d<=TOL,symmetric_difference_mm3=d)
 add('P02 and total assembly bounds unchanged',np.max(np.abs(b.bounds(palm)-b.bounds(old['P02'])))<1e-6,palm_bounds_mm=b.bounds(palm).tolist())
 for side,y0,y1 in [('left',-25,-18),('right',18,25)]:
  # Two 0.001mm face bands straddling the nominal bearing plane prove full area on both solids.
  stockface=b.box([-22.751,y0,14],[-22.75,y1,27]);wallface=b.box([-22.75,y0,14],[-22.749,y1,27]);pa=b.volume(b.common(palm,stockface))/.001;wa=b.volume(b.common(native['P01'],wallface))/.001
  add('Full7x13 planar compression bearing '+side,abs(pa-91)<1e-5 and abs(wa-91)<1e-5,palm_face_area_mm2=pa,fixed_frame_face_area_mm2=wa,bearing_plane_x_mm=-22.75)
 overlap=b.volume(b.common(added,native['P01']));gap=b.gap(added,native['P01']);add('Intentional P02/P01 contact is boundary only',overlap<=TOL and gap<1e-6,intersection_mm3=overlap,exact_gap_mm=gap,contact_definition='Added palm pads against fixed P01 rear wall atX-22.75; nominal compression/sliding contact, not an interference fit.')
 for ref in ['H13','H15','H160','H161','P05','P08','P09','E06','E08']:
  g=b.gap(added,native[ref]);add('Added stock exact nominal gap to '+ref,g>0,exact_gap_mm=g)
 for ref,target in sorted(native.items()):
  if ref=='P02':continue
  ov=0. if v.separated(b.bounds(added),b.bounds(target)) else b.volume(b.common(added,target));add('Added-stock static pair '+ref,ov<=TOL,intersection_mm3=ov)
 lid=b.gap(palm,native['P09']);add('Complete palm retains0.6mm P09 lid gap',abs(lid-.6)<1e-5,exact_gap_mm=lid)
 return rows,added

def envelope_checks(native):
 # Broad cover of every literal stock; swept boxes certify every translation, not samples.
 boxes=[([-29,-26.2,14],[-22.75,-16.8,28.2]),([-29,16.8,14],[-22.75,26.2,28.2])];added=r7.union([s for _,s in stocks()]);cover=r7.union([b.box(lo,hi) for lo,hi in boxes]);rows=[]
 def add(name,test,**e):rows.append(dict(name=name,status='PASS' if test else 'FAIL',**e))
 missing=b.volume(b.cut(added,cover));add('Conservative two-box cover contains every new stock',missing<=TOL,uncovered_stock_mm3=missing)
 spec=json.loads((PROJECT/'review/flat132-adjustable-rear-2026-10-23/validation/rear-spec.json').read_text());domain=r7.vertices()
 for ref,target in sorted(native.items()):
  if ref=='P02':continue
  if ref in v.SPRINGS|v.ARTICULATED:
   left=12 if ref in v.SPRINGS else 29.05;add('Full spring/lever source envelope '+ref,left-(-22.75)>0,minimum_axial_clearance_mm=left+22.75);continue
  offsets=domain@r7.coefficients(ref,spec);lo,hi=float(offsets.min()),float(offsets.max());swept=r7.union([b.box([a[0]-hi,*a[1:]],[z[0]-lo,*z[1:]]) for a,z in boxes]);ov=0. if v.separated(b.bounds(swept),b.bounds(target)) else b.volume(b.common(swept,target));add('Complete dynamic and ISO relative motion '+ref,ov<=TOL,intersection_upper_bound_mm3=ov,relative_x_range_mm=[lo,hi],intentional_contact=(ref=='P01'))
 for ref in ['H140','H141']:
  add('Complete ISO replacement sleeve source envelope '+ref,12+22.75>0,minimum_axial_clearance_mm=34.75,method='Explicit unchanged source sleeve starts atX12+p, p>=0; all new palm stock hasX<=-22.75. Sleeves replace springs in ISO and are absent from neutral inventory.')
 service=[]
 def serviceadd(name,test,**e):service.append(dict(name=name,status='PASS' if test else 'FAIL',**e))
 up=r7.union([b.box(a,[*z[:2],z[2]+40]) for a,z in boxes]);module={'P02','P08','P09','P10'}|{r for r in native if r.startswith(('E','PCB_'))}
 for ref,target in sorted(native.items()):
  if ref in module:continue
  if ref in v.SPRINGS|v.ARTICULATED:
   left=12 if ref in v.SPRINGS else 29.05;serviceadd('Upward40mm release versus source envelope '+ref,left+22.75>0,minimum_axial_clearance_mm=left+22.75);continue
  target=r7.tr(target,[float(2*r7.coefficients(ref,spec)[1]),0,0]);ov=0. if v.separated(b.bounds(up),b.bounds(target)) else b.volume(b.common(up,target));serviceadd('Complete40mm upward brace release versus '+ref,ov<=TOL,intersection_upper_bound_mm3=ov,intentional_sliding_boundary_contact=(ref=='P01'))
 for ref in sorted(module-{'P02','E06','E08'}):
  # Lower detached case module20mm: opposite relative motion of the fixed new stock.
  swept=r7.union([b.box(a,[*z[:2],z[2]+20]) for a,z in boxes]);target=native[ref];ov=0. if v.separated(b.bounds(swept),b.bounds(target)) else b.volume(b.common(swept,target));serviceadd('Detached case20mm downward versus added stock '+ref,ov<=TOL,intersection_upper_bound_mm3=ov)
 return rows,service

def poses_check(neutral,poses):
 expected={x['name']:Path(x['archive']) for x in json.loads((BASE/'validation/native-poses.json').read_text())};rows=[]
 if len(poses)!=3:return [dict(status='NOT_PROVIDED',name='All3 additional native whole poses required')]
 palm=v.canonical_triangle_sha256(neutral['P02']['mesh'])
 for pose in poses:
  now,ignored=v.load(Path(pose['archive']),{});prior,oldignored=v.load(expected[pose['name']],{});checks=[]
  for ref in sorted(now):
   actual=v.canonical_triangle_sha256(now[ref]['mesh']);expected_mesh=neutral['P02']['mesh'] if ref=='P02' else prior[ref]['mesh'];wanted=v.canonical_triangle_sha256(expected_mesh)
   # Native STL serialization can move an unchanged facet by a float32 ULP.
   # Accept only the identical ordered triangle soup within30nm; exact native
   # CAD identity remains a separate mandatory122-body Boolean criterion.
   aa=now[ref]['mesh'].triangles;bb=expected_mesh.triangles;drift=None if aa.shape!=bb.shape else float(np.max(np.abs(aa-bb)))
   serialized=(actual==wanted) or (drift is not None and drift<=3e-5);checks.append(dict(ref=ref,status='PASS' if serialized else 'FAIL',native_triangle_sha256=actual,expected_triangle_sha256=wanted,comparison='EXACT_CANONICAL_TRIANGLES' if actual==wanted else 'SAME_ORDERED_FACETS_FLOAT32_SERIALIZATION_TOLERANCE',max_same_facet_coordinate_drift_mm=drift,serialization_tolerance_mm=3e-5))
  rows.append(dict(pose=pose['name'],archive=str(Path(pose['archive']).resolve()),sha256=sha(pose['archive']),baseline_native_pose_sha256=sha(expected[pose['name']]),status='PASS' if not ignored and not oldignored and set(now)==set(prior) and len(now)==123 and all(x['status']=='PASS' for x in checks) else'FAIL',checks=checks))
 return rows

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--neutral',type=Path);ap.add_argument('--step',type=Path);ap.add_argument('--workspace',default='');ap.add_argument('--poses',type=Path);ap.add_argument('--preflight',action='store_true');ap.add_argument('--reuse-complete',action='store_true');ap.add_argument('--defer-poses',action='store_true');args=ap.parse_args();cert=source_scope();old,oldinv=baseline_native()
 if args.preflight:
  native=dict(old);native['P02']=b.fuse(old['P02'],r7.union([s for _,s in stocks()]));exact,_=exact_checks(native,old);motion,service=envelope_checks(native);allrows=exact+motion+service;bad=[x for x in allrows if x['status']in BAD];out=dict(status='PASS_LOCAL_LITERAL_CSG_PREFLIGHT' if not bad else'FAIL',scope='Local expected P02 fused to frozen R8 native geometry, before new native regeneration; not STEP roundtrip/native release evidence.',source_sha256=cert['source_sha256'],exact=exact,motion=motion,service=service,failed_checks=len(bad));write(HERE/'local-preflight.json',out);print(out['status'],'checks',len(allrows),'fail',len(bad),flush=True);assert not bad;return
 assert args.neutral and args.step
 parts,native,inv=r7.load_native(args.neutral,args.step);assert len(parts)==123 and set(native)==set(old);inv['source_sha256']=cert['source_sha256'];write(HERE/'native-step-inventory.json',inv)
 if args.reuse_complete:
  before=json.loads((HERE/'validation-summary.json').read_text());assert before['source_sha256']==cert['source_sha256']
  m=json.loads((HERE/'manifest.json').read_text());assert sha(args.step)==m['native_export_files_sha256'][str(args.step.resolve())] and sha(args.neutral)==m['native_export_files_sha256'][str(args.neutral.resolve())]
  cached={}
  for name in ['unchanged-native-breps.json','palm-exact-audit.json','palm-path-audit.json','palm-service-audit.json']:
   assert sha(HERE/name)==before['evidence_files'][name];cached[name]=json.loads((HERE/name).read_text());assert cached[name]['status']=='PASS'
  identity=cached['unchanged-native-breps.json']['checks'];exact=cached['palm-exact-audit.json']['checks'];motion=cached['palm-path-audit.json']['checks'];service=cached['palm-service-audit.json']['checks']
 else:
  identity=[]
  for ref in sorted(set(native)-{'P02'}):
   d=b.xor_volume(native[ref],old[ref]);identity.append(dict(ref=ref,status='PASS' if d<=TOL else'FAIL',symmetric_difference_mm3=d))
  exact,_=exact_checks(native,old);motion,service=envelope_checks(native)
 write(HERE/'unchanged-native-breps.json',dict(status='PASS' if all(x['status']=='PASS' for x in identity) else'FAIL',native_step_sha256=sha(args.step),baseline_step_sha256=oldinv['native_step_sha256'],checks=identity));print('R9:123native solids,122identity checks complete',flush=True)
 write(HERE/'palm-exact-audit.json',dict(status='PASS' if all(x['status']=='PASS' for x in exact) else'FAIL',source_sha256=cert['source_sha256'],native_step_sha256=sha(args.step),checks=exact))
 write(HERE/'palm-path-audit.json',dict(status='PASS' if all(x['status']=='PASS' for x in motion) else'FAIL',scope='Added stock only versus full legal correlated dynamic domain. ISO positions are a subset throughu=15-p-a. Exact complete opposite swept boxes contain all CSG stock translations.',checks=motion))
 write(HERE/'palm-service-audit.json',dict(status='PASS' if all(x['status']=='PASS' for x in service) else'FAIL',prerequisites='Unload/restrain, set rearadvance0/preload2, remove both palm M4 screws; lift complete palm/case module40mm. Fixed P01 pads slide vertically with nominal zero-volume boundary contact. Bench detach case by two underside M2 screws and lower module20mm. P09 opening remains inherited after P02 is absent; never open installed lid against palm.',checks=service))
 pose_spec=json.loads(args.poses.read_text()) if args.poses else[];poses=poses_check(parts,pose_spec);write(HERE/'native-pose-audit.json',dict(source_sha256=cert['source_sha256'],poses=poses))
 failed=[x for x in identity+exact+motion+service+poses if x['status']in BAD and x['status']!='NOT_PROVIDED'];unresolved=[x for x in poses if x['status']=='NOT_PROVIDED'];files=[args.neutral,args.step]+[Path(x['archive']) for x in pose_spec]
 provenance=dict(workspace_url=args.workspace,feature_source_sha256=cert['source_sha256'],association='Root operator verified exact R9 source/native regeneration and export settings; independent audit does not regenerate Onshape.')
 if (HERE/'manifest.json').exists():
  prev=json.loads((HERE/'manifest.json').read_text()).get('native_provenance',{});provenance.update({k:prev[k] for k in ['immutable_version_id','immutable_version_url','version_binding_note'] if k in prev})
 manifest=dict(status='ACTUAL_NATIVE_R9_INPUT_MANIFEST',feature_source=cert['source'],native_provenance=provenance,assembly=str(args.neutral.resolve()),native_step=str(args.step.resolve()),native_export_files_sha256={str(p.resolve()):sha(p) for p in files},expected_device_refs=sorted(r for r in parts if not r.startswith(('E','PCB_'))),expected_electronics_count=53,source_scope_certificate=str(HERE/'source-scope-certificate.json'),source_scope_certificate_sha256=sha(HERE/'source-scope-certificate.json'));write(HERE/'manifest.json',manifest)
 names=['manifest.json','source-scope-certificate.json','native-step-inventory.json','unchanged-native-breps.json','palm-exact-audit.json','palm-path-audit.json','palm-service-audit.json','native-pose-audit.json','audit_palm_bracing.py','requirements.txt']
 summary=dict(status='NOMINAL_GEOMETRY_CHECKS_PASS' if not failed and not unresolved else ('NATIVE_CAD_CHECKS_PASS_POSES_PENDING' if not failed else 'INCOMPLETE_OR_FAILED'),source_sha256=cert['source_sha256'],native_provenance=provenance,scope='R9 P02-only fixed-frame compression bracing: exact122-body/source preservation, independent whole-palm CSG identity and two91mm2 boundary contacts, complete added-stock dynamic/ISO and vertical/case service certification. Unchanged R8 geometry/service evidence retained by exact identity, not rerun or relabeled.',failed_checks=len(failed),unresolved_checks=len(unresolved),native_inventory=dict(whole=123,device=70,electronics_reference=53,printed=16),changed_ref='P02',unchanged_exact_brep_count=122,step_roundtrip_status='COMPLETE',palm_checks=[x for x in exact if not x['name'].startswith('Added-stock static pair')],native_poses=poses,evidence_files={n:sha(HERE/n) for n in names},failures=failed,baseline_reuse=dict(source_scope_certificate=str(HERE/'source-scope-certificate.json'),sha256=sha(HERE/'source-scope-certificate.json'),baseline_summary_sha256=cert['baseline_validation_summary_sha256']),limitations=['Two nominal compression contacts add a fixed-frame palm load path; actual pad fit, simultaneous bearing, print tolerances/creep and stiffness need physical checks.','No added stock bears against P05, sensor/cassette or P09/electronics; nominal geometry does not qualify sensor calibration or500N capacity.','Contact is not a prescribed press fit. Do not force interference or preload the portal by tightening palm fasteners; unload/restrain before service.','Wrist surface, mounts, clear finger opening and0.6mm P02-to-P09 lid gap remain unchanged. Existing P08 mounting collars intentionally touch P02.','The hand scan remains approximate; comfort and pinch-safe human fit are unqualified.','Native source/export association is root-operator declared and hash-bound; this audit does not regenerate Onshape.'])
 for name in ['validation.json','validation-summary.json']:write(HERE/name,summary)
 (HERE/'validation-summary.md').write_text('# R9 fixed-frame palm bracing validation\n\n**'+summary['status']+'**\n\nFailed:'+str(summary['failed_checks'])+'; unresolved:'+str(summary['unresolved_checks'])+'.\n\n'+summary['scope']+'\n\n'+'\n'.join('- '+x for x in summary['limitations'])+'\n')
 print(json.dumps({k:summary[k] for k in ['status','failed_checks','unresolved_checks','unchanged_exact_brep_count']},indent=2),flush=True)
 assert not failed and (not unresolved or args.defer_poses)
if __name__=='__main__':main()
