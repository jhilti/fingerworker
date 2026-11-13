#!/usr/bin/env python3
"""Compact index to the full R2 native geometry evidence; no extra tests."""
import json
from pathlib import Path
import validate_finished as v

report=json.loads((v.HERE/'validation.json').read_text())
inventory=json.loads((v.HERE/'native-step-inventory.json').read_text())
source_fit=json.loads((v.HERE/'source-fit-certificate.json').read_text())
m=report['manifest']
archives=[m['assembly']]+[pose['assembly'] for pose in m['native_poses']]
summary={
    'status':report['status'],
    'scope':'Nominal native CAD geometry, configured motion and stated finite service paths; 500 N is a design target, not a qualified printed working-load rating',
    'source_sha256':m['native_provenance']['feature_source_sha256'],
    'native_provenance':m['native_provenance'],
    'operating_domain':m['configuration_domain_description'],
    'domain_vertices_stroke_preload_mm':m['configuration_domain_vertices_stroke_preload_mm'],
    'manual_setup_required':'After every preload change, reset H10 click cam by the same axial amount in the negative X direction; check switch operation and relock. No automatic coupling is modeled.',
    'native_neutral_inventory':{'device':len(m['expected_device_refs']),'electronics_references':m['expected_electronics_count'],'total':len(report['mesh_inventory'])},
    'native_archives':[{'path':p,'sha256':v.sha(p)} for p in archives],
    'native_step':{'path':inventory['native_step'],'sha256':inventory['native_step_sha256'],'solids':inventory['native_step_solids'],'valid_positive_solids':inventory['valid_positive_solids'],'status':inventory['status']},
    'baseline_scope_comparison':next(row for row in report['preflight'] if row['name'].startswith('Print reinforcement scope')),
    'failed_checks':report['failed_checks'],'unresolved_checks':report['unresolved_checks'],'status_counts':report['status_counts'],
    'check_group_counts':{name:len(report[name]) for name in ('static_pairs','continuous_pairs','dimension_checks','material_and_clearance_probes','spring_envelopes','service_sweeps','exact_brep_pairs')},
    'native_poses':[{'key':pose['key'],'status':pose['status'],'pairs_checked':len(pose.get('pairs',[])),'source_motion_checks':len(pose.get('pose_semantics',[]))} for pose in report['native_poses']],
    'sensor_identity':report['sensor_identity'],
    'exact_brep_pairs':report['exact_brep_pairs'],
    'source_fit_status':source_fit['status'],
    'service_changes':{'sensor_yoke_stack':'Forward +X3.5 mm with no initial lift, then +Z40 mm, after all listed removals with preload0.','H15_keeper':'Wristward -X2.0 mm before upward removal.'},
    'evidence_files':{name:v.sha(v.HERE/name) for name in ('manifest.json','validation.json','native-step-inventory.json','source-fit-certificate.json','r2-domain-adapter-check.json')},
    'limitations':report['limitations']+['No manufacturing or physical load/strength/creep/fatigue qualification is issued. Source geometry and selected probes do not establish a global minimum wall.'],
}
if inventory['status']!='PASS' or source_fit['status']!='EXACT_SOURCE_LEVEL_DISJOINTNESS_CERTIFIED':summary['status']='INCOMPLETE'
v.write(v.HERE/'validation-summary.json',summary)
md=f'''# R2 nominal native CAD validation

Status: **{summary['status']}**. Failed checks: **{report['failed_checks']}**. Unresolved checks: **{report['unresolved_checks']}**.

This is nominal geometry evidence. **500 N remains a design target, not a verified working-load rating for the print.** Material, print orientation, layer adhesion, tolerances, creep, fatigue and loaded prototype behavior require physical qualification.

Source SHA256: `{summary['source_sha256']}`.

Immutable checkpoint: [{m['native_provenance'].get('immutable_version_id','pending')}]({m['native_provenance'].get('immutable_version_url','#')}). Neutral ZIP and STEP retain source6c export provenance; an independently checked exact single UI-guard replacement binds their unchanged geometry to final sourced5. Maximum and isometric ZIP exports were generated from final sourced5.

Native model: **52 device solids +53 electronics reference solids =105**. Neutral and both regenerated maximum28/preload2 and isometric13/preload2 configurations are included. The declared legal domain is stroke≥0, preload0–2 mm, stroke+preload≤30 mm. Maximum frame stroke is 30 mm at preload0 and 28 mm at preload2. The complete continuous domain is certified rather than inferred from those native endpoint snapshots.

**Manual setup:** reset the H10 click cam by −preload after each preload change, verify switch operation, and relock. The native source includes this required configured position; it does not create an automatic coupling.

Only P01 and P05 change shape from R1. Four old M4 stop screw/nut previews are removed. All remaining neutral native STL bodies must remain byte-identical to R1, with H15/P04 facet ordering permitted only after exact native triangle-coordinate set identity (no rounding or tolerance) is proved. Integral printed P05 stop faces now return end force through the yoke and sensor. Selected probes measure 14×22 mm broad stop faces, 10×22 mm arm sections, a 6.75 mm reaction wall, 5 mm guides, a 3 mm upper bridge, the driver-access and lead clearances, and the retained 35 mm frame height.

The exact native sensor BRep is checked against the canonical manufacturer STEP. The exact native P02/P03 BRep pair is checked for zero positive overlap. All105 native STEP solids must be valid positive volumes and uniquely correspond to the final neutral STL inventory.

Declared service changes: after the listed removals at preload0, translate the assembled sensor/yoke/pusher stack **forward3.5 mm before lifting40 mm**, with no initial lift. H15 keeper removal requires a **2 mm wristward translation before lift**. The complete prerequisites and all finite pair paths are recorded in the manifest/report.

Full machine-readable evidence: [validation.json](validation.json), [native-step-inventory.json](native-step-inventory.json), [source-fit-certificate.json](source-fit-certificate.json) and the compact [validation-summary.json](validation-summary.json). R2 domain-adapter diagnostics check the new mapping mathematics independently; they are not physical strength evidence.
'''
(v.HERE/'validation-summary.md').write_text(md)
print(json.dumps({k:summary[k] for k in ('status','failed_checks','unresolved_checks','check_group_counts')},indent=2))
