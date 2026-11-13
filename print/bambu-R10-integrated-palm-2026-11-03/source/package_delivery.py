"""Ship one editable native 3MF, 18 STLs, provenance and instructions, no Gcode."""
from pathlib import Path
from hashlib import sha256
import json,zipfile,csv
OUT=Path(__file__).resolve().parents[1];ROOT=OUT.parents[1]
def sha(p):return sha256(p.read_bytes()).hexdigest()
layout=json.loads((OUT/'plate-layout.json').read_text());qa=json.loads((OUT/'validation/native-project-check.json').read_text());paths=json.loads((OUT/'validation/toolpath-check.json').read_text())
assert qa['status']=='NATIVE_PROJECT_AND_BOTH_SLICES_PASS' and paths['failed_checks']==0
assert layout['native_R10_version'] and not layout['native_R10_version'].startswith('PENDING')
assert qa['CAD_source_sha256']==paths['CAD_source_sha256']==layout['CAD_source_sha256']
project=OUT/layout['native_project'];assert sha(project)==qa['native_sha256']==paths['editable_project_sha256']
independent=json.loads((OUT/'validation/independent-print-qa.json').read_text())
assert independent['status']=='PASS'
assert independent['native_project_sha256']==sha(project)
assert independent.get('source_cad_sha256',independent.get('source_sha256'))==layout['CAD_source_sha256']
assert independent.get('source_P01_sha256',independent.get('native_P01_source_sha256'))==layout['placements'][0]['source_sha256']
assert independent['slice_archive_sha256']==qa['sliced_internal_evidence_sha256']
study=ROOT/'review/flat132-integrated-palm-2026-11-03'
mount=(study/'MONTAGE.md').read_text()
mount=mount.replace('../../print/bambu-R10-integrated-palm-2026-11-03/README.md','README.md').replace('../../print/bambu-R10-integrated-palm-2026-11-03/FIT_TEST_README.md','FIT_TEST_README.md')
(OUT/'MONTAGE.md').write_text(mount)
(OUT/'BOM_Aenderungen.csv').write_bytes((study/'BOM_Aenderungen.csv').read_bytes())
for name in ('H15_R10.step','H15.step'):
    step=study/'mechanical-mm'/name
    if step.exists():
        (OUT/'CAD').mkdir(exist_ok=True);(OUT/'CAD/H15_R10.step').write_bytes(step.read_bytes())
        (OUT/'CAD/README.md').write_text('# H15 – spätere Metallfertigung\n\nH15_R10.step ist die revidierte Stahl-Keeperplatte mit zwei glatten Ø3,4-mm-Durchgängen. Die alten Senkungen entfallen. Das STEP gehört nicht zum 18-teiligen Drucksatz und wird für die unbelastete Q01-Passprobe nicht benötigt. Montage und Service stehen in [MONTAGE.md](../MONTAGE.md).\n')
        break
stls=json.loads((OUT/'STL-print-oriented/manifest.json').read_text());assert stls['objects']==18
rows=layout['placements']
with (OUT/'Druckliste.csv').open('w',newline='') as f:
    w=csv.writer(f);w.writerow(['Ref','Menge','Platte','Material','Hinweis','STL'])
    for r in rows:w.writerow([r['ref'],1,r['plate'],'PLA',r['intent'],next(p['file'] for p in stls['parts'] if p['ref']==r['ref'])])
def duration(seconds):
    hours,minutes=divmod(round(seconds/60),60)
    return f'{hours} h {minutes:02d} min'
