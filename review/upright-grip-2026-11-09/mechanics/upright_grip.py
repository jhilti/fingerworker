#!/usr/bin/env python3
"""R16: one upright palm rail, rounded socket shoulders and sloped thumb returns.

Frozen R15 native CAD is the baseline. This module creates exact CSG and the
matching appended FeatureScript construction. No original functional socket
or fixed sensor reaction stock below Z30 is removed.
"""
from pathlib import Path
import hashlib, importlib.util, json, math
import numpy as np
HERE=Path(__file__).resolve().parent; STUDY=HERE.parent; ROOT=STUDY.parents[1]
R15=ROOT/'review/inboard-straps-2026-11-08'
s=importlib.util.spec_from_file_location('r16_r14_helpers',ROOT/'review/near-palm-2026-11-06/mechanics/near_palm.py')
oldmod=importlib.util.module_from_spec(s);s.loader.exec_module(oldmod)
b,r7,prior=oldmod.b,oldmod.r7,oldmod.prior
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeEdge,BRepBuilderAPI_MakeWire,BRepBuilderAPI_MakeFace
from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism
from OCP.BRepFilletAPI import BRepFilletAPI_MakeFillet
from OCP.GC import GC_MakeArcOfCircle
from OCP.gp import gp_Pnt,gp_Vec
from OCP.TopAbs import TopAbs_EDGE,TopAbs_SOLID,TopAbs_SHELL
from OCP.TopExp import TopExp_Explorer
from OCP.TopoDS import TopoDS
from OCP.BRepCheck import BRepCheck_Analyzer
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
BASE_SOURCE=R15/'fingerworker_R15_inboard_straps.fs'
BASE_SHA='97e2010cc17d06eb8648cf278b9aae2fd85b6e909bd657b9b216f3b37748665f'
vec=oldmod.vec
LEDGE_TRIM=([-40,-70,11.5],[-29,70,14.5])

def load():
    inv=json.loads((R15/'validation/native-step-inventory.json').read_text())
    assert sha(inv['native_step'])==inv['native_step_sha256']
    solids,_,_=b.read_step(inv['native_step'])
    return {ref:solids[x['candidates'][0]['solid_index']] for ref,x in inv['native_part_correspondence'].items()},inv

def profile(a,c,lines,arcs,fillet_radius,edge_points):
    point=lambda xz:gp_Pnt(xz[0],a,xz[1]); edges=[]
    for p,q in lines:edges.append((p,q,BRepBuilderAPI_MakeEdge(point(p),point(q)).Edge()))
    for p,m,q in arcs:edges.append((p,q,BRepBuilderAPI_MakeEdge(GC_MakeArcOfCircle(point(p),point(m),point(q)).Value()).Edge()))
    wire=BRepBuilderAPI_MakeWire()
    current=edges[0][0]
    while edges:
        i=next(i for i,(p,q,e) in enumerate(edges) if p==current)
        p,q,e=edges.pop(i);wire.Add(e);current=q
    shape=BRepPrimAPI_MakePrism(BRepBuilderAPI_MakeFace(wire.Wire()).Face(),gp_Vec(0,c-a,0)).Shape()
    # Match Onshape qContainsPoint selections on the curved upper contour.
    f=BRepFilletAPI_MakeFillet(shape)
    for y in [a,c]:
        picked=[];ex=TopExp_Explorer(shape,TopAbs_EDGE)
        while ex.More():
            e=TopoDS.Edge(ex.Current());bb=b.bounds(e)
            for p in edge_points:
                xyz=np.array([p[0],y,p[1]])
                if np.all(xyz>=bb[0]-1e-6) and np.all(xyz<=bb[1]+1e-6):
                    if not any(e.IsSame(other) for other in picked):picked.append(e)
            ex.Next()
        assert len(picked)==len(edge_points),(len(picked),edge_points)
        for e in picked:f.Add(fillet_radius,e)
    f.Build();assert f.IsDone(),'Profile end rounding failed'
    shape=f.Shape();assert BRepCheck_Analyzer(shape).IsValid()
    return shape

RAIL_LINES=[((-29,14.4),(-29,28)),((-24,33),(-19,33)),((-16,30),(-16,26)),
            ((-16,26),(-22.5,19.5)),((-22.5,19.5),(-22.5,14.4)),((-22.5,14.4),(-29,14.4))]
RAIL_MID=(-24-5/math.sqrt(2),28+5/math.sqrt(2))
RAIL_ARCS=[((-29,28),RAIL_MID,(-24,33)),((-19,33),oldmod.FRONT_MID,(-16,30))]
CAP_LINES=[((-24,24),(-24,29)),((-20,33),(-12,33)),((-8,29),(-8,24)),((-8,24),(-24,24))]
CAP_MID=(-20-4/math.sqrt(2),29+4/math.sqrt(2))
CAP_ARCS=[((-24,29),CAP_MID,(-20,33)),((-12,33),(-12+4/math.sqrt(2),29+4/math.sqrt(2)),(-8,29))]

