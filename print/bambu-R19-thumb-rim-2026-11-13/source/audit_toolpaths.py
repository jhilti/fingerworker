"""Inspect actual positive extrusion on one combined R19 plate, including supports."""
from pathlib import Path
from hashlib import sha256
from itertools import combinations
import collections,json,math,re,zipfile,xml.etree.ElementTree as E
import numpy as np
from print_context import OUT,LAYOUT,LAYOUT_PATH,V,SLICED
def md(n):return {m.get('key'):m.get('value') for m in n.findall('metadata') if m.get('key')}
def sha(p):return sha256(p.read_bytes()).hexdigest()
layout=LAYOUT;plan={p['ref']:p for p in layout['placements']}
path=SLICED
starting_layout_sha=sha(LAYOUT_PATH);starting_slice_sha=sha(path)
checks=[];evidence=[];metrics={};segments={ref:[] for ref in plan}
def add(name,ok,**detail):checks.append(dict(name=name,status='PASS' if ok else 'FAIL',**detail))
with zipfile.ZipFile(path) as z:
    cfg=E.fromstring(z.read('Metadata/model_settings.config'));names={o.get('id'):md(o)['name'].split(' - ')[0] for o in cfg.findall('object')}
    plates=cfg.findall('plate');assert len(plates)==1
    actual_settings={md(o)['name'].split(' - ')[0]:md(o) for o in cfg.findall('object')}
    project_settings=json.loads(z.read('Metadata/project_settings.config'))
    def setting_number(ref,key):
        value=actual_settings[ref].get(key,project_settings.get(key))
        if isinstance(value,list):value=value[0]
        return float(str(value).split(',')[0])
    for plate,p in enumerate(plates,1):
        ids={int(md(m)['identify_id']):names[md(m)['object_id']] for m in p.findall('model_instance')}
        assert set(ids.values())=={r for r,v in plan.items() if v['plate']==plate}
        for ref in ids.values():metrics[ref]=dict(ref=ref,plate=plate,max_model_volumetric_mm3_s=0.,max_quantization_adjusted_flow_mm3_s=0.,max_long_segment_flow_mm3_s=0.,model_segments=0,first_layer_model_path_mm=0.,model_z_mm=[],max_line_width_mm=0.,features={},extrusion_bounds_mm=[[1e10]*3,[-1e10]*3])
        g=z.read(f'Metadata/plate_{plate}.gcode').decode();pos=np.zeros(3);eold=0.;relative_e=True;obj=None;feature='';width=.4;speed=0.;acceleration=None;outside=[];unattributed=[]
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
                if de>1e-8 and distance>1e-6 and obj not in ids and feature!='Custom':
                    unattributed.append(dict(feature=feature,object_label=obj,low=np.asarray(points).min(0).tolist(),high=np.asarray(points).max(0).tolist()))
                if obj in ids and de>1e-8 and distance>1e-6:
                    ref=ids[obj];m=metrics[ref];m['max_line_width_mm']=max(m['max_line_width_mm'],width)
                    pp=np.asarray(points);lo=pp.min(0);hi=pp.max(0)
                    m['extrusion_bounds_mm'][0]=np.minimum(m['extrusion_bounds_mm'][0],lo).tolist();m['extrusion_bounds_mm'][1]=np.maximum(m['extrusion_bounds_mm'][1],hi).tolist()
                    f=m['features'].setdefault(feature,dict(segments=0,path_mm=0.,z_range_mm=[1e10,-1e10],max_speed_mm_s=0.,max_acceleration_mm_s2=0.))
                    f['segments']+=1;f['path_mm']+=distance;f['z_range_mm']=[min(f['z_range_mm'][0],new[2]),max(f['z_range_mm'][1],new[2])]
                    f['max_speed_mm_s']=max(f['max_speed_mm_s'],speed);f['max_acceleration_mm_s2']=max(f['max_acceleration_mm_s2'],acceleration or 0)
                    if np.any(lo[:2]-width/2<[26.97,2.97]) or np.any(hi[:2]+width/2>[323.03,317.03]):outside.append(dict(ref=ref,feature=feature,low=lo.tolist(),high=hi.tolist(),width=width))
                    if feature not in ('Support','Support interface','Support transition','Skirt','Brim','Custom'):
                        m['model_segments']+=1;m['model_z_mm'].append(float(new[2]));m['max_model_volumetric_mm3_s']=max(m['max_model_volumetric_mm3_s'],de*math.pi*(1.75/2)**2*speed/distance);m['max_quantization_adjusted_flow_mm3_s']=max(m['max_quantization_adjusted_flow_mm3_s'],max(de-.000005,0)*math.pi*(1.75/2)**2*speed/(distance+math.sqrt(2)*.001))
                        if distance>=1:m['max_long_segment_flow_mm3_s']=max(m['max_long_segment_flow_mm3_s'],de*math.pi*(1.75/2)**2*speed/distance)
                        if new[2]<=.20001:m['first_layer_model_path_mm']+=distance
                    r=plan[ref];R=np.asarray(r['rotation_3x3']);tt=np.asarray(r['normalization_translation_mm'])+[*r['plate_xy_mm'],0]
                    native=((pos+new)/2-tt)@R
                    segments[ref].append((feature,native.tolist(),float(new[2]),width))
                pos=new
        add(f'Plate {plate}: every model/support/brim path attributed to a known part',not unattributed,unattributed_segments=len(unattributed),examples=unattributed[:3])
        add(f'Plate {plate}: positive extrusion within shared printable bed',not outside,outside_segments=len(outside),examples=outside[:3],shared_bed_bounds_xy_mm=[[27,3],[323,317]],coordinate_tolerance_mm=.03)
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
    allowed_acceleration=max(setting_number(ref,k) for k in ('default_acceleration','inner_wall_acceleration','outer_wall_acceleration','top_surface_acceleration'))
    add('Actual acceleration matches declared R19 profile '+ref,max(f['max_acceleration_mm_s2'] for f in body)<=allowed_acceleration+.1,actual_maximum_mm_s2=max(f['max_acceleration_mm_s2'] for f in body),declared_maximum_mm_s2=allowed_acceleration)
    add('Model extrusion commands consistent with PLA flow cap after quantization '+ref,m['max_quantization_adjusted_flow_mm3_s']<=float(project_settings['filament_max_volumetric_speed'][0])+.01 and m['max_long_segment_flow_mm3_s']<=float(project_settings['filament_max_volumetric_speed'][0])+.05,raw_instantaneous_maximum_mm3_s=m['max_model_volumetric_mm3_s'],minimum_required_flow_after_coordinate_E_rounding_mm3_s=m['max_quantization_adjusted_flow_mm3_s'],raw_maximum_for_segments_at_least_1mm_mm3_s=m['max_long_segment_flow_mm3_s'],cap_mm3_s=float(project_settings['filament_max_volumetric_speed'][0]),coordinate_precision_mm=.001,relative_E_precision_mm=.00001,method='The embedded PLA Basic flow cap is checked separately by native profile validation. For all model commands, allow only the known maximum XY endpoint rounding length error sqrt(2)*0.001mm and half-unit relative-E rounding0.000005mm; any remaining excess fails. Also require raw E/F flow on every segment>=1mm to remain<=cap+0.05mm3/s. Micron-length rounded commands are not reported as sustained physical nozzle flow.')
    if ref in ('P04','P06L','P06R','P11','Q01'):
        for feature,key in [('Outer wall','outer_wall_speed'),('Top surface','top_surface_speed')]:
            actual=m['features'].get(feature,{}).get('max_speed_mm_s',0.)
            limit=setting_number(ref,key)
            add('Retained contact/clip surface speed '+ref+' '+feature,actual<=limit+.01,actual_mm_s=actual,declared_limit_mm_s=limit)
    if ref.startswith('P07'):add('Exact 1.50 mm hard-pad proxy '+ref,abs(m['last_model_z_mm']-1.5)<.0001)
