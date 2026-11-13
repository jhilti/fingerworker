"""Run real MCP stdio calls; preserve tool schemas and raw review evidence."""
import asyncio, json, hashlib, subprocess
from pathlib import Path
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'electronics/kicad/reports/seeed-review-2026-10-11'
OUT.mkdir(parents=True, exist_ok=True)
CAD = ROOT / 'electronics/kicad'

async def main():
    params = StdioServerParameters(command='/bin/bash', args=[str(ROOT/'tools/run-kicad-mcp.sh')])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            init = await session.initialize()
            catalog = await session.list_tools()
            (OUT/'tools.json').write_text(catalog.model_dump_json(indent=2))
            evidence = {'server': init.model_dump(mode='json'), 'upstream_commit': subprocess.check_output(['git','-C',str(ROOT/'tools/kicad-mcp-server'),'rev-parse','HEAD'],text=True).strip(), 'calls': []}
            calls = [
                ('get_schematic_info', {'file_path':str(CAD/'Fingerworker_RevA.kicad_sch')}),
                ('run_erc', {'schematic_path':str(CAD/'Fingerworker_RevA.kicad_sch')}),
                ('run_drc', {'pcb_path':str(CAD/'Fingerworker_RevA.kicad_pcb')}),
                ('generate_netlist', {'schematic_path':str(CAD/'Fingerworker_RevA.kicad_sch')}),
                ('get_netlist_components', {'netlist_path':str(CAD/'reports/full-review-netlist.xml')}),
                ('get_netlist_nets', {'netlist_path':str(CAD/'reports/full-review-netlist.xml')}),
                ('get_pcb_statistics', {'file_path':str(CAD/'Fingerworker_RevA.kicad_pcb')}),
                ('list_pcb_footprints', {'file_path':str(CAD/'Fingerworker_RevA.kicad_pcb')}),
                ('analyze_pcb_nets', {'file_path':str(CAD/'Fingerworker_RevA.kicad_pcb')}),
                ('analyze_pcb_signal_integrity', {'file_path':str(CAD/'Fingerworker_RevA.kicad_pcb')}),
                ('analyze_pcb_power_integrity', {'file_path':str(CAD/'Fingerworker_RevA.kicad_pcb')}),
                ('get_native_pcb_review', {'file_path':str(CAD/'Fingerworker_RevA.kicad_pcb')}),
            ]
            for ref in ['U1','U2','U3','U4','Q1','J2','J3']:
                calls.append(('trace_netlist_connection',{'netlist_path':str(CAD/'reports/full-review-netlist.xml'),'reference':ref}))
            for tool, args in calls:
                try:
                    result = await session.call_tool(tool, args)
                    data = result.model_dump(mode='json')
                except Exception as error:
                    data = {'exception':repr(error)}
                item = {'tool':tool,'arguments':args,'result':data}
                evidence['calls'].append(item)
                label = tool + ('-'+args['reference'] if 'reference' in args else '')
                (OUT/(label+'.json')).write_text(json.dumps(item,indent=2))
                print(label, 'ERROR' if data.get('isError') or data.get('exception') else 'returned', flush=True)
                (OUT/'mcp-evidence.json').write_text(json.dumps(evidence,indent=2))
                for block in data.get('content', []):
                    if block.get('text', '').startswith(('Error', '❌', '⚠️ Automatic')):
                        raise RuntimeError(f"{label}: {block['text']}")
                if data.get('isError') or data.get('exception'):
                    raise RuntimeError(f'MCP call failed: {label}')

asyncio.run(main())
