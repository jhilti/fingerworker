from pathlib import Path
import sys,json
sys.path.insert(0,str(Path(__file__).parent));import thumb_rim as m
from OCP.BRepTools import BRepTools
from OCP.BRep import BRep_Builder,BRep_Tool
from OCP.TopoDS import TopoDS_Shape
from OCP.TopExp import TopExp
from OCP.BRepFilletAPI import BRepFilletAPI_MakeFillet
from OCP.BRepCheck import BRepCheck_Analyzer
raw=TopoDS_Shape();BRepTools.Read_s(raw,str(m.HERE/'raw_mouth.brep'),BRep_Builder())
f=BRepFilletAPI_MakeFillet(raw)
for e in m.r17.mouth_edges(raw):f.Add(.4,e)
settings=[]
for i in range(1,f.NbContours()+1):
 seen=[]
 for j in range(1,f.NbEdges(i)+1):
  e=f.Edge(i,j)
  for v in [TopExp.FirstVertex_s(e),TopExp.LastVertex_s(e)]:
   if any(v.IsSame(s) for s in seen):continue
   seen.append(v);p=BRep_Tool.Pnt_s(v);r=.4
   if p.X()<-27.5 and p.Z()>27.9:r=1
   if p.Z()>32:r=2
   f.SetRadius(r,i,v);settings.append(dict(contour=i,point=list(p.Coord()),radius=r))
f.Build();d=dict(status='VALID' if f.IsDone() and BRepCheck_Analyzer(f.Shape()).IsValid() else 'FAILED',done=f.IsDone(),settings=settings)
if d['status']=='VALID':m.prior.export(f.Shape(),m.HERE/'variable_native_like_probe')
(m.HERE/'variable-local-probe.json').write_text(json.dumps(d,indent=2))
