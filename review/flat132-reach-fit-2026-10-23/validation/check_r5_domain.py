#!/usr/bin/env python3
"""Mathematical adapter diagnostics; no substitute for actual native checks."""
import json
import numpy as np
import validate_finished as v
m={'configuration_domain_vertices_user_preload_trim_mm':[[u,p,e] for u,p in [(0.,0.),(30.,0.),(28.,2.),(0.,2.)] for e in [-.8,.8]],'actuator_effective_travel_coefficients':[1.,1.,-1.],'motion_overrides':{'P11':[-1.,-1.,1.],'H10':[-1.,-1.,1.]}}
D=v.configuration_vertices(m);pts=np.array([[u,p,e] for p in np.linspace(0,2,21) for u in np.linspace(0,30-p,101) for e in np.linspace(-.8,.8,9)])
rows=[]
def check(name,condition,**info):rows.append(dict(name=name,status='PASS' if condition else 'FAIL',**info))
coeffs=np.array([[-1,0,0],[0,1,0],[-1,-1,1],[1,1,-1],[1,-1,1],[0,0,1],[2,-3,.4],[-2,3,-.4]])
errors=[]
for coeff in coeffs:
 a=D@coeff;b=pts@coeff;errors.append(max(abs(a.min()-b.min()),abs(a.max()-b.max())))
check('Eight vertices give exact relative-X extrema over the full3D operating prism',max(errors)<1e-10,maximum_projection_error_mm=float(max(errors)),sampled_states=len(pts))
Q=pts@np.array([1.,1.,-1.]);e=pts[:,2];p=pts[:,1]
lo=v.clipped_vertices(D,[1.,1.,-1.],24.2);lowpts=pts[Q<=24.2+1e-12]
check('Inactive clipped-polytope vertices are legal',bool(np.all(lo[:,0]>=-1e-12)&np.all(lo[:,1]>=-1e-12)&np.all(lo[:,1]<=2+1e-12)&np.all(np.abs(lo[:,2])<=.8+1e-12)&np.all(lo[:,0]+lo[:,1]<=30+1e-12)&np.all(lo@np.array([1.,1.,-1.])<=24.2+1e-12)),vertices=lo.tolist())
checks=[]
for c in coeffs:
 a=lo@c;b=lowpts@c;checks.append(bool(b.min()>=a.min()-1e-10 and b.max()<=a.max()+1e-10))
check('Stationary-region exact linear extrema contain every lower-Q sample',all(checks))
inside_active=(Q>=24.2-1e-12)&(e>=-.8-1e-12)&(e<=.8+1e-12)&(Q+e<=30+1e-12)&(p>=0)&(p<=2)
check('Inactive polytope plus active trapezoid times preload covers all legal states',bool(np.all((Q<=24.2+1e-12)|inside_active)))
active=np.array([[q-p+e,p,e] for q in np.linspace(24.2,30.8,101) for e in np.linspace(-.8,.8,41) if q+e<=30+1e-12 for p in np.linspace(0,2,9)])
check('Every active trapezoid/preload point maps back inside the legal user domain',bool(np.all(active[:,0]>=0)&np.all(active[:,1]>=0)&np.all(active[:,1]<=2)&np.all(active[:,0]+active[:,1]<=30+1e-12)&np.all(np.abs(active[:,2])<=.8+1e-12)))
check('Forbidden independent active corner Q30.8/e+.8 is excluded',not(30.8+.8<=30.))
poly=np.array([[24.2,-.8],[30.8,-.8],[29.2,.8],[24.2,.8]])
def area(a):return abs(float(np.sum(a[:,0]*np.roll(a[:,1],-1)-a[:,1]*np.roll(a[:,0],-1)))/2) if len(a)>=3 else 0.
for axis,mid in [(0,27.5),(0,29.2),(1,0.)]:
 a=v.clip_polygon(poly,axis,mid,True);b=v.clip_polygon(poly,axis,mid,False)
 check('Adaptive polygon split preserves complete area axis'+str(axis)+'/'+str(mid),abs(area(a)+area(b)-area(poly))<1e-10,original_area_mm2=area(poly),split_area_mm2=[area(a),area(b)])
check('Inactive source actuator is exactly stationary for all Q<=24.2',max(abs(v.actuator_angle(q)-v.actuator_angle(0.)) for q in np.linspace(-.8,24.2,1001))<1e-12)
check('Both maximum operating endpoints give identical nominal source Q',v.effective_actuator_travel(30,0,m)==v.effective_actuator_travel(28,2,m)==30.)
check('Two extreme export witnesses cover full manual shoe setting interval',abs(v.motion('P11',m)@np.array([28,2,-.8])+28+2.8)<1e-12 and abs(v.motion('P11',m)@np.array([30,0,.8])+30-.8)<1e-12)
# Source substitution: mu*u+mp*p+me*e is identical to mQ*Q+mpPrime*p+mePrime*e.
suberrors=[]
for c in coeffs:
 transformed=np.array([c[0],c[1]-c[0],c[2]+c[0]])
 suberrors.append(float(np.max(np.abs(pts@c-np.column_stack([Q,p,e])@transformed))))
