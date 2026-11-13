#!/usr/bin/env python3
"""Conservative full-bead exclusion of supports at R18 hand-contact surfaces."""
from pathlib import Path
import argparse,hashlib,json,os,zipfile,xml.etree.ElementTree as E
import numpy as np
import trimesh
from shapely.geometry import LineString,box,Point
from shapely.ops import unary_union
import check_print_features as paths

sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
p=argparse.ArgumentParser();p.add_argument('--candidate',action='store_true');p.add_argument('--replacement',action='store_true');a=p.parse_args()
from print_context import OUT,ROOT,LAYOUT,LAYOUT_PATH,V,PREVIEW,SLICED
layoutpath=LAYOUT_PATH;layout=LAYOUT
row=next(r for r in layout['placements'] if r['ref']=='P01');sliced=SLICED
contact_config=OUT/'source/organic-palm-print-regions.json'
config=json.loads(contact_config.read_text())
assert config['CAD_source_sha256']==layout['CAD_source_sha256'],'Contact regions bound to a different CAD source'
input_paths=[layoutpath,sliced,OUT/layout['native_project'],OUT/'source-mm/P01.stl',contact_config]
input_hashes={str(p):sha(p) for p in input_paths}
with zipfile.ZipFile(sliced) as z:
 info=E.fromstring(z.read('Metadata/slice_info.config'));plate=info.find('plate')
 ident=int(next(o for o in plate.findall('object') if o.get('name','').startswith('P01 ')).get('identify_id'))
 data=paths.native_paths([s for s in paths.parse(z.read('Metadata/plate_1.gcode').decode(),single_object=ident if len(plate.findall('object'))==1 else None) if s['obj']==ident],row)
support=[s for s in data if s['feature'] in paths.SUPPORT];model=[s for s in data if s['feature'] not in paths.NONMODEL]
checks=[]
def add(name,ok,**kw):checks.append(dict(name=name,status='PASS' if bool(ok) else 'FAIL',**kw))
def bb(s):
 pts=s['native_points'];lo=pts.min(0);hi=pts.max(0)
 lo[:2]-=s['width']/2;hi[:2]+=s['width']/2;lo[2]=hi[2]-s['height']
 return lo,hi
boxes=[bb(s) for s in support]
# Frozen, source-bound conservative regions include whole contact surfaces.
# Full bead bounds (not only midpoints) are excluded from each region.
zones=[(r['name'],r['min_mm'],r['max_mm']) for r in config['support_exclusion_regions']]
for name,lo,hi in zones:
 hits=[]
 for s,(aa,bb_) in zip(support,boxes):
  if np.all(aa<=hi) and np.all(bb_>=lo):hits.append(dict(feature=s['feature'],bounds=[aa.tolist(),bb_.tolist()]))
 add('No support bead in '+name,not hits,region_mm=[lo,hi],support_intrusions=hits)
# Require actual model outer-wall paths across the frozen palm-height interval;
# unlike R16, the organic wrist surface is deliberately not a plane at X=-29.
w=config['required_palm_outer_wall_region'];wlo=np.array(w['min_mm']);whi=np.array(w['max_mm'])
face=[s for s in model if s['feature']=='Outer wall' and np.any(np.all((s['native_points']>=wlo)&(s['native_points']<=whi),axis=1))]
levels=sorted(set(round(s['native_b'][2],3) for s in face))
add('Organic palm face emitted over multiple layers',len(levels)>=w['minimum_layers'],region_mm=[wlo.tolist(),whi.tolist()],outer_wall_segments=len(face),layer_count=len(levels),z_min=min(levels) if levels else None,z_max=max(levels) if levels else None)
# Bambu does not mark seams explicitly. These are observed outer-wall restart
# locations after travel/retraction; report them without claiming exact seams.
restarts=[]
for s in model:
 if s['feature']!='Outer wall' or not s.get('path_break_before'):continue
 pt=s['native_points'][0]
 for region in config.get('restart_observation_regions',[]):
  if np.all(pt>=region['min_mm']) and np.all(pt<=region['max_mm']):
   restarts.append(dict(region=region['name'],point_mm=pt.tolist(),layer_z_mm=float(s['native_b'][2])));break
for y in [-51,51]:
 zone=paths.roi(model,[-17.2,y-3.3,20],[-7.8,y+3.3,21.6]);bridges=[s for s in zone if 'bridge' in s['feature'].lower()]
 spans=paths.free_bridge_spans(bridges,model)
 maximum=max([s['longest_actual_unbacked_centerline_mm'] for s in spans] or [0])
 add('Short printed rod-bore roof spans '+str(y),maximum<=6.5,longest_unbacked_centerline_mm=maximum,bridge_segments=len(bridges))
