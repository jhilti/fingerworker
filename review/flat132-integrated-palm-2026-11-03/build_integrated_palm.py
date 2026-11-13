#!/usr/bin/env python3
"""Construct R10 integrated frame/palm FeatureScript from frozen R9.

Only source construction is certified here. Native regeneration, mesh export,
assembly/service access and printability are separate validation steps.
"""
from pathlib import Path
from hashlib import sha256
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE_RELATIVE = 'review/flat132-palm-bracing-2026-10-25/fingerworker_flat132_palm_bracing.fs'
PROJECT_BASE = ROOT / BASE_RELATIVE
BUNDLED_BASE = HERE / 'reference/baseline/fingerworker_flat132_palm_bracing.fs'
BASE = PROJECT_BASE if PROJECT_BASE.is_file() else BUNDLED_BASE
BASE_SHA = '16972ba9341f4cdf763a5570dad82a4fbd601f0935d0a7657be85813f97ff2b1'
OUT = HERE / 'fingerworker_flat132_integrated_palm.fs'
raw = BASE.read_bytes()
assert sha256(raw).hexdigest() == BASE_SHA, 'Frozen R9 source changed'
source = raw.decode()
changes = []


def replace(label, old, new):
    global source
    assert source.count(old) == 1, (label, source.count(old))
    source = source.replace(old, new)
    changes.append(dict(label=label, count=1, old=old, new=new))


old_header = source[source.index('/**'):source.index('\nfunction makeBox')]
new_header = '''/**
 * Fingerworker MVP - R10 integral frame and solid palm CAD prototype.
 * P01 includes the former P02 rigid palm, its R8 electronics cover and R9
 * portal braces as ONE continuous printed solid. There is no palm sleeve,
 * palm-to-frame joint, M4 palm fastener, locating key or mounting recess.
 * The two forward drops overlap their fixed feet by0.2 mm inZ. The two R9
 * brace ends overlap the FIXED portal by0.2 mm inX. Wrist contact geometry,
 * enclosure M2 pilots and0.6 mm nominal lid gap are retained.
 * No moving yoke, sensor/cassette, keeper or electronics body is fused.
 * The central keeper/adjuster opening is retained. Keeper M3x8 screws now
 * approach from the sensor side; their heads are recessed in P01 atX-17.
 * H15 is a plain-hole plate; H17 nuts sit behind it atX-24.8..-23.
 * A small lower front notch permits unloaded keeper removal by-2 mmX,
 * then+35 mmZ after removing the sensor stack and keeper hardware.
 * Service-access fix: obsolete palm mount feet/ears/drops stop atX-17.
 * H18/H19 cassette retainers can exit alongY through newØ6.4 passages
 * in the outer front rod blocks. Unload and reset sensor preload to0 first.
 * The former detachable-palm lift-off service route no longer exists.
 *
 * Foreign-part collision audits run on the separate construction regions
 * BEFORE the final union. Their geometry includes the positive overlaps;
 * only the internal Palm/Base pair is omitted as an intended single solid.
 * This preserves region-specific contact policies and avoids qCreatedBy
 * tracing the whole fused frame as "palm" during hand/electronics checks.
 * The final union has an explicit exactly-one-solid assertion.
 *
 * Inherited R7/R9 mechanism dimensions and manual setup are unchanged:
 * rear advance a and sensor preload p require a>=0,p>=0,a+p<=2;
 * dynamic user travel u obeys0<=u<=30-p-a and absolute q=5+a+u.
 * Selected81 mm ISO sleeves use q=20-p and approach15-p-a.
 * Two M4x10 rear adjusters, captive DIN562 nuts, OD12 reaction washers,
 * DIN439 jam nuts and two M2 shoe-retaining pins remain hardware.
 * P07 return bumpers remain separate; no flexible palm sleeve is required.
 * H09 is an Omron SS-01GL2 DRAWING reference, not manufacturer STEP.
 * Native regeneration, assembly/service and printability checks are required.
 * This nominal CAD prototype has no tested load rating or500 N qualification.
 *
 * X=pull direction, Y=finger-bar width, Z=height above the base.
 * Flat132 envelope:132 mm width,72 mm clear pocket,84 mm deck,
 * 102 mm spring-axis spacing,6 mm nominal floor,35 mm device height.
 * Frozen parent:R9 source SHA16972ba9341f4cdf763a5570dad82a4fbd601f0935d0a7657be85813f97ff2b1.
 */
'''
replace('R10 scope and service identity', old_header, new_header)
replace('R10 feature name',
        '"Feature Name Template" : "Flat132 R9 - palm braced on fixed frame"',
        '"Feature Name Template" : "Flat132 R10 - integral frame and solid palm"')

