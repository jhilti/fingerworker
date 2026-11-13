#!/usr/bin/env python3
"""Independent R10 assembly/service audit; never edits CAD or native exports.

The local mode is a conservative mesh CSG preflight. --native-archive switches
the very same declared paths to the actual fresh Onshape STL export. A fresh
native STEP and unchanged-body identity are certified by audit_native.py.
"""
from pathlib import Path
import argparse, copy, hashlib, json, sys
import numpy as np
import manifold3d as md

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
ROOT = STUDY.parents[1]
R9 = ROOT / 'review/flat132-palm-bracing-2026-10-25'
R5 = ROOT / 'review/flat132-reach-fit-2026-10-23/validation'
sys.path.insert(0, str(R5))
import validate_finished as v

BAD = {'FAIL','INTERFERENCE','UNCHECKED','UNRESOLVED_NEAR_CONTACT'}
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def box(lo,hi):
    return md.Manifold.cube((np.array(hi)-lo).tolist()).translate(lo)


def cyl(x0,x1,y,z,r0,r1=None):
    return md.Manifold.cylinder(x1-x0,r0,r0 if r1 is None else r1,128).rotate([0,90,0]).translate([x0,y,z])


def ycyl(y0,y1,x,z,r):
    return md.Manifold.cylinder(y1-y0,r,r,128).rotate([-90,0,0]).translate([x,y0,z])


def preflight(old):
    """Literal independent CSG, excluding all source-agent builder imports."""
    out=copy.copy(old)
    frame=old['P01']['object'];palm=old['P02']['object']
    for y in [-31.5,31.5]:
        frame=frame-box([-22,y-3,6.3],[-20,y+3,8])
        # Restored M4 insert pilot is vertical, entirely inside the old foot.
        frame=frame+md.Manifold.cylinder(6.3,2.6,2.6,128).translate([-16,y,.2])
        palm=palm+box([-23,y-5.5,6.3],[-9.5,y+5.5,6.5])
        palm=palm+box([-22.25,y-3.25,6.4],[-19.75,y+3.25,8.3])
        palm=palm+md.Manifold.cylinder(4.2,2.2,2.2,128).translate([-16,y,6.3])
        palm=palm+md.Manifold.cylinder(4,4,4,128).translate([-16,y,10.5])
        # The obsolete forward M4 mounting stock is now absent. Do not trim
        # the old overlapping foot belowZ4: that is still the base floor.
        frame=frame-box([-17,y-5.5,4],[-8.9,y+5.5,6.6])
        palm=palm-box([-17,y-5.5,6.3],[-9.4,y+5.5,14.6])
    for lo,hi in [(-25,-18),(18,25)]:
        palm=palm+box([-22.75,lo,14],[-22.55,hi,27])
    palm=palm-box([-25.5,-16.5,9.2],[-23.1,16.5,14.7])
    keeper=old['H15']['object']
    for i,y in enumerate([-11,11]):
        frame=frame+box([-18,y-2.85,21.15],[-16,y+2.85,26.85])
        frame=frame-cyl(-23,-15.8,y,24,1.7)
        frame=frame-cyl(-18.5,-17,y,24,1.5,3)
        frame=frame-cyl(-17,-15.8,y,24,3.2)
        keeper=keeper+cyl(-23,-21.5,y,24,3,1.5)
        keeper=keeper-cyl(-24,-20,y,24,1.7)
        out[f'H16{i}']=dict(old[f'H16{i}'],object=old[f'H16{i}']['object'].transform([[-1,0,0,-40],[0,1,0,0],[0,0,1,0]]))
        out[f'H17{i}']=dict(old[f'H17{i}'],object=old[f'H17{i}']['object'].translate([-6.9,0,0]))
    out['P01']=dict(old['P01'],object=frame+palm)
    for y0,y1 in [(-66.5,-38.8),(38.8,66.5)]:
        out['P01']['object']=out['P01']['object']-ycyl(y0,y1,-12.8,8.5,3.2)
    out['H15']=dict(old['H15'],object=keeper)
    del out['P02']
    return out


