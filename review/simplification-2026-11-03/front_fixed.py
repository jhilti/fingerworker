#!/usr/bin/env python3
"""Fixed sensor reaction support: independent local R12 study/integration API.

Keeps real H12/sensor/pusher/keeper geometry; removes user-rejected preload.
"""
from pathlib import Path
import hashlib,json,re,sys
import numpy as np

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE))
import rear_gate as rear
b,r7=rear.b,rear.r7
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.TopAbs import TopAbs_SOLID
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps

REMOVED={'H11','H13','H15','H160','H161','H170','H171','H21','H22'}
PROFILE=[[-9,3.8],[9,3.8],[9,9.5],[11,11.5],[11,26],[-11,26],[-11,11.5],[-9,9.5]]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def union(ss):
    out=ss[0]
    for s in ss[1:]:out=b.fuse(out,s)
    return out


def stocks():
    wall=b.box([-22.75,-25.4,3.8],[-16,25.4,33])
    support=r7.xprism(-16.2,-12,PROFILE)
    # Native construction later reapplies the inherited sensor-floor pocket.
    # It removes the lowest0.4mm of the front0.3mm strip from this pad.
    support=b.cut(support,b.box([-12.3,-15.3,2.7],[2.9,15.3,4.2]))
    palm=b.box([-25.5,-16.5,9.5],[-23.25,16.5,14.5])
    slotfills=[];roundholes=[]
    for side in [-1,1]:
        lo=-20.5 if side<0 else 15.5
        guide=b.box([-16.2,lo,3.8],[-8,lo+5,29])
        slotlo=-20.7 if side<0 else 15.3
        oldslot=union([r7.cyl([-12.6,side*15.3,8.5],[-12.6,side*20.7,8.5],2.2),
            r7.cyl([-11,side*15.3,8.5],[-11,side*20.7,8.5],2.2),
            b.box([-12.6,slotlo,6.3],[-11,slotlo+5.4,10.7])])
        slotfills.append(b.common(oldslot,guide))
        roundholes.append(r7.cyl([-12.8,side*15.3,8.5],[-12.8,side*20.7,8.5],2.2))
    # Only the free centre of the old top bridge is unique material; its
    # overlap in the main wall and two sloping buttresses remains unchanged.
    bridgecut=b.box([-16,-20.3,30],[-12.5,20.3,33])
    return dict(wall=wall,support=support,palm=palm,slotfills=slotfills,
                roundholes=roundholes,bridgecut=bridgecut)


def expected(old):
    s=stocks()
    frame=union([old['P01'],s['wall'],s['support'],s['palm']]+s['slotfills'])
    for h in s['roundholes']:frame=b.cut(frame,h)
    frame=b.cut(frame,s['bridgecut'])
    return {'P01':frame}


