#!/usr/bin/env python3
"""Bind R18 documentation to final native CAD and both sealed print variants."""
from pathlib import Path
import argparse,csv,hashlib,json,re
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
PACK=ROOT/'print/bambu-R18-organic-palm-2026-11-13'
SOURCE=HERE/'fingerworker_R18_organic_palm.fs'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text())
def write(p,d):Path(p).write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
def passed(p):
 d=read(p);assert d['status'].startswith('PASS'),(p,d.get('status'))
 for k in ['failures','issues','failed']:assert not d.get(k),(p,k,d[k])
 return d
def validate(allow_gui_pending=False):
 sh=sha(SOURCE);v=read(HERE/'onshape-version.json');d=passed(PACK/'delivery-specification.json')
 assert v['source_sha256']==d['CAD_source_sha256']==sh
 assert v['version_id']==d['onshape_version'] and d['object_count']==1 and d['secondary_object_count']==6
 assert d['primary_variant']=='P01_replacement'
 verified={}
 paths=[HERE/'validation/native-integration.json',HERE/'validation/native-section-fidelity.json',HERE/'validation/native-release-binding.json',HERE/'mechanics/preflight.json']
 for p in paths:
  q=passed(p)
  if 'source_sha256' in q:assert q['source_sha256']==sh,p
  verified[str(p.relative_to(ROOT))]=dict(status=q['status'],sha256=sha(p))
 for p,e in {**d.get('CAD_verification',{}),**d['verification']}.items():
  q=passed(ROOT/p);assert sha(ROOT/p)==e['sha256'],p;verified[p]=e
 for p,h in d['files_sha256'].items():assert sha(ROOT/p)==h,p
 inv=read(HERE/'validation/native-step-inventory.json');assert len(inv['native_part_correspondence'])==93
 assert inv['native_step_sha256']==d['native_step_sha256']
 assert sha(HERE/'native/Flat132_R18_neutral_final.zip')==d['native_zip_sha256']
 assert sha(HERE/'native/Flat132_R18_final_AP214.step')==d['native_step_sha256']
 gui_path=PACK/'validation/P01-replacement/gui-check.json'
 if gui_path.exists():
  gui=passed(gui_path)
  assert gui['source_sha256']==sh and gui['project_sha256']==sha(ROOT/d['project']) and not gui['printer_job_started']
  gui['verified']=True
 else:
  assert allow_gui_pending,'Final Bambu GUI record missing; explicit pending mode required.'
  assert not d.get('gui_verified',False)
  gui=dict(status='GUI_PENDING_MAC_LOCKED',verified=False,summary='Bambu Studio: Öffnen und visuelle Vorschau ausstehend, bis der Mac entsperrt ist. Native CAD- und vollständige Slice-Prüfungen sind abgeschlossen.',printer_job_started=False)
 cad=read(HERE/'evidence/P01-final-native-provenance.json');assert cad['status']=='RENDERED_FINAL_NATIVE_R18_P01'
 assert cad['source_sha256']==sh and cad['native_zip_sha256']==d['native_zip_sha256'] and cad['image_sha256']==sha(HERE/'evidence/P01-final-native.png')
 visual=passed(HERE/'evidence/P01-final-native-visual-check.json');assert visual['image_sha256']==cad['image_sha256'] and visual['source_sha256']==sh
 g=read(HERE/'mechanics/design-specification.json');assert g['source_sha256']==sh
 return sh,v,d,verified,g,gui

