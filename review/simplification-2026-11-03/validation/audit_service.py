#!/usr/bin/env python3
"""Recheck retained sensor service routes against the actual R12 native mesh.

R12 enclosure and rear-gate release paths have their own explicit clip tests.
This script retains the established sensor/hardware routes and tool envelopes.
"""
from pathlib import Path
import argparse, importlib.util, json, hashlib, sys

HERE=Path(__file__).resolve().parent
STUDY=HERE.parent
ROOT=STUDY.parents[1]
OLD=ROOT/'review/flat132-integrated-palm-2026-11-03/validation/audit_service.py'
spec=importlib.util.spec_from_file_location('r10_service',OLD)
prior=importlib.util.module_from_spec(spec);spec.loader.exec_module(prior)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def tools(parts):
    rows=[];frame=parts['P01']['object']
    def check(name,tool,ref,**e):
        vol=(tool^parts[ref]['object']).volume()
        rows.append(dict(name=name,target=ref,status='PASS' if vol<=.01 else 'FAIL',intersection_mm3=vol,**e))
    for side in [-1,1]:
        if side==1:seated=prior.ycyl(13,21,-12.8,8.5,1.5)+prior.ycyl(21,24.001,-12.8,8.5,2.75)
        else:seated=prior.ycyl(-21,-13,-12.8,8.5,1.5)+prior.ycyl(-24.001,-21,-12.8,8.5,2.75)
        for ref in ['P01','H190' if side==-1 else 'H191']:
            check('Complete seated H18 release0..0.001mm envelope',seated,ref,side=side)
        y0,y1=(23.9,90) if side==1 else (-90,-23.9)
        for radius,label in [(1.5,'3mm hex-driver shaft'),(2.75,'5.5mm screw-head extraction')]:
            check('H18 full side access: '+label,prior.ycyl(y0,y1,-12.8,8.5,radius),'P01',side=side)
    for y in [-59,59]:
        tool=prior.md.Manifold.cylinder(35.8,1.5,1.5,96).translate([-26.5,y,-29])
        check('Optional case M2 screw underside driver',tool,'P01',side_y_mm=y)
    return rows

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--archive',type=Path,required=True);a=ap.parse_args()
    parts,ignored=prior.v.load(a.archive,{})
    assert not ignored
    assert not {r:x.get('error') for r,x in parts.items() if x.get('error') and r not in prior.v.SPRINGS}
    certificate=HERE/'native-motion.json';motion=json.loads(certificate.read_text())
    assert motion['status'].startswith('PASS')
    assert motion['native_stl_archive_sha256']==sha(a.archive)
    assert motion['source_sha256']==sha(STUDY/'fingerworker_R12_simplified.fs')
    initial=next(r for r in motion['checks'] if r['name']=='Complete H12 initial release envelope0..0.001mm')
    assert initial['status']=='PASS' and initial['all_boolean_results_valid']
    paths=[]
    for route in prior.specs(parts):
        if not route['name'].startswith(('H18 ','H19 ','Sensor-yoke')):continue
        assert all(r in parts for r in route['moving_refs'])
        route['fixed_refs']=[r for r in route['fixed_refs'] if r in parts and r!='P06']
        route['prerequisites']=route['prerequisites'].replace('rear caps','rear gate P06').replace('R10','R12').replace('set preload0.','fixed sensor datum.').replace('preload0','fixed sensor datum').replace('Retain H13/H15 while removing the complete sensor/yoke stack.','H13/H15 and the complete preload mechanism are absent. The fixed support stays integral with P01.').replace('guide slot','round guide hole')
        if route['name'].startswith('Sensor-yoke') and route['direction']==[1,0,0]:
            route['initial_translation_mm']=[.001,0,0];route['range_mm']=[0,3.199]
            route['prerequisites']+=' Initial0..0.001mm contact release is certified by the complete conservative native H12 envelope in native-motion.json.'
        paths.append(route)
    manifest=json.loads((prior.R5/'manifest.json').read_text());manifest['service_sweeps']=paths
    rows=prior.v.service_sweeps(parts,manifest)
    toolrows=tools(parts)
    bad=[r for r in rows if r['status'] in prior.BAD]+[r for r in toolrows if r['status']=='FAIL']
    report=dict(status='PASS_NATIVE_R12_SENSOR_SERVICE' if not bad else 'FAIL',
        native_archive_sha256=sha(a.archive),source_sha256=sha(STUDY/'fingerworker_R12_simplified.fs'),
        validator_sha256=sha(__file__),initial_contact_certificate_sha256=sha(certificate),initial_contact_certificate=initial,declared_paths=paths,checks=rows,tool_checks=toolrows,
        failed_count=len(bad),failures=bad,
        scope='Retained unloaded sensor/hardware service routes on final native STL; finite path sampling plus declared conservative tool envelopes. Rear-gate and enclosure release are checked separately.',
        limitations='No physical fit, wiring slack, hand access, latch force or load qualification.')
    (HERE/'service-native.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(status=report['status'],paths=len(paths),checks=len(rows),tool_checks=len(toolrows),failed_count=len(bad),failures=bad),indent=2))
    return bool(bad)

if __name__=='__main__':raise SystemExit(main())
