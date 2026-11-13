#!/usr/bin/env python3
"""Bind R15 documents and publish only the final native/no-brim print release."""
from pathlib import Path
import argparse,csv,hashlib,json,re
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
OLD=ROOT/'review/near-palm-2026-11-06'
PACK=ROOT/'print/bambu-R15-inboard-straps-2026-11-08'
BASE='Fingerworker_R15_H2D_04mm_PLA_Inboard_Straps';SOURCE=HERE/'fingerworker_R15_inboard_straps.fs'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text())
def write(p,d):Path(p).write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
def passed(p):
 d=read(p);assert str(d['status']).startswith(('PASS','NATIVE_PROJECT')),(p,d['status'])
 assert not d.get('failures') and not d.get('issues') and not d.get('failed'),p
 assert not d.get('failed_count',d.get('failed_checks',0)),p
 return d

def validate():
 source_hash=sha(SOURCE);v=read(HERE/'onshape-version.json');layout=read(PACK/'plate-layout.json')
 assert v['source_sha256']==source_hash==layout['CAD_source_sha256'] and layout['native_R15_version']==v['version_id']
 assert layout['object_count']==6 and layout['plate_count']==1 and layout['modifier_count']==4
 assert {r['ref'] for r in layout['placements']}=={'P01','P04','P05','P06','P11','Q01'}
 paths=[HERE/'validation'/n for n in ['native-geometry.json','native-motion.json','service-native.json','fixture-q01-check.json','independent-strap-native.json']]
 paths+=[HERE/'mechanics/preflight.json',HERE/'evidence/strap-routing-visual-check.json']
 paths+=[PACK/'validation'/n for n in ['native-project-check.json','toolpath-check.json','print-feature-check.json','palm-support-check.json','strap-slot-check.json','strap-routing-check.json','p04-surface-check.json','no-brim-check.json','cli-diagnostics.json','independent-profile-review.json']]
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
  verified[str(p.relative_to(ROOT))]={'status':d['status'],'sha256':sha(p)}
 native=read(paths[0]);motion=read(paths[1]);service=read(paths[2]);fixture=read(paths[3]);qa=read(PACK/'validation/native-project-check.json')
 assert len(native['unchanged_native_breps'])==92
 assert native['native_step_sha256']==sha(HERE/'native/Flat132_R15_final_AP214.step')==motion['native_step_sha256']==fixture['native_assembly_step_sha256']
 assert native['native_zip_sha256']==sha(HERE/'native/Flat132_R15_neutral_final.zip')==service['native_archive_sha256']
 assert qa['all_checks_passed'] and all(qa['checks'].values()) and qa['geometry_and_orientations_preserved']
 geo=read(HERE/'mechanics/design-specification.json');assert geo['source_sha256']==source_hash
 st=geo['strap_mount'];assert st['slot_count']==4 and st['position_count']==2 and st['slot_size_mm']==[27,4]
 assert st['slot_center_y_mm']==[-57.5,57.5] and st['overall_width_mm']==132.4 and st['strap_width_mm']==25
 assert st['position_x_mm']==[28,65]
 assert st['strap_thickness_envelope_mm']==2
 route=read(HERE/'evidence/strap-routing-provenance.json');visual=passed(HERE/'evidence/strap-routing-visual-check.json')
 assert route['source_sha256']==source_hash and route['native_step_sha256']==native['native_step_sha256']
 assert route['image_sha256']==sha(HERE/'evidence/strap-routing.svg')==visual['svg_sha256']
 assert visual['rendered_png_sha256']==sha(HERE/'evidence/strap-routing-preview.png')
 return source_hash,v,layout,verified,native,qa,geo

