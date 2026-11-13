"""Cursory source/import and two-piece slice check, without physical qualification."""
from pathlib import Path
from hashlib import sha256
from collections import defaultdict
import json,re,zipfile,xml.etree.ElementTree as E,numpy as np,trimesh as tm
OUT=Path(__file__).resolve().parents[1];NS={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}
def meta(n):return {x.get('key'):x.get('value') for x in n.findall('metadata') if x.get('key')}
project=OUT/'S01_22mm_spacers_H2D_04mm_PLA.3mf';sliced=OUT/'validation/S01_spacer_slice_verification.gcode.3mf'
src=tm.load_mesh(OUT/'source-mm/S01_spring_spacer_22mm.stl')
with zipfile.ZipFile(project) as z:
 assert z.testzip() is None and not any(n.endswith('.gcode') for n in z.namelist())
 c=json.loads(z.read('Metadata/project_settings.config'));assert c['printer_model']=='Bambu Lab H2D' and c['nozzle_diameter']==['0.4','0.4'] and c['filament_type']==['PLA']
 assert c['layer_height']=='0.2' and c['wall_loops']=='4' and c['sparse_infill_density']=='100%' and c['sparse_infill_pattern']=='zig-zag' and c['enable_support']=='0'
 stats=E.fromstring(z.read('Metadata/model_settings.config'));assert len(stats.findall('plate'))==1 and len(stats.find('plate').findall('model_instance'))==2
 obj=stats.find('object');assert meta(obj)['enable_support']=='0' and meta(obj)['sparse_infill_density']=='100%'
 model=E.fromstring(z.read('3D/3dmodel.model'));assert len(model.findall('m:build/m:item',NS))==2
 meshfile=next(n for n in z.namelist() if n.startswith('3D/Objects/') and n.endswith('.model'));d=E.fromstring(z.read(meshfile));mesh=d.find('m:resources/m:object/m:mesh',NS)
 v=np.array([[float(x.get(k)) for k in ['x','y','z']] for x in mesh.findall('m:vertices/m:vertex',NS)]);f=np.array([[int(x.get(k)) for k in ['v1','v2','v3']] for x in mesh.findall('m:triangles/m:triangle',NS)])
 assert np.array_equal(f,src.faces) and np.allclose(v-v.min(0),src.vertices-src.bounds[0],rtol=0,atol=.00001)
 macro=json.loads((OUT/'profiles/profile-manifest.json').read_text())
 for k,h in macro['machine_macro_hashes'].items():assert sha256(json.dumps(c[k],sort_keys=True).encode()).hexdigest()==h
with zipfile.ZipFile(sliced) as z:
 assert z.testzip() is None;p=E.fromstring(z.read('Metadata/slice_info.config')).find('plate');pm=meta(p)
 objects=p.findall('object');labels={o.get('identify_id') for o in objects};assert len(labels)==2 and all(o.get('skipped')=='false' for o in objects)
 assert pm['outside']=='false' and pm['support_used']=='false' and all(x.get('type')=='PLA' for x in p.findall('filament'))
 g=z.read('Metadata/plate_1.gcode').decode();current=None;zheight=0;feature='';paths=defaultdict(list);features=defaultdict(lambda:defaultdict(int))
 for line in g.splitlines():
  m=re.match(r'; start printing object, unique label id: (\d+)',line)
  if m:current=m[1]
  if line.startswith('; stop printing object'):current=None
  if line.startswith('; FEATURE:'):feature=line.split(':',1)[1].strip()
  if line.startswith(('G0 ','G1 ')):
   zm=re.search(r'\bZ(-?[\d.]+)',line)
   if zm:zheight=float(zm[1])
   em=re.search(r'\bE(-?[\d.]+)',line)
   if current in labels and em and float(em[1])>0 and re.search(r'\b[XY]-?[\d.]',line):paths[current].append(zheight);features[current][feature]+=1
 for label in labels:
  assert len(paths[label])>100 and abs(min(paths[label])-.2)<.001 and abs(max(paths[label])-24)<.001
  assert features[label]['Internal solid infill']>0
 report={'status':'SOURCE_IMPORT_AND_CURSORY_SLICE_PASS','scope':'Two exact full-scale source instances, saved profiles and actual model paths; no physical strength/creep qualification','project_sha256':sha256(project.read_bytes()).hexdigest(),'source_sha256':sha256((OUT/'source-mm/S01_spring_spacer_22mm.stl').read_bytes()).hexdigest(),'slice_sha256':sha256(sliced.read_bytes()).hexdigest(),'CLI_import_exit_code':0,'CLI_slice_exit_code':0,'pieces':2,'scale':1,'layer_height_mm':.2,'walls':4,'infill_percent':100,'supports_used':False,'actual_paths':{label:{'positive_segments':len(paths[label]),'minZ_mm':min(paths[label]),'maxZ_mm':max(paths[label]),'features':features[label]} for label in labels},'stock_machine_macros_preserved':True,'estimated_seconds':int(pm['prediction']),'estimated_grams':float(pm['weight']),'no_printer_transmission':True,'slicer':'Official Bambu Studio02.08.02.61','infill_enum_source':'https://github.com/bambulab/BambuStudio/blob/v02.08.02.61/src/libslic3r/PrintConfig.cpp'}
(OUT/'validation/slice-check.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['status','project_sha256','estimated_seconds','estimated_grams','pieces']},indent=2))
