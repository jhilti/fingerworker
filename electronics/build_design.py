#!/usr/bin/env python3
"""Fingerworker Rev A: pin-level design, BOM and vector schematic from one source.

This exports review documents, not fabrication data or a simulated circuit.
Run with the Codex bundled Python (reportlab).
"""
from pathlib import Path
from collections import defaultdict
import csv, json, math, hashlib, sys
from xml.etree import ElementTree as ET
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, white
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT = Path(__file__).resolve().parent
OUT = ROOT.parent / 'output' / 'pdf'
OUT.mkdir(parents=True, exist_ok=True)
parts = []

def part(ref, value, mpn, package, pins, page, kind='ic', note='', source=''):
    pins = {str(k): {'name': v[0], 'net': v[1]} for k,v in pins.items()}
    parts.append(dict(ref=ref, value=value, mpn=mpn, package=package, pins=pins,
                      page=page, kind=kind, note=note, source=source))

def passive(ref, value, a, b, page, kind='resistor', spec='0603; 1%; 0.1 W'):
    part(ref,value,'Specification controlled',spec,{1:('1',a),2:('2',b)},page,kind)

SOURCES = {
 'xiao':'https://files.seeedstudio.com/wiki/XIAO-BLE/Res/260828_XIAO_nRF52840.pdf',
 'adc':'https://www.ti.com/lit/ds/symlink/ads1220.pdf',
 'boost':'https://www.ti.com/lit/ds/symlink/tps61041.pdf',
 'ldo':'https://www.ti.com/lit/ds/symlink/tps7a20.pdf',
 'sensor':'https://www.te.com/commerce/DocumentDelivery/DDEController?Action=srchrtrv&DocFormat=pdf&DocLang=English&DocNm=FX19&DocType=Data+Sheet&PartCntxt=FX1901-0001-0200-L',
 'switch':'https://omronfs.omron.com/en_US/ecb/products/pdf/en-ss.pdf',
 'battery':'https://cdn-shop.adafruit.com/product-files/1570/1570datasheet.pdf',
 'jst':'https://www.jst-mfg.com/product/pdf/eng/ePH.pdf',
 'button':'https://industry.panasonic.com/global/en/products/control/switch/light-touch/number/evqpuc02k',
 'mosfet':'https://assets.nexperia.com/documents/data-sheet/2N7002.pdf',
 'diode':'https://www.onsemi.com/pdf/datasheet/mbr0520lt1-d.pdf',
 'inductor':'https://www.coilcraft.com/en-us/products/power/shielded-inductors/molded-inductor/xfl/xfl3012/xfl3012-103/',
}
part('U1','XIAO nRF52840','Seeed 102010448','21 x 17.8 mm module; no headers',{
 1:('D0 / P0.02','BOOST_EN'),2:('D1 / P0.03','ANALOG_EN'),
 3:('D2 / P0.28','ADC_CS_MCU'),4:('D3 / P0.29','ADC_DRDY_N'),
 5:('D4 / P0.04','BUTTON_N'),6:('D5 / P0.05','ENDSTOP_N'),
 7:('D6 / P1.11','USB_PRESENT'),8:('D7 / P1.12',None),
 9:('D8 / P1.13','SPI_SCK_MCU'),10:('D9 / P1.14','SPI_MISO'),
 11:('D10 / P1.15','SPI_MOSI_MCU'),12:('3V3 OUT','V3V3'),
 13:('GND','GND'),14:('VBUS / 5V','VBUS_USB'),
 'BAT+':('bottom BAT+','VBAT'), 'BAT-':('bottom BAT-','GND')},1,
 note='Onboard USB, charger and USB/battery source selection. Check delivered board revision.',source=SOURCES['xiao'])
part('J1','LiPo socket','S2B-PH-SM4-TB(LF)(SN)','JST PH; side-entry SMT',
     {1:('battery +','VBAT'),2:('battery -','GND')},1,'connector',
     note='Design assigns pin 1 positive. Verify pad numbering against actual battery harness before routing.',source=SOURCES['jst'])
