#!/usr/bin/env python3
"""Publish R19 native CAD/docs only. Print setup is explicitly deferred by the user."""
from pathlib import Path
import argparse,csv,hashlib,json,re
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];SOURCE=HERE/'fingerworker_R19_thumb_rim.fs'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text())
def write(p,d):Path(p).write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
def passed(p):
 d=read(p);assert d['status'].startswith('PASS'),(p,d.get('status'))
 for k in ['failures','issues','failed']:assert not d.get(k),(p,k,d[k])
 return d
def prepare():
 v=read(HERE/'onshape-version.json');sh=sha(SOURCE);assert v['source_sha256']==sh and v['native_parts']==94
 verified={}
 for p in [HERE/'validation/native-integration.json',HERE/'validation/native-rim-check.json',HERE/'validation/native-release-binding.json']:
  q=passed(p);assert q['source_sha256']==sh
  verified[str(p.relative_to(ROOT))]=dict(status=q['status'],sha256=sha(p))
 inv=read(HERE/'validation/native-step-inventory.json');assert len(inv['native_part_correspondence'])==94
 for name,key in [('Flat132_R19_neutral_final.zip','stl_zip_sha256'),('Flat132_R19_final_AP214.step','step_sha256')]:assert sha(HERE/'native'/name)==v[key]
 cad=read(HERE/'evidence/P01-final-native-provenance.json');assert cad['source_sha256']==sh and cad['native_zip_sha256']==v['stl_zip_sha256'] and cad['image_sha256']==sha(HERE/'evidence/P01-final-native.png')
 visual=passed(HERE/'evidence/P01-final-native-visual-check.json');assert visual['source_sha256']==sh and visual['image_sha256']==cad['image_sha256']
 url=v['url'];status='**Native R19-Geometrie geprüft. Druckvorbereitung auf deinen Wunsch zurückgestellt.** Es gibt noch kein freigegebenes R19-Bambu-Projekt, keinen neuen Slice und keinen gestarteten Druckauftrag.'
 (HERE/'README.md').write_text(f'''# Flat132 R19 – weichere Daumenränder und massive Halter

Stand 13.11.2026. {status}

Die obere und handgelenkseitige Kante beider Daumenmulden ist jetzt deutlich weicher: oben2mm, an der Handgelenkseite1mm, mit Übergang zur unveränderten unteren0,4-mm-Rundung. Die breite organische Handballenform bleibt erhalten. Der kleinste gemessene Steg zum vorhandenen Rückgriff beträgt2,43mm; alle58 geprüften Boden-/Lippenquerschnitte bleiben unverändert.

**Die hintere Klicktraverse entfällt.** P06L/P06R sind zwei separate massive Stangenblöcke, je mit zwei vorhandenen M3×8-Schrauben zu befestigen. Dünne Arme, Querbrücke und ungenutzte Heckrastnocken am P01 sind entfernt. Die optionale Elektronikwanne P08 hat feste Schraubohren statt der hohen Clips und benötigt zwei M2×8. P09 bleibt der separate Klickdeckel.

[Gespeichertes Onshape R19]({url}) · [Native STEP-Baugruppe](native/Flat132_R19_final_AP214.step) · [Native STL-Geometrie](native/Flat132_R19_neutral_final.zip) · [Übersicht](../../Uebersicht.html)

[Montage](MONTAGE.md) · [Änderungsreview](parts-review.md) · [Stückliste](BOM_Aenderungen.csv) · [Nachweise](final-specification.json)

![Finaler nativer R19-Grundrahmen](evidence/P01-final-native.png)

Für einen späteren mechanischen Nachdruck sind P01/P06L/P06R die geänderten Teile. Vorhandene P04/P05/P11/Q01 und echte Führungsstangen können weiterverwendet werden. Elektronik bleibt vorerst separat. Diese Aufzählung ist keine vorbereitete Druckplatte: Ausrichtung, Support, Zeit und Bambu-Dateien werden erst wieder bearbeitet, wenn du es anforderst. Native STL-Dateien sind CAD-Exporte in Baugruppenlage.

P01 bleibt ein zusammenhängendes Teil. Die Krone liegt nominal beiZ34,5, die mittlere Handgelenkseite etwa beiX−31. Der Messkraftpfad mit separatem P05, Stangenbohrungen,30-mm-Hub und die vier Gurtdurchlässe bleiben erhalten. Die Baugruppe enthält94 native Körper;90 bisherige Körper behalten ihre Geometrie. Handkomfort, Passung, Insertsitz und reale Belastbarkeit sind am Ausdruck zu prüfen.
''')
 (HERE/'parts-review.md').write_text(f'''# R19 – Konstruktionsreview

{status}

| Bereich | Umsetzung |
|---|---|
| P01 Daumenrand | Beidseitig variable Rundung; obenR2, HandgelenkseiteR1, untere LippeR0,4 |
| Verbleibender Steg | Native Mindestabstände2,432/2,433mm zum bestehenden Rückgriff; vorher3,090mm |
| Unterlippe | Alle58 unabhängigen Boden-/Lippenquerschnitte bleiben identisch |
| Organische Handballenauflage | R18-Loft und Kontaktlage unverändert; KroneZ34,5 und mittlere Wölbung etwaX−31 |
| P06L/P06R | Zwei massive getrennte Stangenblöcke, je zwei erforderliche M3×8; Brücke und Schnapparme entfernt |
| P01 Heckgegenhalter | Nicht mehr benötigte Rastnocken entfernt; ursprünglicher gerundeter Boden wieder frei |
| P08 optional | Hohe Schnappclips durch feste Schraubohren ersetzt; zwei erforderliche M2×8 in bestehenden M2-Inserts |
| P09 | Separater Klickdeckel mit Kabelhalter unverändert |
| Kraftpfad/Service | P05 separat; Stangenbohrungen, Sensorzugang,30-mm-Hub und Q01-Entnahme geprüft |
| Gurte | Vier innenliegende27×4-mm-Schlitze für zwei25-mm-Gurte erhalten |
| Teilezahl |94 native Körper;90 bisherige Körper geometrisch unverändert. P06 wird durch zwei Körper ersetzt |
| Druckstatus | PRINT_SETUP_DEFERRED_BY_USER – keine R19-Slice- oder Bambu-Freigabe |

Die größere Rundung entsteht an den ursprünglichen Muldenkanten vor dem unveränderten organischen Loft. Der native Onshape-Export ist maßgeblich. Die fehlgeschlagenen lokalen Defeaturing-Versuche sind nur Diagnosehistorie und keine Fertigungsgeometrie. Die variable Rundung schützt die dünne Unterlippe vor einer pauschalen großen Abrundung.

[Native Integration:81 Prüfungen](validation/native-integration.json) · [Native Randmessung](validation/native-rim-check.json) · [Versionsbindung](validation/native-release-binding.json) · [Massive Halter: lokaler Check](latches/design-specification.json)
''')
 rows=[['Ref','Menge Geraet','CAD-Aenderung','Hardware / Hinweis'],['P01',1,'Weiche variable Daumenraender; Heckrastnocken entfernt.','Einteiliger Rahmen; Druckvorbereitung zurueckgestellt.'],['P06L/P06R',2,'Separate massive Stangenbloecke.','Je2 M3x8 in vorhandenenM3-Inserts erforderlich.'],['P04/P05/P11',3,'Unveraendert.','Vorhandene Teile weiterverwenden.'],['Q01','Passhilfe','Unveraendert.','Nur federfrei; vor Sensor-/Federbetrieb entfernen.'],['P08',1,'Feste Schraubohren statt hoher Clips; optionaler Elektronikaufbau.','2 M2x8 ohne Scheibe plusM2-Inserts3.2x3mm erforderlich.'],['P09',1,'Unveraenderter separater Klickdeckel.','Elektronikaufbau optional.'],['H30',4,'Schraubengeometrie unveraendert; jetzt erforderliche Blockbefestigung.','4 M3x8 plus vorhandeneM3-Inserts.'],['H040/H041',2,'Unveraendert.','Vorhandene echteStahlstangen verwenden.'],['G01/G02',2,'Vier27x4mm-Schlitze erhalten.','Echte25mm-Gurte.'],['NativeKoerper',94,'90bisherigeKoerper geometrischunveraendert.','Kein aktuellerR19Drucksatz freigegeben.']]
 with (HERE/'BOM_Aenderungen.csv').open('w',newline='') as f:csv.writer(f).writerows(rows)
 design=dict(revision='R19',source_sha256=sh,onshape_version=v['version_id'],palm=dict(organic_shape='R18 native loft retained',crown_z_mm=34.5,wrist_extent_x_mm=-31,upper_rim_radius_controls_mm=2,wrist_rim_radius_controls_mm=1,lower_rim_radius_mm=.4,variable_transition=True),rigid_mounts=read(HERE/'latches/design-specification.json'),native_rim_measurements=read(HERE/'validation/native-rim-check.json'),print_status='PRINT_SETUP_DEFERRED_BY_USER')
 write(HERE/'mechanics/design-specification.json',design)
 names=['fingerworker_R19_thumb_rim.fs','native/Flat132_R19_final_AP214.step','native/Flat132_R19_neutral_final.zip','mechanics/design-specification.json','evidence/P01-final-native.png','evidence/P01-final-native-provenance.json','evidence/P01-final-native-detail.png','evidence/P01-final-native-detail.json','evidence/assembly-final-native.png','evidence/assembly-final-native.json','evidence/rigid-parts-final-native.png','evidence/rigid-parts-final-native.json','evidence/strap-routing.svg','evidence/strap-routing-provenance.json','README.md','MONTAGE.md','parts-review.md','BOM_Aenderungen.csv']
 hashes={str((HERE/p).relative_to(ROOT)):sha(HERE/p) for p in names}
 spec=dict(revision='Flat132 R19 rounded thumb rims and rigid mounts',date='2026-11-13',status='PASS_NATIVE_CAD_PRINT_SETUP_DEFERRED',source_sha256=sh,onshape_version=v['version_id'],onshape_url=url,changed=['P01','P06','P08'],new=['P06L','P06R'],removed=['P06'],native_solids=94,unchanged_exact_native_breps=90,changed_mechanical_parts=['P01','P06L','P06R'],optional_electronics_parts=['P08'],printed_device_bodies=8,verification=verified,design=design,overview_assets=dict(cad_image=str((HERE/'evidence/P01-final-native.png').relative_to(ROOT)),cad_image_provenance=str((HERE/'evidence/P01-final-native-provenance.json').relative_to(ROOT)),strap_image=str((HERE/'evidence/strap-routing.svg').relative_to(ROOT))),files_sha256=hashes,print_setup_status='PRINT_SETUP_DEFERRED_BY_USER',print_ready=False,gui_verified=False,gui_status='NOT_REQUESTED_PRINT_SETUP_DEFERRED',gui_summary='Druckvorbereitung auf deinen Wunsch zurückgestellt. Kein neues R19-Bambu-Projekt oder neuer Slice freigegeben.',limitations='Native nominal CAD only; actual comfort, fit, insert retention, strength and lifetime require physical evaluation.')
 write(HERE/'final-specification.json',spec);write(HERE/'documentation-ready.json',dict(status='PASS_DOCUMENTATION_BOUND_TO_R19_NATIVE_CAD',source_sha256=sh,onshape_version=v['version_id'],files_sha256=hashes,verification=verified,print_setup_status='PRINT_SETUP_DEFERRED_BY_USER'));write(HERE/'source-build.json',dict(status='PASS_NATIVE_REGENERATED_AND_DOCUMENTED',source_sha256=sh,onshape_version=v['version_id'],native_solids=94,print_setup_status='PRINT_SETUP_DEFERRED_BY_USER'))
 return spec

