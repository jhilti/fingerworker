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
MOVING = {'P04','H10','P11','H060','H061'}
PRELOAD = set('P05 H050 H051 H12 H01 H02 H13 H180 H181 H190 H191 H20 H23 H240 H241 H242 H243 H250 H251 H252 H253'.split())
SPRINGS = {'H030','H031'}
ARTICULATED = {'H09a','H09b'}
PIVOT=np.array([29.5,-13.1,10.7])
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


def canonical_triangle_sha256(mesh):
    """Exact native triangle coordinates, ignoring facet/vertex order only.

    No rounding, welding, repair, scaling or geometric tolerance is used.
    Positive solid validity is checked separately. Normalize signed zero only.
    """
    triangles=np.asarray(mesh.triangles,float).copy();triangles[triangles==0.]=0.
    order=np.lexsort((triangles[:,:,2],triangles[:,:,1],triangles[:,:,0]),axis=1)
    triangles=np.take_along_axis(triangles,order[:,:,None],axis=1)
    flat=triangles.reshape(-1,9);order=np.lexsort(tuple(flat[:,i] for i in range(8,-1,-1)))
    return hashlib.sha256(flat[order].astype('<f8').tobytes()).hexdigest()


def canonical_planar_boundary_sha256(mesh):
    """Exact coplanar boundary edges, cancelling internal triangulation diagonals.

    Fractions preserve every stored STL coordinate exactly. This narrowly
    supports the four unchanged rectangular TPU return pads, whose CAD face
    triangulation may change after a rigid source-coordinate relocation.
    There is no rounding, geometric tolerance, scaling or re-meshing.
    """
    from fractions import Fraction as F
    from collections import defaultdict
    planes={}
    def point(v):return tuple(F(float(x)) for x in v)
    def sub(a,b):return tuple(x-y for x,y in zip(a,b))
    for triangle in mesh.triangles:
        a,b,c=map(point,triangle);u=sub(b,a);w=sub(c,a)
        n=(u[1]*w[2]-u[2]*w[1],u[2]*w[0]-u[0]*w[2],u[0]*w[1]-u[1]*w[0])
        first=next((x for x in n if x),None)
        if first is None:raise ValueError('Degenerate triangle cannot prove planar boundary identity')
        d=-sum(x*y for x,y in zip(n,a));key=(tuple(x/first for x in (*n,d)),1 if first>0 else -1)
        edges=planes.setdefault(key,defaultdict(int))
        for x,y in ((a,b),(b,c),(c,a)):
            edge=tuple(sorted((x,y)));edges[edge]+=1 if edge==(x,y) else -1
    canonical=[]
    for plane,edges in planes.items():
        boundary=sorted((edge,count) for edge,count in edges.items() if count)
        if any(abs(count)!=1 for _,count in boundary):raise ValueError('Non-simple coplanar edge multiplicity')
        canonical.append((plane,boundary))
    return hashlib.sha256(repr(sorted(canonical)).encode()).hexdigest()


def native_float32_box_identity(ref,current,baseline,manifest,translation):
    """Four return pads only: exact STEP preservation plus one-ULP STL boxes.

    An exact source shift can change float32 quantization at different absolute
    coordinates. This is not an exact triangle-coordinate identity claim.
    """
    from OCP.STEPControl import STEPControl_Reader
    from OCP.TopExp import TopExp_Explorer
    from OCP.TopAbs import TopAbs_SOLID
    from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
    from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut
    from OCP.BRepGProp import BRepGProp
    from OCP.GProp import GProp_GProps
    from OCP.gp import gp_Trsf,gp_Vec
    assert ref in {'P070a','P070b','P071a','P071b'} and translation==[5.,0.,0.]
    bi_path=ROOT/'review/flat132-switch-fit-2026-10-23/validation/native-step-inventory.json'
    ni_path=HERE/'native-step-inventory.json';bi=json.loads(bi_path.read_text());ni=json.loads(ni_path.read_text())
    assert ni['status']==bi['status']=='PASS'
    for inventory,archive in [(ni,manifest['assembly']),(bi,manifest['baseline_native_comparison']['assembly'])]:
        assert sha(inventory['native_step'])==inventory['native_step_sha256']
        assert sha(archive)==inventory['native_stl_archive_sha256']
    assert sha(manifest['sensor']['native_assembly_step'])==ni['native_step_sha256']
    def get(inventory):
        reader=STEPControl_Reader();assert str(reader.ReadFile(inventory['native_step'])).endswith('RetDone');reader.TransferRoots()
        ex=TopExp_Explorer(reader.OneShape(),TopAbs_SOLID);solids=[]
        while ex.More():solids.append(ex.Current());ex.Next()
        match=inventory['native_part_correspondence'][ref];assert match['status']=='PASS' and len(match['candidates'])==1
        return solids[match['candidates'][0]['solid_index']],inventory['solid_inventory'][match['candidates'][0]['solid_index']]['bounds_mm']
    first,first_bounds=get(ni);second,second_bounds=get(bi)
    tr=gp_Trsf();tr.SetTranslation(gp_Vec(*translation));first=BRepBuilderAPI_Transform(first,tr,True).Shape()
    def volume(shape):
        prop=GProp_GProps();BRepGProp.VolumeProperties_s(shape,prop);return abs(float(prop.Mass()))
    xor=volume(BRepAlgoAPI_Cut(first,second).Shape())+volume(BRepAlgoAPI_Cut(second,first).Shape())
    evidence=[]
    for mesh,box in [(current,first_bounds),(baseline,second_bounds)]:
        # current supplied here is the original untranslated native mesh.
        box=np.array(box,float);limits=np.abs(np.spacing(box.astype(np.float32))).astype(float)
        delta=np.abs(mesh.bounds-box)
        coords=[np.unique(mesh.vertices[:,i]) for i in range(3)]
        rectangular=(len(mesh.vertices)==8 and len(mesh.faces)==12 and all(len(c)==2 for c in coords) and len(set(map(tuple,mesh.vertices)))==8)
        exact_box=md.Manifold.cube(mesh.extents.tolist()).translate(mesh.bounds[0].tolist())
        box_error=(solid(mesh)-exact_box).volume()+(exact_box-solid(mesh)).volume()
        evidence.append({'maximum_native_to_step_bound_error_mm':float(delta.max()),'per_bound_float32_ULP_mm':limits.tolist(),'all_bounds_within_one_float32_ULP':bool(np.all(delta<=limits+1e-12)),'eight_vertex_twelve_triangle_rectangular_box':rectangular,'mesh_box_symmetric_difference_mm3':box_error})
    passed=xor<=1e-9 and all(x['all_bounds_within_one_float32_ULP'] and x['eight_vertex_twelve_triangle_rectangular_box'] and abs(x['mesh_box_symmetric_difference_mm3'])<=1e-9 for x in evidence)
    return {'status':'PASS' if passed else 'FAIL','criterion':'Exact native STEP symmetric difference after declared5mm shift is zero; each native STL is the matching8-vertex rectangular box within one coordinate float32 ULP. No mesh rounding, shape waiver or collision-tolerance change.','exact_step_symmetric_difference_mm3':xor,'native_box_checks':evidence,'current_step_sha256':ni['native_step_sha256'],'baseline_step_sha256':bi['native_step_sha256']}


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
    convex configuration polygon under their relative displacement is exactly [start,stop].
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


