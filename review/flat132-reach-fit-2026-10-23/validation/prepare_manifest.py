#!/usr/bin/env python3
"""Bind R5 native exports to explicit u/p/trim and106-part validation intent."""
import argparse,json,copy
from pathlib import Path
import validate_finished as v
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--neutral',type=Path,required=True);p.add_argument('--step',type=Path,required=True)
p.add_argument('--source',type=Path,default=v.HERE.parent/'fingerworker_flat132_reach_fit.fs')
p.add_argument('--workspace',required=True)
p.add_argument('--native-pose',nargs=5,action='append',metavar=('MODE','USER_U','PRELOAD','TRIM','ZIP'),default=[])
p.add_argument('--output',type=Path,default=v.HERE/'manifest.json')
a=p.parse_args()
base=v.ROOT/'review/flat132-switch-fit-2026-10-23'
m=json.loads((base/'validation/manifest.json').read_text())
m.update(status='ACTUAL_NATIVE_R5_INPUT_MANIFEST',schema_version=2,assembly=str(a.neutral.resolve()),feature_source=str(a.source.resolve()))
m['native_provenance']={'workspace_url':a.workspace,'feature_source_sha256':v.sha(a.source),'association':'Root operator verified exact native source readback/regeneration; export association remains operator-declared and hash-bound.'}
m['native_provenance']['dynamic_mode_equivalence']={'certificate':str((v.HERE/'dynamic-mode-equivalence.json').resolve()),'certificate_sha256':v.sha(v.HERE/'dynamic-mode-equivalence.json')}
m['native_provenance']['original_dynamic_source_sha256']='61885fd717b30eaf1dfc39a1f7f65f017bfc1b4ac077c3e3493399ef3373a9a3'
m['native_provenance']['association']='Root operator verified exact final ISO81 native source/regeneration. Neutral and dynamic native exports retain their original61885 source association and are reused only through the exact isometricLock=false inverse-source certificate. The new ISO81 export originates from the final source.'
m['expected_device_refs']=sorted(set(m['expected_device_refs'])|{'P11'})
m['motion_overrides']={'H10':[-1.,-1.,1.],'P11':[-1.,-1.,1.]}
m.pop('configuration_domain_vertices_stroke_preload_mm',None)
m['configuration_domain_vertices_user_preload_trim_mm']=[[u,p,e] for u,p in [(0.,0.),(30.,0.),(28.,2.),(0.,2.)] for e in [-.8,.8]]
m['configuration_domain_description']='u>=0,0<=p<=2,u+p<=30,-0.8<=camTrim e<=0.8. Actual carriage offset=5+u; cam shoe/clamp setting=e-p before actual carriage translation. Configuration geometry only, not real switch operating-travel qualification.'
m['actuator_effective_travel_coefficients']=[1.,1.,-1.]
m['continuous_preferred_moving_ref_pairs']=[{'pair':['P11','P04'],'moving_ref':'P11','reason':'The swept shoe hull is contained by its well; relative frame change is exact.'}]
clamp_covers=[dict(type='cylinder_z',x_mm=65.5,y_mm=3.5,start_z_mm=25.,end_z_mm=28.,radius_mm=2.75001),dict(type='cylinder_z',x_mm=65.5,y_mm=3.5,start_z_mm=15.,end_z_mm=25.1,radius_mm=1.50001)]
m['continuous_convex_moving_covers']=[{'pair':['H10','P04'],'moving_ref':'H10','covers':clamp_covers,'reason':'Two outward conservative convex cylinders contain every native clamp triangle and its full solid. Each swept hull is checked; no hull wedge or material erosion.'}]
m['rest_offset_mm']=5.;m['isometric_sleeve_length_mm']=81.;m['isometric_user_stroke_plus_preload_mm']=15.
m['isometric_description']='Selected81mm sleeves: actual carriage offset20-p, user-relative approach15-p. Isometric grip is5mm closer than R4, matching the dynamic grip shift.'
m['sensor']['native_assembly_step']=str(a.step.resolve())
m['native_part_steps']={}
m['native_poses']=[{'mode':mode,'stroke_mm':float(u),'preload_mm':float(p),'trim_mm':float(e),'actual_carriage_offset_mm':5.+float(u),'assembly':str(Path(z).resolve())} for mode,u,p,e,z in a.native_pose]
m['required_native_pose_keys']=['dynamic:28:2:0','isometric:13:2:0','dynamic:28:2:-0.8','dynamic:30:0:0.8']
m['baseline_native_comparison']={
 'assembly':str((base/'native/Flat132_R4_neutral_final.zip').resolve()),'assembly_sha256':v.sha(base/'native/Flat132_R4_neutral_final.zip'),
 'only_changed_refs':['P01','P04','P05','P060','P061','H10','H030','H031'],
 'added_refs':['P11'],'removed_refs':[],
 'new_to_baseline_rigid_translation_mm':{r:[5.,0.,0.] for r in ['H060','H061','P070a','P070b','P071a','P071b']},
 'permitted_triangle_order_only_refs':'ALL_EXCEPT_EXPECTED_GEOMETRY_CHANGES','exact_step_preserved_float32_box_refs':['P070a','P070b','P071a','P071b'],'require_each_expected_change':True,
 'meaning':'Only rail-extension P01,shoe-well P04,shortened-stop P05,return-boss retainers P060/P061,vertical H10 and indicative coils may change existing geometry; P11 is the only added body. Six unchanged seats/pads may move exactly-5X. All other bodies retain exact native triangle coordinates; no rounding or arbitrary registration.'}
