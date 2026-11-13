#!/usr/bin/env python3
"""R16 independent interface checks and exact native/candidate binding.

Only P01 may change. The frozen R15 native assembly is the identity baseline.
The changing contact skin is checked separately from protected functional stock.
"""
from pathlib import Path
import argparse, importlib.util, json, hashlib, sys, zipfile
import numpy as np

HERE=Path(__file__).resolve().parent;STUDY=HERE.parent;ROOT=STUDY.parents[1]
def module(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
rear=module('r16_validation_rear',ROOT/'review/simplification-2026-11-03/rear_gate.py')
b=rear.b
v=module('r16_validation_mesh',ROOT/'review/flat132-reach-fit-2026-10-23/validation/validate_finished.py')
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.TopAbs import TopAbs_SOLID,TopAbs_SHELL
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
SOURCE=STUDY/'fingerworker_R16_upright_grip.fs'
BASE=ROOT/'review/inboard-straps-2026-11-08'

def load_baseline():
    inv=json.loads((BASE/'validation/native-step-inventory.json').read_text())
    assert sha(inv['native_step'])==inv['native_step_sha256']
    ss,_,_=b.read_step(inv['native_step'])
    return {r:ss[x['candidates'][0]['solid_index']] for r,x in inv['native_part_correspondence'].items()},inv

def volume(shape):
    assert BRepCheck_Analyzer(shape).IsValid(),'Invalid Boolean result'
    return b.volume(shape)

def difference(a,c):
    return volume(b.cut(a,c))+volume(b.cut(c,a))

def interfaces(frame,old):
    rows=[]
    def add(name,ok,**e):rows.append(dict(name=name,status='PASS' if bool(ok) else 'FAIL',**e))
    add('One connected valid P01 solid and shell',BRepCheck_Analyzer(frame).IsValid() and b.count(frame,TopAbs_SOLID)==b.count(frame,TopAbs_SHELL)==1)
    removed=b.cut(old['P01'],frame);added=b.cut(frame,old['P01'])
    add('P01 changes are meaningful',volume(removed)+volume(added)>1.,removed_mm3=volume(removed),added_mm3=volume(added))
    ledge_cut=b.box([-40,-70,11.5],[-29,70,14.5])
    structural_removal=b.cut(removed,ledge_cut)
    zones=[('electronics roof',b.box([-60,-70,-3],[-23.5,70,14.5])),
           ('negative tray catch landing',b.box([-30,-66,9.4],[-24,-62,16.5])),
           ('positive tray catch landing',b.box([-30,62,9.4],[-24,66,16.5])),
           ('central sensor reaction and guides below Z30',b.box([-22.75,-25.4,-3],[2,25.4,30])),
           ('negative front rod socket block',b.box([-18,-63,3.8],[-8,-39,28])),
           ('positive front rod socket block',b.box([-18,39,3.8],[-8,63,28]))]
    for name,zone in zones:
        rv=volume(b.common(structural_removal,zone))
        add('Original functional material retained: '+name,rv<1e-6,removed_mm3=rv,exception='Explicit obsolete roof step X-40..-29,Z11.5..14.5 only')
    for sign in [-1,1]:
        yl,yh=sorted([sign*62,sign*66])
        catch=b.box([-29,yl,9.4],[-24,yh,16.5])
        rv=volume(b.common(removed,catch))
        add('Entire active electronics catch landing retained '+str(sign),rv<1e-6,removed_mm3=rv)
    roof_core=b.box([-38,-62,9.5],[-29,62,11.5])
    missing=volume(b.cut(roof_core,frame))
    add('Continuous 2mm electronics roof beneath removed step',missing<1e-6,missing_mm3=missing,witness_bounds_mm=b.bounds(roof_core).tolist())
    # Roof/catch/rod voids must stay clear. A top blend may add above the
    # existing socket, but cannot add into its already declared block envelope.
    # New rail root begins atZ14.4, embedding0.1mm into the roof top. At the
    # curved outer roof corners this adds a tiny real transition wedge, so
    # preserve the full original roof above, but reserve voids only below14.4.
    # Actual enclosure contacts/removal are independently checked below.
    clear_zones=[('electronics roof below rail embedding',b.box([-60,-70,-3],[-23.5,70,14.4]))]+zones[4:]
    for name,zone in clear_zones:
        av=volume(b.common(added,zone))
        add('Interface clearance retained: '+name,av<1e-6,added_mm3=av)
    blend=volume(b.common(added,b.box([-60,-70,14.4],[-23.5,70,14.5])))
    add('Roof transition confined to declared 0.1mm embedding',blend<.001,top_transition_added_mm3=blend,allowed_z_mm=[14.4,14.5],scope='Small added corner transition only; no removal of original roof is permitted.')
    # The rail now spans Y+/-63, so an arbitrary broad landing rectangle is
    # not a clearance void. Instead use the actual hooks' entire lateral
    # flex/downward-removal bounding domain. Only additions matter; retained
    # landing material and the original release are independently established.
    for sign in [-1,1]:
        lo,hi=sorted([sign*63.6,sign*66.1])
        envelope=b.box([-29,lo,-20],[-25.6,hi,16.2])
        av=volume(b.common(added,envelope))
        add('No new stock in complete electronics hook flex/removal envelope '+str(sign),av<1e-6,added_intersection_mm3=av,deflection_mm=.6,downward_removal_mm=20)
    # Independently bound all changes to the palm end above its existing roof.
    # This protects the central guide, straps, rear catches and floor in full.
    # Shoulder caps extend2mm beyond the original sockets (Y+/-63) so their
    # rounded ends cover the old square socket corners; they remain inside
    # the existing132mm floor. The central rail stops at Y+/-63 for hook room.
    upper_palm=b.box([-46.2,-65.0001,14.3999],[-7.9999,65.0001,33.0001])
    permitted=b.fuse(upper_palm,ledge_cut)
    rv=volume(b.cut(removed,permitted));av=volume(b.cut(added,permitted))
    add('Only declared upper palm and obsolete roof step change',rv<1e-6 and av<1e-6,removed_outside_mm3=rv,added_outside_mm3=av,upper_palm_bounds_mm=b.bounds(upper_palm).tolist(),ledge_cut_bounds_mm=b.bounds(ledge_cut).tolist())
    bb=b.bounds(frame);ob=b.bounds(old['P01'])
    add('Original floor footprint and crown envelope retained',np.max(np.abs(bb-ob))<1e-6,bounds_mm=bb.tolist(),baseline_bounds_mm=ob.tolist())
    # All seated parts, including the real sensor, wiring reference geometry
    # and tray/lid, remain mutually separate from the changed frame.
    for ref,other in old.items():
        if ref=='P01':continue
        aa,cc=b.bounds(frame),b.bounds(other)
        separated=np.any(aa[1]<cc[0]) or np.any(cc[1]<aa[0])
        ov=0. if separated else volume(b.common(frame,other))
        add('Seated separation P01/'+ref,ov<1e-6,intersection_mm3=ov)
    for ref in ['P05','H01','H02','H23']:
        gap=b.gap(frame,old[ref]);prior=b.gap(old['P01'],old[ref])
        add('Sensor path gap not reduced: '+ref,gap>=prior-1e-6 and gap>1e-6,gap_mm=gap,baseline_gap_mm=prior)
    for sign in [-1,1]:
        y=sign*51
        rodvoid=rear.r7.cyl([-17,y,18],[-7,y,18],3.1)
        ov=volume(b.common(frame,rodvoid))
        add('Intact 6.2mm front rod bore '+str(sign),ov<1e-6,intersection_mm3=ov)
        lo,hi=(-72,-15.3) if sign<0 else (15.3,72)
        tool=rear.r7.cyl([-12.8,lo,8.5],[-12.8,hi,8.5],3.2)
        ov=volume(b.common(added,tool))
        add('H18 side tool route not obstructed '+str(sign),ov<1e-6,added_intersection_mm3=ov)
    for y in [-59,59]:
        pilot=rear.r7.cyl([-26.5,y,9.4],[-26.5,y,13.5],1.6)
        ov=volume(b.common(frame,pilot))
        add('Optional M2 underside pilot open '+str(y),ov<1e-6,intersection_mm3=ov)
    return rows

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--step',type=Path)
    ap.add_argument('--archive',type=Path)
    ap.add_argument('--candidate-only',type=Path)
    ap.add_argument('--source-sha',help='Exact source SHA bound by the UI operator to these native exports')
    args=ap.parse_args()
    old,baseinv=load_baseline()
    if args.candidate_only:
        shapes,inventory,_=b.read_step(args.candidate_only)
        assert len(shapes)==1
        rows=interfaces(shapes[0],old)
        bad=[r for r in rows if r['status']=='FAIL']
        result=dict(status='PASS_LOCAL_CANDIDATE_INTERFACES' if not bad else 'FAIL',candidate_step_sha256=sha(args.candidate_only),baseline_native_step_sha256=baseinv['native_step_sha256'],validator_sha256=sha(__file__),checks=rows,failures=bad,limitations='Local candidate only; no native export binding, full travel or service certification.')
        (HERE/'candidate-interfaces.json').write_text(json.dumps(result,indent=2)+'\n')
        print(json.dumps(dict(status=result['status'],checks=len(rows),failures=bad),indent=2))
        return bool(bad)
    assert args.step and args.archive,'--step and --archive are required for native validation'
    assert args.source_sha==sha(SOURCE),'Current source differs from UI-bound native export source'
    input_hashes=(sha(SOURCE),sha(args.step),sha(args.archive))
    parts,ignored=v.load(args.archive,{})
    assert not ignored
    shapes,inventory,roots=b.read_step(args.step)
    assoc=b.associate(shapes,inventory,parts)
    assert all(x['status']=='PASS' and len(x['candidates'])==1 for x in assoc.values())
    native={r:shapes[x['candidates'][0]['solid_index']] for r,x in assoc.items()}
    rows=[]
    def add(name,ok,**e):rows.append(dict(name=name,status='PASS' if bool(ok) else 'FAIL',**e))
    add('Exact 93-body inventory',set(native)==set(old) and len(native)==93,count=len(native))
    add('All native solids valid positive volumes',all(x['valid'] and x['volume_mm3']>0 for x in inventory))
    candidate=module('r16_candidate_geometry',STUDY/'mechanics/upright_grip.py')
    expected=candidate.expected(old)['P01']
    delta=difference(native['P01'],expected)
    add('Native P01 matches declared local CSG',delta<1e-6,symmetric_difference_mm3=delta)
    print('P01 native-candidate XOR',delta,flush=True)
    checkpoint=STUDY/'native/checkpoint-e296'
    cp_parts,cp_ignored=v.load(checkpoint/'Flat132_R16_neutral_final.zip',{})
    assert not cp_ignored
    cp_shapes,cp_inventory,_=b.read_step(checkpoint/'Flat132_R16_final_AP214.step')
    cp_assoc=b.associate(cp_shapes,cp_inventory,cp_parts)
    assert cp_assoc['P01']['status']=='PASS' and len(cp_assoc['P01']['candidates'])==1
    cp_frame=cp_shapes[cp_assoc['P01']['candidates'][0]['solid_index']]
    cp_trimmed=b.cut(cp_frame,b.box([-40,-70,11.5],[-29,70,14.5]))
    delta=difference(native['P01'],cp_trimmed)
    add('Final native equals approved grip checkpoint minus explicit obsolete step',delta<1e-6,symmetric_difference_mm3=delta,checkpoint_native_step_sha256=sha(checkpoint/'Flat132_R16_final_AP214.step'),cut_bounds_mm=[[-40,-70,11.5],[-29,70,14.5]])
    identities=[]
    for ref in sorted(set(native)-{'P01'}):
        delta=difference(native[ref],old[ref])
        identities.append(dict(ref=ref,status='PASS' if delta<1e-6 else 'FAIL',symmetric_difference_mm3=delta))
    add('All other 92 bodies exact R15 identity',len(identities)==92 and all(x['status']=='PASS' for x in identities),count=len(identities))
    rows+=interfaces(native['P01'],dict(native,P01=old['P01']))
    refs=sorted(r for r in native if r.startswith('P') and not r.startswith('PCB_'))
    add('Seven printed device bodies',refs==['P01','P04','P05','P06','P08','P09','P11'],refs=refs)
    assert input_hashes==(sha(SOURCE),sha(args.step),sha(args.archive)),'An input changed during validation'
    output=STUDY/'print-mm';output.mkdir(exist_ok=True);manifest={}
    with zipfile.ZipFile(args.archive) as z:
        for ref in refs:
            raw=z.read(parts[ref]['member']);target=output/(ref+'.stl');target.write_bytes(raw)
            manifest[ref]=dict(native_member=parts[ref]['member'],sha256=sha(target),bytes=len(raw))
    (output/'part-manifest.json').write_text(json.dumps(dict(source_sha256=sha(SOURCE),native_zip_sha256=sha(args.archive),units='mm',count=len(refs),parts=manifest,identity='Byte-identical native Onshape STL ZIP members in assembly coordinates.'),indent=2)+'\n')
    (HERE/'native-step-inventory.json').write_text(json.dumps(dict(native_step=str(args.step.resolve()),native_step_sha256=sha(args.step),native_stl_archive_sha256=sha(args.archive),native_part_correspondence=assoc,solid_inventory=inventory),indent=2)+'\n')
    bad=[r for r in rows+identities if r['status']=='FAIL']
    report=dict(status='PASS_EXACT_NATIVE_R16' if not bad else 'FAIL',source_sha256=sha(SOURCE),candidate_source_sha256=sha(STUDY/'mechanics/upright_grip.py'),baseline_native_step_sha256=baseinv['native_step_sha256'],native_step_sha256=sha(args.step),native_zip_sha256=sha(args.archive),validator_sha256=sha(__file__),checks=rows,unchanged_native_breps=identities,failed_count=len(bad),failures=bad,limitations='Nominal geometry only. Source/export association declared by UI operator. No physical strength, creep, comfort, thumb fit or snap-cycle qualification.')
    (HERE/'native-geometry.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(status=report['status'],checks=len(rows),unchanged=len(identities),failures=bad),indent=2))
    return bool(bad)

if __name__=='__main__':raise SystemExit(main())