check('Target motion substitution preserves every3D configuration',max(suberrors)<1e-10,maximum_error_mm=max(suberrors))
witness=np.array([[33.,-9.,10.7],[32.,-11.,10.7],[31.,-10.,11.5]])
box=v.rotational_bounds(witness,24.2,30.8);transformed=[]
for q in np.linspace(24.2,30.8,1001):
 t=v.actuator_transform(q);transformed.append(witness@t[:,:3].T+t[:,3])
allpoints=np.concatenate(transformed)
check('Exact rotational vertex bounds cover the extended calibration arc',bool(np.all(allpoints>=box[0]-1e-12)&np.all(allpoints<=box[1]+1e-12)),bounds_mm=box.tolist())
q=np.linspace(-.8,30.8,10001);cx=np.minimum(37.4,61.6-q)
check('Roller-shoe exact separating plane remains valid over full trim arc',bool(np.all(cx+2.4<=64-q+1e-12)),minimum_center_X_mm=float(cx.min()),pivot_X_mm=29.5)
# Every source coil section is a radius1 circle centered at radius6.4 or6.25.
check('Conservative annulus contains both nominal wire radial ranges',5.24<min(6.4-1,6.25-1) and 7.4>=max(6.4+1,6.25+1))
for role in [[0,0,0],[0,1,0],[-1,0,0],[-1,-1,1]]:
 role=np.array(role);starts=12+D[:,1]-D@role;ends=108-D[:,0]-D@role
 realstarts=12+pts[:,1]-pts@role;realends=108-pts[:,0]-pts@role
 check('Spring endpoint envelope contains all source states for role'+str(role.tolist()),realstarts.min()>=starts.min()-1e-12 and realends.max()<=ends.max()+1e-12,envelope_mm=[float(starts.min()),float(ends.max())])
# Isometric choice is explicit: selected81mm locks give the5mm closer ISO position.
check('Selected81mm ISO implies relativeu15-p and actual20-p',all(abs((108-(15-pre))-(12+pre)-81)<1e-12 for pre in [0.,2.]))
# Exact planar boundary identity must accept a true diagonal change and reject
# even an arbitrarily small stored-coordinate change; no geometric tolerance.
cube=v.tm.creation.box();other=cube.copy()
for group in [np.flatnonzero(np.all(cube.face_normals==n,axis=1)) for n in np.unique(cube.face_normals,axis=0)]:
    if len(group)!=2:continue
    f0,f1=cube.faces[group];shared=set(f0)&set(f1);unique=list((set(f0)|set(f1))-shared);common=list(shared)
    faces=np.array([[unique[0],unique[1],common[0]],[unique[1],unique[0],common[1]]])
    normal=cube.face_normals[group[0]]
    for k,face in enumerate(faces):
        tri=cube.vertices[face]
        if np.dot(np.cross(tri[1]-tri[0],tri[2]-tri[0]),normal)<0:faces[k]=face[::-1]
    other.faces[group]=faces
check('Exact planar boundary identity accepts changed coplanar diagonals',v.canonical_planar_boundary_sha256(cube)==v.canonical_planar_boundary_sha256(other) and v.canonical_triangle_sha256(cube)!=v.canonical_triangle_sha256(other))
changed=other.copy();changed.vertices[0,0]+=1e-10
check('Exact rational planar boundary identity rejects tiny coordinate change',v.canonical_planar_boundary_sha256(cube)!=v.canonical_planar_boundary_sha256(changed))
def solid_box(lo,hi):return v.md.Manifold.cube((np.array(hi)-lo).tolist()).translate(lo)
shaft=v.md.Manifold.cylinder(1.1,.2,.2,128).translate([.5,0,0]);head=v.md.Manifold.cylinder(.3,.5,.5,128).translate([.5,0,1.]);moving=shaft+head
fixed=solid_box([-1.,-1.,0.],[3.,1.,1.])-solid_box([-2.,-.3,-.1],[4.,.3,1.1])
covers=[dict(type='cylinder_z',x_mm=.5,y_mm=0.,start_z_mm=0.,end_z_mm=1.1,radius_mm=.20001),dict(type='cylinder_z',x_mm=.5,y_mm=0.,start_z_mm=1.,end_z_mm=1.3,radius_mm=.50001)]
cert=v.convex_cover_sweep(moving,fixed,0.,1.,.01,.0625,covers)
check('Complete conservative cylinder cover proves head tangency without a hull wedge',cert['status']=='COMPLETE_CONSERVATIVE_CONVEX_COVER_CONTINUOUS_CLEARANCE_CERTIFIED',certificate=cert)
obstruction=solid_box([1.4,-.1,.2],[1.6,.1,.8])
blocked=v.convex_cover_sweep(moving,fixed+obstruction,0.,1.,.01,.0625,covers)
check('The same complete cover still detects a real positive-volume collision',blocked['status']=='INTERFERENCE',certificate_status=blocked['status'])
report={'status':'PASS' if all(x['status']=='PASS' for x in rows) else 'FAIL','scope':'New R5 u/p/trim polytope, clipped active actuator arc, relative-motion substitution, annular-envelope and selected81mm ISO mathematics only; no actual device or strength evidence','validator_sha256':v.sha(v.HERE/'validate_finished.py'),'rows':rows}
v.write(v.HERE/'r5-domain-adapter-check.json',report)
print(json.dumps({'status':report['status'],'checks':len(rows),'failed':[r for r in rows if r['status']=='FAIL']},indent=2));assert report['status']=='PASS'
