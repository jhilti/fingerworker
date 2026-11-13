#!/usr/bin/env python3
"""Publish R13 only after native and print validations are complete."""
from pathlib import Path
import hashlib,json,re
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
PACK=ROOT/'print/bambu-R13-simple-palm-2026-11-03'
BASE='Fingerworker_R13_H2D_04mm_PLA_Fit_Test'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text())
source=HERE/'fingerworker_R13_simple_palm.fs';source_hash=sha(source)
version=read(HERE/'onshape-version.json');layout=read(PACK/'plate-layout.json')
assert layout['native_R13_version']==version['version_id']
assert layout['CAD_source_sha256']==source_hash==version['source_sha256']
reports=[HERE/'validation/native-geometry.json',HERE/'validation/native-motion.json',HERE/'validation/service-native.json',HERE/'mechanics/preflight.json',HERE/'validation/fixture-q01-check.json',PACK/'validation/native-project-check.json',PACK/'validation/toolpath-check.json',PACK/'validation/print-feature-check.json',PACK/'validation/palm-support-check.json',PACK/'validation/p04-surface-check.json',PACK/'validation/cli-diagnostics.json']
verified={}
for p in reports:
 d=read(p);assert d['status'].startswith(('PASS','NATIVE_PROJECT')),(p,d['status'])
 assert not d.get('failures') and not d.get('issues') and not d.get('failed'),p
 for key in ('source_sha256','CAD_source_sha256'):
  if key in d:assert d[key]==source_hash,(p,key)
 verified[str(p.relative_to(ROOT))]={'status':d['status'],'sha256':sha(p)}
native=read(reports[0]);motion=read(reports[1]);qa=read(PACK/'validation/native-project-check.json')
assert len(native['unchanged_native_breps'])==92
assert native['native_step_sha256']==sha(HERE/'native/Flat132_R13_final_AP214.step')
assert native['native_zip_sha256']==sha(HERE/'native/Flat132_R13_neutral_final.zip')
assert motion['native_step_sha256']==native['native_step_sha256']
assert qa['native_sha256']==sha(PACK/(BASE+'.3mf'))
project=PACK/(BASE+'.3mf');package=PACK/(BASE+'_Package.zip');assert package.is_file()
spec=read(ROOT/'review/simplification-2026-11-03/final-specification.json')
spec.update(revision='Flat132 R13 continuous palm support',date='2026-11-03',status='PASS_NOMINAL_CAD_AND_PLA_PRINT',source_sha256=source_hash,onshape_version=version['version_id'],onshape_url=version['url'],changed=['P01'],new=[],removed=[],unchanged_exact_native_breps=92,new_prints_required=['P01'],fixed_sensor_reaction_area_mm2=454.4,estimates=qa['estimates'],verification=verified)
spec['palm_simplification']={'constant_radius_mm':10.25,'nominal_rail_length_mm':116,'web_envelope_mm':[[-27,-58,9.5],[-17.1,58,30]],'added_solid_volume_mm3':next(x['added_volume_mm3'] for x in read(HERE/'mechanics/preflight.json')['checks'] if 'added_volume_mm3' in x),'existing_electronics_clearance_below_z9_5_preserved':True,'R12_Q01_compatible':True}
spec['overview_assets']={'cad_image':'review/palm-simplification-2026-11-03/evidence/onshape-R13-simple-palm.png'}
spec['files_sha256']={str(p.relative_to(ROOT)):sha(p) for p in [source,project,package,HERE/'native/Flat132_R13_final_AP214.step',HERE/'native/Flat132_R13_neutral_final.zip']}
(HERE/'final-specification.json').write_text(json.dumps(spec,indent=2)+'\n')
(ROOT/'fingerworker_mvp.fs').write_bytes(source.read_bytes())
build=read(HERE/'source-build.json')
assert build['source_sha256']==source_hash
build.update(status='PASS_NATIVE_REGENERATED_AND_RELEASED',onshape_version=version['version_id'],native_geometry_report_sha256=sha(reports[0]))
(HERE/'source-build.json').write_text(json.dumps(build,indent=2)+'\n')
review='review/palm-simplification-2026-11-03';pack='print/bambu-R13-simple-palm-2026-11-03'
block=f"""<!-- CURRENT_FLAT132_R13_START -->
> **03.11.2026 – aktueller Flat132 R13, PLA:** Die Handballenauflage ist jetzt ein durchgängiger abgerundeter Balken mit breiter Verbindung zum Rahmen. Alte Stufen, schmale Stützrippen und Zwischenräume gehen in einer einfachen Form auf. **Gegenüber R12 nur P01 neu drucken.** Die übrigen sechs Gerätedruckteile, Q01 und die beiden Stangen-Formhilfen bleiben kompatibel. Elektronikunterseite, Klickflächen, Sensoraufnahme, 30-mm-Hub und feste Anschläge bleiben erhalten. Beide Vorspannverstellungen bleiben entfernt. [CAD/Review]({review}/README.md) · [Montage]({review}/MONTAGE.md) · [Onshape R13]({version['url']}).

> [Bambu H2D / 0,4 mm / PLA – 3MF]({pack}/{BASE}.3mf) · [Druckpaket ZIP]({pack}/{BASE}_Package.zip). Sieben Geräteteile, drei unbelastete Passhilfen, drei Platten. Alle Platten tatsächlich gesliced. Keine gedruckten Schrauben/Muttern. Die neue Form ist geometrisch und auf Druckbarkeit geprüft; reale Passung, Handkomfort und Belastbarkeit bleiben am Muster zu prüfen. Ältere Revisionsangaben unten sind historisch.
<!-- CURRENT_FLAT132_R13_END -->"""
for name in ['README.md','PRINTING.md','EINKAUFSTEILE.md','DEVICE_UPGRADES.md','print/REVISION_STATUS.md']:
 p=ROOT/name;s=p.read_text();use=block
 if name.startswith('print/'):
  use=block.replace('](review/','](../review/').replace('](print/','](../print/')
 s=re.sub(r'<!-- CURRENT_FLAT132_R(?:12|13)_START -->.*?<!-- CURRENT_FLAT132_R(?:12|13)_END -->',use,s,count=1,flags=re.S)
 s=s.replace('HTML-Projektübersicht R12','HTML-Projektübersicht R13');p.write_text(s)
