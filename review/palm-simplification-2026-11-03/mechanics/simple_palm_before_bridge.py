#!/usr/bin/env python3
"""Offline R13 palm candidate. Frozen R12 source and native geometry are inputs."""
from pathlib import Path
import hashlib, importlib.util, json, sys
import numpy as np

HERE=Path(__file__).resolve().parent
STUDY=HERE.parent
ROOT=STUDY.parents[1]
R12=ROOT/'review/simplification-2026-11-03'
_spec=importlib.util.spec_from_file_location('palm_r12_rear',R12/'rear_gate.py')
rear=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(rear)
b,r7=rear.b,rear.r7
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepFilletAPI import BRepFilletAPI_MakeFillet
from OCP.TopAbs import TopAbs_EDGE,TopAbs_SOLID
from OCP.TopExp import TopExp_Explorer
from OCP.TopoDS import TopoDS
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.StlAPI import StlAPI_Writer
from OCP.STEPControl import STEPControl_Writer,STEPControl_AsIs

sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def union(shapes):
    out=shapes[0]
    for s in shapes[1:]:out=b.fuse(out,s)
    return out

def fillet(s,r,vertical=False):
    f=BRepFilletAPI_MakeFillet(s);e=TopExp_Explorer(s,TopAbs_EDGE)
    while e.More():
        edge=TopoDS.Edge(e.Current());bounds=b.bounds(edge);d=bounds[1]-bounds[0]
        if not vertical or (d[0]<1e-6 and d[1]<1e-6 and d[2]>1e-3):f.Add(r,edge)
        e.Next()
    f.Build();assert f.IsDone();assert BRepCheck_Analyzer(f.Shape()).IsValid()
    return f.Shape()

def stocks():
    # Same nominal central contact curve as R12, now uniform over116 mm.
    rail=fillet(r7.cyl([-27,-58,19.75],[-27,58,19.75],10.25),1.2)
    rail=b.cut(rail,b.box([-27,-60,0],[0,60,40]))
    # Stop before original front-rod socket and H18 lateral access envelopes.
    # Leave end catch shelves atY+/-64 andZ14.5 completely unchanged.
    web=fillet(b.box([-27.1,-58,9.5],[-17.1,58,30]),2,vertical=True)
    holes=[r7.cyl([-26.5,y,9.4],[-26.5,y,13.5],1.6) for y in [-59,59]]
    return dict(rail=rail,web=web,pilots=holes)

def expected(old):
    g=stocks();out=union([old['P01'],g['rail'],g['web']])
    # Existing pilot cylinders reach inward toY57.4: recut after both unions.
    for h in g['pilots']:out=b.cut(out,h)
    return {'P01':out}

def load():
    inv=json.loads((R12/'validation/native-step-inventory.json').read_text())
    assert sha(inv['native_step'])==inv['native_step_sha256']
    ss,_,_=b.read_step(inv['native_step'])
    return {r:ss[x['candidates'][0]['solid_index']] for r,x in inv['native_part_correspondence'].items()},inv

def patch_source(source):
    anchor='        const integratedFrame=qBodyType(qUnion([body(id + "base"),body(id + "palmPad")]),BodyType.SOLID);'
    assert source.count(anchor)==1 and 'R13PalmUniformRail' not in source
    patch='''        // R13: one constant-radius palm rail and one broad continuous web.
        // R12 underside, electronics catches and functional sensor portal stay.
        makeCylinder(context,id + "R13PalmUniformRail",vector(-27,-58,19.75)*mm,
            vector(-27,58,19.75)*mm,10.25*mm);
        opFillet(context,id + "R13PalmEndRound",{
            "entities":qCreatedBy(id + "R13PalmUniformRail",EntityType.EDGE),
            "radius":1.2*mm,"tangentPropagation":true });
        makeBox(context,id + "R13PalmForwardHalfTool",vector(-27,-60,0)*mm,
            vector(0,60,40)*mm);
        cut(context,id + "R13PalmHalfCut",body(id + "R13PalmUniformRail"),
            body(id + "R13PalmForwardHalfTool"));
        makeBox(context,id + "R13PalmContinuousWeb",vector(-27.1,-58,9.5)*mm,
            vector(-17.1,58,30)*mm);
        opFillet(context,id + "R13PalmWebCorners",{
            "entities":qParallelEdges(qCreatedBy(id + "R13PalmContinuousWeb",EntityType.EDGE),vector(0,0,1)),
            "radius":2*mm,"tangentPropagation":true });
        join(context,id + "R13PalmContinuousJoin",[body(id + "base"),
            body(id + "R13PalmUniformRail"),body(id + "R13PalmContinuousWeb")]);
        // New web reaches the inner edges of the existing optional M2 pilots.
        // Recut them after union so both original mounting routes remain open.
        for (var y in [-59,59])
        {
            const s=y < 0 ? "0" : "1";
            makeCylinder(context,id + ("R13PalmPilot"~s),
                vector(-26.5,y,9.4)*mm,vector(-26.5,y,13.5)*mm,1.6*mm);
            cut(context,id + ("R13PalmPilotCut"~s),body(id + "base"),
                body(id + ("R13PalmPilot"~s)));
        }
'''
    source=source.replace(anchor,patch+anchor)
    source=source.replace('P01 PRINT STUDY - Flat132 integral frame and solid palm, no palm fasteners or sleeve',
                          'P01 PRINT STUDY - Flat132 continuous palm rail and web, fixed sensor support')
    return source

