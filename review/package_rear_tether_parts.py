#!/usr/bin/env python3
"""Package the fresh rear-tether Onshape export without scaling or mesh repair.

Validate all eleven printable parts before writing the development print pack.
Only rigid rotations and translations are applied; STL units stay millimetres.
"""
from pathlib import Path
from collections import Counter
import argparse
import hashlib
import json
import re
import struct
import zipfile

root = Path(__file__).resolve().parents[1]
source = root / 'review/rear-tether-2026-09-29/Onshape_open_all_parts.zip'
out = root / 'print/rear-tether-2026-09-29/parts'
report_path = root / 'review/rear-tether-print-validation.json'
pack_path = root / 'print/Fingerworker_RearTether_2026-09-29.zip'
names = {
    'P01': 'base', 'P02': 'palm_bolster', 'P03': 'palm_sleeve_TPU',
    'P04': 'climbing_carriage', 'P05': 'floating_yoke',
    'P060': 'rear_retainer_left', 'P061': 'rear_retainer_right',
    'P070a': 'return_pad_left_a_TPU', 'P070b': 'return_pad_left_b_TPU',
    'P071a': 'return_pad_right_a_TPU', 'P071b': 'return_pad_right_b_TPU',
}

PACK_README = """Fingerworker — Entwicklungs-Drucksatz vom 29.09.2026

Elf STL-Dateien in parts/, Einheit Millimeter. Nur P01_base.stl ist neu:
172 x 180 x 29 mm, mit zwei integrierten hinteren Augen fuer 6-mm-Reepschnur.
Die anderen zehn Druckteile sind identisch zum Satz vom 21.09.2026.
Der beiliegende Pruefbericht belegt geschlossene Netze, keine Belastbarkeit.

Entwicklungsprototyp OHNE Lastfreigabe. Zielkraft, Druckmaterial und Druckprozess
sind noch offen. Querbohrungen im Slicer pruefen; Schnurkontakt nach dem Druck
glatt und gratfrei ausfuehren. Jedes Auge muss fuer die volle geplante Zugkraft
am gedruckten Teil geprueft werden. Sensor, Metallteile und Federn fehlen im Satz.

Beide Augen am FESTEN Rahmen verwenden. Schnurstraenge und Knoten hinter dem
Geraet halten, ausserhalb beweglicher Teile. Nicht am Schlitten, Joch, an den
Fuehrungsstangen oder den abnehmbaren hinteren Haltern befestigen. Vor Messung
im Seilbetrieb neu nullen und mit bekannter aeusserer Zuglast pruefen.
Kraftdaten am mechanischen Endanschlag sind ungueltig.

Live-CAD:
https://cad.onshape.com/documents/15316cc6370631845af136b2/w/664d0779b5d992870442f997/e/d253eb87b70818ebde8215f0
Weitere Montagehinweise und benoetigte Stahlteile stehen im Projektordner in
REAR_TETHER.md und DEVICE_UPGRADES.md.
"""


