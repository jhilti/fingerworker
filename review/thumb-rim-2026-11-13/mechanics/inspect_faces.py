from pathlib import Path
import importlib.util,json
import numpy as np
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.TopAbs import TopAbs_FACE
from OCP.TopExp import TopExp_Explorer
from OCP.TopoDS import TopoDS
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
R=Path.cwd();s=importlib.util.spec_from_file_location('r18',R/'review/organic-palm-2026-11-13/mechanics/organic_palm.py');g=importlib.util.module_from_spec(s);s.loader.exec_module(g)
i=json.loads((R/'review/organic-palm-2026-11-13/validation/native-step-inventory.json').read_text());ss,_,_=g.b.read_step(i['native_step']);shape=ss[i['native_part_correspondence']['P01']['candidates'][0]['solid_index']]
rows=[];ex=TopExp_Explorer(shape,TopAbs_FACE);n=0
while ex.More():
 f=TopoDS.Face(ex.Current());ex.Next();a=BRepAdaptor_Surface(f);bb=g.b.bounds(f);n+=1
 if bb[0,0]>-32 and bb[1,0]<-10 and bb[0,1]>59 and bb[1,1]<67 and bb[1,2]>19:
  p=GProp_GProps();BRepGProp.SurfaceProperties_s(f,p);c=p.CentreOfMass();typ=str(a.GetType());d=dict(index=n,type=typ,bounds=bb.tolist(),area=p.Mass(),center=list(c.Coord()))
  if 'Cylinder' in typ:d['radius']=a.Cylinder().Radius()
  if 'Torus' in typ:d.update(major=a.Torus().MajorRadius(),minor=a.Torus().MinorRadius())
  uv=((a.FirstUParameter()+a.LastUParameter())/2,(a.FirstVParameter()+a.LastVParameter())/2);d['uv_midpoint']=list(a.Value(*uv).Coord());rows.append(d)
(R/'review/thumb-rim-2026-11-13/mechanics/native-rim-faces.json').write_text(json.dumps(rows,indent=2)+'\n')
