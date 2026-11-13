#!/usr/bin/env python3
"""Independent declared-profile review; actual toolpaths retain their separate QA."""
from pathlib import Path
from hashlib import sha256
import argparse,datetime,json,zipfile,xml.etree.ElementTree as E
OUT=Path(__file__).resolve().parents[1];ROOT=OUT.parents[1]
sha=lambda p:sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text())
def inspect(path):
 with zipfile.ZipFile(path) as z:
  cfg=json.loads(z.read('Metadata/project_settings.config'))
  xml=E.fromstring(z.read('Metadata/model_settings.config'));objects={};modifiers=[]
  for ob in xml.findall('object'):
   d={m.get('key'):m.get('value') for m in ob.findall('metadata') if m.get('key')}
   ref=d['name'].split(' - ')[0];objects[ref]=d
   for part in ob.findall('part'):
    if part.get('subtype')=='modifier_part':
     modifiers.append(dict(owner=ref,id=part.get('id'),settings={m.get('key'):m.get('value') for m in part.findall('metadata')}))
  return cfg,objects,modifiers

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--layout',default='plate-layout.json');ap.add_argument('--candidate',action='store_true');a=ap.parse_args()
 layout=read(OUT/a.layout);project=OUT/layout['native_project'];baseline=ROOT/layout['baseline_project']
 cfg,objects,modifiers=inspect(project);old,oldobjects,oldmodifiers=inspect(baseline);checks=[]
 def check(name,ok,**e):checks.append({'name':name,'status':'PASS' if ok else 'FAIL',**e})
 def equal(value,expected):
  values=value if isinstance(value,list) else str(value).split(',')
  return all(str(x)==str(expected) for x in values)
 check('Baseline is the frozen R13 mechanical print profile retained through R14',sha(baseline)=='6c8d3d766ea78e08310d741d8104fa17f4d0a7ba163688030f10340c743fabe2')
 differences={k:{'R13_profile':old.get(k),'R15':cfg.get(k)} for k in set(cfg)|set(old) if cfg.get(k)!=old.get(k)}
 check('Native global profile differs only in display name',set(differences)=={'print_settings_id'},differences=differences)
 check('Exported project settings exactly match native embedded settings',read(OUT/'profiles/project_settings_H2D.json')==cfg)
 pm=read(OUT/'profiles/profile-manifest.json')
 check('Every exported profile matches regenerated manifest',all(sha(OUT/'profiles'/n)==h for n,h in pm['output_profiles'].items()),output_profiles=pm['output_profiles'])
 expected={'layer_height':'0.2','wall_loops':'4','top_shell_layers':'5','bottom_shell_layers':'5','top_shell_thickness':'1','sparse_infill_density':'20%','sparse_infill_pattern':'gyroid','enable_arc_fitting':'0','filament_max_volumetric_speed':'12','default_acceleration':'6000','inner_wall_acceleration':'6000','outer_wall_acceleration':'1500','top_surface_acceleration':'1500'}
 check('Declared global layers, walls, infill, flow and acceleration',all(equal(cfg[k],v) for k,v in expected.items()),expected=expected,actual={k:cfg[k] for k in expected})
 macros=['machine_start_gcode','machine_end_gcode','change_filament_gcode','time_lapse_gcode','wrapping_detection_gcode','layer_change_gcode','machine_pause_gcode']
 check('Official H2D macro strings preserved exactly',all(cfg.get(k)==old.get(k) for k in macros))
 check('Temperature, nozzle and bed settings retained',all(cfg.get(k)==old.get(k) for k in ['nozzle_temperature','nozzle_temperature_initial_layer','nozzle_diameter','curr_bed_type','printable_area','printable_height']))
 check('Only intended six printable parts',set(objects)=={'P01','P04','P05','P06','P11','Q01'},refs=sorted(objects))
 check('All six model brims explicitly disabled',all(equal(ob.get('brim_width'),'0') and ob.get('brim_type')=='no_brim' for ob in objects.values()))
 declared=layout.get('local_density_modifiers',[])
 check('Four local solid strap-eye modifiers belong only to P01',layout.get('modifier_count')==4 and len(modifiers)==4 and len(declared)==4 and all(m['owner']=='P01' and m['settings'].get('sparse_infill_density')=='100%' and m['settings'].get('sparse_infill_pattern')=='zig-zag' and set(m['settings'])=={'name','matrix','sparse_infill_density','sparse_infill_pattern'} for m in modifiers),modifiers=modifiers)
 check('Local solid masks match declared names and density',sorted(m['settings']['name'] for m in modifiers)==sorted(m['name'] for m in declared) and all(m['sparse_infill_density']=='100%' and m['sparse_infill_pattern']=='zig-zag' for m in declared),declared_modifiers=declared)
 check('Local solid masks retain approved inboard bounds',sorted(str(m['native_bounds_mm']) for m in declared)==sorted(str([[x-18.5,-66 if sign<0 else 52,-2],[x+18.5,-52 if sign<0 else 66,4]]) for x in (28,65) for sign in (-1,1)))
 overrides={ref:{k:v for k,v in ob.items() if 'acceleration' in k} for ref,ob in objects.items()}
 check('No ignored object acceleration overrides present',all(not x for x in overrides.values()),per_object=overrides)
 for ref in objects:
  changes={k:(oldobjects[ref].get(k),objects[ref].get(k)) for k in set(oldobjects[ref])|set(objects[ref]) if objects[ref].get(k)!=oldobjects[ref].get(k)}
  allowed={'brim_width','brim_type'} | ({'name'} if ref=='P01' else set())
  check(ref+' retained object profile except declared brim removal and P01 label',set(changes)<=allowed,differences=changes)
 p04={'outer_wall_speed':'60','top_surface_speed':'40','support_speed':'60','support_type':'tree(auto)','support_style':'tree_slim','support_on_build_plate_only':'1','support_top_z_distance':'0.25','brim_width':'0'}
 check('P04 retains protected surfaces and removable bed tree supports',all(equal(objects['P04'][k],v) for k,v in p04.items()),expected=p04)
 p06={'outer_wall_speed':'60','inner_wall_speed':'100','top_surface_speed':'40','enable_support':'0','brim_width':'0'}
 check('P06 retains protected click-arm speeds and no supports',all(equal(objects['P06'][k],v) for k,v in p06.items()),expected=p06)
 check('P11 remains solid at0.1mm and Q01 remains solid',equal(objects['P11']['sparse_infill_density'],'100%') and equal(objects['P11']['layer_height'],'0.1') and equal(objects['Q01']['sparse_infill_density'],'100%'))
 check('P01 support remains accessible from build plate',equal(objects['P01']['enable_support'],'1') and equal(objects['P01']['support_type'],'normal(auto)') and equal(objects['P01']['support_on_build_plate_only'],'1') and equal(objects['P01']['support_top_z_distance'],'0.25'))
 bindings={}
 if not a.candidate:
  for name in ['native-project-check.json','toolpath-check.json','p04-surface-check.json']:
   path=OUT/'validation'/name;d=read(path)
   ok=d['status'].startswith(('PASS','NATIVE_PROJECT')) and not d.get('failures') and not d.get('failed_count',d.get('failed_checks',0))
   check('Current '+name+' completed without failure',ok)
   bindings[name]=sha(path)
   for k in ['native_project_sha256','editable_project_sha256','native_editable_project_sha256']:
    if k in d:check(name+' project hash matches',d[k]==sha(project))
   if 'layout_sha256' in d:check(name+' layout hash matches',d['layout_sha256']==sha(OUT/a.layout))
  sliced=OUT/'validation'/(project.stem+'_verification.gcode.3mf')
  for name in ['native-project-check.json','toolpath-check.json','p04-surface-check.json']:
   d=read(OUT/'validation'/name)
   for k in ['sliced_project_sha256','sliced_internal_evidence_sha256','sliced_archive_sha256']:
    if k in d:check(name+' slice hash matches',d[k]==sha(sliced))
 else:sliced=OUT/'validation'/'candidate-flat'/(project.stem+'_verification.gcode.3mf')
 failed=[c for c in checks if c['status']=='FAIL']
 d={'status':('PASS_CANDIDATE_PROFILE_REVIEW' if a.candidate else 'PASS_INDEPENDENT_PROFILE_REVIEW') if not failed else 'FAIL','revision':'R15','reviewed_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'failed_checks':len(failed),'failures':failed,'checks':checks,'layout_sha256':sha(OUT/a.layout),'CAD_source_sha256':layout['CAD_source_sha256'],'editable_project_sha256':sha(project),'sliced_internal_evidence_sha256':sha(sliced),'baseline_project_sha256':sha(baseline),'validator_sha256':sha(__file__),'profile_manifest_sha256':sha(OUT/'profiles/profile-manifest.json'),'bound_actual_QA_sha256':bindings,'scope':'Independent native profile inspection and exported-profile consistency. Actual extrusion/acceleration/support paths are separately checked in the hash-bound QA reports; this is not a physical surface or strength qualification.','limits':'Per-object speed metadata is not a blanket claim about actual feature speed. All parts use global internal/default6000 and exterior/top1500 acceleration; P11 actual inner speed is assessed in toolpath QA.'}
 target=OUT/'validation'/('candidate-flat' if a.candidate else '')/'independent-profile-review.json';target.parent.mkdir(parents=True,exist_ok=True);target.write_text(json.dumps(d,indent=2)+'\n')
 print(json.dumps({'status':d['status'],'checks':len(checks),'failed':failed},indent=2));return bool(failed)
if __name__=='__main__':raise SystemExit(main())
