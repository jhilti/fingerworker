#!/usr/bin/env python3
"""R14 near-sensor palm: exact CSG and matching FS patch over frozen R13."""
from pathlib import Path
import hashlib, importlib.util, json, math
import numpy as np

HERE=Path(__file__).resolve().parent
STUDY=HERE.parent
ROOT=STUDY.parents[1]
R13=ROOT/'review/palm-simplification-2026-11-03'
s=importlib.util.spec_from_file_location('r14_old_palm',R13/'mechanics/simple_palm.py')
prior=importlib.util.module_from_spec(s);s.loader.exec_module(prior)
b,r7=prior.b,prior.r7
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeEdge,BRepBuilderAPI_MakeWire,BRepBuilderAPI_MakeFace
from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism
from OCP.BRepFilletAPI import BRepFilletAPI_MakeFillet,BRepFilletAPI_MakeChamfer
from OCP.GC import GC_MakeArcOfCircle
from OCP.gp import gp_Pnt,gp_Vec
from OCP.TopAbs import TopAbs_EDGE,TopAbs_SOLID,TopAbs_SHELL
from OCP.TopExp import TopExp_Explorer
from OCP.TopoDS import TopoDS
from OCP.BRepCheck import BRepCheck_Analyzer

sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
BASE_SOURCE=R13/'fingerworker_R13_simple_palm.fs'
BASE_SHA='82b7d65708c46cd9d4b6ac271047eac2f638f0222451df99eae0780525edd851'

# Remove high obsolete palm stock while retaining the exact electronics roof,
# fixed reaction wall and original rod blocks (X-18..-8,Y39..63,Z3.8..28).
TRIMS=[
 ([-60,-70,14.5],[-22.75,70,40]),
 ([-22.75,25.4,14.5],[-18,70,40]),
 ([-22.75,-70,14.5],[-18,-25.4,40]),
 ([-18,25.4,14.5],[-16,39,40]),
 ([-18,-39,14.5],[-16,-25.4,40]),
 ([-18,39,28],[-16,70,40]),
 ([-18,-70,28],[-16,-39,40]),
]
TIP_TRIMS=[([-16,20.3,30],[-6,25.4,40]),([-16,-25.4,30],[-6,-20.3,40])]
REAR_MID=(-20-14/math.sqrt(2),19+14/math.sqrt(2))
FRONT_MID=(-19+3/math.sqrt(2),30+3/math.sqrt(2))
STRAP_X=[5,80]
STRAP_Y=[-69.5,69.5]

def make_contact():
    """76-wide,18-deep asymmetric R14/R3 contact; rear-supported45deg nose."""
    y=-38
    point=lambda xz:gp_Pnt(xz[0],y,xz[1])
    edges=[]
    def line(a,c):edges.append(BRepBuilderAPI_MakeEdge(point(a),point(c)).Edge())
    def arc(a,m,c):edges.append(BRepBuilderAPI_MakeEdge(GC_MakeArcOfCircle(point(a),point(m),point(c)).Value()).Edge())
    line((-34,14.4),(-34,19))
    arc((-34,19),REAR_MID,(-20,33))
    line((-20,33),(-19,33))
    arc((-19,33),FRONT_MID,(-16,30))
    line((-16,30),(-16,26))
    line((-16,26),(-22.5,19.5))
    line((-22.5,19.5),(-22.5,14.4))
    line((-22.5,14.4),(-34,14.4))
    wire=BRepBuilderAPI_MakeWire()
    for edge in edges:wire.Add(edge)
    shape=BRepPrimAPI_MakePrism(BRepBuilderAPI_MakeFace(wire.Wire()).Face(),gp_Vec(0,76,0)).Shape()
    # Only the upper end contour: bottom and45-degree underside stay sharp
    # against their supporting stock, avoiding lifted underside edge pockets.
    fillet=BRepFilletAPI_MakeFillet(shape);ex=TopExp_Explorer(shape,TopAbs_EDGE);picked=[]
    while ex.More():
        e=TopoDS.Edge(ex.Current());bb=b.bounds(e)
        if bb[1,1]-bb[0,1]<1e-5 and abs(abs(bb[0,1])-38)<1e-5 and bb[0,0]<-33.9 and bb[1,2]>32.9:
            if not any(e.IsSame(other) for other in picked):
                fillet.Add(2,e);picked.append(e)
        ex.Next()
    assert len(picked)==2,len(picked)
    fillet.Build();assert fillet.IsDone(),'End fillet failed'
    shape=fillet.Shape();assert BRepCheck_Analyzer(shape).IsValid()
    return shape

