#!/usr/bin/env python3
"""Generate native KiCad schematic + footprint placement from reviewed Rev A.
Run using KiCad's bundled Python (pcbnew). Not a fabrication release.
"""
import os, json, uuid, math, shutil, copy, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
os.environ['KICAD_CONFIG_HOME']=str(ROOT/'.config')
import pcbnew as pcb
LIB=Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport')
SRC=ROOT.parent
if (ROOT/'Fingerworker_RevA.kicad_sch').exists() and '--regenerate-reviewed-schematic' not in sys.argv:
    raise SystemExit('Refusing to overwrite reviewed native schematics/libraries/settings. Use --regenerate-reviewed-schematic only intentionally, then rerun verification and packaging.')
NAME='Fingerworker_RevA'
def uid(s): return str(uuid.uuid5(uuid.NAMESPACE_URL,'fingerworker/kicad/reva/'+s))
def q(s): return json.dumps(str(s),ensure_ascii=False)
def mm(x): return pcb.FromMM(x)
def v(x,y): return pcb.VECTOR2I(mm(x),mm(y))
data=json.loads((SRC/'design.json').read_text())
parts=copy.deepcopy(data['parts'])
by={p['ref']:p for p in parts}
# Physical pin mapping checked against the official Seeed SMD symbol.
u=by['U1']['pins'];u['19']=u.pop('BAT+');u['20']=u.pop('BAT-')
for n,name,net in [('15','SWDIO',None),('16','SWCLK',None),('17','RESET_N',None),('18','GND','GND'),('21','NFC1',None),('22','NFC2',None)]:u[n]={'name':name,'net':net}
u=by['U1']['pins']=dict(sorted(u.items(),key=lambda kv:int(kv[0])))
sw=by['SW2']['pins'];sw['1']=sw.pop('A');sw['2']=sw.pop('B')
# Actual PCB symbol values, not function descriptions.
for r,val in {'U1':'XIAO_nRF52840','U2':'TPS61041DBVR','U3':'TPS7A2050PDBVR','U4':'ADS1220IPWR','Q1':'2N7002','D1':'MBR0520LT1G','SW2':'EVQPUC02K','J1':'JST_PH_2','J2':'FORCE_4','J3':'END_2'}.items():by[r]['value']=val
fmap={
'U1':'Seeed_XIAO_nRF52840_SMD','U2':'SOT-23-5','U3':'SOT-23-5','U4':'TSSOP-16_4.4x5mm_P0.65mm',
'Q1':'SOT-23','D1':'D_SOD-123','L1':'L_Coilcraft_XFL3012','SW2':'Panasonic_EVQPUL_EVQPUC',
'J1':'JST_PH_S2B-PH-SM4-TB_1x02-1MP_P2.00mm_Horizontal','J2':'SolderWire_4x2mm_P2.54','J3':'SolderWire_2x2mm_P2.54'}
for p in parts:
 r=p['ref']
 if r.startswith('R'):fmap[r]='R_0603_1608Metric'
 if r.startswith('C'):fmap[r]='C_0805_2012Metric' if '0805' in p['package'] else 'C_0603_1608Metric'
 if p['kind']=='external': continue
 p['footprint']='Fingerworker:'+fmap[r]
