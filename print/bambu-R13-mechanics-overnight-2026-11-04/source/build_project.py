"""Six-piece overnight plate: exact R13 meshes, moderate H2D speed settings."""
from pathlib import Path
from hashlib import sha256
import copy,json,shutil,xml.etree.ElementTree as E,zipfile
OUT=Path(__file__).resolve().parents[1]; ROOT=OUT.parents[1]
OLD=ROOT/'print/bambu-R13-one-plate-2026-11-04'
BASE='Fingerworker_R13_H2D_04mm_PLA_Mechanics_Overnight'
KEEP={'P01','P04','P05','P06','P11','Q01'}
NS={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}
E.register_namespace('',NS['m']);E.register_namespace('p','http://schemas.microsoft.com/3dmanufacturing/production/2015/06')
meta=lambda e:{m.get('key'):m.get('value') for m in e.findall('metadata')}
sha=lambda p:sha256(p.read_bytes()).hexdigest()
for folder in ('profiles','source-mm','STL-print-oriented','preview','runtime','validation','evidence'):(OUT/folder).mkdir(parents=True,exist_ok=True)
for p in (OLD/'profiles').iterdir():shutil.copyfile(p,OUT/'profiles'/p.name)
shutil.copyfile(OLD/'source/run_slicer.py',OUT/'source/run_slicer.py')
prior=json.loads((OLD/'plate-layout.json').read_text());layout=copy.deepcopy(prior)
layout['placements']=[r for r in layout['placements'] if r['ref'] in KEEP]
layout['object_settings']={k:v for k,v in layout['object_settings'].items() if k in KEEP}
for r in layout['placements']:
 for folder in ('source-mm','STL-print-oriented'):shutil.copyfile(OLD/folder/(r['ref']+'.stl'),OUT/folder/(r['ref']+'.stl'))
process=json.loads((OUT/'profiles/H2D_process.json').read_text())
changes={'outer_wall_speed':100,'inner_wall_speed':180,'internal_solid_infill_speed':160,'sparse_infill_speed':200,'gap_infill_speed':120,'top_surface_speed':60,'support_speed':100,'default_acceleration':6000,'inner_wall_acceleration':6000,'outer_wall_acceleration':1500,'top_surface_acceleration':1500,'travel_acceleration':8000}
for k,v in changes.items():process[k]=[str(v)]*len(process[k])
process['enable_arc_fitting']='0'
process['sparse_infill_density']='20%'
process['name']=process['print_settings_id']='Fingerworker R13 mechanics overnight 0.20mm'
(OUT/'profiles/H2D_process.json').write_text(json.dumps(process,indent=2)+'\n')
overrides={
 'P04':{'outer_wall_speed':'60','top_surface_speed':'40','support_speed':'60'},
 'P06':{'outer_wall_speed':'60','inner_wall_speed':'100','top_surface_speed':'40'}}
baseline=OLD/prior['native_project']
with zipfile.ZipFile(baseline) as z:
 model=E.fromstring(z.read('3D/3dmodel.model'));config=E.fromstring(z.read('Metadata/model_settings.config'))
 model.set('xmlns:BambuStudio','http://schemas.bambulab.com/package/2021')
 objects={o.get('id'):meta(o)['name'].split(' - ')[0] for o in config.findall('object')}
 keep_ids={i for i,k in objects.items() if k in KEEP}
 for o in list(config.findall('object')):
  key=objects[o.get('id')]
  if key not in KEEP:config.remove(o);continue
  for k,v in overrides.get(key,{}).items():
   node=next((n for n in o.findall('metadata') if n.get('key')==k),None)
   if node is None:node=E.SubElement(o,'metadata',key=k)
   node.set('value',','.join([v]*7));layout['object_settings'][key][k]=v
 build=model.find('m:build',NS)
 for item in list(build):
  if item.get('objectid') not in keep_ids:build.remove(item)
 for plate in config.findall('plate'):
  for item in list(plate.findall('model_instance')):
   if meta(item)['object_id'] not in keep_ids:plate.remove(item)
  for n in plate.findall('metadata'):
   if n.get('key')=='plater_name':n.set('value','R13 mechanics - 6 pieces - PLA')
 for node in model.findall('m:metadata',NS):
  if node.get('name')=='Title':node.text='Fingerworker R13 mechanical overnight plate'
  if node.get('name')=='Description':node.text='Six unchanged R13 pieces. Electronics housing, lid and printed rods omitted. Moderate H2D speed profile; click and finger surfaces retain slower exterior settings.'
 seed=OUT/(BASE+'_seed.3mf')
 with zipfile.ZipFile(seed,'w',zipfile.ZIP_DEFLATED) as dest:
  for name in z.namelist():
   if name.startswith('Metadata/') and (name.endswith('.png') or name in ('Metadata/slice_info.config','Metadata/filament_sequence.json')):continue
   if name=='3D/3dmodel.model':data=E.tostring(model,encoding='utf-8',xml_declaration=True)
   elif name=='Metadata/model_settings.config':data=E.tostring(config,encoding='utf-8',xml_declaration=True)
   elif name=='Metadata/project_settings.config':
    settings=json.loads(z.read(name));settings.update({k:process[k] for k in [*changes,'sparse_infill_density','enable_arc_fitting','print_settings_id']});data=json.dumps(settings,indent=2).encode()
   else:data=z.read(name)
   dest.writestr(name,data)
layout.update(status='MECHANICS_OVERNIGHT_PENDING_SLICE',object_count=6,native_project=BASE+'.3mf',seed_path=seed.name,seed_sha256=sha(seed),baseline_project=str(baseline.relative_to(ROOT)),baseline_project_sha256=sha(baseline),changes='Removed P08, P09, H040 and H041. Exact mesh geometry, rotations and placements retained. Moderate speed/acceleration changes and20%gyroid; layer heights, four walls and support geometry retained. P11 andQ01 remain solid. Arc fitting disabled for connected printer compatibility.',profile_changes={**changes,'sparse_infill_density':'20%','enable_arc_fitting':'0'},omitted=['P08','P09','H040','H041'],deadline_local='2026-11-05T09:00:00+01:00')
(OUT/'plate-layout.json').write_text(json.dumps(layout,indent=2)+'\n')
print(json.dumps({'objects':len(KEEP),'profile_changes':changes,'project':layout['native_project']}))