def export(s,path):
    path=Path(path)
    w=STEPControl_Writer();w.Transfer(s,STEPControl_AsIs);w.Write(str(path.with_suffix('.step')))
    BRepMesh_IncrementalMesh(s,.025,False,.15,True)
    w=StlAPI_Writer();w.ASCIIMode=False;w.Write(s,str(path.with_suffix('.stl')))

def run():
    old,inv=load();new=expected(old)['P01'];g=stocks()
    source=R12/'fingerworker_R12_simplified.fs'
    (HERE/'R13_palm_candidate.fs').write_text(patch_source(source.read_text()))
    export(new,HERE/'P01_simple_palm');export(g['rail'],HERE/'uniform_rail');export(g['web'],HERE/'continuous_web')
    rows=[]
    def add(name,ok,**e):rows.append(dict(name=name,status='PASS' if bool(ok) else 'FAIL',**e))
    def vol(s):
        assert BRepCheck_Analyzer(s).IsValid(),'Invalid Boolean';return b.volume(s)
    ex=TopExp_Explorer(new,TopAbs_SOLID);count=0
    while ex.More():count+=1;ex.Next()
    add('Valid single P01 solid',BRepCheck_Analyzer(new).IsValid() and count==1,solids=count)
    added=b.cut(new,old['P01']);removed=b.cut(old['P01'],new)
    add('No R12 frame material removed',vol(removed)<1e-6,removed_mm3=vol(removed))
    aa=b.bounds(added)
    add('Added material behind functional interfaces and above lid',aa[1,0]<-17 and aa[0,2]>=9.5-1e-6,
        bounds_mm=aa.tolist(),added_volume_mm3=vol(added))
    for ref,s in old.items():
        if ref=='P01':continue
        bb=b.bounds(s)
        if np.any(aa[1]<bb[0]) or np.any(bb[1]<aa[0]):continue
        ov=vol(b.common(added,s))
        add('No new intersection with '+ref,ov<1e-6,intersection_mm3=ov)
    # Exact preservation of the existing clearance belowZ9.5 and both clip
    # landings, not samples. New downward faces atZ9.5 still need slice review.
    low=b.box([-60,-70,-3],[0,70,9.5])
    for label,zone in [('electronics clearance volume below Z9.5',low),
        ('negative tray catch landing',b.box([-30,-66,9.4],[-24,-62,16.5])),
        ('positive tray catch landing',b.box([-30,62,9.4],[-24,66,16.5])),
        ('sensor functional front region',b.box([-17,-70,-3],[35,70,50]))]:
        delta=vol(b.common(added,zone))+vol(b.common(removed,zone))
        add('Unchanged '+label,delta<1e-6,difference_mm3=delta)
    for i,h in enumerate(g['pilots']):
        ov=vol(b.common(new,h));add('Optional M2 pilot remains open '+str(i),ov<1e-6,intersection_mm3=ov)
    # Full H18 tool/head/spacer outward route uses this fixed XZ cylinder.
    for side in [-1,1]:
        y0,y1=(-72,-15.3) if side<0 else (15.3,72)
        route=r7.cyl([-12.8,y0,8.5],[-12.8,y1,8.5],3.2)
        add('No new H18 lateral service obstruction '+str(side),vol(b.common(added,route))<1e-6)
    report=dict(status='PASS_LOCAL_CONTINUOUS_PALM' if all(x['status']=='PASS' for x in rows) else 'FAIL',
        baseline_native_step_sha256=inv['native_step_sha256'],baseline_source_sha256=sha(source),
        candidate_source_sha256=sha(HERE/'R13_palm_candidate.fs'),generator_sha256=sha(__file__),
        checks=rows,limitations='Offline geometry candidate only. Native CAD export, full service/motion and actual slice must be rechecked. New undersides over small gaps may create new support and require slicing review.')
    (HERE/'preflight.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(status=report['status'],checks=len(rows),failed=[x for x in rows if x['status']=='FAIL'],added_volume_mm3=vol(added)),indent=2))

if __name__=='__main__':run()