def duration(sec):return f'{sec//3600} h {sec%3600//60:02d} min {sec%60:02d} s'
def prepare(data):
 sh,v,d,verified,g,gui=data;url=v.get('url',v.get('version_url'));assert url and '/v/' in url
 status='**Native R18-Geometrie und PLA-Druckwege geprüft.** Der nächste Ausdruck bleibt die praktische Prüfung von Handkomfort, Halt, Passung und Belastbarkeit.'
 if not gui['verified']:status+=' **Bambu Studio: Öffnen und visuelle Vorschau warten auf das Entsperren des Mac.**'
 (HERE/'README.md').write_text(f'''# Flat132 R18 – organische Handballenauflage

Stand 13.11.2026. {status}

Die feste Handballenauflage ist jetzt breit und weich gewölbt. Ihre Kontur fließt in beide Daumenschultern; an beiden Außenseiten liegen offene, gerundete Daumenmulden. P01 bleibt ein einziges Druckteil, ohne Sleeve, Zusatzkappe oder neue Kleinteile. Gegenüber dem veröffentlichten R16 ändern sich nur P01 und dessen Handkontaktform; die anderen 92 nativen Körper bleiben exakt erhalten.

**Für dein vorhandenes Gerät nur P01 neu drucken:** [Bambu-Projekt](../../{d['project']}) · [P01-Druckpaket](../../{d['package']}). Eine Platte, **{duration(d['estimated_seconds'])} / {d['estimated_grams']:.2f} g PLA**. H2D, linke Standarddüse 0,4 mm, Bambu PLA Basic; Teile und Stützen verwenden PLA. Kein Brim, notwendige Stützen bleiben aktiv. Kein Druckauftrag wurde gestartet.

Wenn du nochmals alles drucken möchtest: [Komplettes 3MF](../../{d['secondary_project']}) · [Komplettpaket](../../{d['secondary_package']}). P01/P04/P05/P06/P11 und Q01 auf einer Platte, **{duration(d['secondary_estimated_seconds'])} / {d['secondary_estimated_grams']:.2f} g PLA**. Die beiden Pakete sind Alternativen. Echte vorhandene Stangen weiterverwenden; Elektronikgehäuse, Schrauben und Muttern gehören nicht zum Drucksatz.

[Gespeichertes Onshape R18]({url}) · [Übersicht](../../Uebersicht.html) · [Montage](MONTAGE.md) · [Änderungsreview](parts-review.md) · [Stückliste](BOM_Aenderungen.csv) · [Nachweise](final-specification.json)

![Finaler nativer R18-Grundrahmen](evidence/P01-final-native.png)

Die neue obere Handballenfläche reicht nominal bis Z34,5 statt Z33; ihre mittlere Handgelenkseite wölbt sich rund 2 mm nach außen. Damit bleibt die Kontaktlage nahe am bewährten Griff. Die Mulden an beiden Außenseiten sind ungefähr 4 mm tief. Sie ergänzen die vorhandenen flachen Rückgriffe auf der Handgelenkseite. Alle Kontaktflächen sind fest mit dem Rahmen verbunden; P05 bleibt als Messjoch separat.

Zuerst federfrei Handlage und vollen Hub prüfen. Q01 vor dem Sensor- und Federeinbau vollständig entfernen. Klickstellen dienen der Montage; die vorgesehenen Sicherungsschrauben für den Funktionsaufbau bleiben erhalten.
''')
 body=(ROOT/'review/upright-grip-2026-11-09/MONTAGE.md').read_text();body=body[body.index('## Federfreier Passaufbau'):]
 body=body.replace('R16','R18').replace('Das R18-Projekt druckt alle sechs Teile ohne Brim.','Beide R18-Druckvarianten sind ohne Brim eingerichtet.')
 (HERE/'MONTAGE.md').write_text(f'''# R18 – Montage mit organischer Handballenauflage

Stand 13.11.2026. {status}

Nur P01 ersetzen. Vorhandene P04/P05/P06/P11, Q01 und echte Führungsstangen weiterverwenden. Das empfohlene P01-Paket enthält nur den neuen Rahmen; der optionale vollständige Satz enthält sechs Druckstücke. Kein zusätzliches Handballenteil montieren.

## Neue Handkontaktflächen

Stützen unter dem Gehäusedach und den äußeren Schulterlippen entfernen; Rastspalte und Stangenbohrungen säubern. Die große gewölbte Handballenfläche, die Krone und die seitlichen Daumenmulden sollen frei von Stützenkontakt bleiben. Keine scharfen Stützreste im Kontaktbereich stehen lassen.

Federfrei den Handballen gegen die breite Wölbung setzen und den Daumen seitlich in eine Mulde legen. Links und rechts sind gleich aufgebaut. Prüfen, ob das Halten ohne Tisch und die Druckverteilung zur eigenen Hand passen. P05 und der bewegliche Griff müssen frei bleiben. Die seitliche Mulde ist offen und ungefähr 4 mm tief; sie ist keine geschlossene Handsicherung.

Die Oberkante ist nominal 1,5 mm höher als R16. Die obere Wölbung und die Daumenmulden verändern die Handanlage, nicht den Sensoraufbau. Für belasteten Federbetrieb bleiben die vorgesehenen Sicherungsschrauben erforderlich; reale Belastbarkeit und Dauerverhalten sind nicht durch die CAD-Prüfung belegt.

'''+body)
 (HERE/'parts-review.md').write_text(f'''# R18 – Form- und Schnittstellenreview

{status}

| Bereich | Umsetzung |
|---|---|
| Handballenauflage | Sieben einfache, gerundete Querschnitte ergeben eine breite, weich gewölbte Auflage; Krone nominal Z34,5 |
| Handlage | Mittlere Wölbung etwa 2 mm zur Handgelenkseite; Kontur bleibt nahe am bisherigen Griff |
| Schulterübergänge | Weicher Übergang in beide bestehende Daumenbereiche; nur die alte obere Krone über Z30 wird lokal neu geformt |
| Seitliche Daumenmulden | Beidseitig am festen P01; nominal 4 mm tief; offene Oberseite, Boden R1,5 und Mundkante R0,4 |
| Vorhandene Rückgriffe | Die flachen handgelenkseitigen Daumenrückgriffe bleiben erhalten |
| Tragende Verbindung | Einteiliger P01-Rahmen; ursprüngliche untere Kraftabstützung bleibt erhalten |
| Stangensockel | Ø6,2-Bohrungen unverändert; äußeres Material wird für die Seitenmulden lokal geformt, verbleibende Wand geprüft |
| Messkraftpfad | P05 bleibt separat; zentraler neuer Körper bleibt hinter X−16; nomineller Sensorgap und Service bleiben erhalten |
| Montage | Klickstellen, Gehäusedach, H18-Werkzeugzugang, 30-mm-Hub und Q01-Entnahme bleiben erhalten |
| Gurte | Vier innenliegende 27×4-mm-Schlitze für zwei echte 25-mm-Gurte unverändert |
| Teilezahl | Keine neuen Teile; nur P01 neu drucken, übrige 92 native Körper unverändert |

Der lokale OCC-Loft und der native Parasolid-Loft verwenden dieselben Querschnittskontrollen. An den sieben Querschnitten beträgt die größte gemessene Abweichung rund 0,00244 mm. Zwischen den Querschnitten unterscheiden sich die interpolierten Flächen: der Stichprobenvergleich der oberen Ansichtsnetze zeigt bis 1,20 mm einschließlich Tessellierungsabweichung. Der visuell geprüfte native Onshape-Export ist maßgeblich. Die native Geometrie wird deshalb unmittelbar auf Funktionsabstände, geschützte Schnittstellen und erlaubte Formänderungen geprüft. Die lokale Vorschau ersetzt diesen Vergleich nicht.

Die geerbte Kopfkommentierung der eingefrorenen FeatureScript-Quelle nennt noch X−29/Z33 für den ursprünglichen R16-Quergriff. Diese Angaben beschreiben das darunterliegende Ausgangsteil vor dem angehängten R18-Loft. Die aktuelle R18-Krone liegt nominal bei Z34,5; die mittlere Wölbung reicht etwa bis X−31. Maßgeblich sind der R18-Abschnitt, die Querschnittskontrollen und der gespeicherte native Export.

Der Kraftpfad bleibt P04 → Federn bzw. P05-Endanschläge → P05 → Druckstift → Sensor → Stahlrückplatte → feste P01-Abstützung → Handballen. Keine feste Griffwölbung darf das Messjoch berühren.

[Native Integrationsprüfung](validation/native-integration.json) · [Versionsbindung](validation/native-release-binding.json) · [Lokaler Vorabcheck](mechanics/preflight.json) · [Druckprüfung](../../{str(PACK.relative_to(ROOT))}/PRINT_QA_NOTES.md)
''')
 rows=[['Ref','Menge Geraet','P01 Ersatzpaket','Komplettpaket','Aenderung'],['P01',1,1,1,'Organische integrierte Handballenauflage und beidseitige offene Daumenmulden.'],['P04/P05/P06/P11',4,0,4,'Unveraendert; bestehende Ausdrucke wiederverwenden.'],['P08/P09',2,0,0,'Elektronikgehaeuse unveraendert; derzeit nicht drucken.'],['Q01','Passhilfe',0,1,'Unveraendert; nur federfrei, vor Funktionsaufbau entfernen.'],['H040/H041',2,0,0,'Vorhandene echte Stahlstangen verwenden.'],['G01/G02',2,0,0,'Echte 25mm-Gurte; Schlitze unveraendert.'],['Neue Griffkleinteile',0,0,0,'Keine Kappe, kein Sleeve, keine neuen Clips.'],['Native Koerper',93,'','', 'Nur P01 geaendert;92 andere Koerper erhalten.']]
 with (HERE/'BOM_Aenderungen.csv').open('w',newline='') as f:csv.writer(f).writerows(rows)
 files=[SOURCE,HERE/'native/Flat132_R18_final_AP214.step',HERE/'native/Flat132_R18_neutral_final.zip',HERE/'mechanics/design-specification.json',HERE/'evidence/P01-final-native.png',HERE/'evidence/P01-final-native-provenance.json',HERE/'evidence/strap-routing.svg',HERE/'evidence/strap-routing-provenance.json']+[HERE/n for n in ['README.md','MONTAGE.md','parts-review.md','BOM_Aenderungen.csv']]+[ROOT/d[k] for k in ['project','package','secondary_project','secondary_package']]+[PACK/'delivery-specification.json']
 hashes={str(p.relative_to(ROOT)):sha(p) for p in files}
 spec=dict(revision='Flat132 R18 organic palm bolster',date='2026-11-13',status='PASS_NOMINAL_CAD_AND_PLA_PRINT',source_sha256=sh,onshape_version=v['version_id'],onshape_url=url,changed=['P01'],new=[],removed=[],native_solids=93,unchanged_exact_native_breps=92,new_prints_required=['P01'],fit_test_pieces=6,primary_print_pieces=1,plates=1,printed_device_bodies=7,primary_printed_device_bodies=1,primary_unloaded_fixtures=0,omitted_from_primary_print=['P04','P05','P06','P08','P09','P11','Q01','H040','H041'],estimates=dict(seconds=d['estimated_seconds'],filament_g=d['estimated_grams']),secondary_estimates=dict(seconds=d['secondary_estimated_seconds'],filament_g=d['secondary_estimated_grams']),verification=verified,organic_palm=g,overview_assets=dict(cad_image=str((HERE/'evidence/P01-final-native.png').relative_to(ROOT)),cad_image_provenance=str((HERE/'evidence/P01-final-native-provenance.json').relative_to(ROOT)),strap_image=str((HERE/'evidence/strap-routing.svg').relative_to(ROOT))),project=d['project'],package=d['package'],secondary_project=d['secondary_project'],secondary_package=d['secondary_package'],brim_policy='No brim on either variant; necessary supports retained.',files_sha256=hashes,limitations='Nominal CAD and computed paths only; actual comfort, grip, fit, adhesion, strength and lifetime require the printed part.')
 spec.update(gui_verified=gui['verified'],gui_status=gui['status'],gui_summary=gui.get('summary',''))
 write(HERE/'final-specification.json',spec);write(HERE/'documentation-ready.json',dict(status='PASS_DOCUMENTATION_BOUND_TO_R18_EVIDENCE',source_sha256=sh,onshape_version=v['version_id'],files_sha256=hashes,verification=verified,gui_verified=gui['verified'],gui_status=gui['status']));write(HERE/'source-build.json',dict(status='PASS_NATIVE_REGENERATED_AND_DOCUMENTED',source_sha256=sh,onshape_version=v['version_id'],changed=['P01'],native_solids=93,new_prints_required=['P01'],primary_variant='P01_replacement',gui_verified=gui['verified'],gui_status=gui['status']))
 print('R18 documentation staged; root entrypoints unchanged.')
