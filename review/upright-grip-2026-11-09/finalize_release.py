#!/usr/bin/env python3
"""Stage evidence-bound R16 documents; publish shared entrypoints only with --publish."""
from pathlib import Path
import argparse,csv,hashlib,json,re
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
OLD=ROOT/'review/inboard-straps-2026-11-08'
PACK=ROOT/'print/bambu-R16-upright-grip-2026-11-09'
SOURCE=HERE/'fingerworker_R16_upright_grip.fs'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text())
def write(p,d):Path(p).write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
def passed(p):
 d=read(p);assert str(d.get('status','')).startswith(('PASS','NATIVE_PROJECT')),(p,d.get('status'))
 for k in ['failures','issues','failed']:
  assert not d.get(k),(p,k,d[k])
 assert not d.get('failed_count',d.get('failed_checks',0)),p
 return d
def validate():
 sh=sha(SOURCE);version=read(HERE/'onshape-version.json');delivery=passed(PACK/'delivery-specification.json')
 assert version['source_sha256']==delivery['CAD_source_sha256']==sh
 assert version['version_id']==delivery['onshape_version']
 assert delivery['object_count']==6
 verified={}
 for p in [HERE/'validation'/n for n in ['native-geometry.json','native-motion.json','service-native.json','fixture-q01-check.json','native-stl-identity.json','native-step-trim-check.json']]+[HERE/'mechanics/preflight.json']:
  d=passed(p)
  if 'source_sha256' in d:assert d['source_sha256']==sh,p
  if 'metrics' in d:assert d['metrics']['source_sha256']==sh,p
  verified[str(p.relative_to(ROOT))]=dict(status=d['status'],sha256=sha(p))
 for path,e in delivery['verification'].items():
  p=ROOT/path;d=passed(p);assert sha(p)==e['sha256'],path
  verified[path]=e
 for path,h in delivery['files_sha256'].items():assert sha(ROOT/path)==h,path
 inv=read(HERE/'validation/native-step-inventory.json');assert len(inv['native_part_correspondence'])==93
 assert inv['native_step_sha256']==delivery['native_step_sha256']
 assert sha(HERE/'native/Flat132_R16_neutral_final.zip')==delivery['native_zip_sha256']
 cad=read(HERE/'evidence/P01-final-native-provenance.json')
 assert cad['status']=='RENDERED_FINAL_NATIVE_R16_P01'
 assert cad['source_sha256']==sh and cad['native_zip_sha256']==delivery['native_zip_sha256']
 assert cad['image_sha256']==sha(HERE/'evidence/P01-final-native.png')
 gui=passed(PACK/'validation/gui-check.json')
 assert not gui.get('printer_job_started',False)
 assert gui['source_sha256']==sh and gui['project_sha256']==sha(ROOT/delivery['project'])
 visual=passed(HERE/'evidence/P01-final-native-visual-check.json')
 assert visual['image_sha256']==cad['image_sha256'] and visual['source_sha256']==sh
 verified[str((PACK/'validation/gui-check.json').relative_to(ROOT))]=dict(status=gui['status'],sha256=sha(PACK/'validation/gui-check.json'))
 geo=read(HERE/'mechanics/design-specification.json');assert geo['source_sha256']==sh
 return sh,version,delivery,verified,geo,gui

