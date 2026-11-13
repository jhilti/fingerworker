#!/usr/bin/env python3
"""Release native R20 CAD and documentation; no print setup or slicing."""
from pathlib import Path
import argparse,csv,hashlib,json,re,shutil
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];SOURCE=HERE/'fingerworker_R20_rear_locating_pegs.fs'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text())
def write(p,d):Path(p).write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
def prepare():
 v=read(HERE/'onshape-version.json');sh=sha(SOURCE);assert v['source_sha256']==sh and v['native_parts']==94
 verified={}
 for name in ['native-locating-fit.json','native-release-binding.json']:
  p=HERE/'validation'/name;q=read(p);assert q['status'].startswith('PASS') and q['source_sha256']==sh and not q.get('failures')
  verified[str(p.relative_to(ROOT))]=dict(status=q['status'],sha256=sha(p))
 for name,key in [('Flat132_R20_neutral_final.zip','stl_zip_sha256'),('Flat132_R20_final_AP214.step','step_sha256')]:assert sha(HERE/'native'/name)==v[key]
 assert len(read(HERE/'validation/native-step-inventory.json')['native_part_correspondence'])==94
 for image,prov in [('P01-final-native.png','P01-final-native-provenance.json'),('P01-final-native-detail.png','P01-final-native-detail.json'),('assembly-final-native.png','assembly-final-native.json'),('rigid-parts-final-native.png','rigid-parts-final-native.json'),('strap-routing.svg','strap-routing-provenance.json'),('rear-locator-detail.png','rear-locator-detail.json')]:
  p=read(HERE/'evidence'/prov);assert p['source_sha256']==sh and p['image_sha256']==sha(HERE/'evidence'/image)
 visual=read(HERE/'evidence/P01-final-native-visual-check.json');assert visual['status'].startswith('PASS') and visual['source_sha256']==sh
 url=v['url'];status='**Native R20-CAD-Geometrie geprüft. Druckvorbereitung auf deinen Wunsch zurückgestellt.** Kein neues Bambu-Projekt, kein neuer Slice und kein Druckauftrag.'
 (HERE/'README.md').write_text(f'''# Flat132 R20 – massive Positionierzapfen

Stand 13.11.2026. {status}

P06L und P06R besitzen jetzt je einen integrierten **Ø5 × 2 mm Positionierzapfen** an der Unterseite. Die Grundplatte erhält zwei passende, hinten offene Sacknuten: 5,4 mm breit, mit 0,2 mm seitlichem Spiel und 0,3 mm Bodenluft. Der Zapfenansatz ist mit R0,4 gerundet; eine 0,4-mm-Spitzenfase und eine 0,5-mm-Einführung an der Nut erleichtern das Fügen. Keine zusätzlichen Kleinteile oder biegsamen Rastarme.

Die Öffnung nach hinten ist nötig: Beide Stangenenden sitzen in Blindbohrungen. Der Block wird daher axial auf die Stange geschoben, während der Zapfen von hinten in die Nut einfährt. Eine geschlossene Bohrung für senkrechtes Einstecken würde diesen Montageweg versperren.

**Schraubenlos nur federfrei und unbelastet positionieren.** Die offene Nut verriegelt nicht gegen Herausziehen. Bereits vorgespannte Federn belasten die Blöcke in Ruhestellung. Deshalb müssen die vier vorhandenen M3×8 in ihren Inserts fest sitzen, bevor Federkraft oder andere Last freigegeben wird. Die Zapfen sind eine Pass- und Positionierhilfe, kein Ersatz für diese Befestigung.

[Onshape R20]({url}) · [Native STEP-Baugruppe](native/Flat132_R20_final_AP214.step) · [Native STL-Geometrie](native/Flat132_R20_neutral_final.zip) · [Übersicht](../../Uebersicht.html)

[Montage](MONTAGE.md) · [Review](parts-review.md) · [Stückliste](BOM_Aenderungen.csv) · [Prüfbindung](final-specification.json)

![Positionierzapfen und hinten offene Nut](evidence/rear-locator-detail.png)

Nur P01/P06L/P06R ändern sich gegenüber R19; die Baugruppe bleibt bei94 Körpern,91 davon geometrisch unverändert. Die organische Handballenauflage, weicheren Daumenmulden, Stangenbohrungen, der30-mm-Hub, Messkraftpfad und Gurtdurchlässe bleiben erhalten. P08 bleibt die optionale, mit zwei M2×8 befestigte Elektronikwanne. PLA bleibt Standard. Reale Passung und Belastbarkeit sind am Ausdruck zu prüfen.
''')
 (HERE/'MONTAGE.md').write_text('''# R20 – Positionieren und sichern

Die Druckvorbereitung ist auf Nutzerwunsch zurückgestellt. Diese Anleitung beschreibt die CAD-Konstruktion und den späteren Aufbau.

## Federfreier Passaufbau

Diese Reihenfolge beginnt mit bereits federfreien Einzelteilen. Sie ist keine Anleitung zum Zerlegen eines vorhandenen Federaufbaus: Dessen Federn bleiben auf den Stangen gefangen und besitzen auch in Ruhestellung Vorspannung. Vor dem Lösen eines Heckblocks muss diese Last kontrolliert zurückgehalten und abgebaut werden. Eine praktisch geprüfte Rückhalte- und Entlastungsprozedur ist hier noch nicht festgelegt; keinen belasteten Block einfach losschrauben.

1. Den ersten Passaufbau ohne Federn und ohne äußere Last beginnen. Vorhandene echte Führungsstangen weiterverwenden.
2. R20-Grundrahmen P01 und beide R20-Heckblöcke P06L/P06R zusammen verwenden. Die neuen Zapfen passen nicht auf den alten R19-Rahmen ohne Nuten. Keine separaten Zapfen montieren.
3. P05 und Q01 federfrei ausrichten, P04 von hinten in die zentrale Führung schieben und die Stangen einsetzen. Q01 ist nur eine unbelastete Passhilfe.
4. Jeden Heckblock von hinten axial in−X auf das Stangenende schieben. Gleichzeitig fährt sein Unterseitenzapfen durch den offenen hinteren Eingang in die Nut. Der breite Blockfuß sitzt weiterhin auf den bisherigen Auflagen; der Zapfenboden hat nominal0,3 mm Luft. Nicht senkrecht auf die eingebauten Stangen drücken.
5. Ohne Federn lassen sich Lage, Spiel und voller30-mm-Hub zunächst ohne Schrauben prüfen. Die Blöcke sind dabei nicht gegen Herausziehen verriegelt.
6. **Je zwei M3×8 pro Block in den vorhandenen M3-Inserts befestigen, vier insgesamt. Vor Federkraft, auch vor der Vorspannung in Ruhestellung, müssen alle vier Schrauben sitzen.** Ein Aufbau mit Federn und unverschraubten Blöcken ist nicht vorgesehen. Q01 vor Sensor-/Federbetrieb entfernen.

## Demontage des federfreien Passaufbaus

Nur am bereits federfreien, unbelasteten Passaufbau die zwei Schrauben des betreffenden Blocks lösen und ihn mindestens12 mm axial in+X abziehen. Der Zapfen verlässt die offene Nut in derselben Richtung; kein Rastarm muss gebogen werden. Erst danach nach oben abheben. Für einen vorhandenen Federaufbau gilt zunächst die oben beschriebene Anforderung an kontrolliertes Rückhalten und Entlasten; die Federn können nicht vorab ohne Zugang über die Heckblöcke entfernt werden.

## Unveränderte Schnittstellen

Die organische Handballenfläche und beide weichen Daumenränder bleiben wie R19. P05 bleibt separat und muss frei vom festen P01 sein. P11 dient weiter ausschließlich dem Schalterabgleich mit±0,8 mm Feinweg; es gibt keine Vorspannverstellung.

Die optionale Elektronikwanne P08 benötigt zwei M2×8 ohne Scheibe durch ihreØ2,2-mm-Löcher an X−26,5/Y±59. Die5,5-mm-Auflage lässt nominal2,5 mm Eingriff in die bestehenden M2-InsertsØ3,2×3 mm. Für Service beide Schrauben entfernen, die Wanne20 mm absenken und P09 außerhalb des Geräts öffnen. Keine früheren M2×6 übernehmen.

Vier27×4-mm-Gurtschlitze bei X28/65,Y±57,5 bleiben für zwei echte25-mm-Gurte erhalten. Bandenden von unten einführen, außen über die Stege zurückführen und am eigenen Band sichern; kein Band über die Mechanik legen.

Der geprüfte Sensor-Entnahmeweg setzt voraus, dass der Aufbau sicher entlastet ist und Federn, Stangen, Heckblöcke sowie H18/H19 bereits ausgebaut sind. Dann den Sensorstapel zuerst+X3,2 mm, danach+Z40 mm entnehmen. Das ist ein geometrischer Zugangscheck, keine validierte Entlastungsanleitung für einen Federaufbau. Für Isometrie bleiben die81-mm-Stahlhülsen mit15-mm-Anfahrweg vorgesehen. Gedruckte Passung, Insertsitz, Komfort und reale Last sind nicht durch nominales CAD qualifiziert.
''')
 (HERE/'parts-review.md').write_text(f'''# R20 – fokussiertes CAD-Review

{status}

| Bereich | Ergebnis |
|---|---|
| P06L/P06R | Je ein integrierterØ5×2-mm-Zapfen, R0,4 am Ansatz,0,4-mm-Fase an der Spitze |
| P01 | Zwei hinten offene5,4-mm-Sacknuten; BodenZ2,2;0,5-mm-Einführung |
| Passung | Nominal0,2 mm radial und0,3 mm am Boden; keine Übermaßpassung |
| Montageweg | Vollständiger12-mm-Weg in+X zur Entnahme bleibt frei; Einsetzen in−X |
| Material | Originaler Blockkörper bleibt erhalten; keine neue dünne Federlasche |
| M3-Inserts | Kleinste gemessene Wand zur Nut4,2 mm |
| Grundplattenboden |4,2 mm im Inneren;2,873 mm am geprüften gerundeten hinteren Rand |
| Teilezahl |94 Körper; nur P01/P06L/P06R geändert,91 geometrisch unverändert |
| Schrauben | Vier vorhandene M3×8 vor Federbelastung erforderlich; kein axialer Rastverschluss |
| Andere Funktionen | R19-Palm-/Daumenform, Stangenbohrungen, Hub, Kraftpfad, Gurte und Elektronik unverändert |
| Druckstatus | PRINT_SETUP_DEFERRED_BY_USER |

Die hinten offene Nut ist bewusst gewählt, weil die vorhandenen Stangen in beidseitigen Blindbohrungen sitzen. Ein senkrecht einzusetzender Zapfen in einer ringsum geschlossenen Tasche wäre mit diesem axialen Fügeweg nicht montierbar. Die neue Verbindung zentriert und erleichtert den federfreien Passaufbau; Federkraft würde einen unverschraubten Block weiterhin nach hinten herausdrücken können.

[Native Passungs- und Wegeprüfung](validation/native-locating-fit.json) · [Native Versionsbindung](validation/native-release-binding.json) · [Lokaler Vorabcheck](validation/local-locating-fit.json)
''')
 rows=[['Ref','Menge Geraet','R20-Aenderung','Hardware / Hinweis'],['P01',1,'Zwei hinten offene Sacknuten fuer integrale Heckblockzapfen.','Nur mit R20-P06L/P06R kombinieren.'],['P06L/P06R',2,'Je ein integraler Durchmesser5 x2mm Positionierzapfen.','Keine separaten Zapfen; je2 M3x8 vor Federbelastung erforderlich.'],['H30',4,'Unveraendert, fuer Federbetrieb zwingend.','4 M3x8 plus vorhandeneM3-Inserts; federfreie Passprobe ohne Schrauben moeglich.'],['P04/P05/P11',3,'Unveraendert.','Vorhandene Teile weiterverwenden.'],['Q01','Passhilfe','Unveraendert.','Nur federfrei; vor Sensor-/Federbetrieb entfernen.'],['P08/P09',2,'R19-Ausfuehrung unveraendert; optional.','P08 mit2 M2x8 und vorhandenen M2-Inserts; P09 Klickdeckel.'],['H040/H041',2,'Unveraendert.','Vorhandene echteStahlstangen.'],['G01/G02',2,'Unveraendert.','Echte25mm-Gurte.'],['NativeKoerper',94,'91 unveraendert gegenueberR19.','Druckvorbereitung bleibt zurueckgestellt.']]
 with (HERE/'BOM_Aenderungen.csv').open('w',newline='') as f:csv.writer(f).writerows(rows)
 design=read(HERE/'design-specification.json');design.update(status='PASS_NATIVE_R20_LOCATING_GEOMETRY',onshape_version=v['version_id']);write(HERE/'design-specification.json',design)
 names=['fingerworker_R20_rear_locating_pegs.fs','native/Flat132_R20_final_AP214.step','native/Flat132_R20_neutral_final.zip','design-specification.json','README.md','MONTAGE.md','parts-review.md','BOM_Aenderungen.csv']
 names += ['evidence/'+q for q in ['P01-final-native.png','P01-final-native-provenance.json','P01-final-native-detail.png','P01-final-native-detail.json','assembly-final-native.png','assembly-final-native.json','rigid-parts-final-native.png','rigid-parts-final-native.json','strap-routing.svg','strap-routing-provenance.json','rear-locator-detail.png','rear-locator-detail.json']]
 hashes={str((HERE/p).relative_to(ROOT)):sha(HERE/p) for p in names}
 spec=dict(revision='Flat132 R20 rear locating pegs',date='2026-11-13',status='PASS_NATIVE_CAD_PRINT_SETUP_DEFERRED',source_sha256=sh,onshape_version=v['version_id'],onshape_url=url,changed=['P01','P06L','P06R'],native_solids=94,unchanged_exact_native_breps=91,changed_mechanical_parts=['P01','P06L','P06R'],optional_electronics_parts=['P08','P09'],printed_device_bodies=8,verification=verified,design=design,files_sha256=hashes,print_setup_status='PRINT_SETUP_DEFERRED_BY_USER',print_ready=False,gui_verified=False,gui_status='NOT_REQUESTED_PRINT_SETUP_DEFERRED',gui_summary='Druckvorbereitung bleibt auf Nutzerwunsch zurückgestellt.',limitations='Spring-free locating fit only. Four M3 screws required before any spring preload or load. Physical PLA fit and strength unqualified.')
 write(HERE/'final-specification.json',spec);write(HERE/'documentation-ready.json',dict(status='PASS_DOCUMENTATION_BOUND_TO_R20_NATIVE_CAD',source_sha256=sh,onshape_version=v['version_id'],files_sha256=hashes,verification=verified,print_setup_status=spec['print_setup_status']));write(HERE/'source-build.json',dict(status='PASS_NATIVE_REGENERATED_AND_DOCUMENTED',source_sha256=sh,onshape_version=v['version_id'],native_solids=94,print_setup_status=spec['print_setup_status']))
 return spec

