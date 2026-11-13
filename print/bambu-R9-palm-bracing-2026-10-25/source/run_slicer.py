#!/usr/bin/env python3
"""Run the pinned official Bambu CLI locally. Never sends jobs to a printer."""
from pathlib import Path
import argparse,subprocess,json
from hashlib import sha256
OUT=Path(__file__).resolve().parents[1]
CLI=Path('/tmp/fingerworker-bambu-r8-runtime/BambuStudio.app/Contents/MacOS/BambuStudio')
p=argparse.ArgumentParser();p.add_argument('action',choices=['import','slice']);p.add_argument('--palm-only',action='store_true');a=p.parse_args()
base='Fingerworker_R9_P02_wrist_down_H2D_04mm_PLA' if a.palm_only else 'Fingerworker_R9_H2D_04mm_PLA_Fit_Test'
seed=OUT/(base+'_seed.3mf') if a.palm_only else OUT/'Fingerworker_R9_H2D_04mm_PLA_FIT_seed.3mf'
native=OUT/(base+'.3mf');target=native if a.action=='import' else OUT/'validation'/((base+'_verification.gcode.3mf') if a.palm_only else 'Fingerworker_R9_slice_verification.gcode.3mf')
args=[str(CLI),'--datadir','/tmp/fingerworker-bambu-r9-data','--arrange','0','--orient','0','--ensure-on-bed','--debug','2']
if a.action=='import':args+=['--load-settings',str(OUT/'profiles/H2D_machine.json')+';'+str(OUT/'profiles/H2D_process.json'),'--load-filaments',str(OUT/'profiles/H2D_PLA.json')]
else:args+=['--slice','1']
args+=['--outputdir',str(target.parent),'--export-3mf',target.name,str(seed if a.action=='import' else native)]
log=OUT/'runtime'/((base+'-'+a.action)+'.log')
with log.open('w') as f:r=subprocess.run(args,cwd=OUT,stdout=f,stderr=subprocess.STDOUT)
record={'command':args,'exit_code':r.returncode,'log':str(log.relative_to(OUT)),'target':str(target.relative_to(OUT)),'target_sha256':sha256(target.read_bytes()).hexdigest() if r.returncode==0 else None,'no_printer_transmission':True}
(OUT/'runtime'/((base+'-'+a.action)+'.json')).write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record,indent=2));raise SystemExit(r.returncode)