def stocks():
    rail=profile(-63,63,RAIL_LINES,RAIL_ARCS,3,[RAIL_MID])
    caps=[profile(a,c,CAP_LINES,CAP_ARCS,2,[CAP_MID]) for a,c in [(-65,-37),(37,65)]]
    thumbtools=[]
    for y in [-51,51]:
        # Plan-circle gives a smooth open return: depth4 at Ycenter,14mm
        # opening chord. Sloped roof Z=-X-5 grows45deg toward the wrist.
        round_tool=r7.cyl([-33,y,14.3],[-33,y,26],8)
        ramp=prior.yprism(y-8.1,y+8.1,[[-42,14.3],[-25,14.3],[-25,20],[-31,26],[-42,26]])
        tool=b.common(round_tool,ramp);thumbtools.append(tool);rail=b.cut(rail,tool)
    # Round every exposed upper/side thumb-pocket mouth edge. The tools start
    # below rail bottom, so there is no thin0.1mm lip; original roof is intact.
    f=BRepFilletAPI_MakeFillet(rail);seen=[];ex=TopExp_Explorer(rail,TopAbs_EDGE)
    while ex.More():
        e=TopoDS.Edge(ex.Current());bb=b.bounds(e)
        if not any(e.IsSame(other) for other in seen):
            seen.append(e)
            if abs(bb[0,0]+29)<1e-5 and abs(bb[1,0]+29)<1e-5 and abs(bb[1,2]-24)<1e-5 and bb[1,1]-bb[0,1]<16:f.Add(.8,e)
        ex.Next()
    f.Build();assert f.IsDone();rail=f.Shape();assert BRepCheck_Analyzer(rail).IsValid()
    return dict(contact=rail,caps=caps,thumb_tools=thumbtools,
                obsolete_tools=[b.box(*p) for p in oldmod.TRIMS])

def expected(old=None):
    if old is None:old,_=load()
    out=old['P01'];g=stocks()
    for tool in g['obsolete_tools']:out=b.cut(out,tool)
    out=b.fuse(out,g['contact'])
    for cap in g['caps']:out=b.fuse(out,cap)
    # User removed the obsolete3mm raised step behind the upright grip.
    # Keep the2mm electronics roof and all stock under/forward ofX-29.
    out=b.cut(out,b.box(*LEDGE_TRIM))
    return {'P01':out}

def profile_fs(name,a,c,lines,arcs,rad,points):
    sk=name+'Sketch';p=f'''        var {sk}=newSketchOnPlane(context,id + "{sk}",{{
            "sketchPlane":plane({vec([0,a,0])},vector(0,-1,0),vector(1,0,0)) }});
'''
    for i,(q,r) in enumerate(lines):p+=f'        skLineSegment({sk},"line{i}",{{"start":{vec(q)},"end":{vec(r)}}});\n'
    for i,(q,m,r) in enumerate(arcs):p+=f'        skArc({sk},"arc{i}",{{"start":{vec(q)},"mid":{vec(m)},"end":{vec(r)}}});\n'
    p+=f'''        skSolve({sk});
        opExtrude(context,id + "{name}",{{"entities":qSketchRegion(id + "{sk}"),
            "direction":vector(0,1,0),"endBound":BoundingType.BLIND,"endDepth":{c-a}*mm }});
        opDeleteBodies(context,id + "{sk}Delete",{{"entities":qCreatedBy(id + "{sk}",EntityType.BODY)}});
        opFillet(context,id + "{name}Ends",{{"entities":qUnion([
'''
    picks=[f'qContainsPoint(qOwnedByBody(body(id + "{name}"),EntityType.EDGE),{vec([q[0],y,q[1]])})' for y in [a,c] for q in points]
    p+='            '+',\n            '.join(picks)+f']),"radius":{rad}*mm,"tangentPropagation":true }});\n'
    return p

