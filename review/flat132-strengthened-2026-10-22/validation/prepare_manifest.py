#!/usr/bin/env python3
"""Bind actual native export paths to the finished source and explicit checks.

The operator must supply the matching branch URL and exports from that branch.
This records the association; it does not independently regenerate Onshape.
"""
import argparse
from pathlib import Path
import validate_finished as v

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--neutral',type=Path,required=True)
p.add_argument('--step',type=Path,required=True)
p.add_argument('--part-step',nargs=2,action='append',metavar=('REF','STEP'),default=[])
p.add_argument('--workspace',required=True)
p.add_argument('--source',type=Path,default=v.HERE.parent/'fingerworker_flat132_strengthened.fs')
p.add_argument('--native-pose',nargs=4,action='append',metavar=('MODE','STROKE','PRELOAD','ZIP'),default=[])
p.add_argument('--output',type=Path,default=v.HERE/'manifest.json')
p.add_argument('--baseline',type=Path,default=v.ROOT/'review/flat132-finished-2026-10-22/native/Flat132_R1_neutral_final.zip')
args=p.parse_args()
m=v.template();m['status']='ACTUAL_NATIVE_INPUT_MANIFEST'
m['assembly']=str(args.neutral.resolve());m['feature_source']=str(args.source.resolve())
m['native_provenance']={'workspace_url':args.workspace,'feature_source_sha256':v.sha(args.source),
    'association':'Operator-supplied native export/source association; original filenames and each member SHA256 are checked in report.'}
certificate=v.HERE.parent/'source-ui-guard-only-certificate.json'
if certificate.exists():
    import json
    c=json.loads(certificate.read_text())
    m['native_provenance']['source_geometry_equivalence']={'certificate':str(certificate.resolve()),'certificate_sha256':v.sha(certificate),
        'native_step_original_source_sha256':c['prior_source_sha256'],
        'native_neutral_original_source_sha256':c['prior_source_sha256'],
        'native_poses_original_source_sha256':c['final_source_sha256'],
        'meaning':'The neutral ZIP and STEP were exported from the prior source. The exact single changed UI rejection condition leaves every geometry expression unchanged throughout the exact legal configuration domain. The maximum/isometric native pose ZIP exports are associated with the final guarded source; both neutral exports retain their exact prior source association.'}
m['expected_device_refs']=sorted((v.DEVICE|{'H23','H240','H241','H242','H243','H250','H251','H252','H253'})-{'H070','H071','H080','H081'})
m['motion_overrides']={'H10':[-1.,-1.]}
m['configuration_domain_vertices_stroke_preload_mm']=[[0.,0.],[30.,0.],[28.,2.],[0.,2.]]
m['configuration_domain_description']='0<=preload<=2, stroke>=0, stroke+preload<=30 mm. Printed moving stop faces reduce maximum stroke to 30-preload. H10 cam must be manually reset by -preload after each preload change.'
m['actuator_effective_travel_coefficients']=[1.,1.]
m['continuous_transverse_partitions']=[{'pair':['P04','P05'],'axis':1,'planes_mm':[-31.,-17.,17.,31.],'reason':'Exact complete Y-slab partition separates central cam protrusion from broad endpoint stop faces; never waives overlap.'}]
m['sensor']['native_assembly_step']=str(args.step.resolve())
m['native_part_steps']={ref:str(Path(path).resolve()) for ref,path in args.part_step}
m['contacts']=[
    {'pair':['H01','H02'],'kind':'exterior_contact','reason':'Spherical button/pusher load contact; no material overlap permitted'},
    {'pair':['H01','H12'],'kind':'exterior_contact','reason':'Actual flat rear support; no material overlap permitted'},
    {'pair':['P02','P03'],'kind':'nominal_surface_fit_mesh_artifact','maximum_intersection_volume_mm3':1.75,
     'reason':'Native analytic R7.75 core/sleeve surfaces coincide. Separate STL facets can overlap; exact native BRep intersection must independently be zero.',
     'requires_exact_brep_pair':True},
    {'pair':['H09a','H09b'],'kind':'purchased_actuator_internal_joint','maximum_intersection_volume_mm3':1.53,
     'reason':'Unchanged Omron actuator previews meet at roller axle. The lever cylinder terminates at roller centre. Analytic upper bound pi*(0.45)^2*2.4=1.52682mm3; joint is not independent device-body clearance.'},
    {'pair':['E08','PCB_SW2'],'kind':'intended_switch_actuation_travel_envelope','maximum_intersection_volume_mm3':3.22,
     'reason':'E08 is an explicit swept side-button actuator TRAVEL/clearance envelope, not material. It deliberately reaches the SW2 switch courtyard/height envelope. Other component/enclosure clearances remain checked.'}]
