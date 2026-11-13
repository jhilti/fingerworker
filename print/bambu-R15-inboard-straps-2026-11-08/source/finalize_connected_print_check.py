#!/usr/bin/env python3
"""Bind the separately saved connected project and its actual GUI slice audits."""
from pathlib import Path
import json,hashlib,zipfile,xml.etree.ElementTree as ET
P=Path(__file__).resolve().parents[1];V=P/'validation'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ready=P/'Fingerworker_R15_H2D_04mm_PLA_Basic_Print_Ready.3mf'
sliced=V/'Fingerworker_R15_H2D_04mm_PLA_Basic_Print_Ready_verification.gcode.3mf'
baseline=P/'Fingerworker_R15_H2D_04mm_PLA_Inboard_Straps.3mf'
rh,sh=sha(ready),sha(sliced);checks=[];evidence={}
def add(name,ok,**kw):checks.append(dict(name=name,status='PASS' if ok else 'FAIL',**kw))
add('Frozen generic project remains unchanged',sha(baseline)=='860843b3df9f988d67db68bae78e30dd8f2d7fc0fbe8e4c810ef78087e17eaa1')
add('GUI saved project and slice match observed hashes',rh=='b8eeb41a267ef7808fde1a6ee5a036eed1ef9a24f7610044177396576bca23d7' and sh=='d077b2ff3f6340495e3c6914a3aa4bb674d00c2c64635fe523878e370c63e15c')
reports=['connected-geometry-settings-check.json','connected-actual-path-check.json','connected-p04-support-check.json','connected-flow-check.json','connected-gui-check.json']
for filename in reports:
 p=V/filename;d=json.loads(p.read_text());bound=d.get('sliced_archive_sha256',d.get('connected_sliced_archive_sha256'))==sh
 if 'project_sha256' in d:bound=bound and d['project_sha256']==rh
 if 'connected_project_sha256' in d:bound=bound and d['connected_project_sha256']==rh
 add(filename+' passed for this exact ready slice',d['status'].startswith('PASS') and bound,status_reported=d['status'])
 evidence[filename]=dict(path=str(p.resolve()),sha256=sha(p),status=d['status'],checks=len(d.get('checks',[])))
with zipfile.ZipFile(sliced) as z:
 plate=ET.fromstring(z.read('Metadata/slice_info.config')).find('plate');md={m.get('key'):m.get('value') for m in plate.findall('metadata')}
add('GUI slice has no pause or outside-plate warning',md['pause_count']=='0' and md['outside']=='false',pause_count=md['pause_count'],outside=md['outside'])
pathcheck=json.loads((V/'connected-actual-path-check.json').read_text());minimum=min(c['minimum_complete_bead_coverage'] for c in pathcheck['checks'] if 'minimum_complete_bead_coverage' in c)
failures=[c for c in checks if c['status']!='PASS']
result=dict(status='PASS_CONNECTED_R15_PRINT_READY' if not failures else 'FAIL',checks=checks,failures=failures,failed_count=len(failures),connected_project=ready.name,connected_project_sha256=rh,connected_sliced_archive_sha256=sh,baseline_project_sha256=sha(baseline),baseline_native_CAD_source_sha256='97e2010cc17d06eb8648cf278b9aae2fd85b6e909bd657b9b216f3b37748665f',native_R15_version='e8453217d87e9cfdc9a33f65',prediction_seconds=int(md['prediction']),estimate='10 h 49 min 11 s',filament_g=float(md['weight']),filament_m=77.07,used_material='Bambu PLA Basic',used_project_filament=1,used_nozzle='Left 0.4 Standard',AMS_slot_from_GUI='A3',PETG_used=False,printer_job_started=False,minimum_dense_core_bead_coverage=minimum,evidence=evidence,settings_changes=dict(material_preset=['Generic PLA','Bambu PLA Basic @BBL H2D'],standard_nozzle_flow_cap_mm3_s=[12,25],density_g_cm3=[1.24,1.26],part_fan_min_percent=[100,60],part_fan_max_percent=[100,80],aux_fan_percent=[70,75],cooling_slowdown_layer_time_s=[8,4],nozzle_temperature_C=[220,220],textured_PEI_temperature_C=[55,55],flow_ratio=[.98,.98],protected_object_process_support_and_speed_settings='identical',object_brims='all six no_brim / width 0',unused_AMS_inventory='Additional PLA/PETG slots listed but not used'),scope='Narrow validation of connected GUI save and actual GUI slice. All six printable meshes, placements, object settings and effective four modifier volumes match frozen generic project (modifier coordinate round-trip tolerance 0.00001mm). New actual paths directly pass four slot openings, sixteen dense cores, P04 support-contact checks, all first layers, zero brim/skirt and selected material flow cap. Unchanged native CAD/service evidence is reused, not rerun.',path_difference_explanation='Saved GUI project uses the synchronized PLA Basic material preset. P01/P04/P05 model path segmentation differs, and P04 support segmentation differs; aggregate path equality is not claimed. P01/P05 support geometry signatures match generic exactly. Critical changed areas are directly revalidated in the actual GUI slice.',limitations=['Nominal geometry and G-code validation do not prove printed tolerance, strength or adhesion.','Observe P11 first layer on clean textured PEI.','Required support structures still need removal.','GUI Send dialog was prepared, but Send was not clicked.'],validator_sha256=sha(__file__))
(V/'connected-print-check.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(status=result['status'],checks=len(checks),failed_count=len(failures),minimum_dense_core_bead_coverage=minimum,estimate=result['estimate']),indent=2));raise SystemExit(bool(failures))
