#!/usr/bin/env python3
"""Independent finite strap-route clearance and complete translation proof."""
from pathlib import Path
import argparse,hashlib,importlib.util,json
import numpy as np
OUT=Path(__file__).resolve().parents[1];ROOT=OUT.parents[1];STUDY=ROOT/'review/near-palm-2026-11-06'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ap=argparse.ArgumentParser();ap.add_argument('--candidate',action='store_true');args=ap.parse_args()
generator=STUDY/'mechanics/near_palm.py';spec=importlib.util.spec_from_file_location('r14_routing_nominal',generator);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
b=m.b
from OCP.BRepCheck import BRepCheck_Analyzer
if args.candidate:
    parts,inv=m.load();step_path=STUDY/'mechanics/P01_near_palm.step';parts['P01']=b.read_step(step_path)[0][0]
else:
    inv=json.loads((STUDY/'validation/native-step-inventory.json').read_text());step_path=Path(inv['native_step'])
    assert sha(step_path)==inv['native_step_sha256']
    ss=b.read_step(step_path)[0];parts={r:ss[v['candidates'][0]['solid_index']] for r,v in inv['native_part_correspondence'].items()}
rows=[];routes=m.strap_geometry()['routes']
def add(name,ok,**detail):rows.append(dict(name=name,status='PASS' if bool(ok) else 'FAIL',**detail))
def axis_gaps(a,c):return np.maximum(c[0]-a[1],a[0]-c[1])
for i,route in enumerate(routes):
    shape=route['shape'];rb=b.bounds(shape)
    add('Finite2mm single/4mm return envelope valid '+str(i),BRepCheck_Analyzer(shape).IsValid(),bounds_mm=rb.tolist(),station_x_mm=route['x'],slot_y_mm=route['y'])
    for ref in ['P04','H060','H061','P11','H10']:
        sb=b.bounds(parts[ref]).copy();travel=[-30.8,.8] if ref in ['P11','H10'] else [-30,0]
        sb[0,0]+=travel[0];sb[1,0]+=travel[1];gaps=axis_gaps(rb,sb)
        add('Whole motion separates strap'+str(i)+'/'+ref,float(gaps.max())>1e-6,
            complete_motion_bounds_mm=sb.tolist(),relative_x_interval_mm=travel,axis_separations_mm=gaps.tolist(),separating_axis='XYZ'[int(np.argmax(gaps))],
            proof='AABB extends native minimumX by the entire negative translation and maximumX by the entire positive translation. Positive separation on one axis certifies all intermediate poses, not sampled positions.')
    gate=b.bounds(parts['P06']).copy();gate[0]-=[.1,.9,0];gate[1]+=[12,.9,0];gaps=axis_gaps(rb,gate)
    add('Whole rear-gate release separates strap'+str(i),float(gaps.max())>1e-6,
        conservative_release_bounds_mm=gate.tolist(),axis_separations_mm=gaps.tolist(),release_x_mm=[0,12],maximum_outward_clip_deflection_mm=.9)
    potential=[]
    for ref,part in parts.items():
        gaps=axis_gaps(rb,b.bounds(part))
        if float(gaps.max())>1e-6:continue
        overlap=b.common(shape,part);valid=BRepCheck_Analyzer(overlap).IsValid();volume=b.volume(overlap) if valid else None
        potential.append(dict(ref=ref,valid_boolean=valid,intersection_mm3=volume))
    add('Seated route has no positive overlap '+str(i),all(v['valid_boolean'] and v['intersection_mm3']<1e-6 for v in potential),
        exact_nearby_tests=potential,all_other_parts_proved_separate_by_bounds=True,
        intended_contact='Outer bar topZ4 and outboardY±78 edge may touch; no positive solid intersection permitted.')
failures=[r for r in rows if r['status']!='PASS'];source=STUDY/'fingerworker_R14_near_palm.fs'
report=dict(status=('PASS_LOCAL_R14_STRAP_ROUTING_CANDIDATE' if args.candidate else 'PASS_NATIVE_R14_STRAP_ROUTING') if not failures else 'FAIL',checks=rows,failures=failures,failed_count=len(failures),
    native_step_sha256=sha(step_path),source_sha256=sha(source),nominal_generator_sha256=sha(generator),validator_sha256=sha(__file__),
    strap_width_mm=25,single_thickness_mm=2,external_double_back_thickness_mm=4,
    scope='Four finite end routes coveringZ−20..8 and|Y|≤82. Complete moving-grip/cam translations and rear-gate release are proved by conservative separating axes; nearby seated bodies use valid exact intersections.',
    limitations=['Free strap belowZ−20 and the actual support object/thigh are not modeled.','Use the stated external double-back route; a band across the mechanism top is not covered.','No tension, pressure, retention, PLA strength, fatigue or strap-bend qualification.'])
folder=OUT/'validation'/('candidate-flat' if args.candidate else '');folder.mkdir(parents=True,exist_ok=True)
(folder/'strap-routing-check.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(dict(status=report['status'],checks=len(rows),failures=failures),indent=2));raise SystemExit(bool(failures))
