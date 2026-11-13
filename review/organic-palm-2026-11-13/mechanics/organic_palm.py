#!/usr/bin/env python3
"""R18 organic palm bolster, based on frozen R17 thumb seats and R16 native CAD."""
from pathlib import Path
import hashlib,importlib.util,json,math
import numpy as np
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeEdge,BRepBuilderAPI_MakeWire,BRepBuilderAPI_MakeFace
from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism
from OCP.BRepOffsetAPI import BRepOffsetAPI_ThruSections
from OCP.GC import GC_MakeArcOfCircle
from OCP.gp import gp_Pnt,gp_Vec
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepBndLib import BRepBndLib
from OCP.Bnd import Bnd_Box
from OCP.TopAbs import TopAbs_SOLID,TopAbs_SHELL
HERE=Path(__file__).resolve().parent;STUDY=HERE.parent;ROOT=STUDY.parents[1]
R17=ROOT/'review/side-thumb-2026-11-12'
s=importlib.util.spec_from_file_location('organic_r17',R17/'mechanics/side_thumb.py');r17=importlib.util.module_from_spec(s);s.loader.exec_module(r17)
b,r7,prior,vec=r17.b,r17.r7,r17.prior,r17.vec
BASE_SOURCE=R17/'fingerworker_R17_side_thumb.fs'
BASE_SHA='780dfdbaf9c6ab4bf4bbf3ab3de0dab3f9ac7dc5f8de49cf015c51ee95cc16e4'
SOURCE=STUDY/'fingerworker_R18_organic_palm.fs'
sha=r17.sha
# y, crown z, left/right top tangent x, back/front radii, lower section z.
HALF_SECTIONS=[(0,34.5,-23.5,-20.5,7.5,4,21.5),
               (30,34.1,-23.5,-20.5,7.4,4,21.5),
               (43,33.7,-23.5,-12.7,5.6,4.7,26.1),
               (58,33,-24,-12,5,4,26)]
SECTIONS=[(-q[0],*q[1:]) for q in HALF_SECTIONS[:0:-1]]+HALF_SECTIONS
TRIM=([-40,-58,30],[-7.9,58,40])
FORWARD_ENVELOPE=[(-40,-60),(-8,-60),(-8,-43),(-16,-32),(-16,32),(-8,43),(-8,60),(-40,60)]
def load():return r17.load()
def tight_bounds(shape):
 bb=Bnd_Box();BRepBndLib.AddOptimal_s(shape,bb,False,False);return np.array([bb.CornerMin().Coord(),bb.CornerMax().Coord()])
def bolster_bounds(shape):
 # OCC's untriangulated BSpline bounds can include trimmed-off surface stock.
 # Intersect that conservative box with the exact analytic clipping envelope.
 bounds=tight_bounds(shape);bounds[0]=np.maximum(bounds[0],[-40,-60,15]);bounds[1]=np.minimum(bounds[1],[-8,60,40]);return bounds
def section(row):
 y,zt,xl,xr,rb,rf,z0=row;zc=zt-rb
 assert abs(z0-zc)<rb and z0<=zc
 a=(xl-math.sqrt(rb*rb-(z0-zc)**2),z0);m=(xl-rb,zc);t=(xl,zt)
 # The lower front edge slopes out of retained root stock. Side sections lie
 # within the existing rod-socket shoulders and do not need a forward ramp.
 root_x=-22.5 if abs(y)<=30 else xr+rf
 u=(xr,zt);fm=(xr+rf/math.sqrt(2),zt-rf+rf/math.sqrt(2));v=(xr+rf,zt-rf);r=(root_x,z0)
 return [('arc',a,m,t),('line',t,u),('arc',u,fm,v),('line',v,r),('line',r,a)]
def loft():
 maker=BRepOffsetAPI_ThruSections(True,False,1e-6);maker.CheckCompatibility(False);maker.SetMaxDegree(3)
 for row in SECTIONS:
  y=row[0];p=lambda xz:gp_Pnt(xz[0],y,xz[1]);wire=BRepBuilderAPI_MakeWire()
  for typ,*pts in section(row):
   edge=BRepBuilderAPI_MakeEdge(GC_MakeArcOfCircle(*[p(q) for q in pts]).Value()).Edge() if typ=='arc' else BRepBuilderAPI_MakeEdge(*[p(q) for q in pts]).Edge()
   wire.Add(edge)
  maker.AddWire(wire.Wire())
 maker.Build();assert maker.IsDone(),'Loft failed';shape=maker.Shape();assert BRepCheck_Analyzer(shape).IsValid(),'Invalid loft'
 return shape
def build(old):
 base=r17.expected(old)['P01'];bolster=loft();wire=BRepBuilderAPI_MakeWire()
 for p,q in zip(FORWARD_ENVELOPE,FORWARD_ENVELOPE[1:]+FORWARD_ENVELOPE[:1]):
  wire.Add(BRepBuilderAPI_MakeEdge(gp_Pnt(*p,15),gp_Pnt(*q,15)).Edge())
 envelope=BRepPrimAPI_MakePrism(BRepBuilderAPI_MakeFace(wire.Wire()).Face(),gp_Vec(0,0,25)).Shape()
 bolster=b.common(bolster,envelope);frame=b.fuse(b.cut(base,b.box(*TRIM)),bolster)
 assert BRepCheck_Analyzer(frame).IsValid(),'Invalid frame'
 return frame,base,bolster
