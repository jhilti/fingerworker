#!/usr/bin/env python3
"""Build R7 compact adjustable rear prototype from immutable R6 source."""
from pathlib import Path
from hashlib import sha256
import json
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
PROJECT_BASE=ROOT/'review/flat132-solid-palm-2026-10-23/fingerworker_flat132_solid_palm.fs'
BUNDLED_BASE=HERE/'reference/baseline/fingerworker_flat132_solid_palm.fs'
BASE=PROJECT_BASE if PROJECT_BASE.is_file() else BUNDLED_BASE
BASE_SHA='62fabee79cf36d0e0b6d4cd8430700519dbc529a5ea08f70018b14b0c3f2271f'
OUT=HERE/'fingerworker_flat132_adjustable_rear.fs'
raw=BASE.read_bytes();assert sha256(raw).hexdigest()==BASE_SHA
source=raw.decode();changes=[]
def replace(label,old,new,expected=1):
 global source
 assert source.count(old)==expected,(label,source.count(old),expected)
 source=source.replace(old,new);changes.append(dict(label=label,old=old,new=new,count=expected))
replace('R7 identity',' * Fingerworker MVP - R6 solid-palm CAD prototype; load rating unverified.',''' * Fingerworker MVP - R7 compact adjustable rear CAD prototype; load rating unverified.
 * R7: base and rods shorten5 mm; rear shoes adjust equally by0..2 mm.
 * Two M4x10 adjusters use captive DIN562 nuts, OD12 reaction washers
 * and accessible DIN439 jam nuts. Two M2 pins positively retain shoes.
 * Rear cap screws are now explicitly modeled; nominal hardware only.
 * With extra rest advance a, a+p<=2 and u<=30-p-a retain28..30 mm stroke.
 * q=5+a+u dynamically; ISO q=20-p, approach15-p-a. No auto synchronization.
 * Device X envelope176.5 mm includes protruding adjuster ends at a0.
 * Physical locking, setup, print strength and500 N target remain unqualified.''')
replace('feature name','"Feature Name Template" : "Flat132 R6 - one-piece printable palm block"','"Feature Name Template" : "Flat132 R7 - compact screw-adjusted rear"')
replace('new rest parameter','        annotation { "Name" : "Additional synchronized preload (0 to 2 mm)" }','''        annotation { "Name" : "Equal rear screw advance a (0 to 2 mm; a + preload <= 2)" }
        isLength(definition.rearAdvance, { (millimeter) : [0, 0, 2] } as LengthBoundSpec);
        annotation { "Name" : "Additional synchronized preload (0 to 2 mm)" }''')
replace('travel label','"User travel from closer rest (0 to 30 mm minus preload; reset cam shoe)"','"User travel (0 to 30 minus preload minus rear advance; reset cam shoe)"')
replace('ISO label','"Isometric: BOTH81 mm sleeves; approach13-15 mm from closer rest"','"Isometric: BOTH81 mm sleeves; approach15 minus preload minus rear advance"')
replace('rest domain','        const restOffset=5*mm;','''        const rearAdvance=definition.rearAdvance;
        if (rearAdvance < 0*mm || rearAdvance > 2*mm || rearAdvance+preload > 2*mm+1e-6*mm)
            throw regenError("Set BOTH rear screws equally: advance plus sensor preload must be0..2 mm to retain28..30 mm stroke.",["rearAdvance","preloadAdjustment"]);
        const restOffset=5*mm+rearAdvance;''')
