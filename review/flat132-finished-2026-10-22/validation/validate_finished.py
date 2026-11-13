#!/usr/bin/env python3
"""Reproducible native CAD audit; does not create or repair production geometry.

Run with /tmp/fingerworker-sensor-cad-20261022/bin/python. All tolerances and
intentional contacts are recorded. An absent native pose or unresolved sweep
cannot become PASS. Neutral STL must be the assembled 0 stroke/0 preload pose.
"""
from __future__ import annotations
import argparse
from io import BytesIO
from itertools import combinations
import hashlib
import importlib.metadata
import json
from pathlib import Path
import re
import time
import zipfile

import manifold3d as md
import numpy as np
import trimesh as tm

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DEVICE = set('H01 H02 H030 H031 H040 H041 H050 H051 H060 H061 H070 H071 H080 H081 H09 H09a H09b H10 H11 H12 H13 H15 H160 H161 H170 H171 H180 H181 H190 H191 H20 H21 H22 P01 P02 P03 P04 P05 P060 P061 P070a P070b P071a P071b P08 P09 P10'.split())
MOVING = {'P04','H10','H060','H061'}
PRELOAD = set('P05 H050 H051 H12 H01 H02 H13 H180 H181 H190 H191 H20 H23 H240 H241 H242 H243 H250 H251 H252 H253'.split())
SPRINGS = {'H030','H031'}
ARTICULATED = {'H09a','H09b'}
PIVOT=np.array([25.5,-14.1,9.2])
LEVER_LENGTH=float(np.hypot(3.1,16.7))
REF = re.compile(r'(?<![A-Za-z0-9])([PH]\d{2}(?:\d[a-d]?|[a-d])?)(?=[\s_.-]|$)')
PCB = re.compile(r'REF[ _-]+PCB[ _-]+([A-Z]+\d+)',re.I)
ELEC = re.compile(r'REF[ _-]+(E\d{2})(?=[\s_.-]|$)',re.I)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    def convert(value):
        if isinstance(value,np.generic):return value.item()
        if isinstance(value,np.ndarray):return value.tolist()
        raise TypeError('Not JSON serializable: '+repr(type(value)))
    path.write_text(json.dumps(obj,indent=2,allow_nan=False,default=convert)+'\n')


def solid(mesh):
    if not mesh.is_watertight or not mesh.is_volume:
        raise ValueError('Not a closed, positive, consistently oriented volume')
    obj=md.Manifold(md.Mesh64(vert_properties=np.asarray(mesh.vertices,np.float64),tri_verts=np.asarray(mesh.faces,np.uint64)))
    if obj.status()!=md.Error.NoError:
        raise ValueError('Manifold: '+str(obj.status()))
    return obj


def identify(name):
    stem=Path(name).stem
    m=PCB.search(stem)
    if m:return 'PCB_'+m[1].upper()
    m=ELEC.search(stem)
    if m:return m[1].upper()
    m=REF.search(stem)
    return m[1] if m else None


def load(path, manifest):
    path=Path(path)
    if path.is_dir():
        rows=[(str(p.relative_to(path)),p.read_bytes()) for p in sorted(path.rglob('*')) if p.suffix.lower()=='.stl']
    else:
        with zipfile.ZipFile(path) as z:
            rows=[(n,z.read(n)) for n in z.namelist() if n.lower().endswith('.stl')]
    out,ignored={},[]
    for name,raw in rows:
        if any(re.search(p,name) for p in manifest.get('ignore_member_patterns',[])):
            ignored.append({'member':name,'reason':'Explicit manifest pattern'});continue
        ref=manifest.get('member_ref_overrides',{}).get(name,identify(name))
        if ref is None:
            ignored.append({'member':name,'reason':'UNRECOGNIZED'});continue
        if ref in out:raise ValueError('Duplicate ref '+ref+': '+out[ref]['member']+' / '+name)
        mesh=tm.load_mesh(BytesIO(raw),file_type='stl',process=True)
        # Unite duplicate coordinates for topology only. No geometric repairs.
        out[ref]={'member':name,'sha256':hashlib.sha256(raw).hexdigest(),'mesh':mesh}
        try:
            out[ref]['object']=solid(mesh)
            out[ref]['connected_solid_count']=len(out[ref]['object'].decompose())
            if out[ref]['connected_solid_count']!=1 and ref not in SPRINGS and ref not in manifest.get('allow_disconnected_refs',[]):
                out[ref]['error']='Native per-part STL contains '+str(out[ref]['connected_solid_count'])+' disconnected solids'
        except Exception as e:out[ref]['error']=str(e)
    return out,ignored


def identities(inputs):
    return {r:v['sha256'] for r,v in inputs.items()}


def aabb_gap(a,b):
    separation=np.maximum(np.maximum(a[0]-b[1],b[0]-a[1]),0.)
    return float(np.linalg.norm(separation))


def bounds(obj):
    return np.asarray(obj.bounding_box(),float).reshape(2,3)


def separated(a,b):
    return bool(np.any(np.minimum(a[1],b[1])-np.maximum(a[0],b[0])<=0.))


def pair(a,b,tol,search):
    aa,bb=bounds(a),bounds(b)
    if aabb_gap(aa,bb)>=search:
        return {'intersection_volume_mm3':0.,'minimum_gap_mm':search,
                'gap_search_cap_mm':search,'gap_is_lower_bound':True,
                'status':'CLEAR_AT_NUMERICAL_TOLERANCE','method':'AABB gap lower bound exceeds search cap'}
    if separated(aa,bb):
        volume=0.
    else:volume=float((a^b).volume())
    gap=0. if volume>tol else float(a.min_gap(b,search))
    return {'intersection_volume_mm3':volume,'minimum_gap_mm':gap,
            'gap_search_cap_mm':search,'gap_is_lower_bound':bool(gap>=search-1e-8),
            'status':'INTERFERENCE' if volume>tol else 'CLEAR_AT_NUMERICAL_TOLERANCE'}


