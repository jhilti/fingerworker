#!/usr/bin/env python3
"""Build the offline R18 overview only from released CAD and print artifacts."""
from pathlib import Path
from html import escape
from hashlib import sha256
import base64,json,re
HERE=Path(__file__).resolve().parent;ROOT=next(p for p in HERE.parents if (p/'firmware').is_dir())
REVIEW='review/organic-palm-2026-11-13';PACK='print/bambu-R18-organic-palm-2026-11-13'
BASE='Fingerworker_R18_H2D_04mm_PLA_Basic_Upright_Grip'
PROJECT=PACK+'/'+BASE+'.3mf';PROJECT_ZIP=PACK+'/'+BASE+'_Package.zip'
CAD_STEP=REVIEW+'/native/Flat132_R18_final_AP214.step'
read=lambda p:json.loads((ROOT/p).read_text())
digest=lambda p:sha256(Path(p).read_bytes()).hexdigest()
def asset(path):
 p=ROOT/path;assert p.is_file(),path
 mime='image/svg+xml' if p.suffix.lower()=='.svg' else 'image/jpeg' if p.suffix.lower() in ['.jpg','.jpeg'] else 'image/png'
 return 'data:'+mime+';base64,'+base64.b64encode(p.read_bytes()).decode()
def link(path,label,download=False):
 assert '://' in path or (ROOT/path).is_file(),path
 return '<a class="file" href="'+escape(path,quote=True)+'"'+(' download' if download else '')+'>'+escape(label)+'</a>'
source=read(REVIEW+'/final-specification.json');delivery=read(PACK+'/delivery-specification.json');layout=read(PACK+'/plate-layout.json')
assert source['status'].startswith('PASS') and source['fit_test_pieces']==6 and source['plates']==1
assert source['native_solids']==93 and source['printed_device_bodies']==7
assert delivery['status']=='PASS_R18_ORGANIC_PALM_DELIVERY' and delivery['object_count']==1 and delivery['secondary_object_count']==6
assert delivery['CAD_source_sha256']==source['source_sha256'] and delivery['onshape_version']==source['onshape_version']
assert layout['CAD_source_sha256']==source['source_sha256'] and layout['native_R18_version']==source['onshape_version']
for owner in (source,delivery):
 for p,h in owner['files_sha256'].items():assert digest(ROOT/p)==h,p
# The delivery manifest binds both separately sealed packages.
gui_path=ROOT/PACK/'validation/P01-replacement/gui-check.json'
if gui_path.exists():
 gui=read(str(gui_path.relative_to(ROOT)));assert gui['status'].startswith('PASS') and not gui['printer_job_started']
 assert gui['source_sha256']==source['source_sha256'] and gui['project_sha256']==digest(ROOT/delivery['project'])
else:
 assert source['gui_verified']==delivery['gui_verified']==False
 assert source['gui_status']=='GUI_PENDING_MAC_LOCKED'
 gui=dict(status=source['gui_status'],summary=source['gui_summary'],printer_job_started=False)
READY_PROJECT=delivery['project'];READY_ZIP=delivery['package']
# GUI evidence is optional only in the explicit, documented locked-Mac mode.
model=json.loads((HERE/'model/manifest.json').read_text());assert model['revision']=='R18' and model['source_sha256']==source['source_sha256']
assert len(model['parts'])==93 and model['counts']['print']==7
content=json.loads((HERE/'content.json').read_text());assert content['revision']=='R18' and content['print_count']==6
labels={
 'P01':('Grundrahmen mit organischer Handballenauflage und seitlichen Daumenmulden','new','R18: nur P01 neu drucken'),
 'P04':('Fingergriff in bewährter Stirnseiten-Drucklage','reuse','R16-Geometrie unverändert'),
 'P05':('Messjoch mit integralen Anschlägen','reuse','R16-Geometrie unverändert'),
 'P06':('Gemeinsame feste hintere Klicktraverse','reuse','R16-Geometrie unverändert'),
 'P11':('Einstellbarer Schalternocken','reuse','R16-Geometrie unverändert'),
 'Q01':('Passhilfe für feste Sensorabstützung','proxy','R12–R18 kompatibel · nur federfrei')}