part('BT1','Protected 100 mAh LiPo','Adafruit 1570','OFF BOARD; nominal 11.5 x 31 x 3.8 mm',
     {'+':('red +','VBAT'),'-':('black -','GND')},1,'external',
     note='Connect through J1; symbol shows electrical relationship, not a second battery path.',source=SOURCES['battery'])
passive('C1','10 uF','V3V3','GND',1,'capacitor','0805; X5R/X7R; >=16 V; effective >=4.7 uF at 3.3 V')
passive('R1','100 k','VBUS_USB','USB_PRESENT',1)
passive('R2','100 k','USB_PRESENT','GND',1)
passive('C2','10 nF','USB_PRESENT','GND',1,'capacitor','0603; X7R; >=16 V')

part('U2','Boost ~5.43 V','TPS61041DBVR','SOT-23-5 / DBV',
 {1:('SW','BOOST_SW'),2:('GND','GND'),3:('FB','BOOST_FB'),4:('EN','BOOST_EN'),5:('VIN','V3V3')},2,source=SOURCES['boost'])
part('L1','10 uH','XFL3012-103MEC','3 x 3 x 1.2 mm; shielded',
 {1:('1','V3V3'),2:('2','BOOST_SW')},2,'inductor',source=SOURCES['inductor'])
part('D1','Schottky 0.5 A / 20 V','MBR0520LT1G','SOD-123',
 {1:('K','VBOOST'),2:('A','BOOST_SW')},2,'diode',source=SOURCES['diode'])
passive('R3','680 k','VBOOST','BOOST_FB',2,spec='0603; 0.1%; >=0.1 W; thin film')
passive('R4','200 k','BOOST_FB','GND',2,spec='0603; 0.1%; >=0.1 W; thin film')
passive('R5','100 k','BOOST_EN','GND',2)
passive('C3','10 uF','V3V3','GND',2,'capacitor','0805; X5R/X7R; >=16 V; effective >=4.7 uF at 3.3 V')
passive('C4','22 uF','VBOOST','GND',2,'capacitor','0805; X5R/X7R; >=25 V; effective >=4.7 uF at 5.5 V')
passive('C5','47 pF','VBOOST','BOOST_FB',2,'capacitor','0603; C0G; 5%; >=25 V; tune after ripple test')
part('U3','Quiet 5 V / output discharge','TPS7A2050PDBVR','SOT-23-5 / DBV',
 {1:('IN','VBOOST'),2:('GND','GND'),3:('EN','ANALOG_EN'),4:('NC',None),5:('OUT','V5A')},2,source=SOURCES['ldo'])
passive('R6','100 k','ANALOG_EN','GND',2)
passive('C6','1 uF','VBOOST','GND',2,'capacitor','0603; X7R; >=16 V; adjacent to U3')
passive('C7','22 uF','V5A','GND',2,'capacitor','0805; X5R/X7R; >=25 V; effective >=1 uF at 5 V')

part('U4','24-bit ADC / PGA','ADS1220IPWR','TSSOP-16 / PW; 5 x 6.4 mm including leads',
 {1:('SCLK','SPI_SCK_ADC'),2:('CS_N','ADC_CS_N'),3:('CLK','GND'),4:('DGND','GND'),
 5:('AVSS','GND'),6:('AIN3 / REFN1',None),7:('AIN2',None),8:('REFN0','REF_N'),
 9:('REFP0','REF_P'),10:('AIN1','AIN_N'),11:('AIN0 / REFP1','AIN_P'),12:('AVDD','V5A'),
 13:('DVDD','V3V3'),14:('DRDY_N','ADC_DRDY_N'),15:('DOUT','SPI_MISO'),16:('DIN','SPI_MOSI_ADC')},3,source=SOURCES['adc'])
part('J2','Force sensor landing','4 labelled solder pads','PCB pads + printed strain relief',
 {1:('EXC+ red','V5A'),2:('SIG+ yellow','SIG_P'),3:('SIG- white','SIG_N'),4:('EXC- black','GND'),5:('Sense+ internal','EXC_SENSE_P'),6:('Sense- internal','EXC_SENSE_N')},3,'connector',
 note='4-wire connection; Internal net ties join pads 1/5 and 4/6; sense traces reach the excitation solder lands only. Wire colors per TE family sheet.',source=SOURCES['sensor'])
