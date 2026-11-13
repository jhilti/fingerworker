#!/usr/bin/env python3
"""Pinned official local CLI import/slice. Never communicates with a printer."""
from pathlib import Path
from hashlib import sha256
import argparse,json,subprocess
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
(OUT/'runtime'/(stem+'-'+a.action+'.json')).write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record,indent=2));raise SystemExit(r.returncode)
