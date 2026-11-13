#!/usr/bin/env python3
"""Compact R5 evidence index; no geometry calculations or result waivers."""
import json
import validate_finished as v
r=json.loads((v.HERE/'validation.json').read_text());m=r['manifest']
i=json.loads((v.HERE/'native-step-inventory.json').read_text());f=json.loads((v.HERE/'source-fit-certificate.json').read_text())
a=json.loads((v.HERE/'reach-fit-audit.json').read_text());d=json.loads((v.HERE/'r5-domain-adapter-check.json').read_text());eq=json.loads((v.HERE/'dynamic-mode-equivalence.json').read_text())
summary={
 'status':r['status'],'scope':'Nominal native CAD, full user/preload/trim domain and finite service geometry; actual switch motion, printed load rating and human comfort remain unqualified',
 'source_sha256':m['native_provenance']['feature_source_sha256'],'native_provenance':m['native_provenance'],
 'changed_existing_parts':['P01 fixed guide extended toX29','P04 stepped-shoe well and vertical clamp slots','P05 integral stop face shortened5mm with primary web/root retained','P060/P061 rigid return bosses','H10 vertical M3x10 clamp','H030/H031 indicative coils adjusted to installed span'],
 'added_part':'P11 guided stepped cam shoe; fifteen printed bodies total',
 'preserved_geometry':'97 existing exact BReps preserve shape; six seats/TPU pads translate5mm toward the palm. All others remain at their original coordinates. Exact four-pad STEP preservation resolves one-ULP STL box quantization without changing collision tolerances.',
 'operating_domain':m['configuration_domain_description'],'domain_vertices_user_preload_trim_mm':m['configuration_domain_vertices_user_preload_trim_mm'],
 'rest_and_endpoint_shift_mm':5.,'usable_dynamic_travel_at_p0_p2_mm':[30.,28.],
 'isometric':{'sleeve_length_mm':m['isometric_sleeve_length_mm'],'user_approach_at_p0_p2_mm':[15.,13.],'actual_carriage_offset':'20-preload','contact_position_shift_from_R4_mm':5.},
 'manual_setup_required':'Physically position P11 to camTrim-preload after each preload change, calibrate the purchased switch and clamp H10. Source poses do not create automatic coupling or guarantee real operating/total travel.',
 'native_neutral_inventory':{'device':len(m['expected_device_refs']),'electronics_references':m['expected_electronics_count'],'total':len(r['mesh_inventory'])},
 'native_archives':[{'path':path,'sha256':v.sha(path),'origin':m['native_provenance']['native_export_origins'][path]} for path in [m['assembly']]+[p['assembly'] for p in m['native_poses']]],
 'native_step':{'path':i['native_step'],'sha256':i['native_step_sha256'],'solids':i['native_step_solids'],'valid_positive_solids':i['valid_positive_solids'],'status':i['status'],'origin':m['native_provenance']['native_export_origins'][i['native_step']]},
 'source_mode_equivalence':{'status':eq['status'],'prior_source_sha256':eq['prior_source_sha256'],'final_source_sha256':eq['final_source_sha256'],'scope':eq['scope']},
 'baseline_scope_comparison':next(x for x in r['preflight'] if x['name'].startswith('R5 reach-fit change scope')),
 'failed_checks':r['failed_checks'],'unresolved_checks':r['unresolved_checks'],'status_counts':r['status_counts'],
 'check_group_counts':{name:len(r[name]) for name in ('static_pairs','continuous_pairs','dimension_checks','material_and_clearance_probes','spring_envelopes','service_sweeps','exact_brep_pairs')},
 'native_poses':[{'key':p['key'],'status':p['status'],'pairs_checked':len(p.get('pairs',[])),'source_motion_checks':len(p.get('pose_semantics',[]))} for p in r['native_poses']],
 'independent_reach_CSG_and_clearance_audit':{'status':a['status'],'checks':len(a['rows']),'checks_passed':sum(x['status']=='PASS' for x in a['rows']),'driver_shank_corridor_pairs':len(a['tool_corridor_pairs']),'preserved_exact_breps':len(a['unchanged_brep_comparison'])},
 'domain_adapter_status':d['status'],'sensor_identity':r['sensor_identity'],'exact_brep_pairs':r['exact_brep_pairs'],'source_fit_status':f['status'],
 'evidence_files':{name:v.sha(v.HERE/name) for name in ('manifest.json','validation.json','native-step-inventory.json','source-fit-certificate.json','reach-fit-audit.json','r5-domain-adapter-check.json','dynamic-mode-equivalence.json')},
 'limitations':r['limitations']+a['limitations']+['500N is a design target, not a verified printed working-load rating.']}
