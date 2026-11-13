#!/usr/bin/env python3
"""Independent P02-only project geometry and functional-face orientation comparison."""
from pathlib import Path
import json,hashlib,zipfile,xml.etree.ElementTree as ET,re,math
import numpy as np,trimesh
import audit_bambu_project as a
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];OUT=ROOT/'print/bambu-R9-palm-bracing-2026-10-25';CAD=ROOT/'review/flat132-palm-bracing-2026-10-25'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
NS=a.NS;P=a.P

def actual_mesh(z):
 docs={}
 def node(path,ident):
  if path not in docs:docs[path]=ET.fromstring(z.read(path))
  root=docs[path];assert root.get('unit')=='millimeter';o=next(x for x in root.findall('m:resources/m:object',NS) if x.get('id')==ident);m=o.find('m:mesh',NS)
  if m is not None:return np.array([[float(v.get(k)) for k in ['x','y','z']] for v in m.findall('m:vertices/m:vertex',NS)]),np.array([[int(t.get(k)) for k in ['v1','v2','v3']] for t in m.findall('m:triangles/m:triangle',NS)])
  children=o.findall('m:components/m:component',NS);assert len(children)==1;c=children[0];vv,ff=node(c.get(P+'path',path).lstrip('/'),c.get('objectid'));t=a.trans(c.get('transform'));return vv@t[:3,:3].T+t[:3,3],ff
 root=ET.fromstring(z.read('3D/3dmodel.model'));items=root.findall('m:build/m:item',NS);assert len(items)==1;item=items[0];vv,ff=node('3D/3dmodel.model',item.get('objectid'));t=a.trans(item.get('transform'));return vv@t[:3,:3].T+t[:3,3],ff

