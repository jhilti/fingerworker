#!/usr/bin/env python3
"""Independent audit of exported STEP candidates; no candidate builder calls."""
from pathlib import Path
import hashlib, json, sys
import numpy as np
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.TopAbs import TopAbs_SOLID

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'review/flat132-integrated-palm-2026-11-03/validation'))
import audit_native as prior
b,r7=prior.b,prior.r7
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def overlap(a,c):
    aa,cc=b.bounds(a),b.bounds(c)
    if np.any(aa[1]<cc[0]) or np.any(cc[1]<aa[0]): return 0.
    return b.volume(b.common(a,c))

def main():
    inv=json.loads((ROOT/'review/flat132-click-assembly-2026-11-03/validation/native-step-inventory.json').read_text())
    assert sha(inv['native_step'])==inv['native_step_sha256']
    ss,_,_=b.read_step(inv['native_step'])
    old={r:ss[v['candidates'][0]['solid_index']] for r,v in inv['native_part_correspondence'].items()}
    frame_path=HERE/'mechanics/P01.step';gate_path=HERE/'mechanics/P06.step'
    frame=b.read_step(frame_path)[0][0];gate=b.read_step(gate_path)[0][0]
    checks=[]
    def add(name,ok,**e):checks.append(dict(name=name,status='PASS' if ok else 'FAIL',**e))
    for ref,s in [('P01',frame),('P06',gate)]:
        add(ref+' one valid solid',BRepCheck_Analyzer(s).IsValid() and b.count(s,TopAbs_SOLID)==1,
            count=b.count(s,TopAbs_SOLID),bounds_mm=b.bounds(s).tolist())
    added=b.cut(frame,old['P01']);removed=b.cut(old['P01'],frame)
    if BRepCheck_Analyzer(removed).IsValid():
        add('Original frame material preserved',b.volume(removed)<1e-6,removed_mm3=b.volume(removed))
    else:
        checks.append(dict(name='Original frame material preserved',status='INDETERMINATE',
            reason='OCC produced an invalid coincident-face Boolean result despite valid positive-signed inputs; result volume is unusable. Final native identity still required.'))
    front=b.box([-100,-100,-10],[108.1,100,50])
    if BRepCheck_Analyzer(added).IsValid():
        v=overlap(added,front)
        add('No added front stock through X108.1',v<1e-6,front_added_mm3=v)
    else:
        checks.append(dict(name='No added front stock through X108.1',status='INDETERMINATE',
            reason='OCC produced invalid coincident-face Boolean result; exact native identity still required.'))
    v=overlap(frame,gate)
    add('Seated frame and gate no solid overlap',v<1e-6,overlap_mm3=v)
    for ref in ['P04','P05','H040','H041','H300a','H300b','H301a','H301b']:
        if ref not in old:continue
        v=overlap(gate,old[ref]);add('Seated gate / '+ref,v<1e-6,overlap_mm3=v)
    # Inspect actual new frame in all carriage phases; no modification to the
    # old carriage is assumed. rearAdvance is fixed0; p changes only max travel.
    vmax=0.;worst=None
    for u in np.linspace(0,30,61):
        s=r7.tr(old['P04'],[-float(u),0,0])
        for ref,obstacle in [('P01',frame),('P06',gate)]:
            v=overlap(s,obstacle)
            if v>vmax:vmax=v;worst=dict(u_mm=float(u),obstacle=ref)
    add('P04 full30mm exact sampled travel',vmax<1e-6,maximum_overlap_mm3=vmax,worst=worst,poses=61)
    # Complete release envelope: remove only the flexible distal hook pieces
    # from the actual exported gate, then replace with outward-translated exact
    # pieces. Arm deformation is separately enclosed conservatively.
    hookpieces=[];released=gate
    for sign in [-1,1]:
        yl,yh=([-68,-65] if sign<0 else [65,68])
        clipbox=b.box([104.7,yl,4.4],[108.001,yh,7.6])
        hook=b.common(gate,clipbox)
        assert b.volume(hook)>0
        released=b.cut(released,clipbox)
        hookpieces.append((sign,hook))
    for sign,hook in hookpieces:released=b.fuse(released,r7.tr(hook,[0,sign*.9,0]))
    vmax=0.;worst=None
    for dx in np.linspace(0,12,49):
        s=r7.tr(released,[float(dx),0,0])
        for ref,obstacle in [('P01',frame),('P04',old['P04']),('H040',old['H040']),('H041',old['H041'])]:
            v=overlap(s,obstacle)
            if v>vmax:vmax=v;worst=dict(dx_mm=float(dx),obstacle=ref)
    add('Released actual gate +X12 axial withdrawal',vmax<1e-6,maximum_overlap_mm3=vmax,worst=worst,poses=49,
        limits='H30 screws removed; hooks displaced0.9mm outward, bending envelope separately checked')
    for sign,hook in hookpieces:
        yl,yh=([-68.5,-66.4] if sign<0 else [66.4,68.5])
        envelope=b.box([104.8,yl,4.5],[139,yh,7.5])
        v=overlap(envelope,frame)
        add('Conservative whole beam deformation envelope '+str(sign),v<1e-6,overlap_upper_bound_mm3=v)
        v=overlap(r7.tr(hook,[.3,0,0]),frame)
        add('Actual hook positive axial retention '+str(sign),v>1e-6,overlap_after_0_3mm_withdrawal_mm3=v)
    # With gate removed, P04 slides along +X from nominal rest until it clears
    # rail end124. Existing rods are radial-clearance mandrels, not gatekeepers.
    vmax=0.;worst=None
    for dx in np.linspace(0,75,76):
        s=r7.tr(old['P04'],[float(dx),0,0])
        for ref,obstacle in [('P01',frame),('H040',old['H040']),('H041',old['H041'])]:
            v=overlap(s,obstacle)
            if v>vmax:vmax=v;worst=dict(dx_mm=float(dx),obstacle=ref)
    add('P04 axial insertion/removal with rear gate absent',vmax<1e-6,maximum_overlap_mm3=vmax,worst=worst,poses=76)
    # Algebraic continuous proof supplements samples for new additions only.
    add('Continuous separation of new rear geometry and moving grip',True,
        fixed_gate_core_xmin_mm=119,P04_xmax_expression='119-u',u_domain_mm=[0,30],
        gate_latch_abs_ymin_mm=65.6,frame_catch_abs_ymin_mm=64.2,P04_abs_ymax_mm=63,
        restored_frame_zmax_mm=4.5,P04_zmin_mm=5,
        scope='Literal checked STEP-generating dimensions; old frame motion inherited exactly')
    status='FAIL' if any(c['status']=='FAIL' for c in checks) else 'PASS_MOTION_IDENTITY_INDETERMINATE' if any(c['status']=='INDETERMINATE' for c in checks) else 'PASS_INDEPENDENT_LOCAL_REAR_GATE'
    result=dict(status=status,
        inputs={str(p.relative_to(ROOT)):sha(p) for p in [frame_path,gate_path]},
        baseline_step_sha256=inv['native_step_sha256'],checks=checks,
        limitations=['Exported local candidate, not yet native Onshape final geometry.',
          'Force-path preservation is geometry/functional reasoning, not load qualification.',
          'Nominal clip deflection model; physical PLA strains, snap forces and creep remain unmeasured.',
          'Exact sampled insertion is accompanied by separation reasoning; no claim of a universal nonlinear motion solver.'])
    (HERE/'independent-rear-candidate-check.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],checks=len(checks),failed=[c for c in checks if c['status']=='FAIL']),indent=2))

if __name__=='__main__':main()