def prepare_docs(data):
 sh,v,d,verified,g,gui=data;sec=d['estimated_seconds'];grams=d['estimated_grams']
 duration=f'{sec//3600} h {(sec%3600)//60:02d} min {sec%60:02d} s'
 project=d['project'];package=d['package'];url=v.get('url',v.get('version_url'))
 assert url and '/v/' in url
 status='**R16-CAD und berechnete PLA-Druckwege geprüft.** Die Nachweise gelten für den unten verlinkten nativen Stand. Handkomfort, sicherer Halt, Druckpassung und Belastbarkeit bleiben am Ausdruck zu prüfen.'
 (HERE/'README.md').write_text(f'''# Flat132 R16 – integrierter Druckgriff für den Handballen

Stand 09.11.2026. {status}

P01 hat jetzt eine aufrechte Handballenfläche, durchgehend gerundete Schultern über beiden vorderen Stangensockeln und zwei flache Daumenrückgriffe auf der Handgelenkseite. Die Auflage ist weiterhin Teil des Grundrahmens. Die alte erhöhte Stufe hinter dem Griff entfällt; darunter bleibt ein durchgängiges 2-mm-Dach über der Elektronik. Keine zusätzliche Kappe, kein Sleeve und keine neuen Kleinteile.

**Gegenüber R15 nur P01 neu drucken.** Die 92 anderen nativen Körper bleiben unverändert. Die Handballenfläche liegt bei X−29; die obere Höhe bleibt Z33. Der Quergriff ist 126 mm breit, die gerundeten Schultern reichen insgesamt über 130 mm. Die Grundplattenbreite und die vier innenliegenden Gurtschlitze bleiben unverändert.

**Drucksatz:** P01, P04, P05, P06, P11 und die unbelastete Passhilfe Q01 auf einer Platte. H2D, linke 0,4-mm-Standarddüse, Bambu PLA Basic; auch die Stützen sind PLA. Alle sechs Teile ohne Brim. Vorhandene echte Stangen verwenden; Elektronikgehäuse, Schrauben und Muttern sind nicht im Drucksatz. Geprüfter Slice: **{duration} / {grams:.2f} g PLA**. Ein Druckauftrag wurde nicht gestartet.

[Onshape R16]({url}) · [Bambu-Projekt](../../{project}) · [Druckpaket](../../{package}) · [Übersicht](../../Uebersicht.html)

[Montage](MONTAGE.md) · [Änderungsreview](parts-review.md) · [Stückliste](BOM_Aenderungen.csv) · [Konstruktionsmaße](mechanics/design-specification.json) · [Nachweise](final-specification.json)

![Finaler nativer R16-Grundrahmen](evidence/P01-final-native.png)

Die Daumenrückgriffe sind zum aktiven Halten vorgesehen. Sie ersetzen keinen Handgurt, wenn das Gerät auch bei entspannter Hand gehalten werden soll. Zunächst ohne Federn Handposition, Daumenkontakt und freien Hub beurteilen. Q01 vor Sensor- und Federeinbau vollständig entfernen. Die vorgesehenen Sicherungsschrauben bleiben für den Funktionsaufbau erhalten.
''')
 old=(OLD/'MONTAGE.md').read_text();body=old[old.index('## Federfreier Passaufbau'):]
 body=body.replace('R15','R16').replace('Die griffnahe integrierte Handballenauflage','Die neue aufrechte integrierte Handballenauflage')
 intro=f'''# R16 – Montage des integrierten Handballengriffs

Stand 09.11.2026. {status}

## Änderung gegenüber R15

Nur P01 ändert sich. Eine 126 mm breite aufrechte Druckfläche ersetzt die bisherige kurze Rundung. Beide Stangensockel bekommen gerundete Schultern; flache Daumenrückgriffe liegen auf der Handgelenkseite. Der Griff bleibt fest mit dem Rahmen verbunden, P05 bleibt als separates Messjoch frei. Die Höhe bleibt Z33; die 30 mm Griffbewegung und alle Montage-/Servicewege bleiben erhalten. Die alte 3-mm-Stufe auf der Handgelenkseite ist entfernt. Das darunterliegende Elektronikdach bleibt 2 mm dick; Raststellen und Schraubpiloten bleiben erhalten.

P01/P04/P05/P06/P11 und Q01 werden gemeinsam aus PLA gedruckt, ohne Brim. Die vorhandenen echten Stangen verwenden. P08/P09 bleiben für den späteren Elektronikaufbau kompatibel und fehlen absichtlich im mechanischen Drucksatz. Es gibt keine gedruckten Schrauben, Muttern oder neuen kleinen Griffteile.

## Neue Kontaktflächen prüfen

Vor dem Zusammenbau Stützreste unter dem Rahmen und in den vorgesehenen Bohrungen entfernen. Die große aufrechte Palmfläche und die gerundeten Schultern auf gleichmäßige Oberfläche prüfen. Die Daumenrückgriffe sind nur etwa 4 mm tief; ihre schrägen Dächer und die kleinen Randrundungen nicht mit Gewalt aufweiten. Die niedrig liegenden Elektronikraststellen an den Enden bleiben frei.

Federfrei den Handballen gegen die aufrechte Fläche setzen, den Daumen an einer gerundeten Schulter beziehungsweise im Rückgriff anlegen und den Fingergriff vollständig bewegen. Kontakt zu Federn, Messjoch und Sensor vermeiden. Die Rückgriffe sollen das aktive Halten unterstützen; den tatsächlichen Halt am Ausdruck prüfen. Ein entspanntes Loslassen wird durch diese Form nicht gesichert.

'''
 (HERE/'MONTAGE.md').write_text(intro+body)
 (HERE/'parts-review.md').write_text(f'''# R16 – Konstruktions- und Schnittstellenreview

{status}

| Bereich | Umsetzung |
|---|---|
| P01-Handballenfläche | Aufrechte Handgelenkseite bei X−29; obere Höhe weiterhin Z33; Quergriff 126 mm |
| Daumenkontakt | Gerundete Schultern über beiden vorhandenen Stangensockeln; 130 mm Gesamtbreite |
| Daumenrückgriffe | Beidseitig Y±51; etwa 4 mm tief; 45°-Dach; Mundkanten R0,8 |
| Kontakt-Rundungen | Handballenkante R5; Sensorseite R3; Quergriffenden R3; Schulteroberseiten R4, Schulterenden R2 |
| Tragende Verbindung | Breite vorhandene Abstützung; kein freistehender schmaler Stiel |
| Alte Stufe hinter dem Griff | Nur X−40…−29, Z11,5…14,5 entfernt; durchgängiges 2-mm-Elektronikdach und alle Raststellen bleiben |
| Stangensockel | Ursprüngliches Material und Ø6,2-Bohrungen vollständig erhalten |
| Sensorpfad | P05 bleibt vom festen Rahmen getrennt; feste Reaktion und Führung unter Z30 bleiben erhalten |
| Service | H18-Zugänge, Sensorentnahme +X3,2/+Z40, Elektronikrastung und Entnahmewege erhalten |
| Gurtaufnahme | Vier unveränderte 27×4-mm-Schlitze für zwei echte 25-mm-Gurte |
| Druckumfang | Kein zusätzliches Teil; P01 neu, übrige fünf Stücke im Druckpaket geometrisch unverändert |

Die gerundeten Schultern überdecken die zuvor scharfkantigen Sockeloberseiten. Die neue Griffgeometrie liegt hinter dem bewegten Mechanismus. Ein tiefer umlaufender Untergriff wurde nicht umgesetzt: dafür müssten Stangensockel oder Elektronikdach ausgeschnitten werden. Stattdessen bilden zwei flache, von der Handgelenkseite zugängliche Rückgriffe eine Haltekante.

Der Kraftpfad bleibt **P04 → Federn bzw. P05-Endanschläge → P05 → Druckstift → Sensor → Stahlrückplatte → feste P01-Abstützung → Handballen**. Keine neue feste Fläche darf das bewegliche Messjoch berühren. Die CAD-Prüfung bestätigt diese nominale Trennung; sie ist keine Belastungsprüfung des PLA-Teils.

Die Grundfläche bleibt unverändert. P01 liegt beim Druck mit dem Boden auf dem Bett. Die Handballenfläche ist eine Außenwand, die Daumenrückgriffe haben schräge Dächer. Der finale Slice und die Kontaktflächenprüfung sind im [Druckpaket](../../{package}) enthalten. Druckparameter und Stützen können die reale Oberfläche beeinflussen; der nächste Ausdruck bleibt die Komfort- und Montageprobe.

[Native Geometrie](validation/native-geometry.json) · [Bewegung](validation/native-motion.json) · [Service](validation/service-native.json) · [Q01](validation/fixture-q01-check.json) · [Lokaler Vorabcheck](mechanics/preflight.json)
''')
 rows=[['Ref','Menge R15 Geraet','Menge R16 Geraet','Stuecke Druckpaket','Aenderung'],
 ['P01',1,1,1,'Aufrechter integraler Handballengriff; gerundete Stangensockelschultern; zwei flache Daumenrueckgriffe; alte handgelenkseitige Stufe entfernt, Elektronikdach2mm.'],
 ['P04/P05/P06/P11',4,4,4,'Native Geometrie erhalten; vorhandene Drucke wiederverwenden.'],
 ['P08/P09',2,2,0,'Elektronikgehaeuse erhalten; nicht im mechanischen Drucksatz.'],
 ['Q01','Passhilfe','Passhilfe',1,'Unveraendert; ausschliesslich federfrei.'],
 ['H040/H041',2,2,0,'Echte vorhandene Stahlstangen verwenden.'],
 ['G01/G02',2,2,0,'25mm-Gurte maximal2mm je Lage; unveraenderte innenliegende Schlitze.'],
 ['Neue Griffkleinteile',0,0,0,'Kein Sleeve, keine Kappe, keine Zusatzclips.'],
 ['Druckteile Geraet',7,7,5,'P01/P04/P05/P06/P08/P09/P11; mechanischer Drucksatz ohneP08/P09.'],
 ['Druckstuecke Paket','','',6,'Fuenf Geraeteteile undQ01.'],
 ['Native Koerper',93,93,'','P01 neu;92 andere Koerper unveraendert.']]
 with (HERE/'BOM_Aenderungen.csv').open('w',newline='') as f:csv.writer(f).writerows(rows)
 files=[SOURCE,HERE/'native/Flat132_R16_final_AP214.step',HERE/'native/Flat132_R16_neutral_final.zip',HERE/'evidence/P01-final-native.png',HERE/'evidence/P01-final-native-provenance.json',HERE/'evidence/strap-routing.svg',HERE/'evidence/strap-routing-provenance.json',HERE/'mechanics/design-specification.json']
 files += [HERE/n for n in ['README.md','MONTAGE.md','parts-review.md','BOM_Aenderungen.csv']]
 files += [ROOT/project,ROOT/package,PACK/'delivery-specification.json']
 docfiles={str(p.relative_to(ROOT)):sha(p) for p in files}
 spec=dict(revision='Flat132 R16 upright integral palm grip',date='2026-11-09',status='PASS_NOMINAL_CAD_AND_PLA_PRINT',source_sha256=sh,onshape_version=v['version_id'],onshape_url=url,
    changed=['P01'],new=[],removed=[],native_solids=93,unchanged_exact_native_breps=92,new_prints_required=['P01'],fit_test_pieces=6,plates=1,printed_device_bodies=7,primary_printed_device_bodies=5,primary_unloaded_fixtures=1,
    omitted_from_primary_print=['P08','P09','H040','H041'],estimates=dict(seconds=sec,filament_g=grams),verification=verified,upright_grip=g,near_palm=g,
    overview_assets=dict(cad_image=str((HERE/'evidence/P01-final-native.png').relative_to(ROOT)),cad_image_provenance=str((HERE/'evidence/P01-final-native-provenance.json').relative_to(ROOT)),strap_image=str((HERE/'evidence/strap-routing.svg').relative_to(ROOT))),
    project=project,package=package,brim_policy='All six model objects: no_brim; necessary supports retained.',files_sha256=docfiles,
    limitations='Nominal CAD and computed print paths only; actual fit, comfort, retention, PLA load capacity and lifetime require physical evaluation.')
 write(HERE/'final-specification.json',spec)
 write(HERE/'documentation-ready.json',dict(status='PASS_DOCUMENTATION_BOUND_TO_R16_EVIDENCE',source_sha256=sh,onshape_version=v['version_id'],verification=verified,files_sha256=docfiles))
 write(HERE/'source-build.json',dict(status='PASS_NATIVE_REGENERATED_AND_DOCUMENTED',source_sha256=sh,onshape_version=v['version_id'],changed=['P01'],new=[],removed=[],device_prints=7,fit_pieces=6,native_solids=93,new_prints_required=['P01']))
 print('R16 documents staged. Root entrypoints remain unchanged.')