def classify(row,contact,tol):
    if not contact:return row
    row['declared_contact']=contact
    volume=row.get('intersection_volume_mm3',row.get('maximum_sampled_volume_mm3',0.))
    kind=contact.get('kind','exterior_contact')
    maximum=float(contact.get('maximum_intersection_volume_mm3',tol))
    if kind=='exterior_contact':maximum=tol  # exterior contact never permits material overlap
    if volume>maximum:
        row['status']='INTERFERENCE'
    elif volume>tol:
        row['status']='DECLARED_NOMINAL_FIT_OVERLAP'
        row['qualification']='NOT_ESTABLISHED; explicit modeled fit, not a clearance claim'
    elif row['status']=='CLEAR_AT_NUMERICAL_TOLERANCE':
        row['status']='INTENDED_EXTERIOR_CONTACT_OR_CLEARANCE'
    return row


def relative_sweep(a,b,start,stop,tol,minimum_interval,contact=None):
    """Certify full relative X interval with an exact 1-Lipschitz gap bound.

    When each body translates affinely along X, image of the stroke/preload
    rectangle under their relative displacement is exactly [start,stop].
    Therefore this certificate covers independent parameters, not just samples.
    """
    result={'relative_x_range_mm':[start,stop],'status':'UNCHECKED','certified_intervals':0,
            'intersections':[],'unresolved_intervals':[],'samples':[]}
    if abs(stop-start)<1e-12:
        result.update(pair(a.translate([start,0,0]),b,tol,2.))
        return classify(result,contact,tol)
    ab,bb=bounds(a),bounds(b)
    swept=ab.copy();swept[0,0]+=start;swept[1,0]+=stop
    if separated(swept,bb):
        result.update(status='CONTINUOUS_CLEARANCE_CERTIFIED',certified_intervals=1,
                      method='Swept AABB separation including permitted exterior boundary touch',maximum_sampled_volume_mm3=0.)
        return result
    # Clip the translating solid to the fixed body's transverse slab. This
    # is exact for pure X translation and proves end-stop tangency without
    # interpreting finite sample spacing as a continuous certificate.
    clipped=a
    for axis in (1,2):
        n=[0.,0.,0.];n[axis]=1.;clipped=clipped.trim_by_plane(n,float(bb[0,axis]))
        n[axis]=-1.;clipped=clipped.trim_by_plane(n,float(-bb[1,axis]))
    if clipped.is_empty():
        result.update(status='CONTINUOUS_CLEARANCE_CERTIFIED',certified_intervals=1,
                      method='Empty exact transverse slab',maximum_sampled_volume_mm3=0.);return result
    cb=bounds(clipped)
    if cb[0,0]+start>=bb[1,0] or cb[1,0]+stop<=bb[0,0]:
        result.update(status='CONTINUOUS_CLEARANCE_CERTIFIED',certified_intervals=1,
                      method='Exact transverse slab + swept axial bounds',
                      clipped_bounds_mm=cb.tolist(),maximum_sampled_volume_mm3=0.);return result
    # Every intermediate translate is contained in the convex hull of the
    # two endpoint solids. A Boolean against that conservative envelope bounds
    # the intersection at every pose, including intended slot-end tangency.
    # Filling concavities can only cause this certificate to be inconclusive.
    swept_hull=(a.translate([start,0,0])+a.translate([stop,0,0])).hull()
    hull_overlap=float((swept_hull^b).volume())
    if hull_overlap<=tol:
        result.update(status='CONTINUOUS_CLEARANCE_AT_NUMERICAL_VOLUME_TOLERANCE',certified_intervals=1,
            method='Conservative complete swept convex-hull intersection volume bounds every pose',
            complete_swept_envelope_intersection_upper_bound_mm3=hull_overlap,
            maximum_sampled_volume_mm3=0.)
        return result
    samples={}
    def sample(t,search):
        if t not in samples:
            obj=a.translate([t,0,0]);v=float((obj^b).volume())
            samples[t]={'relative_x_mm':t,'intersection_volume_mm3':v,'gap_mm':0.,'gap_search_cap_mm':0.}
            if v>tol:result['intersections'].append({'relative_x_mm':t,'volume_mm3':v})
        row=samples[t]
        if row['intersection_volume_mm3']<=tol and row['gap_search_cap_mm']<search:
            row['gap_mm']=float(a.translate([t,0,0]).min_gap(b,search));row['gap_search_cap_mm']=search
        return row
    def certify(lo,hi):
        ba=ab.copy();ba[0,0]+=lo;ba[1,0]+=hi
        if separated(ba,bb):result['certified_intervals']+=1;return
        mid,half=(lo+hi)/2,(hi-lo)/2
        item=sample(mid,half+.01)
        if item['intersection_volume_mm3']>tol:return
        if item['gap_mm']>half+1e-5:result['certified_intervals']+=1;return
        if hi-lo<=minimum_interval:
            result['unresolved_intervals'].append({'relative_x_interval_mm':[lo,hi],'midpoint_gap_mm':item['gap_mm']});return
        certify(lo,mid);certify(mid,hi)
    try:
        sample(start,.01);sample(stop,.01);certify(start,stop)
        result['samples']=[samples[t] for t in sorted(samples)]
        result['maximum_sampled_volume_mm3']=max(x['intersection_volume_mm3'] for x in samples.values())
        result['status']='INTERFERENCE' if result['intersections'] else 'UNRESOLVED_NEAR_CONTACT' if result['unresolved_intervals'] else 'CONTINUOUS_CLEARANCE_CERTIFIED'
        # Never make an unresolved moving fit PASS from a sampled maximum.
    except Exception as e:result.update(status='UNCHECKED',reason=repr(e))
    return result


def motion(ref,manifest):
    override=manifest.get('motion_overrides',{}).get(ref)
    if override is not None:return np.asarray(override,float)
    return np.array([-1. if ref in MOVING else 0.,1. if ref in PRELOAD else 0.])


def actuator_angle(stroke):
    dx=min(33.4,60-stroke-2.4)-25.5
    return float(np.arctan2(np.sqrt(LEVER_LENGTH**2-dx**2),dx))


def actuator_transform(stroke):
    angle=actuator_angle(stroke)-actuator_angle(0.)
    c,s=np.cos(angle),np.sin(angle)
    rot=np.array([[c,-s,0.],[s,c,0.],[0.,0.,1.]])
    return np.column_stack((rot,PIVOT-rot@PIVOT))


