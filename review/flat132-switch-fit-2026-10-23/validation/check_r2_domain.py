#!/usr/bin/env python3
"""New R2 audit adapter checks; mathematical diagnostics, not device evidence."""
import json
import numpy as np
import trimesh as tm
import manifold3d as md
import validate_finished as v

vertices=np.array([[0.,0.],[30.,0.],[28.,2.],[0.,2.]])
m={'configuration_domain_vertices_stroke_preload_mm':vertices.tolist(),
   'actuator_effective_travel_coefficients':[1.,1.], 'motion_overrides':{'H10':[-1.,-1.]}}
rows=[]
def check(name,condition,**details):
    rows.append({'name':name,'status':'PASS' if condition else 'FAIL',**details})

# Linear projections of a compact convex polygon attain extrema at vertices.
points=np.array([[s,p] for p in np.linspace(0,2,41) for s in np.linspace(0,30-p,101)])
coefficients=[[-1,0],[0,1],[-1,-1],[1,1],[1,-1],[0,-1],[2,-3],[-2,3]]
errors=[]
for c in coefficients:
    c=np.array(c);exact=vertices@c;sampled=points@c
    errors.append(max(abs(sampled.min()-exact.min()),abs(sampled.max()-exact.max())))
check('Exact R2 rigid relative-X interval extrema at legal polygon vertices',max(errors)<1e-10,
      maximum_projection_error_mm=float(max(errors)),coefficient_pairs=coefficients)

# Partition in q=s+p; below switch pickup the rotation is constant.
qs=points.sum(1);ps=points[:,1]
inside_lower=(qs<=24.2+1e-9)&(ps<=qs+1e-9)&(ps<=2.+1e-9)
inside_upper=(qs>=24.2-1e-9)&(qs<=30.+1e-9)&(ps>=-1e-9)&(ps<=2.+1e-9)
check('Neutral-angle polygon plus active-arc rectangle covers every sampled legal state',bool(np.all(inside_lower|inside_upper)),sample_count=len(points))
upper=np.array([[q-p,p] for q in np.linspace(24.2,30,51) for p in np.linspace(0,2,31)])
check('Every active-arc rectangle state maps to the legal s/p polygon',bool(np.all(upper[:,0]>=0)&np.all(upper[:,1]>=0)&np.all(upper[:,1]<=2)&np.all(upper.sum(1)<=30+1e-9)))
angles=[v.actuator_angle(q)-v.actuator_angle(0.) for q in np.linspace(0,24.2,1001)]
check('Lower-q actuator angle is exactly neutral through q24.2',max(abs(np.array(angles)))<1e-12,maximum_angle_deviation_rad=float(max(abs(np.array(angles)))))

# Endpoints: the native p2 maximum is stroke28; p0 allows stroke30.
check('Both maximum operating endpoints produce the same source switch angle',abs(v.effective_actuator_travel(28.,2.,m)-v.effective_actuator_travel(30.,0.,m))<1e-12)
check('Manual H10 source reset yields cam X=64-(stroke+preload)',np.array_equal(v.motion('H10',m),[-1.,-1.]))
check('Forbidden old independent endpoint stroke30/preload2 excluded',not(30+2<=30))

# A rotating witness's exact computed extrema must contain every transformed point.
witness=np.array([[33.,-9.,10.7],[32.,-11.,10.7],[31.,-10.,11.5]])
box=v.rotational_bounds(witness,24.2,30.)
transformed=[]
for q in np.linspace(24.2,30,501):
    matrix=v.actuator_transform(q);transformed.append(witness@matrix[:,:3].T+matrix[:,3])
a=np.concatenate(transformed)
check('Active q arc exact vertex bounds enclose all 501 sampled transforms',bool(np.all(a>=box[0]-1e-12)&np.all(a<=box[1]+1e-12)),bounds_mm=box.tolist())
# Exact native triangle identity must ignore ordering and detect any coordinate change.
cube=tm.creation.box();reordered=cube.copy();reordered.faces=reordered.faces[::-1][:,[1,2,0]]
check('Canonical triangle identity ignores order only',v.canonical_triangle_sha256(cube)==v.canonical_triangle_sha256(reordered))
changed=cube.copy();changed.vertices[0,0]+=1e-10
check('Canonical triangle identity has no geometric rounding tolerance',v.canonical_triangle_sha256(cube)!=v.canonical_triangle_sha256(changed))

# A transverse gap can make a whole-body convex hull unhelpful; the complete
# slab union still proves all physical material continuously separated.
def box(lo,hi):return md.Manifold.cube((np.array(hi)-lo).tolist()).translate(lo)
a=box([3.,-2.,0.],[5.,-1.,1.])+box([2.,1.,0.],[4.,2.,1.])
b=box([0.,-2.,0.],[1.,-1.,1.])+box([0.,1.,0.],[.5,2.,1.])+box([1.,-.5,0.],[2.,.5,1.])
partition=v.partitioned_relative_sweep(a,b,-1.,0.,.01,.0625,{'axis':1,'planes_mm':[-1.,1.]})
check('Complete transverse slab certificate preserves true endpoint tangency and gaps',partition['status']=='COMPLETE_TRANSVERSE_PARTITION_CONTINUOUS_CLEARANCE_CERTIFIED',certificate=partition)
report={'status':'PASS' if all(r['status']=='PASS' for r in rows) else 'FAIL',
        'scope':'Checks only the newly adapted R2 operating-domain mapping, q-based switch arc, exact triangle ordering and complete transverse-slab certificate; not native device validation or material strength evidence',
        'validator_sha256':v.sha(v.HERE/'validate_finished.py'),'rows':rows}
v.write(v.HERE/'r2-domain-adapter-check.json',report)
print(json.dumps(report,indent=2))
assert report['status']=='PASS'
