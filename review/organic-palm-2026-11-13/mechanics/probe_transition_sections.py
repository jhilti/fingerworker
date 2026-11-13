from pathlib import Path
import json,math
import numpy as np
from OCP.BRepClass3d import BRepClass3d_SolidClassifier
from OCP.gp import gp_Pnt
from OCP.TopAbs import TopAbs_IN,TopAbs_ON
import organic_palm as g
H=Path(__file__).resolve().parent;V=H.parent/'validation'
def get(name):
 i=json.loads((V/name).read_text());ss,_,_=g.b.read_step(i['native_step']);return ss[i['native_part_correspondence']['P01']['candidates'][0]['solid_index']],i
native,ni=get('native-step-inventory.json');base,bi=get('foundation-step-inventory.json')
rows=[]
for label,shape in [('native_R18',native),('foundation_R17',base)]:
 c=BRepClass3d_SolidClassifier(shape)
 for z in [23.799,23.9,23.999,24.0,24.001,24.1,24.2]:
  for y in [36,37,37.5,38.008,38.416,38.967,39]:
   coords=np.arange(-20,-7.99,.02);inside=[]
   for x in coords:
    c.Perform(gp_Pnt(float(x),y,z),1e-7);inside.append(c.State() in (TopAbs_IN,TopAbs_ON))
   segs=[];start=None
   for idx,val in enumerate(inside+[False]):
    if val and start is None:start=coords[idx]
    if not val and start is not None:segs.append([float(start),float(coords[idx-1])]);start=None
   rows.append(dict(part=label,y_mm=y,z_mm=z,occupied_x_intervals_mm=segs))
(H/'transition-sections.json').write_text(json.dumps(dict(status='MEASURED_NATIVE_CAD_CLASSIFICATION',native_step_sha256=ni['native_step_sha256'],foundation_step_sha256=bi['native_step_sha256'],method='Exact BRep point classifier,0.02mm X-grid; ON counted occupied; valuesjustabove/belowZ24 distinguish originalcapbottom.',rows=rows),indent=2)+'\n')