part('H1','Force sensor 200 lbf','FX1901-0001-0200-L','EXISTING / OFF BOARD',
 {'RED':('V+','V5A'),'YELLOW':('O+','SIG_P'),'WHITE':('O-','SIG_N'),'BLACK':('V-','GND')},3,'external',source=SOURCES['sensor'])
passive('R7','1 k','SIG_P','AIN_P',3,spec='0603; 0.1%; matched pair with R8')
passive('R8','1 k','SIG_N','AIN_N',3,spec='0603; 0.1%; matched pair with R7')
passive('C8','470 nF','AIN_P','AIN_N',3,'capacitor','0603; X7R; 10%; >=16 V')
passive('C9','4.7 nF','AIN_P','GND',3,'capacitor','0603; C0G; 5%; >=25 V')
passive('C10','4.7 nF','AIN_N','GND',3,'capacitor','0603; C0G; 5%; >=25 V')
passive('R9','100 R','EXC_SENSE_P','REF_P',3)
passive('R10','100 R','EXC_SENSE_N','REF_N',3)
passive('C11','100 nF','REF_P','REF_N',3,'capacitor','0603; X7R; >=16 V')
passive('C12','100 nF','V5A','GND',3,'capacitor','0603; X7R; >=16 V; at U4.12')
passive('C13','1 uF','V5A','GND',3,'capacitor','0603; X7R; >=16 V; at U4.12')
passive('C14','100 nF','V3V3','GND',3,'capacitor','0603; X7R; >=16 V; at U4.13')
passive('R11','33 R','SPI_SCK_MCU','SPI_SCK_ADC',3)
passive('R12','33 R','SPI_MOSI_MCU','SPI_MOSI_ADC',3)
passive('R13','33 R','ADC_CS_MCU','ADC_CS_N',3)
passive('R14','47 k','V3V3','ADC_CS_N',3)
passive('R15','100 k','SPI_SCK_ADC','GND',3)
passive('R16','100 k','SPI_MOSI_ADC','GND',3)

part('J3','End switch landing','2 labelled solder pads','PCB pads + printed strain relief',
 {1:('NC','END_CONTACT'),2:('COM','GND')},4,'connector')
part('SW1','Existing end switch','Omron SS-01GL2','OFF BOARD / solder terminals',
 {'NC':('NC','END_CONTACT'),'COM':('COM','GND'),'NO':('NO',None)},4,'external',source=SOURCES['switch'])
part('Q1','5 V to 3.3 V sense','2N7002,215','Nexperia SOT-23',
 {1:('G','END_GATE'),2:('S','GND'),3:('D','ENDSTOP_N')},4,'ic',source=SOURCES['mosfet'])
passive('R17','4.7 k','V5A','END_CONTACT',4)
passive('R18','1 k','END_CONTACT','END_GATE',4)
passive('C15','100 nF','END_GATE','GND',4,'capacitor','0603; X7R; >=16 V')
passive('R19','47 k','V3V3','ENDSTOP_N',4)
part('SW2','Wake / tare / sleep','Panasonic EVQPUC02K','4.7 x 4.5 x 1.65 mm; side push',
 {'A':('contact A','BUTTON_RAW'),'B':('contact B','GND')},4,'switch',
 note='Functional contact IDs; physical duplicate contacts and shell mapping to follow official footprint.',source=SOURCES['button'])
passive('R20','100 k','V3V3','BUTTON_N',4)
passive('R21','1 k','BUTTON_RAW','BUTTON_N',4)
passive('C16','100 nF','BUTTON_N','GND',4,'capacitor','0603; X7R; >=16 V')

byref={p['ref']:p for p in parts}
assert len(byref)==len(parts)
nets=defaultdict(list)
for p in parts:
    for pin,v in p['pins'].items():
        if v['net'] is not None: nets[v['net']].append({'ref':p['ref'],'pin':pin,'name':v['name']})
assert all(len(nodes)>=2 for nodes in nets.values()), 'Unintended one-pin net'

