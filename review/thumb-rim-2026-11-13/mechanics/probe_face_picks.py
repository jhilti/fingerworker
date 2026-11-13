import thumb_rim as g,json
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeVertex
from OCP.gp import gp_Pnt
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
old,_=g.load();fs=g.faces(old['P01']);rows=[]
for pt in g.FACE_PICKS:
 v=BRepBuilderAPI_MakeVertex(gp_Pnt(*pt)).Vertex();hits=[]
 for i,f in enumerate(fs):
  op=BRepExtrema_DistShapeShape(v,f);op.Perform()
  if op.Value()<.1:hits.append(dict(index=i+1,gap=op.Value(),point=list(op.PointOnShape2(1).Coord())))
 rows.append(dict(original=pt,hits=hits))
(g.HERE/'face-pick-diagnostics.json').write_text(json.dumps(rows,indent=2)+'\n')
