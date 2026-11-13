#!/usr/bin/env python3
"""Bind R7 source delta to frozen R6 and its unchanged-mechanism evidence."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent
STUDY=HERE.parent
PROJECT=STUDY.parents[1]
BASE=PROJECT/'review/flat132-solid-palm-2026-10-23'
BASE_SHA='62fabee79cf36d0e0b6d4cd8430700519dbc529a5ea08f70018b14b0c3f2271f'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
def main():
    ledger=json.loads((STUDY/'source-build.json').read_text())
    source_path=STUDY/'fingerworker_flat132_adjustable_rear.fs'
    source=source_path.read_text();baseline=(BASE/'fingerworker_flat132_solid_palm.fs').read_text()
    assert hashlib.sha256(baseline.encode()).hexdigest()==BASE_SHA
    generated=baseline;changes=[]
    for item in ledger['changes']:
        n=generated.count(item['old']);assert n==item['count'],(item['label'],n,item['count'])
        generated=generated.replace(item['old'],item['new'])
        changes.append({'label':item['label'],'replacement_count':n})
    assert generated==source
    approved={'R7 identity','feature name','new rest parameter','travel label','ISO label','rest domain','max user travel','travel guard explanation','frame envelope','shorten base','shorten rods','rod labels','replace fixed rear bosses with compact screw-adjusted retained shoes','rear bench holes','audit rear includes new shoes','print rest setting','current motion explanatory comment','new default','P01 label','new shoe appearance'}
    assert {x['label'] for x in ledger['changes']}==approved
    assert 'const restOffset=5*mm+rearAdvance;' in source
    assert 'const maxDynamicTravel = 30 * mm - preload - rearAdvance;' in source
    assert 'rearAdvance+preload > 2*mm+1e-6*mm' in source
    assert 'const stroke = definition.isometricLock ? 20 * mm - preload : restOffset+definition.previewTravel;' in source
    assert '"Cam trim (-0.8 to +0.8 mm; physical calibration)"' in source
    assert sha(source_path)==ledger['sha256']
    summary_path=BASE/'validation/validation-summary.json';summary=json.loads(summary_path.read_text())
    assert summary['status']=='NOMINAL_GEOMETRY_CHECKS_PASS'
    assert summary['failed_checks']==summary['unresolved_checks']==0
    assert summary['source_sha256']==BASE_SHA
    evidence={}
    for name,digest in summary['evidence_files'].items():
        p=BASE/'validation'/name;assert sha(p)==digest,name;evidence[str(p)]=digest
    report={'status':'PASS_EXACT_R7_REAR_DELTA_RECONSTRUCTION','scope':'All R7 bytes are reconstructed from the frozen R6 source and declared replacement ledger. Independent native body identity and changed-rear geometry checks are separate requirements.',
      'baseline_source':str(BASE/'fingerworker_flat132_solid_palm.fs'),'baseline_source_sha256':BASE_SHA,
      'source':str(source_path),'source_sha256':sha(source_path),'source_build_sha256':sha(STUDY/'source-build.json'),
      'exact_forward_reconstruction_matches_all_source_bytes':True,'replacement_ledger':changes,
      'baseline_validation_summary':str(summary_path),'baseline_validation_summary_sha256':sha(summary_path),
      'baseline_evidence_files_sha256':evidence,
      'changed_old_geometry_refs':['P01','P060','P061','H040','H041'],
      'unchanged_motion_equivalence':{'map':'u_R6=a_R7+u_R7; p_R6=p_R7; e_R6=e_R7',
       'domain':'a>=0,p>=0,a+p<=2,u>=0,u+a+p<=30,e in[-0.8,0.8]',
       'meaning':'Every R7 dynamic front-mechanism pose belongs to the prior R6 domain. ISO absolute q=20-p remains unchanged. Rear pads/shoes and adjuster motion are audited newly.'},
      'limitations':['A source ledger is not a CAD regeneration or strength proof. The independent rear audit must pass before this source certificate supports baseline evidence reuse.']}
    write(HERE/'source-scope-certificate.json',report);print(json.dumps({'status':report['status'],'source_sha256':report['source_sha256']}))
    return report
if __name__=='__main__':main()
