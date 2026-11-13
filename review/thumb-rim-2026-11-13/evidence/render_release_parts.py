#!/usr/bin/env python3
"""Native R19 assembly and separately spaced rigid-parts views; display only."""
from pathlib import Path
import argparse,hashlib,io,json,zipfile,re
import numpy as np,trimesh
from vtkmodules.vtkCommonCore import vtkPoints
from vtkmodules.vtkCommonDataModel import vtkCellArray,vtkPolyData
from vtkmodules.vtkFiltersCore import vtkQuadricDecimation,vtkPolyDataNormals
from vtkmodules.util.numpy_support import numpy_to_vtk,numpy_to_vtkIdTypeArray,vtk_to_numpy
from PIL import Image,ImageDraw,ImageFont
HERE=Path(__file__).resolve().parent;STUDY=HERE.parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
p=argparse.ArgumentParser();p.add_argument('--rigid',action='store_true');args=p.parse_args()
spec=json.loads((STUDY/'onshape-version.json').read_text());archive=STUDY/'native/Flat132_R19_neutral_final.zip';assert sha(archive)==spec['stl_zip_sha256']
meshes=[];source_parts=[]
with zipfile.ZipFile(archive) as z:
 for name in z.namelist():
  if not name.endswith('.stl'):continue
  label=name.removeprefix('Fingerworker MVP - ');match=re.match(r'(P[0-9]+[LR]?|H[0-9]+[a-z]?)\b',label)
  if not match:continue
  ref=match.group(1)
  if args.rigid and ref not in ['P06L','P06R','P08']:continue
  blob=z.read(name);mesh=trimesh.load(io.BytesIO(blob),file_type='stl',process=True)
  if args.rigid and ref.startswith('P06'):
   mesh.apply_translation([-119+(0 if ref=='P06L' else 26),51 if ref=='P06L' else-51,-4.5])
  color=[55.,148.,167.] if ref=='P01' else [233.,167.,90.] if ref in ['P06L','P06R'] else [47.,169.,180.] if ref=='P08' else [184.,190.,194.]
  meshes.append((ref,mesh,color));source_parts.append(dict(ref=ref,native_member=name,native_stl_sha256=hashlib.sha256(blob).hexdigest()))
assert len(meshes)==3 if args.rigid else len(meshes)>10
def display(mesh,budget):
 mesh=mesh.copy();mesh.update_faces(mesh.area_faces!=0);mesh.remove_unreferenced_vertices()
 pts=vtkPoints();pts.SetData(numpy_to_vtk(np.asarray(mesh.vertices,dtype=np.float64),deep=True))
 cells=vtkCellArray();cells.SetCells(len(mesh.faces),numpy_to_vtkIdTypeArray(np.column_stack((np.full(len(mesh.faces),3,dtype=np.int64),mesh.faces)).astype(np.int64).ravel(),deep=True))
 poly=vtkPolyData();poly.SetPoints(pts);poly.SetPolys(cells)
 dec=vtkQuadricDecimation();dec.SetInputData(poly);dec.SetTargetReduction(max(0,1-budget/len(mesh.faces)));dec.Update()
 norm=vtkPolyDataNormals();norm.SetInputConnection(dec.GetOutputPort());norm.SetFeatureAngle(35);norm.SplittingOn();norm.ConsistencyOn();norm.AutoOrientNormalsOn();norm.Update();d=norm.GetOutput()
 return np.asarray(vtk_to_numpy(d.GetPoints().GetData())),np.asarray(vtk_to_numpy(d.GetPolys().GetData())).reshape(-1,4)[:,1:],np.asarray(vtk_to_numpy(d.GetPointData().GetNormals()))
parts=[(name,*display(mesh,50000 if name=='P01' else 12000 if name=='P04' else 8000),np.array(color)) for name,mesh,color in meshes]
eye=np.array([-230.,-290.,230.]);eye/=np.linalg.norm(eye);right=np.cross(-eye,[0,0,1]);right/=np.linalg.norm(right);up=np.cross(right,-eye)
v=np.concatenate([part[1] for part in parts]);pv=np.column_stack((v@right,v@up,v@eye));focus=np.ones(len(v),dtype=bool)
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
draw.text((24,14),'R19 native rigid parts - spaced for inspection' if args.rigid else 'R19 native assembly - two separate solid rear blocks',font=font,fill=(31,67,78))
output=HERE/('rigid-parts-final-native.png' if args.rigid else 'assembly-final-native.png');image.save(output)
report=dict(status='RENDERED_FINAL_NATIVE_R19_RIGID_PARTS' if args.rigid else 'RENDERED_FINAL_NATIVE_R19_ASSEMBLY',source_sha256=spec['source_sha256'],native_zip_sha256=sha(archive),onshape_version=spec['version_id'],image_sha256=sha(output),renderer_sha256=sha(__file__),parts=source_parts,scope='Literal native parts; display decimation only. Rigid-parts view deliberately translates rear blocks for visibility; assembly view uses native coordinates. No geometry change or physical strength assertion.')
output.with_suffix('.json').write_text(json.dumps(report,indent=2)+'\n');print(output)