# Independent electrical envelope and pin checks, not SPICE/ERC.
assert byref['U4']['pins']['12']['net']=='V5A'
assert byref['U4']['pins']['13']['net']=='V3V3'
assert byref['U4']['pins']['9']['net']=='REF_P'
assert byref['U4']['pins']['8']['net']=='REF_N'
assert byref['Q1']['pins']['3']['net']=='ENDSTOP_N'
assert byref['U1']['pins']['6']['net']=='ENDSTOP_N'
assert not any(n['ref']=='U1' for n in nets['V5A'])
assert {n['ref'] for n in nets['VBAT']}=={'BT1','J1','U1'}
assert byref['U3']['pins']['3']['net']=='ANALOG_EN'
ratio=680e3/200e3
vboost=1.233*(1+ratio)
vboost_min=1.208*(1+ratio*.999/1.001)
vboost_max=1.258*(1+ratio*1.001/.999)
exc=5.0; gain=8; vinmax=exc*(37.8+15)/1000
cmmin=max(exc/4,.2+gain*vinmax/2); cmmax=exc-.2-gain*vinmax/2
fc=[1/(2*math.pi*(rs+2000)*(470e-9+4.7e-9/2)) for rs in [1760,2200,2640]]
bridge=exc/2400*1000
assert vboost_max<6
assert vboost_min>5.075+.145
assert vinmax<(exc-.4)/gain
assert cmmin<2.5<cmmax
assert 5*.985/(4700*1.01)>0.001
checks=dict(status='SCHEMATIC REVIEW DRAFT; no EDA ERC, SPICE, layout or hardware test',
 part_count=len(parts),net_count=len(nets),
 boost_V=dict(nominal=vboost,min_static=vboost_min,max_static=vboost_max),
 max_force_input_V=vinmax,adc_code_range_V=exc/gain,
 pga_max_differential_at_mid_supply_V=(exc-.4)/gain,
 allowed_common_mode_V=[cmmin,cmmax],
 input_RC_Hz=fc,bridge_current_max_mA=bridge,
 end_contact_current_min_mA=5*.985/(4700*1.01)*1000,
 battery_current_budget_mA=[10,20], runtime_hours_with_80mAh=[4,8],
 adc_registers_hex=['06','84','40','00'],
 validations=['All references unique','All non-NC nets have >=2 endpoints',
 'ADC package-specific pin assignment asserted','No 5 V net directly reaches a XIAO GPIO',
 'Only battery socket/module attach to VBAT','LDO headroom DC corner checked',
 'PGA differential and assumed mid-rail common-mode checked','End-contact current >=1mA'],
 outstanding=['Actual TE output common-mode','Battery harness polarity / footprint pad mapping',
 'SW2 contact and shell footprint mapping','Boost ripple / startup and ADC rail ramps',
 'RF keepout and routed board fit','Charge current / termination on delivered XIAO',
 'Physical test and calibration'])
(ROOT/'design.json').write_text(json.dumps(dict(revision='A',date='2026-09-21',parts=parts,nets=nets,sources=SOURCES),indent=2)+'\n')
(ROOT/'validation.json').write_text(json.dumps(checks,indent=2)+'\n')
with (ROOT/'bom.csv').open('w',newline='') as f:
    w=csv.writer(f);w.writerow(['Reference','Qty','Value','Manufacturer part / specification','Package / constraints','Note','Source'])
    for p in parts:w.writerow([p['ref'],1,p['value'],p['mpn'],p['package'],p['note'],p['source']])
with (ROOT/'connections.csv').open('w',newline='') as f:
    w=csv.writer(f);w.writerow(['Net','Reference','Pin','Pin name'])
    for net,nodes in sorted(nets.items()):
        for n in nodes:w.writerow([net,n['ref'],n['pin'],n['name']])

# Portable XML connectivity; intentionally not called a KiCad-ready board netlist.
root=ET.Element('fingerworker_netlist',revision='A')
for name,nodes in sorted(nets.items()):
    net=ET.SubElement(root,'net',name=name)
    for n in nodes:ET.SubElement(net,'node',**n)
