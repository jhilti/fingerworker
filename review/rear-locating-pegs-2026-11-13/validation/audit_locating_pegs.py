#!/usr/bin/env python3
"""Independent R20 locating fit and complete axial-sweep checks; no slicing."""
from pathlib import Path
import importlib.util,json,argparse
import numpy as np
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.TopAbs import TopAbs_SOLID,TopAbs_SHELL,TopAbs_FACE,TopAbs_EDGE
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeEdge
from OCP.TopExp import TopExp_Explorer
from OCP.gp import gp_Pnt
HERE=Path(__file__).resolve().parent;STUDY=HERE.parent;ROOT=STUDY.parents[1];BASE=ROOT/'review/thumb-rim-2026-11-13'
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
r=module('r20_r19_validator',BASE/'validation/audit_native_r19.py');b=r.b;sha=r.sha

def baseline():
 release=json.loads((BASE/'validation/native-release-binding.json').read_text());assert release['status']=='PASS_NATIVE_R19_SOURCE_EXPORT_REPORT_BINDING'
 inv=json.loads((BASE/'validation/native-step-inventory.json').read_text());assert sha(inv['native_step'])==release['native_step_sha256']
 ss,_,_=b.read_step(inv['native_step']);return {ref:ss[q['candidates'][0]['solid_index']] for ref,q in inv['native_part_correspondence'].items()},release

def vol(shape):
 assert BRepCheck_Analyzer(shape).IsValid();return b.volume(shape)
def empty(shape):return BRepCheck_Analyzer(shape).IsValid() and b.count(shape,TopAbs_SOLID)==b.count(shape,TopAbs_FACE)==0

def capsule(cx,y,rad,zlo,zhi,travel):
 cyl=r.m.m.r7.cyl
 out=cyl([cx,y,zlo],[cx,y,zhi],rad)
 if travel:
  out=b.fuse(out,cyl([cx+travel,y,zlo],[cx+travel,y,zhi],rad));out=b.fuse(out,b.box([cx,y-rad,zlo],[cx+travel,y+rad,zhi]))
 return out

def peg_envelope(y,travel=0):
 # Conservative bands for Ø5 peg / R0.4 root. The entire root is covered;
 # no untested discrete travel steps are substituted for a continuous sweep.
 return r.r.a.a.union([capsule(123.8,y,2.5,2.5,4.1,travel),capsule(123.8,y,2.56,4.1,4.3,travel),capsule(123.8,y,2.9,4.3,4.5,travel)])

