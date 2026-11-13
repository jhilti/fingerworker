#!/usr/bin/env python3
"""Audit delivered Q01 STEP and print STL against the current fixed front.

Use --frame-step for a native P01-only STEP once available. Baseline P05 and
hardware are unchanged; their native identity is a separate final CAD check.
"""
from pathlib import Path
import argparse, hashlib, json, sys
import numpy as np
import trimesh
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
REVIEW=Path(__file__).resolve().parents[1];ROOT=REVIEW.parents[1]
HERE=ROOT/'review/simplification-2026-11-03/fixture'
sys.path.insert(0,str(ROOT/'review/simplification-2026-11-03'));import rear_gate as rear
b,r7=rear.b,rear.r7
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def common(a,c):
 op=b.common(a,c);assert BRepCheck_Analyzer(op).IsValid(),'Invalid Boolean result'
 return op
def overlap(a,c):
 aa,bb=b.bounds(a),b.bounds(c)
 if np.any(aa[1]<bb[0]) or np.any(bb[1]<aa[0]):return 0.
 return b.volume(common(a,c))
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--frame-step',type=Path,default=REVIEW/'native/P01_native.step')
 ap.add_argument('--native',action='store_true');args=ap.parse_args();args.frame_step=args.frame_step.resolve()
 old,inv=rear.load()
 native_inventory=REVIEW/'validation/native-step-inventory.json'
 native_binding={}
 if args.native:
  current=json.loads(native_inventory.read_text());native_assembly=Path(current['native_step'])
  assert sha(native_assembly)==current['native_step_sha256']
  native_binding=dict(native_assembly_step_sha256=current['native_step_sha256'],native_P01_solid_index=current['native_part_correspondence']['P01']['candidates'][0]['solid_index'])
  native_shapes=b.read_step(native_assembly)[0]
  frame=native_shapes[native_binding['native_P01_solid_index']]
  for ref in ('P04','P05','H040','H041'):
   old[ref]=native_shapes[current['native_part_correspondence'][ref]['candidates'][0]['solid_index']]
 else:frame=b.read_step(args.frame_step)[0][0]
 manifest=json.loads((HERE/'manifest.json').read_text());name=manifest['name']
 fixture_path=HERE/(name+'_assembly-mm.step');q=b.read_step(fixture_path)[0][0]
 checks=[]
 def add(name,ok,**e):checks.append(dict(name=name,status='PASS' if ok else 'FAIL',**e))
 for ref,ob in [('P01',frame),('P05',old['P05']),('H040',old['H040']),('H041',old['H041'])]:
  v=overlap(q,ob);add('Q01 seated / '+ref,v<1e-6,overlap_mm3=v)
 # Tangential solid-common may discard faces, so use a0.001mm signed
 # penetration witness on each datum and exact zero gap in seated position.
 for label,ob,delta,expected in [
  ('fixed X-12 reaction',frame,[-.001,0,0],249.6),
  ('grounded Z2.7 pocket floor',frame,[0,0,-.001],48.),
  ('P05 X1 shoulder',old['P05'],[.001,0,0],np.pi*(4**2-1.6**2)),
 ]:
  area=overlap(r7.tr(q,delta),ob)/.001;gap=b.gap(q,ob)
  add(label+' contact',abs(area-expected)<.01 and gap<1e-7,
      area_from_1um_penetration_mm2=area,expected_mm2=expected,seated_gap_mm=gap)
 maxv=0
 for u in np.linspace(0,30,61):maxv=max(maxv,overlap(q,r7.tr(old['P04'],[-float(u),0,0])))
 add('Unloaded carriage complete30mm motion',maxv<1e-6,maximum_overlap_mm3=maxv,poses=61)
 maxv=0
 for d in np.linspace(0,12,49):maxv=max(maxv,overlap(q,r7.tr(old['P05'],[float(d),0,0])))
 add('P05 withdraws +X12 from plain Q01 tail',maxv<1e-6,maximum_overlap_mm3=maxv,poses=49)
 maxv=0
 for d in np.linspace(0,40,81):
  for obstacle in [frame,r7.tr(old['P05'],[12,0,0])]:maxv=max(maxv,overlap(r7.tr(q,[0,0,float(d)]),obstacle))
 add('Q01 +Z40 removal after P05 +X12',maxv<1e-6,maximum_overlap_mm3=maxv,poses=81)
 mesh=trimesh.load(HERE/(name+'_print-mm.stl'),force='mesh')
 # Any downward surface steeper than a45° overhang must be the bed face.
 severe=(mesh.face_normals[:,2]<-.72)&(mesh.triangles_center[:,2]>.001)
 add('Support-free print geometry',not np.any(severe),unsupported_steep_area_mm2=float(mesh.area_faces[severe].sum()),
     reaction_face_down=True,integral_shoulder_taper_degrees=45)
 add('One closed positive STL',mesh.is_watertight and mesh.is_volume and len(mesh.split())==1,
     bounds_mm=mesh.bounds.tolist(),volume_mm3=float(mesh.volume))
 status='PASS_Q01_NATIVE_FIT' if args.native else 'PASS_Q01_LOCAL_FIXED_FRONT_FIT'
 if any(r['status']=='FAIL' for r in checks):status='FAIL'
 result=dict(status=status,checks=checks,**native_binding,baseline_native_step_sha256=inv['native_step_sha256'],
  files_sha256={str(p.relative_to(ROOT)):sha(p) for p in [fixture_path,HERE/'manifest.json',HERE/(name+'_print-mm.stl')]+([] if args.native else [args.frame_step])},
  frame_scope='P01 extracted from native assembly at native_P01_solid_index' if args.native else 'Local fixed-front candidate; repeat against final native export',
  limitations=['Unloaded CAD geometry only; not physical print, sensor, switch, force or lifetime qualification.',
   'Sensor stack, springs, spring seats and isometric sleeves must be absent when Q01 is fitted.',
   'Y-axis alignment comes from P05/rods; the foot provides vertical location, no axial latch.'])
 if args.native:
  result['files_sha256'].update({str(p.relative_to(ROOT)):sha(p) for p in [native_inventory,native_assembly]})
 (REVIEW/'validation/fixture-q01-check.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps(dict(status=status,checks=len(checks),failed=[r for r in checks if r['status']=='FAIL']),indent=2))
if __name__=='__main__':main()