def rotational_bounds(vertices,stroke0,stroke1):
    """Exact extrema of every mesh vertex under a monotone Z rotation arc."""
    low,high=actuator_angle(stroke0)-actuator_angle(0.),actuator_angle(stroke1)-actuator_angle(0.)
    v=vertices-PIVOT;r=np.linalg.norm(v[:,:2],axis=1)
    result=np.array([[0.,0.,vertices[:,2].min()],[0.,0.,vertices[:,2].max()]])
    for axis,phase in [(0,np.arctan2(-v[:,1],v[:,0])),(1,np.arctan2(v[:,0],v[:,1]))]:
        ends=np.stack((r*np.cos(low-phase),r*np.cos(high-phase)))
        minima,maxima=ends.min(0),ends.max(0)
        maxi=phase+2*np.pi*np.ceil((low-phase)/(2*np.pi))
        mini=phase+np.pi+2*np.pi*np.ceil((low-phase-np.pi)/(2*np.pi))
        maxima=np.where(maxi<=high+1e-12,r,maxima)
        minima=np.where(mini<=high+1e-12,-r,minima)
        result[0,axis]=minima.min()+PIVOT[axis];result[1,axis]=maxima.max()+PIVOT[axis]
    return result


def articulated_sweep(ref,target,inputs,manifest):
    """Full source actuator arc × independent preload interval certificate."""
    tol=manifest.get('volume_tolerance_mm3',.01);minimum=manifest.get('minimum_interval_mm',.0625)
    row={'pair':[ref,target],'status':'UNCHECKED','stroke_range_mm':[0.,30.],'preload_range_mm':[0.,2.],
         'model':'Source fixed-length actuator rotating about (25.5,-14.1,9.2), roller centre min(33.4,57.6−stroke)',
         'certified_rectangles':0,'intersections':[],'unresolved_rectangles':[],'samples':[]}
    try:
        aa,bb=inputs[ref]['object'],inputs[target]['object'];vertices=inputs[ref]['mesh'].vertices
        mb=motion(target,manifest);bbox=bounds(bb)
        if target in ARTICULATED:
            contact=next((v for v in manifest.get('contacts',[]) if set(v['pair'])=={ref,target}),None)
            if not contact:raise ValueError('Actuator joint requires explicit purchased-assembly contact declaration')
            row.update(classify(pair(aa,bb,tol,2.),contact,tol))
            row.update(method='Both actuator previews share the identical rigid rotation; intersection volume invariant',certified_rectangles=1)
            return row
        if ref=='H09b' and target=='H10':
            center=np.array([33.4,-14.1+np.sqrt(LEVER_LENGTH**2-(33.4-25.5)**2),9.2])
            radial=np.linalg.norm(vertices[:,:2]-center[:2],axis=1)
            if radial.max()>2.40001 or bounds(bb)[0,0]<59.99999:raise ValueError('Cam/roller source analytic witness does not match native meshes')
            row.update(status='CONTINUOUS_CLEARANCE_CERTIFIED',certified_rectangles=1,
                method='Analytic exterior-contact separating X plane: roller maxX ≤ min(35.8,60−stroke), cam minX=60−stroke; all preload independent',
                maximum_sampled_volume_mm3=0.)
            return row
        radius=float(np.linalg.norm(vertices-PIVOT,axis=1).max());samples={}
        def obj(s,p):
            return aa.transform(actuator_transform(s).tolist()).translate([-float(mb@np.array([s,p])),0.,0.])
        def sample(s,p,search):
            key=(s,p)
            if key not in samples:
                result=pair(obj(s,p),bb,tol,search)
                samples[key]={'stroke_mm':s,'preload_mm':p,**result}
                if result['intersection_volume_mm3']>tol:row['intersections'].append(samples[key])
            elif samples[key]['gap_search_cap_mm']<search and samples[key]['intersection_volume_mm3']<=tol:
                samples[key].update(pair(obj(s,p),bb,tol,search))
            return samples[key]
        def certify(s0,s1,p0,p1):
            ab=rotational_bounds(vertices,s0,s1)
            offsets=[-float(mb@np.array([s,p])) for s in (s0,s1) for p in (p0,p1)]
            ab[0,0]+=min(offsets);ab[1,0]+=max(offsets)
            if separated(ab,bbox):row['certified_rectangles']+=1;return
            sm,pm=(s0+s1)/2,(p0+p1)/2
            angular=max(abs(actuator_angle(sm)-actuator_angle(s0)),abs(actuator_angle(s1)-actuator_angle(sm)))
            travel=2*radius*np.sin(angular/2)+abs(mb[0])*(s1-s0)/2+abs(mb[1])*(p1-p0)/2
            value=sample(sm,pm,travel+.01)
            if value['intersection_volume_mm3']>tol:return
            if value['minimum_gap_mm']>travel+1e-5:row['certified_rectangles']+=1;return
            if s1-s0<=minimum and (p1-p0<=minimum or abs(mb[1])<1e-12):
                row['unresolved_rectangles'].append({'stroke_mm':[s0,s1],'preload_mm':[p0,p1],'midpoint_gap_mm':value['minimum_gap_mm']});return
            if (s1-s0)*(1+radius*.067)>=abs(mb[1])*(p1-p0):
                certify(s0,sm,p0,p1);certify(sm,s1,p0,p1)
            else:certify(s0,s1,p0,pm);certify(s0,s1,pm,p1)
        for s in (0.,24.2,30.):
            for p in (0.,2.):sample(s,p,.01)
        certify(0.,24.2,0.,2.);certify(24.2,30.,0.,2.)
        row['samples']=list(samples.values());row['maximum_sampled_volume_mm3']=max(x['intersection_volume_mm3'] for x in samples.values())
        row['status']='INTERFERENCE' if row['intersections'] else 'UNRESOLVED_NEAR_CONTACT' if row['unresolved_rectangles'] else 'CONTINUOUS_CLEARANCE_CERTIFIED'
    except Exception as e:row.update(status='UNCHECKED',reason=repr(e))
    return row


