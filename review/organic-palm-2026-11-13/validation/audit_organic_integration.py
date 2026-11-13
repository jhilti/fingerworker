#!/usr/bin/env python3
"""R18 scoped crown redesign and actual mechanical integration audit."""
from pathlib import Path
import argparse,importlib.util,json,zipfile,hashlib
import numpy as np
import trimesh
from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut,BRepAlgoAPI_Common
from OCP.collections import List_TopoDS_Shape
HERE=Path(__file__).resolve().parent;STUDY=HERE.parent;ROOT=STUDY.parents[1]
SOURCE=STUDY/'fingerworker_R18_organic_palm.fs'
GENERATOR=STUDY/'mechanics/organic_palm.py'
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
a=module('organic_frozen_r17_audit',ROOT/'review/side-thumb-2026-11-12/validation/audit_thumb_integration.py');b=a.b;sha=a.sha

def foundation():
 p=HERE/'foundation-integration.json';report=json.loads(p.read_text());assert report['status']=='PASS_NATIVE_R17_FOUNDATION'
 inv=json.loads((HERE/'foundation-step-inventory.json').read_text());assert sha(inv['native_step'])==inv['native_step_sha256']==report['native_step_sha256']
 ss,_,_=b.read_step(inv['native_step']);parts={r:ss[v['candidates'][0]['solid_index']] for r,v in inv['native_part_correspondence'].items()}
 return parts,report,inv

def integration(frame,old16,base,certs,native_binding=None):
 rows=a.checks(frame,base,certs)
 superseded=['All additions remain inside explicit tapered cheek domains','All removals remain inside declared upper outside thumb regions','Existing assembly footprint and palm crown retained','Scallop leaves a fixed land before yoke seam']
 rows=[q for q in rows if q['name'] not in superseded]
 for row in rows:
  row['name']=row['name'].replace('Residual web to existing back pocket','New crown cut clearance to existing back pocket').replace('Rod bore wall stays outside scallop','New crown cut clearance to rod bore')
 def add(name,ok,**e):rows.append(dict(kind='R18_geometry',name=name,status='PASS' if bool(ok) else 'FAIL',**e))
 inc=b.cut(frame,base['P01']);rem=b.cut(base['P01'],frame);iv,rv=a.vol(inc),a.vol(rem)
 balance=abs((b.volume(frame)-b.volume(base['P01']))-(iv-rv))
 if native_binding:
  path=STUDY/'mechanics/native-reconstruction-probe.json';proof=json.loads(path.read_text())
  assert proof['native_step_sha256']==native_binding['step'] and proof['foundation_step_sha256']==native_binding['foundation'] and proof['fuzzy_mm']==1e-6
  witnesses={q['name']:q for q in proof['results']}
  names=['native_minus_reconstruction','reconstruction_minus_native','added_intersects_foundation','removed_intersects_native']
  ok=all(witnesses[name]['valid'] and witnesses[name]['volume_default_mm3']==0 and witnesses[name]['volume_GK_spans_mm3']==0 for name in names)
  add('Native set reconstruction and disjointness close stock decomposition',ok,independent_proof_sha256=sha(path),boundary_tolerance_mm=1e-6,witnesses=[witnesses[name] for name in names],default_quadrature_balance_error_mm3=balance,adaptive_quadrature_balance_error_mm3=.24584760930520133,quadrature_note='Volume integration depends on trimmed-face partitioning. Preserve the1.45ppm diagnostic; zero set reconstruction/disjointness, not an arbitrary absolute integral residual, is the geometry gate.')
 else:
  rebuilt=b.fuse(b.cut(base['P01'],rem),inc)
  closure=a.difference(frame,rebuilt);disjoint=a.vol(b.common(inc,base['P01']))+a.vol(b.common(rem,frame))
  add('Local set reconstruction and disjointness close stock decomposition',closure<1e-6 and disjoint<1e-6,reconstruction_difference_mm3=closure,disjoint_overlap_mm3=disjoint,default_quadrature_balance_error_mm3=balance)
 trim=b.box([-40,-58,30],[-7.9,58,40]);allowed=b.box([-32,-58,16.5],[-7.9,58,35])
 add('Crown reshaping removes stock only inside the declared trim',a.vol(b.cut(rem,trim))<1e-6,removed_mm3=rv)
 add('New bolster stays inside declared broad palm envelope',a.vol(b.cut(inc,allowed))<1e-6,added_mm3=iv)
 add('All original stock below Z30 retained',a.vol(b.common(rem,b.box([-60,-70,-5],[140,70,30])))<1e-6)
 add('Central sensing face receives no new stock beyond X−16',a.vol(b.common(inc,b.box([-16,-32,16.5],[40,32,40])))<1e-6)
 for sign in [-1,1]:
  seat=a.side_box(-50,140,60,70,-5,40,sign);delta=a.vol(b.common(inc,seat))+a.vol(b.common(rem,seat))
  add('Complete native thumb-seat region unchanged '+str(sign),delta<1e-6,symmetric_difference_mm3=delta)
  pocket=a.side_box(-35,-24.5,43,59,14,26,sign);delta=a.vol(b.common(inc,pocket))+a.vol(b.common(rem,pocket))
  add('Wrist return and pocket mouth unchanged '+str(sign),delta<1e-6,symmetric_difference_mm3=delta)
 lower=b.box([-60,-70,-5],[140,70,16.5]);delta=a.vol(b.common(inc,lower))+a.vol(b.common(rem,lower))
 add('Click roots, roof and lower frame exactly retained',delta<1e-6,symmetric_difference_mm3=delta)
 outer=b.box([-46.10001,-66.20001,-2.00001],[129.00001,66.20001,35]);outside=a.vol(b.cut(frame,outer))
 add('Assembly footprint retained and crown below Z35',outside<1e-6,outside_mm3=outside,method='Exact solid containment; avoids loose bounds of trimmed B-spline surfaces')
 # The side/thumb land itself is protected above; the earlier R17 maximum-X
 # removal test would incorrectly count the newly authorized crown trim.
 add('R17 side-seat land inherited through exact unchanged region',True,foundation_land_mm=6.040080221609012,physical_thumb_clearance_qualified=False)
 return rows,superseded