# Local copies make the project portable without external footprint-library setup.
libmap={'SOT-23-5':'Package_TO_SOT_SMD','SOT-23':'Package_TO_SOT_SMD','TSSOP-16_4.4x5mm_P0.65mm':'Package_SO','D_SOD-123':'Diode_SMD','Panasonic_EVQPUL_EVQPUC':'Button_Switch_SMD','JST_PH_S2B-PH-SM4-TB_1x02-1MP_P2.00mm_Horizontal':'Connector_JST','R_0603_1608Metric':'Resistor_SMD','C_0805_2012Metric':'Capacitor_SMD','C_0603_1608Metric':'Capacitor_SMD'}
for name,lib in libmap.items():shutil.copyfile(LIB/'footprints'/f'{lib}.pretty'/f'{name}.kicad_mod',ROOT/'Fingerworker.pretty'/f'{name}.kicad_mod')
dp=ROOT/'Fingerworker.pretty/D_SOD-123.kicad_mod'
dp.write_text(dp.read_text().replace('"F.SilkS"','"F.Fab"'))
xiao=(SRC/'vendor/xiao_footprints/Seeed_Studio_XIAO_Series.pretty/XIAO-nRF52840-SMD.kicad_mod').read_text()
xiao=xiao.replace('(footprint "XIAO-nRF52840-SMD"','(footprint "Seeed_XIAO_nRF52840_SMD"',1)
# Preserve all official copper dimensions; move decorative outline to fabrication.
# It otherwise crosses castellated solder lands and the board edge (USB overhang).
xiao=xiao.replace('"F.SilkS"','"F.Fab"')
xiao=xiao[:xiao.rfind(')')]+'(attr smd)\n'+xiao[xiao.rfind(')'):]
(ROOT/'Fingerworker.pretty/Seeed_XIAO_nRF52840_SMD.kicad_mod').write_text(xiao)
def make_fp(name,pads,body,courtyard,descr):
 s=f'(footprint {q(name)} (version 20241229) (generator "pcbnew") (layer "F.Cu") (descr {q(descr)}) (attr smd)\n'
 s+='(property "Reference" "REF**" (at 0 -3 0) (layer "F.SilkS") (effects (font (size 0.8 0.8) (thickness 0.12))))\n'
 s+=f'(property "Value" {q(name)} (at 0 3 0) (layer "F.Fab") (effects (font (size 0.8 0.8) (thickness 0.1))))\n'
 for layer,box,w in [('F.Fab',body,.1),('F.CrtYd',courtyard,.05)]:
  a,b,c,d=box;s+=f'(fp_rect (start {a} {b}) (end {c} {d}) (stroke (width {w}) (type default)) (fill none) (layer {q(layer)}))\n'
 for num,x,y,sx,sy in pads:s+=f'(pad {q(num)} smd roundrect (at {x} {y}) (size {sx} {sy}) (layers "F.Cu" "F.Paste" "F.Mask") (roundrect_rratio 0.1))\n'
 s+=')\n';(ROOT/'Fingerworker.pretty'/f'{name}.kicad_mod').write_text(s)
make_fp('L_Coilcraft_XFL3012',[('1',-1.015,0,1,2.9),('2',1.015,0,1,2.9)],(-1.5,-1.5,1.5,1.5),(-1.85,-1.85,1.85,1.85),'Coilcraft document 747-1: 1.00 x 2.90 lands, 2.03 mm centers, 1.30 mm maximum height; dot/start lead on pad 2 (SW).')
for n in [2,4]:
 # Wire pads have no solder paste, for hand-soldered leads with case strain relief.
 name=f'SolderWire_{n}x2mm_P2.54'
 make_fp(name,[(str(i+1),0,2.54*(i-(n-1)/2),2,1.7) for i in range(n)],(-1,-n*1.27,1,n*1.27),(-1.3,-n*1.27,1.3,n*1.27),'Hand-solder wire land; separate printed strain relief required')
 p=ROOT/'Fingerworker.pretty'/f'{name}.kicad_mod';p.write_text(p.read_text().replace('"F.Cu" "F.Paste" "F.Mask"','"F.Cu" "F.Mask"'))
# Separate Kelvin sense nets physically join at the excitation solder lands only.
kp=ROOT/'Fingerworker.pretty/SolderWire_4x2mm_P2.54.kicad_mod'
kt=kp.read_text().rstrip();kt=kt[:-1]+'(net_tie_pad_groups "1,5" "4,6")\n'
for n,y,ey in [('5',-4.95,-3.81),('6',4.95,3.81)]:
 kt+=f'(pad "{n}" smd rect (at 0 {y}) (size .6 .3) (layers "F.Cu"))\n'
 kt+=f'(fp_line (start 0 {y}) (end 0 {ey}) (stroke (width .3) (type default)) (layer "F.Cu"))\n'
