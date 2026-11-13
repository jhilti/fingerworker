#!/usr/bin/env python3
"""Package the validated one-plate option without changing frozen R13 CAD."""
from pathlib import Path
from hashlib import sha256
import csv,json,re,shutil,zipfile

OUT=Path(__file__).resolve().parents[1];ROOT=OUT.parents[1]
STUDY=ROOT/'review/palm-simplification-2026-11-03'
FROZEN=ROOT/'print/bambu-R13-simple-palm-2026-11-03'
BASE='Fingerworker_R13_H2D_04mm_PLA_One_Plate'
DEVICE={'P01','P04','P05','P06','P08','P09','P11'}
FIXTURES={'H040','H041','Q01'}
sha=lambda p:sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text())

def passed(path):
    d=read(path);assert str(d.get('status','')).startswith(('PASS','NATIVE_PROJECT')),(path,d.get('status'))
    assert not d.get('failures') and not d.get('failed') and not d.get('issues'),path
    assert d.get('failed_checks',d.get('failed_count',0))==0,path
    return d

def duration(seconds):
    h,r=divmod(int(seconds),3600);m,s=divmod(r,60)
    return f'{h} h {m:02d} min {s:02d} s'

def main():
    frozen=passed(STUDY/'final-specification.json')
    for name,h in frozen['files_sha256'].items():assert sha(ROOT/name)==h,name
    layout=read(OUT/'plate-layout.json');rows=layout['placements']
    assert len(rows)==10 and {r['ref'] for r in rows}==DEVICE|FIXTURES
    assert {r['plate'] for r in rows}=={1} and layout['object_count']==10
    assert layout['CAD_source_sha256']==frozen['source_sha256']
    assert layout['native_R13_version']==frozen['onshape_version']
    qa=passed(OUT/'validation/native-project-check.json')
    assert qa['status']=='NATIVE_PROJECT_AND_SINGLE_PLATE_SLICE_PASS'
    assert qa['plate_count']==1 and qa['object_count']==10
    assert qa['orientations_and_object_settings_unchanged'] and not qa['stock_macros_modified']
    project=OUT/layout['native_project'];assert project.name==BASE+'.3mf'
    assert sha(project)==qa['native_sha256']
    assert qa['CAD_source_sha256']==frozen['source_sha256']
    sliced=OUT/'validation'/(BASE+'_verification.gcode.3mf')
    assert sha(sliced)==qa['sliced_internal_evidence_sha256']
    estimates=qa['estimates'];assert len(estimates)==1 and int(estimates[0]['plate'])==1
    reports=['native-project-check.json','toolpath-check.json','print-feature-check.json','palm-support-check.json','p04-surface-check.json','cli-diagnostics.json','model-coverage-check.json','model-coverage-independent-review.json','connected-gui-check.json']
    verification={}
    for name in reports:
        path=OUT/'validation'/name;d=passed(path)
        for k in ('source_sha256','CAD_source_sha256'):
            if k in d:assert d[k]==frozen['source_sha256'],(name,k)
        for k in ('native_sha256','native_editable_project_sha256','editable_project_sha256'):
            if k in d:assert d[k]==sha(project),(name,k)
        for k in ('native_sliced_archive_sha256','sliced_archive_sha256','sliced_internal_evidence_sha256'):
            if k in d:assert d[k]==sha(sliced),(name,k)
        if 'layout_sha256' in d:assert d['layout_sha256']==sha(OUT/'plate-layout.json'),name
        if name=='cli-diagnostics.json':
            assert d['cli_exit_code']==0 and not d['unexpected_diagnostics'] and not d['missing_expected_diagnostics']
            assert d['official_machine_macros_identical_to_R13']
        verification[str(path.relative_to(ROOT))]={'status':d['status'],'sha256':sha(path)}
    p04=read(OUT/'validation/p04-surface-check.json')
    gui=passed(OUT/'validation/connected-gui-check.json')
    assert gui['opened_generic_project_sha256']==sha(project) and not gui['printer_job_started']
    for name,h in gui['evidence'].items():assert sha(OUT/'evidence'/name)==h,name
    independent=read(OUT/'validation/model-coverage-independent-review.json')
    assert independent['coverage_report_sha256']==sha(OUT/'validation/model-coverage-check.json')
    p04row=next(r for r in rows if r['ref']=='P04')
    with zipfile.ZipFile(sliced) as z:gcode=z.read('Metadata/plate_1.gcode').decode().replace('\r\n','\n')
    assert sha256(gcode.encode()).hexdigest()==p04['gcode_sha256']
    for k in ('rotation_3x3','normalization_translation_mm','plate_xy_mm'):assert p04[k]==p04row[k],k
    for r in rows:assert sha(ROOT/r['source_path'])==r['source_sha256'],r['ref']

    # Reuse assembly instructions, explicitly adapting only their print grouping.
    montage=(STUDY/'MONTAGE.md').read_text()
    montage=montage.replace('auf drei Druckplatten','auf einer gemeinsamen Druckplatte')
    (OUT/'MONTAGE.md').write_text(montage)
    shutil.copyfile(STUDY/'BOM_Aenderungen.csv',OUT/'BOM_Aenderungen.csv')
    (OUT/'source').mkdir(exist_ok=True)
    (OUT/'source-mm').mkdir(exist_ok=True)
    shutil.copyfile(STUDY/'fingerworker_R13_simple_palm.fs',OUT/'source/fingerworker_R13_simple_palm.fs')
    (OUT/'source/README.md').write_text('Autorenquellen und Skripte als Nachweis. Das 3MF-Projekt ist eigenständig. Die Skripte benötigen das Fingerworker-Repository und die lokale Bambu-Laufzeit. CAD-Revision R13 bleibt unverändert.\n')
    (OUT/'source-mm/README.md').write_text('Unveränderte R13-Geräte- und Passhilfenmeshes in Millimetern. Für den Druck das vorbereitete 3MF-Projekt verwenden. Gedruckte Stangen und Q01 sind ausschließlich federfreie Passhilfen.\n')
    # These frozen CAD/service results establish geometry provenance; the new
    # one-plate slice has its own reports above and never reuses old slice QA.
    cad_reports=[]
    for name in ('native-geometry.json','native-motion.json','service-native.json'):
        target=OUT/'validation'/('cad-R13-'+name)
        shutil.copyfile(STUDY/'validation'/name,target);cad_reports.append(target)
    fixture=STUDY/'fixture/validation.json'
    if not fixture.exists():fixture=STUDY/'validation/fixture-q01-check.json'
    target=OUT/'validation/cad-R13-fixture-q01-check.json'
    shutil.copyfile(fixture,target);cad_reports.append(target)
    parts=[]
    for r in rows:
        p=OUT/'STL-print-oriented'/(r['ref']+'.stl');assert p.is_file()
        parts.append({'ref':r['ref'],'quantity':1,'plate':1,'material':'PLA','category':'device' if r['ref'] in DEVICE else 'unloaded_fixture','intent':r['intent'],'file':p.name,'sha256':sha(p)})
    (OUT/'Druckliste.json').write_text(json.dumps({'revision':'R13','print_variant':'one_plate','device_parts':7,'unloaded_fixtures':3,'parts':parts},indent=2,ensure_ascii=False)+'\n')
    with (OUT/'Druckliste.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['Ref','Menge','Platte','Material','Kategorie','Hinweis','STL'])
        for r in parts:w.writerow([r['ref'],1,1,'PLA','Geräteteil' if r['category']=='device' else 'Unbelastete Passhilfe',r['intent'],'STL-print-oriented/'+r['file']])
    (OUT/'STL-print-oriented/manifest.json').write_text(json.dumps({'objects':10,'device_parts':7,'unloaded_fixtures':3,'identity':'Unchanged R13 geometry; rigid print placement only.','parts':parts},indent=2,ensure_ascii=False)+'\n')
    total_seconds=qa['estimated_seconds'];total_grams=qa['estimated_grams']
    readme=f'''# Fingerworker R13 – alle zehn Teile auf einer Platte

`{project.name}` in Bambu Studio als **Projekt** öffnen. Bambu H2D, Standarddüsen 0,4 mm, PLA, strukturierte PEI-Platte, Maßstab 100 %. Die Anordnung und individuellen Stützen übernehmen. Bei verbundenem Drucker Düsen und AMS synchronisieren und das tatsächlich eingelegte PLA zuordnen.

**Eine Platte, sieben Geräteteile und drei unbelastete Passhilfen.** P01, P04, P05, P06, P08, P09 und P11 gehören zum Gerät. H040/H041 und Q01 dienen nur dem federfreien Passaufbau. Keine gedruckten Schrauben, Muttern oder kleinen Sicherungsstifte.

Die CAD-Geometrie bleibt exakt R13. Es ändert sich ausschließlich die Druckanordnung. Alle Teile werden schichtweise gemeinsam gedruckt. Die Ausrichtungen für die saubere Fingerkontaktfläche, Klickarme und zugänglichen Stützen bleiben erhalten.

Vollständig gesliced: **{duration(total_seconds)} / {total_grams:.2f} g PLA**, einschließlich Stützen und Brims. Das Paket enthält das editierbare 3MF und zehn einzelne STLs. Kein Druckauftrag wurde gesendet.

Am verbundenen H2D zeigt die neu synchronisierte Bambu-Studio-Vorschau **{gui['displayed_estimate']} / {gui['displayed_filament_g']:.2f} g PLA**. Dabei wurden Düsen/AMS übernommen und Arc Fitting automatisch an die Firmware angepasst. Die Geräteanpassung bleibt im geöffneten Projekt; die generische Paketdatei ist unverändert.

Wenn du bereits einen R12-Satz hast und nur die neue Handballenform brauchst, genügt P01. Dafür bleibt das separate Dreiplattenprojekt vom 03.11.2026 mit P01 allein auf Platte 1 verfügbar. Vorhandene R13-Teile musst du für diese Ein-Platten-Variante nicht erneut drucken.

[Montage](MONTAGE.md) · [Druckliste](Druckliste.csv) · [Druckprüfung](PRINT_QA_NOTES.md) · [Onshape R13]({frozen['onshape_url']})

Gedruckte Passhilfen vor Einbau von Sensor und Federn entfernen. Reale Passung, Stützentfernung, Rastkraft und Belastbarkeit bleiben am Ausdruck zu prüfen.
'''
    (OUT/'README.md').write_text(readme)
    notes=f'''# R13 – Prüfung der gemeinsamen Druckplatte

Geprüft wurde das neue Ein-Platten-Projekt mit allen zehn Teilen, nicht lediglich die Summe der vorherigen Einzelplatten. Die native Projektprüfung bestätigt die richtige H2D-Konfiguration, die zehn Quellmeshes, unveränderte Geometrie und die finale Anordnung. Sämtliche Teile sind im tatsächlichen Slice enthalten.

Slicer-Schätzung: **{duration(total_seconds)} / {total_grams:.2f} g PLA** einschließlich Stützen und Brims.

Die Werkzeugwegprüfung kontrolliert Druckraumgrenzen und Abstände der tatsächlichen Extrusionswege einschließlich Stützen und Brims. Detailprüfungen decken die Fingerkontaktflächen, Führungen, Klickarme, festen Sensorflächen und die Handballen-Unterseite ab. Konkrete Toleranzen und Einzelwerte stehen in den beigefügten JSON-Berichten.

- [Native Projektprüfung](validation/native-project-check.json)
- [Druckraum und Werkzeugwege](validation/toolpath-check.json)
- [Bauteil- und Klickmerkmale](validation/print-feature-check.json)
- [Handballenauflage und Stützzugänge](validation/palm-support-check.json)
- [P04-Fingeroberfläche](validation/p04-surface-check.json)
- [Slicer-Diagnosen](validation/cli-diagnostics.json)
- [Gedruckte Modellbereiche](validation/model-coverage-check.json)
- [Unabhängige Prüfung der Nahtabweichungen](validation/model-coverage-independent-review.json)
- [Vorschau am verbundenen H2D](validation/connected-gui-check.json)

P04 bleibt in seiner geprüften Stirnseitenlage. Stützen vor der Montage vollständig entfernen. P09 und die hintere Traverse bleiben separat und ohne Stützen. Die neue gemeinsame Anordnung ändert keine Montagefunktion und entfernt keine Funktionshardware.

CAD-Quelle: `{frozen['source_sha256']}`. Die Berichte mit Präfix `cad-R13-` stammen aus der unveränderten R13-Freigabe vom 03.11.2026. Sie belegen Geometrie, Bewegungen und Service. Die Ein-Platten-Berichte sind separat an das neue Projekt, die Platzierung und den tatsächlichen Slice gebunden.

Das 3MF ist ein editierbares Projekt. Interne Prüfgcodes werden nicht ausgeliefert. Die Prüfungen bescheinigen nominelle Geometrie und berechnete Werkzeugwege; reale Passung, Oberfläche, Rastkraft, Stützentfernung und Belastbarkeit wurden nicht gemessen.

Der Diagnosebericht erfasst die bekannten Meldungen der unveränderten H2D-Herstellermakros ausdrücklich. Der finale Ein-Platten-Lauf fügt gegenüber der R13-Referenz keine neue Diagnose hinzu und endet mit Code 0.
'''
    (OUT/'PRINT_QA_NOTES.md').write_text(notes)
    files=[project]+[OUT/n for n in ('README.md','MONTAGE.md','BOM_Aenderungen.csv','PRINT_QA_NOTES.md','Druckliste.csv','Druckliste.json','plate-layout.json')]
    for folder in ('profiles','STL-print-oriented','source-mm','source','preview'):
        files.extend(p for p in (OUT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc')
    files.extend(OUT/'evidence'/n for n in gui['evidence'])
    files.extend(OUT/'validation'/n for n in reports);files.extend(cad_reports)
    files=sorted(set(files));assert all(p.is_file() for p in files)
    assert sum(p.suffix=='.3mf' for p in files)==1
    assert not any(p.name.endswith(('.gcode','.gcode.3mf')) for p in files)
    for p in [p for p in files if p.suffix=='.md']:
        for link in re.findall(r'\]\(([^)]+)\)',p.read_text()):
            if '://' in link or link.startswith('#'):continue
            target=(p.parent/link.split('#')[0]).resolve()
            assert target.is_relative_to(OUT) and target.is_file(),(p,link)
    hashes={str(p.relative_to(OUT)):sha(p) for p in files}
    (OUT/'SHA256.json').write_text(json.dumps({'status':'DELIVERY_HASH_MANIFEST','revision':'R13','print_variant':'one_plate','device_parts':7,'unloaded_fixtures':3,'files':hashes},indent=2)+'\n')
    files.append(OUT/'SHA256.json');package=OUT/(BASE+'_Package.zip')
    with zipfile.ZipFile(package,'w',zipfile.ZIP_DEFLATED) as z:
        for p in files:z.write(p,p.relative_to(OUT))
    with zipfile.ZipFile(package) as z:
        assert z.testzip() is None
        for name,h in hashes.items():assert sha256(z.read(name)).hexdigest()==h
        assert sum(n.startswith('STL-print-oriented/') and n.endswith('.stl') for n in z.namelist())==10
        assert sum(n.endswith('.3mf') for n in z.namelist())==1
    delivery={'status':'PASS_R13_ONE_PLATE_DELIVERY','date':'2026-11-04','cad_revision':'R13','CAD_source_sha256':frozen['source_sha256'],'onshape_version':frozen['onshape_version'],'plate_count':1,'object_count':10,'device_parts':7,'unloaded_fixtures':3,'estimates':estimates,'estimated_seconds':total_seconds,'estimated_grams':total_grams,'verification':verification,'frozen_cad_specification_sha256':sha(STUDY/'final-specification.json'),'files_sha256':{str(p.relative_to(ROOT)):sha(p) for p in (project,package,OUT/'plate-layout.json',OUT/'SHA256.json')},'geometry_changes':False}
    delivery['connected_device_preview']=gui
    (OUT/'delivery-specification.json').write_text(json.dumps(delivery,indent=2)+'\n')
    print(json.dumps({'status':delivery['status'],'zip':package.name,'sha256':sha(package),'bytes':package.stat().st_size,'files':len(files),'plates':1,'objects':10},indent=2))

if __name__=='__main__':main()
