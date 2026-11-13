#!/usr/bin/env python3
"""Independent surface measurements for the selected native thumb-rim faces."""
from pathlib import Path
import importlib.util,json,hashlib
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE
from OCP.TopoDS import TopoDS
from OCP.BRep import BRep_Tool
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeVertex
from OCP.GeomAPI import GeomAPI_ProjectPointOnSurf
from OCP.GeomLProp import GeomLProp_SLProps
from OCP.gp import gp_Pnt
HERE=Path(__file__).resolve().parent;STUDY=HERE.parent;ROOT=STUDY.parents[1];BASE=ROOT/'review/organic-palm-2026-11-13'
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
a=module('rim_prior_validation',BASE/'validation/audit_organic_integration.py');b=a.b;sha=a.sha

def baseline():
 release=json.loads((BASE/'validation/native-release-binding.json').read_text())
 assert release['status']=='PASS_NATIVE_R18_SOURCE_EXPORT_REPORT_BINDING' and release['version_id']=='13e353d6762b6cc58530122b'
 assert sha(BASE/'fingerworker_R18_organic_palm.fs')==release['source_sha256']=='345b90327031276f8085e2c225c795946036d7faa4f2ac01b764101b9f4b3dd1'
 inv=json.loads((BASE/'validation/native-step-inventory.json').read_text());assert sha(inv['native_step'])==release['native_step_sha256']
 ss,_,_=b.read_step(inv['native_step']);parts={r:ss[q['candidates'][0]['solid_index']] for r,q in inv['native_part_correspondence'].items()}
 return parts,inv,release

def faces(shape):
 ex=TopExp_Explorer(shape,TopAbs_FACE);out=[]
 while ex.More():out.append(TopoDS.Face(ex.Current()));ex.Next()
 return out

def curvature_at(face,point):
 surface=BRep_Tool.Surface_s(face);projection=GeomAPI_ProjectPointOnSurf(gp_Pnt(*point),surface);assert projection.NbPoints()>0
 u,v=projection.LowerDistanceParameters();props=GeomLProp_SLProps(surface,u,v,2,1e-9);assert props.IsCurvatureDefined()
 curvature=[float(props.MaxCurvature()),float(props.MinCurvature())]
 return dict(surface_projection_distance_mm=float(projection.LowerDistance()),principal_curvatures_per_mm=curvature,principal_radii_mm=[1/abs(k) if abs(k)>1e-9 else None for k in curvature])

def main():
 old,_,release=baseline();picks=json.loads((STUDY/'mechanics/native-face-picks.json').read_text());assert picks['native_R18_step_sha256']==release['native_step_sha256']
 fs=faces(old['P01']);rows=[]
 for row in picks['faces']:
  vertex=BRepBuilderAPI_MakeVertex(gp_Pnt(*row['point_mm'])).Vertex()
  hits=[(i,f) for i,f in enumerate(fs) if b.gap(vertex,f)<1e-6];assert len(hits)==1
  index,face=hits[0]
  rows.append(dict(declared_native_face_index=row['native_face_index'],zero_based_face_index=index,point_mm=row['point_mm'],**curvature_at(face,row['point_mm'])))
 report=dict(status='MEASURED_R18_RIM_BASELINE',source_sha256=release['source_sha256'],native_step_sha256=release['native_step_sha256'],native_release_binding_sha256=sha(BASE/'validation/native-release-binding.json'),face_picks_sha256=sha(STUDY/'mechanics/native-face-picks.json'),validator_sha256=sha(__file__),checks=rows)
 (HERE/'baseline-rim-measurements.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(rows,indent=2))
if __name__=='__main__':main()