def all_pairs(inputs,manifest,stroke=0.,preload=0.,sweeps=False):
    rows=[];tol=manifest.get('volume_tolerance_mm3',.01)
    contacts={frozenset(v['pair']):v for v in manifest.get('contacts',[])}
    refs=sorted(set(inputs)-SPRINGS)
    for a,b in combinations(refs,2):
        row={'pair':[a,b]}
        try:
            if 'object' not in inputs[a] or 'object' not in inputs[b]:
                raise ValueError('Missing valid solid')
            aa,bb=inputs[a]['object'],inputs[b]['object']
            ma,mb=motion(a,manifest),motion(b,manifest)
            contact=contacts.get(frozenset((a,b)))
            if sweeps:
                if a in ARTICULATED or b in ARTICULATED:
                    ref,target=(a,b) if a in ARTICULATED else (b,a)
                    row.update(articulated_sweep(ref,target,inputs,manifest))
                else:
                    dm=ma-mb
                    corners=[dm@np.array([s,p]) for s in (0.,30.) for p in (0.,2.)]
                    if b in MOVING and a not in MOVING:
                        row.update(relative_sweep(bb,aa,float(-max(corners)),float(-min(corners)),tol,manifest.get('minimum_interval_mm',.0625),contact))
                        row['pair']=[b,a];row['relative_x_coefficients_stroke_preload']=(-dm).tolist()
                    else:
                        row.update(relative_sweep(aa,bb,float(min(corners)),float(max(corners)),tol,manifest.get('minimum_interval_mm',.0625),contact))
                        row['relative_x_coefficients_stroke_preload']=dm.tolist()
            else:
                row.update(classify(pair(aa,bb,tol,manifest.get('gap_search_mm',2.)),contact,tol))
                row.update(native_stroke_mm=stroke,native_preload_mm=preload)
        except Exception as e:row.update(status='UNCHECKED',reason=repr(e))
        rows.append(row)
    return rows


def ray_levels(mesh,origin,direction,axis):
    """Vectorized Moller-Trumbore ray intersections, no spatial-index dependency."""
    triangles=np.asarray(mesh.triangles,float)
    orig,vec=np.asarray(origin,float),np.asarray(direction,float)
    e1=triangles[:,1]-triangles[:,0];e2=triangles[:,2]-triangles[:,0]
    p=np.cross(np.broadcast_to(vec,e2.shape),e2);det=np.einsum('ij,ij->i',e1,p)
    good=np.abs(det)>1e-10
    inv=np.zeros_like(det);inv[good]=1/det[good]
    tvec=orig-triangles[:,0];u=np.einsum('ij,ij->i',tvec,p)*inv
    q=np.cross(tvec,e1);v=np.einsum('j,ij->i',vec,q)*inv
    t=np.einsum('ij,ij->i',e2,q)*inv
    valid=good&(u>=-1e-9)&(v>=-1e-9)&(u+v<=1+1e-9)&(t>=-1e-9)
    return np.unique(np.round((orig+t[valid,None]*vec)[:,axis],7))


def dimensions(inputs,manifest):
    rows=[]
    for spec in manifest.get('dimension_checks',[]):
        row=dict(spec)
        try:
            mesh=inputs[spec['ref']]['mesh']
            if spec['type']=='bounds':
                value=float({'minimum':mesh.bounds[0],'maximum':mesh.bounds[1],'extent':mesh.extents,'center':mesh.bounds.mean(0)}[spec['component']][spec['axis']])
            elif spec['type']=='ray_levels':
                levels=ray_levels(mesh,spec['origin_mm'],spec['direction'],spec['axis'])
                row['ray_levels_mm']=levels.tolist()
                value=float(levels[spec['level_indices'][0]]-levels[spec['level_indices'][1]]) if len(spec['level_indices'])==2 else float(levels[spec['level_indices'][0]])
            else:raise ValueError('Unknown dimension type')
            row['measured_mm']=value
            if 'expected_mm' in spec:good=abs(value-spec['expected_mm'])<=spec.get('tolerance_mm',.02)
            else:good=value>=spec['minimum_mm'] and value<=spec.get('maximum_mm',1e30)
            row['status']='PASS' if good else 'FAIL'
        except Exception as e:row.update(status='UNCHECKED',reason=repr(e))
        rows.append(row)
    return rows


def probe_object(spec):
    if spec['type']=='box':
        lo,hi=np.asarray(spec['minimum_mm']),np.asarray(spec['maximum_mm'])
        return md.Manifold.cube((hi-lo).tolist()).translate(lo.tolist())
    if spec['type']=='cylinder_x':
        # Conservative circumscribed cylinder: suitable for empty-clearance
        # probes. For material inclusion, explicitly choose inscribed=True.
        n=128;r=spec['radius_mm']/(1. if spec.get('inscribed') else np.cos(np.pi/n))
        return md.Manifold.cylinder(spec['end_x_mm']-spec['start_x_mm'],r,r,n).rotate([0,90,0]).translate([spec['start_x_mm'],spec['y_mm'],spec['z_mm']])
    raise ValueError('Unknown probe type')


def probes(inputs,manifest):
    rows=[]
    for spec in manifest.get('material_and_clearance_probes',[]):
        row=dict(spec)
        try:
            probe=probe_object(spec);target=inputs[spec['ref']]['object']
            value=float((probe^target).volume()) if spec['expect']=='empty' else float((probe-target).volume())
            row.update(error_volume_mm3=value,status='PASS' if value<=spec.get('volume_tolerance_mm3',.01) else 'FAIL')
        except Exception as e:row.update(status='UNCHECKED',reason=repr(e))
        rows.append(row)
    return rows


