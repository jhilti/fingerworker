#!/usr/bin/env python3
"""Validate current UI captures. Archived or modified-source results cannot pass."""
from pathlib import Path
import hashlib, json
root=Path(__file__).resolve().parents[1]
source=(root/'fingerworker_mvp.fs').read_bytes()
capture=json.loads((root/'review/onshape-full-review.json').read_text())
fnv=2166136261
for c in source.decode(): fnv=((fnv^ord(c))*16777619)&0xffffffff
sha=hashlib.sha256(source).hexdigest()
assert f'{fnv:08x}'==capture['source_fnv1a32'] and sha==capture['cad_source_sha256'],'Source changed: fresh Onshape captures required'
expected={(15,0,True,False),(0,0,True,False),(30,0,True,False),(30,2,True,False),(0,2,True,False),(15,1,True,False),(30,2,False,False),(13,2,False,True),(15,0,False,True)}
seen=set(); results=[]
for c in capture['cases']:
 key=(c['travel_mm'],c['preload_mm'],c['light'],c['isometric']);assert key not in seen;seen.add(key)
 rows=c['rows'];assert len(rows)==43 and len({x['pair'] for x in rows})==43
 assert all(x['pose_mm']==c['travel_mm'] and x['interferences']==0 and 'SKIPPED' not in x['status'] for x in rows)
 electronics=[x for x in rows if x['pair'].startswith(('Electronics ','Battery /','USB approach /'))]
 assert len(electronics)==7 and all(x['status']=='CLEAR' and not x['unclassified'] for x in electronics)
 results.append({**{k:v for k,v in c.items() if k!='rows'},'selected_pairs':43,'solid_interferences':0,'mechanical_contact_review_pairs':[x['pair'] for x in rows if x['unclassified']],'electronics_gaps_mm':{x['pair']:x['gap_mm'] for x in electronics}})
assert seen==expected
report={'study':'Current Onshape source: sampled solid collision review; not manufacturing release','cad_source_sha256':sha,'source_capture':'onshape-full-review.json','parameters':{'hand':'illustrative, enabled','electronics':True},'part_count':103,'configuration_results':results,'pose_results':[c for c in results if c['preload_mm']==0 and c['light'] and not c['isometric']], 'limitations':['9 discrete configurations, not a continuous sweep or tolerance/deformation analysis.','Contact pairs remain REVIEW; no blanket clearance assertion for intentional contacts.','0.6 mm housing/mechanism minimum is nominal, not a validated FDM clearance.','Illustrative hand results do not resolve conflicts with the real scan.','Electronics mounting, harness, battery retention, sensor capture, strength and electrical behavior are not released.'],'manufacturing_release':False}
(root/'review/electronics-packaging-validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(f'PASS: {len(results)} configurations x 43 selected groups; zero solid interference; all 63 electronics groups CLEAR.')
