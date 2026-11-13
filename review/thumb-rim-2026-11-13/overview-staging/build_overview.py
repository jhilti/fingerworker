#!/usr/bin/env python3
"""Offline R19 CAD overview. No print package or slice is represented as ready."""
from pathlib import Path
from html import escape
from hashlib import sha256
import base64,json,re
HERE=Path(__file__).resolve().parent;ROOT=next(p for p in HERE.parents if (p/'firmware').is_dir());REVIEW='review/thumb-rim-2026-11-13'
read=lambda p:json.loads((ROOT/p).read_text());digest=lambda p:sha256(Path(p).read_bytes()).hexdigest()
def asset(path):
 p=ROOT/path;assert p.is_file();mime='image/svg+xml' if p.suffix=='.svg' else 'image/png'
 return 'data:'+mime+';base64,'+base64.b64encode(p.read_bytes()).decode()
def link(path,label,download=False):
 assert '://' in path or (ROOT/path).is_file(),path
 return '<a class="file" href="'+escape(path,quote=True)+'"'+(' download' if download else '')+'>'+escape(label)+'</a>'
spec=read(REVIEW+'/final-specification.json');assert spec['status']=='PASS_NATIVE_CAD_PRINT_SETUP_DEFERRED' and spec['native_solids']==94 and not spec['print_ready']
assert spec['print_setup_status']=='PRINT_SETUP_DEFERRED_BY_USER'
for path,h in spec['files_sha256'].items():assert digest(ROOT/path)==h,path
model=json.loads((HERE/'model/manifest.json').read_text());assert model['revision']=='R19' and model['source_sha256']==spec['source_sha256'] and len(model['parts'])==94 and model['counts']['print']==8
content=json.loads((HERE/'content.json').read_text());assert content['revision']=='R19' and content['print_count']==8
labels={'P01':('Grundrahmen mit weichen Daumenrändern','new','R19 geändert'),'P06L':('Massiver hinterer Stangenblock links','new','R19 neu'),'P06R':('Massiver hinterer Stangenblock rechts','new','R19 neu'),'P08':('Optionale Elektronikwanne mit festen Schraubohren','new','R19 geändert · optional'),'P04':('Fingergriff','reuse','Unverändert'),'P05':('Separates Messjoch mit Anschlägen','reuse','Unverändert'),'P11':('Schalternocken für Feinabgleich','reuse','Unverändert'),'P09':('Separater Klickdeckel mit Kabelhalter','reuse','Unverändert · optional')}
rows=[];step=REVIEW+'/native/Flat132_R19_final_AP214.step';native_zip=REVIEW+'/native/Flat132_R19_neutral_final.zip'
for ref,(label,scope,state) in labels.items():
 rows.append(f'<tr data-scope="{scope}" data-new="{str(scope=="new").lower()}"><td class="code">{ref}</td><td><strong>{escape(label)}</strong></td><td>1</td><td><span class="badge {"good" if scope=="new" else ""}">{escape(state)}</span></td><td>{link(step,"Baugruppe ↓",True)}</td></tr>')
hardware=[]
for group,ref,qty,name,status,note in content['hardware']:
 style='good' if status.startswith('Vorhanden') else 'warn' if any(x in status.lower() for x in ['unbestätigt','prüfen','erforderlich']) else ''
 hardware.append(f'<tr data-group="{escape(group)}"><td><strong>{escape(ref)}</strong><small>{escape(qty)}</small></td><td>{escape(group)}</td><td>{escape(name)}<small>{escape(note)}</small></td><td><span class="badge {style}">{escape(status)}</span></td></tr>')
checks=[]
for ident,title,desc,path,group in content['checks']:
 checks.append(f'<article class="check-item"><input type="checkbox" id="check-{ident}" data-check="{ident}"><div><label for="check-{ident}">{escape(title)}</label><p>{escape(desc)} {link(path,"Quelle ↗")}</p></div><span class="badge">{escape(group)}</span></article>')
