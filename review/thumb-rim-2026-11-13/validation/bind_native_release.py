#!/usr/bin/env python3
"""Seal the focused R19 native CAD evidence after measured PASS reports."""
from pathlib import Path
import hashlib,json,shutil
HERE=Path(__file__).resolve().parent;STUDY=HERE.parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def main():
 verpath=STUDY/'onshape-version.json';ver=read(verpath);source=STUDY/'fingerworker_R19_thumb_rim.fs';assert ver['source_sha256']==sha(source) and ver['source_readback_exact'] and ver['native_parts']==94
 integration=read(HERE/'native-integration.json');rim=read(HERE/'native-rim-check.json')
 assert integration['status']=='PASS_NATIVE_R19_INTEGRATION' and rim['status']=='PASS_NATIVE_R19_RIM_CHECK'
 for report in [integration,rim]:
  assert report['source_sha256']==ver['source_sha256'] and report['version_id']==ver['version_id']
  assert report['native_step_sha256']==ver['step_sha256'] and report['native_zip_sha256']==ver['stl_zip_sha256']
 assert len(integration['unchanged_native_bodies'])==90 and all(q['status']=='PASS' for q in integration['unchanged_native_bodies'])
 inv=read(HERE/'native-step-inventory.json');assert inv['native_step_sha256']==ver['step_sha256']==sha(inv['native_step'])
 ver['status']='PASS_NATIVE_REGENERATION_AND_EXPORT_AUDITS';verpath.write_text(json.dumps(ver,indent=2)+'\n');snapshot=HERE/'onshape-version-at-validation.json';shutil.copyfile(verpath,snapshot)
 reports={}
 for name in ['native-integration.json','native-rim-check.json','rim-probe-check.json','native-shape-delta.json']:
  p=HERE/name;d=read(p);assert d['status'].startswith('PASS');reports[name]=dict(path=str(p),sha256=sha(p),status=d['status'])
 native_stls={ref:dict(member=inv['native_part_correspondence'][ref]['native_stl_member'],sha256=inv['native_part_correspondence'][ref]['native_stl_sha256']) for ref in ['P01','P06L','P06R','P08']}
 report=dict(status='PASS_NATIVE_R19_SOURCE_EXPORT_REPORT_BINDING',version_id=ver['version_id'],version_url=ver['url'],source_sha256=ver['source_sha256'],native_step_sha256=ver['step_sha256'],native_zip_sha256=ver['stl_zip_sha256'],native_P01_stl_sha256=native_stls['P01']['sha256'],native_changed_stls=native_stls,native_parts=94,unchanged_native_bodies=90,source_readback_exact=True,native_version_snapshot=dict(path=str(snapshot),sha256=sha(snapshot)),reports=reports,native_inventory_sha256=sha(HERE/'native-step-inventory.json'),baseline_native_release_binding_sha256=integration['baseline_release_binding_sha256'],validator_sha256=sha(__file__),scope='Focused native CAD source/export/interface binding. Required rearM3 and trayM2 screw fastening replaces the removed snap retention. Bambu machine settings, support/contact surfaces and sliced-path printability require separate fresh package checks.',limitations=['No printed comfort, durability, load or insert-retention qualification.','Variable topR2/wristR1 blends preserve the old lower lip; geometric web2.432mm minimum is a CAD dimension, not a strength rating.'])
 (HERE/'native-release-binding.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status=report['status'],sha256=sha(HERE/'native-release-binding.json'),source_sha256=ver['source_sha256']),indent=2))
if __name__=='__main__':main()