def partitioned_relative_sweep(a,b,start,stop,tol,minimum_interval,spec,contact=None):
    """A complete union of transverse slabs; every possible intersection is checked.

    Pure X translation leaves Y/Z unchanged. Partitioning both solids along a
    transverse axis therefore preserves and covers every possible intersection,
    including the endpoint planes that a whole-body convex hull can obscure.
    """
    axis=int(spec['axis'])
    if axis not in (1,2):raise ValueError('Relative-X sweep partition must be transverse')
    ab,bb=bounds(a),bounds(b)
    edges=sorted(set([min(ab[0,axis],bb[0,axis])]+list(map(float,spec['planes_mm']))+[max(ab[1,axis],bb[1,axis])]))
    result={'relative_x_range_mm':[start,stop],'partition_axis':axis,'partition_edges_mm':edges,
        'method':'Complete union of exact transverse slabs; each slab uses the strict continuous relative-X certificate',
        'status':'UNCHECKED','slabs':[]}
    for lo,hi in zip(edges[:-1],edges[1:]):
        parts=[]
        for obj in (a,b):
            normal=[0.,0.,0.];normal[axis]=1.;obj=obj.trim_by_plane(normal,float(lo))
            normal[axis]=-1.;obj=obj.trim_by_plane(normal,float(-hi));parts.append(obj)
        if any(obj.is_empty() for obj in parts):
            row={'status':'CONTINUOUS_CLEARANCE_CERTIFIED','method':'One side has no material in this transverse slab','maximum_sampled_volume_mm3':0.}
        else:row=relative_sweep(parts[0],parts[1],start,stop,tol,minimum_interval,contact)
        result['slabs'].append(dict(transverse_interval_mm=[lo,hi],**row))
    statuses={row['status'] for row in result['slabs']}
    result['status']='INTERFERENCE' if 'INTERFERENCE' in statuses else 'UNCHECKED' if 'UNCHECKED' in statuses else 'UNRESOLVED_NEAR_CONTACT' if 'UNRESOLVED_NEAR_CONTACT' in statuses else 'COMPLETE_TRANSVERSE_PARTITION_CONTINUOUS_CLEARANCE_CERTIFIED'
    result['maximum_sampled_volume_mm3']=max(row.get('maximum_sampled_volume_mm3',row.get('intersection_volume_mm3',0.)) for row in result['slabs'])
    return result