ET.indent(root)
ET.ElementTree(root).write(ROOT/'connectivity.xml',encoding='utf-8',xml_declaration=True)

if '--data-only' in sys.argv:
    print('Updated electrical data only; historical PDF left unchanged.')
    raise SystemExit(0)

W,H=1190.55,841.89
ink=HexColor('#142A37'); teal=HexColor('#087F8C'); muted=HexColor('#536672'); light=HexColor('#E9F2F4'); line=HexColor('#B7C9D1')
pdf=canvas.Canvas(str(OUT/'Fingerworker_Elektronik_RevA.pdf'),pagesize=(W,H))
pdfmetrics.registerFont(TTFont('FW-Regular','/System/Library/Fonts/Supplemental/Arial.ttf'))
pdfmetrics.registerFont(TTFont('FW-Bold','/System/Library/Fonts/Supplemental/Arial Bold.ttf'))
pdf.setTitle('Fingerworker - Elektronik Rev A - Schaltungsentwurf')
pdf.setAuthor('Fingerworker development')
drawn=set()
def text(x,y,s,size=11,bold=False,color=ink):
    pdf.setFillColor(color);pdf.setFont('FW-Bold' if bold else 'FW-Regular',size);pdf.drawString(x,H-y,s)
def rect(x,y,w,h,fill=None):
    pdf.setStrokeColor(line);pdf.setLineWidth(.7);pdf.setFillColor(fill or white);pdf.rect(x,H-y-h,w,h,stroke=1,fill=1)
def ln(x,y,x2,y2,col=teal):
    pdf.setStrokeColor(col);pdf.setLineWidth(1);pdf.line(x,H-y,x2,H-y2)
def page(n,title,subtitle):
    rect(0,0,W,85,ink);text(36,30,'FINGERWORKER / ELECTRONICS',10,True,HexColor('#7AD1D8'))
    text(36,61,title,24,True,white);text(36,109,subtitle,11,color=muted)
    ln(36,790,W-36,790,line)
    text(36,812,'REV A / 20.09.2026 / ENTWURF ZUR PRUEFUNG - KEINE FERTIGUNGSFREIGABE',9,color=muted)
    text(W-150,812,f'{n} / 5',10,True)
def note(x,y,lines):
    for i,s in enumerate(lines):text(x,y+i*17,s,10,color=muted)
def ic(ref,x,y,w=485):
    p=byref[ref]; drawn.add(ref);h=60+len(p['pins'])*19
    rect(x,y,w,h);text(x+14,y+23,ref+'  '+p['value'],13,True)
    text(x+14,y+42,p['mpn'],10,color=muted)
    for i,(pin,v) in enumerate(p['pins'].items()):
        yy=y+65+i*19
        text(x+14,yy,str(pin),9,True);text(x+70,yy,v['name'],10)
        ln(x+w-170,yy-4,x+w-155,yy-4)
        text(x+w-150,yy,v['net'] or 'NC (offen)',10,True,teal if v['net'] else muted)
    return y+h
def item(ref,x,y,w=485):
    p=byref[ref];drawn.add(ref)
    pins=list(p['pins'].items()); (p1,v1),(p2,v2)=pins
    text(x,y,p['ref']+'  '+p['value'],10,True)
    text(x,y+17,v1['net'],9,color=teal)
    text(x+w-150,y+17,v2['net'],9,color=teal)
    mid=x+w/2; yy=y+13
    ln(mid-47,yy,mid-14,yy);ln(mid+14,yy,mid+47,yy)
    if p['kind']=='capacitor':
        ln(mid-3,yy-7,mid-3,yy+7);ln(mid+3,yy-7,mid+3,yy+7)
        ln(mid-14,yy,mid-3,yy);ln(mid+3,yy,mid+14,yy)
    elif p['kind']=='inductor':
        pdf.setStrokeColor(teal)
        for j in range(4):
            pdf.arc(mid-14+j*7,H-yy-3.5,mid-7+j*7,H-yy+3.5,0,180)
    elif p['kind']=='diode':
        ln(mid-8,yy-7,mid-8,yy+7)
        path=pdf.beginPath();path.moveTo(mid+9,H-yy+7);path.lineTo(mid+9,H-yy-7);path.lineTo(mid-8,H-yy);path.close()
        pdf.setStrokeColor(teal);pdf.drawPath(path,stroke=1,fill=0)
        ln(mid-14,yy,mid-8,yy);ln(mid+9,yy,mid+14,yy)
    else: rect(mid-14,yy-5,28,10)
    text(mid-54,yy-5,p1,7,color=muted);text(mid+49,yy-5,p2,7,color=muted)