replace('max user travel','const maxDynamicTravel = 30 * mm - preload;','const maxDynamicTravel = 30 * mm - preload - rearAdvance;')
replace('travel guard explanation','R5 user travel remains30 mm minus preload. Use28 mm at2 mm preload; manually reset the shoe by minus the preload change.','R7 user travel is30 mm minus preload minus rear advance. Keep advance plus preload<=2; manually reset the cam shoe after preload changes.')
replace('frame envelope','// Envelope180.1 x132 x35 including enclosure and captive sensor; base156 x132, floor6 (Z-2 to Z4); pocket20 deep, floor2.7 above guide.','// Envelope176.5 x132 x35 at rear advance0; base151 x132, floor6 (Z-2 to Z4); rear washer pocket retains2.8 mm floor.')
replace('shorten base','vector(134,66,4)*mm','vector(129,66,4)*mm')
replace('shorten rods','vector(130,y,18)*mm','vector(125,y,18)*mm')
replace('rod labels','Steel guide rod dia 6 x 146 mm','Steel guide rod dia 6 x 141 mm')
start=source.index('            // Rear assembly sweep:')
end=source.index('\n        }\n\n        // Broad integral PRINTED sensing stops',start)
block='''            // R7 rear: five-mm-shorter frame/rods, independently guided return
            // shoes. Adjust BOTH M4 screws equally, then counterhold with2 mm
            // hex and tighten7 mm jam nuts. These are RETURN stops only.
            makeBox(context,id + ("rearFoot"~s),vector(119.5,y-14,3.8)*mm,vector(129,y+14,4.5)*mm);
            baseBodies=append(baseBodies,body(id + ("rearFoot"~s)));
            makeBox(context,id + ("rearBlock"~s),vector(120.5,y-14,4.5)*mm,vector(128.5,y+14,28)*mm);
            makeBox(context,id + ("rearCaptureRoof"~s),vector(120.5,y-4.5,27)*mm,vector(129.5,y+4.5,30.5)*mm);
            join(context,id + ("rearRoofJoin"~s),[body(id + ("rearBlock"~s)),body(id + ("rearCaptureRoof"~s))]);
            makeCylinder(context,id + ("rearSocket"~s),vector(120,y,18)*mm,vector(126.2,y,18)*mm,3.1*mm);
            cut(context,id + ("rearBore"~s),body(id + ("rearBlock"~s)),body(id + ("rearSocket"~s)));
            // Preserve a1.5 mm radial socket wall through the front shoe relief.
            makeBox(context,id + ("shoeForkPocket"~s),vector(118.8,y-10.05,13.7)*mm,vector(121.8,y+10.05,26.8)*mm);
            makeCylinder(context,id + ("shoePocketRodKeep"~s),vector(118.7,y,18)*mm,vector(121.9,y,18)*mm,4.6*mm);
            cut(context,id + ("shoePocketRodMask"~s),body(id + ("shoeForkPocket"~s)),body(id + ("shoePocketRodKeep"~s)));
            cut(context,id + ("shoeForkRelief"~s),body(id + ("rearBlock"~s)),body(id + ("shoeForkPocket"~s)));
            makeBox(context,id + ("shoeConnectorPocket"~s),vector(118.8,y-4.8,3.0)*mm,vector(121.8,y+4.8,24.8)*mm);
            makeCylinder(context,id + ("connectorRodKeep"~s),vector(118.7,y,18)*mm,vector(121.9,y,18)*mm,4.6*mm);
            cut(context,id + ("connectorPocketMask"~s),body(id + ("shoeConnectorPocket"~s)),body(id + ("connectorRodKeep"~s)));
            cut(context,id + ("shoeConnectorRelief"~s),body(id + ("rearBlock"~s)),body(id + ("shoeConnectorPocket"~s)));
            makeBox(context,id + ("shoeTonguePocket"~s),vector(118.8,y-3.3,23.2)*mm,vector(128.9,y+3.3,26.8)*mm);
            cut(context,id + ("shoeTongueRelief"~s),body(id + ("rearBlock"~s)),body(id + ("shoeTonguePocket"~s)));
            // Main nut loads an ordinary OD12 steel washer against the printed
            // shoulder OUTSIDE the R5.5 rear tool well. Nut trap is open below;
            // the P01 seat closes it after installing both retainers.
            makeBox(context,id + ("rearMainNutTrap"~s),vector(120.4,y-3.7,4.4)*mm,vector(124.1,y+3.7,10.7)*mm);
            makeBox(context,id + ("rearWasherTrap"~s),vector(123.7,y-6.2,4.4)*mm,vector(124.9,y+6.2,13.2)*mm);
            makeCylinder(context,id + ("rearJamToolWell"~s),vector(124.9,y,7)*mm,vector(132,y,7)*mm,5.5*mm);
            cut(context,id + ("rearAdjusterPockets"~s),body(id + ("rearBlock"~s)),qUnion([
                body(id + ("rearMainNutTrap"~s)),body(id + ("rearWasherTrap"~s)),body(id + ("rearJamToolWell"~s))]));
            makeBox(context,id + ("rearBaseNutPocket"~s),vector(121.5,y-3.7,3.3)*mm,vector(124.1,y+3.7,4.7)*mm);
            makeBox(context,id + ("rearBaseWasherPocket"~s),vector(123.7,y-6.2,0.8)*mm,vector(130,y+6.2,4.7)*mm);
            makeBox(context,id + ("rearBaseShoePocket"~s),vector(116.9,y-4.8,3.0)*mm,vector(130,y+4.8,4.7)*mm);
            makeCylinder(context,id + ("rearBaseToolWell"~s),vector(124.9,y,7)*mm,vector(132,y,7)*mm,5.5*mm);
            cut(context,id + ("rearFootAccess"~s),qUnion([body(id + "base"),body(id + ("rearFoot"~s))]),qUnion([
                body(id + ("rearBaseNutPocket"~s)),body(id + ("rearBaseWasherPocket"~s)),
                body(id + ("rearBaseShoePocket"~s)),body(id + ("rearBaseToolWell"~s))]));
            // Two-pad shoe is a single rigid print. A fork clears the retained
            // rod socket boss; the upper tongue remains positively captured.
            makeBox(context,id + ("rearShoe"~s),vector(119.2,y-4.5,3.3)*mm,vector(120.4,y+4.5,11.7)*mm);
            makeBox(context,id + ("rearShoeConnector"~s),vector(120.2,y-4.5,3.3)*mm,vector(121.5,y+4.5,24.5)*mm);
            makeBox(context,id + ("rearShoeFork"~s),vector(120.5,y-9.75,14)*mm,vector(121.5,y+9.75,26.5)*mm);
            makeBox(context,id + ("rearShoeTongue"~s),vector(119.2,y-3,23.5)*mm,vector(128.6,y+3,26.5)*mm);
            join(context,id + ("rearShoeJoin"~s),[body(id + ("rearShoe"~s)),body(id + ("rearShoeConnector"~s)),
                body(id + ("rearShoeFork"~s)),body(id + ("rearShoeTongue"~s))]);
            makeCylinder(context,id + ("rearShoeRodTool"~s),vector(118.8,y,18)*mm,vector(129,y,18)*mm,4.9*mm);
            cut(context,id + ("rearShoeRodClearance"~s),body(id + ("rearShoe"~s)),body(id + ("rearShoeRodTool"~s)));
            // Annular backing supports the thrust plate locally. The bore
            // starts atX120.4, leaving its full1.2 mm front wall intact.
            makeCylinder(context,id + ("rearShoeShaftTool"~s),vector(120.4,y,7)*mm,vector(121.8,y,7)*mm,2.2*mm);
            cut(context,id + ("rearShoeShaftClearance"~s),body(id + ("rearShoe"~s)),body(id + ("rearShoeShaftTool"~s)));
            // Capture slot has2 mm centre travel plus0.1 mm radial clearance.
            makeCylinder(context,id + ("rearShoeSlot0"~s),vector(124.2,y,23.2)*mm,vector(124.2,y,26.8)*mm,1.1*mm);
            makeCylinder(context,id + ("rearShoeSlot1"~s),vector(126.2,y,23.2)*mm,vector(126.2,y,26.8)*mm,1.1*mm);
            makeBox(context,id + ("rearShoeSlotMid"~s),vector(124.2,y-1.1,23.2)*mm,vector(126.2,y+1.1,26.8)*mm);
            cut(context,id + ("rearShoeCaptureSlot"~s),body(id + ("rearShoe"~s)),qUnion([
                body(id + ("rearShoeSlot0"~s)),body(id + ("rearShoeSlot1"~s)),body(id + ("rearShoeSlotMid"~s))]));
            nameBody(context,body(id + ("rearShoe"~s)),"P12"~s~" PRINT STUDY - captured two-pad adjustable return shoe");
            // M4x10 ISO4026 flat point,2 mm hex. Thread envelopes are nominal.
            makeCylinder(context,id + ("rearAdjustScrew"~s),vector(120.8,y,7)*mm,vector(130.4,y,7)*mm,2*mm);
            fCone(context,id + ("rearAdjustTip"~s),{"bottomCenter":vector(120.4,y,7)*mm,
                "topCenter":vector(120.8,y,7)*mm,"bottomRadius":1.25*mm,"topRadius":2*mm});
            join(context,id + ("rearAdjustScrewJoin"~s),[body(id + ("rearAdjustScrew"~s)),body(id + ("rearAdjustTip"~s))]);
            makeXPrism(context,id + ("rearAdjustHexTool"~s),127.9*mm,130.6*mm,
                [vector(y+1.154701,7)*mm,vector(y+0.57735,8)*mm,vector(y-0.57735,8)*mm,
                 vector(y-1.154701,7)*mm,vector(y-0.57735,6)*mm,vector(y+0.57735,6)*mm]);
            cut(context,id + ("rearAdjustHex"~s),body(id + ("rearAdjustScrew"~s)),body(id + ("rearAdjustHexTool"~s) + "body"));
            nameBody(context,body(id + ("rearAdjustScrew"~s)),"H26"~s~" M4x10 ISO4026 flat-point rear adjuster - 2 mm hex");
            makeBox(context,id + ("rearMainNut"~s),vector(121.7,y-3.5,3.5)*mm,vector(123.9,y+3.5,10.5)*mm);
            makeCylinder(context,id + ("rearNutBore"~s),vector(121.6,y,7)*mm,vector(124,y,7)*mm,2.05*mm);
            cut(context,id + ("rearNutThread"~s),body(id + ("rearMainNut"~s)),body(id + ("rearNutBore"~s)));
            nameBody(context,body(id + ("rearMainNut"~s)),"H27"~s~" M4 DIN562 thin square nut 7x7x2.2 - captive reaction");
            makeCylinder(context,id + ("rearReactionWasher"~s),vector(123.9,y,7)*mm,vector(124.9,y,7)*mm,6*mm);
            makeCylinder(context,id + ("rearWasherBore"~s),vector(123.8,y,7)*mm,vector(125,y,7)*mm,2.15*mm);
            cut(context,id + ("rearWasherHole"~s),body(id + ("rearReactionWasher"~s)),body(id + ("rearWasherBore"~s)));
            nameBody(context,body(id + ("rearReactionWasher"~s)),"H31"~s~" M4 DIN9021 steel reaction washer 12x4.3x1");
            makeXPrism(context,id + ("rearJamNut"~s),124.9*mm,127.1*mm,
                [vector(y+4.041452,7)*mm,vector(y+2.020726,10.5)*mm,vector(y-2.020726,10.5)*mm,
                 vector(y-4.041452,7)*mm,vector(y-2.020726,3.5)*mm,vector(y+2.020726,3.5)*mm]);
            makeCylinder(context,id + ("rearJamBore"~s),vector(124.8,y,7)*mm,vector(127.2,y,7)*mm,2.05*mm);
            cut(context,id + ("rearJamThread"~s),body(id + ("rearJamNut"~s) + "body"),body(id + ("rearJamBore"~s)));
            nameBody(context,body(id + ("rearJamNut"~s) + "body"),"H32"~s~" M4 DIN439 jam nut AF7x2.2 - tighten while counterholding adjuster");
            // Removable M2x8 pin through tongue slot, in rear-loaded steel nut.
            makeCylinder(context,id + ("rearCaptureBore"~s),vector(124.2,y,22.3)*mm,vector(124.2,y,30.7)*mm,1.15*mm);
            makeBox(context,id + ("rearCaptureNutTrap"~s),vector(122,y-2.2,27.4)*mm,vector(129.7,y+2.2,28.8)*mm);
            cut(context,id + ("rearCapturePockets"~s),body(id + ("rearBlock"~s)),qUnion([
                body(id + ("rearCaptureBore"~s)),body(id + ("rearCaptureNutTrap"~s))]));
            makeCylinder(context,id + ("rearCaptureScrew"~s),vector(124.2,y,22.5)*mm,vector(124.2,y,30.6)*mm,1*mm);
            makeCylinder(context,id + ("rearCaptureHead"~s),vector(124.2,y,30.5)*mm,vector(124.2,y,32.5)*mm,1.9*mm);
            join(context,id + ("rearCaptureScrewJoin"~s),[body(id + ("rearCaptureScrew"~s)),body(id + ("rearCaptureHead"~s))]);
            nameBody(context,body(id + ("rearCaptureScrew"~s)),"H28"~s~" M2x8 socket cap shoe retention pin - remove only for service");
            makeBox(context,id + ("rearCaptureNut"~s),vector(122.2,y-2,27.5)*mm,vector(126.2,y+2,28.7)*mm);
            makeCylinder(context,id + ("rearCaptureNutBore"~s),vector(124.2,y,27.4)*mm,vector(124.2,y,28.8)*mm,1.05*mm);
            cut(context,id + ("rearCaptureNutThread"~s),body(id + ("rearCaptureNut"~s)),body(id + ("rearCaptureNutBore"~s)));
            nameBody(context,body(id + ("rearCaptureNut"~s)),"H29"~s~" M2 DIN562 steel square nut 4x4x1.2 - capture pin");
            for (var offset in [-9.5,9.5])
            {
                const t=offset < 0 ? "a" : "b";
                makeCylinder(context,id + ("rearHole"~s~t),vector(124.5,y+offset,4)*mm,vector(124.5,y+offset,29)*mm,1.7*mm);
                makeCylinder(context,id + ("rearHead"~s~t),vector(124.5,y+offset,10)*mm,vector(124.5,y+offset,29)*mm,3.2*mm);
                cut(context,id + ("rearMount"~s~t),body(id + ("rearBlock"~s)),qUnion([
                    body(id + ("rearHole"~s~t)),body(id + ("rearHead"~s~t))]));
                makeCylinder(context,id + ("rearInsert"~s~t),vector(124.5,y+offset,0.5)*mm,vector(124.5,y+offset,4.6)*mm,2.1*mm);
                insertTools=append(insertTools,body(id + ("rearInsert"~s~t)));
                // Actual retained rear fasteners, formerly only bores in CAD.
                makeCylinder(context,id + ("rearMountScrew"~s~t),vector(124.5,y+offset,2)*mm,vector(124.5,y+offset,10.1)*mm,1.5*mm);
                makeCylinder(context,id + ("rearMountHead"~s~t),vector(124.5,y+offset,10)*mm,vector(124.5,y+offset,13)*mm,2.75*mm);
                join(context,id + ("rearMountScrewJoin"~s~t),[body(id + ("rearMountScrew"~s~t)),body(id + ("rearMountHead"~s~t))]);
                nameBody(context,body(id + ("rearMountScrew"~s~t)),"H30"~s~t~" M3x8 rear cap screw - ISO4762 head5.5x3 envelope");
                const padY=y+(offset < 0 ? -7.5 : 7.5);
                makeBox(context,id + ("returnPad"~s~t),vector(119,padY-2.25,14)*mm,vector(120.5,padY+2.25,20)*mm);
                nameBody(context,body(id + ("returnPad"~s~t)),"P07"~s~t~" TPU PRINT - return bumper");
                if (rearAdvance > 0*mm)
                    opTransform(context,id + ("returnPadSetting"~s~t),{"bodies":body(id + ("returnPad"~s~t)),
                        "transform":transform(vector(-rearAdvance,0*mm,0*mm))});
            }
            if (rearAdvance > 0*mm)
                opTransform(context,id + ("rearShoeSetting"~s),{"bodies":qUnion([
                    body(id + ("rearShoe"~s)),body(id + ("rearAdjustScrew"~s))]),
                    "transform":transform(vector(-rearAdvance,0*mm,0*mm))});
            nameBody(context,body(id + ("rearBlock"~s)),"P06"~s~" PRINT STUDY - compact rear retainer with captured adjustable shoe");
'''
replace('replace fixed rear bosses with compact screw-adjusted retained shoes',source[start:end],block)
replace('rear bench holes','for (var x in [16,127])','for (var x in [16,122])')
replace('audit rear includes new shoes','const rear = qUnion([body(id + "rearBlock0"), body(id + "rearBlock1")]);','const rear = qUnion([body(id + "rearBlock0"), body(id + "rearBlock1"),body(id + "rearShoe0"),body(id + "rearShoe1")]);')
replace('print rest setting','"userTravelFromCloserRest":userTravel,"restOffset":restOffset,"camTrim":camTrim,','"userTravelFromCloserRest":userTravel,"restOffset":restOffset,"rearAdvance":rearAdvance,"camTrim":camTrim,')
replace('current motion explanatory comment',' * Carriage absolute offset q=5+u; selected81 mm ISO sleeves use q=20-p\n * and user-relative approach u=15-p. Dynamic and ISO grip are5 mm closer.',' * R7 carriage q=5+a+u; selected81 mm ISO sleeves use q=20-p\n * and user-relative approach u=15-p-a. Rear adjustment requires equal setup.')
replace('new default','"previewTravel":0*millimeter,"preloadAdjustment":0*millimeter,"camTrim":0*millimeter,','"previewTravel":0*millimeter,"preloadAdjustment":0*millimeter,"rearAdvance":0*millimeter,"camTrim":0*millimeter,')
replace('P01 label','Flat132 reinforced reaction portal, 5 mm cassette guides, 6 mm floor','Flat132 compact adjustable-rear frame, 5 mm cassette guides, 6 mm nominal floor')
replace('new shoe appearance','        if (!definition.isometricLock)\n            finishBody(context,qUnion([body(id + "spring0"','        finishBody(context,qUnion([body(id + "rearShoe0"),body(id + "rearShoe1")]),color(0.36,0.48,0.42));\n        if (!definition.isometricLock)\n            finishBody(context,qUnion([body(id + "spring0"')
OUT.write_text(source)
manifest=dict(file=OUT.name,sha256=sha256(OUT.read_bytes()).hexdigest(),bytes=OUT.stat().st_size,status='LOCAL_R7_SOURCE_NATIVE_REGEN_AND_VALIDATION_PENDING',baseline_source='review/flat132-solid-palm-2026-10-23/fingerworker_flat132_solid_palm.fs',baseline_source_sha256=BASE_SHA,expected_native_body_count_with_electronics=123,expected_device_body_count=70,expected_print_part_count=16,changed_old_refs=['P01','P060','P061','H040','H041'],added_print_refs=['P120','P121'],added_hardware_refs=['H260','H261','H270','H271','H280','H281','H290','H291','H300a','H300b','H301a','H301b','H310','H311','H320','H321'],changed_configured_old_refs=['P070a','P070b','P071a','P071b'],legal_domain='a>=0,p>=0,a+p<=2,u>=0,u+a+p<=30;dynamicq=5+a+u;ISOq20-p,userapproach15-p-a',mechanism='Two manually matched M4x10 rear screws with DIN562 main nuts, DIN9021OD12reactionwashers,DIN439jamnuts andpositiveM2shoecapture',geometry_change_ledger=['Base maxX134->129; rear benchholes127->122; rodend130->125,length146->141; rearfoot/capmove5mm; washerandlowerhubwithdrawalchannelsopenstorearX130.','RearM3boltcentresX124.5,Y±51±9.5; cap/footlocalYhalfwidth14(globalmax65),giving1.2mmwebtobasewasherchannel.','M4axisY±51/Z7. Mainnut121.7..123.9,washer123.9..124.9,jam124.9..127.1. M4x10tip120.4-a,rear130.4-a.','Basewasherpocketfloor0.8retains2.8mmstockaboveZ-2; toolR5.5atZ7minimumZ1.5retains3.5mmfloor.','P12shoehas0.2mmrigidrestgap,existing1.5mmTPUpads,upper6x3tongueandM2pin;rodkeeperR4.6retainedinsideR4.9shoebore.','Uppercapturebossrear129.5,Z30.5;M2headtop32.5. Peakframewidth132,height35unchanged.','OverallX176.5at a0vsR6 180.1. P02solidpalm,P04pocket,P05sensingstops,ISO81,sensor/switchandcamunchanged.'],changes=changes)
(HERE/'source-build.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({k:manifest[k] for k in ['file','sha256','bytes','expected_native_body_count_with_electronics','expected_device_body_count','expected_print_part_count']}))
