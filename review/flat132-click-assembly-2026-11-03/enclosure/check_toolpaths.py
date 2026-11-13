#!/usr/bin/env python3
"""Inspect actual local draft extrusion paths and every external clip."""
from pathlib import Path
import re,json,zipfile,math
import numpy as np
HERE=Path(__file__).resolve().parent
data=zipfile.ZipFile(HERE/'enclosure_preflight_verification.gcode.3mf').read('Metadata/plate_1.gcode').decode()
obj=None;feature='';x=y=z=0.;ss=[]
for line in data.splitlines():
 if 'start printing object, unique label id:' in line:obj=int(line.split(':')[-1])
 elif 'stop printing object' in line:obj=None
 elif line.startswith('; FEATURE: '):feature=line[11:]
 elif line.startswith('G92 '):
  v={k:float(v) for k,v in re.findall(r'([XYZ])([-+.\d]+)',line)};x=v.get('X',x);y=v.get('Y',y);z=v.get('Z',z)
 elif re.match(r'^G[0123] ',line):
  v={k:float(v) for k,v in re.findall(r'([XYZEF])([-+.\d]+)',line)};nx=v.get('X',x);ny=v.get('Y',y);nz=v.get('Z',z)
  if v.get('E',0)>0 and ('X' in v or 'Y' in v):ss.append(dict(obj=obj,feature=feature,a=[x,y,z],b=[nx,ny,nz],length=math.hypot(nx-x,ny-y)))
  x,y,z=nx,ny,nz
metrics={}
for ident,ref in [(1,'P08'),(2,'P09')]:
 s=[s for s in ss if s['obj']==ident and s['feature'] not in ['Support','Support interface','Brim']]
 bs=[x for x in s if 'Bridge' in x['feature']]
 metrics[ref]=dict(model_extrusion_segments=len(s),first_layer_extrusion_mm=sum(x['length'] for x in s if x['b'][2]<.201),max_model_z_mm=max(x['b'][2] for x in s),bridge_segments=len(bs),longest_bridge_segment_mm=max([x['length'] for x in bs] or [0]))
checks=[]
def add(name,ok,**e):checks.append(dict(name=name,status='PASS' if ok else 'FAIL',**e))
for r in metrics:add(r+' begins on bed',metrics[r]['first_layer_extrusion_mm']>100,**metrics[r])
for sign,y0,y1 in [(-1,80,81.2),(1,209.8,211)]:
 s=[s for s in ss if s['obj']==1 and s['feature'] not in ['Support','Support interface','Brim'] and 97.9<=s['b'][0]<=101.7 and y0-.2<=s['b'][1]<=y1+.2]
 add('Palm clip printed to full16.2mm side'+str(sign),max(x['b'][2] for x in s)>=16.2-.001,model_extrusion_segments=len(s),max_z_mm=max(x['b'][2] for x in s))
for name,y0,y1 in [('negative',170,173),('positive',102,105)]:
 s=[s for s in ss if s['obj']==2 and s['feature'] not in ['Support','Support interface','Brim'] and 129.8<=s['b'][0]<=132.5 and y0-.2<=s['b'][1]<=y1+.2]
 add('Lid arm and hook printed '+name,len(s)>30 and min(x['b'][2] for x in s)<.201 and max(x['b'][2] for x in s)>4.5,model_extrusion_segments=len(s),min_z_mm=min(x['b'][2] for x in s),max_z_mm=max(x['b'][2] for x in s))
support=[s for s in ss if 'Support' in s['feature']]
usb=[s for s in support if 85.2<s['b'][0]<98.6 and 90.2<s['b'][1]<92 and 6.5<s['b'][2]<7.6]
add('USB roof still supported',len(usb)>5,support_and_interface_segments=len(usb))
result=dict(status='PASS' if all(x['status']=='PASS' for x in checks) else 'FAIL',object_metrics=metrics,checks=checks,scope='Actual PLA H2D0.4 local CSG candidate paths; final native project must be independently sliced.',stock_macro_parser_diagnostics=['T1001','T65535','T65279'],diagnostic_note='Stock H2D machine macros unchanged; local slicer import and slice both returned0. No printer transmission.')
(HERE/'toolpath-preflight.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
