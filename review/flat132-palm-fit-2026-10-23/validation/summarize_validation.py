#!/usr/bin/env python3
"""Compact index to complete native R3 palm-fit evidence; no additional tests."""
import json
import validate_finished as v

r=json.loads((v.HERE/'validation.json').read_text());m=r['manifest']
i=json.loads((v.HERE/'native-step-inventory.json').read_text())
f=json.loads((v.HERE/'source-fit-certificate.json').read_text())
comparative=[row for row in r['dimension_checks'] if row['type']=='bounds_difference_from_baseline']
archives=[m['assembly']]+[pose['assembly'] for pose in m['native_poses']]
summary={
    'status':r['status'],
    'scope':'Nominal native CAD geometry and configured motion/service paths; no physical material, retention, comfort or load qualification',
    'source_sha256':m['native_provenance']['feature_source_sha256'],'native_provenance':m['native_provenance'],
    'only_changed_parts':['P02 rigid palm','P03 TPU cap'],
    'nominal_wrist_contact_shift_mm':7.,'nominal_new_wrist_tangent_X_mm':-37.25,
    'nominal_palm_axis_X_Z_mm':[-27.,19.75],
    'native_baseline_bound_comparisons':comparative,
    'contact_shape':'Wrist-facing rigid half-round core and TPU cap, with two outboard front return bands for nominal capture',
    'retention_scope':'Return bands are geometric capture features; assembly flex, pull-off force, tolerances, wear and creep require physical prototype checks.',
    'unchanged_operating_domain':m['configuration_domain_description'],
    'domain_vertices_stroke_preload_mm':m['configuration_domain_vertices_stroke_preload_mm'],
    'manual_setup_required':'Retained R2 requirement: reset H10 click cam by -preload after every preload change, verify switch operation and relock.',
    'native_neutral_inventory':{'device':len(m['expected_device_refs']),'electronics_references':m['expected_electronics_count'],'total':len(r['mesh_inventory'])},
    'native_archives':[{'path':path,'sha256':v.sha(path)} for path in archives],
    'native_step':{'path':i['native_step'],'sha256':i['native_step_sha256'],'solids':i['native_step_solids'],'valid_positive_solids':i['valid_positive_solids'],'status':i['status']},
    'baseline_scope_comparison':next(row for row in r['preflight'] if row['name'].startswith('Palm-fit change scope')),
    'failed_checks':r['failed_checks'],'unresolved_checks':r['unresolved_checks'],'status_counts':r['status_counts'],
    'check_group_counts':{name:len(r[name]) for name in ('static_pairs','continuous_pairs','dimension_checks','material_and_clearance_probes','spring_envelopes','service_sweeps','exact_brep_pairs')},
    'native_poses':[{'key':pose['key'],'status':pose['status'],'pairs_checked':len(pose.get('pairs',[])),'source_motion_checks':len(pose.get('pose_semantics',[]))} for pose in r['native_poses']],
    'sensor_identity':r['sensor_identity'],'exact_brep_pairs':r['exact_brep_pairs'],'source_fit_status':f['status'],
    'evidence_files':{name:v.sha(v.HERE/name) for name in ('manifest.json','validation.json','native-step-inventory.json','source-fit-certificate.json','r2-domain-adapter-check.json')},
    'limitations':r['limitations']+['The 500 N load remains a design target, not a verified printed working-load rating.']
}
if i['status']!='PASS' or f['status']!='EXACT_SOURCE_LEVEL_DISJOINTNESS_CERTIFIED':summary['status']='INCOMPLETE'
v.write(v.HERE/'validation-summary.json',summary)
version=m['native_provenance'].get('immutable_version_url')
checkpoint=f'Immutable checkpoint: [Onshape R3]({version}).' if version else 'Immutable checkpoint association pending.'
md=f'''# R3 half-round palm: nominal native CAD validation

Status: **{summary['status']}**. Failed checks: **{r['failed_checks']}**. Unresolved checks: **{r['unresolved_checks']}**.

{checkpoint}

Source SHA256: `{summary['source_sha256']}`.

The nominal palm wrist tangent moves exactly **7 mm** toward the finger grip, from X−44.25 to X−37.25. The new axis is X−27/Z19.75. P02 retains the wrist-facing half of the radius 7.75 mm rigid core, and P03 uses the corresponding radius 10.25 mm TPU cap. Two 4 mm wide, 2.5 mm deep outboard return bands provide nominal capture around the core flat. Real fit, assembly flex, pull-off force, wear and creep remain prototype checks.

Only P02 and P03 change shape from R2. All remaining frame, mechanism, electronics and hardware bodies retain identical native geometry. Any raw facet-order change requires exact canonical triangle-coordinate identity without rounding or geometric tolerance. There are no added or removed hardware parts. Direct comparisons against the native R2 palm bounds check the 7 mm change.

The native model retains **52 device solids + 53 electronics reference solids = 105**. Neutral, maximum stroke 28 mm/preload 2 mm and isometric stroke 13 mm/preload 2 mm exports are checked. The complete continuous legal domain remains stroke ≥0, preload 0–2 mm, stroke+preload ≤30 mm. The 72 mm finger opening and all R2 reinforcement/stop geometry remain unchanged.

The H10 click cam still requires manual resetting by −preload after each preload change, followed by switch verification and relocking. The source models this configured position; it creates no automatic linkage.

Exact native STEP checks verify the genuine manufacturer sensor remains unchanged, the P02/P03 intersection has zero positive volume, and all 105 STEP solids are valid positive volumes uniquely matched to the native neutral STL inventory. A separate source certificate proves curved-surface and return-band-plane separation. Selected local probes cover the revised contact profile, half-core front, bands, mounting plate and clearances. The inherited configured motion, spring envelopes and finite service paths remain strict.

The evidence is nominal CAD geometry, not a physical load or comfort qualification. **500 N remains a design target rather than a verified working-load rating for the print.**

Full evidence: [validation.json](validation.json), [native-step-inventory.json](native-step-inventory.json), [source-fit-certificate.json](source-fit-certificate.json), and [validation-summary.json](validation-summary.json). The conservative in-memory candidate diagnostic is separate from the final native evidence.
'''
(v.HERE/'validation-summary.md').write_text(md)
print(json.dumps({key:summary[key] for key in ('status','failed_checks','unresolved_checks','check_group_counts')},indent=2))
