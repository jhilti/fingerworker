#!/usr/bin/env python3
"""Focused native R19 delta audit; retains frozen R18 evidence by identity."""
from pathlib import Path
import importlib.util,json,argparse,zipfile,re
import numpy as np
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.TopAbs import TopAbs_SOLID,TopAbs_SHELL,TopAbs_FACE
HERE=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('rim_meas_final',HERE/'rim_measurements.py');r=importlib.util.module_from_spec(s);s.loader.exec_module(r);b=r.b;sha=r.sha
m=r.module('rigid_final',r.STUDY/'latches/rigid_mounts.py');v=r.a.a.v

def empty(shape):
 return BRepCheck_Analyzer(shape).IsValid() and b.count(shape,TopAbs_SOLID)==0 and b.count(shape,TopAbs_FACE)==0

def comparison(left,right):
 aa=b.cut(left,right);bb=b.cut(right,left)
 return dict(valid=bool(BRepCheck_Analyzer(aa).IsValid() and BRepCheck_Analyzer(bb).IsValid()),left_only_solids=b.count(aa,TopAbs_SOLID),right_only_solids=b.count(bb,TopAbs_SOLID),left_only_faces=b.count(aa,TopAbs_FACE),right_only_faces=b.count(bb,TopAbs_FACE),symmetric_difference_mm3=b.volume(aa)+b.volume(bb),empty=empty(aa) and empty(bb))

