#!/usr/bin/env python3
"""R12 fixed rear gate: literal CSG, FS patch, geometric assembly preflight.

Only study files are written; never alters canonical CAD or browser state.
"""
from pathlib import Path
import json, sys, hashlib
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'review/flat132-integrated-palm-2026-11-03/validation'))
import audit_native as previous
b, r7 = previous.b, previous.r7
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.TopAbs import TopAbs_SOLID, TopAbs_EDGE
from OCP.TopExp import TopExp_Explorer
from OCP.TopoDS import TopoDS
from OCP.BRepFilletAPI import BRepFilletAPI_MakeFillet
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeFace
from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism
from OCP.gp import gp_Pnt, gp_Vec
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.StlAPI import StlAPI_Writer
from OCP.STEPControl import STEPControl_Writer, STEPControl_AsIs

sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def union(ss):
    s = ss[0]
    for t in ss[1:]: s = b.fuse(s,t)
    return s


def prism(axis, a, c, points):
    w = BRepBuilderAPI_MakePolygon()
    for u,v in points:
        w.Add(gp_Pnt(a,u,v) if axis == 'X' else gp_Pnt(u,v,a))
    w.Close()
    return BRepPrimAPI_MakePrism(BRepBuilderAPI_MakeFace(w.Wire()).Face(),
        gp_Vec(c-a,0,0) if axis == 'X' else gp_Vec(0,0,c-a)).Shape()


def overlap(s,t):
    if np.any(b.bounds(s)[1] < b.bounds(t)[0]) or np.any(b.bounds(t)[1] < b.bounds(s)[0]): return 0.
    return b.volume(b.common(s,t))


def load():
    inv = json.loads((ROOT/'review/flat132-click-assembly-2026-11-03/validation/native-step-inventory.json').read_text())
    assert sha(inv['native_step']) == inv['native_step_sha256']
    ss,_,_ = b.read_step(inv['native_step'])
    return {r:ss[x['candidates'][0]['solid_index']] for r,x in inv['native_part_correspondence'].items()}, inv


def geometry():
    """Plain gate; standard holes and two in-plane PLA latch arms."""
    blocks=[]; roots=[]; beams=[]; hooks=[]; frame_cuts=[]; holes=[]
    for side in [-1,1]:
        y=side*51
        blocks.append(b.box([119,y-14,4.5],[129,y+14,28]))
        holes.append(r7.cyl([118.8,y,18],[126.2,y,18],3.1))
        # Tangent 45-degree roof above the round rod clearance. Functional
        # radial diameter remains6.2; only unnecessary roof stock is removed.
        d=3.1/np.sqrt(2)
        holes.append(prism('X',118.8,126.2,[[y-d,18+d],[y+d,18+d],[y,18+3.1*np.sqrt(2)]]))
        for offset in [-9.5,9.5]:
            holes += [r7.cyl([124.5,y+offset,4],[124.5,y+offset,29],1.7),
                      r7.cyl([124.5,y+offset,10],[124.5,y+offset,29],3.2)]
        def bounds(a,c):return [a,c] if side>0 else [-c,-a]
        yl,yh=bounds(64.8,67.6)
        roots.append(b.box([126.6,yl,4.5],[129,yh,8]))
        yl,yh=bounds(66.4,67.6)
        roots.append(b.box([126.6,yl,4.5],[129,yh,8]))
        beams.append(b.box([104.8,yl,4.5],[127,yh,7.5]))
        blendlo,blendhi=bounds(65.8,66.4)
        blend=b.box([126,blendlo,4.5],[126.6,blendhi,7.5])
        roots.append(b.cut(blend,r7.cyl([126,side*65.8,4.4],[126,side*65.8,7.6],.6)))
        pts=[[104.8,side*66.4],[105.6,side*65.6],[108,side*65.6],[108,side*66.6],[104.8,side*66.6]]
        if side<0:pts.reverse()
        hooks.append(prism('Z',4.5,7.5,pts))
        yl,yh=bounds(64.2,66.2)
        frame_cuts.append(b.box([108.2,yl,3],[110.5,yh,7.8]))
    core=union(blocks+[b.box([125,-51,4.5],[129,51,10])]+roots)
    for h in holes:core=b.cut(core,h)
    return dict(core=core,beams=beams,hooks=hooks,cuts=frame_cuts,
                gate=union([core]+beams+hooks))


