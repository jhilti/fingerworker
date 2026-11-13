#!/usr/bin/env python3
"""Independent literal-CSG and exact native BRep identity for R10.

Uses frozen R9 STEP as its only geometric baseline, never executes the R10
source builder and never edits CAD. Also exports byte-identical native STLs.
"""
from pathlib import Path
import argparse, hashlib, json, sys, zipfile
import numpy as np

HERE=Path(__file__).resolve().parent;STUDY=HERE.parent;ROOT=STUDY.parents[1]
R9=ROOT/'review/flat132-palm-bracing-2026-10-25'
sys.path.insert(0,str(R9/'validation'))
import audit_palm_bracing as prior
b=prior.b;r7=prior.r7;v=prior.v
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepPrimAPI import BRepPrimAPI_MakeCone
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCP.TopAbs import TopAbs_SOLID,TopAbs_SHELL
from OCP.gp import gp_Ax2,gp_Pnt,gp_Dir,gp_Trsf
from OCP.Interface import Interface_Static
from OCP.STEPControl import STEPControl_Writer,STEPControl_AsIs

TOL=1e-6
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
CHANGED={'P01','P02','H15','H160','H161','H170','H171'}


def cone(x0,x1,y,z,r0,r1):
    return BRepPrimAPI_MakeCone(gp_Ax2(gp_Pnt(x0,y,z),gp_Dir(1,0,0)),r0,r1,x1-x0).Shape()


def overlap(a,c):
    return 0. if v.separated(b.bounds(a),b.bounds(c)) else b.volume(b.common(a,c))


