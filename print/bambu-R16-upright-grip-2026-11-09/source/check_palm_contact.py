#!/usr/bin/env python3
"""Conservative full-bead exclusion of supports at R16 hand-contact surfaces."""
from pathlib import Path
import argparse,hashlib,json,os,zipfile,xml.etree.ElementTree as E
import numpy as np
import trimesh
from shapely.geometry import LineString,box
from shapely.ops import unary_union
import check_print_features as paths

OUT=Path(__file__).resolve().parents[1];ROOT=OUT.parents[1]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
p=argparse.ArgumentParser();p.add_argument('--candidate',action='store_true');a=p.parse_args()
layoutpath=OUT/('candidate-layout.json' if a.candidate else 'plate-layout.json');layout=json.loads(layoutpath.read_text())
row=next(r for r in layout['placements'] if r['ref']=='P01');V=OUT/'validation'/('candidate' if a.candidate else '')
sliced=V/(Path(layout['native_project']).stem+'_verification.gcode.3mf')
input_paths=[layoutpath,sliced,OUT/layout['native_project'],OUT/'source-mm/P01.stl']
input_hashes={str(p):sha(p) for p in input_paths}
with zipfile.ZipFile(sliced) as z:
 info=E.fromstring(z.read('Metadata/slice_info.config'));plate=info.find('plate')
 ident=int(next(o for o in plate.findall('object') if o.get('name','').startswith('P01 ')).get('identify_id'))
 data=paths.native_paths([s for s in paths.parse(z.read('Metadata/plate_1.gcode').decode()) if s['obj']==ident],row)
support=[s for s in data if s['feature'] in paths.SUPPORT];model=[s for s in data if s['feature'] not in paths.NONMODEL]
checks=[]
def add(name,ok,**kw):checks.append(dict(name=name,status='PASS' if bool(ok) else 'FAIL',**kw))
def bb(s):
 pts=s['native_points'];lo=pts.min(0);hi=pts.max(0)
 lo[:2]-=s['width']/2;hi[:2]+=s['width']/2;lo[2]=hi[2]-s['height']
 return lo,hi
boxes=[bb(s) for s in support]
# These boxes contain the entire intended face/curves and the thumb cavity
# roofs, not just road midpoints. Any overlap fails, even if only a bead cap.
# Palm rail is exactly Y±63; support under the separate shoulder overhangs
# outside that range is permitted below Z24, away from their Z28+ contact crown.
zones=[('wrist face and both thumb returns',[-35,-63,14.4],[-22.45,63,33.5]),
       ('rounded palm and shoulder tops',[-30,-65.5,27.5],[-7.5,65.5,33.5]),
       ('central sensor-side sloping underside',[-22.45,-36,19.1],[-15.5,36,27.4])]
for name,lo,hi in zones:
 hits=[]
 for s,(aa,bb_) in zip(support,boxes):
  if np.all(aa<=hi) and np.all(bb_>=lo):hits.append(dict(feature=s['feature'],bounds=[aa.tolist(),bb_.tolist()]))
 add('No support bead in '+name,not hits,region_mm=[lo,hi],support_intrusions=hits)
# A broad upright face must actually be emitted as model walls.
face=[s for s in model if s['feature']=='Outer wall' and np.max(np.abs(s['native_points'][:,0]+29))<.5 and s['native_points'][:,1].min()<35 and s['native_points'][:,1].max()>-35 and 15<s['native_b'][2]<27.5]
levels=sorted(set(round(s['native_b'][2],3) for s in face))
add('Upright palm face emitted over multiple layers',len(levels)>=50,outer_wall_segments=len(face),layer_count=len(levels),z_min=min(levels) if levels else None,z_max=max(levels) if levels else None)
for y in [-51,51]:
 zone=paths.roi(model,[-17.2,y-3.3,20],[-7.8,y+3.3,21.6]);bridges=[s for s in zone if 'bridge' in s['feature'].lower()]
 spans=paths.free_bridge_spans(bridges,model)
 maximum=max([s['longest_actual_unbacked_centerline_mm'] for s in spans] or [0])
 add('Short printed rod-bore roof spans '+str(y),maximum<=6.5,longest_unbacked_centerline_mm=maximum,bridge_segments=len(bridges))
bad=[c for c in checks if c['status']!='PASS']
report=dict(status='PASS_R16_PALM_CONTACT_SUPPORTS' if not bad else 'FAIL',candidate=a.candidate,checks=checks,failures=bad,
 source_sha256=layout['CAD_source_sha256'],layout_sha256=sha(layoutpath),project_sha256=sha(OUT/layout['native_project']),sliced_archive_sha256=sha(sliced),validator_sha256=sha(__file__),
 scope='Whole support bead axis-aligned bounds include full line width, complete native path extrema and layer height. No support overlap permitted in conservative R16 hand-contact zones; actual upright model wall layers and rod-bore roof bridge spans checked.',
 limitations='Nominal sliced geometry only, not measured surface finish, physical adhesion or hand comfort.')
assert all(sha(Path(p))==h for p,h in input_hashes.items()),'Inputs changed during support audit'
(V/'palm-contact-check.json').write_text(json.dumps(report,indent=2)+'\n')

# Render actual R16 P01 mesh sections together with actual support roads.
os.environ.setdefault('MPLCONFIGDIR','/tmp/fingerworker-r16-mpl')
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
fig,axes=plt.subplots(1,2,figsize=(14,6),layout='constrained');mesh=trimesh.load(OUT/'source-mm/P01.stl',force='mesh')
for ax,y,title in zip(axes,[0,-51],['Center: upright palm face','End: shallow thumb return']):
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
fig.suptitle('R16 palm grip — actual mesh sections and support paths',size=15)
fig.supxlabel('Blue: support roads within ±3 mm of each section. Contact faces and thumb-return ceilings remain clear.',size=10)
name='P01-contact-supports-candidate.png' if a.candidate else 'P01-contact-supports.png';image=OUT/'preview'/name
fig.savefig(image,dpi=160);plt.close(fig)
(V/'palm-preview-provenance.json').write_text(json.dumps(dict(status='RENDERED_ACTUAL_R16_P01_SUPPORT_PATHS',candidate=a.candidate,source_mesh_sha256=sha(OUT/'source-mm/P01.stl'),sliced_archive_sha256=sha(sliced),layout_sha256=sha(layoutpath),image_sha256=sha(image),renderer_sha256=sha(__file__)),indent=2)+'\n')
assert all(sha(Path(p))==h for p,h in input_hashes.items()),'Inputs changed during support audit'
print(json.dumps(dict(status=report['status'],candidate=a.candidate,checks=len(checks),failures=[dict(name=c['name'],hits=len(c.get('support_intrusions',[]))) for c in bad]),indent=2));raise SystemExit(bool(bad))
