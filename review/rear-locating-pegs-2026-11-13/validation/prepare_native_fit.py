#!/usr/bin/env python3
"""Focused native STEP fit proof, later sealed against final native meshes."""
from pathlib import Path
import importlib.util,json
import numpy as np
HERE=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('r20_stepfit',HERE/'audit_locating_pegs.py');v=importlib.util.module_from_spec(s);s.loader.exec_module(v);b=v.b;sha=v.sha
step=v.STUDY/'native/Flat132_R20_final_AP214.step';source=v.STUDY/'fingerworker_R20_rear_locating_pegs.fs';old,release=v.baseline();c=v.module('r20_stepcandidate',v.STUDY/'mechanics/rear_pegs.py');want=c.expected(old);shapes,inventory,_=b.read_step(step);assert len(shapes)==94
parts=dict(old);indices={}
for ref in ['P06L','P06R']:
 bounds=b.bounds(want[ref]);found=[i for i,q in enumerate(inventory) if np.max(abs(np.array(q['bounds_mm'])-bounds))<1e-5];assert len(found)==1,(ref,found);indices[ref]=found[0];parts[ref]=shapes[found[0]]
indices['P01']=next(i for i,q in enumerate(inventory) if q['bounds_mm'][0][0]<-40 and q['bounds_mm'][1][0]>120 and q['bounds_mm'][1][1]-q['bounds_mm'][0][1]>130);parts['P01']=shapes[indices['P01']]
rows=v.checks(parts,old)
for ref in ['P06L','P06R']:
 comp=v.r.comparison(parts[ref],want[ref]);rows.append(dict(name='Native pegged block matches reviewed geometry '+ref,status='PASS' if comp['empty'] else 'FAIL',**comp))
rear=b.box([100,-70,-5],[140,70,40]);comp=v.r.comparison(b.common(parts['P01'],rear),b.common(want['P01'],rear));rows.append(dict(name='Native rear pockets match reviewed geometry',status='PASS' if comp['empty'] else 'FAIL',**comp))
failed=[q for q in rows if q['status']!='PASS'];report=dict(status='PASS_NATIVE_R20_STEP_FIT' if not failed else 'REVIEW_NATIVE_R20_STEP_FIT',source_sha256=sha(source),native_step_sha256=sha(step),baseline_native_step_sha256=release['native_step_sha256'],generator_sha256=sha(v.STUDY/'mechanics/rear_pegs.py'),focused_validator_sha256=sha(HERE/'audit_locating_pegs.py'),validator_sha256=sha(__file__),native_changed_part_indices=indices,checks=rows,failures=failed,scope='Actual native changed solids. Unchanged moving references are inherited R19 pending final91-body native identity gate; mesh/source release binding follows separately.')
(HERE/'native-fit-step.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status=report['status'],checks=len(rows),failures=failed),indent=2))
