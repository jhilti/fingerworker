#!/usr/bin/env python3
"""Compare fresh R11 Onshape STEP/STL to frozen R10 and literal changes."""
from pathlib import Path
from hashlib import sha256
import argparse, importlib.util, json, sys, zipfile
HERE=Path(__file__).resolve().parent;STUDY=HERE.parent;ROOT=STUDY.parents[1]
R10=ROOT/'review/flat132-integrated-palm-2026-11-03'
sys.path.insert(0,str(R10/'validation'))
import audit_native as oldaudit
b=oldaudit.b;v=oldaudit.v
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.TopAbs import TopAbs_SOLID,TopAbs_SHELL
def sha(p):return sha256(Path(p).read_bytes()).hexdigest()
def mod(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def main():
    p=argparse.ArgumentParser();p.add_argument('--step',type=Path,required=True);p.add_argument('--archive',type=Path,required=True);a=p.parse_args()
    inv=json.loads((R10/'validation/native-step-inventory.json').read_text())
    assert sha(inv['native_step'])==inv['native_step_sha256']
    oldshapes,_,_=b.read_step(inv['native_step'])
    old={r:oldshapes[x['candidates'][0]['solid_index']] for r,x in inv['native_part_correspondence'].items()}
    parts,ignored=v.load(a.archive,{})
    shapes,inventory,roots=b.read_step(a.step)
    association=b.associate(shapes,inventory,parts)
    assert not ignored and all(x['status']=='PASS' and len(x['candidates'])==1 for x in association.values())
    native={r:shapes[x['candidates'][0]['solid_index']] for r,x in association.items()}
    removed={'P10','P070a','P070b','P071a','P071b'}
    changed={'P08','P09','P120','P121'}
    rows=[]
    def add(name,ok,**e):rows.append(dict(name=name,status='PASS' if ok else 'FAIL',**e))
    add('Native R11 inventory exactly R10 minus five integrated small bodies',set(native)==set(old)-removed and len(native)==117,native_count=len(native))
    add('All native BReps valid positive solids',all(x['valid'] and x['volume_mm3']>0 for x in inventory))
    expect=mod('r11_enclosure_literal',STUDY/'enclosure/build_enclosure.py').expected(old)
    expect.update(mod('r11_shoes_literal',STUDY/'check_rear_shoes.py').expected(old))
    for ref,want in expect.items():
        delta=b.xor_volume(native[ref],want)
        add('Exact independent R10 plus literal CSG '+ref,delta<=1e-6,ref=ref,symmetric_difference_mm3=delta)
        add('One valid connected solid and shell '+ref,BRepCheck_Analyzer(native[ref]).IsValid() and b.count(native[ref],TopAbs_SOLID)==b.count(native[ref],TopAbs_SHELL)==1)
        print(ref,'XOR',delta,flush=True)
    identities=[]
    for ref in sorted(set(native)-changed):
        delta=b.xor_volume(native[ref],old[ref]);identities.append(dict(ref=ref,status='PASS' if delta<=1e-6 else 'FAIL',symmetric_difference_mm3=delta))
    add('All113 other exact native BReps unchanged',len(identities)==113 and all(x['status']=='PASS' for x in identities),count=len(identities))
    add('Existing printed R10 main frame reusable',next(x for x in identities if x['ref']=='P01')['status']=='PASS')
    add('Existing P04 geometry retained for orientation-only fix',next(x for x in identities if x['ref']=='P04')['status']=='PASS')
    refs=set(json.loads((R10/'print-mm/part-manifest.json').read_text())['parts'])-removed
    output=STUDY/'print-mm';output.mkdir(exist_ok=True);manifest={}
    with zipfile.ZipFile(a.archive) as z:
        for ref in sorted(refs):
            raw=z.read(parts[ref]['member']);target=output/(ref+'.stl');target.write_bytes(raw)
            manifest[ref]=dict(native_member=parts[ref]['member'],output='print-mm/'+target.name,sha256=sha(target),bytes=len(raw))
    source=STUDY/'fingerworker_flat132_PLA_click.fs'
    v.write(output/'part-manifest.json',dict(source_sha256=sha(source),native_zip_sha256=sha(a.archive),units='mm',count=len(refs),identity='Byte-identical fresh native Onshape STL ZIP members; original assembly coordinates.',parts=manifest))
    v.write(HERE/'native-step-inventory.json',dict(status='PASS',native_step=str(a.step.resolve()),native_step_sha256=sha(a.step),native_stl_archive_sha256=sha(a.archive),native_step_solids=len(shapes),solid_inventory=inventory,native_part_correspondence=association))
    failed=[x for x in rows+identities if x['status']=='FAIL']
    result=dict(status='PASS_EXACT_NATIVE_R11' if not failed else 'FAIL',source_sha256=sha(source),native_step_sha256=sha(a.step),native_zip_sha256=sha(a.archive),checks=rows,unchanged_native_breps=identities,failed_count=len(failed),failures=failed,limitations='Nominal BRep geometry. No physical fit, clip force, fatigue, creep or load qualification. Inherited motion is covered by exact set identity of shoes plus old pads and unchanged force-path geometry.')
    v.write(HERE/'native-geometry.json',result)
    print(json.dumps(dict(status=result['status'],checks=len(rows),unchanged=len(identities),print_parts=len(refs),failures=failed),indent=2))
    return bool(failed)
if __name__=='__main__':raise SystemExit(main())
