#!/usr/bin/env python3
"""Package final checked R12 native PLA files, excluding printer G-code.

Run only after the final fixed-front native export, the replacement Q01
fixture, all three slices and all validation reports are complete.
"""
from pathlib import Path
from hashlib import sha256
import argparse,csv,json,re,shutil,zipfile

OUT=Path(__file__).resolve().parents[1];ROOT=OUT.parents[1]
STUDY=ROOT/'review/simplification-2026-11-03'
BASE='Fingerworker_R12_H2D_04mm_PLA_Fit_Test'
DEVICE={'P01','P04','P05','P06','P08','P09','P11'}
FIXTURES={'H040','H041','Q01'}
sha=lambda p:sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text())

def duration(seconds):
    h,r=divmod(int(seconds),3600);m,s=divmod(r,60);return f'{h} h {m:02d} min {s:02d} s'

def passed(path):
    data=read(path)
    assert str(data.get('status','')).startswith(('PASS','NATIVE_PROJECT')), (path,data.get('status'))
    assert data.get('failed_checks',data.get('failed_count',0))==0,path
    assert not data.get('failures') and not data.get('failed'),path
    return data

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--fixture-manifest',type=Path,default=STUDY/'fixture/manifest.json')
    parser.add_argument('--fixture-qa',type=Path,default=STUDY/'fixture/validation.json')
    args=parser.parse_args()
    layout=read(OUT/'plate-layout.json');qa=passed(OUT/'validation/native-project-check.json')
    assert qa['status']=='NATIVE_PROJECT_AND_ALL_THREE_SLICES_PASS'
    assert qa['plate_count']==3 and qa['object_count']==10
    rows=layout['placements'];refs={r['ref'] for r in rows}
    assert len(rows)==10 and refs==DEVICE|FIXTURES
    assert [sum(r['plate']==n for r in rows) for n in (1,2,3)]==[1,8,1]
    project=OUT/layout['native_project'];assert project.name==BASE+'.3mf' and sha(project)==qa['native_sha256']
    sliced=OUT/'validation'/(BASE+'_verification.gcode.3mf')
    assert sha(sliced)==qa['sliced_internal_evidence_sha256']
    cad=STUDY/'fingerworker_R12_simplified.fs';cad_hash=sha(cad)
    assert cad_hash==layout['CAD_source_sha256']==qa['CAD_source_sha256']
    text=cad.read_text()
    assert '"H13 M6x1 flat-tip adjuster' not in text, 'Superseded adjustable front source'
    native=passed(STUDY/'validation/native-geometry.json')
    assert native['status']=='PASS_EXACT_NATIVE_R12' and native['source_sha256']==cad_hash
    inventory=read(STUDY/'validation/native-step-inventory.json')
    native_refs=set(inventory['native_part_correspondence'])
    assert {r for r in native_refs if r.startswith('P') and not r.startswith('PCB_')}==DEVICE
    assert not native_refs&{'H11','H13','H15','H160','H161','H170','H171','H21','H22'}
    service=passed(STUDY/'validation/service-native.json');assert service['source_sha256']==cad_hash
    assert service['native_archive_sha256']==native['native_zip_sha256']
    motion=passed(STUDY/'validation/native-motion.json')
    assert motion['source_sha256']==cad_hash and motion['native_step_sha256']==native['native_step_sha256']
    assert motion['native_stl_archive_sha256']==native['native_zip_sha256']
    assert service['initial_contact_certificate_sha256']==sha(STUDY/'validation/native-motion.json')

    reports=['native-project-check.json','toolpath-check.json','print-feature-check.json','p04-surface-check.json']
    for name in reports:
        report=passed(OUT/'validation'/name)
        for key in ('CAD_source_sha256','source_sha256'):
            if key in report:assert report[key]==cad_hash,(name,key)
        for key in ('native_sha256','native_editable_project_sha256','editable_project_sha256'):
            if key in report:assert report[key]==qa['native_sha256'],(name,key)
        for key in ('native_sliced_archive_sha256','sliced_archive_sha256','sliced_internal_evidence_sha256'):
            if key in report:assert report[key]==qa['sliced_internal_evidence_sha256'],(name,key)
        if 'native_step_sha256' in report:assert report['native_step_sha256']==native['native_step_sha256'],name
        if 'layout_sha256' in report:assert report['layout_sha256']==sha(OUT/'plate-layout.json'),name
        if name=='p04-surface-check.json':
            p04row=next(r for r in rows if r['ref']=='P04')
            with zipfile.ZipFile(sliced) as archive:
                gcode=archive.read(f'Metadata/plate_{p04row["plate"]}.gcode').decode().replace('\r\n','\n')
            assert sha256(gcode.encode()).hexdigest()==report['gcode_sha256'],'P04 report must bind the final plate G-code'
            for field in ('rotation_3x3','normalization_translation_mm','plate_xy_mm'):
                assert report[field]==p04row[field],('P04 report transform mismatch',field)
    # Current Q01 must be a replacement for the removed H11-pocket fixture.
    # Its manifest contract is supplied by the independent fixture builder.
    fixture=read(args.fixture_manifest);fixture_qa=passed(args.fixture_qa)
    qrow=next(r for r in rows if r['ref']=='Q01');qsource=ROOT/qrow['source_path']
    assert qsource.is_relative_to(STUDY), 'Historical Q01 is incompatible with filled H11 pocket'
    assert sha(qsource)==qrow['source_sha256']
    fixture_hashes=set()
    def collect_hashes(value):
        if isinstance(value,dict):
            for k,v in value.items():
                if 'sha256' in k.lower() and isinstance(v,str):fixture_hashes.add(v)
                collect_hashes(v)
        elif isinstance(value,list):
            for v in value:collect_hashes(v)
    collect_hashes(fixture);collect_hashes(fixture_qa)
    assert qrow['source_sha256'] in fixture_hashes, 'Q01 source must be hash-bound by its current manifest/report'
    assert fixture_qa['status']=='PASS_Q01_NATIVE_FIT', 'Q01 must be checked against the final native frame'
    assert fixture_qa['native_P01_solid_index']==inventory['native_part_correspondence']['P01']['candidates'][0]['solid_index']
    assert fixture_qa['native_assembly_step_sha256']==native['native_step_sha256'], 'Q01 QA is not bound to this native assembly'
    for relative_path,expected in fixture_qa['files_sha256'].items():
        assert sha(ROOT/relative_path)==expected,('Stale Q01 validation input',relative_path)
    assert sha(args.fixture_manifest)==qrow['fixture_manifest_sha256']

    for name in ('MONTAGE.md','BOM_Aenderungen.csv'):
        shutil.copyfile(STUDY/name,OUT/name)
    montage=(OUT/'MONTAGE.md').read_text()
    for obsolete in ('zentrale H13-Sensorvorspannung bleibt bestehen','zentrale Vorspannung auf null','0 ≤ p ≤ 2'):
        assert obsolete not in montage, ('Obsolete central adjustment instruction',obsolete)
    (OUT/'source-mm').mkdir(exist_ok=True);(OUT/'source').mkdir(exist_ok=True)
    (OUT/'source-mm/README.md').write_text('Native Geräte-STLs und die gesondert geprüften Passhilfen in Millimetern. Für den Druck das 3MF-Projekt oder STL-print-oriented verwenden. H040/H041 und Q01 sind ausschließlich unbelastete Form-/Montagehilfen. Die neue Q01 gehört zum festen R12-Sensordatum; ältere Q01 nicht verwenden.\n')
    (OUT/'source/README.md').write_text('Quelltext und Autorenskripte als Nachweis. Das native 3MF-Projekt ist eigenständig; Skripte benötigen das Fingerworker-Repository und die dokumentierte lokale Bambu-Laufzeit. Die verworfene integrierte Elektronikdecke gehört nicht zu dieser Lieferung.\n')
    shutil.copyfile(cad,OUT/'source/fingerworker_R12_simplified.fs')
    (OUT/'fixture').mkdir(exist_ok=True)
    shutil.copyfile(args.fixture_manifest,OUT/'fixture/manifest.json')
    shutil.copyfile(args.fixture_qa,OUT/'validation/fixture-q01-check.json')
    reports.append('fixture-q01-check.json')
    for name in ('README.md','ASSEMBLY.txt'):
        source=args.fixture_manifest.parent/name
        if source.is_file():shutil.copyfile(source,OUT/'fixture'/name)
    for name in ('native-geometry.json','native-motion.json','service-native.json'):
        shutil.copyfile(STUDY/'validation'/name,OUT/'validation'/name);reports.append(name)

    parts=[]
    for row in rows:
        p=OUT/'STL-print-oriented'/(row['ref']+'.stl');assert p.is_file()
        parts.append(dict(ref=row['ref'],file=p.name,sha256=sha(p),plate=row['plate'],units='mm',scale=1.0,
            category='device' if row['ref'] in DEVICE else 'unloaded_fixture',intent=row['intent']))
    (OUT/'STL-print-oriented/manifest.json').write_text(json.dumps(dict(objects=10,device_parts=7,unloaded_fixtures=3,
        identity='Rigid rotations/translations of exact native meshes or separately validated unloaded fixtures; no repair or rescale.',parts=parts),indent=2)+'\n')
    with (OUT/'Druckliste.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['Ref','Menge','Platte','Material','Kategorie','Hinweis','STL'])
        for row in rows:w.writerow([row['ref'],1,row['plate'],'PLA','Geräteteil' if row['ref'] in DEVICE else 'Unbelastete Passhilfe',row['intent'],row['ref']+'.stl'])
    table='\n'.join(f'| {r["plate"]} | {r["objects"]} | {duration(r["seconds"])} | {r["grams"]:.2f} g |' for r in qa['estimates'])
    version=layout['native_R12_version'];assert re.fullmatch(r'[0-9a-f]{24}',version),'Final Onshape version required'
    version_url='https://cad.onshape.com/documents/15316cc6370631845af136b2/v/'+version+'/e/d253eb87b70818ebde8215f0'
    notes=f'''# R12 – finale Druckprüfung

**Bestanden:** sieben Geräteteile plus drei unbelastete Passhilfen, insgesamt zehn Modelle auf drei vollständig geslicten Platten. H2D, Standarddüsen 0,4 mm, PLA, strukturierte PEI-Platte, Maßstab 100 %.

| Platte | Stücke | Slicerzeit | PLA einschließlich Stützen/Brim |
|---|---:|---:|---:|
{table}

Komplett: **{duration(qa['estimated_seconds'])} / {qa['estimated_grams']:.2f} g**.

P01 hat eine feste, vom Boden aufsteigende Sensorabstützung und die Gegenhalter der neuen Traverse. P06 ersetzt vier bisherige hintere Druckteile durch ein großes Teil mit langen PLA-Rastarmen. Sowohl hintere Verstellung als auch zentraler H13-Vorspannmechanismus sind entfernt. Dies bedeutet keine unbelasteten Federn: Die nominale Feder-Einbaulänge in Ruhe bleibt 96 mm. Gegenüber den freien Längen 102/105 mm sind die bisherigen Federn bereits 6/9 mm geometrisch komprimiert. Der feste Nutzweg beträgt 30 mm; mit 81-mm-Isometriehülsen beträgt der Anfahrweg15 mm.

Neu benötigt werden P01, P06 und die zum festen Sensordatum passende Q01-Passhilfe. Alte Q01 verwendet die entfernte Muttertasche und passt nicht. Ein vorhandenes R11-P08 bleibt kompatibel; die neue Version füllt lediglich zwei unbenutzte Pilotlöcher. P04, P05, P09, P11 und die beiden Stangen-Formhilfen bleiben wiederverwendbar. Alte P060/P061/P120/P121 und entfernte Verstellhardware gehören nicht in den R12-Aufbau.

Der finale native STEP enthält {len(native_refs)} eindeutig zugeordnete Körper. Die geänderten Körper sind gegen unabhängige CSG geprüft; beibehaltene Körper werden separat auf Geometrieidentität geprüft. Die native Bambu-Datei stimmt mit allen zehn Quellmeshes überein: Plattenverteilung 1/8/1, Maßstab 1:1, starre Transformationen, geschlossene Volumina und keine automatische Meshreparatur. Messungen, Quellen und konkrete Prüfzahlen stehen in den mitgelieferten JSON-Berichten.

Die Werkzeugwegprüfung umfasst P06-Rastarme, freie Biegespalte, offene Stangenbohrungen und deren selbsttragende Dachform, P01-Gegenhalter sowie die feste Sensorauflage. Die Sensor-Kontaktfläche und die 45°-Schultern benötigen keine Stützen; die frühere obere Reaktionsbrücke ist entfernt. Die Traverse wird ohne Stützen gedruckt. Zugängliche Stützen an P01 vollständig entfernen, bevor die Clips montiert werden.

P08/P09 behalten die bewährten langen Klickarme. P09 bleibt separat und ohne Stützen; die Integration seiner PCB-Haltefläche in P01 wurde wegen zusätzlicher Stützspuren verworfen. P08 benötigt am USB-Dach und an den außen zugänglichen Endhaken Stützen. P04 bleibt auf Platte 3 in der geprüften Stirnseitenlage: Die Fingerkontakt-/Führungsregionen sind ohne Support-, Interface- oder Transitionpfade. Die gegenüberliegende Muldenwand bleibt gestützt.

Q01 und die gedruckten Stangen dienen nur der federfreien Passprobe. Für den Funktionsaufbau bleiben Sensor, Stahlstangen, Federsitze und geeignete Sicherungsschrauben vorgesehen. Die vier M3-Traversenschrauben bleiben zur Sicherung verfügbar; PLA-Clips allein sind keine Federlastfreigabe.

Offizielle Bambu Studio 02.08.02.61; Import und vollständiger Slice mit Code 0. Originale H2D-Maschinenmakros bleiben erhalten. Kein Druckauftrag wurde übertragen. Dieses Paket enthält ein editierbares 3MF-Projekt und keine Drucker-Gcodes.

Quellhash: `{cad_hash}`. [Onshape R12]({version_url}). Die Berichte in validation binden Projekt, native CAD-Geometrie, Fixture und internen Slice.

Die Prüfungen betreffen nominale Geometrie und berechnete Werkzeugwege. Reale Rastkraft, Passung, Stützentfernung, Oberflächen, Kriechen und Belastbarkeit bleiben am Ausdruck zu prüfen. Eine 500-N- oder Lebensdauerfreigabe ist damit nicht verbunden.
'''
    (OUT/'PRINT_QA_NOTES.md').write_text(notes)
    readme=f'''# Fingerworker R12 – PLA, feste Geometrie und Klickmontage

`{project.name}` in Bambu Studio als **Projekt** öffnen. Drucker: Bambu H2D, 0,4-mm-Standarddüsen, PLA. Maßstab 100 %. Die vorbereitete Ausrichtung und Stützen übernehmen und vor dem Druck die tatsächliche Filament-/Druckerzuordnung prüfen.

Der Satz enthält **7 Geräteteile und 3 unbelastete Passhilfen auf 3 Platten**; keine gedruckten Schrauben oder Muttern. Alle Vorspannverstellungen sind entfernt, die vorhandene geometrische Federkompression bleibt erhalten.

- Platte 1: P01 mit fester Sensorabstützung und hinteren Gegenhaltern.
- Platte 2: P05, P06, P08, P09, P11, H040/H041 und die neue Q01.
- Platte 3: P04 mit sauberer Fingerkontaktfläche.

**P01, P06 und Q01 neu drucken.** Ein R11-P08 bleibt verwendbar. Die übrigen unveränderten Teile können übernommen werden; alte hintere Kappen/Schuhe und alte Q01 nicht zusätzlich montieren.

[Montage und Service](MONTAGE.md) · [Druckliste](Druckliste.csv) · [Änderungen an Teilen/Hardware](BOM_Aenderungen.csv) · [Druckprüfung](PRINT_QA_NOTES.md) · [Onshape R12]({version_url})

Vollständig gesliced: **{duration(qa['estimated_seconds'])} / {qa['estimated_grams']:.0f} g PLA** einschließlich Stützen und Brims. Die Passhilfen sind ausschließlich für federfreie Montage; vor dem Funktionsaufbau entfernen. Ein Druckauftrag wurde nicht gesendet.
'''
    (OUT/'README.md').write_text(readme)

    root_names=['README.md','MONTAGE.md','BOM_Aenderungen.csv','PRINT_QA_NOTES.md','Druckliste.csv','Druckliste.json','plate-layout.json']
    files=[project]+[OUT/name for name in root_names]
    for folder in ('profiles','STL-print-oriented','source-mm','source','preview','fixture'):
        files.extend(p for p in (OUT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc')
    files.extend(OUT/'validation'/name for name in reports)
    files=sorted(set(files));assert all(p.is_file() for p in files)
    assert sum(p.suffix=='.3mf' for p in files)==1
    assert not any(p.name.endswith(('.gcode','.gcode.3mf')) for p in files)
    assert not any('H15_R10' in p.name or 'MONTAGE_R10' in p.name for p in files)
    for p in [p for p in files if p.suffix=='.md']:
        for link in re.findall(r'\]\(([^)]+)\)',p.read_text()):
            if '://' in link or link.startswith('#'):continue
            dest=(p.parent/link.split('#')[0]).resolve()
            assert dest.is_relative_to(OUT) and dest.exists(),(p,link)
    manifest={str(p.relative_to(OUT)):sha(p) for p in files}
    (OUT/'SHA256.json').write_text(json.dumps(dict(status='DELIVERY_HASH_MANIFEST',revision='R12',device_parts=7,unloaded_fixtures=3,files=manifest),indent=2)+'\n')
    files.append(OUT/'SHA256.json');target=OUT/(BASE+'_Package.zip')
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
        for p in files:z.write(p,p.relative_to(OUT))
    with zipfile.ZipFile(target) as z:
        assert z.testzip() is None
        for name,h in manifest.items():assert sha256(z.read(name)).hexdigest()==h
        assert sum(n.startswith('STL-print-oriented/') and n.endswith('.stl') for n in z.namelist())==10
        assert sum(n.endswith('.3mf') for n in z.namelist())==1
    print(json.dumps(dict(status='R12_DELIVERY_PASS',zip=target.name,sha256=sha(target),bytes=target.stat().st_size,
        files=len(files),print_objects=10,device_parts=7,unloaded_fixtures=3,plates=3),indent=2))

if __name__=='__main__':main()
