"""Separate rigid palm mockup for the PETG/PLA assessment pack, mm.
The functional FeatureScript retains its elastic sleeve reference.
"""
from pathlib import Path
import json, hashlib
import cadquery as cq
import trimesh as tm
OUT=Path(__file__).resolve().parents[1]
for folder in ['step','stl']:(OUT/folder).mkdir(exist_ok=True)
def box(x0,x1,y0,y1,z0,z1):
    return cq.Solid.makeBox(x1-x0,y1-y0,z1-z0,cq.Vector(x0,y0,z0))
outer=cq.Solid.makeCylinder(10.25,86,cq.Vector(-34,-43,19.75),cq.Vector(0,1,0))
outer=cq.Workplane(obj=outer).edges('%Circle').fillet(1.2).val()
inner=cq.Solid.makeCylinder(8.05,88,cq.Vector(-34,-44,19.75),cq.Vector(0,1,0))
blank=outer.cut(inner).cut(box(-50,-18,-45,45,0,14.6))
parts=[]
for name,split in [('P03a_Palm_shell_left_PETG_MOCKUP',box(-50,-34.15,-45,45,0,35)),
                   ('P03b_Palm_shell_right_PETG_MOCKUP',box(-33.85,-18,-45,45,0,35))]:
    solid=blank.intersect(split)
    assert solid.isValid() and len(solid.Solids())==1
    cq.exporters.export(solid,str(OUT/'step'/(name+'.step')))
    oriented=solid.rotate((0,0,0),(1,0,0),90)
    bb=oriented.BoundingBox();oriented=oriented.translate((-bb.xmin,-bb.ymin,-bb.zmin))
    path=OUT/'stl'/(name+'.stl')
    cq.exporters.export(oriented,str(path),tolerance=.015,angularTolerance=.06)
    mesh=tm.load_mesh(path);assert mesh.is_watertight and mesh.is_volume and abs(mesh.bounds[0,2])<.001
    parts.append(dict(file=path.name,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                      volume_mm3=solid.Volume(),valid_single_solid=True))
(OUT/'validation.json').write_text(json.dumps(dict(status='PASS',material='PETG or PLA, rigid assessment only',
    inner_diameter_mm=16.1,palm_core_diameter_mm=15.5,radial_clearance_mm=.3,split_gap_mm=.3,
    parts=parts),indent=2)+'\n')
print('PASS: two rigid half-shells, 0.3 mm radial clearance and split gap')