rows=[]
assert {p['ref'] for p in layout['placements']}==set(labels)
for ref,(label,scope,state) in labels.items():
 r=next(p for p in layout['placements'] if p['ref']==ref);assert r['plate']==1
 path=PACK+'/STL-print-oriented/'+ref+'.stl'
 rows.append(f'<tr data-scope="{scope}" data-new="{str(ref=="P01").lower()}" data-plate="1"><td class="code">{ref}<small>1 × PLA</small></td><td><strong>{escape(label)}</strong></td><td>1</td><td><span class="badge {"good" if scope=="new" else ""}">{escape(state)}</span></td><td>{link(path,"STL ↓",True)}</td></tr>')
hardware=[]
for group,ref,qty,name,status,note in content['hardware']:
 style='good' if status.startswith('Vorhanden') else 'warn' if ('unbestätigt' in status or 'Bestand prüfen' in status or 'Fertiger' in status or 'erforderlich' in status) else ''
 hardware.append(f'<tr data-group="{escape(group)}"><td><strong>{escape(ref)}</strong><small>{escape(qty)}</small></td><td>{escape(group)}</td><td>{escape(name)}<small>{escape(note)}</small></td><td><span class="badge {style}">{escape(status)}</span></td></tr>')
checks=[]
for ident,title,desc,path,group in content['checks']:
 checks.append(f'<article class="check-item"><input type="checkbox" id="check-{ident}" data-check="{ident}"><div><label for="check-{ident}">{escape(title)}</label><p>{escape(desc)} {link(path,"Quelle ↗")}</p></div><span class="badge">{escape(group)}</span></article>')
files=[
 (READY_PROJECT,'P01: empfohlenes Ersatzprojekt','Nur den neuen Rahmen drucken · PLA Basic · linke 0,4-mm-Düse','3MF'),
 (READY_ZIP,'P01-Ersatzpaket','Ein Druckteil, vorbereitetes Projekt, Montage und aktuelle Nachweise','ZIP'),
 (delivery['secondary_project'],'Optional: vollständiger R18-Satz','Sechs Stücke auf einer Platte; Alternative zum P01-Nachdruck','3MF'),
 (delivery['secondary_package'],'Optional: vollständiges Druckpaket','Alle sechs Teile, Montage und Prüfberichte','ZIP'),
 (CAD_STEP,'Gesamtes natives R18-CAD','93 Körper; maßgebliche R18-Geometrie','STEP'),
 (REVIEW+'/fingerworker_R18_organic_palm.fs','Parametrische CAD-Quelle','Eingefrorener R18-FeatureScript-Stand','FS'),
 (REVIEW+'/MONTAGE.md','Montage und Entriegelung','Aufrechter Griff, Daumenrückgriffe und Sensorservice','MD'),
 (REVIEW+'/BOM_Aenderungen.csv','Stücklistenänderungen R18','Nur P01 ändert seine Form; keine neuen Griffkleinteile','CSV'),
 (REVIEW+'/parts-review.md','Review des integrierten Handballengriffs','Kontaktfläche, Sensor-Kraftpfad, Klickflächen und Service','MD'),
 (REVIEW+'/mechanics/design-specification.json','Maße der neuen Kontaktflächen','Gewölbte Handballenfläche, beidseitige Daumenmulden, erhaltene Schnittstellen','JSON'),
 (PACK+'/PRINT_QA_NOTES.md','Prüfung der R18-Druckplatte','Tatsächliche Druckwege, Kontaktflächen, Stützen und Abstände','MD'),
 ('print/bambu-R13-one-plate-2026-11-04/README.md','Historie: vollständiger R13-Satz','Enthält den früheren P01; keine R18-Druckvorlage','MD'),
 ('electronics/Fingerworker_KiCad_RevA_Routed.zip','Elektronik-CAD Rev A-P1','Gerouteter KiCad-Prototyp; neuere JLC-Prüfung beachten','ZIP'),
 ('electronics/jlc-review-2026-11-02/placement-review.json','JLC-Platzierungsprüfung 02.11.','Korrigierte Ansicht; D1-Polung offen','JSON'),
 ('firmware/README.md','Firmware und Bench-Erststart','Build, Flashen, Kalibrierung und Hardwarefreigabe','MD'),
 ('ios/README.md','iPhone-App und BLE','Installation, Training, lokale Archive und Export','MD')]
