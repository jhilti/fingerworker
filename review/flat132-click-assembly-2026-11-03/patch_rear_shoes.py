#!/usr/bin/env python3
"""Compose R11 integral return lands into frozen R10 FeatureScript.

This is deliberately a small source transform for the release owner to compose.
No root/source file or existing print artifact is modified by importing it.
Coordinates are construction coordinates before the common rearAdvance shift.
"""
from pathlib import Path
import hashlib
import json

R10_SHA = '5ce830ff2b06cd8d318d3c44dbc1f3385697526a9a679d2a2078f64f81854237'


def patch_source(source: str) -> str:
    old = '''                makeBox(context,id + ("returnPad"~s~t),vector(119,padY-2.25,14)*mm,vector(120.5,padY+2.25,20)*mm);
                nameBody(context,body(id + ("returnPad"~s~t)),"P07"~s~t~" TPU PRINT - return bumper");
                if (rearAdvance > 0*mm)
                    opTransform(context,id + ("returnPadSetting"~s~t),{"bodies":body(id + ("returnPad"~s~t)),
                        "transform":transform(vector(-rearAdvance,0*mm,0*mm))});'''
    new = '''                // R11: hard return lands belong to the full-size shoe.
                // Front datum X119 is unchanged. Extra0.2 mm extends INTO
                // its fork (X120.5..121.5), guaranteeing positive fusion.
                // The complete shoe receives rearAdvance once below.
                makeBox(context,id + ("returnPad"~s~t),vector(119,padY-2.25,14)*mm,vector(120.7,padY+2.25,20)*mm);
                join(context,id + ("integralReturnLand"~s~t),[
                    body(id + ("rearShoe"~s)),body(id + ("returnPad"~s~t))]);'''
    assert source.count(old) == 1, 'R10 return-pad source anchor not unique'
    source = source.replace(old, new)
    old_audit = '''    const pads = qUnion([body(id + "returnPad0a"),body(id + "returnPad0b"),
                        body(id + "returnPad1a"),body(id + "returnPad1b")]);'''
    # Boolean tools no longer survive as independent bodies. The full shoe
    # carries the old contact lands, so use that body for the contact audit.
    if old_audit in source:
        source = source.replace(old_audit, '''    const pads = qUnion([body(id + "rearShoe0"),body(id + "rearShoe1")]); // R11 integral hard return lands''')
    else:
        raise AssertionError('R10 pad audit source anchor changed')
    source = source.replace('auditSolidPair(context,"Carriage / rear retainers",carriage,rear,false)',
        'auditSolidPair(context,"Carriage / rear caps",carriage,qUnion([body(id + "rearBlock0"),body(id + "rearBlock1")]),false)')
    source = source.replace('auditSolidPair(context,"Carriage / return pads",carriage,pads,true)',
        'auditSolidPair(context,"Carriage / integral return lands and shoes",carriage,pads,true)')
    source = source.replace('P07 return bumpers remain separate; no flexible palm sleeve is required.',
        'R11 return lands are integral in P120/P121; no separate pads or palm sleeve.')
    source = source.replace('"P12"~s~" PRINT STUDY - captured two-pad adjustable return shoe"',
        '"P12"~s~" PRINT STUDY - captured adjustable return shoe with integral hard lands"')
    return source


def main():
    here = Path(__file__).resolve().parent
    root = here.parents[1]
    base = root / 'review/flat132-integrated-palm-2026-11-03/fingerworker_flat132_integrated_palm.fs'
    raw = base.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == R10_SHA
    candidate = patch_source(raw.decode())
    target = here / 'candidate-rear-shoes.fs'
    target.write_text(candidate)
    record = {'status': 'SOURCE_PATCH_PREPARED_NOT_NATIVE_REGENERATED',
              'baseline_sha256': R10_SHA, 'candidate_sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
              'scope': 'P120/P121 gain old P07 contact lands; four separate P07 bodies disappear. P01 unchanged.',
              'front_contact_x_mm': 119.0, 'common_adjustment_x_mm': [0.0, -2.0],
              'overlap_into_existing_fork_mm': 0.2, 'separate_parts_removed': 4,
              'material_intent': 'Rigid PLA for initial spring-free assembly; no impact/creep qualification.'}
    (here / 'rear-shoes-source-patch.json').write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps(record, indent=2))


if __name__ == '__main__':
    main()