def strap_text(geo):
 st=geo['strap_mount'];a,b=st['position_x_mm'];sep=b-a
 return f'''<!-- STRAP_ROUTING_START -->
## Befestigung mit zwei Gurten

Die vier gerundeten **27 × 4-mm-Öffnungen liegen in der Grundplatte**, symmetrisch bei **Y±57,5 mm**. Die äußeren R14-Laschen entfallen vollständig. Der Hauptboden bleibt **132 mm breit**; vorhandene Klickgegenhalter ergeben **132,4 mm P01-Außenmaß**. Die zwei Gurtpositionen bei **X{a:g} und X{b:g} mm** liegen **{sep:g} mm auseinander**. Sie sind so angeordnet, dass die Bänder die Federsitze und den Griff auch am Ende seines 30-mm-Hubs freilassen.

Der native Bewegungsnachweis ergibt für eine einzelne 2-mm-Gurtlage mindestens **2,26 mm Abstand zu den bewegten Federsitzen** und **3,5 mm zur hinteren Griffbrücke**. Keine doppelte Gurtlage über den Steg legen; die Rückfaltung gehört außerhalb der Platte. Der Abstand der Gurtpositionen sinkt von 75 auf {sep:g} mm. Dadurch nimmt ihre geometrische Abstützung gegen Verdrehen ab; den sicheren Sitz am tatsächlichen Gegenstand beim Passaufbau beurteilen.

Die Schlitze durchtrennen lokal den 6-mm-Boden. Es gibt keine flächige Bodenvertiefung und keine neue dünne Gurtbrücke. Neben jedem Schlitz bleiben nominal **6,5 mm äußerer Steg** und **17,5 mm innerer Restquerschnitt** bis zur vorhandenen Rahmenöffnung. Diese Maße und die lokale massive Füllung sind keine geprüfte Tragfähigkeitsangabe.

Benötigt werden **zwei echte 25-mm-Gurte**, höchstens **2 mm dick** im Durchlass. Die beiden Enden jedes Gurts müssen sich nach außen zurückfalten und sicher am eigenen Gurt befestigen lassen. Die Länge richtet sich nach dem Gegenstand oder Oberschenkelumfang plus beiden Rückfaltungen. Gurte werden nicht gedruckt. Die vier Schlitzbereiche und ihre tragenden Stege werden lokal mit 100 % geradlinigem Infill gedruckt; der übrige P01 bleibt bei 20 % Gyroid. Die Modifikatoren sind Einstellungen im 3MF, keine zusätzlichen Teile.

1. Den langen Gurt unten um den Gegenstand führen. Je ein Ende von unten durch die linke beziehungsweise rechte Öffnung derselben X-Position nach oben stecken.
2. Jedes Ende direkt über den **äußeren Plattensteg** und dann außerhalb der Plattenkante nach unten zurückführen. Die doppelte Lage bleibt außen; im Durchlass liegt nur eine Lage.
3. Beide Enden sicher am eigenen Gurt befestigen. Keine Gurtstrecke quer über Griff oder Federn führen. Den zweiten Gurt an der anderen Position genauso montieren.

![Gurtführung am nativen Schnitt der Grundplatte](evidence/strap-routing.svg)

Die Abbildung zeigt die echte Rahmenkontur; Gurt und Gegenstand sind schematisch. Vor der ersten belasteten Nutzung zunächst federfrei den Sitz, vollen Hub und die sichere Endbefestigung prüfen. Für Demontage und Elektronikservice die Gurte abnehmen. Reale Gurtpassung, Druckfestigkeit, Rutschfestigkeit und Dauerverhalten sind noch zu prüfen.
<!-- STRAP_ROUTING_END -->'''

