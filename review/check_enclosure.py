"""Validate fresh Onshape enclosure captures against current source and matrix."""
from pathlib import Path
import re,json,hashlib,math
ROOT=Path(__file__).resolve().parents[1];DIR=ROOT/'review/enclosure-2026-10-11'
source=ROOT/'fingerworker_mvp.fs';capture=DIR/'onshape-enclosure.json'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
c=json.loads(capture.read_text());assert c['sourceSHA256']==sha(source)
labels=set(re.findall(r'auditSolidPair\(context,\s*"([^"]+)"',source.read_text()));assert len(labels)==45
wanted={(x,p,l,False) for x in [0,15,30] for p in [0,2] for l in [True,False]}|{(15,p,False,True) for p in [0,2]}
seen=set();contact_reviews=0;checks=0;minimum={}
for case in c['cases']:
    x,p,l,iso=[case[k] for k in ['previewTravelMm','preloadMm','lightSprings','isometricLock']]
    key=(x,p,l,iso);assert key in wanted and key not in seen;seen.add(key)
    raw=case['raw'];assert 'Result: Regeneration complete' in raw
    actual=float(re.search(r'actualStroke : ([0-9.eE+-]+) meter',raw).group(1))
    assert math.isclose(actual,(15-p if iso else x)/1000,abs_tol=1e-9)
    preload=float(re.search(r'additionalPreload : ([0-9.eE+-]+) meter',raw).group(1));assert math.isclose(preload,p/1000,abs_tol=1e-9)
    assert ('mode : ISOMETRIC' if iso else 'mode : DYNAMIC') in raw
    assert ('springArticle : 0X-DF2194' if l else 'springArticle : 0X-DF2185') in raw
    parsed=[dict(f.strip().split(' : ',1) for f in m.group(1).split(' , ')) for m in re.finditer(r'\{([^{}]*)\}',raw)]
    groups=[g for g in parsed if 'pair' in g]
    assert groups==case['groups'] and len(groups)==45 and {g['pair'] for g in groups}==labels
    for g in groups:
        assert int(g['interferences'])==0
        assert g['status']=='CLEAR' or g['status'].startswith('REVIEW') or g['status']=='EXPECTED CONTACT'
        gap=float(g['gap'].split()[0]);assert math.isfinite(gap) and gap>=0
        if g['pair'].startswith('Electronics') or g['pair'].startswith('USB'):minimum[g['pair']]=min(minimum.get(g['pair'],math.inf),gap*1000)
        contact_reviews+=g['status'].startswith('REVIEW');checks+=1
assert seen==wanted
out=dict(status='PASS',source_sha256=sha(source),capture_sha256=sha(capture),configurations=len(seen),group_checks=checks,solid_interference_records=0,contact_review_results=contact_reviews,minimum_gap_mm=minimum,scope='Sampled nominal exact-solid CAD checks, including intended housing/P02 and PCB support contacts; no physical fit or strength qualification')
(DIR/'cad-validation.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
