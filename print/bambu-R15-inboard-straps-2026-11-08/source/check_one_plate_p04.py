#!/usr/bin/env python3
"""Run retained P04 contact checker at the current one-plate rigid placement."""
from pathlib import Path
import json,hashlib
import check_p04_supports as check
OUT=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
layout_path=OUT/'plate-layout.json';layout=json.loads(layout_path.read_text());row=next(r for r in layout['placements'] if r['ref']=='P04')
sliced=OUT/'validation'/(Path(layout['native_project']).stem+'_verification.gcode.3mf')
start=(sha(layout_path),sha(sliced))
r=check.check(sliced,row['rotation_3x3'],row['normalization_translation_mm'],row['plate_xy_mm'],row['plate'])
r.update(layout_sha256=start[0],sliced_archive_sha256=start[1],CAD_source_sha256=layout['CAD_source_sha256'],validator_sha256=sha(Path(__file__)),retained_checker_sha256=sha(Path(check.__file__)))
assert (sha(layout_path),sha(sliced))==start
(OUT/'validation/p04-surface-check.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({k:r[k] for k in ('status','support_segments_in_critical_regions','issues','layout_sha256','sliced_archive_sha256')},indent=2))
raise SystemExit(0 if r['status']=='PASS' else 1)
