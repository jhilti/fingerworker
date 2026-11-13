from pathlib import Path
import sys,json
import numpy as np
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];R8=ROOT/'review/flat132-palm-cover-2026-10-23'
sys.path.insert(0,str(ROOT/'review/flat132-adjustable-rear-2026-10-23/validation'));import audit_adjustable_rear as r7
b=r7.b;v=r7.v
inv=json.loads((R8/'validation/native-step-inventory.json').read_text());shapes,_,_=b.read_step(Path(inv['native_step']));native={r:shapes[x['candidates'][0]['solid_index']] for r,x in inv['native_part_correspondence'].items()}
# Complete conservative cover, broader than side/top CSG blends.
boxes=[([-29,-26.2,14],[-22.75,-16.8,28.2]),([-29,16.8,14],[-22.75,26.2,28.2])];cover=r7.union([b.box(lo,hi) for lo,hi in boxes]);rows=[]
for ref,part in native.items():
 if ref=='P02':continue
 overlap=0. if v.separated(b.bounds(cover),b.bounds(part)) else b.volume(b.common(cover,part))
 delta=np.maximum(b.bounds(part)[0]-b.bounds(cover)[1],b.bounds(cover)[0]-b.bounds(part)[1]);boundgap=float(np.linalg.norm(np.maximum(delta,0)))
 gap=boundgap if boundgap>0 else b.gap(cover,part)
 if gap<6 or overlap>0:rows.append(dict(ref=ref,gap_mm=gap,intersection_mm3=overlap,bounds_mm=b.bounds(part).tolist()))
print(json.dumps(rows,indent=2))
# Exact complete relative translation certificates from source-derived full dynamic domain.
spec=json.loads((ROOT/'review/flat132-adjustable-rear-2026-10-23/validation/rear-spec.json').read_text());domain=r7.vertices();motion=[]
for ref,part in native.items():
 if ref=='P02' or ref in v.SPRINGS|v.ARTICULATED:continue
 offsets=domain@r7.coefficients(ref,spec);low,high=float(offsets.min()),float(offsets.max());swept=r7.union([b.box([lo[0]-high,*lo[1:]],[hi[0]-low,*hi[1:]]) for lo,hi in boxes]);ov=0. if v.separated(b.bounds(swept),b.bounds(part)) else b.volume(b.common(swept,part))
 if ov>1e-6:motion.append(dict(ref=ref,intersection_mm3=ov,relative_x_range_mm=[low,high]))
service=[]
for ref,part in native.items():
 if ref=='P02' or ref.startswith(('P08','P09','P10','E','PCB_')) or ref in v.SPRINGS|v.ARTICULATED:continue
 # p2 service setup; shift fixed declared preload motion objects first.
 delta=2*r7.coefficients(ref,spec)[1];p=r7.tr(part,[delta,0,0]);swept=r7.union([b.box(lo,[*hi[:2],hi[2]+40]) for lo,hi in boxes]);ov=0. if v.separated(b.bounds(swept),b.bounds(p)) else b.volume(b.common(swept,p))
 if ov>1e-6:service.append(dict(ref=ref,intersection_mm3=ov))
result={'status':'PASS_CONSERVATIVE_BRACE_ENVELOPE_PRECHECK' if not motion and not service and not any(x['intersection_mm3']>1e-6 for x in rows) else 'FAIL','scope':'Broad two-box cover of proposed pads and R1.2 root blends, not final native geometry','boxes_mm':boxes,'nearby_pairs':rows,'full_dynamic_domain_collisions':motion,'continuous40mm_vertical_service_collisions':service}
(HERE/'preaudit-brace-envelopes.json').write_text(json.dumps(result,indent=2)+'\n');print(result['status'],motion,service)
