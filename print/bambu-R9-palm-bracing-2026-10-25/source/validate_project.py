"""Verify Bambu native editable project preserves all nineteen exact source meshes."""
from pathlib import Path
from hashlib import sha256
import json, zipfile, xml.etree.ElementTree as E
import numpy as np
import trimesh as tm
from collections import defaultdict
from itertools import product
def nearest_error(a,b):
 buckets=defaultdict(list)
 for v in b:buckets[tuple(np.floor(v*1000).astype(int))].append(v)
 result=0.0
 for v in a:
  k=np.floor(v*1000).astype(int);near=[w for d in product((-1,0,1),repeat=3) for w in buckets.get(tuple(k+np.array(d)),[])]
  assert near
  result=max(result,float(np.linalg.norm(np.array(near)-v,axis=1).min()))
 return result
OUT=Path(__file__).resolve().parents[1]
ROOT=OUT.parents[1]
NATIVE=OUT/'Fingerworker_R9_H2D_04mm_PLA_Fit_Test.3mf'
SLICED=OUT/'validation/Fingerworker_R9_slice_verification.gcode.3mf'
NS={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}
PROD='{http://schemas.microsoft.com/3dmanufacturing/production/2015/06}'
def meta(node):return {n.get('key'):n.get('value') for n in node.findall('metadata') if n.get('key')}
def sha(p):return sha256(p.read_bytes()).hexdigest()
def translation(n):
 a=np.array([float(x) for x in n.get('transform').split()]);assert np.allclose(a[:9],np.eye(3).ravel());return a[9:]
layout=json.loads((OUT/'plate-layout.json').read_text());expected={r['ref']:r for r in layout['placements']}
macro=json.loads((OUT/'profiles/profile-manifest.json').read_text())
meshes={};audit=[]
with zipfile.ZipFile(NATIVE) as z:
 assert z.testzip() is None
 assert not any(n.endswith('.gcode') for n in z.namelist())
 cfg=json.loads(z.read('Metadata/project_settings.config'))
 assert cfg['printer_model']=='Bambu Lab H2D' and cfg['nozzle_diameter']==['0.4','0.4']
 assert cfg['filament_type']==['PLA'] and cfg['filament_map']==['1']
 assert cfg['extruder_nozzle_stats']==['Standard#1','Standard#1']
 assert cfg['curr_bed_type']=='Textured PEI Plate'
 macros={}
 for k,h in macro['machine_macro_hashes'].items():
  actual=sha256(json.dumps(cfg[k],sort_keys=True).encode()).hexdigest();assert actual==h,(k,h,actual);macros[k]=actual
 settings=E.fromstring(z.read('Metadata/model_settings.config'))
 objects={o.get('id'):o for o in settings.findall('object')};assert len(objects)==19
 plates=settings.findall('plate');assert len(plates)==1
 instances=plates[0].findall('model_instance');assert len(instances)==19
 for name in z.namelist():
  if name.startswith('3D/Objects/') and name.endswith('.model'):
   d=E.fromstring(z.read(name))
   for o in d.findall('m:resources/m:object',NS):
    m=o.find('m:mesh',NS)
    v=np.array([[float(v.get(k)) for k in ['x','y','z']] for v in m.findall('m:vertices/m:vertex',NS)])
    f=np.array([[int(f.get(k)) for k in ['v1','v2','v3']] for f in m.findall('m:triangles/m:triangle',NS)])
    meshes[o.get('id')]=tm.Trimesh(vertices=v,faces=f)
 assert len(meshes)==19
 model=E.fromstring(z.read('3D/3dmodel.model'));wrappers={o.get('id'):o for o in model.findall('m:resources/m:object',NS)}
 items=model.findall('m:build/m:item',NS);assert len(items)==19
 for item in items:
  oid=item.get('objectid');obj=objects[oid];m=meta(obj);key=m['name'].split(' - ')[0];r=expected[key]
  assert m['extruder']=='1'
  for k,v in layout['object_settings'][key].items():assert all(x==v for x in m[k].split(',')),(key,k,m.get(k),v)
  part=obj.find('part');source=tm.load_mesh(ROOT/r['source_path']);native=meshes[part.get('id')]
  assert sha(ROOT/r['source_path'])==r['source_sha256']==sha(OUT/'source-mm'/f'{key}.stl')
  R=np.array(r['rotation_3x3']);assert np.isclose(np.linalg.det(R),1)
  rotated=source.vertices@R.T+np.array(r['normalization_translation_mm'])
  a=native.vertices-native.bounds[0];b=rotated-rotated.min(0)
  err=nearest_error(a,b);assert err<.0001,(key,err)
  assert len(native.faces)==r['faces'] and native.is_watertight and native.is_volume
  assert np.allclose(native.extents,r['size_oriented_mm'],atol=.0001)
  assert abs(native.volume-source.volume)<max(.01,source.volume*1e-5)
  comp=wrappers[oid].find('m:components/m:component',NS)
  bbox=native.bounds+translation(comp)+translation(item)
  assert np.allclose(bbox[0],[*r['plate_xy_mm'],0],atol=.0001),(key,bbox)
  assert bbox[0,0]>=27 and bbox[1,0]<=323 and bbox[0,1]>=3 and bbox[1,1]<=317
  stats=part.find('mesh_stat');assert all(int(stats.get(k,'0'))==0 for k in ['edges_fixed','degenerate_facets','facets_removed','facets_reversed','backwards_edges'])
  audit.append(dict(ref=key,source_sha256=r['source_sha256'],mesh_roundtrip_max_error_mm=err,rigid_rotation_det=float(np.linalg.det(R)),bbox_plate_mm=bbox.tolist(),faces=len(native.faces),automatic_repairs=0))
with zipfile.ZipFile(SLICED) as z:
 assert z.testzip() is None
 info=E.fromstring(z.read('Metadata/slice_info.config'));p=info.find('plate');m=meta(p)
 assert m['outside']=='false'
 o=p.findall('object');assert len(o)==19 and all(i.get('skipped')=='false' for i in o)
 assert [f.get('type') for f in p.findall('filament')]==['PLA']
 g=z.read('Metadata/plate_1.gcode').decode()
 import re
 labels=set(re.findall(r'; start printing object, unique label id: (\d+)',g));assert len(labels)==19
 header_heights=[float(x) for x in re.search(r'; object max height: ([^\n]+)',g)[1].split(',')]
 assert header_heights[14:18]==[1.5]*4
 result=dict(status='NATIVE_PROJECT_AND_SLICE_PASS',scope='Exact native mesh/rigid placements, full stock macro preservation, 19 objects with sliced toolpaths. Critical feature path QA is independent.',native_project=NATIVE.name,native_sha256=sha(NATIVE),sliced_internal_evidence_sha256=sha(SLICED),plate_count=1,object_count=19,no_printer_transmission=True,estimated_seconds=int(m['prediction']),estimated_grams=float(m['weight']),slicer_exit_code=0,header_object_heights_mm=header_heights,mesh_roundtrip=audit,machine_macro_hashes=macros,stock_macros_modified=False,stock_macro_parser_diagnostics=['T1001','T65535','T65279'])
(OUT/'validation/native-project-check.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:result[k] for k in ['status','native_sha256','object_count','estimated_seconds','estimated_grams']},indent=2))
