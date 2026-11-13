#!/usr/bin/env python3
"""Audit actual R19 CLI paths, using R18 solely for first-layer contact comparison.

Native CAD is checked independently. The selected object footprints, supports, brim
absence, slot openings and dense ligaments are all rechecked on the new slice.
"""
from pathlib import Path
import json, zipfile, xml.etree.ElementTree as ET
import numpy as np
from shapely.geometry import box, LineString
from shapely.ops import unary_union
import check_print_features as paths

from print_context import OUT,LAYOUT,LAYOUT_PATH,V,PROJECT,SLICED
SLICE=SLICED;layout=LAYOUT;sha=paths.sha
config=json.loads((OUT/'source/strap-print-regions.json').read_text())
checks=[]; metrics={}
def add(name,ok,**kw):checks.append(dict(name=name,status='PASS' if bool(ok) else 'FAIL',**kw))
with zipfile.ZipFile(PROJECT) as z:
 settings=json.loads(z.read('Metadata/project_settings.config'))
 cfg=ET.fromstring(z.read('Metadata/model_settings.config'))
 object_settings={}
 for ob in cfg.findall('object'):
  m={n.get('key'):n.get('value') for n in ob.findall('metadata')};object_settings[m['name'].split(' - ')[0]]=m
with zipfile.ZipFile(SLICE) as z:
 info=ET.fromstring(z.read('Metadata/slice_info.config'));plates=info.findall('plate');plate=plates[0]
 names={int(o.get('identify_id')):o.get('name').split(' - ')[0] for o in plate.findall('object')}
 filament=[dict(f.attrib) for f in plate.findall('filament')]
 gcode=z.read('Metadata/plate_1.gcode').decode();data=paths.parse(gcode,single_object=next(iter(names)) if len(names)==1 else None)
add('Exactly the selected expected objects on one plate',len(plates)==1 and set(names.values())=={r['ref'] for r in layout['placements']},objects=names)
add('Only filament 1 PLA is used for models and supports',len(filament)==1 and filament[0]['id']=='1' and filament[0]['type']=='PLA' and filament[0]['used_for_object']=='true' and filament[0]['used_for_support']=='true',used_filaments=filament)
add('Global brim and skirt disabled',settings['brim_type']=='no_brim' and float(settings['brim_width'])==0 and int(settings['skirt_loops'])==0)
add('No actual Brim or Skirt extrusion',not any(s['feature'] in ('Brim','Skirt') for s in data),brim_segments=sum(s['feature']=='Brim' for s in data),skirt_segments=sum(s['feature']=='Skirt' for s in data))
baseline_path=OUT.parents[1]/'print/bambu-R18-organic-palm-2026-11-13/validation/actual-path-check.json'
baseline=json.loads(baseline_path.read_text())['metrics']
for ident,ref in names.items():
 m=object_settings[ref];model=[s for s in data if s['obj']==ident and s['feature'] not in paths.NONMODEL];support=[s for s in data if s['obj']==ident and s['feature'] in paths.SUPPORT]
 first=[s for s in model if s['b'][2]<=.201]
 footprint=unary_union([LineString([s['a'][:2],s['b'][:2]]).buffer(s['width']/2,quad_segs=8) for s in first])
 joined=footprint.buffer(.01).buffer(-.01);islands=list(joined.geoms) if hasattr(joined,'geoms') else [joined];areas=[s.area for s in islands]
 fraction=max(areas)/sum(areas);expected=ref in ('P01','P04','P05')
 add(ref+' no brim and filament 1',m['brim_type']=='no_brim' and float(m['brim_width'])==0 and m['extruder']=='1')
 if ref in ('P06L','P06R'):
  add(ref+' flat mounting face has broad connected first-layer contact',footprint.area>=220 and fraction>.999,model_only_area_mm2=footprint.area,minimum_contact_mm2=220,largest_connected_fraction=fraction)
 else:
  add(ref+' connected first-layer contact retained',footprint.area>=baseline[ref]['first_layer_area_mm2']*.99 and fraction>.999,model_only_area_mm2=footprint.area,baseline_mm2=baseline[ref]['first_layer_area_mm2'],largest_connected_fraction=fraction)
 add(ref+' required support presence retained',m['enable_support']==('1' if expected else '0') and bool(support)==expected,actual_support_segments=len(support))
 metrics[ref]=dict(first_layer_area_mm2=footprint.area,model_segments=len(model),support_segments=len(support))
 print(ref,'first-layer/support checked',flush=True)

