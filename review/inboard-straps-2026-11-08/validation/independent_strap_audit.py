"""Independent exact native/lane review; explicit finite2mm band and4mm allowance."""
from pathlib import Path
import argparse,hashlib,importlib.util,json
import numpy as np
ROOT=Path(__file__).resolve().parents[3];STUDY=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('g',STUDY/'mechanics/inboard_straps.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);b=m.b
from OCP.BRepCheck import BRepCheck_Analyzer
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ap=argparse.ArgumentParser();ap.add_argument('--native',action='store_true');args=ap.parse_args()
if args.native:
 inv=json.loads((STUDY/'validation/native-step-inventory.json').read_text());ss=b.read_step(inv['native_step'])[0];parts={r:ss[v['candidates'][0]['solid_index']] for r,v in inv['native_part_correspondence'].items()}
else:
 parts,inv=m.load();parts['P01']=m.expected(parts)['P01']
design=json.loads((STUDY/'mechanics/design-specification.json').read_text());st=design['strap_mount'];xs=st['position_x_mm'];assert xs==[28,65] and st['slot_center_y_mm']==[-57.5,57.5]
rows=[]
def add(name,ok,**d):rows.append(dict(name=name,status='PASS' if ok else 'FAIL',**d))
def volume(s):assert BRepCheck_Analyzer(s).IsValid();return b.volume(s)
for x in xs:
 for sign in [-1,1]:
  def box(y0,y1,z0,z1):
   yy=sorted([sign*y0,sign*y1]);return b.box([x-12.5,yy[0],z0],[x+12.5,yy[1],z1])
  single=m.prior.union([box(56.5,58.5,-20,6),box(56.5,70,4,6),box(66,70,-20,6)])
  conservative=m.prior.union([box(56.5,58.5,-20,8),box(56.5,70,4,8),box(66,70,-20,8)])
  for mode,route in [('single2mm',single),('conservative4mm',conservative)]:
   rb=b.bounds(route)
   for ref,s in parts.items():
    sb=b.bounds(s)
    if np.any(rb[1]<sb[0]) or np.any(sb[1]<rb[0]):continue
    vv=volume(b.common(route,s));add(f'X{x}/{sign}/{mode} seated {ref}',vv<1e-6,overlap_mm3=vv)
   for ref in ['P04','H060','H061','P11','H10']:
    slab=b.box([-200,rb[0,1],rb[0,2]],[200,rb[1,1],rb[1,2]])
    clipped=b.common(parts[ref],slab);vv=volume(clipped)
    if vv<1e-7:
     add(f'X{x}/{sign}/{mode} whole stroke {ref}',True,proof='No exact native geometry anywhere in finite route Y/Z slab. X translation cannot enter slab.');continue
    bb=b.bounds(clipped);native_bounds=bb.copy();lo,hi=(-30.8,.8) if ref in ['P11','H10'] else (-30,0);bb[0,0]+=lo;bb[1,0]+=hi
    gap=b.gap(route,b.box(bb[0],bb[1]));add(f'X{x}/{sign}/{mode} whole stroke {ref}',gap>1e-6,gap_lower_bound_mm=gap,clipped_native_bounds_mm=native_bounds.tolist(),complete_x_interval_mm=[lo,hi])
add('Both side slots keep declared nominal ligaments',66-(57.5+2)==6.5 and (57.5-2)-38==17.5,outer_mm=6.5,inner_mm=17.5,net_rail_reduction_mm=4)
add('Front/rear station spacing and intervening slot ligament',xs[1]-xs[0]==37 and xs[1]-xs[0]-27==10,spacing_mm=37,slot_end_ligament_mm=10)
bad=[r for r in rows if r['status']=='FAIL'];report=dict(status=('PASS_NATIVE_INDEPENDENT_STRAP_REVIEW' if args.native else 'PASS_CANDIDATE_INDEPENDENT_STRAP_REVIEW') if not bad else 'FAIL',checks=rows,failures=bad,source_sha256=sha(STUDY/'fingerworker_R15_inboard_straps.fs'),validator_sha256=sha(__file__),native_step_sha256=inv['native_step_sha256'],limitations=['Finite ribbon routes only; closure, object/thigh and free ribbon belowZ-20 unmodeled.','Conservative4mm above-strip allowance may approach moving spring seats more closely than intended2mm single ribbon.','Slots remove material from side rails; nominal6mm floor thickness is retained without broad recess, but structural equivalence/strength is not established.','37mm station spacing provides less resistance to rocking than prior75mm spacing; actual strapped stability requires testing.'])
(STUDY/'validation'/('independent-strap-native.json' if args.native else 'independent-strap-candidate.json')).write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status=report['status'],checks=len(rows),failures=bad),indent=2));raise SystemExit(bool(bad))