def sensor_check(inputs,manifest):
    spec=manifest.get('sensor',{});row={'status':'UNCHECKED','requirement':'Unmodified manufacturer BRep under a rigid unit-scale transform'}
    if not spec:return dict(row,reason='No sensor provenance supplied')
    try:
        canonical=Path(spec['canonical_placed_step'])
        native_path=manifest.get('native_part_steps',{}).get('H01',spec.get('native_assembly_step'))
        row.update(canonical_placed_step=str(canonical),canonical_sha256=sha(canonical),
                   native_step_file=native_path)
        if sha(canonical)!=spec['canonical_sha256']:raise ValueError('Canonical sensor hash mismatch')
        if not native_path:raise ValueError('Native sensor or assembly STEP required for exact unchanged sensor BRep check')
        from OCP.STEPControl import STEPControl_Reader
        from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut
        from OCP.BRepCheck import BRepCheck_Analyzer
        from OCP.BRepGProp import BRepGProp
        from OCP.GProp import GProp_GProps
        from OCP.TopExp import TopExp_Explorer
        from OCP.TopAbs import TopAbs_SOLID
        from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
        from OCP.gp import gp_Trsf
        def read(path):
            reader=STEPControl_Reader()
            if not str(reader.ReadFile(str(path))).endswith('RetDone'):raise ValueError('STEP reader failed')
            reader.TransferRoots();return reader.OneShape()
        def vol(shape):
            props=GProp_GProps();BRepGProp.VolumeProperties_s(shape,props);return float(props.Mass())
        original=read(canonical)
        matrix=np.asarray(spec.get('additional_rigid_transform',np.eye(4)),float)
        if matrix.shape!=(4,4) or not np.allclose(matrix[3],[0,0,0,1]) or not np.allclose(matrix[:3,:3].T@matrix[:3,:3],np.eye(3),atol=1e-9) or not np.isclose(np.linalg.det(matrix[:3,:3]),1):
            raise ValueError('Sensor transform is not a proper unit-scale rigid transform')
        tr=gp_Trsf();tr.SetValues(*matrix[:3,:].ravel());original=BRepBuilderAPI_Transform(original,tr,True).Shape()
        whole=read(Path(native_path));exp=TopExp_Explorer(whole,TopAbs_SOLID)
        original_volume=vol(original);candidates=[];index=0
        while exp.More():
            obj=exp.Current();v=vol(obj)
            if abs(v-original_volume)<.1:
                forward=BRepAlgoAPI_Cut(obj,original);reverse=BRepAlgoAPI_Cut(original,obj)
                forward.Build();reverse.Build()
                if not forward.IsDone() or not reverse.IsDone():raise ValueError('BRep difference failed')
                xor=vol(forward.Shape())+vol(reverse.Shape())
                candidates.append({'solid_index':index,'volume_mm3':v,'symmetric_difference_mm3':xor,'valid':bool(BRepCheck_Analyzer(obj).IsValid())})
            index+=1;exp.Next()
        row.update(native_step_sha256=sha(native_path),original_volume_mm3=original_volume,
                   total_native_solids=index,candidates=candidates,additional_rigid_transform=matrix.tolist())
        best=min(candidates,key=lambda v:v['symmetric_difference_mm3']) if candidates else None
        row['status']='PASS' if best and best['valid'] and best['symmetric_difference_mm3']<=spec.get('brep_volume_tolerance_mm3',1e-4) else 'FAIL'
        row['matching_native_solid']=best
        ref=spec.get('ref','H01')
        row['sensor_stl_ref']=ref;row['sensor_stl_sha256']=inputs.get(ref,{}).get('sha256')
    except Exception as e:row.update(status='UNCHECKED',reason=repr(e))
    return row


def exact_brep_pairs(inputs,manifest):
    """Resolve a declared nominal-surface STL artifact with actual native BRep.

    STEP solid association requires a unique match in all six bounds and
    volume. Ambiguity remains UNCHECKED; no guessed body index is accepted.
    """
    specs=manifest.get('exact_brep_pairs',[])
    if not specs:return []
    rows=[]
    try:
        from OCP.STEPControl import STEPControl_Reader
        from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
        from OCP.BRepGProp import BRepGProp
        from OCP.GProp import GProp_GProps
        from OCP.TopExp import TopExp_Explorer
        from OCP.TopAbs import TopAbs_SOLID
        from OCP.BRepBndLib import BRepBndLib
        from OCP.Bnd import Bnd_Box
        paths=[Path(v) for v in sorted(set(manifest.get('native_part_steps',{}).values()))]
        if not paths:paths=[Path(manifest['sensor']['native_assembly_step'])]
        solids=[]
        def volume(obj):
            prop=GProp_GProps();BRepGProp.VolumeProperties_s(obj,prop);return float(prop.Mass())
        for path in paths:
            reader=STEPControl_Reader()
            if not str(reader.ReadFile(str(path))).endswith('RetDone'):raise ValueError('Native STEP read failure')
            reader.TransferRoots();exp=TopExp_Explorer(reader.OneShape(),TopAbs_SOLID)
            while exp.More():
                obj=exp.Current();box=Bnd_Box();BRepBndLib.AddOptimal_s(obj,box,False)
                solids.append({'index':len(solids),'source_file':str(path),'shape':obj,'bounds':np.array([box.CornerMin().Coord(),box.CornerMax().Coord()]),'volume':volume(obj)})
                exp.Next()
        def find(ref):
            mesh=inputs[ref]['mesh'];candidates=[]
            for item in solids:
                be=float(np.max(np.abs(mesh.bounds-item['bounds'])))
                ve=abs(item['volume']-mesh.volume)
                if be<=.05 and ve<=max(.1,abs(mesh.volume)*.002):candidates.append((item,be,ve))
            if len(candidates)!=1:raise ValueError(f'{ref}: expected unique BRep bounds/volume correspondence, found {len(candidates)}')
            return candidates[0]
        for spec in specs:
            row=dict(spec,native_step_files={str(path):sha(path) for path in paths})
            try:
                a,b=spec['pair'];aa,abe,ave=find(a);bb,bbe,bve=find(b)
                result=BRepAlgoAPI_Common(aa['shape'],bb['shape']);result.Build()
                if not result.IsDone():raise ValueError('BRep intersection failed')
                vi=volume(result.Shape())
                row.update(intersection_volume_mm3=vi,matched_solid_indices=[aa['index'],bb['index']],
                    matched_source_files=[aa['source_file'],bb['source_file']],
                    correspondence_bound_errors_mm=[abe,bbe],correspondence_volume_errors_mm3=[ave,bve],
                    status='PASS' if vi<=spec.get('maximum_intersection_volume_mm3',1e-6) else 'FAIL')
            except Exception as e:row.update(status='UNCHECKED',reason=repr(e))
            rows.append(row)
    except Exception as e:rows=[dict(spec,status='UNCHECKED',reason=repr(e)) for spec in specs]
    return rows


def inventory(inputs):
    return {r:{'member':v['member'],'sha256':v['sha256'],'bounds_mm':v['mesh'].bounds.tolist(),
        'volume_mm3':float(v['mesh'].volume),'triangles':len(v['mesh'].faces),
        'watertight':bool(v['mesh'].is_watertight),'is_volume':bool(v['mesh'].is_volume),
        'status':'ILLUSTRATIVE_SPRING' if r in SPRINGS else 'INVALID' if 'error' in v else 'VALID',
        'connected_solid_count':v.get('connected_solid_count'),'error':v.get('error')} for r,v in inputs.items()}


