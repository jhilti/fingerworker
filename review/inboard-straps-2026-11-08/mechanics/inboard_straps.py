#!/usr/bin/env python3
"""R15: four inboard strap slots, preserving the R14 palm and all interfaces."""
from pathlib import Path
import hashlib, importlib.util, json, math
import numpy as np

HERE=Path(__file__).resolve().parent; STUDY=HERE.parent; ROOT=STUDY.parents[1]
R14=ROOT/'review/near-palm-2026-11-06'
s=importlib.util.spec_from_file_location('r15_frozen_r14',R14/'mechanics/near_palm.py')
oldmod=importlib.util.module_from_spec(s);s.loader.exec_module(oldmod)
b,r7,prior=oldmod.b,oldmod.r7,oldmod.prior
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepFilletAPI import BRepFilletAPI_MakeFillet,BRepFilletAPI_MakeChamfer
from OCP.TopAbs import TopAbs_SOLID,TopAbs_SHELL
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
BASE_SOURCE=R14/'fingerworker_R14_near_palm.fs'
BASE_SHA='9286d5a51880dc79d1e9a07135e8c905f4022a1ed757801b8430f23f51a04829'
STRAP_X=[28,65];STRAP_Y=[-57.5,57.5]
vec=oldmod.vec

def load():
    inv=json.loads((R14/'validation/native-step-inventory.json').read_text())
    assert sha(inv['native_step'])==inv['native_step_sha256']
    solids,_,_=b.read_step(inv['native_step'])
    return {ref:solids[x['candidates'][0]['solid_index']] for ref,x in inv['native_part_correspondence'].items()},inv

def strap_geometry():
    slots=[];witnesses=[];routes=[]
    for x in STRAP_X:
        for cy in STRAP_Y:
            sign=-1 if cy<0 else 1
            slot=prior.union([b.box([x-11.5,cy-2,-3],[x+11.5,cy+2,5]),
                r7.cyl([x-11.5,cy,-3],[x-11.5,cy,5],2),r7.cyl([x+11.5,cy,-3],[x+11.5,cy,5],2)])
            slots.append(slot)
            witnesses.append(b.box([x-12.5,cy-1,-3],[x+12.5,cy+1,5]))
            def sy(lo,hi):return sorted([sign*lo,sign*hi])
            low,high=sy(56.5,58.5)
            through=b.box([x-12.5,low,-20],[x+12.5,high,6])
            # Conservative top envelope admits4mm doubled stock although the
            # intended route has a single2mm layer over the bearing strip.
            low,high=sy(56.5,70)
            over=b.box([x-12.5,low,4],[x+12.5,high,8])
            low,high=sy(66,70)
            outside=b.box([x-12.5,low,-20],[x+12.5,high,8])
            routes.append(dict(x=x,y=cy,shape=prior.union([through,over,outside])))
    return dict(slots=slots,witnesses=witnesses,routes=routes)

def palm_only():
    # Reconstruct the frozen, natively verified R14 palm from its original
    # input, omitting only its separate ear/fillet-root additions. This restores
    # the original R1.5 edge around the132mm floor exactly.
    older,_=oldmod.load();g=oldmod.stocks();out=older['P01']
    for tool in g['obsolete_tools']+g['tip_tools']+[g['wall_sculpt']]:out=b.cut(out,tool)
    return b.fuse(out,g['contact'])

def expected(old=None):
    out=palm_only();g=strap_geometry()
    for i,slot in enumerate(g['slots']):
        x=g['routes'][i]['x'];cy=g['routes'][i]['y'];sign=-1 if cy<0 else 1
        out=b.cut(out,slot)
        f=BRepFilletAPI_MakeFillet(out);f.Add(.8,oldmod.edge_at(out,[x,cy+sign*2,4]))
        f.Build();assert f.IsDone(),('slot top round',i);out=f.Shape()
        c=BRepFilletAPI_MakeChamfer(out);c.Add(.8,oldmod.edge_at(out,[x,cy+sign*2,-2]))
        c.Build();assert c.IsDone(),('slot bottom chamfer',i);out=c.Shape()
        assert BRepCheck_Analyzer(out).IsValid()
    return {'P01':out}

