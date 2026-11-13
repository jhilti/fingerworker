#!/usr/bin/env python3
"""Bind native CAD evidence to the immutable Onshape version and source."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent;STUDY=HERE.parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 version_path=STUDY/'onshape-version.json';version=json.loads(version_path.read_text())
 assert version['version_id'] and version['source_readback_exact'] and version['native_parts']==93
 source=STUDY/'fingerworker_R18_organic_palm.fs';step=STUDY/'native/Flat132_R18_final_AP214.step';archive=STUDY/'native/Flat132_R18_neutral_final.zip'
 assert sha(source)==version['source_sha256'] and sha(step)==version['step_sha256'] and sha(archive)==version['stl_zip_sha256']
 reports={name:json.loads((HERE/name).read_text()) for name in ['native-integration.json','native-section-fidelity.json','native-layer-growth.json','foundation-integration.json']}
 integration=reports['native-integration.json'];sections=reports['native-section-fidelity.json'];growth=reports['native-layer-growth.json'];foundation=reports['foundation-integration.json']
 assert integration['status']=='PASS_NATIVE_R18_INTEGRATION' and not integration['failures']
 assert len(integration['unchanged_native_bodies'])==92 and all(q['status']=='PASS' for q in integration['unchanged_native_bodies'])
 assert sections['status']=='PASS_NATIVE_R18_SECTION_FIDELITY' and len(sections['checks'])==7
 assert growth['native_mesh'] and growth['status'] in ['PASS_GEOMETRIC_LAYER_GROWTH','REVIEW_GEOMETRIC_LAYER_GROWTH']
 assert foundation['status']=='PASS_NATIVE_R17_FOUNDATION'
 for d in [integration,sections,growth]:assert d['source_sha256']==version['source_sha256']
 assert integration['native_step_sha256']==sections['native_step_sha256']==version['step_sha256']
 assert integration['native_zip_sha256']==version['stl_zip_sha256']
 assert integration['foundation_report_sha256']==sha(HERE/'foundation-integration.json')
 for script,report in [('audit_organic_integration.py',integration),('audit_section_fidelity.py',sections),('audit_layer_growth.py',growth)]:assert sha(HERE/script)==report['validator_sha256']
 assert sha(STUDY/'mechanics/organic_palm.py')==integration['generator_sha256']==sections['generator_sha256']
 inv=json.loads((HERE/'native-step-inventory.json').read_text());assert inv['native_step_sha256']==version['step_sha256']
 p01=inv['native_part_correspondence']['P01'];assert p01['native_stl_sha256']==growth['mesh_sha256']==sha(HERE/'native-P01-assembly-mm.stl')
 provisional=json.loads((HERE/'native-provisional-p01-inventory.json').read_text())
 assert provisional['native_step_sha256']==version['step_sha256'] and provisional['native_part_correspondence']['P01']['candidates'][0]['solid_index']==p01['candidates'][0]['solid_index']
 reconstruction_path=STUDY/'mechanics/native-reconstruction-probe.json';reconstruction=json.loads(reconstruction_path.read_text())
 assert reconstruction['native_step_sha256']==version['step_sha256'] and reconstruction['foundation_step_sha256']==foundation['native_step_sha256']
 reconstruction_row=next(q for q in integration['checks'] if q['name']=='Native set reconstruction and disjointness close stock decomposition')
 assert reconstruction_row['independent_proof_sha256']==sha(reconstruction_path) and reconstruction_row['status']=='PASS'
 empty_path=STUDY/'mechanics/native-reconstruction-empty-check.json';empty=json.loads(empty_path.read_text())
 assert empty['native_step_sha256']==version['step_sha256'] and empty['foundation_step_sha256']==foundation['native_step_sha256']
 empty_by_name={q['name']:q for q in empty['results']}
 zero_names=['native_minus_reconstruction','reconstruction_minus_native','added_intersects_foundation','removed_intersects_native']
 assert all(empty_by_name[name]['valid'] and empty_by_name[name]['solid_count']==0 and empty_by_name[name]['face_count']==0 for name in zero_names)
 comparison_path=HERE/'native-local-surface-comparison.json';surface=json.loads(comparison_path.read_text())
 assert surface['source_sha256']==version['source_sha256'] and surface['native_mesh_sha256']==growth['mesh_sha256']
 snapshot=HERE/'onshape-version-at-validation.json';snapshot.write_bytes(version_path.read_bytes())
 result=dict(status='PASS_NATIVE_R18_SOURCE_EXPORT_REPORT_BINDING',version_id=version['version_id'],version_url=version['url'],source_sha256=version['source_sha256'],native_step_sha256=version['step_sha256'],native_zip_sha256=version['stl_zip_sha256'],native_P01_stl_sha256=growth['mesh_sha256'],native_parts=93,unchanged_native_bodies=92,source_readback_exact=True,validator_sha256=sha(__file__),native_version_snapshot=dict(path=str(snapshot),sha256=sha(snapshot)),reports={name:dict(path=str(HERE/name),sha256=sha(HERE/name),status=d['status']) for name,d in reports.items()},native_inventory_sha256=sha(HERE/'native-step-inventory.json'),native_loft_comparison=integration['local_native_loft_comparison'],printability_screen_status=growth['status'],actual_slice_review_required=True,scope='Native CAD source/export/report binding and mechanical interface evidence. G-code support, bridge paths, machine settings and print readiness are separate package checks. A geometric growth REVIEW flag requires actual sliced-path review; it is not relabeled PASS here.')
 result['independent_stock_reconstruction']=dict(sha256=sha(reconstruction_path),evidence=reconstruction)
 result['empty_set_witness']=dict(path=str(empty_path),sha256=sha(empty_path),evidence=empty)
 result['native_local_surface_comparison']=dict(path=str(comparison_path),sha256=sha(comparison_path),evidence=surface,disposition='Informational interstation kernel variation, maximum sampled1.20mm. Native silhouette was visually accepted; native geometry remains authoritative after section, envelope, interface and actual slice checks.')
 result['native_functional_boolean_boundary_tolerance_mm']=integration['native_functional_boolean_boundary_tolerance_mm']
 (HERE/'native-release-binding.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(status=result['status'],version_id=result['version_id'],reports={k:v['status'] for k,v in result['reports'].items()}),indent=2))
if __name__=='__main__':main()