def pose_semantics(neutral,posed,pose,manifest):
    """Independently check native regenerated pose against declared source motion."""
    rows=[];stroke,preload=pose['stroke_mm'],pose['preload_mm']
    for ref in sorted(set(neutral)&set(posed)-SPRINGS-ARTICULATED):
        row={'name':'Native rigid pose / '+ref,'ref':ref}
        try:
            delta=float(motion(ref,manifest)@np.array([stroke,preload]))
            expected=neutral[ref]['object'].translate([delta,0,0]);actual=posed[ref]['object']
            error=float((expected-actual).volume()+(actual-expected).volume())
            bound_error=float(np.max(np.abs(bounds(expected)-bounds(actual))))
            row.update(expected_translation_x_mm=delta,symmetric_difference_mm3=error,
                maximum_bound_error_mm=bound_error,status='PASS' if error<=manifest.get('native_pose_mesh_xor_tolerance_mm3',.1) and bound_error<=.02 else 'FAIL')
        except Exception as e:row.update(status='UNCHECKED',reason=repr(e))
        rows.append(row)
    for ref in sorted(ARTICULATED&set(neutral)&set(posed)):
        row={'name':'Native actuator source arc / '+ref,'ref':ref}
        try:
            expected=neutral[ref]['object'].transform(actuator_transform(stroke).tolist());actual=posed[ref]['object']
            error=float((expected-actual).volume()+(actual-expected).volume())
            row.update(symmetric_difference_mm3=error,rotation_radians=actuator_angle(stroke)-actuator_angle(0.),
                status='PASS' if error<=manifest.get('native_pose_mesh_xor_tolerance_mm3',.1) else 'FAIL')
        except Exception as e:row.update(status='UNCHECKED',reason=repr(e))
        rows.append(row)
    def scalar(name,value,expected,tol=.02):
        rows.append({'name':name,'measured_mm':float(value),'expected_mm':float(expected),'tolerance_mm':tol,
                     'status':'PASS' if abs(value-expected)<=tol else 'FAIL'})
    try:
        roller_x=min(33.4,60-stroke-2.4)
        roller_y=-14.1+np.sqrt(3.1**2+16.7**2-(roller_x-25.5)**2)
        scalar('Source articulated roller center X',posed['H09b']['mesh'].bounds[:,0].mean(),roller_x)
        scalar('Source articulated roller center Y',posed['H09b']['mesh'].bounds[:,1].mean(),roller_y)
        for ref in ('H050','H051'):
            scalar(ref+' fixed seat spring face X',posed[ref]['mesh'].bounds[1,0],12+preload)
        for ref in ('H060','H061'):
            scalar(ref+' moving seat spring face X',posed[ref]['mesh'].bounds[0,0],113-stroke)
        if pose['mode']=='isometric':
            scalar('Native isometric fixed-length stroke',stroke,15-preload)
            for ref,side in [('H140',-1),('H141',1)]:
                mb=posed[ref]['mesh'].bounds
                scalar(ref+' lock-sleeve start X',mb[0,0],12+preload)
                scalar(ref+' lock-sleeve end X',mb[1,0],113-stroke)
                scalar(ref+' lock-sleeve length',mb[1,0]-mb[0,0],86.)
                scalar(ref+' lock-sleeve center Y',mb[:,1].mean(),51*side)
    except Exception as e:rows.append({'name':'Actual articulated / isometric datums','status':'UNCHECKED','reason':repr(e)})
    return rows


def spring_envelopes(inputs,manifest):
    rows=[];tol=manifest.get('volume_tolerance_mm3',.01)
    # The whole envelope at zero stroke and preload covers every shortening
    # coil interval at any operating combination. Front endpoints advance up
    # to 2 mm. It is conservative and does not represent wire solid height.
    for side in (-1,1):
        env=probe_object({'type':'cylinder_x','start_x_mm':12.,'end_x_mm':113.,'y_mm':51.*side,'z_mm':18.,'radius_mm':7.4})
        for ref in sorted(inputs):
            if ref in SPRINGS or ref in ARTICULATED:continue
            if ref not in {'P01','P02','P03','P04','P05','H01','H12'} and not ref.startswith(('E','PCB_')):continue
            if 'object' not in inputs[ref]:continue
            # In a fixed body's frame: [12+p,113−s] is a subset of [12,113].
            # In a preload body's frame: [12,113−s−p] is a subset.
            # In a carriage body's frame: [12+p+s,113] is a subset.
            # Do not translate the neutral full-length cylinder with the
            # shortening spring: that would falsely extend beyond its seat.
            coefficients=motion(ref,manifest)
            if tuple(coefficients) not in {(0.,0.),(0.,1.),(-1.,0.)}:raise ValueError('Spring subset certificate requires a known source motion role')
            item=pair(env,inputs[ref]['object'],tol,manifest.get('gap_search_mm',2.))
            if item['status']=='CLEAR_AT_NUMERICAL_TOLERANCE':item['status']='CONTINUOUS_CLEARANCE_CERTIFIED'
            rows.append(dict(side=side,target=ref,radius_mm=7.4,envelope_scope='Whole exact shortening spring interval is a subset of neutral [12,113] in each target source motion frame',**item))
    return rows


