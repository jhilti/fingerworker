#!/usr/bin/env python3
"""Build the R8 one-piece palm cover from the frozen R7 prototype."""
from pathlib import Path
from hashlib import sha256
import json

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
PROJECT_BASE=ROOT/'review/flat132-adjustable-rear-2026-10-23/fingerworker_flat132_adjustable_rear.fs'
BUNDLED_BASE=HERE/'reference/baseline/fingerworker_flat132_adjustable_rear.fs'
BASE=PROJECT_BASE if PROJECT_BASE.is_file() else BUNDLED_BASE
BASE_SHA='d42805e8ee10158408099bf7185e49cf9a6eb06c23c327c90c01edfcd04eaddd'
OUT=HERE/'fingerworker_flat132_palm_cover.fs'
raw=BASE.read_bytes()
assert sha256(raw).hexdigest()==BASE_SHA,'Frozen R7 source changed'
source=raw.decode()
changes=[]
def replace(label,old,new,expected=1):
 global source
 count=source.count(old)
 assert count==expected,(label,count,expected)
 source=source.replace(old,new)
 changes.append(dict(label=label,count=count,old=old,new=new))
replace('R8 study identity',' * Fingerworker MVP - R7 compact adjustable rear CAD prototype; load rating unverified.',
''' * Fingerworker MVP - R8 palm-cover CAD prototype; load rating unverified.
 * R8 changes P02 only: a2 mm flat wrist ledge extends toX-46.1 over P09.
 * The added ledge is joined rigid stock, not a sleeve or an integrated lid.
 * Its undersideZ9.5 retains0.6 mm nominal gap to the lid topZ8.9.
 * P08/P09 and all mounts, openings and R7 mechanism geometry are unchanged.
 * Remove the palm/case unit and detach the case before lifting its lid.
 * USB plug/tool fit, print process, joint strength and500 N remain unqualified.''')
replace('R8 feature name','"Feature Name Template" : "Flat132 R7 - compact screw-adjusted rear"',
        '"Feature Name Template" : "Flat132 R8 - one-piece palm with electronics cover"')
old='''        nameBody(context,body(id + "palmPad"),
            "P02 PRINT STUDY - one-piece rigid half-round palm block, retained keyed mounts");'''
new='''        // R8: extend the existing flat underside over the exposed enclosure.
        // Actual P09 lid is square X-46.1..-23.6, Y+/-55, topZ8.9.
        // R2 plan corners lie outside that footprint because this ledge spans
        // Y+/-64. Its wrist datum is flushX-46.1, so whole-device X is unchanged.
        // Four-and-a-quarter mm overlap into the old plate gives a continuous
        // union through its rounded corners; neither mounts nor lid are cut.
        makeBox(context,id + "palmCoverLedge",vector(-46.1,-64,9.5)*mm,
            vector(-33,64,11.5)*mm);
        opFillet(context,id + "palmCoverCorners",{
            "entities":qParallelEdges(qCreatedBy(id + "palmCoverLedge",EntityType.EDGE),vector(0,0,1)),
            "radius":2*mm,"tangentPropagation":true });
        // Round the upper perimeter only. Keep underside and lower wrist band
        // intact so top-view projection still fully covers the square lid.
        opFillet(context,id + "palmCoverUpperEdge",{
            "entities":qContainsPoint(qOwnedByBody(body(id + "palmCoverLedge"),EntityType.EDGE),
                vector(-46.1,0,11.5)*mm),
            "radius":0.5*mm,"tangentPropagation":true });
        join(context,id + "palmCoverJoin",[body(id + "palmPad"),body(id + "palmCoverLedge")]);
        nameBody(context,body(id + "palmPad"),
            "P02 PRINT STUDY - one-piece rigid half-round palm with flat electronics cover");'''
replace('P02 only: join flush wrist ledge over complete lid footprint',old,new)
assert source.count('"palmCoverLedge"')==4,source.count('"palmCoverLedge"')
OUT.write_bytes(source.encode())
manifest={
 'file':OUT.name,'sha256':sha256(OUT.read_bytes()).hexdigest(),'bytes':OUT.stat().st_size,
 'status':'LOCAL_R8_SOURCE_NATIVE_REGEN_AND_VALIDATION_PENDING',
 'baseline_source':'review/flat132-adjustable-rear-2026-10-23/fingerworker_flat132_adjustable_rear.fs',
 'baseline_source_sha256':BASE_SHA,
 'baseline_immutable_version_id':'6dd467818da7364197461627',
 'expected_native_body_count_with_electronics':123,'expected_device_body_count':70,'expected_print_part_count':16,
 'changed_old_refs':['P02'],'added_print_refs':[],'added_hardware_refs':[],'removed_refs':[],
 'legal_domain_unchanged':'a>=0,p>=0,a+p<=2,u>=0,u+a+p<=30;dynamicq=5+a+u;ISOq20-p,userapproach15-p-a',
 'geometry_change_ledger':[
  'Only P02 geometry changes: union a2mm-thick ledge X-46.1..-33,Y-64..64,Z9.5..11.5 into the existing rigid palm.',
  'New wrist extent extends8.85mm beyond old flatplateX-37.25;4.25mm nominal overlap joins old plate through its R2 plan corners.',
  'Ledge plan cornersR2; upper perimeterR0.5 only; underside remainsZ9.5 and lower wrist edge remainsX-46.1.',
  'P09 square lid footprintX-46.1..-23.6/Y±55 is covered in projection by extended P02;0.6mm nominal underside-to-lid gap.',
  'No new stock belowZ9.5; enclosure USB/sidebutton/wire openings, P08/P09 separate lids and their hardware/mounts remain unchanged.',
  'Added ledge stopsX-33,4.4mm from oldP08collarXmin-28.6; existing P02/collar contact is unchanged, not a new gap claim.',
  'Curved R10.25 palm contact axisX-27/Z19.75 and wrist tangentX-37.25 remain unchanged; new flatledgeXmin-46.1 is a different feature.',
  'P02 remains one rigid printable block; no sleeve or P09 lid integration. Frame132,clearopening72,ISO81,rear settings/travel and maximum overall X176.5 remain unchanged.',
  'Lid service requires removing the palm/case module and detaching case from palm before lifting P09; retained underside mounting screws stay accessible.'
 ],
 'qualification':'Nominal CAD only: actual USB plug/tool clearances, physical fit, print process and500N strength are not qualified.',
 'changes':changes}
(HERE/'source-build.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({k:manifest[k] for k in ['file','sha256','bytes','expected_native_body_count_with_electronics','expected_device_body_count','expected_print_part_count']}))