def prepare_docs(data):
 sh,v,layout,verified,native,qa,geo=data
 status='<!-- RELEASE_STATUS_START -->\n**Nominale R15-CAD- und PLA-Druckprüfung bestanden.** Native Geometrie, voller Hub, Sensorservice, Q01-Passung und tatsächliche Druckwege sind an diese Revision gebunden. Reale Passung, Haftung, Komfort und Belastbarkeit bleiben am Ausdruck zu prüfen.\n<!-- RELEASE_STATUS_END -->'
 montage=(OLD/'MONTAGE.md').read_text();start=montage.index('## Federfreier Passaufbau');end=montage.index('<!-- STRAP_ROUTING_START -->')
 body=montage[start:end]
 body=body.replace('Brims und alle zugänglichen Stützen entfernen.','Alle zugänglichen Stützen entfernen. Das R15-Projekt druckt alle sechs Teile ohne Brim.')
 body=body.replace('Die Grundplatte bleibt 132 mm breit; die neuen äußeren Gurtösen ergeben **156 mm Gesamtbreite**. Die hinteren Rastarme liegen innerhalb dieser Breite.','Der Hauptboden bleibt mit innenliegenden Gurtschlitzen **132 mm breit**; P01 misst einschließlich vorhandener Klickgegenhalter **132,4 mm**. Die vorhandenen hinteren Rastarme ergeben weiterhin **135,2 mm maximale Baugruppenbreite**.')
 intro=f'''# R15 – Gurtschlitze innerhalb der Grundplatte

Stand 08.11.2026. PLA, Bambu H2D, Standarddüse 0,4 mm.

{status}

## Was sich gegenüber R14 ändert

Die vier seitlich vorstehenden Gurtlaschen entfallen. Vier gerundete Schlitze in der Grundplatte übernehmen die Aufnahme der beiden 25-mm-Bänder. Die griffnahe integrierte Handballenauflage, Sensorabstützung, zentrale Führung und Klickfunktionen bleiben erhalten. Gegenüber R14 ist nur **P01 neu zu drucken**; die übrigen 92 nativen Körper ändern ihre Geometrie nicht.

**Druckumfang:** P01/P04/P05/P06/P11 und Q01, sechs Stücke auf einer Platte. Vorhandene echte Führungsstangen verwenden. P08/P09 und gedruckte Stangen entfallen in diesem mechanischen Druckauftrag. Keine Schrauben oder Muttern drucken. Q01 ist ausschließlich eine federfreie Sensor-Passhilfe.

Alle sechs Modelle werden **ohne Brim** gedruckt. Benötigte Stützen bleiben erhalten; sie sind nicht mit dem dünnen umlaufenden Haftrand zu verwechseln. Das kleine P11 bei der ersten Schicht kurz auf Haftung beobachten. Das Druckprofil ersetzt keine reale Haftungsprüfung.

'''
 (HERE/'MONTAGE.md').write_text(intro+body+strap_text(geo)+'\n\n[Native Geometrie](validation/native-geometry.json) · [Bewegung](validation/native-motion.json) · [Sensorservice](validation/service-native.json) · [Q01-Passung](validation/fixture-q01-check.json)\n')
 st=geo['strap_mount'];a,b=st['position_x_mm']
 review=f'''# R15 – Änderungsreview der innenliegenden Gurtaufnahme

{status}

P01 verliert die vier äußeren R14-Laschen. Neue 27 × 4-mm-Schlitze bei X{a:g}/{b:g} und Y±57,5 liegen auf beiden Seiten innerhalb der ursprünglichen 132-mm-Platte. Die Positionen werden gegenüber den bisherigen äußeren Ösen nach innen und axial verschoben, um den vollständigen Griffhub und die Federsitze freizuhalten. Ein nur seitliches Verschieben der R14-Schlitze wäre nicht ausreichend.

| Schnittstelle | R15 |
|---|---|
| Handballenauflage | R14-Form und Lage exakt erhalten |
| P04/P05/P06/P11, Sensorhardware, Stangen und Federn | Native Geometrie unverändert |
| P08/P09 und Servicezugänge | Weiter vorhanden, nicht Teil dieses Drucksatzes |
| Gurte | Zwei echte 25-mm-Bänder, höchstens 2 mm je Lage |
| Schlitze | Vier, 27 × 4 mm, innerhalb P01 |
| Boden | 6 mm; nur die Schlitze schneiden lokal hindurch, keine Gurtvertiefung |
| Verbleibender Steg außen / innen | Nominal 6,5 / 17,5 mm |
| Hauptboden / P01 / maximale Baugruppenbreite | 132 / 132,4 / 135,2 mm |
| Druck | Eine Platte, sechs Teile, alle ohne Brim; benötigte Stützen erhalten |

Die Öffnungen reduzieren lokal den Nettoquerschnitt der Seitenstreifen. Der neue Aufbau wird deshalb nicht als gleich fest wie der ungeschnittene R14-Boden bezeichnet. Im Projekt sind die Schlitzbereiche mit 100 % geradlinigem Infill vorgesehen. Der nominale Geometrie- und Drucknachweis bestätigt weder Zugkraft der Befestigung noch PLA-Kriechen oder Lebensdauer.

Die [Konstruktionsmaße](mechanics/design-specification.json), [native Geometrie](validation/native-geometry.json), [vollständige Bewegung](validation/native-motion.json), [Sensorservice](validation/service-native.json) und [Q01-Passung](validation/fixture-q01-check.json) sind an den finalen R15-Stand gebunden.

{strap_text(geo)}
'''
 (HERE/'parts-review.md').write_text(review)
 rows=[['Ref','Menge R14 Geraet','Menge R15 Geraet','Stuecke aktuelles Druckpaket','Aenderung'],['P01',1,1,1,'Vier aeussere Laschen entfallen; vier27 x4 mm-Gurtschlitze innen; Hauptboden132 mm, P01-Aussenmass132,4 mm; R14-Handballenauflage erhalten.'],['P04/P05/P06/P11',4,4,4,'Native Geometrie exakt erhalten; vorhandene Drucke verwenden. Neue Projektvariante ohne Brims.'],['P08/P09',2,2,0,'Elektronikaufnahme unveraendert; im mechanischen Druckauftrag weggelassen.'],['H040/H041',2,2,0,'Echte Fuehrungsstangen vorhanden; nicht drucken.'],['Q01','Passhilfe','Passhilfe',1,'Unveraendert und nur federfrei verwenden.'],['G01/G02',2,2,0,'Zwei25 mm-Gurte, max2 mm Dicke, beide Enden sicher rueckfaltbar; Laenge nach Umfang. Nicht drucken.'],['Druckteile Geraet',7,7,5,'Keine neuen kleinen Teile.'],['Druckstuecke aktuelles Paket','','',6,'Fuenf Geraeteteile und eine Passhilfe.'],['Zusaetzliche Kaufteile',0,0,0,'Keine zusaetzlichen Kaufteile gegenueber R14; zwei Gurte bleiben erforderlich.'],['Native CAD-Koerper',93,93,'','P01 geaendert;92 andere Koerper exakt erhalten.']]
 with (HERE/'BOM_Aenderungen.csv').open('w',newline='') as f:csv.writer(f).writerows(rows)
 sec=qa['estimate_seconds']
 (HERE/'README.md').write_text(f'''# Flat132 R15 – innenliegende Gurtschlitze, ohne Brims

{status}

Vier **27 × 4-mm-Gurtschlitze auf beiden Seiten innerhalb der Grundplatte** ersetzen die äußeren R14-Laschen. Der Hauptboden ist 132 mm breit; P01 misst wegen bestehender Klickgegenhalter 132,4 mm; die vorhandenen hinteren Rastarme bestimmen die maximale Baugruppenbreite von135,2 mm. Die integrierte griffnahe Handballenauflage bleibt unverändert.

**Gegenüber R14 nur P01 neu drucken.** Die übrigen92 nativen Körper sind unverändert. Der mechanische Drucksatz enthältP01/P04/P05/P06/P11 undQ01 auf einer Platte. Vorhandene echte Stangen verwenden; Elektronikgehäuse und gedruckte Stangen entfallen.

Alle sechs Modelle drucken ohne Brim; erforderliche Stützen bleiben erhalten. Vier Wände,20 % Gyroid, lokal100 % an den Gurtstegen; PLA, H2D,0,4-mm-Standarddüse. Tatsächlicher Slice: **{sec//3600} h {(sec%3600)//60:02d} min {sec%60:02d} s / {qa['filament_g']:.2f} g PLA**. P11 bei der ersten Schicht kurz auf Haftung beobachten.

[Onshape R15]({v['url']}) · [Bambu-Projekt](../../print/bambu-R15-inboard-straps-2026-11-08/{BASE}.3mf) · [Druckpaket](../../print/bambu-R15-inboard-straps-2026-11-08/{BASE}_Package.zip) · [Übersicht](../../Uebersicht.html)

[Montage](MONTAGE.md) · [Review](parts-review.md) · [Stückliste](BOM_Aenderungen.csv) · [Maße](mechanics/design-specification.json) · [Finale Spezifikation](final-specification.json)

{strap_text(geo)}

Q01 nur federfrei einsetzen und vor Sensor-/Federeinbau entfernen. Clips dienen der Montage; die vorgesehenen Sicherungsschrauben bleiben für Federlast erforderlich. Kein Druckauftrag wurde gestartet.
'''.replace('wieder 132','wieder 132').replace('von135','von 135').replace('übrigen92','übrigen 92').replace('enthältP','enthält P').replace('undQ','und Q').replace('Wände,20','Wände, 20').replace('lokal100','lokal 100').replace('H2D,0','H2D, 0'))
 files=[HERE/n for n in ['README.md','MONTAGE.md','parts-review.md','BOM_Aenderungen.csv','evidence/strap-routing.svg','evidence/strap-routing-provenance.json']]
 write(HERE/'documentation-ready.json',dict(status='PASS_DOCUMENTATION_BOUND_TO_R15_EVIDENCE',source_sha256=sh,onshape_version=v['version_id'],verification=verified,design_specification_sha256=sha(HERE/'mechanics/design-specification.json'),files_sha256={str(p.relative_to(ROOT)):sha(p) for p in files}))
 print('R15 docs prepared; entrypoints still gated on package.')