def patch_source(source):
    assert hashlib.sha256(source.encode()).hexdigest()==BASE_SHA
    start=source.index('        // Two25mm straps: four integral outboard eyes')
    end=source.index('        const integratedFrame=',start)
    patch='''        // R15: four27x4mm strap openings stay inside the original132mm base.
        // StationsX28/65 clear the front fixed seats and the complete moving
        // rear bridge stroke. The6mm floor is not thinned; outside tabs vanish.
        // Each25x2mm strap end folds over the6.5mm outer bearing strip and
        // returns down outside. No ribbon crosses the central moving deck.
'''
    for i,(x,cy) in enumerate((x,y) for x in STRAP_X for y in STRAP_Y):
        sign=-1 if cy<0 else 1;name=f'R15StrapSlot{i}'
        patch+=f'        makeBox(context,id + "{name}",{vec([x-11.5,cy-2,-3])},{vec([x+11.5,cy+2,5])});\n'
        for j,xc in enumerate([x-11.5,x+11.5]):
            patch+=f'        makeCylinder(context,id + "{name}End{j}",{vec([xc,cy,-3])},{vec([xc,cy,5])},2*mm);\n'
        patch+=f'        join(context,id + "{name}Join",[body(id + "{name}"),body(id + "{name}End0"),body(id + "{name}End1")]);\n'
        patch+=f'        cut(context,id + "{name}Cut",body(id + "base"),body(id + "{name}"));\n'
        patch+=f'''        opFillet(context,id + "{name}TopRound",{{
            "entities":qContainsPoint(qOwnedByBody(body(id + "base"),EntityType.EDGE),{vec([x,cy+sign*2,4])}),
            "radius":0.8*mm,"tangentPropagation":true }});
        opChamfer(context,id + "{name}BottomLeadIn",{{
            "entities":qContainsPoint(qOwnedByBody(body(id + "base"),EntityType.EDGE),{vec([x,cy+sign*2,-2])}),
            "chamferType":ChamferType.EQUAL_OFFSETS,"width":0.8*mm,"tangentPropagation":true }});
'''
    source=source[:start]+patch+source[end:]
    source=source.replace('Fingerworker Flat132 R14 - near-sensor rounded palm support.','Fingerworker Flat132 R15 - inboard strap slots and near-sensor palm support.')
    source=source.replace('"Flat132 R14 - near-sensor palm support"','"Flat132 R15 - inboard strap slots"')
    source=source.replace('P01 PRINT STUDY - Flat132 near-sensor rounded palm, fixed sensor support','P01 PRINT STUDY - Flat132 inboard strap slots, near-sensor palm, fixed sensor support')
    source=source.replace(' * Main base width132mm; four integral strap eyes extend total width to156mm.\n * Two25mm straps use27x4mm throats atX5/80,Y+/-69.5;2mm single ribbon.\n * Strap end returns stay outside the outer bars; no across-top ribbon route.',
        ' * Base width132mm; four inboard27x4mm strap slots atX28/65,Y+/-57.5.\n * Two25mm straps use2mm single ribbons; outer bearing strips remain6.5mm.\n * Original6mm floor is not thinned; strap returns remain outside the mechanism.')
    return source

def validvolume(shape):
    assert BRepCheck_Analyzer(shape).IsValid(),'Invalid Boolean result'
    return b.volume(shape)

