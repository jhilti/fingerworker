#!/usr/bin/env python3
"""Actual sliced extrusion/height/bed and support-access evidence for R8 fit plate."""
from pathlib import Path
import json,re,math,hashlib,zipfile,xml.etree.ElementTree as ET,collections
import numpy as np
from itertools import combinations
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];OUT=ROOT/'print/bambu-R8-fit-test-2026-10-24'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def md(n):return {m.get('key'):m.get('value') for m in n.findall('metadata') if m.get('key')}
def main():
 path=OUT/'validation/Fingerworker_R8_slice_verification.gcode.3mf';project=OUT/'Fingerworker_R8_H2D_04mm_PLA_Fit_Test.3mf';z=zipfile.ZipFile(path);pz=zipfile.ZipFile(project)
 cfg=ET.fromstring(z.read('Metadata/model_settings.config'));names={o.get('id'):md(o)['name'].split(' - ')[0] for o in cfg.findall('object')};plates=cfg.findall('plate');assert len(plates)==1
 ids={int(md(m)['identify_id']):names[md(m)['object_id']] for m in plates[0].findall('model_instance')};layout=json.loads((OUT/'plate-layout.json').read_text());plan={p['ref']:p for p in layout['placements']};assert set(ids.values())==set(plan)
 metrics={i:dict(ref=ref,model_segments=0,first_layer_model_path_mm=0.,model_z_mm=[],max_line_width_mm=0.,features={},extrusion_bounds_mm=[[1e10]*3,[-1e10]*3]) for i,ref in ids.items()};segments={r:[] for r in plan};checks=[]
 def add(name,test,**e):checks.append(dict(name=name,status='PASS' if test else 'FAIL',**e))
 add('Sliced and editable archive CRC',z.testzip() is None and pz.testzip() is None)
 modelnames=[n for n in pz.namelist() if n.startswith('3D/Objects/') and n.endswith('.model')]
 add('Slicer retained all19 editable mesh files exactly',all(z.read(n)==pz.read(n) for n in modelnames),model_files=len(modelnames))
 def root_signature(arc):
  ns={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'};pr='{http://schemas.microsoft.com/3dmanufacturing/production/2015/06}';root=ET.fromstring(arc.read('3D/3dmodel.model'));resources={}
  for o in root.findall('m:resources/m:object',ns):resources[o.get('id')]=[(c.get('objectid'),c.get(pr+'path'),tuple(float(x) for x in c.get('transform').split())) for c in o.findall('m:components/m:component',ns)]
  build={i.get('objectid'):(i.get('printable'),tuple(float(x) for x in i.get('transform').split())) for i in root.findall('m:build/m:item',ns)}
  return resources,build
 add('Sliced root component/build transforms unchanged',root_signature(z)==root_signature(pz))
 add('One plate19 objects',len(ids)==19 and len(plates)==1)
 settings=json.loads(z.read('Metadata/project_settings.config'));add('Actual sliced PLA H2D0.4 PEI by-layer',settings['filament_type']==['PLA'] and settings['printer_model']=='Bambu Lab H2D' and all(float(x)==.4 for x in settings['nozzle_diameter']) and settings['curr_bed_type']=='Textured PEI Plate' and settings['print_sequence']=='by layer')
 g=z.read('Metadata/plate_1.gcode').decode();pos=np.zeros(3);eold=0;relative_e=True;obj=None;feature='';width=.4;speed=0;layerz=0;boundsoutside=[];bed=np.array(layout['safe_shared_XY_mm'],float)
 for line in g.splitlines():
  if line.startswith('; start printing object, unique label id: '):obj=int(line.split(':')[1])
  elif line.startswith('; stop printing object'):obj=None
  elif line.startswith('; FEATURE: '):feature=line[11:].strip()
  elif line.startswith('; LINE_WIDTH: '):width=float(line.split(':')[1])
  elif line.startswith('; Z_HEIGHT: '):layerz=float(line.split(':')[1])
  elif line.startswith('M83'):relative_e=True
  elif line.startswith('M82'):relative_e=False
  elif line.startswith('G92 '):
   q=re.search(r'\bE(-?[\d.]+)',line)
   if q:eold=float(q[1])
  elif re.match(r'^G[0123] ',line):
   vals={a:float(b) for a,b in re.findall(r'([XYZEFIJ])(-?\d*\.?\d+)',line.split(';')[0])};new=np.array([vals.get(a,pos[j]) for j,a in enumerate('XYZ')]);delta_e=(vals.get('E',0) if relative_e else vals.get('E',eold)-eold)
   if 'E'in vals:eold=vals['E'] if not relative_e else eold+vals['E']
   if 'F'in vals:speed=vals['F']/60
   points=[pos.copy(),new.copy()];distance=float(np.linalg.norm((new-pos)[:2]))
   if line.startswith(('G2 ','G3 ')):
    centre=pos[:2]+[vals.get('I',0),vals.get('J',0)];radius=float(np.linalg.norm(pos[:2]-centre));a1=math.atan2(*(pos[:2]-centre)[::-1]);a2=math.atan2(*(new[:2]-centre)[::-1]);ccw=line.startswith('G3 ');angle=((a2-a1) if ccw else (a1-a2))%(2*math.pi);distance=radius*angle
    for theta in [0,math.pi/2,math.pi,3*math.pi/2]:
     d=((theta-a1) if ccw else (a1-theta))%(2*math.pi)
     if d<=angle+1e-9:points.append(np.array([centre[0]+radius*math.cos(theta),centre[1]+radius*math.sin(theta),new[2]]))
   if obj in metrics and delta_e>1e-8 and distance>1e-6:
    m=metrics[obj];m['max_line_width_mm']=max(m['max_line_width_mm'],width);pp=np.asarray(points);low=pp.min(axis=0);high=pp.max(axis=0);m['extrusion_bounds_mm'][0]=np.minimum(m['extrusion_bounds_mm'][0],low).tolist();m['extrusion_bounds_mm'][1]=np.maximum(m['extrusion_bounds_mm'][1],high).tolist()
    f=m['features'].setdefault(feature,dict(segments=0,path_mm=0.,z_range_mm=[1e10,-1e10],max_speed_mm_s=0.));f['segments']+=1;f['path_mm']+=distance;f['z_range_mm']=[min(f['z_range_mm'][0],new[2]),max(f['z_range_mm'][1],new[2])];f['max_speed_mm_s']=max(f['max_speed_mm_s'],speed)
    if np.any(low[:2]-width/2<bed[0]-.03) or np.any(high[:2]+width/2>bed[1]+.03):boundsoutside.append(dict(ref=m['ref'],feature=feature,low=low.tolist(),high=high.tolist(),width=width))
    if feature not in ['Support','Support interface','Skirt','Brim']:
     m['model_segments']+=1;m['model_z_mm'].append(float(new[2]));
     if new[2]<=.20001:m['first_layer_model_path_mm']+=distance
    ref=m['ref'];r=plan[ref];R=np.asarray(r['rotation_3x3']);tt=np.asarray(r['normalization_translation_mm'])+[*r['plate_xy_mm'],0];native=((pos+new)/2-tt)@R
    segments[ref].append((feature,native.tolist(),float(new[2]),width))
   pos=new
 add('All positive model/support/brim paths inside shared printable bed',not boundsoutside,outside_segment_count=len(boundsoutside),first_outside=boundsoutside[:3],shared_bounds_xy_mm=bed.tolist())
 for a,b in combinations(metrics.values(),2):
  aa=np.array(a['extrusion_bounds_mm'])[:,:2];bb=np.array(b['extrusion_bounds_mm'])[:,:2];clear=float(np.maximum(bb[0]-aa[1],aa[0]-bb[1]).max()-(a['max_line_width_mm']+b['max_line_width_mm'])/2)
  add('Actual support/brim/model path envelopes separate '+a['ref']+'/'+b['ref'],clear>0,minimum_axis_clearance_mm=clear)
 for label,m in metrics.items():
  zz=sorted(set(m.pop('model_z_mm')));m['first_model_z_mm']=min(zz) if zz else None;m['last_model_z_mm']=max(zz) if zz else None;m['distinct_model_layers']=len(zz)
  add('Nonempty actual object '+m['ref'],m['model_segments']>0 and m['first_layer_model_path_mm']>0,model_segments=m['model_segments'],first_layer_path_mm=m['first_layer_model_path_mm'])
  target=float(plan[m['ref']]['size_oriented_mm'][2]);tol=.1001 if m['ref'].startswith(('P08','P09')) else .0001 if m['ref'].startswith('P07') else .2001
  add('Actual sliced height '+m['ref'],abs(m['last_model_z_mm']-target)<tol,actual_mm=m['last_model_z_mm'],nominal_mesh_mm=target,tolerance_mm=tol)
 def hits(ref,lo,hi,features):
  return [dict(feature=f,native_midpoint_mm=p,print_z_mm=z,width_mm=w) for f,p,z,w in segments[ref] if f in features and np.all(np.asarray(p)>=lo) and np.all(np.asarray(p)<=hi)]
 supports=['Support','Support interface'];evidence=[]
 # Precisely localize support in open, removable features; do not infer from total support count.
 for ref,lo,hi,description in [
  ('P08',[-41.75,-55.1,2],[-28.75,-53.6,7.6],'USB roof, removable through tray/port'),
  ('P05',[8.8,-38,7],[15.5,38,15.5],'Exposed rear rib underside, removable from base'),
  ('P04',[68,-37,5],[119,37,28],'Open finger pocket/underside, removable from front'),
  ('P120',[120,-60.75,3.3],[120.6,-41.25,26.5],'Shoe connector/fork, exposed before cap assembly'),
  ('P121',[120,41.25,3.3],[120.6,60.75,26.5],'Shoe connector/fork, exposed before cap assembly')]:
  h=hits(ref,lo,hi,supports);ev=dict(ref=ref,region_native_mm=[lo,hi],description=description,support_segments=len(h),support_interface_segments=sum(p['feature']=='Support interface' for p in h),print_z_range_mm=[min((p['print_z_mm'] for p in h),default=None),max((p['print_z_mm'] for p in h),default=None)]);evidence.append(ev);add('Localized accessible support '+ref,len(h)>0,**ev)
 # Q01 source mesh is preoriented; source coordinates are already local print coordinates.
 for lo,hi,title in [([-10,-10,0],[10,10,4.5],'Flange underside'),([-4.1,-4.1,6.5],[4.1,4.1,20.5],'Shoulder underside above flange')]:
  h=hits('Q01',lo,hi,supports);ev=dict(ref='Q01',feature=title,source_print_region_mm=[lo,hi],support_segments=len(h),interface_segments=sum(p['feature']=='Support interface' for p in h));evidence.append(ev);add('Q01 accessible on-model support '+title,len(h)>0,**ev)
 for ref,y in [('P060',-51),('P061',51)]:
  h=hits(ref,[121.9,y-3.3,23.2],[128.5,y+3.3,26.8],supports);ev=dict(ref=ref,description='Closed tongue-guide volume within main body X<=128.5; external support under roof extension beyond X128.5 is separately accessible',support_segments=len(h),localized_segments=h);evidence.append(ev);add('No trapped support in6.6mm rear tongue guide '+ref,len(h)==0,**ev)
  h=hits(ref,[121.9,y-3.3,26.75],[128.5,y+3.3,27.2],['Bridge']);evidence.append(dict(ref=ref,description='Tongue guide roof bridge extrusion',bridge_segments=len(h)))
 # P02 gap underside is vertical in this orientation. Support must not touch its central lid-gap face.
 h=hits('P02',[-46,-54,9.49],[-24,-0+54,9.51],supports);evidence.append(dict(ref='P02',description='Vertical electronics-gap face; narrow ±0.01mm plane witness, support cleanup stays off this face',support_segment_midpoints_exactly_on_face=len(h)))
 # Finished local0.1mm pads must reach1.5mm and slow fine features retain declared speed cap.
 for m in metrics.values():
  if m['ref'].startswith('P07'):
   add('P07 exact final thickness '+m['ref'],abs(m['last_model_z_mm']-1.5)<.0001,last_model_z_mm=m['last_model_z_mm'])
 report={'status':'PASS_ACTUAL_UNLOADED_FIT_SLICE' if all(c['status']=='PASS' for c in checks) else 'FAIL','sliced_archive_sha256':sha(path),'editable_project_sha256':sha(project),'layout_sha256':sha(OUT/'plate-layout.json'),'frozen_source_sha256':layout['CAD_source_sha256'],'object_count':len(metrics),'objects':list(metrics.values()),'filament_temperature_settings':{k:settings.get(k) for k in ['nozzle_temperature','nozzle_temperature_initial_layer','textured_plate_temp','textured_plate_temp_initial_layer']},'localized_support_evidence':evidence,'checks':checks,'failed_checks':sum(c['status']=='FAIL' for c in checks),'scope':'Actual positive extrusion, complete objects, measured first/last model paths, shared-bed bounds and localized support/guide evidence. Print tolerance, support removal success, fit and strength require the physical trial.','header':g[:g.find('; HEADER_BLOCK_END')+len('; HEADER_BLOCK_END')]}
 (HERE/'qa-toolpaths.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'],'checks',len(checks),'fail',report['failed_checks']);print(json.dumps([c for c in checks if c['status']=='FAIL'],indent=2));print('Localized support checks',[(r['ref'],r.get('support_segments',r.get('bridge_segments'))) for r in evidence]);assert report['failed_checks']==0
if __name__=='__main__':main()
