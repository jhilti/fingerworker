#!/usr/bin/env python3
"""Publish only a fully audited native R16 print package; no printer operation."""
from pathlib import Path
import argparse,csv,hashlib,json,shutil,zipfile
OUT=Path(__file__).resolve().parents[1];ROOT=OUT.parents[1]
STUDY=ROOT/'review/upright-grip-2026-11-09'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text())
def write(p,d):Path(p).write_text(json.dumps(d,indent=2)+'\n')
def rel(p):return str(Path(p).relative_to(ROOT))
def passed(p):
 d=read(p);assert d['status'].startswith('PASS'),str(p)+' not PASS';return d
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--native-step',type=Path,required=True);ap.add_argument('--native-zip',type=Path,required=True);a=ap.parse_args()
 step=a.native_step.resolve();archive=a.native_zip.resolve();layout=read(OUT/'plate-layout.json');version=read(STUDY/'onshape-version.json')
 source=ROOT/layout['CAD_source_path'];source_sha=sha(source);version_id=layout['native_R16_version']
 assert source_sha==layout['CAD_source_sha256']==version['source_sha256']
 assert version_id==version['version_id'];assert layout['candidate_zero_area_facets_omitted']==0
 assert layout['native_STL_archive_sha256']==sha(archive)
 assert sha(OUT/'source/fingerworker_R16_upright_grip.fs')==source_sha
 native_members={}
 with zipfile.ZipFile(archive) as z:
  for ref in ('P01','P04','P05','P06','P11'):
   members=[n for n in z.namelist() if ' - '+ref+' ' in n and n.endswith('.stl')];assert len(members)==1
   assert hashlib.sha256(z.read(members[0])).hexdigest()==sha(OUT/'source-mm'/(ref+'.stl')),ref+' differs from final native archive'
   native_members[ref]=dict(member=members[0],sha256=sha(OUT/'source-mm'/(ref+'.stl')))
 project=OUT/layout['native_project'];sliced=OUT/'validation'/(project.stem+'_verification.gcode.3mf')
 local_names=['native-project-check','toolpath-check','actual-path-check','connected-flow-check','p04-surface-check','palm-contact-check','cli-diagnostics']
 verification={};reports={}
 for name in local_names:
  path=OUT/'validation'/(name+'.json');d=passed(path);reports[name]=d
  for key in ('layout_sha256',):
   if key in d:assert d[key]==sha(OUT/'plate-layout.json'),name+' stale layout'
  for key in ('native_project_sha256','project_sha256','editable_project_sha256'):
   if key in d:assert d[key]==sha(project),name+' stale project'
  for key in ('sliced_project_sha256','sliced_archive_sha256','sliced_internal_evidence_sha256'):
   if key in d:assert d[key]==sha(sliced),name+' stale slice'
  for key in ('CAD_source_sha256','source_sha256'):
   if key in d:assert d[key]==source_sha,name+' stale source'
  verification[rel(path)]=dict(status=d['status'],sha256=sha(path))
 assert not reports['palm-contact-check']['candidate']
 assert reports['native-project-check']['CAD_source_sha256']==source_sha
 assert reports['native-project-check']['native_R16_version']==version_id
 cad_names=['native-geometry','native-motion','service-native','fixture-q01-check','native-stl-identity']
 cad_verification={}
 for name in cad_names:
  path=STUDY/'validation'/(name+'.json');d=passed(path)
  for k in ('source_sha256','CAD_source_sha256'):
   if k in d:assert d[k]==source_sha,name+' stale CAD source'
  for k in ('native_step_sha256','native_assembly_step_sha256'):
   if k in d:assert d[k]==sha(step),name+' stale STEP'
  for k in ('native_zip_sha256','native_archive_sha256','native_stl_archive_sha256'):
   if k in d:assert d[k]==sha(archive),name+' stale ZIP'
  copy=OUT/'validation'/('cad-R16-'+name+'.json');shutil.copyfile(path,copy)
  cad_verification[rel(path)]=dict(status=d['status'],sha256=sha(path))
  verification[rel(copy)]=dict(status=d['status'],sha256=sha(copy))
 for name,img in [('palm-preview-provenance','P01-contact-supports.png'),('p04-preview-provenance','P04-Stuetzen.png'),('plate-preview-provenance','plate_1.png')]:
  path=OUT/'validation'/(name+'.json');d=read(path)
  assert d['layout_sha256']==sha(OUT/'plate-layout.json') and d['sliced_archive_sha256']==sha(sliced) and d['image_sha256']==sha(OUT/'preview'/img)
  assert not d.get('candidate',False)
 gui=OUT/'validation/gui-check.json'
 if gui.exists():
  d=passed(gui)
  for k in ('project_sha256','opened_project_sha256','native_project_sha256'):
   if k in d:assert d[k]==sha(project),'stale GUI record'
  assert d['source_sha256']==source_sha and d['onshape_version']==version_id
  assert d['active_nozzle']=='left' and d['objects']==6 and d['plates']==1 and not d['printer_job_started']
  verification[rel(gui)]=dict(status=d['status'],sha256=sha(gui))
 seconds=reports['native-project-check']['estimate_seconds'];grams=reports['native-project-check']['filament_g']
 duration=f'{seconds//3600} h {(seconds%3600)//60:02d} min {seconds%60:02d} s'
 gui_sentence='Das finale Projekt wurde zusätzlich in Bambu Studio 2.8.2.61 geöffnet und frisch geslicet: eine Platte, sechs Teile, nur PLA 1 auf der linken Düse, rechts leer. Die GUI bestätigt 10 h 59 min und 238,18 g. Die Datei wurde dabei nicht neu gespeichert; kein Druckauftrag wurde gesendet.' if gui.exists() else 'Die Schätzung stammt vom vollständigen lokalen Slice; die GUI-Prüfung ist noch nicht enthalten.'
 onshape=f'https://cad.onshape.com/documents/15316cc6370631845af136b2/v/{version_id}/e/d253eb87b70818ebde8215f0'
 package=OUT/(project.stem+'_Package.zip')
 metadata=dict(status='PASS_R16_UPRIGHT_GRIP_DELIVERY',date='2026-11-09',cad_revision='R16',CAD_source_sha256=source_sha,onshape_version=version_id,onshape_url=onshape,native_step_sha256=sha(step),native_zip_sha256=sha(archive),plate_count=1,object_count=6,device_parts=5,unloaded_fixtures=1,estimated_seconds=seconds,estimated_grams=grams,project=rel(project),package=rel(package),verification=verification,CAD_verification=cad_verification,geometry_changes=['P01'],omitted=['P08','P09','H040','H041'],material='Bambu PLA Basic',printer='Bambu Lab H2D',nozzle_mm=.4,nozzle='left',filament_mapping='Manual; all six mapped to 1',brim=False,modifier_count=4,printer_job_started=False,gui_verified=gui.exists(),limitations=['Nominal CAD and sliced paths checked; physical comfort, fit, adhesion, strength and creep remain unqualified.','Q01 is for an unloaded spring-free fit check only.','Machine remains unstarted; final device/material selection remains in Bambu Studio.'])
 write(OUT/'release-metadata.json',metadata)
 write(OUT/'source/native-part-provenance.json',dict(status='EXACT_FIVE_NATIVE_ONSHAPE_MEMBERS',source_sha256=source_sha,onshape_version=version_id,native_archive=rel(archive),native_archive_sha256=sha(archive),members=native_members,Q01=dict(source='Retained R12-compatible unloaded fixed-support fixture; separate Q01 native-fit check',sha256=sha(OUT/'source-mm/Q01.stl'))))
 shutil.copyfile(STUDY/'onshape-version.json',OUT/'source/onshape-version.json')
 write(OUT/'STL-print-oriented/manifest.json',dict(units='mm',scale=1,quantity_each=1,note='Six alternate STL files for individual use. The 3MF already contains all six; do not import them additionally.',parts={r['ref']:dict(file=r['ref']+'.stl',sha256=sha(OUT/'STL-print-oriented'/(r['ref']+'.stl')),source_sha256=sha(OUT/'source-mm'/(r['ref']+'.stl')),rotation_3x3=r['rotation_3x3'],normalization_translation_mm=r['normalization_translation_mm']) for r in layout['placements']}))
 with (OUT/'Druckliste.csv').open('w',newline='') as f:
  writer=csv.writer(f);writer.writerow(['Ref','Menge','Platte','Material','Kategorie','Hinweis','STL'])
  names={'P01':'Rahmen mit integrierter aufrechter Handballenauflage und gerundeten Daumenschultern','P04':'Schiebegriff; bestehende Oberflächenorientierung','P05':'Sensorschlitten','P06':'Klickbare hintere Traverse','P11':'Schaltnocke','Q01':'Sensor-Passhilfe; nur federfrei und unbelastet'}
  for r in layout['placements']:
   ref=r['ref'];writer.writerow([ref,1,1,'PLA Basic','Unbelastete Passhilfe' if ref=='Q01' else 'Geräteteil',names[ref],'STL-print-oriented/'+ref+'.stl'])
 (OUT/'README.md').write_text(f'''# Fingerworker R16 – integrierter Handballengriff

**{project.name}** in Bambu Studio als **Projekt** öffnen. H2D, linke Standarddüse 0,4 mm, Bambu PLA Basic, strukturierte PEI-Platte, 100 % Maßstab. Die Filamentzuordnung ist manuell auf die linke Düse festgelegt. Im Druckdialog das tatsächlich eingelegte PLA zuordnen. Alle Modelle und Stützen verwenden PLA; PETG wird nicht gedruckt.

**Eine Platte, sechs Stücke, {duration}, {grams:.2f} g PLA** laut vollständigem Bambu-Slice. Fünf Geräteteile P01/P04/P05/P06/P11 plus die unbelastete Passhilfe Q01. Bestehende echte Stangen verwenden. Elektronikwanne, Deckel, gedruckte Stangen und Schrauben/Muttern sind nicht enthalten. Kein Druckauftrag wurde gesendet.

{gui_sentence}

P01 trägt jetzt eine breite aufrechte Gegenfläche zum Drücken, eine gerundete Krone und beidseitige flache Daumenrückhalteflächen. Die alte erhöhte Stufe hinter dem Griff ist entfernt. Griff und Rahmen bleiben ein Teil; keine zusätzlichen Kleinteile oder Schrauben für die Handballenauflage. Die anderen fünf Druckteile und ihre Anordnung bleiben erhalten. Die vier innenliegenden Öffnungen für zwei 25-mm-Gurte sind unverändert.

Alle sechs Teile sind **ohne Brim** eingerichtet. Erforderliche Stützen bleiben aktiv: unter P01-Gehäusedach und den äußeren Schulterüberständen sowie bei P04/P05. Die Handballen-Gegenfläche, Krone und Daumenmulden haben laut tatsächlichen Druckwegen keinen Stützenkontakt. Kleine Stützen unter den äußersten Schulterlippen entfernen. P04 behält seine geprüfte Lage: Fingerzugfläche oben, Muldenboden als Außenwand. Drucklage und Stützen übernehmen; das Projekt nicht automatisch neu ausrichten.

Vier Wände, 20 % Gyroid, 0,2-mm-Schichten; P11 mit 0,1 mm. P11/Q01 und die vier Gurtsteg-Modifikatoren sind massiv gefüllt. Die Modifikatoren sind Einstellungen, keine zusätzlichen Teile. Die vorhandenen Bambu-PLA-Basic-Werte und die langsameren P04/P06-Oberflächenparameter bleiben erhalten.

Die Datei ist ein editierbares 3MF. `validation/*_verification.gcode.3mf` ist der vollständig geprüfte Slice mit gleicher Geometrie. `STL-print-oriented` enthält dieselben sechs Teile einzeln ausgerichtet, `source-mm` dieselben Teile in Baugruppenkoordinaten; diese Kopien nicht zusätzlich drucken.

[Montage](MONTAGE.md) · [Druckliste](Druckliste.csv) · [Druckprüfung](PRINT_QA_NOTES.md) · [Onshape R16]({onshape})

Zuerst federfrei prüfen. Q01 vor Sensor- und Federmontage entfernen. Reale Passung, Handkomfort, Stützentfernung und Belastbarkeit müssen am Ausdruck beurteilt werden; die Klickhaken ersetzen bei Federlast keine Schraubensicherung.
''')
 (OUT/'MONTAGE.md').write_text('''# R16 – mechanischer Passaufbau

Enthalten: P01, P04, P05, P06, P11 und Q01. Vorhandene echte Stangen verwenden. P01 integriert Handballen-Gegenfläche und Daumenbereiche; kein zusätzliches Handballenteil montieren.

1. Stützen von P01/P04/P05 entfernen. Besonders Gehäusedach, äußere Schulterunterseiten, Stangenbohrungen, Gleitführung und Rastflächen säubern. Handballenfläche und Daumenmulden brauchen laut Slice keine Stützen. Die dünnen umlaufenden Brims entfallen.
2. Federfrei montieren: Q01 mit dem Fuß auf den Boden der Sensortasche und der Rückseite an die feste Abstützung setzen. P05 in Richtung −X über den glatten Ø3-Zapfen schieben, bis es an dessen Schulter liegt. Der Zapfen verriegelt nicht axial; die Teile leicht in Druckrichtung zusammenhalten. Sensor, Federn, Federsitze und Isometriehülsen bleiben dabei ausgebaut.
3. P04 von hinten auf die offene zentrale Führung schieben. Echte Führungsstangen durch die Aufnahmen in die vorderen Sockel einsetzen.
4. P06 von hinten in Richtung −X auf die Stangen schieben. Beide seitlichen Haken einrasten lassen; bei enger Passung leicht nach außen führen. Beide müssen zurückfedern. 30 mm vollen Hub ohne Klemmen prüfen.
5. P11 in seine Führung setzen; erst mit echtem Schalter über H10 M3×10 einstellen und klemmen. Die separate Nocke dient dem Schaltpunktabgleich, nicht einer Vorspannverstellung.

Zum Handtest den Ballen gegen die neue aufrechte Fläche setzen und den Daumen an der gerundeten Schulter beziehungsweise flachen Rückhaltefläche anlegen. Zunächst unbelastet prüfen, ob die Lage, Druckverteilung und das Halten ohne Tisch zur eigenen Hand passen. Kein weiterer Sleeve ist vorgesehen.

**Q01 bleibt ausschließlich eine unbelastete, federfreie Passhilfe.** Vor dem Funktionsaufbau vollständig entfernen: P05 mindestens 12 mm in Richtung +X vom Zapfen abziehen; Q01 40 mm nach oben herausnehmen. Echten Sensorstapel und Stahlhardware verwenden. Für Federbetrieb sind die vier H30 M3×8 mit geeigneten Inserts zur Sicherung der Traverse vorgesehen. Die PLA-Clips dienen der Montage; Belastbarkeit ist nicht durch die CAD-Prüfung freigegeben.

Zum Lösen P06 vollständig entlasten, vorhandene Schrauben entfernen, beide Haken ca. 0,9 mm nach außen führen und die Traverse mindestens 12 mm nach hinten ziehen. Für Sensorservice Federkraft beseitigen und Traverse, Stangen und Federn entfernen; H18/H19 seitlich lösen. Den zusammenhängenden Sensor-/Jochstapel 3,2 mm zum Griff (+X), dann 40 mm nach oben entnehmen.

Zwei echte 25-mm-Gurte mit höchstens 2 mm Einzeldicke verwenden. Den langen Gurt unten um den Gegenstand führen; je ein Ende durch die gegenüberliegenden Schlitze derselben X-Position nach oben stecken. Direkt über den äußeren Plattensteg und außen nach unten zurückführen und am eigenen Gurt befestigen. Doppelte Gurtlagen bleiben außen, kein Band läuft über Griff oder Federn. Zweiten Gurt ebenso montieren. Die rückwärtige Laschenanordnung ist nicht mehr vorgesehen; die vier Schlitze liegen innerhalb der Grundplatte.

Nach dem Druck prüfen: Rastfunktion ohne Weißbruch, leichter voller Hub, frei einsetzbare Stangen, sauber entfernbarer Support und angenehme Daumen-/Ballenflächen. Der Lastpfad und Sensoraufbau bleiben funktional erhalten, sind aber am realen Gerät noch nicht belastungs- oder lebensdauergeprüft.
''')
 (OUT/'PRINT_QA_NOTES.md').write_text(f'''# R16 – Druckprüfung

Geprüfter nativer Onshape-Stand: `{version_id}`, FeatureScript SHA-256 `{source_sha}`. P01 stammt bytegleich aus dem nativen STL-Archiv; die anderen fünf Druckmeshes sind unverändert. Native CAD-, Hub-, Service- und Q01-Prüfungen sind unter `validation/cad-R16-*` gebunden.

Vollständiger lokaler Slice mit Bambu Studio 2.8.2.61: **{duration}, {grams:.2f} g**, eine Platte, sechs Teile, keine Pausen, nur PLA. Linke Düse über manuelle Filamentzuordnung beibehalten. Das editierbare 3MF enthält alle Prozess- und Materialwerte des verbundenen R15-Projekts; nur P01, Projektname und die gegen automatische Umzuordnung festgehaltene Düsenwahl ändern sich.

{gui_sentence}

- Meshkoordinaten, Topologie, Transformationen, vier massive Gurtmodifikatoren und alle beibehaltenen Profilwerte geprüft.
- Tatsächliche Extrusionsbahnen auf Druckbettgrenzen und gegenseitigen Abstand geprüft, einschließlich Stützenbreite.
- Keine Brim-/Skirt-Bahnen; zusammenhängende erste Schicht aller sechs Teile gegenüber R15 erhalten.
- Alle vier 25 × 2-mm-Gurtdurchlässe offen; 16 Gurtsteg-Kernbereiche über mindestens 20 Schichten zu mindestens 98 % von nominalen Materialbahnen bedeckt.
- Ganze Stützbahnbreiten und Schichthöhen von Handballenfläche, Krone, Daumenmulden und zentraler Schräge ausgeschlossen. Kleine Stützen unter den äußeren Schulterlippen bleiben außerhalb des Handkontaktbereichs.
- P04-Fingerzugfläche und Muldenboden frei von Stützenkontakt; übrige Gegenwand gezielt gestützt.
- Geschwindigkeiten, Beschleunigungen und Volumenfluss gegen das aktive PLA-Basic-Profil geprüft.

Frisch aus diesen Werkzeugwegen erzeugte Abbildungen: `preview/plate_1.png`, `preview/P01-contact-supports.png`, `preview/P04-Stuetzen.png`. Die zugehörigen Prüfsummen stehen in den Vorschau-Provenienzdateien.

Der offizielle CLI-Lauf beendet sich erfolgreich. Seine unveränderten herstellerspezifischen T1001/T65535/T65279-Parserdiagnosen und Preset-/Düsen-Kompatibilitätswarnungen sind vollständig in `validation/cli-diagnostics.json` dokumentiert und gegen den früheren offiziellen Lauf verglichen; das Log wird nicht als fehlerfrei bezeichnet.

Nominale Geometrie und Druckwege sind geprüft. Haftung, Layerfestigkeit, Dauerlast, Rastzyklen und Handkomfort erfordern den realen Ausdruck. P11 ist klein und ohne Brim; die erste Schicht auf sauberer PEI-Platte beobachten. Q01 nur federfrei verwenden. Kein Druckauftrag wurde gesendet.
''')
 files=[project,OUT/'README.md',OUT/'MONTAGE.md',OUT/'PRINT_QA_NOTES.md',OUT/'Druckliste.csv',OUT/'plate-layout.json',OUT/'release-metadata.json',sliced]
 for folder in ['source-mm','STL-print-oriented','profiles','source']:
  files.extend(p for p in (OUT/folder).iterdir() if p.is_file() and p.suffix in ('.stl','.json','.py','.fs'))
 files.extend(OUT/'preview'/n for n in ['plate_1.png','P01-contact-supports.png','P04-Stuetzen.png'])
 files.extend(OUT/'validation'/(n+'.json') for n in local_names+['palm-preview-provenance','p04-preview-provenance','plate-preview-provenance'])
 files.extend(OUT/'validation'/('cad-R16-'+n+'.json') for n in cad_names)
 if gui.exists():files.append(gui)
 files.extend(OUT/'runtime'/(project.stem+'-'+action+ext) for action in ['import','slice'] for ext in ['.log','.json'])
 files=sorted(set(files));assert all(p.is_file() for p in files)
 manifest=dict(status='SHA256_PACKAGE_PAYLOAD',files={str(p.relative_to(OUT)):sha(p) for p in files},excludes=['SHA256.json itself','External delivery-specification.json and ZIP to avoid cyclic hashes'])
 write(OUT/'SHA256.json',manifest);files.append(OUT/'SHA256.json')
 with zipfile.ZipFile(package,'w',zipfile.ZIP_DEFLATED) as z:
  for path in files:
   info=zipfile.ZipInfo(path.relative_to(OUT).as_posix(),date_time=(2026,11,9,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16;z.writestr(info,path.read_bytes())
 with zipfile.ZipFile(package) as z:
  assert z.testzip() is None
  for name,h in manifest['files'].items():assert hashlib.sha256(z.read(name)).hexdigest()==h
 delivery=dict(metadata,files_sha256={rel(p):sha(p) for p in files+[package]},package_manifest_sha256=sha(OUT/'SHA256.json'),package_payload_files=len(files))
 write(OUT/'delivery-specification.json',delivery)
 print(json.dumps(dict(status=delivery['status'],project=delivery['project'],package=delivery['package'],seconds=seconds,grams=grams,files=len(files)),indent=2))
if __name__=='__main__':main()