ident=next(i for i,r in names.items() if r=='P01');row=next(r for r in layout['placements'] if r['ref']=='P01')
printed=paths.native_paths([s for s in data if s['obj']==ident],row)
# Precompute swept bead bounding boxes once; exact footprint checks follow.
lo=np.array([s['native_points'].min(0) for s in printed]);hi=np.array([s['native_points'].max(0) for s in printed]);width=np.array([s['width'] for s in printed]);height=np.array([s['height'] for s in printed]);lo[:,:2]-=width[:,None]/2;hi[:,:2]+=width[:,None]/2;lo[:,2]=hi[:,2]-height
modelmask=np.array([s['feature'] not in paths.NONMODEL for s in printed]);tops=np.array([s['native_b'][2] for s in printed]);beads={}
def bead(i):
 if i not in beads:beads[i]=paths.xy_line(printed[i]).buffer(printed[i]['width']/2,quad_segs=16)
 return beads[i]
for slot in config['slots']:
 x,y=slot['x_mm'],slot['y_mm'];zmin,zmax=slot['z_mm'];name=slot['name'];core=box(x-12.5,y-1,x+12.5,y+1);throat=LineString([(x-11.5,y),(x+11.5,y)]).buffer(2,quad_segs=64)
 near=np.where((hi[:,2]>=zmin)&(lo[:,2]<=zmax)&(hi[:,0]>=x-15)&(lo[:,0]<=x+15)&(hi[:,1]>=y-3.5)&(lo[:,1]<=y+3.5))[0]
 intrusions=[];supports=[];layers=set()
 for i in near:
  s=printed[i]
  if modelmask[i]:
   layers.add(round(tops[i],4));a=bead(i).intersection(core).area
   if a>1e-7:intrusions.append(dict(z=tops[i],area_mm2=a,feature=s['feature']))
  elif s['feature'] in paths.SUPPORT and bead(i).intersection(throat.buffer(-.03)).area>1e-7:supports.append(int(i))
 add('Actual 25x2mm slot remains open '+name,not intrusions and len(layers)>=29,model_layers=len(layers),intrusions=intrusions)
 add('No actual support inside slot '+name,not supports,support_intrusions=len(supports))
 for reg in slot['solid_cores']:
  (xl,yl,zl),(xh,yh,zh)=reg['bounds_mm'];poly=box(xl,yl,xh,yh)
  hits=np.where(modelmask&(tops>=zl+.001)&(tops<=zh+.001)&(hi[:,0]>=xl)&(lo[:,0]<=xh)&(hi[:,1]>=yl)&(lo[:,1]<=yh))[0];grouped={}
  for i in hits:
   b=bead(i).intersection(poly)
   if not b.is_empty:grouped.setdefault(round(tops[i],4),[]).append(b)
  coverage=[dict(top_z_mm=z,covered_fraction=unary_union(bs).area/poly.area) for z,bs in sorted(grouped.items())];minimum=min([r['covered_fraction'] for r in coverage] or [0])
  add('Actual solid core '+name+' '+reg['name'],len(coverage)>=20 and minimum>=.98,interior_layers=len(coverage),minimum_complete_bead_coverage=minimum,per_layer=coverage)
 print(name,'slot and all four dense cores checked',flush=True)

failures=[c for c in checks if c['status']!='PASS']
report=dict(status='PASS_R19_ACTUAL_PRINT_PATHS' if not failures else 'FAIL',checks=checks,failed_count=len(failures),failures=failures,metrics=metrics,used_filaments=filament,project_sha256=sha(PROJECT),sliced_archive_sha256=sha(SLICE),validator_sha256=sha(__file__),layout_sha256=sha(LAYOUT_PATH),strap_regions_sha256=sha(OUT/'source/strap-print-regions.json'),baseline_first_layer_evidence=dict(path=str(baseline_path),sha256=sha(baseline_path)),native_geometry_scope='Solid CAD must be checked by the separate R19 native geometry audit; this checks actual emitted beads.',scope='Actual pinned local CLI slice: selected objects, only PLA, no model brims, first-layer contact, required supports, four open 25x2mm strap throats and all 16 local dense ligament cores.',limitations=['Emitted bead geometry is a nominal audit, not a physical strength or adhesion test.','Observe P11 first layer on clean textured PEI.'])
(V/'actual-path-check.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(dict(status=report['status'],checks=len(checks),failures=failures),indent=2))
raise SystemExit(bool(failures))