def edge_at(shape,point):
    """Find the unique straight edge containing a midpoint by tight bounds."""
    found=[];ex=TopExp_Explorer(shape,TopAbs_EDGE);p=np.array(point)
    while ex.More():
        e=TopoDS.Edge(ex.Current());bb=b.bounds(e)
        if np.all(p>=bb[0]-1e-6) and np.all(p<=bb[1]+1e-6):
            if not any(e.IsSame(other) for other in found):found.append(e)
        ex.Next()
    assert len(found)==1,(point,len(found))
    return found[0]

def strap_geometry():
    """Four integral eyes, exact25x2 throat witnesses and outboard fold envelopes."""
    ears=[];roots=[];slots=[];witnesses=[];routes=[]
    for x in STRAP_X:
        for cy in STRAP_Y:
            sign=-1 if cy<0 else 1
            yl,yh=sorted([sign*58,sign*78])
            ear=prior.fillet(b.box([x-19.5,yl,-2],[x+19.5,yh,4]),5,vertical=True)
            slot=prior.union([b.box([x-11.5,cy-2,-3],[x+11.5,cy+2,5]),
                r7.cyl([x-11.5,cy,-3],[x-11.5,cy,5],2),r7.cyl([x+11.5,cy,-3],[x+11.5,cy,5],2)])
            ear=b.cut(ear,slot)
            f=BRepFilletAPI_MakeFillet(ear)
            for p in [[x,cy+sign*2,4],[x,sign*78,4]]:f.Add(.8,edge_at(ear,p))
            f.Build();assert f.IsDone();ear=f.Shape()
            ch=BRepFilletAPI_MakeChamfer(ear)
            for p in [[x,cy+sign*2,-2],[x,sign*78,-2]]:ch.Add(.8,edge_at(ear,p))
            ch.Build();assert ch.IsDone();ear=ch.Shape()
            assert BRepCheck_Analyzer(ear).IsValid();ears.append(ear);slots.append(slot)
            # Explicit concaveR3 root stock: no post-fusion edge selection.
            for sx in [-1,1]:
                xr=x+sx*19.5;xc=x+sx*22.5;yc=sign*69
                lo=[min(xr,xc)-(.1 if sx>0 else 0),min(sign*64.4,sign*69),-2]
                hi=[max(xr,xc)+(.1 if sx<0 else 0),max(sign*64.4,sign*69),4]
                root=b.cut(b.box(lo,hi),r7.cyl([xc,yc,-2.1],[xc,yc,4.1],3));roots.append(root)
            witnesses.append(b.box([x-12.5,cy-1,-3],[x+12.5,cy+1,5]))
            # A single2mm strand in the slot; up to4mm doubled outside.
            # Free ribbon continues around the chosen object belowZ-20.
            def sy(lo,hi):return sorted([sign*lo,sign*hi])
            low,high=sy(68.5,70.5)
            through=b.box([x-12.5,low,-20],[x+12.5,high,6])
            low,high=sy(68.5,82)
            over=b.box([x-12.5,low,4],[x+12.5,high,8])
            low,high=sy(78,82)
            outside=b.box([x-12.5,low,-20],[x+12.5,high,8])
            routes.append(dict(x=x,y=cy,shape=prior.union([through,over,outside])))
    return dict(ears=ears,roots=roots,slots=slots,witnesses=witnesses,routes=routes)

def stocks():
    cap=make_contact()
    sculpt=b.cut(b.box([-22.75,-25.4,30],[-16,25.4,40]),cap)
    return dict(contact=cap,obsolete_tools=[b.box(*p) for p in TRIMS],
                tip_tools=[b.box(*p) for p in TIP_TRIMS],wall_sculpt=sculpt,straps=strap_geometry())

def expected(old):
    g=stocks();out=old['P01']
    for tool in g['obsolete_tools']+g['tip_tools']+[g['wall_sculpt']]:out=b.cut(out,tool)
    out=b.fuse(out,g['contact'])
    for stock in g['straps']['ears']+g['straps']['roots']:out=b.fuse(out,stock)
    return {'P01':out}