replace('Audit construction-region contract',
        ' * Regenerate independently with previewTravel = 0, 15 and 30 mm and showHand',
        ''' * R10 calls this BEFORE final P01/P02 fusion. The construction regions
 * retain their own contact policies; their intended internal connection is
 * not an interference pair. All external geometry is still checked.
 * Regenerate independently with previewTravel = 0, 15 and 30 mm and showHand''')
replace('Do not audit a planned fused interface as two foreign bodies',
        '        auditSolidPair(context,"Palm support / base",palm,base,true),\n',
        '        // R10 Palm/Base is an internal fused interface, not a collision pair.\n')

replace('Integral feet identity',
        '''        // Flat132 detachable palm: two narrow feet remain outside sensor wall
        // |Y|24 and inside rod blocks |Y|39, with2 mm nominal gaps each side.
        // Positive keys supplement two M4 bolts; joint strength is unqualified.
        // Case front X-23.6 clears foot wrist edge X-23 by0.6 mm.''',
        '''        // R10 integral palm: retain two feet outside the sensor wall and
        // inside the rod blocks; their former locating keys are omitted.
        // Case frontX-23.6 clears foot wrist edgeX-23 by0.6 mm.
        // Feet and upper drops receive0.2 mm positive vertical overlap.''')
key_start = source.index('        for (var side in [-1,1])\n        {\n            const s=side == -1 ? "0" : "1";\n            const y=side*31.5;\n            makeBox(context,id + ("palmKey"~s)')
key_end = source.index('        makeBox(context,id + "palmPad"', key_start)
replace('Omit the two positive palm locating keys', source[key_start:key_end], '')
replace('Fuse the left drop through positive foot overlap',
        'makeBox(context,id + "palmClampDropLeft",vector(-23,-37,6.5)*mm,vector(-9.5,-26,9.6)*mm);',
        'makeBox(context,id + "palmClampDropLeft",vector(-23,-37,6.3)*mm,vector(-9.5,-26,9.6)*mm);')
replace('Fuse the right drop through positive foot overlap',
        'makeBox(context,id + "palmClampDropRight",vector(-23,26,6.5)*mm,vector(-9.5,37,9.6)*mm);',
        'makeBox(context,id + "palmClampDropRight",vector(-23,26,6.3)*mm,vector(-9.5,37,9.6)*mm);')
for label, old, new in [
    ('left foot','vector(-9,-26,6.5)*mm);','vector(-17,-26,6.5)*mm);'),
    ('right foot','vector(-9,37,6.5)*mm);','vector(-17,37,6.5)*mm);'),
    ('left upper ear','vector(-9.5,-26,14.5)*mm);','vector(-17,-26,14.5)*mm);'),
    ('right upper ear','vector(-9.5,37,14.5)*mm);','vector(-17,37,14.5)*mm);'),
    ('left drop','vector(-9.5,-26,9.6)*mm);','vector(-17,-26,9.6)*mm);'),
    ('right drop','vector(-9.5,37,9.6)*mm);','vector(-17,37,9.6)*mm);'),
]:
    replace('Trim obsolete M4 mounting stock: '+label, old, new)

cut_start = source.index('        var insertTools=[];\n        var palmTools=[];')
cut_end = source.index('        // R6 one-piece rigid palm block.', cut_start)
replace('Omit palm key slots, M4 insert pilots, through holes and head recesses',
        source[cut_start:cut_end],
        '''        // R10: no palm attachment hardware or key slots. Keep the later
        // rear-cap and switch insert pilots in this shared tools collection.
        var insertTools=[];
        var n=0;
''')
replace('Integral portal braces identity',
        '''        // R9: broad direct compression bearings on the FIXED P01 rear
        // wall, which starts atX-22.75. Central H15 keeper/adjuster access
        // remains open. The moving P05 and sensor stack are never a brace.
        // Main pads overlap the old palm's flatX-27 root by2 mm. Each flat
        // contact face is7 mm wide and13 mm high, without a slender lip.''',
        '''        // R10: retain R9 broad braces and blend roots, and extend their
        // ends0.2 mm into the FIXED portal starting atX-22.75. This positive
        // volume becomes one printed body at the final union, never a fit.
        // The central H15 keeper/adjuster opening remains unchanged.
        // Moving P05 and the sensor stack are not part of this fusion.''')
