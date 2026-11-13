from pathlib import Path
import sys,json
sys.path.insert(0,str(Path(__file__).parent));import thumb_rim as m
from OCP.BRepFilletAPI import BRepFilletAPI_MakeFillet
from OCP.BRepAdaptor import BRepAdaptor_Curve
from OCP.TopExp import TopExp
from OCP.BRep import BRep_Tool
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepTools import BRepTools
old,_=m.r17.load();g=m.r17.stocks();raw=old['P01']
for c in g['cheeks']:raw=m.b.fuse(raw,c)
for t in g['tools']:raw=m.b.cut(raw,t)
assert BRepCheck_Analyzer(raw).IsValid()
BRepTools.Write_s(raw,str(m.HERE/'raw_mouth.brep'))
fil=BRepFilletAPI_MakeFillet(raw)
for e in m.r17.mouth_edges(raw):fil.Add(.4,e)
rows=[]
for i in range(1,fil.NbContours()+1):
 for j in range(1,fil.NbEdges(i)+1):
  e=fil.Edge(i,j);a=BRepAdaptor_Curve(e)
  rows.append(dict(contour=i,edge=j,mid=m.r17.middle(e),bounds=m.b.bounds(e).tolist(),start=list(a.Value(a.FirstParameter()).Coord()),end=list(a.Value(a.LastParameter()).Coord()),type=str(a.GetType())))
(m.HERE/'raw-mouth-contours.json').write_text(json.dumps(rows,indent=2)+'\n')
