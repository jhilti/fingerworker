#!/usr/bin/env python3
"""Native R18/R19 geometry loaders; final source is composed by integrate_source.py.
The manufacturing geometry uses the successful native variable fillet, not the
archived failed OCC/direct-edit diagnostic.
"""
from pathlib import Path
import importlib.util,json,hashlib,math
import numpy as np
from OCP.BRepAlgoAPI import BRepAlgoAPI_Defeaturing
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeVertex
from OCP.BRepAdaptor import BRepAdaptor_Curve
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE
from OCP.TopoDS import TopoDS
from OCP.gp import gp_Pnt
HERE=Path(__file__).resolve().parent;STUDY=HERE.parent;ROOT=STUDY.parents[1];BASE=ROOT/'review/organic-palm-2026-11-13'
s=importlib.util.spec_from_file_location('rim_r18',BASE/'mechanics/organic_palm.py');r18=importlib.util.module_from_spec(s);s.loader.exec_module(r18)
b,r17,prior,vec=r18.b,r18.r17,r18.prior,r18.vec
SOURCE=STUDY/'fingerworker_R19_thumb_rim.fs';BASE_SOURCE=BASE/'fingerworker_R18_organic_palm.fs';BASE_SHA='345b90327031276f8085e2c225c795946036d7faa4f2ac01b764101b9f4b3dd1';sha=r18.sha
rows=json.loads((HERE/'native-rim-faces.json').read_text())
POSITIVE_PICKS=[q['uv_midpoint'] for q in rows if q['index'] in [341,342,343,344,345,346]]
FACE_PICKS=[q['point_mm'] for q in json.loads((HERE/'native-face-picks.json').read_text())['faces']]
def load():
 inv=json.loads((BASE/'validation/native-step-inventory.json').read_text());assert sha(inv['native_step'])==inv['native_step_sha256'];ss,_,_=b.read_step(inv['native_step'])
 return {ref:ss[q['candidates'][0]['solid_index']] for ref,q in inv['native_part_correspondence'].items()},inv

def faces(shape):
 ex=TopExp_Explorer(shape,TopAbs_FACE);out=[]
 while ex.More():out.append(TopoDS.Face(ex.Current()));ex.Next()
 return out

def selected_faces(shape):
 fs=faces(shape);selected=[]
 for pt in FACE_PICKS:
  vertex=BRepBuilderAPI_MakeVertex(gp_Pnt(*pt)).Vertex();hits=[f for f in fs if b.gap(vertex,f)<1e-6]
  assert len(hits)==1,(pt,len(hits));selected+=hits
 assert len(selected)==12
 return selected

def load_rim_probe():
 """Return literal native successful variable-rim probe, never an OCC surrogate."""
 binding=json.loads((STUDY/'native-probe/probe-binding.json').read_text())
 step=ROOT/binding['native_step'];assert sha(step)==binding['native_step_sha256']
 solids,_,_=b.read_step(step);old,_=load();bb=b.bounds(old['P01'])
 hits=[q for q in solids if np.max(np.abs(b.bounds(q)-bb))<.01]
 assert len(hits)==1 and BRepCheck_Analyzer(hits[0]).IsValid()
 return hits[0],binding

if __name__=='__main__':
 raise SystemExit('Use integrate_source.py for the final source; native probe is authoritative for the variable rim.')