for c in m['contacts']:
 if set(c['pair'])=={'H09a','H09b'}:
  c['kind']='drawing_reference_actuator_internal_joint';c['reason']='Unchanged illustrative fixed-length lever cylinder terminates at roller axle. Bound pi*.45²*2.4=1.52682mm3 is confined to this source-preview joint, not an actual factory mechanism or general clearance waiver.'
# Retain reviewed R4 dimensions/probes except the replaced horizontal cam.
drop=['Recessed cam head face X neutral','M3x8 cam shaft end X neutral','Removed old projecting P04 cam nub','Cam head recess nominal diameter','Intact guide web below head recess','Cam insert pilot nominal diameter']
m['dimension_checks']=[x for x in m['dimension_checks'] if x['name'] not in drop]
for d in m['dimension_checks']:
 if d['ref']=='P04' and d['type']=='ray_levels':d['origin_mm'][0]-=5.
 if d['name']=='Integral sensing-stop front datum at neutral':d['expected_mm']=30.
 if 'printed sensing stop bearing' in d['name'].lower() and d['type']=='ray_levels':d['origin_mm'][0]=29.
m['material_and_clearance_probes']=[x for x in m['material_and_clearance_probes'] if not x['name'].startswith(('R4 head recess','R4 insert pilot','R4 cam through','R4 guide roof'))]
for b in m['material_and_clearance_probes']:
 if b['name'].startswith('Broad integral printed stop face stock'):b['maximum_mm'][0]=29.99
# New local material probes are kept small and separate from global clearances.
def dim(name,ref,axis,component,expected):return dict(name=name,ref=ref,type='bounds',axis=axis,component=component,expected_mm=expected,tolerance_mm=.02)
def ray(name,ref,origin,direction,axis,indices,expected):return dict(name=name,ref=ref,type='ray_levels',origin_mm=origin,direction=direction,axis=axis,level_indices=indices,expected_mm=expected,tolerance_mm=.025)
def box(name,ref,lo,hi,expect):return dict(name=name,ref=ref,type='box',minimum_mm=lo,maximum_mm=hi,expect=expect)
def cz(name,ref,x,y,z0,z1,r,expect='empty'):return dict(name=name,ref=ref,type='cylinder_z',x_mm=x,y_mm=y,start_z_mm=z0,end_z_mm=z1,radius_mm=r,expect=expect)
m['dimension_checks'] += [
 dim('R5 closer-rest carriage front X','P04',0,'minimum',60.),
 dim('R5 carriage rear plane at closer rest','P04',0,'maximum',119.),
 dim('New stepped shoe front upper boss X at neutral','P11',0,'minimum',62.5),
 dim('New shoe rear plane at neutral','P11',0,'maximum',68.5),
 dim('New shoe body height','P11',2,'extent',10.),
 dim('Vertical M3x10 complete envelope height','H10',2,'extent',13.),
 dim('Vertical clamp head top below grip lip','H10',2,'maximum',28.),
 dim('Vertical clamp axis X neutral','H10',0,'center',65.5),
 ray('Intact1.3mm guide roof under new shoe well','P04',[65,0,100],[0,0,-1],2,[1,0],1.3),
 ray('Restored2.2mm rear wall between shoe well and pocket','P04',[100,0,17],[-1,0,0],0,[1,0],2.2),
 ray('Shoe insert front X ligament','P11',[100,3.5,17],[-1,0,0],0,[1,0],.9),
 ray('Shoe insert rear X ligament','P11',[100,3.5,17],[-1,0,0],0,[-1,-2],.9),
 ray('Shoe insert pilot floor stock','P11',[65.5,3.5,100],[0,0,-1],2,[-1,0],5.5),
 ray('Extended guide front datum at Y10/Z5','P01',[-100,10,5],[1,0,0],0,[-2],29.),
 ray('Extended guide total axial length at Y10/Z5','P01',[-100,10,5],[1,0,0],0,[-1,-2],95.)]