def run():
    old,inv=load();g=strap_geometry();plain=palm_only();new=expected(old)['P01']
    source=STUDY/'fingerworker_R15_inboard_straps.fs';source.write_text(patch_source(BASE_SOURCE.read_text()))
    prior.export(new,HERE/'P01_inboard_straps')
    for i,r in enumerate(g['routes']):prior.export(r['shape'],HERE/f'strap_route_{i}')
    rows=[]
    def add(name,ok,**detail):rows.append(dict(name=name,status='PASS' if bool(ok) else 'FAIL',**detail))
    removed=b.cut(old['P01'],new);added=b.cut(new,old['P01'])
    add('One valid connected P01 solid and shell',BRepCheck_Analyzer(new).IsValid() and b.count(new,TopAbs_SOLID)==b.count(new,TopAbs_SHELL)==1)
    add('No material added compared with R14',validvolume(added)<1e-6,added_mm3=validvolume(added))
    masks=[]
    for x in STRAP_X:
        for cy in STRAP_Y:masks.append(b.box([x-14.3,cy-2.8,-3],[x+14.3,cy+2.8,5]))
    removed_slots=b.cut(plain,new)
    add('Only declared inboard slot lead-ins cut the original floor',validvolume(b.cut(removed_slots,prior.union(masks)))<1e-6)
    add('Original floor footprint and retained latch bosses restored exactly',np.max(np.abs(b.bounds(new)-b.bounds(plain)))<1e-6,width_mm=float(np.ptp(b.bounds(new)[:,1])),original_palm_frame_width_mm=float(np.ptp(b.bounds(plain)[:,1])),floor_nominal_width_mm=132)
    add('Entire R14 palm and functional stock above floor retained',validvolume(b.common(removed,b.box([-60,-80,4],[140,80,50])))<1e-6)
    for x in STRAP_X:
        for sign in [-1,1]:
            yl,yh=sorted([sign*60.4,sign*64.4])
            core=b.box([x-11,yl,-1.1],[x+11,yh,3.1])
            add(f'Full-thickness outer bearing core retained {x}/{sign}',validvolume(b.cut(core,new))<1e-6)
            yl,yh=sorted([sign*38,sign*54.5]);core=b.box([x-11,yl,-1.1],[x+11,yh,3.1])
            add(f'Inner spring-rail core retained {x}/{sign}',validvolume(b.cut(core,new))<1e-6)
    for ref,shape in old.items():
        if ref=='P01':continue
        aa,bb=b.bounds(new),b.bounds(shape)
        if np.any(aa[1]<bb[0]) or np.any(bb[1]<aa[0]):continue
        iv=validvolume(b.common(new,shape));add('Seated separation P01/'+ref,iv<1e-6,intersection_mm3=iv)
    for i,(witness,route) in enumerate(zip(g['witnesses'],g['routes'])):
        iv=validvolume(b.common(new,witness));add('Exact25x2mm throat '+str(i),iv<1e-6,intersection_mm3=iv)
        for ref,shape in dict(old,P01=new).items():
            aa,bb=b.bounds(route['shape']),b.bounds(shape)
            if np.any(aa[1]<bb[0]) or np.any(bb[1]<aa[0]):continue
            iv=validvolume(b.common(route['shape'],shape));add(f'Finite strap route{i} / {ref}',iv<1e-6,intersection_mm3=iv)
        for ref in ['P04','H060','H061','P11','H10']:
            # Rigid translation is parallelX. Intersect the actual native part
            # with the route's fullY/Z slab first; every possibly interfering
            # point lies in this exact subset. Its bounding box swept over the
            # completeX interval is a conservative continuous certificate.
            rb=b.bounds(route['shape']);slab=b.box([-200,rb[0,1],rb[0,2]],[200,rb[1,1],rb[1,2]])
            part=b.common(old[ref],slab);pv=validvolume(part)
            if pv<1e-9:
                add(f'Full strap route{i} / {ref} motion',True,clipped_native_volume_mm3=pv,proof='No native material in the route Y/Z slab; translation alongX cannot enter it.')
            else:
                bb=b.bounds(part);lo,hi=(-30.8,.8) if ref in ['P11','H10'] else (-30.,0.)
                bb[0,0]+=lo;bb[1,0]+=hi;gap=b.gap(route['shape'],b.box(bb[0],bb[1]))
                add(f'Full strap route{i} / {ref} motion',gap>1e-6,gap_lower_bound_mm=gap,translation_range_mm=[lo,hi],clipped_native_volume_mm3=pv,proof='Exact native geometry clipped to the full strapY/Z slab, then bounded and extended over the completeX translation interval.')
    spec=json.loads((R14/'mechanics/design-specification.json').read_text())
    spec.update(revision='R15',source_sha256=sha(source),baseline_source_sha256=BASE_SHA,baseline_native_step_sha256=inv['native_step_sha256'],added_mm3=validvolume(added),removed_mm3=validvolume(removed),P01_volume_mm3=validvolume(new),baseline_P01_volume_mm3=validvolume(old['P01']),changed=['P01'],other_native_bodies_unchanged=92)
    spec['strap_mount']=dict(slot_count=4,position_count=2,position_x_mm=STRAP_X,position_spacing_mm=37,slot_center_y_mm=STRAP_Y,slot_size_mm=[27,4],slot_plan_end_radius_mm=2,slot_top_radius_mm=.8,slot_bottom_chamfer_mm=.8,slot_bottom_chamfer_degrees=45,strap_width_mm=25,strap_thickness_envelope_mm=2,external_doubled_thickness_envelope_mm=4,minimum_throat_chord_at_2mm_band_mm=23+2*math.sqrt(3),overall_width_mm=132.4,main_floor_width_mm=132,existing_latch_boss_width_mm=132.4,eye_z_mm=[-2,4],original_floor_thickness_mm=6,floor_recess_mm=0,nominal_outer_bar_mm=6.5,minimum_outer_bar_at_top_surface_mm=4.2,nominal_inner_rail_mm=17.5,slot_end_spacing_mm=10,strap_quantity=2,straps_printed=False,extra_printed_parts=0,routing='Each end rises through its inboard slot, turns over the outer bearing strip, descends outside and fastens back to itself. The free strap wraps under the chosen object; no across-top ribbon. Folded ends remain outside.',route_audit_extent_z_mm=[-20,8],route_audit_outer_y_mm=70,intended_bearing_contacts='Top of outer strip atZ4 and outside edge atY+/-66. Positive volume overlap prohibited; face contact intended.',station_selection='X28/65 keeps the rear25mm ribbon span3.5mm before the exact native full-stroke rear-bridge startX81; front band beginsX15.5 after the fixedseat endX12. Source carriage is already advanced5mm in the native rest configuration; audit adds the full30mm stroke to that native pose. OriginalX80 rearstation would interfere with the moving bridge.',limitations='Nominal25x2mm ribbon allowance. Physical strap fit, force capacity and creep require printed validation; smaller37mm station spacing gives less rotational restraint than R14.')
    (HERE/'design-specification.json').write_text(json.dumps(spec,indent=2)+'\n')
    report=dict(status='PASS_LOCAL_INBOARD_STRAPS' if all(r['status']=='PASS' for r in rows) else 'FAIL',checks=rows,metrics=spec,generator_sha256=sha(__file__),candidate_source_sha256=sha(source),baseline_native_step_sha256=inv['native_step_sha256'])
    (HERE/'preflight.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(status=report['status'],checks=len(rows),failures=[r for r in rows if r['status']=='FAIL'],source_sha256=sha(source),P01_volume_mm3=spec['P01_volume_mm3']),indent=2),flush=True)

if __name__=='__main__':run()