kt+=')\n';kt=kt.replace('(start -1.3 -5.08) (end 1.3 5.08)','(start -1.3 -5.4) (end 1.3 5.4)')
kp.write_text(kt)
(ROOT/'fp-lib-table').write_text('(fp_lib_table (version 7) (lib (name "Fingerworker")(type "KiCad")(uri "${KIPRJMOD}/Fingerworker.pretty")(options "")(descr "Local verified geometry for Rev A")))\n')
(ROOT/'sym-lib-table').write_text('(sym_lib_table (version 7) (lib (name "Fingerworker")(type "KiCad")(uri "${KIPRJMOD}/Fingerworker.kicad_sym")(options "")(descr "Pin-typed project symbols")))\n')
# Native symbol generation. Passive symbols use familiar IEC glyphs.
def effects(size=1.0,extra=''):return f'(effects (font (size {size} {size})) {extra})'
def prop(name,value,x=0,y=0,hide=False):return f'(property {q(name)} {q(value)} (at {x} {y} 0) {effects(1.0,"(hide yes)" if hide else "")})'
def line(pts):return '(polyline (pts '+' '.join(f'(xy {x} {y})' for x,y in pts)+') (stroke (width 0.254) (type default)) (fill (type none)))'
def pin_type(r,n,p):
 if r=='U1':
  if n in ['12','14']:return 'power_out'
  if n in ['13','18','20']:return 'power_in'
  if n=='19':return 'passive' # charger output and battery input in one physical pin
  if n in ['1','2','3','9','11']:return 'output'
  if n in ['4','5','6','7','10','16','17']:return 'input'
  return 'bidirectional'
 if r=='U2':return {'1':'open_collector','2':'power_in','3':'input','4':'input','5':'power_in'}[n]
 if r=='U3':return {'1':'power_in','2':'power_in','3':'input','4':'no_connect','5':'power_out'}[n]
 if r=='U4':
  if n in ['4','5','12','13']:return 'power_in'
  if n=='14':return 'output'
  if n=='15':return 'tri_state'
  return 'input'
 if r=='Q1':return 'input' if n=='1' else 'passive'
 if r=='H1':return 'output' if n in ['YELLOW','WHITE'] else 'power_in'
 if r=='BT1':return 'passive' # charged and discharged
 return 'passive'
layouts={};symbols={}
for p in parts:
 r=p['ref'];pins=p['pins'];kind=p['kind']; simple=kind in ['resistor','capacitor','inductor','diode','switch']
 name='Part_'+r
 if simple:
  pn=list(pins);coords={pn[0]:(-5.08,0,0),pn[1]:(5.08,0,180)};top=3.81
  if kind=='resistor':g='(rectangle (start -2.54 1.016) (end 2.54 -1.016) (stroke (width 0.254) (type default)) (fill (type none)))'
  elif kind=='capacitor':g=line([(-1.016,-2.54),(-1.016,2.54)])+line([(1.016,-2.54),(1.016,2.54)])
  elif kind=='inductor':g=''.join(f'(arc (start {x} 0) (mid {x+.635} .635) (end {x+1.27} 0) (stroke (width .254) (type default)) (fill (type none)))' for x in [-2.54,-1.27,0,1.27])
  elif kind=='diode':g=line([(-2,0),(2,2),(2,-2),(-2,0)])+line([(-2,-2),(-2,2)])
  else:g=line([(-2.54,0),(2,2)])+line([(2.54,0),(3,0)])
  lens={n:(4.064 if kind=='capacitor' else 2.54) for n in pins}
 else:
  keys=list(pins);left=keys[:math.ceil(len(keys)/2)];right=keys[math.ceil(len(keys)/2):]
  h=max(len(left),len(right))*2.54/2+1.27;top=h+2.54;half=17.78 if r=='U1' else 12.7
  coords={n:(-half-2.54,((len(left)-1)/2-i)*2.54,0) for i,n in enumerate(left)}
  coords.update({n:(half+2.54,((len(right)-1)/2-i)*2.54,180) for i,n in enumerate(right)})
  g=f'(rectangle (start {-half} {h}) (end {half} {-h}) (stroke (width 0.254) (type default)) (fill (type background)))'
  lens={n:2.54 for n in pins}
 layouts[r]=(coords,top)
 ss=f'(symbol {q(name)} (pin_names (offset 0.7)'+(' (hide yes)' if simple else '')+') (in_bom yes) (on_board '+('no' if kind=='external' else 'yes')+')\n'
 ss+=('(pin_numbers (hide yes))' if kind=='external' else '')
 ss+=prop('Reference',r,0,top)+prop('Value',p['value'],0,top+2.54)+prop('Footprint',p.get('footprint',''),hide=True)+prop('Datasheet',p['source'],hide=True)
 ss+=f'(symbol {q(name+"_0_1")} {g})\n(symbol {q(name+"_1_1")}\n'
 for n,pin in pins.items():
  x,y,a=coords[n]
  ss+=f'(pin {pin_type(r,n,p)} line (at {x} {y} {a}) (length {lens[n]}) (name {q(pin["name"])} {effects(.95)}) (number {q(n)} {effects(.95)}))\n'
 ss+='))\n';symbols[r]=ss
