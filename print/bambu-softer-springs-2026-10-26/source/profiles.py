#!/usr/bin/env python3
"""Resolve pinned official H2D presets, preserving every stock machine G-code macro."""
from pathlib import Path
from hashlib import sha256
import json,zipfile
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parents[1]
SOURCE=Path('/tmp/fingerworker-bambu-r8-runtime/BambuStudio.app/Contents/Resources/profiles/BBL')
assert SOURCE.is_dir()
presets={};sources={}
for p in SOURCE.rglob('*.json'):
 try:d=json.loads(p.read_text())
 except Exception:continue
 if 'name' in d:presets[d['name']]=d;sources[d['name']]=p
used={}
def resolve(name):
 d=presets[name];used[name]=sources[name]
 result=resolve(d['inherits']) if d.get('inherits') else {}
 for include in d.get('include',[]):result.update(resolve(include))
 result.update(d);result.pop('inherits',None);result.pop('include',None)
 return result
machine=resolve('Bambu Lab H2D 0.4 nozzle');machine['printer_settings_id']=machine['name']
process=resolve('0.20mm Standard @BBL H2D');process.update(name='Fingerworker S01 spacers 0.20mm',print_settings_id='Fingerworker S01 spacers 0.20mm',layer_height='0.2',initial_layer_print_height='0.2',wall_loops='4',top_shell_layers='5',bottom_shell_layers='5',sparse_infill_density='100%',sparse_infill_pattern='zig-zag',wall_generator='arachne',enable_support='0',support_type='normal(auto)',support_on_build_plate_only='1',brim_type='no_brim',brim_width='0',print_sequence='by layer',**{'from':'user'})
quality={'outer_wall_speed':'60','inner_wall_speed':'100','top_surface_speed':'40','internal_solid_infill_speed':'100','sparse_infill_speed':'120','bridge_speed':'25','gap_infill_speed':'80','default_acceleration':'1500','outer_wall_acceleration':'1500','inner_wall_acceleration':'1500','top_surface_acceleration':'1500','travel_acceleration':'3000','initial_layer_travel_acceleration':'3000','initial_layer_speed':'20','initial_layer_infill_speed':'20','support_speed':'60','support_interface_speed':'40'}
for key,value in quality.items():process[key]=[value]*len(process[key]) if isinstance(process.get(key),list) else value
filament=resolve('Generic PLA @BBL H2D');filament['filament_settings_id']=[filament['name']];filament['filament_colour']=['#518AAD']
for filename,d in [('H2D_machine.json',machine),('H2D_process.json',process),('H2D_PLA.json',filament)]:
 (OUT/'profiles'/filename).write_text(json.dumps(d,indent=2)+'\n')
prior=ROOT/'print/bambu-2026-10-13-RevF/Fingerworker_RevF_H2D_04mm_PETG.3mf'
with zipfile.ZipFile(prior) as archive:settings=json.loads(archive.read('Metadata/project_settings.config'))
settings.update(machine);settings.update(process);settings.update(filament);settings.update(curr_bed_type='Textured PEI Plate',filament_map=['1'],filament_volume_map=['0'],extruder_nozzle_stats=['Standard#1','Standard#1'],printer_model='Bambu Lab H2D',nozzle_diameter=['0.4','0.4'])
(OUT/'profiles/project_settings_H2D.json').write_text(json.dumps(settings,indent=2)+'\n')
macros={k:sha256(json.dumps(v,sort_keys=True).encode()).hexdigest() for k,v in machine.items() if 'gcode' in k}
record={'status':'OFFICIAL_PINNED_PRESETS_RESOLVED','slicer_version':'02.08.02.61','profile_root':str(SOURCE),'machine_macro_hashes':macros,'machine_macros_modified':False,'source_files':{str(p):sha256(p.read_bytes()).hexdigest() for p in used.values()},'output_profiles':{p.name:sha256(p.read_bytes()).hexdigest() for p in sorted((OUT/'profiles').glob('*.json')) if p.name!='profile-manifest.json'},'profile_intent':'Single PLA filament, H2D standard0.4, textured PEI, full-scale S01 spring spacers prototype; no printer transmission'}
(OUT/'profiles/profile-manifest.json').write_text(json.dumps(record,indent=2)+'\n');print('PASS: pinned official H2D/PLA presets; stock machine macros preserved')