def publish(data):
 sh,v,d,verified,g,gui=data;spec=passed(HERE/'final-specification.json');docs=passed(HERE/'documentation-ready.json')
 assert spec['source_sha256']==docs['source_sha256']==sh
 for p,h in docs['files_sha256'].items():assert sha(ROOT/p)==h,p
 (ROOT/'fingerworker_mvp.fs').write_bytes(SOURCE.read_bytes())
 review=str(HERE.relative_to(ROOT));sec=d['estimated_seconds'];url=spec['onshape_url']
 block=f'''<!-- CURRENT_FLAT132_R16_START -->
> **09.11.2026 – Flat132 R16: aufrechter integrierter Handballengriff.** Breite Druckfläche, gerundete Schultern über beiden Stangensockeln und flache Daumenrückgriffe. Höhe, innenliegende Gurtschlitze, Sensorpfad und Klickfunktionen bleiben erhalten. **Gegenüber R15 nur P01 ersetzen.** Die übrigen 92 nativen Körper sind unverändert. [CAD/Review]({review}/README.md) · [Montage]({review}/MONTAGE.md) · [Onshape R16]({url}).

> **Sechs Teile auf einer H2D-Platte, alle ohne Brim:** P01/P04/P05/P06/P11 und Q01. Bambu PLA Basic, linke 0,4-mm-Düse; nötige Stützen bleiben erhalten. Echte Stangen verwenden, Elektronikgehäuse entfallen vorerst. Geprüfter Slice: **{sec//3600} h {(sec%3600)//60:02d} min / {d['estimated_grams']:.2f} g PLA**. [3MF]({d['project']}) · [Druckpaket]({d['package']}). Q01 nur federfrei; Komfort, Passung und Belastbarkeit am Ausdruck prüfen. Kein Druckauftrag gestartet. Ältere Angaben bleiben Historie.
<!-- CURRENT_FLAT132_R16_END -->'''
 for name in ['README.md','PRINTING.md','EINKAUFSTEILE.md','DEVICE_UPGRADES.md','print/REVISION_STATUS.md']:
  p=ROOT/name;s=p.read_text();use=block.replace('](review/','](../review/').replace('](print/','](../print/') if name.startswith('print/') else block
  pat=r'<!-- CURRENT_FLAT132_R(?:15|16)_START -->.*?<!-- CURRENT_FLAT132_R(?:15|16)_END -->';assert re.search(pat,s,re.S),name
  p.write_text(re.sub(pat,use,s,count=1,flags=re.S).replace('HTML-Projektübersicht R15','HTML-Projektübersicht R16'))
 build=read(HERE/'source-build.json');build['status']='PASS_NATIVE_REGENERATED_AND_RELEASED';write(HERE/'source-build.json',build)
 print('R16 root source and documentation entrypoints published.')

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--publish',action='store_true');a=p.parse_args();data=validate();prepare_docs(data)
 if a.publish:publish(data)
