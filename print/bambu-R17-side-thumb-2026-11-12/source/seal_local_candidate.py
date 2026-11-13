#!/usr/bin/env python3
"""Package the explicitly labelled local P01 test while native Onshape sync waits."""
from pathlib import Path
import argparse,hashlib,json,shutil,zipfile
from print_context import OUT,ROOT,LAYOUT,LAYOUT_PATH,V,PREVIEW,PROJECT,SLICED,CANDIDATE,REPLACEMENT
assert CANDIDATE and REPLACEMENT,'This publisher is exclusively for a local one-part candidate'
parser=argparse.ArgumentParser();parser.add_argument('--candidate',action='store_true');parser.add_argument('--replacement',action='store_true');parser.add_argument('--geometry-report',type=Path,action='append',required=True);args=parser.parse_args()
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text())
source=ROOT/LAYOUT['CAD_source_path'];source_sha=sha(source);assert source_sha==LAYOUT['CAD_source_sha256']
assert [r['ref'] for r in LAYOUT['placements']]==['P01']
assert LAYOUT['placements'][0]['source_geometry']=='LOCAL_R17_CANDIDATE_STL'
assert sha(OUT/'source-mm/P01.stl')==LAYOUT['placements'][0]['source_sha256']
names=['native-project-check','toolpath-check','actual-path-check','connected-flow-check','palm-contact-check','side-thumb-check','cli-diagnostics']
verified={};reports={}
for name in names:
 path=V/(name+'.json');d=read(path);assert d['status'].startswith('PASS'),name
 for key in ('layout_sha256',):
  if key in d:assert d[key]==sha(LAYOUT_PATH),name+' stale layout'
 for key in ('native_project_sha256','project_sha256','editable_project_sha256'):
  if key in d:assert d[key]==sha(PROJECT),name+' stale project'
 for key in ('sliced_project_sha256','sliced_archive_sha256','sliced_internal_evidence_sha256'):
  if key in d:assert d[key]==sha(SLICED),name+' stale slice'
 for key in ('source_sha256','CAD_source_sha256'):
  if key in d:assert d[key]==source_sha,name+' stale source'
 verified[str(path.relative_to(ROOT))]=dict(status=d['status'],sha256=sha(path));reports[name]=d
assert reports['native-project-check']['status']=='PASS_LOCAL_R17_PRINT_CANDIDATE' and reports['native-project-check']['candidate']
assert reports['palm-contact-check']['candidate'] and reports['side-thumb-check']['candidate']
geometry=[];supporting_evidence={}
for path in args.geometry_report:
 path=path.resolve();d=read(path)
 assert d['status'].startswith('PASS') or d['status']=='MEASURED_LOCAL_FLOOR_SECTIONS',str(path)
 for key in ('source_sha256','CAD_source_sha256'):
  if key in d:assert d[key]==source_sha,str(path)+' stale geometry source'
 copied=V/('cad-local-'+path.stem+'.json');shutil.copyfile(path,copied);geometry.append(copied)
 target=verified if d['status'].startswith('PASS') else supporting_evidence
 target[str(path.relative_to(ROOT))]=dict(status=d['status'],sha256=sha(path))
