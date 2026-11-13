#!/usr/bin/env python3
"""R17 local prototype: mirrored side thumb scallops in fixed P01 only.
Frozen R16 native STEP and source are inputs, never modified by this module.
"""
from pathlib import Path
import hashlib,importlib.util,json,math
import numpy as np
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepFilletAPI import BRepFilletAPI_MakeFillet
from OCP.BRepAdaptor import BRepAdaptor_Curve
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_EDGE,TopAbs_SOLID,TopAbs_SHELL
from OCP.TopoDS import TopoDS
HERE=Path(__file__).resolve().parent;STUDY=HERE.parent;ROOT=STUDY.parents[1]
R16=ROOT/'review/upright-grip-2026-11-09'
s=importlib.util.spec_from_file_location('side_thumb_r16',R16/'mechanics/upright_grip.py');r16=importlib.util.module_from_spec(s);s.loader.exec_module(r16)
b,r7,prior=r16.b,r16.r7,r16.prior
BASE_SOURCE=R16/'fingerworker_R16_upright_grip.fs'
BASE_SHA='1f492dd841c35a14f488be418e4f4dd8dea8edb63f3d321a492dc2ec3c907ab4'
SOURCE=STUDY/'fingerworker_R17_side_thumb.fs'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
CX=-24;CY=75;RADIUS=14;FLOOR=20;CUT_TOP=40;BOTTOM_RADIUS=1.5;MOUTH_RADIUS=.4
CHEEK_X=(-24,-8);CHEEK_PROFILE=[(59,16.5),(63,16.5),(65,18.5),(65,24.1),(59,24.1)]
vec=r16.vec

def load():
 inv=json.loads((R16/'validation/native-step-inventory.json').read_text());assert sha(inv['native_step'])==inv['native_step_sha256']
 solids,_,_=b.read_step(inv['native_step'])
 return {ref:solids[v['candidates'][0]['solid_index']] for ref,v in inv['native_part_correspondence'].items()},inv

def edges(shape):
 result=[];ex=TopExp_Explorer(shape,TopAbs_EDGE)
 while ex.More():
  e=TopoDS.Edge(ex.Current());ex.Next()
  if not any(e.IsSame(q) for q in result):result.append(e)
 return result

def middle(edge):
 a=BRepAdaptor_Curve(edge);return list(a.Value((a.FirstParameter()+a.LastParameter())/2).Coord())

def rounded(shape,selected,radius):
 assert selected,'Empty fillet selection';f=BRepFilletAPI_MakeFillet(shape)
 for e in selected:f.Add(radius,e)
 f.Build();assert f.IsDone(),'Fillet failed';out=f.Shape();assert BRepCheck_Analyzer(out).IsValid(),'Invalid fillet result'
 return out

def stocks():
 cheeks=[];tools=[]
 for sign in [-1,1]:
  cheek=r7.xprism(*CHEEK_X,[(sign*y,z) for y,z in CHEEK_PROFILE])
  es=[e for e in edges(cheek) if (lambda bb:abs(bb[0,2]-16.5)<1e-6 and abs(bb[1,2]-16.5)<1e-6 and bb[1,0]-bb[0,0]>15)(b.bounds(e))]
  cheek=rounded(cheek,es,.6)
  es=[e for e in edges(cheek) if (lambda bb:abs(bb[1,0]-bb[0,0])<1e-6 and abs(abs(bb[0,1])-65)<1e-6 and abs(bb[1,1]-bb[0,1])<1e-6 and bb[1,2]-bb[0,2]>4)(b.bounds(e))]
  cheek=rounded(cheek,es,2);cheeks.append(cheek)
  tool=r7.cyl([CX,sign*CY,FLOOR],[CX,sign*CY,CUT_TOP],RADIUS)
  es=[e for e in edges(tool) if (lambda bb:abs(bb[0,2]-FLOOR)<1e-6 and abs(bb[1,2]-FLOOR)<1e-6)(b.bounds(e))]
  tools.append(rounded(tool,es,BOTTOM_RADIUS))
 return dict(cheeks=cheeks,gussets=cheeks,tools=tools)

def mouth_edges(frame):
 found=[]
 for e in edges(frame):
  a=BRepAdaptor_Curve(e);pts=[a.Value(a.FirstParameter()+(a.LastParameter()-a.FirstParameter())*t) for t in [.2,.5,.8]]
  if not all(abs(math.hypot(p.X()-CX,abs(p.Y())-CY)-RADIUS)<1e-4 for p in pts):continue
  bb=b.bounds(e)
  if bb[0,2]>28 or (bb[1,2]-bb[0,2]>1 and abs(bb[1,0]-bb[0,0])<1e-6):found.append(e)
 return found

def build(old):
 g=stocks();frame=old['P01']
 for c in g['cheeks']:frame=b.fuse(frame,c)
 assert BRepCheck_Analyzer(frame).IsValid()
 for t in g['tools']:frame=b.cut(frame,t)
 assert BRepCheck_Analyzer(frame).IsValid()
 es=mouth_edges(frame);picks=[middle(e) for e in es]
 frame=rounded(frame,es,MOUTH_RADIUS)
 return frame,g,picks

