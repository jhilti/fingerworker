#!/usr/bin/env python3
"""Native R14 fixed support and rear-gate continuous envelope certificates."""
from pathlib import Path
import argparse,importlib.util,json,hashlib,sys
import numpy as np
HERE=Path(__file__).resolve().parent;STUDY=HERE.parent;ROOT=STUDY.parents[1]
sys.path.insert(0,str(ROOT/'review/simplification-2026-11-03'));import rear_gate as rear
b,r7=rear.b,rear.r7
from OCP.BRepCheck import BRepCheck_Analyzer

sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def union(ss):
    s=ss[0]
    for t in ss[1:]:s=b.fuse(s,t)
    return s

def validvolume(s):
    assert BRepCheck_Analyzer(s).IsValid(),'Invalid Boolean result'
    return b.volume(s)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source-sha',required=True,help='Source SHA explicitly bound to this native export by the UI operator');args=ap.parse_args()
    assert len(args.source_sha)==64 and all(c in '0123456789abcdef' for c in args.source_sha)
    assert sha(STUDY/'fingerworker_R14_near_palm.fs')==args.source_sha,'Current source differs from UI-bound export source'
    inv=json.loads((HERE/'native-step-inventory.json').read_text())
    assert sha(inv['native_step'])==inv['native_step_sha256']
    ss,_,_=b.read_step(inv['native_step']);n={r:ss[x['candidates'][0]['solid_index']] for r,x in inv['native_part_correspondence'].items()}
    rows=[]
    def add(name,ok,**e):rows.append(dict(name=name,status='PASS' if bool(ok) else 'FAIL',**e))
    def write(status):
        result=dict(status=status,native_step_sha256=inv['native_step_sha256'],native_stl_archive_sha256=inv['native_stl_archive_sha256'],
            source_sha256=args.source_sha,validator_sha256=sha(__file__),checks=rows,
            limitations='Native nominal geometry only. Conservative envelopes certify declared rigid translations and bounded latch deflection; no material/force/creep qualification.')
        (HERE/'native-motion.json').write_text(json.dumps(result,indent=2)+'\n')
    # Exact conservative partition of native H12. Each convex box extends its
    # positive X end byδ, hence contains every intermediate translated box.
    delta=.001
    covers=[b.box([-12,-15,3],[-8.65+delta,15,33]),
            b.box([-15.5,-15,4.5],[-12+delta,-11.5,11]),
            b.box([-15.5,11.5,4.5],[-12+delta,15,11])]
    envelope=union(covers)
    missing=validvolume(b.cut(n['H12'],envelope))
    overlap=validvolume(b.common(envelope,n['P01']))
    add('Complete H12 initial release envelope0..0.001mm',missing<1e-6 and overlap<1e-6,
        uncovered_native_volume_mm3=missing,complete_envelope_intersection_upper_bound_mm3=overlap,
        travel_interval_mm=[0,.001],direction=[1,0,0],all_boolean_results_valid=True,
        covers_bounds_mm=[b.bounds(s).tolist() for s in covers],
        proof='Native H12 is contained in a complete union of convex slab/collar and ear boxes. Extending each positive X bound by0.001 contains their complete translational Minkowski sum. The full envelope has no solid intersection with native P01. This includes the exact seated contact, not sampled poses.')
    write('INITIAL_RELEASE_CERTIFICATE_PASS_REMAINING_CHECKS_PENDING' if rows[-1]['status']=='PASS' else 'FAIL')
    print('Initial H12 release',rows[-1]['status'],flush=True)
    # Actual complete native frame and plate, not local stock substitutes.
    probes=[]
    for d in [.001,.01]:
        c=b.common(r7.tr(n['P01'],[d,0,0]),n['H12']);vol=validvolume(c)
        probes.append(dict(probe_shift_mm=d,area_mm2=vol/d))
    gap=b.gap(n['P01'],n['H12'])
    add('Native fixed reaction plane contacts H12',gap<1e-6 and all(abs(x['area_mm2']-454.4)<1e-3 for x in probes),
        nominal_gap_mm=gap,area_probes=probes,method='Positive-shift copies for contact area only; nominal parts remain unshifted.')
    for ref in ['P05','H01','H02','H23']:
        gap=b.gap(n['P01'],n[ref]);ov=validvolume(b.common(n['P01'],n[ref]))
        add('Native frame does not bypass sensor through '+ref,gap>1e-6 and ov<1e-6,gap_mm=gap,overlap_mm3=ov)
    # Conservative complete envelope of the rear gate after releasing both
    # latches. Four H30 bolts are removed. No sample spacing is treated as proof.
    gate=n['P06'];released=gate;hooks=[]
    for sign in [-1,1]:
        yl,yh=([-68,-65] if sign<0 else [65,68])
        clip=b.box([104.7,yl,4.4],[108.001,yh,7.6])
        h=b.common(gate,clip);assert validvolume(h)>0
        released=b.cut(released,clip);hooks.append((sign,h))
    for sign,h in hooks:released=b.fuse(released,r7.tr(h,[0,sign*.9,0]))
    pieces=[]
    for sign in [-1,1]:
        y=sign*51
        cap=b.cut(b.box([119,y-14,4.5],[141,y+14,28]),r7.cyl([118.8,y,18],[126.2,y,18],3.1))
        pieces.append(cap)
        def yy(lo,hi):return [lo,hi] if sign>0 else [-hi,-lo]
        lo,hi=yy(64.8,67.6);pieces.append(b.box([126,lo,4.5],[141,hi,8]))
        lo,hi=yy(66.4,68.5);pieces.append(b.box([108,lo,4.5],[139,hi,7.5]))
        # While axially seated, the whole hook can move outward from0..0.9.
        # Its rear face remains before the frame catch atX108.2. Only after
        # reaching0.9mm is the hook withdrawn axially in the following box.
        lo,hi=yy(65.6,68.5);pieces.append(b.box([104.7,lo,4.5],[108.001,hi,7.5]))
        lo,hi=yy(66.5,68.5);pieces.append(b.box([104.7,lo,4.5],[120.001,hi,7.5]))
    pieces.append(b.box([125,-51,4.5],[141,51,10]))
    gateenv=union(pieces)
    missing=validvolume(b.cut(released,gateenv))
    add('Released native gate is contained in conservative assembly envelope',missing<1e-6,
        uncovered_volume_mm3=missing,translation_range_mm=[0,12],hook_deflection_mm=.9,
        proof='Caps, rear crossbar and root stocks extend their +X bounds by12. Beam boxes include all bounded outward deflection0..0.9. Separate hook boxes cover the complete outward flex while seated, then every axial withdrawal pose after0.9mm deflection. Rod bores remain conservatively open only throughX126.2, beyond the rod tipsX125.')
    for ref,s in n.items():
        if ref=='P06' or ref.startswith('H30'):continue
        aa,bb=b.bounds(gateenv),b.bounds(s)
        if np.any(aa[1]<bb[0]) or np.any(bb[1]<aa[0]):continue
        ov=validvolume(b.common(gateenv,s))
        add('Complete native gate release envelope / '+ref,ov<1e-6,intersection_upper_bound_mm3=ov,travel_range_mm=[0,12])
    for sign,h in hooks:
        ov=validvolume(b.common(r7.tr(h,[.3,0,0]),n['P01']))
        add('Native latch retains before0.3mm axial withdrawal '+str(sign),ov>1e-6,restraining_overlap_mm3=ov)
    # Finite strap ends use one2mm layer through each eye, then a4mm exterior
    # double-back envelope. Actual native frame contact at Z4/Y+/-78 is allowed;
    # positive overlap is not. Analytic envelopes contain whole motion domains.
    spec=importlib.util.spec_from_file_location('r14_strap_geometry',STUDY/'mechanics/near_palm.py')
    c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
    routes=c.strap_geometry()['routes']
    for i,route in enumerate(routes):
        shape=route['shape'];rb=b.bounds(shape)
        for ref,s in n.items():
            sb=b.bounds(s)
            if np.any(rb[1]<sb[0]) or np.any(sb[1]<rb[0]):continue
            ov=validvolume(b.common(shape,s))
            add('Finite strap route '+str(i)+' / native '+ref,ov<1e-6,intersection_mm3=ov,
                single_ribbon_mm=2,external_fold_mm=4,route_bounds_mm=rb.tolist())
        for ref in ['P04','H060','H061','P11','H10']:
            lo,hi=(-30.8,.8) if ref in ['P11','H10'] else (-30.,0.)
            bb=b.bounds(n[ref]);bb[0,0]+=lo;bb[1,0]+=hi
            sweep=b.box(bb[0],bb[1]);gap=b.gap(shape,sweep)
            add('Complete finite strap route '+str(i)+' / '+ref+' stroke envelope',gap>1e-6,gap_lower_bound_mm=gap,
                translation_range_mm=[lo,hi],proof='The native body bounding box extended by the full translation interval contains every intermediate pose. This complete conservative box is separated from the finite strap envelope.')
        gap=b.gap(shape,gateenv)
        add('Complete finite strap route '+str(i)+' / gate release envelope',gap>1e-6,gap_lower_bound_mm=gap,
            proof='Separated from the complete gate flex0..0.9mm and withdrawal0..12mm envelope certified above.')
        tray=b.bounds(n['P08']);tray[0,2]-=20;tray[0,1]-=.6;tray[1,1]+=.6
        gap=b.gap(shape,b.box(tray[0],tray[1]))
        add('Complete finite strap route '+str(i)+' / tray removal envelope',gap>1e-6,gap_lower_bound_mm=gap,
            proof='Native tray bounding box enlarged by both0.6mm latch deflections and full downward20mm removal is disjoint from the finite strap route.')
    # Complete-domain translation checks on the actual native STL members.
    # The original switch actuator and compressing springs keep their previous
    # qualified *geometry* scope via exact R11 body identity; they are not
    # incorrectly treated here as static bodies during motion.
    path=ROOT/'review/flat132-reach-fit-2026-10-23/validation/validate_finished.py'
    spec=importlib.util.spec_from_file_location('r12_motion_mesh',path);v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
    archive=STUDY/'native/Flat132_R14_neutral_final.zip'
    assert sha(archive)==inv['native_stl_archive_sha256']
    parts,ignored=v.load(archive,{})
    assert not ignored
    moving=['P04','H060','H061','P11','H10']
    fixed=['P01','P06','P05','H040','H041','H050','H051','H12','H01','H09','P08','P09']
    for ref in moving:
        lo,hi=(-30.8,.8) if ref in ['P11','H10'] else (-30.,0.)
        for target in fixed:
            aa=parts[ref]['object'];bb=parts[target]['object']
            if target=='P06':
                result=v.partitioned_relative_sweep(aa,bb,lo,hi,.01,.03125,
                    {'axis':1,'planes_mm':[-65.6,-63,-37,37,63,65.6]})
            else:result=v.relative_sweep(aa,bb,lo,hi,.01,.03125)
            ok=result['status'] not in ['INTERFERENCE','UNCHECKED','UNRESOLVED_NEAR_CONTACT']
            add('Full native movement '+ref+' / '+target,ok,certificate=result,
                scope='Complete user stroke0..30mm; P11/H10 also include all physical cam trim−0.8..+0.8mm. Native mesh numerical volume tolerance0.01mm³.')
            print('Native motion',ref,target,result['status'],flush=True)
    write('PASS_NATIVE_FIXED_SUPPORT_AND_FULL_TRANSLATIONAL_MOTION' if all(x['status']=='PASS' for x in rows) else 'FAIL')
    print(json.dumps(dict(status='PASS' if all(x['status']=='PASS' for x in rows) else 'FAIL',checks=len(rows),failed=[x for x in rows if x['status']=='FAIL']),indent=2),flush=True)

if __name__=='__main__':main()
