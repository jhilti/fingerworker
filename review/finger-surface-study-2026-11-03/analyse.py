from pathlib import Path
import json,math,re,numpy as np
OUT=Path(__file__).resolve().parent
geom=json.loads((OUT/'P04_orientation_study-geometry.json').read_text())
# All exported gcode uses bed-local coordinates, independent of display plate grid.
def parse(text):
 pos=np.zeros(3);feature='';obj=None;F=0
 for line in text.splitlines():
  if line.startswith('; FEATURE: '):feature=line[11:].strip()
  if line.startswith('; start printing object, unique label id:'):obj=int(line.rsplit(':',1)[1])
  if line.startswith('; stop printing object'):obj=None
  if line.startswith('; OBJECT_ID: '):obj=int(line.rsplit(':',1)[1])
  if not re.match(r'^G[0123] ',line):continue
  vals={a:float(b) for a,b in re.findall(r'([XYZEIJF])(-?\d*\.?\d+)',line.split(';')[0])};end=np.array([vals.get(k,pos[i]) for i,k in enumerate('XYZ')]);start=pos.copy();pos=end
  if 'F' in vals:F=vals['F']/60
  if vals.get('E',0)>0 and np.linalg.norm(end-start)>1e-5:
   yield start,end,feature,obj,F

def metric(i,row,path=None):
 path=path or OUT/f'plate_{i}.gcode';text=path.read_text();R=np.array(row['rotation_3x3']);T=np.array(row['normalization_translation_mm']);samples=[];features={};contact={n:{} for n in ['loaded_wall','floor','guide','left_rod_bore','right_rod_bore']}
 for a,b,f,obj,speed in parse(text):
  if obj is None and not f.startswith('Support'):continue
  mid=((a+b)/2-np.array([100,80,0])-T)@R
  x,y,z=mid;L=float(np.linalg.norm(b-a));d=features.setdefault(f,{'segments':0,'path_mm':0,'max_chord_mm':0});d['segments']+=1;d['path_mm']+=L;d['max_chord_mm']=max(d['max_chord_mm'],L)
  if f not in ['Bridge','Top surface','Outer wall','Overhang wall','Support','Support interface','Support transition','Bottom surface']:continue
  masks={'loaded_wall':abs(x-72)<.8 and abs(y)<28 and 14<z<26,'floor':abs(z-10)<.7 and 77<x<101 and abs(y)<25,'guide':64<x<119 and abs(y)<18 and 3.5<z<7.6,'left_rod_bore':111.2<x<118.8 and ((y+51)**2+(z-18)**2)<3.8**2,'right_rod_bore':111.2<x<118.8 and ((y-51)**2+(z-18)**2)<3.8**2}
  for k,yes in masks.items():
   if yes:
    d=contact[k].setdefault(f,{'segments':0,'path_mm':0,'max_chord_mm':0});d['segments']+=1;d['path_mm']+=L;d['max_chord_mm']=max(d['max_chord_mm'],L)
 header={}
 for line in text.splitlines()[:20]:
  if 'total estimated time' in line:header['time']=line.split('total estimated time:')[1].strip()
  if 'total filament weight' in line:header['weight_g']=float(line.split(':')[1])
 return {'variant':row['variant'],'header':header,'features':features,'regions':contact}
if __name__=='__main__':
 results=[metric(i+1,row) for i,row in enumerate(geom['variants'])]
 (OUT/'gcode-comparison.json').write_text(json.dumps(results,indent=2))
 for r in results:
  print(r['variant'],r['header']);print('loaded_wall',r['regions']['loaded_wall']);print('floor',r['regions']['floor']);print('guide',r['regions']['guide']);print('rod_left',r['regions']['left_rod_bore'])
