"""Independent local STL boolean hypothesis. Not a native regeneration."""
from pathlib import Path
import json, hashlib
import numpy as np
import trimesh as tm
import manifold3d as md
HERE=Path(__file__).resolve().parent
BASE=HERE.parent/'flat132-finished-2026-10-22'
A=BASE/'assembly-mm'
def solid(m): return md.Manifold(md.Mesh64(np.asarray(m.vertices,np.float64),np.asarray(m.faces,np.uint64)))
def box(lo,hi): return md.Manifold.cube(tuple(np.array(hi)-lo)).translate(lo)
def ycyl(x,y0,y1,z,r):return md.Manifold.cylinder(y1-y0,r,circular_segments=512).rotate((-90,0,0)).translate((x,y0,z))
def xcyl(x0,x1,y,z,r):return md.Manifold.cylinder(x1-x0,r,circular_segments=512).rotate((0,90,0)).translate((x0,y,z))
def zcyl(x,y,z0,z1,r):return md.Manifold.cylinder(z1-z0,r,circular_segments=512).translate((x,y,z0))
def prism(y0,y1,p):
    return md.CrossSection([p]).extrude(y1-y0).rotate((90,0,0)).translate((0,y1,0))
parts={p.stem:solid(tm.load(p,force='mesh',process=True)) for p in A.glob('*.stl')}
wall=box((-22.75,-25.4,3.8),(-16,25.4,33))
for side in [-1,1]:
    lo=-25.4 if side<0 else 20.3
    r=prism(lo,lo+5.1,[(-22.75,11.75),(-7.6,11.75),(-7.6,13),(-12.5,33),(-22.75,33)])
    if side>0:r-=box((-10.35,20.1,11.5),(-7.4,27.5,24.5))
    wall+=r
wall+=box((-16.2,-25.4,30),(-12.5,25.4,33))
wall-=box((-23.1,-16.2,8.8),(-20.9,16.2,28.2))
wall-=box((-22.1,-6.2,11.8),(-15.9,6.2,24.2))
wall-=xcyl(-23,-15,0,18,3.2)
for y in [-11,11]:
    wall-=xcyl(-23,-15.8,y,24,1.7)
    wall-=box((-18,y-2.85,21.15),(-15.8,y+2.85,26.85))
wall-=zcyl(-19,0,21,30,1.6)
wall-=zcyl(-19,0,26,30,2.9)+zcyl(-19,0,29.2,34,3.1)
# Widen the existing guides including their endcaps and source pockets.
guides=[]
for side in [-1,1]:
    lo=-20.5 if side<0 else 15.5
    g=box((-16.2,lo,3.8),(-8,lo+5,29))+box((-8.1,lo,3.8),(-6.5,lo+5,11.7))
    if side>0:g-=box((-10.35,15.3,12),(-7.4,20.7,24))
    y0=-20.7 if side<0 else 15.3
    y1=y0+5.4
    g-=ycyl(-12.6,y0,y1,8.5,2.2)+ycyl(-11,y0,y1,8.5,2.2)+box((-12.6,y0,6.3),(-11,y1,10.7))
    guides.append(g)
P=(parts['P01']+wall+guides[0]+guides[1])-zcyl(-19,0,29.2,34,3.1)
P-=box((-10.35,15.3,12),(-7.4,20.7,24))
P-=box((-12.3,-15.3,2.7),(2.9,15.3,4.2))
# New P05 lower reliefs exactly match source; all otherP05faces unchanged.
yoke=parts['P05']-box((-8.2,-21,3.3),(-6, -15,12.2))-box((-8.2,15,3.3),(-6,21,12.2))
parts['P05']=yoke
# Existing H15 hardware geometry is preserved exactly.
added=P-parts['P01'];removed=parts['P01']-P
pre=set('P05 H050 H051 H12 H01 H02 H13 H180 H181 H190 H191 H20 H23 H240 H241 H242 H243 H250 H251 H252 H253'.split())
checks=[]
for ref,b in parts.items():
    if ref=='P01':continue
    for p in [0,0.5,1,1.5,2] if ref in pre else [0]:
        q=b.translate((p,0,0))
        v=float((added^q).volume())
        gap=float(added.min_gap(q,2)) if v<1e-5 else 0
        checks.append(dict(ref=ref,preload_mm=p,added_material_overlap_mm3=v,gap_up_to2mm=gap))
def mesh(o):
    a=o.to_mesh64();return tm.Trimesh(a.vert_properties[:,:3],a.tri_verts,process=True)
mesh(added).export(HERE/'reinforcement-additions-mock.stl')
mesh(P).export(HERE/'reinforcement-P01-mock.stl')
mesh(yoke).export(HERE/'reinforcement-P05-mock.stl')
report=dict(status='LOCAL_MESH_HYPOTHESIS_ONLY',source_sha256=hashlib.sha256((BASE/'fingerworker_flat132_finished.fs').read_bytes()).hexdigest(),proposal_sha256=hashlib.sha256((HERE/'reinforcement-proposal.fs').read_bytes()).hexdigest(),added_volume_mm3=added.volume(),removed_P01_volume_mm3=removed.volume(),connected_count=len(P.decompose()),checks=checks,interferences=[c for c in checks if c['added_material_overlap_mm3']>1e-4],minimum_positive_gap=min((c['gap_up_to2mm'] for c in checks if c['gap_up_to2mm']>1e-5),default=None))
(HERE/'reinforcement-mock.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='checks'},indent=2))