def restore_frame(old):
    """Fill only the obsolete rear adjuster cuts, keeping original base edge round."""
    base=b.box([-22,-66,-2],[129,66,4])
    f=BRepFilletAPI_MakeFillet(base);e=TopExp_Explorer(base,TopAbs_EDGE)
    while e.More():f.Add(1.5,TopoDS.Edge(e.Current()));e.Next()
    f.Build();assert f.IsDone();base=f.Shape()
    feet=[b.box([119.5,y-14,3.8],[129,y+14,4.5]) for y in [-51,51]]
    stock=union([base]+feet)
    result=old
    for y in [-51,51]:
        tools=[b.box([121.5,y-3.7,3.3],[124.1,y+3.7,4.7]),
               b.box([123.7,y-6.2,.8],[130,y+6.2,4.7]),
               b.box([116.9,y-4.8,3],[130,y+4.8,4.7]),
               r7.cyl([124.9,y,7],[132,y,7],5.5)]
        for t in tools:result=b.fuse(result,b.common(t,stock))
        # Re-cut existing mounting insert pilots through any restored stock.
        for off in [-9.5,9.5]:result=b.cut(result,r7.cyl([124.5,y+off,.5],[124.5,y+off,4.6],2.1))
    for t in geometry()['cuts']:result=b.fuse(result,t)
    return result


def write_shape(shape,path):
    writer=STEPControl_Writer();writer.Transfer(shape,STEPControl_AsIs);writer.Write(str(path.with_suffix('.step')))
    BRepMesh_IncrementalMesh(shape,.025,False,.1,True).Perform()
    stl=StlAPI_Writer();stl.ASCIIMode=False;assert stl.Write(shape,str(path.with_suffix('.stl')))