file_cards=[]
for path,title,desc,ext in files:
 assert (ROOT/path).is_file(),path
 file_cards.append(f'<a class="file-card" href="{escape(path,quote=True)}"'+(' download' if ext in ['3MF','ZIP','STEP','FS','CSV'] else '')+f'><span><strong>{escape(title)}</strong><small>{escape(desc)}</small></span><span class="extension">{ext} ↗</span></a>')
report_titles={'native-integration.json':'Native R18-Geometrie, Hub, Service und 92 unveränderte Körper','native-section-fidelity.json':'Native organische Form und Querschnittskontrollen','native-release-binding.json':'Bindung an die gespeicherte Onshape-Version','native-geometry.json':'Native R18-Geometrie und 92 unveränderte Körper','native-motion.json':'Voller Hub und Sensor-Kraftpfad','service-native.json':'Sensorservice an der nativen Baugruppe','fixture-q01-check.json':'Q01-Passung und Entnahme','native-project-check.json':'Finales natives 3MF-Projekt','toolpath-check.json':'Tatsächliche Extrusionswege','p04-surface-check.json':'P04-Fingeroberfläche und Führung','palm-support-check.json':'Neue Handballenfläche und Daumenrückgriffe im Slice','strap-slot-check.json':'Vier offene Gurtschlitze und dichte Stege im Slice','strap-routing-check.json':'Gurtführung und Bewegungsraum','strap-routing-visual-check.json':'Gerenderte Montageabbildung','print-feature-check.json':'Gedruckte Funktionsmerkmale','independent-profile-review.json':'Unabhängige Profilprüfung','preflight.json':'Lokale Konstruktion und Schnittstellen','no-brim-check.json':'Alle sechs Modelle ohne Brim','independent-strap-native.json':'Unabhängige native Gurtprüfung'}
verification={**source['verification'],**delivery['verification']};report_rows=[]
for path,e in verification.items():
 p=ROOT/path;assert digest(p)==e['sha256'],path
 if p.name=='gui-check.json':continue
 title=report_titles.get(p.name,p.stem.replace('-',' ').replace('_',' ').capitalize())
 state='PASS' if e['status'].startswith(('PASS','NATIVE_PROJECT')) else e['status']
 report_rows.append(f'<div class="report"><div>{link(path,title+" ↗")}<small>Hashgebundener Nachweis; Geltungsbereich und Toleranzen im Bericht.</small></div><span class="badge good">{escape(state)}</span></div>')
for path,title in [('electronics/jlc-review-2026-11-01/cam-analysis.json','JLC-CAM-Abgleich · 01.11.2026'),('ios/TRAINING_VERIFICATION.md','Softwareprüfung · 11.10.2026')]:
 report_rows.append(f'<div class="report"><div>{link(path,title+" ↗")}<small>Historischer Nachweis; reale Elektronik-/BLE-Abnahme weiterhin offen.</small></div><span class="badge">Dokumentiert</span></div>')
