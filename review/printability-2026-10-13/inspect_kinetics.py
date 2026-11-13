"""Actual Rev F extrusion heights, velocities, acceleration, and feature checks."""
from pathlib import Path
import zipfile,xml.etree.ElementTree as ET,json,re,math,collections
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
ZFILE=OUT/'H2D-RevF-verification.gcode.3mf'
def md(n):return {m.get('key'):m.get('value') for m in n.findall('metadata') if m.get('key')}
result=[]
with zipfile.ZipFile(ZFILE) as z:
    settings=ET.fromstring(z.read('Metadata/model_settings.config'))
    names={o.get('id'):md(o)['name'].split(' - ')[0] for o in settings.findall('object')}
    for i,plate in enumerate(settings.findall('plate'),1):
        ids={int(md(m)['identify_id']):names[md(m)['object_id']] for m in plate.findall('model_instance')}
        metrics={n:dict(plate=i,label=n,part=k,model_segments=0,max_z_mm=0.,first_layer_path_mm=0.,
                    max_model_speed_mm_s=0.,max_model_acceleration_mm_s2=0.,features={}) for n,k in ids.items()}
        pos={'X':0.,'Y':0.,'Z':0.};obj=None;feature='';speed=0.;accel=0.;layerz=0.;width=0.
        for line in z.read(f'Metadata/plate_{i}.gcode').decode().splitlines():
            if line.startswith('; Z_HEIGHT: '):layerz=float(line.split(':')[1])
            elif line.startswith('; LINE_WIDTH: '):width=float(line.split(':')[1])
            elif line.startswith('; start printing object, unique label id: '):obj=int(line.split(':')[1])
            elif line.startswith('; stop printing object'):obj=None
            elif line.startswith('; FEATURE: '):feature=line[11:].strip()
            elif line.startswith('M204 '):
                m=re.search(r'S([\d.]+)',line)
                if m:accel=float(m.group(1))
            elif re.match(r'^G[0123] ',line):
                vals={a:float(b) for a,b in re.findall(r'([XYZEIJF])(-?\d*\.?\d+)',line.split(';')[0])}
                new={k:vals.get(k,pos[k]) for k in pos};d=math.hypot(new['X']-pos['X'],new['Y']-pos['Y'])
                if line.startswith(('G2 ','G3 ')):
                    cx=pos['X']+vals.get('I',0);cy=pos['Y']+vals.get('J',0);radius=math.hypot(pos['X']-cx,pos['Y']-cy)
                    a1=math.atan2(pos['Y']-cy,pos['X']-cx);a2=math.atan2(new['Y']-cy,new['X']-cx)
                    delta=((a2-a1)%(2*math.pi)) if line.startswith('G3 ') else ((a1-a2)%(2*math.pi));d=radius*delta
                if 'F' in vals:speed=vals['F']/60
                if obj in metrics and vals.get('E',0)>0 and d>.00001:
                    m=metrics[obj];f=m['features'].setdefault(feature,dict(segments=0,path_mm=0.,max_segment_mm=0.,max_speed_mm_s=0.,min_width_mm=width,max_width_mm=width))
                    f['segments']+=1;f['path_mm']+=d;f['max_segment_mm']=max(f['max_segment_mm'],d);f['max_speed_mm_s']=max(f['max_speed_mm_s'],speed);f['min_width_mm']=min(f['min_width_mm'],width);f['max_width_mm']=max(f['max_width_mm'],width)
                    if feature not in ['Support','Support interface','Skirt','Brim']:
                        m['model_segments']+=1;m['max_z_mm']=max(m['max_z_mm'],layerz)
                        m['max_model_speed_mm_s']=max(m['max_model_speed_mm_s'],speed);m['max_model_acceleration_mm_s2']=max(m['max_model_acceleration_mm_s2'],accel)
                        if layerz<=.20001:m['first_layer_path_mm']+=d
                pos=new
        for m in metrics.values():
            assert m['model_segments']>0 and m['first_layer_path_mm']>0,(m['part'],m['plate'])
            result.append(m)
assert len(result)==32
for m in result:
    key=m['part']
    if key.startswith('P07'):assert abs(m['max_z_mm']-1.5)<.002,m
    if key in ['P03a','P03b','H14']:
        print('Tall kinetic check',key,m['max_model_speed_mm_s'],m['max_model_acceleration_mm_s2'])
    if key in ['P10','H19','H22'] or key.startswith('P07'):
        print('Small kinetic check',key,m['max_model_speed_mm_s'],m['max_model_acceleration_mm_s2'])
    if key=='CouponFemale':assert m['features'].get('Bridge',{}).get('segments',0)==0
    if key in ['P060','P061','P05','H12','H02']:print('Bridge kinetic check',key,m['features'].get('Bridge',{}).get('max_speed_mm_s',0))
report=dict(status='KINETICS_CHECK_PENDING',scope='Actual positive extrusion paths, complete object counts, physical layer heights and kinetic limits; support access separately inspected',objects=result)
(OUT/'kinetics-debug.json').write_text(json.dumps(report,indent=2)+'\n')
for m in result:print(m['part'],m['label'],'height',m['max_z_mm'],'speed',round(m['max_model_speed_mm_s'],2),'accel',m['max_model_acceleration_mm_s2'],'first_layer_path',round(m['first_layer_path_mm'],2))
