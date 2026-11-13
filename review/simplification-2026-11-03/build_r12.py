#!/usr/bin/env python3
"""Compose fixed rear gate, fixed sensor reaction and tray cleanup from R11."""
from pathlib import Path
import hashlib, importlib.util, json, re

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
BASE=ROOT/'review/flat132-click-assembly-2026-11-03/fingerworker_flat132_PLA_click.fs'
def module(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
rear=module('r12_rear',HERE/'rear_gate.py')
enclosure=module('r12_ceiling',HERE/'enclosure_cleanup.py')
front=module('r12_fixed_front',HERE/'front_fixed.py')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def expected(old):
    changed=rear.expected(old)
    changed.update(front.expected(dict(old,**changed)))
    changed.update(enclosure.expected_cleanup(old))
    return changed

def build():
    assert sha(BASE)=='c8ec18f08149553001ccf8173f35fe57eee6a16be0294be2d7f88577f658cf5e'
    source=enclosure.source_cleanup_patch(front.patch_source(rear.patch_source(BASE.read_text())))
    start=source.index('/**');end=source.index('*/',start)+2
    source=source[:start]+'''/**
 * Fingerworker Flat132 R12 - simplified PLA click assembly.
 * Seven printed device bodies: P01 frame/palm, P04 grip,
 * P05 floating force yoke, P06 fixed rear gate, P08 tray, P09 lid, P11 cam.
 * All preload adjustment is removed: a=p=0, q=5+u, 0<=u<=30.
 * H12 bears on a broad fixed support integral with P01 at X=-12 mm.
 * P11 retains camTrim +/-0.8 mm only for physical switch calibration.
 * ISO sleeves remain81 mm with fixed15 mm approach, q=20.
 * One plain removable rear gate replaces both caps and return shoes.
 * Rear M4 adjusters/nuts/washers/jam nuts and M2 shoe pins are omitted.
 * PLA gate latches permit unloaded fitting; four M3 securing screws remain
 * for the loaded assembly. Release both side arms outward0.9mm then+X12mm.
 * Keep the separately printable P09 click lid with integral wire support.
 * Spread P08 hooks0.6mm then lower20mm; open P09 only after removal.
 * Two obsolete former P10 screw pilot holes in P08 are omitted.
 * H11/H13/H15/H16/H17/H21/H22 and their service pockets are omitted.
 * Sensor stack service remains+X3.2mm then+Z40mm after unloading,
 * removing springs, rods, rear gate and side retainers H18/H19.
 * P04/P05 and the central sensor force path retain exact R11 geometry.
 * P04 print orientation stays front end down with bed-only slim trees.
 * Nominal base width132mm; rear latch outer envelope135.2mm.
 * PLA fit, snap cycling, creep and loaded performance require physical tests.
 * No500N qualification; printed rods/Q01 are unloaded fit aids only.
 * Coordinates: X pull direction, Y grip width, Z above base; nominal floor6mm.
 */'''+source[end:]
    source=source.replace('        annotation { "Name" : "Equal rear screw advance a (0 to 2 mm; a + preload <= 2)" }\n        isLength(definition.rearAdvance, { (millimeter) : [0, 0, 2] } as LengthBoundSpec);\n','')
    source=source.replace('        if (definition.rearAdvance != 0*mm)\n            throw regenError("R12 has a fixed rear stop. Set obsolete rear advance to0.",["rearAdvance"]);\n','')
    source=source.replace('        if (rearAdvance < 0*mm || rearAdvance > 2*mm || rearAdvance+preload > 2*mm+1e-6*mm)\n            throw regenError("Set BOTH rear screws equally: advance plus sensor preload must be0..2 mm to retain28..30 mm stroke.",["rearAdvance","preloadAdjustment"]);\n','')
    source=source.replace('0 to 30 minus preload minus rear advance; reset cam shoe','0 to 30 minus sensor preload; reset cam shoe')
    source=source.replace('approach15 minus preload minus rear advance','approach15 minus preload')
    source=source.replace('R7 user travel is30 mm minus preload minus rear advance. Keep advance plus preload<=2; manually reset the cam shoe after preload changes.','R12 travel is30 mm minus sensor preload. Manually reset the cam shoe after preload changes.')
    source=source.replace('"rearAdvance":0*millimeter,','')
    source=source.replace('"Flat132 R10 - integral frame and solid palm"','"Flat132 R12 - simplified click assembly"')
    source=source.replace('compact adjustable-rear frame','fixed rear gate frame')
    source=source.replace('R12 seat reliefs','radius12 seat reliefs')
    source=source.replace('R11 union requires','R12 union requires')
    source=source.replace('The central H15 keeper/adjuster opening remains unchanged.','The obsolete H15 service notch is filled; the palm remains integral.')
    source=source.replace('k=camTrim-preload represents physical setting, not automatic coupling.','camTrim represents physical switch calibration, independent of the fixed stops.')
    source=source.replace('R5 rest compression: DF2194 6..8 mm; DF2185 9..11 mm; user travel30-preload.','R12 fixed rest compression: DF2194 6 mm; DF2185 9 mm; user travel30 mm.')
    source=source.replace('They seat after u=15-preload from the new closer rest.','They seat after u=15 mm from the fixed rest.')
    source=source.replace('FaceX30+preload meets P04front65-q: q+preload<=35.','Fixed stop faceX30 meets P04front65-q at q=35.')
    source=source.replace('With q=5+u the retained user travel is u<=30-preload.','With q=5+u the retained user travel is u<=30 mm.')
    source=source.replace('        finishBody(context,qUnion([body(id + "rearShoe0"),body(id + "rearShoe1")]),color(0.36,0.48,0.42));\n','')
    assert 'definition.rearAdvance' not in source
    assert 'definition.preloadAdjustment' not in source
    target=HERE/'fingerworker_R12_simplified.fs';target.write_text(source)
    report=dict(status='SOURCE_COMPOSED_PENDING_NATIVE_REGENERATION',date='2026-11-03',baseline_sha256=sha(BASE),source_sha256=sha(target),changed=['P01','P08'],new=['P06'],removed=['P060','P061','P120','P121']+[f'H{n}{i}' for n in [26,27,28,29,31,32] for i in [0,1]]+sorted(front.REMOVED),device_prints=7,fit_pieces=10,native_solids=93,central_preload_retained=False)
    (HERE/'source-build.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':build()