def publish(spec):
 assert (ROOT/'overview/archive-r18-final-2026-11-13/archive-manifest.json').is_file()
 for p,h in spec['files_sha256'].items():assert sha(ROOT/p)==h,p
 (ROOT/'fingerworker_mvp.fs').write_bytes(SOURCE.read_bytes());review=str(HERE.relative_to(ROOT))
 block=f'''<!-- CURRENT_FLAT132_R19_START -->
> **13.11.2026 – Flat132 R19: weichere Daumenränder und massive Stangenblöcke.** Beide Daumenmulden sind oben und handgelenkseitig stärker gerundet. Zwei separate massive P06L/P06R-Blöcke ersetzen die dünne Heck-Klicktraverse; je zwei M3×8 sind erforderlich. Die optionale P08-Wanne besitzt feste Schraubohren für zwei M2×8. [Onshape R19]({spec['onshape_url']}) · [Native STEP-Baugruppe]({review}/native/Flat132_R19_final_AP214.step) · [Review]({review}/README.md) · [Montage]({review}/MONTAGE.md).

> **Druckvorbereitung auf Nutzerwunsch zurückgestellt (PRINT_SETUP_DEFERRED_BY_USER).** Kein R19-Bambu-Projekt oder neuer Slice ist freigegeben; kein Druckauftrag gestartet. Frühere R18-Druckpakete sind historische Stände und enthalten diese Änderungen nicht. Native R19-CAD-Prüfung:94 Körper,90 bisherige Körper geometrisch unverändert. Die Übersicht zeigt den aktuellen CAD-Stand.
<!-- CURRENT_FLAT132_R19_END -->'''
 for name in ['README.md','PRINTING.md','EINKAUFSTEILE.md','DEVICE_UPGRADES.md','print/REVISION_STATUS.md']:
  p=ROOT/name;text=p.read_text();use=block.replace('](review/','](../review/') if name.startswith('print/') else block
  pat=r'<!-- CURRENT_FLAT132_R(?:16|17|18|19)_START -->.*?<!-- CURRENT_FLAT132_R(?:16|17|18|19)_END -->';assert re.search(pat,text,re.S),name
  text=re.sub(pat,use,text,count=1,flags=re.S).replace('HTML-Projektübersicht R18','HTML-Projektübersicht R19').replace('Historischer Stand R15 – für R18 die Dateien oben verwenden','Historischer Stand R15 – für R19 den CAD-Stand oben beachten; Druckvorbereitung zurückgestellt')
  p.write_text(text)
 q=read(HERE/'source-build.json');q['status']='PASS_NATIVE_CAD_RELEASED_PRINT_SETUP_DEFERRED';write(HERE/'source-build.json',q)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--publish',action='store_true');args=p.parse_args();s=prepare()
 if args.publish:publish(s)
 print(s['status'])