def service_sweeps(inputs,manifest):
    """Finite declared assembly/tool paths; never imply an unspecified sequence."""
    rows=[]
    for spec in manifest.get('service_sweeps',[]):
        vec=np.asarray(spec['direction'],float);speed=float(np.linalg.norm(vec))
        if speed<1e-12:
            rows.append({'name':spec['name'],'status':'UNCHECKED','reason':'Zero service vector'});continue
        first=vec/speed
        seed=np.array([0.,0.,1.]) if abs(first[2])<.9 else np.array([0.,1.,0.])
        second=np.cross(seed,first);second/=np.linalg.norm(second)
        third=np.cross(first,second)
        rotation=np.stack((first,second,third));matrix=np.column_stack((rotation,np.zeros(3))).tolist()
        moving=spec['moving_refs'];fixed=spec.get('fixed_refs',sorted(set(inputs)-set(moving)-set(spec.get('removed_refs',[]))-SPRINGS))
        shift=np.asarray(spec.get('initial_translation_mm',[0.,0.,0.]),float)
        stroke=spec.get('stroke_mm',0.);preload=spec.get('preload_mm',0.)
        for a in moving:
            for b in fixed:
                row={'name':spec['name'],'pair':[a,b],'prerequisites':spec.get('prerequisites','NOT_SPECIFIED'),
                    'direction':vec.tolist(),'parameter_range_mm':spec.get('range_mm',[0.,10.]),
                    'removed_refs':spec.get('removed_refs',[]),'native_start_stroke_mm':stroke,'native_start_preload_mm':preload}
                try:
                    aa=inputs[a]['object'].translate((shift+[float(motion(a,manifest)@np.array([stroke,preload])),0.,0.]).tolist()).transform(matrix)
                    bb=inputs[b]['object'].translate([float(motion(b,manifest)@np.array([stroke,preload])),0.,0.]).transform(matrix)
                    lo,hi=spec.get('range_mm',[0.,10.])
                    row.update(relative_sweep(aa,bb,lo*speed,hi*speed,manifest.get('volume_tolerance_mm3',.01),manifest.get('minimum_interval_mm',.0625)))
                except Exception as e:row.update(status='UNCHECKED',reason=repr(e))
                rows.append(row)
    return rows


def template():
    expected=sorted(DEVICE)
    return {'schema_version':1,'status':'TEMPLATE_NOT_VALIDATION','native_provenance':{'workspace_url':'PENDING','feature_source_sha256':'PENDING'},
        'assembly':'PENDING_NATIVE_NEUTRAL_STL.zip','feature_source':'PENDING_REVISED_SOURCE.fs','expected_device_refs':expected,
        'expected_electronics_count':53,'volume_tolerance_mm3':.01,'gap_search_mm':2.,'minimum_interval_mm':.0625,
        'ignore_member_patterns':[],'member_ref_overrides':{},'motion_overrides':{},
        'contacts':[{'pair':['H01','H02'],'kind':'exterior_contact','reason':'Spherical load button/pusher contact: no volume overlap permitted'},
                    {'pair':['H01','H12'],'kind':'exterior_contact','reason':'Rear support contact: no volume overlap permitted'},
                    {'pair':['P02','P03'],'kind':'nominal_soft_fit','maximum_intersection_volume_mm3':0.01,'reason':'Set only after exact matching nominal surfaces are independently established; do not grandfather a changed interference'}],
        'sensor':{'ref':'H01','canonical_placed_step':str(ROOT/'review/actual-sensor-cad-2026-10-22/sensor/TE_FX1901_actual_apex_aligned_132_mm.step'),
                  'canonical_sha256':'241c8b522707e9ce3b611db3c783d6c9e3bd6e492175c530d5e9795d9dc98097',
                  'native_assembly_step':'PENDING_NATIVE_ASSEMBLY.step','additional_rigid_transform':np.eye(4).tolist(),'brep_volume_tolerance_mm3':1e-4},
        'native_poses':[{'mode':'dynamic','stroke_mm':s,'preload_mm':p,'assembly':'PENDING_NATIVE_POSE.zip'} for s,p in [(25,0),(27,0),(30,0),(30,2)]]+
                       [{'mode':'isometric','stroke_mm':15-p,'preload_mm':p,'assembly':'PENDING_NATIVE_ISOMETRIC.zip'} for p in (0,2)],
        'dimension_checks':[{'name':'132 mm fixed-frame width','type':'bounds','ref':'P01','component':'extent','axis':1,'expected_mm':132.,'tolerance_mm':.02},
            {'name':'72 mm finger-pocket inner width at X94/Z20','type':'ray_levels','ref':'P04','origin_mm':[94,-200,20],'direction':[0,1,0],'axis':1,'level_indices':[2,1],'expected_mm':72.,'tolerance_mm':.02}],
        'material_and_clearance_probes':[],
        'service_sweeps':[],
        'exact_brep_pairs':[{'pair':['P02','P03'],'maximum_intersection_volume_mm3':1e-6,'reason':'Verify coincident nominal TPU/core fit has no BRep material overlap'}],
        'required_native_pose_keys':['dynamic:25:0','dynamic:27:0','dynamic:30:0','dynamic:30:2','isometric:15:0','isometric:13:2']}