def publish(data):
 sh,v,d,verified,g,gui=data;spec=passed(HERE/'final-specification.json');docs=passed(HERE/'documentation-ready.json')
 for p,h in docs['files_sha256'].items():assert sha(ROOT/p)==h,p
 (ROOT/'fingerworker_mvp.fs').write_bytes(SOURCE.read_bytes());review=str(HERE.relative_to(ROOT))
 block=f'''<!-- CURRENT_FLAT132_R18_START -->
> **13.11.2026 – Flat132 R18: organische Handballenauflage und beidseitige Daumenmulden.** Ein zusammenhängender P01-Rahmen mit weich gewölbter Druckfläche. Klickfunktionen, Gurtschlitze, Sensorpfad und voller Hub bleiben erhalten. **Nur P01 neu drucken; die übrigen 92 nativen Körper bleiben unverändert.** [Review]({review}/README.md) · [Montage]({review}/MONTAGE.md) · [Onshape R18]({spec['onshape_url']}).

> **Empfohlenes P01-Ersatzpaket:** H2D, linke 0,4-mm-Düse, Bambu PLA Basic, ohne Brim; notwendige Stützen bleiben. **{duration(d['estimated_seconds'])} / {d['estimated_grams']:.2f}g PLA.** [3MF]({d['project']}) · [P01-Paket]({d['package']}). Alternativ [sechs Teile auf einer Platte]({d['secondary_project']}) · [Komplettpaket]({d['secondary_package']}). Echte Stangen weiterverwenden. Komfort, Halt und Passung am Ausdruck prüfen. Kein Druckauftrag gestartet. Ältere Angaben bleiben Historie.
<!-- CURRENT_FLAT132_R18_END -->'''
 if not gui['verified']:block=block.replace('Kein Druckauftrag gestartet.','Bambu-Studio-Vorschau wartet auf das Entsperren des Mac. Kein Druckauftrag gestartet.')
 for name in ['README.md','PRINTING.md','EINKAUFSTEILE.md','DEVICE_UPGRADES.md','print/REVISION_STATUS.md']:
  p=ROOT/name;s=p.read_text();use=block.replace('](review/','](../review/').replace('](print/','](../print/') if name.startswith('print/') else block
  pat=r'<!-- CURRENT_FLAT132_R(?:16|17|18)_START -->.*?<!-- CURRENT_FLAT132_R(?:16|17|18)_END -->';assert re.search(pat,s,re.S),name
  p.write_text(re.sub(pat,use,s,count=1,flags=re.S).replace('HTML-Projektübersicht R16','HTML-Projektübersicht R18'))
 q=read(HERE/'source-build.json');q['status']='PASS_NATIVE_REGENERATED_AND_RELEASED';write(HERE/'source-build.json',q);print('Published R18 source and root documentation.')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--publish',action='store_true');p.add_argument('--allow-gui-pending',action='store_true');a=p.parse_args();data=validate(a.allow_gui_pending);prepare(data)
 if a.publish:publish(data)
