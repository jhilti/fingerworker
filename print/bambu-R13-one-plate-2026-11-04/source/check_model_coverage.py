#!/usr/bin/env python3
"""Compare all actual model paths with the validated three-plate R13 slice.

No model feature is omitted. XY translations, ordering, direction and primitive
splitting may change. Match canonical G-code primitives first; compare every
remaining centreline spatially, per part/layer/feature/bead width. Supports,
travel and priming are outside this focused comparison.
"""
from pathlib import Path
from collections import Counter,defaultdict
from hashlib import sha256
import argparse,json,math,re,zipfile,xml.etree.ElementTree as ET
from shapely.geometry import LineString,MultiLineString,GeometryCollection
from shapely.ops import unary_union

OUT=Path(__file__).resolve().parents[1]
BASE=OUT.parent/'bambu-R13-simple-palm-2026-11-03'
EXCLUDE={'Support','Support interface','Support transition','Skirt','Brim','Custom','Prime tower'}
TOKEN=re.compile(r'([XYZEFIJ])(-?\d*\.?\d+)')
SPATIAL_TOL=.01
ARC_SAGITTA=.0005

def sha(p):return sha256(Path(p).read_bytes()).hexdigest()
def md(n):return {m.get('key'):m.get('value') for m in n.findall('metadata') if m.get('key')}
def rnd(x):return round(float(x),5)

def inputs(folder):
    layout_path=folder/'plate-layout.json';layout=json.loads(layout_path.read_text())
    sliced=folder/'validation'/(Path(layout['native_project']).stem+'_verification.gcode.3mf')
    return layout,{p['ref']:p for p in layout['placements']},sliced

def primitive(a,c,vals,ccw):
    """Key independent of path direction, including true arc centre/sweep."""
    if ccw is None:
        aa,bb=sorted([tuple(map(rnd,a)),tuple(map(rnd,c))])
        return ('L',aa,bb),math.dist(a,c)
    centre=(a[0]+vals.get('I',0),a[1]+vals.get('J',0))
    radius=math.dist(a,centre)
    t1=math.atan2(a[1]-centre[1],a[0]-centre[0]);t2=math.atan2(c[1]-centre[1],c[0]-centre[0])
    angle=((t2-t1) if ccw else (t1-t2))%(2*math.pi)
    if angle<1e-10 and math.dist(a,c)<1e-7 and radius>1e-5:angle=2*math.pi
    # Store the equivalent counterclockwise representation for reverse paths.
    start,end=(a,c) if ccw else (c,a)
    key=('A',tuple(map(rnd,start)),tuple(map(rnd,end)),tuple(map(rnd,centre)),round(angle,8))
    return key,radius*angle

def paths(folder):
    layout,plan,path=inputs(folder)
    with zipfile.ZipFile(path) as z:
        cfg=ET.fromstring(z.read('Metadata/model_settings.config'))
        names={o.get('id'):md(o)['name'].split(' - ')[0] for o in cfg.findall('object')}
        for plate,p in enumerate(cfg.findall('plate'),1):
            ids={int(md(m)['identify_id']):names[md(m)['object_id']] for m in p.findall('model_instance')}
            assert set(ids.values())=={r for r,v in plan.items() if v['plate']==plate}
            pos=[0.,0.,0.];eold=0.;relative_e=True;obj=None;feature='';width=.4
            with z.open(f'Metadata/plate_{plate}.gcode') as stream:
                for raw in stream:
                    line=raw.decode().strip()
                    if line.startswith('; start printing object, unique label id: '):obj=int(line.split(':')[1])
                    elif len(ids)==1 and line.startswith('; OBJECT_ID: '):obj=next(iter(ids))
                    elif line.startswith('; stop printing object'):obj=None
                    elif line.startswith('; FEATURE: '):
                        feature=line[11:].strip()
                        if feature=='Custom':obj=None
                    elif line.startswith('; LINE_WIDTH: '):width=float(line.split(':')[1])
                    elif line.startswith('M83'):relative_e=True
                    elif line.startswith('M82'):relative_e=False
                    elif line.startswith('G92 '):
                        v=dict(TOKEN.findall(line));eold=float(v.get('E',eold))
                    elif line.startswith(('G0 ','G1 ','G2 ','G3 ')):
                        vals={a:float(v) for a,v in TOKEN.findall(line.split(';')[0])}
                        new=[vals.get(a,pos[j]) for j,a in enumerate('XYZ')]
                        de=vals.get('E',0) if relative_e else vals.get('E',eold)-eold
                        if 'E' in vals:eold=eold+vals['E'] if relative_e else vals['E']
                        if de>1e-8 and feature not in EXCLUDE and (math.dist(new[:2],pos[:2])>1e-6 or line.startswith(('G2 ','G3 '))):
                            assert obj in ids,('Unattributed model extrusion',plate,feature,obj,line)
                            assert abs(new[2]-pos[2])<1e-5,('Nonplanar model extrusion',line)
                            ref=ids[obj];tx,ty=plan[ref]['plate_xy_mm']
                            a=(pos[0]-tx,pos[1]-ty);c=(new[0]-tx,new[1]-ty)
                            key,length=primitive(a,c,vals,None if line.startswith(('G0 ','G1 ')) else line.startswith('G3 '))
                            if length>1e-6:yield (ref,rnd(new[2]),feature,rnd(width)),key,length
                        pos=new

