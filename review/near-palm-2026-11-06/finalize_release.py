#!/usr/bin/env python3
"""Prepare evidence-bound R14 docs, then publish after the six-piece package exists."""
from pathlib import Path
import argparse,csv,hashlib,json,re
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
PACK=ROOT/'print/bambu-R14-near-palm-2026-11-06'
BASE='Fingerworker_R14_H2D_04mm_PLA_Near_Palm'
SOURCE=HERE/'fingerworker_R14_near_palm.fs'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text())
def write(path,value):Path(path).write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n')
def passed(path):
 d=read(path);assert str(d['status']).startswith(('PASS','NATIVE_PROJECT')),(path,d['status'])
 assert not d.get('failures') and not d.get('issues') and not d.get('failed'),path
 assert not d.get('failed_count',d.get('failed_checks',0)),path
 return d

def validate():
 source_hash=sha(SOURCE);version=read(HERE/'onshape-version.json');layout=read(PACK/'plate-layout.json')
 assert source_hash==version['source_sha256']==layout['CAD_source_sha256']
 assert layout['native_R14_version']==version['version_id']
 assert layout['object_count']==6 and layout['plate_count']==1
 assert layout['modifier_count']==4 and len(layout['local_density_modifiers'])==4
 assert {r['ref'] for r in layout['placements']}=={'P01','P04','P05','P06','P11','Q01'}
 names=['native-geometry.json','native-motion.json','service-native.json','fixture-q01-check.json']
 paths=[HERE/'validation'/n for n in names]+[HERE/'mechanics/preflight.json',HERE/'evidence/strap-routing-visual-check.json']
 paths += [PACK/'validation'/n for n in ['native-project-check.json','toolpath-check.json','print-feature-check.json','palm-support-check.json','strap-slot-check.json','strap-routing-check.json','p04-surface-check.json','cli-diagnostics.json','independent-profile-review.json']]
 if (PACK/'validation/connected-gui-check.json').exists():paths.append(PACK/'validation/connected-gui-check.json')
 verified={}
 for p in paths:
  d=passed(p)
  for k in ('source_sha256','CAD_source_sha256'):
   if k in d:assert d[k]==source_hash,(p,k)
  if p.is_relative_to(PACK):
   for k in ('native_sha256','native_project_sha256','native_editable_project_sha256','editable_project_sha256','opened_generic_project_sha256'):
    if k in d:assert d[k]==sha(PACK/(BASE+'.3mf')),(p,k)
   for k in ('native_sliced_archive_sha256','sliced_project_sha256','sliced_archive_sha256','sliced_internal_evidence_sha256'):
    if k in d:assert d[k]==sha(PACK/'validation'/(BASE+'_verification.gcode.3mf')),(p,k)
   if 'layout_sha256' in d:assert d['layout_sha256']==sha(PACK/'plate-layout.json'),p
   if 'native_step_sha256' in d:assert d['native_step_sha256']==sha(HERE/'native/Flat132_R14_final_AP214.step'),p
  verified[str(p.relative_to(ROOT))]={'status':d['status'],'sha256':sha(p)}
 native=read(paths[0]);motion=read(paths[1]);service=read(paths[2]);fixture=read(paths[3]);qa=read(PACK/'validation/native-project-check.json')
 assert len(native['unchanged_native_breps'])==92
 assert native['native_step_sha256']==sha(HERE/'native/Flat132_R14_final_AP214.step')
 assert native['native_zip_sha256']==sha(HERE/'native/Flat132_R14_neutral_final.zip')
 assert motion['native_step_sha256']==native['native_step_sha256']
 assert service['native_archive_sha256']==native['native_zip_sha256']
 assert fixture['native_assembly_step_sha256']==native['native_step_sha256']
 assert qa['native_project_sha256']==sha(PACK/(BASE+'.3mf'))
 assert qa['sliced_project_sha256']==sha(PACK/'validation'/(BASE+'_verification.gcode.3mf'))
 assert qa['all_checks_passed'] and all(qa['checks'].values()) and qa['geometry_and_orientations_preserved']
 geometry=read(HERE/'mechanics/design-specification.json')
 assert geometry['source_sha256']==source_hash and geometry.get('strap_mount'), 'Final palm + strap design required'
 strap=geometry['strap_mount']
 assert strap['slot_count']==4 and strap['position_count']==2
 assert strap['slot_size_mm']==[27,4] and strap['position_x_mm']==[5,80]
 assert strap['slot_center_y_mm']==[-69.5,69.5] and strap['overall_width_mm']==156
 assert strap['strap_width_mm']==25 and strap['strap_thickness_envelope_mm']==2
 image=read(HERE/'evidence/strap-routing-provenance.json')
 assert image['status']=='RENDERED_NATIVE_R14_STRAP_ROUTING' and image['source_sha256']==source_hash
 assert image['native_step_sha256']==native['native_step_sha256'] and image['image_sha256']==sha(HERE/'evidence/strap-routing.svg')
 visual=passed(HERE/'evidence/strap-routing-visual-check.json')
 assert visual['svg_sha256']==sha(HERE/'evidence/strap-routing.svg') and visual['rendered_png_sha256']==sha(HERE/'evidence/strap-routing-preview.png')
 return source_hash,version,layout,verified,native,qa,geometry