def publish(spec):
 archive=ROOT/'overview/archive-r19-final-2026-11-13'
 if not archive.exists():
  archive.mkdir();files=[ROOT/n for n in ['fingerworker_mvp.fs','Uebersicht.html','README.md','PRINTING.md','EINKAUFSTEILE.md','DEVICE_UPGRADES.md','print/REVISION_STATUS.md']]+[p for p in (ROOT/'overview').rglob('*') if p.is_file() and not any(q.startswith('archive-') for q in p.relative_to(ROOT/'overview').parts)]
  hashes={}
  for p in files:
   rel=p.relative_to(ROOT);dest=archive/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest);hashes[str(rel)]=sha(dest)
  write(archive/'archive-manifest.json',dict(revision='R19',files_sha256=hashes))
 for p,h in spec['files_sha256'].items():assert sha(ROOT/p)==h,p
 (ROOT/'fingerworker_mvp.fs').write_bytes(SOURCE.read_bytes());review=str(HERE.relative_to(ROOT))
 block=f'''<!-- CURRENT_FLAT132_R20_START -->
> **13.11.2026 – Flat132 R20: integrierte Positionierzapfen.** P06L/P06R erhalten je einenØ5×2-mm-Unterseitenzapfen; P01 passende hinten offene Sacknuten. So bleibt das axiale Aufschieben auf die Stangen möglich. Schraubenlos nur federfrei und unbelastet positionieren. **Vier M3×8 sind vor Federkraft, auch vor Vorspannung in Ruhestellung, erforderlich.** [Onshape R20]({spec['onshape_url']}) · [Native STEP]({review}/native/Flat132_R20_final_AP214.step) · [Review]({review}/README.md) · [Montage]({review}/MONTAGE.md).

> **Druckvorbereitung auf Nutzerwunsch zurückgestellt (PRINT_SETUP_DEFERRED_BY_USER).** Kein neues Bambu-Projekt, kein neuer Slice oder Druckauftrag. Native R20-CAD-Prüfung:94 Körper,91 gegenüberR19 geometrisch unverändert. Frühere Druckpakete enthalten diese neuen Zapfen/Nuten nicht.
<!-- CURRENT_FLAT132_R20_END -->'''
 for name in ['README.md','PRINTING.md','EINKAUFSTEILE.md','DEVICE_UPGRADES.md','print/REVISION_STATUS.md']:
  p=ROOT/name;text=p.read_text();use=block.replace('](review/','](../review/') if name.startswith('print/') else block
  pat=r'<!-- CURRENT_FLAT132_R(?:16|17|18|19|20)_START -->.*?<!-- CURRENT_FLAT132_R(?:16|17|18|19|20)_END -->';assert re.search(pat,text,re.S)
  text=re.sub(pat,use,text,count=1,flags=re.S).replace('HTML-Projektübersicht R19','HTML-Projektübersicht R20').replace('Historischer Stand R15 – für R19 den CAD-Stand oben beachten','Historischer Stand R15 – für R20 den CAD-Stand oben beachten');p.write_text(text)
 write(HERE/'source-build.json',dict(status='PASS_NATIVE_CAD_RELEASED_PRINT_SETUP_DEFERRED',source_sha256=spec['source_sha256'],onshape_version=spec['onshape_version'],native_solids=94,print_setup_status=spec['print_setup_status']))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--publish',action='store_true');a=p.parse_args();s=prepare()
 if a.publish:publish(s)
 print(s['status'])