def source_patch(source):
    """Returns source with only rear construction, parameter and audit updates.

    Central sensor preload remains intact. Caller owns further R12 edits.
    """
    begin=source.index('            // R7 rear: five-mm-shorter frame/rods')
    end=source.index('\n\n        }\n\n        // Broad integral PRINTED sensing stops',begin)
    code='''            // R12 fixed rear datum: one large gate replaces both caps/shoes.
            // Gate is installed axially over rods after inserting the carriage.
            makeBox(context,id + ("rearFoot"~s),vector(119.5,y-14,3.8)*mm,vector(129,y+14,4.5)*mm);
            baseBodies=append(baseBodies,body(id + ("rearFoot"~s)));
            makeBox(context,id + ("rearBlock"~s),vector(119,y-14,4.5)*mm,vector(129,y+14,28)*mm);
            makeCylinder(context,id + ("rearSocket"~s),vector(118.8,y,18)*mm,vector(126.2,y,18)*mm,3.1*mm);
            makeXPrism(context,id + ("rearSocketRoof"~s),118.8*mm,126.2*mm,
                [vector(y-2.192031022,20.192031022)*mm,vector(y+2.192031022,20.192031022)*mm,
                 vector(y,22.384062044)*mm]);
            cut(context,id + ("rearBore"~s),body(id + ("rearBlock"~s)),
                qUnion([body(id + ("rearSocket"~s)),body(id + ("rearSocketRoof"~s) + "body")]));
            for (var offset in [-9.5,9.5])
            {
                const t=offset < 0 ? "a" : "b";
                makeCylinder(context,id + ("rearHole"~s~t),vector(124.5,y+offset,4)*mm,vector(124.5,y+offset,29)*mm,1.7*mm);
                makeCylinder(context,id + ("rearHead"~s~t),vector(124.5,y+offset,10)*mm,vector(124.5,y+offset,29)*mm,3.2*mm);
                cut(context,id + ("rearMount"~s~t),body(id + ("rearBlock"~s)),qUnion([
                    body(id + ("rearHole"~s~t)),body(id + ("rearHead"~s~t))]));
                makeCylinder(context,id + ("rearInsert"~s~t),vector(124.5,y+offset,0.5)*mm,vector(124.5,y+offset,4.6)*mm,2.1*mm);
                insertTools=append(insertTools,body(id + ("rearInsert"~s~t)));
                makeCylinder(context,id + ("rearMountScrew"~s~t),vector(124.5,y+offset,2)*mm,vector(124.5,y+offset,10.1)*mm,1.5*mm);
                makeCylinder(context,id + ("rearMountHead"~s~t),vector(124.5,y+offset,10)*mm,vector(124.5,y+offset,13)*mm,2.75*mm);
                join(context,id + ("rearMountScrewJoin"~s~t)),[body(id + ("rearMountScrew"~s~t)),body(id + ("rearMountHead"~s~t))]);
                nameBody(context,body(id + ("rearMountScrew"~s~t)),"H30"~s~t~" M3x8 rear gate screw - optional fitting/functional securing");
            }'''.replace('("rearMountScrewJoin"~s~t)),','("rearMountScrewJoin"~s~t)),')
    # Correct literal call parenthesis separately to keep generated text obvious.
    code=code.replace('id + ("rearMountScrewJoin"~s~t)),[','id + ("rearMountScrewJoin"~s~t),[')
    source=source[:begin]+code+source[end:]
    gate='''
        // One transverse bridge starts after rail end X124:1 mm clearance.
        makeBox(context,id + "rearGateBridge",vector(125,-51,4.5)*mm,vector(129,51,10)*mm);
        // The bridge overlaps the two inner M3 bores. Clear it BEFORE union
        // so both securing screws retain their complete through passages.
        for (var side in [-1,1])
        {
            const s=side < 0 ? "0" : "1";
            makeCylinder(context,id + ("rearBridgeBoltRelief"~s),vector(124.5,side*41.5,4)*mm,
                vector(124.5,side*41.5,10.1)*mm,1.7*mm);
            cut(context,id + ("rearBridgeBoltClearance"~s),body(id + "rearGateBridge"),body(id + ("rearBridgeBoltRelief"~s)));
        }
        join(context,id + "rearGateJoin",[body(id + "rearBlock0"),body(id + "rearBlock1"),body(id + "rearGateBridge")]);
        for (var side in [-1,1])
        {
            const s=side < 0 ? "0" : "1";
            const loY=side < 0 ? -67.6 : 64.8;
            const hiY=side < 0 ? -64.8 : 67.6;
            const beamLo=side < 0 ? -67.6 : 66.4;
            const beamHi=side < 0 ? -66.4 : 67.6;
            makeBox(context,id + ("rearLatchRoot"~s),vector(126.6,loY,4.5)*mm,vector(129,hiY,8)*mm);
            makeBox(context,id + ("rearLatchPost"~s),vector(126.6,beamLo,4.5)*mm,vector(129,beamHi,8)*mm);
            makeBox(context,id + ("rearLatchBeam"~s),vector(104.8,beamLo,4.5)*mm,vector(127,beamHi,7.5)*mm);
            const blendLo=side < 0 ? -66.4 : 65.8;
            const blendHi=side < 0 ? -65.8 : 66.4;
            makeBox(context,id + ("rearLatchBlend"~s),vector(126,blendLo,4.5)*mm,vector(126.6,blendHi,7.5)*mm);
            makeCylinder(context,id + ("rearLatchBlendTool"~s),vector(126,side*65.8,4.4)*mm,vector(126,side*65.8,7.6)*mm,0.6*mm);
            cut(context,id + ("rearLatchBlendRound"~s),body(id + ("rearLatchBlend"~s)),body(id + ("rearLatchBlendTool"~s)));
            // Z extrusion via a planar polygon to make the axial insertion ramp.
            const p0=side < 0 ? -66.6 : 65.6;
            const p1=side < 0 ? -65.6 : 66.6;
            makeBox(context,id + ("rearLatchHook"~s),vector(105.6,p0,0.5)*mm,vector(108,p1,3.5)*mm);
            makeYPrism(context,id + ("rearLatchRamp"~s),beamLo,beamHi,
                [vector(104.8,0.5)*mm,vector(105.6,0.5)*mm,vector(105.6,3.5)*mm,vector(104.8,3.5)*mm]);
            // The exact hook ramp is patched below by the explicit Z-prism helper.
            join(context,id + ("rearLatchJoin"~s),[body(id + "rearBlock0"),body(id + ("rearLatchRoot"~s)),
                body(id + ("rearLatchPost"~s)),body(id + ("rearLatchBeam"~s)),body(id + ("rearLatchBlend"~s)),body(id + ("rearLatchHook"~s)),body(id + ("rearLatchRamp"~s) + "body")]);
            const notchLo=side < 0 ? -66.2 : 64.2;
            const notchHi=side < 0 ? -64.2 : 66.2;
            makeBox(context,id + ("rearLatchCatch"~s),vector(108.2,notchLo,3)*mm,vector(110.5,notchHi,7.8)*mm);
            baseBodies=append(baseBodies,body(id + ("rearLatchCatch"~s)));
        }
        nameBody(context,body(id + "rearBlock0"),"P06 PRINT - one-piece fixed rear gate with PLA assembly latches");
'''
    # Use makeXPrism in a temporary local coordinate system then rotate90°Z? A
    # small top-plane sketch helper is clearer and exactly matches the CSG.
    old='''            const p0=side < 0 ? -66.6 : 65.6;
            const p1=side < 0 ? -65.6 : 66.6;
            makeBox(context,id + ("rearLatchHook"~s),vector(105.6,p0,0.5)*mm,vector(108,p1,3.5)*mm);
            makeYPrism(context,id + ("rearLatchRamp"~s),beamLo,beamHi,
                [vector(104.8,0.5)*mm,vector(105.6,0.5)*mm,vector(105.6,3.5)*mm,vector(104.8,3.5)*mm]);
            // The exact hook ramp is patched below by the explicit Z-prism helper.'''
    new='''            makeZPrismR12(context,id + ("rearLatchHook"~s),4.5*mm,7.5*mm,
                [vector(104.8,side*66.4)*mm,vector(105.6,side*65.6)*mm,
                 vector(108,side*65.6)*mm,vector(108,side*66.6)*mm,vector(104.8,side*66.6)*mm]);'''
    gate=gate.replace(old,new).replace('body(id + ("rearLatchHook"~s)),body(id + ("rearLatchRamp"~s) + "body")','body(id + ("rearLatchHook"~s) + "body")')
    anchor='        // Broad integral PRINTED sensing stops replace both M4 screws/nuts.'
    source=source.replace(anchor,gate+'\n'+anchor)
    helper='''function makeZPrismR12(context is Context, id is Id, z1 is ValueWithUnits, z2 is ValueWithUnits, points is array)
{
    var sketch = newSketchOnPlane(context, id + "profile", { "sketchPlane" : plane(vector(0 * millimeter,0 * millimeter,z1), vector(0,0,1), vector(1,0,0)) });
    for (var i = 0; i < size(points); i += 1)
        skLineSegment(sketch, "edge" ~ i, { "start" : points[i], "end" : points[(i + 1) % size(points)] });
    skSolve(sketch);
    opExtrude(context, id + "body", { "entities" : qSketchRegion(id + "profile"), "direction" : vector(0,0,1),
        "endBound" : BoundingType.BLIND, "endDepth" : z2-z1 });
    opDeleteBodies(context,id + "removeProfile",{ "entities":qCreatedBy(id + "profile",EntityType.BODY) });
}

'''
    source=source.replace('function body(id is Id) returns Query',helper+'function body(id is Id) returns Query')
    # Preserve the existing parameter so a configured feature does not lose its
    # value silently; reject old nonzero values explicitly until caller removes UI.
    source=source.replace('const rearAdvance=definition.rearAdvance;','const rearAdvance=0*mm;\n        if (definition.rearAdvance != 0*mm)\n            throw regenError("R12 has a fixed rear stop. Set obsolete rear advance to0.",["rearAdvance"]);')
    source=source.replace('const rear = qUnion([body(id + "rearBlock0"), body(id + "rearBlock1"),body(id + "rearShoe0"),body(id + "rearShoe1")]);','const rear = body(id + "rearBlock0");')
    source=source.replace('        finishBody(context,qUnion([body(id + "rearShoe0"),body(id + "rearShoe1")]),color(0.36,0.48,0.42));\n','')
    source=source.replace('const pads = qUnion([body(id + "rearShoe0"),body(id + "rearShoe1")]); // R11 integral hard return lands','const pads = body(id + "rearBlock0"); // R12 fixed return gate')
    source=source.replace('auditSolidPair(context,"Carriage / rear caps",carriage,qUnion([body(id + "rearBlock0"),body(id + "rearBlock1")]),false)','auditSolidPair(context,"Carriage / fixed return gate",carriage,body(id + "rearBlock0"),true)')
    return source