# Power flags explicitly identify passive delivery paths, without changing pin types.
flag='(symbol "PowerFlag" (power) (pin_names (offset 0)) (in_bom no) (on_board no) '+prop('Reference','#FLG',0,2,True)+prop('Value','PWR_FLAG',0,4)+ '(symbol "PowerFlag_0_1" '+line([(0,0),(0,2),(-1.27,3),(0,4),(1.27,3),(0,2)])+') (symbol "PowerFlag_1_1" (pin power_out line (at 0 0 90) (length 0) (name "pwr" '+effects()+') (number "1" '+effects()+'))))'
(ROOT/'Fingerworker.kicad_sym').write_text('(kicad_symbol_lib (version 20250114) (generator "kicad_symbol_editor")\n'+''.join(symbols.values())+flag+')\n')
rootid=uid('root')
sheets={
'Power':{'id':uid('sheet-power'),'page':'2','title':'BLE, battery and switched 5 V','refs':['U1','J1','BT1','C1','R1','R2','C2','U2','L1','D1','R3','R4','R5','C3','C4','C5','U3','R6','C6','C7']},
'Acquisition':{'id':uid('sheet-adc'),'page':'3','title':'Force bridge, input filters and ADS1220','refs':['U4','J2','H1','R7','R8','C8','C9','C10','R9','R10','C11','C12','C13','C14','R11','R12','R13','R14','R15','R16']},
'Controls':{'id':uid('sheet-controls'),'page':'4','title':'End switch and wake / tare button','refs':['J3','SW1','Q1','R17','R18','C15','R19','SW2','R20','R21','C16']}}
# Native global labels on short wires; no purely graphical connection tables.
positions={
'U1':(83.82,71.12),'J1':(254,45.72),'BT1':(342.9,45.72),'C1':(185.42,104.14),'R1':(254,78.74),'R2':(342.9,78.74),'C2':(254,104.14),
'U2':(83.82,167.64),'L1':(83.82,129.54),'D1':(185.42,129.54),'C3':(83.82,208.28),'C4':(185.42,208.28),'R3':(185.42,160.02),'R4':(185.42,182.88),'C5':(185.42,231.14),'R5':(83.82,231.14),
'U3':(304.8,167.64),'C6':(266.7,208.28),'C7':(355.6,208.28),'R6':(304.8,233.68),
'U4':(254,71.12),'J2':(63.5,48.26),'H1':(63.5,86.36),'R7':(137.16,43.18),'R8':(137.16,66.04),'C8':(137.16,91.44),'C9':(43.18,139.7),'C10':(137.16,139.7),'R9':(43.18,177.8),'R10':(137.16,177.8),'C11':(137.16,205.74),
'C12':(233.68,129.54),'C13':(233.68,152.4),'C14':(330.2,129.54),'R11':(233.68,190.5),'R12':(330.2,190.5),'R13':(233.68,215.9),'R14':(330.2,215.9),'R15':(233.68,241.3),'R16':(330.2,241.3),
'J3':(63.5,53.34),'SW1':(63.5,99.06),'Q1':(254,81.28),'R17':(152.4,53.34),'R18':(152.4,81.28),'C15':(152.4,109.22),'R19':(342.9,81.28),'SW2':(63.5,187.96),'R20':(254,187.96),'R21':(152.4,187.96),'C16':(254,215.9)}
def text_s(t,x,y,size=1.6):return f'(text {q(t)} (at {x} {y} 0) {effects(size,"(justify left)")} (uuid {q(uid(t+str(x)+str(y)))}))\n'
def global_s(net,x,y,a=0):
 return f'(global_label {q(net)} (shape input) (at {x} {y} {a}) {effects(.95,"(justify "+("left" if a==0 else "right")+")")} (uuid {q(uid("label"+net+str(x)+str(y)+label_context))}) (property "Intersheetrefs" "${{INTERSHEET_REFS}}" (at {x} {y} {a}) {effects(1,"(hide yes)")}))\n'
