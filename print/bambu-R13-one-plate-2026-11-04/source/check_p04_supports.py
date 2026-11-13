#!/usr/bin/env python3
"""Check actual P04 paths in native coordinates after any rigid print transform.

Example:
 python check_p04_supports.py --gcode plate_1.gcode \
 --rotation '[[0,0,-1],[0,1,0],[1,0,0]]' --translation '[30,63,-60]' \
 --xy '[100,80]' --output validation.json

Translation is the normalization applied AFTER rotation, before plate XY.
Every positive-extrusion support segment is sampled at <=0.35 mm spacing.
Regions are deliberately inside the main contact/guide/rod surfaces; the
rolled lip is additionally checked against its exact radius in the XZ plane.
This does not certify physical surface finish, strength, or support removal.
"""
from pathlib import Path
import argparse,json,re,math,hashlib,collections
import numpy as np
from zipfile import ZipFile

SUPPORTS={'Support','Support interface','Support transition'}

def read_gcode(path,plate=1):
 if str(path).endswith('.3mf'):
  with ZipFile(path) as z:return z.read(f'Metadata/plate_{plate}.gcode').decode()
 return Path(path).read_text()

def segments(text):
 pos=np.zeros(3);feature='';obj=None;speed=0.;width=.42;relative=True;eabs=0.
 for line in text.splitlines():
  if line.startswith('; FEATURE: '):feature=line[11:].strip()
  if line.startswith('; LINE_WIDTH: '):width=float(line.split(':',1)[1])
  if line.startswith('; OBJECT_ID: '):obj=int(line.rsplit(':',1)[1])
  if line.startswith('; start printing object, unique label id:'):obj=int(line.rsplit(':',1)[1])
  if line.startswith('; stop printing object'):obj=None
  code=line.split(';')[0]
  if code.startswith('M83'):relative=True
  if code.startswith('M82'):relative=False
  if code.startswith('G92'):
   vv=dict(re.findall(r'([XYZE])(-?\d*\.?\d+)',code))
   if 'E' in vv:eabs=float(vv['E'])
  if not re.match(r'^G[0123] ',code):continue
  v={k:float(x) for k,x in re.findall(r'([XYZEIJF])(-?\d*\.?\d+)',code)}
  end=np.array([v.get(k,pos[i]) for i,k in enumerate('XYZ')]);start=pos.copy();pos=end
  if 'F' in v:speed=v['F']/60
  e=v.get('E',0) if relative else v.get('E',eabs)-eabs
  if 'E' in v:eabs=eabs+v['E'] if relative else v['E']
  if e<=0:continue
  arc=code.startswith(('G2 ','G3 '));length=float(np.linalg.norm(end-start));points=None
  if arc:
   center=start[:2]+[v.get('I',0),v.get('J',0)];r=float(np.linalg.norm(start[:2]-center));a1=math.atan2(start[1]-center[1],start[0]-center[0]);a2=math.atan2(end[1]-center[1],end[0]-center[0]);direction=1 if code.startswith('G3 ') else -1
   theta=(direction*(a2-a1))%(2*math.pi)
   if theta<1e-10:theta=2*math.pi
   length=math.hypot(r*theta,end[2]-start[2]);count=max(2,math.ceil(length/.35)+1);ts=np.linspace(0,1,count);aa=a1+direction*theta*ts;points=np.column_stack((center[0]+r*np.cos(aa),center[1]+r*np.sin(aa),start[2]+(end[2]-start[2])*ts))
  elif length>1e-6:points=start+(end-start)*np.linspace(0,1,max(2,math.ceil(length/.35)+1))[:,None]
  if points is not None:yield dict(points=points,start=start,end=end,feature=feature,object=obj,length=length,speed=speed,width=width)