page(1,'Controller, USB und Akku','Gleiche Netznamen sind elektrisch verbunden. Pinbelegung nach der Herstellerzeichnung; NC bleibt offen.')
ic('U1',36,139,528)
ic('J1',630,139,524);ic('BT1',630,252,524)
for i,r in enumerate(['C1','R1','R2','C2']):item(r,646,379+i*46,500)
note(36,542,[
 'USB-C und BQ25101 bleiben auf dem XIAO. Keine zweite Ladeschaltung.',
 'VBAT ist nur Akku/Lader. Alle zusaetzlichen Verbraucher starten an V3V3.',
 'Der XIAO waehlt intern USB oder Akku vor seinem 3,3-V-Regler.',
 'P0.13: Eingang ohne Pull-up/-down fuer nominal 50 mA Ladestrom.',
 'P0.14: frueh auf LOW setzen; Batteriemessung intern an P0.31.',
 'Nicht HIGH setzen: siehe Warnhinweis und Teiler im Seeed-Schaltplan.',
 'Der Seitentaster (Blatt 4) weckt das Geraet und aktiviert Standby.',
 'Standby trennt den Messzweig; vollstaendige Trennung durch Abstecken des Akkus.'])
note(630,595,[
 'J1-Polaritaet ist eine Designzuordnung, keine universelle JST-Norm.',
 'Vor PCB-Routing: Originalakku, Pin-1-Markierung und Footprint abgleichen.',
 'Akku mit Schutzschaltung; 4,2-V-Ladung, keine ungeschuetzte Ersatzzelle.',
 'Der XIAO ueberwacht keine Zelltemperatur (TS mit Festwiderstand).',
 'Ladetest am Muster bei zulaessiger Zelltemperatur; 50 mA verifizieren.',
 '100 mA per GPIO wird in dieser Revision nicht verwendet.'])
pdf.showPage()

page(2,'Schaltbare, ruhige Sensorversorgung','V3V3 -> TPS61041 -> ca. 5,43 V -> TPS7A2050 -> V5A. Gemeinsame Masse, kurze Schaltstromschleife.')
ic('U2',36,142,520);ic('U3',635,142,520)
for i,r in enumerate(['L1','D1','R3','R4','C5']):item(r,45,329+i*48,495)
for i,r in enumerate(['R5','R6','C3','C4','C6','C7']):item(r,648,329+i*48,490)
note(36,604,[
 'R3/R4: 680 k / 200 k, jeweils 0,1%. Sollwert 1,233 x (1 + 3,4).',
 f'DC-Eckwerte aus Referenz + Widerstaenden: {vboost_min:.3f} bis {vboost_max:.3f} V.',
 'Keine Aussage ueber Ripple, Lastspruenge oder Einschaltueberschwingen.',
 'C5: 47 pF Startwert; 10/22/47/100 pF am Muster auf Ripple abstimmen.',
 'C3 direkt bei U2.5; C4 am Diodenausgang; C6 direkt bei U3.1.',
 'L1 >=0,5 A Saettigungsgrenze; D1-Kathode an VBOOST.'])
note(635,644,[
 'BOOST_EN zuerst HIGH; nach 10 ms ANALOG_EN HIGH (Startwert).',
 'V5A stabil abwarten, ADC resetten, Register schreiben und zuruecklesen.',
 'Ausschalten: ADC POWERDOWN, CS HIGH, ANALOG_EN LOW, BOOST_EN LOW.',
 'U2 allein trennt den Eingang NICHT galvanisch vom Ausgang.',
 'U3 sperrt den Messzweig und entlaedt V5A im ausgeschalteten Zustand.',
 'AVDD/DVDD-Anstiege am Oszilloskop gegen ADS1220-Rampenregel pruefen.'])
