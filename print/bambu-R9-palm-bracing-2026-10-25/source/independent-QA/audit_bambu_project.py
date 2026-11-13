#!/usr/bin/env python3
"""Independent read-only 3MF source-to-mesh, transform/profile/plate audit."""
from pathlib import Path
from itertools import product,combinations
import json,hashlib,zipfile,xml.etree.ElementTree as ET
import numpy as np
import trimesh
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];OUT=ROOT/'print/bambu-R9-palm-bracing-2026-10-25';R8=ROOT/'review/flat132-palm-bracing-2026-10-25'
NS={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'};P='{http://schemas.microsoft.com/3dmanufacturing/production/2015/06}'
TOL=3e-5
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def md(n):return {m.get('key'):m.get('value') for m in n.findall('metadata') if m.get('key')}
def trans(s):
 if s is None:return np.eye(4)
 v=np.array([float(x) for x in s.split()]);assert len(v)==12
 t=np.eye(4);t[:3,:]=v.reshape(4,3).T;return t
def sorted_faces(f):
 f=np.sort(f,axis=1);return f[np.lexsort((f[:,2],f[:,1],f[:,0]))]
def correspondence(actual,expected):
 # Grid-nearest, preserving topology. No welding, repairing or quantized-geometry acceptance.
 cell=.001;d={}
 for i,point in enumerate(expected):d.setdefault(tuple(np.floor(point/cell).astype(int)),[]).append(i)
 mapping=[];largest=0.
 for point in actual:
  key=np.floor(point/cell).astype(int);cand=[]
  for delta in product([-1,0,1],repeat=3):cand.extend(d.get(tuple(key+delta),[]))
  if not cand:raise AssertionError('No source vertex within neighboring .001mm cells')
  dist=np.linalg.norm(expected[cand]-point,axis=1);j=int(np.argmin(dist));largest=max(largest,float(dist[j]));mapping.append(cand[j])
 return np.asarray(mapping),largest

def main():
 checks=[]
 def add(name,test,**ev):checks.append(dict(name=name,status='PASS' if test else 'FAIL',**ev))
 layout=json.loads((OUT/'plate-layout.json').read_text());plan={r['ref']:r for r in layout['placements']}
 project=OUT/'Fingerworker_R9_H2D_04mm_PLA_Fit_Test.3mf';z=zipfile.ZipFile(project);add('Editable archive CRC',z.testzip() is None)
 config=ET.fromstring(z.read('Metadata/model_settings.config'));names={o.get('id'):md(o)['name'].split(' - ')[0] for o in config.findall('object')}
 settings={names[o.get('id')]:md(o) for o in config.findall('object')};globalsettings=json.loads(z.read('Metadata/project_settings.config'))
 roots={};objects={}
 def load(path):
  if path not in roots:
   root=ET.fromstring(z.read(path));assert root.get('unit')=='millimeter';roots[path]=root;objects[path]={o.get('id'):o for o in root.findall('m:resources/m:object',NS)}
  return roots[path]
 def mesh(path,ident):
  load(path);o=objects[path][ident];raw=o.find('m:mesh',NS)
  if raw is not None:
   verts=np.array([[float(v.get(k)) for k in ['x','y','z']] for v in raw.findall('m:vertices/m:vertex',NS)]);faces=np.array([[int(t.get(k)) for k in ['v1','v2','v3']] for t in raw.findall('m:triangles/m:triangle',NS)]);return verts,faces
  vv=[];ff=[];n=0
  for child in o.findall('m:components/m:component',NS):
   a,f=mesh(child.get(P+'path',path).lstrip('/'),child.get('objectid'));t=trans(child.get('transform'));a=a@t[:3,:3].T+t[:3,3];vv.append(a);ff.append(f+n);n+=len(a)
  assert vv;return np.concatenate(vv),np.concatenate(ff)
 root=load('3D/3dmodel.model');build=root.findall('m:build/m:item',NS);add('One plate and19 editable objects',len(build)==19 and len(config.findall('plate'))==1,build_count=len(build),plate_count=len(config.findall('plate')))
 add('Exact selected references',set(names.values())==set(plan) and len(plan)==19,refs=sorted(plan))
 manifest=json.loads((R8/'assembly-mm/part-manifest.json').read_text())['parts'];qmanifest=json.loads((OUT/'fixture/manifest.json').read_text())
 rows=[]
 for item in build:
  ref=names[item.get('objectid')];row=plan[ref];src=ROOT/row['source_path'];digest=sha(src)
  expected_hash=manifest[ref]['output_sha256'] if ref!='Q01' else qmanifest['files']['Q01_UNLOADED_TEST_FIXTURE_print-mm.stl']['sha256']
  add('Exact source hash '+ref,digest==expected_hash==row['source_sha256'] and sha(OUT/'source-mm'/(ref+'.stl'))==digest,source_sha256=digest)
  source=trimesh.load(src,force='mesh');R=np.array(row['rotation_3x3']);tt=np.array(row['normalization_translation_mm'])+[*row['plate_xy_mm'],0]
  add('Proper rigid scale1 transform '+ref,np.allclose(R.T@R,np.eye(3)) and abs(np.linalg.det(R)-1)<1e-10 and row['scale']==1,determinant=float(np.linalg.det(R)))
  expected=source.vertices@R.T+tt;vv,ff=mesh('3D/3dmodel.model',item.get('objectid'));t=trans(item.get('transform'));vv=vv@t[:3,:3].T+t[:3,3]
  mapping,error=correspondence(vv,expected);same=len(ff)==len(source.faces) and np.array_equal(sorted_faces(mapping[ff]),sorted_faces(source.faces))
  add('Native editable mesh equals rigid source '+ref,same and error<TOL and item.get('printable')=='1',max_vertex_error_mm=error,triangle_connectivity_equal=same,triangles=len(ff))
  bounds=np.array([vv.min(axis=0),vv.max(axis=0)]);margin=row['reserved_margin_mm'];reserved=np.array([bounds[0,:2]-margin,bounds[1,:2]+margin]);safe=np.array(layout['safe_shared_XY_mm'])
  add('Model/brim reservation inside H2D shared-bed region '+ref,bool(np.all(reserved[0]>=safe[0]-TOL) and np.all(reserved[1]<=safe[1]+TOL) and abs(bounds[0,2])<TOL),bounds_mm=bounds.tolist(),reserved_bounds_xy_mm=reserved.tolist())
  rows.append({'ref':ref,'bounds_mm':bounds.tolist(),'reserved_bounds_xy_mm':reserved.tolist(),'mesh_error_mm':error,'volume_mm3':float(source.volume),'source_sha256':digest})
 for a,b in combinations(rows,2):
  aa=np.array(a['reserved_bounds_xy_mm']);bb=np.array(b['reserved_bounds_xy_mm']);sep=np.maximum(bb[0]-aa[1],aa[0]-bb[1]);add('Pairwise brim/support reservation separation '+a['ref']+'/'+b['ref'],bool(np.max(sep)>=1.5-TOL),minimum_axis_separation_mm=float(np.max(sep)))
 for name,test in [('printer_model',lambda v:v=='Bambu Lab H2D'),('nozzle_diameter',lambda v:all(float(x)==.4 for x in v)),('filament_type',lambda v:v==['PLA']),('curr_bed_type',lambda v:v=='Textured PEI Plate'),('print_sequence',lambda v:v=='by layer'),('layer_height',lambda v:float(v)==.2),('wall_loops',lambda v:int(v)==4)]:add('Pinned global setting '+name,test(globalsettings.get(name)),value=globalsettings.get(name))
 for ref in plan:
  for key,value in layout['object_settings'][ref].items():
   actual=settings[ref].get(key,globalsettings.get(key));add('Object override '+ref+'/'+key,all(x==str(value) for x in str(actual).split(',')),actual=actual,expected=value)
 add('Q01/P04/P08 support on model; P06 buildplate only',all(settings[r]['support_on_build_plate_only']=='0' for r in ['Q01','P04','P08']) and all(settings[r]['support_on_build_plate_only']=='1' for r in ['P060','P061']))
 add('P07 nominal1.5 via0.1 layers',all(settings[r]['layer_height']=='0.1' for r in plan if r.startswith('P07')))
 profile=json.loads((OUT/'profiles/profile-manifest.json').read_text())
 for key,digest in profile['machine_macro_hashes'].items():
  actual=hashlib.sha256(json.dumps(globalsettings[key],sort_keys=True).encode()).hexdigest();add('Official machine macro retained '+key,actual==digest,sha256=actual)
 result={'status':'PASS_FULL_SCALE_NATIVE_EDITABLE_PROJECT' if all(c['status']=='PASS' for c in checks) else 'FAIL','project':str(project),'project_sha256':sha(project),'layout_sha256':sha(OUT/'plate-layout.json'),'source_revision':'R9','frozen_source_sha256':sha(R8/'fingerworker_flat132_palm_bracing.fs'),'native_version_binding':'See parent R9 validation manifest','fixture_manifest_sha256':sha(OUT/'fixture/manifest.json'),'object_count':len(rows),'objects':rows,'checks':checks,'failed_checks':sum(c['status']=='FAIL' for c in checks),'comparison_tolerance_mm':TOL,'scope':'Native editable3MF matches source triangles under proper rigid transforms and scale1; nominal reserved bed/layout and profiles. Actual sliced support/extrusion paths require separate toolpath report.'}
 (HERE/'qa-project.json').write_text(json.dumps(result,indent=2)+'\n');print(result['status'],'checks',len(checks),'fail',result['failed_checks']);print(json.dumps([c for c in checks if c['status']=='FAIL'],indent=2));assert result['failed_checks']==0
if __name__=='__main__':main()
