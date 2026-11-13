#!/usr/bin/env python3
"""Selected R12 enclosure cleanup: retain R11 clips/lid, omit two stale pilots."""
from pathlib import Path
import hashlib,json,re,sys
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.TopAbs import TopAbs_SOLID
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'review/flat132-click-assembly-2026-11-03/enclosure'))
import build_enclosure as e

def expected_cleanup(old):
    """Accept final R11 native part map; fill only former P10 pilot voids."""
    fills=[e.cylinder(-26.5,y,1.2,3.4,.625) for y in (24,31)]
    return {'P08':e.union([old['P08']]+fills)}

def source_cleanup_patch(source):
    lines=[];removed=[]
    for line in source.splitlines():
        m=re.search(r'"P08_Electronics_tray_(\d+)(?:Cut|Join)?"',line)
        if m and int(m.group(1)) in (21,23):removed.append(line)
        else:lines.append(line)
    assert len(removed)==4,(len(removed),removed)
    result='\n'.join(lines)+'\n'
    assert 'P09_Electronics_lid' in result and 'R11TraylidCatch0' in result
    assert 'R11LidlidHook0' in result
    return result

def main():
    old,inv=e.load();r11=old.copy();r11.update(e.expected(old));del r11['P10']
    new=expected_cleanup(r11)['P08'];before=r11['P08'];checks=[]
    def add(name,ok,**kw):checks.append(dict(name=name,status='PASS' if ok else 'FAIL',**kw))
    add('P08 remains a valid single solid',BRepCheck_Analyzer(new).IsValid() and e.b.count(new,TopAbs_SOLID)==1,solids=e.b.count(new,TopAbs_SOLID))
    added=e.b.cut(new,before);removed=e.b.cut(before,new)
    add('No prior material removed',e.b.volume(removed)<1e-6,removed_mm3=e.b.volume(removed))
    expect=2*3.141592653589793*.625**2*(3.4-1.2)
    add('Only two obsolete pilot volumes filled',abs(e.b.volume(added)-expect)<1e-6,
        added_mm3=e.b.volume(added),analytic_two_cylinders_mm3=expect)
    add('External part bounds unchanged',abs(e.b.bounds(new)-e.b.bounds(before)).max()<1e-7,
        before_bounds_mm=e.b.bounds(before).tolist(),after_bounds_mm=e.b.bounds(new).tolist())
    # Added volumes stay entirely within the existing two short support posts,
    # below the former top plane. No clip, mounting, rail, or access stock moves.
    for ref,target in r11.items():
        if ref=='P08':continue
        ov=e.b.volume(e.b.common(added,target))
        add('Added pilot fill static interference '+ref,ov<1e-6,intersection_mm3=ov)
    result=dict(status='PASS_SELECTED_P08_MICROFEATURE_CLEANUP' if all(c['status']=='PASS' for c in checks) else 'FAIL',
        date='2026-11-03',baseline_R10_native_sha256=inv['native_step_sha256'],
        reconstruction='Exact R11 P08/P09 reconstructed using previously native-validated additive clip stocks',
        changed_refs=['P08'],removed_refs=[],checks=checks,failed=[c for c in checks if c['status']=='FAIL'],
        scope='Two unused M1.6 pilot bores removed from the short wire-support posts. P09, all clips, three optional lid screw posts and both optional frame M2 mounts unchanged.',
        limitations=['Local exact OCP cleanup; final native R12 export must independently match expected_cleanup(old).','No physical PLA fit, flex fatigue or electronics qualification.'])
    (HERE/'enclosure-cleanup-check.json').write_text(json.dumps(result,indent=2)+'\n')
    (HERE/'fingerworker_R12_enclosure_cleanup_candidate.fs').write_text(source_cleanup_patch((ROOT/'fingerworker_mvp.fs').read_text()))
    print(json.dumps(dict(status=result['status'],checks=len(checks),failed=result['failed'],added_mm3=e.b.volume(added)),indent=2))

if __name__=='__main__':main()
