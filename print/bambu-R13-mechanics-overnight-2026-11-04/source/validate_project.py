"""Audit selected native geometry, print settings, and complete six-object slice."""
from pathlib import Path
from hashlib import sha256
import json,zipfile,xml.etree.ElementTree as E
import numpy as np
OUT=Path(__file__).resolve().parents[1];ROOT=OUT.parents[1]
layout=json.loads((OUT/'plate-layout.json').read_text())
native=OUT/layout['native_project'];baseline=ROOT/layout['baseline_project']
sliced=OUT/'validation'/(native.stem+'_verification.gcode.3mf')
NS={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'};PN='{http://schemas.microsoft.com/3dmanufacturing/production/2015/06}'
meta=lambda e:{m.get('key'):m.get('value') for m in e.findall('metadata') if m.get('key')}
sha=lambda p:sha256(p.read_bytes()).hexdigest()
checks={}
def check(key,result):checks[key]=bool(result)
def inspect(p):
 with zipfile.ZipFile(p) as z:
  model=E.fromstring(z.read('3D/3dmodel.model'));cfg=E.fromstring(z.read('Metadata/model_settings.config'));settings=json.loads(z.read('Metadata/project_settings.config'))
  objects={o.get('id'):o for o in cfg.findall('object')};resources={o.get('id'):o for o in model.findall('m:resources/m:object',NS)};data={}
  for item in model.findall('m:build/m:item',NS):
   o=objects[item.get('objectid')];key=meta(o)['name'].split(' - ')[0];parts=[]
   for c in resources[item.get('objectid')].findall('m:components/m:component',NS):
    sub=E.fromstring(z.read(c.get(PN+'path').lstrip('/')));mesh=sub.find('m:resources/m:object/m:mesh',NS)
    vertices=np.array([[float(v.get(a)) for a in ('x','y','z')] for v in mesh.findall('m:vertices/m:vertex',NS)])
    faces=np.array([[int(t.get(a)) for a in ('v1','v2','v3')] for t in mesh.findall('m:triangles/m:triangle',NS)])
    parts.append((vertices,faces,c.get('transform')))
   data[key]={'parts':parts,'transform':[float(v) for v in item.get('transform').split()],'settings':meta(o),'object':o,'printable':item.get('printable')}
  return data,cfg,settings,model.get('unit')
old,_,oldsettings,_=inspect(baseline);new,cfg,settings,unit=inspect(native)
check('exact_selected_refs',set(new)=={'P01','P04','P05','P06','P11','Q01'})
check('millimeter_units',unit=='millimeter')
check('one_plate',len(cfg.findall('plate'))==1)
check('six_instances',len(cfg.findall('plate/model_instance'))==6)
check('by_layer',meta(cfg.find('plate'))['print_sequence']=='by layer')
for ref,now in new.items():
 prior=old[ref]
 check(ref+'_mesh_count',len(now['parts'])==len(prior['parts'])==1)
 for index,(a,b) in enumerate(zip(now['parts'],prior['parts'])):
  check(ref+'_exact_vertices',np.array_equal(a[0],b[0]));check(ref+'_exact_triangles',np.array_equal(a[1],b[1]));check(ref+'_component_transform',a[2]==b[2])
 check(ref+'_build_transform',np.allclose(now['transform'],prior['transform'],atol=1e-6,rtol=0))
 check(ref+'_printable',now['printable']=='1')
 check(ref+'_no_mesh_repairs',all(all(int(s.get(k,'0'))==0 for k in ('edges_fixed','degenerate_facets','facets_removed','facets_reversed','backwards_edges')) for s in now['object'].findall('part/mesh_stat')))
 for k,v in layout['object_settings'][ref].items():
  actual=now['settings'].get(k)
  check(ref+'_setting_'+k,actual is not None and all(a==v for a in actual.split(',')))
 for k,v in prior['settings'].items():
  if k in layout['object_settings'][ref]:continue
  check(ref+'_retained_'+k,now['settings'].get(k)==v)
 r=next(r for r in layout['placements'] if r['ref']==ref)
 check(ref+'_source_hash',sha(ROOT/r['source_path'])==r['source_sha256'])
for k,v in {'layer_height':'0.2','wall_loops':'4','top_shell_layers':'5','bottom_shell_layers':'5','top_shell_thickness':'1','sparse_infill_density':'20%','enable_arc_fitting':'0'}.items():check('global_'+k,str(settings.get(k))==v)
for k,v in layout['profile_changes'].items():
 actual=settings.get(k);vals=actual if isinstance(actual,list) else str(actual).split(',')
 check('profile_'+k,all(str(a)==str(v) for a in vals))
for k in ('filament_max_volumetric_speed','nozzle_temperature','nozzle_temperature_initial_layer','machine_start_gcode','machine_end_gcode','change_filament_gcode','nozzle_diameter','printable_area','printable_height'):
 check('retained_'+k,settings.get(k)==oldsettings.get(k))
with zipfile.ZipFile(sliced) as z:
 info=E.fromstring(z.read('Metadata/slice_info.config'));plate=info.find('plate');sm=meta(plate)
 check('one_complete_slice',len(info.findall('plate'))==1 and sm.get('outside')=='false')
 check('six_sliced_objects',len(plate.findall('object'))==6 and {o.get('name').split(' - ')[0] for o in plate.findall('object')}==set(new) and all(o.get('skipped')=='false' for o in plate.findall('object')))
 check('PLA_only',all(f.get('type')=='PLA' for f in plate.findall('filament')))
 check('no_pauses',sm.get('pause_count')=='0')
 for name in z.namelist():
  if name.startswith('Metadata/') and name.endswith('.png'):(OUT/'preview'/Path(name).name).write_bytes(z.read(name))
 prediction=int(sm['prediction']);grams=float(sm['weight'])
failed=[k for k,v in checks.items() if not v]
report={'status':'PASS_NATIVE_MECHANICS_OVERNIGHT' if not failed else 'FAIL','plate_count':1,'object_count':6,'native_project_sha256':sha(native),'sliced_project_sha256':sha(sliced),'geometry_and_orientations_preserved':all(v for k,v in checks.items() if any(t in k for t in ('exact_vertices','exact_triangles','transform'))),'all_checks_passed':not failed,'checks':checks,'failures':failed,'estimate_seconds':prediction,'filament_g':grams,'profile_changes':layout['profile_changes'],'scope':'Exact retained native meshes and placements, declared settings and complete local slice. Physical quality/strength and finish time are not guaranteed; no printer transmission.'}
(OUT/'validation/native-project-check.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'status':report['status'],'checks':len(checks),'failures':failed,'seconds':prediction,'grams':grams}))
raise SystemExit(bool(failed))