m['material_and_clearance_probes'] += [
 box('Retained guide roof under full shoe well','P04',[60.01,-.99,7.31],[69.79,7.99,8.59],'solid'),
 box('Restored rear well wall after removing all old horizontal bores','P04',[69.81,-.5,9],[71.99,7.5,18.9],'solid'),
 box('Stepped shoe forward upper boss stock','P11',[62.51,-.69,13.21],[63.39,7.69,18.99],'solid'),
 box('Stepped shoe lower switch-contact face stock','P11',[64.01,-.69,9.01],[64.19,7.69,12.29],'solid'),
 cz('P11 diameter4.2 blind insert pilot','P11',65.5,3.5,14.501,18.999,2.099),
 cz('Vertical clamp top driver clearance at neutral','P04',65.5,3.5,28.01,35.,1.999),
 box('Added central guide stock before old X34 datum','P01',[29.01,-10,4.01],[33.99,10,6.99],'solid')]
for side in (-1,1):
 ref='P060' if side<0 else 'P061'
 m['dimension_checks'].append(dim('Rigid return extension front '+ref,ref,0,'minimum',120.5))
 for sign in (-1,1):
  y=side*51+sign*7.5
  m['material_and_clearance_probes'].append(box('Rigid return boss stock '+ref+'/'+str(sign),ref,[120.51,y-2.24,14.01],[125.49,y+2.24,19.99],'solid'))
# Existing service prerequisites persist; the new shoe is now also an obstacle.
for svc in m['service_sweeps']:
 if 'fixed_refs' in svc and svc['name'] not in ('Keeper wristward release','Keeper upward removal after wristward release','Removed stack: yoke/pusher axial separation from sensor keeper'):
  svc['fixed_refs']=sorted(set(svc['fixed_refs'])|{'P11'})
all_device=set(m['expected_device_refs'])
without_coils=all_device-v.SPRINGS
m['service_sweeps'] += [
 {'name':'Vertical cam clamp upward removal','moving_refs':['H10'],'fixed_refs':sorted(without_coils-{'H10'}),'direction':[0,0,1],'range_mm':[0,20],
  'moving_convex_cover':{'moving_ref':'H10','covers':clamp_covers},'prerequisites':'Usertravel0/preload0/trim0; restrain/remove spring energy and unscrew H10 completely. Nominal rigid hardware envelope only.'},
 {'name':'Unclamped stepped shoe forward release','moving_refs':['P11'],'fixed_refs':sorted(without_coils-{'H10','P11'}),'removed_refs':['H10'],'direction':[-1,0,0],'range_mm':[0,9],
  'prerequisites':'Usertravel0/preload0/trim0; spring energy removed, vertical H10 fully removed. Slide shoe9mm wristward through the open-front well; do not lift through the narrow roof slot.'},
 {'name':'Stepped shoe upward removal after forward release','moving_refs':['P11'],'fixed_refs':sorted(without_coils-{'H10','P11'}),'removed_refs':['H10'],'direction':[0,0,1],'range_mm':[0,25],'initial_translation_mm':[-9,0,0],
  'prerequisites':'Same safe-unloaded neutral setup and H10 removal; shoe already slid9mm wristward and lies0.5mm outside the carriage front.'}]
m['design_target']['fit_scope']='R5 dynamic rest/end grip shifted5mm toward unchanged palm while retaining30-p user travel. P05 face endsX30,primary web/root retained; P01guide extended toX29; return bosses establish closer rest. P11 is an actuation-only printed shoe, with vertical H10 manual clamp; source-approximate trim does not qualify physical switch OP/total travel.'
m['reach_fit_reference']={'rest_offset_mm':5.,'retained_user_travel_max_p0_p2_mm':[30.,28.],'minimum_spring_length_mm':66.,'spring_tradeoff':str((v.ROOT/'review/flat132-reach-study-2026-10-23/spring-tradeoff.json').resolve()),'camTrim_range_mm':[-.8,.8],'shoe_setting':'e-p, then translate with actual carriage5+u','source_actuator_Q':'u+p-e','native_device_count':53,'native_total_count':106,'print_part_count':15,'manufacture_release':False}
m.pop('switch_fit_reference',None)
m['native_export_files_sha256']={}
cert=json.loads((v.HERE/'dynamic-mode-equivalence.json').read_text())
m['native_provenance']['native_export_origins']=dict(cert['native_export_origins'])
for pose in m['native_poses']:
 if pose['mode']=='isometric':m['native_provenance']['native_export_origins'][pose['assembly']]={'sha256':v.sha(pose['assembly']),'original_source_sha256':v.sha(a.source),'isometricLock':True,'pose': {'u':pose['stroke_mm'],'p':pose['preload_mm'],'e':pose['trim_mm']}}

for path in [a.neutral,a.step]+[Path(p['assembly']) for p in m['native_poses']]:
 if path.is_file():m['native_export_files_sha256'][str(path.resolve())]=v.sha(path)
v.write(a.output,m);print(a.output)
