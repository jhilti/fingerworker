#!/usr/bin/env python3
"""Build the local R9 P02 bracing candidate from immutable R8 source.

This script prepares FeatureScript only. Native regeneration, export and
independent validation are separate required steps, not implied by this build.
"""
from pathlib import Path
from hashlib import sha256
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE_RELATIVE = 'review/flat132-palm-cover-2026-10-23/fingerworker_flat132_palm_cover.fs'
PROJECT_BASE = ROOT / BASE_RELATIVE
BUNDLED_BASE = HERE / 'reference/baseline/fingerworker_flat132_palm_cover.fs'
BASE = PROJECT_BASE if PROJECT_BASE.is_file() else BUNDLED_BASE
BASE_SHA = '6099df42e341ff9f5c3439709a23107325d10ef922f616bdcda6fa6ef64d41c1'
OUT = HERE / 'fingerworker_flat132_palm_bracing.fs'
raw = BASE.read_bytes()
assert sha256(raw).hexdigest() == BASE_SHA, 'Frozen R8 source changed'
source = raw.decode()
changes = []


def replace(label, old, new):
    global source
    assert source.count(old) == 1, (label, source.count(old))
    source = source.replace(old, new)
    changes.append(dict(label=label, count=1, old=old, new=new))


replace('R9 study identity',
        ' * Fingerworker MVP - R8 palm-cover CAD prototype; load rating unverified.',
        ''' * Fingerworker MVP - R9 fixed-frame palm bracing CAD prototype; load rating unverified.
 * R9 changes P02 only: two broad integral compression pads bear against
 * fixed P01 atX-22.75, not the floating yoke, cell or electronics lid.
 * Each7 x13 mm nominal bearing face is atY18..25 orY-25..-18/Z14..27.
 * Two-mm root overlap and explicitR1.2 concave root stocks join the palm.
 * Exact nominal contact needs physical fitting; do not force an interference
 * fit or preload the fixed portal when tightening the palm fasteners.
 * All other bodies, wrist contact, mounts and R8 lid gap remain unchanged.
 * Unload/restrain before removing both M4 bolts and lifting the palm/case
 * module vertically; the contact pads have no hooks or undercuts.''')
replace('R9 feature name',
        '"Feature Name Template" : "Flat132 R8 - one-piece palm with electronics cover"',
        '"Feature Name Template" : "Flat132 R9 - palm braced on fixed frame"')

old = '''        nameBody(context,body(id + "palmPad"),
            "P02 PRINT STUDY - one-piece rigid half-round palm with flat electronics cover");'''
new = '''        // R9: broad direct compression bearings on the FIXED P01 rear
        // wall, which starts atX-22.75. Central H15 keeper/adjuster access
        // remains open. The moving P05 and sensor stack are never a brace.
        // Main pads overlap the old palm's flatX-27 root by2 mm. Each flat
        // contact face is7 mm wide and13 mm high, without a slender lip.
        // Explicit box-minus-cylinder root stocks formR1.2 concave blends;
        // this avoids topology-dependent post-union fillet selection.
        var palmBraceStocks=[body(id + "palmPad")];
        for (var side in [-1,1])
        {
            const s=side == -1 ? "0" : "1";
            const loY=side == -1 ? -25 : 18;
            const hiY=loY+7;
            makeBox(context,id + ("palmBracePad"~s),vector(-29,loY,14)*mm,
                vector(-22.75,hiY,27)*mm);
            palmBraceStocks=append(palmBraceStocks,body(id + ("palmBracePad"~s)));
            // Side-root wedges are tangent atX-27 and the pad side. Their
            // extra0.1 mm rear overlap guarantees positive fusion to P02.
            for (var edge in [0,1])
            {
                const t=s~edge;
                const edgeY=edge == 0 ? loY : hiY;
                const centerY=edge == 0 ? edgeY-1.2 : edgeY+1.2;
                const wedgeLoY=edge == 0 ? centerY : edgeY;
                const wedgeHiY=edge == 0 ? edgeY : centerY;
                makeBox(context,id + ("palmBraceSideRoot"~t),
                    vector(-27.1,wedgeLoY,14)*mm,vector(-25.8,wedgeHiY,27)*mm);
                makeCylinder(context,id + ("palmBraceSideRoundTool"~t),
                    vector(-25.8,centerY,13.9)*mm,
                    vector(-25.8,centerY,27.1)*mm,1.2*mm);
                cut(context,id + ("palmBraceSideRound"~t),
                    body(id + ("palmBraceSideRoot"~t)),
                    body(id + ("palmBraceSideRoundTool"~t)));
                palmBraceStocks=append(palmBraceStocks,body(id + ("palmBraceSideRoot"~t)));
            }
            // Upper-rootR1.2 tangent blends spread the root into the solid
            // half-round. The lower root already overlaps its5 mm plate.
            makeBox(context,id + ("palmBraceTopRoot"~s),
                vector(-27.1,loY,27)*mm,vector(-25.8,hiY,28.2)*mm);
            makeCylinder(context,id + ("palmBraceTopRoundTool"~s),
                vector(-25.8,loY-0.1,28.2)*mm,
                vector(-25.8,hiY+0.1,28.2)*mm,1.2*mm);
            cut(context,id + ("palmBraceTopRound"~s),
                body(id + ("palmBraceTopRoot"~s)),
                body(id + ("palmBraceTopRoundTool"~s)));
            palmBraceStocks=append(palmBraceStocks,body(id + ("palmBraceTopRoot"~s)));
        }
        join(context,id + "palmBraceJoin",palmBraceStocks);
        nameBody(context,body(id + "palmPad"),
            "P02 PRINT STUDY - solid half-round palm with fixed-frame compression braces and electronics cover");'''
