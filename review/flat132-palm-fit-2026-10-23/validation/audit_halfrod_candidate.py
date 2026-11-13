#!/usr/bin/env python3
"""Conservative in-memory half-round palm feasibility; not native CAD validation."""
from pathlib import Path
import json
import hashlib
import numpy as np
import manifold3d as md
import validate_finished as v

baseline=v.ROOT/'review/flat132-strengthened-2026-10-22/validation/manifest.json'
m=json.loads(baseline.read_text());parts,_=v.load(m['assembly'],m)

def cylinder_y(y0,y1,r,circumscribed=False):
    n=256;r=r/np.cos(np.pi/n) if circumscribed else r
    return md.Manifold.cylinder(y1-y0,r,r,n).rotate([-90,0,0]).translate([-27.,y0,19.75])

# This retains every existing plate/ear/counterbore belowZ14.5, then crops the
# unused wrist7mm. A new plate wrist-corner fillet only removes more material.
plate=parts['P02']['object'].trim_by_plane([0.,0.,-1.],-14.5).trim_by_plane([1.,0.,0.],-37.25)
# Circumscribed outer polygons conservatively contain each exact circle;
# no end fillets are applied, making this a superset of the intended geometry.
core=cylinder_y(-58.,58.,7.75,True).trim_by_plane([-1.,0.,0.],27.)
rigid=plate+core
outer=cylinder_y(-43.,43.,10.25,True)
inner=cylinder_y(-44.,44.,7.75,False)
sleeve=(outer-inner).trim_by_plane([-1.,0.,0.],27.).trim_by_plane([0.,0.,1.],14.6)
for lo_y,hi_y in [(-43.,-39.),(39.,43.)]:
    band=md.Manifold.cube([2.5,hi_y-lo_y,15.4]).translate([-27.,lo_y,14.6])
    sleeve=sleeve+band
for ref,obj in [('P02',rigid),('P03',sleeve)]:
    parts[ref]={'object':obj,'mesh':None,'sha256':'IN_MEMORY_CONSERVATIVE_CANDIDATE'}

rows=[]
for ref in ('P02','P03'):
    for target in sorted(set(parts)-{'P02','P03'}-v.SPRINGS):
        row={'pair':[ref,target]}
        try:
            if target in v.ARTICULATED:
                row.update(v.articulated_sweep(target,ref,parts,m))
            else:
                dm=v.motion(ref,m)-v.motion(target,m)
                interval=v.configuration_vertices(m)@dm
                row.update(v.relative_sweep(parts[ref]['object'],parts[target]['object'],float(interval.min()),float(interval.max()),.01,.0625))
        except Exception as e:row.update(status='UNCHECKED',reason=repr(e))
        rows.append(row)
issues=[row for row in rows if row['status'] in ('INTERFERENCE','UNCHECKED','UNRESOLVED_NEAR_CONTACT')]
# The candidate core and TPU models deliberately overlap by circumscription;
# their shared-radius exact source proof and native BRep pair remain required.
report={'status':'CONSERVATIVE_AFFECTED_FEASIBILITY_PASS' if not issues else 'CANDIDATE_ISSUES',
    'scope':'In-memory conservative unfilleted half-round palm only against actual R2 native parts over the unchanged complete legal configuration domain; not a native R3 or strength qualification',
    'baseline_manifest_sha256':v.sha(baseline),'baseline_native_archive_sha256':v.sha(m['assembly']),
    'intended_contact_shift_mm':7.,'candidate_axis_X_Z_mm':[-27.,19.75],
    'rigid_core_radius_mm':7.75,'TPU_outer_radius_mm':10.25,
    'wrist_contact_X_mm':-37.25,'flat_front_X_mm':-27.,
    'rigid_plate_wrist_X_mm':-37.25,'rigid_plate_front_X_mm':-23.25,
    'candidate_bounds_mm':{ref:v.bounds(parts[ref]['object']).tolist() for ref in ('P02','P03')},
    'pair_count':len(rows),'issues':issues,'rows':rows,
    'retention':'Two TPU front return bands, Y[-43,-39] and[39,43], X[-27,-24.5], Z[14.6,30], close the flat-front side locally and create nominal geometric capture of the D-core. Assembly flex, retention force, print fit and durability remain unqualified.',
    'limitations':['Outer circle polygons are conservative supersets and source end fillets only shrink the intended material.',
        'The preserved lower plate is based on its R2 native facets; R3 native exact BRep and source checks remain required.',
        'Shared core/TPU coincident surfaces are excluded from this conservative candidate pair test and must separately have zero exact native BRep intersection.',
        'No hardware, mechanism, electronics placement or force-path structural material was moved by this feasibility construction.']}
v.write(v.HERE/'halfrod-candidate-audit.json',report)
print(json.dumps({'status':report['status'],'pair_count':len(rows),'issues':issues,'candidate_bounds_mm':report['candidate_bounds_mm']},indent=2))
