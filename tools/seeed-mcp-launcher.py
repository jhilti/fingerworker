"""Upstream Seeed server with a read-only native pcbnew subprocess tool.

macOS KiCad 10.0.6 bundles Python 3.9; Seeed requires 3.10+. Keeping
the interpreters separate avoids modifying KiCad or silently trusting fallback geometry.
"""
import asyncio, json, os
from pathlib import Path
from kicad_mcp_server.server import mcp

@mcp.tool()
async def get_native_pcb_review(file_path: str) -> dict:
    """Get precise native KiCad board, net, pad, zone and decoupling geometry.

    Uses KiCad's bundled Python in a subprocess; does not modify the PCB.
    Lengths are sums of track segments, not point-to-point signal path lengths.
    Decoupling distances are pad-center straight-line distances, not routed lengths.
    Prefer this over upstream text-fallback PCB geometry on this macOS installation.
    """
    path = Path(file_path).resolve(strict=True)
    if path.suffix != '.kicad_pcb':
        raise ValueError('Expected .kicad_pcb')
    proc = await asyncio.create_subprocess_exec(os.environ['KICAD_PYTHON'],
        str(Path(__file__).with_name('native-pcb-review.py')), str(path),
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    out, err = await asyncio.wait_for(proc.communicate(), timeout=60)
    if proc.returncode:
        raise RuntimeError(err.decode())
    return json.loads(out)

mcp.run(show_banner=False)
