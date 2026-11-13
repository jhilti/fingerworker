"""Audit selected native geometry, print settings, and complete selected-object slice."""
from pathlib import Path
from hashlib import sha256
import json,zipfile,xml.etree.ElementTree as E
import numpy as np
import trimesh
from print_context import OUT,ROOT,LAYOUT,LAYOUT_PATH,V,PREVIEW,PROJECT,SLICED,REPLACEMENT,CANDIDATE
layout=LAYOUT
native=OUT/layout['native_project'];baseline=ROOT/layout['baseline_project']
sliced=SLICED
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
   o=objects[item.get('objectid')];key=meta(o)['name'].split(' - ')[0];parts=[];modifiers=[];part_metadata={p.get('id'):p for p in o.findall('part')}
   for c in resources[item.get('objectid')].findall('m:components/m:component',NS):
    sub=E.fromstring(z.read(c.get(PN+'path').lstrip('/')))
    # Official export consolidates an object's printable mesh and its modifiers
    # in one resource file; resolve the component's exact resource ID.
    mesh=next(o for o in sub.findall('m:resources/m:object',NS) if o.get('id')==c.get('objectid')).find('m:mesh',NS)
    vertices=np.array([[float(v.get(a)) for a in ('x','y','z')] for v in mesh.findall('m:vertices/m:vertex',NS)])
    faces=np.array([[int(t.get(a)) for a in ('v1','v2','v3')] for t in mesh.findall('m:triangles/m:triangle',NS)])
    part=part_metadata[c.get('objectid')]
    if part.get('subtype')=='normal_part':parts.append((vertices,faces,c.get('transform')))
    else:modifiers.append(dict(vertices=vertices,faces=faces,transform=c.get('transform'),subtype=part.get('subtype'),settings=meta(part)))
   data[key]={'parts':parts,'modifiers':modifiers,'transform':[float(v) for v in item.get('transform').split()],'settings':meta(o),'object':o,'printable':item.get('printable')}
  return data,cfg,settings,model.get('unit')
old,_,oldsettings,_=inspect(baseline);new,cfg,settings,unit=inspect(native)
check('exact_selected_refs',set(new)=={r['ref'] for r in layout['placements']})
check('millimeter_units',unit=='millimeter')
if REPLACEMENT:check('derived_from_exact_complete_project',sha(OUT/layout['parent_complete_project'])==layout['parent_complete_project_sha256'])
check('slot_region_configuration_hash',sha(ROOT/layout['strap_print_regions_path'])==layout['strap_print_regions_sha256'])
check('current_CAD_source_hash',sha(ROOT/layout['CAD_source_path'])==layout['CAD_source_sha256'])
check('baseline_native_hash',sha(baseline)==layout['baseline_project_sha256'])
for k,v in oldsettings.items():
 if k in ('print_settings_id','different_settings_to_system','inherits_group','filament_map_2','filament_map_mode'):continue
 check('same_process_'+k,settings.get(k)==v)
check('derived_empty_inheritance_metadata',all(not x for k in ('different_settings_to_system','inherits_group') for x in settings.get(k,[])))
check('derived_left_extruder_mapping',settings.get('filament_map_2')==['1'])
check('manual_left_extruder_mapping',settings['filament_map_mode']=='Manual' and settings['filament_map']==['1']*6)
check('plate_manual_left_extruder_mapping',meta(cfg.find('plate'))['filament_map_mode']=='Manual' and meta(cfg.find('plate'))['filament_maps']=='1 1 1 1 1 1')
check('one_plate',len(cfg.findall('plate'))==1)
check('selected_instance_count',len(cfg.findall('plate/model_instance'))==len(new))
check('by_layer',meta(cfg.find('plate'))['print_sequence']=='by layer')
for ref,now in new.items():
 prior=old['P06' if ref in ('P06L','P06R') else ref]
 check(ref+'_mesh_count',len(now['parts'])==len(prior['parts'])==1)
 r=next(r for r in layout['placements'] if r['ref']==ref)
 for index,(a,b) in enumerate(zip(now['parts'],prior['parts'])):
  if ref in layout.get('changed_mesh_refs',['P01']):
   original=trimesh.load(ROOT/r['source_path'],force='mesh',process=False)
   vertices,indices=np.unique(original.vertices,axis=0,return_inverse=True);faces=indices[original.faces]
   if CANDIDATE:faces=faces[np.array([len(set(f))==3 for f in faces])]
   oriented=vertices@np.asarray(r['rotation_3x3']).T;expected=oriented-(oriented.min(0)+oriented.max(0))/2
   check(ref+'_exact_source_vertices_to_float_precision',a[0].shape==expected.shape and np.allclose(a[0],expected,atol=1e-5,rtol=0))
   check(ref+'_exact_triangles',np.array_equal(a[1],faces))
  else:check(ref+'_exact_vertices',np.array_equal(a[0],b[0]));check(ref+'_exact_triangles',np.array_equal(a[1],b[1]))
  check(ref+'_component_transform',a[2]==b[2])
 expected_transform=[1,0,0,0,1,0,0,0,1,*[r['plate_xy_mm'][i]+r['size_oriented_mm'][i]/2 for i in range(2)],r['size_oriented_mm'][2]/2] if ref in layout.get('changed_mesh_refs',['P01']) else prior['transform']
 check(ref+'_build_transform',np.allclose(now['transform'],expected_transform,atol=1e-5,rtol=0))
 check(ref+'_printable',now['printable']=='1')
 check(ref+'_no_mesh_repairs',all(all(int(s.get(k,'0'))==0 for k in ('edges_fixed','degenerate_facets','facets_removed','facets_reversed','backwards_edges')) for s in now['object'].findall('part/mesh_stat')))
 for k,v in layout['object_settings'][ref].items():
  actual=now['settings'].get(k)
  check(ref+'_setting_'+k,actual is not None and all(a==v for a in actual.split(',')))
 for k,v in prior['settings'].items():
  if k in layout['object_settings'][ref] or (ref in layout.get('changed_mesh_refs',['P01']) and k=='name'):continue
  check(ref+'_retained_'+k,now['settings'].get(k)==v)
 r=next(r for r in layout['placements'] if r['ref']==ref)
 check(ref+'_source_hash',sha(ROOT/r['source_path'])==r['source_sha256'])
