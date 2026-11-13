#!/usr/bin/env python3
"""Focused R17 integration audit against frozen, validated R16 native solids.

Local mode is explicitly a prototype review. Native mode also binds every
exported body to the intended revision. Unchanged R16 path checks are inherited
only after proving all newly added stock clear of complete swept envelopes.
"""
from pathlib import Path
import argparse, hashlib, importlib.util, json, sys, zipfile
import numpy as np
import trimesh

HERE=Path(__file__).resolve().parent;STUDY=HERE.parent;ROOT=STUDY.parents[1]
BASE=ROOT/'review/upright-grip-2026-11-09'
BASE_SHA='1f492dd841c35a14f488be418e4f4dd8dea8edb63f3d321a492dc2ec3c907ab4'
BASE_VERSION='d4421f391a091e249b08aeb1'
SOURCE=STUDY/'fingerworker_R17_side_thumb.fs'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def module(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
r16=module('r17_frozen_r16_builder',BASE/'mechanics/upright_grip.py');b=r16.b
v=module('r17_mesh_reader',ROOT/'review/flat132-reach-fit-2026-10-23/validation/validate_finished.py')
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.TopAbs import TopAbs_SOLID,TopAbs_SHELL
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon,BRepBuilderAPI_MakeFace
from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism
from OCP.gp import gp_Pnt,gp_Vec

def vol(s):
    assert BRepCheck_Analyzer(s).IsValid(),'Invalid exact Boolean result'
    return b.volume(s)
def difference(a,c):return vol(b.cut(a,c))+vol(b.cut(c,a))
def union(ss):
    out=ss[0]
    for s in ss[1:]:out=b.fuse(out,s)
    return out
def side_box(x0,x1,y0,y1,z0,z1,sign):
    lo,hi=sorted([sign*y0,sign*y1]);return b.box([x0,lo,z0],[x1,hi,z1])
def cheek_domain(sign):
    yz=[(59,16.5),(63,16.5),(65,18.5),(65,24.1),(59,24.1)]
    points=[gp_Pnt(-24,sign*y,z) for y,z in yz]
    if sign<0:points=points[::-1]
    wire=BRepBuilderAPI_MakePolygon()
    for p in points:wire.Add(p)
    wire.Close()
    return BRepPrimAPI_MakePrism(BRepBuilderAPI_MakeFace(wire.Wire()).Face(),gp_Vec(16,0,0)).Shape()

def baseline():
    assert sha(BASE/'fingerworker_R16_upright_grip.fs')==BASE_SHA
    ver=json.loads((BASE/'onshape-version.json').read_text());assert ver['version_id']==BASE_VERSION and ver['source_sha256']==BASE_SHA
    inv=json.loads((BASE/'validation/native-step-inventory.json').read_text())
    assert sha(inv['native_step'])==inv['native_step_sha256']==ver['step_sha256']
    ss,_,_=b.read_step(inv['native_step'])
    parts={r:ss[x['candidates'][0]['solid_index']] for r,x in inv['native_part_correspondence'].items()}
    certs={}
    for name in ['native-geometry.json','native-motion.json','service-native.json','fixture-q01-check.json']:
        p=BASE/'validation'/name;d=json.loads(p.read_text());assert d['status'].startswith('PASS')
        if 'source_sha256' in d:assert d['source_sha256']==BASE_SHA
        certs[name]=dict(sha256=sha(p),status=d['status'])
    return parts,inv,certs

def checks(frame,old,certs):
    rows=[]
    def add(kind,name,ok,**e):rows.append(dict(kind=kind,name=name,status='PASS' if bool(ok) else 'FAIL',**e))
    inc=b.cut(frame,old['P01']);rem=b.cut(old['P01'],frame)
    av,rv=vol(inc),vol(rem)
    add('geometry','One valid connected frame solid/shell',BRepCheck_Analyzer(frame).IsValid() and b.count(frame,TopAbs_SOLID)==b.count(frame,TopAbs_SHELL)==1)
    add('geometry','Only one existing printed part changes',av>0 and rv>0,added_mm3=av,removed_mm3=rv)
    add_allowed=union([cheek_domain(s) for s in [-1,1]])
    remove_allowed=union([side_box(-30,-12.9,60,65.1,19,33.1,s) for s in [-1,1]])
    outside_add=vol(b.cut(inc,add_allowed));outside_rem=vol(b.cut(rem,remove_allowed))
    add('geometry','All additions remain inside explicit tapered cheek domains',outside_add<1e-6,unexpected_added_mm3=outside_add)
    add('geometry','All removals remain inside declared upper outside thumb regions',outside_rem<1e-6,unexpected_removed_mm3=outside_rem)
    add('geometry','Existing assembly footprint and palm crown retained',np.max(np.abs(b.bounds(frame)-b.bounds(old['P01'])))<1e-6,bounds_mm=b.bounds(frame).tolist())
    # Original wrist-side returns are retained, including their native R0.8
    # mouth radii. The uncut profile only bounds those voids; the native frame
    # determines the actual pocket shape used for the wall measurement.
    raw=r16.profile(-63,63,r16.RAIL_LINES,r16.RAIL_ARCS,3,[r16.RAIL_MID])
    voids=b.cut(raw,old['P01'])
    for sign in [-1,1]:
        pocket=b.common(voids,side_box(-30,-24.5,42,60,14,26,sign))
        side_rem=b.common(rem,side_box(-40,0,40,70,0,40,sign))
        web=b.gap(side_rem,pocket)
        add('geometry','Residual web to existing back pocket '+str(sign),web>=3-1e-6,minimum_wall_mm=web,geometric_design_target_mm=3,meaning='Geometric spacing between voids; not a strength qualification')
        add('geometry','Existing back pocket is not filled '+str(sign),vol(b.common(inc,pocket))<1e-6)
        bore=r16.r7.cyl([-17,sign*51,18],[-7,sign*51,18],3.1)
        wall=b.gap(side_rem,bore)
        add('geometry','Rod bore wall stays outside scallop '+str(sign),wall>=6,minimum_removed_to_bore_mm=wall,geometric_design_target_mm=6)
        add('geometry','Rod bore remains open '+str(sign),vol(b.common(frame,bore))<1e-6)
        core=side_box(-18,-8,44,58,11.7,28,sign)
        add('geometry','Critical inner rod-socket stock retained '+str(sign),vol(b.common(rem,core))<1e-6)
        landing=side_box(-29,-25.6,63.6,64,9.5,14.5,sign)
        add('geometry','Active electronics hook landing unchanged '+str(sign),vol(b.common(rem,landing))+vol(b.common(inc,landing))<1e-6)
        backing=side_box(-23.9,-18.1,59.6,60.5,20,28,sign)
        missing=vol(b.cut(backing,frame))
        add('geometry','Continuous cheek backing across former hollow '+str(sign),missing<1e-6,missing_mm3=missing,witness_bounds_mm=b.bounds(backing).tolist())
        lo,hi=(-72,-15.3) if sign<0 else (15.3,72)
        tool=r16.r7.cyl([-12.8,lo,8.5],[-12.8,hi,8.5],3.2)
        add('service','H18 complete lateral access receives no new stock '+str(sign),vol(b.common(inc,tool))<1e-6)
        add('geometry','H18 passage wall remains clear of cut '+str(sign),b.gap(side_rem,tool)>=3.2,minimum_removed_to_passage_mm=b.gap(side_rem,tool))
    rb=b.bounds(rem)
    add('geometry','Scallop leaves a fixed land before yoke seam',rb[1,0]<=-13,most_forward_cut_x_mm=float(rb[1,0]),minimum_land_to_fixed_front_x_minus8_mm=float(-8-rb[1,0]),meaning='Land geometry only; a real thumb can extend beyond the cut envelope')
    for ref in ['P05','H01','H02','H23']:
        gap=b.gap(frame,old[ref]);before=b.gap(old['P01'],old[ref])
        add('geometry','Sensing gap not reduced '+ref,gap>=before-1e-6 and gap>1e-6,gap_mm=gap,baseline_gap_mm=before)
    # No new static interference anywhere in the preserved assembly.
    for ref,shape in old.items():
        if ref=='P01':continue
        aa,bb=b.bounds(frame),b.bounds(shape)
        if np.any(aa[1]<bb[0]) or np.any(bb[1]<aa[0]):continue
        overlap=vol(b.common(frame,shape))
        add('geometry','Seated frame separation '+ref,overlap<1e-6,overlap_mm3=overlap)
    # A subtractive change cannot obstruct an established motion/service path.
    # Separating the added stock from complete conservative swept bounds makes
    # the inherited R16 certificates applicable without repeating unrelated
    # moving/moving or hardware tests.
    for ref in ['P04','H060','H061','P11','H10']:
        lo,hi=(-30.8,.8) if ref in ['P11','H10'] else (-30,0)
        bb=b.bounds(old[ref]).copy();bb[0,0]+=lo;bb[1,0]+=hi
        sweep=b.box(bb[0],bb[1]);gap=b.gap(inc,sweep)
        add('motion','Added cheek clears full travel '+ref,gap>1e-6,gap_lower_bound_mm=gap,translation_interval_mm=[lo,hi],baseline_certificate=certs['native-motion.json']['sha256'])
    service=json.loads((BASE/'validation/service-native.json').read_text())
    for route in service['declared_paths']:
        for ref in route['moving_refs']:
            bb=b.bounds(old[ref]).copy();offset=np.array(route.get('initial_translation_mm',[0,0,0]),float)
            v0=offset+np.array(route['direction'])*route['range_mm'][0]
            v1=offset+np.array(route['direction'])*route['range_mm'][1]
            bb[0]+=np.minimum(v0,v1);bb[1]+=np.maximum(v0,v1)
            gap=b.gap(inc,b.box(bb[0],bb[1]))
            add('service',route['name']+' / added stock / '+ref,gap>1e-6,gap_lower_bound_mm=gap,full_swept_bounds_mm=bb.tolist(),baseline_certificate=certs['service-native.json']['sha256'])
    tray=b.bounds(old['P08']).copy();tray[0,1]-=.6;tray[1,1]+=.6;tray[0,2]-=20
    gap=b.gap(inc,b.box(tray[0],tray[1]))
    add('service','Full tray outward flex and downward removal clears additions',gap>1e-6,gap_lower_bound_mm=gap,flex_mm=.6,downward_mm=20)
    for sign in [-1,1]:
        sweep=side_box(-29,-25.6,63.6,66.1,-20,16.2,sign);gap=b.gap(inc,sweep)
        add('service','Complete high hook release envelope '+str(sign),gap>1e-6,gap_lower_bound_mm=gap)
    fixture=ROOT/'review/simplification-2026-11-03/fixture'
    fm=json.loads((fixture/'manifest.json').read_text());qpath=fixture/(fm['name']+'_assembly-mm.step')
    q=b.read_step(qpath)[0][0];qb=b.bounds(q).copy();qb[1,2]+=40
    qgap=b.gap(inc,b.box(qb[0],qb[1]))
    add('fixture','Q01 entire 40mm removal path clears additions',qgap>1e-6,gap_lower_bound_mm=qgap,baseline_certificate=certs['fixture-q01-check.json']['sha256'])
    add('fixture','Q01 seating contact region receives no removals',vol(b.common(rem,b.box([-16,-16,2],[2,16,34])))<1e-6)
    add('geometry','Base, strap slots and central guide untouched',vol(b.common(inc,b.box([-60,-80,-3],[140,80,14.4])))+vol(b.common(rem,b.box([-60,-80,-3],[140,80,14.4])))<1e-6)
    return rows

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source-sha',required=True);ap.add_argument('--native-step',type=Path);ap.add_argument('--native-archive',type=Path);ap.add_argument('--mesh',type=Path);args=ap.parse_args()
    assert sha(SOURCE)==args.source_sha
    generator_sha=sha(STUDY/'mechanics/side_thumb.py')
    old,baseinv,certs=baseline();c=module('r17_candidate',STUDY/'mechanics/side_thumb.py');changed=c.expected(old)
    assert set(changed)=={'P01'},'Candidate changes an unexpected part'
    want=changed['P01']
    native=bool(args.native_step or args.native_archive);extra=[];identities=[]
    if native:
        assert args.native_step and args.native_archive
        native_input_hashes=(sha(args.native_step),sha(args.native_archive))
        parts,ignored=v.load(args.native_archive,{});assert not ignored
        shapes,inventory,_=b.read_step(args.native_step);assoc=b.associate(shapes,inventory,parts)
        assert all(x['status']=='PASS' and len(x['candidates'])==1 for x in assoc.values())
        n={r:shapes[x['candidates'][0]['solid_index']] for r,x in assoc.items()};assert set(n)==set(old) and len(n)==93
        frame=n['P01'];delta=difference(frame,want)
        extra.append(dict(kind='geometry',name='Native frame equals declared local candidate',status='PASS' if delta<1e-6 else 'FAIL',symmetric_difference_mm3=delta))
        baseline_zip=BASE/'native/Flat132_R16_neutral_final.zip'
        assert sha(baseline_zip)==json.loads((BASE/'onshape-version.json').read_text())['stl_zip_sha256']
        with zipfile.ZipFile(baseline_zip) as z:
            old_stl_sha={v.identify(name):hashlib.sha256(z.read(name)).hexdigest() for name in z.namelist() if name.lower().endswith('.stl')}
        for ref in sorted(set(old)-{'P01'}):
            d=difference(n[ref],old[ref]);identical=old_stl_sha[ref]==parts[ref]['sha256']
            identities.append(dict(ref=ref,status='PASS' if d<1e-6 and identical else 'FAIL',symmetric_difference_mm3=d,stl_byte_identical=identical,native_stl_sha256=parts[ref]['sha256']))
        old=dict(n,P01=old['P01'])
        mesh=parts['P01']['mesh'] if 'mesh' in parts['P01'] else None
        import io
        with zipfile.ZipFile(args.native_archive) as z:
            raw=z.read(parts['P01']['member']);mesh=trimesh.load(io.BytesIO(raw),file_type='stl',force='mesh')
        binding=dict(native_step_sha256=sha(args.native_step),native_zip_sha256=sha(args.native_archive))
        inv=dict(native_step=str(args.native_step.resolve()),**binding,native_stl_archive_sha256=binding['native_zip_sha256'],native_part_correspondence=assoc,solid_inventory=inventory)
        (HERE/'native-step-inventory.json').write_text(json.dumps(inv,indent=2)+'\n')
    else:
        assert args.mesh,'--mesh required for local prototype review'
        frame=want;mesh=trimesh.load(args.mesh,force='mesh');binding=dict(local_mesh_sha256=sha(args.mesh))
    rows=checks(frame,old,certs)+extra
    rows.append(dict(kind='mesh',name='One watertight positive mesh component',status='PASS' if mesh.is_watertight and mesh.is_volume and len(mesh.split())==1 else 'FAIL',watertight=bool(mesh.is_watertight),positive_volume=bool(mesh.is_volume),components=len(mesh.split()),mesh_volume_mm3=float(mesh.volume)))
    diff=np.max(np.abs(mesh.bounds-b.bounds(frame)))
    verr=abs(mesh.volume-b.volume(frame))
    rows.append(dict(kind='mesh',name='Exported mesh bounds and volume match reviewed solid',status='PASS' if diff<.002 and verr<.0005*b.volume(frame) else 'FAIL',maximum_bound_error_mm=float(diff),volume_error_mm3=float(verr),scope='Tessellation sanity check, not a native CAD identity claim'))
    assert sha(SOURCE)==args.source_sha,'Source changed during validation'
    assert sha(STUDY/'mechanics/side_thumb.py')==generator_sha,'Candidate generator changed during validation'
    if native:assert native_input_hashes==(sha(args.native_step),sha(args.native_archive)),'Native inputs changed during validation'
    bad=[x for x in rows+identities if x['status']=='FAIL']
    report=dict(status=('PASS_NATIVE_R17_THUMB_INTEGRATION' if native else 'PASS_LOCAL_R17_THUMB_INTEGRATION') if not bad else 'FAIL',source_sha256=args.source_sha,validator_sha256=sha(__file__),candidate_generator_sha256=generator_sha,baseline_version=BASE_VERSION,baseline_source_sha256=BASE_SHA,baseline_native_step_sha256=baseinv['native_step_sha256'],baseline_certificates=certs,**binding,checks=rows,unchanged_native_bodies=identities,failures=bad,limitations=['Nominal geometry only; no thumb anthropometry, physical comfort, skin clearance, strength or print adhesion qualification.','New-stock separation plus retained interfaces extends the frozen R16 path certificates; unrelated pairs are not redundantly rerun.','Native status requires actual native STEP and STL ZIP, not local STEP roundtrip.'])
    out=HERE/('native-integration.json' if native else 'local-integration.json');out.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(status=report['status'],checks=len(rows),unchanged=len(identities),failures=bad),indent=2))
    return bool(bad)
if __name__=='__main__':raise SystemExit(main())
