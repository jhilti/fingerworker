#!/usr/bin/env python3
from pathlib import Path
import json
import organic_palm as g
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.TopAbs import TopAbs_SOLID,TopAbs_SHELL
import numpy as np
b=g.b
old,inv=g.load();frame,base,bolster=g.build(old);rows=[]
def v(s):
 assert BRepCheck_Analyzer(s).IsValid()
 return b.volume(s)
def check(name,condition,**detail):rows.append(dict(name=name,status='PASS' if condition else 'FAIL',**detail))
added=b.cut(frame,base);removed=b.cut(base,frame)
check('One valid P01 solid/shell',BRepCheck_Analyzer(frame).IsValid() and b.count(frame,TopAbs_SOLID)==b.count(frame,TopAbs_SHELL)==1)
for ref,p in old.items():
 if ref=='P01':continue
 if np.any(b.bounds(frame)[1]<b.bounds(p)[0]) or np.any(b.bounds(p)[1]<b.bounds(frame)[0]):continue
 ov=v(b.common(frame,p));check('Seated separation '+ref,ov<1e-6,overlap_mm3=ov)
for name,lo,hi in [('roof/catches/base',[-60,-70,-3],[140,70,16.5]),('negative thumb seats',[-40,-70,14],[-7.9,-60,40]),('positive thumb seats',[-40,60,14],[-7.9,70,40]),('negative wrist thumb pocket lower',[-40,-59,14],[-24,-43,26]),('positive wrist thumb pocket lower',[-40,43,14],[-24,59,26])]:
 zone=b.box(lo,hi);diff=v(b.common(added,zone))+v(b.common(removed,zone));check('Protected '+name,diff<1e-6,symmetric_difference_mm3=diff)
ov=v(b.cut(removed,b.box(*g.TRIM)));check('Removal only old upper crown',ov<1e-6,outside_trim_mm3=ov)
zone=b.box([-16,-25.4,16.5],[0,25.4,40]);ov=v(b.common(added,zone));check('Central fixed sensor gap preserved',ov<1e-6,newstock_in_gap_mm3=ov)
for y in [-51,51]:
 tool=g.r7.cyl([-17,y,18],[-7,y,18],3.1);ov=v(b.common(frame,tool));check('Rod bore open '+str(y),ov<1e-6,overlap_mm3=ov)
for sign in [-1,1]:
 lo,hi=([-29,63.6,-20],[-25.6,66.1,16.2]) if sign>0 else ([-29,-66.1,-20],[-25.6,-63.6,16.2]);ov=v(b.common(added,b.box(lo,hi)));check('P08 full release '+str(sign),ov<1e-6,overlap_mm3=ov)
route=g.r7.cyl([-12.8,-72,8.5],[-12.8,72,8.5],3.2);ov=v(b.common(added,route));check('H18 tool route',ov<1e-6,overlap_mm3=ov)
for ref in ['P04','H060','H061','P11','H10']:
 bb=b.bounds(old[ref]).copy();bb[0,0]-=30.8 if ref in ['P11','H10'] else 30
 if ref in ['P11','H10']:bb[1,0]+=.8
 gap=b.gap(added,b.box(*bb));check('Added stock full motion '+ref,gap>1e-6,gap_lower_bound_mm=gap)
report=dict(status='PASS_LOCAL_ORGANIC_PALM' if all(q['status']=='PASS' for q in rows) else 'FAIL',source_sha256=g.sha(g.SOURCE),generator_sha256=g.sha(g.__file__),checks=rows,added_mm3=v(added),removed_mm3=v(removed),P01_bounds_mm=b.bounds(frame).tolist(),scope='Local analytic profile prototype; native loft is final authority, with exact interfaces independently audited.')
(g.HERE/'preflight.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='checks'},indent=2));print([q for q in rows if q['status']=='FAIL'])