def expected(old=None):
 if old is None:old,_=load()
 return {'P01':build(old)[0]}
def patch_source():
 source=BASE_SOURCE.read_text();assert sha(BASE_SOURCE)==BASE_SHA
 for i in [0,1]:source=source.replace(f'body(id + "R17Cheek{i}body")',f'body(id + "R17Cheek{i}" + "body")')
 anchor='        const integratedFrame=qBodyType(qUnion([body(id + "base"),body(id + "palmPad")]),BodyType.SOLID);'
 assert source.count(anchor)==1
 patch='        // R18: matched rounded profiles form one broad, gently cambered palm bolster.\n'
 names=[]
 for i,row in enumerate(SECTIONS):
  name=f'R18PalmSection{i}';names.append(name)
  patch+=f'        var {name}=newSketchOnPlane(context,id + "{name}",{{"sketchPlane":plane({vec([0,row[0],0])},vector(0,-1,0),vector(1,0,0))}});\n'
  for j,(typ,*pts) in enumerate(section(row)):
   if typ=='arc':patch+=f'        skArc({name},"edge{j}",{{"start":{vec(pts[0])},"mid":{vec(pts[1])},"end":{vec(pts[2])}}});\n'
   else:patch+=f'        skLineSegment({name},"edge{j}",{{"start":{vec(pts[0])},"end":{vec(pts[1])}}});\n'
  patch+=f'        skSolve({name});\n'
 patch+='        opLoft(context,id + "R18PalmBolster",{"profileSubqueries":['+','.join(f'qSketchRegion(id + "{n}")' for n in names)+'],"bodyType":ToolBodyType.SOLID});\n'
 patch+='        opDeleteBodies(context,id + "R18ProfileCleanup",{"entities":qUnion(['+','.join(f'qCreatedBy(id + "{n}",EntityType.BODY)' for n in names)+'])});\n'
 patch+='        makeZPrismR12(context,id + "R18ForwardEnvelope",15*mm,40*mm,['+','.join(vec(q) for q in FORWARD_ENVELOPE)+']);\n'
 patch+='        opBoolean(context,id + "R18BoundedBolster",{"tools":qUnion([body(id + "R18PalmBolster"),body(id + "R18ForwardEnvelope" + "body")]),"operationType":BooleanOperationType.INTERSECTION});\n'
 patch+=f'        makeBox(context,id + "R18CrownTrim",{vec(TRIM[0])},{vec(TRIM[1])});\n'
 patch+='        cut(context,id + "R18CrownTrimCut",body(id + "base"),body(id + "R18CrownTrim"));\n'
 patch+='        join(context,id + "R18PalmUnion",[body(id + "base"),body(id + "R18BoundedBolster")]);\n'
 source=source.replace(anchor,patch+anchor).replace('Flat132 R17 - rounded side thumb seats','Flat132 R18 - organic palm bolster and side thumb seats')
 source=source.replace('Fingerworker Flat132 R17 - integral side thumb seats on the fixed palm frame.','Fingerworker Flat132 R18 - organic palm bolster and integral side thumb seats.')
 source=source.replace('P01 PRINT STUDY - Flat132 rounded side thumb seats, upright palm, inboard straps','P01 PRINT STUDY - Flat132 organic palm bolster, side thumb seats, inboard straps')
 return source
def run():
 old,inv=load();frame,base,bolster=build(old);SOURCE.write_text(patch_source())
 mesh=r17.export_mesh(frame,HERE/'P01_organic_palm');prior.export(bolster,HERE/'organic_bolster')
 spec=dict(revision='R18 candidate',status='LOCAL_PROTOTYPE_PENDING_NATIVE_REGENERATION',source_sha256=sha(SOURCE),baseline_R17_source_sha256=BASE_SHA,changed=['P01'],new_parts=[],other_native_bodies_unchanged=92,
  sections=[dict(y_mm=q[0],crown_z_mm=q[1],top_left_x_mm=q[2],top_right_x_mm=q[3],back_radius_mm=q[4],front_radius_mm=q[5],floor_z_mm=q[6],edges=section(q)) for q in SECTIONS],crown_trim_mm=TRIM,forward_envelope_xy_mm=FORWARD_ENVELOPE,loft_bounds_mm=bolster_bounds(bolster).tolist(),P01_bounds_mm=tight_bounds(frame).tolist(),P01_volume_mm3=b.volume(frame),mesh=mesh)
 (HERE/'design-specification.json').write_text(json.dumps(spec,indent=2)+'\n')
 print(json.dumps(dict(status='BUILT_VALID_LOCAL_PREVIEW',source_sha256=sha(SOURCE),bounds=spec['P01_bounds_mm'],mesh=mesh),indent=2))
if __name__=='__main__':run()