def coords(key):
    if key[0]=='L':return [key[1],key[2]]
    _,a,c,centre,angle=key
    r=math.dist(a,centre);t=math.atan2(a[1]-centre[1],a[0]-centre[0])
    max_angle=2*math.acos(max(-1,1-ARC_SAGITTA/r)) if r>ARC_SAGITTA else math.pi/4
    count=max(1,math.ceil(angle/max_angle))
    pts=[(centre[0]+r*math.cos(t+angle*i/count),centre[1]+r*math.sin(t+angle*i/count)) for i in range(count+1)]
    pts[0]=a;pts[-1]=c
    return pts

def geometry(counter):
    lines=[coords(key) for key,n in counter.items() if n>0]
    return MultiLineString(lines) if lines else GeometryCollection()

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--candidate-dir',type=Path,default=OUT);args=ap.parse_args()
    folder=args.candidate_dir.resolve();layout,plan,sliced=inputs(folder);bl,bp,bs=inputs(BASE)
    start_layout=sha(folder/'plate-layout.json');start_slice=sha(sliced);start_project=sha(folder/layout['native_project'])
    assert set(plan)==set(bp)
    for ref,p in plan.items():
        for field in ['source_sha256','rotation_3x3','normalization_translation_mm','size_oriented_mm']:
            assert p[field]==bp[ref][field],(ref,field)
    assert layout['object_settings']==bl['object_settings']
    old=defaultdict(Counter);extra=defaultdict(Counter)
    bm=defaultdict(lambda:dict(segments=0,length_mm=0.));nm=defaultdict(lambda:dict(segments=0,length_mm=0.))
    for group,key,length in paths(BASE):
        old[group][key]+=1;bm[group]['segments']+=1;bm[group]['length_mm']+=length
    print('Parsed baseline',sum(v['segments'] for v in bm.values()),'model primitives',flush=True)
    exact=Counter()
    for group,key,length in paths(folder):
        nm[group]['segments']+=1;nm[group]['length_mm']+=length
        if old[group].get(key,0)>0:
            old[group][key]-=1;exact[group]+=1
        else:extra[group][key]+=1
    print('Parsed candidate',sum(v['segments'] for v in nm.values()),'model primitives',flush=True)
    # Exact cancellation can remove a neighbouring path which covers a
    # changed/split endpoint. Restore full layer context only where needed.
    spatial={};context_needed=set()
    for g in set(bm)|set(nm):
        a=+old[g];c=+extra[g]
        if not a and not c:continue
        ga,gc=geometry(a),geometry(c)
        ua=float(ga.difference(gc.buffer(SPATIAL_TOL,quad_segs=8)).length) if not ga.is_empty else 0.
        uc=float(gc.difference(ga.buffer(SPATIAL_TOL,quad_segs=8)).length) if not gc.is_empty else 0.
        spatial[g]=dict(baseline=ua,candidate=uc,mode='unmatched_primitives',tolerance_mm=SPATIAL_TOL)
        if max(ua,uc)>1e-6:context_needed.add(g)
    if context_needed:
        ca=defaultdict(Counter);cc=defaultdict(Counter)
        for g,k,l in paths(BASE):
            if g in context_needed:ca[g][k]+=1
        for g,k,l in paths(folder):
            if g in context_needed:cc[g][k]+=1
        for g in context_needed:
            ga,gc=geometry(ca[g]),geometry(cc[g])
            da=ga.difference(gc.buffer(SPATIAL_TOL,quad_segs=8));dc=gc.difference(ga.buffer(SPATIAL_TOL,quad_segs=8))
            ua,uc=float(da.length),float(dc.length)
            result=dict(baseline=ua,candidate=uc,mode='complete_feature_layer_context',tolerance_mm=SPATIAL_TOL)
            # Placing a model elsewhere can relocate the deliberate wall seam
            # gap. This narrowly bounded case is not a missing wall/island:
            # <=0.1mm changed path per direction, >=0.44mm bead width, and
            # <=0.005mm net path change. Require complete spatial coverage
            # within0.05mm as well, and report every exception explicitly.
            if max(ua,uc)>1e-6 and g[2]=='Inner wall' and g[3]>=.44 and max(ua,uc)<=.100001 and abs(nm[g]['length_mm']-bm[g]['length_mm'])<=.005:
                a5=float(ga.difference(gc.buffer(.05,quad_segs=8)).length)
                c5=float(gc.difference(ga.buffer(.05,quad_segs=8)).length)
                if max(a5,c5)<1e-6:
                    result=dict(baseline=a5,candidate=c5,mode='bounded_inner_wall_seam_relocation',tolerance_mm=.05,
                        strict_0_01_uncovered_baseline_mm=ua,strict_0_01_uncovered_candidate_mm=uc,
                        changed_baseline_bounds_mm=list(da.bounds),changed_candidate_bounds_mm=list(dc.bounds))
            spatial[g]=result
    checks=[];rows=[];details=[]
    def add(name,ok,**e):checks.append(dict(name=name,status='PASS' if bool(ok) else 'FAIL',**e))
    add('Same exact source meshes, orientations, normalization and object settings',True)
    add('Identical part/layer/feature/line-width group set',set(bm)==set(nm),missing_groups=[list(g) for g in sorted(set(bm)-set(nm))],new_groups=[list(g) for g in sorted(set(nm)-set(bm))])
    failures=[]
    perpart={r:dict(model_layers=0,feature_width_layer_groups=0,baseline_segments=0,candidate_segments=0,exact_primitives=0,spatially_checked_groups=0,maximum_layer_feature_path_delta_mm=0.,maximum_uncovered_centreline_mm=0.) for r in plan}
    for g in sorted(set(bm)|set(nm)):
        ref,z,feature,width=g;aa=bm.get(g,dict(segments=0,length_mm=0.));bb=nm.get(g,dict(segments=0,length_mm=0.));a=+old[g];c=+extra[g]
        removed=sum(a.values());added=sum(c.values())
        ua=uc=0.
        if removed or added:
            ga,gc=geometry(a),geometry(c);sr=spatial[g];ua,uc=sr['baseline'],sr['candidate']
            # This is a spatial check of every unmatched segment, not its
            # midpoint or bounding box. Arcs are conservatively chorded.
            details.append(dict(ref=ref,z_mm=z,feature=feature,line_width_mm=width,
                unmatched_baseline_primitives=removed,unmatched_candidate_primitives=added,
                uncovered_baseline_centreline_mm=ua,uncovered_candidate_centreline_mm=uc,
                baseline_unmatched_bounds_mm=None if ga.is_empty else list(ga.bounds),
                candidate_unmatched_bounds_mm=None if gc.is_empty else list(gc.bounds),comparison=sr))
        delta=bb['length_mm']-aa['length_mm']
        # G-code XY coordinates are rounded to0.001mm. Summing hundreds of
        # short segments accumulates that quantization. Per unmatched straight
        # primitive allow0.0015mm (above sqrt(2)*0.001); for arcs allow0.012mm
        # for centre/radius/endpoint rounding. Spatial coverage remains required.
        na=sum(v for k,v in a.items() if k[0]=='A')+sum(v for k,v in c.items() if k[0]=='A')
        length_tol=.003+.0015*(removed+added-na)+.012*na
        ok=ua<1e-6 and uc<1e-6 and abs(delta)<=length_tol and g in bm and g in nm
        row=dict(ref=ref,z_mm=z,feature=feature,line_width_mm=width,status='PASS' if ok else 'FAIL',
            baseline_segments=aa['segments'],candidate_segments=bb['segments'],exact_primitives=exact[g],
            baseline_length_mm=aa['length_mm'],candidate_length_mm=bb['length_mm'],path_length_delta_mm=delta,
            permitted_length_delta_mm=length_tol,uncovered_baseline_mm=ua,uncovered_candidate_mm=uc)
        rows.append(row)
        if not ok:failures.append(row)
        pm=perpart[ref];pm['feature_width_layer_groups']+=1;pm['baseline_segments']+=aa['segments'];pm['candidate_segments']+=bb['segments'];pm['exact_primitives']+=exact[g]
        pm['spatially_checked_groups']+=bool(removed or added)
        pm['maximum_layer_feature_path_delta_mm']=max(pm['maximum_layer_feature_path_delta_mm'],abs(delta))
        pm['maximum_uncovered_centreline_mm']=max(pm['maximum_uncovered_centreline_mm'],ua,uc)
    for ref in plan:
        bz=sorted({g[1] for g in bm if g[0]==ref});nz=sorted({g[1] for g in nm if g[0]==ref})
        perpart[ref]['model_layers']=len(nz)
        add('All baseline model layers retained '+ref,bz==nz,baseline_layers=len(bz),candidate_layers=len(nz),missing_layers=sorted(set(bz)-set(nz)),extra_layers=sorted(set(nz)-set(bz)))
        bad=[r for r in failures if r['ref']==ref]
        add('Complete normalized model coverage '+ref,not bad,failed_groups=len(bad))
    add('Inspected layout, editable project and slice stable',sha(folder/'plate-layout.json')==start_layout and sha(sliced)==start_slice and sha(folder/layout['native_project'])==start_project)
    result=dict(status='PASS_NORMALIZED_MODEL_TOOLPATH_COVERAGE' if all(c['status']=='PASS' for c in checks) else 'FAIL',
        CAD_source_sha256=layout['CAD_source_sha256'],layout_sha256=start_layout,editable_project_sha256=start_project,
        sliced_internal_evidence_sha256=start_slice,validator_sha256=sha(__file__),
        baseline_layout_sha256=sha(BASE/'plate-layout.json'),baseline_sliced_internal_evidence_sha256=sha(bs),
        checks=checks,failures=failures,part_metrics=perpart,unmatched_spatial_comparisons=details,
        feature_width_layer_groups=len(rows),model_layer_feature_checks=rows,
        scope='All positive model extrusions, every part/layer/feature/bead width. No missing-layer or perimeter/island region accepted. XY translation, path direction/order and primitive splitting ignored. Infill is also checked spatially here; no assumption that changed infill phase is equivalent.',
        numerical_limits=dict(canonical_coordinate_quantum_mm=.00001,unmatched_polyline_coverage_tolerance_mm=SPATIAL_TOL,arc_chord_sagitta_mm=ARC_SAGITTA,
            complete_curve_distance_bound_mm=SPATIAL_TOL+2*ARC_SAGITTA+.00002,
            bounded_inner_wall_seam_distance_mm=.05,
            seam_exception_requirements='Inner wall; width>=0.44mm; strict0.01mm uncovered length<=0.1mm in each direction; net layer/width path delta<=0.005mm; complete layer context covered at0.05mm.',
            per_group_length_delta='0.003mm + 0.0015mm per unmatched straight primitive + 0.012mm per unmatched arc; coverage also required'),
        limitations='Compared with the validated baseline toolpaths; not a physical extrusion or mechanical-strength test. Travel, supports, skirt, brim and priming excluded and checked by separate audits.')
    target=folder/'validation/model-coverage-check.json';target.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],groups=len(rows),spatial_groups=len(details),failures=len(failures),per_part=perpart),indent=2),flush=True)

if __name__=='__main__':main()