for i in range(4):
    m['contacts'].append({'pair':['H12','H25'+str(i)],'kind':'nominal_screw_thread_engagement','maximum_intersection_volume_mm3':1.9,
        'reason':'Nominal M2 shaft R1 occupies its R0.85 tap-drill envelope over the 2.15mm backing plate. Ideal annular envelope pi*(1^2−0.85^2)*2.15=1.87437mm3. Helical steel thread teeth are not modeled.'})
for ref in ('H180','H181'):
    m['contacts'].append({'pair':['H12',ref],'kind':'nominal_screw_thread_engagement','maximum_intersection_volume_mm3':4.35,
        'reason':'Finished M3x0.5 thread is represented by its standard diameter2.5mm tap-drill bore; the nominal shaft radius1.5mm engages for2mm. Ideal thread-envelope annulus pi*(1.5^2−1.25^2)*2=4.31969mm3. Helical thread teeth are not modeled.'})
m['native_poses']=[{'mode':mode,'stroke_mm':float(s),'preload_mm':float(pre),'assembly':str(Path(path).resolve())} for mode,s,pre,path in args.native_pose]
m['required_native_pose_keys']=['dynamic:28:2','isometric:13:2']
m['baseline_native_comparison']={'assembly':str(args.baseline.resolve()),'assembly_sha256':v.sha(args.baseline),'only_changed_refs':['P01','P05'],'removed_refs':['H070','H071','H080','H081'],'permitted_triangle_order_only_refs':['H15','P04'],'require_each_expected_change':True,'meaning':'Except the four intentionally removed M4 stop screw/nut previews, all hardware, manufacturer sensor, palm, finger grip, spring, electronics and other unchanged native STL members must match their R1 bytes exactly at neutral, except H15/P04 facet ordering is ignored only after exact native triangle-coordinate hashes match with no rounding or geometric tolerance. This isolates print reinforcement geometry; it is not a material strength assessment.'}
def dimension(name,ref,axis,component,expected):
    return {'name':name,'type':'bounds','ref':ref,'axis':axis,'component':component,'expected_mm':expected,'tolerance_mm':.02}
def ray(name,ref,origin,direction,axis,indices,expected):
    return {'name':name,'type':'ray_levels','ref':ref,'origin_mm':origin,'direction':direction,'axis':axis,'level_indices':indices,'expected_mm':expected,'tolerance_mm':.025}
m['dimension_checks'] += [
    dimension('Actual sensor axial envelope (no scale)', 'H01',0,'extent',7.95),
    dimension('Actual sensor housing/lead transverse envelope Z', 'H01',2,'extent',25.),
    ray('Sensor backing plate axial thickness','H12',[100,0,18],[-1,0,0],0,[-1,0],2.15),
    ray('Backing collar nominal steel wall, non-lead side','H12',[-9, -100,18],[0,1,0],1,[-1,0],.75),
    ray('Front stainless keeper thickness','H23',[100,0,31],[-1,0,0],0,[-1,0],.5),
    ray('Frame floor below sensor pocket','P01',[-5,0,100],[0,0,-1],2,[-1,0],4.7),
    dimension('H190 retention spacer length','H190',1,'extent',6.),
    dimension('H191 retention spacer length','H191',1,'extent',6.)]
for side in (-1,1):
    m['dimension_checks'] += [
        ray(f'Restored carriage rear roof side{side}','P04',[114,side*41.99,100],[0,0,-1],2,[-1,-2],4.063065),
        ray(f'Closed guide-slot front ligament side{side}','P01',[100,side*16.5,8.5],[-1,0,0],0,[-1,-2],2.3),
        ray(f'Cassette ear upper ligament side{side}','H12',[-12.8,side*13,100],[0,0,-1],2,[-1,-2],1.25),
        ray(f'Cassette ear rear ligament side{side}','H12',[-100,side*13,8.5],[1,0,0],0,[1,0],1.45)]