def specs(parts):
    old=json.loads((ROOT/'review/flat132-finished-2026-10-22/validation/manifest.json').read_text())['service_sweeps']
    rows=[]
    removed_for_sensor=set(v.SPRINGS)|{'H040','H041','P060','P061','P070a','P070b','P071a','P071b'}
    # The two side retention screws and their spacers must be reachable with
    # the palm FIXED. Only the known nominal screw/root-thread engagement is
    # excluded during the first2.3mm of real rotational unthreading.
    for i,side in [(0,-1),(1,1)]:
        ref=f'H18{i}';fixed=sorted(set(parts)-removed_for_sensor-{ref,'H12'})
        rows.append(dict(name='H18 initial2.3mm rotational thread release',moving_refs=[ref],fixed_refs=fixed,direction=[0,side,0],range_mm=[0,2.299],initial_translation_mm=[0,side*.001,0],prerequisites='Unload/remove springs and guide rods; set preload0. Unscrew H18 with2.5mm hex from the outer side through the new rod-block access bore. H12 is excluded only for intentional nominal thread engagement. Initial0..0.001mm exact seated-face release has a separate complete cylindrical envelope certificate.'))
        fixed=sorted(set(parts)-removed_for_sensor-{ref})
        rows.append(dict(name='H18 full55mm side withdrawal after unthreading',moving_refs=[ref],fixed_refs=fixed,direction=[0,side,0],range_mm=[0,55],initial_translation_mm=[0,side*2.3,0],prerequisites='H18 already rotationally unthreaded2.3mm; entire head and shank pass outward through the6.4mm rod-block access bore, preload0.'))
    for i,side in [(0,-1),(1,1)]:
        ref=f'H19{i}';fixed=sorted(set(parts)-removed_for_sensor-{ref,'H180','H181'})
        rows.append(dict(name='H19 full55mm side spacer withdrawal',moving_refs=[ref],fixed_refs=fixed,direction=[0,side,0],range_mm=[0,55],prerequisites='Both H18 screws removed, preload0. Withdraw each OD4x6 spacer sideways through its guide slot, clear shortened palm foot and new rod-block bore.'))
    # The old sensor removal route remains, but now the palm is fixed P01.
    for s in old:
        if s['name'].startswith('Sensor-yoke'):
            s=copy.deepcopy(s)
            s['fixed_refs']=[r for r in s['fixed_refs'] if r in parts]
            s['removed_refs']=[r for r in s['removed_refs'] if r in parts and r!='P01']
            s['prerequisites']='Unload/restrain and remove springs, guide rods, rear caps and H18/H19 retention; preload0. Keep the integrated frame/palm in place. Retain H13/H15 while removing the complete sensor/yoke stack.'
            if s['direction']==[1,0,0]:s['range_mm']=[0,3.2]
            else:s['initial_translation_mm']=[3.2,0,0]
            rows.append(s)
    def add(name,moving,fixed,direction,travel,initial=None,pre=''):
        rows.append(dict(name=name,moving_refs=moving,fixed_refs=fixed,direction=direction,range_mm=[0,travel],initial_translation_mm=initial or [0,0,0],prerequisites=pre))
    add('H21 preload lock20mm upward removal',['H21'],['P01','H11','H13','H15'],[0,0,1],20,[0,0,.001],pre='Release/remove standard M3 preload lock from above before removing the adjuster; no spring energy remains. Initial0..0.001mm seated-face release has a separate complete cylindrical envelope certificate.')
    add('H22 brass lock pad20mm upward removal',['H22'],['P01','H11','H13','H15'],[0,0,1],20,pre='H21 removed; lift the loose brass lock pad through the same open vertical access before M6 nut removal.')
    fixed=['P01','H11','H15','H160','H161','H170','H171','H21','H22']
    pre='Remove sensor/yoke stack first; release H21 locking screw, keep the brass pad retained. Unscrew H13 toward+X, then lift only after the complete thread clears H11.'
    add('Adjuster12mm forward thread release',['H13'],fixed,[1,0,0],12,pre=pre)
    add('Adjuster40mm upward removal',['H13'],fixed,[0,0,1],40,[12,0,0],pre)
    pre='Sensor/yoke stack and H13 removed; support H15. Counterhold H17 from above with a slim AF5.5 open-end wrench. Fully remove both H16 screws toward+X; actual wiring disconnected/secured.'
    for i in [0,1]:
        add('Keeper screw12mm forward withdrawal',[f'H16{i}'],['P01','H11','H15',f'H17{i}'],[1,0,0],12,[.05,0,0],pre+' The initial0..0.05mm seated cone release is certified separately by its analytic axial envelope.')
        add('Keeper nut40mm upward withdrawal',[f'H17{i}'],['P01','H11','H15'],[0,0,1],40,pre='Both H16 screws completely removed; lift the loose square nuts out with the wrench or tweezers.')
    add('Keeper2mm wristward release',['H15'],['P01','H11'],[-1,0,0],2,pre='Remove sensor/yoke stack,H13,both H16 screws and both H17 nuts; keep frame/palm fixed.')
    add('Keeper35mm upward removal',['H15'],['P01','H11'],[0,0,1],35,[-2,0,0],pre='Keeper already shifted2mm wristward through the lower palm service notch; H16/H17/H13 absent.')
    add('M6 nut9mm forward release',['H11'],['P01'],[1,0,0],9,pre='Sensor/yoke,H13,H15,H16,H17,H21,H22 removed; extract the M6 nut toward the open sensor cavity.')
    add('M6 nut40mm upward removal',['H11'],['P01'],[0,0,1],40,[9,0,0],pre='M6 nut already advanced9mm into the empty sensor cavity.')
    case=['P08','P09','P10']+[r for r in parts if r.startswith(('E','PCB_')) and r not in ('E06','E08')]
    add('Case20mm direct downward removal',case,['P01'],[0,0,-1],20,pre='Support device clear of bench; remove both underside enclosure M2 screws and disconnect/secure wiring. Closed P08/P09/P10/electronics module lowers as a unit; integrated frame/palm stays fixed.')
    add('Detached lid15mm upward release',['P09'],['P08','P10']+[r for r in parts if r.startswith(('E','PCB_')) and r not in ('E06','E08')],[0,0,1],15,[0,0,.001],pre='Complete electronics case detached from fixed palm and on bench; remove three countersunk lid screws. Initial0.001mm removes exact seated boundary contact; earlier R8 exact plain-lid sections retained. Never lift installed P09 into the palm cover.')
    return rows