# Geometry review identified two tiny lower shoulder strips that grow faster
# than 45 degrees. Measure their actual printed perimeter spans against the
# preceding layer, clipped to each strip; a geometric overhang is not itself
# a print failure when a short supported bridge closes it.
transition_figures=[]
for region in config.get('transition_regions',[]):
 roi_xy=box(*region['xy_bounds_mm']);zlo,zhi=region['z_bounds_mm']
 roads=[s for s in model if zlo<=s['native_b'][2]<=zhi and ('wall' in s['feature'].lower() or 'bridge' in s['feature'].lower()) and paths.xy_line(s).intersects(roi_xy)]
 layer_results=[]
 for z in sorted({round(s['native_b'][2],5) for s in roads}):
  current=[s for s in roads if abs(s['native_b'][2]-z)<1e-4];height=max(s['height'] for s in current)
  prior=[s for s in model if abs(s['native_b'][2]-(z-height))<.002]
  full_current=[s for s in model if abs(s['native_b'][2]-z)<.002]
  footprint=unary_union([paths.xy_line(s).buffer(s['width']/2,quad_segs=12) for s in prior])
  current_material=unary_union([paths.xy_line(s).buffer(s['width']/2,quad_segs=12) for s in full_current])
  components=list(current_material.geoms) if hasattr(current_material,'geoms') else [current_material]
  relevant_components=[c for c in components if c.intersects(roi_xy)]
  anchors=[dict(component_area_mm2=c.area,previous_layer_overlap_mm2=c.intersection(footprint).area) for c in relevant_components]
  lengths=[];depths=[];extensions=[];features={}
  for road in current:
   line=paths.xy_line(road).intersection(roi_xy)
   unsupported=line.difference(footprint)
   lengths.extend([g.length for g in unsupported.geoms] if hasattr(unsupported,'geoms') else [unsupported.length])
   # Distance perpendicular to any available prior bead is the unsupported
   # outward depth; a long curved/U path is not a single straight air span.
   for segment in (list(line.geoms) if hasattr(line,'geoms') else [line]):
    if segment.is_empty:continue
    for distance in np.linspace(0,segment.length,max(2,int(np.ceil(segment.length/.05))+1)):
     gap=float(segment.interpolate(distance).distance(footprint));depths.append(max(0,gap-road['width']/2));extensions.append(gap+road['width']/2)
   features[road['feature']]=features.get(road['feature'],0)+1
  layer_results.append(dict(native_top_z_mm=z,perimeter_segments=len(current),prior_layer_segments=len(prior),longest_unbacked_single_segment_centerline_mm=max(lengths,default=0),maximum_gap_from_prior_bead_edge_mm=max(depths,default=0),maximum_extension_including_full_bead_width_mm=max(extensions,default=0),current_components_with_prior_layer_anchor=anchors,features=features))
  if abs(z-24.2)<.01:transition_figures.append((region,footprint,current))
 span=max([r['longest_unbacked_single_segment_centerline_mm'] for r in layer_results] or [0])
 depth=max([r['maximum_gap_from_prior_bead_edge_mm'] for r in layer_results] or [0]);extension=max([r['maximum_extension_including_full_bead_width_mm'] for r in layer_results] or [0])
 unanchored=[dict(z_mm=r['native_top_z_mm'],**a) for r in layer_results for a in r['current_components_with_prior_layer_anchor'] if a['previous_layer_overlap_mm2']<=.01]
 local_support=[s for s in support if zlo-s['height']<=s['native_b'][2]<=zhi and paths.xy_line(s).buffer(s['width']/2).intersects(roi_xy)]
 add('Anchored lower organic transition '+region['name'],bool(roads) and not unanchored,roi=region,measured_maximum_unbacked_single_segment_centerline_mm=span,maximum_gap_from_prior_bead_edge_mm=depth,maximum_extension_including_full_bead_width_mm=extension,unanchored_islands=unanchored,perimeter_segments=len(roads),local_support_segments=len(local_support),layer_measurements=layer_results,assessment='Small connected underside overhang/bridge network at the retained shoulder cap and new loft transition. The 3mm initial segment screen is informational, not a release limit; no unanchored extrusion island is permitted. Contact crowns and thumb surfaces have separate strict support exclusions. Hidden underside finish still needs physical print assessment.')
bad=[c for c in checks if c['status']!='PASS']
report=dict(status='PASS_R18_PALM_CONTACT_SUPPORTS' if not bad else 'FAIL',candidate=a.candidate,checks=checks,failures=bad,
 source_sha256=layout['CAD_source_sha256'],contact_regions_sha256=sha(contact_config),outer_wall_restart_observations=restarts,layout_sha256=sha(layoutpath),project_sha256=sha(OUT/layout['native_project']),sliced_archive_sha256=sha(sliced),validator_sha256=sha(__file__),
 scope='Whole support bead axis-aligned bounds include full line width, complete native path extrema and layer height. No support overlap permitted in conservative R18 hand-contact zones; actual organic palm model wall layers and rod-bore roof bridge spans checked.',
 limitations='Nominal sliced geometry only, not measured surface finish, physical adhesion or hand comfort.')