seconds=delivery['estimated_seconds']
gui_note=gui.get('summary','In Bambu Studio geöffnet und gesliced; kein Druckauftrag gestartet. Aktuelle Filamentzuordnung vor dem Drucken prüfen.')
cad=read(source['overview_assets']['cad_image_provenance'])
assert cad['image_sha256']==digest(ROOT/source['overview_assets']['cad_image']) and cad['source_sha256']==source['source_sha256']
assert cad['native_zip_sha256']==delivery['native_zip_sha256']
support=PACK+'/preview/P04-Stuetzen.png'
provenance=read(PACK+'/validation/p04-preview-provenance.json')
assert provenance['image_sha256']==digest(ROOT/support)
assert provenance['layout_sha256']==digest(ROOT/PACK/'plate-layout.json')
strap=source['overview_assets']['strap_image'];routing=read(REVIEW+'/evidence/strap-routing-provenance.json')
assert routing['image_sha256']==digest(ROOT/strap) and routing['source_sha256']==source['source_sha256']
assert routing['native_step_sha256']==delivery['native_step_sha256']
replacements={
 'CSS':(HERE/'style.css').read_text()+'\n#fw3d{border:0} @media print{#fw3d{display:none!important}}',
 'JS':(HERE/'app.js').read_text(),'DATA':json.dumps(content,ensure_ascii=False).replace('</','<\\/'),
 'MODEL':(HERE/'model/component.html').read_text(),'PACK':PACK,'REVIEW':REVIEW,'PROJECT':READY_PROJECT,'PROJECT_ZIP':READY_ZIP,'CAD_STEP':CAD_STEP,
 'ONSHAPE':source['onshape_url'],'CAD_BODY_COUNT':str(source['native_solids']),
 'FRAME_WIDTH':'132','PALM_WIDTH':'116','PALM_DEPTH':'15',
 'SECONDARY_PROJECT':delivery['secondary_project'],'SECONDARY_PACKAGE':delivery['secondary_package'],
 'SECONDARY_TIME':f"{delivery['secondary_estimated_seconds']//3600}h{delivery['secondary_estimated_seconds']%3600//60:02d}m",'SECONDARY_GRAMS':f"{delivery['secondary_estimated_grams']:.2f}".replace('.',','),
 'TOTAL_TIME':f'{seconds//3600}h{seconds%3600//60:02d}m','TOTAL_GRAMS':f"{delivery['estimated_grams']:.2f}".replace('.',','),
 'GUI_NOTE':gui_note,'ZIP_SIZE':f'{(ROOT/READY_ZIP).stat().st_size/1e6:.1f}'.replace('.',',')+' MB',
 'SOURCE_HASH_SHORT':source['source_sha256'][:16]+'…'+source['source_sha256'][-8:],
 'PRINT_ROWS':'\n'.join(rows),'HARDWARE_ROWS':'\n'.join(hardware),'CHECK_ROWS':'\n'.join(checks),'HW_COUNT':str(len(hardware)),
 'FILE_CARDS':'\n'.join(file_cards),'REPORT_ROWS':'\n'.join(report_rows),
 'IMG_STRAP':asset(strap),'IMG_PLATE':asset(PACK+'/preview/P01-replacement/plate_1.png'),'IMG_CAD':asset(source['overview_assets']['cad_image']),'IMG_SUPPORT':asset(support)}
html=(HERE/'template.html').read_text()
if support.startswith(PACK+'/'):
 html=html.replace('Tatsächliche Slicerpfade des Dreiplatten-Projekts. Die gleichen acht Kontaktregionen sind auch in der aktuellen Mechanikplatte geprüft.','Tatsächliche Slicerpfade der aktuellen R18-Mechanikplatte. Acht Kontaktregionen sind im Bericht geprüft.')
for key,value in replacements.items():html=html.replace('@@'+key+'@@',value)
assert not re.search(r'@@[A-Z0-9_]+@@',html)
output=(ROOT/'Uebersicht.html') if HERE==ROOT/'overview' else HERE/'Uebersicht.preview.html'
if HERE!=ROOT/'overview':html=html.replace('<head>','<head><base href="'+ROOT.as_uri()+'/">',1)
output.write_text(html)
inputs=[HERE/n for n in ['template.html','style.css','app.js','content.json','model/component.html','model/manifest.json']]
inputs += [ROOT/REVIEW/'final-specification.json',ROOT/PACK/'delivery-specification.json',ROOT/PACK/'plate-layout.json',ROOT/strap,ROOT/REVIEW/'evidence/strap-routing-provenance.json']
if gui_path.exists():inputs.append(gui_path)
manifest=dict(gui_verified=source['gui_verified'],gui_status=source['gui_status'],primary_print_profile='PLA_Basic',connected_ready_project_sha256=digest(ROOT/READY_PROJECT),date='2026-11-13',status='BUILT_PENDING_BROWSER_QA',html=output.name,html_bytes=output.stat().st_size,html_sha256=digest(output),revision='R18',primary_print_variant='P01_replacement',native_onshape_version=source['onshape_version'],source_sha256=source['source_sha256'],print_items=len(rows),hardware_rows=len(hardware),personal_check_items=len(checks),inline_assets=True,external_runtime_requests=False,source_files={str(p.relative_to(ROOT)):digest(p) for p in inputs})
(HERE/'build-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({k:manifest[k] for k in ['status','html','html_bytes','html_sha256','print_items','hardware_rows']},indent=2))
