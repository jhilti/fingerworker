"""Check P02-only convenience project against the full project's exact mesh and settings."""
from pathlib import Path
from hashlib import sha256
import json,re,zipfile,xml.etree.ElementTree as E,numpy as np
OUT=Path(__file__).resolve().parents[1];NS={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}
def meta(n):return {m.get('key'):m.get('value') for m in n.findall('metadata') if m.get('key')}
def palm(path):
 with zipfile.ZipFile(path) as z:
  assert z.testzip() is None and not any(n.endswith('.gcode') for n in z.namelist())
  settings=E.fromstring(z.read('Metadata/model_settings.config'));objects=settings.findall('object')
  o=next(o for o in objects if meta(o)['name'].startswith('P02 - '));part=o.find('part');mid=part.get('id')
  v=f=None
  for n in z.namelist():
   if n.startswith('3D/Objects/') and n.endswith('.model'):
    d=E.fromstring(z.read(n))
    for obj in d.findall('m:resources/m:object',NS):
     if obj.get('id')==mid:
      m=obj.find('m:mesh',NS);v=np.array([[float(p.get(k)) for k in ['x','y','z']] for p in m.findall('m:vertices/m:vertex',NS)]);f=np.array([[int(p.get(k)) for k in ['v1','v2','v3']] for p in m.findall('m:triangles/m:triangle',NS)])
  assert v is not None
  return len(objects),v,f,meta(o),json.loads(z.read('Metadata/project_settings.config'))
full=OUT/'Fingerworker_R9_H2D_04mm_PLA_Fit_Test.3mf';single=OUT/'Fingerworker_R9_P02_wrist_down_H2D_04mm_PLA.3mf'
n,a,fa,ma,ca=palm(full);m,b,fb,mb,cb=palm(single);assert n==19 and m==1
assert np.array_equal(fa,fb) and np.allclose(a-a.min(0),b-b.min(0),rtol=0,atol=1e-5)
opts=json.loads((OUT/'plate-layout.json').read_text())['object_settings']['P02']
for k in opts:assert ma[k]==mb[k]
for k in ['printer_model','nozzle_diameter','filament_type','curr_bed_type','wall_loops','sparse_infill_density','print_sequence']:assert ca[k]==cb[k]
assert cb['filament_type']==['PLA']
sliced=OUT/'validation/Fingerworker_R9_P02_wrist_down_H2D_04mm_PLA_verification.gcode.3mf'
with zipfile.ZipFile(sliced) as z:
 assert z.testzip() is None;plate=E.fromstring(z.read('Metadata/slice_info.config')).find('plate');pm=meta(plate)
 assert pm['outside']=='false' and len(plate.findall('object'))==1 and plate.find('object').get('skipped')=='false'
 g=z.read('Metadata/plate_1.gcode').decode();assert 'max_z_height: 36.60' in g
 # Single-object Gcode has no cancel-object labels. Restrict evidence to actual model feature blocks.
 model_types={'Outer wall','Inner wall','Sparse infill','Internal solid infill','Top surface','Bottom surface','Bridge','Overhang wall','Gap infill'}
 zheight=0.;feature='';heights=[];segments=0
 for line in g.splitlines():
  if line.startswith('; FEATURE:'):feature=line.split(':',1)[1].strip()
  if line.startswith(('G0 ','G1 ')):
   zm=re.search(r'\bZ(-?[\d.]+)',line)
   if zm:zheight=float(zm[1])
   em=re.search(r'\bE(-?[\d.]+)',line)
   if em and float(em[1])>0 and feature in model_types and re.search(r'\b[XY]-?[\d.]',line):segments+=1;heights.append(zheight)
 assert segments>1000 and abs(max(heights)-36.6)<.001,(segments,max(heights) if heights else None)
 report={'status':'P02_ONLY_REPRINT_CHECKS_PASS','native_project_sha256':sha256(single.read_bytes()).hexdigest(),'full_project_sha256':sha256(full.read_bytes()).hexdigest(),'slice_sha256':sha256(sliced.read_bytes()).hexdigest(),'mesh_faces_identical_to_full':True,'normalized_vertices_max_error_mm':float(np.max(np.abs((a-a.min(0))-(b-b.min(0))))),'support_settings_identical_to_full':True,'model_positive_segments':segments,'actual_model_max_Z_mm':max(heights),'one_PLA_object_sliced':True,'estimated_seconds':int(pm['prediction']),'estimated_grams':float(pm['weight']),'no_printer_transmission':True}
(OUT/'validation/palm-only-check.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
