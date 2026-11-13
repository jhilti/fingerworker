#!/usr/bin/env python3
"""Local R12 candidate only: move the rigid lid into P01, retain P08 clicks.

No canonical source or browser mutation. R10 native solids are exact retained
R11 bodies except the R11 enclosure stocks explicitly reconstructed here.
"""
from pathlib import Path
import hashlib,json,sys,re
import numpy as np
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.TopAbs import TopAbs_SOLID
from OCP.STEPControl import STEPControl_Writer,STEPControl_AsIs
from OCP.StlAPI import StlAPI_Writer
from OCP.BRepMesh import BRepMesh_IncrementalMesh

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'review/flat132-click-assembly-2026-11-03/enclosure'))
import build_enclosure as e

def write(name,data): (HERE/name).write_text(json.dumps(data,indent=2)+'\n')
def export(ref,shape):
    writer=STEPControl_Writer();writer.Transfer(shape,STEPControl_AsIs);writer.Write(str(HERE/(ref+'.step')))
    mesh=BRepMesh_IncrementalMesh(shape,.025,False,.1,True);mesh.Perform()
    stl=StlAPI_Writer();stl.ASCIIMode=False;assert stl.Write(shape,str(HERE/(ref+'_assembly.stl')))

def ledger_shape(key,omit=()):
    ledger=json.loads((ROOT/'mechanical/manufacturing-2026-10-11/source/operation-ledger.json').read_text())[key]
    result=None
    for i,op in enumerate(ledger):
        if i in omit:continue
        a=op['args']
        if op['shape']=='box':s=e.b.box(*a)
        elif op['shape']=='cyl':
            assert a[0][:2]==a[1][:2]
            s=e.cylinder(a[0][0],a[0][1],a[0][2],a[1][2],a[2])
        else:raise ValueError(op)
        if op['operation']=='base':result=s
        elif op['operation']=='add':result=e.b.fuse(result,s)
        else:result=e.b.cut(result,s)
    return result

def make(old):
    ts,ls=e.stocks()
    bridge=e.b.box([-46.1,-55,8.9],[-23.6,55,9.6])
    # Preserve reliefs where the existing P08 optional M2 mount ears enter.
    for y0,y1 in [(-56.1,-53.9),(53.9,56.1)]:
        bridge=e.b.cut(bridge,e.b.box([-29.1,y0,8.8],[-23.9,y1,9.7]))
    # H15 keeper slides toward -X before rising. Retain the R10 service notch
    # above the 0.8 mm ceiling skin; the skin top 8.9 stays below H15 Zmin 9.
    bridge=e.b.cut(bridge,e.b.box([-25.5,-16.5,8.9],[-23.1,16.5,14.7]))
    # Fixed ceiling needs neither three lid screw holes nor their posts.
    rigid_lid=ledger_shape('P09_Electronics_lid',range(3,9))
    keeper=e.union([rigid_lid]+[s['shape'] for s in ls if s['tag']=='integralWireClamp'])
    additions=e.union([keeper,bridge])
    frame=e.b.fuse(old['P01'],additions)
    # No separate lid, so its two exterior catches are unnecessary.
    tray_stocks=[s for s in ts if not s['tag'].startswith('lidCatch')]
    tray_core=ledger_shape('P08_Electronics_tray',set(range(14,20))|{21,23})
    tray=e.union([tray_core]+[s['shape'] for s in tray_stocks])
    return frame,tray,additions,tray_stocks

def expected(old):
    """R12 ceiling/tray outputs; composes with independently edited old P01."""
    frame,tray,_,_=make(old)
    return {'P01':frame,'P08':tray}

