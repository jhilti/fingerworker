#!/usr/bin/env python3
"""Build Q01, an unloaded p=0 position fixture, separate from frozen R8 CAD.

Requires cadquery-ocp and trimesh. Example runtime used for this build:
  /tmp/fingerworker-sensor-cad-20261022/bin/python build_q01.py
Dimensions are mm. There are no modeled or functional printed threads.
"""
from pathlib import Path
import hashlib
import json
import math
import numpy as np
import trimesh
from OCP.BRepAlgoAPI import BRepAlgoAPI_Fuse
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepGProp import BRepGProp
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder
from OCP.GProp import GProp_GProps
from OCP.gp import gp_Ax2, gp_Dir, gp_Pnt, gp_Trsf
from OCP.Interface import Interface_Static
from OCP.STEPControl import STEPControl_Writer, STEPControl_AsIs
from OCP.StlAPI import StlAPI_Writer
from OCP.TopAbs import TopAbs_SOLID, TopAbs_SHELL
from OCP.TopExp import TopExp_Explorer

HERE = Path(__file__).resolve().parent
NAME = 'Q01_UNLOADED_TEST_FIXTURE'
PARAMETERS = {
    'axis_y_z_mm': [0.0, 18.0],
    'square_locator': {'x_mm': [-20.5, -16.0], 'y_mm': [-6.0, 6.0], 'z_mm': [12.0, 24.0]},
    'reaction_flange': {'x_mm': [-16.0, -14.0], 'radius_mm': 9.0},
    'forward_shaft': {'x_mm': [-14.01, 0.1], 'radius_mm': 2.8},
    'pusher_shoulder': {'x_mm': [0.0, 1.0], 'radius_mm': 4.0},
    'unthreaded_tail': {'x_mm': [0.9, 7.5], 'radius_mm': 1.5},
}


def cylinder(x0, x1, radius):
    return BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(x0, 0, 18), gp_Dir(1, 0, 0)), radius, x1-x0).Shape()


def fuse(a, b):
    operation = BRepAlgoAPI_Fuse(a, b)
    operation.Build()
    assert operation.IsDone()
    return operation.Shape()


def build():
    shape = BRepPrimAPI_MakeBox(gp_Pnt(-20.5, -6, 12), gp_Pnt(-16, 6, 24)).Shape()
    for name in ['reaction_flange', 'forward_shaft', 'pusher_shoulder', 'unthreaded_tail']:
        spec = PARAMETERS[name]
        shape = fuse(shape, cylinder(*spec['x_mm'], spec['radius_mm']))
    assert BRepCheck_Analyzer(shape).IsValid()
    return shape


def count(shape, kind):
    explorer = TopExp_Explorer(shape, kind)
    result = 0
    while explorer.More():
        result += 1
        explorer.Next()
    return result


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def export_stl(shape, path):
    BRepMesh_IncrementalMesh(shape, 0.015, False, 0.08, True).Perform()
    writer = StlAPI_Writer()
    assert writer.Write(shape, str(path))
    mesh = trimesh.load(path, force='mesh')
    mesh.export(path, file_type='stl')  # Compact standard binary STL.
    # Use the delivered binary vertices for the subsequent rigid print transform.
    return trimesh.load(path, force='mesh')


