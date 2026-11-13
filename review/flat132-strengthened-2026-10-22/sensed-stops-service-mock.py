from pathlib import Path
import importlib.util,json,hashlib
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('candidate',HERE/'sensed-stops-mock.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
spec=importlib.util.spec_from_file_location('validator',HERE.parent/'flat132-finished-2026-10-22/validation/validate_finished.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
manifest=json.loads((HERE.parent/'flat132-finished-2026-10-22/validation/manifest.json').read_text())
manifest['service_sweeps']=[s for s in manifest['service_sweeps'] if s['name'] in ['Keeper wristward release','Keeper upward removal after wristward release','Sensor-yoke stack forward lead-window release','Sensor-yoke stack final upward removal']]
manifest['motion_overrides']['H10']=[-1,-1]
for s in manifest['service_sweeps']:
 if s['name']=='Keeper wristward release':s['range_mm']=[0,2.0]
 if s['name']=='Keeper upward removal after wristward release':s['initial_translation_mm']=[-2.0,0,0]
 if s['name']=='Sensor-yoke stack forward lead-window release':s['range_mm']=[0,3.5]
 if s['name']=='Sensor-yoke stack final upward removal':s['initial_translation_mm']=[3.5,0,0]
 s['fixed_refs']=[r for r in s['fixed_refs'] if r not in ['H070','H071','H080','H081']]
inputs={r:{'object':o} for r,o in m.parts.items()}
rows=v.service_sweeps(inputs,manifest)
fail=[r for r in rows if r['status'] not in ['CONTINUOUS_CLEARANCE_CERTIFIED','CONTINUOUS_CLEARANCE_AT_NUMERICAL_VOLUME_TOLERANCE','CLEAR_AT_NUMERICAL_TOLERANCE']]
report=dict(status='LOCAL_MESH_SERVICE_HYPOTHESIS_ONLY',proposal_sha256=hashlib.sha256((HERE/'sensed-stops-proposal.fs').read_bytes()).hexdigest(),failure_count=len(fail),failures=fail,rows=rows)
(HERE/'sensed-stops-service-mock.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'service_pair_count':len(rows),'failures':fail},indent=2))