def source_patch(source):
    """Patch R11, or a rear-only derivative; roof exists with electronics off."""
    start=source.index('    makeBox(context,id + "P09_Electronics_lid",')
    end=source.index('\n}\n// END GENERATED ENCLOSURE REV A',start)
    source=source[:start]+'    return body(id + "P08_Electronics_tray");'+source[end:]
    omit=set(range(14,20))|{21,23}
    lines=[]
    for line in source.splitlines():
        m=re.search(r'"P08_Electronics_tray_(\d+)(?:Cut|Join)?"',line)
        if m and int(m.group(1)) in omit:continue
        if '"R11TraylidCatch' in line:continue
        lines.append(line)
    source='\n'.join(lines)+'\n'
    assert 'P09_Electronics_lid' not in source
    def v(x):return 'vector('+','.join(f'{n:g}' for n in x)+')*mm'
    ledger=json.loads((ROOT/'mechanical/manufacturing-2026-10-11/source/operation-ledger.json').read_text())['P09_Electronics_lid']
    root='R12FixedElectronicsCeiling'
    code=['// R12 permanent electronics ceiling: always part of P01.',
          '// Call after all legacy region audits, immediately before final fusion.',
          'function makeIntegratedElectronicsCeiling(context is Context, id is Id) returns Query',
          '{','    const mm=millimeter;']
    for i,op in enumerate(ledger):
        if i in range(3,9):continue
        assert op['shape']=='box'
        tag=root if i==0 else root+str(i)
        code.append(f'    makeBox(context,id + "{tag}",{v(op["args"][0])},{v(op["args"][1])});')
        if op['operation']=='add':code.append(f'    join(context,id + "{tag}Join",[body(id + "{root}"),body(id + "{tag}")]);')
        elif op['operation']=='cut':code.append(f'    cut(context,id + "{tag}Cut",body(id + "{root}"),body(id + "{tag}"));')
    code += [f'    makeBox(context,id + "R12FixedWireClamp",vector(-28.1,22.4,3.4)*mm,vector(-24.9,32.6,8.2)*mm);',
             f'    join(context,id + "R12FixedWireClampJoin",[body(id + "{root}"),body(id + "R12FixedWireClamp")]);',
             '    makeBox(context,id + "R12RoofBridge",vector(-46.1,-55,8.9)*mm,vector(-23.6,55,9.6)*mm);']
    for tag,y0,y1 in [('L',-56.1,-53.9),('R',53.9,56.1)]:
        code += [f'    makeBox(context,id + "R12RoofRelief{tag}",vector(-29.1,{y0:g},8.8)*mm,vector(-23.9,{y1:g},9.7)*mm);',
                 f'    cut(context,id + "R12RoofRelief{tag}Cut",body(id + "R12RoofBridge"),body(id + "R12RoofRelief{tag}"));']
    code += ['    makeBox(context,id + "R12RoofKeeperService",vector(-25.5,-16.5,8.9)*mm,vector(-23.1,16.5,14.7)*mm);',
             '    cut(context,id + "R12RoofKeeperServiceCut",body(id + "R12RoofBridge"),body(id + "R12RoofKeeperService"));']
    code += [f'    join(context,id + "R12RoofBridgeJoin",[body(id + "{root}"),body(id + "R12RoofBridge")]);',
             f'    return body(id + "{root}");','}','']
    anchor='// BEGIN GENERATED ENCLOSURE REV A'
    assert source.count(anchor)==1
    source=source.replace(anchor,'\n'.join(code)+'\n'+anchor)
    anchor='        const integratedFrame=qBodyType(qUnion([body(id + "base"),body(id + "palmPad")]),BodyType.SOLID);'
    assert source.count(anchor)==1
    source=source.replace(anchor,'        const fixedElectronicsCeiling=makeIntegratedElectronicsCeiling(context,id);\n'
        +'        join(context,id + "integrateElectronicsCeiling",[body(id + "base"),fixedElectronicsCeiling]);\n'+anchor)
    source=source.replace('P01 PRINT STUDY - Flat132 integral frame and solid palm, no palm fasteners or sleeve',
        'P01 PRINT STUDY - Flat132 integral frame palm and electronics ceiling')
    source=source.replace('P08 PRINT - Snap electronics tray, optional M2 mount',
        'P08 PRINT - Simple snap electronics tray, fixed P01 ceiling, optional M2 mount')
    return source

