"""Count actual extrusion segments by object, feature, and first layer, not travel comments."""
from pathlib import Path
import zipfile,xml.etree.ElementTree as E,json,re,math
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
FILES={'RevE':ROOT/'review/coupon-orientation-2026-10-13/H2D-RevE-verification.gcode.3mf','candidate':OUT/'Small_candidate-verification.gcode.3mf','finepads':OUT/'Small_finepads-verification.gcode.3mf'}
def check(path):
 z=zipfile.ZipFile(path);settings=E.fromstring(z.read('Metadata/model_settings.config'))
 def md(obj):return {m.get('key'):m.get('value') for m in obj.findall('metadata')}
 objects={o.get('id'):md(o)['name'].split(' - ')[0] for o in settings.findall('object')}
 report={}
 for i,plate in enumerate(settings.findall('plate'),1):
  names={int(md(m)['identify_id']):objects[md(m)['object_id']] for m in plate.findall('model_instance')}
  s=z.read(f'Metadata/plate_{i}.gcode').decode();xy=[0.,0.];layerz=0.;obj=None;feat='';metrics={label:dict(key=key,features={},first_layer_segments=0,first_layer_length_mm=0.,first_layer_min_width_mm=100.,bridge_max_segment_mm=0.,bridge_segments=0,bridge_length_mm=0.) for label,key in names.items()};width=0
  for line in s.splitlines():
   if line.startswith('; Z_HEIGHT: '):layerz=float(line.split(':')[1])
   elif line.startswith('; LINE_WIDTH: '):width=float(line.split(':')[1])
   elif line.startswith('; start printing object, unique label id: '):obj=int(line.split(':')[1])
   elif line.startswith('; stop printing object'):obj=None
   elif line.startswith('; FEATURE: '):feat=line[11:]
   elif line.startswith(('G0 ','G1 ','G2 ','G3 ')):
    code=line.split(';')[0];words={a:float(b) for a,b in re.findall(r'([XYZEIJ])(-?\d*\.?\d+)',code)};newxy=[words.get(k,xy[n]) for n,k in enumerate(['X','Y'])];d=math.hypot(newxy[0]-xy[0],newxy[1]-xy[1]);
    if line.startswith(('G2 ','G3 ')):
     cx=xy[0]+words.get('I',0);cy=xy[1]+words.get('J',0);radius=math.hypot(xy[0]-cx,xy[1]-cy);a1=math.atan2(xy[1]-cy,xy[0]-cx);a2=math.atan2(newxy[1]-cy,newxy[0]-cx);da=((a2-a1)%(2*math.pi)) if line.startswith('G3 ') else ((a1-a2)%(2*math.pi));d=radius*da
    xy=newxy
    if obj in metrics and words.get('E',0)>0 and d>0:
     m=metrics[obj];f=m['features'].setdefault(feat,dict(extrusion_segments=0,length_mm=0.,min_z_mm=layerz,max_z_mm=layerz,min_width_mm=width,max_width_mm=width));f['extrusion_segments']+=1;f['length_mm']+=d;f['min_z_mm']=min(f['min_z_mm'],layerz);f['max_z_mm']=max(f['max_z_mm'],layerz);f['min_width_mm']=min(f['min_width_mm'],width);f['max_width_mm']=max(f['max_width_mm'],width)
     if layerz==.2 and feat not in ['Support','Support interface','Skirt','Brim']:
      m['first_layer_segments']+=1;m['first_layer_length_mm']+=d;m['first_layer_min_width_mm']=min(m['first_layer_min_width_mm'],width)
     if feat=='Bridge':m['bridge_max_segment_mm']=max(m['bridge_max_segment_mm'],d);m['bridge_segments']+=1;m['bridge_length_mm']+=d
  for label,m in metrics.items():report[f'{i}:{label}:{names[label]}']=m
 return report
reports={key:check(path) for key,path in FILES.items() if path.exists()}
(OUT/'gcode-metrics.json').write_text(json.dumps(reports,indent=2)+'\n')
for key,data in reports.items():
 print('\n',key)
 for name,m in data.items():
  if not m['key'].startswith(('H','P07')):continue
  print(name,'bridge',m['bridge_segments'],round(m['bridge_max_segment_mm'],3),'first_layer_mm',round(m['first_layer_length_mm'],2),'width',round(m['first_layer_min_width_mm'],4),'support_length',round(sum(f['length_mm'] for fn,f in m['features'].items() if fn.startswith('Support')),2))
