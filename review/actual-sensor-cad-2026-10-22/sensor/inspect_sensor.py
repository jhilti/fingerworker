"""Inspect and place TE's unchanged FX1901 STEP; do not alter the mechanism.

Run with /tmp/fingerworker-sensor-cad-20261022/bin/python.
Placement is contact-datum registration, not a claim that the real sensor fits.
"""
from pathlib import Path
import hashlib
import importlib.metadata
import json
import shutil
import numpy as np
import trimesh
import manifold3d as md
from OCP.STEPControl import STEPControl_Reader, STEPControl_Writer, STEPControl_AsIs
from OCP.BRepBndLib import BRepBndLib
from OCP.Bnd import Bnd_Box
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE, TopAbs_SOLID, TopAbs_REVERSED
from OCP.TopoDS import TopoDS
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.GeomAbs import GeomAbs_Plane, GeomAbs_Cylinder, GeomAbs_Sphere
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.BRep import BRep_Tool
from OCP.TopLoc import TopLoc_Location
from OCP.gp import gp_Trsf
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = ROOT / "vendor/te_fx1901/c-fx1901-0001-0200-l-f-3d.stp"
ASSEMBLY = ROOT / "review/flat132-hand-fit-2026-10-19/assembly-mm"
MATRIX = np.array([[0,0,1,-1.9], [1,0,0,0], [0,1,0,18], [0,0,0,1]],float)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def bounds(shape):
    box = Bnd_Box()
    # Read the analytic BRep, not triangulation inflated by mesh deflection.
    BRepBndLib.AddOptimal_s(shape, box, False)
    return [list(box.CornerMin().Coord()), list(box.CornerMax().Coord())]

def volume(shape):
    props = GProp_GProps()
    BRepGProp.VolumeProperties_s(shape, props)
    return props.Mass()

def solid_count(shape):
    exp = TopExp_Explorer(shape, TopAbs_SOLID)
    count = 0
    while exp.More():
        count += 1
        exp.Next()
    return count

def tessellate(shape):
    BRepMesh_IncrementalMesh(shape, .01, False, .08, True)
    exp = TopExp_Explorer(shape, TopAbs_FACE)
    points, triangles = [], []
    while exp.More():
        face = TopoDS.Face(exp.Current())
        loc = TopLoc_Location()
        tri = BRep_Tool.Triangulation_s(face, loc)
        start = len(points)
        if tri:
            points.extend(tri.Node(i).Transformed(loc.Transformation()).Coord()
                          for i in range(1, tri.NbNodes()+1))
            for i in range(1, tri.NbTriangles()+1):
                a,b,c = tri.Triangle(i).Get()
                if face.Orientation() == TopAbs_REVERSED:
                    b,c = c,b
                triangles.append((a+start-1,b+start-1,c+start-1))
        exp.Next()
    mesh = trimesh.Trimesh(np.array(points), np.array(triangles), process=True)
    # Two tessellator pole triangles collapse after identical boundary vertices
    # are merged. Drop zero-area triangles only; no hole filling or remeshing.
    before = len(mesh.faces)
    mesh.update_faces(mesh.nondegenerate_faces())
    mesh.metadata['zero_area_triangles_removed'] = before-len(mesh.faces)
    assert mesh.is_watertight and mesh.is_volume
    return mesh

def manifold(mesh):
    value = md.Manifold(md.Mesh(np.asarray(mesh.vertices,np.float32),
                               np.asarray(mesh.faces,np.uint32)))
    assert str(value.status()).endswith("NoError"), value.status()
    return value

reader = STEPControl_Reader()
read_status = str(reader.ReadFile(str(SOURCE)))
assert read_status.endswith("RetDone")
reader.TransferRoots()
shape = reader.OneShape()
assert BRepCheck_Analyzer(shape).IsValid()

faces = []
exp = TopExp_Explorer(shape,TopAbs_FACE)
while exp.More():
    face = TopoDS.Face(exp.Current())
    surf = BRepAdaptor_Surface(face,True)
    props = GProp_GProps()
    BRepGProp.SurfaceProperties_s(face,props)
    row = dict(index=len(faces), type=str(surf.GetType()), area_mm2=props.Mass(),
               centroid_mm=list(props.CentreOfMass().Coord()), bounds_mm=bounds(face))
    if surf.GetType() == GeomAbs_Plane:
        row['plane_origin_mm'] = list(surf.Plane().Location().Coord())
        row['plane_normal'] = list(surf.Plane().Axis().Direction().Coord())
    if surf.GetType() == GeomAbs_Cylinder:
        row['cylinder_origin_mm'] = list(surf.Cylinder().Location().Coord())
        row['cylinder_axis'] = list(surf.Cylinder().Axis().Direction().Coord())
        row['cylinder_radius_mm'] = surf.Cylinder().Radius()
    if surf.GetType() == GeomAbs_Sphere:
        row['sphere_center_mm'] = list(surf.Sphere().Location().Coord())
        row['sphere_radius_mm'] = surf.Sphere().Radius()
    faces.append(row)
    exp.Next()

raw = tessellate(shape)
raw_step_path = HERE / "TE_FX1901_official_original.step"
shutil.copy2(SOURCE,raw_step_path)
raw_path = HERE / "TE_FX1901_official_native_mm.stl"
raw.export(raw_path)
placed = raw.copy()
placed.apply_transform(MATRIX)
placed_path = HERE / "TE_FX1901_actual_apex_aligned_132_mm.stl"
placed.export(placed_path)
transform = gp_Trsf()
transform.SetValues(*MATRIX[:3,:].ravel())
placed_shape = BRepBuilderAPI_Transform(shape,transform,True).Shape()
writer = STEPControl_Writer()
writer.Transfer(placed_shape,STEPControl_AsIs)
step_path = HERE / "TE_FX1901_actual_apex_aligned_132_mm.step"
if not step_path.exists():
    assert str(writer.Write(str(step_path))).endswith("RetDone")

