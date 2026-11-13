"""Validate the JLC review evidence against its exact source and portal BOM."""
import json, csv, hashlib, xml.etree.ElementTree as ET
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
BASE=ROOT/'electronics/kicad/reports/seeed-review-2026-10-11'
SOURCE=ROOT/'electronics/order/RevA-P1-JLC/source'
INPUTS=[*SOURCE.glob('*.kicad_sch'),*SOURCE.glob('*.kicad_pro'),*SOURCE.glob('*.kicad_pcb'),SOURCE/'native_design.json',
        ROOT/'electronics/order/RevA-P1-JLC/upload/BOM_JLC_portal.csv',ROOT/'electronics/order/RevA-P1-JLC/upload/CPL_JLC_portal.csv']
def hashes():return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in INPUTS}
before=hashes()
parts=json.loads((SOURCE/'native_design.json').read_text())['parts']
expected={(c['ref'],str(pin)):v['net'] for c in parts for pin,v in c['pins'].items()}
actual={};errors=[]
for net in ET.parse(BASE/'order/netlist.xml').findall('./nets/net'):
    for node in net.findall('node'):
        key=(node.attrib['ref'],node.attrib['pin'])
        if key in actual:errors.append(['duplicate',key])
        actual[key]=net.attrib['name'].lstrip('/')
for key in sorted(set(expected)|set(actual)):
    want=expected.get(key);got=actual.get(key)
    if not (key in expected and ((want is not None and got==want) or (want is None and (got is None or got.startswith('unconnected-'))))):errors.append([key,want,got])
b=json.loads((BASE/'order/native-pcb.json').read_text())
assert b['sha256']==before['electronics/order/RevA-P1-JLC/source/Fingerworker_RevA.kicad_pcb']
board_parts={c['ref']:c for c in parts if c.get('footprint')}
assert set(b['footprints'])==set(board_parts)
for ref,fp in b['footprints'].items():
    for pin,pad in fp['pads'].items():
        if not pin:continue # unnumbered NPTH / mechanical pads
        key=(ref,pin);net=pad['net'].lstrip('/')
        if key==('J1','MP') and not net:continue # verified JST solder anchors
        want=expected.get(key)
        if key not in expected or (want and net!=want) or (want is None and net and not net.startswith('unconnected-')):errors.append(['pad',key,want,net])
    for pin,pad in board_parts[ref]['pins'].items():
        if pad['net'] and pin not in fp['pads']:errors.append(['missing_pad',ref,pin])
rows=list(csv.DictReader((ROOT/'electronics/order/RevA-P1-JLC/upload/BOM_JLC_portal.csv').open()))
refs=[ref.strip() for row in rows for ref in row['Designator'].split(',')]
assert set(refs)==set(b['footprints'])-{'J2','J3'} and len(refs)==len(set(refs))
assert not errors,errors
erc=json.loads((BASE/'order/erc.json').read_text())
drc=json.loads((BASE/'order/drc.json').read_text())
assert not erc.get('violations',[]) and not any(s.get('violations',[]) for s in erc.get('sheets',[]))
assert not any(drc.get(k,[]) for k in ['violations','unconnected_items','schematic_parity'])
assert before==hashes(),'Input changed during review'
report={'status':'PASS: order ERC/DRC, strict pin and pad parity, BOM references',
        'connected_pins_checked':sum(v is not None for v in expected.values()),'unused_pins_checked':sum(v is None for v in expected.values()),
        'bom_groups':len(rows),'bom_references':len(refs),'sha256':before,'mismatches':errors}
(BASE/'order/parity-and-bom.json').write_text(json.dumps(report,indent=2)+'\n')
print(report['status'],report['connected_pins_checked'],report['unused_pins_checked'],len(rows),len(refs))
