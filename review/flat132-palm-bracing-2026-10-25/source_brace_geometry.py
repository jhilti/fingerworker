#!/usr/bin/env python3
"""Independent local BRep witness for R9's added P02 stock; not native CAD.

The public brace_stocks/brace_union functions accept the existing frozen audit
geometry helper and its cylinder/union helper, so the validator can reconstruct
the new FeatureScript's explicit CSG without fragile native edge selections.
"""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent


def brace_stocks(b, r7):
    """Return named box/cylinder-CSG stocks in native assembly millimetres."""
    rows = []
    for side in [-1, 1]:
        s = '0' if side == -1 else '1'
        lo_y = -25 if side == -1 else 18
        hi_y = lo_y + 7
        rows.append((f'pad{s}', b.box([-29, lo_y, 14], [-22.75, hi_y, 27])))
        for edge in [0, 1]:
            edge_y = lo_y if edge == 0 else hi_y
            center_y = edge_y - 1.2 if edge == 0 else edge_y + 1.2
            wedge_lo_y = center_y if edge == 0 else edge_y
            wedge_hi_y = edge_y if edge == 0 else center_y
            stock = b.box([-27.1, wedge_lo_y, 14], [-25.8, wedge_hi_y, 27])
            tool = r7.cyl([-25.8, center_y, 13.9], [-25.8, center_y, 27.1], 1.2)
            rows.append((f'side_root{s}{edge}', b.cut(stock, tool)))
        stock = b.box([-27.1, lo_y, 27], [-25.8, hi_y, 28.2])
        tool = r7.cyl([-25.8, lo_y - .1, 28.2], [-25.8, hi_y + .1, 28.2], 1.2)
        rows.append((f'top_root{s}', b.cut(stock, tool)))
    return rows


def brace_union(b, r7):
    return r7.union([shape for _, shape in brace_stocks(b, r7)])


if __name__ == '__main__':
    import json
    sys.path.insert(0, str(HERE.parents[1] / 'review/flat132-adjustable-rear-2026-10-23/validation'))
    import audit_adjustable_rear as r7
    from OCP.BRepCheck import BRepCheck_Analyzer
    from OCP.TopAbs import TopAbs_SOLID
    b = r7.b
    rows = brace_stocks(b, r7)
    print(json.dumps([
        {'stock': name, 'bounds_mm': b.bounds(shape).tolist(),
         'volume_mm3': b.volume(shape), 'solid_count': b.count(shape, TopAbs_SOLID),
         'valid': BRepCheck_Analyzer(shape).IsValid()}
        for name, shape in rows], indent=2))
