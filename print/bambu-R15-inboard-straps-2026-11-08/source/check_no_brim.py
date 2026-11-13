#!/usr/bin/env python3
"""Verify removed model brims from settings and actual paths, preserving supports."""
from pathlib import Path
import argparse,json,zipfile,xml.etree.ElementTree as ET
import numpy as np
from shapely.geometry import LineString
from shapely.ops import unary_union
import check_print_features as paths

OUT=Path(__file__).resolve().parents[1];ROOT=OUT.parents[1];sha=paths.sha
ap=argparse.ArgumentParser();ap.add_argument('--candidate',action='store_true');args=ap.parse_args()
layout_path=OUT/('candidate-flat-layout.json' if args.candidate else 'plate-layout.json');layout=json.loads(layout_path.read_text())
evidence=OUT/'validation'/('candidate-flat' if args.candidate else '')
sliced=evidence/(Path(layout['native_project']).stem+'_verification.gcode.3mf')
project=OUT/layout['native_project'];source=OUT/'validation/R14-first-layer-contact-review.json';baseline=json.loads(source.read_text())['parts']
checks=[];parts={}
def add(name,ok,**detail):checks.append(dict(name=name,status='PASS' if bool(ok) else 'FAIL',**detail))
with zipfile.ZipFile(project) as z:
 cfg=ET.fromstring(z.read('Metadata/model_settings.config'));settings=json.loads(z.read('Metadata/project_settings.config'))
 object_settings={}
 for ob in cfg.findall('object'):
  m={n.get('key'):n.get('value') for n in ob.findall('metadata') if n.get('key')};object_settings[m['name'].split(' - ')[0]]=m
add('Global model brim and skirt disabled',settings['brim_type']=='no_brim' and float(settings['brim_width'])==0 and int(settings['skirt_loops'])==0,brim_type=settings['brim_type'],brim_width=settings['brim_width'],skirt_loops=settings['skirt_loops'])
with zipfile.ZipFile(sliced) as z:
 info=ET.fromstring(z.read('Metadata/slice_info.config'));names={int(o.get('identify_id')):o.get('name').split(' - ')[0] for o in info.find('plate').findall('object')};data=paths.parse(z.read('Metadata/plate_1.gcode').decode())
add('No actual Brim or Skirt extrusion',not any(p['feature'] in ('Brim','Skirt') for p in data),actual_brim_segments=sum(p['feature']=='Brim' for p in data),actual_skirt_segments=sum(p['feature']=='Skirt' for p in data))
for ident,ref in names.items():
 m=object_settings[ref];row=next(r for r in layout['placements'] if r['ref']==ref)
 add(ref+' explicit object brim disabled',m['brim_type']=='no_brim' and float(m['brim_width'])==0,old_brim_width_mm=baseline[ref]['original_brim_width_mm'],new_type=m['brim_type'],new_width_mm=float(m['brim_width']))
 model=[p for p in data if p['obj']==ident and p['feature'] not in paths.NONMODEL];zmin=min(p['b'][2] for p in model)
 first=[p for p in model if abs(p['b'][2]-zmin)<1e-5]
 footprint=unary_union([LineString([p['a'][:2],p['b'][:2]]).buffer(p['width']/2,quad_segs=8) for p in first]);joined=footprint.buffer(.01).buffer(-.01);islands=list(joined.geoms) if hasattr(joined,'geoms') else [joined]
 areas=sorted([p.area for p in islands],reverse=True);old=baseline[ref]['actual_model_first_layer_area_mm2'];minimum=12000 if ref=='P01' else old*.99
 add(ref+' substantial model first-layer contact',footprint.area>=minimum and abs(zmin-.2)<1e-4 and max(areas)/sum(areas)>.999,
  model_only_area_mm2=footprint.area,minimum_mm2=minimum,baseline_area_mm2=old,largest_connected_fraction=max(areas)/sum(areas),first_layer_top_z_mm=zmin,
  method='Union of actual first-layer model bead footprints, excluding support and adhesion additions. Tiny tessellation residue is merged across0.02mm gaps only for connectivity; raw area remains measured independently.')
 support=[p for p in data if p['obj']==ident and p['feature'] in paths.SUPPORT];expected_support=layout['object_settings'][ref].get('enable_support')=='1'
 add(ref+' required support setting retained',m.get('enable_support')==('1' if expected_support else '0') and (bool(support) if expected_support else not support),enabled=expected_support,actual_support_segments=len(support))
 b=footprint.bounds;parts[ref]=dict(first_layer_area_mm2=footprint.area,first_layer_span_mm=[b[2]-b[0],b[3]-b[1]],height_mm=row['size_oriented_mm'][2],largest_connected_fraction=max(areas)/sum(areas),support_segments=len(support),brim_width_mm=0)
failures=[c for c in checks if c['status']!='PASS']
report=dict(status=('PASS_LOCAL_R15_NO_BRIM_CANDIDATE' if args.candidate else 'PASS_R15_NO_BRIM') if not failures else 'FAIL',checks=checks,failures=failures,parts=parts,
 project_sha256=sha(project),sliced_archive_sha256=sha(sliced),layout_sha256=sha(layout_path),CAD_source_sha256=layout['CAD_source_sha256'],baseline_measurement_sha256=sha(source),validator_sha256=sha(__file__),
 scope='No removable model Brim/Skirt paths on any of the six parts. Required geometric support structures and their printable bases are retained. Actual model-only contact is measured.',
 limitations=['First-layer adhesion is not experimentally measured.','P11 has the smallest contact area; observe its first layer on the clean texturedPEI plate.','Supports below overhangs still require removal; they are not the former perimeter brim.'])
(evidence/'no-brim-check.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status=report['status'],checks=len(checks),failures=failures),indent=2));raise SystemExit(bool(failures))
