#!/usr/bin/env python3
"""Audit actual native and printed25x2mm clear passages in four R14 strap eyes."""
from pathlib import Path
import argparse,json,sys,zipfile,xml.etree.ElementTree as ET
import numpy as np
from shapely.geometry import box as rectangle,LineString
from shapely.ops import unary_union
import check_print_features as paths

OUT=Path(__file__).resolve().parents[1];ROOT=OUT.parents[1]
STUDY=ROOT/'review/near-palm-2026-11-06';sha=paths.sha
ap=argparse.ArgumentParser();ap.add_argument('--candidate',action='store_true');args=ap.parse_args()
layout_path=OUT/('candidate-flat-layout.json' if args.candidate else 'plate-layout.json');layout=json.loads(layout_path.read_text())
evidence=OUT/'validation'/('candidate-flat' if args.candidate else '')
sliced=evidence/(Path(layout['native_project']).stem+'_verification.gcode.3mf')
row=next(r for r in layout['placements'] if r['ref']=='P01')
assert np.allclose(row['rotation_3x3'],np.eye(3))
snapshots={str(p):sha(p) for p in (layout_path,sliced)}
with zipfile.ZipFile(sliced) as z:
    info=ET.fromstring(z.read('Metadata/slice_info.config'));plate=info.find('plate')
    label=int(next(o for o in plate.findall('object') if o.get('name','').startswith('P01 ')).get('identify_id'))
    printed=paths.native_paths([s for s in paths.parse(z.read('Metadata/plate_1.gcode').decode()) if s['obj']==label],row)
sys.path.insert(0,str(ROOT/'review/flat132-solid-palm-2026-10-23/validation'))
import audit_solid_palm as b
from OCP.BRepCheck import BRepCheck_Analyzer
if args.candidate:
    step_path=STUDY/'mechanics/P01_near_palm.step';frame=b.read_step(step_path)[0][0]
else:
    inv_path=STUDY/'validation/native-step-inventory.json';inv=json.loads(inv_path.read_text());step_path=Path(inv['native_step'])
    assert sha(step_path)==inv['native_step_sha256']
    ss=b.read_step(step_path)[0];frame=ss[inv['native_part_correspondence']['P01']['candidates'][0]['solid_index']]