pdf.showPage()

page(3,'Kraftsignal und Messwandler','Ratiometrisch: Sensorversorgung und Referenz vom selben EXC-Anschlusspunkt. 3,3-V-SPI, 5-V-Analogversorgung.')
ic('U4',36,140,525)
ic('J2',36,530,525)
drawn.add('H1')
text(36,699,'H1  TE FX1901-0001-0200-L (vorhanden)',12,True)
note(36,723,['RED / V+ -> J2.1; YELLOW / O+ -> J2.2',
             'WHITE / O- -> J2.3; BLACK / V- -> J2.4',
             'R7/R8 und C8-C10 direkt am ADC; R9/R10 am EXC-Anschlusspunkt.'])
for i,r in enumerate(['R7','R8','C8','C9','C10','R9','R10','C11','C12','C13','C14','R11','R12','R13','R14','R15','R16']):
    item(r,648,144+i*35,495)
pdf.showPage()

page(4,'Endschalter und Bedienung','Der vorhandene Omron bekommt nominal 5 V / 1 mA Kontaktlast. Q1 trennt den 5-V-Pegel vom Controller.')
ic('Q1',36,140,525);ic('J3',36,277,525);ic('SW1',36,398,525)
for i,r in enumerate(['R17','R18','C15','R19']):item(r,651,150+i*48,490)
ic('SW2',635,385,520)
for i,r in enumerate(['R20','R21','C16']):item(r,648,511+i*45,490)
note(36,548,[
 'SW1: COM an GND, NC an J3.1, NO isoliert offen lassen.',
 'Unbetaetigt: NC geschlossen, END_CONTACT LOW, ENDSTOP_N HIGH.',
 'Betaetigt oder Draht offen: END_CONTACT HIGH, ENDSTOP_N LOW.',
 'Bei abgeschalteter V5A ist der Endlagenwert ungueltig.',
 'R17 ergibt selbst bei 4,925 V und +1% R mindestens 1,038 mA.',
 '5-10 ms Softwareentprellung; Signal mit geraeteseitigem Zeitstempel.',
 'Drahtbruch wirkt wie Endlage; Kurzschluss nach GND nicht erkennbar.'])
note(635,680,[
 'SW2 seitlich zugaenglich; kurz = Tarieren, lang = Standby, Druck = Wecken.',
 'Vor System-OFF Loslassen abwarten, damit LOW-Wakeup nicht sofort ausloest.',
 'Tasterkontakt A/B funktional: doppelte Pads und Schirm im Footprint zuordnen.',
 'Schalter ist ein Ereignissignal; er misst keinen kontinuierlichen Weg.'])
pdf.showPage()

page(5,'Auslegung und Inbetriebnahme','Pruefbarer Entwurf fuer den ersten Tischaufbau. Platinenrouting und Bauraumnachweis mit echten Footprints folgen.')
text(36,150,'MESSBEREICH',13,True,teal)
note(36,178,[
 'TE 200 lbf: (37,8 + 15) mV/V x 5 V = 264 mV Maximalsignal inkl. Offset.',
 'ADC-Codebereich bei Gain 8 / 5 V: +/-625 mV.',
 'PGA-Hub bei mittigem Gleichtakt enger: maximal +/-575 mV.',
 'Fuer 264 mV muss der Eingangsgleichtakt 1,256 bis 3,744 V betragen.',
 '2,5 V liegt darin; echten Sensor-Gleichtakt vor Verstaerkung 8 messen.',
 'RC mit Sensor-Ausgangswiderstand: Eckfrequenz ca. 73-90 Hz.',
 'Das ist ein Vorfilter; die spaetere Anzeige bekommt einen digitalen Tiefpass.'])