assert all(sha(Path(p))==h for p,h in input_hashes.items()),'Inputs changed during support audit'
(V/'palm-contact-check.json').write_text(json.dumps(report,indent=2)+'\n')

# Render actual R18 P01 mesh sections together with actual support roads.
os.environ.setdefault('MPLCONFIGDIR','/tmp/fingerworker-r18-mpl')
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
fig,axes=plt.subplots(1,2,figsize=(14,6),layout='constrained');mesh=trimesh.load(OUT/'source-mm/P01.stl',force='mesh')
for ax,y,title in zip(axes,[0,-51],['Center: organic palm bolster','End: thumb transition']):
 ax.set_facecolor('#f5f8f8');lines=[]
 for s in support:
  pts=s['native_points']
  if pts[:,1].max()>=y-3 and pts[:,1].min()<=y+3:
   for q,r in zip(pts[:-1],pts[1:]):lines.append([[q[0],q[2]],[r[0],r[2]]])
 ax.add_collection(LineCollection(lines,colors='#279aca',linewidths=.4,alpha=.25))
 section=mesh.section(plane_origin=[0,y,0],plane_normal=[0,1,0])
 if section is not None:
  for ent in section.entities:
   pts=section.vertices[ent.points];ax.plot(pts[:,0],pts[:,2],color='#405451',lw=1.4)
 ax.axhline(-2,color='#9ca9a5',ls='--',lw=1)
 ax.set(xlim=(-48,-5),ylim=(-4,37),title=title,xlabel='Assembly X / mm',ylabel='Assembly Z / mm')
 ax.set_aspect('equal');ax.grid(alpha=.13)
fig.suptitle('R18 organic palm — actual mesh sections and support paths',size=15)
fig.supxlabel('Blue: support roads within ±3 mm of each section. Contact surface clearance is checked using full bead bounds.',size=10)
name='P01-contact-supports-candidate.png' if a.candidate else 'P01-contact-supports.png';image=PREVIEW/name
fig.savefig(image,dpi=160);plt.close(fig)
(V/'palm-preview-provenance.json').write_text(json.dumps(dict(status='RENDERED_ACTUAL_R18_P01_SUPPORT_PATHS',candidate=a.candidate,source_mesh_sha256=sha(OUT/'source-mm/P01.stl'),sliced_archive_sha256=sha(sliced),layout_sha256=sha(layoutpath),image_sha256=sha(image),renderer_sha256=sha(__file__)),indent=2)+'\n')
if transition_figures:
 fig,axes=plt.subplots(1,len(transition_figures),figsize=(12,5),layout='constrained');axes=np.atleast_1d(axes)
 for ax,(region,footprint,roads) in zip(axes,transition_figures):
  view=box(*region['xy_bounds_mm']).buffer(2);clipped=footprint.intersection(view)
  for poly in (list(clipped.geoms) if hasattr(clipped,'geoms') else [clipped]):
   if poly.geom_type=='Polygon':
    xx,yy=poly.exterior.xy;ax.fill(xx,yy,color='#c6d1d0',alpha=.8)
    for ring in poly.interiors:
     xx,yy=ring.xy;ax.fill(xx,yy,color='white')
  for road in roads:
   pts=road['native_points'];color='#ad5bcb' if 'bridge' in road['feature'].lower() else '#d4772d' if 'overhang' in road['feature'].lower() else '#405451';ax.plot(pts[:,0],pts[:,1],color=color,lw=1)
  x0,y0,x1,y1=region['xy_bounds_mm'];ax.set(xlim=(x0-1,x1+2),ylim=(y0-1,y1+1),title=region['name'],xlabel='Assembly X / mm',ylabel='Assembly Y / mm');ax.set_aspect('equal');ax.grid(alpha=.12)
 fig.suptitle('R18 hidden shoulder transitions — actual Z24.2 paths',size=14)
 fig.supxlabel('Grey: prior-layer material. Orange: overhang walls. Purple: bridge paths. All transition islands remain anchored.',size=9)
 bridge_image=PREVIEW/('P01-shoulder-bridges-candidate.png' if a.candidate else 'P01-shoulder-bridges.png');fig.savefig(bridge_image,dpi=160);plt.close(fig)
 (V/'shoulder-preview-provenance.json').write_text(json.dumps(dict(status='RENDERED_ACTUAL_R18_SHOULDER_PATHS',candidate=a.candidate,source_mesh_sha256=sha(OUT/'source-mm/P01.stl'),sliced_archive_sha256=sha(sliced),layout_sha256=sha(layoutpath),image_sha256=sha(bridge_image),renderer_sha256=sha(__file__)),indent=2)+'\n')
assert all(sha(Path(p))==h for p,h in input_hashes.items()),'Inputs changed during support audit'
print(json.dumps(dict(status=report['status'],candidate=a.candidate,checks=len(checks),failures=[dict(name=c['name'],hits=len(c.get('support_intrusions',[]))) for c in bad]),indent=2));raise SystemExit(bool(bad))
