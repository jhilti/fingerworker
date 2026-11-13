#!/usr/bin/env python3
"""Publish only a fully audited native R17 print package; no printer operation."""
from pathlib import Path
import argparse,csv,hashlib,json,shutil,zipfile
OUT=Path(__file__).resolve().parents[1];ROOT=OUT.parents[1]
STUDY=ROOT/'review/side-thumb-2026-11-12'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text())
def write(p,d):Path(p).write_text(json.dumps(d,indent=2)+'\n')
def rel(p):return str(Path(p).relative_to(ROOT))
def passed(p):
 d=read(p);assert d['status'].startswith('PASS'),str(p)+' not PASS';return d
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--native-step',type=Path,required=True);ap.add_argument('--native-zip',type=Path,required=True);a=ap.parse_args()
 step=a.native_step.resolve();archive=a.native_zip.resolve();layout=read(OUT/'plate-layout.json');version=read(STUDY/'onshape-version.json')
 source=ROOT/layout['CAD_source_path'];source_sha=sha(source);version_id=layout['native_R17_version']
 assert source_sha==layout['CAD_source_sha256']==version['source_sha256']
 assert version_id==version['version_id'];assert layout['candidate_zero_area_facets_omitted']==0
 assert layout['native_STL_archive_sha256']==sha(archive)
 assert sha(OUT/'source/fingerworker_R17_side_thumb.fs')==source_sha
 native_members={}
 with zipfile.ZipFile(archive) as z:
  for ref in ('P01','P04','P05','P06','P11'):
   members=[n for n in z.namelist() if ' - '+ref+' ' in n and n.endswith('.stl')];assert len(members)==1
   assert hashlib.sha256(z.read(members[0])).hexdigest()==sha(OUT/'source-mm'/(ref+'.stl')),ref+' differs from final native archive'
   native_members[ref]=dict(member=members[0],sha256=sha(OUT/'source-mm'/(ref+'.stl')))
 project=OUT/layout['native_project'];sliced=OUT/'validation'/(project.stem+'_verification.gcode.3mf')
 local_names=['native-project-check','toolpath-check','actual-path-check','connected-flow-check','p04-surface-check','palm-contact-check','side-thumb-check','cli-diagnostics']
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
 assert reports['native-project-check']['status']=='PASS_NATIVE_R17_SIDE_THUMB'
 assert not reports['native-project-check']['candidate']
 assert reports['native-project-check']['CAD_source_sha256']==source_sha
 assert reports['native-project-check']['native_R17_version']==version_id
 replacement_layout=OUT/'replacement-layout.json';rep=read(replacement_layout)
 assert rep['CAD_source_sha256']==source_sha and rep['native_R17_version']==version_id
 assert [r['ref'] for r in rep['placements']]==['P01']
 assert rep['parent_six_part_project_sha256']==sha(project)
 replacement_project=OUT/rep['native_project'];replacement_validation=OUT/'validation/P01-replacement'
 replacement_slice=replacement_validation/(replacement_project.stem+'_verification.gcode.3mf')
 replacement_names=[n for n in local_names if n!='p04-surface-check'];replacement_reports={}
 for name in replacement_names:
  path=replacement_validation/(name+'.json');d=passed(path);replacement_reports[name]=d
  for key in ('layout_sha256',):
   if key in d:assert d[key]==sha(replacement_layout),name+' stale replacement layout'
  for key in ('native_project_sha256','project_sha256','editable_project_sha256'):
   if key in d:assert d[key]==sha(replacement_project),name+' stale replacement project'
  for key in ('sliced_project_sha256','sliced_archive_sha256','sliced_internal_evidence_sha256'):
   if key in d:assert d[key]==sha(replacement_slice),name+' stale replacement slice'
  for key in ('CAD_source_sha256','source_sha256'):
   if key in d:assert d[key]==source_sha,name+' stale replacement source'
  verification[rel(path)]=dict(status=d['status'],sha256=sha(path))
 assert replacement_reports['native-project-check']['object_count']==1
 assert not replacement_reports['palm-contact-check']['candidate']
 rep_seconds=replacement_reports['native-project-check']['estimate_seconds'];rep_grams=replacement_reports['native-project-check']['filament_g']
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
  copy=OUT/'validation'/('cad-R17-'+name+'.json');shutil.copyfile(path,copy)
  cad_verification[rel(path)]=dict(status=d['status'],sha256=sha(path))
  verification[rel(copy)]=dict(status=d['status'],sha256=sha(copy))
 for name,img in [('palm-preview-provenance','P01-contact-supports.png'),('p04-preview-provenance','P04-Stuetzen.png'),('plate-preview-provenance','plate_1.png'),('side-thumb-preview-provenance','P01-side-thumb-supports.png')]:
  path=OUT/'validation'/(name+'.json');d=read(path)
  assert d['layout_sha256']==sha(OUT/'plate-layout.json') and d['sliced_archive_sha256']==sha(sliced) and d['image_sha256']==sha(OUT/'preview'/img)
  assert not d.get('candidate',False)
 for name,img in [('palm-preview-provenance','P01-contact-supports.png'),('plate-preview-provenance','plate_1.png'),('side-thumb-preview-provenance','P01-side-thumb-supports.png')]:
  d=read(replacement_validation/(name+'.json'))
  assert d['layout_sha256']==sha(replacement_layout) and d['sliced_archive_sha256']==sha(replacement_slice) and d['image_sha256']==sha(OUT/'preview/P01-replacement'/img)
  assert not d.get('candidate',False)
 gui=OUT/'validation/gui-check.json';gui_report=None
 if gui.exists():
  d=passed(gui);gui_report=d
  for k in ('project_sha256','opened_project_sha256','native_project_sha256'):
   if k in d:assert d[k]==sha(project),'stale GUI record'
  assert d['source_sha256']==source_sha and d['onshape_version']==version_id
  assert d['active_nozzle']=='left' and d['objects']==6 and d['plates']==1 and not d['printer_job_started']
  verification[rel(gui)]=dict(status=d['status'],sha256=sha(gui))
 replacement_gui=replacement_validation/'gui-check.json'
 if replacement_gui.exists():
  d=passed(replacement_gui)
  assert d['project_sha256']==sha(replacement_project)
  assert d['source_sha256']==source_sha and d['onshape_version']==version_id
  assert d['active_nozzle']=='left' and d['objects']==1 and d['plates']==1 and not d['printer_job_started']
  verification[rel(replacement_gui)]=dict(status=d['status'],sha256=sha(replacement_gui))
 seconds=reports['native-project-check']['estimate_seconds'];grams=reports['native-project-check']['filament_g']
 duration=f'{seconds//3600} h {(seconds%3600)//60:02d} min {seconds%60:02d} s'
 rep_duration=f'{rep_seconds//3600} h {(rep_seconds%3600)//60:02d} min {rep_seconds%60:02d} s'
 gui_sentence=(gui_report.get('summary','Das finale Projekt wurde in Bambu Studio geöffnet und geprüft.') if gui_report else 'Die Schätzung stammt vom vollständigen lokalen Slice; die GUI-Prüfung ist noch nicht enthalten.')
 onshape=f'https://cad.onshape.com/documents/15316cc6370631845af136b2/v/{version_id}/e/d253eb87b70818ebde8215f0'
 package=OUT/(project.stem+'_Package.zip')
 metadata=dict(status='PASS_R17_SIDE_THUMB_DELIVERY',date='2026-11-12',cad_revision='R17',CAD_source_sha256=source_sha,onshape_version=version_id,onshape_url=onshape,native_step_sha256=sha(step),native_zip_sha256=sha(archive),plate_count=1,object_count=6,device_parts=5,unloaded_fixtures=1,estimated_seconds=seconds,estimated_grams=grams,project=rel(project),package=rel(package),verification=verification,CAD_verification=cad_verification,geometry_changes=['P01'],omitted=['P08','P09','H040','H041'],material='Bambu PLA Basic',printer='Bambu Lab H2D',nozzle_mm=.4,nozzle='left',filament_mapping='Manual; all six mapped to 1',brim=False,modifier_count=4,printer_job_started=False,gui_verified=gui.exists(),limitations=['Nominal CAD and sliced paths checked; physical comfort, fit, adhesion, strength and creep remain unqualified.','Q01 is for an unloaded spring-free fit check only.','Machine remains unstarted; final device/material selection remains in Bambu Studio.'])
 metadata.update(replacement_project=rel(replacement_project),replacement_slice=rel(replacement_slice),replacement_estimated_seconds=rep_seconds,replacement_estimated_grams=rep_grams,recommended_project=rel(replacement_project),variants={'complete':dict(project=rel(project),slice=rel(sliced),objects=6,seconds=seconds,grams=grams),'P01_replacement':dict(project=rel(replacement_project),slice=rel(replacement_slice),objects=1,seconds=rep_seconds,grams=rep_grams)})
 metadata.update(gui_verified=gui.exists() or replacement_gui.exists(),gui_variants=dict(complete=gui.exists(),P01_replacement=replacement_gui.exists()))
 write(OUT/'release-metadata.json',metadata)
 write(OUT/'source/native-part-provenance.json',dict(status='EXACT_FIVE_NATIVE_ONSHAPE_MEMBERS',source_sha256=source_sha,onshape_version=version_id,native_archive=rel(archive),native_archive_sha256=sha(archive),members=native_members,Q01=dict(source='Retained R12-compatible unloaded fixed-support fixture; separate Q01 native-fit check',sha256=sha(OUT/'source-mm/Q01.stl'))))
 shutil.copyfile(STUDY/'onshape-version.json',OUT/'source/onshape-version.json')
 write(OUT/'STL-print-oriented/manifest.json',dict(units='mm',scale=1,quantity_each=1,note='Six alternate STL files for individual use. The 3MF already contains all six; do not import them additionally.',parts={r['ref']:dict(file=r['ref']+'.stl',sha256=sha(OUT/'STL-print-oriented'/(r['ref']+'.stl')),source_sha256=sha(OUT/'source-mm'/(r['ref']+'.stl')),rotation_3x3=r['rotation_3x3'],normalization_translation_mm=r['normalization_translation_mm']) for r in layout['placements']}))
 with (OUT/'Druckliste.csv').open('w',newline='') as f:
  writer=csv.writer(f);writer.writerow(['Ref','Menge','Platte','Material','Kategorie','Hinweis','STL'])
  names={'P01':'Rahmen mit aufrechter Handballenauflage und offenen seitlichen Daumenmulden','P04':'Schiebegriff; bestehende Oberflächenorientierung','P05':'Sensorschlitten','P06':'Klickbare hintere Traverse','P11':'Schaltnocke','Q01':'Sensor-Passhilfe; nur federfrei und unbelastet'}
  for r in layout['placements']:
   ref=r['ref'];writer.writerow([ref,1,1,'PLA Basic','Unbelastete Passhilfe' if ref=='Q01' else 'Geräteteil',names[ref],'STL-print-oriented/'+ref+'.stl'])
 (OUT/'README.md').write_text(f'''# Fingerworker R17 – seitliche Daumenmulden

**{project.name}** in Bambu Studio als **Projekt** öffnen. H2D, linke Standarddüse 0,4 mm, Bambu PLA Basic, strukturierte PEI-Platte, 100 % Maßstab. Die Filamentzuordnung ist manuell auf die linke Düse festgelegt. Im Druckdialog das tatsächlich eingelegte PLA zuordnen. Alle Modelle und Stützen verwenden PLA; PETG wird nicht gedruckt.

**Für das vorhandene Gerät genügt P01:** `{replacement_project.name}` druckt nur den neuen Rahmen mit den vier lokalen Gurtsteg-Füllbereichen. Separat geslicet und geprüft: **{rep_duration}, {rep_grams:.2f} g PLA**. Position, Ausrichtung, Material und Prozess entsprechen dem vollständigen Projekt. Die fünf vorhandenen Teile weiterverwenden. Die beiden Projektvarianten sind Alternativen; nicht beide drucken.

**Eine Platte, sechs Stücke, {duration}, {grams:.2f} g PLA** laut vollständigem Bambu-Slice. Fünf Geräteteile P01/P04/P05/P06/P11 plus die unbelastete Passhilfe Q01. Bestehende echte Stangen verwenden. Elektronikwanne, Deckel, gedruckte Stangen und Schrauben/Muttern sind nicht enthalten. Kein Druckauftrag wurde gesendet.

{gui_sentence}

P01 erhält beidseitig offene Daumenmulden in der äußeren Seitenkante. Die Unterseiten der seitlichen Wangen erhalten eine druckbare Schräge; die nach oben offenen Mulden liegen in diesen Wangen. Die aufrechte Gegenfläche, gerundete Krone und bisherigen rückwärtigen Daumenrückhalteflächen aus R16 bleiben erhalten. Griff und Rahmen bleiben ein Teil. Die anderen fünf Druckteile, ihre Anordnung und die vier innenliegenden Öffnungen für zwei 25-mm-Gurte sind unverändert.

Alle sechs Teile sind **ohne Brim** eingerichtet. Erforderliche Stützen bleiben aktiv: unter P01-Gehäusedach und den äußeren Schulterüberständen sowie bei P04/P05. Die Handballen-Gegenfläche, Krone und Daumenmulden haben laut tatsächlichen Druckwegen keinen Stützenkontakt. Kleine Stützen unter den äußersten Schulterlippen entfernen. P04 behält seine geprüfte Lage: Fingerzugfläche oben, Muldenboden als Außenwand. Drucklage und Stützen übernehmen; das Projekt nicht automatisch neu ausrichten.

Vier Wände, 20 % Gyroid, 0,2-mm-Schichten; P11 mit 0,1 mm. P11/Q01 und die vier Gurtsteg-Modifikatoren sind massiv gefüllt. Die Modifikatoren sind Einstellungen, keine zusätzlichen Teile. Die vorhandenen Bambu-PLA-Basic-Werte und die langsameren P04/P06-Oberflächenparameter bleiben erhalten.

Die Datei ist ein editierbares 3MF. `validation/*_verification.gcode.3mf` ist der vollständig geprüfte Slice mit gleicher Geometrie. `STL-print-oriented` enthält dieselben sechs Teile einzeln ausgerichtet, `source-mm` dieselben Teile in Baugruppenkoordinaten; diese Kopien nicht zusätzlich drucken.

[Montage](MONTAGE.md) · [Druckliste](Druckliste.csv) · [Druckprüfung](PRINT_QA_NOTES.md) · [Onshape R17]({onshape})

Zuerst federfrei prüfen. Q01 vor Sensor- und Federmontage entfernen. Reale Passung, Handkomfort, Stützentfernung und Belastbarkeit müssen am Ausdruck beurteilt werden; die Klickhaken ersetzen bei Federlast keine Schraubensicherung.
''')
 (OUT/'MONTAGE.md').write_text('''# R17 – mechanischer Passaufbau

Enthalten: P01, P04, P05, P06, P11 und Q01. Vorhandene echte Stangen verwenden. P01 integriert Handballen-Gegenfläche und Daumenbereiche; kein zusätzliches Handballenteil montieren.

1. Stützen von P01/P04/P05 entfernen. Besonders Gehäusedach, äußere Schulterunterseiten, Stangenbohrungen, Gleitführung und Rastflächen säubern. Handballenfläche und Daumenmulden brauchen laut Slice keine Stützen. Die dünnen umlaufenden Brims entfallen.
2. Federfrei montieren: Q01 mit dem Fuß auf den Boden der Sensortasche und der Rückseite an die feste Abstützung setzen. P05 in Richtung −X über den glatten Ø3-Zapfen schieben, bis es an dessen Schulter liegt. Der Zapfen verriegelt nicht axial; die Teile leicht in Druckrichtung zusammenhalten. Sensor, Federn, Federsitze und Isometriehülsen bleiben dabei ausgebaut.
3. P04 von hinten auf die offene zentrale Führung schieben. Echte Führungsstangen durch die Aufnahmen in die vorderen Sockel einsetzen.
4. P06 von hinten in Richtung −X auf die Stangen schieben. Beide seitlichen Haken einrasten lassen; bei enger Passung leicht nach außen führen. Beide müssen zurückfedern. 30 mm vollen Hub ohne Klemmen prüfen.
5. P11 in seine Führung setzen; erst mit echtem Schalter über H10 M3×10 einstellen und klemmen. Die separate Nocke dient dem Schaltpunktabgleich, nicht einer Vorspannverstellung.

Zum Handtest den Ballen gegen die neue aufrechte Fläche setzen und den Daumen seitlich in die neue offene Mulde legen. Die bisherigen rückwärtigen Rückhalteflächen bleiben ebenfalls verfügbar. Zunächst unbelastet prüfen, ob die Lage, Druckverteilung und das Halten ohne Tisch zur eigenen Hand passen. Kein weiterer Sleeve ist vorgesehen.

**Q01 bleibt ausschließlich eine unbelastete, federfreie Passhilfe.** Vor dem Funktionsaufbau vollständig entfernen: P05 mindestens 12 mm in Richtung +X vom Zapfen abziehen; Q01 40 mm nach oben herausnehmen. Echten Sensorstapel und Stahlhardware verwenden. Für Federbetrieb sind die vier H30 M3×8 mit geeigneten Inserts zur Sicherung der Traverse vorgesehen. Die PLA-Clips dienen der Montage; Belastbarkeit ist nicht durch die CAD-Prüfung freigegeben.

Zum Lösen P06 vollständig entlasten, vorhandene Schrauben entfernen, beide Haken ca. 0,9 mm nach außen führen und die Traverse mindestens 12 mm nach hinten ziehen. Für Sensorservice Federkraft beseitigen und Traverse, Stangen und Federn entfernen; H18/H19 seitlich lösen. Den zusammenhängenden Sensor-/Jochstapel 3,2 mm zum Griff (+X), dann 40 mm nach oben entnehmen.

Zwei echte 25-mm-Gurte mit höchstens 2 mm Einzeldicke verwenden. Den langen Gurt unten um den Gegenstand führen; je ein Ende durch die gegenüberliegenden Schlitze derselben X-Position nach oben stecken. Direkt über den äußeren Plattensteg und außen nach unten zurückführen und am eigenen Gurt befestigen. Doppelte Gurtlagen bleiben außen, kein Band läuft über Griff oder Federn. Zweiten Gurt ebenso montieren. Die rückwärtige Laschenanordnung ist nicht mehr vorgesehen; die vier Schlitze liegen innerhalb der Grundplatte.

Nach dem Druck prüfen: Rastfunktion ohne Weißbruch, leichter voller Hub, frei einsetzbare Stangen, sauber entfernbarer Support und angenehme Daumen-/Ballenflächen. Der Lastpfad und Sensoraufbau bleiben funktional erhalten, sind aber am realen Gerät noch nicht belastungs- oder lebensdauergeprüft.
''')
 (OUT/'PRINT_QA_NOTES.md').write_text(f'''# R17 – Druckprüfung

Geprüfter nativer Onshape-Stand: `{version_id}`, FeatureScript SHA-256 `{source_sha}`. P01 stammt bytegleich aus dem nativen STL-Archiv; die anderen fünf Druckmeshes sind unverändert. Native CAD-, Hub-, Service- und Q01-Prüfungen sind unter `validation/cad-R17-*` gebunden.

Vollständiger lokaler Slice mit Bambu Studio 2.8.2.61: **{duration}, {grams:.2f} g**, eine Platte, sechs Teile, keine Pausen, nur PLA. Linke Düse über manuelle Filamentzuordnung beibehalten. Das editierbare 3MF enthält alle Prozess- und Materialwerte des verbundenen R16-Projekts; nur P01 und der Projektname ändern sich. Die manuelle Zuordnung zur linken Düse bleibt unverändert.

{gui_sentence}

- Meshkoordinaten, Topologie, Transformationen, vier massive Gurtmodifikatoren und alle beibehaltenen Profilwerte geprüft.
- Tatsächliche Extrusionsbahnen auf Druckbettgrenzen und gegenseitigen Abstand geprüft, einschließlich Stützenbreite.
- Keine Brim-/Skirt-Bahnen; zusammenhängende erste Schicht aller sechs Teile gegenüber R16 erhalten.
- Alle vier 25 × 2-mm-Gurtdurchlässe offen; 16 Gurtsteg-Kernbereiche über mindestens 20 Schichten zu mindestens 98 % von nominalen Materialbahnen bedeckt.
- Ganze Stützbahnbreiten und Schichthöhen von Handballenfläche, Krone, Daumenmulden und zentraler Schräge ausgeschlossen. Kleine Stützen unter den äußeren Schulterlippen bleiben außerhalb des Handkontaktbereichs.
- P04-Fingerzugfläche und Muldenboden frei von Stützenkontakt; übrige Gegenwand gezielt gestützt.
- Geschwindigkeiten, Beschleunigungen und Volumenfluss gegen das aktive PLA-Basic-Profil geprüft.

Frisch aus diesen Werkzeugwegen erzeugte Abbildungen: `preview/plate_1.png`, `preview/P01-contact-supports.png`, `preview/P04-Stuetzen.png`. Die zugehörigen Prüfsummen stehen in den Vorschau-Provenienzdateien.

Der offizielle CLI-Lauf beendet sich erfolgreich. Seine unveränderten herstellerspezifischen T1001/T65535/T65279-Parserdiagnosen und Preset-/Düsen-Kompatibilitätswarnungen sind vollständig in `validation/cli-diagnostics.json` dokumentiert und gegen den früheren offiziellen Lauf verglichen; das Log wird nicht als fehlerfrei bezeichnet.

Nominale Geometrie und Druckwege sind geprüft. Haftung, Layerfestigkeit, Dauerlast, Rastzyklen und Handkomfort erfordern den realen Ausdruck. P11 ist klein und ohne Brim; die erste Schicht auf sauberer PEI-Platte beobachten. Q01 nur federfrei verwenden. Kein Druckauftrag wurde gesendet.
''')
 files=[project,replacement_project,replacement_slice,replacement_layout,OUT/'README.md',OUT/'MONTAGE.md',OUT/'PRINT_QA_NOTES.md',OUT/'Druckliste.csv',OUT/'plate-layout.json',OUT/'release-metadata.json',sliced]
 for folder in ['source-mm','STL-print-oriented','profiles','source']:
  files.extend(p for p in (OUT/folder).iterdir() if p.is_file() and p.suffix in ('.stl','.json','.py','.fs'))
 files.extend(OUT/'preview'/n for n in ['plate_1.png','P01-contact-supports.png','P04-Stuetzen.png','P01-side-thumb-supports.png'])
 files.extend(OUT/'validation'/(n+'.json') for n in local_names+['palm-preview-provenance','p04-preview-provenance','plate-preview-provenance','side-thumb-preview-provenance'])
 files.extend(replacement_validation/(n+'.json') for n in replacement_names+['palm-preview-provenance','plate-preview-provenance','side-thumb-preview-provenance'])
 files.extend(OUT/'preview/P01-replacement'/n for n in ['plate_1.png','P01-contact-supports.png','P01-side-thumb-supports.png'])
 files.extend(OUT/'validation'/('cad-R17-'+n+'.json') for n in cad_names)
 if gui.exists():files.append(gui)
 if replacement_gui.exists():files.append(replacement_gui)
 files.extend(OUT/'runtime'/(project.stem+'-'+action+ext) for action in ['import','slice'] for ext in ['.log','.json'])
 files.extend(OUT/'runtime'/(replacement_project.stem+'-'+action+ext) for action in ['import','slice'] for ext in ['.log','.json'])
 files=sorted(set(files));assert all(p.is_file() for p in files)
 manifest=dict(status='SHA256_PACKAGE_PAYLOAD',files={str(p.relative_to(OUT)):sha(p) for p in files},excludes=['SHA256.json itself','External delivery-specification.json and ZIP to avoid cyclic hashes'])
 write(OUT/'SHA256.json',manifest);files.append(OUT/'SHA256.json')
 with zipfile.ZipFile(package,'w',zipfile.ZIP_DEFLATED) as z:
  for path in files:
   info=zipfile.ZipInfo(path.relative_to(OUT).as_posix(),date_time=(2026,11,12,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16;z.writestr(info,path.read_bytes())
 with zipfile.ZipFile(package) as z:
  assert z.testzip() is None
  for name,h in manifest['files'].items():assert hashlib.sha256(z.read(name)).hexdigest()==h
 delivery=dict(metadata,files_sha256={rel(p):sha(p) for p in files+[package]},package_manifest_sha256=sha(OUT/'SHA256.json'),package_payload_files=len(files))
 write(OUT/'delivery-specification.json',delivery)
 print(json.dumps(dict(status=delivery['status'],project=delivery['project'],package=delivery['package'],seconds=seconds,grams=grams,files=len(files)),indent=2))
if __name__=='__main__':main()