def strap_text():
 return """<!-- STRAP_ROUTING_START -->
## Befestigung mit zwei Gurten

Vier integrale, flache Ösen liegen außen an P01: je zwei bei **X5 und X80 mm**, also **75 mm auseinander**. Die gerundeten Öffnungen sind **27 × 4 mm** groß und liegen bei Y±69,5. Der Rahmen ist einschließlich Ösen **156 mm breit**; die ursprüngliche 132-mm-Grundplatte und ihre Führung werden dafür nicht durchtrennt.

Benötigt werden **zwei echte 25-mm-Gurte**, höchstens **2 mm dick** im Durchlass. Beide Enden jedes Gurts müssen sich zurückfalten und sicher an sich selbst befestigen lassen, etwa mit dafür geeignetem selbsthaftendem Gurtband. Die passende Länge richtet sich nach dem Gegenstand beziehungsweise Oberschenkelumfang und dem Platz für beide Rückfaltungen. Gurte gehören nicht zum Druckpaket. Die vier Ösen und ihre kurzen Übergänge zur Platte werden lokal mit 100 % geradlinigem Infill gedruckt; der restliche P01 bleibt bei 20 % Gyroid. Die vier Modifikatoren sind Einstellungen im 3MF und keine zusätzlichen Bauteile.

1. Den langen Gurt unten um den runden Gegenstand führen. Je ein Ende von unten durch die linke beziehungsweise rechte Öffnung derselben X-Position nach oben stecken.
2. Jedes Ende über den **äußeren Steg** falten und **außen nach unten** zurückführen. Die doppelte Lage gehört außerhalb der Öffnung; dort berücksichtigt die nominale Freiraumprüfung bis zu4 mm.
3. Beide Enden sicher am eigenen Gurt befestigen. Es läuft **kein Gurt über den Griff oder quer durch den oberen Bewegungsraum**. Den zweiten Gurt an der anderen X-Position genauso montieren.

![Gurtführung am nativen Querschnitt einer äußeren Öse](evidence/strap-routing.svg)

Die Abbildung zeigt die reale Rahmenkontur einer rechten Öse; Gurtverlauf und Gegenstand sind schematisch. Vor Benutzung am federfreien Aufbau Sitz, vollen Hub, sichere Endbefestigung und freien Zugang zu den Rastarmen prüfen. Gedruckte Tragfähigkeit, Gurtzug und Dauerhaltbarkeit sind noch nicht gemessen. Für Demontage und Elektronikservice die Gurte abnehmen.
<!-- STRAP_ROUTING_END -->""".replace('zu4','zu 4')

