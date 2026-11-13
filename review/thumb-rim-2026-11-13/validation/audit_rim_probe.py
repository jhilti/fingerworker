#!/usr/bin/env python3
"""Focused native variable-rim measurement; not a final assembly release."""
from pathlib import Path
import importlib.util,json
import numpy as np
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeVertex
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
from OCP.gp import gp_Pnt
from OCP.TopAbs import TopAbs_SOLID,TopAbs_SHELL,TopAbs_FACE
HERE=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('rim_measure',HERE/'rim_measurements.py');r=importlib.util.module_from_spec(s);s.loader.exec_module(r);b=r.b

def main():
 binding_path=r.STUDY/'native-probe/probe-binding.json';binding=json.loads(binding_path.read_text());step=r.ROOT/binding['native_step'];source=r.ROOT/binding['source']
 assert r.sha(step)==binding['native_step_sha256'] and r.sha(source)==binding['source_sha256'] and binding['source_readback_exact']
 old,_,release=r.baseline();shapes,inventory,_=b.read_step(step)
 candidates=[i for i,q in enumerate(inventory) if q['bounds_mm'][0][0]<-40 and q['bounds_mm'][1][0]>120 and q['bounds_mm'][1][1]-q['bounds_mm'][0][1]>130];assert len(candidates)==1
 frame=shapes[candidates[0]];r.a.enable_native_boundary_tolerance()
 checks=[]
 def add(name,ok,**details):checks.append(dict(name=name,status='PASS' if bool(ok) else 'FAIL',**details))
 add('One valid native P01 solid and shell',BRepCheck_Analyzer(frame).IsValid() and b.count(frame,TopAbs_SOLID)==b.count(frame,TopAbs_SHELL)==1)
 # Partition the complement of the permitted side-rim boxes. These small
 # retained intersections avoid coincident full-loft classification failures.
 rois={'lower_frame':([-50,-70,-5],[140,70,21.49]),'central_palm_and_sensor':([-50,-58.7,-5],[140,58.7,40]),'front_of_rims':([-12,-70,21.49],[140,70,40]),'wristward_of_rims':([-50,-70,21.49],[-32,70,40]),'above_rims':([-50,-70,33.2],[140,70,40])}
 for name,(lo,hi) in rois.items():
  roi=b.box(lo,hi);before=b.common(old['P01'],roi);after=b.common(frame,roi);inc=b.cut(after,before);rem=b.cut(before,after)
  valid=all(BRepCheck_Analyzer(q).IsValid() for q in [before,after,inc,rem]);empty=all(b.count(q,TopAbs_SOLID)==0 and b.count(q,TopAbs_FACE)==0 for q in [inc,rem])
  add('Protected native region unchanged: '+name,valid and empty,bounds_mm=[lo,hi],added_solids=b.count(inc,TopAbs_SOLID),removed_solids=b.count(rem,TopAbs_SOLID),added_faces=b.count(inc,TopAbs_FACE),removed_faces=b.count(rem,TopAbs_FACE))
 masks=[r.a.a.side_box(-32,-12,58.7,65.2,21.49,33.2,sign) for sign in [-1,1]]
 mask=r.a.a.union(masks)
 for ref in ['P04','H060','H061','P11','H10']:
  lo,hi=(-30.8,.8) if ref in ['P11','H10'] else (-30,0)
  bounds=b.bounds(old[ref]).copy();bounds[0,0]+=lo;bounds[1,0]+=hi;clearance=b.gap(mask,b.box(bounds[0],bounds[1]))
  add('Entire possible rim-change domain clears full travel '+ref,clearance>1e-6,clearance_lower_bound_mm=clearance,travel_interval_mm=[lo,hi])
 # Use the independently certified R16 native pocket void, unchanged in R18.
 old16,_,_=r.a.a.baseline();raw_builder=r.a.a.r16;raw=raw_builder.profile(-63,63,raw_builder.RAIL_LINES,raw_builder.RAIL_ARCS,3,[raw_builder.RAIL_MID]);void=b.cut(raw,old16['P01']);assert BRepCheck_Analyzer(void).IsValid()
 # Surface witnesses below identify every continuous new top/wrist patch.
 floor=r.module('rim_floor',r.ROOT/'review/side-thumb-2026-11-12/validation/probe_floor.py');before=floor.sections(old['P01']);after=floor.sections(frame)
 bm={(q['x_mm'],q['y_mm']):q for q in before};am={(q['x_mm'],q['y_mm']):q for q in after};missing=sorted(set(bm)-set(am));error=max((max(abs(np.array(am[k]['material_z_mm'])-bm[k]['material_z_mm'])) for k in set(bm)&set(am)),default=0)
 add('Previously measured lower lip sections retained',not missing and error<1e-5,section_count=len(bm),missing_sections=missing,maximum_section_change_mm=float(error),baseline_minimum_sampled_thickness_mm=min(q['floor_thickness_mm'] for q in before),new_minimum_sampled_thickness_mm=min(q['floor_thickness_mm'] for q in after))
 picks=json.loads((r.STUDY/'mechanics/native-face-picks.json').read_text())['faces'];fs=r.faces(frame);measurements=[]
 for pick in picks:
  vertex=BRepBuilderAPI_MakeVertex(gp_Pnt(*pick['point_mm'])).Vertex();dist=BRepExtrema_DistShapeShape(vertex,frame);dist.Perform();assert dist.IsDone()
  point=dist.PointOnShape2(1);pv=BRepBuilderAPI_MakeVertex(point).Vertex();hits=[]
  for index,face in enumerate(fs):
   if b.gap(pv,face)>2e-5:continue
   try:
    measured=r.curvature_at(face,list(point.Coord()));radii=[q for q in measured['principal_radii_mm'] if q is not None]
    if radii:hits.append(dict(face_zero_index=index,equivalent_minimum_radius_mm=min(radii),**measured))
   except Exception:pass
  assert hits,'No measurable native face at rim witness'
  target=1 if pick['point_mm'][2]<28 else 2
  best=min(hits,key=lambda q:abs(q['equivalent_minimum_radius_mm']-target));measurements.append(dict(baseline_face_index=pick['native_face_index'],baseline_point_mm=pick['point_mm'],nearest_new_point_mm=list(point.Coord()),witness_displacement_mm=float(dist.Value()),target_peak_radius_mm=target,**best))
 for sign in [-1,1]:
  pocket=b.common(void,r.a.a.side_box(-30,-24.5,42,60,14,26,sign));assert BRepCheck_Analyzer(pocket).IsValid()
  indices=sorted(set(q['face_zero_index'] for q in measurements if q['baseline_point_mm'][1]*sign>0))
  distances=[dict(face_zero_index=i,distance_to_pocket_mm=b.gap(fs[i],pocket)) for i in indices]
  web=min([3.0895691150462334]+[q['distance_to_pocket_mm'] for q in distances])
  add('Remaining wrist-return web '+str(sign),web>=2.4,baseline_web_mm=3.0895691150462334,new_minimum_web_mm=web,declared_geometric_minimum_mm=2.4,native_surface_distances=distances,meaning='CAD spacing between continuous new rim surfaces and retained pocket void; no strength qualification')
 for q in measurements:
  label='Wrist' if q['target_peak_radius_mm']==1 else 'Upper'
  if q['baseline_face_index'] in [345,360]:ok=.85<=q['equivalent_minimum_radius_mm']<=1.15
  elif q['baseline_face_index'] in [344,365]:ok=1.8<=q['equivalent_minimum_radius_mm']<=2.2
  else:ok=q['equivalent_minimum_radius_mm']>.5
  add(label+' rim witness '+str(q['baseline_face_index']),ok,**q)
 report=dict(status='PASS_NATIVE_R19_RIM_PROBE' if all(q['status']=='PASS' for q in checks) else 'REVIEW_NATIVE_R19_RIM_PROBE',source_sha256=binding['source_sha256'],native_step_sha256=binding['native_step_sha256'],baseline_native_step_sha256=release['native_step_sha256'],baseline_release_binding_sha256=r.sha(r.BASE/'validation/native-release-binding.json'),probe_binding_sha256=r.sha(binding_path),validator_sha256=r.sha(__file__),functional_boolean_boundary_tolerance_mm=1e-6,checks=checks,rim_measurements=measurements,failures=[q for q in checks if q['status']!='PASS'],scope='Focused rim-only native checkpoint. Whole-frame stock subtraction is deliberately not used: coincident freeform face classification was unreliable; five exact protected-region comparisons confine the change and conservative full-travel envelopes cover all possible stock in that domain. R1/R2 are variable-radius targets; measured curvature varies in corner transitions. Final assembly identities and rigid mounting changes require the final integrated export. No blanket strength qualification.')
 assert r.sha(source)==binding['source_sha256'] and r.sha(step)==binding['native_step_sha256']
 (HERE/'rim-probe-check.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status=report['status'],checks=len(checks),failures=report['failures'],rim_measurements=measurements),indent=2))
if __name__=='__main__':main()