actual = manifold(placed)
comparisons = []
for ref in ('H01','H01a','H01b','H01c','H01d','H12','P01','P05','H02','H13','H15','P02','P03','H180','H181'):
    path = ASSEMBLY / (ref+'.stl')
    if not path.exists():
        continue
    mesh = trimesh.load_mesh(path,process=True)
    item = dict(reference=ref, mesh_sha256=sha(path), bounds_mm=mesh.bounds.tolist(),
                watertight=bool(mesh.is_watertight), volume_mm3=float(mesh.volume))
    if mesh.is_volume:
        other = manifold(mesh)
        intersection = actual ^ other
        item['intersection_volume_mm3'] = float(intersection.volume())
        item['actual_minus_existing_volume_mm3'] = float((actual - other).volume())
        if ref in ('H12','P01','P05','H02','H13') and item['intersection_volume_mm3'] > .001:
            out = intersection.to_mesh()
            conflict = trimesh.Trimesh(np.asarray(out.vert_properties)[:,:3],np.asarray(out.tri_verts),process=True)
            path = HERE / ('conflict-'+ref+'.stl')
            conflict.export(path)
            item['conflict_mesh'] = path.name
            item['conflict_mesh_sha256'] = sha(path)
    comparisons.append(item)

audit = dict(
    date='2026-10-22', scope='Actual manufacturer BRep registration and nominal mesh intersections; no mechanism edits or release.',
    source=dict(path=str(SOURCE.relative_to(ROOT)),sha256=sha(SOURCE),
        original_filename='c-fx1901-0001-0200-l-f-3d.stp', product='C-FX1901-0001-0200-L',
        vendor='TE Connectivity Ltd.', created='2018-02-15', revision='F from distributed filename', units='mm'),
    runtime={p:importlib.metadata.version(p) for p in ('cadquery-ocp','trimesh','manifold3d','numpy')},
    brep=dict(valid=True,solid_count=solid_count(shape),face_count=len(faces),bounds_mm=bounds(shape),
              volume_mm3=volume(shape),main_cylinder_diameter_mm=25.0,
              front_outer_rim_native_z_mm=0.0,rear_support_plane_native_z_mm=-7.95,
              central_disk_native_z_mm=-.51,central_disk_nominal_radius_mm=2.92,
              central_disk_face_index=6, central_spherical_apex_native_mm=[0,0,0],
              spherical_button_face_indices=[34,35]),
    placement=dict(matrix=MATRIX.tolist(),scale=1.0,
        rationale='Native +Z to mechanism +X; native +X radial lead to mechanism +Y; native +Y to mechanism +Z. Central spherical button apex native (0,0,0) maps to existing force-pusher tip (-1.9,0,18).',
        datum_limitation='Central contact apex identified from BRep geometry, including conical faces32/33 and spherical faces34/35. Confirm load direction and support datums against the matching FX1901 drawing and physical sensor before machining.',
        placed_brep_bounds_mm=bounds(placed_shape),
        placed_rear_support_plane_x_mm=-9.85,
        previous_proxy_rear_plane_x_mm=-8.0,
        rear_plane_difference_mm=-1.85,
        placed_outer_rim_x_mm=-1.9,
        intermediate_disk_alignment_rejected='TE_FX1901_actual_contact_aligned_132_mm.* used translationX−1.39 and caused0.51 mm /1.012873 mm³ force-pusher penetration. Retained only as an intermediate.'),
    tessellation=dict(linear_deflection_mm=.01,angular_deflection_radians=.08,
        relative=False,vertices=len(raw.vertices),triangles=len(raw.faces),
        zero_area_triangles_removed=raw.metadata['zero_area_triangles_removed'],
        watertight=bool(raw.is_watertight),mesh_volume_mm3=float(raw.volume),
        mesh_volume_error_mm3=float(raw.volume-volume(shape))),
    output_files={str(p.relative_to(HERE)):dict(sha256=sha(p),size_bytes=p.stat().st_size)
                  for p in (raw_step_path,raw_path,placed_path,step_path)},
    comparisons=comparisons,
    limitations=[
        'The stored May 2020 FX1901 PDF dimensions illustrations are labeled FX1900-XXX1 / FX1900-0000 and show diameter19.75 x thickness5.45; these do not match the actual FX1901 STEP diameter25 x thickness7.95.',
        'Existing H01/H01a/H01b are simplified reference solids. Replacing them invalidates prior sensor fit results.',
        'Official STEP includes a short radial four-wire stub only, not the full flexible lead or connector. Existing H01c/H01d remain illustrative routing envelopes if displayed.',
        'No dimensional scaling, cutting, or deformation of the manufacturer sensor was performed.',
        'Positive mesh intersection volumes are nominal collisions at this contact-aligned pose, not clearance or assembly approval.'
    ])
(HERE/'sensor-geometry-audit.json').write_text(json.dumps(audit,indent=2)+'\n')
(HERE/'sensor-face-audit.json').write_text(json.dumps(faces,indent=2)+'\n')
print(json.dumps({k:audit[k] for k in ('brep','placement','tessellation','comparisons')},indent=2))