def prepare_docs(data):
 source_hash,version,layout,verified,native,qa,geometry=data
 status='<!-- RELEASE_STATUS_START -->\n**Nominale R14-CAD- und PLA-Druckprüfung bestanden.** Native Geometrie, voller Hub, Sensorservice, Q01-Passung und der tatsächliche H2D-Slice sind an diese Revision gebunden. Reale Reichweite, Handkomfort, Rastkraft und Belastbarkeit bleiben am Ausdruck zu prüfen.\n<!-- RELEASE_STATUS_END -->'
 for name in ['MONTAGE.md','parts-review.md']:
  p=HERE/name;s=p.read_text();s=re.sub(r'<!-- RELEASE_STATUS_START -->.*?<!-- RELEASE_STATUS_END -->',status,s,flags=re.S)
  s=s.replace('Die endgültigen Maße und die Abstände zum Griff werden im Änderungsreview dokumentiert.','Die endgültigen Maße und Abstände stehen in der geprüften Konstruktionsspezifikation dieser Revision.')
  s=re.sub(r'<!-- STRAP_ROUTING_START -->.*?<!-- STRAP_ROUTING_END -->',strap_text(),s,flags=re.S)
  s=s.replace('Die Grundplatte bleibt 132 mm breit; die äußeren Rastarme der Traverse ergeben **135,2 mm Gesamtbreite**.','Die Grundplatte bleibt 132 mm breit; die neuen äußeren Gurtösen ergeben **156 mm Gesamtbreite**. Die hinteren Rastarme liegen innerhalb dieser Breite.')
  s=s.replace('Die genaue unveränderte native Körperzahl wird erst aus dem finalen Export übernommen.','Der finale native Export enthält 93 Körper; die 92 Körper außer P01 sind exakt zum R13-Stand erhalten.')
  s=s.replace('Nur P01 soll gegenüber R13 seine Geometrie ändern.','Nur P01 ändert gegenüber R13 seine Geometrie.')
  s=s.replace('## Zu prüfende Schnittstellen','## Geprüfte Schnittstellen').replace('Erforderlicher Nachweis','Nachweisumfang')
  if '## Geprüfte Enddaten' not in s:
   s+='\n## Geprüfte Enddaten\n\nDie [Konstruktionsspezifikation](mechanics/design-specification.json) enthält die finalen Maße der griffnahen Auflage. [Native Geometrie](validation/native-geometry.json), [Bewegung](validation/native-motion.json), [Sensorservice](validation/service-native.json) und [Q01-Passung](validation/fixture-q01-check.json) beziehen sich auf denselben R14-Export. Die Druckberichte gelten für den tatsächlich geslicten Sechsersatz.\n'
  dimensions=f'''<!-- R14_DIMENSIONS_START -->
## Neue Auflage in Zahlen

| Maß | R14 |
|---|---|
| Breite × Tiefe | {geometry['contact_width_mm']} × {geometry['contact_depth_mm']} mm |
| Scheitel im CAD | X {geometry['crown_x_mm'][0]} bis {geometry['crown_x_mm'][1]} mm, Z {geometry['crown_z_mm']} mm |
| Rundung zum Handgelenk | R {geometry['wrist_radius_mm']} mm |
| Rundung zur Sensorseite / an den Enden | R {geometry['sensor_facing_radius_mm']} / R {geometry['end_radius_mm']} mm |
| Neue Unterseite an der Nase | {geometry['nose_underside_degrees']}° |
| Abstand zur hinteren H12-Sensorebene | {geometry['minimum_contact_to_H12_rear_plane_x_gap_mm']} mm |

Die frühere äußere Auflage und ihr hoher Verbindungssteg entfallen oberhalb Z14,5. Vier integrale flache Gurtösen werden außen am unteren Rahmen ergänzt. Die ursprüngliche 6-mm-Grundplatte und ihre Führungsquerschnitte bleiben ungeschnitten; funktionale Sensor-, Rast- und Elektronikbereiche bleiben erhalten. Der obere Wandrand und die Enden der Stützrippen werden nur oberhalb Z30 angepasst. Die eigentliche Sensorreaktionsfläche endet bereits bei Z26 und bleibt erhalten. Es kommt keine Verbindung zum beweglichen P05 hinzu.
<!-- R14_DIMENSIONS_END -->'''
  if '<!-- R14_DIMENSIONS_START -->' in s:s=re.sub(r'<!-- R14_DIMENSIONS_START -->.*?<!-- R14_DIMENSIONS_END -->',dimensions,s,flags=re.S)
  else:s+='\n'+dimensions+'\n'
  p.write_text(s)
 with (HERE/'BOM_Aenderungen.csv').open(newline='') as f:rows=list(csv.reader(f))
 for row in rows:
  if row[0]=='P04/P05/P06/P11':row[-1]='Native Geometrie exakt zum R13-Stand erhalten; vorhandene Drucke weiterverwenden'
  if row[0]=='Q01':row[-1]='Vorhandene R12/R13-Passhilfe gegen finalen R14-Rahmen geprueft; nur federfrei'
  if row[0] in ['Zusaetzliche Kaufteile','G01/G02']:row[-1]='Zwei echte 25-mm-Gurte; max. 2 mm Dicke im Durchlass; beide Enden sicher rueckfaltbar; Laenge nach Umfang plus Rueckfaltungen. Nicht drucken, nicht im nativen CAD modelliert.'
  if row[0]=='P01':row[-1]='Neu: griffnahe 76 x 18 mm Rundung; aeusserer Handballenbalken entfernt; vier integrale flache 27 x 4 mm-Gurtoeffnungen fuer zwei 25 mm-Gurte; Gesamtbreite 156 mm.'
 if not any(r[0]=='Native CAD-Koerper' for r in rows):rows.append(['Native CAD-Koerper',93,93,'','P01 geaendert; 92 andere Koerper exakt unveraendert'])
 with (HERE/'BOM_Aenderungen.csv').open('w',newline='') as f:csv.writer(f).writerows(rows)
 seconds=qa['estimate_seconds'];minutes=(seconds+59)//60
 (HERE/'README.md').write_text(f'''# Flat132 R14 – griffnahe Handballenauflage und Gurtaufnahme

{status}

Die neue breite Rundung sitzt direkt an der Sensorwand und gehört zum einteiligen Rahmen P01. Der äußere R13-Handballenbalken entfällt. Die Hand kann damit näher am Fingergriff aufliegen, ohne ein zusätzliches Druckteil oder eine Schraubverbindung. Vier gerundete Öffnungen in integralen äußeren Ösen schaffen zwei Befestigungspositionen für echte 25-mm-Gurte; Gesamtbreite 156 mm. Die ursprüngliche Grundplatte bleibt ungeschnitten. Die bevorzugte Reichweite und der Handkomfort werden am neuen Ausdruck beurteilt.

**Gegenüber R13 nur P01 neu drucken.** P04, P05, P06, P08, P09, P11 und Q01 bleiben geometrisch kompatibel. Die vollständige native Baugruppe enthält 93 Körper, davon sieben Gerätedruckteile; 92 Körper außer P01 sind exakt unverändert.

Der aktuelle mechanische Drucksatz enthält **sechs Stücke auf einer Platte**: P01, P04, P05, P06, P11 und die federfreie Sensor-Passhilfe Q01. Vorhandene echte Führungsstangen verwenden. Elektronikwanne, Deckel und gedruckte Stangen werden diesmal weggelassen. Es kommen keine kleinen Montageteile hinzu.

[Onshape R14]({version['url']}) · [Bambu-Projekt](../../print/bambu-R14-near-palm-2026-11-06/{BASE}.3mf) · [Druckpaket](../../print/bambu-R14-near-palm-2026-11-06/{BASE}_Package.zip) · [HTML-Übersicht](../../Uebersicht.html)

[Montage](MONTAGE.md) · [Änderungsreview](parts-review.md) · [Stücklistenänderungen](BOM_Aenderungen.csv) · [Konstruktionsmaße](mechanics/design-specification.json) · [Finale Spezifikation](final-specification.json)

Sensor-Kraftpfad, voller 30-mm-Hub, 15-mm-ISO-Anfahrweg, Rastfunktionen, Elektronikzugänge und Sensorservice sind nominal geprüft. Beide Vorspannverstellungen bleiben entfernt. Q01 bleibt eine unbelastete Passhilfe und wird vor Sensor-/Federeinbau entfernt.

H2D / PLA / 0,4-mm-Standarddüse, vier Wände und 20 % Gyroid; die vier Gurtösen samt kurzem Wurzelbereich sind lokal mit 100 % gefüllt. Die vier Modifikatoren im 3MF sind keine zusätzlichen Druckteile. Das 3MF als Projekt öffnen, damit die individuellen Einstellungen und Stützen erhalten bleiben. Tatsächlicher Slice: **{seconds//3600} h {(seconds%3600)//60:02d} min {seconds%60:02d} s / {qa['filament_g']:.2f} g PLA** einschließlich Stützen und Brims. P04 behält seine bewährte Lage mit freien Fingerkontaktflächen.

{strap_text()}

Reale Passung, neue Handposition, Stützentfernung, PLA-Kriechen und Belastbarkeit sind am Ausdruck zu prüfen. Clips dienen der federfreien Montage; für Federlast bleiben die vorgesehenen Sicherungsschrauben erforderlich. Es wurde kein Druckauftrag gesendet.
''')
 files=[HERE/n for n in ['README.md','MONTAGE.md','parts-review.md','BOM_Aenderungen.csv','evidence/strap-routing.svg','evidence/strap-routing-provenance.json']]
 write(HERE/'documentation-ready.json',{'status':'PASS_DOCUMENTATION_BOUND_TO_R14_EVIDENCE','source_sha256':source_hash,'onshape_version':version['version_id'],'verification':verified,'design_specification_sha256':sha(HERE/'mechanics/design-specification.json'),'files_sha256':{str(p.relative_to(ROOT)):sha(p) for p in files}})
 print('R14 docs ready; final source/entrypoints remain unpublished until package passes.')