overall_time=duration(qa['estimated_seconds']);p1=qa['estimates'][0]
orientation=json.loads((OUT/'validation/orientation-comparison.json').read_text())
flat,wrist=orientation['flat'],orientation['wrist']
assert flat['source_sha256']==rows[0]['source_sha256']
notes=f'''# R10 – Druckprüfung

**Bestanden:** 18 native Meshes, zwei vollständig geslicte Platten. H2D · 0,4 mm · PLA · strukturierte PEI-Platte · 100 %.

Slicer-Schätzung einschließlich Stützen und Brims: **{overall_time} / {qa['estimated_grams']:.0f} g PLA**. Nur das neue P01 auf Platte 1: **{duration(p1['seconds'])} / {p1['grams']:.0f} g PLA**. Vorhandene R9-Restteile können weiterverwendet werden.

P01 bleibt bodenflach; die Stützen unter dem äußeren Handballenüberhang sind über die Handgelenkseite/Unterseite erreichbar. Die zentrale Serviceausnehmung bleibt von unten offen. Ein erfolgreicher Vergleichsslice mit Handgelenkseite unten benötigt {duration(wrist['estimated_seconds'])} / {wrist['estimated_total_grams']:.0f} g und erzeugt {wrist['print_size_mm'][2]:.0f} mm Bauhöhe bei nur {wrist['exact_planar_bed_contact_area_mm2']:.0f} mm² ebener Bettauflage. Die ausgelieferte flache Lage benötigt {duration(flat['estimated_seconds'])} / {flat['estimated_total_grams']:.0f} g, bleibt {flat['print_size_mm'][2]:.0f} mm hoch und hat rund {flat['exact_planar_bed_contact_area_mm2']:.0f} mm² ebene Bettauflage. Der alternative Kandidat wird nicht mitgeliefert.

Die restlichen 17 Stücke übernehmen die unveränderten R9-Quellmeshes, Drucklagen und individuellen Einstellungen. Alle Objekte besitzen tatsächliche Extrusionsbahnen ab der ersten Schicht und erreichen ihre Höhe; die vier P07-Dummies enden bei exakt 1,50 mm.

Die 3MF-Rückprüfung bestätigt Maßstab 1:1, geschlossene Volumen, starre Transformationen, maximal 0,0001 mm Vertexabweichung und keine automatischen Meshreparaturen. Tatsächliche Modell-/Stütz-/Brimbahnen bleiben im gemeinsam nutzbaren H2D-Bettbereich; die Bahnhüllen der Teile auf Platte 2 überschneiden sich nicht. Lokalisiertes Stützmaterial wurde unter Palm, USB-Dach, Fingerraum, Joch und hinteren Schuhverbindern geprüft; die geschlossenen hinteren Zungenführungen enthalten keine eingeschlossenen Stützen.

Offizielle Bambu Studio 02.08.02.61, originale H2D-Maschinenmakros unverändert. Die bekannten lokalen Parserdiagnosen T1001/T65535/T65279 aus diesen Makros verhindern die beiden erfolgreichen Slices nicht. Es wurde kein Druckauftrag übertragen. Das Lieferprojekt enthält keine Gcode-Datei.

CAD-Quellhash: `{layout['CAD_source_sha256']}`. Native Onshape-Version: `{layout['native_R10_version']}`. Die einzelnen Prüfberichte binden Quellhash, Projekt und internes Slice-Artefakt.

Die Prüfung bewertet Geometrie und Werkzeugwege. Die reale Entfernung der Stützen, Passung und Festigkeit sind am unbelasteten Druckteil zu bestätigen. Infill ist keine Festigkeitsfreigabe; Q01, die gedruckten Stangen und harten Pads ersetzen die belasteten Funktionsteile nicht.
'''
(OUT/'PRINT_QA_NOTES.md').write_text(notes)
files=[project,OUT/'README.md',OUT/'FIT_TEST_README.md',OUT/'MONTAGE.md',OUT/'BOM_Aenderungen.csv',OUT/'PRINT_QA_NOTES.md',OUT/'Druckliste.json',OUT/'Druckliste.csv',OUT/'plate-layout.json']
for folder in ('profiles','STL-print-oriented','source-mm','fixture','source','preview','CAD'):
    files.extend(p for p in (OUT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts and not p.name.endswith('.pyc'))
files.extend(OUT/'validation'/name for name in ('native-project-check.json','toolpath-check.json','independent-print-qa.json','orientation-comparison.json') if (OUT/'validation'/name).exists())
assert all(not p.name.endswith(('.gcode','.gcode.3mf')) for p in files)
assert sum(p.suffix=='.3mf' for p in files)==1
manifest={str(p.relative_to(OUT)):sha(p) for p in sorted(files)}
(OUT/'SHA256.json').write_text(json.dumps(dict(status='DELIVERY_HASH_MANIFEST',files=manifest),indent=2)+'\n');files.append(OUT/'SHA256.json')
target=OUT/'Fingerworker_R10_H2D_04mm_PLA_Fit_Test_Package.zip'
with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
    for p in sorted(files):z.write(p,p.relative_to(OUT))
with zipfile.ZipFile(target) as z:
    assert z.testzip() is None
    for name,h in manifest.items():assert sha256(z.read(name)).hexdigest()==h
    assert len([n for n in z.namelist() if n.startswith('STL-print-oriented/') and n.endswith('.stl')])==18
    assert not any(n.endswith('.gcode') for n in z.namelist())
print(json.dumps(dict(status='R10_DELIVERY_ZIP_PASS',path=str(target),bytes=target.stat().st_size,sha256=sha(target),files=len(files),native_projects=1,print_oriented_stls=18),indent=2))