def convex_cover_sweep(a,b,start,stop,tol,minimum,specs,initial=None,transform=None):
    """Verify a complete conservative convex cover, then sweep every cover.

    Every native triangle must have all3 vertices inside one convex analytic
    cylinder; its complete triangle then lies inside that cylinder. A separate
    Boolean also checks complete solid inclusion. No input material is removed.
    Cylinders use a tiny outward radial margin and circumscribed polygon, so
    their swept hulls conservatively bound the complete moving material.
    """
    mesh=a.to_mesh64();verts=np.asarray(mesh.vert_properties)[:,:3];faces=np.asarray(mesh.tri_verts)
    covered=np.zeros(len(faces),bool);parts=[]
    for spec in specs:
        if spec['type']!='cylinder_z':raise ValueError('Only reviewed vertical clamp cylinder covers supported')
        inside=((verts[:,0]-spec['x_mm'])**2+(verts[:,1]-spec['y_mm'])**2<=spec['radius_mm']**2)&(verts[:,2]>=spec['start_z_mm'])&(verts[:,2]<=spec['end_z_mm'])
        covered|=np.all(inside[faces],axis=1);parts.append(probe_object(spec))
    union=parts[0]
    for part in parts[1:]:union=union+part
    missing=max(0.,float((a-union).volume()));uncovered=int((~covered).sum())
    result={'relative_x_range_mm':[start,stop],'status':'UNCHECKED','method':'Complete conservative convex-cylinder cover, each swept against full target; all native triangles and full solid inclusion independently checked',
        'uncovered_native_triangles':uncovered,'uncovered_input_volume_mm3':missing,'input_coverage_volume_tolerance_mm3':1e-8,'cover_specs':specs,'cover_sweeps':[]}
    if uncovered or missing>1e-8:return result
    for part in parts:
        if initial is not None:part=part.translate(initial)
        if transform is not None:part=part.transform(transform)
        result['cover_sweeps'].append(relative_sweep(part,b,start,stop,tol,minimum))
    rows=result['cover_sweeps'];states={r['status'] for r in rows}
    upper=missing+sum(max(0.,r.get('complete_swept_envelope_intersection_upper_bound_mm3',r.get('intersection_volume_mm3',0.))) for r in rows)
    result['complete_cover_overlap_upper_bound_mm3']=upper
    result['maximum_sampled_volume_mm3']=max([r.get('maximum_sampled_volume_mm3',r.get('intersection_volume_mm3',0.)) for r in rows]+[0.])
    result['status']='INTERFERENCE' if 'INTERFERENCE' in states else 'UNCHECKED' if 'UNCHECKED' in states else 'UNRESOLVED_NEAR_CONTACT' if 'UNRESOLVED_NEAR_CONTACT' in states or upper>tol else 'COMPLETE_CONSERVATIVE_CONVEX_COVER_CONTINUOUS_CLEARANCE_CERTIFIED'
    return result


def configured_relative_sweep(a,b,start,stop,tol,minimum_interval,manifest,refs,contact=None):
    cover=next((item for item in manifest.get('continuous_convex_moving_covers',[]) if set(item['pair'])==set(refs)),None)
    if cover:
        if refs[0]==cover['moving_ref']:return convex_cover_sweep(a,b,start,stop,tol,minimum_interval,cover['covers'])
        return convex_cover_sweep(b,a,-stop,-start,tol,minimum_interval,cover['covers'])
    spec=next((item for item in manifest.get('continuous_transverse_partitions',[]) if set(item['pair'])==set(refs)),None)
    return partitioned_relative_sweep(a,b,start,stop,tol,minimum_interval,spec,contact) if spec else relative_sweep(a,b,start,stop,tol,minimum_interval,contact)


def motion(ref,manifest):
    override=manifest.get('motion_overrides',{}).get(ref)
    if override is not None:return np.asarray(override,float)
    return np.array([-1. if ref in MOVING else 0.,1. if ref in PRELOAD else 0.,0.])


def configuration_vertices(manifest):
    vertices=np.asarray(manifest['configuration_domain_vertices_user_preload_trim_mm'],float)
    if vertices.ndim!=2 or vertices.shape[1]!=3 or len(vertices)<4:raise ValueError('Invalid3D user/preload/trim domain vertices')
    return vertices


def effective_actuator_travel(stroke,preload,manifest,trim=0.):
    coefficients=np.asarray(manifest['actuator_effective_travel_coefficients'],float)
    return float(coefficients@np.asarray([stroke,preload,trim],float))


def clipped_vertices(vertices,normal,limit):
    """Exact convex-polytope halfspace intersection vertices plus interior points.

    Intersections of all crossing vertex pairs include every crossing edge.
    Extra intersections are interior to the original convex polytope and cannot
    change any subsequent linear extrema. No axis-aligned domain enlargement.
    """
    vertices=np.asarray(vertices,float);normal=np.asarray(normal,float)
    distances=vertices@normal-limit;out=[x for x,d in zip(vertices,distances) if d<=1e-12]
    for i in range(len(vertices)):
        for j in range(i):
            if distances[i]*distances[j]<0.:
                f=distances[i]/(distances[i]-distances[j]);out.append(vertices[i]+f*(vertices[j]-vertices[i]))
    return np.unique(np.asarray(out),axis=0) if out else np.empty((0,vertices.shape[1]))


def clip_polygon(poly,axis,level,less=True):
    """Ordered convex polygon clipped by one exact coordinate halfspace."""
    out=[];n=len(poly)
    for i in range(n):
        a=np.asarray(poly[i]);b=np.asarray(poly[(i+1)%n])
        da=(a[axis]-level)*(1 if less else -1);db=(b[axis]-level)*(1 if less else -1)
        ia=da<=1e-12;ib=db<=1e-12
        if ia:out.append(a)
        if ia!=ib:
            f=da/(da-db);out.append(a+f*(b-a))
    return np.asarray(out)


