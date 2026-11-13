#!/usr/bin/env python3
"""R12 unloaded sensor-stack fit proxy; no product sensor/load substitution.

One grounded block bears at the new fixed X=-12 reaction datum. The original
P05 shoulder face X=1 and diameter3 locating tail remain. All dimensions mm.
"""
from pathlib import Path
import hashlib, json, sys
import numpy as np
import trimesh
from OCP.BRepAlgoAPI import BRepAlgoAPI_Fuse
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepGProp import BRepGProp
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder, BRepPrimAPI_MakeCone
from OCP.GProp import GProp_GProps
from OCP.gp import gp_Ax2, gp_Dir, gp_Pnt
from OCP.Interface import Interface_Static
from OCP.STEPControl import STEPControl_Writer, STEPControl_AsIs
from OCP.StlAPI import StlAPI_Writer
from OCP.TopAbs import TopAbs_SOLID, TopAbs_SHELL
from OCP.TopExp import TopExp_Explorer

HERE=Path(__file__).resolve().parent
NAME='Q01_R12_FIXED_UNLOADED_FIXTURE'
PARAMETERS={
 'axis_y_z_mm':[0,18],
 'grounded_reaction_block':{'x_mm':[-12,-8],'y_mm':[-6,6],'z_mm':[2.7,25]},
 'shaft':{'x_mm':[-8.1,.1],'radius_mm':2.8},
 'shoulder_support_cone':{'x_mm':[-1.2,0],'radii_mm':[2.8,4]},
 'pusher_shoulder':{'x_mm':[0,1],'radius_mm':4},
 'unthreaded_tail':{'x_mm':[.9,7.5],'radius_mm':1.5},
}
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def axis(x):return gp_Ax2(gp_Pnt(x,0,18),gp_Dir(1,0,0))
def cylinder(x0,x1,r):return BRepPrimAPI_MakeCylinder(axis(x0),r,x1-x0).Shape()
def fuse(a,b):
 op=BRepAlgoAPI_Fuse(a,b);op.Build();assert op.IsDone();return op.Shape()
def count(shape,kind):
 e=TopExp_Explorer(shape,kind);n=0
 while e.More():n+=1;e.Next()
 return n
def build():
 s=BRepPrimAPI_MakeBox(gp_Pnt(-12,-6,2.7),gp_Pnt(-8,6,25)).Shape()
 for name in ['shaft','pusher_shoulder','unthreaded_tail']:
  p=PARAMETERS[name];s=fuse(s,cylinder(*p['x_mm'],p['radius_mm']))
 s=fuse(s,BRepPrimAPI_MakeCone(axis(-1.2),2.8,4,1.2).Shape())
 assert BRepCheck_Analyzer(s).IsValid() and count(s,TopAbs_SOLID)==1
 return s
def main():
 shape=build();p=GProp_GProps();BRepGProp.VolumeProperties_s(shape,p)
 BRepMesh_IncrementalMesh(shape,.015,False,.08,True).Perform()
 assembly=HERE/(NAME+'_assembly-mm.stl')
 assert StlAPI_Writer().Write(shape,str(assembly))
 mesh=trimesh.load(assembly,force='mesh');mesh.export(assembly,file_type='stl')
 mesh=trimesh.load(assembly,force='mesh');assert mesh.is_watertight and mesh.is_volume
 Interface_Static.SetCVal_s('write.step.schema','AP214')
 writer=STEPControl_Writer();writer.Transfer(shape,STEPControl_AsIs)
 step=HERE/(NAME+'_assembly-mm.step');assert str(writer.Write(str(step))).endswith('RetDone')
 # Broad reaction face down. All outward growth is either on the bed or45°.
 matrix=np.array([[0.,1.,0.,0.],[0.,0.,1.,-13.85],[1.,0.,0.,12.],[0.,0.,0.,1.]])
 assert abs(np.linalg.det(matrix[:3,:3])-1)<1e-12
 printed=mesh.copy();printed.apply_transform(matrix)
 print_stl=HERE/(NAME+'_print-mm.stl');printed.export(print_stl)
 manifest=dict(ref='Q01',name=NAME,status='LOCAL_PRINT_TEST_FIXTURE_NOT_PRODUCT_CAD',
  source=Path(__file__).name,source_sha256=sha(__file__),product_revision='R12',units='mm',quantity=1,
  parameters=PARAMETERS,brep_valid=True,solid_count=1,shell_count=count(shape,TopAbs_SHELL),
  brep_volume_mm3=p.Mass(),stl_watertight=bool(mesh.is_watertight),
  assembly_bounds_mm=mesh.bounds.tolist(),print_bounds_mm=printed.bounds.tolist(),
  assembly_to_print_matrix=matrix.tolist(),
  placement='Reaction block rear X-12 against fixed support; foot Z2.7 on base; P05 shoulder face X1; axis Y0/Z18.',
  contacts=[dict(ref='P01',description='Block rear face seats on new fixed X-12 reaction and foot on pocket floor Z2.7.'),
   dict(ref='P05',description='Shoulder front X1 bears on yoke; plain diameter3 tail enters diameter3.2 bore.')],
  nominal_clearances_mm=dict(tail_radial=.1,block_to_P05_x=1),
  legal_test_domain=dict(preload_p_mm=0,rear_advance_a_mm=0,user_stroke_u_mm=[0,30]),
  print=dict(orientation='Supplied print-mm STL: full12x22.3mm reaction face down, Xaxis vertical.',
   material='PLA unloaded fit proxy',layer_height_mm=.2,wall_loops=4,infill_percent=100,
   supports='None; integral45-degree shoulder taper. Reaction face first layer; P05 shoulder facing upward.',brim_mm=3),
  assembly=[
   'Omit all real sensor-stack parts, springs, spring-seat hardware and isometric sleeves. Never combine Q01 with the real sensor stack.',
   'Place the flat foot on the pocket floor Z2.7 and the broad rear face against the fixed X-12 support. Tail points toward the grip (+X).',
   'Slide P05 from +X over the plain diameter3 tail until its rear bearing face touches the shoulder at X1. Align using the rods; keep gentle compression by hand.',
   'Complete the unloaded carriage and rear-gate assembly. Manually inspect0..30mm travel. Do not apply springs, isometric force or calibration loads.',
   'Remove rear gate/rods as needed, slide P05 +X clear of the tail, then lift Q01 straight upward +Z40 before installing the real sensor stack.'
  ],
  limitations=['No axial latch: support the assembly and keep gentle hand contact; do not lift by Q01.',
   'No force-bearing sensor replacement, calibration tool or strength test specimen.',
   'CAD clearances do not qualify physical print fit, friction, strength or sensor response.'],
  files={q.name:dict(sha256=sha(q),bytes=q.stat().st_size) for q in [assembly,step,print_stl]})
 (HERE/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 print(json.dumps(dict(status='BUILT',print_bounds_mm=manifest['print_bounds_mm'],files=manifest['files']),indent=2))
if __name__=='__main__':main()
