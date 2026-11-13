#!/usr/bin/env python3
"""Check actual native articulated click and isometric poses, without moving CAD."""
from pathlib import Path
import argparse
import hashlib
import json
import math
import sys
import time

import numpy as np

D=Path(__file__).resolve().parent
ROOT=D.parents[1]
sys.path.insert(0,str(ROOT/'review/narrow-design-2026-10-17'))
import validate_narrow as core
from validate_narrow import Auditor, REFS, SPRINGS, load_inputs, clean_numbers


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('assembly',type=Path)
    parser.add_argument('--stroke',type=float,required=True)
    parser.add_argument('--preload',type=float,required=True)
    parser.add_argument('--mode',choices=('dynamic','isometric'),default='dynamic')
    parser.add_argument('--source',type=Path,default=D/'fingerworker_flat132.fs')
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    start=time.monotonic()
    source=ROOT/'fingerworker_mvp.fs'
    original_source_sha=sha(source)
    original_refs=set(core.REFS)
    iso_refs={'H140','H141'}
    core.REFS=original_refs|iso_refs
    inputs,ignored=load_inputs(args.assembly,None)
    core.REFS=original_refs
    expected=(original_refs-SPRINGS)|iso_refs if args.mode=='isometric' else original_refs
    audit=Auditor(inputs,.01,.0625)
    report=dict(status='RUNNING',units='mm',mode=args.mode,actual_native_pose=True,
        scope='Actual regenerated pose, limited articulated click and lock sleeve checks; neutral assembly report supplies continuous rigid-motion certificates',
        assembly=str(args.assembly.resolve()),assembly_sha256=sha(args.assembly),
        source_sha256=sha(args.source),validator_sha256=sha(Path(__file__)),
        declared_stroke_mm=args.stroke,declared_preload_mm=args.preload,
        device_part_count=len(inputs),missing_refs=sorted(expected-set(inputs)),
        unexpected_refs=sorted(set(inputs)-expected),invalid_solids=audit.invalid,
        ignored_members=ignored,mesh_inventory={},dimensions=[],pairs=[],legacy_contacts=[],
        limitations=['Helical coils are illustrative; spring force values are not measurements.',
            'Click actuator is a source approximation; actual switch operating force, overtravel and hysteresis need physical verification.',
            'Geometry does not establish plastic strength, fatigue, print tolerance or sensor accuracy.'])
    for ref,item in sorted(inputs.items()):
        mesh=item['mesh']
        report['mesh_inventory'][ref]=dict(sha256=item['sha256'],member=item['member'],
            bounds_mm=mesh.bounds.tolist(),watertight=bool(mesh.is_watertight),is_volume=bool(mesh.is_volume))
        if not mesh.is_watertight or not mesh.is_volume:
            report['invalid_solids'][ref]='Not a closed positive-volume mesh'
    def scalar(name,value,target,tolerance=.01):
        report['dimensions'].append(dict(name=name,measured_mm=float(value),expected_mm=target,
            tolerance_mm=tolerance,status='PASS' if abs(value-target)<=tolerance else 'FAIL'))
    if not report['missing_refs'] and not report['unexpected_refs'] and not report['invalid_solids']:
        stroke,preload=args.stroke,args.preload
        scalar('Actual carriage return face X',inputs['P04']['mesh'].bounds[1,0],124-stroke)
        scalar('Actual cam front face X',inputs['H10']['mesh'].bounds[0,0],60-stroke)
        scalar('Actual yoke rear face X',inputs['P05']['mesh'].bounds[0,0],-7+preload)
        scalar('Actual fixed-seat front face X',inputs['H050']['mesh'].bounds[0,0],9+preload)
        scalar('Actual moving-seat front face X',inputs['H060']['mesh'].bounds[0,0],113-stroke)
        roller_x=min(33.4,60-stroke-2.4)
        roller_y=-14.1+math.sqrt(3.1**2+16.7**2-(roller_x-25.5)**2)
        scalar('Actual articulated roller center X',inputs['H09b']['mesh'].bounds[:,0].mean(),roller_x)
        scalar('Actual articulated roller center Y',inputs['H09b']['mesh'].bounds[:,1].mean(),roller_y)
        scalar('Cam/roller nominal axial contact gap',inputs['H10']['mesh'].bounds[0,0]-inputs['H09b']['mesh'].bounds[1,0],max(0,60-stroke-35.8))
        pairs=[('P04','P01'),('P04','P05'),('P04','H09'),('P04','H09a'),('P04','H09b'),
            ('H10','P01'),('H10','H09'),('H10','H09a'),('H10','H09b'),
            ('H09a','P01'),('H09b','P01'),('H09a','H09'),('H09b','H09'),('H09a','P05'),('H09b','P05')]
        for a,b in pairs:
            row=audit.pair(a,b)
            if {a,b}=={'H10','H09b'}:
                row['intended_contact']='Source roller is articulated to the cam face; only exterior contact is permitted'
            report['pairs'].append(row)
        # Keep the original soft sleeve / adjuster-end interaction visible.
        # It is not the intended sleeve/core fit, and is never labelled CLEAR
        # or qualified merely because the same source geometry was retained.
        old,_=load_inputs(ROOT/'review/narrow-design-2026-10-17/assembly-mm',None)
        before=Auditor(old,.01,.0625)
        now_volume=float((audit.objects['P03']^audit.objects['H13']).volume())
        old_volume=float((before.objects['P03']^before.objects['H13'].translate([preload,0,0])).volume())
        report['legacy_contacts'].append(dict(pair=['P03','H13'],preload_mm=preload,
            intersection_volume_mm3=now_volume,baseline_at_same_preload_volume_mm3=old_volume,
            status='INHERITED_NOMINAL_SOFT_PART_CONTACT' if now_volume>.01 and abs(now_volume-old_volume)<=.01 else
                'NEW_OR_CHANGED_INTERFERENCE' if now_volume>.01 else 'CLEAR',
            qualification='NOT_ESTABLISHED',
            meaning='Soft sleeve overlaps the original adjuster shaft end at zero preload. This is separate from the intended sleeve/core fit. Physical deformation, adjustment friction and load effects remain unverified. The2 mm service pose clears it.'))
        if args.mode=='isometric':
            for ref,side in [('H140',-1),('H141',1)]:
                bounds=inputs[ref]['mesh'].bounds
                scalar(ref+' sleeve length',bounds[1,0]-bounds[0,0],86.)
                scalar(ref+' sleeve axis Y',bounds[:,1].mean(),side*51)
                scalar(ref+' sleeve front X',bounds[0,0],12+preload)
                scalar(ref+' sleeve rear X',bounds[1,0],113-stroke)
                for target in sorted(expected-{ref,'H140' if ref=='H141' else 'H141'}):
                    row=audit.pair(ref,target)
                    if target in (('H050','H060') if side<0 else ('H051','H061')):
                        row['intended_contact']='Lock sleeve exterior end contact with steel seats'
                    report['pairs'].append(row)
    rows=report['dimensions']+report['pairs']
    failures=[row for row in rows if row['status'] in ('FAIL','INTERFERENCE')]
    uncertain=[row for row in rows if row['status']=='UNCHECKED']
    good_inputs=not (report['missing_refs'] or report['unexpected_refs'] or report['invalid_solids'])
    legacy=any(row['status']=='INHERITED_NOMINAL_SOFT_PART_CONTACT' for row in report['legacy_contacts'])
    new_contact=any(row['status']=='NEW_OR_CHANGED_INTERFERENCE' for row in report['legacy_contacts'])
    report.update(status=('PASS_CHECKED_POSE_PAIRS_WITH_INHERITED_SOFT_CONTACT' if legacy else 'PASS') if good_inputs and not failures and not uncertain and not new_contact else 'FAIL' if failures or new_contact else 'INVALID_OR_UNRESOLVED',
        failed_checks=len(failures),unresolved_checks=len(uncertain),
        main_source_unchanged=sha(source)==original_source_sha,
        elapsed_seconds=time.monotonic()-start)
    args.output.write_text(json.dumps(clean_numbers(report),indent=2)+'\n')
    print(json.dumps({key:report[key] for key in ('status','mode','device_part_count','failed_checks','unresolved_checks','elapsed_seconds')},indent=2),flush=True)
    for row in failures+uncertain:print(json.dumps(row),flush=True)


if __name__=='__main__':main()