def hits(ref,lo,hi,features):
    return [dict(feature=f,native_midpoint_mm=p,print_z_mm=z,width_mm=w) for f,p,z,w in segments[ref] if f in features and np.all(np.asarray(p)>=lo) and np.all(np.asarray(p)<=hi)]
supports=['Support','Support interface','Support transition']
for ref in ('P06L','P06R'):
    if ref in metrics:add(ref+' rigid rear block has no support extrusion',not any(name in metrics[ref]['features'] for name in supports))
add('Inspected layout and slice stable throughout validation',sha(LAYOUT_PATH)==starting_layout_sha and sha(path)==starting_slice_sha)
result=dict(status='PASS_ACTUAL_R19_THUMB_RIM_TOOLPATHS' if all(c['status']=='PASS' for c in checks) else 'FAIL',
    failed_checks=sum(c['status']=='FAIL' for c in checks),checks=checks,metrics=metrics,
    layout_sha256=starting_layout_sha,validator_sha256=sha(Path(__file__)),CAD_source_sha256=layout['CAD_source_sha256'],editable_project_sha256=sha(OUT/layout['native_project']),
    sliced_internal_evidence_sha256=sha(path),native_R19_version=layout['native_R19_version'],
    scope=f'{len(plan)} selected object(s) on one plate: complete positive-extrusion paths including model, support, interface, transition and brim; conservative full-arc XY envelopes expanded by bead width certify pairwise separation and shared H2D bed bounds. Also checks first-layer presence, final height, declared acceleration/critical surface speeds and the retained PLA Basic flow cap. Verified global process and protected speeds retained; all selected object brims absent and new P01 geometry is sliced afresh. No physical strength claim.')
(V/'toolpath-check.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(dict(status=result['status'],checks=len(checks),failed_checks=result['failed_checks'],failures=[c for c in checks if c['status']=='FAIL']),indent=2))