def patch_source(source):
    # The old notch exists only to service the now deleted H15 plate.
    a=source.index('        // R10: lower H15 edge needs2 mm rearward release')
    z=source.index('        nameBody(context,body(id + "palmPad"),',a)
    source=source[:a]+source[z:]
    a=source.index('        makeBox(context,id + "reactionTopBridge"')
    z=source.index('        baseBodies=append(baseBodies,body(id + "loadCellWall"));',a)
    fixed='''        // R12: no preload mechanism. H12 rear datum X-12 bears on this
        // broad fixed support. Lower pillar and45-degree shoulders print
        // upward from the base and clear all four rear keeper-screw tips.
        makeXPrism(context,id + "fixedSensorReaction",-16.2*mm,-12*mm,
            [vector(-9,3.8)*mm,vector(9,3.8)*mm,vector(9,9.5)*mm,
             vector(11,11.5)*mm,vector(11,26)*mm,vector(-11,26)*mm,
             vector(-11,11.5)*mm,vector(-9,9.5)*mm]);
        join(context,id + "fixedSensorReactionJoin",[body(id + "loadCellWall"),body(id + "fixedSensorReaction" + "body")]);
'''
    source=source[:a]+fixed+source[z:]
    a=source.index('            // Slot X=-14.8..-8.8;')
    z=source.index('            makeCylinder(context,id + ("captureSpacer"~t)',a)
    source=source[:a]+'''            // Fixed cassette retention: no deliberate axial adjustment slot.
            // ExistingOD4 steel spacers have0.2mm nominal radial clearance.
            makeCylinder(context,id + ("captureFixedBore"~t),vector(-12.8,side*15.3,8.5)*mm,
                vector(-12.8,side*20.7,8.5)*mm,2.2*mm);
            cut(context,id + ("captureFixedDrill"~t),body(id + ("cassetteGuide"~t)),body(id + ("captureFixedBore"~t)));
'''+source[z:]
    source=source.replace('Steel spacer 4 x 3.2 x 6 - preload travel limiter','Steel spacer 4 x 3.2 x 6 - fixed cassette retention')
    a=source.index('        makeCylinder(context,id + "preloadScrew"')
    z=source.index('        // H01 is the genuine STEP solid selected above',a)
    source=source[:a]+source[z:]
    source=source.replace('''        annotation { "Name" : "Additional synchronized preload (0 to 2 mm)" }
        isLength(definition.preloadAdjustment, LENGTH_BOUNDS);
''','')
    source=source.replace('''        const preload = definition.preloadAdjustment;
        if (preload < 0 * mm || preload > 2 * mm)
            throw regenError("Additional preload must be between 0 and 2 mm.", ["preloadAdjustment"]);''',
        '        const preload = 0*mm; // R12 fixed sensor reaction, no adjustable preload.')
    a=source.index('        if (preload > 0*mm)')
    z=source.index('        println({"mode":',a)
    source=source[:a]+source[z:]
    # Remove audits of deleted hardware; keep an explicit intended H12/frame
    # reaction-face contact and all sensor/yoke separation policies.
    labels=['Keeper hardware / fixed wall and keeper','Keeper hardware / moving stack and palm',
            'Preload lock / adjusting screw','Adjustment hardware / base',
            'Adjustment hardware / yoke carriage palm','Preload screw / cassette','Preload screw / palm']
    for label in labels:
        token='        auditSolidPair(context,"'+label+'"'
        a=source.index(token);j=source.index('(',a);depth=0;quoted=False;escaped=False
        for k in range(j,len(source)):
            c=source[k]
            if quoted:
                if escaped:escaped=False
                elif c==chr(92):escaped=True
                elif c=='"':quoted=False
            elif c=='"':quoted=True
            elif c=='(':depth+=1
            elif c==')':
                depth-=1
                if depth==0:
                    z=k+1
                    if source[z:z+1]==',':z+=1
                    if source[z:z+1]=='\n':z+=1
                    break
        source=source[:a]+source[z:]
    source=re.sub(r'    const keeperHardware=.*?;\n','',source,count=1)
    source=source.replace(',sensor,body(id + "preloadScrew"),keeperHardware]),false)',',sensor]),false)')
    source=source.replace('"Sensor / translating cassette"','"Sensor / fixed cassette"')
    source=source.replace('"Cassette / fixed guide",body(id + "sensorCassette"),base,false',
                          '"Cassette / fixed reaction and guide",body(id + "sensorCassette"),base,true')
    source=source.replace('"preloadAdjustment":0*millimeter,','')
    # The rear-gate patch may deliberately retain a zero-only legacy input.
    # R12 final UI removes it, since the user has now rejected all adjusters.
    source=source.replace('''        annotation { "Name" : "Equal rear screw advance a (0 to 2 mm; a + preload <= 2)" }
        isLength(definition.rearAdvance, { (millimeter) : [0, 0, 2] } as LengthBoundSpec);
''','')
    source=source.replace('''const rearAdvance=0*mm;
        if (definition.rearAdvance != 0*mm)
            throw regenError("R12 has a fixed rear stop. Set obsolete rear advance to0.",["rearAdvance"]);''','const rearAdvance=0*mm;')
    source=source.replace('const rearAdvance=definition.rearAdvance;','const rearAdvance=0*mm;')
    source=source.replace('"rearAdvance":0*millimeter,','')
    source=source.replace('''        if (rearAdvance < 0*mm || rearAdvance > 2*mm || rearAdvance+preload > 2*mm+1e-6*mm)
            throw regenError("Set BOTH rear screws equally: advance plus sensor preload must be0..2 mm to retain28..30 mm stroke.",["rearAdvance","preloadAdjustment"]);
''','')
    source=source.replace('User travel (0 to 30 minus preload minus rear advance; reset cam shoe)','User travel (0 to 30 mm; fixed rest and sensor reaction)')
    source=source.replace('Isometric: BOTH81 mm sleeves; approach15 minus preload minus rear advance','Isometric: BOTH81 mm sleeves; fixed15 mm approach')
    source=source.replace('R7 user travel is30 mm minus preload minus rear advance. Keep advance plus preload<=2; manually reset the cam shoe after preload changes.','R12 user travel is0..30 mm with fixed rest and sensor reaction.')
    source=source.replace('["previewTravel", "preloadAdjustment"]','["previewTravel"]')
    source=source.replace('P11 PRINT STUDY - guided stepped cam shoe, manually set trim minus preload','P11 PRINT STUDY - guided switch cam, physical calibration trim only')
    return source


