from pathlib import Path
import importlib.util,json
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_EDGE
from OCP.TopoDS import TopoDS
from OCP.BRepAdaptor import BRepAdaptor_Curve
from OCP.BRepFilletAPI import BRepFilletAPI_MakeFillet
from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut
r=Path(__file__).resolve().parents[3];spec=importlib.util.spec_from_file_location('r16',r/'review/upright-grip-2026-11-09/mechanics/upright_grip.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);b=m.b
inv=json.loads((r/'review/upright-grip-2026-11-09/validation/native-step-inventory.json').read_text());solids,_,_=b.read_step(inv['native_step']);old={k:solids[v['candidates'][0]['solid_index']] for k,v in inv['native_part_correspondence'].items()};frame=old['P01']
for sign in [-1,1]:
 yz=[(sign*y,z) for y,z in [(59.0,16.5),(63,16.5),(65,18.5),(65,24.1),(59.0,24.1)]]
 gusset=m.r7.xprism(-24,-8,yz);f=BRepFilletAPI_MakeFillet(gusset);ex=TopExp_Explorer(gusset,TopAbs_EDGE);seen=[]
 while ex.More():
  e=TopoDS.Edge(ex.Current());ex.Next()
  if any(e.IsSame(x) for x in seen):continue
  seen.append(e);bb=b.bounds(e)
  if abs(bb[0,2]-16.5)<1e-6 and abs(bb[1,2]-16.5)<1e-6 and bb[1,0]-bb[0,0]>13:f.Add(.6,e)
 f.Build();assert f.IsDone();gusset=f.Shape()
 f=BRepFilletAPI_MakeFillet(gusset);ex=TopExp_Explorer(gusset,TopAbs_EDGE);seen=[]
 while ex.More():
  e=TopoDS.Edge(ex.Current());ex.Next()
  if any(e.IsSame(x) for x in seen):continue
  seen.append(e);bb=b.bounds(e)
  if abs(bb[1,0]-bb[0,0])<1e-6 and abs(abs(bb[0,1])-65)<1e-6 and abs(bb[1,1]-bb[0,1])<1e-6 and bb[1,2]-bb[0,2]>4:f.Add(2,e)
 f.Build();assert f.IsDone();gusset=f.Shape();assert BRepCheck_Analyzer(gusset).IsValid();frame=b.fuse(frame,gusset)
from OCP.ShapeUpgrade import ShapeUpgrade_UnifySameDomain
print('Joinedvalid',BRepCheck_Analyzer(frame).IsValid(),flush=True);assert BRepCheck_Analyzer(frame).IsValid()
tools=[]
for y in [-75,75]:
 tool=m.r7.cyl([-24,y,20],[-24,y,40],14)
 ex=TopExp_Explorer(tool,TopAbs_EDGE);f=BRepFilletAPI_MakeFillet(tool);seen=[]
 while ex.More():
  e=TopoDS.Edge(ex.Current());ex.Next()
  if any(e.IsSame(x) for x in seen):continue
  seen.append(e);bb=b.bounds(e)
  if abs(bb[0,2]-20)<1e-6 and abs(bb[1,2]-20)<1e-6:f.Add(2,e)
 f.Build();assert f.IsDone();tool=f.Shape();assert BRepCheck_Analyzer(tool).IsValid();tools.append(tool)
 frame=b.cut(frame,tool)
removed=b.cut(old['P01'],frame)
print('valid',BRepCheck_Analyzer(frame).IsValid(),'removed',b.volume(removed),b.bounds(removed).tolist(),flush=True)
seen=[];chosen=[];ex=TopExp_Explorer(frame,TopAbs_EDGE)
while ex.More():
 e=TopoDS.Edge(ex.Current());ex.Next()
 if any(e.IsSame(x) for x in seen):continue
 seen.append(e);bb=b.bounds(e)
 if bb[0,1]>60.9 and bb[1,0]<-9 and bb[0,0]>-36 and bb[1,2]>13.9:
  a=BRepAdaptor_Curve(e);p=a.Value((a.FirstParameter()+a.LastParameter())/2)
  print(len(chosen),'type',str(a.GetType()),'bbox',bb.round(5).tolist(),'mid',list(p.Coord()),flush=True)
  chosen.append(e)
for y in [-51,51]:
 rod=m.r7.cyl([-17,y,18],[-7,y,18],3.1)
 print('removed to bore',y,b.gap(removed,rod),flush=True)
print('removed to H18',b.gap(removed,m.r7.cyl([-12.8,-72,8.5],[-12.8,72,8.5],3.2)),flush=True)

import math
cut_edges=[];ex=TopExp_Explorer(frame,TopAbs_EDGE)
while ex.More():
 e=TopoDS.Edge(ex.Current());ex.Next()
 if any(e.IsSame(x) for x in cut_edges):continue
 a=BRepAdaptor_Curve(e);pts=[a.Value(a.FirstParameter()+(a.LastParameter()-a.FirstParameter())*t) for t in [.2,.5,.8]]
 if all(abs(math.hypot(p.X()+24,abs(p.Y())-75)-14)<1e-4 for p in pts):cut_edges.append(e)
print('Cut edges',len(cut_edges),flush=True)
m.prior.export(frame,Path(__file__).parent/'P01_unrounded')
es=[e for e in cut_edges if (lambda bb:bb[0,2]>28 or (bb[1,2]-bb[0,2]>1 and abs(bb[1,0]-bb[0,0])<1e-6))(b.bounds(e))]
print('Final edges',len(es),flush=True)
for radius in [.8,.6,.4]:
 f=BRepFilletAPI_MakeFillet(frame)
 for e in es:f.Add(radius,e)
 f.Build();print('FILLET',radius,f.IsDone(),flush=True)
 if f.IsDone():
  print('VALID',BRepCheck_Analyzer(f.Shape()).IsValid(),flush=True)
  if BRepCheck_Analyzer(f.Shape()).IsValid():m.prior.export(f.Shape(),Path(__file__).parent/'P01_round_topmouth')
