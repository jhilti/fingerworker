#!/usr/bin/env python3
"""Compare all official H2D CLI diagnostics, normalizing only per-plate messages."""
from pathlib import Path
from collections import Counter
import hashlib,json,re,zipfile,xml.etree.ElementTree as ET
OUT=Path(__file__).resolve().parents[1];ROOT=OUT.parents[1]
BASE=ROOT/'print/bambu-R13-mechanics-overnight-2026-11-04'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read_run(folder):
    layout=json.loads((folder/'plate-layout.json').read_text());stem=Path(layout['native_project']).stem
    log=folder/'runtime'/(stem+'-slice.log');run=json.loads((folder/'runtime'/(stem+'-slice.json')).read_text())
    messages=Counter()
    for line in log.read_text().splitlines():
        match=re.search(r'\[(error|warning)\]\s*(.*)',line)
        if match:messages[(match[1],match[2].strip())]+=1
    with zipfile.ZipFile(folder/layout['native_project']) as z:config=json.loads(z.read('Metadata/project_settings.config'))
    sliced=folder/run['target']
    with zipfile.ZipFile(sliced) as z:plates=len(ET.fromstring(z.read('Metadata/slice_info.config')).findall('plate'))
    return layout,log,run,messages,config,sliced,plates
old_layout,old_log,old_run,old,old_cfg,old_sliced,old_plates=read_run(BASE)
layout,log,run,new,cfg,sliced,plates=read_run(OUT)
manifest=json.loads((OUT/'profiles/profile-manifest.json').read_text())
hashes={k:hashlib.sha256(json.dumps(cfg[k],sort_keys=True).encode()).hexdigest() for k in manifest['machine_macro_hashes']}
unchanged=all(cfg[k]==old_cfg[k] and hashes[k]==h for k,h in manifest['machine_macro_hashes'].items())
per_plate={('error',f'Invalid T command ({t}).') for t in ('T1001','T65535','T65279')}
per_plate.add(('warning','load_nozzle_infos_with_compatibility: building nozzle list from filament map and volume types'))
old_profile=old_cfg['print_settings_id'];new_profile=cfg['print_settings_id']
if isinstance(old_profile,list):old_profile=old_profile[0]
if isinstance(new_profile,list):new_profile=new_profile[0]
normalized_old=Counter();baseline_messages={}
for k,v in old.items():
    message=k[1]
    if k[0]=='warning' and '/process_full/' in message:
        assert message.endswith('/'+old_profile+'.json'),('Unexpected baseline preset warning',message,old_profile)
        message=message[:-len(old_profile+'.json')]+new_profile+'.json'
    nk=(k[0],message);normalized_old[nk]+=v;baseline_messages[nk]=k[1]
expected=Counter({k:(plates if k in per_plate else v) for k,v in normalized_old.items()})
extra=new-expected;missing=expected-new
baseline_valid=all(old[k]==old_plates for k in per_plate)
actual_errors={k:v for k,v in new.items() if k[0]=='error'}
ok=(not extra and not missing and baseline_valid and plates==1 and old_plates==1 and unchanged
    and run['exit_code']==old_run['exit_code']==0 and sha(sliced)==run['target_sha256'])
result=dict(status='PASS_R15_OFFICIAL_H2D_DIAGNOSTICS' if ok else 'FAIL',
    classification='All warning/error messages are compared with the frozen R13 six-piece run; each has one plate. Only the expected process-preset filename is changed to the declared embedded R15 profile name, without suppressing any message. The documented per-plate messages remain: the T1001/T65535/T65279 parser errors and nozzle-list compatibility warning. These retained vendor parser diagnostics are explicitly recorded, not described as an error-free log.',
    plate_count=plates,baseline_plate_count=old_plates,
    warnings_and_errors=[dict(severity=k[0],message=k[1],count=new[k],baseline_count=normalized_old[k],baseline_message=baseline_messages.get(k),expected_count=expected[k],counting='per plate' if k in per_plate else 'per run') for k in sorted(set(normalized_old)|set(new))],
    unexpected_diagnostics=[dict(severity=k[0],message=k[1],count=v) for k,v in extra.items()],
    missing_expected_diagnostics=[dict(severity=k[0],message=k[1],count=v) for k,v in missing.items()],
    declared_process_preset_name_change={'baseline':old_profile,'current':new_profile},official_machine_macros_identical_to_R13=unchanged,machine_macro_hashes=hashes,
    cli_exit_code=run['exit_code'],baseline_cli_exit_code=old_run['exit_code'],log_sha256=sha(log),baseline_log_sha256=sha(old_log),
    sliced_archive_sha256=sha(sliced),baseline_sliced_archive_sha256=sha(old_sliced),CAD_source_sha256=layout['CAD_source_sha256'],layout_sha256=sha(OUT/'plate-layout.json'),validator_sha256=sha(Path(__file__)),
    scope='Local slicer completion and diagnostic comparison. Editable-project validation separately checks exact settings/meshes and the complete one-plate slice. No printer job sent.')
(OUT/'validation/cli-diagnostics.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(dict(status=result['status'],unexpected_diagnostics=result['unexpected_diagnostics'],missing_expected_diagnostics=result['missing_expected_diagnostics'],error_counts={k[1]:v for k,v in actual_errors.items()}),indent=2))
raise SystemExit(not ok)
