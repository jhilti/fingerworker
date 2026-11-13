#!/usr/bin/env python3
"""Independent native-3MF geometry, settings, object/plate and clearance audit."""
from pathlib import Path
from zipfile import ZipFile
import xml.etree.ElementTree as ET,json,hashlib,argparse,math
import numpy as np,trimesh as tm
from scipy.spatial import cKDTree
NS={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}

def meta(node):return {m.get('key'):m.get('value') for m in node.findall('metadata') if m.get('key')}
def matrix(value):
 if not value:return np.eye(3),np.zeros(3)
 a=np.array([float(v) for v in value.split()]).reshape(4,3);return a[:3],a[3]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def audit(pack):
 layout=json.loads((pack/'plate-layout.json').read_text());assert layout['object_count']==13 and layout['plate_count']==3
 project=pack/layout['native_project'];expected={r['ref']:r for r in layout['placements']};reports=[];ROOT=pack.parents[1]
 with ZipFile(project) as z:
  cfg=ET.fromstring(z.read('Metadata/model_settings.config'));objects=cfg.findall('object');plates=cfg.findall('plate');assert len(objects)==13 and len(plates)==3
  assert not any(n.endswith('.gcode') for n in z.namelist())
  settings=json.loads(z.read('Metadata/project_settings.config'));assert settings['filament_type']==['PLA'];assert all(abs(float(d)-.4)<1e-9 for d in settings['nozzle_diameter']);assert settings['printer_model']=='Bambu Lab H2D'
  root=ET.fromstring(z.read('3D/3dmodel.model'));wrappers={o.get('id'):o for o in root.findall('m:resources/m:object',NS)};builds={b.get('objectid'):b for b in root.findall('m:build/m:item',NS)}
  table={};counts=[]
  for i,p in enumerate(plates,1):
   inst=p.findall('model_instance');counts.append(len(inst))
   for n in inst:
    d=meta(n);assert d['object_id'] not in table;table[d['object_id']]=i
  assert counts==[1,11,1],counts
  for o in objects:
   od=meta(o);key=od['name'].split(' - ')[0];row=expected[key];oid=o.get('id');assert row['plate']==table[oid]
   component=wrappers[oid].find('m:components/m:component',NS);path=next((v for k,v in component.attrib.items() if k.endswith('path')),None);assert path
   node=ET.fromstring(z.read(path.lstrip('/')));mesh=node.find('.//m:mesh',NS);assert mesh is not None
   v=np.array([[float(n.get(k)) for k in 'xyz'] for n in mesh.findall('m:vertices/m:vertex',NS)]);faces=np.array([[int(n.get(k)) for k in ['v1','v2','v3']] for n in mesh.findall('m:triangles/m:triangle',NS)])
   A,t=matrix(component.get('transform'));local=v@A+t;A2,t2=matrix(builds[oid].get('transform'));world=local@A2+t2
   src=ROOT/row['source_path'];assert sha(src)==row['source_sha256'];s=tm.load_mesh(src);R=np.array(row['rotation_3x3']);wanted=s.vertices@R.T;wanted-=wanted.min(axis=0);actual=local-local.min(axis=0)
   assert len(v)==len(s.vertices) and len(faces)==len(s.faces),(key,len(v),len(s.vertices))
   error=float(cKDTree(wanted).query(actual)[0].max());assert error<.0001,(key,error)
   meshNative=tm.Trimesh(vertices=actual,faces=faces,process=False);assert meshNative.is_watertight and meshNative.is_volume,(key,'native invalid')
   assert abs(abs(meshNative.volume)-abs(s.volume))<max(.01,abs(s.volume)*1e-6),(key,'volume')
   assert int(row['scale'])==1 and abs(np.linalg.det(R)-1)<1e-9
   p=row['plate'];col=(p-1)%2;line=(p-1)//2;orig=np.array([420*col,-384*line,0]);bedmin=world.min(axis=0)-orig
   # Current official Bambu display grid is two columns for three plates.
   # Verify world position against that convention, plus original seed positions.
   xy=np.asarray(row['plate_xy_mm']);position_error=float(np.max(abs(bedmin[:2]-xy)));assert position_error<.0001,(key,'placement',bedmin,xy)
   assert abs(bedmin[2])<.0001,(key,'floating')
   margin=row['reserved_margin_mm'];b=[*list(bedmin[:2]-margin),*list(bedmin[:2]+meshNative.extents[:2]+margin)];assert b[0]>=27-1e-4 and b[1]>=3-1e-4 and b[2]<=323+1e-4 and b[3]<=317+1e-4,(key,'boundary')
   if key=='P04':
    for k,val in {'support_type':'tree(auto)','support_style':'tree_slim','support_on_build_plate_only':'1','support_top_z_distance':'0.25'}.items():assert od[k]==val,(k,od.get(k))
   reports.append({'ref':key,'plate':p,'roundtrip_max_vertex_error_mm':error,'native_watertight':bool(meshNative.is_watertight),'source_sha256':sha(src),'native_volume_mm3':float(meshNative.volume),'bed_min_mm':bedmin.tolist(),'reserved_bbox_xy_mm':b})
  for i,r in enumerate(reports):
   for q in reports[:i]:
    if q['plate']!=r['plate']:continue
    a=r['reserved_bbox_xy_mm'];b=q['reserved_bbox_xy_mm'];assert a[2]+1.49<=b[0] or b[2]+1.49<=a[0] or a[3]+1.49<=b[1] or b[3]+1.49<=a[1],(r['ref'],q['ref'],'overlap')
  old=json.loads((ROOT/'print/bambu-R10-integrated-palm-2026-11-03/profiles/project_settings_H2D.json').read_text())
  for k in ['machine_start_gcode','machine_end_gcode','change_filament_gcode','before_layer_change_gcode','layer_change_gcode']:assert settings.get(k)==old.get(k),(k,'stock macro changed')
 return {'status':'PASS','scope':'Independent native 3MF raw XML, source-mesh comparison, plate counts and physical placement, material/nozzle, support settings, unchanged machine macros','project_sha256':sha(project),'object_count':13,'plate_counts':counts,'material':'PLA','nozzle_mm':.4,'native_gcode_present':False,'all_roundtrip_errors_below_mm':.0001,'objects':reports}
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--pack',type=Path,required=True);a.add_argument('--output',type=Path,required=True);s=a.parse_args();r=audit(s.pack.resolve());s.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:r[k] for k in ['status','object_count','plate_counts','material','nozzle_mm']},indent=2))
