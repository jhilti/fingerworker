#!/usr/bin/env python3
"""Package the validated six-piece mechanics print; CAD R14 stays frozen."""
from pathlib import Path
from hashlib import sha256
import csv,json,re,shutil,zipfile

OUT=Path(__file__).resolve().parents[1];ROOT=OUT.parents[1]
STUDY=ROOT/'review/near-palm-2026-11-06'
BASELINE_STUDY=ROOT/'review/palm-simplification-2026-11-03'
BASE='Fingerworker_R14_H2D_04mm_PLA_Near_Palm'
DEVICE={'P01','P04','P05','P06','P11'}
FIXTURES={'Q01'}
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
    baseline=passed(BASELINE_STUDY/'final-specification.json')
    for name,h in baseline['files_sha256'].items():assert sha(ROOT/name)==h,name
    source=STUDY/'fingerworker_R14_near_palm.fs';version=read(STUDY/'onshape-version.json')
    native=passed(STUDY/'validation/native-geometry.json')
    assert sha(source)==native['source_sha256']==version['source_sha256']
    assert native['native_step_sha256']==sha(STUDY/'native/Flat132_R14_final_AP214.step')
    assert native['native_zip_sha256']==sha(STUDY/'native/Flat132_R14_neutral_final.zip')
    assert len(native['unchanged_native_breps'])==92
    design=read(STUDY/'mechanics/design-specification.json');assert design.get('strap_mount')
    assert design['source_sha256']==sha(source)
    frozen={'source_sha256':sha(source),'onshape_version':version['version_id'],'onshape_url':version['url']}
    docs=passed(STUDY/'documentation-ready.json')
    assert docs['source_sha256']==sha(source) and docs['onshape_version']==version['version_id']
    for name,h in docs['files_sha256'].items():assert sha(ROOT/name)==h,name
    for name,e in docs['verification'].items():assert sha(ROOT/name)==e['sha256'],name
    layout=read(OUT/'plate-layout.json');rows=layout['placements']
    assert len(rows)==6 and {r['ref'] for r in rows}==DEVICE|FIXTURES
    assert {r['plate'] for r in rows}=={1} and layout['object_count']==6
    assert layout['modifier_count']==4 and len(layout['local_density_modifiers'])==4
    assert layout['CAD_source_sha256']==frozen['source_sha256']
    assert layout['native_R14_version']==frozen['onshape_version']
    qa=passed(OUT/'validation/native-project-check.json')
    assert qa['status'].startswith(('PASS','NATIVE_PROJECT'))
    assert qa['plate_count']==1 and qa['object_count']==6
    assert qa['geometry_and_orientations_preserved'] and qa['all_checks_passed']
    assert all(qa['checks'].values())
    for k in ('retained_machine_start_gcode','retained_machine_end_gcode','retained_change_filament_gcode'):assert qa['checks'][k]
    assert {r['ref'] for r in rows}=={'P01','P04','P05','P06','P11','Q01'}
    assert set(layout['omitted'])=={'P08','P09','H040','H041'}
    project=OUT/layout['native_project'];assert project.name==BASE+'.3mf'
    assert sha(project)==qa['native_project_sha256']
    sliced=OUT/'validation'/(BASE+'_verification.gcode.3mf')
    assert sha(sliced)==qa['sliced_project_sha256']
    estimates=[{'plate':1,'seconds':qa['estimate_seconds'],'grams':qa['filament_g']}]
    reports=['native-project-check.json','toolpath-check.json','print-feature-check.json','palm-support-check.json','strap-slot-check.json','strap-routing-check.json','p04-surface-check.json','cli-diagnostics.json','independent-profile-review.json']
    if (OUT/'validation/connected-gui-check.json').exists():reports.append('connected-gui-check.json')
    verification={}
    for name in reports:
        path=OUT/'validation'/name;d=passed(path)
        for k in ('source_sha256','CAD_source_sha256'):
            if k in d:assert d[k]==frozen['source_sha256'],(name,k)
        for k in ('native_sha256','native_project_sha256','native_editable_project_sha256','editable_project_sha256'):
            if k in d:assert d[k]==sha(project),(name,k)
        for k in ('native_sliced_archive_sha256','sliced_project_sha256','sliced_archive_sha256','sliced_internal_evidence_sha256'):
            if k in d:assert d[k]==sha(sliced),(name,k)
        if 'layout_sha256' in d:assert d['layout_sha256']==sha(OUT/'plate-layout.json'),name
        if 'native_step_sha256' in d:assert d['native_step_sha256']==native['native_step_sha256'],name
        if name=='cli-diagnostics.json':
            assert d['cli_exit_code']==0 and not d['unexpected_diagnostics'] and not d['missing_expected_diagnostics']
            assert d.get('official_machine_macros_identical_to_R14',d.get('official_machine_macros_identical_to_R13',False))
        verification[str(path.relative_to(ROOT))]={'status':d['status'],'sha256':sha(path)}
    preview_path=OUT/'validation/p04-preview-provenance.json';preview=read(preview_path)
    assert preview['status']=='RENDERED_ACTUAL_R14_P04_SUPPORT_PATHS'
    assert preview['sliced_archive_sha256']==sha(sliced)
    assert preview['layout_sha256']==sha(OUT/'plate-layout.json')
    assert preview['image_sha256']==sha(OUT/'preview/P04-Stuetzen.png')
    p04=read(OUT/'validation/p04-surface-check.json')
    gui=None
    if 'connected-gui-check.json' in reports:
        gui=passed(OUT/'validation/connected-gui-check.json')
        assert gui['opened_generic_project_sha256']==sha(project) and not gui['printer_job_started']
        for name,h in gui['evidence'].items():assert sha(OUT/'evidence'/name)==h,name
    gui_limitation=read(OUT/'validation/gui-check.json') if (OUT/'validation/gui-check.json').exists() else None
    if gui_limitation:
        assert gui_limitation['project_sha256']==sha(project) and not gui_limitation['print_started'] and not gui_limitation['existing_printer_job_modified']
    p04row=next(r for r in rows if r['ref']=='P04')
    with zipfile.ZipFile(sliced) as z:gcode=z.read('Metadata/plate_1.gcode').decode().replace('\r\n','\n')
    assert sha256(gcode.encode()).hexdigest()==p04['gcode_sha256']
    for k in ('rotation_3x3','normalization_translation_mm','plate_xy_mm'):assert p04[k]==p04row[k],k
    for r in rows:assert sha(ROOT/r['source_path'])==r['source_sha256'],r['ref']

    # Reuse assembly instructions, explicitly adapting only their print grouping.
    montage=(STUDY/'MONTAGE.md').read_text()
    montage='# Mechanischer Passaufbau – Druckumfang dieser Platte\n\nEnthalten: P01, P04, P05, P06, P11 und Q01. Vorhandene echte Führungsstangen verwenden; P08/P09 und gedruckte Stangen entfallen in diesem Druckauftrag. Die folgende vollständige R14-Montage beschreibt auch den späteren Elektronikaufbau. Q01 bleibt ausschließlich eine unbelastete, federfreie Passhilfe.\n\n'+montage
    montage=montage.replace('(mechanics/design-specification.json)','(source/design-specification.json)').replace('(evidence/strap-routing.svg)','(preview/strap-routing.svg)')
    routing=read(STUDY/'evidence/strap-routing-provenance.json')
    assert routing['native_step_sha256']==native['native_step_sha256'] and routing['source_sha256']==sha(source)
    assert routing['image_sha256']==sha(STUDY/'evidence/strap-routing.svg')
    (OUT/'preview').mkdir(exist_ok=True)
    shutil.copyfile(STUDY/'evidence/strap-routing.svg',OUT/'preview/strap-routing.svg')
    shutil.copyfile(STUDY/'evidence/strap-routing-provenance.json',OUT/'preview/strap-routing-provenance.json')
    shutil.copyfile(STUDY/'evidence/strap-routing-visual-check.json',OUT/'preview/strap-routing-visual-check.json')
    shutil.copyfile(STUDY/'evidence/strap-routing-preview.png',OUT/'preview/strap-routing-preview.png')
    for name in ('native-geometry.json','native-motion.json','service-native.json','fixture-q01-check.json'):
        montage=montage.replace('(validation/'+name+')','(validation/cad-R14-'+name+')')
    (OUT/'MONTAGE.md').write_text(montage)
    shutil.copyfile(STUDY/'BOM_Aenderungen.csv',OUT/'BOM_Aenderungen.csv')
    (OUT/'source').mkdir(exist_ok=True)
    (OUT/'source-mm').mkdir(exist_ok=True)
    shutil.copyfile(STUDY/'fingerworker_R14_near_palm.fs',OUT/'source/fingerworker_R14_near_palm.fs')
    shutil.copyfile(STUDY/'mechanics/design-specification.json',OUT/'source/design-specification.json')
    shutil.copyfile(STUDY/'evidence/render_strap_routing.py',OUT/'source/render_strap_routing.py')
    if not (OUT/'source/README.md').exists():(OUT/'source/README.md').write_text('Autorenquellen und Skripte als Nachweis. Das 3MF-Projekt ist eigenständig. Die Skripte benötigen das Fingerworker-Repository und die lokale Bambu-Laufzeit. CAD-Revision R14 mit neuer griffnaher Handballenauflage; nicht mit einem alten P01 verwechseln.\n')
    (OUT/'source-mm/README.md').write_text('Finale native R14-Meshes für P01/P04/P05/P06/P11 und Q01 in Millimetern. Für den Druck das vorbereitete 3MF-Projekt verwenden. Q01 ist ausschließlich eine federfreie Passhilfe. Die vorhandenen echten Führungsstangen verwenden.\n')
    # These frozen CAD/service results establish geometry provenance; the new
    # one-plate slice has its own reports above and never reuses old slice QA.
    cad_reports=[]
    for name in ('native-geometry.json','native-motion.json','service-native.json'):
        target=OUT/'validation'/('cad-R14-'+name)
        current=passed(STUDY/'validation'/name)
        assert current['source_sha256']==sha(source)
        shutil.copyfile(STUDY/'validation'/name,target);cad_reports.append(target)
    fixture=STUDY/'fixture/validation.json'
    if not fixture.exists():fixture=STUDY/'validation/fixture-q01-check.json'
    target=OUT/'validation/cad-R14-fixture-q01-check.json'
    fixture_qa=passed(fixture);assert fixture_qa['native_assembly_step_sha256']==native['native_step_sha256']
    shutil.copyfile(fixture,target);cad_reports.append(target)
    parts=[]
    for r in rows:
        p=OUT/'STL-print-oriented'/(r['ref']+'.stl');assert p.is_file()
        parts.append({'ref':r['ref'],'quantity':1,'plate':1,'material':'PLA','category':'device' if r['ref'] in DEVICE else 'unloaded_fixture','intent':r['intent'],'file':p.name,'sha256':sha(p)})
    (OUT/'Druckliste.json').write_text(json.dumps({'revision':'R14','print_variant':'near_palm','device_parts':5,'unloaded_fixtures':1,'parts':parts},indent=2,ensure_ascii=False)+'\n')
    with (OUT/'Druckliste.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['Ref','Menge','Platte','Material','Kategorie','Hinweis','STL'])
        for r in parts:w.writerow([r['ref'],1,1,'PLA','Geräteteil' if r['category']=='device' else 'Unbelastete Passhilfe',r['intent'],'STL-print-oriented/'+r['file']])
    (OUT/'STL-print-oriented/manifest.json').write_text(json.dumps({'objects':6,'device_parts':5,'unloaded_fixtures':1,'identity':'Exact final native R14 geometry; print orientation only.','parts':parts},indent=2,ensure_ascii=False)+'\n')
    total_seconds=qa['estimate_seconds'];total_grams=qa['filament_g']
    gui_note=(f"Am verbundenen H2D zeigt die aktuelle Vorschau **{gui['displayed_estimate']} / {gui['displayed_filament_g']:.2f} g PLA**. Vor dem Start tatsächliches PLA zuordnen.\n\n" if gui else '')
    if gui_limitation:gui_note+='Die neue Datei wurde in der geöffneten Bambu-Studio-Sitzung noch nicht angezeigt; ein bestehendes ungespeichertes Projekt blieb erhalten. Import, Slice und tatsächliche Druckwege sind mit der offiziellen Bambu-Laufzeit geprüft. [GUI-Prüfstand](validation/gui-check.json)\n\n'
    readme=f'''# Fingerworker R14 – griffnahe Handballenauflage mit Gurtaufnahme

`{project.name}` in Bambu Studio als **Projekt** öffnen. Bambu H2D, Standarddüsen 0,4 mm, PLA, strukturierte PEI-Platte, Maßstab 100 %. Die Anordnung und individuellen Stützen übernehmen. Düsen und AMS synchronisieren und das tatsächlich eingelegte PLA zuordnen.

**Eine Platte: fünf Geräteteile P01/P04/P05/P06/P11 und die unbelastete Sensor-Passhilfe Q01.** Die echten Führungsstangen sind bereits vorhanden. Elektronikwanne P08, Deckel P09 und gedruckte Stangen H040/H041 werden hier weggelassen. Keine Schrauben, Muttern oder Mini-Pins drucken.

P01 hat eine neue breite Rundung nahe der Sensorwand; der äußere Handballenbalken entfällt. Die Auflage bleibt mit dem Rahmen ein Druckteil. Vier gerundete 27 × 4-mm-Öffnungen in flachen äußeren Ösen schaffen zwei Positionen für echte 25-mm-Gurte; Gurte werden nicht gedruckt. Beide Enden werden durch die jeweilige Öffnung nach oben, über den äußeren Steg und außen zurückgeführt und sicher an sich selbst befestigt. Der lange Gurt läuft unten um den Gegenstand; über dem Griff bleibt der Bewegungsraum frei. Die übrigen nativen Teile bleiben gegenüber R13 unverändert. Das Profil für den mechanischen Passaufbau verwendet 20 % Gyroid. Vier lokale 100-%-Bereiche mit geradlinigem Infill füllen die Gurtösen und ihre kurzen Übergänge zur Platte dicht. Diese Modifikatoren sind Einstellungen im 3MF, keine zusätzlichen Druckteile. Vier Wände und 0,2-mm-Schichten bleiben erhalten; P11 druckt weiterhin mit 0,1 mm. P11 und Q01 bleiben 100 % gefüllt. P04 behält seine bewährte Drucklage sowie die langsameren Außen-, Oberflächen- und Stützgeschwindigkeiten; P06 behält seine Klickarm-Außenparameter. Die Beschleunigung beträgt global bis zu 6000 mm/s² innen und 1500 mm/s² an Außenwänden sowie oberen Flächen. P01 druckt außen mit bis zu 100 mm/s und obere Flächen mit bis zu 60 mm/s; Handkomfort und Oberfläche sind am neuen Ausdruck zu beurteilen. Das Druckprofil ist noch keine physische Festigkeitsqualifikation.

Vollständig gesliced: **{duration(total_seconds)} / {total_grams:.2f} g PLA**, einschließlich Stützen und Brims. Das Paket enthält ein editierbares 3MF und sechs STLs. Kein Druckauftrag wurde gesendet.

{gui_note}Die tatsächliche Dauer hängt vom Drucker und seinem aktuellen Profil ab. 

[Montage](MONTAGE.md) · [Druckliste](Druckliste.csv) · [Druckprüfung](PRINT_QA_NOTES.md) · [Onshape R14]({frozen['onshape_url']})

Zunächst federfrei mit Q01 montieren. Q01 vor Einbau von Sensor und Federn entfernen. Reale Passung, Stützentfernung, Rastkraft und Belastbarkeit bleiben am Ausdruck zu prüfen. Vorhandene P04/P05/P06/P11 und echte Führungsstangen bleiben verwendbar. Für die neue Handposition muss P01 R14 verwendet werden. P08/P09 bleiben für den späteren Elektronikaufbau separat verfügbar.
'''
    (OUT/'README.md').write_text(readme)
    notes=f'''# R14 – Prüfung der mechanischen Druckplatte

Geprüft wurde der aktuelle Slice mit sechs Teilen. Slicer-Schätzung: **{duration(total_seconds)} / {total_grams:.2f} g PLA**, einschließlich Stützen und Brims.

Die native Projektprüfung bindet die sechs aktuellen Druckmeshes, Druckausrichtungen und erklärten Einstellungen an das Projekt. Die Werkzeugwegprüfung kontrolliert die tatsächlichen Extrusionswege einschließlich Stützen und Brims, Druckraumgrenzen und Abstände. Detailprüfungen betreffen Fingerkontaktflächen, Führungen, Klickarme, feste Sensorflächen und die Handballen-Unterseite.

- [Native Projektprüfung](validation/native-project-check.json)
- [Druckraum und Werkzeugwege](validation/toolpath-check.json)
- [Bauteil- und Klickmerkmale](validation/print-feature-check.json)
- [Handballenauflage und Stützzugänge](validation/palm-support-check.json)
- [Vier freie Gurtöffnungen und dichte Ösen](validation/strap-slot-check.json)
- [Gurtführung und Bewegungsraum](validation/strap-routing-check.json)
- [P04-Fingeroberfläche](validation/p04-surface-check.json)
- [Slicer-Diagnosen](validation/cli-diagnostics.json)
- [Unabhängige Profilprüfung](validation/independent-profile-review.json)

Die neue P01-Geometrie und der tatsächliche Slice werden gemeinsam geprüft. Die übrigen Teile behalten ihre nativen Funktionen. Die Kontaktflächen, freien Stützzugänge und berechneten Druckwege sind separat geprüft; gleicher Handkomfort oder gleiche Festigkeit werden daraus nicht abgeleitet.

P04 bleibt in der geprüften Stirnseitenlage. Stützen vor der Montage vollständig entfernen. P06 bleibt ohne Stützen. P08/P09 und gedruckte Führungsstangen sind nicht Bestandteil dieses Druckauftrags; vorhandene echte Stangen verwenden.

CAD-Quelle: `{frozen['source_sha256']}`. Die Berichte mit Präfix `cad-R14-` belegen die aktuelle native Geometrie, Bewegungen und Service dieser R14-Revision. Die neuen Druckberichte sind an das aktuelle Projekt, die Platzierung und den tatsächlichen Slice gebunden.

Das 3MF ist ein editierbares Projekt. Interne Prüfgcodes werden nicht ausgeliefert. Reale Passung, Oberfläche, Rastkraft, Stützentfernung, Festigkeit und Dauerverhalten sind noch nicht gemessen. Q01 bleibt ausschließlich eine federfreie Passhilfe.
'''
    if gui:notes+='\n[Vorschau am verbundenen H2D](validation/connected-gui-check.json)\n'
    if gui_limitation:notes+='\n[GUI-Prüfstand: bestehendes Nutzerprojekt erhalten](validation/gui-check.json). Kein neuer GUI-Slice-Nachweis; offizielle CLI-Prüfung und tatsächliche Druckwege sind oben dokumentiert.\n'
    (OUT/'PRINT_QA_NOTES.md').write_text(notes)
    files=[project]+[OUT/n for n in ('README.md','MONTAGE.md','BOM_Aenderungen.csv','PRINT_QA_NOTES.md','Druckliste.csv','Druckliste.json','plate-layout.json')]
    for folder in ('profiles','STL-print-oriented','source-mm','source','preview'):
        files.extend(p for p in (OUT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc')
    if gui:files.extend(OUT/'evidence'/n for n in gui['evidence'])
    files.extend(OUT/'validation'/n for n in reports);files.extend(cad_reports);files.append(preview_path)
    if gui_limitation:files.append(OUT/'validation/gui-check.json')
    files=sorted(set(files));assert all(p.is_file() for p in files)
    assert sum(p.suffix=='.3mf' for p in files)==1
    assert not any(p.name.endswith(('.gcode','.gcode.3mf')) for p in files)
    for p in [p for p in files if p.suffix=='.md']:
        for link in re.findall(r'\]\(([^)]+)\)',p.read_text()):
            if '://' in link or link.startswith('#'):continue
            target=(p.parent/link.split('#')[0]).resolve()
            assert target.is_relative_to(OUT) and target.is_file(),(p,link)
    hashes={str(p.relative_to(OUT)):sha(p) for p in files}
    (OUT/'SHA256.json').write_text(json.dumps({'status':'DELIVERY_HASH_MANIFEST','revision':'R14','print_variant':'near_palm','device_parts':5,'unloaded_fixtures':1,'files':hashes},indent=2)+'\n')
    files.append(OUT/'SHA256.json');package=OUT/(BASE+'_Package.zip')
    with zipfile.ZipFile(package,'w',zipfile.ZIP_DEFLATED) as z:
        for p in files:z.write(p,p.relative_to(OUT))
    with zipfile.ZipFile(package) as z:
        assert z.testzip() is None
        for name,h in hashes.items():assert sha256(z.read(name)).hexdigest()==h
        assert sum(n.startswith('STL-print-oriented/') and n.endswith('.stl') for n in z.namelist())==6
        assert sum(n.endswith('.3mf') for n in z.namelist())==1
    delivery={'status':'PASS_R14_NEAR_PALM_DELIVERY','date':'2026-11-06','cad_revision':'R14','CAD_source_sha256':frozen['source_sha256'],'onshape_version':frozen['onshape_version'],'plate_count':1,'object_count':6,'device_parts':5,'unloaded_fixtures':1,'estimates':estimates,'estimated_seconds':total_seconds,'estimated_grams':total_grams,'verification':verification,'baseline_R13_specification_sha256':sha(BASELINE_STUDY/'final-specification.json'),'native_step_sha256':native['native_step_sha256'],'native_zip_sha256':native['native_zip_sha256'],'files_sha256':{str(p.relative_to(ROOT)):sha(p) for p in (project,package,OUT/'plate-layout.json',OUT/'SHA256.json')},'geometry_changes':['P01']}
    delivery['connected_device_preview']=gui
    delivery['gui_preview_limitation']=gui_limitation
    delivery['profile_changes']=layout['profile_changes']
    delivery['modifier_count']=layout['modifier_count']
    delivery['local_density_modifiers']=layout['local_density_modifiers']
    delivery['preview_provenance']={str(preview_path.relative_to(ROOT)):sha(preview_path)}
    delivery['omitted']=layout['omitted']
    delivery['CAD_verification']={str(x.relative_to(ROOT)):{'status':read(x)['status'],'sha256':sha(x)} for x in [STUDY/'validation'/n for n in ['native-geometry.json','native-motion.json','service-native.json','fixture-q01-check.json']]}
    delivery['source_files_sha256']={str(x.relative_to(ROOT)):sha(x) for x in [source,STUDY/'onshape-version.json']}
    (OUT/'delivery-specification.json').write_text(json.dumps(delivery,indent=2)+'\n')
    print(json.dumps({'status':delivery['status'],'zip':package.name,'sha256':sha(package),'bytes':package.stat().st_size,'files':len(files),'plates':1,'objects':6},indent=2))

if __name__=='__main__':main()
