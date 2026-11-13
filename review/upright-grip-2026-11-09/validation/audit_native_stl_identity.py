#!/usr/bin/env python3
"""Check that every native export member except P01 remains byte-identical."""
from pathlib import Path
import argparse, zipfile, hashlib, json

HERE=Path(__file__).resolve().parent;STUDY=HERE.parent;ROOT=STUDY.parents[1]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ap=argparse.ArgumentParser();ap.add_argument('--source-sha',required=True);args=ap.parse_args()
source=STUDY/'fingerworker_R16_upright_grip.fs';assert sha(source)==args.source_sha
old=ROOT/'review/inboard-straps-2026-11-08/native/Flat132_R15_neutral_final.zip'
new=STUDY/'native/Flat132_R16_neutral_final.zip'
with zipfile.ZipFile(old) as a,zipfile.ZipFile(new) as b:
    oldnames=set(a.namelist());newnames=set(b.namelist());common=oldnames&newnames
    rows=[dict(member=n,sha256=hashlib.sha256(b.read(n)).hexdigest(),identical=a.read(n)==b.read(n)) for n in sorted(common)]
    removed=sorted(oldnames-newnames);added=sorted(newnames-oldnames)
    ok=len(newnames)==93 and len(rows)==92 and all(r['identical'] for r in rows) and len(removed)==len(added)==1 and all(' - P01 ' in n for n in removed+added)
    result=dict(status='PASS_92_UNCHANGED_NATIVE_STLS' if ok else 'FAIL',baseline_archive_sha256=sha(old),native_archive_sha256=sha(new),source_sha256=sha(source),validator_sha256=sha(__file__),native_count=len(newnames),new_members=added,removed_members=removed,checks=rows)
(HERE/'native-stl-identity.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(dict(status=result['status'],native_count=len(newnames),unchanged_count=len(rows)),indent=2))
raise SystemExit(not ok)