def main():
    shape = build()
    assert count(shape, TopAbs_SOLID) == 1
    assert count(shape, TopAbs_SHELL) == 1
    properties = GProp_GProps()
    BRepGProp.VolumeProperties_s(shape, properties)
    stl = HERE / (NAME + '_assembly-mm.stl')
    mesh = export_stl(shape, stl)
    assert mesh.is_watertight and mesh.is_volume
    Interface_Static.SetCVal_s('write.step.schema', 'AP214')
    writer = STEPControl_Writer()
    writer.Transfer(shape, STEPControl_AsIs)
    step = HERE / (NAME + '_assembly-mm.step')
    assert str(writer.Write(str(step))).endswith('RetDone')

    # Square locating end down. This rigid transform preserves all dimensions.
    # print X = assembly Y; print Y = assembly Z - 18; print Z = assembly X + 20.5.
    # This cyclic axis permutation is a proper rigid rotation (determinant +1).
    matrix = np.array([[0., 1., 0., 0.], [0., 0., 1., -18.], [1., 0., 0., 20.5], [0., 0., 0., 1.]])
    assert abs(np.linalg.det(matrix[:3, :3]) - 1.) < 1e-12
    print_mesh = mesh.copy()
    print_mesh.apply_transform(matrix)
    print_stl = HERE / (NAME + '_print-mm.stl')
    print_mesh.export(print_stl)
    manifest = {
        'ref': 'Q01', 'name': NAME,
        'status': 'LOCAL_PRINT_TEST_FIXTURE_NOT_PRODUCT_CAD',
        'source': Path(__file__).name, 'source_sha256': sha(Path(__file__)),
        'frozen_product_revision': 'R8',
        'frozen_onshape_version_id': '6965afcca3af7c58ef3ac73f',
        'units': 'mm', 'quantity': 1,
        'parameters': PARAMETERS,
        'brep_valid': True, 'solid_count': 1, 'shell_count': 1,
        'brep_volume_mm3': properties.Mass(),
        'stl_watertight': bool(mesh.is_watertight),
        'assembly_bounds_mm': mesh.bounds.tolist(),
        'print_bounds_mm': print_mesh.bounds.tolist(),
        'assembly_to_print_matrix': matrix.tolist(),
        'placement': 'Assembly coordinates: axis Y0/Z18; portal reaction face X-16; p=0 P05 shoulder bearing face X1.',
        'contacts': [
            {'ref': 'P01', 'description': 'Flange rear X-16 bears only on portal material outside the 12.4 mm square pocket.'},
            {'ref': 'P05', 'description': 'Shoulder front X1 bears on the p=0 yoke; plain diameter3 tail locates in diameter3.2 bore.'},
        ],
        'nominal_clearances_mm': {'locator_per_flat': 0.2, 'tail_radial': 0.1, 'flange_to_upper_bridge': 3.0},
        'legal_test_domain': {'preload_p_mm': 0, 'rear_advance_a_mm': [0, 2], 'user_stroke_u_mm': '0 <= u <= 30-a'},
        'print': {
            'orientation': 'Square locating end X-20.5 down, fixture X axis vertical; use supplied print-mm STL at 100 percent scale.',
            'material': 'PLA shape/fit prototype', 'layer_height_mm': 0.2,
            'wall_loops': 4, 'infill_percent': 100,
            'supports': 'Normal supports allowed on model: buildplate supports under the diameter18 flange; supports on flange top under the diameter8 shoulder. Clean the supported portal flange datum flat without shortening it; the forward shoulder bearing face is upward and support-free.',
            'brim_mm': 3,
        },
        'assembly': [
            'Omit the real sensor, pusher, pusher nut, steel cassette, preload nut/keeper/adjuster/lock, cassette retention hardware, springs and isometric sleeves. Never combine Q01 with the real sensor stack.',
            'Insert the square locating plug from the open front (+X) into the empty P01 square pocket until the flange rear face seats at X-16.',
            'With the guide rods available for alignment, slide P05 from +X onto the plain diameter3 tail until its rear pusher face seats against the shoulder at X1. Complete the unloaded guide/carriage assembly.',
            'Keep the assembly supported. The plug and tail provide radial location, not an axial latch. Maintain gentle hand contact in the normal compression direction; do not pull the yoke off the fixture or lift the assembly by Q01.',
            'At p=0 and equal rear setting a, manually guide the carriage from u0 to u(30-a). No springs, force, preload or calibration test is valid with this fixture.',
            'For removal, slide the unloaded P05 clear of the plain tail toward +X, then withdraw Q01 toward +X from the portal before installing any real sensor-stack parts.',
        ],
        'limitations': [
            'Unloaded geometry/hand-fit/motion fixture only. Not a force-bearing sensor replacement, calibrated sensor emulator, preload adjuster, safety stop or strength test specimen.',
            'The 500 N product design target is unqualified and must not be applied to this print test.',
            'Nominal CAD clearance does not qualify printer tolerances, real hardware fits or support-removal quality.',
        ],
        'files': {p.name: {'sha256': sha(p), 'bytes': p.stat().st_size} for p in [stl, step, print_stl]},
    }
    (HERE / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps({'status': 'BUILT', 'source_sha256': manifest['source_sha256'], 'assembly_bounds_mm': manifest['assembly_bounds_mm'], 'print_bounds_mm': manifest['print_bounds_mm'], 'files': manifest['files']}, indent=2))


if __name__ == '__main__':
    main()
