"""Resolve official bundled Bambu Studio presets for standalone CLI validation."""
from pathlib import Path
import json
SOURCE=Path('/tmp/fingerworker-bambu-mount/BambuStudio.app/Contents/Resources/profiles/BBL')
OUT=Path(__file__).resolve().parents[1]/'profiles'
OUT.mkdir(exist_ok=True)
presets={}
for p in SOURCE.rglob('*.json'):
    try:d=json.loads(p.read_text())
    except Exception:continue
    if 'name' in d:presets[d['name']]=d
def resolve(name):
    d=presets[name];result=resolve(d['inherits']) if d.get('inherits') else {}
    for inc in d.get('include',[]):result.update(resolve(inc))
    result.update(d);result.pop('inherits',None);result.pop('include',None)
    return result
for model,process in [('H2D','0.20mm Standard @BBL H2D')]:
    label=model.replace(' ','')
    machine=resolve(f'Bambu Lab {model} 0.4 nozzle')
    machine['printer_settings_id']=machine['name']
    (OUT/f'{label}_machine.json').write_text(json.dumps(machine,indent=2)+'\n')
    proc=resolve(process)
    proc.update(layer_height='0.2',wall_loops='4',top_shell_layers='5',bottom_shell_layers='5',
                sparse_infill_density='30%',sparse_infill_pattern='gyroid',enable_support='0',
                brim_type='no_brim',brim_width='0',print_settings_id='Fingerworker RevF 0.20mm',
                name='Fingerworker RevF 0.20mm',from_='user',wall_generator='arachne',support_type='normal(auto)')
    proc['print_settings_id']='Fingerworker RevF 0.20mm'
    proc.pop('from_',None);proc['from']='user'
    (OUT/f'{label}_process.json').write_text(json.dumps(proc,indent=2)+'\n')
    for material in ['PETG']:
        name=f'Generic {material} @BBL H2D'
        filament=resolve(name)
        filament['filament_settings_id']=[filament['name']]
        filament['filament_colour']=['#518AAD' if material=='PETG' else '#9E9E9E']
        (OUT/f'{label}_{material}.json').write_text(json.dumps(filament,indent=2)+'\n')
print('Resolved official machine/process/PETG presets for H2D, 0.4 mm nozzles')
