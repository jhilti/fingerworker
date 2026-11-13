#!/usr/bin/env python3
"""Check changed material flow cap and retained protected speeds in GUI gcode."""
from pathlib import Path
import json,math,re,zipfile,xml.etree.ElementTree as ET
from hashlib import sha256
P=Path(__file__).resolve().parents[1];V=P/'validation'
S=V/'Fingerworker_R16_H2D_04mm_PLA_Basic_Print_Ready_verification.gcode.3mf'
with zipfile.ZipFile(S) as z:
 g=z.read('Metadata/plate_1.gcode').decode();cfg=json.loads(z.read('Metadata/project_settings.config'));info=ET.fromstring(z.read('Metadata/slice_info.config'))
with zipfile.ZipFile(P/'Fingerworker_R16_H2D_04mm_PLA_Basic_Print_Ready.3mf') as z:
 mc=ET.fromstring(z.read('Metadata/model_settings.config'))
names={int(o.get('identify_id')):o.get('name').split(' - ')[0] for o in info.find('plate').findall('object')}
settings={}
for ob in mc.findall('object'):
 md={m.get('key'):m.get('value') for m in ob.findall('metadata')};settings[md['name'].split(' - ')[0]]=md
metrics={ref:dict(model_segments=0,max_adjusted_flow_mm3_s=0.,max_long_segment_flow_mm3_s=0.,speeds={}) for ref in names.values()}
obj=None;feature='';pos=[0.,0.,0.];eold=0.;relative=True;speed=0.;pattern=re.compile(r'([XYZEFIJ])(-?\d*\.?\d+)')
for line in g.splitlines():
 if line.startswith('; start printing object, unique label id:'):obj=int(line.rsplit(':',1)[1]);continue
 if line.startswith('; stop printing object'):obj=None;continue
 if line.startswith('; FEATURE: '):
  feature=line[11:].strip()
  if feature=='Custom':obj=None
  continue
 if line.startswith('M83'):relative=True;continue
 if line.startswith('M82'):relative=False;continue
 if line.startswith('G92 '):
  v=dict((a,float(b)) for a,b in pattern.findall(line));eold=v.get('E',eold)
  for i,k in enumerate('XYZ'):pos[i]=v.get(k,pos[i])
  continue
 if not line.startswith(('G0 ','G1 ','G2 ','G3 ')):continue
 v={a:float(b) for a,b in pattern.findall(line.split(';')[0])};new=[v.get(k,pos[i]) for i,k in enumerate('XYZ')];de=v.get('E',0.) if relative else v.get('E',eold)-eold
 if 'E' in v:eold=eold+v['E'] if relative else v['E']
 if 'F' in v:speed=v['F']/60
 distance=math.hypot(new[0]-pos[0],new[1]-pos[1])
 if line.startswith(('G2 ','G3 ')):
  cx,cy=pos[0]+v.get('I',0),pos[1]+v.get('J',0);radius=math.hypot(pos[0]-cx,pos[1]-cy);a1=math.atan2(pos[1]-cy,pos[0]-cx);a2=math.atan2(new[1]-cy,new[0]-cx);angle=((a2-a1) if line.startswith('G3 ') else (a1-a2))%(2*math.pi)
  if angle<1e-10 and distance<1e-7 and radius>1e-5:angle=2*math.pi
  distance=radius*angle
 if obj in names and de>1e-8 and distance>1e-6 and feature not in ('Custom','Support','Support interface','Support transition','Brim','Skirt'):
  m=metrics[names[obj]];m['model_segments']+=1;m['max_adjusted_flow_mm3_s']=max(m['max_adjusted_flow_mm3_s'],max(de-.000005,0)*math.pi*(1.75/2)**2*speed/(distance+math.sqrt(2)*.001))
  if distance>=1:m['max_long_segment_flow_mm3_s']=max(m['max_long_segment_flow_mm3_s'],de*math.pi*(1.75/2)**2*speed/distance)
  m['speeds'][feature]=max(m['speeds'].get(feature,0),speed)
 pos=new
checks=[]
def add(name,ok,**kw):checks.append(dict(name=name,status='PASS' if ok else 'FAIL',**kw))
cap=float(cfg['filament_max_volumetric_speed'][0])
add('Selected PLA Basic standard-nozzle flow cap is 25',cap==25,cap_mm3_s=cap)
for ref,m in metrics.items():
 add(ref+' actual commands respect selected material flow cap',m['model_segments']>0 and m['max_adjusted_flow_mm3_s']<=cap+.01 and m['max_long_segment_flow_mm3_s']<=cap+.05,**{k:v for k,v in m.items() if k!='speeds'})
 if ref in ('P04','P06','P11','Q01'):
  for feature,key in (('Outer wall','outer_wall_speed'),('Top surface','top_surface_speed')):
   value=settings[ref].get(key,cfg.get(key));limit=float(str(value[0] if isinstance(value,list) else value).split(',')[0]);actual=m['speeds'].get(feature,0)
   add(ref+' protected '+feature+' speed retained',actual<=limit+.01,actual_mm_s=actual,limit_mm_s=limit)
failures=[c for c in checks if c['status']!='PASS'];report=dict(status='PASS_CONNECTED_MATERIAL_FLOW' if not failures else 'FAIL',checks=checks,failures=failures,metrics=metrics,selected_cap_mm3_s=cap,sliced_archive_sha256=sha256(S.read_bytes()).hexdigest(),validator_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),method='All positive model commands parsed; circular arcs use exact radius/sweep. Flow check allows only known XY0.001mm and E0.00001mm serialization rounding. Long segments also meet raw cap+0.05mm3/s. Unchanged native CAD/profile audits are not rerun.')
(V/'connected-flow-check.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status=report['status'],checks=len(checks),failures=failures),indent=2));raise SystemExit(bool(failures))