def load():
    inv=json.loads((R13/'validation/native-step-inventory.json').read_text())
    assert sha(inv['native_step'])==inv['native_step_sha256']
    ss,_,_=b.read_step(inv['native_step'])
    return {ref:ss[x['candidates'][0]['solid_index']] for ref,x in inv['native_part_correspondence'].items()},inv

def vec(a):return 'vector('+','.join(format(float(x),'.12g') for x in a)+')*mm'

def patch_source(source):
    assert hashlib.sha256(source.encode()).hexdigest()==BASE_SHA
    anchor='        const integratedFrame=qBodyType(qUnion([body(id + "base"),body(id + "palmPad")]),BodyType.SOLID);'
    assert source.count(anchor)==1
    patch='''        // R14: local near-sensor palm contact replaces the obsolete outer bolster.
        // Lower roof/catches/feet, front rod blocks and all sensor datums remain.
'''
    for i,(lo,hi) in enumerate(TRIMS):
        patch+=f'        makeBox(context,id + "R14PalmTrim{i}",{vec(lo)},{vec(hi)});\n'
        patch+=f'        cut(context,id + "R14PalmTrimCut{i}",body(id + "base"),body(id + "R14PalmTrim{i}"));\n'
    patch+='''        //76mm width,18mm depth. R14 wrist curve meets a1mm long landing
        // atX-20..-19,Z33, thenR3 to the retained sensor-facing limitX-16.
        var nearPalmSketch=newSketchOnPlane(context,id + "R14PalmSketch",{
            "sketchPlane":plane(vector(0,-38,0)*mm,vector(0,-1,0),vector(1,0,0)) });
'''
    lines=[((-34,14.4),(-34,19)),((-20,33),(-19,33)),((-16,30),(-16,26)),((-16,26),(-22.5,19.5)),((-22.5,19.5),(-22.5,14.4)),((-22.5,14.4),(-34,14.4))]
    for i,(a,c) in enumerate(lines):patch+=f'        skLineSegment(nearPalmSketch,"line{i}",{{"start":{vec(a)},"end":{vec(c)}}});\n'
    for i,(a,m,c) in enumerate([((-34,19),REAR_MID,(-20,33)),((-19,33),FRONT_MID,(-16,30))]):
        patch+=f'        skArc(nearPalmSketch,"arc{i}",{{"start":{vec(a)},"mid":{vec(m)},"end":{vec(c)}}});\n'
    patch+='''        skSolve(nearPalmSketch);
        opExtrude(context,id + "R14PalmContact",{
            "entities":qSketchRegion(id + "R14PalmSketch"),"direction":vector(0,1,0),
            "endBound":BoundingType.BLIND,"endDepth":76*mm });
        opDeleteBodies(context,id + "R14PalmSketchDelete",{
            "entities":qCreatedBy(id + "R14PalmSketch",EntityType.BODY) });
        opFillet(context,id + "R14PalmEndRound",{
            "entities":qUnion([
'''
    for i,y in enumerate([-38,38]):patch+=f'                qContainsPoint(qOwnedByBody(body(id + "R14PalmContact"),EntityType.EDGE),{vec([REAR_MID[0],y,REAR_MID[1]])})'+(',' if i==0 else '')+'\n'
    patch+='''            ]),"radius":2*mm,"tangentPropagation":true });
        // Remove the original narrow rim where it would protrude through the
        // rounded contact. No original reaction/guide stock belowZ30 is lost.
        makeBox(context,id + "R14WallSculpt",vector(-22.75,-25.4,30)*mm,vector(-16,25.4,40)*mm);
        opBoolean(context,id + "R14WallSculptMask",{
            "targets":body(id + "R14WallSculpt"),"tools":body(id + "R14PalmContact"),
            "operationType":BooleanOperationType.SUBTRACTION,"keepTools":true });
        cut(context,id + "R14WallSculptCut",body(id + "base"),body(id + "R14WallSculpt"));
'''
    for i,(lo,hi) in enumerate(TIP_TRIMS):
        patch+=f'        makeBox(context,id + "R14ButtressTip{i}",{vec(lo)},{vec(hi)});\n'
        patch+=f'        cut(context,id + "R14ButtressTipCut{i}",body(id + "base"),body(id + "R14ButtressTip{i}"));\n'
    patch+='''        join(context,id + "R14NearPalmJoin",[body(id + "base"),body(id + "R14PalmContact")]);
'''
    patch+='''        // Two25mm straps: four integral outboard eyes with27x4mm throats.
        // Each2mm end rises through its own eye, folds over the outer bar,
        // and secures back to itself outside the mechanism. No top crossing.
        // Original6mm floor and guide section are retained without cuts.
'''
    for i,(x,cy) in enumerate((x,y) for x in STRAP_X for y in STRAP_Y):
        sign=-1 if cy<0 else 1;yl,yh=sorted([sign*58,sign*78]);name=f'R14StrapEye{i}'
        patch+=f'        makeBox(context,id + "{name}",{vec([x-19.5,yl,-2])},{vec([x+19.5,yh,4])});\n'
        patch+=f'''        opFillet(context,id + "{name}PlanRound",{{
            "entities":qParallelEdges(qCreatedBy(id + "{name}",EntityType.EDGE),vector(0,0,1)),
            "radius":5*mm,"tangentPropagation":true }});
'''
        patch+=f'        makeBox(context,id + "{name}Slot",{vec([x-11.5,cy-2,-3])},{vec([x+11.5,cy+2,5])});\n'
        for j,xc in enumerate([x-11.5,x+11.5]):
            patch+=f'        makeCylinder(context,id + "{name}SlotEnd{j}",{vec([xc,cy,-3])},{vec([xc,cy,5])},2*mm);\n'
        patch+=f'        join(context,id + "{name}SlotJoin",[body(id + "{name}Slot"),body(id + "{name}SlotEnd0"),body(id + "{name}SlotEnd1")]);\n'
        patch+=f'        cut(context,id + "{name}SlotCut",body(id + "{name}"),body(id + "{name}Slot"));\n'
        patch+=f'''        opFillet(context,id + "{name}TopBearingRound",{{
            "entities":qUnion([qContainsPoint(qOwnedByBody(body(id + "{name}"),EntityType.EDGE),{vec([x,cy+sign*2,4])}),qContainsPoint(qOwnedByBody(body(id + "{name}"),EntityType.EDGE),{vec([x,sign*78,4])})]),
            "radius":0.8*mm,"tangentPropagation":true }});
        opChamfer(context,id + "{name}BottomLeadIn",{{
            "entities":qUnion([qContainsPoint(qOwnedByBody(body(id + "{name}"),EntityType.EDGE),{vec([x,cy+sign*2,-2])}),qContainsPoint(qOwnedByBody(body(id + "{name}"),EntityType.EDGE),{vec([x,sign*78,-2])})]),
            "chamferType":ChamferType.EQUAL_OFFSETS,"width":0.8*mm,"tangentPropagation":true }});
'''
        patch+=f'        join(context,id + "{name}FrameJoin",[body(id + "base"),body(id + "{name}")]);\n'
        for j,sx in enumerate([-1,1]):
            xr=x+sx*19.5;xc=x+sx*22.5;yc=sign*69
            lo=[min(xr,xc)-(.1 if sx>0 else 0),min(sign*64.4,sign*69),-2]
            hi=[max(xr,xc)+(.1 if sx<0 else 0),max(sign*64.4,sign*69),4]
            root=f'{name}Root{j}'
            patch+=f'        makeBox(context,id + "{root}",{vec(lo)},{vec(hi)});\n'
            patch+=f'        makeCylinder(context,id + "{root}Tool",{vec([xc,yc,-2.1])},{vec([xc,yc,4.1])},3*mm);\n'
            patch+=f'        cut(context,id + "{root}Cut",body(id + "{root}"),body(id + "{root}Tool"));\n'
            patch+=f'        join(context,id + "{root}Join",[body(id + "base"),body(id + "{root}")]);\n'
    source=source.replace(anchor,patch+anchor)
    source=source.replace('import(path : "onshape/std/geometry.fs", version : "3070.0");','import(path : "onshape/std/geometry.fs", version : "3070.0");\nimport(path : "onshape/std/chamfertype.gen.fs", version : "3070.0");')
    source=source.replace('Fingerworker Flat132 R13 - continuous rounded palm support.','Fingerworker Flat132 R14 - near-sensor rounded palm support.')
    source=source.replace(' * One constant-radius palm rail and a broad web absorb old steps and ribs.',' * One local76x18mm asymmetric palm rail replaces the obsolete outer bolster.\n * CrownX-20..-19,Z33; all palm stock stays behindX-16; no extra printed part.')
    source=source.replace('"Flat132 R13 - continuous palm support"','"Flat132 R14 - near-sensor palm support"')
    source=source.replace('P01 PRINT STUDY - Flat132 continuous palm rail and web, fixed sensor support','P01 PRINT STUDY - Flat132 near-sensor rounded palm, fixed sensor support')
    source=source.replace(' * contact face X-37.25. Legacy illustrative hand pose is retained for',' * R14 contact crownX-20..-19,Z33. Legacy illustrative hand pose is retained for')
    source=source.replace(' * Nominal base width132mm; rear latch outer envelope135.2mm.',' * Main base width132mm; four integral strap eyes extend total width to156mm.\n * Two25mm straps use27x4mm throats atX5/80,Y+/-69.5;2mm single ribbon.\n * Strap end returns stay outside the outer bars; no across-top ribbon route.')
    return source

