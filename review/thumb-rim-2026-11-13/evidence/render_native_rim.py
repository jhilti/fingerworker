#!/usr/bin/env python3
"""Render literal exported native R19 rim geometry; display decimation only."""
from pathlib import Path
import argparse,hashlib,json,sys
import numpy as np,trimesh
from vtkmodules.vtkCommonCore import vtkPoints
from vtkmodules.vtkCommonDataModel import vtkCellArray,vtkPolyData
from vtkmodules.vtkFiltersCore import vtkQuadricDecimation,vtkPolyDataNormals
from vtkmodules.util.numpy_support import numpy_to_vtk,numpy_to_vtkIdTypeArray,vtk_to_numpy
from PIL import Image,ImageDraw,ImageFont
HERE=Path(__file__).resolve().parent;STUDY=HERE.parent
sys.path.insert(0,str(STUDY/'mechanics'));import thumb_rim as m
sha=m.sha
p=argparse.ArgumentParser();p.add_argument('--step',required=True);p.add_argument('--source',required=True);p.add_argument('--detail',action='store_true');args=p.parse_args()
step=Path(args.step);source=Path(args.source);solids,_,_=m.b.read_step(step)
old,_=m.load();expected_bounds=m.b.bounds(old['P01'])
frame_candidates=[s for s in solids if np.max(np.abs(m.b.bounds(s)-expected_bounds))<.01]
assert len(frame_candidates)==1
frame=frame_candidates[0];stembase=HERE/'P01-native-rim-probe';m.prior.export(frame,stembase)
native_blob=stembase.with_suffix('.stl').read_bytes()
meshes=[('P01',trimesh.load(stembase.with_suffix('.stl'),process=True),[55.,148.,167.])]
p05stem=HERE/'P05-reference';m.prior.export(old['P05'],p05stem);p05sha=sha(p05stem.with_suffix('.stl'))
meshes.append(('P05',trimesh.load(p05stem.with_suffix('.stl'),process=True),[177.,181.,184.]))
def display(mesh,budget):
 mesh=mesh.copy();mesh.update_faces(mesh.area_faces!=0);mesh.remove_unreferenced_vertices();assert mesh.is_watertight and mesh.is_winding_consistent
 pts=vtkPoints();pts.SetData(numpy_to_vtk(np.asarray(mesh.vertices,dtype=np.float64),deep=True))
 cells=vtkCellArray();cells.SetCells(len(mesh.faces),numpy_to_vtkIdTypeArray(np.column_stack((np.full(len(mesh.faces),3,dtype=np.int64),mesh.faces)).astype(np.int64).ravel(),deep=True))
 poly=vtkPolyData();poly.SetPoints(pts);poly.SetPolys(cells)
 dec=vtkQuadricDecimation();dec.SetInputData(poly);dec.SetTargetReduction(max(0,1-budget/len(mesh.faces)));dec.Update()
 norm=vtkPolyDataNormals();norm.SetInputConnection(dec.GetOutputPort());norm.SetFeatureAngle(35);norm.SplittingOn();norm.ConsistencyOn();norm.AutoOrientNormalsOn();norm.Update();d=norm.GetOutput()
 return np.asarray(vtk_to_numpy(d.GetPoints().GetData())),np.asarray(vtk_to_numpy(d.GetPolys().GetData())).reshape(-1,4)[:,1:],np.asarray(vtk_to_numpy(d.GetPointData().GetNormals()))
parts=[(name,*display(mesh,100000000),np.array(color)) for name,mesh,color in meshes]
eye=np.array([-230.,-400.,210.] if args.detail else [-230.,-290.,230.]);eye/=np.linalg.norm(eye);right=np.cross(-eye,[0,0,1]);right/=np.linalg.norm(right);up=np.cross(right,-eye)
v=parts[0][1];pv=np.column_stack((v@right,v@up,v@eye));focus=(v[:,0]<-10)&(v[:,0]>-32)&(v[:,1]<-56)&(v[:,2]>18) if args.detail else np.ones(len(v),dtype=bool)
lo=pv[focus,:2].min(0);hi=pv[focus,:2].max(0);width,height=1680,1080;scale=min((width-130)/(hi[0]-lo[0]),(height-160)/(hi[1]-lo[1]))
pixels=np.empty((height,width,3),dtype=np.uint8);pixels[:]=[245,249,250];depth=np.full((height,width),-np.inf);light=np.array([-.35,-.4,1.]);light/=np.linalg.norm(light)
for name,v,f,vertex_normals,base in parts:
 pv=np.column_stack((v@right,v@up,v@eye));pv[:,0]=(pv[:,0]-(lo[0]+hi[0])/2)*scale+width/2;pv[:,1]=height/2+20-(pv[:,1]-(lo[1]+hi[1])/2)*scale
 for indices in f:
  t=pv[indices];x0,y0=np.maximum(np.floor(t[:,:2].min(0)).astype(int),[0,0]);x1,y1=np.minimum(np.ceil(t[:,:2].max(0)).astype(int),[width-1,height-1])
  if x0>x1 or y0>y1:continue
  xx,yy=np.meshgrid(np.arange(x0,x1+1)+.5,np.arange(y0,y1+1)+.5);den=(t[1,1]-t[2,1])*(t[0,0]-t[2,0])+(t[2,0]-t[1,0])*(t[0,1]-t[2,1])
  if abs(den)<1e-12:continue
  a=((t[1,1]-t[2,1])*(xx-t[2,0])+(t[2,0]-t[1,0])*(yy-t[2,1]))/den;bb=((t[2,1]-t[0,1])*(xx-t[2,0])+(t[0,0]-t[2,0])*(yy-t[2,1]))/den;c=1-a-bb
  z=a*t[0,2]+bb*t[1,2]+c*t[2,2];db=depth[y0:y1+1,x0:x1+1];mask=(a>=-1e-8)&(bb>=-1e-8)&(c>=-1e-8)&(z>db)
  if not np.any(mask):continue
  ns=a[mask,None]*vertex_normals[indices[0]]+bb[mask,None]*vertex_normals[indices[1]]+c[mask,None]*vertex_normals[indices[2]];ns/=np.maximum(np.linalg.norm(ns,axis=1)[:,None],1e-12)
  colors=np.clip(base[None,:]*(.40+.60*np.clip(ns@light,0,1))[:,None],0,255).astype(np.uint8);db[mask]=z[mask];pixels[y0:y1+1,x0:x1+1][mask]=colors
image=Image.fromarray(pixels);draw=ImageDraw.Draw(image);draw.rectangle((0,0,width,52),fill=(245,249,250));font=ImageFont.load_default(size=23)
draw.text((24,14),'R19 native trial - softly rounded thumb recess',font=font,fill=(31,67,78))
if args.detail:draw.text((1030,14),'One side shown; both sides changed',font=font,fill=(31,67,78))
output=HERE/('P01-native-rim-detail.png' if args.detail else 'P01-native-rim-full.png');image.save(output)
report=dict(status='RENDERED_NATIVE_R19_TRIAL',source_sha256=sha(source),native_step_sha256=sha(step),image_sha256=sha(output),renderer_sha256=sha(__file__),scope='Actual native STEP geometry; exactly zero-area triangles omitted for display, no decimation; camera crop only. P05 reference is unchanged R18 body. Not a final release render until independent checks pass.')
output.with_suffix('.json').write_text(json.dumps(report,indent=2)+'\n');print(output)
