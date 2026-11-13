from pathlib import Path
import ast,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
HERE=Path(__file__).resolve().parents[1];ROOT=HERE.parents[1];PACK=ROOT/'print/bambu-R15-inboard-straps-2026-11-08';OUT=PACK/'validation'
validator=PACK/'source/validate_project.py';tree=ast.parse(validator.read_text());fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='inspect')
NS={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'};PN='{http://schemas.microsoft.com/3dmanufacturing/production/2015/06}';meta=lambda e:{m.get('key'):m.get('value') for m in e.findall('metadata') if m.get('key')}
exec(compile(ast.Module(body=[fn],type_ignores=[]),str(validator),'exec'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
baseline=PACK/'Fingerworker_R15_H2D_04mm_PLA_Inboard_Straps.3mf';ready=PACK/'Fingerworker_R15_H2D_04mm_PLA_Basic_Print_Ready.3mf';sliced=OUT/'Fingerworker_R15_H2D_04mm_PLA_Basic_Print_Ready_verification.gcode.3mf'
a,ca,sa,ua=inspect(baseline);b,cb,sb,ub=inspect(ready);checks=[];changes={};modifier_metadata_changes=[]
def check(name,ok,**data):checks.append(dict(name=name,passed=bool(ok),**data))
def equivalent(a,b):
 if a==b:return True
 x=a if isinstance(a,list) else str(a).split(',');y=b if isinstance(b,list) else str(b).split(',')
 return len(set(map(str,x+y)))==1
check('baseline immutable generic project',sha(baseline)=='860843b3df9f988d67db68bae78e30dd8f2d7fc0fbe8e4c810ef78087e17eaa1')
check('ready project exact UI save',sha(ready)=='b8eeb41a267ef7808fde1a6ee5a036eed1ef9a24f7610044177396576bca23d7')
check('single six-object millimeter plate',len(cb.findall('plate'))==1 and len(cb.findall('plate/model_instance'))==6 and ua==ub=='millimeter' and set(a)==set(b)=={'P01','P04','P05','P06','P11','Q01'})
check('by layer sequence retained',meta(ca.find('plate'))['print_sequence']==meta(cb.find('plate'))['print_sequence']=='by layer')
for ref in a:
 x,y=a[ref],b[ref];check(ref+' one mesh',len(x['parts'])==len(y['parts'])==1)
 check(ref+' exact vertices and faces',all(np.array_equal(p[0],q[0]) and np.array_equal(p[1],q[1]) for p,q in zip(x['parts'],y['parts'])))
 check(ref+' exact component transforms',all(p[2]==q[2] for p,q in zip(x['parts'],y['parts'])))
 check(ref+' exact plate placement',x['transform']==y['transform'])
 check(ref+' remains printable',y['printable']=='1')
 differences={k:{'generic':x['settings'].get(k),'ready':y['settings'].get(k)} for k in x['settings'].keys()|y['settings'].keys() if not equivalent(x['settings'].get(k),y['settings'].get(k))}
 changes[ref]=differences
 check(ref+' exact object process settings',not differences,changes=differences)
 check(ref+' no brim',y['settings'].get('brim_type')=='no_brim' and equivalent(y['settings'].get('brim_width'),'0'))
 xm,ym=x['modifiers'],y['modifiers'];check(ref+' same modifier count',len(xm)==len(ym)==(4 if ref=='P01' else 0))
 for i,(p,q) in enumerate(zip(xm,ym)):
  pt=np.asarray(list(map(float,p['transform'].split())));qt=np.asarray(list(map(float,q['transform'].split())))
  pw=p['vertices']@pt[:9].reshape(3,3)+pt[9:];qw=q['vertices']@qt[:9].reshape(3,3)+qt[9:]
  check(ref+' modifier '+str(i)+' effective geometry and placement within export precision',np.allclose(pw,qw,atol=1e-5,rtol=0) and np.array_equal(p['faces'],q['faces']),max_coordinate_difference_mm=float(np.max(np.abs(pw-qw))))
  ps={k:v for k,v in p['settings'].items() if k!='matrix'};qs={k:v for k,v in q['settings'].items() if k!='matrix'}
  check(ref+' modifier '+str(i)+' exact effective density settings',ps==qs and qs['sparse_infill_density']=='100%' and qs['sparse_infill_pattern']=='zig-zag')
  modifier_metadata_changes.append(dict(name=q['settings']['name'],generic_source_matrix=p['settings'].get('matrix'),ready_source_matrix=q['settings'].get('matrix'),interpretation='Source-file matrix metadata is rewritten on GUI save. Operational component transform and transformed mesh are independently checked; actual dense extrusion cores require the separate connected toolpath audit.'))
protected=['layer_height','initial_layer_print_height','wall_loops','top_shell_layers','bottom_shell_layers','top_shell_thickness','sparse_infill_density','sparse_infill_pattern','enable_arc_fitting','default_acceleration','inner_wall_acceleration','outer_wall_acceleration','top_surface_acceleration','outer_wall_speed','inner_wall_speed','top_surface_speed','sparse_infill_speed','bridge_speed','support_speed','support_interface_speed','support_type','support_style','support_top_z_distance','support_bottom_z_distance','support_on_build_plate_only','brim_type','brim_width','machine_start_gcode','machine_end_gcode','change_filament_gcode','nozzle_diameter','nozzle_type','printer_model','curr_bed_type','printable_area','printable_height','support_filament','support_interface_filament']
for k in protected:check('global protected '+k,equivalent(sa.get(k),sb.get(k)))
check('active project material is PLA Basic',sb['filament_type'][0]=='PLA' and 'PLA Basic' in sb['filament_settings_id'][0])
check('all six objects assigned first material',all(x['settings'].get('extruder','1')=='1' for x in b.values()))
check('global support uses object filament',str(sb['support_filament'])=='0' and str(sb['support_interface_filament'])=='0')
failed=[c for c in checks if not c['passed']]
report=dict(status='PASS_CONNECTED_GEOMETRY_AND_SETTINGS' if not failed else 'FAIL',checks=checks,failed_checks=len(failed),failures=failed,source_sha256=read(HERE/'onshape-version.json')['source_sha256'],baseline_project_sha256=sha(baseline),connected_project_sha256=sha(ready),connected_sliced_archive_sha256=sha(sliced),validator_sha256=sha(Path(__file__)),extracted_inspector_sha256=sha(validator),object_changed_values=changes,modifier_source_metadata_changes=modifier_metadata_changes,global_changed_keys=sorted(k for k in sa.keys()|sb.keys() if sa.get(k)!=sb.get(k)),used_material_settings={k:sb[k][0] for k in ['filament_type','filament_settings_id','filament_max_volumetric_speed','filament_flow_ratio','filament_density','nozzle_temperature','nozzle_temperature_initial_layer']},scope='Exact six saved printable meshes/topology and placements, four effective density modifiers within1e-5mm export precision and all object overrides compared to validated generic project. Protected global geometry/speed/support/machine values retained. Material inventory/profiles intentionally changed by connected AMS sync; active material1 is PLA Basic. Actual extrusion paths and tool usage audited separately.')
(OUT/'connected-geometry-settings-check.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status=report['status'],checks=len(checks),failures=failed,object_changes=changes),indent=2));raise SystemExit(bool(failed))