def patch_source(source):
    assert hashlib.sha256(source.encode()).hexdigest()==BASE_SHA
    anchor='        const integratedFrame=qBodyType(qUnion([body(id + "base"),body(id + "palmPad")]),BodyType.SOLID);'
    patch='''        // R16: upright palm contact, rounded socket shoulders and thumb returns.
        // Retain the fixed reaction/guide stock belowZ30 and every rod socket.
        // Only the obsolete R14 curved upper palm is replaced.
'''
    for i,(lo,hi) in enumerate(oldmod.TRIMS):
        patch+=f'        makeBox(context,id + "R16Trim{i}",{vec(lo)},{vec(hi)});\n'
        patch+=f'        cut(context,id + "R16TrimCut{i}",body(id + "base"),body(id + "R16Trim{i}"));\n'
    patch+=profile_fs('R16PalmRail',-63,63,RAIL_LINES,RAIL_ARCS,3,[RAIL_MID])
    for i,y in enumerate([-51,51]):
        patch+=f'        makeCylinder(context,id + "R16ThumbRound{i}",{vec([-33,y,14.3])},{vec([-33,y,26])},8*mm);\n'
        patch+=f'        makeYPrism(context,id + "R16ThumbRamp{i}",{y-8.1}*mm,{y+8.1}*mm,[{",".join(vec(q) for q in [[-42,14.3],[-25,14.3],[-25,20],[-31,26],[-42,26]])}]);\n'
        patch+=f'''        opBoolean(context,id + "R16ThumbIntersect{i}",{{
            "tools":qUnion([body(id + "R16ThumbRound{i}"),body(id + "R16ThumbRamp{i}" + "body")]),
            "operationType":BooleanOperationType.INTERSECTION }});
        cut(context,id + "R16ThumbCut{i}",body(id + "R16PalmRail"),
            body(id + "R16ThumbIntersect{i}"));
'''
    picks=[[-29,y,24] for y in [-51,51]]+[[-29,y+s*math.sqrt(48),19] for y in [-51,51] for s in [-1,1]]
    patch+='        opFillet(context,id + "R16ThumbMouthRound",{"entities":qUnion([\n'
    patch+='            '+',\n            '.join(f'qContainsPoint(qOwnedByBody(body(id + "R16PalmRail"),EntityType.EDGE),{vec(p)})' for p in picks)+']),"radius":0.8*mm,"tangentPropagation":true });\n'
    patch+='        join(context,id + "R16PalmRailJoin",[body(id + "base"),body(id + "R16PalmRail")]);\n'
    for i,(a,c) in enumerate([(-65,-37),(37,65)]):
        patch+=profile_fs(f'R16Shoulder{i}',a,c,CAP_LINES,CAP_ARCS,2,[CAP_MID])
        patch+=f'        join(context,id + "R16ShoulderJoin{i}",[body(id + "base"),body(id + "R16Shoulder{i}")]);\n'
    patch+='''        // Remove the obsolete raised palm step wristward of the new grip.
        // Retain the2mm electronics roofZ9.5..11.5, root and catchesX>=-29.
        makeBox(context,id + "R16ObsoleteLedge",vector(-40,-70,11.5)*mm,vector(-29,70,14.5)*mm);
        cut(context,id + "R16ObsoleteLedgeCut",body(id + "base"),body(id + "R16ObsoleteLedge"));
'''
    source=source.replace(anchor,patch+anchor)
    source=source.replace('Fingerworker Flat132 R15 - inboard strap slots and near-sensor palm support.','Fingerworker Flat132 R16 - upright integral palm grip and rounded thumb shoulders.')
    source=source.replace(' * One local76x18mm asymmetric palm rail replaces the obsolete outer bolster.\n * CrownX-20..-19,Z33; all palm stock stays behindX-16; no extra printed part.',
        ' * One126mm-wide upright palm rail has a wrist face atX-29 and crownZ33.\n * Two rounded socket shoulders span130mm and shallow45-degree thumb returns are integral.\n * Central palm stock stays behindX-16; original rod sockets are retained.\n * Obsolete wristward3mm step removed; continuous2mm electronics roof retained.')
    source=source.replace('"Flat132 R15 - inboard strap slots"','"Flat132 R16 - upright palm grip"')
    source=source.replace('P01 PRINT STUDY - Flat132 inboard strap slots, near-sensor palm, fixed sensor support',
        'P01 PRINT STUDY - Flat132 upright palm grip, rounded thumb shoulders, inboard straps')
    return source

