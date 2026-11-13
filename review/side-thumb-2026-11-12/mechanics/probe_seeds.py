import side_thumb as m
from OCP.BRepFilletAPI import BRepFilletAPI_MakeFillet
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.ShapeUpgrade import ShapeUpgrade_UnifySameDomain
from OCP.GeomAbs import GeomAbs_Circle
from OCP.BRepAdaptor import BRepAdaptor_Curve
import sys
frame=m.b.read_step(m.HERE/'P01_unrounded.step')[0][0]
mode=sys.argv[1]
if mode=='scoped':
 u=ShapeUpgrade_UnifySameDomain(frame,True,True,False)
 for e in m.edges(frame):
  bb=m.b.bounds(e)
  # Only merge the artificial coplanar y65 lower/upper cheek seam edges.
  seam=abs(abs(bb[0,1])-65)<1e-6 and abs(bb[1,1]-bb[0,1])<1e-6 and bb[0,2]>=23.99 and bb[1,2]<=24.11
  if not seam:u.KeepShape(e)
 u.Build();frame=u.Shape();print('UNIFIED',BRepCheck_Analyzer(frame).IsValid(),flush=True)
 assert BRepCheck_Analyzer(frame).IsValid()
es=m.mouth_edges(frame)
if mode=='topseed':es=[e for e in es if (lambda bb:abs(bb[0,2]-33)<1e-5 and abs(bb[1,2]-33)<1e-5)(m.b.bounds(e))]
if mode=='verticalseed':es=[e for e in es if (lambda bb:abs(bb[1,0]-bb[0,0])<1e-6 and abs(abs(bb[0,1])-65)<1e-6 and bb[0,2]>24)(m.b.bounds(e))]
print('SEEDS',len(es),[m.middle(e) for e in es],flush=True)
f=BRepFilletAPI_MakeFillet(frame)
for e in es:f.Add(.8,e)
print('CONTOURS',f.NbContours(),[f.NbEdges(i) for i in range(1,f.NbContours()+1)],flush=True)
f.Build();print('DONE',f.IsDone(),flush=True)
if f.IsDone():
 print('VALID',BRepCheck_Analyzer(f.Shape()).IsValid(),flush=True)
 if BRepCheck_Analyzer(f.Shape()).IsValid():m.prior.export(f.Shape(),m.HERE/('probe_'+mode))
