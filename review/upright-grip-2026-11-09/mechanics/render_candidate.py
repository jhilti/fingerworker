#!/usr/bin/env python3
"""Render local candidate P01 for review; VTK display decimation + CPU z-buffer."""
from pathlib import Path
import hashlib,io,json,zipfile
import numpy as np,trimesh
from vtkmodules.vtkCommonCore import vtkPoints
from vtkmodules.vtkCommonDataModel import vtkCellArray,vtkPolyData
from vtkmodules.vtkFiltersCore import vtkQuadricDecimation,vtkPolyDataNormals
from vtkmodules.util.numpy_support import numpy_to_vtk,numpy_to_vtkIdTypeArray
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from vtkmodules.util.numpy_support import vtk_to_numpy
HERE=Path(__file__).resolve().parent;STUDY=HERE.parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text())
meshpath=HERE/'P01_upright_grip.stl'
mesh=trimesh.load(meshpath,process=True)
pts=vtkPoints();pts.SetData(numpy_to_vtk(np.asarray(mesh.vertices,dtype=np.float64),deep=True))
cells=vtkCellArray();cells.SetCells(len(mesh.faces),numpy_to_vtkIdTypeArray(np.column_stack((np.full(len(mesh.faces),3,dtype=np.int64),mesh.faces)).astype(np.int64).ravel(),deep=True))
poly=vtkPolyData();poly.SetPoints(pts);poly.SetPolys(cells)
dec=vtkQuadricDecimation();dec.SetInputData(poly);dec.SetTargetReduction(max(0,1-40000/len(mesh.faces)));dec.Update()
norm=vtkPolyDataNormals();norm.SetInputConnection(dec.GetOutputPort());norm.SetFeatureAngle(35);norm.SplittingOn();norm.ConsistencyOn();norm.AutoOrientNormalsOn();norm.Update()
from PIL import Image
from vtkmodules.util.numpy_support import vtk_to_numpy
display=norm.GetOutput();v=np.asarray(vtk_to_numpy(display.GetPoints().GetData()));f=np.asarray(vtk_to_numpy(display.GetPolys().GetData())).reshape(-1,4)[:,1:]
vertex_normals=np.asarray(vtk_to_numpy(display.GetPointData().GetNormals()))
eye=np.array([-230.,-290.,230.]);eye/=np.linalg.norm(eye);right=np.cross(-eye,[0,0,1]);right/=np.linalg.norm(right);up=np.cross(right,-eye)
pv=np.column_stack((v@right,v@up,v@eye));lo=pv[:,:2].min(0);hi=pv[:,:2].max(0)
width,height=1680,1080;scale=min((width-130)/(hi[0]-lo[0]),(height-130)/(hi[1]-lo[1]))
pv[:,0]=(pv[:,0]-(lo[0]+hi[0])/2)*scale+width/2;pv[:,1]=height/2-(pv[:,1]-(lo[1]+hi[1])/2)*scale
pixels=np.empty((height,width,3),dtype=np.uint8);pixels[:]=[245,249,250];depth=np.full((height,width),-np.inf)
light=np.array([-.35,-.4,1.]);light/=np.linalg.norm(light)
base=np.array([55.,148.,167.])
for indices in f:
 t=pv[indices];x0,y0=np.maximum(np.floor(t[:,:2].min(0)).astype(int),[0,0]);x1,y1=np.minimum(np.ceil(t[:,:2].max(0)).astype(int),[width-1,height-1])
 if x0>x1 or y0>y1:continue
 xx,yy=np.meshgrid(np.arange(x0,x1+1)+.5,np.arange(y0,y1+1)+.5)
 den=(t[1,1]-t[2,1])*(t[0,0]-t[2,0])+(t[2,0]-t[1,0])*(t[0,1]-t[2,1])
 if abs(den)<1e-12:continue
 a=((t[1,1]-t[2,1])*(xx-t[2,0])+(t[2,0]-t[1,0])*(yy-t[2,1]))/den
 bb=((t[2,1]-t[0,1])*(xx-t[2,0])+(t[0,0]-t[2,0])*(yy-t[2,1]))/den;c=1-a-bb
 z=a*t[0,2]+bb*t[1,2]+c*t[2,2];db=depth[y0:y1+1,x0:x1+1]
 mask=(a>=-1e-8)&(bb>=-1e-8)&(c>=-1e-8)&(z>db)
 if not np.any(mask):continue
 ns=a[mask,None]*vertex_normals[indices[0]]+bb[mask,None]*vertex_normals[indices[1]]+c[mask,None]*vertex_normals[indices[2]]
 ns/=np.maximum(np.linalg.norm(ns,axis=1)[:,None],1e-12)
 intensity=.40+.60*np.clip(ns@light,0,1)
 colors=np.clip(base[None,:]*intensity[:,None],0,255).astype(np.uint8)
 db[mask]=z[mask];pixels[y0:y1+1,x0:x1+1][mask]=colors
output=HERE/'P01-candidate-iso.png';Image.fromarray(pixels).save(output)
print(output)
