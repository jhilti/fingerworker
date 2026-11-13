from pathlib import Path
import importlib.util,json
p=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('r15',(p/'mechanics/inboard_straps.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
b=m.b;r=m.r7;n,inv=m.load();rows=[]
for sign,ref in [(-1,'H060'),(1,'H061')]:
 y=sign*51
 # Seat translation domain is the full cylinder/washer sweep X78..111.
 swept=b.cut(r.cyl([78,y,18],[111,y,18],11),r.cyl([77.9,y,18],[111.1,y,18],4))
 missing=m.validvolume(b.cut(n[ref],swept)); assert missing<1e-6,(ref,missing)
 for top in [6,8]:
  lo,hi=sorted([sign*56.5,sign*70]);env=b.box([52.5,lo,4],[77.5,hi,top])
  gap=b.gap(env,swept)
  rows.append(dict(sign=sign,seat=ref,native_containment_missing_mm3=missing,top_z_mm=top,gap_mm=gap,meaning='intended single2mm overbar' if top==6 else 'extra conservative4mm overbar'))
out=dict(status='PASS' if all(x['gap_mm']>0 for x in rows) else 'FAIL',source_sha256=m.sha(p/'fingerworker_R15_inboard_straps.fs'),baseline_native_step_sha256=inv['native_step_sha256'],method='Exact swept22mm OD/8mm ID annulus across full X78..111 interval compared to finite rear strap top envelope. This swept cylinder contains every moving seat pose; native seat dimensions verified separately by native comparison.',checks=rows)
(p/'validation/seat-strap-clearances.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
