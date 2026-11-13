#!/usr/bin/env python3
"""Bind the R6 palm-only source delta and the reused R5 motion evidence."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
PROJECT = STUDY.parents[1]
BASE = PROJECT / 'review/flat132-reach-fit-2026-10-23'
BASE_SHA = 'd7f476fa34e862e2b0e1b5a5e91fff0f852b9308a589fafd11ce59e01269915a'
FINAL_SHA = '62fabee79cf36d0e0b6d4cd8430700519dbc529a5ea08f70018b14b0c3f2271f'

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def write(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')

def main():
    base_path = BASE / 'fingerworker_flat132_reach_fit.fs'
    final_path = STUDY / 'fingerworker_flat132_solid_palm.fs'
    baseline = base_path.read_text()
    source = final_path.read_text()
    ledger_path = STUDY / 'source-build.json'
    ledger = json.loads(ledger_path.read_text())
    generated = baseline
    changes = []
    for item in ledger['changes']:
        count = generated.count(item['old'])
        assert count == item['count'], (item['label'], count)
        generated = generated.replace(item['old'], item['new'])
        changes.append({'label': item['label'], 'replacement_count': count})
    assert generated == source
    assert sha(base_path) == BASE_SHA
    assert sha(final_path) == FINAL_SHA == ledger['sha256']
    # Exactly one construction replacement; all other replacements are audited
    # metadata, visual appearance or audit-query updates for the merged body.
    construction = [x for x in ledger['changes'] if x['label'] ==
                    'replace separate hollow palm cap with joined solid contact stock']
    assert len(construction) == 1
    block = construction[0]['new']
    assert 'vector(-27,-43,19.75)' in block and 'vector(-27,43,19.75)' in block
    assert '10.25*mm' in block and '"radius":1.2*mm' in block
    assert 'body(id + "palmPad"),body(id + "palmContactStock")' in block
    assert 'sleeveCoreTool' not in block and 'sleeveBottomTool' not in block
    assert 'palmSleeveReturn' not in source and '"P03 ' not in source
    other_allowed = {
        'R6 study identification', 'R6 feature name', 'remove obsolete sleeve body query',
        'merged palm collision groups', 'direct merged palm collision query',
        'remove obsolete palm-to-sleeve contact audit', 'hand now contacts rigid palm block',
        'hand exclusion follows merged palm', 'remove separate soft cap appearance',
        'appearance comment reflects rigid contact'}
    assert {x['label'] for x in ledger['changes']} == other_allowed | {construction[0]['label']}
    # Source ranges upstream/downstream of palm construction carry all prior
    # moving geometry, domain, preload, ISO81 and electronics definitions.
    old_block = construction[0]['old']
    assert baseline.count(old_block) == source.count(block) == 1
    base_summary_path = BASE / 'validation/validation-summary.json'
    summary = json.loads(base_summary_path.read_text())
    assert summary['status'] == 'NOMINAL_GEOMETRY_CHECKS_PASS'
    assert summary['failed_checks'] == summary['unresolved_checks'] == 0
    assert summary['source_sha256'] == BASE_SHA
    evidence = {}
    for name, expected in summary['evidence_files'].items():
        path = BASE / 'validation' / name
        assert sha(path) == expected, name
        evidence[str(path)] = expected
    result = {
        'status': 'PASS_EXACT_PALM_ONLY_SOURCE_SCOPE',
        'scope': 'R6 alters only fixed P02 construction, removes separate P03 and its two retention tabs, and updates related naming/appearance/audit queries. No other geometry expression or operating domain changes.',
        'baseline_source': str(base_path), 'baseline_source_sha256': BASE_SHA,
        'source': str(final_path), 'source_sha256': FINAL_SHA,
        'source_build_sha256': sha(ledger_path),
        'exact_forward_reconstruction_matches_all_source_bytes': True,
        'replacement_ledger': changes,
        'changed_ref': 'P02', 'removed_ref': 'P03',
        'unchanged_domains': {
            'dynamic': 'u>=0, p in[0,2], u+p<=30, camTrim in[-0.8,0.8]',
            'absolute_carriage_offset_mm': '5+u',
            'usable_stroke_at_p0_p2_mm': [30.0, 28.0],
            'isometric_sleeve_length_mm': 81.0,
            'isometric_approach_mm': '15-p',
            'frame_width_mm': 132.0, 'finger_opening_mm': 72.0},
        'reuse_policy': 'Prior source-bound checks between all refs except P02/P03 remain applicable by exact unchanged source expressions. New native STEP identity of104 surviving unchanged bodies and a focused changed-P02 audit are required before the R6 summary may pass. Prior archives keep their original R5 provenance.',
        'baseline_validation_summary': str(base_summary_path),
        'baseline_validation_summary_sha256': sha(base_summary_path),
        'baseline_evidence_files_sha256': evidence,
        'limitations': ['No printed material strength,500 N working-load rating, comfort or durability is qualified. Solid CAD stock does not prescribe slicer infill.']}
    write(HERE / 'source-scope-certificate.json', result)
    print(json.dumps({k: result[k] for k in ('status', 'source_sha256', 'changed_ref', 'removed_ref')}))

if __name__ == '__main__':
    main()
