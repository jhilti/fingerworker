#!/usr/bin/env python3
"""Literal native mesh detail: cropped rear pocket and block underside, separate views."""
from pathlib import Path
import hashlib,io,json,zipfile
import numpy as np,trimesh
from PIL import Image,ImageDraw,ImageFont
from vtkmodules.vtkCommonCore import vtkPoints
from vtkmodules.vtkCommonDataModel import vtkCellArray,vtkPolyData
from vtkmodules.vtkFiltersCore import vtkPolyDataNormals
from vtkmodules.util.numpy_support import numpy_to_vtk,numpy_to_vtkIdTypeArray,vtk_to_numpy
HERE=Path(__file__).resolve().parent;STUDY=HERE.parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
spec=json.loads((STUDY/'onshape-version.json').read_text());archive=STUDY/'native/Flat132_R20_neutral_final.zip';assert sha(archive)==spec['stl_zip_sha256']
meshes={};members={}
with zipfile.ZipFile(archive) as z:
 for ref in ['P01','P06L']:
  name=next(n for n in z.namelist() if n.startswith('Fingerworker MVP - '+ref+' '));blob=z.read(name)
  meshes[ref]=trimesh.load(io.BytesIO(blob),file_type='stl',process=True);members[ref]=dict(member=name,sha256=hashlib.sha256(blob).hexdigest())

def render(mesh,eye,base):
 mesh=mesh.copy();mesh.update_faces(mesh.area_faces!=0);mesh.remove_unreferenced_vertices()
 pts=vtkPoints();pts.SetData(numpy_to_vtk(np.asarray(mesh.vertices,dtype=np.float64),deep=True));cells=vtkCellArray();cells.SetCells(len(mesh.faces),numpy_to_vtkIdTypeArray(np.column_stack((np.full(len(mesh.faces),3,dtype=np.int64),mesh.faces)).astype(np.int64).ravel(),deep=True))
 poly=vtkPolyData();poly.SetPoints(pts);poly.SetPolys(cells);norm=vtkPolyDataNormals();norm.SetInputData(poly);norm.SetFeatureAngle(35);norm.SplittingOn();norm.ConsistencyOn();norm.Update();d=norm.GetOutput()
 v=np.asarray(vtk_to_numpy(d.GetPoints().GetData()));f=np.asarray(vtk_to_numpy(d.GetPolys().GetData())).reshape(-1,4)[:,1:];ns=np.asarray(vtk_to_numpy(d.GetPointData().GetNormals()))
 eye=np.array(eye,dtype=float);eye/=np.linalg.norm(eye);right=np.cross(-eye,[0,0,1]);right/=np.linalg.norm(right);up=np.cross(right,-eye)
 pv=np.column_stack((v@right,v@up,v@eye));lo=pv[:,:2].min(0);hi=pv[:,:2].max(0);w,h=820,830;scale=min((w-130)/(hi[0]-lo[0]),(h-160)/(hi[1]-lo[1]))
 pv[:,0]=(pv[:,0]-(lo[0]+hi[0])/2)*scale+w/2;pv[:,1]=h/2+25-(pv[:,1]-(lo[1]+hi[1])/2)*scale
 pixels=np.full((h,w,3),[245,249,250],dtype=np.uint8);depth=np.full((h,w),-np.inf);light=eye.copy();light[2]+=1 if eye[2]>0 else-1;light/=np.linalg.norm(light);base=np.array(base)
 for ids in f:
  t=pv[ids];x0,y0=np.maximum(np.floor(t[:,:2].min(0)).astype(int),[0,0]);x1,y1=np.minimum(np.ceil(t[:,:2].max(0)).astype(int),[w-1,h-1])
  if x0>x1 or y0>y1:continue
  xx,yy=np.meshgrid(np.arange(x0,x1+1)+.5,np.arange(y0,y1+1)+.5);den=(t[1,1]-t[2,1])*(t[0,0]-t[2,0])+(t[2,0]-t[1,0])*(t[0,1]-t[2,1])
  if abs(den)<1e-12:continue
  a=((t[1,1]-t[2,1])*(xx-t[2,0])+(t[2,0]-t[1,0])*(yy-t[2,1]))/den;bb=((t[2,1]-t[0,1])*(xx-t[2,0])+(t[0,0]-t[2,0])*(yy-t[2,1]))/den;c=1-a-bb
  z=a*t[0,2]+bb*t[1,2]+c*t[2,2];db=depth[y0:y1+1,x0:x1+1];mask=(a>=-1e-8)&(bb>=-1e-8)&(c>=-1e-8)&(z>db)
  if not np.any(mask):continue
  n=a[mask,None]*ns[ids[0]]+bb[mask,None]*ns[ids[1]]+c[mask,None]*ns[ids[2]];n/=np.maximum(np.linalg.norm(n,axis=1)[:,None],1e-12)
  colors=np.clip(base[None,:]*(.4+.6*np.clip(n@light,0,1))[:,None],0,255).astype(np.uint8);db[mask]=z[mask];pixels[y0:y1+1,x0:x1+1][mask]=colors
 return Image.fromarray(pixels)

frame=meshes['P01']
for origin,normal in [([116,0,0],[1,0,0]),([0,-67,0],[0,1,0]),([0,-35,0],[0,-1,0])]:frame=frame.slice_plane(origin,normal)
left=render(frame,[180,-230,220],[55,148,167]);right=render(meshes['P06L'],[180,-250,-200],[233,167,90])
image=Image.new('RGB',(1680,1000),(245,249,250));image.paste(left,(20,80));image.paste(right,(840,80));d=ImageDraw.Draw(image);font=ImageFont.load_default(size=24);small=ImageFont.load_default(size=20)
d.text((28,18),'R20 native CAD - rear locating fit, mirrored on both sides',font=font,fill=(31,67,78))
d.text((35,67),'P01 - rear pocket (cropped view)',font=small,fill=(31,67,78));d.text((860,67),'P06L - underside with integral peg',font=small,fill=(31,67,78))
d.text((35,925),'Rear-open entry; 5.4 mm wide; blind bottom',font=small,fill=(31,67,78));d.text((860,925),'Diameter 5 x 2 mm; R0.4 root; chamfered tip',font=small,fill=(31,67,78))
d.text((35,966),'Unloaded spring-free locating only. Four M3 screws are required before spring preload or load.',font=small,fill=(31,67,78))
out=HERE/'rear-locator-detail.png';image.save(out)
report=dict(status='RENDERED_NATIVE_R20_LOCATOR_DETAIL',source_sha256=spec['source_sha256'],onshape_version=spec['version_id'],native_zip_sha256=sha(archive),image_sha256=sha(out),renderer_sha256=sha(__file__),parts=members,scope='Native STL meshes only. Left frame is clipped at X116/Y-67/-35 for a labelled inspection detail; right is the complete rear-block underside. Separate cameras; not an assembled pose or manufacturing modification.')
out.with_suffix('.json').write_text(json.dumps(report,indent=2)+'\n');print(out)