minutes=(qa['estimated_seconds']+59)//60
(HERE/'README.md').write_text(f'''# Flat132 R13 – einfache Handballenauflage

Die markierte Handballenaufnahme ist jetzt ein durchgängiger abgerundeter Balken mit einer breiten Verbindung zum Rahmen. Die abgestuften Enden, schmalen Stützrippen und offenen Zwischenräume sind in einer einfachen Form zusammengefasst. Der bisherige Kontaktradius von 10,25 mm bleibt erhalten und läuft über eine nominelle Länge von 116 mm. Die höhere mittlere Sensorwand bleibt als funktionaler Schutz bestehen.

**Gegenüber R12 nur P01 neu drucken.** P04, P05, P06, P08, P09, P11, Q01 und beide Stangen-Formhilfen bleiben verwendbar. Der vollständige Satz enthält weiterhin sieben Geräteteile und drei federfreie Passhilfen auf drei Platten. Es kommen keine Kleinteile hinzu.

Die vorhandenen Freiräume unterhalb Z9,5, die Elektronik-Rastflächen und der gesamte Sensor-/Stangenbereich vor X−17 sind unverändert. Der Deckel behält 0,6 mm nominellen Abstand. Beide optionalen M2-Piloten wurden nach der Vereinigung erneut ausgeschnitten. Beide Vorspannverstellungen bleiben entfernt; Hub 30 mm und Isometrie-Anfahrweg 15 mm bleiben erhalten.

[Onshape R13]({version['url']}) · [Bambu-Projekt](../../{pack}/{BASE}.3mf) · [Druckpaket](../../{pack}/{BASE}_Package.zip) · [HTML-Übersicht](../../Uebersicht.html)

[Änderungsreview](parts-review.md) · [Montage](MONTAGE.md) · [Stückliste](BOM_Aenderungen.csv) · [Geprüfte Spezifikation](final-specification.json)

Die neue native P01-Geometrie wurde gegen die unabhängige Konstruktion geprüft. Alle 92 anderen nativen Körper sind exakt zum R12-Stand erhalten. Sensor-Service, voller Hub und die Rastfunktionen sind nominal geprüft. Die drei H2D-Platten wurden vollständig mit PLA gesliced und auf Stützen, Brücken und Fingerkontaktflächen geprüft. Schätzung für den vollständigen Satz: **{minutes//60} h {minutes%60:02d} min / {qa['estimated_grams']:.2f} g PLA**. Das 3MF als Projekt öffnen, damit die geprüften individuellen Druckeinstellungen erhalten bleiben.

Die breitere Handballenform, reale Passungen, PLA-Kriechen und Belastbarkeit sind am Ausdruck zu bestätigen. Clips dienen der federfreien Montage; für Federlast bleiben die vorgesehenen Sicherungsschrauben erforderlich. Q01 und gedruckte Stangen sind ausschließlich Passhilfen.
''')
print(json.dumps({'status':spec['status'],'revision':'R13','source_sha256':source_hash,'reports':len(reports)},indent=2))