def expected(old=None):
 if old is None:old,_=load()
 return {'P01':build(old)[0]}

def patch_source(source,picks):
 assert hashlib.sha256(source.encode()).hexdigest()==BASE_SHA
 anchor='        const integratedFrame=qBodyType(qUnion([body(id + "base"),body(id + "palmPad")]),BodyType.SOLID);'
 assert source.count(anchor)==1
 patch='''        // R17: fixed side thumb seats. P05 and all other parts are unchanged.
        // Small integral cheeks remove the old shoulder/socket step locally.
        // Their lower45deg taper stays above the enclosure catch/tool domains.
'''
 for i,sign in enumerate([-1,1]):
  points=[(sign*y,z) for y,z in CHEEK_PROFILE];name=f'R17Cheek{i}';bodyid=name+'body'
  patch+=f'        makeXPrism(context,id + "{name}",{-24}*mm,{-8}*mm,[{",".join(vec(q) for q in points)}]);\n'
  qs=[f'qContainsPoint(qOwnedByBody(body(id + "{bodyid}"),EntityType.EDGE),{vec([-16,sign*y,16.5])})' for y in [59,63]]
  patch+='        opFillet(context,id + "'+name+'LowerRound",{"entities":qUnion(['+','.join(qs)+']),"radius":0.6*mm,"tangentPropagation":true});\n'
  qs=[f'qContainsPoint(qOwnedByBody(body(id + "{bodyid}"),EntityType.EDGE),{vec([x,sign*65,22])})' for x in [-24,-8]]
  patch+='        opFillet(context,id + "'+name+'OuterRound",{"entities":qUnion(['+','.join(qs)+']),"radius":2*mm,"tangentPropagation":true});\n'
  patch+=f'        join(context,id + "{name}Join",[body(id + "base"),body(id + "{bodyid}")]);\n'
 for i,sign in enumerate([-1,1]):
  name=f'R17ThumbSideTool{i}'
  patch+=f'        makeCylinder(context,id + "{name}",{vec([CX,sign*CY,FLOOR])},{vec([CX,sign*CY,CUT_TOP])},{RADIUS}*mm);\n'
  patch+=f'        opFillet(context,id + "{name}FloorRound",{{"entities":qContainsPoint(qOwnedByBody(body(id + "{name}"),EntityType.EDGE),{vec([CX+RADIUS,sign*CY,FLOOR])}),"radius":{BOTTOM_RADIUS}*mm,"tangentPropagation":true}});\n'
  patch+=f'        cut(context,id + "R17ThumbSideCut{i}",body(id + "base"),body(id + "{name}"));\n'
 patch+='        opFillet(context,id + "R17ThumbSideMouthRound",{"entities":qUnion([\n'
 patch+='            '+',\n            '.join(f'qContainsPoint(qOwnedByBody(body(id + "base"),EntityType.EDGE),{vec(q)})' for q in picks)+f']),"radius":{MOUTH_RADIUS}*mm,"tangentPropagation":true}});\n'
 source=source.replace(anchor,patch+anchor)
 source=source.replace('Fingerworker Flat132 R16 - upright integral palm grip and rounded thumb shoulders.','Fingerworker Flat132 R17 - integral side thumb seats on the fixed palm frame.')
 source=source.replace(' * Central palm stock stays behindX-16; original rod sockets are retained.',' * R17 adds two outside tapered cheeks and rounds open-top side thumb scallops.\n * Rod bores are unchanged; outer socket stock is locally shaped with remaining wall checked.')
 source=source.replace('"Flat132 R16 - upright palm grip"','"Flat132 R17 - rounded side thumb seats"')
 source=source.replace('P01 PRINT STUDY - Flat132 upright palm grip, rounded thumb shoulders, inboard straps','P01 PRINT STUDY - Flat132 rounded side thumb seats, upright palm, inboard straps')
 return source

def export_mesh(shape,path):
 import trimesh
 prior.export(shape,path);meshpath=path.with_suffix('.stl');mesh=trimesh.load(meshpath,process=True)
 bad=mesh.area_faces==0;count=int(bad.sum());assert np.all(mesh.area_faces[bad]==0)
 mesh.update_faces(~bad);mesh.remove_unreferenced_vertices()
 assert mesh.is_watertight and mesh.is_winding_consistent and len(mesh.split())==1
 mesh.export(meshpath)
 return dict(watertight=True,winding_consistent=True,shells=1,zero_area_triangles_removed=count,removed_triangle_area_mm2=0.0,triangles=len(mesh.faces),sha256=sha(meshpath),scope='Only exactly zero-area triangles removed; no hole fill, remeshing or geometry modification.')

