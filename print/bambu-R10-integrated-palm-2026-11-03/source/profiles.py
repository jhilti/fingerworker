"""Copy the proven R9 official H2D/PLA settings; change only the project label."""
from pathlib import Path
from hashlib import sha256
import json
OUT=Path(__file__).resolve().parents[1];ROOT=OUT.parents[1]
OLD=ROOT/'print/bambu-R9-palm-bracing-2026-10-25/profiles'
manifest=json.loads((OLD/'profile-manifest.json').read_text())
for name in ('H2D_machine.json','H2D_process.json','H2D_PLA.json','project_settings_H2D.json'):
    src=OLD/name
    assert sha256(src.read_bytes()).hexdigest()==manifest['output_profiles'][name]
    data=json.loads(src.read_text())
    if name=='H2D_process.json':data['name']='Fingerworker R10 integrated palm fit test 0.20mm'
    if name in ('H2D_process.json','project_settings_H2D.json'):data['print_settings_id']='Fingerworker R10 integrated palm fit test 0.20mm'
    (OUT/'profiles'/name).write_text(json.dumps(data,indent=2)+'\n')
manifest.update(status='PINNED_R9_OFFICIAL_PRESETS_COPIED_FOR_R10',profile_intent='H2D standard 0.4 mm, one PLA filament, textured PEI; unloaded assessment; no printer transmission',prior_profile_manifest_sha256=sha256((OLD/'profile-manifest.json').read_bytes()).hexdigest())
manifest['output_profiles']={p.name:sha256(p.read_bytes()).hexdigest() for p in sorted((OUT/'profiles').glob('*.json')) if p.name!='profile-manifest.json'}
(OUT/'profiles/profile-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('PASS: R9 stock H2D/PLA macros preserved; R10 project label')