def box(name,ref,lo,hi,expect):return {'name':name,'ref':ref,'type':'box','minimum_mm':lo,'maximum_mm':hi,'expect':expect}
def cylinder(name,ref,x0,x1,y,z,r,expect='empty'):
    return {'name':name,'ref':ref,'type':'cylinder_x','start_x_mm':x0,'end_x_mm':x1,'y_mm':y,'z_mm':z,'radius_mm':r,'expect':expect}
m['material_and_clearance_probes']=[
    box('Continuous flat steel rear support centre','H12',[-11.99,-7,10],[-9.86,7,26],'solid'),
    box('Retained 4.7mm frame floor under cell','P01',[-12,-5,-1.99],[1,5,2.69],'solid'),
    box('P05 central reaction web beside pusher','P05',[1.41,-5,14],[4.99,-3,22],'solid'),
    box('Positive-side fixed-guide lead exit','P01',[-10.19,15.51,12.31],[-8.01,18.49,23.99],'empty'),
    cylinder('Backing collar ID25.5 air envelope','H12',-9.849,-8.651,0,18,12.74),
    cylinder('Stainless keeper ID20 air envelope','H23',-1.399,-.901,0,18,9.99),
    cylinder('Soft sleeve swept adjuster relief','P03',-24.49,-21.31,0,18,3.49)]
for y in (-10.5,10.5):
    for z in (7.5,28.5):
        m['material_and_clearance_probes'] += [
            cylinder('M2 front keeper clearance hole','H23',-1.399,-.901,y,z,1.099),
            cylinder('M2 panhead/yoke clearance pocket','P05',-1.49,1.39,y,z,2.59),
            cylinder('M2 rear backing pilot bore','H12',-11.99,-9.86,y,z,.849)]
m['service_sweeps']=[
    {'name':'Complete palm/electronics module upward release','moving_refs':['P02','P03','P08','P09','P10'],
     'removed_refs':[], 'direction':[0,0,1],'range_mm':[0,40], 'initial_translation_mm':[0,0,.001],'preload_mm':2.,
     'prerequisites':'Release H21 preload lock, restrain/remove spring energy, set preload2mm, remove both palm M4s. Electronics reference bodies are part of the module and excluded as fixed obstacles.',
     'fixed_refs':sorted((set(m['expected_device_refs'])-{'P02','P03','P08','P09','P10'}-v.SPRINGS))},
    {'name':'Keeper wristward release','moving_refs':['H15'],'fixed_refs':['P01'], 'direction':[-1,0,0],'range_mm':[0,2.0],
     'prerequisites':'Remove complete palm/case module, H160/H161 keeper screws, H13 adjuster first.'},
    {'name':'Keeper upward removal after wristward release','moving_refs':['H15'],'fixed_refs':['P01'],
     'direction':[0,0,1],'range_mm':[0,35],'initial_translation_mm':[-2.0,0,0],
     'prerequisites':'Same removals as wristward release; keeper already shifted 2.0 mm.'}]
stack={'H01','H02','H12','H20','P05','H050','H051','H23','H240','H241','H242','H243','H250','H251','H252','H253'}
removed={'P02','P03','P08','P09','P10','H040','H041','H030','H031','H180','H181','H190','H191','P060','P061','P070a','P070b','P071a','P071b'}
remaining=sorted(set(m['expected_device_refs'])-stack-removed)
prereq='Remove palm/case module; safely release/remove springs, rear caps/bumpers and both rods; remove H18/H19 retention hardware. Keep the whole sensor cassette/keeper/yoke/pusher stack together; preload0.'
for name,direction,interval,initial in [
    ('Sensor-yoke stack forward lead-window release',[1,0,0],[0,3.5],[0,0,0]),
    ('Sensor-yoke stack final upward removal',[0,0,1],[0,40],[3.5,0,0])]:
    m['service_sweeps'].append({'name':name,'moving_refs':sorted(stack),'fixed_refs':remaining,
        'removed_refs':sorted(removed),'direction':direction,'range_mm':interval,'initial_translation_mm':initial,'prerequisites':prereq})
m['service_sweeps'].append({'name':'Removed stack: yoke/pusher axial separation from sensor keeper',
    'moving_refs':['P05','H02','H20','H050','H051'],'fixed_refs':sorted(stack-{'P05','H02','H20','H050','H051'}),
    'direction':[1,0,0],'range_mm':[0,30],'prerequisites':'Complete assembled sensor/yoke stack removed onto bench using the preceding sequence. No other device bodies in this local separation check.'})