for sn,sd in sheets.items():
 label_context=sn
 ss=f'(kicad_sch (version 20250114) (generator "eeschema") (uuid {q(uid("file-"+sn))}) (paper "A3") (title_block (title {q("FINGERWORKER | "+sd["title"])}) (date "2026-09-21") (rev "A / draft") (company "Fingerworker") (comment 1 "Engineering draft - not released for fabrication"))\n(lib_symbols\n'
 for r in sd['refs']:ss+=symbols[r].replace('(symbol "Part_'+r+'"','(symbol "Fingerworker:Part_'+r+'"',1)
 if sn=='Power':ss+=flag.replace('(symbol "PowerFlag"','(symbol "Fingerworker:PowerFlag"',1)
 ss+=')\n'+text_s(sd['title'].upper(),15,17,2.54)
 for r in sd['refs']:
  p=by[r];x,y=positions[r];coords,top=layouts[r];sid=uid('sym-'+r);p['uuid']=sid;p['sheetpath']='/'+rootid+'/'+sd['id']
  ss+=f'(symbol (lib_id "Fingerworker:Part_{r}") (at {x} {y} 0) (unit 1) (in_bom yes) (on_board '+('no' if p['kind']=='external' else 'yes')+f') (dnp no) (uuid {q(sid)})\n'
  ss+=prop('Reference',r,x,y-top-2.54)+prop('Value',p['value'],x,y-top)+prop('Footprint',p.get('footprint',''),x,y,True)+prop('Datasheet',p['source'],x,y,True)+prop('MPN',p['mpn'],x,y,True)
  for n in p['pins']:ss+=f'(pin {q(n)} (uuid {q(uid(r+"pin"+n))}))\n'
  ss+=f'(instances (project {q(NAME)} (path {q(p["sheetpath"])} (reference {q(r)}) (unit 1)))))\n'
  for n,pin in p['pins'].items():
   dx,dy,a=coords[n];px=round(x+dx,4);py=round(y-dy,4)
   if pin['net'] is None:ss+=f'(no_connect (at {px} {py}) (uuid {q(uid(r+"nc"+n))}))\n';continue
   ex=round(px+(-5.08 if a==0 else 5.08),4)
   ss+=f'(wire (pts (xy {px} {py}) (xy {ex} {py})) (stroke (width 0) (type default)) (uuid {q(uid(r+"wire"+n))}))\n'
   ss+=global_s(pin['net'],ex,py,180 if a==0 else 0)
 if sn=='Power':
  for i,net in enumerate(['GND','VBAT','VBOOST']):
   x=38.1+i*73.66;y=261.62;ref='#FLG0'+str(i+1);sid=uid(ref)
   ss+=f'(symbol (lib_id "Fingerworker:PowerFlag") (at {x} {y} 0) (unit 1) (in_bom no) (on_board no) (dnp no) (uuid {q(sid)})'+prop('Reference',ref,x,y-6,True)+prop('Value','PWR_FLAG',x,y-6)+f'(pin "1" (uuid {q(uid(ref+"pin"))})) (instances (project {q(NAME)} (path {q("/"+rootid+"/"+sd["id"])} (reference {q(ref)}) (unit 1)))))'+global_s(net,x,y)
  ss+=text_s('U1 pad 19 = BAT+, pads 18/20 = GND. Charge setting: P0.13 high-Z. P0.14 LOW.',15,282,1.27)
 elif sn=='Acquisition':ss+=text_s('REF_P / REF_N: EXC_SENSE_P/N join V5A/GND only at J2 pads 1/5 and 4/6. Keep inputs away from BOOST_SW.\nPGA=8, 330 SPS, external REF0. Verify sensor common mode and both supply ramps before use.',15,267,1.27)
 else:ss+=text_s('ENDSTOP_N = LOW at endstop OR open cable; HIGH = NC loop closed. Invalid while V5A is off.\nSW1 microload: 5 V / 1 mA. SW2 footprint duplicates pads 1 and 2.\nExternal symbols H1, BT1, SW1 are excluded from the PCB.',15,248,1.27)
 ss+='(embedded_fonts no))\n';(ROOT/f'{sn}.kicad_sch').write_text(ss)