def check(path,rotation,translation,xy,plate=1):
 R=np.asarray(rotation);T=np.asarray(translation);O=np.array([*xy,0.]);assert np.allclose(R.T@R,np.eye(3)) and abs(np.linalg.det(R)-1)<1e-9
 text=read_gcode(path,plate);regions={k:{} for k in ['loaded_wall','pocket_floor','guide_cavity','left_rod_bore','right_rod_bore','rolled_front_lip','front_floor_fillet','front_corner_walls']};model_count=0;first_layer_path=0.;maxz=0;support_count=0
 for s in segments(text):
  f=s['feature'];pts=(s['points']-O-T)@R;x,y,z=pts.T
  if f in SUPPORTS:support_count+=1
  elif s['object'] is not None and f not in ['Brim','Skirt']:
   # Only P04's print envelope. In a shared plate, other part paths cannot be
   # counted as P04 paths even if labels are assigned differently by importer.
   mid=np.mean(pts,axis=0)
   if 59.99<=mid[0]<=119.01 and abs(mid[1])<=63.01 and 4.99<=mid[2]<=30.01:
    model_count+=1;maxz=max(maxz,float(s['points'][:,2].max()))
    if float(s['points'][:,2].max())<=.201:first_layer_path+=s['length']
  masks={'loaded_wall':(abs(x-72)<.8)&(abs(y)<28)&(z>14)&(z<26),
         'pocket_floor':(abs(z-10)<.7)&(x>77)&(x<101)&(abs(y)<25),
         'guide_cavity':(x>60.2)&(x<118.8)&(abs(y)<18)&(z>3.5)&(z<7.6),
         'left_rod_bore':(x>111.2)&(x<118.8)&(((y+51)**2+(z-18)**2)<3.8**2),
         'right_rod_bore':(x>111.2)&(x<118.8)&(((y-51)**2+(z-18)**2)<3.8**2),
         # Inner front lip is the R4 quarter-circle, center X68,Z26.
         # Exact core spans |Y|<28, excluding the real cam-head slot
         # (capsule X62.7..66.3, Y3.5, radius3) where the lip is absent.
         # Centers of 0.42 mm support roads closer
         # than 0.25 mm to this surface would risk physical contact.
         'front_floor_fillet':(x>71.8)&(x<76.2)&(z>9.8)&(z<14.2)&(abs(y)<28)&(abs(np.sqrt((x-76)**2+(z-14)**2)-4)<.25),
         'front_corner_walls':(x>71.8)&(x<80.2)&(abs(y)>28)&(abs(y)<36.2)&(z>14)&(z<26)&(abs(np.sqrt((x-80)**2+(abs(y)-28)**2)-8)<.25),
         'rolled_front_lip':(x>67.8)&(x<72.2)&(z>26)&(z<30.2)&(abs(y)<28)&(abs(np.sqrt((x-68)**2+(z-26)**2)-4)<.25)&((np.maximum(np.maximum(62.7-x,x-66.3),0)**2+(y-3.5)**2)>3.2**2)}
  for name,mask in masks.items():
   if mask.any():
    d=regions[name].setdefault(f,{'segments':0,'sample_points':0,'path_mm':0.,'max_speed_mm_s':0.});d['segments']+=1;d['sample_points']+=int(mask.sum());d['path_mm']+=s['length'];d['max_speed_mm_s']=max(d['max_speed_mm_s'],s['speed'])
 contact={k:sum(v['segments'] for f,v in fs.items() if f in SUPPORTS) for k,fs in regions.items()}
 problems=[k for k,n in contact.items() if n]
 if not model_count or first_layer_path<=0:problems.append('missing_P04_first_layer_or_model')
 header={}
 for line in text.splitlines()[:20]:
  if 'total estimated time:' in line:header['estimated_time']=line.split('total estimated time:')[1].strip()
  if 'total filament weight' in line:header['estimated_weight_g']=float(line.split(':')[1])
 return {'status':'PASS' if not problems else 'FAIL','scope':'P04 main finger-contact surfaces, exact rolled front lip core, central guide cavity, and inner 8 mm rod bores; support roads sampled at <=0.35 mm','gcode_sha256':hashlib.sha256(text.encode()).hexdigest(),'rotation_3x3':R.tolist(),'normalization_translation_mm':T.tolist(),'plate_xy_mm':xy,'model_segments':model_count,'first_layer_path_mm':first_layer_path,'max_model_print_z_mm':maxz,'support_segments':support_count,'support_segments_in_critical_regions':contact,'regions':regions,'issues':problems,**header}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--gcode',required=True,type=Path);p.add_argument('--rotation',required=True);p.add_argument('--translation',required=True);p.add_argument('--xy',required=True);p.add_argument('--output',required=True,type=Path);p.add_argument('--plate',type=int,default=1);a=p.parse_args()
 r=check(a.gcode,json.loads(a.rotation),json.loads(a.translation),json.loads(a.xy),a.plate);a.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:r[k] for k in ['status','support_segments_in_critical_regions','estimated_time','estimated_weight_g','issues']},indent=2));raise SystemExit(0 if r['status']=='PASS' else 1)