def publish(data):
 source_hash,version,layout,verified,native,qa,geometry=data
 docs=passed(HERE/'documentation-ready.json')
 assert docs['source_sha256']==source_hash and docs['verification']==verified
 assert docs['design_specification_sha256']==sha(HERE/'mechanics/design-specification.json')
 for p,h in docs['files_sha256'].items():assert sha(ROOT/p)==h,p
 delivery=passed(PACK/'delivery-specification.json')
 assert delivery['status']=='PASS_R14_NEAR_PALM_DELIVERY' and delivery['CAD_source_sha256']==source_hash
 assert delivery['onshape_version']==version['version_id'] and delivery['geometry_changes']==['P01']
 for p,h in delivery['files_sha256'].items():assert sha(ROOT/p)==h,p
 for p,e in delivery['verification'].items():assert sha(ROOT/p)==e['sha256'],p
 spec=read(ROOT/'review/palm-simplification-2026-11-03/final-specification.json')
 spec.pop('palm_simplification',None)
 spec.update(revision='Flat132 R14 near-palm integrated support and strap mounting',date='2026-11-06',status='PASS_NOMINAL_CAD_AND_PLA_PRINT',source_sha256=source_hash,onshape_version=version['version_id'],onshape_url=version['url'],changed=['P01'],new=[],removed=[],unchanged_exact_native_breps=92,new_prints_required=['P01'],fit_test_pieces=6,plates=1,printed_device_bodies=7,primary_printed_device_bodies=5,primary_unloaded_fixtures=1,omitted_from_primary_print=['P08','P09','H040','H041'],modifier_count=4,local_density_modifiers=layout['local_density_modifiers'],estimates=delivery['estimates'],verification=verified,near_palm=geometry,new_nonprinted_parts={'G01/G02':{'quantity':2,'type':'fastening straps','width_mm':25,'maximum_single_thickness_mm':2,'both_ends_securely_double_back':True,'native_modeled':False}})
 spec['gui_preview_limitation']=delivery.get('gui_preview_limitation')
 spec['overview_assets']={'cad_image':'review/near-palm-2026-11-06/evidence/P01-final-native.png','cad_image_provenance':'review/near-palm-2026-11-06/evidence/P01-final-native-provenance.json','strap_image':'review/near-palm-2026-11-06/evidence/strap-routing.svg'}
 files=[HERE/'evidence/P01-final-native.png',HERE/'evidence/P01-final-native-provenance.json',SOURCE,HERE/'native/Flat132_R14_final_AP214.step',HERE/'native/Flat132_R14_neutral_final.zip',PACK/(BASE+'.3mf'),PACK/(BASE+'_Package.zip'),PACK/'delivery-specification.json',HERE/'documentation-ready.json',HERE/'mechanics/design-specification.json']
 spec['files_sha256']={str(p.relative_to(ROOT)):sha(p) for p in files}
 write(HERE/'final-specification.json',spec)
 (ROOT/'fingerworker_mvp.fs').write_bytes(SOURCE.read_bytes())
 build=read(HERE/'source-build.json') if (HERE/'source-build.json').exists() else dict(baseline_source_sha256=geometry['baseline_source_sha256'],source_sha256=source_hash,changed=['P01'],new=[],removed=[],device_prints=7,fit_pieces=6,native_solids=93,new_prints_required=['P01'])
 assert build['source_sha256']==source_hash
 build.update(status='PASS_NATIVE_REGENERATED_AND_RELEASED',onshape_version=version['version_id'],native_geometry_report_sha256=sha(HERE/'validation/native-geometry.json'));write(HERE/'source-build.json',build)
 review='review/near-palm-2026-11-06';pack='print/bambu-R14-near-palm-2026-11-06';seconds=qa['estimate_seconds']
 block=f'''<!-- CURRENT_FLAT132_R14_START -->
> **06.11.2026 – Flat132 R14: griffnahe Handballenauflage und Gurtaufnahme.** Die breite abgerundete Auflage sitzt direkt an der Sensorwand und ist Teil von P01. Der äußere Handballenbalken entfällt; vier gerundete Öffnungen schaffen zwei Gurtpositionen. **Gegenüber R13 nur P01 ersetzen.** Die 92 übrigen nativen Körper bleiben exakt unverändert; voller Hub, Sensor-Kraftpfad, Klickfunktionen und Service sind nominal geprüft. Reale Reichweite und Handkomfort bleiben am Ausdruck zu beurteilen. [CAD/Review]({review}/README.md) · [Montage]({review}/MONTAGE.md) · [Onshape R14]({version['url']}).

> **Mechanischer Drucksatz: sechs Teile auf einer H2D-Platte**, P01/P04/P05/P06/P11 und Q01. Vorhandene echte Führungsstangen verwenden; Elektronikwanne, Deckel und gedruckte Stangen werden nicht mitgedruckt. Zwei echte 25-mm-Gurte mit rückfaltbaren, sicher an sich selbst befestigten Enden ergänzen; Länge nach Umfang wählen. PLA, 0,4-mm-Standarddüse, vier Wände und 20 % Gyroid. Tatsächlicher Slice: **{seconds//3600} h {(seconds%3600)//60:02d} min / {qa['filament_g']:.2f} g PLA**. [3MF-Projekt]({pack}/{BASE}.3mf) · [Druckpaket ZIP]({pack}/{BASE}_Package.zip) · [Druckanleitung]({pack}/README.md). Q01 nur federfrei verwenden. Die folgenden älteren Revisionsangaben bleiben Historie.
<!-- CURRENT_FLAT132_R14_END -->'''
 for name in ['README.md','PRINTING.md','EINKAUFSTEILE.md','DEVICE_UPGRADES.md','print/REVISION_STATUS.md']:
  p=ROOT/name;s=p.read_text();s=re.sub(r'<!-- CURRENT_R13_OVERNIGHT_START -->.*?<!-- CURRENT_R13_OVERNIGHT_END -->\s*','',s,flags=re.S)
  use=block.replace('](review/','](../review/').replace('](print/','](../print/') if name.startswith('print/') else block
  pattern=r'<!-- CURRENT_FLAT132_R(?:13|14)_START -->.*?<!-- CURRENT_FLAT132_R(?:13|14)_END -->'
  assert re.search(pattern,s,flags=re.S),name
  s=re.sub(pattern,use,s,count=1,flags=re.S).replace('HTML-Projektübersicht R13','HTML-Projektübersicht R14');p.write_text(s)
 print(json.dumps({'status':spec['status'],'revision':'R14','source_sha256':source_hash,'reports':len(verified),'primary_pieces':6},indent=2))

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--prepare-docs',action='store_true');args=ap.parse_args();data=validate()
 prepare_docs(data) if args.prepare_docs else publish(data)