def overlap(left,right):
 q=b.common(left,right);assert BRepCheck_Analyzer(q).IsValid();return b.volume(q)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--native-step',type=Path,required=True);ap.add_argument('--native-archive',type=Path,required=True);args=ap.parse_args()
 source=r.STUDY/'fingerworker_R19_thumb_rim.fs';ver=json.loads((r.STUDY/'onshape-version.json').read_text());sourcehash=sha(source);assert sourcehash==ver['source_sha256'] and ver['source_readback_exact'];inputs=[sha(args.native_step),sha(args.native_archive)]
 old,oldinv,release=r.baseline();probe=json.loads((HERE/'rim-probe-check.json').read_text());assert probe['status']=='PASS_NATIVE_R19_RIM_PROBE'
 with zipfile.ZipFile(args.native_archive) as z:
  overrides={name:'P06'+match[1] for name in z.namelist() if (match:=re.search(r'\bP06([LR])(?=[ _.-])',name))}
 parts,ignored=v.load(args.native_archive,{'member_ref_overrides':overrides});assert not ignored,ignored
 shapes,inventory,_=b.read_step(args.native_step);assoc=b.associate(shapes,inventory,parts);assert all(q['status']=='PASS' for q in assoc.values()),[k for k,q in assoc.items() if q['status']!='PASS']
 model={ref:shapes[q['candidates'][0]['solid_index']] for ref,q in assoc.items()};assert len(model)==len(shapes)==94 and set(model)==(set(old)-{'P06'})|{'P06L','P06R'}
 (HERE/'native-step-inventory.json').write_text(json.dumps(dict(native_step=str(args.native_step.resolve()),native_step_sha256=inputs[0],native_part_correspondence=assoc,solid_inventory=inventory),indent=2)+'\n')
 oldmesh,_=v.load(r.BASE/'native/Flat132_R18_neutral_final.zip',{});identities=[]
 for ref in sorted(set(old)-{'P01','P06','P08'}):
  comp=comparison(model[ref],old[ref]);samebytes=parts[ref]['sha256']==oldmesh[ref]['sha256'];sametri=samebytes or v.canonical_triangle_sha256(parts[ref]['mesh'])==v.canonical_triangle_sha256(oldmesh[ref]['mesh'])
  identities.append(dict(ref=ref,status='PASS' if comp['empty'] and sametri else 'FAIL',stl_byte_identical=samebytes,exact_stl_triangle_identity=sametri,**comp))
 print('IDENTITIES',sum(x['status']=='PASS' for x in identities),len(identities),flush=True)
 r.a.enable_native_boundary_tolerance();rows=[]
 def ck(name,ok,**details):rows.append(dict(name=name,status='PASS' if bool(ok) else 'FAIL',**details))
 for ref in ['P01','P06L','P06R','P08']:
  shape=model[ref];mesh=parts[ref]['mesh'];ck('Valid single native solid/shell '+ref,BRepCheck_Analyzer(shape).IsValid() and b.count(shape,TopAbs_SOLID)==b.count(shape,TopAbs_SHELL)==1)
  ck('Native print mesh is one closed positive component '+ref,mesh.is_watertight and mesh.is_volume and parts[ref].get('connected_solid_count')==1,native_stl_sha256=parts[ref]['sha256'],triangles=len(mesh.faces),watertight=bool(mesh.is_watertight),component_count=parts[ref].get('connected_solid_count'),mesh_error=parts[ref].get('error'))
 # Reuse the already completed STEP-only geometric comparisons, bound to
 # these same final bytes and to the unchanged rigid generator/probe report.
 delta_path=HERE/'native-shape-delta.json';delta=json.loads(delta_path.read_text())
 assert delta['status']=='PASS_NATIVE_R19_SHAPE_DELTA' and delta['source_sha256']==sourcehash and delta['native_step_sha256']==inputs[0]
 assert delta['probe_report_sha256']==sha(HERE/'rim-probe-check.json') and delta['generator_sha256']==sha(r.STUDY/'latches/rigid_mounts.py')
 assert delta['validator_sha256']==sha(HERE/'prepare_native_delta.py')
 rows.extend(delta['checks'])
 # Independent rigid subtractions and retained mating surfaces.
 for ref in ['P06L','P06R']:
  extra=b.cut(model[ref],old['P06']);ck('Rear block contains only original block stock '+ref,empty(extra),extra_mm3=b.volume(extra))
 same=comparison(m.move(model['P06L'],[0,102,0]),model['P06R']);ck('Two rear blocks identical after102mm translation',same['empty'],**same)
 for ref in ['P06L','P06R','P08']:
  for other in ['P01','P04','P05','P09','E01','E05','E06','E07','E08']:
   if other not in model:continue
   ov=overlap(model[ref],model[other]);prior=overlap(old['P06'] if ref.startswith('P06') else old['P08'],old[other]);ck(ref+' seated clearance retained '+other,ov<=prior+1e-6,overlap_mm3=ov,baseline_overlap_mm3=prior)
 for side in [-1,1]:
  y=side*59;head=m.m.r7.cyl([-26.5,y,2.4],[-26.5,y,3.999],1.9);driver=m.m.r7.cyl([-26.5,y,-20],[-26.5,y,3.999],2.5);shank=m.m.r7.cyl([-26.5,y,4.001],[-26.5,y,12],1.0);insert=m.m.r7.cyl([-26.5,y,9.5],[-26.5,y,12.5],1.6)
  for tool,label in [(head,'M2 head'),(driver,'5mm driver approach')]:
   for ref in ['P01','P08','P09']:
    vol=overlap(tool,model[ref]);ck(label+' clears '+ref+' '+str(side),vol<1e-6,overlap_mm3=vol)
  vol=sum(overlap(shank,model[ref]) for ref in ['P01','P08']);ck('M2x8 shank clearance '+str(side),vol<1e-6,overlap_mm3=vol,nominal_engagement_mm=2.5)
  vol=overlap(insert,model['P01']);ck('Existing M2 insert envelope retained '+str(side),vol<1e-6,overlap_mm3=vol)
  # Conservative complete sweep of every possible newly added ear/root point.
  sweep=m.boxside(-29,-23.8,53.8,62,-20,9.5,side);vol=overlap(sweep,model['P01']);ck('Rigid ear continuous20mm downward route '+str(side),vol<1e-6,overlap_mm3=vol,method='Complete conservative added-stock swept box; no flex prerequisite')
  for ref in ['P04','H060','H061','P11','H10']:
   bb=b.bounds(old[ref]).copy();bb[0,0]+=(-30.8 if ref in ['P11','H10'] else -30);bb[1,0]+=(.8 if ref in ['P11','H10'] else 0)
   separation=b.gap(m.ear(side),b.box(bb[0],bb[1]));ck('Added rigid ear clears full stroke '+ref+' '+str(side),separation>1e-6,clearance_lower_bound_mm=separation)
 # Specific rear block extraction after removing mandatory screws. Full moving
 # block is a subset of the already validated rear-gate axial route.
 for ref in ['P06L','P06R']:
  for dx in [0,.25,1,5,12]:
   shifted=m.move(model[ref],[dx,0,0]);vol=overlap(shifted,model['P01']);ck('Rear block axial withdrawal '+ref+' '+str(dx),vol<1e-6,overlap_mm3=vol)
 assert inputs==[sha(args.native_step),sha(args.native_archive)] and sourcehash==sha(source)
 failed=[q for q in rows+identities if q['status']!='PASS']
 report=dict(status='PASS_NATIVE_R19_INTEGRATION' if not failed else 'FAIL_NATIVE_R19_INTEGRATION',source_sha256=sourcehash,version_id=ver['version_id'],native_step_sha256=inputs[0],native_zip_sha256=inputs[1],baseline_native_step_sha256=release['native_step_sha256'],baseline_release_binding_sha256=sha(r.BASE/'validation/native-release-binding.json'),validator_sha256=sha(__file__),rim_probe_report_sha256=sha(HERE/'rim-probe-check.json'),rigid_generator_sha256=sha(r.STUDY/'latches/rigid_mounts.py'),shape_delta_report_sha256=sha(delta_path),native_part_count=94,checks=rows,unchanged_native_bodies=identities,failures=failed,boundary_tolerance_mm=1e-6,unchanged_body_method='Strict BRep bidirectional empty differences and exact native STL triangle identity. H30 naming metadata may differ.',inherited_evidence='R18 native motion, sensing, fixture, strap and pocket proof is retained through90 unchanged bodies and scoped P01 comparisons. New rigid ear stock has explicit full-stroke and downward-removal envelope checks. The removed rear latch arms eliminate the old flex prerequisite; screw removal is mandatory.',limitations=['CAD nominal clearances and dimensions only; no printed strength, insert retention, comfort or fatigue qualification.','Required rear4M3x8 and tray2M2x8 screws replace the removed snap retention.','Floor samples describe retained existing geometry; they are not a blanket strength claim.'])
 (HERE/'native-integration.json').write_text(json.dumps(report,indent=2)+'\n')
 rim=dict(status='PASS_NATIVE_R19_RIM_CHECK' if not failed else 'WAIT_INTEGRATION',source_sha256=sourcehash,version_id=ver['version_id'],native_step_sha256=inputs[0],native_zip_sha256=inputs[1],probe_report_sha256=sha(HERE/'rim-probe-check.json'),native_integration_sha256=sha(HERE/'native-integration.json'),method='The complete front region of final native P01 is geometrically identical to the isolated measured native rim probe.',probe_measurements=probe,final_front_comparison=next(q for q in rows if q['name']=='Complete front frame and reviewed variable rims'))
 (HERE/'native-rim-check.json').write_text(json.dumps(rim,indent=2)+'\n');print(json.dumps(dict(status=report['status'],checks=len(rows),unchanged=len(identities),failures=failed),indent=2))
 return bool(failed)
if __name__=='__main__':raise SystemExit(main())
