#!/usr/bin/env python3
"""R11 added enclosure stocks versus the complete legal R10 motion domain.

Every affine X displacement is extremized on the exact correlated domain's
vertices. Whole target bounding boxes swept by that complete interval contain
all intervening poses. Positive clearance to those boxes certifies the whole
range without sampled travel or interpolation assumptions about the mesh.
"""
from pathlib import Path
import json,hashlib
import numpy as np
import build_enclosure as e

HERE=Path(__file__).resolve().parent;ROOT=e.ROOT
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    native,inv=e.load();tray,lid=e.stocks()
    stockrows=[('P08 '+s['tag']+str(s.get('side','')),s) for s in tray]+[('P09 '+s['tag'],s) for s in lid]
    rear=ROOT/'review/flat132-adjustable-rear-2026-10-23/validation/rear-spec.json'
    manifest=ROOT/'review/flat132-reach-fit-2026-10-23/validation/manifest.json'
    spec=json.loads(rear.read_text());m=json.loads(manifest.read_text())
    domain=np.array([[u,p,a,c] for u,p,a in [(0,0,0),(0,2,0),(0,0,2),(30,0,0),(28,2,0),(28,0,2)] for c in [-.8,.8]])
    def coef(ref):
        if ref in spec['adjusting_refs']:return np.array([0,0,-1,0.])
        old=e.b.v.motion(ref,m)
        return np.array([old[0],old[1],old[0],old[2]])
    targets=[]
    for ref,shape in sorted(native.items()):
        if ref in e.b.v.SPRINGS:
            yy=-51 if ref=='H030' else 51
            bounds=np.array([[12,yy-9.5,8.5],[108,yy+9.5,27.5]])
            targets.append(dict(ref=ref,kind='conservative complete spring operating cover',bounds=bounds,xrange=[0.,0.],coeff=None))
        elif ref in e.b.v.ARTICULATED:
            targets.append(dict(ref=ref,kind='conservative complete articulated switch operating cover',bounds=np.array([[26,-14,8],[41,8,14]]),xrange=[0.,0.],coeff=None))
        else:
            c=coef(ref)
            if np.max(np.abs(c))<1e-12:continue
            offsets=domain@c;lo,hi=float(offsets.min()),float(offsets.max())
            bounds=e.b.bounds(shape).copy();bounds[0,0]+=lo;bounds[1,0]+=hi
            targets.append(dict(ref=ref,kind='whole exact native shape bounded across exact affine motion range',bounds=bounds,xrange=[lo,hi],coeff=c.tolist()))
    # Additional R10 assembly variants retained by the shared mechanism.
    for yy in [-51,51]:
        for tag,a,c in [('H14 steel ISO sleeve',12,95),('S01 soft-spring adapter',12,38)]:
            targets.append(dict(ref=tag+' Y'+str(yy),kind='complete source-defined optional assembly cover',bounds=np.array([[a,yy-8,10],[c,yy+8,26]]),xrange=[0.,0.],coeff=None))
    rows=[]
    for name,s in stockrows:
        bounds=e.b.bounds(s['shape'])
        for t in targets:
            envelope=e.b.box(*t['bounds'])
            overlap=e.b.volume(e.b.common(s['shape'],envelope))
            gap=e.b.gap(s['shape'],envelope)
            rows.append(dict(name=name,target=t['ref'],status='PASS' if overlap<1e-6 and gap>0 else 'FAIL',target_envelope_kind=t['kind'],target_affine_coefficients_u_p_a_e=t['coeff'],complete_target_x_displacement_range_mm=t['xrange'],conservative_swept_target_bounds_mm=t['bounds'].tolist(),new_stock_bounds_mm=bounds.tolist(),intersection_upper_bound_mm3=overlap,conservative_gap_lower_bound_mm=gap))
    failed=[r for r in rows if r['status']!='PASS']
    out=dict(status='PASS_COMPLETE_CORRELATED_MOTION_DOMAIN' if not failed else 'FAIL',revision='R11',date='2026-11-03',native_R10_step_sha256=inv['native_step_sha256'],enclosure_spec_sha256=sha(HERE/'enclosure-spec.json'),builder_sha256=sha(HERE/'build_enclosure.py'),rear_motion_spec_sha256=sha(rear),inherited_motion_manifest_sha256=sha(manifest),validator_sha256=sha(Path(__file__)),method='Affine displacement extrema on all exact convex-domain vertices, then full conservative target AABB sweep in X. Exact OCP intersection with each new enclosure stock. No sampled-travel certification.',domain='u>=0,p>=0,a>=0,p+a<=2,u+p+a<=30,-0.8<=e<=0.8; coordinates u,p,a,e in mm',domain_vertices_u_p_a_e=domain.tolist(),source_domain_reference='review/flat132-integrated-palm-2026-11-03/validation/audit_motion.py',new_additive_stock_count=len(stockrows),moving_and_variant_target_count=len(targets),checks=rows,check_count=len(rows),failed_count=len(failed),failures=failed,minimum_conservative_gap_mm=min(r['conservative_gap_lower_bound_mm'] for r in rows),limitations=['New additive P08/P09 stocks only. Existing R10 static contacts and existing whole mechanism motion checks remain separate inputs.','Native R11 stock identity must be established independently against expected(old) before inheriting this certificate.','Spring and articulated switch motion use source-defined conservative covers, without qualification of physical buckling, real wiring or human anatomy.','Nominal geometry only; no spring-load, material, creep, strength, fatigue or electrical qualification.'])
    (HERE/'motion-preflight.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k] for k in ['status','new_additive_stock_count','moving_and_variant_target_count','check_count','failed_count','minimum_conservative_gap_mm']},indent=2))
    return bool(failed)

if __name__=='__main__':raise SystemExit(main())
