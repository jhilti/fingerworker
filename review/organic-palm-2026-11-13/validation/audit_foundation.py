#!/usr/bin/env python3
"""Verify actual native R17 foundation before the R18 freeform loft."""
from pathlib import Path
import hashlib,importlib.util,json
import trimesh
HERE=Path(__file__).resolve().parent;STUDY=HERE.parent;ROOT=STUDY.parents[1]
R17=ROOT/'review/side-thumb-2026-11-12'
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
a=module('foundation_audit_r17',R17/'validation/audit_thumb_integration.py');b=a.b
sha=a.sha

def main():
 meta=STUDY/'native-probe/foundation-binding.json';d=json.loads(meta.read_text())
 source=ROOT/d['source'];step=ROOT/d['step'];assert sha(source)==d['source_sha256'] and sha(step)==d['step_sha256']
 assert d['source_sha256']=='98ae2cce0dd16401bd4aaa30de850711286ce56143b0259b5d858895de64e791'
 assert d['source_readback_match'] and d['visible_parts']==93
 assert sha(R17/'fingerworker_R17_side_thumb.fs')=='780dfdbaf9c6ab4bf4bbf3ab3de0dab3f9ac7dc5f8de49cf015c51ee95cc16e4'
 original=(R17/'fingerworker_R17_side_thumb.fs').read_text();corrected=original
 for i in [0,1]:corrected=corrected.replace(f'body(id + "R17Cheek{i}body")',f'body(id + "R17Cheek{i}" + "body")')
 assert source.read_text()==corrected,'Foundation source includes an unexpected change'
 old,baseinv,certs=a.baseline();c=module('foundation_expected_r17',R17/'mechanics/side_thumb.py');expected=c.expected(old)['P01']
 references,_=a.v.load(a.BASE/'native/Flat132_R16_neutral_final.zip',{})
 local=R17/'mechanics/P01_side_thumb.stl'
 references['P01']=dict(mesh=trimesh.load(local,force='mesh'),member='LOCAL R17 reference P01_side_thumb.stl',sha256=sha(local))
 shapes,inventory,_=b.read_step(step);association=b.associate(shapes,inventory,references)
 assert all(q['status']=='PASS' and len(q['candidates'])==1 for q in association.values())
 native={r:shapes[q['candidates'][0]['solid_index']] for r,q in association.items()}
 assert len(native)==len(shapes)==93 and set(native)==set(old)
 delta=a.difference(native['P01'],expected)
 rows=[dict(name='Native foundation P01 equals frozen local R17 CSG',status='PASS' if delta<1e-6 else 'FAIL',symmetric_difference_mm3=delta)]
 identities=[]
 for ref in sorted(set(old)-{'P01'}):
  diff=a.difference(native[ref],old[ref]);identities.append(dict(ref=ref,status='PASS' if diff<1e-6 else 'FAIL',symmetric_difference_mm3=diff))
 rows+=a.checks(native['P01'],dict(native,P01=old['P01']),certs)
 assert sha(source)==d['source_sha256'] and sha(step)==d['step_sha256']
 bad=[q for q in rows+identities if q['status']!='PASS']
 report=dict(status='PASS_NATIVE_R17_FOUNDATION' if not bad else 'FAIL',source_sha256=d['source_sha256'],native_step_sha256=d['step_sha256'],source_binding_sha256=sha(meta),validator_sha256=sha(__file__),baseline_R16_step_sha256=baseinv['native_step_sha256'],baseline_R17_source_sha256=sha(R17/'fingerworker_R17_side_thumb.fs'),checks=rows,unchanged_native_bodies=identities,failures=bad,scope='Intermediate native analytic foundation only. Does not contain R18 organic loft. Part correspondence uses R16 native mesh references plus the reviewed LOCAL R17 P01 mesh; actual STEP solids are then checked exactly.')
 (HERE/'foundation-integration.json').write_text(json.dumps(report,indent=2)+'\n')
 (HERE/'foundation-step-inventory.json').write_text(json.dumps(dict(native_step=str(step),native_step_sha256=sha(step),native_part_correspondence=association,solid_inventory=inventory),indent=2)+'\n')
 print(json.dumps(dict(status=report['status'],checks=len(rows),unchanged=len(identities),P01_difference_mm3=delta,failures=bad),indent=2))
 return bool(bad)
if __name__=='__main__':raise SystemExit(main())