def actuator_angle(stroke):
    dx=min(37.4,64-stroke-2.4)-29.5
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
    """Strict3D certificate for u+p<=30 and trim e in[-.8,.8].

    Set Q=u+p-e. In the active arc Q>=24.2, the exact Q/e polygon is
    [(24.2,-.8),(30.8,-.8),(29.2,.8),(24.2,.8)], times p in[0,2].
    It enforces Q+e<=30; forbidden independent corners are never sampled.
    The inactive part is clipped directly from the original8-vertex prism.
    """
    tol=manifest.get('volume_tolerance_mm3',.01);minimum=manifest.get('minimum_interval_mm',.0625)
    domain=configuration_vertices(manifest)
    row={'pair':[ref,target],'status':'UNCHECKED','user_preload_trim_domain_vertices_mm':domain.tolist(),
         'effective_actuator_Q_range_mm':[-.8,30.8],
         'model':'Q=u+p-e; fixed pivot29.5/-13.1/10.7; roller centerX=min37.4,61.6-Q; approximate source actuator only',
         'certified_prisms':0,'intersections':[],'unresolved_prisms':[],'samples':[]}
    try:
        expected=np.array([[u,p,e] for u,p in [(0,0),(30,0),(28,2),(0,2)] for e in [-.8,.8]],float)
        if set(map(tuple,domain))!=set(map(tuple,expected)):raise ValueError('Certificate requires exact declared u/p/trim prism')
        if manifest['actuator_effective_travel_coefficients']!=[1.,1.,-1.]:raise ValueError('Certificate requires Q=u+p-e')
        aa,bb=inputs[ref]['object'],inputs[target]['object'];vertices=inputs[ref]['mesh'].vertices
        original=motion(target,manifest)
        # u=Q-p+e; targetX=mu*Q+(mp-mu)*p+(me+mu)*e.
        mb=np.array([original[0],original[1]-original[0],original[2]+original[0]])
        bbox=bounds(bb)
        if target in ARTICULATED:
            contact=next((v for v in manifest.get('contacts',[]) if set(v['pair'])=={ref,target}),None)
            if not contact:raise ValueError('Explicit source actuator-joint declaration required')
            row.update(classify(pair(aa,bb,tol,2.),contact,tol))
            row.update(method='Both illustrative actuator pieces share identical Q rotation; joint volume invariant',certified_prisms=1)
            return row
        if ref=='H09b' and target=='P11':
            center=np.array([37.4,-13.1+np.sqrt(LEVER_LENGTH**2-(37.4-29.5)**2),10.7])
            radial=np.linalg.norm(vertices[:,:2]-center[:2],axis=1)
            # Exact complete target Z slab that can meet the rotating roller.
            # The upper forward boss starts13.2, above roller top12.3.
            z0,z1=vertices[:,2].min(),vertices[:,2].max()
            clipped=bb.trim_by_plane([0,0,1],float(z0)).trim_by_plane([0,0,-1],float(-z1))
            if radial.max()>2.40001 or bounds(clipped)[0,0]<63.99999 or not np.array_equal(original,[-1.,-1.,1.]):
                raise ValueError('Native roller/shoe Z-slab witness differs from source Q datum')
            row.update(status='CONTINUOUS_CLEARANCE_CERTIFIED',certified_prisms=1,
                method='Complete roller-Z slab of P11 has frontX64-Q. Roller maxX<=min39.8,64-Q over Q[-.8,30.8]. All excluded P11 material is vertically separated; no overlap waiver.',
                target_clipped_Z_range_mm=[z0,z1],target_neutral_clipped_front_X_mm=float(bounds(clipped)[0,0]),maximum_sampled_volume_mm3=0.)
            return row
        lower=clipped_vertices(domain,[1.,1.,-1.],24.2)
        offsets=-lower@original
        lowcert=relative_sweep(aa,bb,float(offsets.min()),float(offsets.max()),tol,minimum)
        row['stationary_actuator_domain_vertices_u_p_e_mm']=lower.tolist();row['stationary_certificate']=lowcert
        if lowcert['status'] in ('INTERFERENCE','UNCHECKED','UNRESOLVED_NEAR_CONTACT'):
            row.update(status=lowcert['status'],reason='Stationary Q region not certified');return row
        row['certified_prisms']+=1
        polygon=np.array([[24.2,-.8],[30.8,-.8],[29.2,.8],[24.2,.8]])
        row['active_Q_e_polygon_mm']=polygon.tolist();row['active_preload_range_mm']=[0.,2.]
        radius=float(np.linalg.norm(vertices-PIVOT,axis=1).max());samples={}
        def sample(Q,p,e,search):
            key=(float(Q),float(p),float(e))
            if key not in samples or samples[key]['gap_search_cap_mm']<search:
                obj=aa.transform(actuator_transform(Q).tolist()).translate([-float(mb@np.array([Q,p,e])),0.,0.])
                result=pair(obj,bb,tol,search)
                samples[key]={'effective_Q_mm':Q,'user_stroke_mm':Q-p+e,'preload_mm':p,'trim_mm':e,**result}
                if result['intersection_volume_mm3']>tol:row['intersections'].append(samples[key])
            return samples[key]
        def certify(poly,p0,p1):
            if len(poly)<3:return
            q0,q1=poly[:,0].min(),poly[:,0].max();e0,e1=poly[:,1].min(),poly[:,1].max()
            projected=np.array([-float(mb@np.array([Q,p,e])) for Q,e in poly for p in (p0,p1)])
            ab=rotational_bounds(vertices,float(q0),float(q1));ab[0,0]+=projected.min();ab[1,0]+=projected.max()
            if separated(ab,bbox):row['certified_prisms']+=1;return
            Q,e=poly.mean(0);p=(p0+p1)/2
            angular=max(abs(actuator_angle(Q)-actuator_angle(q0)),abs(actuator_angle(q1)-actuator_angle(Q)))
            offset=-float(mb@np.array([Q,p,e]));variation=max(abs(projected.min()-offset),abs(projected.max()-offset))
            travel=2*radius*np.sin(angular/2)+variation
            value=sample(Q,p,e,travel+.01)
            if value['intersection_volume_mm3']>tol:return
            if value['minimum_gap_mm']>travel+1e-5:row['certified_prisms']+=1;return
            if q1-q0<=minimum and (p1-p0<=minimum or abs(mb[1])<1e-12) and (e1-e0<=minimum or abs(mb[2])<1e-12):
                row['unresolved_prisms'].append({'Q_e_polygon_mm':poly.tolist(),'preload_range_mm':[p0,p1],'midpoint_gap_mm':value['minimum_gap_mm']});return
            weights=[(q1-q0)*(1+radius*.067+abs(mb[0])),(p1-p0)*abs(mb[1]),(e1-e0)*abs(mb[2])]
            axis=int(np.argmax(weights))
            if axis==1:
                certify(poly,p0,p);certify(poly,p,p1)
            else:
                k=0 if axis==0 else 1;mid=(poly[:,k].min()+poly[:,k].max())/2
                for less in (True,False):certify(clip_polygon(poly,k,float(mid),less),p0,p1)
        for Q,e in polygon:
            for p in (0.,2.):sample(float(Q),p,float(e),.01)
        certify(polygon,0.,2.)
        row['samples']=list(samples.values())
        row['maximum_sampled_volume_mm3']=max([x['intersection_volume_mm3'] for x in samples.values()]+[lowcert.get('maximum_sampled_volume_mm3',lowcert.get('intersection_volume_mm3',0.))])
        row['status']='INTERFERENCE' if row['intersections'] else 'UNRESOLVED_NEAR_CONTACT' if row['unresolved_prisms'] else 'CONTINUOUS_CLEARANCE_CERTIFIED'
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
                    corners=[dm@point for point in configuration_vertices(manifest)]
                    preferred=next((item['moving_ref'] for item in manifest.get('continuous_preferred_moving_ref_pairs',[]) if set(item['pair'])=={a,b}),None)
                    if preferred==b or (preferred is None and b in MOVING and a not in MOVING):
                        row.update(configured_relative_sweep(bb,aa,float(-max(corners)),float(-min(corners)),tol,manifest.get('minimum_interval_mm',.0625),manifest,[b,a],contact))
                        row['pair']=[b,a];row['relative_x_coefficients_stroke_preload']=(-dm).tolist()
                    else:
                        row.update(configured_relative_sweep(aa,bb,float(min(corners)),float(max(corners)),tol,manifest.get('minimum_interval_mm',.0625),manifest,[a,b],contact))
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


