"""Inspect actual positive extrusion on all three R13 plates, including supports."""
from pathlib import Path
from hashlib import sha256
from itertools import combinations
import collections,json,math,re,zipfile,xml.etree.ElementTree as E
import numpy as np
OUT=Path(__file__).resolve().parents[1]
def md(n):return {m.get('key'):m.get('value') for m in n.findall('metadata') if m.get('key')}
def sha(p):return sha256(p.read_bytes()).hexdigest()
layout=json.loads((OUT/'plate-layout.json').read_text());plan={p['ref']:p for p in layout['placements']}
path=OUT/'validation'/(Path(layout['native_project']).stem+'_verification.gcode.3mf')
checks=[];evidence=[];metrics={};segments={ref:[] for ref in plan}
def add(name,ok,**detail):checks.append(dict(name=name,status='PASS' if ok else 'FAIL',**detail))
with zipfile.ZipFile(path) as z:
    cfg=E.fromstring(z.read('Metadata/model_settings.config'));names={o.get('id'):md(o)['name'].split(' - ')[0] for o in cfg.findall('object')}
    plates=cfg.findall('plate');assert len(plates)==3
    for plate,p in enumerate(plates,1):
        ids={int(md(m)['identify_id']):names[md(m)['object_id']] for m in p.findall('model_instance')}
        assert set(ids.values())=={r for r,v in plan.items() if v['plate']==plate}
        for ref in ids.values():metrics[ref]=dict(ref=ref,plate=plate,model_segments=0,first_layer_model_path_mm=0.,model_z_mm=[],max_line_width_mm=0.,features={},extrusion_bounds_mm=[[1e10]*3,[-1e10]*3])
        g=z.read(f'Metadata/plate_{plate}.gcode').decode();pos=np.zeros(3);eold=0.;relative_e=True;obj=None;feature='';width=.4;speed=0.;acceleration=None;outside=[]
        for line in g.splitlines():
            if line.startswith('; start printing object, unique label id: '):obj=int(line.split(':')[1])
            elif len(ids)==1 and line.startswith('; OBJECT_ID: '):obj=next(iter(ids))
            elif line.startswith('; stop printing object'):obj=None
            elif line.startswith('; FEATURE: '):
                feature=line[11:].strip()
                if feature=='Custom':obj=None
            elif line.startswith('; LINE_WIDTH: '):width=float(line.split(':')[1])
            elif line.startswith('M83'):relative_e=True
            elif line.startswith('M82'):relative_e=False
            elif line.startswith('M204 '):
                m=re.search(r'\bS([\d.]+)',line)
                if m:acceleration=float(m[1])
            elif line.startswith('G92 '):
                m=re.search(r'\bE(-?[\d.]+)',line)
                if m:eold=float(m[1])
            elif re.match(r'^G[0123] ',line):
                vals={a:float(b) for a,b in re.findall(r'([XYZEFIJ])(-?\d*\.?\d+)',line.split(';')[0])}
                new=np.array([vals.get(a,pos[j]) for j,a in enumerate('XYZ')]);de=vals.get('E',0) if relative_e else vals.get('E',eold)-eold
                if 'E' in vals:eold=eold+vals['E'] if relative_e else vals['E']
                if 'F' in vals:speed=vals['F']/60
                points=[pos.copy(),new.copy()];distance=float(np.linalg.norm((new-pos)[:2]))
                if line.startswith(('G2 ','G3 ')):
                    centre=pos[:2]+[vals.get('I',0),vals.get('J',0)];radius=float(np.linalg.norm(pos[:2]-centre))
                    a1=math.atan2(*(pos[:2]-centre)[::-1]);a2=math.atan2(*(new[:2]-centre)[::-1]);ccw=line.startswith('G3 ')
                    angle=((a2-a1) if ccw else (a1-a2))%(2*math.pi)
                    if angle<1e-10 and np.linalg.norm(new[:2]-pos[:2])<1e-7 and radius>1e-5:angle=2*math.pi
                    distance=radius*angle
                    for theta in (0,math.pi/2,math.pi,3*math.pi/2):
                        d=((theta-a1) if ccw else (a1-theta))%(2*math.pi)
                        if d<=angle+1e-9:points.append(np.array([centre[0]+radius*math.cos(theta),centre[1]+radius*math.sin(theta),new[2]]))
                if obj in ids and de>1e-8 and distance>1e-6:
                    ref=ids[obj];m=metrics[ref];m['max_line_width_mm']=max(m['max_line_width_mm'],width)
                    pp=np.asarray(points);lo=pp.min(0);hi=pp.max(0)
                    m['extrusion_bounds_mm'][0]=np.minimum(m['extrusion_bounds_mm'][0],lo).tolist();m['extrusion_bounds_mm'][1]=np.maximum(m['extrusion_bounds_mm'][1],hi).tolist()
                    f=m['features'].setdefault(feature,dict(segments=0,path_mm=0.,z_range_mm=[1e10,-1e10],max_speed_mm_s=0.,max_acceleration_mm_s2=0.))
                    f['segments']+=1;f['path_mm']+=distance;f['z_range_mm']=[min(f['z_range_mm'][0],new[2]),max(f['z_range_mm'][1],new[2])]
                    f['max_speed_mm_s']=max(f['max_speed_mm_s'],speed);f['max_acceleration_mm_s2']=max(f['max_acceleration_mm_s2'],acceleration or 0)
                    if np.any(lo[:2]-width/2<[26.97,2.97]) or np.any(hi[:2]+width/2>[323.03,317.03]):outside.append(dict(ref=ref,feature=feature,low=lo.tolist(),high=hi.tolist(),width=width))
                    if feature not in ('Support','Support interface','Support transition','Skirt','Brim','Custom'):
                        m['model_segments']+=1;m['model_z_mm'].append(float(new[2]))
                        if new[2]<=.20001:m['first_layer_model_path_mm']+=distance
                    r=plan[ref];R=np.asarray(r['rotation_3x3']);tt=np.asarray(r['normalization_translation_mm'])+[*r['plate_xy_mm'],0]
                    native=((pos+new)/2-tt)@R
                    segments[ref].append((feature,native.tolist(),float(new[2]),width))
                pos=new
        add(f'Plate {plate}: positive extrusion within shared printable bed',not outside,outside_segments=len(outside),examples=outside[:3])
        for a,b in combinations([metrics[r] for r in ids.values()],2):
            aa=np.array(a['extrusion_bounds_mm'])[:,:2];bb=np.array(b['extrusion_bounds_mm'])[:,:2]
            clear=float(np.maximum(bb[0]-aa[1],aa[0]-bb[1]).max()-(a['max_line_width_mm']+b['max_line_width_mm'])/2)
            add('Separate actual path envelopes '+a['ref']+'/'+b['ref'],clear>0,minimum_axis_clearance_mm=clear)