seconds=reports['native-project-check']['estimate_seconds'];grams=reports['native-project-check']['filament_g']
duration=f'{seconds//3600} h {(seconds%3600)//60:02d} min {seconds%60:02d} s'
note=OUT/'P01_LOCAL_TEST_CANDIDATE_README.md'
note.write_text(f'''# R17 P01 – lokaler Drucktest

**Lokaler Kandidat; noch kein nativer Onshape-R17-Export.** Die Onshape-Anmeldung und anschließende Übernahme/Exportprüfung stehen aus. Der freigegebene R16-Stand bleibt unverändert.

`{PROJECT.name}` als Projekt in Bambu Studio öffnen. Nur der neue P01-Rahmen wird gedruckt; alle übrigen vorhandenen Geräteteile weiterverwenden. Der Kandidat enthält seitlich offene Daumenmulden und behält die bestehende aufrechte Handballenfläche. Nominelle lokale CAD-Passung sowie die tatsächlichen Druckwege wurden geprüft.

H2D, linke 0,4-mm-Standarddüse, Bambu PLA Basic, strukturierte PEI-Platte, ohne Brim. Die vier lokalen massiven Gurtsteg-Bereiche bleiben erhalten. Erforderliche Stützen bleiben aktiv. Die neue Daumenfläche wurde auf Stützenkontakt und zentrale Außenwand-Neustarts als mögliche Nahtstellen geprüft. Die Datei nicht neu ausrichten oder skalieren.

Separater vollständiger Slice: **{duration}, {grams:.2f} g PLA**. Kein Druckauftrag wurde gesendet. Das tatsächlich eingelegte PLA beim späteren Senden zuordnen. Die `.gcode.3mf` ist der geprüfte Slice, die andere `.3mf` das editierbare Projekt; sie beschreiben denselben einzelnen Druck.

Zunächst federfrei Passung, Hub und Handkomfort prüfen. Vorhandene Stangen und übrige Teile übernehmen. Q01 bleibt ausschließlich eine unbelastete Sensor-Passhilfe. PLA-Klickhaken sind Montagehilfen; die vorhandene Schraubensicherung bleibt für den Federbetrieb erforderlich. Reale Festigkeit und Komfort sind nicht durch die nominale Prüfung qualifiziert.

Lokaler FeatureScript-Stand: `{source_sha}`. Dieser Hash ist kein Nachweis einer Onshape-Synchronisierung.
''')
stl=OUT/'P01_SIDE_THUMB_LOCAL_TEST_CANDIDATE.stl';shutil.copyfile(OUT/'STL-print-oriented/P01.stl',stl)
paths=[PROJECT,SLICED,LAYOUT_PATH,note,stl,source,OUT/'source/side-thumb-print-regions.json']+geometry+[V/(name+'.json') for name in names]
for name,image in [('palm-preview-provenance','P01-contact-supports-candidate.png'),('side-thumb-preview-provenance','P01-side-thumb-supports-candidate.png'),('plate-preview-provenance','plate_1.png')]:
 evidence=V/(name+'.json');d=read(evidence)
 assert d['layout_sha256']==sha(LAYOUT_PATH) and d['sliced_archive_sha256']==sha(SLICED) and d['image_sha256']==sha(PREVIEW/image)
 paths.extend([evidence,PREVIEW/image])
package=OUT/'Fingerworker_R17_P01_Replacement_LOCAL_TEST_CANDIDATE_Package.zip'
with zipfile.ZipFile(package,'w',zipfile.ZIP_DEFLATED) as z:
 for path in paths:
  name=str(path.relative_to(OUT)) if path.is_relative_to(OUT) else 'local-source/'+path.name
  z.write(path,name)
with zipfile.ZipFile(package) as z:assert z.testzip() is None
delivery=dict(status='PASS_LOCAL_R17_P01_PRINT_CANDIDATE',native_onshape_sync=False,CAD_source_sha256=source_sha,source_mesh_sha256=sha(OUT/'source-mm/P01.stl'),project=str(PROJECT.relative_to(ROOT)),package=str(package.relative_to(ROOT)),slice=str(SLICED.relative_to(ROOT)),object_count=1,estimated_seconds=seconds,estimated_grams=grams,verification=verified,supporting_evidence=supporting_evidence,files_sha256={str(p.relative_to(ROOT)):sha(p) for p in paths+[package]},printer_job_started=False,pending=['Onshape sign-in','Native Onshape commit/export identity','Native final CAD/print release'])
(OUT/'local-candidate-delivery.json').write_text(json.dumps(delivery,indent=2)+'\n')
print(json.dumps({k:delivery[k] for k in ['status','project','package','estimated_seconds','estimated_grams']},indent=2))
