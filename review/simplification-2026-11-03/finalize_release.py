#!/usr/bin/env python3
"""Publish the R12 local entry points only after hash-bound native checks pass."""
from pathlib import Path
import hashlib,json,re

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
PACK=ROOT/'print/bambu-R12-simplified-2026-11-03'
BASE='Fingerworker_R12_H2D_04mm_PLA_Fit_Test'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text())
source=HERE/'fingerworker_R12_simplified.fs';source_hash=sha(source)
version=read(HERE/'onshape-version.json')
layout=read(PACK/'plate-layout.json')
assert layout['native_R12_version']==version['version_id']
assert layout['CAD_source_sha256']==source_hash==version['source_sha256']
reports=[HERE/'validation/native-geometry.json',HERE/'validation/native-motion.json',
 HERE/'validation/service-native.json',HERE/'independent-fixed-front-check.json',
 HERE/'fixture/validation.json',PACK/'validation/native-project-check.json',
 PACK/'validation/toolpath-check.json',PACK/'validation/print-feature-check.json',
 PACK/'validation/p04-surface-check.json']
verified={}
for p in reports:
 d=read(p);assert d['status'].startswith(('PASS','NATIVE_PROJECT')),(p,d['status'])
 assert not d.get('failures') and not d.get('issues') and not d.get('failed'),p
 for key in ('source_sha256','CAD_source_sha256'):
  if key in d:assert d[key]==source_hash,(p,key)
 verified[str(p.relative_to(ROOT))]={'status':d['status'],'sha256':sha(p)}
native=read(reports[0]);motion=read(reports[1]);qa=read(PACK/'validation/native-project-check.json')
assert native['native_step_sha256']==sha(HERE/'native/Flat132_R12_final_AP214.step')
assert native['native_zip_sha256']==sha(HERE/'native/Flat132_R12_neutral_final.zip')
assert motion['native_step_sha256']==native['native_step_sha256']
assert motion['native_stl_archive_sha256']==native['native_zip_sha256']
assert qa['native_sha256']==sha(PACK/(BASE+'.3mf'))
assert len(native['unchanged_native_breps'])==90
project=PACK/(BASE+'.3mf');package=PACK/(BASE+'_Package.zip');assert package.is_file()
paths=[source,project,package,HERE/'native/Flat132_R12_final_AP214.step',HERE/'native/Flat132_R12_neutral_final.zip']
spec=dict(revision='Flat132 R12 simplified PLA click assembly',date='2026-11-03',
 status='PASS_NOMINAL_CAD_AND_PLA_PRINT',source_sha256=source_hash,
 onshape_version=version['version_id'],onshape_url=version['url'],
 native_solids=93,device_bodies=40,electronics_reference_bodies=53,
 printed_device_bodies=7,fit_test_pieces=10,plates=3,
 changed=['P01','P08'],new=['P06'],removed=read(HERE/'source-build.json')['removed'],
 unchanged_exact_native_breps=90,PLA_standard=True,second_material_required=False,
 P01_reprint_required=True,P04_reprint_for_surface=False,new_prints_required=['P01','P06','Q01'],
 fixed_preload_adjustment_mm=0,fixed_rear_advance_mm=0,user_travel_mm=30,
 isometric_approach_mm=15,isometric_sleeve_length_mm=81,
 rest_spring_length_mm=96,rest_spring_compression_mm={'DF2194':6,'DF2185':9},
 fixed_sensor_reaction_area_mm2=454.4,
 estimates=qa['estimates'],verification=verified,
 files_sha256={str(p.relative_to(ROOT)):sha(p) for p in paths},
 limitations='Nominal CAD and calculated toolpaths only. Real PLA fit, latch force, support removal, cycling, creep, sensor calibration and loaded performance require physical verification. Clips support unloaded assembly; securing screws remain for loaded use. No 500 N qualification. Q01/printed rods are unloaded fit aids only.')
(HERE/'final-specification.json').write_text(json.dumps(spec,indent=2)+'\n')
(ROOT/'fingerworker_mvp.fs').write_bytes(source.read_bytes())
review='review/simplification-2026-11-03';pack='print/bambu-R12-simplified-2026-11-03'
block=f'''<!-- CURRENT_FLAT132_R12_START -->
> **03.11.2026 – aktueller Flat132 R12, PLA:** Sieben Gerätedruckteile statt zehn. Eine lösbare Klicktraverse P06 ersetzt beide hinteren Kappen und Anschlagschuhe. Alle hinteren und zentralen Vorspannverstellungen entfallen, einschließlich H13-Daumenrad; H12 stützt sich fest in P01 ab. 21 bisherige Metallteile entfallen. P11 bleibt ausschließlich zur Schalterkalibrierung. **P01, P06 und Q01 neu drucken; vorhandene R11-P04/P05/P08/P09/P11 bleiben verwendbar.** [CAD/Review]({review}/README.md) · [Montage]({review}/MONTAGE.md) · [Stückliste]({review}/BOM_Aenderungen.csv) · [Onshape R12]({version['url']}).

> [Bambu H2D / 0,4 mm / PLA – 3MF]({pack}/{BASE}.3mf) · [Druckpaket ZIP]({pack}/{BASE}_Package.zip). **10 Druckstücke auf drei Platten:** sieben Geräteteile, zwei unbelastete Stangen-Formhilfen, neue Q01. Keine gedruckten Schrauben/Muttern. Alle Platten tatsächlich gesliced; Fingerkontaktflächen ohne Supportkontakt. Fester Hub 30 mm, Isometrie-Anfahrweg 15 mm mit 81-mm-Hülsen. Die Federn bleiben in Ruhe 6/9 mm komprimiert; nur die Verstellmechanismen entfallen. Reale Passung/Festigkeit bleiben am Muster zu prüfen. Ältere Revisionsangaben unten sind historisch.
<!-- CURRENT_FLAT132_R12_END -->'''
for name in ['README.md','PRINTING.md','EINKAUFSTEILE.md']:
 p=ROOT/name;text=p.read_text()
 text=re.sub(r'<!-- CURRENT_FLAT132_R(?:11|12)_START -->.*?<!-- CURRENT_FLAT132_R(?:11|12)_END -->',block,text,count=1,flags=re.S)
 text=text.replace('HTML-Projektübersicht R11','HTML-Projektübersicht R12')
 p.write_text(text)
