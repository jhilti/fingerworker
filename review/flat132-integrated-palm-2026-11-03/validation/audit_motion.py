#!/usr/bin/env python3
"""Focused complete-domain R10 integration check using native R9/R10 meshes.

Independent conservative new-stock covers are swept over the exact correlated
u,p,a,e domain. Unchanged R9 geometry is bound separately by exact native BRep
identity; removed material cannot create a new interference.
"""
from pathlib import Path
import hashlib,json,sys
import numpy as np
from audit_service import ROOT,STUDY,HERE,R9,R5,box,cyl,v,BAD

sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
CHANGED={'H15','H160','H161','H170','H171'}


def stocks():
    out=[]
    for y in [-31.5,31.5]:
        # A4.01mm radius circumscribes every restored M4 pilot, through-hole
        # and counterbore; the whole known extra cover stays far from motion.
        import manifold3d as md
        out.append((f'M4 restoration y{y}',md.Manifold.cylinder(14.3,4.01,4.01,128).translate([-16,y,.2])))
        out.append((f'key-slot restoration y{y}',box([-22.25,y-3.25,6.4],[-19.75,y+3.25,8.3])))
        out.append((f'integral drop y{y}',box([-23,y-5.5,6.3],[-9.5,y+5.5,6.5])))
    for lo,hi in [(-25,-18),(18,25)]:
        out.append((f'portal overlap y{lo}',box([-22.75,lo,14],[-22.55,hi,27])))
    for y in [-11,11]:
        # Retaining all of the old trap's filled box is conservative against
        # unchanged foreign parts. Changed fasteners are checked separately
        # against the complete actual P01 with its precise new head cuts.
        out.append((f'restored former nut trap y{y}',box([-18,y-2.85,21.15],[-16,y+2.85,26.85])))
    return out


def main():
    archive=STUDY/'native/Flat132_R10_neutral_final.zip';parts,ignored=v.load(archive,{})
    assert not ignored
    spec=json.loads((ROOT/'review/flat132-adjustable-rear-2026-10-23/validation/rear-spec.json').read_text())
    m=json.loads((R5/'manifest.json').read_text())
    domain=np.array([[u,p,a,e]for u,p,a in [(0,0,0),(0,2,0),(0,0,2),(30,0,0),(28,2,0),(28,0,2)]for e in [-.8,.8]])
    def coef(ref):
        if ref in spec['adjusting_refs']:return np.array([0,0,-1,0.])
        old=v.motion(ref,m);return np.array([old[0],old[1],old[0],old[2]])
    rows=[]
    def check(name,obj,ref,target,relative):
        lo,hi=float(relative.min()),float(relative.max())
        if abs(hi-lo)<1e-12:
            volume=float((obj.translate([lo,0,0])^target).volume())
            row=dict(status='STATIC_NO_VOLUME_INTERFERENCE'if volume<=.01 else'INTERFERENCE',intersection_volume_mm3=volume,relative_x_range_mm=[lo,hi])
        else:row=v.relative_sweep(obj,target,lo,hi,.01,.03125)
        row.update(name=name,target=ref);rows.append(row)
    for name,obj in stocks():
        for ref,item in sorted(parts.items()):
            if ref=='P01'or ref in CHANGED:continue
            if ref in v.SPRINGS:
                y=-51 if ref=='H030' else 51
                target=box([12,y-9.5,8.5],[108,y+9.5,27.5]);relative=np.array([0.])
            elif ref in v.ARTICULATED:
                target=box([26,-14,8],[41,8,14]);relative=np.array([0.])
            else:target=item['object'];relative=-(domain@coef(ref))
            check('Complete new fixed-frame stock: '+name,obj,ref,target,relative)
    for ref in sorted(CHANGED):
        obj=parts[ref]['object']
        for target,item in sorted(parts.items()):
            if target==ref:continue
            if target in v.SPRINGS:
                y=-51 if target=='H030' else 51
                obstacle=box([12,y-9.5,8.5],[108,y+9.5,27.5]);relative=np.array([0.])
            elif target in v.ARTICULATED:obstacle=box([26,-14,8],[41,8,14]);relative=np.array([0.])
            else:obstacle=item['object'];relative=domain@(coef(ref)-coef(target))
            check('Whole changed native hardware '+ref,obj,target,obstacle,relative)
    # New soft-spring accessory remains entirely ahead of all changed regions.
    for ref,obj in [('new stock '+n,s)for n,s in stocks()]+[(r,parts[r]['object'])for r in CHANGED]:
        for y in [-51,51]:
            check('S01 accessory full operating cover: '+ref,obj,'S01 '+str(y),box([12,y-8,10],[38,y+8,26]),np.array([0.]))
            check('Steel81mm ISO sleeve full configuration cover: '+ref,obj,'H14 ISO '+str(y),box([12,y-8,10],[95,y+8,26]),np.array([0.]))
    bad=[r for r in rows if r['status']in BAD]
    out=dict(status='PASS_COMPLETE_DOMAIN_CHANGED_GEOMETRY'if not bad else'FAIL',scope='Focused changed-stock and changed-hardware native audit. Exact unchanged R9 BRep identity is a separate mandatory input; no old qualification is relabeled. Complete convex relative domain, not sampled travel. Conservative restored-stock covers contain extra known original material.',native_archive_sha256=sha(archive),source_sha256=sha(STUDY/'fingerworker_flat132_integrated_palm.fs'),validator_sha256=sha(Path(__file__)),domain_vertices_u_p_a_e=domain.tolist(),checks=rows,failed_count=len(bad),failures=bad,limitations=['Nominal geometry only; no load, stiffness, fatigue, creep, human fit or real electrical calibration qualified.','Soft spring and articulated switch checks use conservative full operating envelopes; actual spring shape/buckling and lead routing remain physical checks.'])
    v.write(HERE/'motion-native.json',out)
    print(json.dumps(dict(status=out['status'],checks=len(rows),failed=len(bad),failures=[dict(name=r['name'],target=r['target'],status=r['status'],intersection_volume_mm3=r.get('intersection_volume_mm3'),maximum_sampled_volume_mm3=r.get('maximum_sampled_volume_mm3'))for r in bad]),indent=2),flush=True)
    return bool(bad)


if __name__=='__main__':raise SystemExit(main())