def run():
    old,inv=load();g=stocks();new=expected(old)['P01'];rows=[]
    def add(name,ok,**e):rows.append(dict(name=name,status='PASS' if bool(ok) else 'FAIL',**e))
    def vv(shape):assert BRepCheck_Analyzer(shape).IsValid();return b.volume(shape)
    added=b.cut(new,old['P01']);removed=b.cut(old['P01'],new)
    add('One valid solid and shell',BRepCheck_Analyzer(new).IsValid() and b.count(new,TopAbs_SOLID)==b.count(new,TopAbs_SHELL)==1)
    for ref,shape in old.items():
        if ref=='P01':continue
        aa,bb=b.bounds(new),b.bounds(shape)
        if np.any(aa[1]<bb[0]) or np.any(bb[1]<aa[0]):continue
        ov=vv(b.common(new,shape));add('Seated separation / '+ref,ov<1e-6,overlap_mm3=ov)
    # Original baseline interface volumes must remain identical.
    for name,lo,hi in [('fixed reaction/guide belowZ30',[-22.75,-25.4,-3],[2,25.4,30]),
        ('lower roof/floor',[-60,-70,-3],[140,70,14.5]),
        ('left rod socket',[-18,-63,3.8],[-8,-39,28]),('right rod socket',[-18,39,3.8],[-8,63,28])]:
        zone=b.box(lo,hi)
        if name=='lower roof/floor':zone=b.cut(zone,b.box(*LEDGE_TRIM))
        missing=vv(b.common(removed,zone));add('Original '+name+' retained outside declared obsolete step',missing<1e-6,removed_mm3=missing)
    roof=b.box([-38,-62,9.5],[-29,62,11.5]);missing=vv(b.cut(roof,new))
    add('Continuous2mm roof retained below removed step',missing<1e-6,missing_mm3=missing)
    for y in [-51,51]:
        bore=r7.cyl([-17,y,18],[-7,y,18],3.1);ov=vv(b.common(new,bore))
        add('Rod bore open '+str(y),ov<1e-6,overlap_mm3=ov)
    for sign in [-1,1]:
        a,c=(-72,-15.3) if sign<0 else (15.3,72)
        route=r7.cyl([-12.8,a,8.5],[-12.8,c,8.5],3.2);ov=vv(b.common(added,route))
        add('No addition in H18 tool route '+str(sign),ov<1e-6,overlap_mm3=ov)
    for y in [-59,59]:
        ov=vv(b.common(new,r7.cyl([-26.5,y,9.4],[-26.5,y,13.5],1.6)))
        add('Optional enclosure pilot open '+str(y),ov<1e-6,overlap_mm3=ov)
    add('Frame footprint unchanged',np.max(np.abs(b.bounds(new)[:,:2]-b.bounds(old['P01'])[:,:2]))<1e-6)
    for ref in ['P04','H060','H061','P11','H10']:
        # All new material stays behindX-8. Exact swept bounds prove separation.
        bb=b.bounds(old[ref]).copy();bb[0,0]-=30.8 if ref in ['P11','H10'] else 30
        if ref in ['P11','H10']:bb[1,0]+=.8
        gap=b.gap(added,b.box(bb[0],bb[1]));add('Full motion added stock / '+ref,gap>1e-6,gap_lower_bound_mm=gap)
    source=STUDY/'fingerworker_R16_upright_grip.fs';source.write_text(patch_source(BASE_SOURCE.read_text()))
    prior.export(new,HERE/'P01_upright_grip');prior.export(g['contact'],HERE/'contact_rail')
    for i,c in enumerate(g['caps']):prior.export(c,HERE/f'shoulder_{i}')
    spec=dict(revision='R16',source_sha256=sha(source),baseline_source_sha256=BASE_SHA,baseline_native_step_sha256=inv['native_step_sha256'],
        changed=['P01'],new_parts=[],other_native_bodies_unchanged=92,contact_width_mm=126,contact_depth_mm=13,shoulder_width_mm=130,central_wrist_face_x_mm=-29,crown_z_mm=33,
        central_top_radius_mm=5,sensor_side_top_radius_mm=3,rail_end_radius_mm=3,shoulder_top_radius_mm=4,shoulder_end_radius_mm=2,
        thumb_return_centers_y_mm=[-51,51],thumb_return_depth_mm=4,thumb_return_plan_radius_mm=8,thumb_return_ceiling_degrees=45,thumb_mouth_radius_mm=.8,
        contact_envelope_mm=b.bounds(g['contact']).tolist(),shoulder_envelopes_mm=[b.bounds(c).tolist() for c in g['caps']],
        added_mm3=vv(added),removed_mm3=vv(removed),P01_volume_mm3=vv(new),baseline_P01_volume_mm3=vv(old['P01']),
        obsolete_step_removed_bounds_mm=LEDGE_TRIM,wristward_roof_thickness_mm=2,
        preserved='Original rod sockets, reaction/guide stock belowZ30, lower roof/floor outside declared obsolete step, continuous2mm wristward electronics roof, clips, strap slots and all non-P01 bodies.',
        limitations='Local nominal geometry only; native regeneration, full service audits, sliced toolpaths and physical fit/load tests are separate.')
    spec['strap_mount']=json.loads((R15/'mechanics/design-specification.json').read_text())['strap_mount']
    (HERE/'design-specification.json').write_text(json.dumps(spec,indent=2)+'\n')
    report=dict(status='PASS_LOCAL_UPRIGHT_GRIP' if all(r['status']=='PASS' for r in rows) else 'FAIL',checks=rows,metrics=spec,generator_sha256=sha(__file__))
    (HERE/'preflight.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(status=report['status'],checks=len(rows),failures=[r for r in rows if r['status']=='FAIL'],source_sha256=sha(source)),indent=2))

if __name__=='__main__':run()
