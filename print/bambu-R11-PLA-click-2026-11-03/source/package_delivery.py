#!/usr/bin/env python3
"""Package the checked native PLA project; never ship printer Gcode."""
from pathlib import Path
from hashlib import sha256
import csv,json,re,zipfile
OUT=Path(__file__).resolve().parents[1];ROOT=OUT.parents[1]
STUDY=ROOT/'review/flat132-click-assembly-2026-11-03'
R10=ROOT/'review/flat132-integrated-palm-2026-11-03'
def sha(p):return sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
layout=read(OUT/'plate-layout.json');qa=read(OUT/'validation/native-project-check.json')
assert qa['status']=='NATIVE_PROJECT_AND_ALL_THREE_SLICES_PASS'
assert qa['plate_count']==3 and qa['object_count']==13
project=OUT/layout['native_project'];assert sha(project)==qa['native_sha256']
reports=['native-project-check.json','toolpath-check.json','independent-native-review.json',
         'enclosure-toolpath-check.json','p04-surface-check.json','rear-shoe-toolpath-check.json']
for n in reports:
    j=read(OUT/'validation'/n)
    assert j['status'].startswith(('PASS','NATIVE_PROJECT')), (n,j['status'])
    assert j.get('failed_checks',j.get('failed_count',0))==0,n
native=read(STUDY/'validation/native-geometry.json');assert native['status']=='PASS_EXACT_NATIVE_R11'
assert native['source_sha256']==layout['CAD_source_sha256']==qa['CAD_source_sha256']

for n in ['MONTAGE.md','ASSEMBLY_JOINT_REVIEW.md','BOM_Aenderungen.csv']:
    content=(STUDY/n).read_text()
    content=content.replace('../flat132-integrated-palm-2026-11-03/MONTAGE.md','MONTAGE_R10_SERVICE.md')
    (OUT/n).write_text(content)
old=(R10/'MONTAGE.md').read_text()
old=re.sub(r'\]\(../../print/bambu-R10-integrated-palm-2026-11-03/[^)]+\)','](README.md)',old)
(OUT/'MONTAGE_R10_SERVICE.md').write_text('> Historische R10-Serviceanleitung. Für R11-Teile und Klickgehäuse gilt vorrangig [MONTAGE.md](MONTAGE.md). Die Sensor-, Vorspann- und Werkzeugwege bleiben gültig.\n\n'+old)
(OUT/'source-mm/README.md').write_text('Roh-STLs in nativen CAD-Millimeterkoordinaten. Für den Druck das 3MF-Projekt oder STL-print-oriented verwenden. H040/H041 sind unbelastete Formhilfen, Q01 eine federfreie Passhilfe.\n')
(OUT/'source/README.md').write_text('Quelltext und Autorenskripte als Nachweis. Der native 3MF-Drucksatz ist eigenständig. Die Skripte benötigen das ursprüngliche Fingerworker-Repository und die dokumentierte lokale Bambu-Laufzeit.\n')
parts=[]
for row in layout['placements']:
    f=OUT/'STL-print-oriented'/(row['ref']+'.stl');assert f.is_file()
    parts.append(dict(ref=row['ref'],file=f.name,sha256=sha(f),plate=row['plate'],units='mm',scale=1.0,intent=row['intent']))
(OUT/'STL-print-oriented/manifest.json').write_text(json.dumps(dict(objects=13,identity='Rigidly rotated/translated native meshes or unchanged explicitly named unloaded fixtures; no repair or rescale.',parts=parts),indent=2)+'\n')
with (OUT/'Druckliste.csv').open('w',newline='') as f:
    w=csv.writer(f);w.writerow(['Ref','Menge','Platte','Material','Hinweis','STL'])
    for r in layout['placements']:w.writerow([r['ref'],1,r['plate'],'PLA',r['intent'],r['ref']+'.stl'])
def duration(seconds):
    h,r=divmod(seconds,3600);m,s=divmod(r,60);return f'{h} h {m:02d} min {s:02d} s'
