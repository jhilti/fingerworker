#!/usr/bin/env python3
"""Engineering preview of actual local R17 P01; display decimation only."""
from pathlib import Path
import argparse,hashlib,io,json,zipfile
import numpy as np,trimesh
from vtkmodules.vtkCommonCore import vtkPoints
from vtkmodules.vtkCommonDataModel import vtkCellArray,vtkPolyData
from vtkmodules.vtkFiltersCore import vtkQuadricDecimation,vtkPolyDataNormals
from vtkmodules.util.numpy_support import numpy_to_vtk,numpy_to_vtkIdTypeArray,vtk_to_numpy
from PIL import Image,ImageDraw,ImageFont
HERE=Path(__file__).resolve().parent;STUDY=HERE.parent;ROOT=STUDY.parents[1]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
p=argparse.ArgumentParser();p.add_argument('--detail',action='store_true');args=p.parse_args()
spec=json.loads((HERE/'design-specification.json').read_text());meshpath=HERE/'P01_side_thumb.stl';assert sha(meshpath)==spec['mesh']['sha256']
meshes=[('P01',trimesh.load(meshpath,process=True),[55.,148.,167.])];p05sha=None
if args.detail:
 with zipfile.ZipFile(ROOT/'review/upright-grip-2026-11-09/native/Flat132_R16_neutral_final.zip') as z:
  member=next(n for n in z.namelist() if n.startswith('Fingerworker MVP - P05 '));blob=z.read(member);p05sha=hashlib.sha256(blob).hexdigest()
 meshes.append(('P05',trimesh.load(io.BytesIO(blob),file_type='stl',process=True),[177.,181.,184.]))
def display(mesh,budget):
 pts=vtkPoints();pts.SetData(numpy_to_vtk(np.asarray(mesh.vertices,dtype=np.float64),deep=True))
 cells=vtkCellArray();cells.SetCells(len(mesh.faces),numpy_to_vtkIdTypeArray(np.column_stack((np.full(len(mesh.faces),3,dtype=np.int64),mesh.faces)).astype(np.int64).ravel(),deep=True))
 poly=vtkPolyData();poly.SetPoints(pts);poly.SetPolys(cells)
 dec=vtkQuadricDecimation();dec.SetInputData(poly);dec.SetTargetReduction(max(0,1-budget/len(mesh.faces)));dec.Update()
 norm=vtkPolyDataNormals();norm.SetInputConnection(dec.GetOutputPort());norm.SetFeatureAngle(35);norm.SplittingOn();norm.ConsistencyOn();norm.AutoOrientNormalsOn();norm.Update();d=norm.GetOutput()
 return np.asarray(vtk_to_numpy(d.GetPoints().GetData())),np.asarray(vtk_to_numpy(d.GetPolys().GetData())).reshape(-1,4)[:,1:],np.asarray(vtk_to_numpy(d.GetPointData().GetNormals()))
parts=[(name,*display(mesh,40000 if name=='P01' else 10000),np.array(color)) for name,mesh,color in meshes]
eye=np.array([-230.,-400.,210.] if args.detail else [-230.,-290.,230.]);eye/=np.linalg.norm(eye);right=np.cross(-eye,[0,0,1]);right/=np.linalg.norm(right);up=np.cross(right,-eye)
v=parts[0][1];pv=np.column_stack((v@right,v@up,v@eye));focus=(v[:,0]<-6)&(v[:,1]<-34)&(v[:,2]>7) if args.detail else np.ones(len(v),dtype=bool)
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
draw.text((24,14),'R17 local prototype - Onshape sync pending',font=font,fill=(31,67,78))
if args.detail:draw.text((930,14),'Blue: fixed P01   Grey: unchanged P05',font=font,fill=(31,67,78))
output=HERE/('P01-prototype-thumb-detail.png' if args.detail else 'P01-prototype-full.png');image.save(output)
report=dict(status='RENDERED_LOCAL_R17_PROTOTYPE',source_sha256=spec['source_sha256'],candidate_stl_sha256=sha(meshpath),image_sha256=sha(output),renderer_sha256=sha(__file__),P05_native_stl_sha256=p05sha,scope='Actual local CSG preview; simplified display meshes only. Detail contains unchanged native R16 P05 in grey. Camera crop only, no geometry clipping. Native Onshape regeneration pending.')
output.with_suffix('.json').write_text(json.dumps(report,indent=2)+'\n');print(output)
