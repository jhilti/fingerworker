import side_thumb as m
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepFilletAPI import BRepFilletAPI_MakeFillet
from OCP.BRepAdaptor import BRepAdaptor_Curve
import math
old,_=m.load();g=m.stocks();
def cutedges(shape):
 out=[]
 for e in m.edges(shape):
  a=BRepAdaptor_Curve(e);pts=[a.Value(a.FirstParameter()+(a.LastParameter()-a.FirstParameter())*t) for t in [.2,.5,.8]]
  if all(abs(math.hypot(p.X()-m.CX,abs(p.Y())-m.CY)-m.RADIUS)<1e-4 for p in pts):out.append(e)
 return out
for name,frame in [('plain',old['P01'])]:
 for tool in g['tools']:frame=m.b.cut(frame,tool)
 es=[e for e in cutedges(frame) if (lambda bb:bb[0,2]>28 or (bb[1,2]-bb[0,2]>1 and abs(bb[1,0]-bb[0,0])<1e-6) or (abs(bb[0,2]-24)<1e-6 and abs(bb[1,2]-24)<1e-6))(m.b.bounds(e))]
 print(name,'edges',len(es),flush=True)
 f=BRepFilletAPI_MakeFillet(frame)
 for e in es:f.Add(.8,e)
 f.Build();print('BASE',f.IsDone(),flush=True)
 if not f.IsDone():continue
 frame=f.Shape();print('BASEVALID',BRepCheck_Analyzer(frame).IsValid(),flush=True)
 if not BRepCheck_Analyzer(frame).IsValid():continue
 m.prior.export(frame,m.HERE/'probe_order_base')
 for i,(cheek,tool) in enumerate(zip(g['cheeks'],g['tools'])):
  cheek=m.b.cut(cheek,tool)
  es=[e for e in cutedges(cheek) if (lambda bb:bb[1,2]-bb[0,2]>1 and abs(bb[1,0]-bb[0,0])<1e-6 and abs(abs(bb[0,1])-65)<1e-6)(m.b.bounds(e))]
  print('CHEEK',i,'edges',len(es),[m.middle(e) for e in es],flush=True)
  f=BRepFilletAPI_MakeFillet(cheek)
  for e in es:f.Add(.8,e)
  f.Build();print('CHEEKFILLET',f.IsDone(),flush=True)
  if f.IsDone():
   cheek=f.Shape();print('CHEEKVALID',BRepCheck_Analyzer(cheek).IsValid(),flush=True)
   if BRepCheck_Analyzer(cheek).IsValid():frame=m.b.fuse(frame,cheek)
 print('FINALVALID',BRepCheck_Analyzer(frame).IsValid(),flush=True)
 if BRepCheck_Analyzer(frame).IsValid():m.prior.export(frame,m.HERE/'probe_order_final')