def dimensions(inputs,manifest,baseline_inputs=None):
    rows=[]
    for spec in manifest.get('dimension_checks',[]):
        row=dict(spec)
        try:
            mesh=inputs[spec['ref']]['mesh']
            if spec['type']=='bounds':
                value=float({'minimum':mesh.bounds[0],'maximum':mesh.bounds[1],'extent':mesh.extents,'center':mesh.bounds.mean(0)}[spec['component']][spec['axis']])
            elif spec['type']=='bounds_difference_from_baseline':
                if baseline_inputs is None:baseline_inputs,_=load(manifest['baseline_native_comparison']['assembly'],manifest)
                original=baseline_inputs[spec['ref']]['mesh']
                current_value={'minimum':mesh.bounds[0],'maximum':mesh.bounds[1],'extent':mesh.extents,'center':mesh.bounds.mean(0)}[spec['component']][spec['axis']]
                baseline_value={'minimum':original.bounds[0],'maximum':original.bounds[1],'extent':original.extents,'center':original.bounds.mean(0)}[spec['component']][spec['axis']]
                row['baseline_value_mm']=float(baseline_value);row['current_value_mm']=float(current_value)
                value=float(current_value-baseline_value)
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
    if spec['type'] in ('cylinder_x','cylinder_z'):
        # Conservative circumscribed cylinder: suitable for empty-clearance
        # probes. For material inclusion, explicitly choose inscribed=True.
        n=128;r=spec['radius_mm']/(1. if spec.get('inscribed') else np.cos(np.pi/n))
        if spec['type']=='cylinder_z':return md.Manifold.cylinder(spec['end_z_mm']-spec['start_z_mm'],r,r,n).translate([spec['x_mm'],spec['y_mm'],spec['start_z_mm']])
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
    rows=[];stroke,preload,trim=pose['stroke_mm'],pose['preload_mm'],pose.get('trim_mm',0.)
    legal=stroke>=0. and 0.<=preload<=2. and stroke+preload<=30.+1e-9 and -.8-1e-9<=trim<=.8+1e-9
    rows.append({'name':'Native pose inside declared stop-limited operating domain','stroke_mm':stroke,'preload_mm':preload,'status':'PASS' if legal else 'FAIL'})
    for ref in sorted(set(neutral)&set(posed)-SPRINGS-ARTICULATED):
        row={'name':'Native rigid pose / '+ref,'ref':ref}
        try:
            delta=float(motion(ref,manifest)@np.array([stroke,preload,trim]))
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
            effective=effective_actuator_travel(stroke,preload,manifest,trim)
            expected=neutral[ref]['object'].transform(actuator_transform(effective).tolist());actual=posed[ref]['object']
            error=float((expected-actual).volume()+(actual-expected).volume())
            row.update(symmetric_difference_mm3=error,effective_travel_q_mm=effective,rotation_radians=actuator_angle(effective)-actuator_angle(0.),
                status='PASS' if error<=manifest.get('native_pose_mesh_xor_tolerance_mm3',.1) else 'FAIL')
        except Exception as e:row.update(status='UNCHECKED',reason=repr(e))
        rows.append(row)
    def scalar(name,value,expected,tol=.02):
        rows.append({'name':name,'measured_mm':float(value),'expected_mm':float(expected),'tolerance_mm':tol,
                     'status':'PASS' if abs(value-expected)<=tol else 'FAIL'})
    try:
        effective=effective_actuator_travel(stroke,preload,manifest,trim)
        roller_x=min(37.4,64-effective-2.4)
        roller_y=-13.1+np.sqrt(3.1**2+16.7**2-(roller_x-29.5)**2)
        scalar('Source articulated roller center X',posed['H09b']['mesh'].bounds[:,0].mean(),roller_x)
        scalar('Source articulated roller center Y',posed['H09b']['mesh'].bounds[:,1].mean(),roller_y)
        for ref in ('H050','H051'):
            scalar(ref+' fixed seat spring face X',posed[ref]['mesh'].bounds[1,0],12+preload)
        for ref in ('H060','H061'):
            scalar(ref+' moving seat spring face X',posed[ref]['mesh'].bounds[0,0],108-stroke)
        if pose['mode']=='isometric':
            scalar('Native isometric user stroke',stroke,manifest['isometric_user_stroke_plus_preload_mm']-preload)
            for ref,side in [('H140',-1),('H141',1)]:
                mb=posed[ref]['mesh'].bounds
                scalar(ref+' lock-sleeve start X',mb[0,0],12+preload)
                scalar(ref+' lock-sleeve end X',mb[1,0],108-stroke)
                scalar(ref+' lock-sleeve length',mb[1,0]-mb[0,0],manifest['isometric_sleeve_length_mm'])
                scalar(ref+' lock-sleeve center Y',mb[:,1].mean(),51*side)
    except Exception as e:rows.append({'name':'Actual articulated / isometric datums','status':'UNCHECKED','reason':repr(e)})
    return rows


