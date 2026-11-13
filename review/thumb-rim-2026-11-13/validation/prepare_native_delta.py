from pathlib import Path
import importlib.util,json
import numpy as np
HERE=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('native_audit',HERE/'audit_native_r19.py');a=importlib.util.module_from_spec(s);s.loader.exec_module(a);b=a.b;r=a.r
step=r.STUDY/'native/Flat132_R19_final_AP214.step';old,_,_=r.baseline();want=a.m.expected(old);shapes,inv,_=b.read_step(step);assert len(shapes)==94
models={}
for ref in ['P06L','P06R','P08']:
 bound=b.bounds(want[ref]);indices=[i for i,q in enumerate(inv) if np.max(abs(np.array(q['bounds_mm'])-bound))<1e-5];assert len(indices)==1,(ref,indices);models[ref]=shapes[indices[0]]
models['P01']=shapes[next(i for i,q in enumerate(inv) if q['bounds_mm'][0][0]<-40 and q['bounds_mm'][1][0]>120 and q['bounds_mm'][1][1]-q['bounds_mm'][0][1]>130)]
r.a.enable_native_boundary_tolerance();rows=[]
for ref in ['P06L','P06R','P08']:
 result=a.comparison(models[ref],want[ref]);row=dict(name='Native geometry equals reviewed rigid mount '+ref,status='PASS' if result['empty'] else 'FAIL',**result);rows.append(row);print(row,flush=True)
psh,pinv,_=b.read_step(r.STUDY/'native-probe/Flat132_R19_thumb_rim_probe_AP214.step');pf=psh[next(i for i,q in enumerate(pinv) if q['bounds_mm'][0][0]<-40 and q['bounds_mm'][1][0]>120 and q['bounds_mm'][1][1]-q['bounds_mm'][0][1]>130)]
for name,roi,reference in [('Complete front frame and reviewed variable rims',b.box([-50,-70,-5],[100,70,40]),pf),('Rear floor and obsolete catch removal',b.box([100,-70,-5],[140,70,40]),want['P01_without_rear_catches'])]:
 result=a.comparison(b.common(models['P01'],roi),b.common(reference,roi));row=dict(name=name,status='PASS' if result['empty'] else 'FAIL',**result);rows.append(row);print(row,flush=True)
report=dict(status='PASS_NATIVE_R19_SHAPE_DELTA' if all(q['status']=='PASS' for q in rows) else 'REVIEW_NATIVE_R19_SHAPE_DELTA',source_sha256=r.sha(r.STUDY/'fingerworker_R19_thumb_rim.fs'),native_step_sha256=r.sha(step),probe_report_sha256=r.sha(HERE/'rim-probe-check.json'),generator_sha256=r.sha(r.STUDY/'latches/rigid_mounts.py'),validator_sha256=r.sha(__file__),comparison_implementation_sha256=r.sha(HERE/'audit_native_r19.py'),checks=rows)
(HERE/'native-shape-delta.json').write_text(json.dumps(report,indent=2)+'\n')