def pose_key(p):return f"{p['mode']}:{p['stroke_mm']:g}:{p['preload_mm']:g}"


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest',type=Path,nargs='?')
    parser.add_argument('--write-template',type=Path)
    parser.add_argument('--output',type=Path,default=HERE/'validation.json')
    parser.add_argument('--static-only',action='store_true',help='Diagnostic only: cannot yield a complete PASS')
    args=parser.parse_args()
    if args.write_template:write(args.write_template,template());return
    if not args.manifest:parser.error('manifest required')
    began=time.monotonic();m=json.loads(args.manifest.read_text())
    report={'status':'RUNNING','scope':'Nominal native solid geometry, no fabricated material/load/fatigue/comfort qualification',
        'validator_sha256':sha(Path(__file__)),'manifest_sha256':sha(args.manifest),'manifest':m,
        'runtime':{p:importlib.metadata.version(p) for p in ['numpy','trimesh','manifold3d','cadquery-ocp']},
        'limitations':['Native exports and source association are operator-declared and hash-bound; this script does not regenerate Onshape.',
            'STL intersection tolerance is numerical, not a permitted design penetration or print clearance.',
            'Actuator continuous certificates depend on the stated FeatureScript kinematics. Native pose/source congruence is separately checked; the actual purchased switch and click force remain unqualified.',
            'Selected wall-ray/probe checks do not establish a global minimum wall or strength.',
            'No hand-volume clearance is inferred from an open scan in a provisional registration. No comfort qualification.',
            'No spring fatigue/coil-bind or load-cell electrical/calibration qualification is established.'],
        'preflight':[],'mesh_inventory':{},'static_pairs':[],'continuous_pairs':[],'native_poses':[],
        'dimension_checks':[],'material_and_clearance_probes':[],'spring_envelopes':[],'service_sweeps':[],'exact_brep_pairs':[]}
    inputs={};initial={}
    try:
        source=Path(m['feature_source']);source_sha=sha(source)
        report['preflight'].append({'name':'Revised feature source identity','sha256':source_sha,'status':'PASS' if source_sha==m['native_provenance']['feature_source_sha256'] else 'FAIL'})
        inputs,ignored=load(m['assembly'],m);initial=identities(inputs)
        report['mesh_inventory']=inventory(inputs);report['ignored_members']=ignored
        missing=set(m['expected_device_refs'])-set(inputs)
        unexpected={r for r in inputs if r not in m['expected_device_refs'] and not r.startswith(('E','PCB_'))}
        invalid={r:v.get('error') for r,v in inputs.items() if 'error' in v and r not in SPRINGS}
        elec=[r for r in inputs if r.startswith(('E','PCB_'))]
        report['preflight'] += [
            {'name':'Complete device references','missing':sorted(missing),'unexpected':sorted(unexpected),'status':'FAIL' if missing or unexpected else 'PASS'},
            {'name':'Closed positive native solids','invalid':invalid,'status':'FAIL' if invalid else 'PASS'},
            {'name':'Unrecognized native members','members':[r for r in ignored if r['reason']=='UNRECOGNIZED'],'status':'FAIL' if any(r['reason']=='UNRECOGNIZED' for r in ignored) else 'PASS'},
            {'name':'Electronics reference inventory','count':len(elec),'expected':m.get('expected_electronics_count',0),'status':'PASS' if len(elec)==m.get('expected_electronics_count',0) else 'FAIL'}]
        report['sensor_identity']=sensor_check(inputs,m)
        report['exact_brep_pairs']=exact_brep_pairs(inputs,m)
        report['static_pairs']=all_pairs(inputs,m)
        print('Static checks complete; nonclear:',[(v['pair'],v['status'],v.get('intersection_volume_mm3')) for v in report['static_pairs'] if v['status'] in ('INTERFERENCE','UNCHECKED')],flush=True)
        write(args.output,report)
        report['dimension_checks']=dimensions(inputs,m)
        report['material_and_clearance_probes']=probes(inputs,m)
        if not args.static_only:
            report['continuous_pairs']=all_pairs(inputs,m,sweeps=True)
            report['spring_envelopes']=spring_envelopes(inputs,m)
            report['service_sweeps']=service_sweeps(inputs,m)
        for pose in m.get('native_poses',[]):
            pr={'key':pose_key(pose),'configuration':pose,'status':'RUNNING'}
            try:
                pi,ig=load(pose['assembly'],m);expected=set(m['expected_device_refs'])
                if pose['mode']=='isometric':expected=(expected-SPRINGS)|{'H140','H141'}
                required=expected|set(elec)
                pr.update(mesh_inventory=inventory(pi),missing=sorted(required-set(pi)),unexpected=sorted(set(pi)-required),ignored_members=ig)
                pr['pairs']=all_pairs(pi,m,pose['stroke_mm'],pose['preload_mm'])
                pr['pose_semantics']=pose_semantics(inputs,pi,pose,m)
                pr['status']='FAIL' if pr['missing'] or pr['unexpected'] or any(v['status']=='INTERFERENCE' for v in pr['pairs']) or any(v['status']=='FAIL' for v in pr['pose_semantics']) else 'CHECKED_NATIVE_POSE'
            except Exception as e:pr.update(status='UNCHECKED',reason=repr(e))
            report['native_poses'].append(pr)
        present={v['key'] for v in report['native_poses'] if v['status']=='CHECKED_NATIVE_POSE'}
        missing_poses=sorted(set(m.get('required_native_pose_keys',[]))-present)
        report['preflight'].append({'name':'Required native articulated/isometric poses','missing':missing_poses,'status':'FAIL' if missing_poses else 'PASS'})
        report['preflight'].append({'name':'Inputs remain unchanged','status':'PASS' if identities(load(m['assembly'],m)[0])==initial and sha(source)==source_sha else 'FAIL'})
    except Exception as e:report['preflight'].append({'name':'Native input availability','status':'UNCHECKED','reason':repr(e)})
    groups=['preflight','static_pairs','continuous_pairs','dimension_checks','material_and_clearance_probes','spring_envelopes','service_sweeps','exact_brep_pairs']
    flat=[v for g in groups for v in report[g]]+[report.get('sensor_identity',{'status':'UNCHECKED'})]
    flat += [v for p in report['native_poses'] for v in p.get('pairs',[])]+[v for p in report['native_poses'] for v in p.get('pose_semantics',[])]+report['native_poses']
    failures=[v for v in flat if v['status'] in ('FAIL','INTERFERENCE')]
    unresolved=[v for v in flat if v['status'] in ('UNCHECKED','UNRESOLVED_NEAR_CONTACT')]
    mesh_rows=[v for g in groups if g!='exact_brep_pairs' for v in report[g]]
    mesh_rows += [v for p in report['native_poses'] for v in p.get('pairs',[])]+[v for p in report['native_poses'] for v in p.get('pose_semantics',[])]+report['native_poses']
    mesh_fail=any(v['status'] in ('FAIL','INTERFERENCE') for v in mesh_rows)
    mesh_unresolved=any(v['status'] in ('UNCHECKED','UNRESOLVED_NEAR_CONTACT') for v in mesh_rows)
    report.update(status='FAIL' if failures else 'INCOMPLETE' if unresolved or args.static_only or not report['continuous_pairs'] else 'NOMINAL_GEOMETRY_CHECKS_PASS',
        nominal_native_mesh_status='FAIL' if mesh_fail else 'INCOMPLETE' if mesh_unresolved or args.static_only or not report['continuous_pairs'] else 'PASS_WITH_EXPLICIT_CONTACT_MODELS',
        step_roundtrip_status='COMPLETE' if report.get('sensor_identity',{}).get('status')=='PASS' and all(v['status']=='PASS' for v in report['exact_brep_pairs']) else 'PENDING_OR_UNRESOLVED',
        failed_checks=len(failures),unresolved_checks=len(unresolved),elapsed_seconds=time.monotonic()-began,
        articulated_continuous_qualification='Nominal source rotating actuator arc; native regenerated pose congruence separately checked',
        manufacture_release='NOT_ISSUED_BY_GEOMETRY_SCRIPT',
        status_counts={s:sum(v['status']==s for v in flat) for s in sorted({v['status'] for v in flat})})
    write(args.output,report)
    print(json.dumps({k:report[k] for k in ['status','failed_checks','unresolved_checks','elapsed_seconds','status_counts']},indent=2))


if __name__=='__main__':main()
