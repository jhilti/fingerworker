#!/usr/bin/env python3
"""Analytic solids sanity checks for the validator, not a device fit report."""
import json
from pathlib import Path
import numpy as np
import manifold3d as md
import validate_finished as v

rows=[]

def check(name,condition,details):
    rows.append({'name':name,'status':'PASS' if condition else 'FAIL','details':details})
    if not condition:raise AssertionError(name)

a=md.Manifold.cube([1,1,1])
b=md.Manifold.cube([1,1,1]).translate([3,0,0])
clear=v.relative_sweep(a,b,0.,2.,.01,.0625)
check('Continuous exterior end-stop touch is certified',clear['status']=='CONTINUOUS_CLEARANCE_CERTIFIED',clear)
hit=v.relative_sweep(a,b,0.,2.5,.01,.0625)
check('Known 0.5 mm end penetration fails',hit['status']=='INTERFERENCE' and hit['maximum_sampled_volume_mm3']>=.4999,hit)
cross=v.relative_sweep(a,b,0.,4.,.01,.0625)
check('Clear endpoints cannot hide intermediate crossing',cross['status']=='INTERFERENCE',cross)
c=md.Manifold.cube([1,1,1]).translate([0,1.2,0])
lateral=v.relative_sweep(a,c,-30.,2.,.01,.0625)
check('Transverse continuous separation certifies',lateral['status']=='CONTINUOUS_CLEARANCE_CERTIFIED',lateral)
coeff=v.motion('P04',{})-v.motion('P05',{})
corners=[float(coeff@np.array([s,p])) for s in (0.,30.) for p in (0.,2.)]
check('Full independent stroke/preload rectangle maps to [-32,0]',min(corners)==-32 and max(corners)==0,{'coefficients':coeff.tolist(),'corners':corners})
mesh=v.tm.creation.box(extents=[2.,4.,6.])
levels=v.ray_levels(mesh,[0,-10,0],[0,1,0],1)
check('Ray section measures exact box boundaries',np.allclose(levels,[-2.,2.]),levels.tolist())
no_override=v.classify({'status':'INTERFERENCE','intersection_volume_mm3':.5},{'kind':'exterior_contact','maximum_intersection_volume_mm3':1000},.01)
check('Exterior-contact annotation cannot waive penetration',no_override['status']=='INTERFERENCE',no_override)
vertices=np.array([[33.4,2.5,7.6],[25.5,-14.1,9.2],[30.,1.,10.8]])
arc_bounds=v.rotational_bounds(vertices,0.,30.)
arc_points=[]
for stroke in np.linspace(0.,30.,1001):
    tr=v.actuator_transform(stroke)
    arc_points.append(vertices@tr[:,:3].T+tr[:,3])
arc_points=np.concatenate(arc_points)
check('Analytic rotating-vertex bounds contain the whole source arc',bool(np.all(arc_points>=arc_bounds[0]-1e-10) and np.all(arc_points<=arc_bounds[1]+1e-10)),{'bounds_mm':arc_bounds.tolist()})
v.write(Path(__file__).with_name('validator-math-checks.json'),{'status':'PASS','scope':'Analytic validation-algorithm sanity checks only; no CAD device qualification','checks':rows})
print(json.dumps({'status':'PASS','checks':len(rows)},indent=2))
