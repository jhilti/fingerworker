"""Regression guard: real KiCad 10 ERC schema must not produce false PASS."""
import json,tempfile
from pathlib import Path
from kicad_mcp_server.tools.validation import _parse_erc_report, _parse_drc_report
ROOT=Path(__file__).resolve().parent.parent
base=json.loads((ROOT/'electronics/kicad/reports/erc-full-review.json').read_text())
v={'severity':'error','type':'pin_not_connected','description':'Review regression sentinel','items':[]}
with tempfile.TemporaryDirectory() as temp:
    p=Path(temp)/'erc.json'
    base['sheets'][0]['violations']=[v];p.write_text(json.dumps(base))
    assert len(_parse_erc_report(p))==1,'Nested ERC violations silently lost'
    p.write_text(json.dumps({'violations':[v]}));assert len(_parse_erc_report(p))==1
    p.write_text(json.dumps({'violations':[],'unconnected_items':[v],'schematic_parity':[v]}));assert len(_parse_drc_report(p))==2
import asyncio
from kicad_mcp_server.tools.netlist import trace_netlist_connection
text=asyncio.run(trace_netlist_connection(str(ROOT/'electronics/kicad/reports/full-review-netlist.xml'),'U1'))
assert not text.startswith('❌'),text
assert '**Pins:** 13, 18, 20' in text,text
print('PASS: nested/flat ERC, open/parity DRC, and multi-pin GND net tracing')