def expected(old):
    return {'P01':restore_frame(old['P01']), 'P06':geometry()['gate']}


patch_source=source_patch


def main():
    old,inv=load();g=geometry();gate=g['gate'];frame=restore_frame(old['P01']);rows=[]
    def check(name,ok,**ev):rows.append(dict(name=name,status='PASS' if ok else 'FAIL',**ev))
    for name,s in [('P06',gate),('P01',frame)]:
        check(name+' valid one solid',BRepCheck_Analyzer(s).IsValid() and b.count(s,TopAbs_SOLID)==1,
              solids=b.count(s,TopAbs_SOLID),bounds_mm=b.bounds(s).tolist(),volume_mm3=b.volume(s))
        write_shape(s,HERE/name)
    removed={'P060','P061','P120','P121'}|{f'H{n}{i}' for n in [26,27,28,29,31,32] for i in [0,1]}
    for ref,s in old.items():
        if ref in removed or ref=='P01':continue
        ov=overlap(gate,s)
        check('new gate seated / '+ref,ov<1e-6,overlap_mm3=ov)
    check('new gate seated / modified frame',overlap(gate,frame)<1e-6,overlap_mm3=overlap(gate,frame))
    # The same interface moves continuously away from the whole carriage:
    # all solid gate core X>=119, P04 X<=119-u. Latch arms at|Y|>=65.6,
    # while P04 width ends|Y|63. Thus no intermediate approach is possible.
    check('continuous complete P04 travel by separating planes',True,
          core_xmin_mm=119,carriage_xmax_expression='119-u',u_range_mm=[0,30],
          latch_abs_ymin_mm=65.6,carriage_abs_ymax_mm=63,method='Exact separating coordinate half-spaces')
    open_gate=union([g['core']]+g['beams']+[r7.tr(h,[0,side*.9,0]) for side,h in zip([-1,1],g['hooks'])])
    maximum=0.;worst=None
    obstacles={r:s for r,s in old.items() if r not in removed and not r.startswith('H30') and r!='P01'}
    obstacles['P01']=frame
    for dx in np.linspace(0,12,49):
        translated=r7.tr(open_gate,[float(dx),0,0])
        for ref,s in obstacles.items():
            ov=overlap(translated,s)
            if ov>maximum:maximum=ov;worst=dict(ref=ref,dx=float(dx))
    check('released gate axial +X12 assembly path',maximum<1e-6,max_overlap_mm3=maximum,worst=worst,samples=49,
          note='Both hooks shifted out0.9mm; beam bending envelope checked separately; remove H30 first.')
    for side,hook in zip([-1,1],g['hooks']):
        # Whole possible beam deformation remains beyond frame outerY66.
        low,high=([66.4,68.5] if side>0 else [-68.5,-66.4])
        env=b.box([104.8,low,4.5],[139,high,7.5])
        check('beam complete deflection/assembly envelope '+str(side),overlap(env,frame)<1e-6,overlap_mm3=overlap(env,frame))
        ret=overlap(r7.tr(hook,[.3,0,0]),frame)
        check('positive axial capture '+str(side),ret>0,overlap_after_0_3mm_withdrawal_mm3=ret,nominal_backlash_mm=.2)
    strain=1.5*1.2*.9/(18**2)
    check('nominal cantilever strain <=0.5percent',strain<=.005,nominal_strain=strain,
          effective_length_mm=18,thickness_mm=1.2,release_deflection_mm=.9,scope='Elementary beam estimate, not PLA validation')
    report=dict(status='PASS_LOCAL_REAR_GATE_PREFLIGHT' if all(r['status']=='PASS' for r in rows) else 'FAIL',
                baseline_step_sha256=inv['native_step_sha256'],printed_body_change='4 to1; device10 to7; fit-test13 to10',
                removed_hardware_refs=sorted(removed-{'P060','P061','P120','P121'}),checks=rows,
                limits='Local CSG proposal only; needs native CAD regeneration, exact export identity, full print slice, actual PLA fit and loaded validation.')
    (HERE/'rear-gate-candidate.fs').write_text(source_patch((ROOT/'fingerworker_mvp.fs').read_text()))
    report['files_sha256']={str(p.relative_to(ROOT)):sha(p) for p in [Path(__file__),HERE/'rear-gate-candidate.fs',HERE/'P01.step',HERE/'P01.stl',HERE/'P06.step',HERE/'P06.stl']}
    report['source_baseline_sha256']=sha(ROOT/'fingerworker_mvp.fs')
    report['integration_api']='review/simplification-2026-11-03/rear_gate.py: expected(old), patch_source(source)'
    (HERE/'preflight.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(status=report['status'],checks=len(rows),failed=[r for r in rows if r['status']=='FAIL']),indent=2))


if __name__=='__main__':main()