m['dimension_checks'] += [
    ray('Strengthened reaction wall depth at Y0/Z6', 'P01',[-100,0,6],[1,0,0],0,[1,0],6.75),
    ray('Upper reaction bridge roof at X-14/Y0', 'P01',[-14,0,100],[0,0,-1],2,[-1,-2],3.0),
    ray('Strengthened negative cassette guide width at X-9.2/Z27', 'P01',[-9.2,-100,27],[0,1,0],1,[3,2],5.0),
    ray('Strengthened positive cassette guide width at X-9.2/Z27', 'P01',[-9.2,-100,27],[0,1,0],1,[5,4],5.0),
    ray('Upper driver access diameter at X-19/Z32', 'P01',[-19,-100,32],[0,1,0],1,[2,1],6.2),
    dimension('Fixed frame overall Z extent remains 35 mm', 'P01',2,'extent',35.0)]
for side in (-1,1):
    lo,hi=(15.51,20.49) if side==1 else (-20.49,-15.51)
    blo,bhi=(20.51,25.39) if side==1 else (-25.39,-20.51)
    m['material_and_clearance_probes'] += [
        box(f'Five mm guide stock behind lead notch side{side}','P01',[-15.99,lo,12.01],[-13.01,hi,28.99],'solid'),
        box(f'Upper reaction buttress continuous stock side{side}','P01',[-15.99,blo,12.01],[-13.01,bhi,28.99],'solid')]
m['material_and_clearance_probes'] += [
    box('Positive lead exit through widened guide and buttress','P01',[-10.34,15.51,12.31],[-7.61,25.39,23.99],'empty'),
    box('Upper bridge continuous front strip beyond driver-access front X-15.9','P01',[-15.89,-25.39,30.01],[-12.51,25.39,32.99],'solid')]
m['dimension_checks'] += [
    dimension('Integral sensing-stop front datum at neutral', 'P05',0,'maximum',35.0),
    ray('Negative printed sensing stop bearing width','P05',[34,-100,18],[0,1,0],1,[1,0],14.0),
    ray('Positive printed sensing stop bearing width','P05',[34,-100,18],[0,1,0],1,[3,2],14.0),
    ray('Negative printed stop arm root width','P05',[20,-100,18],[0,1,0],1,[1,0],10.0),
    ray('Positive printed stop arm root width','P05',[20,-100,18],[0,1,0],1,[3,2],10.0)]
for side in (-1,1):
    lo,hi=(17.01,30.99) if side==1 else (-30.99,-17.01)
    rlo,rhi=(19.01,28.99) if side==1 else (-28.99,-19.01)
    m['dimension_checks'].append(ray(f'Printed sensing stop bearing height side{side}', 'P05',[34,side*24,100],[0,0,-1],2,[-1,0],22.0))
    m['material_and_clearance_probes'] += [
        box(f'Broad integral printed stop face stock side{side}','P05',[25.01,lo,7.01],[34.99,hi,28.99],'solid'),
        box(f'Axial printed stop-arm root stock side{side}','P05',[8.51,rlo,7.01],[24.99,rhi,28.99],'solid')]
m['design_target']={'maximum_hand_force_N':500,'qualification':'DESIGN_TARGET_ONLY; geometry checks do not establish a print/material load rating',
    'reinforcement_scope':'Printed P01 and P05 geometry changes; M4 stop screws/nuts H070/H071/H080/H081 removed in favor of broad integral printed P05 stop faces. Remaining hardware must match previous R1 native exports exactly at neutral'}
m['localized_wall_check_meaning']='Recorded nominal local sections, not global material strength or a global minimum wall. R2 reaction wall local depth 6.75 mm, guide widths 5 mm and top bridge 3 mm; fixed-guide end wall remains 2.3 mm and non-primary cassette ear roof 1.25 mm. Print orientation, material, strength, fatigue and retention durability remain unqualified.'
m['native_export_files_sha256']={}
for path in [args.neutral,args.step]+[Path(pose['assembly']) for pose in m['native_poses']]:
    if path.is_file():m['native_export_files_sha256'][str(path.resolve())]=v.sha(path)
v.write(args.output,m)
print(args.output)
