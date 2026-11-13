#!/usr/bin/env python3
"""Read-only actual H2D candidate toolpath localisation for functional surfaces."""
from pathlib import Path
import json,sys,zipfile,hashlib,collections
import numpy as np
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'review/flat132-click-assembly-2026-11-03/enclosure'))
import check_final_toolpaths as t

def main():
    row=json.loads((HERE/'candidate-flat-layout.json').read_text())['placements'][0]
    off=np.array(row['normalization_translation_mm'])+[*row['plate_xy_mm'],0]
    archive=HERE/'validation/integrated_ceiling_verification.gcode.3mf'
    with zipfile.ZipFile(archive) as z:paths=t.parse(z.read('Metadata/plate_1.gcode').decode())
    regions={'ceiling_skin':([-46.1,-55,7.4],[-23.6,55,8.11]),
        'PCB_keeper':([-44.6,-27,1.6],[-25.1,-25,2.16]),
        'battery_rail':([-41.5,36,6.0],[-29.5,39,6.61]),
        'wire_clamp':([-28.1,22.4,2.8],[-24.9,32.6,3.41])}
    rows=[]
    for name,(lo,hi) in regions.items():
        subset=[x for x in paths if 'Support' in x['feature'] and np.all((x['a']+x['b'])/2-off>=lo) and np.all((x['a']+x['b'])/2-off<=hi)]
        rows.append(dict(region=name,bounds_mm=[lo,hi],support_segments=len(subset),
            support_chord_path_mm=sum(x['length'] for x in subset),features=dict(collections.Counter(x['feature'] for x in subset))))
    report=dict(status='REVIEW_REQUIRED_FUNCTIONAL_FACES_NOW_SUPPORTED',date='2026-11-03',
        archive_sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),regions=rows,
        printer='H2D 0.4 mm PLA',candidate_P01_prediction_seconds=30615,candidate_P01_mass_g=133.81,
        reference_R11_P01_prediction_seconds=29786,reference_R11_P01_mass_g=131.35,
        nominal_PCB_keeper_clearance_mm=.05,
        access='All new underside shelves and ribs remain open downward and toward the wrist. No closed support chamber is introduced; actual removal force and cleaned contact fit are untested.',
        limitation='ROI uses recovered native segment midpoint and chord lengths; this localizes support but is not a full swept-extrusion/support-removal proof. Native final export and re-slice required.',
        recommendation='Keep the separate support-free P09 if zero new functional-surface cleanup is prioritized. Merged P01 is feasible nominally, but costs a frame reprint and needs careful keeper/clamp cleanup.')
    (HERE/'support-review.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
