#!/usr/bin/env python3
"""Publish only a fully audited native R19 print package; no printer operation."""
from pathlib import Path
import argparse,csv,hashlib,json,shutil,zipfile
OUT=Path(__file__).resolve().parents[1];ROOT=OUT.parents[1]
STUDY=ROOT/'review/thumb-rim-2026-11-13'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text())
def write(p,d):Path(p).write_text(json.dumps(d,indent=2)+'\n')
def rel(p):return str(Path(p).relative_to(ROOT))
def passed(p):
 d=read(p);assert d['status'].startswith('PASS'),str(p)+' not PASS';return d
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--native-step',type=Path,required=True);ap.add_argument('--native-zip',type=Path,required=True);a=ap.parse_args()
 step=a.native_step.resolve();archive=a.native_zip.resolve();layout=read(OUT/'plate-layout.json');version=read(STUDY/'onshape-version.json')
 source=ROOT/layout['CAD_source_path'];source_sha=sha(source);version_id=layout['native_R19_version']
 assert source_sha==layout['CAD_source_sha256']==version['source_sha256']
 assert version_id==version['version_id'];assert layout['candidate_zero_area_facets_omitted']==0
 assert layout['native_STL_archive_sha256']==sha(archive)
 assert sha(OUT/'source/fingerworker_R19_thumb_rim.fs')==source_sha
 native_members={}
 with zipfile.ZipFile(archive) as z:
  assert len([n for n in z.namelist() if n.endswith('.stl')])==94
  for ref in ('P01','P04','P05','P06L','P06R','P11'):
   members=[n for n in z.namelist() if ' - '+ref+' ' in n and n.endswith('.stl')];assert len(members)==1
   assert hashlib.sha256(z.read(members[0])).hexdigest()==sha(OUT/'source-mm'/(ref+'.stl')),ref+' differs from final native archive'
   native_members[ref]=dict(member=members[0],sha256=sha(OUT/'source-mm'/(ref+'.stl')))
 project=OUT/layout['native_project'];sliced=OUT/'validation'/(project.stem+'_verification.gcode.3mf')
 local_names=['native-project-check','toolpath-check','actual-path-check','connected-flow-check','p04-surface-check','palm-contact-check','side-thumb-check','rear-block-check','cli-diagnostics']
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
 assert reports['native-project-check']['status']=='PASS_NATIVE_R19_THUMB_RIM'
 assert not reports['native-project-check']['candidate']
 assert reports['native-project-check']['CAD_source_sha256']==source_sha
 assert reports['native-project-check']['native_R19_version']==version_id
 replacement_layout=OUT/'replacement-layout.json';rep=read(replacement_layout)
 assert rep['CAD_source_sha256']==source_sha and rep['native_R19_version']==version_id
 assert {r['ref'] for r in rep['placements']}=={'P01','P06L','P06R'}
 assert rep['parent_complete_project_sha256']==sha(project)
 replacement_project=OUT/rep['native_project'];replacement_validation=OUT/'validation/replacement'
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
 assert replacement_reports['native-project-check']['object_count']==3
 assert not replacement_reports['palm-contact-check']['candidate']
 rep_seconds=replacement_reports['native-project-check']['estimate_seconds'];rep_grams=replacement_reports['native-project-check']['filament_g']
 cad_names=['native-integration','native-rim-check','native-release-binding']
 cad_verification={}
 for name in cad_names:
  path=STUDY/'validation'/(name+'.json');d=passed(path)
  for k in ('source_sha256','CAD_source_sha256'):
   if k in d:assert d[k]==source_sha,name+' stale CAD source'
  for k in ('native_step_sha256','native_assembly_step_sha256'):
   if k in d:assert d[k]==sha(step),name+' stale STEP'
  for k in ('native_zip_sha256','native_archive_sha256','native_stl_archive_sha256'):
   if k in d:assert d[k]==sha(archive),name+' stale ZIP'
  copy=OUT/'validation'/('cad-R19-'+name+'.json');shutil.copyfile(path,copy)
  cad_verification[rel(path)]=dict(status=d['status'],sha256=sha(path))
  verification[rel(copy)]=dict(status=d['status'],sha256=sha(copy))
 supplementary={};supplementary_files=[]
 for name,img in [('palm-preview-provenance','P01-contact-supports.png'),('p04-preview-provenance','P04-Stuetzen.png'),('plate-preview-provenance','plate_1.png'),('side-thumb-preview-provenance','P01-side-thumb-supports.png'),('shoulder-preview-provenance','P01-shoulder-bridges.png')]:
  path=OUT/'validation'/(name+'.json');d=read(path)
  assert d['layout_sha256']==sha(OUT/'plate-layout.json') and d['sliced_archive_sha256']==sha(sliced) and d['image_sha256']==sha(OUT/'preview'/img)
  assert not d.get('candidate',False)
 for name,img in [('palm-preview-provenance','P01-contact-supports.png'),('plate-preview-provenance','plate_1.png'),('side-thumb-preview-provenance','P01-side-thumb-supports.png'),('shoulder-preview-provenance','P01-shoulder-bridges.png')]:
  d=read(replacement_validation/(name+'.json'))
  assert d['layout_sha256']==sha(replacement_layout) and d['sliced_archive_sha256']==sha(replacement_slice) and d['image_sha256']==sha(OUT/'preview/replacement'/img)
  assert not d.get('candidate',False)
 gui=OUT/'validation/gui-check.json';gui_report=None
 if gui.exists():
  d=passed(gui);gui_report=d
  for k in ('project_sha256','opened_project_sha256','native_project_sha256'):
   if k in d:assert d[k]==sha(project),'stale GUI record'
  assert d['source_sha256']==source_sha and d['onshape_version']==version_id
  assert d['active_nozzle']=='left' and d['objects']==7 and d['plates']==1 and not d['printer_job_started']
  verification[rel(gui)]=dict(status=d['status'],sha256=sha(gui))
 replacement_gui=replacement_validation/'gui-check.json'
 if replacement_gui.exists():
  d=passed(replacement_gui)
  assert d['project_sha256']==sha(replacement_project)
  assert d['source_sha256']==source_sha and d['onshape_version']==version_id
  assert d['active_nozzle']=='left' and d['objects']==3 and d['plates']==1 and not d['printer_job_started']
  verification[rel(replacement_gui)]=dict(status=d['status'],sha256=sha(replacement_gui))
 seconds=reports['native-project-check']['estimate_seconds'];grams=reports['native-project-check']['filament_g']
 duration=f'{seconds//3600} h {(seconds%3600)//60:02d} min {seconds%60:02d} s'
 rep_duration=f'{rep_seconds//3600} h {(rep_seconds%3600)//60:02d} min {rep_seconds%60:02d} s'
 gui_sentence=(read(replacement_gui).get('summary','Das dreiteilige Ersatzprojekt wurde in Bambu Studio geöffnet und geprüft.') if replacement_gui.exists() else 'Native Onshape-Geometrie und beide vollständigen lokalen Slices sind geprüft. Die abschließende sichtbare Bambu-Studio-Vorschau steht noch aus, (GUI_PENDING_REVIEW). Kein Druckauftrag wurde gesendet.')
 onshape=f'https://cad.onshape.com/documents/15316cc6370631845af136b2/v/{version_id}/e/d253eb87b70818ebde8215f0'
 complete_package=OUT/(project.stem+'_Package.zip')
 replacement_package=OUT/(replacement_project.stem+'_Package.zip')
 package=replacement_package
 metadata=dict(status='PASS_R19_THUMB_RIM_DELIVERY',date='2026-11-13',cad_revision='R19',CAD_source_sha256=source_sha,onshape_version=version_id,onshape_url=onshape,native_step_sha256=sha(step),native_zip_sha256=sha(archive),plate_count=1,object_count=3,device_parts=3,unloaded_fixtures=0,estimated_seconds=rep_seconds,estimated_grams=rep_grams,project=rel(replacement_project),package=rel(replacement_package),verification=verification,CAD_verification=cad_verification,supplementary_evidence=supplementary,geometry_changes=['P01','P06L','P06R','P08'],retired_parts=['P06'],expected_native_parts=94,expected_unchanged_native_parts=90,omitted=['P08','P09','H040','H041'],material='Bambu PLA Basic',printer='Bambu Lab H2D',nozzle_mm=.4,nozzle='left',filament_mapping='Manual left nozzle; all printed models and supports use PLA1',brim=False,modifier_count=4,printer_job_started=False,gui_verified=gui.exists(),limitations=['Nominal CAD and sliced paths checked; physical comfort, fit, adhesion, strength and creep remain unqualified.','Q01 is for an unloaded spring-free fit check only.','Machine remains unstarted; final device/material selection remains in Bambu Studio.'])
 metadata.update(
  primary_variant='replacement',recommended_project=rel(replacement_project),
  replacement_project=rel(replacement_project),replacement_package=rel(replacement_package),replacement_slice=rel(replacement_slice),replacement_estimated_seconds=rep_seconds,replacement_estimated_grams=rep_grams,
  secondary_project=rel(project),secondary_package=rel(complete_package),secondary_slice=rel(sliced),secondary_object_count=7,secondary_estimated_seconds=seconds,secondary_estimated_grams=grams,
  variants={
   'replacement':dict(project=rel(replacement_project),package=rel(replacement_package),slice=rel(replacement_slice),object_count=3,objects=3,estimated_seconds=rep_seconds,estimated_grams=rep_grams,seconds=rep_seconds,grams=rep_grams,gui_verified=replacement_gui.exists()),
   'complete':dict(project=rel(project),package=rel(complete_package),slice=rel(sliced),object_count=7,objects=7,estimated_seconds=seconds,estimated_grams=grams,seconds=seconds,grams=grams,gui_verified=gui.exists())},
  gui_verified=replacement_gui.exists(),gui_status='PASS_GUI_PRIMARY' if replacement_gui.exists() else 'GUI_PENDING_REVIEW',native_verified=True,cli_verified=True,gui_variants=dict(complete=gui.exists(),replacement=replacement_gui.exists()))
 optional_dir=OUT/'optional-electronics';optional_manifest=read(optional_dir/'manifest.json')
 assert optional_manifest['CAD_source_sha256']==source_sha and optional_manifest['native_version']==version_id
 optional_raw=optional_dir/'P08-native-assembly-mm.stl';optional_oriented=optional_dir/'P08-base-down-mm.stl'
 assert sha(optional_raw)==optional_manifest['source_sha256'] and sha(optional_oriented)==optional_manifest['oriented_sha256']
 with zipfile.ZipFile(archive) as native_z:assert native_z.read(optional_manifest['native_archive_member'])==optional_raw.read_bytes()
 metadata['optional_electronics']=dict(status='NATIVE_STL_ONLY_NOT_SLICED',ref='P08',source_stl=rel(optional_raw),print_oriented_stl=rel(optional_oriented),manifest=rel(optional_dir/'manifest.json'),instructions=rel(optional_dir/'README.md'),included_in_mechanical_projects=False,hardware='2xM2x8 screws and2xM2 inserts; see hardware-delta.json',gui_verified=False)
 metadata['required_mechanical_hardware']='4 existing M3x8 screws +4 existing M3 inserts;2 screws per rigid rear block'
 write(OUT/'release-metadata.json',metadata)
 write(OUT/'source/native-part-provenance.json',dict(status='EXACT_SIX_NATIVE_ONSHAPE_MEMBERS',source_sha256=source_sha,onshape_version=version_id,native_archive=rel(archive),native_archive_sha256=sha(archive),members=native_members,Q01=dict(source='Retained R12-compatible unloaded fixed-support fixture; separate Q01 native-fit check',sha256=sha(OUT/'source-mm/Q01.stl'))))
 shutil.copyfile(STUDY/'onshape-version.json',OUT/'source/onshape-version.json')
 write(OUT/'STL-print-oriented/manifest.json',dict(units='mm',scale=1,quantity_each=1,note='Seven alternate STL files for individual use. The 3MF already contains all seven; do not import them additionally.',parts={r['ref']:dict(file=r['ref']+'.stl',sha256=sha(OUT/'STL-print-oriented'/(r['ref']+'.stl')),source_sha256=sha(OUT/'source-mm'/(r['ref']+'.stl')),rotation_3x3=r['rotation_3x3'],normalization_translation_mm=r['normalization_translation_mm']) for r in layout['placements']}))
 with (OUT/'Druckliste.csv').open('w',newline='') as f:
  writer=csv.writer(f);writer.writerow(['Ref','Menge','Platte','Material','Kategorie','Hinweis','STL'])
  names={'P01':'Rahmen mit organischer Handballenauflage und offenen seitlichen Daumenmulden','P04':'Schiebegriff; bestehende Oberflächenorientierung','P05':'Sensorschlitten','P06L':'Hinterer Stangenblock; zwei M3-Schrauben erforderlich','P06R':'Hinterer Stangenblock; zwei M3-Schrauben erforderlich','P11':'Schaltnocke','Q01':'Sensor-Passhilfe; nur federfrei und unbelastet'}
  for r in layout['placements']:
   ref=r['ref'];writer.writerow([ref,1,1,'PLA Basic','Unbelastete Passhilfe' if ref=='Q01' else 'Geräteteil',names[ref],'STL-print-oriented/'+ref+'.stl'])
 hardware_src=STUDY/'latches/hardware-delta.json';shutil.copyfile(hardware_src,OUT/'hardware-delta.json')
 (OUT/'README.md').write_text(f'''# Fingerworker R19 – weichere Daumenränder und feste Stangenhalter

**Empfohlener Ersatzsatz:** `{replacement_project.name}` in Bambu Studio als **Projekt** öffnen. Er enthält P01, P06L und P06R auf einer Platte: **{rep_duration}, {rep_grams:.2f} g PLA** laut geprüftem Slice. Die neue Grundplatte ersetzt P01; die beiden festen Stangenhalter ersetzen gemeinsam die alte P06-Traverse. P04/P05/P11 und vorhandene echte Stangen weiterverwenden. **Vier vorhandene M3×8-Schrauben mit den vier M3-Inserts sind jetzt für die Befestigung erforderlich, je zwei pro Block.**

**Optionaler kompletter mechanischer Satz:** `{project.name}` enthält sieben Stücke auf einer Platte: P01/P04/P05/P06L/P06R/P11 und die unbelastete Passhilfe Q01. Schätzung **{duration}, {grams:.2f} g PLA**. Ersatzsatz und kompletter Satz sind Alternativen; nicht beide drucken.

Beide Projekte: H2D, linke Standarddüse 0,4 mm, Bambu PLA Basic, strukturierte PEI-Platte, 100 % Maßstab, manuelle linke Filamentzuordnung, kein Brim. Alle Modelle und erforderlichen Stützen verwenden PLA. Im späteren Druckdialog das tatsächlich eingelegte PLA zuordnen. Kein Druckauftrag wurde gesendet.

{gui_sentence}

P01 behält die organische Handballenauflage und erhält weichere obere und senkrechte Ränder an beiden Daumenmulden. Die hinteren Rasthaken entfallen; P06L/P06R sind kompakte, feste Stangenhalter ohne Quertraverse und Schnapparme. Ihre flachen Montageflächen liegen beim Druck unten, die Schraublöcher stehen senkrecht. Die native Geometrie, vollständige Druckwege, Kontaktflächen, Gurtöffnungen und Plattenabstände werden mit den beigefügten Berichten gebunden.

Elektronikwanne P08, Deckel P09, gedruckte Stangen und Stahlhardware sind in beiden mechanischen Druckprojekten ausgeschlossen. Die separat bereitgestellte **optionale P08-Wanne** hat feste Schraubohren und benötigt zwei M2×8-Schrauben sowie die passenden vorhandenen M2-Inserts. Sie liegt nur als natives und ausgerichtetes STL im separaten Ordner/ZIP vor; kein geprüfter P08-Slice ist enthalten.

Vier Wände, 20 % Gyroid und 0,2-mm-Schichten bleiben erhalten. P11 wird mit 0,1 mm gedruckt; P11/Q01 und vier lokale Gurtsteg-Modifikatoren sind massiv. Die Modifikatoren sind keine zusätzlichen Teile. Notwendige Stützen unter P01/P04/P05 bleiben; die beiden neuen Stangenblöcke werden ohne Stützen geprüft. Die Ballen- und Daumenkontaktflächen bleiben laut Druckwegprüfung ohne Stützenkontakt.

Die 3MF-Projekte sind editierbar. Die jeweiligen `validation/*_verification.gcode.3mf` enthalten den geprüften Slice. Die STL-Kopien sind Alternativen für Einzelimporte, nicht zusätzliche Druckteile.

[Montage](MONTAGE.md) · [Druckprüfung](PRINT_QA_NOTES.md) · [Onshape R19]({onshape})

Zuerst federfrei montieren und prüfen. Reale Passung, Druckfestigkeit und Handkomfort sind am Ausdruck zu beurteilen. Q01 ist nur eine federfreie, unbelastete Passhilfe.
''')
 (OUT/'MONTAGE.md').write_text('''# R19 – Montage mit festen hinteren Stangenhaltern

1. P01 sowie P06L/P06R drucken. Beim vollständigen Satz zusätzlich P04/P05/P11/Q01 drucken. Stützen von P01/P04/P05 entfernen; Führungen, Stangenbohrungen und Gurtöffnungen säubern. Die alten P06-Schnapphaken und die Quertraverse werden nicht weiterverwendet.
2. Federfrei montieren: Q01 bei Bedarf in die Sensortasche setzen, P05 auf dessen glatten Zapfen schieben. Q01 verriegelt nicht axial und ersetzt keinen belastbaren Sensor. Sensor, Federn, Federsitze und Isometriehülsen für den Passversuch ausgebaut lassen.
3. P04 von hinten in die offene zentrale Führung schieben und die echten Führungsstangen in die vorderen Aufnahmen einsetzen.
4. Die beiden baugleichen hinteren Blöcke auf die Stangen schieben und auf die vorgesehenen Montageflächen setzen. Jeden Block mit zwei vorhandenen H30 M3×8-Schrauben in den bestehenden M3-Inserts befestigen. Die Schrauben sind jetzt Teil der normalen Montage. Es gibt keine einzurastenden Haltearme. Federfrei den vollen Hub auf Leichtgängigkeit prüfen.
5. P11 in seine Führung setzen und den Schaltpunkt erst mit echtem Schalter über H10 M3×10 einstellen. Die Nocke ist keine Vorspannverstellung.

Ballen gegen die organische Fläche setzen; Daumen an den gerundeten seitlichen Muldenrändern auflegen. Lage, Druckverteilung und Griffgefühl zuerst unbelastet beurteilen.

Vor Funktionsbetrieb Q01 entfernen: P05 mindestens 12 mm in +X vom Zapfen abziehen; Q01 nach oben herausnehmen. Den echten Sensoraufbau und die Stahlhardware montieren. Q01 ausschließlich federfrei verwenden.

Zum Service die Federkraft vollständig beseitigen, die vier M3-Befestigungsschrauben lösen und beide hinteren Stangenblöcke abnehmen. Stangen/Federn entfernen; den Sensorstapel über seine vorgesehenen Schrauben lösen und entlang des dokumentierten Servicewegs entnehmen. Die übrigen Führungs- und Sensoranschlüsse bleiben erhalten.

Optional P08: Die überarbeitete Elektronikwanne besitzt feste Ohren statt Clips. Zwei M2-Inserts nominal Ø3,2 × 3 mm in den vorhandenen unteren Blindaufnahmen bei X−26,5/Y±59 bis bündig Z9,5 einsetzen. Von unten mit zwei H14 M2×8-Schrauben befestigen. Geprüfte Schraubenköpfe höchstens Ø3,8 × 1,6 mm; keine Unterlegscheiben in diesem Längenaufbau. Der vorhandene P09-Deckel bleibt verwendbar. Hardwaremaße und Insert-Sitz am realen Teil prüfen.

Zwei echte 25-mm-Gurte mit höchstens 2 mm Einzeldicke durch die vier inneren Schlitze führen. Die Enden über die äußeren Stege zurück nach unten legen und am jeweiligen Gurt sichern. Doppelte Lagen bleiben außen; kein Gurt läuft über beweglichen Griff oder Federn.
''')
 (OUT/'PRINT_QA_NOTES.md').write_text(f'''# R19 – Druckprüfung

Native Onshape-Version `{version_id}`, FeatureScript SHA-256 `{source_sha}`. Die Baugruppe enthält 94 native Teile; die native Integration bindet 90 unveränderte Körper. Geändert sind P01, die zwei neuen P06L/P06R anstelle P06 und die separat behandelte P08-Wanne.

**Ersatzsatz:** drei Objekte, {rep_duration}, {rep_grams:.2f} g PLA. **Mechanischer Komplettsatz:** sieben Objekte, {duration}, {grams:.2f} g PLA. Beide wurden mit dem gepinnten Bambu Studio 2.8.2.61 vollständig neu geslicet. Kein Druckauftrag wurde gesendet.

{gui_sentence}

Geprüft werden native Meshkoordinaten/Topologie, alle Platzierungen, linke PLA-Zuordnung, Prozesswerte, vier Gurtsteg-Modifikatoren, tatsächliche Druckbettgrenzen, Abstände einschließlich Supportbreite, erste Schicht, keine Brims, offene Gurtöffnungen, lokale Füllung und vollständige Modellhöhe. P06L/P06R erhalten eine breite zusammenhängende Auflage und keine Stützen. Ihre vertikalen Schraubdurchlässe und horizontalen Stangenaufnahmen müssen frei bleiben.

Die tatsächlichen Stützbahnen dürfen weder Ballenfläche/Krone noch Daumenmulden und deren gerundete Ränder berühren. P04 behält seine geprüfte Orientierung mit nach oben gerichteter Fingerzugfläche. Die bereits in R18 vorhandenen kleinen inneren Schulterunterseiten werden im neuen Slice auf verankerte Druckbahnen geprüft; eine raue verdeckte Unterseite ist kein Nachweis für eine raue Handkontaktfläche.

Vorschauen und ihre gebundenen Prüfsummen liegen unter `preview` bzw. für den Ersatzsatz unter `preview/replacement`. Native CAD-Berichte und tatsächliche Druckwegprüfungen stehen unter `validation`.

Die offiziellen T1001/T65535/T65279-Parserdiagnosen und Preset-/Düsen-Kompatibilitätswarnungen bleiben vollständig dokumentiert und werden gegen den eingefrorenen R18-Lauf verglichen. Der erfolgreiche Slice wird nicht als diagnosefreies Log bezeichnet.

P08 ist optionales natives STL ohne Sliceprüfung und ohne Zeitschätzung; es ist in keiner mechanischen Druckplatte enthalten. Nominale Geometrie und Druckwege ersetzen keine Prüfung von Haftung, Insert-Sitz, Layerfestigkeit, Dauerlast oder Handkomfort am realen Ausdruck.
''')
 # Separate payloads keep the recommended replacement archive unambiguous.
 common=[OUT/'README.md',OUT/'MONTAGE.md',OUT/'PRINT_QA_NOTES.md',OUT/'release-metadata.json',OUT/'hardware-delta.json']
 for folder in ('profiles','source'):
  common.extend(p for p in (OUT/folder).iterdir() if p.is_file() and p.suffix in ('.json','.py','.fs'))
 common.extend(OUT/'validation'/('cad-R19-'+n+'.json') for n in cad_names)
 common.extend(supplementary_files)
 full_files=common+[project,sliced,OUT/'Druckliste.csv',OUT/'plate-layout.json',OUT/'STL-print-oriented/manifest.json']
 rep_manifest=OUT/'STL-print-oriented/replacement-manifest.json'
 full_stl_manifest=read(OUT/'STL-print-oriented/manifest.json')
 write(rep_manifest,dict(units='mm',scale=1,quantity_each=1,note='Three revised mechanical STL files only. The replacement 3MF already contains it; do not import additionally.',parts={r:full_stl_manifest['parts'][r] for r in ('P01','P06L','P06R')}))
 rep_list=OUT/'Replacement-Druckliste.csv'
 with rep_list.open('w',newline='') as f:
  writer=csv.writer(f);writer.writerow(['Ref','Menge','Platte','Material','Hinweis','STL'])
  for ref in ('P01','P06L','P06R'):writer.writerow([ref,1,1,'PLA Basic','Ersatzteil; die beiden Stangenblöcke benötigen je zwei M3-Schrauben','STL-print-oriented/'+ref+'.stl'])
 rep_files=common+[replacement_project,replacement_slice,replacement_layout,rep_list,rep_manifest]
 for folder in ('source-mm','STL-print-oriented'):
  full_files.extend(OUT/folder/(ref+'.stl') for ref in ('P01','P04','P05','P06L','P06R','P11','Q01'))
  rep_files.extend(OUT/folder/(ref+'.stl') for ref in ('P01','P06L','P06R'))
 full_files.extend(OUT/'preview'/n for n in ('plate_1.png','P01-contact-supports.png','P04-Stuetzen.png','P01-side-thumb-supports.png','P01-shoulder-bridges.png'))
 full_files.extend(OUT/'validation'/(n+'.json') for n in local_names+['palm-preview-provenance','p04-preview-provenance','plate-preview-provenance','side-thumb-preview-provenance','shoulder-preview-provenance'])
 rep_files.extend(replacement_validation/(n+'.json') for n in replacement_names+['palm-preview-provenance','plate-preview-provenance','side-thumb-preview-provenance','shoulder-preview-provenance'])
 rep_files.extend(OUT/'preview/replacement'/n for n in ('plate_1.png','P01-contact-supports.png','P01-side-thumb-supports.png','P01-shoulder-bridges.png'))
 if gui.exists():full_files.append(gui)
 if replacement_gui.exists():rep_files.append(replacement_gui)
 full_files.extend(OUT/'runtime'/(project.stem+'-'+action+ext) for action in ('import','slice') for ext in ('.log','.json'))
 rep_files.extend(OUT/'runtime'/(replacement_project.stem+'-'+action+ext) for action in ('import','slice') for ext in ('.log','.json'))
 (OUT/'manifests').mkdir(exist_ok=True)
 package_manifests={};all_files=set();payload_counts={}
 for variant,zip_path,files in [('replacement',replacement_package,rep_files),('complete',complete_package,full_files)]:
  files=sorted(set(files));assert all(p.is_file() for p in files)
  manifest_path=OUT/'manifests'/(variant+'-SHA256.json')
  manifest=dict(status='SHA256_PACKAGE_PAYLOAD',variant=variant,files={str(p.relative_to(OUT)):sha(p) for p in files},excludes=['SHA256.json itself','External delivery-specification.json and ZIP to avoid cyclic hashes'])
  write(manifest_path,manifest)
  with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED) as z:
   for path in files+[manifest_path]:
    arc='SHA256.json' if path==manifest_path else path.relative_to(OUT).as_posix()
    info=zipfile.ZipInfo(arc,date_time=(2026,11,13,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16;z.writestr(info,path.read_bytes())
  with zipfile.ZipFile(zip_path) as z:
   assert z.testzip() is None
   for name,h in manifest['files'].items():assert hashlib.sha256(z.read(name)).hexdigest()==h
   if variant=='replacement':
    assert not any(n.endswith('/'+r+'.stl') for n in z.namelist() for r in ('P04','P05','P11','Q01'))
    assert project.name not in z.namelist() and str(sliced.relative_to(OUT)) not in z.namelist()
  package_manifests[variant]=dict(path=rel(manifest_path),sha256=sha(manifest_path),package_sha256=sha(zip_path))
  payload_counts[variant]=len(files)+1;all_files.update(files+[manifest_path])
 manifest=dict(status='SHA256_DELIVERY_PAYLOAD',files={str(p.relative_to(OUT)):sha(p) for p in sorted(all_files)},excludes=['SHA256.json itself','External delivery-specification.json and ZIPs to avoid cyclic hashes'])
 write(OUT/'SHA256.json',manifest);all_files.add(OUT/'SHA256.json')
 all_files.update(p for p in optional_dir.iterdir() if p.is_file())
 delivery=dict(metadata,files_sha256={rel(p):sha(p) for p in sorted(all_files|{replacement_package,complete_package})},package_manifest_sha256=sha(OUT/'SHA256.json'),package_manifests=package_manifests,package_payload_files=payload_counts)
 write(OUT/'delivery-specification.json',delivery)
 print(json.dumps(dict(status=delivery['status'],primary=delivery['variants']['replacement'],secondary=delivery['variants']['complete'],package_payload_files=payload_counts),indent=2))
if __name__=='__main__':main()
