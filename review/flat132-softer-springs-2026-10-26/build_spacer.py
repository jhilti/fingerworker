#!/usr/bin/env python3
"""Build a local prototype adapter for a shorter, softer catalogue spring.

Run with /tmp/fingerworker-sensor-cad-20261022/bin/python.
This is a separate prototype accessory, not an Onshape R9 modification.
"""
from pathlib import Path
import hashlib
import json
import math

from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut, BRepAlgoAPI_Fuse
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepGProp import BRepGProp
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.BRepPrimAPI import BRepPrimAPI_MakeCylinder
from OCP.GProp import GProp_GProps
from OCP.IFSelect import IFSelect_RetDone
from OCP.STEPControl import STEPControl_Writer, STEPControl_AsIs
from OCP.StlAPI import StlAPI_Writer
from OCP.gp import gp_Ax2, gp_Dir, gp_Pnt
import trimesh

HERE = Path(__file__).resolve().parent
OUT = HERE / 'print'
OUT.mkdir(exist_ok=True)

def cylinder(z, height, radius):
    return BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(0, 0, z), gp_Dir(0, 0, 1)), radius, height).Shape()

# The spring rests on the z=22 annular shoulder. The 2 mm pilot is inside
# the spring and does not add to the 22 mm effective spacer length.
body = cylinder(0, 22, 8)
pilot = cylinder(21.9, 2.1, 5.7)
union = BRepAlgoAPI_Fuse(body, pilot).Shape()
spacer = BRepAlgoAPI_Cut(union, cylinder(-.1, 24.2, 3.3)).Shape()
assert BRepCheck_Analyzer(spacer).IsValid()
props = GProp_GProps()
BRepGProp.VolumeProperties_s(spacer, props)
expected = math.pi * ((8**2 - 3.3**2)*22 + (5.7**2 - 3.3**2)*2)
assert abs(props.Mass()-expected) < 1e-6
step = OUT / 'S01_spring_spacer_22mm.step'
writer = STEPControl_Writer()
writer.Transfer(spacer, STEPControl_AsIs)
assert writer.Write(str(step)) == IFSelect_RetDone
BRepMesh_IncrementalMesh(spacer, .015, False, .08, True).Perform()
stl = OUT / 'S01_spring_spacer_22mm.stl'
sw = StlAPI_Writer()
sw.ASCIIMode = False
assert sw.Write(spacer, str(stl))
mesh = trimesh.load(stl, force='mesh')
assert mesh.is_watertight and mesh.is_winding_consistent
parents = list(range(len(mesh.faces)))
def root(n):
    while parents[n] != n:
        parents[n] = parents[parents[n]]
        n = parents[n]
    return n
for left, right in mesh.face_adjacency:
    parents[root(int(left))] = root(int(right))
assert len({root(n) for n in range(len(mesh.faces))}) == 1
assert abs(mesh.bounds[0, 2]) < 1e-6 and abs(mesh.bounds[1, 2] - 24) < 1e-6
spec = {
    'status': 'LOCAL_PROTOTYPE_ACCESSORY_NOT_PHYSICAL_LOAD_RELEASE',
    'date': '2026-10-26', 'quantity': 2,
    'base_cad': 'Frozen R9; no Onshape or original print package changes',
    'existing_spring': {'part': '0X-DF2194', 'free_length_mm': 102, 'rate_each_N_per_mm': 3.307},
    'proposed_spring': {'part': '0X-RDF2127', 'quantity': 2, 'free_length_mm': 80,
        'rate_each_N_per_mm': 2.212, 'OD_mm': 16, 'ID_mm': 12.4,
        'wire_mm': 1.8, 'catalog_L1_mm': 34.75, 'catalog_F1_N': 100.09,
        'approximate_solid_length_mm': 29.92, 'ends': 'ground', 'material': '1.4310',
        'source': 'https://www.febrotec.de/de-DE/druckfedern/schraubendruckfedern/0x-rdf2127/',
        'source_checked_live': '2026-10-26 via manufacturer product page'},
    'adapter': {'body_OD_mm': 16, 'body_length_mm': 22, 'through_bore_mm': 6.6,
        'pilot_OD_mm': 11.4, 'pilot_extension_mm': 2, 'overall_height_mm': 24,
        'spring_bearing_shoulder_mm': 22, 'position': 'One per side on fixed/yoke steel spring seat',
        'assembly_X_mm': 'body12+p..34+p; pilot34+p..36+p; spring34+p..108-a-u',
        'volume_mm3': props.Mass(), 'nominal_mass_PLA_g': props.Mass()*.00124},
    'force_ratio_to_original': 2.212/3.307,
    'nominal_reduction_percent': 100*(1-2.212/3.307),
    'user_target_ratio': 2/3,
    'spring_installed_length_mm': '74-a-p-u', 'legal_domain': '0<=a+p<=2; 0<=u<=30-a-p',
    'minimum_spring_length_mm': 44, 'catalog_L1_reserve_mm': 44-34.75,
    'pair_force_N': '4.424*(6+a+p+u)',
    'force_rows_zero_adjustment': [
        {'travel_mm': u, 'existing_pair_N': 2*3.307*(6+u),
         'proposed_pair_N': 2*2.212*(6+u),
         'proposed_pair_kgf': 2*2.212*(6+u)/9.80665}
        for u in [0, 10, 20, 30]],
    'nominal_only': 'Linear spring calculation excludes tolerance and friction. No fatigue or load rating established.',
    'local_part_checks': {'valid_BRep': True, 'STL_watertight': True, 'one_mesh_component': True,
        'dimensions_mm': mesh.extents.tolist(), 'analytical_volume_matches': True},
    'files': {p.name: {'bytes': p.stat().st_size, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}
              for p in [step, stl]},
}
(HERE/'spring-change.json').write_text(json.dumps(spec, indent=2)+'\n')
print(json.dumps({'files': spec['files'], 'force_ratio':spec['force_ratio_to_original'],
    'part_volume_mm3': props.Mass(), 'STL_checks':spec['local_part_checks']}, indent=2))
