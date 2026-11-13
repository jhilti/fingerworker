#!/usr/bin/env python3
"""Audit native rear-block orientation and actual fastener/rod access cores."""
import json,zipfile,xml.etree.ElementTree as E
import numpy as np
from shapely.geometry import Point,box
import check_print_features as paths
from print_context import OUT,LAYOUT,LAYOUT_PATH,V,PROJECT,SLICED
sha=paths.sha;checks=[];metrics={}
def add(name,ok,**e):checks.append(dict(name=name,status='PASS' if bool(ok) else 'FAIL',**e))
with zipfile.ZipFile(SLICED) as z:
 plate=E.fromstring(z.read('Metadata/slice_info.config')).find('plate');ids={o.get('name').split(' - ')[0]:int(o.get('identify_id')) for o in plate.findall('object')};data=paths.parse(z.read('Metadata/plate_1.gcode').decode())
for ref in ('P06L','P06R'):
 row=next(r for r in LAYOUT['placements'] if r['ref']==ref);yy=-float(row['normalization_translation_mm'][1])+14
 native=paths.native_paths([s for s in data if s['obj']==ids[ref]],row);model=[s for s in native if s['feature'] not in paths.NONMODEL];support=[s for s in native if s['feature'] in paths.SUPPORT]
 add(ref+' flat mounting face down',np.allclose(row['rotation_3x3'],np.eye(3)) and abs(row['normalization_translation_mm'][2]+4.5)<.01 and np.allclose(row['size_oriented_mm'],[10,28,23.5],atol=.02))
 add(ref+' no supports to remove from sockets or screw recesses',not support,support_segments=len(support))
 core_metrics=[]
 for dy in (-9.5,9.5):
  for kind,radius,zlo in [('M3 through core',1.45,4.65),('screw-head access core',2.8,10.3)]:
   core=Point(124.5,yy+dy).buffer(radius,quad_segs=64);hits=[];levels=set()
   for s in model:
    z=float(s['native_b'][2])
    if not zlo<=z<=28.01:continue
    pts=s['native_points'];lo=pts[:,:2].min(0)-s['width']/2;hi=pts[:,:2].max(0)+s['width']/2
    if np.any(hi<[124.5-radius,yy+dy-radius]) or np.any(lo>[124.5+radius,yy+dy+radius]):continue
    levels.add(round(z,4));area=paths.xy_line(s).buffer(s['width']/2,quad_segs=12).intersection(core).area
    if area>1e-6:hits.append(dict(z_mm=z,area_mm2=area,feature=s['feature']))
   add(ref+' '+kind+' atY'+str(yy+dy),not hits,center_xy_mm=[124.5,yy+dy],core_radius_mm=radius,z_mm=[zlo,28],intrusions=hits)
   core_metrics.append(dict(kind=kind,center_xy_mm=[124.5,yy+dy],core_radius_mm=radius,intrusions=len(hits)))
 hits=[];rod_layers=set();radius=2.7
 for s in model:
  zhi=float(s['native_b'][2]);zlo=zhi-s['height'];dz=0 if zlo<=18<=zhi else min(abs(zlo-18),abs(zhi-18))
  if dz>=radius:continue
  half=np.sqrt(radius**2-dz**2);core=box(119.15,yy-half,126.0,yy+half);pts=s['native_points'];lo=pts[:,:2].min(0)-s['width']/2;hi=pts[:,:2].max(0)+s['width']/2
  if np.any(hi<[119.15,yy-half]) or np.any(lo>[126,yy+half]):continue
  rod_layers.add(round(zhi,4));area=paths.xy_line(s).buffer(s['width']/2,quad_segs=12).intersection(core).area
  if area>1e-6:hits.append(dict(z_mm=zhi,area_mm2=area,feature=s['feature']))
 add(ref+' horizontal rod-socket core remains clear',not hits,axis_yz_mm=[yy,18],core_radius_mm=radius,x_mm=[119.15,126],intrusions=hits)
 metrics[ref]=dict(model_segments=len(model),support_segments=len(support),rod_core_radius_mm=radius,rod_core_intrusions=len(hits),screw_cores=core_metrics)
failed=[c for c in checks if c['status']!='PASS'];report=dict(status='PASS_R19_REAR_BLOCK_PRINT_PATHS' if not failed else 'FAIL',checks=checks,failures=failed,metrics=metrics,CAD_source_sha256=LAYOUT['CAD_source_sha256'],layout_sha256=sha(LAYOUT_PATH),project_sha256=sha(PROJECT),sliced_archive_sha256=sha(SLICED),validator_sha256=sha(__file__),scope='Both rigid rear blocks base-down, without support; complete emitted bead widths and layer heights excluded from conservative vertical screw/head cores and horizontal rod cores. Native CAD independently checks the full nominal hole geometry.',limitations='The conservative clear-core checks do not certify physical screw, insert or rod fit, material strength or screw torque.')
(V/'rear-block-check.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status=report['status'],checks=len(checks),failures=failed),indent=2));raise SystemExit(bool(failed))