for ref,m in metrics.items():
    zz=sorted(set(m.pop('model_z_mm')));m.update(first_model_z_mm=min(zz) if zz else None,last_model_z_mm=max(zz) if zz else None,distinct_model_layers=len(zz))
    add('Model present on first layer '+ref,m['model_segments']>0 and m['first_layer_model_path_mm']>0,model_segments=m['model_segments'],first_layer_path_mm=m['first_layer_model_path_mm'])
    target=float(plan[ref]['size_oriented_mm'][2]);tol=.1001 if ref in ('P08','P09') else .0001 if ref.startswith('P07') else .2001
    add('Complete model height '+ref,abs(m['last_model_z_mm']-target)<tol,actual_mm=m['last_model_z_mm'],mesh_mm=target,tolerance_mm=tol)
    body=[f for name,f in m['features'].items() if name not in ('Support','Support interface','Support transition','Skirt','Brim','Custom')]
    add('Conservative actual acceleration '+ref,max(f['max_acceleration_mm_s2'] for f in body)<=1500.1)
    if ref.startswith('P07'):add('Exact 1.50 mm hard-pad proxy '+ref,abs(m['last_model_z_mm']-1.5)<.0001)
def hits(ref,lo,hi,features):
    return [dict(feature=f,native_midpoint_mm=p,print_z_mm=z,width_mm=w) for f,p,z,w in segments[ref] if f in features and np.all(np.asarray(p)>=lo) and np.all(np.asarray(p)<=hi)]
supports=['Support','Support interface','Support transition']
add('Rear gate has no support extrusion',not any(name in metrics['P06']['features'] for name in supports))
result=dict(status='PASS_ACTUAL_R13_TOOLPATHS' if all(c['status']=='PASS' for c in checks) else 'FAIL',
    failed_checks=sum(c['status']=='FAIL' for c in checks),checks=checks,metrics=metrics,
    CAD_source_sha256=layout['CAD_source_sha256'],editable_project_sha256=sha(OUT/layout['native_project']),
    sliced_internal_evidence_sha256=sha(path),native_R13_version=layout['native_R13_version'],
    scope='All actual object extrusion bounds, separation, first-layer presence, final height and acceleration; no physical strength claim.')
(OUT/'validation/toolpath-check.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(dict(status=result['status'],checks=len(checks),failed_checks=result['failed_checks'],failures=[c for c in checks if c['status']=='FAIL']),indent=2))