check('four_local_density_modifiers',len(new['P01']['modifiers'])==layout['modifier_count']==4 and all(not v['modifiers'] for k,v in new.items() if k!='P01'))
for mod in new['P01']['modifiers']:
 name=mod['settings']['name'];expected=next((v for v in layout['local_density_modifiers'] if v['name']==name),None)
 check('modifier_declared_'+name,expected is not None and mod['subtype']=='modifier_part')
 check('modifier_density_'+name,mod['settings'].get('sparse_infill_density')=='100%')
 check('modifier_pattern_'+name,mod['settings'].get('sparse_infill_pattern')=='zig-zag')
 if expected:
  transform=np.asarray([float(v) for v in mod['transform'].split()]);build=np.asarray(new['P01']['transform']);row=next(r for r in layout['placements'] if r['ref']=='P01')
  points=(mod['vertices']@transform[:9].reshape(3,3)+transform[9:])@build[:9].reshape(3,3)+build[9:]
  points-=np.asarray(row['normalization_translation_mm'])+[*row['plate_xy_mm'],0]
  check('modifier_native_bounds_'+name,np.allclose([points.min(0),points.max(0)],expected['native_bounds_mm'],atol=1e-5,rtol=0))
  check('modifier_closed_cube_'+name,len(mod['vertices'])==8 and len(mod['faces'])==12)
for k,v in {'layer_height':'0.2','wall_loops':'4','top_shell_layers':'5','bottom_shell_layers':'5','top_shell_thickness':'1','sparse_infill_density':'20%','enable_arc_fitting':'0'}.items():check('global_'+k,str(settings.get(k))==v)
for k,v in layout['profile_changes'].items():
 actual=settings.get(k);vals=actual if isinstance(actual,list) else str(actual).split(',')
 check('profile_'+k,all(str(a)==str(v) for a in vals))
for k in ('filament_max_volumetric_speed','nozzle_temperature','nozzle_temperature_initial_layer','machine_start_gcode','machine_end_gcode','change_filament_gcode','nozzle_diameter','printable_area','printable_height'):
 check('retained_'+k,settings.get(k)==oldsettings.get(k))
with zipfile.ZipFile(sliced) as z:
 info=E.fromstring(z.read('Metadata/slice_info.config'));plate=info.find('plate');sm=meta(plate)
 check('one_complete_slice',len(info.findall('plate'))==1 and sm.get('outside')=='false')
 check('selected_sliced_objects',len(plate.findall('object'))==len(new) and {o.get('name').split(' - ')[0] for o in plate.findall('object')}==set(new) and all(o.get('skipped')=='false' for o in plate.findall('object')))
 check('PLA_only',all(f.get('type')=='PLA' for f in plate.findall('filament')))
 check('actual_slice_left_extruder_mapping',sm.get('filament_maps')=='1 1 1 1 1 1')
 check('no_pauses',sm.get('pause_count')=='0')
 for name in z.namelist():
  if name.startswith('Metadata/') and name.endswith('.png'):(PREVIEW/Path(name).name).write_bytes(z.read(name))
 (V/'plate-preview-provenance.json').write_text(json.dumps(dict(status='EXTRACTED_ACTUAL_R19_SLICED_PLATE_PREVIEW',sliced_archive_sha256=sha(sliced),layout_sha256=sha(LAYOUT_PATH),image_sha256=sha(PREVIEW/'plate_1.png'),image_archive_member='Metadata/plate_1.png',validator_sha256=sha(Path(__file__))),indent=2)+'\n')
 prediction=int(sm['prediction']);grams=float(sm['weight'])
failed=[k for k,v in checks.items() if not v]
report={'status':('PASS_LOCAL_R19_PRINT_CANDIDATE' if CANDIDATE else 'PASS_NATIVE_R19_THUMB_RIM') if not failed else 'FAIL','candidate':CANDIDATE,'plate_count':1,'object_count':len(new),'modifier_count':4,'native_project_sha256':sha(native),'sliced_project_sha256':sha(sliced),'geometry_and_orientations_preserved':all(v for k,v in checks.items() if any(t in k for t in ('exact_vertices','exact_source_vertices','exact_triangles','transform'))),'all_checks_passed':not failed,'checks':checks,'failures':failed,'estimate_seconds':prediction,'filament_g':grams,'profile_changes':layout['profile_changes'],'CAD_source_sha256':layout['CAD_source_sha256'],'native_R19_version':layout['native_R19_version'],'layout_sha256':sha(LAYOUT_PATH),'validator_sha256':sha(Path(__file__)),'scope':('LOCAL CANDIDATE only; no Onshape export identity claim. ' if CANDIDATE else 'Native Onshape source. ')+'Every changed selected mesh (P01/P06L/P06R) matches its declared native source STL to1e-5mm floating-point precision; face topology preserved (candidate only omits declared repeated-index zero-area facets). Retained meshes and all declared rigid placements unchanged. Declared settings including no_brim on every selected object and complete local slice checked. Physical quality/strength not qualified; no printer transmission.'}
(V/'native-project-check.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'status':report['status'],'checks':len(checks),'failures':failed,'seconds':prediction,'grams':grams}))
raise SystemExit(bool(failed))