revision_status=ROOT/'print/REVISION_STATUS.md'
status_text=revision_status.read_text()
relative_block=block.replace('](review/','](../review/').replace('](print/','](../print/')
status_text=re.sub(r'<!-- CURRENT_FLAT132_R(?:11|12)_START -->.*?<!-- CURRENT_FLAT132_R(?:11|12)_END -->',relative_block,status_text,count=1,flags=re.S)
revision_status.write_text(status_text)
upgrade=ROOT/'DEVICE_UPGRADES.md'
if upgrade.exists():
 text=upgrade.read_text();text=re.sub(r'<!-- CURRENT_FLAT132_R12_START -->.*?<!-- CURRENT_FLAT132_R12_END -->\n*','',text,count=1,flags=re.S)
 upgrade.write_text(block+'\n\n'+text)
seconds=qa['estimated_seconds'];minutes=(seconds+59)//60
readme=f'''# Flat132 R12 – vereinfachte PLA-Klickmontage

Die tatsächlichen Gerätedruckteile wurden von 10 auf 7 reduziert. P060/P061/P120/P121 werden durch eine gemeinsame abnehmbare Traverse P06 ersetzt. Hintere Rücklaufverstellung und zentrale H13-Vorspannung sind vollständig entfernt; 21 Metallteile entfallen. Die feste H12-Auflage ist in den durchgängigen Rahmen mit Handballenauflage integriert.

**Neu drucken: P01, P06 und die neue Q01-Passhilfe.** Ein vorhandenes R11-P08 bleibt kompatibel, obwohl die neue Wanne zwei unbenutzte Pilotlöcher weniger hat. P04/P05/P09/P11 und vorhandene passende Stangen-Formhilfen sind unverändert. Der Griff behält seine gerundeten Komfortflächen und die geprüfte Drucklage mit Fingerkontaktfläche nach oben. Die großen rückseitigen PLA-Clips erlauben federfreies Zusammenstecken; vier M3-Sicherungen bleiben für den Funktionsaufbau vorgesehen.

Der echte Sensor und seine Stahlstütze bleiben erhalten. P05 bleibt schwimmend, damit der Kraftpfad durch den Sensor führt. P09 bleibt ein separater sauber gedruckter Klickdeckel: Eine getestete Fusion erzeugte Support auf der nur 0,05 mm freien PCB-Halterfläche und wurde verworfen. P11 bleibt das einzige kleine gedruckte Kalibrierteil, weil die reale Schaltertoleranz weiterhin ±0,8 mm Einstellung benötigt.

Feste Geometrie: 30 mm Nutzweg, 15 mm Anfahrweg mit 81-mm-Isometriehülsen, 96 mm Feder-Einbaulänge in Ruhe. Die vorhandenen 102/105 mm Federn bleiben 6/9 mm komprimiert. Keine verbleibende Vorspannverstellung, aber auch keine Behauptung kraftloser Federn. Die Sensorstützfläche beträgt 454,4 mm². Sensorservice: nach Entfernen der Federn/Stangen/Traverse und H18/H19 den kompletten Stapel +X 3,2 mm und dann +Z 40 mm entnehmen.

[Onshape R12]({version['url']}) · [Bambu-Projekt](../../{pack}/{BASE}.3mf) · [Druckpaket](../../{pack}/{BASE}_Package.zip) · [HTML-Übersicht](../../Uebersicht.html)

[Alle Teile im Review](parts-review.md) · [Montage und Service](MONTAGE.md) · [Stücklistenänderungen](BOM_Aenderungen.csv) · [Geprüfte Spezifikation](final-specification.json)

Finale Prüfung: 93 native CAD-Körper, drei geänderte/neue Druckkörper gegen unabhängige CSG und 90 andere Körper identisch zu R11; Bewegungs-/Entriegelungs- und Sensorserviceprüfung. Alle zehn Druckobjekte 1:1 ohne Meshreparatur in ein natives H2D-3MF übernommen und auf drei Platten vollständig gesliced. Gesamtabschätzung: **{minutes//60} h {minutes%60:02d} min / {qa['estimated_grams']:.2f} g PLA** einschließlich Brims/Stützen. Kein Druckauftrag wurde versendet.

Die tatsächlichen Rasten, Drucktoleranzen, Stützentfernung, PLA-Kriechen, Kraftkalibrierung und Belastbarkeit sind am Muster zu prüfen. Gedruckte Stangen und Q01 dienen ausschließlich der federfreien Passprobe; keine 500-N-Freigabe.
'''
(HERE/'README.md').write_text(readme)
print(json.dumps({'status':spec['status'],'source_sha256':source_hash,'onshape_version':version['version_id'],'reports':len(reports)},indent=2))
