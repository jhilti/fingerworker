#!/usr/bin/env python3
"""Exact local BRep preflight of integral P07 lands; not native CAD proof."""
from pathlib import Path
import hashlib
import json
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
R10 = ROOT / 'review/flat132-integrated-palm-2026-11-03'
sys.path.insert(0, str(R10 / 'validation'))
import audit_native as previous
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.TopAbs import TopAbs_SOLID, TopAbs_SHELL
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.StlAPI import StlAPI_Writer

b = previous.b
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def expected(old):
    """Exact desired solid identity, suitable for the final native validator."""
    return {'P120': previous.r7.union([old['P120'], old['P070a'], old['P070b']]),
            'P121': previous.r7.union([old['P121'], old['P071a'], old['P071b']])}


def main():
    inv = json.loads((R10 / 'validation/native-step-inventory.json').read_text())
    assert sha(inv['native_step']) == inv['native_step_sha256']
    shapes, _, _ = b.read_step(Path(inv['native_step']))
    parts = {r: shapes[row['candidates'][0]['solid_index']]
             for r, row in inv['native_part_correspondence'].items()}
    rows = []
    for side, y in [(0, -51), (1, 51)]:
        ref = 'P12' + str(side)
        desired = parts[ref]
        candidate = parts[ref]
        for suffix, py in [('a', y-7.5), ('b', y+7.5)]:
            desired = b.fuse(desired, parts[f'P07{side}{suffix}'])
            candidate = b.fuse(candidate, b.box([119, py-2.25, 14], [120.7, py+2.25, 20]))
        difference = b.xor_volume(candidate, desired)
        extra = b.volume(candidate)-b.volume(parts[ref])
        rows.append({'ref': ref, 'status': 'PASS' if difference < 1e-6
                     and abs(extra-81) < 1e-6 and BRepCheck_Analyzer(candidate).IsValid()
                     and b.count(candidate, TopAbs_SOLID) == b.count(candidate, TopAbs_SHELL) == 1 else 'FAIL',
                     'symmetric_difference_from_old_shoe_plus_old_pads_mm3': difference,
                     'volume_increase_mm3': extra, 'one_solid': b.count(candidate, TopAbs_SOLID) == 1,
                     'bounds_mm': b.bounds(candidate).tolist(), 'front_x_mm': 119,
                     'moving_assembly_common_x_shift_mm': [0, -2]})
        output = HERE / 'local-preflight-meshes'
        output.mkdir(exist_ok=True)
        BRepMesh_IncrementalMesh(candidate, 0.03, False, 0.15, True).Perform()
        writer = StlAPI_Writer(); writer.ASCIIMode = False
        assert writer.Write(candidate, str(output / (ref + '.stl')))
    report = {'status': 'PASS_LOCAL_EXACT_CSG_PREFLIGHT' if all(r['status']=='PASS' for r in rows) else 'FAIL',
              'baseline_step_sha256': inv['native_step_sha256'], 'checks': rows,
              'meaning': 'The union has exactly the old shoe+pad geometry, so prior motion clearances remain nominally unchanged. Positive Boolean overlap only lies inside old shoe stock.',
              'all_rear_advance_values': {'a_mm': [0, 2], 'method': 'Exact set identity commutes with the common translation T(-a). No sampling of a is needed.',
                 'integral_contact_plane_x_mm': '119-a', 'carriage_rear_plane_x_mm': '124-(5+a+u)=119-a-u',
                 'separation_along_x_mm': 'u >= 0, nominal exterior contact at u=0'},
              'limitations': 'This local CSG witness does not regenerate Onshape, certify a native export, test a print, or qualify hard-land impact/creep strength.'}
    (HERE / 'rear-shoes-geometry-preflight.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