def rotate(v, key):
    x, y, z = v
    if key == 'P03':
        return (x, -z, y)  # sleeve axis stands vertical
    if key.startswith('P07'):
        return (-z, y, x)  # 1.5 mm pad thickness vertical
    return v


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--expected-cad-sha256', required=True,
                        help='CAD source hash verified when this Onshape export was captured')
    args = parser.parse_args()
    cad_sha = hashlib.sha256((root / 'fingerworker_mvp.fs').read_bytes()).hexdigest()
    assert cad_sha == args.expected_cad_sha256, 'CAD changed after the export capture'
    previous = json.loads((root / 'review/full-review-print-validation.json').read_text())
    old_parts = {p['file']: p for p in previous['parts']}
    assert set(old_parts) == {f'{key}_{name}.stl' for key, name in names.items()}
    report = {
        'source': 'Onshape, two integral rear cord eyes for provisional 6 mm cord, '
                  '29 September 2026; 0 mm pose, preload 0 mm, light springs, '
                  'hand/electronics/cord reference off; binary STL, millimetres, Fine',
        'source_zip_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
        'cad_source_sha256': cad_sha,
        'parts': [],
    }
    outputs = {}
    with zipfile.ZipFile(source) as archive:
        files = []
        for filename in archive.namelist():
            match = re.search(r' - (P\w+)\b', filename)
            if match and match[1] in names:
                files.append((filename, match[1]))
        assert len(files) == len(names) == 11, 'Expected eleven printable Onshape solids'
        assert {key for _, key in files} == set(names), 'Missing or duplicate printable part'
        for filename, key in files:
            assert filename.endswith('.stl') and '/' not in filename
            data = archive.read(filename)
            assert len(data) >= 84, (key, 'Truncated STL')
            count = struct.unpack_from('<I', data, 80)[0]
            assert count > 0 and len(data) == 84 + 50 * count, (key, 'Invalid binary STL')
            triangles, normals = [], []
            for i in range(count):
                vals = struct.unpack_from('<12fH', data, 84 + 50 * i)
                normals.append(rotate(vals[:3], key))
                triangles.append([rotate(vals[j:j + 3], key) for j in (3, 6, 9)])
            mins = tuple(min(v[i] for t in triangles for v in t) for i in range(3))
            maxs = tuple(max(v[i] for t in triangles for v in t) for i in range(3))
            triangles = [[tuple(v[i] - mins[i] for i in range(3)) for v in t]
                         for t in triangles]
            edges, volume = Counter(), 0
            for tri in triangles:
                points = [tuple(round(x, 5) for x in p) for p in tri]
                for a, b in zip(points, points[1:] + points[:1]):
                    if a != b:
                        edges[tuple(sorted((a, b)))] += 1
                a, b, c = tri
                volume += (a[0] * (b[1] * c[2] - b[2] * c[1])
                           + a[1] * (b[2] * c[0] - b[0] * c[2])
                           + a[2] * (b[0] * c[1] - b[1] * c[0])) / 6
            bad_edges = sum(v != 2 for v in edges.values())
            assert bad_edges == 0, (key, bad_edges)
            assert volume > 0, (key, volume)
            size = tuple(maxs[i] - mins[i] for i in range(3))
            expected = (172, 180, 29) if key == 'P01' else None
            if key == 'P04':
                expected = (60, 174, 25)
            if expected:
                assert all(abs(a - b) < .01 for a, b in zip(size, expected)), (key, size)
            assert max(size[:2]) <= 220, (key, size)
            target_name = f'{key}_{names[key]}.stl'
            if key != 'P01':
                old = old_parts[target_name]
                assert all(abs(a - b) < .01 for a, b in zip(size, old['size_mm'])), (key, size)
                assert abs(volume - old['volume_mm3']) < max(.1, old['volume_mm3'] * .0001), (key, volume)
            binary = bytearray(b'Fingerworker printable part; mm; rigid orientation only'.ljust(80, b'\0'))
            binary.extend(struct.pack('<I', count))
            for normal, tri in zip(normals, triangles):
                binary.extend(struct.pack('<12fH', *normal, *tri[0], *tri[1], *tri[2], 0))
            outputs[target_name] = binary
            report['parts'].append({
                'file': target_name, 'triangles': count,
                'size_mm': [round(x, 3) for x in size], 'volume_mm3': round(volume, 3),
                'nonmanifold_edges_at_1e-5mm': bad_edges,
                'sha256': hashlib.sha256(binary).hexdigest(),
            })
            print(f'{target_name}: closed mesh; {count} facets; '
                  + ' x '.join(f'{x:.2f}' for x in size) + ' mm')
    old_volume = sum(p['volume_mm3'] for p in previous['parts'])
    new_volume = sum(p['volume_mm3'] for p in report['parts'])
    report['material_comparison'] = {
        'previous_revision': '21 September 2026 full review',
        'previous_solid_volume_cm3': round(old_volume / 1000, 3),
        'current_solid_volume_cm3': round(new_volume / 1000, 3),
        'increase_percent': round((new_volume / old_volume - 1) * 100, 2),
        'meaning': 'Geometric volume of eleven printable solids; actual filament depends on infill, walls and supports.',
    }
    report['manufacturing_release'] = False
    report['limitations'] = [
        'Development meshes only. Cord-anchor force rating, real-hand fit and assembly tests remain open.',
        'No geometry repair or scaling; rigid print orientation only. Metal parts excluded.',
    ]
    out.mkdir(parents=True, exist_ok=True)
    assert not {p.name for p in out.iterdir()} - set(outputs), 'Unexpected files in output parts folder'
    for filename, data in outputs.items():
        (out / filename).write_bytes(data)
    report_path.write_text(json.dumps(report, indent=2) + '\n')
    with zipfile.ZipFile(pack_path, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        for filename in sorted(outputs):
            archive.write(out / filename, f'parts/{filename}')
        archive.write(report_path, 'rear-tether-print-validation.json')
        archive.writestr('README.txt', PACK_README)
    print(report['material_comparison'])
    print('Development print pack saved to', pack_path)


if __name__ == '__main__':
    main()