replace('Positive portal overlap for both brace stocks',
        'vector(-22.75,hiY,27)*mm);',
        'vector(-22.55,hiY,27)*mm);')
replace('Temporary palm region label before final fusion',
        '"P02 PRINT STUDY - solid half-round palm with fixed-frame compression braces and electronics cover"',
        '"R10 construction region - solid palm and braces, fused into P01 at feature end"')

replace('Reverse keeper hardware for sensor-side service',
        '''            makeBox(context,id + ("keeperNutTrap"~t),vector(-18,side*11-2.85,21.15)*mm,vector(-15.8,side*11+2.85,26.85)*mm);
            cut(context,id + ("keeperNutTrapCut"~t),body(id + "loadCellWall"),body(id + ("keeperNutTrap"~t)));
            makeBox(context,id + ("keeperNut"~t),vector(-17.9,side*11-2.75,21.25)*mm,vector(-16.1,side*11+2.75,26.75)*mm);
            makeCylinder(context,id + ("keeperNutBore"~t),vector(-18.1,side*11,24)*mm,vector(-16,side*11,24)*mm,1.55*mm);
            cut(context,id + ("keeperNutThread"~t),body(id + ("keeperNut"~t)),body(id + ("keeperNutBore"~t)));
            makeCylinder(context,id + ("keeperScrew"~t),vector(-21.6,side*11,24)*mm,vector(-15,side*11,24)*mm,1.5*mm);
            fCone(context,id + ("keeperCountersink"~t),{"bottomCenter":vector(-23,side*11,24)*mm,"topCenter":vector(-21.5,side*11,24)*mm,"bottomRadius":3*mm,"topRadius":1.5*mm});
            cut(context,id + ("keeperCountersinkCut"~t),body(id + "nutKeeper"),body(id + ("keeperCountersink"~t)));
            fCone(context,id + ("keeperHead"~t),{"bottomCenter":vector(-23,side*11,24)*mm,"topCenter":vector(-21.5,side*11,24)*mm,"bottomRadius":3*mm,"topRadius":1.5*mm});
            join(context,id + ("keeperScrewJoin"~t),[body(id + ("keeperScrew"~t)),body(id + ("keeperHead"~t))]);
            nameBody(context,body(id + ("keeperScrew"~t)),"H16"~t~" M3 x 8 countersunk keeper screw - 90 deg max head diameter 6");''',
        '''            // R10: remove the sensor/yoke stack first, then approach
            // these standard M3x8 screw heads from +X. A1 mm front recess
            // places the head face atX-17 and the screw tip atX-25.
            // The full1.8 mm H17 rear nut is engaged, with0.2 mm tip excess.
            // H15 is now a plain Ø3.4 plate; no reverse countersink in steel.
            makeBox(context,id + ("keeperNut"~t),vector(-24.8,side*11-2.75,21.25)*mm,vector(-23,side*11+2.75,26.75)*mm);
            makeCylinder(context,id + ("keeperNutBore"~t),vector(-24.9,side*11,24)*mm,vector(-22.9,side*11,24)*mm,1.55*mm);
            cut(context,id + ("keeperNutThread"~t),body(id + ("keeperNut"~t)),body(id + ("keeperNutBore"~t)));
            fCone(context,id + ("keeperFrontCountersink"~t),{"bottomCenter":vector(-18.5,side*11,24)*mm,"topCenter":vector(-17,side*11,24)*mm,"bottomRadius":1.5*mm,"topRadius":3*mm});
            makeCylinder(context,id + ("keeperFrontHeadAccess"~t),vector(-17,side*11,24)*mm,vector(-15.8,side*11,24)*mm,3.2*mm);
            cut(context,id + ("keeperFrontHeadRelief"~t),body(id + "loadCellWall"),qUnion([body(id + ("keeperFrontCountersink"~t)),body(id + ("keeperFrontHeadAccess"~t))]));
            makeCylinder(context,id + ("keeperScrew"~t),vector(-25,side*11,24)*mm,vector(-18.4,side*11,24)*mm,1.5*mm);
            fCone(context,id + ("keeperHead"~t),{"bottomCenter":vector(-18.5,side*11,24)*mm,"topCenter":vector(-17,side*11,24)*mm,"bottomRadius":1.5*mm,"topRadius":3*mm});
            join(context,id + ("keeperScrewJoin"~t),[body(id + ("keeperScrew"~t)),body(id + ("keeperHead"~t))]);
            nameBody(context,body(id + ("keeperScrew"~t)),"H16"~t~" M3 x 8 countersunk keeper screw - sensor-side head, max diameter 6");''')