def inspect_case(tag,R):
 proj=OUT/f'Fingerworker_R9_{tag}_H2D_04mm_PLA.3mf';arc=OUT/f'validation/Fingerworker_R9_{tag}_H2D_04mm_PLA_verification.gcode.3mf';z=zipfile.ZipFile(proj);gz=zipfile.ZipFile(arc);source=trimesh.load(CAD/'print-mm/P02.stl',force='mesh');oriented=source.vertices@R.T;tt=-oriented.min(axis=0)+[163.25,96,0];expected=oriented+tt;vv,ff=actual_mesh(z);mapping,error=a.correspondence(vv,expected);same=np.array_equal(a.sorted_faces(mapping[ff]),a.sorted_faces(source.faces))
 checks=[]
 def add(name,test,**e):checks.append(dict(name=name,status='PASS' if test else'FAIL',**e))
 add('One whole1:1 native P02 mesh with proper rotation',same and error<3e-5 and abs(np.linalg.det(R)-1)<1e-10,max_vertex_error_mm=error,triangles=len(ff),determinant=float(np.linalg.det(R)))
 add('Both project archives CRC',z.testzip() is None and gz.testzip() is None)
 globalsettings=json.loads(z.read('Metadata/project_settings.config'));full=json.loads(zipfile.ZipFile(OUT/'Fingerworker_R9_H2D_04mm_PLA_Fit_Test.3mf').read('Metadata/project_settings.config'));add('Same official PLA/H2D global settings as full19',globalsettings==full)
 cfg=ET.fromstring(z.read('Metadata/model_settings.config'));objects=cfg.findall('object');plates=cfg.findall('plate');add('One editable object/plate',len(objects)==len(plates)==1)
 settings=a.md(objects[0]);base=json.loads((OUT/'palm-only-layout.json').read_text())['settings'];add('Same P02 per-object support/brim settings',all(settings.get(k)==str(v) for k,v in base.items()))
 g=gz.read('Metadata/plate_1.gcode').decode();pos=np.zeros(3);obj=None;feature='';width=.4;segments=[];bounds=[np.full(3,1e9),np.full(3,-1e9)];first=0.;last=0.;model=0;maxwidth=0.
 for line in g.splitlines():
  if line.startswith('; start printing object'):obj=True
  elif line.startswith('; stop printing object'):obj=None
  elif line.startswith('; FEATURE: '):
   feature=line[11:].strip();obj=feature not in ['', 'Custom']
  elif line.startswith('; LINE_WIDTH: '):width=float(line.split(':')[1])
  elif re.match(r'^G[0123] ',line):
   vals={k:float(v) for k,v in re.findall(r'([XYZEFIJ])(-?\d*\.?\d+)',line.split(';')[0])};new=np.array([vals.get(k,pos[j]) for j,k in enumerate('XYZ')]);distance=float(np.linalg.norm(new[:2]-pos[:2]))
   if obj and vals.get('E',0)>0 and distance>1e-6:
    mid=((pos+new)/2-tt)@R;segments.append((feature,mid,new[2]));bounds=[np.minimum(bounds[0],np.minimum(pos,new)),np.maximum(bounds[1],np.maximum(pos,new))];maxwidth=max(maxwidth,width)
    if feature not in ['Support','Support interface','Brim','Skirt']:
     model+=1;last=max(last,new[2]);
     if new[2]<=.20001:first+=distance
   pos=new
 add('Actual positive first-layer and complete-height model',first>0 and model>0 and abs(last-36.6)<.001,first_layer_model_path_mm=first,last_model_z_mm=last,model_segments=model)
 add('All P02-only positive path bounds inside shared bed',all(bounds[0][:2]-maxwidth/2>=[27,3]) and all(bounds[1][:2]+maxwidth/2<=[323,317]),centreline_bounds_mm=[b.tolist() for b in bounds],max_line_width_mm=maxwidth)
 faces=[]
 for side,y0,y1 in [('left',-25,-18),('right',18,25)]:
  adjacent=[(f,p,z) for f,p,z in segments if f.startswith('Support') and -22.75<=p[0]<=-21.5 and y0+.1<=p[1]<=y1-.1 and 14.1<=p[2]<=26.9]
  top=[p for f,p,z in segments if f=='Top surface' and abs(p[0]+22.75)<.3 and y0+.1<=p[1]<=y1-.1 and 14.1<=p[2]<=26.9]
  face=dict(side=side,normal_z_print=float(R[2,0]),adjacent_support_segments=len(adjacent),top_surface_segments=len(top),top_surface_native_x_range_mm=[min((p[0] for p in top),default=None),max((p[0] for p in top),default=None)])
  add('Bearing-face actual strategy '+side,(len(adjacent)==0 and len(top)>0) if R[2,0]>0 else len(adjacent)>0,**face);faces.append(face)
 contact=source.triangles@R.T;bottom=oriented[:,2].min();on=np.all(abs(contact[:,:,2]-bottom)<1e-5,axis=1);contact_area=float(source.area_faces[on].sum())
 return dict(status='PASS' if all(c['status']=='PASS' for c in checks) else'FAIL',project=str(proj),project_sha256=sha(proj),sliced_archive_sha256=sha(arc),source_stl_sha256=sha(CAD/'print-mm/P02.stl'),source_to_print_rotation=R.tolist(),source_to_print_translation=tt.tolist(),source_minimum_plane_contact_area_mm2=contact_area,faces=faces,checks=checks,header=g[:g.find('; HEADER_BLOCK_END')+len('; HEADER_BLOCK_END')])

def main():
 rows=[inspect_case('P02_only',np.array([[0,0,1],[0,1,0],[-1,0,0]])),inspect_case('P02_wrist_down',np.array([[0,0,-1],[0,1,0],[1,0,0]]))]
 result=dict(status='PASS_P02_ORIENTATION_COMPARISON' if all(x['status']=='PASS' for x in rows) else'FAIL',cases=rows,recommendation='Wrist-ledge Xmin down: bearing faces print upward with top skin and no adjacent support; lid-gap face remains vertical. Curved wrist skin may need gentle support cleanup/comfort finishing. Retain brim5 and normal plate supports; this is an unloaded fit print, not a load rating.')
 (HERE/'qa-palm-only-comparison.json').write_text(json.dumps(result,indent=2)+'\n');print(result['status']);print(json.dumps([dict(project=x['project'],status=x['status'],faces=x['faces'],contact=x['source_minimum_plane_contact_area_mm2'],failed=[c for c in x['checks'] if c['status']=='FAIL']) for x in rows],indent=2));assert result['status'].startswith('PASS')
if __name__=='__main__':main()