def run():
 old,inv=load();frame,g,picks=build(old);rows=[]
 def check(name,condition,**details):rows.append(dict(name=name,status='PASS' if condition else 'FAIL',**details))
 def validvol(shape):assert BRepCheck_Analyzer(shape).IsValid();return b.volume(shape)
 added=b.cut(frame,old['P01']);removed=b.cut(old['P01'],frame)
 check('One valid solid and shell',BRepCheck_Analyzer(frame).IsValid() and b.count(frame,TopAbs_SOLID)==b.count(frame,TopAbs_SHELL)==1)
 for ref,shape in old.items():
  if ref=='P01':continue
  if np.any(b.bounds(frame)[1]<b.bounds(shape)[0]) or np.any(b.bounds(shape)[1]<b.bounds(frame)[0]):continue
  overlap=validvol(b.common(frame,shape));check('Seated separation / '+ref,overlap<1e-6,overlap_mm3=overlap)
 for name,lo,hi in [('lower frame and catch landings',[-60,-70,-10],[140,70,16.49]),('central sensor and guide',[-29,-38,-3],[5,38,40]),('strap region',[12,-70,-3],[105,70,9])]:
  zone=b.box(lo,hi);v=validvol(b.common(added,zone))+validvol(b.common(removed,zone));check('Unchanged '+name,v<1e-6,symmetric_difference_mm3=v)
 boregaps=[]
 for y in [-51,51]:
  bore=r7.cyl([-17,y,18],[-7,y,18],3.1);v=validvol(b.common(frame,bore));gap=b.gap(removed,bore);boregaps.append(gap)
  check('Original rod bore open '+str(y),v<1e-6,overlap_mm3=v);check('Removal distance to rod bore '+str(y),gap>6,minimum_mm=gap)
 for sign in [-1,1]:
  lo,hi=([-29,63.6,-20],[-25.6,66.1,16.2]) if sign>0 else ([-29,-66.1,-20],[-25.6,-63.6,16.2])
  ov=validvol(b.common(added,b.box(lo,hi)));check('P08 full hook flex/removal envelope '+str(sign),ov<1e-6,overlap_mm3=ov)
 route=r7.cyl([-12.8,-72,8.5],[-12.8,72,8.5],3.2);gap=b.gap(added,route)
 check('H18 side tool route clear',validvol(b.common(added,route))<1e-6,addition_gap_mm=gap)
 for ref in ['P04','H060','H061','P11','H10']:
  bb=b.bounds(old[ref]).copy();bb[0,0]-=30.8 if ref in ['P11','H10'] else 30
  if ref in ['P11','H10']:bb[1,0]+=.8
  gap=b.gap(added,b.box(*bb));check('Full motion addition / '+ref,gap>1e-6,gap_lower_bound_mm=gap)
 check('P01 external bounds unchanged',np.max(np.abs(b.bounds(frame)-b.bounds(old['P01'])))<1e-5)
 source=patch_source(BASE_SOURCE.read_text(),picks);SOURCE.write_text(source)
 mesh=export_mesh(frame,HERE/'P01_side_thumb');prior.export(added,HERE/'added_cheeks');prior.export(removed,HERE/'removed_scallops')
 for i,t in enumerate(g['tools']):prior.export(t,HERE/f'side_thumb_tool_{i}')
 spec=dict(revision='R17 candidate',status='LOCAL_PROTOTYPE_PENDING_NATIVE_REGENERATION',source_sha256=sha(SOURCE),baseline_source_sha256=BASE_SHA,baseline_native_step_sha256=inv['native_step_sha256'],changed=['P01'],new_parts=[],other_native_bodies_unchanged=92,
  side_thumb=dict(center_x_mm=CX,center_y_mm=[-CY,CY],cutter_radius_mm=RADIUS,cutter_bottom_z_mm=FLOOR,cutter_top_z_mm=CUT_TOP,bottom_radius_mm=BOTTOM_RADIUS,mouth_radius_mm=MOUTH_RADIUS,maximum_nominal_side_depth_mm=4,opening_chord_at_y65_mm=2*math.sqrt(RADIUS**2-(CY-65)**2),nominal_height_mm=33-FLOOR,actual_removed_bounds_mm=b.bounds(removed).tolist(),cheek_x_mm=list(CHEEK_X),cheek_positive_yz_profile_mm=CHEEK_PROFILE,cheek_lower_edge_radius_mm=.6,cheek_outer_corner_radius_mm=2,existing_wrist_thumb_returns_retained=True),
  added_mm3=validvol(added),removed_mm3=validvol(removed),P01_volume_mm3=validvol(frame),minimum_removal_to_rod_bore_mm=min(boregaps),mouth_selection_points_mm=picks,mesh=mesh,
  preserved='P05 and other92 native bodies, sensor path, rod bores, H18 access, clips, roof and straps. Outer socket stock is locally shaped, not claimed wholly unchanged.',limitations='Local nominal CAD prototype only. Native regeneration, native comparisons, final sliced paths and physical comfort/strength checks remain separate.')
 (HERE/'design-specification.json').write_text(json.dumps(spec,indent=2)+'\n')
 report=dict(status='PASS_LOCAL_SIDE_THUMB' if all(q['status']=='PASS' for q in rows) else 'FAIL',source_sha256=sha(SOURCE),generator_sha256=sha(__file__),checks=rows,metrics=spec)
 (HERE/'preflight.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status=report['status'],checks=len(rows),failures=[q for q in rows if q['status']=='FAIL'],source_sha256=sha(SOURCE),mesh=mesh),indent=2))

if __name__=='__main__':run()