def checks(parts,old):
 rows=[]
 def ck(name,ok,**details):rows.append(dict(name=name,status='PASS' if bool(ok) else 'FAIL',**details))
 for ref in ['P01','P06L','P06R']:
  q=parts[ref];ck('One valid solid and shell '+ref,BRepCheck_Analyzer(q).IsValid() and b.count(q,TopAbs_SOLID)==b.count(q,TopAbs_SHELL)==1)
 # Clip away the unrelated freeform palm before rear stock comparisons.
 rear=b.box([100,-70,-5],[140,70,40]);front=b.box([-50,-70,-5],[100,70,40])
 comp=r.comparison(b.common(parts['P01'],front),b.common(old['P01'],front));ck('Complete front frame and R19 ergonomics unchanged',comp['empty'],**comp)
 pbefore=b.common(old['P01'],rear);pafter=b.common(parts['P01'],rear);removed=b.cut(pbefore,pafter);added=b.cut(pafter,pbefore)
 ck('Frame receives no added obstruction',empty(added),added_mm3=vol(added))
 allowed=r.r.a.a.union([r.m.boxside(120.5,129.2,47.7,54.3,2.19,4.61,sign) for sign in [-1,1]])
 outside=b.cut(removed,allowed);ck('Frame removal limited to the two blind-bottom rear slots',empty(outside),unexpected_removed_mm3=vol(outside))
 for sign,ref in [(-1,'P06L'),(1,'P06R')]:
  y=sign*51;block=parts[ref];inc=b.cut(block,old[ref]);lost=b.cut(old[ref],block)
  ck('Original block rod socket and screw stock retained '+ref,empty(lost),removed_original_mm3=vol(lost))
  outside=b.cut(inc,peg_envelope(y));ck('New stock confined to short integral peg and root '+ref,empty(outside),unexpected_added_mm3=vol(outside))
  clear=b.gap(inc,parts['P01']);ck('Peg has positive nominal mating clearance '+ref,clear>=.19,minimum_clearance_mm=clear,nominal_shaft_side_clearance_mm=.2,nominal_bottom_clearance_mm=.3,fit='Clearance fit; physical printing tolerances unqualified')
  sweep=peg_envelope(y,12);inter=b.common(sweep,parts['P01']);clear=b.gap(sweep,parts['P01'])
  ck('Complete12mm axial peg insertion/extraction clears frame '+ref,vol(inter)<1e-6 and clear>.05,overlap_mm3=vol(inter),clearance_lower_bound_mm=clear,travel_mm=[0,12],method='Whole continuous swept conservative three-band peg/root envelope')
  for off in [-9.5,9.5]:
   insert=r.m.m.r7.cyl([124.5,y+off,.5],[124.5,y+off,4.6],2.1);gap=b.gap(removed,insert)
   ck('Slot keeps M3 insert wall '+ref+' '+str(off),gap>=4.15,minimum_remaining_mm=gap)
  rod=r.m.m.r7.cyl([-16,y,18],[125,y,18],3);gap=b.gap(inc,rod);ck('Peg clear of existing rod '+ref,gap>=10.49,clearance_mm=gap)
  for moving in ['P04','H060','H061','P11','H10']:
   bb=b.bounds(old[moving]).copy();lo,hi=(-30.8,.8) if moving in ['P11','H10'] else (-30,0);bb[0,0]+=lo;bb[1,0]+=hi;gap=b.gap(inc,b.box(bb[0],bb[1]))
   ck('New peg clear of complete travel '+ref+' '+moving,gap>1e-6,clearance_lower_bound_mm=gap)
 # The slot opens at the rear; sample actual retained underside including the
 # rounded plate exit. Interior and edge measurements are reported separately.
 floor=[]
 for sign in [-1,1]:
  for x in [121.5,123.8,126,127.5,128,128.5,128.9,128.99]:
   line=BRepBuilderAPI_MakeEdge(gp_Pnt(x,sign*51,-5),gp_Pnt(x,sign*51,5)).Edge();section=b.common(parts['P01'],line);ex=TopExp_Explorer(section,TopAbs_EDGE);intervals=[]
   while ex.More():
    q=b.bounds(ex.Current());intervals.append([float(q[0,2]),float(q[1,2])]);ex.Next()
   material=[q for q in intervals if q[0]<0 and 2<q[1]<2.3];assert len(material)==1,(x,sign,intervals)
   zz=material[0];floor.append(dict(x_mm=x,y_mm=sign*51,z_interval_mm=zz,thickness_mm=zz[1]-zz[0]))
 interior=min(q['thickness_mm'] for q in floor if q['x_mm']<=127.5);edge=min(q['thickness_mm'] for q in floor)
 ck('Blind slot retains base floor',interior>=4.19 and edge>=2.69,interior_minimum_sampled_thickness_mm=interior,rear_rounded_edge_minimum_sampled_thickness_mm=edge,sections=floor,scope='Exact vertical sections; edge thickness follows the pre-existing rear base fillet')
 same=r.comparison(r.m.move(parts['P06L'],[0,102,0]),parts['P06R']);ck('Pegged blocks remain identical after102mm translation',same['empty'],**same)
 return rows

def main():
 old,release=baseline();c=module('r20_candidate',STUDY/'mechanics/rear_pegs.py');changed=c.expected(old);assert set(changed)=={'P01','P06L','P06R'};parts={**old,**changed}
 rows=checks(parts,old);failed=[q for q in rows if q['status']!='PASS']
 sources=list(STUDY.glob('fingerworker_R20*.fs'));assert len(sources)==1
 report=dict(status='PASS_LOCAL_R20_LOCATING_FIT' if not failed else 'REVIEW_LOCAL_R20_LOCATING_FIT',source_sha256=sha(sources[0]),generator_sha256=sha(STUDY/'mechanics/rear_pegs.py'),baseline_release_binding_sha256=sha(BASE/'validation/native-release-binding.json'),baseline_native_step_sha256=release['native_step_sha256'],validator_sha256=sha(__file__),checks=rows,failures=failed,scope='Local candidate nominal fit and complete axial peg path; fresh native regeneration/export validation remains required. No print projects changed, no physical interference-fit claim, screwless dry fit requires springs removed/unloaded because existing fixed spring compression already loads the rear blocks at rest; no substitute for required rear screws.')
 (HERE/'local-locating-fit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status=report['status'],checks=len(rows),failures=failed),indent=2));return bool(failed)
if __name__=='__main__':raise SystemExit(main())