replace('P02 only: union two broad bearings and explicit rounded root stocks', old, new)
OUT.write_bytes(source.encode())
manifest = {
    'file': OUT.name,
    'sha256': sha256(OUT.read_bytes()).hexdigest(),
    'bytes': OUT.stat().st_size,
    'status': 'LOCAL_R9_SOURCE_NATIVE_REGEN_AND_VALIDATION_PENDING',
    'baseline_source': BASE_RELATIVE,
    'baseline_source_sha256': BASE_SHA,
    'baseline_immutable_version_id': '6965afcca3af7c58ef3ac73f',
    'expected_native_body_count_with_electronics': 123,
    'expected_device_body_count': 70,
    'expected_print_part_count': 16,
    'changed_old_refs': ['P02'],
    'added_print_refs': [], 'added_hardware_refs': [], 'removed_refs': [],
    'legal_domain_unchanged': 'a>=0,p>=0,a+p<=2,u>=0,u+a+p<=30;dynamicq=5+a+u;ISOq20-p,userapproach15-p-a',
    'brace_geometry': {
        'bearing_plane_x_mm': -22.75,
        'bearing_face_area_mm2_each': 91,
        'core_stock_bounds_mm': [
            [[-29, -25, 14], [-22.75, -18, 27]],
            [[-29, 18, 14], [-22.75, 25, 27]],
        ],
        'root_round_radius_mm': 1.2,
        'root_round_tangent_x_mm': -27,
        'root_round_rear_overlap_mm': .1,
        'root_round_cylinder_center_x_mm': -25.8,
        'root_stock_z_max_mm': 28.2,
        'root_stock_absolute_y_max_mm': 26.2,
        'root_stock_absolute_y_min_mm': 16.8,
        'intended_contact_pair': ['P02', 'P01'],
        'excluded_supports': ['P05', 'sensor/cassette', 'P09 lid', 'electronics'],
    },
    'geometry_change_ledger': [
        'Only P02 changes. Two joined solid pads reach fixed P01 rear planeX-22.75 with7x13mm nominal bearing faces.',
        'Main stocks areX-29..-22.75,Y-25..-18/+18..25,Z14..27; they overlap the oldX-27 palm flat by2mm.',
        'Four lateral and two top box-minus-cylinder root wedges create explicitR1.2 tangent root transitions; rear0.1mm overlap guarantees fusion.',
        'Central keeper/adjuster space remains open; no moving sensor-force-path body or electronics part is made a palm support.',
        'All original P02 material, curved wrist contact, mounting keys/pilots, cover, enclosure and0.6mm nominal lid gap are retained.',
        'No hooks or underside captures: intended service is the existing unloaded40mm upward removal of the palm/case unit after removing both M4 screws.',
        'The123body/70device/16printed inventory,132mm width,72mm opening,81mm ISO sleeves and28..30mm nominal travel remain unchanged.',
    ],
    'qualification': 'Candidate nominal CAD only. Native regeneration and exact/continuous/service checks remain pending; print tolerances, load sharing, stiffness, material creep and500N strength require physical qualification.',
    'changes': changes,
}
(HERE / 'source-build.json').write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + '\n')
print(json.dumps({k: manifest[k] for k in ['file', 'sha256', 'bytes', 'status']}, indent=2))
