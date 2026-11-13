#!/usr/bin/env python3
"""Record and compare every warning/error against the frozen official R15 run."""
from pathlib import Path
from collections import Counter
import hashlib,json,re,zipfile
OUT=Path(__file__).resolve().parents[1];ROOT=OUT.parents[1]
OLD=ROOT/'print/bambu-R15-inboard-straps-2026-11-08'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
layout=json.loads((OUT/'plate-layout.json').read_text())
project=OUT/layout['native_project'];stem=project.stem
log=OUT/'runtime'/(stem+'-slice.log')
baseline=OLD/'runtime/Fingerworker_R15_H2D_04mm_PLA_Inboard_Straps-slice.log'
def messages(path):
 return Counter((m.group(1),m.group(2).strip()) for line in path.read_text().splitlines() if (m:=re.search(r'\[(warning|error|fatal)\]\s*(.*)',line)))
old=messages(baseline);new=messages(log)
old_name='Fingerworker R15 inboard straps no brim 0.20mm'
new_name='Fingerworker R16 upright palm no brim 0.20mm'
expected=Counter({(s,m.replace(old_name,new_name)):n for (s,m),n in old.items()})
run=json.loads((OUT/'runtime'/(stem+'-slice.json')).read_text())
with zipfile.ZipFile(project) as z:settings=json.loads(z.read('Metadata/project_settings.config'))
with zipfile.ZipFile(ROOT/layout['baseline_project']) as z:prior=json.loads(z.read('Metadata/project_settings.config'))
keys=('gcode_flavor','machine_start_gcode','machine_end_gcode','time_lapse_gcode','wrapping_detection_gcode','change_filament_gcode','layer_change_gcode','machine_pause_gcode')
same=all(settings.get(k)==prior.get(k) for k in keys)
bad=new-expected;missing=expected-new
okay=not bad and not missing and same and run['exit_code']==0 and sha(OUT/run['target'])==run['target_sha256']
report=dict(status='PASS_R16_OFFICIAL_H2D_DIAGNOSTICS' if okay else 'FAIL',classification='All warning/error/fatal lines compared against the frozen official R15 run. Only the declared process preset label is normalized. Retained vendor T1001/T65535/T65279 parser errors and preset/nozzle compatibility warnings remain explicitly recorded; this is not an error-free log.',warnings_and_errors=[dict(severity=s,message=m,count=n) for (s,m),n in sorted(new.items())],unexpected_diagnostics=[dict(severity=s,message=m,count=n) for (s,m),n in bad.items()],missing_expected_diagnostics=[dict(severity=s,message=m,count=n) for (s,m),n in missing.items()],official_machine_macros_unchanged=same,cli_exit_code=run['exit_code'],cli_version=run['cli_version'],cli_sha256=run['cli_sha256'],log_sha256=sha(log),baseline_log_sha256=sha(baseline),project_sha256=sha(project),sliced_archive_sha256=run['target_sha256'],layout_sha256=sha(OUT/'plate-layout.json'),validator_sha256=sha(__file__),printer_job_started=False)
(OUT/'validation/cli-diagnostics.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(dict(status=report['status'],unexpected=report['unexpected_diagnostics'],missing=report['missing_expected_diagnostics'])))
raise SystemExit(not okay)
