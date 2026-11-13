#!/usr/bin/env python3
"""Check native palm outlines at the seven declared loft stations.

Uses exact CAD plane/solid section curves and sampled point-to-CAD-curve
distances in both directions. Between-station interpolation is deliberately
not required to be bit-identical across the two CAD kernels.
"""
from pathlib import Path
import argparse,importlib.util,json
import numpy as np
from OCP.BRepAlgoAPI import BRepAlgoAPI_Section
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeVertex
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
from OCP.BRepAdaptor import BRepAdaptor_Curve
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.TopAbs import TopAbs_EDGE
from OCP.TopExp import TopExp_Explorer
from OCP.TopoDS import TopoDS
from OCP.gp import gp_Pnt,gp_Dir,gp_Pln
HERE=Path(__file__).resolve().parent;STUDY=HERE.parent
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
a=module('section_integration',HERE/'audit_organic_integration.py');b=a.b;sha=a.sha

def section(frame,y):
 operation=BRepAlgoAPI_Section(frame,gp_Pln(gp_Pnt(0,y,0),gp_Dir(0,1,0)),True)
 assert operation.IsDone(),'Native plane section failed'
 result=b.common(operation.Shape(),b.box([-40,y-.01,16.500013],[-7.9,y+.01,40]))
 assert BRepCheck_Analyzer(result).IsValid()
 edges=[];ex=TopExp_Explorer(result,TopAbs_EDGE)
 while ex.More():
  edge=TopoDS.Edge(ex.Current());ex.Next()
  if not any(edge.IsSame(q) for q in edges):edges.append(edge)
 assert edges,'Empty palm section'
 return result,edges

def directed(edges,target):
 maximum=0.;where=None;count=0
 for edge in edges:
  curve=BRepAdaptor_Curve(edge)
  for t in np.linspace(curve.FirstParameter(),curve.LastParameter(),65):
   p=curve.Value(float(t));vertex=BRepBuilderAPI_MakeVertex(p).Vertex()
   distance=BRepExtrema_DistShapeShape(vertex,target);distance.Perform();assert distance.IsDone()
   value=float(distance.Value());count+=1
   if value>maximum:maximum=value;where=list(p.Coord())
 return dict(maximum_point_to_curve_distance_mm=maximum,worst_sample_mm=where,sampled_points=count)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--source-sha',required=True);ap.add_argument('--native-step',type=Path,required=True);ap.add_argument('--inventory',type=Path,default=HERE/'native-step-inventory.json');args=ap.parse_args()
 assert sha(a.SOURCE)==args.source_sha;step_sha=sha(args.native_step)
 inv=json.loads(args.inventory.read_text());assert inv['native_step_sha256']==step_sha
 solids,_,_=b.read_step(args.native_step);native=solids[inv['native_part_correspondence']['P01']['candidates'][0]['solid_index']]
 old,_,_=a.a.baseline();c=module('section_candidate',a.GENERATOR);expected=c.expected(old)['P01'];rows=[]
 for row in c.SECTIONS:
  y=float(row[0]);actual,ae=section(native,y);want,we=section(expected,y)
  forward=directed(we,actual);reverse=directed(ae,want);error=max(forward['maximum_point_to_curve_distance_mm'],reverse['maximum_point_to_curve_distance_mm'])
  rows.append(dict(y_mm=y,status='PASS' if error<.01 else 'FAIL',declared_crown_z_mm=row[1],maximum_sampled_symmetric_outline_distance_mm=error,local_to_native=forward,native_to_local=reverse,local_edges=len(we),native_edges=len(ae)))
 assert sha(a.SOURCE)==args.source_sha and sha(args.native_step)==step_sha
 report=dict(status='PASS_NATIVE_R18_SECTION_FIDELITY' if all(q['status']=='PASS' for q in rows) else 'FAIL',source_sha256=args.source_sha,native_step_sha256=step_sha,validator_sha256=sha(__file__),generator_sha256=sha(a.GENERATOR),outline_tolerance_mm=.01,samples_per_section_edge=65,checks=rows,scope='Exact CAD section curves at declared loft stations, compared with explicitly sampled point-to-curve distances in both directions. Does not claim continuous Hausdorff equality or identical interpolation between stations. Hard envelope and mechanical interface checks are in native-integration.json.')
 (HERE/'native-section-fidelity.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status=report['status'],maximum_mm=max(q['maximum_sampled_symmetric_outline_distance_mm'] for q in rows),checks=rows),indent=2))
 return report['status']=='FAIL'
if __name__=='__main__':raise SystemExit(main())
