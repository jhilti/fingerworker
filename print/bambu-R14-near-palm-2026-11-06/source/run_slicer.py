#!/usr/bin/env python3
"""Pinned official local CLI import/slice. Never communicates with a printer."""
from pathlib import Path
from hashlib import sha256
import argparse,json,subprocess,zipfile,xml.etree.ElementTree as ET
OUT=Path(__file__).resolve().parents[1]
CLI=Path('/tmp/fingerworker-bambu-r8-runtime/BambuStudio.app/Contents/MacOS/BambuStudio')
p=argparse.ArgumentParser();p.add_argument('action',choices=['import','slice']);p.add_argument('--candidate',choices=['flat','wrist','side']);a=p.parse_args()
layout_name='candidate-'+a.candidate+'-layout.json' if a.candidate else 'plate-layout.json'
layout=json.loads((OUT/layout_name).read_text());native=OUT/layout['native_project'];stem=native.stem
evidence=OUT/'validation'/('candidate-'+a.candidate) if a.candidate else OUT/'validation'
evidence.mkdir(exist_ok=True)
target=native if a.action=='import' else evidence/(stem+'_verification.gcode.3mf')
args=[str(CLI),'--datadir','/tmp/fingerworker-bambu-r10-data','--arrange','0','--orient','0','--ensure-on-bed','--debug','2']
if a.action=='import':args+=['--load-settings',str(OUT/'profiles/H2D_machine.json')+';'+str(OUT/'profiles/H2D_process.json'),'--load-filaments',str(OUT/'profiles/H2D_PLA.json')]
else:args+=['--slice','0']
args+=['--outputdir',str(target.parent),'--export-3mf',target.name,str(OUT/layout['seed_path'] if a.action=='import' else native)]
log=OUT/'runtime'/(stem+'-'+a.action+'.log')
with log.open('w') as f:r=subprocess.run(args,cwd=OUT,stdout=f,stderr=subprocess.STDOUT)
record=dict(command=args,exit_code=r.returncode,log=str(log.relative_to(OUT)),target=str(target.relative_to(OUT)),target_sha256=sha256(target.read_bytes()).hexdigest() if target.exists() else None,no_printer_transmission=True)
if a.action=='import' and r.returncode==0:
    # Unsupported enums can silently become defaults on official import.
    # The UI's sparse Rectilinear pattern serializes as "zig-zag"; the
    # literal "rectilinear" belongs to the support-pattern enum.
    with zipfile.ZipFile(target) as z:
        cfg=ET.fromstring(z.read('Metadata/model_settings.config'))
    modifiers={}
    for part in cfg.findall('object/part'):
        if part.get('subtype')=='modifier_part':
            values={m.get('key'):m.get('value') for m in part.findall('metadata')}
            modifiers[values['name']]=values
    failures=[]
    for expected in layout.get('local_density_modifiers',[]):
        actual=modifiers.get(expected['name'],{})
        for key in ('sparse_infill_density','sparse_infill_pattern'):
            if actual.get(key)!=expected[key]:
                failures.append(dict(modifier=expected['name'],key=key,expected=expected[key],actual=actual.get(key)))
    if len(modifiers)!=layout.get('modifier_count',0):failures.append(dict(actual_modifier_count=len(modifiers),expected_modifier_count=layout.get('modifier_count',0)))
    record['modifier_import_preserved']=not failures
    record['modifier_import_failures']=failures
    if failures:record['exit_code']=2
(OUT/'runtime'/(stem+'-'+a.action+'.json')).write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record,indent=2));raise SystemExit(record['exit_code'])
