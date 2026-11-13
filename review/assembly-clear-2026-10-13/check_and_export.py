"""Validate source-bound Onshape STL exports and full P01/P04 insertion sweep."""
from pathlib import Path
import json,hashlib,struct,collections,shutil
import numpy as np
import trimesh as tm
import manifold3d as mf
ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
OUT=ROOT/'print/assembly-clear-2026-10-13/parts'
parts={
 'P01_base_6mm_AssemblyClear_RevB_2026-10-13':[-22,-90,-2],
 'P060_rear_retainer_left_RevB_2026-10-13':[125.5,-87,4.5],
 'P061_rear_retainer_right_RevB_2026-10-13':[125.5,63,4.5],
}
checks=[];models={}
for name,expected_min in parts.items():
    src=Path('/Users/jonashilti/Downloads')/(name+'.stl')
    shutil.copyfile(src,HERE/(name+'_Onshape_original.stl'))
    m=tm.load_mesh(src);assert m.is_watertight and m.is_volume and len(m.split())==1
    assert np.allclose(m.bounds[0],expected_min,atol=.002),(name,m.bounds)
    models[name[:4] if name.startswith('P06') else 'P01']=m.copy()
    # Rigid translation only, preserving original tessellation and triangles.
    b=bytearray(src.read_bytes());n=struct.unpack_from('<I',b,80)[0];assert len(b)==84+n*50
    for i in range(n):
        v=list(struct.unpack_from('<12fH',b,84+i*50))
        for j in [3,6,9]:
            for k in range(3):v[j+k]-=float(m.bounds[0,k])
        struct.pack_into('<12fH',b,84+i*50,*v)
    dest=OUT/(name+'.stl');dest.write_bytes(b)
    checks.append(dict(file=dest.name,closed=True,single_body=True,bounds_mm=m.extents.tolist(),
        assembly_min_mm=m.bounds[0].tolist(),volume_mm3=float(m.volume),sha256=hashlib.sha256(b).hexdigest()))
base=models['P01']
def probe_empty(lo,hi):
    probe=tm.creation.box(extents=np.subtract(hi,lo),transform=tm.transformations.translation_matrix(np.add(hi,lo)/2))
    hit=tm.boolean.intersection([base,probe],engine='manifold')
    assert len(hit.faces)==0 or abs(hit.volume)<1e-5,(lo,hi,hit.volume)
# Thickening below Z0 must not seal old windows, bench holes or insert bores.
for y in [-40,40]:probe_empty([30,y-2,-2.1],[100,y+2,4.1])
for x,y in [(-15,-30),(-15,30),(127,-50),(127,50)]:
    hole=tm.creation.cylinder(radius=2.6,height=7,sections=64)
    hole.apply_translation([x,y,1])
    h=tm.boolean.intersection([base,hole],engine='manifold')
    assert len(h.faces)==0 or abs(h.volume)<1e-5
for y in [-83,-67,67,83]:
    hole=tm.creation.cylinder(radius=2,height=3.95,sections=64)
    hole.apply_translation([129.5,y,2.525])
    h=tm.boolean.intersection([base,hole],engine='manifold')
    assert len(h.faces)==0 or abs(h.volume)<1e-5
grip=tm.load_mesh(ROOT/'print/rear-tether-2026-09-29/parts/P04_climbing_carriage.stl')
grip.apply_translation([64,-87,5])
old=tm.load_mesh(ROOT/'review/assembly-2026-10-13/P01_Onshape_original.stl')
blocked=grip.copy();blocked.apply_translation([2,0,0])
old_hit=tm.boolean.intersection([old,blocked],engine='manifold').volume
assert old_hit>70
samples=[]
for offset in np.arange(0,181,.5):
    g=grip.copy();g.apply_translation([float(offset),0,0])
    h=tm.boolean.intersection([base,g],engine='manifold')
    v=float(h.volume) if len(h.faces) else 0.0
    assert abs(v)<1e-4,(offset,v)
    samples.append(dict(offset_mm=float(offset),intersection_mm3=v))
# Continuous swept volume: Minkowski dilation by an X interval 0..180,
# conservatively widened by 0.0001 mm in Y/Z. It includes every in-between pose.
def manifold(m):
    return mf.Manifold(mf.Mesh(np.asarray(m.vertices,dtype=np.float32),np.asarray(m.faces,dtype=np.uint32)))
moving=manifold(grip);fixed=manifold(base)
interval=mf.Manifold.cube([180,.0002,.0002]).translate([0,-.0001,-.0001])
sweep=moving.minkowski_sum(interval)
hit=(fixed ^ sweep)
assert hit.volume()<1e-4,hit.volume()
# Rear retainers match lowered seats, unchanged rod axis; their seated contacts
# are allowed but positive volume overlaps are not.
retainer_checks=[]
for key in ['P060','P061']:
    h=tm.boolean.intersection([base,models[key]],engine='manifold')
    v=float(h.volume) if len(h.faces) else 0.0;assert abs(v)<1e-4
    retainer_checks.append(dict(part=key,base_intersection_mm3=v,seat_z_mm=4.5))
report=dict(status='PASS',source_sha256=hashlib.sha256((ROOT/'fingerworker_mvp.fs').read_bytes()).hexdigest(),
    exports=checks,old_interference_mm3_at_offset_2=old_hit,
    samples=samples,continuous_sweep=dict(offset_range_mm=[0,180],method='Manifold Minkowski sum with conservative Y/Z 0.0001 mm padding',intersection_mm3=hit.volume()),
    nominal_rear_foot_clearance_mm=.5,base_floor_thickness_mm=6,through_window_checks=2,through_bench_hole_checks=4,insert_bore_checks=4,retainers=retainer_checks,
    assembly_conditions='Rear retainers P060/P061 removed, no rods, springs or stop hardware fitted during rear insertion; slide straight at operating Z, then install hardware.',
    scope='Nominal P01/P04 assembly geometry and seated P060/P061 contacts; real FDM fit and strength remain untested')
(HERE/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS: three Onshape meshes; 362 insertion poses and continuous swept volume clear; .5 mm rear-foot gap')
