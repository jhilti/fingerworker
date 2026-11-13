#!/usr/bin/env python3
"""Validate fresh UI-captured spring CAD audits against source and catalogue ledger.
No strength, real hand-fit or manufacturing release is implied.
"""
from pathlib import Path
import hashlib,json,math,re
ROOT=Path(__file__).resolve().parents[1]
CAPTURE=ROOT/'review/software-2026-10-11/onshape-ordered-springs.json'
OUT=ROOT/'review/software-2026-10-11/cad-validation.json'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report={'status':'RUNNING','manufacturing_release':False}
OUT.write_text(json.dumps(report,indent=2)+'\n')
try:
    source_path=ROOT/'review/enclosure-2026-10-11/fingerworker_before_enclosure.fs'
    source=source_path.read_text()
    capture=json.loads(CAPTURE.read_text())
    assert capture['sourceSHA256']==sha(source_path), 'CAD source changed: fresh captures required'
    labels=set(re.findall(r'auditSolidPair\(context,\s*"([^"]+)"',source))
    assert len(labels)==45
    wanted={(x,p,light,False) for x in (0,15,30) for p in (0,2) for light in (True,False)}|{(15,p,False,True) for p in (0,2)}
    seen=set(); reviews=0; total=0
    for case in capture['cases']:
        x,p,light,iso=case['previewTravelMm'],case['preloadMm'],case['lightSprings'],case['isometricLock']
        key=(x,p,light,iso)
        assert key in wanted and key not in seen, 'Unexpected/duplicate configuration'
        seen.add(key)
        assert len(case['groups'])==45 and {g['pair'] for g in case['groups']}==labels
        assert 'Result: Regeneration complete' in case['raw']
        parsed=[dict(field.strip().split(' : ',1) for field in match.group(1).split(' , ')) for match in re.finditer(r'\{([^{}]*)\}',case['raw'])]
        assert [group for group in parsed if 'pair' in group]==case['groups'], 'Captured group ledger differs from raw output'
        actual=(15-p if iso else x)
        actual_stroke=float(re.search(r'actualStroke : ([0-9.eE+-]+) meter',case['raw']).group(1))
        actual_preload=float(re.search(r'additionalPreload : ([0-9.eE+-]+) meter',case['raw']).group(1))
        assert math.isclose(actual_stroke,actual/1000,abs_tol=1e-9)
        assert math.isclose(actual_preload,p/1000,abs_tol=1e-9)
        article,free,k=('0X-DF2194',102,3.307) if light else ('0X-DF2185',105,3.709)
        assert f'springArticle : {article}' in case['raw']
        assert f'springFreeLengthMm : {free}' in case['raw']
        assert f'springRateEachNPerMm : {k}' in case['raw']
        expected=0 if iso else 2*k*(free-(101-p-x))
        actual_force=float(re.search(r'nominalPairForceN : ([0-9.eE+-]+)',case['raw']).group(1))
        assert math.isclose(expected,actual_force,abs_tol=1e-6)
        for g in case['groups']:
            assert int(g['interferences'])==0 and not g['status'].startswith('SKIPPED')
            assert g['status']=='CLEAR' or g['status'].startswith('REVIEW')
            gap=float(g['gap'].split()[0]); assert math.isfinite(gap) and gap>=0
            if g['pair']=='Electronics housing / mechanism': assert gap>=0.0006-1e-9
            if g['pair']=='6 mm cord / fixed frame': assert gap>=0.001-1e-9
            if g['pair']=='6 mm cord / moving and other parts': assert gap>=0.013-1e-9
            reviews+=g['status'].startswith('REVIEW'); total+=1
    assert seen==wanted, 'Missing configurations'
    report.update(status='PASS: 14 configurations / 630 source-bound CAD group checks',configurations=len(seen),group_checks=total,solid_interferences=0,contact_review_results=reviews,cad_source_sha256=sha(source_path),source_file=str(source_path.relative_to(ROOT)),capture_sha256=sha(CAPTURE),scope='Sampled exact-solid CAD clearances with illustrative hand/electronics/cord. Not continuous motion, real hand-fit or strength qualification.')
except Exception as error:
    report.update(status='FAIL',error=str(error));OUT.write_text(json.dumps(report,indent=2)+'\n');raise
OUT.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