def main():
    out=HERE/'front';out.mkdir(exist_ok=True)
    old,inv=rear.load();s=stocks();new=expected(old)['P01'];rows=[]
    def add(name,ok,**e):rows.append(dict(name=name,status='PASS' if ok else 'FAIL',**e))
    add('Fixed P01 is a valid single solid',BRepCheck_Analyzer(new).IsValid() and b.count(new,TopAbs_SOLID)==1,
        solids=b.count(new,TopAbs_SOLID),volume_mm3=b.volume(new),bounds_mm=b.bounds(new).tolist())
    additions=union([s['wall'],s['support'],s['palm']]+s['slotfills'])
    for h in s['roundholes']:additions=b.cut(additions,h)
    # Checks are limited to the literal changed stocks; original R11 geometry
    # and service remains protected by native identity in final integration.
    for ref,other in old.items():
        if ref in REMOVED or ref=='P01':continue
        if np.any(b.bounds(additions)[1]<b.bounds(other)[0]) or np.any(b.bounds(other)[1]<b.bounds(additions)[0]):continue
        common=b.common(additions,other)
        add('Added fixed stock / '+ref,BRepCheck_Analyzer(common).IsValid() and b.volume(common)<1e-6,
            intersection_mm3=b.volume(common),boolean_valid=BRepCheck_Analyzer(common).IsValid())
    probes=[]
    for dx in [.001,.01]:
        # OCC solid-common drops a purely tangent face; advance a copy of the
        # support into the unchanged plate and divide the valid thin overlap
        # volume by its exact axial depth. This does not alter CAD geometry.
        c=b.common(r7.tr(s['support'],[dx,0,0]),old['H12'])
        probes.append(dict(depth_mm=dx,area_mm2=b.volume(c)/dx,boolean_valid=BRepCheck_Analyzer(c).IsValid()))
    add('H12 directly bears on fixed reaction plane',abs(b.gap(s['support'],old['H12']))<1e-7 and all(p['boolean_valid'] and abs(p['area_mm2']-454.4)<1e-4 for p in probes),
        contact_area_mm2=454.4,rear_datum_x_mm=-12,gap_mm=b.gap(s['support'],old['H12']),
        area_method='Two valid thin-overlap volume/depth probes on translated support copies; actual nominal parts have zero overlap.',probes=probes)
    for ref in ['P05','H01','H02','H23','H250','H251','H252','H253']:
        add('Support does not bypass sensor through '+ref,b.gap(s['support'],old[ref])>1e-6,gap_mm=b.gap(s['support'],old[ref]))
    # Service witness only against added stock. Every added stock lies behind
    # the sensor/yoke or outside the ears. Original service path inherited.
    moving=['H01','H02','H050','H051','H12','H20','H23']+[f'H24{i}' for i in range(4)]+[f'H25{i}' for i in range(4)]+['P05']
    maxov=0.;worst=None
    for mode,values in [('forward',np.linspace(0,3.2,17)),('up',np.linspace(0,40,41))]:
        for d in values:
            v=[float(d),0,0] if mode=='forward' else [3.2,0,float(d)]
            for ref in moving:
                q=r7.tr(old[ref],v)
                if np.any(b.bounds(q)[1]<b.bounds(additions)[0]) or np.any(b.bounds(additions)[1]<b.bounds(q)[0]):continue
                c=b.common(q,additions);vol=b.volume(c)
                if not BRepCheck_Analyzer(c).IsValid():raise RuntimeError('Invalid service intersection '+ref)
                if vol>maxov:maxov=vol;worst=dict(ref=ref,mode=mode,d=float(d))
    add('Complete sensor-yoke stack service clears new stocks',maxov<1e-6,max_overlap_mm3=maxov,worst=worst,
        forward_mm=3.2,up_mm=40,poses=58,prerequisites='Unload/remove springs, rods, rear gate and H18/H19; retain sensor keeper assembly.')
    # Round retention bores still clear original spacers and outward access.
    for side,i in [(-1,0),(1,1)]:
        for ref in [f'H18{i}',f'H19{i}']:
            maxov=0.
            for d in np.linspace(0,55,56):
                c=b.common(r7.tr(old[ref],[0,side*float(d),0]),new)
                if not BRepCheck_Analyzer(c).IsValid():raise RuntimeError('Invalid retaining-path intersection '+ref)
                maxov=max(maxov,b.volume(c))
            add(ref+' outward service through fixed circular guide',maxov<1e-6,max_overlap_mm3=maxov,travel_mm=55,poses=56)
    rear._impl.write_shape(new,out/'P01_fixed_front')
    rear._impl.write_shape(s['support'],out/'fixed_reaction_stock')
    source=patch_source(rear.patch_source((ROOT/'fingerworker_mvp.fs').read_text()))
    (out/'R12_rear_and_fixed_front_candidate.fs').write_text(source)
    report=dict(status='PASS_LOCAL_FIXED_FRONT_PREFLIGHT' if all(x['status']=='PASS' for x in rows) else 'FAIL',
        removed_refs=sorted(REMOVED),baseline_step_sha256=inv['native_step_sha256'],checks=rows,
        fixed_parameters=dict(preload_mm=0,rear_advance_mm=0,user_travel_mm=[0,30],isometric_approach_mm=15),
        unchanged_hardware='H12/H01/H02/H18/H19/H20/H23/H24/H25 exact original shapes; only9 obsolete preload bodies deleted.',
        limitations='Local nominal CSG and service checks only. Actual native CAD/export and print paths still required. PLA load, creep and sensor performance remain unqualified.')
    report['files_sha256']={str(p.relative_to(ROOT)):sha(p) for p in [Path(__file__),out/'R12_rear_and_fixed_front_candidate.fs',out/'P01_fixed_front.step',out/'P01_fixed_front.stl']}
    (out/'preflight.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(status=report['status'],checks=len(rows),failed=[x for x in rows if x['status']=='FAIL']),indent=2),flush=True)


if __name__=='__main__':main()
