from pathlib import Path
import json,html,hashlib
R=Path(__file__).resolve().parent;d=json.loads((R/'mechanical-envelopes.json').read_text());items=d['bodies'];B={x['id']:x for x in items};inside=d['case_inner']
audit_path=R.parents[1]/'review/electronics-packaging-validation.json'
audit=json.loads(audit_path.read_text()) if audit_path.exists() else {}
verified=audit.get('cad_source_sha256')==hashlib.sha256((R.parents[1]/'fingerworker_mvp.fs').read_bytes()).hexdigest() and len(audit.get('pose_results',[]))==3
onshape_status='verified 0/15/30 mm; nominal fit, not manufacturing release' if verified else 'pending current source audit'
checks=[]
for q in items:
 if q['id'] in ['elecCase','elecUsb','elecButton']:continue
 gaps=[q['lo'][k]-inside['lo'][k] for k in range(3)]+[inside['hi'][k]-q['hi'][k] for k in range(3)]
 checks.append({'body':q['id'],'inside_reserved_cavity':min(gaps)>=-1e-6,'minimum_gap_mm':round(min(gaps),4)})
report={'scope':'axis-aligned nominal PCB courtyard and height envelopes; NOT a regenerated Onshape collision audit','source_sha256':hashlib.sha256((R.parents[1]/'fingerworker_mvp.fs').read_bytes()).hexdigest(),'case_mm':[22.5,110,8.9],'pcb_mm':[19.5,68.5,.8],'pcb_lateral_gap_mm':.5,'pcb_bottom_gap_mm':.3,'connector_top_gap_with_0_15_solder_allowance_mm':.35,'battery_rear_gap_mm':1,'mating_plug_allowance_to_cell_gap_mm':1.3,'case_to_palm_plate_nominal_gap_mm':.6,'onshape_regeneration':onshape_status,'checks':checks,'limitations':['XIAO 5 mm height is a budget, not a measured module stack.','Mated plug and initial wire extension 6 mm is an allowance; measure actual harness.','Side-button actuator is a travel envelope, not a printable pushrod.','Wire exits, retention, battery swelling and strain relief are not mechanically released.','Nominal housing/mechanism gap 0.6 mm; validate printed tolerances and loaded deformation. Electronics/illustrative-hand gap 4.70 mm.']}
assert all(x['inside_reserved_cavity'] for x in checks),[x for x in checks if not x['inside_reserved_cavity']]
(R/'reports/mechanical-fit-local.json').write_text(json.dumps(report,indent=2)+'\n')
S=[]
def add(x):S.append(x)
def text(x,y,t,size=20,fill='#173b41',weight='400'):add(f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{fill}">{html.escape(t)}</text>')
add('<svg xmlns="http://www.w3.org/2000/svg" width="1480" height="1040" viewBox="0 0 1480 1040"><rect width="1480" height="1040" fill="#f5f7f5"/><g font-family="Arial, sans-serif">')
text(55,60,'FINGERWORKER / Elektronik-Bauraum',32,weight='700');text(55,94,('KiCad-Einbaustudie · Onshape bei 0 / 15 / 30 mm geprüft · Nennmaßprüfung' if verified else 'KiCad-Einbaustudie · aktueller Onshape-Abgleich ausstehend'),18)
# XY view uses the same scale in both directions.
scale=6.7
for q in items:
 if q['id']=='elecUsb':continue
 x=85+(q['lo'][0]+47)*scale;y=140+(q['lo'][1]+55)*scale;w=(q['hi'][0]-q['lo'][0])*scale;h=(q['hi'][1]-q['lo'][1])*scale
 color='#e5efef' if q['id']=='elecCase' else '#33865b' if q['id']=='elecCarrier' else '#e4b44f' if q['id']=='elecBattery' else '#338ac2' if q['id']=='elecPartU1' else '#d8d0b7' if q['id'] in ['elecMate','elecPartJ1'] else '#439485'
 add(f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" rx="1.4" fill="{color}" stroke="#31585b" stroke-width="0.7"/>')
for y,t in [(195,'USB / XIAO BLE'),(323,'Antennenfreiraum'),(395,'5-V-Versorgung'),(464,'ADC + Messfilter'),(573,'Akku-Steckverbinder'),(635,'Gegenstecker / Leitung'),(780,'100-mAh-Akku')]:
 add(f'<path d="M 250 {y} H 286" stroke="#7c989b"/>');text(298,y+6,t,18)
text(86,925,'Draufsicht · Maßstab intern 1:1',16)
# Section in local housing coordinates (global X shifted -1.25 mm). Across J1: case + cavity + PCB + 5.65 mm solder/body envelope.
ox=740;oy=460;sc=22
for lo,hi,col in [([-44.85,0],[-22.35,8.9],'#c8dadb'),([-43.85,1],[-23.35,8.1],'#f5f7f5'),([-43.35,1.3],[-23.85,2.1],'#33865b'),([-36.495,2.1],[-27.205,7.75],'#d8d0b7')]:
 x=ox+(lo[0]+44.85)*sc;y=oy-hi[1]*sc;add(f'<rect x="{x}" y="{y}" width="{(hi[0]-lo[0])*sc}" height="{(hi[1]-lo[1])*sc}" fill="{col}" stroke="#31585b" stroke-width="1"/>')
add(f'<rect x="{ox}" y="{oy-10.5*sc}" width="{22.5*sc}" height="{1*sc}" fill="#596f72"/>')
text(720,170,'Schnitt am Akkustecker',24,weight='700');text(720,205,'Höhen und Breiten maßstäblich; Hüllkörper statt Detail-STEP',15)
text(760,500,'22,5 mm Gehäusebreite',20);text(720,557,'0,5 mm Spiel je Platinenseite',23,weight='700');text(720,596,'0,35 mm Reserve über dem JST inkl. Lötzugabe',19)
text(720,632,'Mechanik-Minimum: 0,6 mm · Drucktoleranz prüfen',19,fill='#a54f25');text(720,668,'8,9 mm Elektronikgehäuse · Gerät weiterhin 30 mm hoch',19)
text(720,735,'Noch physisch zu prüfen',23,weight='700');text(720,775,'Gegenstecker, Kabelbiegung, Tasterbetätigung, Akkuhalterung',17);text(720,807,'und Modulhöhe am tatsächlichen Aufbau.',17)
text(55,993,'Referenzstudie. Kein druckfertiges Gehäuse und keine Fertigungsfreigabe.',17,fill='#6c7b7a');add('</g></svg>')
(R/'preview/mechanical-fit.svg').write_text('\n'.join(S));print('Local nominal fit:',len(checks),'envelopes within cavity; preview saved')
