from pathlib import Path
import importlib.util,json,hashlib
import numpy as np
import trimesh as tm
import manifold3d as md
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('reinf',HERE/'reinforcement-mock.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
p01=m.P;p05=m.parts['P05']
for side in [-1,1]:
 y=side*24
 p01-=m.box((24,y-5,4),(31,y+5,25))
 a=m.box((8.5,y-5,7),(31,y+5,29))+m.box((24.7,y-7,7),(31,y+7,29))
 a-=m.xcyl(23,32,y,18,2.25)+m.box((25.8,y-3.6,14.4),(29.2,y+3.6,30))
 p05+=a
parts=dict(m.parts);parts['P01']=p01;parts['P05']=p05
pre=set(m.pre)|{'H070','H071','H080','H081'}
moving={'P04','H10','H060','H061'}
changed={'P01','P05','H070','H071','H080','H081'}
checks=[]
for preload in [0,.5,1,1.5,2]:
 for stroke in [0,15-preload,30-preload]:
  pose={r:o.translate(((preload if r in pre else 0)-(stroke if r in moving else 0),0,0)) for r,o in parts.items()}
  done=set()
  for a in changed:
   for b in parts:
    if a==b or tuple(sorted([a,b])) in done:continue
    done.add(tuple(sorted([a,b])))
    obj=pose[a]^pose[b];volume=float(obj.volume())
    olda=m.parts[a].translate(((preload if a in m.pre else 0)-(stroke if a in moving else 0),0,0))
    oldb=m.parts[b].translate(((preload if b in m.pre else 0)-(stroke if b in moving else 0),0,0))
    oldvolume=float((olda^oldb).volume())
    checks.append(dict(pair=[a,b],preload_mm=preload,stroke_mm=stroke,volume_mm3=volume,old_volume_mm3=oldvolume))
def mesh(o):
 a=o.to_mesh64();return tm.Trimesh(a.vert_properties[:,:3],a.tri_verts,process=True)
mesh(p01).export(HERE/'sensed-stops-P01-mock.stl');mesh(p05).export(HERE/'sensed-stops-P05-mock.stl')
fail=[r for r in checks if r['volume_mm3']>.01 and r['volume_mm3']>r['old_volume_mm3']+.01]
report=dict(status='LOCAL_MESH_HYPOTHESIS_ONLY',proposal_sha256=hashlib.sha256((HERE/'sensed-stops-proposal.fs').read_bytes()).hexdigest(),source_sha256=hashlib.sha256((HERE/'reinforcement-proposal.fs').read_bytes()).hexdigest(),part_connected_counts={'P01':len(p01.decompose()),'P05':len(p05.decompose())},p01_volume_mm3=p01.volume(),p05_volume_mm3=p05.volume(),new_interferences=fail,checks=checks)
(HERE/'sensed-stops-mock.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='checks'},indent=2))
