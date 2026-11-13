from pathlib import Path
import json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];OV=ROOT/'overview';PACK='print/bambu-R15-inboard-straps-2026-11-08';BASE='Fingerworker_R15_H2D_04mm_PLA_Basic_Print_Ready'
r=json.loads((ROOT/PACK/'connected-ready-delivery.json').read_text());assert r['status']=='PASS_CONNECTED_READY_DELIVERY'
p=OV/'build_overview.py';s=p.read_text();assert 'ready_delivery=' not in s
needle="model=read('overview/model/manifest.json')"
add="""ready_delivery=read(PACK+'/connected-ready-delivery.json')
assert ready_delivery['status']=='PASS_CONNECTED_READY_DELIVERY' and ready_delivery['source_sha256']==source['source_sha256'] and ready_delivery['onshape_version']==source['onshape_version']
for path,h in ready_delivery['files_sha256'].items():assert digest(ROOT/path)==h,path
ready_gui=read(PACK+'/validation/connected-gui-check.json')
assert ready_gui['connected_project_sha256']==ready_delivery['project_sha256'] and not ready_gui['printer_job_started']
READY_PROJECT=ready_delivery['project'];READY_ZIP=ready_delivery['package']
"""
assert needle in s;s=s.replace(needle,add+needle)
s=s.replace(" (PROJECT,'R15: mechanischer Sechsersatz','Innenliegende P01-Gurtschlitze, alle Modelle ohne Brim; echte Stangen verwenden','3MF'),\n (PROJECT_ZIP,'R15-Druckpaket','Projekt, sechs druckfertige STLs, PLA-Profil, Montage und aktuelle Nachweise','ZIP'),", " (READY_PROJECT,'R15: am H2D vorbereitet','Bambu PLA Basic · linke Düse · AMS A3 bei Vorbereitung','3MF'),\n (READY_ZIP,'R15-Druckpaket: Print Ready','Vorbereitetes Projekt, sechs druckfertige STLs, Montage und aktuelle Nachweise','ZIP'),\n (PROJECT,'Alternative: Generic PLA','Unveränderte allgemeine Profilvariante; eigener Slice 10 h 59 min / 230,01 g','3MF'),\n (PROJECT_ZIP,'Generic-PLA-Archivpaket','Getrennte Ausgangsvariante mit eigenen Nachweisen','ZIP'),")
start=s.index("seconds=delivery['estimated_seconds'];gui=");end=s.index("cad=read(source['overview_assets']",start)
s=s[:start]+"""seconds=delivery['estimated_seconds']
gui_note='In Bambu Studio vorbereitet: HAM_H2D_0, Bambu PLA Basic, linke 0,4-mm-Düse und AMS A3. Die rechte Düse und PETG bleiben unbenutzt. GUI-Slice und Sendedialog sind geprüft; kein Druckauftrag wurde gestartet. Beim erneuten Öffnen die aktuelle AMS-Zuordnung prüfen.'
for path,title in [(PACK+'/validation/connected-gui-check.json','Verbundenes H2D-Projekt und Sendedialog'),(ready_delivery['audit_path'],'Tatsächlicher GUI-Slice'),(PACK+'/validation/connected-geometry-settings-check.json','Unveränderte Teile, Platzierung und Druckparameter')]:
 report_rows.append('<div class="report"><div>'+link(path,title+' ↗')+'<small>Nachweis der separaten PLA-Basic-Variante; keine Druckübertragung.</small></div><span class="badge good">PASS</span></div>')
"""+s[end:]
s=s.replace("'PROJECT':PROJECT,'PROJECT_ZIP':PROJECT_ZIP", "'PROJECT':READY_PROJECT,'PROJECT_ZIP':READY_ZIP")
s=s.replace("'TOTAL_TIME':f'{seconds//3600} h {(seconds%3600)//60:02d} min {seconds%60:02d} s','TOTAL_GRAMS':f\"{delivery['estimated_grams']:.2f}\".replace('.',','),", "'TOTAL_TIME':ready_delivery['displayed_estimate'],'TOTAL_GRAMS':f\"{ready_delivery['displayed_filament_g']:.2f}\".replace('.',','),")
s=s.replace("(ROOT/PROJECT_ZIP).stat().st_size/1e6", "(ROOT/READY_ZIP).stat().st_size/1e6")
s=s.replace("manifest=dict(date=", "inputs += [ROOT/PACK/'connected-ready-delivery.json',ROOT/PACK/'validation/connected-gui-check.json',ROOT/ready_delivery['audit_path'],ROOT/PACK/'validation/connected-geometry-settings-check.json']\nmanifest=dict(primary_print_profile='connected_PLA_Basic',connected_ready_project_sha256=ready_delivery['project_sha256'],date=")
p.write_text(s);compile(s,str(p),'exec')
p=OV/'template.html';s=p.read_text().replace('PLA als Standard','Bambu PLA Basic · links · AMS A3').replace('Mechanik-3MF','Druckbereites 3MF').replace('Sechser-Paket','Print-Ready-Paket');s=s.replace('Tatsächliche Slicerpfade der aktuellen R15-Mechanikplatte. Acht Kontaktregionen sind im Bericht geprüft. Die reale Oberfläche und Entfernbarkeit bestätigt der nächste Druck.','Abgebildet sind die Stützpfade der getrennten Generic-PLA-Variante. Die aktuelle PLA-Basic-Variante besitzt einen eigenen Bericht zum tatsächlichen GUI-Slice. Reale Oberfläche und Entfernbarkeit bestätigt der nächste Druck.')
p.write_text(s)
p=OV/'validate_static.py';s=p.read_text().replace("assert 'In Bambu Studio geöffnet' in visible and 'GUI-Slice-Vorschau blieb' in visible", "assert 'In Bambu Studio vorbereitet' in visible and 'GUI-Slice und Sendedialog sind geprüft' in visible\nassert manifest['primary_print_profile']=='connected_PLA_Basic' and '233,58' in visible and '10h49m' in visible")
p.write_text(s);compile(s,str(p),'exec')
print('Connected PLA Basic variant added to overview source; run overview builder and static QA.')

for name in ['README.md','PRINTING.md','EINKAUFSTEILE.md','DEVICE_UPGRADES.md','print/REVISION_STATUS.md']:
 p=ROOT/name;text=p.read_text();assert '<!-- CONNECTED_R15_READY_START -->' not in text
 prefix='../' if name.startswith('print/') else ''
 block=f"""<!-- CONNECTED_R15_READY_START -->
> **08.11.2026 – direkt am H2D vorbereitet:** [PLA-Basic-Projekt]({prefix}{PACK}/{BASE}.3mf) · [Print-Ready-Paket]({prefix}{PACK}/{BASE}_Package.zip). Sechs Teile auf einer Platte, alle ohne Brim, erforderliche PLA-Stützen erhalten. Linke 0,4-mm-Standarddüse, Bambu PLA Basic aus AMS A3 bei Vorbereitung; kein PETG. GUI-Schätzung **10 h 49 min / 233,58 g**. Sendedialog geprüft, **kein Druckauftrag gestartet**. [Nachweise]({prefix}{PACK}/connected-ready-delivery.json). Die folgende Generic-PLA-Variante bleibt als separat geprüfte Ausgangsdatei erhalten.
<!-- CONNECTED_R15_READY_END -->

"""
 marker='<!-- CURRENT_FLAT132_R15_START -->';assert marker in text;text=text.replace(marker,block+marker,1);text=text.replace('Tatsächlicher Slice: **10 h 59 min','Generic-PLA-Slice: **10 h 59 min');p.write_text(text)