if any([i['status']!='PASS',f['status']!='EXACT_SOURCE_LEVEL_DISJOINTNESS_CERTIFIED',a['status']!='PASS',d['status']!='PASS',eq['status']!='PASS_EXACT_MODE_CONDITIONED_EQUIVALENCE',a['manifest_sha256']!=v.sha(v.HERE/'manifest.json'),r['manifest_sha256']!=v.sha(v.HERE/'manifest.json'),d['validator_sha256']!=v.sha(v.HERE/'validate_finished.py')]):summary['status']='INCOMPLETE'
v.write(v.HERE/'validation-summary.json',summary)
url=m['native_provenance'].get('immutable_version_url');checkpoint=f'[Immutable Onshape R5 ISO81]({url})' if url else 'Immutable checkpoint pending'
text=f'''# R5 reach fit: nominal native validation

**{summary['status']}**; **{r['failed_checks']} failed**, **{r['unresolved_checks']} unresolved**. {checkpoint}.

Final source SHA256: `{summary['source_sha256']}`.

Both dynamic rest/end contact positions move5mm closer while retaining30mm user travel at zero preload and28mm at2mm preload. The user selected81mm isometric sleeves; their13–15mm approach also puts the fixed grip5mm closer than R4. Native exports contain106 solids:53 device parts and53 electronics references, including15 printed parts.

P05 retains its primary web/root and shortens its two stop faces5mm. Four rigid return bosses establish the closer rest. P01 extends the fixed guide to preserve both14mm carriage lands. P04 carries a new stepped P11 shoe with vertical M3x10 H10 clamp. Nominal section witnesses check1.3mm guide roof,2.2mm well rear wall,0.9mm pilot ligaments,0.9mm roller-to-upper-boss height separation,4mm nominal insert engagement and0.5mm pilot-floor reserve. A continuous geometric lower bound gives6.3456mm² under-head support; these dimensions do not qualify clamp strength or insert installation.

Continuous geometry covers u≥0, preload0–2mm, u+preload≤30mm and camTrim−0.8…+0.8mm. P11 must be physically set to camTrim−preload and clamped after preload changes. The source actuator is a manufacturer-drawing approximation; actual operating/total travel, switch click, hardware stock and clamp durability remain unqualified. The new81mm ISO native witness is checked separately.

The five neutral/dynamic inputs retain their original61885 source association. An independently rechecked exact inverse certificate restores the entire old source byte-for-byte and proves that only the isometric conditional branch changes coordinates. Those inputs are reused only for isometricLock=false. The new81mm ISO archive originates from the final source. No blanket final-source export claim is made.

Independent exact STEP CSG reconstructs the seven changed rigid parts and compares all97 otherwise-preserved BReps, six under their declared5mm shift. All106 native STEP solids must be valid positive volumes and uniquely match their native STL bodies. The genuine TE sensor stays unscaled. P02/P03 exact intersection is zero, supported by a separate source separation proof. Four translated return-pad STL boxes have one-ULP coordinate quantization differences; exact STEP preservation and strictly bound box checks resolve that without mesh rounding or a collision waiver.

New nominal installed spring lengths are96–94mm at rest and66mm at full user travel. The separate manufacturer spring study records operating-length reserves; no fatigue or printed-load qualification follows. **500N remains a design target.** Prototype force-path, return-boss, fit, creep, fatigue, comfort, actual wire routing and switch/insert/clamp checks remain required.

See [full checks](validation.json), [exact STEP inventory](native-step-inventory.json), [independent CSG/access audit](reach-fit-audit.json), [mode equivalence](dynamic-mode-equivalence.json) and [evidence index](validation-summary.json).
'''
(v.HERE/'validation-summary.md').write_text(text)
print(json.dumps({k:summary[k] for k in ('status','failed_checks','unresolved_checks','check_group_counts','independent_reach_CSG_and_clearance_audit')},indent=2))