def publish(data):
 sh,v,layout,verified,native,qa,geo=data;docs=passed(HERE/'documentation-ready.json');delivery=passed(PACK/'delivery-specification.json')
 assert docs['source_sha256']==sh and docs['verification']==verified
 assert delivery['CAD_source_sha256']==sh and delivery['onshape_version']==v['version_id'] and delivery['geometry_changes']==['P01']
 for owner in [docs,delivery]:
  for p,h in owner['files_sha256'].items():assert sha(ROOT/p)==h,p
 spec=read(OLD/'final-specification.json')
 spec.update(revision='Flat132 R15 inboard strap slots and no model brims',date='2026-11-08',status='PASS_NOMINAL_CAD_AND_PLA_PRINT',source_sha256=sh,onshape_version=v['version_id'],onshape_url=v['url'],changed=['P01'],new=[],removed=[],unchanged_exact_native_breps=92,new_prints_required=['P01'],fit_test_pieces=6,plates=1,printed_device_bodies=7,primary_printed_device_bodies=5,primary_unloaded_fixtures=1,omitted_from_primary_print=['P08','P09','H040','H041'],modifier_count=4,local_density_modifiers=layout['local_density_modifiers'],estimates=delivery['estimates'],verification=verified,near_palm=geo,new_nonprinted_parts={},brim_policy='All six model objects: no_brim, width0. Necessary supports retained.')
 spec['gui_preview_limitation']=delivery.get('gui_preview_limitation')
 spec['overview_assets']={'cad_image':'review/inboard-straps-2026-11-08/evidence/P01-final-native.png','cad_image_provenance':'review/inboard-straps-2026-11-08/evidence/P01-final-native-provenance.json','strap_image':'review/inboard-straps-2026-11-08/evidence/strap-routing.svg'}
 files=[HERE/'evidence/P01-final-native.png',HERE/'evidence/P01-final-native-provenance.json',SOURCE,HERE/'native/Flat132_R15_final_AP214.step',HERE/'native/Flat132_R15_neutral_final.zip',PACK/(BASE+'.3mf'),PACK/(BASE+'_Package.zip'),PACK/'delivery-specification.json',HERE/'documentation-ready.json',HERE/'mechanics/design-specification.json']
 spec['files_sha256']={str(p.relative_to(ROOT)):sha(p) for p in files};write(HERE/'final-specification.json',spec)
 (ROOT/'fingerworker_mvp.fs').write_bytes(SOURCE.read_bytes())
 build=read(HERE/'source-build.json') if (HERE/'source-build.json').exists() else dict(source_sha256=sh,changed=['P01'],new=[],removed=[],device_prints=7,fit_pieces=6,native_solids=93,new_prints_required=['P01'])
 assert build['source_sha256']==sh;build.update(status='PASS_NATIVE_REGENERATED_AND_RELEASED',onshape_version=v['version_id'],native_geometry_report_sha256=sha(HERE/'validation/native-geometry.json'));write(HERE/'source-build.json',build)
 review='review/inboard-straps-2026-11-08';pack='print/bambu-R15-inboard-straps-2026-11-08';sec=qa['estimate_seconds']
 block=f'''<!-- CURRENT_FLAT132_R15_START -->
> **08.11.2026 – Flat132 R15: innenliegende Gurtschlitze auf beiden Seiten.** Vier27 ×4-mm-Schlitze in der132-mm-Grundplatte ersetzen die äußeren Laschen. Die griffnahe Handballenauflage, Sensorpfad und Klickfunktionen bleiben erhalten. **Gegenüber R14 nurP01 ersetzen.** Die92 übrigen nativen Körper bleiben exakt unverändert. [CAD/Review]({review}/README.md) · [Montage]({review}/MONTAGE.md) · [Onshape R15]({v['url']}).

> **Sechs Teile auf einer H2D-Platte, alle ohne Brim:** P01/P04/P05/P06/P11 undQ01. Erforderliche Stützen bleiben erhalten. Echte Stangen verwenden; Elektronikgehäuse und gedruckte Stangen entfallen. Zwei25-mm-Gurte mit sicher rückfaltbaren Enden verwenden. PLA,0,4-mm-Standarddüse. Tatsächlicher Slice: **{sec//3600} h {(sec%3600)//60:02d} min / {qa['filament_g']:.2f} g PLA**. [3MF]({pack}/{BASE}.3mf) · [Druckpaket]({pack}/{BASE}_Package.zip) · [Druckanleitung]({pack}/README.md). Q01 nur federfrei; P11-Erstschichthaftung und reale Belastbarkeit prüfen. Die folgenden älteren Revisionsangaben bleiben Historie.
<!-- CURRENT_FLAT132_R15_END -->'''
 for old,new in [('Vier27','Vier 27'),('×4','× 4'),('der132','der 132'),('nurP01','nur P01'),('Die92','Die 92'),('undQ01','und Q01'),('Zwei25','Zwei 25'),('PLA,0','PLA, 0')]:block=block.replace(old,new)
 for name in ['README.md','PRINTING.md','EINKAUFSTEILE.md','DEVICE_UPGRADES.md','print/REVISION_STATUS.md']:
  p=ROOT/name;s=p.read_text();use=block.replace('](review/','](../review/').replace('](print/','](../print/') if name.startswith('print/') else block
  pat=r'<!-- CURRENT_FLAT132_R(?:14|15)_START -->.*?<!-- CURRENT_FLAT132_R(?:14|15)_END -->';assert re.search(pat,s,re.S),name
  s=re.sub(pat,use,s,count=1,flags=re.S).replace('HTML-Projektübersicht R14','HTML-Projektübersicht R15');p.write_text(s)
 print(json.dumps({'status':spec['status'],'revision':'R15','source_sha256':sh,'reports':len(verified),'primary_pieces':6},indent=2))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--prepare-docs',action='store_true');a=ap.parse_args();data=validate();prepare_docs(data) if a.prepare_docs else publish(data)