table='\n'.join(f'| {e["plate"]} | {e["objects"]} | {duration(e["seconds"])} | {e["grams"]:.2f} g |' for e in qa['estimates'])
notes=f'''# R11 – finale Druckprüfung

**Bestanden:** 13 Modelle, drei vollständig geslicte Platten; H2D, Standarddüsen 0,4 mm, PLA, strukturierte PEI-Platte, 100 %.

| Platte | Stücke | Slicerzeit | PLA einschließlich Stützen/Brim |
|---|---:|---:|---:|
{table}

Komplett: **{duration(qa['estimated_seconds'])} / {qa['estimated_grams']:.2f} g**. Der Rahmen ist zu R10 geometrisch identisch und muss nicht erneut gedruckt werden. Mit vorhandenem Rahmen entfallen Platte 1 und 131,35 g. Auf Platte 2 sind P08/P09/P120/P121 neu; die sieben übrigen Stücke können ebenfalls aus dem vorhandenen Passsatz übernommen werden.

Native STEP-Prüfung: vier geänderte Körper stimmen exakt mit unabhängiger CSG überein, 113 übrige BReps unverändert. P01 und P04 sind darunter. Alle 117 nativen Körper sind gültige Volumina. Vier kleine P07 und die separate P10 verschwinden durch Integration.

Das native Bambu-Projekt wurde unabhängig gegen alle 13 Quellmeshes geprüft: richtige Platten 1/11/1, Maßstab 1:1, starre Transformationen, geschlossene Volumina, höchstens 0,0001 mm Vertexabweichung, keine automatischen Meshreparaturen. Originale H2D-Maschinenmakros bleiben unverändert. 101 allgemeine Werkzeugwegprüfungen bestätigen Druckbereich, getrennte Bahnhüllen, erste Schicht, volle Höhe und begrenzte Beschleunigung.

P04 hat auf Platte 3 acht gesondert geprüfte Kontakt-/Führungsregionen ohne Support-, Interface- oder Transitionpfade. Die Fingerzugwand wird als Topfläche und der Muldenboden als Außenwand gedruckt. Die gegenüberliegende Muldenwand bleibt gestützt. Nur die geprüften Bett-Baumstützen übernehmen.

Beide Gehäuseteile haben vollständige Haken und durchgehende Rastarme; Spalte sind frei. P09 hat keine Bridge-Pfade oder Clipstützen. P08 benötigt am USB-Dach und an den außen zugänglichen Endhaken Stützen; der längste Bridge-Pfad beträgt 1,675 mm. Die nominalen Steck-/Entriegelwege wurden zusätzlich an der CAD-Geometrie geprüft.

Beide P12-Schuhe haben die T-förmige Bettanlage, keine Bridge-Pfade und keine Stützen im M2-Fangschlitz. Die Gabel enthält zugängliche Stützen: **vor dem Einbau vollständig axial aus der offenen Gabel entfernen**. Der durchgehende native R4,9-Entnahmezylinder ist materialfrei. Reale Stützentfernung und Passung bestätigt der Druck.

Offizielle Bambu Studio 02.08.02.61; Import und vollständiger Schnitt beenden mit Code 0. Bekannte T1001/T65535/T65279-Parsermeldungen aus den unveränderten Stock-Makros bleiben diagnostisch. Es wurde kein Druckauftrag übertragen; die Lieferdatei enthält keine Gcodes.

Quellhash: `{layout['CAD_source_sha256']}`. Onshape-Version: `{layout['native_R11_version']}`. Die Berichte im Ordner validation binden Projekt und internen Slice. Das interne Gcode-Artefakt wird nicht mitgeliefert.

Diese Prüfung betrifft nominale Geometrie und berechnete Werkzeugwege. Rastkraft, PLA-Streuung, wiederholtes Entriegeln, Kriechen, tatsächliche Oberfläche und Festigkeit sind am unbelasteten Muster zu prüfen. Sie erteilt keine Lastfreigabe für gedruckte Stangen/Q01 oder den Funktionsaufbau.
'''
(OUT/'PRINT_QA_NOTES.md').write_text(notes)
version='https://cad.onshape.com/documents/15316cc6370631845af136b2/v/'+layout['native_R11_version']+'/e/d253eb87b70818ebde8215f0'
readme=(OUT/'README.md').read_text().split('<!-- FINAL_QA -->')[0].rstrip()
readme+=f'\n\n<!-- FINAL_QA -->\nVollständig geprüft: **{duration(qa["estimated_seconds"])} / {qa["estimated_grams"]:.0f} g PLA** für alle drei Platten. [Onshape R11]({version}).\n'
(OUT/'README.md').write_text(readme)

files=[project]+[p for p in OUT.iterdir() if p.is_file() and p.suffix in ('.md','.csv','.json') and p.name not in ('SHA256.json',)]
for folder in ('profiles','STL-print-oriented','source-mm','source','preview','CAD'):
    files.extend(p for p in (OUT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc')
files.extend(OUT/'validation'/n for n in reports)
files=sorted(set(files))
assert sum(p.suffix=='.3mf' for p in files)==1
assert not any(p.name.endswith(('.gcode','.gcode.3mf')) for p in files)
for p in [p for p in files if p.suffix=='.md']:
    for target in re.findall(r'\]\(([^)]+)\)',p.read_text()):
        if '://' in target or target.startswith('#'):continue
        assert (p.parent/target.split('#')[0]).exists(),(p,target)
manifest={str(p.relative_to(OUT)):sha(p) for p in files}
(OUT/'SHA256.json').write_text(json.dumps(dict(status='DELIVERY_HASH_MANIFEST',files=manifest),indent=2)+'\n');files.append(OUT/'SHA256.json')
target=OUT/'Fingerworker_R11_H2D_04mm_PLA_Fit_Test_Package.zip'
with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
    for p in files:z.write(p,p.relative_to(OUT))
with zipfile.ZipFile(target) as z:
    assert z.testzip() is None
    for n,h in manifest.items():assert sha256(z.read(n)).hexdigest()==h
    assert sum(n.startswith('STL-print-oriented/') and n.endswith('.stl') for n in z.namelist())==13
    assert sum(n.endswith('.3mf') for n in z.namelist())==1
print(json.dumps(dict(status='R11_DELIVERY_PASS',zip=target.name,sha256=sha(target),bytes=target.stat().st_size,files=len(files),print_objects=13,plates=3),indent=2))