def literal(old):
    frame=old['P01'];palm=old['P02'];keeper=old['H15']
    for y in [-31.5,31.5]:
        frame=b.cut(frame,b.box([-22,y-3,6.3],[-20,y+3,8]))
        frame=b.fuse(frame,r7.cyl([-16,y,.2],[-16,y,6.5],2.6))
        palm=b.fuse(palm,b.box([-23,y-5.5,6.3],[-9.5,y+5.5,6.5]))
        palm=b.fuse(palm,b.box([-22.25,y-3.25,6.4],[-19.75,y+3.25,8.3]))
        palm=b.fuse(palm,r7.cyl([-16,y,6.3],[-16,y,10.5],2.2))
        palm=b.fuse(palm,r7.cyl([-16,y,10.5],[-16,y,14.5],4))
        frame=b.cut(frame,b.box([-17,y-5.5,4],[-8.9,y+5.5,6.6]))
        palm=b.cut(palm,b.box([-17,y-5.5,6.3],[-9.4,y+5.5,14.6]))
    for lo,hi in [(-25,-18),(18,25)]:
        palm=b.fuse(palm,b.box([-22.75,lo,14],[-22.55,hi,27]))
    palm=b.cut(palm,b.box([-25.5,-16.5,9.2],[-23.1,16.5,14.7]))
    changed={}
    for i,y in enumerate([-11,11]):
        frame=b.fuse(frame,b.box([-18,y-2.85,21.15],[-16,y+2.85,26.85]))
        frame=b.cut(frame,r7.cyl([-23,y,24],[-15.8,y,24],1.7))
        frame=b.cut(frame,cone(-18.5,-17,y,24,1.5,3))
        frame=b.cut(frame,r7.cyl([-17,y,24],[-15.8,y,24],3.2))
        keeper=b.fuse(keeper,cone(-23,-21.5,y,24,3,1.5))
        keeper=b.cut(keeper,r7.cyl([-24,y,24],[-20,y,24],1.7))
        mirror=gp_Trsf();mirror.SetMirror(gp_Ax2(gp_Pnt(-20,0,0),gp_Dir(1,0,0)))
        changed[f'H16{i}']=BRepBuilderAPI_Transform(old[f'H16{i}'],mirror,True).Shape()
        changed[f'H17{i}']=r7.tr(old[f'H17{i}'],[-6.9,0,0])
    for y0,y1 in [(-66.5,-38.8),(38.8,66.5)]:
        frame=b.cut(frame,r7.cyl([-12.8,y0,8.5],[-12.8,y1,8.5],3.2))
    return dict(P01=b.fuse(frame,palm),H15=keeper,**changed)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--step',type=Path,required=True);ap.add_argument('--archive',type=Path,required=True);args=ap.parse_args()
    inv=json.loads((R9/'validation/native-step-inventory.json').read_text())
    assert sha(inv['native_step'])==inv['native_step_sha256']
    oldshapes,_,_=b.read_step(Path(inv['native_step']))
    old={r:oldshapes[x['candidates'][0]['solid_index']] for r,x in inv['native_part_correspondence'].items()}
    print('Frozen R9 STEP loaded',len(old),flush=True)
    parts,ignored=v.load(args.archive,{})
    assert not ignored,ignored
    shapes,inventory,roots=b.read_step(args.step)
    association=b.associate(shapes,inventory,parts)
    assert all(x['status']=='PASS' and len(x['candidates'])==1 for x in association.values())
    native={r:shapes[x['candidates'][0]['solid_index']] for r,x in association.items()}
    rows=[]
    def add(name,test,**e):rows.append(dict(name=name,status='PASS' if test else 'FAIL',**e))
    add('Native inventory matches R9 minus separate P02',len(native)==122 and set(native)==set(old)-{'P02'},native_count=len(native),device_count=sum(not r.startswith(('E','PCB_')) for r in native),electronics_reference_count=sum(r.startswith(('E','PCB_')) for r in native))
    add('Every native body is a valid positive solid',all(x['valid'] and x['volume_mm3']>0 for x in inventory))
    add('Integrated P01 is exactly one valid solid and shell',BRepCheck_Analyzer(native['P01']).IsValid() and b.count(native['P01'],TopAbs_SOLID)==b.count(native['P01'],TopAbs_SHELL)==1,solid_count=b.count(native['P01'],TopAbs_SOLID),shell_count=b.count(native['P01'],TopAbs_SHELL))
    expected=literal(old)
    print('Independent literal R10 CSG built',flush=True)
    for ref,want in expected.items():
        delta=b.xor_volume(native[ref],want)
        add('Exact independent literal CSG '+ref,delta<=TOL,ref=ref,symmetric_difference_mm3=delta)
        print(ref,'CSG symmetric difference',delta,flush=True)
    identity=[]
    for ref in sorted(set(old)-CHANGED):
        delta=b.xor_volume(native[ref],old[ref]);identity.append(dict(ref=ref,status='PASS' if delta<=TOL else 'FAIL',symmetric_difference_mm3=delta))
    add('All116 other native BReps unchanged',len(identity)==116 and all(x['status']=='PASS' for x in identity),count=len(identity))
    wrist=b.box([-60,-65,9.5],[-27.00001,65,31])
    delta=b.xor_volume(b.common(native['P01'],wrist),b.common(old['P02'],wrist))
    add('Exact curved wrist contact retained',delta<=TOL,symmetric_difference_mm3=delta)
    gap=b.gap(native['P01'],native['P09'])
    add('Complete integrated palm retains0.6mm lid gap',abs(gap-.6)<1e-6,minimum_gap_mm=gap)
    for y0,y1 in [(-37,-26),(26,37)]:
        vol=overlap(native['P01'],b.box([-23,y0,6.3],[-17,y1,6.5]))
        add('Positive6x11x0.2 integral palm-foot connection',abs(vol-13.2)<TOL,side_y_range_mm=[y0,y1],volume_mm3=vol)
    for y0,y1 in [(-25,-18),(18,25)]:
        vol=overlap(native['P01'],b.box([-22.75,y0,14],[-22.55,y1,27]))
        add('Positive7x13x0.2 integral portal-brace connection',abs(vol-18.2)<TOL,side_y_range_mm=[y0,y1],volume_mm3=vol)
    # Whole exact continuous seated screw envelope for0<=dx<=0.05mm.
    # There is no mesh-tessellation exception in this BRep certificate.
    for i,y in enumerate([-11,11]):
        env=r7.union([r7.cyl([-25,y,24],[-18.5,y,24],1.5),cone(-18.5,-17,y,24,1.5,3),r7.cyl([-17,y,24],[-16.95,y,24],3)])
        for ref in ['P01','H11','H15',f'H17{i}']:
            ov=overlap(env,native[ref]);add('Exact seated screw0..0.05mm complete envelope',ov<=TOL,screw=f'H16{i}',obstacle=ref,intersection_upper_bound_mm3=ov)
    # The exact enclosing wrench head/shaft access volume, not sampled poses.
    for i,y in enumerate([-11,11]):
        tool=b.box([-25.5,y-6.5,17],[-23.5,y+6.5,65])
        for ref in ['P01','H15','H11']:
            ov=overlap(tool,native[ref]);gap=b.gap(tool,native[ref]);add('Exact complete slim AF5.5 wrench access envelope',ov<=TOL and gap>=.299999,side=i,obstacle=ref,intersection_upper_bound_mm3=ov,minimum_gap_mm=gap)
    for i,side in [(0,-1),(1,1)]:
        if side==1:env=r7.union([r7.cyl([-12.8,13,8.5],[-12.8,21,8.5],1.5),r7.cyl([-12.8,21,8.5],[-12.8,24.001,8.5],2.75)])
        else:env=r7.union([r7.cyl([-12.8,-21,8.5],[-12.8,-13,8.5],1.5),r7.cyl([-12.8,-24.001,8.5],[-12.8,-21,8.5],2.75)])
        for ref in ['P01',f'H19{i}']:
            ov=overlap(env,native[ref]);add('Exact complete seated H18 release0..0.001mm envelope',ov<=TOL,screw=f'H18{i}',obstacle=ref,intersection_upper_bound_mm3=ov)
        y0,y1=(23.9,90)if side==1 else(-90,-23.9)
        for r,label in [(1.5,'2.5mm hex driver'),(2.75,'whole5.5mm cap head')]:
            tool=r7.cyl([-12.8,y0,8.5],[-12.8,y1,8.5],r);ov=overlap(tool,native['P01']);add('Exact H18 access through outer rod block: '+label,ov<=TOL,side=side,intersection_upper_bound_mm3=ov)
    env=r7.union([r7.cyl([-19,0,22],[-19,0,26],1.5),r7.cyl([-19,0,26],[-19,0,29.001],2.75)])
    for ref in ['P01','H11','H13','H15']:
        ov=overlap(env,native[ref]);add('Exact complete seated H21 release0..0.001mm envelope',ov<=TOL,obstacle=ref,intersection_upper_bound_mm3=ov)
    device={r:parts[r] for r in parts if not r.startswith(('E','PCB_'))}
    printrefs=set(json.loads((R9/'print-mm/part-manifest.json').read_text())['parts'])-{'P02'}
    output=STUDY/'print-mm';output.mkdir(exist_ok=True)
    manifest={}
    with zipfile.ZipFile(args.archive) as z:
        for ref in sorted(printrefs):
            member=parts[ref]['member'];raw=z.read(member);target=output/(ref+'.stl');target.write_bytes(raw)
            manifest[ref]=dict(native_member=member,output='print-mm/'+target.name,sha256=sha(target),bytes=len(raw))
    v.write(output/'part-manifest.json',dict(source_sha256=sha(STUDY/'fingerworker_flat132_integrated_palm.fs'),native_zip=str(args.archive.resolve()),native_zip_sha256=sha(args.archive),units='mm',orientation='Original native assembly coordinates; no rescaling, repair, remeshing or slicing.',identity='Every output STL is byte-identical to its named fresh whole R10 native ZIP member.',count=len(manifest),changed_since_R9=['P01'],removed_since_R9=['P02'],flexible_refs=['P070a','P070b','P071a','P071b'],parts=manifest))
    # The simple H15 CAD file retains exact native geometry and assembly axes.
    # P01 is delivered in the original whole native STEP. OCCT8's optional
    # local P01 reserialization produced valid equal-volume geometry, but its
    # coincident B-spline Boolean roundtrip was not reproducible. Those
    # diagnostics are isolated outside the delivery, never certified here.
    mech=STUDY/'mechanical-mm';mech.mkdir(exist_ok=True);mechanical={}
    Interface_Static.SetCVal_s('write.step.schema','AP214IS')
    Interface_Static.SetIVal_s('write.precision.mode',1)
    Interface_Static.SetRVal_s('write.precision.val',1e-9)
    for ref in ['H15']:
        target=mech/(ref+'.step');writer=STEPControl_Writer()
        assert str(writer.Transfer(native[ref],STEPControl_AsIs)).endswith('RetDone')
        assert str(writer.Write(str(target))).endswith('RetDone')
        roundtrip,_,_=b.read_step(target);delta=b.xor_volume(roundtrip[0],native[ref])if len(roundtrip)==1 else float('inf')
        add('Individual AP214 STEP roundtrip '+ref,len(roundtrip)==1 and delta<=TOL,ref=ref,symmetric_difference_mm3=delta)
        mechanical[ref]=dict(file=target.name,sha256=sha(target),units='mm',coordinates='Original native assembly coordinates; no transform or geometry repair.',native_step_sha256=sha(args.step),roundtrip_symmetric_difference_mm3=delta)
    v.write(mech/'part-manifest.json',dict(source_sha256=sha(STUDY/'fingerworker_flat132_integrated_palm.fs'),parts=mechanical,p01_cad='Use P01 within the original whole native/Flat132_R10_final_AP214.step; no locally reserialized individual P01 STEP is supplied.'))
    nativeinv=dict(status='PASS' if all(x['status']=='PASS' for x in rows) else 'FAIL',scope='All STEP solids valid and uniquely associated to native STL by bounds/volume; exact independent changed-part CSG and116 unchanged BRep identities.',native_step=str(args.step.resolve()),native_step_sha256=sha(args.step),native_stl_archive=str(args.archive.resolve()),native_stl_archive_sha256=sha(args.archive),transferred_roots=roots,native_step_solids=len(shapes),native_stl_parts=len(parts),valid_positive_solids=sum(x['valid'] and x['volume_mm3']>0 for x in inventory),solid_inventory=inventory,native_part_correspondence=association)
    v.write(HERE/'native-step-inventory.json',nativeinv)
    failed=[x for x in rows+identity if x['status']=='FAIL']
    report=dict(status='PASS_EXACT_NATIVE_R10_GEOMETRY' if not failed else 'FAIL',source_sha256=sha(STUDY/'fingerworker_flat132_integrated_palm.fs'),baseline_source_sha256='16972ba9341f4cdf763a5570dad82a4fbd601f0935d0a7657be85813f97ff2b1',native_step_sha256=sha(args.step),native_zip_sha256=sha(args.archive),validator_sha256=sha(Path(__file__)),checks=rows,unchanged_native_breps=identity,failed_count=len(failed),failures=failed,limitations=['Finite nominal CAD geometry; no load, fatigue, creep, comfort, sensor calibration or actual manufactured fits qualified.','The source/native export association is declared by the root operator. This script does not regenerate Onshape.'])
    v.write(HERE/'native-geometry.json',report)
    print(json.dumps(dict(status=report['status'],native_solids=len(shapes),device=len(device),print_parts=len(printrefs),unchanged_breps=len(identity),failed=len(failed),failures=failed),indent=2),flush=True)
    return 1 if failed else 0


if __name__=='__main__':raise SystemExit(main())