checks=[];metrics=[]
def add(name,ok,**detail):checks.append(dict(name=name,status='PASS' if bool(ok) else 'FAIL',**detail))
for x in (5,80):
    for y in (-69.5,69.5):
        name=f'X{x}_Y{y}'
        core=rectangle(x-12.5,y-1,x+12.5,y+1)
        # Rounded27x4 slot: twoR2 end caps whose centres are23mm apart.
        throat=LineString([(x-11.5,y),(x+11.5,y)]).buffer(2,quad_segs=64)
        tool=b.box([x-12.5,y-1,-2.01],[x+12.5,y+1,4.01])
        common=b.common(frame,tool);valid=BRepCheck_Analyzer(common).IsValid()
        overlap=b.volume(common) if valid else None
        add('Native25x2mm through passage '+name,valid and overlap<1e-6,
            exact_probe_bounds_mm=b.bounds(tool).tolist(),intersection_mm3=overlap,valid_boolean=valid)
        model_intrusions=[];support_intrusions=[];brim_intrusions=[];near=0;layers=set()
        for s in printed:
            pp=s['native_points'];lo=pp.min(0).copy();hi=pp.max(0).copy()
            lo[:2]-=s['width']/2;hi[:2]+=s['width']/2;lo[2]=hi[2]-s['height']
            if hi[2]<-2 or lo[2]>4 or np.any(hi[:2]<[x-15,y-3.5]) or np.any(lo[:2]>[x+15,y+3.5]):continue
            near+=1
            bead=paths.xy_line(s).buffer(s['width']/2,quad_segs=16)
            if s['feature'] not in paths.NONMODEL:
                layers.add(round(s['native_b'][2],4));area=bead.intersection(core).area
                if area>1e-7:model_intrusions.append(dict(feature=s['feature'],top_z_mm=s['native_b'][2],area_mm2=area))
            elif s['feature'] in paths.SUPPORT:
                area=bead.intersection(throat.buffer(-.03)).area
                if area>1e-7:support_intrusions.append(dict(feature=s['feature'],top_z_mm=s['native_b'][2],area_mm2=area))
            elif s['feature'] in ('Brim','Skirt'):
                area=bead.intersection(throat.buffer(-.03)).area
                if area>1e-7:brim_intrusions.append(dict(feature=s['feature'],top_z_mm=s['native_b'][2],area_mm2=area))
        add('Actual25x2mm passage remains open '+name,not model_intrusions and len(layers)>=29,
            nearby_model_layers=len(layers),model_intrusions=model_intrusions,
            method='Complete horizontal bead footprints include width and circular-path tessellation at0.05mm maximum chord length. The25x2mm core remains inside the rounded27x4mm CAD slot at all base layers.')
        add('No support or brim inside slot '+name,not support_intrusions and not brim_intrusions,
            support_intrusions=support_intrusions,brim_intrusions=brim_intrusions,
            nominal_slot_length_mm=27,nominal_slot_width_mm=4,edge_coordinate_tolerance_mm=.03)
        sign=1 if y>0 else -1
        for region,yrange in [('outer load bar',(72.5,77)),('base root',(58.8,64.8))]:
            ylo,yhi=sorted([sign*v for v in yrange]);poly=rectangle(x-13.5,ylo,x+13.5,yhi)
            solid_core=b.box([x-13.5,ylo,-1],[x+13.5,yhi,3])
            missing=b.cut(solid_core,frame);valid=BRepCheck_Analyzer(missing).IsValid()
            void=b.volume(missing) if valid else None
            add('Native solid core defined '+region+' '+name,valid and void<1e-6,core_bounds_mm=b.bounds(solid_core).tolist(),missing_native_solid_mm3=void,valid_boolean=valid)
            grouped={};features={}
            for s in printed:
                if s['feature'] in paths.NONMODEL or not (-.999<=s['native_b'][2]<=3.001):continue
                pp=s['native_points'];lo=pp[:,:2].min(0)-s['width']/2;hi=pp[:,:2].max(0)+s['width']/2
                if np.any(hi<[x-13.5,ylo]) or np.any(lo>[x+13.5,yhi]):continue
                z=round(s['native_b'][2],4);bead=paths.xy_line(s).buffer(s['width']/2,quad_segs=16).intersection(poly)
                if bead.is_empty:continue
                grouped.setdefault(z,[]).append(bead);features[s['feature']]=features.get(s['feature'],0)+1
            coverage=[dict(native_top_z_mm=z,covered_fraction=unary_union(beads).area/poly.area) for z,beads in sorted(grouped.items())]
            minimum=min([r['covered_fraction'] for r in coverage] or [0])
            add('Actual solid infill throughout '+region+' '+name,len(coverage)>=20 and minimum>=.98,
                tested_interior_layers=len(coverage),minimum_complete_bead_coverage=minimum,required_fraction=.98,features=features,per_layer=coverage,
                method='Each interior layer of a native-verified solid rectangular bar/root core is compared with the union of complete emitted model bead footprints. This verifies local material coverage rather than trusting modifier metadata; it is not a strength calculation.')
        metrics.append(dict(slot=name,nearby_extrusion_segments=near,model_layers=sorted(layers)))
add('Source slice and layout remained unchanged',all(sha(Path(p))==h for p,h in snapshots.items()))
failures=[c for c in checks if c['status']!='PASS']
result=dict(status=('PASS_LOCAL_R14_STRAP_PRINT_CANDIDATE' if args.candidate else 'PASS_R14_STRAP_SLOT_PRINT_PATHS') if not failures else 'FAIL',checks=checks,failures=failures,failed_count=len(failures),metrics=metrics,
    native_step_sha256=sha(step_path),CAD_source_sha256=layout['CAD_source_sha256'],layout_sha256=sha(layout_path),sliced_archive_sha256=sha(sliced),validator_sha256=sha(__file__),
    scope='Four through-slot passages for25mm-wide single2mm webbing; no support/brim inside the openings; actual dense interior bar/root coverage in all four local100% modifiers. Doubled4mm folds belong outside the slots and are checked by the separate routing audit.',
    limitations='Nominal CAD and emitted paths only. Printed tolerances, actual strap dimensions, strap tension and PLA strength require physical verification.')
(evidence/'strap-slot-check.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(dict(status=result['status'],checks=len(checks),failures=failures),indent=2))
raise SystemExit(bool(failures))