def tools(parts):
    rows=[]
    frame=parts['P01']['object']
    for i,y in enumerate([-11,11]):
        # Full analytic superset of every H16 pose for0<=dx<=0.05:
        # because the90deg head expands toward+X, the starting cone plus
        # a0.05mm radius3 front cylinder bounds the whole swept head exactly.
        # The radius1.5 shank is already contained by that cone at its front.
        seated=cyl(-25,-18.5,y,24,1.5)+cyl(-18.5,-17,y,24,1.5,3)+cyl(-17,-16.95,y,24,3)
        for ref in ['P01','H11','H15',f'H17{i}']:
            vol=(seated^parts[ref]['object']).volume()
            rows.append(dict(name='Complete analytic seated H16 cone release0..0.05mm',side=i,target=ref,status='PASS' if vol<=.01 else 'FAIL',intersection_volume_upper_bound_mm3=vol,numerical_mesh_volume_tolerance_mm3=.01,scope='Complete analytic axial swept envelope, not samples; coincident mesh cone tessellation may leave sub-tolerance volume.'))
        tool=box([-25.5,y-6.5,17],[-23.5,y+6.5,65])
        for ref in ['P01','H15','H11']:
            obj=parts[ref]['object'];vol=(tool^obj).volume()
            rows.append(dict(name='AF5.5 slim wrench complete access envelope',side=i,target=ref,status='PASS' if vol<=.01 else 'FAIL',intersection_volume_mm3=vol,bounds_mm=[[-25.5,y-6.5,17],[-23.5,y+6.5,65]],scope='Conservative13mm head/2mm thickness. Manufacturer STAHLWILLE40065555 lists12.6x2mm,78mm length; complete real hand/tool fit remains physical.'))
        # The driven end of a2mm hex key/bit is bounded by a3mm cylinder.
        tool=cyl(-16.9,34,y,24,1.5)
        vol=(tool^frame).volume()
        rows.append(dict(name='Sensor-side2mm hex driver access after H13/sensor removal',side=i,target='P01',status='PASS' if vol<=.01 else 'FAIL',intersection_volume_mm3=vol,bounds_mm=[[-16.9,y-1.5,22.5],[34,y+1.5,25.5]],scope='Driver shaft3mm diameter; handle remains outside the sensor cavity.'))
    for side in [-1,1]:
        if side==1:seated=ycyl(13,21,-12.8,8.5,1.5)+ycyl(21,24.001,-12.8,8.5,2.75)
        else:seated=ycyl(-21,-13,-12.8,8.5,1.5)+ycyl(-24.001,-21,-12.8,8.5,2.75)
        for ref in ['P01','H190'if side==-1 else'H191']:
            vol=(seated^parts[ref]['object']).volume()
            rows.append(dict(name='Complete seated H18 release0..0.001mm envelope',side=side,target=ref,status='PASS'if vol<=.01 else'FAIL',intersection_volume_upper_bound_mm3=vol,scope='Complete analytic shaft/head axial sweep. Actual H12 thread engagement is intentional and released by unthreading.'))
        y0,y1=(23.9,90)if side==1 else(-90,-23.9)
        for radius,label in [(1.5,'3mm shaft of2.5mm hex key'),(2.75,'Complete5.5mm H18 screw-head straight extraction')]:
            tool=ycyl(y0,y1,-12.8,8.5,radius);vol=(tool^frame).volume()
            rows.append(dict(name='H18 side access at preload0: '+label,side=side,status='PASS' if vol<=.01 else'FAIL',intersection_volume_mm3=vol,scope='Palm feet/ears end atX-17. Outer rod blocks have6.4mm through access. Whole path to outside Y+/-90, not a local head-only probe.'))
    tool=md.Manifold.cylinder(36,1.5,1.5,96).translate([-19,0,29])
    vol=(tool^frame).volume()
    rows.append(dict(name='H21 standard top hex driver access',status='PASS'if vol<=.01 else'FAIL',intersection_volume_mm3=vol,scope='3mm shaft through upper reaction-lock access; open above the device.'))
    seated=md.Manifold.cylinder(4,1.5,1.5,128).translate([-19,0,22])+md.Manifold.cylinder(3.001,2.75,2.75,128).translate([-19,0,26])
    for ref in ['P01','H11','H13','H15']:
        vol=(seated^parts[ref]['object']).volume()
        rows.append(dict(name='Complete seated H21 release0..0.001mm envelope',target=ref,status='PASS'if vol<=.01 else'FAIL',intersection_volume_upper_bound_mm3=vol,scope='Complete analytic shaft/head vertical sweep; exact zero-volume initial shoulder seating.'))
    # Both case screw heads can be approached directly from below.
    for y in [-59,59]:
        tool=md.Manifold.cylinder(35.8,1.5,1.5,96).translate([-26.5,y,-29])
        vol=(tool^frame).volume()
        rows.append(dict(name='Case underside M2 driver approach',side_y_mm=y,status='PASS' if vol<=.01 else 'FAIL',intersection_volume_mm3=vol,scope='3mm driver shaft endingZ6.8 below nominal case screw seatZ7; lift device clear of bench.'))
    return rows


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--native-archive',type=Path);ap.add_argument('--output',type=Path);args=ap.parse_args()
    native=bool(args.native_archive)
    inp=args.native_archive or R9/'native/Flat132_R9_neutral_final.zip'
    parts,ignored=v.load(inp,{})
    assert not ignored,ignored
    assert not {r:x.get('error') for r,x in parts.items() if x.get('error') and r not in v.SPRINGS}
    if not native:parts=preflight(parts)
    assert 'P01'in parts and 'P02'not in parts
    m=json.loads((R5/'manifest.json').read_text());m['service_sweeps']=specs(parts)
    rows=v.service_sweeps(parts,m)
    # P09 and P08 share their intentionally seated boundary initially. The
    # unchanged0.8mm plain lid separates upward. Record exact zero-volume
    # sweep result without inventing a nonzero clearance requirement.
    checks=tools(parts)
    bad=[x for x in rows if x['status']in BAD]+[x for x in checks if x['status']=='FAIL']
    out=dict(status=('PASS_NATIVE_SERVICE_PATHS' if native else 'PASS_LOCAL_SERVICE_PREFLIGHT') if not bad else 'FAIL',scope='Finite declared unloaded assembly/removal paths and conservative tool envelopes, fixed integrated P01 palm. Native mode uses fresh exported meshes; local mode is independent literal CSG, not native regeneration.',input=str(inp.resolve()),input_sha256=sha(inp),source_sha256=sha(STUDY/'fingerworker_flat132_integrated_palm.fs'),validator_sha256=sha(Path(__file__)),native=native,part_count=len(parts),declared_service_paths=m['service_sweeps'],checks=rows,tool_checks=checks,failed_count=len(bad),failures=bad,tool_source=dict(title='STAHLWILLE ELECTRIC12 5.5mm,40065555',url='https://stahlwille.com/de_de/products/detail/870426',verified_date='2026-11-03',manufacturer_dimensions_mm=dict(thickness=2,width=12.6,length=78)),limitations=['No spring/load/strength/creep qualification. All service is unloaded and stored energy removed/restrained.','Flexible wiring/connector slack and actual wrench jaw contour, hand access and printed tolerances must be checked physically.','The wrench box is a conservative enclosing access envelope; it is allowed to intersect the target nut only.','Case remains removable downward; its lid opens only after detaching the complete case.'])
    path=args.output or HERE/('service-native.json' if native else 'service-preflight.json');v.write(path,out)
    print(json.dumps(dict(status=out['status'],native=native,paths=len(m['service_sweeps']),pair_checks=len(rows),tool_checks=len(checks),failed=len(bad),failures=[dict(name=x['name'],pair=x.get('pair'),side=x.get('side'),status=x['status'],maximum_sampled_volume_mm3=x.get('maximum_sampled_volume_mm3'),intersection_volume_mm3=x.get('intersection_volume_mm3')) for x in bad]),indent=2),flush=True)
    return 1 if bad else 0


if __name__=='__main__':raise SystemExit(main())
