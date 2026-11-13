#!/usr/bin/env python3
"""Pinned Bambu Studio CLI import/slice. No printer connection or transmission."""
from pathlib import Path
import argparse,hashlib,json,subprocess
OUT=Path(__file__).resolve().parents[1]
CLI=Path('/tmp/fingerworker-bambu-r8-runtime/BambuStudio.app/Contents/MacOS/BambuStudio')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(CLI)=='1a79017b9f86fb6db92987f4a4c4a4834ac540cf36703d49c7c91ed1959c2026','Unexpected slicer runtime'
p=argparse.ArgumentParser();p.add_argument('action',choices=['import','slice']);p.add_argument('--candidate',action='store_true');a=p.parse_args()
layout=json.loads((OUT/('candidate-layout.json' if a.candidate else 'plate-layout.json')).read_text())
project=OUT/layout['native_project'];stem=project.stem
ev=OUT/'validation'/('candidate' if a.candidate else '');ev.mkdir(exist_ok=True)
target=project if a.action=='import' else ev/(stem+'_verification.gcode.3mf')
args=[str(CLI),'--datadir','/tmp/fingerworker-bambu-r10-data','--arrange','0','--orient','0','--ensure-on-bed','--debug','2']
if a.action=='slice':args+=['--slice','0']
args+=['--outputdir',str(target.parent),'--export-3mf',target.name,str(OUT/layout['seed_path'] if a.action=='import' else project)]
log=OUT/'runtime'/(stem+'-'+a.action+'.log')
with log.open('w') as f:r=subprocess.run(args,cwd=OUT,stdout=f,stderr=subprocess.STDOUT)
report=dict(command=args,exit_code=r.returncode,cli_sha256=sha(CLI),cli_version='BambuStudio-02.08.02.61',log=str(log.relative_to(OUT)),target=str(target.relative_to(OUT)),target_sha256=sha(target) if target.exists() else None,no_printer_transmission=True)
if r.returncode==0 and a.action=='slice' and not a.candidate:
 layout['status']='NATIVE_R16_SLICED_SINGLE_PLATE'
 (OUT/'plate-layout.json').write_text(json.dumps(layout,indent=2)+'\n')
(OUT/'runtime'/(stem+'-'+a.action+'.json')).write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2));raise SystemExit(r.returncode)