replace('Keeper fastener service description',
        '''        // A 2 mm steel keeper is recessed 1 mm into the wall. Through screws
        // react into captive steel nuts; no tapped-plastic load-bearing threads.''',
        '''        // A2 mm steel keeper is recessed1 mm into the wall. R10 uses
        // sensor-side countersunk M3x8 heads in the fixed portal and rear
        // square steel nuts held by a slim AF5.5 open-end wrench from above.
        // These are nominal unthreaded envelopes; printed-seat strength
        // remains unqualified. No tapped-plastic load-bearing thread is used.''')
replace('Plain keeper plate identity',
        '"H15 S355 steel keeper 32 x 19 x 2 - recessed and through bolted"',
        '"H15 S355 steel keeper 32 x 19 x 2 - plain holes, sensor-side screws and rear nuts"')
replace('Lower keeper release notch only in palm construction region',
        '''        nameBody(context,body(id + "palmPad"),
            "R10 construction region - solid palm and braces, fused into P01 at feature end");''',
        '''        // R10: lower H15 edge needs2 mm rearward release before it can
        // lift clear of the fixed portal. This small open notch affects only
        // the palm plate's front strip; the wrist half-round atX<=-27 and
        // brace roots at|Y|>=16.8 are untouched. Never cut the fixed portal.
        makeBox(context,id + "palmKeeperServiceNotch",vector(-25.5,-16.5,9.2)*mm,
            vector(-23.1,16.5,14.7)*mm);
        cut(context,id + "palmKeeperServiceClearance",body(id + "palmPad"),
            body(id + "palmKeeperServiceNotch"));
        nameBody(context,body(id + "palmPad"),
            "R10 construction region - solid palm and braces, fused into P01 at feature end");''')
replace('Outer front rod-block cassette-retainer service passages',
        '''        nameBody(context,body(id + "base"),"P01 PRINT STUDY - Flat132 compact adjustable-rear frame, 5 mm cassette guides, 6 mm nominal floor");''',
        '''        // R10 service-access fix: at PRELOAD0 the H18 M3 cassette
        // retainers and H19 spacers need a clear lateral removal/tool route.
        // Trimmed palm feet/ears/drops end atX-17,1 mm clear of these bores.
        // Cut ONLY the outer front rod blocks, leaving the cassette guides,
        // floor and high rod sockets intact. AtZ11.7 bore top, the original
        // rod-socket bottomZ14.9 retains3.2 mm nominal intervening material.
        for (var side in [-1,1])
        {
            const t=side == -1 ? "0" : "1";
            const fromY=side == -1 ? -66.5 : 38.8;
            const toY=side == -1 ? -38.8 : 66.5;
            makeCylinder(context,id + ("captureServiceBore"~t),
                vector(-12.8,fromY,8.5)*mm,vector(-12.8,toY,8.5)*mm,3.2*mm);
            cut(context,id + ("captureServiceBoreCut"~t),body(id + "base"),
                body(id + ("captureServiceBore"~t)));
        }
        nameBody(context,body(id + "base"),"P01 PRINT STUDY - Flat132 compact adjustable-rear frame, 5 mm cassette guides, 6 mm nominal floor");''')

final_anchor = '''        }

    }, { "previewTravel":0*millimeter'''
