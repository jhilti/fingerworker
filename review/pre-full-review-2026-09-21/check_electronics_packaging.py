#!/usr/bin/env python3
"""Validate current UI-captured Onshape audits; never relabel archived results."""
from pathlib import Path
import copy, hashlib, json
root = Path(__file__).resolve().parents[1]
source = (root / 'fingerworker_mvp.fs').read_bytes()
capture = json.loads((root / 'review/onshape-routed-electronics-audits.json').read_text())
# Same fingerprint used to verify the pasted FeatureScript against the local file.
fnv = 2166136261
for character in source.decode():
    fnv = ((fnv ^ ord(character)) * 16777619) & 0xffffffff
assert f'{fnv:08x}' == capture['source_fnv1a32'], 'CAD changed: obtain fresh Onshape audits.'
sha = hashlib.sha256(source).hexdigest()
if 'cad_source_sha256' in capture:
    assert capture['cad_source_sha256'] == sha, 'CAD changed since capture.'
else:
    capture['cad_source_sha256'] = sha
    (root / 'review/onshape-routed-electronics-audits.json').write_text(json.dumps(capture, indent=2) + '\n')
report = {'study': 'Routed PCB envelope study; NOT manufacturing release',
          'cad_source_sha256': sha, 'source_capture': 'onshape-routed-electronics-audits.json',
          'parameters': capture['parameters'], 'part_count': capture['part_count'], 'pose_results': []}
for stroke in (0, 15, 30):
    rows = copy.deepcopy(capture['base0'])
    for index, values in capture.get(f'changes{stroke}', []):
        rows[index][1:] = values
    assert len(rows) == 36 and len({r[0] for r in rows}) == 36
    assert all(r[2] == 0 and 'SKIPPED' not in r[5] for r in rows)
    electronics = rows[29:]
    assert len(electronics) == 7 and all(r[5] == 'CLEAR' and r[4] == 0 for r in electronics)
    report['pose_results'].append({
        'stroke_mm': stroke, 'selected_pairs': len(rows), 'solid_interferences': 0,
        'mechanical_contact_review_pairs': [r[0] for r in rows if r[4]],
        'electronics_gaps_mm': {r[0]: r[1] for r in electronics}})
    print(f'PASS {stroke} mm: 36 selected pairs, zero solid interference; all 7 electronics pairs CLEAR.')
report['limitations'] = [
    'Three discrete positions; no continuous sweep, loaded deformation, or tolerance-stack validation.',
    'Mechanical zero-gap contacts remain classified REVIEW; not general mechanical approval.',
    'Housing/mechanism minimum 0.1 mm is insufficient as an unvalidated FDM tolerance allowance.',
    'Component envelopes are not complete vendor STEP models; module/harness dimensions need physical checks.',
    'No RF, thermal, battery swelling, cable bend, retention or electrical-function verification.']
(root / 'review/electronics-packaging-validation.json').write_text(json.dumps(report, indent=2) + '\n')
print('LIMIT: 0.1 mm housing/mechanism gap requires tolerance redesign/validation before printing.')