def spring_envelopes(inputs,manifest):
    """Conservative nominal annular coil occupancy over the complete3D prism.

    Source outer radius<=7.4 and inner radius>=5.25 for either bought spring.
    An outer circumscribed7.4 polygon minus inner inscribed5.24 polygon encloses
    every nominal source wire. Coil free-length/rate/OD tolerances remain unknown.
    Linear endpoint extrema are exact over all8 operating-domain vertices.
    """
    rows=[];tol=manifest.get('volume_tolerance_mm3',.01);domain=configuration_vertices(manifest)
    for side in (-1,1):
        for ref in sorted(inputs):
            if ref in SPRINGS or ref in ARTICULATED or 'object' not in inputs[ref]:continue
            m=motion(ref,manifest)
            starts=12.+domain@np.array([0.,1.,0.])-domain@m
            ends=108.-domain@np.array([1.,0.,0.])-domain@m
            lo,hi=float(starts.min()),float(ends.max())
            base={'type':'cylinder_x','start_x_mm':lo,'end_x_mm':hi,'y_mm':51.*side,'z_mm':18.}
            outer=probe_object(dict(base,radius_mm=7.4));inner=probe_object(dict(base,radius_mm=5.24,inscribed=True));env=outer-inner
            item=pair(env,inputs[ref]['object'],tol,manifest.get('gap_search_mm',2.))
            if item['status']=='CLEAR_AT_NUMERICAL_TOLERANCE':item['status']='CONTINUOUS_CLEARANCE_CERTIFIED'
            rows.append(dict(side=side,target=ref,outer_radius_mm=7.4,inner_radius_mm=5.24,target_frame_axial_envelope_mm=[lo,hi],envelope_scope='Conservative annular occupancy enclosing both nominal bought-spring source wires over full u/p/e domain; not coil-bind or fatigue proof',**item))
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
        stroke=spec.get('stroke_mm',0.);preload=spec.get('preload_mm',0.);trim=spec.get('trim_mm',0.)
        for a in moving:
            for b in fixed:
                row={'name':spec['name'],'pair':[a,b],'prerequisites':spec.get('prerequisites','NOT_SPECIFIED'),
                    'direction':vec.tolist(),'parameter_range_mm':spec.get('range_mm',[0.,10.]),
                    'removed_refs':spec.get('removed_refs',[]),'native_start_stroke_mm':stroke,'native_start_preload_mm':preload}
                try:
                    aa=inputs[a]['object'].translate((shift+[float(motion(a,manifest)@np.array([stroke,preload,trim])),0.,0.]).tolist()).transform(matrix)
                    bb=inputs[b]['object'].translate([float(motion(b,manifest)@np.array([stroke,preload,trim])),0.,0.]).transform(matrix)
                    lo,hi=spec.get('range_mm',[0.,10.])
                    cover=spec.get('moving_convex_cover')
                    if cover and a==cover['moving_ref']:
                        initial=(shift+[float(motion(a,manifest)@np.array([stroke,preload,trim])),0.,0.]).tolist()
                        row.update(convex_cover_sweep(inputs[a]['object'],bb,lo*speed,hi*speed,manifest.get('volume_tolerance_mm3',.01),manifest.get('minimum_interval_mm',.0625),cover['covers'],initial,matrix))
                    else:row.update(relative_sweep(aa,bb,lo*speed,hi*speed,manifest.get('volume_tolerance_mm3',.01),manifest.get('minimum_interval_mm',.0625)))
                except Exception as e:row.update(status='UNCHECKED',reason=repr(e))
                rows.append(row)
    return rows


