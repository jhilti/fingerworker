#!/usr/bin/env python3
"""Bind R13 native exports to the reviewed exact CSG and frozen R12 solids."""
from pathlib import Path
import argparse, importlib.util, json, hashlib, sys, zipfile
import numpy as np

HERE=Path(__file__).resolve().parent;STUDY=HERE.parent;ROOT=STUDY.parents[1]
sys.path.insert(0,str(ROOT/'review/flat132-click-assembly-2026-11-03/validation'))
# Import by path because this file intentionally has the conventional audit name.
def module(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
rear=module('r12_rear_api',ROOT/'review/simplification-2026-11-03/rear_gate.py')
b=rear.b
sys.path.insert(0,str(ROOT/'review/flat132-reach-fit-2026-10-23/validation'))
import validate_finished as v
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.TopAbs import TopAbs_SOLID,TopAbs_SHELL
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
REMOVED=set()
CHANGED={'P01'}

def load_baseline():
    path=ROOT/'review/simplification-2026-11-03/validation/native-step-inventory.json'
    inv=json.loads(path.read_text());assert sha(inv['native_step'])==inv['native_step_sha256']
    ss,_,_=b.read_step(inv['native_step'])
    return {r:ss[x['candidates'][0]['solid_index']] for r,x in inv['native_part_correspondence'].items()},inv

def difference(a,b_):
    pieces=[b.cut(a,b_),b.cut(b_,a)]
    valid=all(BRepCheck_Analyzer(s).IsValid() for s in pieces)
    return sum(b.volume(s) for s in pieces),valid

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--step',type=Path,required=True);ap.add_argument('--archive',type=Path,required=True);a=ap.parse_args()
    old,inv=load_baseline()
    parts,ignored=v.load(a.archive,{})
    assert not ignored
    shapes,inventory,roots=b.read_step(a.step)
    assoc=b.associate(shapes,inventory,parts)
    assert all(x['status']=='PASS' and len(x['candidates'])==1 for x in assoc.values())
    native={r:shapes[x['candidates'][0]['solid_index']] for r,x in assoc.items()}
    expected=module('r13_candidate',STUDY/'mechanics/simple_palm.py').expected(old)
    rows=[]
    def add(name,ok,**e):rows.append(dict(name=name,status='PASS' if ok else 'FAIL',**e))
    add('Exact revised body inventory',set(native)==set(old) and len(native)==93,count=len(native),removed=sorted(REMOVED))
    add('All native solids valid positive volumes',all(x['valid'] and x['volume_mm3']>0 for x in inventory))
    for ref,want in expected.items():
        delta,valid=difference(native[ref],want)
        add('Independent exact CSG '+ref,valid and delta<=1e-6,ref=ref,symmetric_difference_mm3=delta,boolean_results_valid=valid)
        add('One connected valid solid and shell '+ref,BRepCheck_Analyzer(native[ref]).IsValid() and b.count(native[ref],TopAbs_SOLID)==b.count(native[ref],TopAbs_SHELL)==1)
        print(ref,'exact XOR',delta,flush=True)
    identities=[]
    for ref in sorted(set(native)-CHANGED):
        delta,valid=difference(native[ref],old[ref]);identities.append(dict(ref=ref,status='PASS' if valid and delta<=1e-6 else 'FAIL',symmetric_difference_mm3=delta,boolean_results_valid=valid))
    add('All92 retained other bodies exact R12 identity',len(identities)==92 and all(x['status']=='PASS' for x in identities),count=len(identities))
    for r in sorted(CHANGED):
        for ref,other in native.items():
            if ref==r:continue
            # An overlap of bounding boxes merely selects an exact BRep test.
            separated=np.any(b.bounds(native[r])[1]<b.bounds(other)[0]) or np.any(b.bounds(other)[1]<b.bounds(native[r])[0])
            intersection=None if separated else b.common(native[r],other)
            overlap=0. if separated else b.volume(intersection)
            valid=bool(separated or BRepCheck_Analyzer(intersection).IsValid())
            add('Seated solid separation '+r+'/'+ref,valid and overlap<1e-6,intersection_mm3=overlap,boolean_result_valid=valid)
    refs=sorted(r for r in native if r.startswith('P') and not r.startswith('PCB_'))
    add('Seven printed device bodies',refs==['P01','P04','P05','P06','P08','P09','P11'],refs=refs)
    output=STUDY/'print-mm';output.mkdir(exist_ok=True);manifest={}
    with zipfile.ZipFile(a.archive) as z:
        for ref in refs:
            raw=z.read(parts[ref]['member']);target=output/(ref+'.stl');target.write_bytes(raw)
            manifest[ref]=dict(native_member=parts[ref]['member'],sha256=sha(target),bytes=len(raw))
    source=STUDY/'fingerworker_R13_simple_palm.fs'
    (output/'part-manifest.json').write_text(json.dumps(dict(source_sha256=sha(source),native_zip_sha256=sha(a.archive),units='mm',count=len(refs),parts=manifest,identity='Byte-identical native Onshape STL ZIP members in assembly coordinates.'),indent=2)+'\n')
    (HERE/'native-step-inventory.json').write_text(json.dumps(dict(native_step=str(a.step.resolve()),native_step_sha256=sha(a.step),native_stl_archive_sha256=sha(a.archive),native_part_correspondence=assoc,solid_inventory=inventory),indent=2)+'\n')
    bad=[x for x in rows+identities if x['status']=='FAIL']
    report=dict(status='PASS_EXACT_NATIVE_R13' if not bad else 'FAIL',source_sha256=sha(source),native_step_sha256=sha(a.step),native_zip_sha256=sha(a.archive),validator_sha256=sha(__file__),checks=rows,unchanged_native_breps=identities,failed_count=len(bad),failures=bad,limitations='Nominal geometry only. Source/export association declared by UI operator; no physical strength, PLA creep, snap cycling or fit qualification.')
    (HERE/'native-geometry.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(status=report['status'],native_count=len(native),checks=len(rows),unchanged=len(identities),failures=bad),indent=2))
    return bool(bad)

if __name__=='__main__':raise SystemExit(main())