# Root hierarchy, project entry point.
s=f'(kicad_sch (version 20250114) (generator "eeschema") (uuid {q(rootid)}) (paper "A4") (title_block (title "FINGERWORKER | Electronics Rev A") (date "2026-09-21") (rev "A") (comment 1 "Native schematic and routed PCB - PROTOTYPE REVIEW")) (lib_symbols)\n'
s+=text_s('FINGERWORKER',20,22,4)+text_s('BLE force measurement | native KiCad engineering draft',20,32,1.8)
for i,(sn,sd) in enumerate(sheets.items()):
 x=25+i*85;y=60
 s+=f'(sheet (at {x} {y}) (size 70 40) (stroke (width 0.254) (type default)) (fill (color 0 0 0 0.0)) (uuid {q(sd["id"])})'+prop('Sheetname',sn,x,y-2.54)+prop('Sheetfile',sn+'.kicad_sch',x,y+43)+f'(instances (project {q(NAME)} (path {q("/"+rootid)} (page {q(sd["page"])})))))\n'
s+=text_s('32 named nets link the sheets through native global labels.\nPower: XIAO / USB / battery, boost and switched 5 V.\nAcquisition: TE bridge, ratiometric ADS1220 and SPI.\nControls: 5 V end-switch contact and wake/tare button.',25,128,1.6)
s+=text_s('PCB target: 19.5 x 68.5 x 0.8 mm, four copper layers (In1 = GND), top-side assembly.\nSee README.md and reports/ for checks and remaining release gates.\nJST battery polarity must be checked against the physical harness.\nRF, load/supply ramp, noise and 3D enclosure checks remain hardware / mechanical work.',25,158,1.5)
s+='(sheet_instances (path "/" (page "1"))) (embedded_fonts no))\n';(ROOT/f'{NAME}.kicad_sch').write_text(s)
# Project settings. Keep all normal ERC/DRC severities; no excluded violations.
pro=json.loads((LIB/'template/EuroCard160mmX100mm/EuroCard160mmX100mm.kicad_pro').read_text())
pro['meta']['filename']=NAME+'.kicad_pro'
rules=pro['board']['design_settings']['rules'];rules.update({'min_clearance':.15,'min_copper_edge_clearance':.25,'min_track_width':.15,'min_silk_clearance':.1,'min_text_height':.8,'min_text_thickness':.1,'min_hole_clearance':.25,'min_via_diameter':.6,'min_via_annular_width':.15,'min_through_hole_diameter':.3})
pro['board']['design_settings']['rule_severities']['missing_courtyard']='warning'
nc=pro['net_settings']['classes'][0];nc.update({'clearance':.15,'track_width':.2,'via_diameter':.6,'via_drill':.3})
pro['net_settings']['classes'].append(dict(nc,name='Power',track_width=.4,priority=0))
pro['net_settings']['netclass_patterns']=[{'netclass':'Power','pattern':n} for n in ['GND','VBAT','V3V3','VBOOST','V5A','BOOST_SW']]
(ROOT/f'{NAME}.kicad_pro').write_text(json.dumps(pro,indent=2)+'\n')
(ROOT/'native_design.json').write_text(json.dumps({'root_uuid':rootid,'parts':parts,'board_mm':[19.5,68.5,.8],'status':'placement; unrouted'},indent=2)+'\n')
print('Native schematic and local libraries written; next build_pcb.py')