def template():
    return {'schema_version':2,'status':'TEMPLATE_NOT_VALIDATION','instruction':'Use prepare_manifest.py to bind all R5 inputs,53 device parts,source/hash,8-vertex3D prism and four additional native poses. A hand-written incomplete template cannot qualify the device.'}


def pose_key(p):return f"{p['mode']}:{p['stroke_mm']:g}:{p['preload_mm']:g}:{p.get('trim_mm',0.):g}"


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
            'Actuator continuous certificates depend on manual P11 shoe reset after each preload change, trim calibration and H10 clamping, plus the stated approximate FeatureScript kinematics. Native pose/source congruence is separately checked; the actual purchased switch and click force remain unqualified.',
            'Selected wall-ray/probe checks do not establish a global minimum wall or strength.',
            'No hand-volume clearance is inferred from an open scan in a provisional registration. No comfort qualification.',
            'No spring fatigue/coil-bind or load-cell electrical/calibration qualification is established.'],
        'preflight':[],'mesh_inventory':{},'static_pairs':[],'continuous_pairs':[],'native_poses':[],
        'dimension_checks':[],'material_and_clearance_probes':[],'spring_envelopes':[],'service_sweeps':[],'exact_brep_pairs':[]}
    inputs={};initial={}
    try:
        source=Path(m['feature_source']);source_sha=sha(source)
        report['preflight'].append({'name':'Revised feature source identity','sha256':source_sha,'status':'PASS' if source_sha==m['native_provenance']['feature_source_sha256'] else 'FAIL'})
        if m['native_provenance'].get('dynamic_mode_equivalence'):
            from certify_dynamic_mode_equivalence import proof
            spec=m['native_provenance']['dynamic_mode_equivalence'];certificate_path=Path(spec['certificate'])
            certificate=json.loads(certificate_path.read_text());recomputed=proof()
            expected_origins=m['native_provenance']['native_export_origins'];origin_checks=[]
            required={m['assembly']:False,m['sensor']['native_assembly_step']:False}
            required.update({p['assembly']:p['mode']=='isometric' for p in m['native_poses']})
            for path,iso in required.items():
                item=expected_origins.get(path,{})
                if iso:valid=(item.get('original_source_sha256')==source_sha and item.get('isometricLock') is True and item.get('sha256')==sha(path))
                else:valid=(item==certificate['native_export_origins'].get(path) and item.get('isometricLock') is False and item.get('sha256')==sha(path))
                origin_checks.append({'path':path,'isometricLock':iso,'original_source_sha256':item.get('original_source_sha256'),'status':'PASS' if valid else 'FAIL'})
            good=(certificate==recomputed and sha(certificate_path)==spec['certificate_sha256'] and all(x['status']=='PASS' for x in origin_checks))
            report['preflight'].append({'name':'Exact mode-conditioned ISO81 source equivalence and honest native export origins','certificate_sha256':sha(certificate_path),'exact_inverse_prior_source_sha256':certificate['exact_inverse_source_sha256'],'proof_mode':'isometricLock=false only; ISO81 native export must originate from final source','native_export_origin_checks':origin_checks,'status':'PASS' if good else 'FAIL'})
        if m['native_provenance'].get('source_geometry_equivalence'):
            spec=m['native_provenance']['source_geometry_equivalence'];certificate_path=Path(spec['certificate'])
            certificate=json.loads(certificate_path.read_text());current=source.read_text()
            exact_new=certificate['exact_single_replacement_new'];exact_old=certificate['exact_single_replacement_old']
            count=current.count(exact_new)
            reverse_sha=hashlib.sha256(current.replace(exact_new,exact_old,1).encode()).hexdigest() if count==1 else None
            good=(sha(certificate_path)==spec['certificate_sha256'] and source_sha==certificate['final_source_sha256'] and
                  reverse_sha==certificate['prior_source_sha256'] and count==1 and
                  certificate['coordinate_or_geometry_expression_changes'] is False and certificate['validation_domain_extension'] is False)
            report['preflight'].append({'name':'Prior STEP source differs only in the explicit UI roundoff rejection guard',
                'certificate':str(certificate_path),'certificate_sha256':sha(certificate_path),
                'final_source_sha256':source_sha,'exact_reversed_prior_source_sha256':reverse_sha,
                'expected_prior_source_sha256':certificate['prior_source_sha256'],
                'proof_domain':'EXACT stroke>=0, preload0..2, stroke+preload<=30; not extended by guard tolerance',
                'status':'PASS' if good else 'FAIL'})
        if m.get('native_export_files_sha256'):
            expected_files={m['assembly'],m['sensor']['native_assembly_step']}|{pose['assembly'] for pose in m.get('native_poses',[])}
            recorded=m['native_export_files_sha256'];mismatches=[]
            for path,expected_hash in recorded.items():
                if not Path(path).is_file() or sha(path)!=expected_hash:mismatches.append(path)
            report['preflight'].append({'name':'Complete hash-bound native export files',
                'missing_hash_records':sorted(expected_files-set(recorded)),
                'mismatching_or_missing_files':mismatches,'files_sha256':recorded,
                'status':'PASS' if not mismatches and expected_files<=set(recorded) else 'FAIL'})
        inputs,ignored=load(m['assembly'],m);initial=identities(inputs)
        report['mesh_inventory']=inventory(inputs);report['ignored_members']=ignored
        if m.get('baseline_native_comparison'):
            spec=m['baseline_native_comparison'];baseline_path=Path(spec['assembly'])
            baseline,baseline_ignored=load(baseline_path,m)
            changed=sorted(r for r in set(inputs)&set(baseline) if inputs[r]['sha256']!=baseline[r]['sha256'])
            expected=set(spec['only_changed_refs']);order_only=[];order_evidence=[]
            order_refs=spec.get('permitted_triangle_order_only_refs',[])
            if order_refs=='ALL_EXCEPT_EXPECTED_GEOMETRY_CHANGES':order_refs=sorted(set(baseline)-expected)
            for ref in order_refs:
                if ref in changed or ref in spec.get('new_to_baseline_rigid_translation_mm',{}):
                    comparison=inputs[ref]['mesh'].copy();translation=spec.get('new_to_baseline_rigid_translation_mm',{}).get(ref,[0.,0.,0.]);comparison.apply_translation(translation)
                    first=canonical_triangle_sha256(baseline[ref]['mesh']);second=canonical_triangle_sha256(comparison)
                    order_evidence.append({'ref':ref,'baseline_triangle_sha256':first,'revised_triangle_sha256':second,
                        'new_to_baseline_translation_mm':translation,'criterion':'Exact native triangle coordinates after only explicitly declared rigid rest translation; no rounding/scaling; facet and vertex order ignored',
                        'status':'PASS' if first==second else 'FAIL'})
                    matched=first==second
                    if not matched and ref in spec.get('permitted_coplanar_retriangulation_refs',[]):
                        planar1=canonical_planar_boundary_sha256(baseline[ref]['mesh']);planar2=canonical_planar_boundary_sha256(comparison)
                        matched=planar1==planar2
                        order_evidence[-1].update(triangle_sets_identical=False,baseline_exact_planar_boundary_sha256=planar1,revised_exact_planar_boundary_sha256=planar2,
                            criterion='Exact rational-coordinate oriented coplanar boundary edges after internal-diagonal cancellation; only declared rigid translation, no rounding/tolerance/resampling',status='PASS' if matched else 'FAIL')
                    if not matched and ref in spec.get('exact_step_preserved_float32_box_refs',[]):
                        step_evidence=native_float32_box_identity(ref,inputs[ref]['mesh'],baseline[ref]['mesh'],m,translation)
                        matched=step_evidence['status']=='PASS'
                        order_evidence[-1].update(triangle_sets_identical=False,exact_step_bound_float32_box_identity=step_evidence,status='PASS' if matched else 'FAIL',criterion=step_evidence['criterion'])

                    if matched and ref in changed:order_only.append(ref)
            geometry_changed=set(changed)-set(order_only)
            allowed_removed=set(spec.get('removed_refs',[]))
            removed=set(baseline)-set(inputs);added=set(inputs)-set(baseline)
            inventory_same=removed==allowed_removed and added==set(spec.get('added_refs',[]))
            input_same=sha(baseline_path)==spec['assembly_sha256']
            good=(inventory_same and input_same and all(x['status']=='PASS' for x in order_evidence if x['ref'] in spec.get('new_to_baseline_rigid_translation_mm',{})) and not(geometry_changed-expected) and
                  (not spec.get('require_each_expected_change') or geometry_changed==expected))
            report['preflight'].append({'name':'R5 reach-fit change scope; exact native shape/declared rigid pose identity',
                'baseline_assembly':str(baseline_path),'baseline_sha256':sha(baseline_path),
                'expected_changed_geometry_refs':sorted(expected),'actual_changed_stl_refs':changed,'actual_changed_geometry_refs':sorted(geometry_changed),'triangle_order_only_evidence':order_evidence,
                'unchanged_geometry_count':len(set(inputs)&set(baseline))-len(geometry_changed),'byte_identical_count':len(set(inputs)&set(baseline))-len(changed),'expected_removed_refs':sorted(allowed_removed),'actual_removed_refs':sorted(removed),'actual_added_refs':sorted(added),'inventory_matches_policy':inventory_same,
                'status':'PASS' if good else 'FAIL'})
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
        report['dimension_checks']=dimensions(inputs,m,baseline if m.get('baseline_native_comparison') else None)
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