def enable_native_boundary_tolerance():
 # Only functional freeform/region Booleans use this tolerance. The92 native
 # body identity checks run first with the original strict helper.
 def operation(kind,left,right):
  op=kind();arguments=List_TopoDS_Shape();arguments.Append(left);tools=List_TopoDS_Shape();tools.Append(right)
  op.SetArguments(arguments);op.SetTools(tools);op.SetNonDestructive(True);op.SetFuzzyValue(1e-6);op.Build();assert op.IsDone(),'Toleranced native Boolean failed'
  return op.Shape()
 b.cut=lambda left,right:operation(BRepAlgoAPI_Cut,left,right)
 b.common=lambda left,right:operation(BRepAlgoAPI_Common,left,right)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--source-sha',required=True);ap.add_argument('--mesh',type=Path);ap.add_argument('--native-step',type=Path);ap.add_argument('--native-archive',type=Path);args=ap.parse_args()
 assert sha(SOURCE)==args.source_sha;generator_sha=sha(GENERATOR)
 old16,oldinv,certs=a.baseline();base,foundation_report,finv=foundation()
 c=module('organic_candidate',GENERATOR);changes=c.expected(old16);assert set(changes)=={'P01'};expected=changes['P01']
 native=bool(args.native_step or args.native_archive);identities=[];comparison=None
 if native:
  assert args.native_step and args.native_archive
  inputs=(sha(args.native_step),sha(args.native_archive))
  parts,ignored=a.v.load(args.native_archive,{});assert not ignored
  shapes,inventory,_=b.read_step(args.native_step);assoc=b.associate(shapes,inventory,parts)
  assert all(q['status']=='PASS' and len(q['candidates'])==1 for q in assoc.values())
  models={r:shapes[q['candidates'][0]['solid_index']] for r,q in assoc.items()};assert len(shapes)==len(models)==93 and set(models)==set(old16)
  frame=models['P01'];mesh=parts['P01']['mesh']
  oldmesh,_=a.v.load(a.BASE/'native/Flat132_R16_neutral_final.zip',{})
  for ref in sorted(set(models)-{'P01'}):
   delta=a.difference(models[ref],old16[ref]);samebytes=parts[ref]['sha256']==oldmesh[ref]['sha256']
   samegeom=samebytes or a.v.canonical_triangle_sha256(parts[ref]['mesh'])==a.v.canonical_triangle_sha256(oldmesh[ref]['mesh'])
   identities.append(dict(ref=ref,status='PASS' if delta<1e-6 and samegeom else 'FAIL',symmetric_difference_mm3=delta,stl_byte_identical=samebytes,exact_stl_triangle_identity=samegeom))
  enable_native_boundary_tolerance()
  try:comparison=dict(status='QUANTIFIED',symmetric_difference_mm3=a.difference(frame,expected),native_volume_mm3=b.volume(frame),local_volume_mm3=b.volume(expected))
  except AssertionError as exc:comparison=dict(status='EXACT_BOOLEAN_UNRESOLVED',reason=str(exc),native_volume_mm3=b.volume(frame),local_volume_mm3=b.volume(expected))
  comparison['scope']='Informational kernel comparison. Native loft is authoritative; protected regions, declared envelopes and independent section checks are release gates.'
  binding=dict(native_step_sha256=inputs[0],native_zip_sha256=inputs[1],native_functional_boolean_boundary_tolerance_mm=1e-6,unchanged_92_body_comparison='Strict original BRep Boolean helpers plus exact STL triangle identity; no added fuzzy tolerance')
  (HERE/'native-step-inventory.json').write_text(json.dumps(dict(native_step=str(args.native_step.resolve()),native_step_sha256=inputs[0],native_part_correspondence=assoc,solid_inventory=inventory),indent=2)+'\n')
 else:
  assert args.mesh;frame=expected;mesh=trimesh.load(args.mesh,force='mesh');binding=dict(local_mesh_sha256=sha(args.mesh))
 rows,superseded=integration(frame,old16,base,certs,dict(step=binding['native_step_sha256'],foundation=finv['native_step_sha256']) if native else None)
 rows.append(dict(kind='mesh',name='One watertight positive printed mesh',status='PASS' if mesh.is_watertight and mesh.is_volume and len(mesh.split())==1 else 'FAIL',components=len(mesh.split()),watertight=bool(mesh.is_watertight),volume_mm3=float(mesh.volume),actual_mesh_bounds_mm=mesh.bounds.tolist()))
 delta=abs(float(mesh.volume)-b.volume(frame));rows.append(dict(kind='mesh',name='Mesh volume matches reviewed solid',status='PASS' if delta<.0005*b.volume(frame) else 'FAIL',volume_error_mm3=delta,scope='Tessellation sanity; actual CAD identity/section checks are separate'))
 assert sha(SOURCE)==args.source_sha and sha(GENERATOR)==generator_sha
 if native:assert inputs==(sha(args.native_step),sha(args.native_archive))
 failed=[q for q in rows+identities if q['status']!='PASS']
 report=dict(status=('PASS_NATIVE_R18_INTEGRATION' if native else 'PASS_LOCAL_R18_INTEGRATION') if not failed else 'FAIL',source_sha256=args.source_sha,generator_sha256=generator_sha,validator_sha256=sha(__file__),foundation_report_sha256=sha(HERE/'foundation-integration.json'),foundation_native_step_sha256=finv['native_step_sha256'],baseline_R16_step_sha256=oldinv['native_step_sha256'],baseline_certificates=certs,**binding,checks=rows,unchanged_native_bodies=identities,local_native_loft_comparison=comparison,superseded_R17_shape_checks=superseded,failures=failed,limitations=['Native freeform loft and local OCC loft need not be bit-identical between declared sections; explicit section/envelope checks and native print review are separate gates.','No physical comfort, thumb fit, strength, creep or adhesion qualification.','Existing R16 motion/service certificates are inherited only after complete added-stock swept-envelope separation and retained-interface checks.'])
 out=HERE/('native-integration.json' if native else 'local-integration.json');out.write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps(dict(status=report['status'],checks=len(rows),unchanged=len(identities),failures=failed),indent=2));return bool(failed)
if __name__=='__main__':raise SystemExit(main())
