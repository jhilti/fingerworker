#!/usr/bin/env python3
"""Audit the actual open side-thumb cavities, including complete support bead width."""
from pathlib import Path
import hashlib,json,os,zipfile,xml.etree.ElementTree as E
import numpy as np,trimesh
from shapely.geometry import Point
import check_print_features as paths
from print_context import OUT,ROOT,LAYOUT,LAYOUT_PATH,V,PREVIEW,PROJECT,SLICED,CANDIDATE,REPLACEMENT
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
region_path=ROOT/LAYOUT['side_thumb_regions_path'];cfg=json.loads(region_path.read_text())
assert sha(region_path)==LAYOUT['side_thumb_regions_sha256']
assert cfg['CAD_source_sha256']==LAYOUT['CAD_source_sha256']
inputs=[LAYOUT_PATH,PROJECT,SLICED,OUT/'source-mm/P01.stl',region_path];start={str(p):sha(p) for p in inputs}
row=next(r for r in LAYOUT['placements'] if r['ref']=='P01')
with zipfile.ZipFile(SLICED) as z:
 plate=E.fromstring(z.read('Metadata/slice_info.config')).find('plate')
 ident=int(next(o for o in plate.findall('object') if o.get('name','').startswith('P01 ')).get('identify_id'))
 data=paths.native_paths([s for s in paths.parse(z.read('Metadata/plate_1.gcode').decode(),single_object=ident if len(plate.findall('object'))==1 else None) if s['obj']==ident],row)
support=[s for s in data if s['feature'] in paths.SUPPORT];model=[s for s in data if s['feature'] not in paths.NONMODEL]
checks=[];metrics=[];seam_points=[]
def add(name,ok,**e):checks.append(dict(name=name,status='PASS' if bool(ok) else 'FAIL',**e))
for pocket in cfg['pockets']:
 center=np.asarray(pocket['center_xy_mm']);radius=pocket['radius_mm'];floor=pocket['floor_z_mm'];top=pocket['top_z_mm'];allowance=pocket['contact_radial_allowance_mm']
 # The 0.02 mm expansion exceeds the inscribed-circle polygon error, retaining
 # a conservative envelope around the true circular cut plus the declared round.
 region=Point(center).buffer(radius+allowance+.02,quad_segs=128)
 hits=[]
 for s in support:
  pts=s['native_points'];zhi=float(pts[:,2].max());zlo=zhi-s['height']
  if zhi<=floor+.05 or zlo>top+.1:continue
  bb=pts[:,:2];lo=bb.min(0)-s['width']/2;hi=bb.max(0)+s['width']/2
  if np.any(hi<center-radius-allowance-.03) or np.any(lo>center+radius+allowance+.03):continue
  area=paths.xy_line(s).buffer(s['width']/2,quad_segs=16).intersection(region).area
  if area>1e-7:hits.append(dict(feature=s['feature'],z_range_mm=[zlo,zhi],intersection_area_mm2=area,bounds_xy_mm=[lo.tolist(),hi.tolist()]))
 add('Open side-thumb contact cavity has no support bead '+pocket['name'],not hits,center_xy_mm=center.tolist(),radius_mm=radius,radial_round_allowance_mm=allowance,z_mm=[floor+.05,top+.1],intrusions=hits)
 walls=[];floor_roads=[]
 for s in model:
  pts=s['native_points'];z=float(pts[:,2].max());xy=pts[:,:2];dist=np.linalg.norm(xy-center,axis=1)
  if s['feature']=='Outer wall' and floor+1<z<top-2 and np.any(np.abs(dist-radius)<.6):walls.append(s)
  if floor-.3<=z<=floor+max(pocket.get('floor_round_mm',0),.6)+.4 and paths.xy_line(s).intersects(Point(center).buffer(radius-.05,quad_segs=128)):floor_roads.append(s)
 levels=sorted(set(round(s['native_b'][2],3) for s in walls))
 add('Side-thumb curved wall printed across layers '+pocket['name'],len(levels)>=20,outer_wall_segments=len(walls),layers=len(levels))
 add('Side-thumb floor and lower round emitted '+pocket['name'],len(floor_roads)>=5,model_segments=len(floor_roads))
 starts=[];central=[]
 for s in model:
  if s['feature']!='Outer wall' or not s.get('path_break_before'):continue
  point=s['native_a'];distance=np.linalg.norm(point[:2]-center)
  if floor+pocket.get('floor_round_mm',0)+.2<point[2]<top-1 and abs(distance-radius)<.8:
   starts.append(point.tolist());seam_points.append(point)
   if abs(point[0]-center[0])<=3 and abs(point[1])<=abs(center[1])-radius+1.2:central.append(point.tolist())
 add('No outer-wall restart in deepest thumb-seat center '+pocket['name'],not central,central_restart_points_mm=central,all_cavity_restart_points_mm=starts,method='Observed extrusion starts after travel/retraction or feature change; seam candidates, not explicit slicer seam markers. Central means X within 3 mm of the cutter center and within 1.2 mm of deepest radial contact, above the floor round and below the crown.')
 metrics.append(dict(name=pocket['name'],wall_layers=len(levels),floor_model_segments=len(floor_roads),support_intrusions=len(hits),outer_wall_restarts=len(starts),central_restarts=len(central)))
