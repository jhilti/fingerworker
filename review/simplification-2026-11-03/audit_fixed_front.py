#!/usr/bin/env python3
"""Independent exported-frame audit: fixed sensor force path and real service.

Reads STEP bodies; does not call front_fixed.py or reproduce its CSG build.
"""
from pathlib import Path
import argparse,hashlib,json,sys
import numpy as np
from OCP.BRepCheck import BRepCheck_Analyzer
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE));import rear_gate as rear
b,r7=rear.b,rear.r7
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
REMOVED={'H11','H13','H15','H160','H161','H170','H171','H21','H22'}
def overlap(a,c):
 aa,cc=b.bounds(a),b.bounds(c)
 if np.any(aa[1]<cc[0]) or np.any(cc[1]<aa[0]):return 0.
 q=b.common(a,c);assert BRepCheck_Analyzer(q).IsValid(),'Invalid Boolean'
 return b.volume(q)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--frame-step',type=Path,default=HERE/'front/P01_fixed_front.step');ap.add_argument('--native',action='store_true');args=ap.parse_args();args.frame_step=args.frame_step.resolve()
 old,inv=rear.load();frame=b.read_step(args.frame_step)[0][0];checks=[]
 native_binding={}
 if args.native:
  current=json.loads((HERE/'validation/native-step-inventory.json').read_text())
  assert sha(current['native_step'])==current['native_step_sha256']
  native_binding=dict(native_assembly_step_sha256=current['native_step_sha256'],native_P01_solid_index=current['native_part_correspondence']['P01']['candidates'][0]['solid_index'])
 def add(name,ok,**e):checks.append(dict(name=name,status='PASS' if ok else 'FAIL',**e))
 retained=['H01','H02','H12','H20','H23','P05']+[f'H24{i}' for i in range(4)]+[f'H25{i}' for i in range(4)]+['H180','H181','H190','H191']
 for ref in retained:
  v=overlap(frame,old[ref]);add('Fixed frame / retained '+ref,v<1e-6,overlap_mm3=v)
 # Entire frame remains clear of moving P05 and the actual sensor/pusher;
 # only H12 has intended direct reaction contact.
 for ref in ['P05','H01','H02','H23']:
  d=b.gap(frame,old[ref]);add('No rigid frame bypass through '+ref,d>1e-6,minimum_gap_mm=d)
 contact=overlap(frame,r7.tr(old['H12'],[-.001,0,0]))/.001
 add('H12 reacts at fixed X-12 plane',abs(contact-454.4)<.02,
     area_from_1um_penetration_mm2=contact,nominal_area_mm2=454.4)
 # Remove spring energy, rear gate, rods and H18/H19; extract the entire
 # sensor+keeper+pusher+yoke together, not an individually detached sensor.
 stack=['H01','H02','H050','H051','H12','H20','H23','P05']+[f'H24{i}' for i in range(4)]+[f'H25{i}' for i in range(4)]
 maxv=0.;worst=None
 for mode,values in [('forward',np.linspace(0,3.2,17)),('up',np.linspace(0,40,41))]:
  for d in values:
   delta=[float(d),0,0] if mode=='forward' else [3.2,0,float(d)]
   for ref in stack:
    v=overlap(frame,r7.tr(old[ref],delta))
    if v>maxv:maxv=v;worst=dict(ref=ref,mode=mode,d_mm=float(d))
 add('Complete real sensor-yoke service +X3.2 then+Z40',maxv<1e-6,
     maximum_overlap_mm3=maxv,worst=worst,poses=58,
     prerequisites='Springs unloaded/removed; rear gate and rods removed; H18/H19 removed')
 for side,i in [(-1,0),(1,1)]:
  for ref in [f'H18{i}',f'H19{i}']:
   v=max(overlap(frame,r7.tr(old[ref],[0,side*float(d),0])) for d in np.linspace(0,55,56))
   add(ref+' outward removal +55mm',v<1e-6,maximum_overlap_mm3=v,poses=56)
 result=dict(status=('PASS_INDEPENDENT_NATIVE_FIXED_FRONT' if args.native else 'PASS_INDEPENDENT_LOCAL_FIXED_FRONT') if all(r['status']=='PASS' for r in checks) else 'FAIL',
  checks=checks,**native_binding,files_sha256={str(args.frame_step.relative_to(ROOT)):sha(args.frame_step)},
  baseline_native_step_sha256=inv['native_step_sha256'],removed_refs=sorted(REMOVED),
  fixed_motion=dict(p_mm=0,a_mm=0,travel_mm=30,iso_approach_mm=15),
  limitations=['Exact exported CAD sampled nominal paths; not physical fit/load/creep/sensor qualification.',
   'Retained hardware identity and final native source/export correspondence require final integration audit.'])
 (HERE/'independent-fixed-front-check.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps(dict(status=result['status'],checks=len(checks),failed=[r for r in checks if r['status']=='FAIL']),indent=2))
if __name__=='__main__':main()
