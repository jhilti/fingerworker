"""Local mesh hypothesis checks, not a native Onshape regeneration.

Applies the proposed FS cap/relief geometry to the unchanged native V6 STL.
Manufacturing source and reviewed source are not modified.
"""
from pathlib import Path
import hashlib
import json
import math
import numpy as np
import trimesh
import manifold3d as md

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ASM = ROOT / 'review/flat132-hand-fit-2026-10-19/assembly-mm'

def solid(mesh):
    return md.Manifold(md.Mesh(np.asarray(mesh.vertices, np.float32),
                               np.asarray(mesh.faces, np.uint32)))

def mesh(value):
    m = value.to_mesh()
    return trimesh.Trimesh(m.vert_properties[:, :3], m.tri_verts, process=True)

def xcyl(x0, x1, y, z, radius):
    return md.Manifold.cylinder(x1-x0, radius, circular_segments=1024).rotate((0,90,0)).translate((x0,y,z))

def cap(side):
    lo, hi = (40.5, 42.0) if side > 0 else (-42.0, -40.5)
    x0, x1, radius = 111.5, 116.5, .35
    contour=[]
    for x,y,a in ((x1-radius,hi-radius,0),(x0+radius,hi-radius,90),
                  (x0+radius,lo+radius,180),(x1-radius,lo+radius,270)):
        for angle in np.linspace(a,a+90,65):
            theta=math.radians(angle)
            contour.append((x+radius*math.cos(theta),y+radius*math.sin(theta)))
    return md.CrossSection([contour]).extrude(1.5).translate((0,0,28.5))

def ray_z(value,x,y):
    hits = value.ray_cast((x,y,100),(x,y,-100))
    return sorted(set(round(float(hit.position[2]),6) for hit in hits))

if __name__ == '__main__':
    inputs={ref:trimesh.load(ASM/f'{ref}.stl',force='mesh',process=True)
            for ref in ['P03','H13','P04','H060','H061','H030','H031','H040','H041']}
    objects={ref:solid(m) for ref,m in inputs.items()}
    sleeve_cut=xcyl(-24.5,-21.3,0,18,3.5)
    sleeve=objects['P03']-sleeve_cut
    caps={side:cap(side) for side in [-1,1]}
    additions={side:caps[side]-xcyl(112,116,side*51,18,12) for side in [-1,1]}
    grip=objects['P04']+additions[-1]+additions[1]
    gm=mesh(grip)
    report=dict(scope='Local Manifold/STL hypothesis only; final native FeatureScript remains to regenerate and re-export.',
        units='mm',input_sha256={ref:hashlib.sha256((ASM/f'{ref}.stl').read_bytes()).hexdigest() for ref in inputs},
        sleeve=dict(removed_volume_mm3=float(objects['P03'].volume()-sleeve.volume()),
            resulting_watertight=bool(mesh(sleeve).is_watertight),poses=[]),
        roof=dict(cap_bounds_mm={str(s):list(caps[s].bounding_box()) for s in caps},
            added_volume_mm3=float(grip.volume()-objects['P04'].volume()),
            resulting_watertight=bool(gm.is_watertight),rays=[],hardware_intersections=[]))
    for p in np.linspace(0,2,21):
        adjuster=objects['H13'].translate((float(p),0,0))
        report['sleeve']['poses'].append(dict(preload_mm=float(p),
            intersection_mm3=float((sleeve^adjuster).volume()),
            minimum_gap_mm=float(sleeve.min_gap(adjuster,2))))
    for s in [-1,1]:
        for y in [41.9,41.99,41.999,41.9999]:
            z=ray_z(grip,114,s*y)
            report['roof']['rays'].append(dict(x_mm=114,y_mm=s*y,z=z,
                roof_mm=z[-1]-z[-2],bottom_mm=z[1]-z[0]))
    for ref in ['H060','H061','H030','H031','H040','H041']:
        report['roof']['hardware_intersections'].append(dict(part=ref,
            original_intersection_mm3=float((objects['P04']^objects[ref]).volume()),
            modified_intersection_mm3=float((grip^objects[ref]).volume()),
            new_cap_only_intersection_mm3=float(((grip-objects['P04'])^objects[ref]).volume())))
    report['roof']['new_material_bounds_mm']=list((grip-objects['P04']).bounding_box())
    (HERE/'comfort-roof-mock.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(sleeve_removed_mm3=report['sleeve']['removed_volume_mm3'],
        sleeve_minimum_gap_mm=min(p['minimum_gap_mm'] for p in report['sleeve']['poses']),
        roof_added_mm3=report['roof']['added_volume_mm3'],
        roof_minimum_sample_mm=min(p['roof_mm'] for p in report['roof']['rays']),
        new_cap_hardware_intersections_mm3={p['part']:p['new_cap_only_intersection_mm3'] for p in report['roof']['hardware_intersections']}),indent=2))