text(635,150,'FIRMWARE-STARTWERTE',13,True,teal)
note(635,178,[
 'SPI Mode 1, MSB zuerst, zum Start 1 MHz, separater DRDY-Interrupt.',
 'ADS1220 Register 00..03: 06 84 40 00 (hex).',
 'AIN0-AIN1, PGA 8, normal, kontinuierlich, 330 SPS, externe REF0.',
 'IDAC, Burnout und interner Low-Side-Schalter ausgeschaltet.',
 'Startsequenz: RESET -> WREG -> RREG pruefen -> START/SYNC.',
 'BLE: Sequenznummer, Mikrosekunden-Zeit, Rohwert, Newton, Endlage, Batterie.',
 '25-Hz-Anzeige und gepufferte Rohdaten; Paketformat vor App-Implementierung fixieren.'])
text(36,335,'ENERGIE UND LADEN',13,True,teal)
note(36,363,[
 'Bruecke: 1,39-2,08 mA bei 5 V; ADC analog grob 0,4-0,7 mA als Budget.',
 'Zusaetzlich Funk/CPU, Reglerverluste und zeitweise Endkontaktlast.',
 'Gesamtansatz am Akku: 10-20 mA, kein gemessener Verbrauch.',
 'Mit 80 mAh nutzbarer Reserve aus 100 mAh: ungefaehr 4-8 Stunden aktiv.',
 'Standby-Ziel <100 uA; kompletter Aufbau inklusive Modul muss gemessen werden.',
 '50-mA-Ladung: mindestens 2 h plus CV-Phase; kein zugesicherter Ladetermin.',
 'USB-Stecken/-Ziehen, BLE-Spitzen und leeren Akku gemeinsam testen.'])
text(635,335,'FLACHER EINBAU',13,True,teal)
note(635,363,[
 'Ziel: 19 x 68,5 mm Traeger, 0,8 mm PCB. Noch nicht geroutet.',
 'XIAO ohne Stiftleisten, TSSOP/SOT-23, 0603/0805-Passive nebeneinander.',
 'JST samt Stecker/Kabel braucht mehr als den bisherigen 8 x 6-mm-Platzhalter.',
 'Vorlaeufig 10 x 12 x 5,5 mm Montagebudget; Bestandshuellen nicht freigegeben.',
 'Antennen-Kupferfreiraum nach Moduldesign, keine Sensorleitung ueber SW-Knoten.',
 'Sensor- und Schalterdraht an beschriftete Pads mit separater Zugentlastung.',
 'Akku isoliert und ohne Last der Handballenplatte lagern.'])
text(36,520,'ABNAHME AM MUSTER',13,True,teal)
note(36,548,[
 '1  Ohne Akku an strombegrenzter Versorgung: 3,3 V, VBOOST, V5A und Rampen.',
 '2  Null-/Volllastsimulator, Rohdaten, Sensor-Gleichtakt und korrekte Kraftpolaritaet.',
 '3  Mechanik mit bekannten Kraeften kalibrieren; Hysterese bei Be-/Entlastung.',
 '4  Endschalter, Taster, Schlafstrom, BLE-Aussetzer und Datenzeitstempel.',
 '5  Akku/Laden: Polaritaet, 50 mA, Ladeende, Temperatur und USB-Umschaltung.',
 '6  Erst danach PCB-Routing, reale 3D-Huellen und gedruckte Halterung freigeben.'])
text(635,520,'QUELLEN / EDITIERBARE DATEN',13,True,teal)
note(635,548,[
 'Hersteller: Seeed XIAO-Schaltplan v1.2; TI ADS1220, TPS61041, TPS7A20;',
 'TE FX1901; Omron SS; Panasonic EVQPU; Nexperia 2N7002; JST PH;',
 'Coilcraft XFL3012; onsemi MBR0520; Adafruit / PKCELL 1570.',
 'Direktlinks und lokale Datenblaetter: electronics/README.md und vendor/.',
 'Vollstaendige Stueckliste: electronics/bom.csv.',
 'Pin-/Netzquelle: electronics/design.json und connections.csv.',
 'Rechenpruefungen: electronics/validation.json; keine EDA-ERC oder Simulation.'])
pdf.showPage();pdf.save()
assert drawn==set(byref), (set(byref)-drawn,drawn-set(byref))
print(json.dumps(checks,indent=2))