bad=[r for r in checks if r['status']!='PASS']
report=dict(status='PASS_R18_ORGANIC_PALM_PRINT_SURFACES' if not bad else 'FAIL',candidate=CANDIDATE,replacement=REPLACEMENT,checks=checks,failures=bad,metrics=metrics,CAD_source_sha256=LAYOUT['CAD_source_sha256'],layout_sha256=sha(LAYOUT_PATH),project_sha256=sha(PROJECT),sliced_archive_sha256=sha(SLICED),regions_sha256=sha(region_path),validator_sha256=sha(__file__),scope='Whole support bead XY sweep and layer height tested against each open cutter disk plus the explicitly declared round allowance above its hand-facing floor. Floor underside supports below the contact plane are outside this check. Curved outer wall layers and floor/round model paths must exist.',limitations='Nominal sliced paths only; actual hand fit, surface texture and support removal remain physical checks.')
os.environ.setdefault('MPLCONFIGDIR','/tmp/fingerworker-r18-mpl')
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
pocket=next((p for p in cfg['pockets'] if p['center_xy_mm'][1]>0),cfg['pockets'][0]);cx,cy=pocket['center_xy_mm'];floor=pocket['floor_z_mm'];radius=pocket['radius_mm'];sign=1 if cy>0 else -1
mesh=trimesh.load(OUT/'source-mm/P01.stl',force='mesh');fig,axes=plt.subplots(1,2,figsize=(13,5.5),layout='constrained')
for ax,origin,normal,indices,title in [(axes[0],[cx,0,0],[1,0,0],[1,2],'Thumb pocket: transverse section'),(axes[1],[0,0,floor+5],[0,0,1],[0,1],'Open side: horizontal section')]:
 section=mesh.section(plane_origin=origin,plane_normal=normal)
 if section:
  for ent in section.entities:
   pts=section.vertices[ent.points];ax.plot(pts[:,indices[0]],pts[:,indices[1]],color='#405451',lw=1.4)
 lines=[]
 axis=0 if normal[0] else 2;value=origin[axis]
 for s in support:
  pts=s['native_points']
  if pts[:,axis].min()<=value+.3 and pts[:,axis].max()>=value-.3:
   lines.extend([[a[indices].tolist(),b[indices].tolist()] for a,b in zip(pts[:-1],pts[1:])])
 ax.add_collection(LineCollection(lines,colors='#279aca',linewidths=.5,alpha=.4));ax.set_aspect('equal');ax.grid(alpha=.15);ax.set_facecolor('#f5f8f8');ax.set_title(title)
 for point in seam_points:
  if (point[1]>0)==(cy>0):ax.scatter(point[indices[0]],point[indices[1]],s=5,c='#a845ad',alpha=.6,zorder=4)
axes[0].set(xlim=sorted([sign*56,sign*70]),ylim=(floor-5,35),xlabel='Assembly Y / mm',ylabel='Assembly Z / mm')
axes[0].axhline(floor,color='#df9f43',ls='--',lw=1)
axes[1].set(xlim=(cx-19,cx+19),ylim=sorted([sign*56,sign*71]),xlabel='Assembly X / mm',ylabel='Assembly Y / mm')
fig.suptitle('R18 side-thumb recess — actual mesh and support roads',size=14)
fig.supxlabel('Blue: support paths near section. Orange: floor. Purple: projected outer-wall restarts (seam candidates).',size=10)
image=PREVIEW/('P01-side-thumb-supports-candidate.png' if CANDIDATE else 'P01-side-thumb-supports.png');fig.savefig(image,dpi=160);plt.close(fig)
assert all(sha(Path(p))==h for p,h in start.items()),'Inputs changed during audit'
(V/'side-thumb-check.json').write_text(json.dumps(report,indent=2)+'\n')
(V/'side-thumb-preview-provenance.json').write_text(json.dumps(dict(status='RENDERED_ACTUAL_R18_ORGANIC_PALM_SUPPORT_PATHS',candidate=CANDIDATE,replacement=REPLACEMENT,source_mesh_sha256=sha(OUT/'source-mm/P01.stl'),sliced_archive_sha256=sha(SLICED),layout_sha256=sha(LAYOUT_PATH),image_sha256=sha(image),renderer_sha256=sha(__file__)),indent=2)+'\n')
print(json.dumps(dict(status=report['status'],checks=len(checks),failures=[dict(name=r['name'],intrusions=len(r.get('intrusions',[]))) for r in bad]),indent=2));raise SystemExit(bool(bad))
