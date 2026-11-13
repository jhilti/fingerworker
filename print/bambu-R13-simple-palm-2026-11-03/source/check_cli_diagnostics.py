#!/usr/bin/env python3
"""Classify official H2D CLI messages against the frozen R12 baseline."""
from pathlib import Path
from collections import Counter
import hashlib,json,re,zipfile
OUT=Path(__file__).resolve().parents[1];ROOT=OUT.parents[1]
BASE=ROOT/'print/bambu-R12-simplified-2026-11-03'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read_run(folder,revision):
    stem=f'Fingerworker_{revision}_H2D_04mm_PLA_Fit_Test'
    log=folder/'runtime'/(stem+'-slice.log');run=json.loads((folder/'runtime'/(stem+'-slice.json')).read_text())
    messages=Counter()
    for line in log.read_text().splitlines():
        match=re.search(r'\[(error|warning)\]\s*(.*)',line)
        if match:messages[(match[1],match[2].strip())]+=1
    with zipfile.ZipFile(folder/(stem+'.3mf')) as z:config=json.loads(z.read('Metadata/project_settings.config'))
    return log,run,messages,config
old_log,old_run,old,old_cfg=read_run(BASE,'R12');log,run,new,cfg=read_run(OUT,'R13')
manifest=json.loads((OUT/'profiles/profile-manifest.json').read_text())
hashes={k:hashlib.sha256(json.dumps(cfg[k],sort_keys=True).encode()).hexdigest() for k in manifest['machine_macro_hashes']}
unchanged=all(cfg[k]==old_cfg[k] and hashes[k]==h for k,h in manifest['machine_macro_hashes'].items())
extra=new-old
expected_errors={('error',f'Invalid T command ({t}).'):3 for t in ('T1001','T65535','T65279')}
actual_errors={k:v for k,v in new.items() if k[0]=='error'}
sliced=OUT/run['target'];ok=not extra and new==old and actual_errors==expected_errors and unchanged and run['exit_code']==old_run['exit_code']==0 and sha(sliced)==run['target_sha256']
layout=json.loads((OUT/'plate-layout.json').read_text())
result=dict(status='PASS_BASELINE_OFFICIAL_H2D_DIAGNOSTICS' if ok else 'FAIL',
    classification='The three Invalid T parser messages occur once per plate in both R12 and R13 with identical official machine macros; no new diagnostic is introduced by R13. They are retained vendor startup/parser diagnostics, not suppressed or reported as an error-free log.',
    warnings_and_errors=[dict(severity=k[0],message=k[1],count=v,baseline_count=old[k]) for k,v in sorted(new.items())],
    unexpected_diagnostics=[dict(severity=k[0],message=k[1],count=v) for k,v in extra.items()],
    official_machine_macros_identical_to_R12=unchanged,machine_macro_hashes=hashes,
    cli_exit_code=run['exit_code'],baseline_cli_exit_code=old_run['exit_code'],log_sha256=sha(log),baseline_log_sha256=sha(old_log),
    sliced_archive_sha256=sha(sliced),CAD_source_sha256=layout['CAD_source_sha256'],
    scope='Local slicer completion and baseline diagnostic classification; editable-project validation separately checks embedded settings, all meshes and all three completed plates. No printer job sent.')
(OUT/'validation/cli-diagnostics.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(dict(status=result['status'],unexpected_diagnostics=result['unexpected_diagnostics'],error_counts={k[1]:v for k,v in actual_errors.items()}),indent=2))
raise SystemExit(not ok)
