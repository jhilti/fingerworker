#!/usr/bin/env python3
"""Fresh native ERC/DRC/netlist verification, bound to unchanged input hashes.
Run with KiCad's bundled Python (pcbnew). This never edits the design.
"""
from pathlib import Path
from datetime import datetime, timezone
import os, json, xml.etree.ElementTree as ET, collections, hashlib, subprocess
R=Path(__file__).resolve().parent
os.environ['KICAD_CONFIG_HOME']=str(R/'.config')
import pcbnew as p
CLI=os.environ.get('KICAD_CLI','/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli')
reports=R/'reports'; reports.mkdir(exist_ok=True)
summary=reports/'verification-summary.json'
# A failed run must not leave a previous PASS report under the current filename.
summary.write_text(json.dumps({'status':'RUNNING; no current result','manufacturing_release':False})+'\n')
def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def input_hashes():
    files=[*R.glob('*.kicad_sch'),*R.glob('*.kicad_pcb'),*R.glob('*.kicad_pro'),*R.glob('*.kicad_dru'),*R.glob('*.kicad_sym'),*R.glob('*.pretty/*.kicad_mod'),R/'native_design.json',R/'sym-lib-table',R/'fp-lib-table']
    return {str(x.relative_to(R)):digest(x) for x in sorted(set(files)) if x.exists()}
before=input_hashes(); commands=[]
for args in [
 ['sch','erc','--exit-code-violations','--format','json','--output',str(reports/'erc-full-review.json'),str(R/'Fingerworker_RevA.kicad_sch')],
 ['pcb','drc','--exit-code-violations','--format','json','--output',str(reports/'drc-full-review.json'),'--schematic-parity',str(R/'Fingerworker_RevA.kicad_pcb')],
 ['sch','export','netlist','--format','kicadxml','--output',str(reports/'full-review-netlist.xml'),str(R/'Fingerworker_RevA.kicad_sch')],
]:
    result=subprocess.run([CLI,*args],capture_output=True,text=True)
    commands.append({'args':args,'returncode':result.returncode,'stdout':result.stdout,'stderr':result.stderr})
    (reports/'verification-commands.json').write_text(json.dumps(commands,indent=2)+'\n')
    if result.returncode: raise RuntimeError(f'Native verification failed: {args[:2]} (see verification-commands.json)')
assert before==input_hashes(),'Design changed during verification; run again'
src=json.loads((R/'native_design.json').read_text())
expected={(c['ref'],str(pin)):v['net'] for c in src['parts'] for pin,v in c['pins'].items()}
actual={}; duplicate_nodes=[]
for net in ET.parse(reports/'full-review-netlist.xml').findall('./nets/net'):
    name=net.attrib['name'].lstrip('/')
    for node in net.findall('node'):
        key=(node.attrib['ref'],node.attrib['pin'])
        if key in actual: duplicate_nodes.append(key)
        actual[key]=name
mismatches=[]
for key in sorted(set(expected)|set(actual)):
    want=expected.get(key); got=actual.get(key)
    # Only explicitly unused design pins may occupy KiCad's isolated NC nets.
    valid=key in expected and ((want is not None and got==want) or (want is None and (got is None or got.startswith('unconnected-'))))
    if not valid: mismatches.append({'pin':list(key),'expected':want,'actual':got})
b=p.LoadBoard(str(R/'Fingerworker_RevA.kicad_pcb')); board_mismatches=[]
board_parts={c['ref']:c for c in src['parts'] if c.get('footprint')}
seen=set()
for fp in b.GetFootprints():
    ref=fp.GetReference(); seen.add(ref)
    if ref not in board_parts: board_mismatches.append({'unexpected_footprint':ref}); continue
    pads={}
    for pad in fp.Pads():
        if not pad.GetNumber(): continue # unnumbered NPTH/mechanical pads
        key=(ref,pad.GetNumber()); got=pad.GetNetname().lstrip('/'); want=expected.get(key)
        # The JST footprint has two isolated solder anchors marked MP.
        if key==('J1','MP') and str(fp.GetFPID().GetLibItemName())=='JST_PH_S2B-PH-SM4-TB_1x02-1MP_P2.00mm_Horizontal' and not got: continue
        pads[pad.GetNumber()]=got
        if key not in expected or (want and want!=got) or (want is None and got and not got.startswith('unconnected-')):
            board_mismatches.append({'pin':list(key),'expected':want,'actual':got})
    for pin,v in board_parts[ref]['pins'].items():
        if v['net'] and pin not in pads: board_mismatches.append({'missing_pad':[ref,pin]})
for ref in board_parts.keys()-seen: board_mismatches.append({'missing_footprint':ref})
drc=json.loads((reports/'drc-full-review.json').read_text()); erc=json.loads((reports/'erc-full-review.json').read_text())
tracks=list(b.GetTracks()); vias=[t for t in tracks if isinstance(t,p.PCB_VIA)]; traces=[t for t in tracks if not isinstance(t,p.PCB_VIA)]
planes=[{'name':z.GetZoneName(),'layer':b.GetLayerName(z.GetLayer()),'net':z.GetNetname(),'filled_islands':z.GetFilledPolysList(z.GetLayer()).OutlineCount()} for z in b.Zones() if not z.GetIsRuleArea()]
report={'status':'PASS: fresh native ERC/DRC and strict pin parity','native_connected_pins_checked':sum(v is not None for v in expected.values()),'explicit_unused_pins_checked':sum(v is None for v in expected.values()),'connectivity_mismatches':mismatches,'pcb_pad_mismatches':board_mismatches,'duplicate_netlist_nodes':duplicate_nodes,'erc_violations':sum(len(s.get('violations',[])) for s in erc['sheets']),'pcb_geometry_violations':len(drc['violations']),'schematic_parity_issues':len(drc['schematic_parity']),'unrouted_connections':len(drc['unconnected_items']),'manufacturing_release':False,'board_mm':[19.5,68.5,p.ToMM(b.GetDesignSettings().GetBoardThickness())],'copper_layers':b.GetCopperLayerCount(),'tracks_by_layer':dict(collections.Counter(b.GetLayerName(t.GetLayer()) for t in traces)),'via_count':len(vias),'via_diameters_drills_mm':sorted(set((p.ToMM(t.GetWidth(p.F_Cu)),p.ToMM(t.GetDrill())) for t in vias)),'planes':planes,'antenna_keepouts_layers':[list(z.GetLayerSet().CuStack()) for z in b.Zones() if z.GetIsRuleArea()],'checked_at':datetime.now(timezone.utc).isoformat(),'kicad_version':subprocess.check_output([CLI,'version'],text=True).strip(),'input_sha256':before,'pcb_sha256':before['Fingerworker_RevA.kicad_pcb'],'report_sha256':{x:digest(reports/x) for x in ['erc-full-review.json','drc-full-review.json','full-review-netlist.xml','verification-commands.json']}}
assert not mismatches and not board_mismatches and not duplicate_nodes,report
assert report['erc_violations']==0 and not drc['violations'] and not drc['unconnected_items'] and not drc['schematic_parity'],report
assert report['tracks_by_layer'].get('In1.Cu',0)==0,'Dedicated GND layer contains tracks'
assert before==input_hashes(),'Design changed during verification'
summary.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ['input_sha256','report_sha256']},indent=2))
