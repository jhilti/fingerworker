from pathlib import Path
import sys,importlib.util,json
import numpy as np
ROOT=Path(__file__).resolve().parents[3];R14=ROOT/'review/near-palm-2026-11-06'
spec=importlib.util.spec_from_file_location('r14',R14/'mechanics/near_palm.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);b=m.b
from OCP.BRepCheck import BRepCheck_Analyzer
inv=json.loads((R14/'validation/native-step-inventory.json').read_text());solids=b.read_step(inv['native_step'])[0]
parts={ref:solids[v['candidates'][0]['solid_index']] for ref,v in inv['native_part_correspondence'].items()}
rows=[]
for sign in [-1,1]:
 yy=sorted([sign*56.5,sign*70])
 window=b.box([-30,yy[0],4],[150,yy[1],8])
 for ref in ['P04','P05','P06','H060','H061','H030','H031','H040','H041','H050','H051']:
  shape=b.common(window,parts[ref]); assert BRepCheck_Analyzer(shape).IsValid()
  vol=b.volume(shape)
  if vol>1e-6:
   bb=b.bounds(shape); rows.append(dict(sign=sign,ref=ref,volume_mm3=vol,bounds=bb.tolist(),fullstroke_x_min=bb[0,0]-30 if ref in ['P04','H060','H061'] else bb[0,0]));print(rows[-1],flush=True)
(Path(__file__).parent/'inboard-nearby-obstacles.json').write_text(json.dumps(rows,indent=2)+'\n')
