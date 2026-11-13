#!/usr/bin/env python3
"""Compact R4 evidence index; no geometry calculations or result waivers."""
import json
import validate_finished as v
r=json.loads((v.HERE/'validation.json').read_text());m=r['manifest']
i=json.loads((v.HERE/'native-step-inventory.json').read_text())
f=json.loads((v.HERE/'source-fit-certificate.json').read_text())
a=json.loads((v.HERE/'switch-fit-audit.json').read_text())
d=json.loads((v.HERE/'r2-domain-adapter-check.json').read_text())
summary={
    'status':r['status'],'scope':'Nominal native CAD geometry and source-configured motion/service; manufacturer-drawing switch reconstruction, not factory switch CAD or physical actuation/load qualification',
    'source_sha256':m['native_provenance']['feature_source_sha256'],'native_provenance':m['native_provenance'],
    'only_changed_parts':['P01 switch pedestal/pilots','P04 cam recess/pilots and old nub','H09 drawing-based body/tab/lug reference','H09a approximate lever','H09b nominal roller/approximate motion','H10 nominal M3x8 manual cam'],
    'switch_fit_reference':m['switch_fit_reference'],
    'preserved_geometry':'P05 force web/integral sensing stops, P02/P03 palm7mm fit and all other99 native bodies retain exact geometry from frozen R3.',
    'unchanged_operating_domain':m['configuration_domain_description'],'domain_vertices_stroke_preload_mm':m['configuration_domain_vertices_stroke_preload_mm'],
    'manual_setup_required':'Reset H10 by-preload after every preload change, then calibrate/verify the actual switch operating and total travel and relock. The source pose creates no automatic mechanical coupling.',
    'native_neutral_inventory':{'device':len(m['expected_device_refs']),'electronics_references':m['expected_electronics_count'],'total':len(r['mesh_inventory'])},
    'native_archives':[{'path':path,'sha256':v.sha(path)} for path in [m['assembly']]+[p['assembly'] for p in m['native_poses']]],
    'native_step':{'path':i['native_step'],'sha256':i['native_step_sha256'],'solids':i['native_step_solids'],'valid_positive_solids':i['valid_positive_solids'],'status':i['status']},
    'baseline_scope_comparison':next(x for x in r['preflight'] if x['name'].startswith('R4 switch-fit change scope')),
    'failed_checks':r['failed_checks'],'unresolved_checks':r['unresolved_checks'],'status_counts':r['status_counts'],
    'check_group_counts':{name:len(r[name]) for name in ('static_pairs','continuous_pairs','dimension_checks','material_and_clearance_probes','spring_envelopes','service_sweeps','exact_brep_pairs')},
    'native_poses':[{'key':p['key'],'status':p['status'],'pairs_checked':len(p.get('pairs',[])),'source_motion_checks':len(p.get('pose_semantics',[]))} for p in r['native_poses']],
    'switch_exact_CSG_and_clearance_audit':{'status':a['status'],'checks':len(a['rows']),'checks_passed':sum(x['status']=='PASS' for x in a['rows']),'partial_driver_shank_pairs':len(a['tool_corridor_pairs']),'unchanged_exact_breps':len(a['unchanged_brep_comparison'])},
    'domain_adapter_status':d['status'],'sensor_identity':r['sensor_identity'],'exact_brep_pairs':r['exact_brep_pairs'],'source_fit_status':f['status'],
    'evidence_files':{name:v.sha(v.HERE/name) for name in ('manifest.json','validation.json','native-step-inventory.json','source-fit-certificate.json','switch-fit-audit.json','r2-domain-adapter-check.json')},
    'limitations':r['limitations']+a['limitations']+['500N remains a design target, not a verified printed working-load rating.']}
if i['status']!='PASS' or f['status']!='EXACT_SOURCE_LEVEL_DISJOINTNESS_CERTIFIED' or a['status']!='PASS' or d['status']!='PASS' or a['manifest_sha256']!=v.sha(v.HERE/'manifest.json'):
    summary['status']='INCOMPLETE'
v.write(v.HERE/'validation-summary.json',summary)
version=m['native_provenance'].get('immutable_version_url')
checkpoint=f'Immutable checkpoint: [Onshape R4]({version}).' if version else 'Immutable checkpoint association pending.'
text=f'''# R4 drawing-based switch fit: nominal native validation

Status: **{summary['status']}**. Failed checks: **{r['failed_checks']}**. Unresolved checks: **{r['unresolved_checks']}**.

{checkpoint}

Source SHA256: `{summary['source_sha256']}`.

The SS-01GL2 reference moves +4X/+1Y/+1.5Zmm. H09 includes three solder-tab boxes and a conservative lower-lug strip based on the manufacturer drawing; it is not factory CAD. The fixed-length H09a/H09b lever/roller preview remains an approximate mechanism. The cam uses a nominal M3x8 screw and recessed head with a diameter5.8mm relief. Selected native measurements check the1.3mm guide roof web, raised pedestal, pilot diameters, tabs/lug and other preserved local sections.

Only P01/P04/H09/H09a/H09b/H10 may change from frozen R3. Exact coordinate-set comparison permits facet-order changes without geometric rounding. An independent exact STEP audit reconstructs the six changes by CSG and compares every remaining native BRep with frozen R3. It separately checks three terminal slabs against the intact P05 through full preload, nominal L4 insert engagement and a partial diameter4mm driver-shank corridor. A full screwdriver handle and head socket are not modeled.

All105 native STEP solids must be valid positive volumes and uniquely associated with the52 device and53 electronics reference bodies. The actual TE sensor remains exact and unscaled. Exact P02/P03 intersection is zero; their shared nominal curved/flat interface is supported by a separate source containment proof. The R3 half-round palm fit and complete P05 force path/stops remain unchanged.

Neutral,28mm/preload2mm maximum and13mm/preload2mm isometric exports are checked against declared source motion. Continuous certificates cover stroke≥0, preload0–2mm and stroke+preload≤30mm; all affected static, spring-envelope and finite service paths remain strict. H10 requires manual resetting by−preload after every preload change, actual switch calibration and relocking. The one-mm nominal trip lead is not a guaranteed margin under operating-position tolerance or unknown total travel.

This evidence qualifies nominal CAD geometry only. Actual switch/insert/screw stock, soldering/wire bends/insulation/strain relief, printed fit and durability, hand comfort and force calibration require prototype checks. **500N remains a design target, not a verified printed working-load rating.**

Full evidence: [validation.json](validation.json), [native-step-inventory.json](native-step-inventory.json), [switch-fit-audit.json](switch-fit-audit.json), [source-fit-certificate.json](source-fit-certificate.json), and [validation-summary.json](validation-summary.json).
'''
(v.HERE/'validation-summary.md').write_text(text)
print(json.dumps({key:summary[key] for key in ('status','failed_checks','unresolved_checks','check_group_counts','switch_exact_CSG_and_clearance_audit')},indent=2))