def main():
    old,inv=e.load();frame,tray,additions,ts=make(old)
    checks=[]
    def add(name,ok,**more):checks.append(dict(name=name,status='PASS' if ok else 'FAIL',**more))
    for ref,s in [('P01_integrated_ceiling',frame),('P08_no_lid_catches',tray)]:
        export(ref,s)
        add(ref+' valid single solid',BRepCheck_Analyzer(s).IsValid() and e.b.count(s,TopAbs_SOLID)==1,
            volume_mm3=e.b.volume(s),bounds_mm=e.b.bounds(s).tolist(),solids=e.b.count(s,TopAbs_SOLID))
    add('P01 stock added',True,added_mm3=e.b.volume(frame)-e.b.volume(old['P01']),
        original_lid_mm3=e.b.volume(old['P09']),original_integral_clamp_mm3=e.b.volume([s['shape'] for s in e.stocks()[1] if s['tag']=='integralWireClamp'][0]))
    # Electronics, PCB envelopes and battery all remain with the removable tray.
    electronics={r:s for r,s in old.items() if r.startswith(('E','PCB_')) and r not in ['E06','E08']}
    for ref,s in electronics.items():
        bb=e.b.bounds(s).copy();bb[0,2]-=20
        bound=e.b.box(*bb)
        v=e.b.volume(e.b.common(frame,bound))
        add('Loaded tray -Z20 continuous electronics envelope '+ref,v<1e-6,
            maximum_intersection_upper_bound_mm3=v,conservative_swept_bounds_mm=bb.tolist())
    # Original tray wall/base has no undercuts in vertical withdrawal. Check
    # each sampled pose of its exact BRep; the separate stock boxes provide
    # conservative continuous envelopes for the two deflected palm snap arms.
    openposts=[]
    for sign in [-1,1]:
        hook=e.union([s['shape'] for s in ts if s.get('side')==sign and s['tag'] in ['palmPost','palmLip','palmRamp']])
        openposts.append(e.tr(hook,[0,sign*.6,0]))
    tray_core=ledger_shape('P08_Electronics_tray',set(range(14,20))|{21,23})
    core=e.union([tray_core]+[s['shape'] for s in ts if s['tag'] not in ['palmPost','palmLip','palmRamp']]+openposts)
    maxov=0
    for dz in np.linspace(-20,0,81):
        maxov=max(maxov,e.b.volume(e.b.common(e.tr(core,[0,0,float(dz)]),frame)))
    add('Complete unloaded P08 opened hooks -Z20 sampled service',maxov<1e-6,
        maximum_sampled_overlap_mm3=maxov,sampled_poses=81)
    for sign in [-1,1]:
        a,b=([64.3,66.1] if sign>0 else [-66.1,-64.3])
        envelope=e.b.box([-45.5,a,-20],[-25.6,b,2.4])
        ov=e.b.volume(e.b.common(frame,envelope))
        add('Continuous deflecting beam envelope '+str(sign),ov<1e-6,intersection_upper_bound_mm3=ov)
    # Added fixed ceiling/keeper must not enter any existing non-electronics
    # solid at the exported nominal position. Existing floating service paths
    # require the complete mechanism validator if the design is selected.
    for ref,target in old.items():
        if ref in ['P01','P08','P09','P10'] or ref in electronics:continue
        ov=e.b.volume(e.b.common(additions,target))
        add('New fixed ceiling static interference '+ref,ov<1e-6,intersection_mm3=ov)
    for ref,dx,dz in [('H15',-2,35),('H13',12,40),('H11',9,40),('H01',3.2,40),('H12',3.2,40),('H23',3.2,40)]:
        maxov=0
        for x in np.linspace(0,dx,25):maxov=max(maxov,e.b.volume(e.b.common(additions,e.tr(old[ref],[float(x),0,0]))))
        for z in np.linspace(0,dz,81):maxov=max(maxov,e.b.volume(e.b.common(additions,e.tr(old[ref],[dx,0,float(z)]))))
        add('Preserved '+ref+' service X then Z versus new ceiling',maxov<1e-6,maximum_sampled_overlap_mm3=maxov,dx_mm=dx,dz_mm=dz)
        bounds=[e.b.bounds(old[ref])]
        if ref=='H13':
            # The single AABB incorrectly puts an 11 mm radius at the M6 shaft
            # tip. Exact source is radius3 shaft plus radius11 thumbwheel.
            bounds=[np.array([[-24,-3,15],[-12,3,21]],dtype=float),np.array([[-15.8,-11,7],[-13,11,29]],dtype=float)]
            cover=e.union([e.b.box(*bb) for bb in bounds])
            missing=e.b.volume(e.b.cut(old[ref],cover))
            add('H13 decomposed conservative cover contains complete native body',missing<1e-6,uncovered_mm3=missing)
        ov=0
        for bb in bounds:
            first=bb.copy();first[0,0]+=min(0,dx);first[1,0]+=max(0,dx)
            second=bb.copy();second[:,0]+=dx;second[1,2]+=dz
            ov=max(ov,e.b.volume(e.b.common(additions,e.b.box(*first))),e.b.volume(e.b.common(additions,e.b.box(*second))))
        add('Conservative complete '+ref+' service envelopes versus new ceiling',ov<1e-6,
            intersection_upper_bound_mm3=ov,dx_mm=dx,dz_mm=dz)
    result=dict(status='PASS_NOMINAL_CANDIDATE' if all(x['status']=='PASS' for x in checks) else 'FAIL_CANDIDATE',
        date='2026-11-03',source_native=inv['native_step'],source_native_sha256=inv['native_step_sha256'],
        design='P09 rigid skin/keeper/rail/clamp permanently joined to P01; P08 and electronics detach downward',
        checks=checks,failed=[x for x in checks if x['status']=='FAIL'],
        limitations=['Candidate only, not native Onshape or released printing geometry.',
            'Electronics envelope service is continuous conservative AABB; tray service is 81 exact sampled poses, not continuous certification.',
            'Nominal PCB, LiPo and wire/plug envelopes; real flexible wiring and component tolerances are not qualified.',
            'No slicing/support-removal or full mechanism dynamic validation in this report.'])
    write('geometry-service-check.json',result)
    (HERE/'fingerworker_R12_enclosure_candidate.fs').write_text(source_patch((ROOT/'fingerworker_mvp.fs').read_text()))
    print(json.dumps(dict(status=result['status'],checks=len(checks),failed=result['failed']),indent=2))

if __name__=='__main__': main()