final_union = '''        }

        // R10 final operation: all audits and electronics creation above use
        // distinct construction regions. After this union qCreatedBy(palmPad)
        // can trace the whole frame, so do not run region audits below it.
        const frameAndPalm=qBodyType(qUnion([body(id + "base"),body(id + "palmPad")]),BodyType.SOLID);
        if (size(evaluateQuery(context,frameAndPalm)) != 2)
            throw regenError("R10 requires the two complete frame/palm construction regions before final fusion.");
        join(context,id + "integratePalmIntoFrame",[body(id + "base"),body(id + "palmPad")]);
        const integratedFrame=qBodyType(qUnion([body(id + "base"),body(id + "palmPad")]),BodyType.SOLID);
        if (size(evaluateQuery(context,integratedFrame)) != 1)
            throw regenError("R10 frame and palm must regenerate as exactly ONE continuous solid.");
        nameBody(context,integratedFrame,
            "P01 PRINT STUDY - Flat132 integral frame and solid palm, no palm fasteners or sleeve");
        finishBody(context,integratedFrame,color(0.27,0.30,0.28));
        println({"R10IntegralFramePalmSolidCount":size(evaluateQuery(context,integratedFrame)),
            "palmFasteners":0,"palmSleeve":false,"palmRemovable":false});

    }, { "previewTravel":0*millimeter'''
replace('Final union after all audits and electronics generation', final_anchor, final_union)

# Fail closed if any omitted mounting operation survives the construction.
for forbidden in ['"palmKey"', '"palmKeySlot"', '"palmInsert"', '"palmHole"', '"palmHead"', '"palmMountHoles"']:
    assert forbidden not in source, forbidden
assert source.index('join(context,id + "integratePalmIntoFrame"') > source.index('for (var check in makeElectronicsStudy')
assert 'body(id + "palmPad"),base,true' not in source
assert source.count('makeBox(context,id + ("palmBracePad"~s)') == 1
assert 'vector(-22.55,hiY,27)' in source
# An omitted block has no unique replacement token to reverse. Forward replay
# from frozen bytes accounts for deletions as well as replacements.
replayed = raw.decode()
for change in changes:
    assert replayed.count(change['old']) == 1
    replayed = replayed.replace(change['old'], change['new'])