files=[(step,'Native R19-Baugruppe','94 Körper; maßgebliche Geometrie','STEP'),(native_zip,'Native R19-STL-Geometrie','CAD-Exporte in Baugruppenlage; keine Druckvorbereitung','ZIP'),(REVIEW+'/fingerworker_R19_thumb_rim.fs','Parametrische R19-Quelle','Weichere Ränder und massive Befestigungen','FS'),(REVIEW+'/MONTAGE.md','Montage und Service','Schrauben, Gurte und Sensorzugang','MD'),(REVIEW+'/BOM_Aenderungen.csv','Stücklistenänderungen R19','Neue Heckblöcke und erforderliche Schrauben','CSV'),(REVIEW+'/parts-review.md','Konstruktionsreview','Radien, Unterlippe und Funktionsschnittstellen','MD'),(REVIEW+'/mechanics/design-specification.json','Maße und Prüfbindung','Native Randmessung und verbleibende Wände','JSON'),('electronics/Fingerworker_KiCad_RevA_Routed.zip','Elektronik-CAD Rev A-P1','Gerouteter Prototyp; Fertigerprüfung beachten','ZIP'),('electronics/jlc-review-2026-11-02/placement-review.json','Bestückungsprüfung','D1-Polung weiterhin offen','JSON'),('firmware/README.md','Firmware und Bench-Erststart','Build, Flashen und Hardwareabnahme','MD'),('ios/README.md','iPhone-App und BLE','Installation, Training und Verbindung','MD')]
cards=[]
for path,title,desc,ext in files:
 assert (ROOT/path).is_file(),path
 cards.append(f'<a class="file-card" href="{escape(path,quote=True)}"'+(' download' if ext in ['ZIP','STEP','FS','CSV'] else '')+f'><span><strong>{escape(title)}</strong><small>{escape(desc)}</small></span><span class="extension">{ext} ↗</span></a>')
reports=[]
for path,e in spec['verification'].items():
 assert digest(ROOT/path)==e['sha256'];reports.append(f'<div class="report"><div>{link(path,Path(path).stem.replace("-"," ")+" ↗")}<small>Native CAD-Prüfung; Toleranzen und Geltungsbereich im Bericht.</small></div><span class="badge good">{escape(e["status"])}</span></div>')
assets={}
for token,png,prov in [('IMG_CAD','P01-final-native.png','P01-final-native-provenance.json'),('IMG_RIM','P01-final-native-detail.png','P01-final-native-detail.json'),('IMG_ASSEMBLY','assembly-final-native.png','assembly-final-native.json'),('IMG_RIGID','rigid-parts-final-native.png','rigid-parts-final-native.json'),('IMG_STRAP','strap-routing.svg','strap-routing-provenance.json')]:
 path=REVIEW+'/evidence/'+png;info=read(REVIEW+'/evidence/'+prov);assert info['source_sha256']==spec['source_sha256'] and info['image_sha256']==digest(ROOT/path);assets[token]=asset(path)
repl={'CSS':(HERE/'style.css').read_text()+'\n#fw3d{border:0}@media print{#fw3d{display:none!important}}','JS':(HERE/'app.js').read_text(),'DATA':json.dumps(content,ensure_ascii=False).replace('</','<\\/'),'MODEL':(HERE/'model/component.html').read_text(),'REVIEW':REVIEW,'ONSHAPE':spec['onshape_url'],'CAD_STEP':step,'CAD_BODY_COUNT':'94','PRINT_ROWS':'\n'.join(rows),'HARDWARE_ROWS':'\n'.join(hardware),'CHECK_ROWS':'\n'.join(checks),'HW_COUNT':str(len(hardware)),'FILE_CARDS':'\n'.join(cards),'REPORT_ROWS':'\n'.join(reports),'SOURCE_HASH_SHORT':spec['source_sha256'][:16]+'…'+spec['source_sha256'][-8:],**assets}
html=(HERE/'template.html').read_text()
for key,value in repl.items():html=html.replace('@@'+key+'@@',value)
assert not re.search(r'@@[A-Z0-9_]+@@',html)
out=ROOT/'Uebersicht.html' if HERE==ROOT/'overview' else HERE/'Uebersicht.preview.html'
if HERE!=ROOT/'overview':html=html.replace('<head>','<head><base href="'+ROOT.as_uri()+'/">',1)
out.write_text(html)
inputs=[HERE/n for n in ['template.html','style.css','app.js','content.json','model/component.html','model/manifest.json']]+[ROOT/REVIEW/'final-specification.json']
manifest=dict(gui_verified=False,gui_status=spec['gui_status'],print_setup_status=spec['print_setup_status'],date='2026-11-13',status='BUILT_CAD_OVERVIEW_PRINT_DEFERRED',html=out.name,html_bytes=out.stat().st_size,html_sha256=digest(out),revision='R19',primary_action='NATIVE_CAD',native_onshape_version=spec['onshape_version'],source_sha256=spec['source_sha256'],print_items=len(rows),hardware_rows=len(hardware),personal_check_items=len(checks),inline_assets=True,external_runtime_requests=False,source_files={str(p.relative_to(ROOT)):digest(p) for p in inputs})
(HERE/'build-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps({k:manifest[k] for k in ['status','html','html_bytes','print_items','hardware_rows']},indent=2))