def run():
    old,inv=load();g=stocks();new=expected(old)['P01'];assert sha(BASE_SOURCE)==BASE_SHA
    source=STUDY/'fingerworker_R14_near_palm.fs';source.write_text(patch_source(BASE_SOURCE.read_text()))
    prior.export(new,HERE/'P01_near_palm');prior.export(g['contact'],HERE/'contact_rail')
    for i,route in enumerate(g['straps']['routes']):prior.export(route['shape'],HERE/f'strap_route_{i}')
    rows=[]
    def add(name,ok,**detail):rows.append(dict(name=name,status='PASS' if bool(ok) else 'FAIL',**detail))
    def vol(shape):assert BRepCheck_Analyzer(shape).IsValid(),'Invalid Boolean';return b.volume(shape)
    added=b.cut(new,old['P01']);removed=b.cut(old['P01'],new)
    add('One valid connected P01 solid and shell',BRepCheck_Analyzer(new).IsValid() and b.count(new,TopAbs_SOLID)==b.count(new,TopAbs_SHELL)==1)
    allowed=prior.union([g['contact']]+g['straps']['ears']+g['straps']['roots'])
    add('All added material lies within declared palm and strap stock',vol(b.cut(added,allowed))<1e-6)
    add('Palm contact remains behind sensor-facing limitX-16',b.bounds(g['contact'])[1,0]<=-16+1e-6,bounds_mm=b.bounds(g['contact']).tolist())
    zones=[('electronics roof and functional stock belowZ14.5',b.box([-60,-70,-3],[140,70,14.5])),
           ('negative tray catch landing',b.box([-30,-66,9.4],[-24,-62,16.5])),
           ('positive tray catch landing',b.box([-30,62,9.4],[-24,66,16.5])),
           ('central sensor reaction and guides belowZ30',b.box([-22.75,-25.4,-3],[2,25.4,30])),
           ('negative front rod socket block',b.box([-18,-63,3.8],[-8,-39,28])),
           ('positive front rod socket block',b.box([-18,39,3.8],[-8,63,28]))]
    for label,zone in zones:
        delta=vol(b.common(removed,zone))
        add('No original material lost: '+label,delta<1e-6,removed_mm3=delta)
    clear_zones=[('electronics roof',b.box([-60,-70,-3],[-23.5,70,14.5]))]+zones[1:3]+zones[4:]
    for label,zone in clear_zones:
        delta=vol(b.common(added,zone));add('No material added: '+label,delta<1e-6,added_mm3=delta)
    for ref,shape in old.items():
        if ref=='P01':continue
        bb=b.bounds(shape);aa=b.bounds(new)
        if np.any(aa[1]<bb[0]) or np.any(bb[1]<aa[0]):continue
        overlap=vol(b.common(new,shape));add('Seated separation P01/'+ref,overlap<1e-6,intersection_mm3=overlap)
    for side in [-1,1]:
        y0,y1=(-72,-15.3) if side<0 else (15.3,72)
        route=r7.cyl([-12.8,y0,8.5],[-12.8,y1,8.5],3.2)
        add('No new H18 lateral tool obstruction '+str(side),vol(b.common(added,route))<1e-6)
    for y in [-59,59]:
        hole=r7.cyl([-26.5,y,9.4],[-26.5,y,13.5],1.6)
        add('Optional M2 underside pilot open '+str(y),vol(b.common(new,hole))<1e-6)
    for i,(witness,route) in enumerate(zip(g['straps']['witnesses'],g['straps']['routes'])):
        iv=vol(b.common(new,witness));add('Exact25x2mm band passes capsule throat '+str(i),iv<1e-6,intersection_mm3=iv)
        iv=vol(b.common(new,route['shape']));add('External2mm single/4mm double-back route clear of P01 '+str(i),iv<1e-6,intersection_mm3=iv,route_bounds_mm=b.bounds(route['shape']).tolist())
        for ref,shape in old.items():
            if ref=='P01':continue
            rb,sb=b.bounds(route['shape']),b.bounds(shape)
            if np.any(rb[1]<sb[0]) or np.any(sb[1]<rb[0]):continue
            iv=vol(b.common(route['shape'],shape));add('Strap route '+str(i)+' seated separation/'+ref,iv<1e-6,intersection_mm3=iv)
    add('Overall base with integral eyes is156mm wide',abs(np.ptp(b.bounds(new)[:,1])-156)<1e-6,width_mm=float(np.ptp(b.bounds(new)[:,1])))
    tips=prior.union(g['tip_tools']);tip_vol=vol(b.common(old['P01'],tips))
    spec=dict(revision='R14',contact_width_mm=76,contact_depth_mm=18,contact_envelope_mm=[[-34,-38,14.4],[-16,38,33]],crown_x_mm=[-20,-19],crown_z_mm=33,
        wrist_radius_mm=14,sensor_facing_radius_mm=3,end_radius_mm=2,nose_underside_degrees=45,
        retained_original_wall_below_z_mm=30,original_sensor_reaction_max_z_mm=26,buttress_tip_removed_mm3=tip_vol,
        added_mm3=vol(added),removed_mm3=vol(removed),P01_volume_mm3=vol(new),baseline_P01_volume_mm3=vol(old['P01']),
        source_sha256=sha(source),baseline_source_sha256=BASE_SHA,baseline_native_step_sha256=inv['native_step_sha256'],
        changed=['P01'],other_native_bodies_unchanged=92,device_printed_parts=7,minimum_contact_to_H12_rear_plane_x_gap_mm=4,
        obsolete_stock_removed='Old outer bolster and high broad web aboveZ14.5, excluding fixed wall and original rod blocks. Wall upper rim and buttress tips sculpted only aboveZ30.',
        limitations='Nominal CAD design dimensions. Authoritative native geometry, service/motion and slicing validation are separate hash-bound release reports. No new loaded-strength qualification.')
    spec['strap_mount']=dict(slot_count=4,position_count=2,position_x_mm=STRAP_X,slot_center_y_mm=STRAP_Y,
        slot_size_mm=[27,4],slot_plan_end_radius_mm=2,slot_top_radius_mm=.8,slot_bottom_chamfer_mm=.8,
        slot_bottom_chamfer_degrees=45,strap_width_mm=25,strap_thickness_envelope_mm=2,
        external_doubled_thickness_envelope_mm=4,minimum_throat_chord_at_2mm_band_mm=23+2*math.sqrt(3),
        overall_width_mm=156,ear_plan_size_mm=[39,20],ear_plan_radius_mm=5,ear_root_radius_mm=3,
        ear_root_x_extent_from_station_mm=22.5,eye_z_mm=[-2,4],original_floor_thickness_mm=6,
        nominal_outer_bar_mm=6.5,minimum_outer_bar_at_top_surface_mm=4.9,nominal_slot_end_ligament_mm=6,
        strap_quantity=2,straps_printed=False,extra_printed_parts=0,
        routing='Each end rises through its own slot, turns over the outer bar, descends outside and fastens back to itself. The free strap wraps around the object; no ribbon crosses the mechanical top or spans between eyes beneath the base in the primary route.',
        route_audit_extent_z_mm=[-20,8],route_audit_outer_y_mm=82,
        intended_bearing_contacts='Top of each outer bar at Z4 and outboard edge at Y+/-78. Positive material overlap is prohibited; face contact is intentional.',
        limitations='25mm width and2mm single thickness are explicit design allowances, not a universal strap-fit or load-rating claim. Closure and length must suit the object; external end folds may be up to4mm thick.')
    (HERE/'design-specification.json').write_text(json.dumps(spec,indent=2)+'\n')
    report=dict(status='PASS_LOCAL_NEAR_PALM' if all(r['status']=='PASS' for r in rows) else 'FAIL',checks=rows,metrics=spec,
        generator_sha256=sha(__file__),candidate_source_sha256=sha(source),baseline_native_step_sha256=inv['native_step_sha256'])
    (HERE/'preflight.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(status=report['status'],checks=len(rows),failures=[r for r in rows if r['status']=='FAIL'],metrics=spec),indent=2))

if __name__=='__main__':run()