assert replayed == source, 'Unaccounted source mutation outside the ledger'
OUT.write_bytes(source.encode())
manifest = {
    'revision': 'Flat132 R10 integral frame and solid palm',
    'file': OUT.name,
    'sha256': sha256(OUT.read_bytes()).hexdigest(),
    'bytes': OUT.stat().st_size,
    'status': 'SOURCE_CONSTRUCTION_PASS_NATIVE_REGEN_EXPORT_SERVICE_AND_PRINT_VALIDATION_PENDING',
    'baseline_source': BASE_RELATIVE,
    'baseline_source_sha256': BASE_SHA,
    'baseline_immutable_version_id': 'e8f782e27bfe45394bf4038b',
    'source_ledger_validation': {
        'status': 'PASS',
        'baseline_sha256': BASE_SHA,
        'forward_replay_sha256': sha256(replayed.encode()).hexdigest(),
        'matches_generated_source_exactly': replayed == source,
        'unaccounted_mutations': 0,
    },
    'expected_native_body_count_with_electronics': 122,
    'expected_device_body_count': 69,
    'expected_print_part_count': 15,
    'changed_old_refs': ['P01', 'P02', 'H15', 'H160', 'H161', 'H170', 'H171'],
    'surviving_integrated_ref': 'P01',
    'removed_separate_print_refs': ['P02'],
    'added_print_refs': [], 'added_hardware_refs': [],
    'palm_attachment_hardware_removed': [
        '2 x M4x10 palm-to-frame bolts (not modeled as separate solids in R9)',
        '2 x M4 heat-set palm inserts (not modeled as separate solids in R9)',
    ],
    'legal_domain_unchanged': 'a>=0,p>=0,a+p<=2,u>=0,u+a+p<=30;dynamicq=5+a+u;ISOq20-p,userapproach15-p-a',
    'csg_change_ledger': [
        {'operation': 'omit positive stocks from P01 construction', 'feature': 'palmKey0/1',
         'bounds_mm': [[[-22,-34.5,6.3],[-20,-28.5,8]],[[-22,28.5,6.3],[-20,34.5,8]]]},
        {'operation': 'omit subtractive tools from P01; retain stock that was drilled in R9',
         'feature': 'palmInsert0/1', 'tool_shape': 'cylinder', 'radius_mm': 2.6,
         'centers_xy_mm': [[-16,-31.5],[-16,31.5]], 'z_interval_mm': [0.2,7.5]},
        {'operation': 'omit subtractive tools from P02; retain original uncut ear/drop stock',
         'feature': 'palmKeySlot0/1',
         'bounds_mm': [[[-22.25,-34.75,6.4],[-19.75,-28.25,8.3]],[[-22.25,28.25,6.4],[-19.75,34.75,8.3]]]},
        {'operation': 'omit subtractive tools from P02; retain original uncut ear/drop stock',
         'feature': 'palmHole0/1', 'tool_shape': 'cylinder', 'radius_mm': 2.2,
         'centers_xy_mm': [[-16,-31.5],[-16,31.5]], 'z_interval_mm': [5.5,31]},
        {'operation': 'omit subtractive tools from P02; retain original uncut ear/drop stock',
         'feature': 'palmHead0/1', 'tool_shape': 'cylinder', 'radius_mm': 4,
         'centers_xy_mm': [[-16,-31.5],[-16,31.5]], 'z_interval_mm': [10.5,31]},
        {'operation': 'extend both original drop stocks down by0.2 mm',
         'feature': 'palmClampDropLeft/Right', 'original_z_min_mm': 6.5, 'new_z_min_mm': 6.3,
         'added_raw_boxes_mm': [[[-23,-37,6.3],[-17,-26,6.5]],[[-23,26,6.3],[-17,37,6.5]]],
         'purpose': 'positive overlap with existing fixed feet, not boundary-only contact'},
        {'operation': 'trim obsolete palm M4 front mounting stock from both feet, ears and drops',
         'feature': 'palmFootLeft/Right, palmEarLeft/Right, palmClampDropLeft/Right',
         'old_foot_x_max_mm': -9, 'old_ear_drop_x_max_mm': -9.5, 'new_all_x_max_mm': -17,
         'foot_and_drop_x_interval_mm': [-23,-17], 'y_intervals_mm': [[-37,-26],[26,37]],
         'each_nominal_foot_join_area_mm2': 66,
         'purpose': 'clear the lateral H18/H19 service/tool corridor and eliminate a thin residual front lip; obsolete M4 joint removed'},
        {'operation': 'subtract two lateral Ø6.4 service passages from P01 outer front rod blocks ONLY',
         'feature': 'captureServiceBore0/1', 'shape': 'Y-axis cylinder',
         'axis_xz_mm': [-12.8,8.5], 'radius_mm': 3.2,
         'y_intervals_mm': [[-66.5,-38.8],[38.8,66.5]],
         'protected_geometry': 'cassette guides|Y|<=20.5; floor topZ4; rod socket bottomZ14.9',
         'nominal_material_between_service_bore_and_rod_socket_mm': 3.2,
         'required_service_setting': 'unloaded and sensor preload0, then H18/H19/2.5mm hex approach along ±Y'},
        {'operation': 'extend both original brace stocks forward by0.2 mm',
         'feature': 'palmBracePad0/1', 'original_x_max_mm': -22.75, 'new_x_max_mm': -22.55,
         'added_raw_boxes_mm': [[[-22.75,-25,14],[-22.55,-18,27]],[[-22.75,18,14],[-22.55,25,27]]],
         'purpose': 'positive overlap with existing fixed portal, not boundary-only contact'},
        {'operation': 'subtract lower keeper-release notch from P02 region ONLY',
         'feature': 'palmKeeperServiceNotch', 'bounds_mm': [[-25.5,-16.5,9.2],[-23.1,16.5,14.7]],
         'purpose': 'H15 rearward2 mm release then upward35 mm service with fixed palm',
         'protected_geometry': 'wrist half-roundX<=-27; R9 brace roots|Y|>=16.8; fixed portal never cut by this tool'},
        {'operation': 'omit two old P01 front square nut traps',
         'feature': 'keeperNutTrap0/1', 'bounds_mm': [[[-18,-13.85,21.15],[-15.8,-8.15,26.85]],[[-18,8.15,21.15],[-15.8,13.85,26.85]]]},
        {'operation': 'cut two P01 sensor-side countersunk screw-head accesses',
         'feature': 'keeperFrontCountersink0/1 and keeperFrontHeadAccess0/1',
         'centers_yz_mm': [[-11,24],[11,24]],
         'cone_x_interval_mm': [-18.5,-17], 'cone_radii_mm': [1.5,3],
         'cylindrical_access_x_interval_mm': [-17,-15.8], 'cylindrical_access_radius_mm': 3.2,
         'existing_shaft_drill': 'Ø3.4 through pilot unchanged'},
        {'operation': 'omit both H15 countersinks; retain plain Ø3.4 holes',
         'feature': 'keeperCountersink0/1', 'old_cone_x_interval_mm': [-23,-21.5], 'old_cone_radii_mm': [3,1.5]},
        {'operation': 'reverse both unchanged nominal M3x8 screw envelopes aboutX-20',
         'refs': ['H160','H161'], 'new_head_face_x_mm': -17, 'new_tip_x_mm': -25,
         'new_shaft_x_interval_mm': [-25,-18.4], 'new_head_cone_x_interval_mm': [-18.5,-17],
         'new_head_cone_radii_mm': [1.5,3], 'approach': '+X sensor side after removing sensor/yoke stack'},
        {'operation': 'relocate both unchanged nominal M3 square nuts behind H15',
         'refs': ['H170','H171'], 'old_x_interval_mm': [-17.9,-16.1], 'new_x_interval_mm': [-24.8,-23],
         'centers_yz_mm': [[-11,24],[11,24]], 'nut_body_af_mm': 5.5, 'nominal_full_engagement_mm': 1.8,
         'nominal_screw_tip_excess_mm': 0.2, 'retention': 'not captive; counterhold with slim AF5.5 open-end wrench'},
        {'operation': 'UNION after audit/electronics construction',
         'feature': 'integratePalmIntoFrame', 'inputs': ['P01 construction region','P02 construction region'],
         'result': 'P01 exactly one solid', 'assertions': ['2 input solids','1 final solid']},
    ],
    'unchanged_geometry_contract': [
        'All R9 bodies other than P01/P02/H15/H160/H161/H170/H171 retain their exact construction code.',
        'P02 wrist half-round, R8 cover, R9 R1.2 root blends and wrist/envelope datums are retained; the central lower front plate has the service notch and obsolete M4 foot/ear/drop fronts shorten toX-17.',
        'Two M2 electronics mounting pilots remain; they attach the enclosure, not the palm to the frame.',
        'P08/P09 and0.6 mm nominal cover/lid gap remain separate and unchanged.',
        'No P03 sleeve existed in R9 and none is introduced in R10.',
        'No moving/sensor/keeper/electronics part is fused; central keeper/adjuster opening remains and gains only the lower palm-side notch.',
    ],
    'audit_strategy': {
        'when': 'before final union, after all mechanism transformations; electronics audit also before final union',
        'regions': 'separate P01/P02 construction solids including the intentional positive connecting overlap',
        'removed_pair': 'Palm support / base (planned internal interface only)',
        'all_other_pairs': 'unchanged region-specific queries and contact policies',
        'reason': 'after UNION qCreatedBy(palmPad) can trace entire P01; pre-union tests avoid self-pairs and broad allowed-contact policies',
        'post_union_checks': 'exactly one final integrated solid; no region-based collision audit after union',
    },
    'service_change': {
        'palm': 'P02 cannot lift off; R9 palm/case40 mm upward-removal route is invalid.',
        'nominal_candidate_sequence': [
            'Unload and restrain mechanism; reset sensor preload to0 before cassette-retainer service.',
            'Approach H18 retainers with standard2.5mm hex from outside ±Y through the Ø6.4 front rod-block passages; remove H18 screws and H19 spacers.',
            'Release sensor/yoke stack forward+3.2mmX, then lift+40mmZ using the separately validated route.',
            'Approach H160/H161 from +X sensor side; counterhold H170/H171 from above.',
            'Remove both M3x8 screws toward +X and remove both rear square nuts from above.',
            'Translate H15 by-2 mmX, then lift+35 mmZ; reverse for installation.',
            'Enclosure P08/P09 remains independently detachable below fixed palm; do not force lid against cover.',
        ],
        'counterhold_tool_requirement': 'AF5.5 open-end wrench, maximum2 mm head thickness and maximum13 mm head width; rear4 mm nominal gap. Tool procurement and physical fit require confirmation.',
        'validation_status': 'Independent BRep/continuous/tool-path checks pending; sequence is not yet a verified claim.',
    },
    'qualification': 'Nominal source candidate only. Native regeneration, CSG identity, continuous motion, assembly/service access and printability are pending. No physical strength or500 N load qualification.',
    'changes': changes,
}
(HERE / 'source-build.json').write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + '\n')
print(json.dumps({k: manifest[k] for k in ['file','sha256','bytes','status']}, indent=2))
