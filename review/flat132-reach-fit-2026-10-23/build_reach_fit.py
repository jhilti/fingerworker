#!/usr/bin/env python3
"""Build local R5 reach-fit CAD study from immutable R4; no cloud actions."""
from pathlib import Path
from hashlib import sha256
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROJECT_BASE = ROOT / "review/flat132-switch-fit-2026-10-23/fingerworker_flat132_switch_fit.fs"
BUNDLED_BASE = HERE / "reference/baseline/fingerworker_flat132_switch_fit.fs"
BASE = PROJECT_BASE if PROJECT_BASE.is_file() else BUNDLED_BASE
BASE_SHA = "b150ff3a76cfaaaaa65ee1ea09e144b7c7d64e45459a925163e56918f48bb3c5"
OUT = HERE / "fingerworker_flat132_reach_fit.fs"
raw = BASE.read_bytes()
assert sha256(raw).hexdigest() == BASE_SHA
source = raw.decode()
changes = []


def replace(label, old, new):
    global source
    count = source.count(old)
    assert count == 1, (label, count)
    source = source.replace(old, new, 1)
    changes.append({"label": label, "count": count, "old": old, "new": new})


def block(label, start, end, new):
    a = source.index(start)
    b = source.index(end, a)
    replace(label, source[a:b], new)


replace("R5 CAD study identification", " * Fingerworker MVP - R4 switch-fit drawing-based prototype; load rating unverified.",
        " * Fingerworker MVP - R5 reach-fit CAD STUDY; load rating unverified.\n"
        " * R5: dynamic rest and end grip5 mm closer; full30-preload user travel.\n"
        " * Carriage absolute offset q=5+u; retained86 mm ISO sleeves use q=15-p\n"
        " * and user-relative approach u=10-p. ISO grip position is unchanged.\n"
        " * New guided P11 cam shoe is manually set to camTrim-preload.\n"
        " * Added pretension, return bosses and print joints need physical checks.\n"
        " * This local source is not a validated or strength-qualified release.")
replace("feature name", '"Feature Name Template" : "Flat132 actual sensor - 30 mm travel"',
        '"Feature Name Template" : "Flat132 R5 reach study - 5 mm closer and full travel"')
replace("current clamp identification", ' * Switch moves +4 X / +1 Y / +1.5 Z mm; manual cam is M3x8.',
        ' * Fixed switch keeps its R4 +4 X / +1 Y / +1.5 Z mm location.\n'
        ' * R5 replaces the former horizontal M3x8 cam with a P11 shoe and\n'
        ' * a vertical M3x10 clamp; actual adjustment remains manual.')
replace("user travel label", '"Frame travel (0 to 30 mm minus preload; reset click cam after preload)"',
        '"User travel from closer rest (0 to 30 mm minus preload; reset cam shoe)"')
replace("cam trim parameter", '        isLength(definition.preloadAdjustment, LENGTH_BOUNDS);',
        '        isLength(definition.preloadAdjustment, LENGTH_BOUNDS);\n'
        '        annotation { "Name" : "Cam trim (-0.8 to +0.8 mm; physical calibration)" }\n'
        '        isLength(definition.camTrim, { (millimeter) : [-0.8, 0, 0.8] } as LengthBoundSpec);')
replace("ISO label", '"Isometric mode: replace BOTH springs with 86 mm steel sleeves"',
        '"Isometric: BOTH existing86 mm sleeves; approach8-10 mm from closer rest"')
block("closer rest and absolute carriage motion",
      '        // Fixed-length compression locks set the grip position geometrically.',
      '        // Fixed dimensions form a coordinated prototype, not independent knobs.',
      '''        // q is absolute carriage displacement from the R4 rest. User travel
        // u starts at the new5 mm closer rest; full dynamic travel is retained.
        const restOffset=5*mm;
        const camTrim=definition.camTrim;
        if (camTrim < -0.8*mm || camTrim > 0.8*mm)
            throw regenError("Cam trim must be between-0.8 and+0.8 mm.",["camTrim"]);
        const maxDynamicTravel = 30 * mm - preload;
        if (!definition.isometricLock && definition.previewTravel > maxDynamicTravel + 1e-6*mm)
            throw regenError("R5 user travel remains30 mm minus preload. Use28 mm at2 mm preload; manually reset the shoe by minus the preload change.", ["previewTravel", "preloadAdjustment"]);
        // Retain the actual86 mm sleeves and their original absolute grip.
        // They seat after u=10-preload, not15-preload from the new rest.
        const stroke = definition.isometricLock ? 15 * mm - preload : restOffset+definition.previewTravel;
        const userTravel=stroke-restOffset;
        if (stroke < restOffset || stroke > 35*mm)
            throw regenError("R5 absolute carriage offset must be5..35 mm; user travel must be nonnegative.", ["previewTravel"]);

''')

cam = '''        // P11 is a manually positioned, top-clamped cam shoe. It carries
        // switch actuation only; it is outside the500 N sensor force path.
        // k=camTrim-preload represents physical setting, not automatic coupling.
        // The entire old horizontal cam bore is omitted, restoring that stock.
        makeBox(context,id + "camShoeWell",vector(64,-1,8.6)*mm,vector(74.8,8,19)*mm);
        makeBox(context,id + "camLeverRelief",vector(64,-14,8.6)*mm,vector(67.2,8,19)*mm);
        // Roof slot covers e-p=-2.8..+0.8; head is recessed below the rolled lip.
        makeCylinder(context,id + "camRoofSlot0",vector(67.7,3.5,18.9)*mm,vector(67.7,3.5,25.2)*mm,1.7*mm);
        makeCylinder(context,id + "camRoofSlot1",vector(71.3,3.5,18.9)*mm,vector(71.3,3.5,25.2)*mm,1.7*mm);
        makeBox(context,id + "camRoofSlotMid",vector(67.7,1.8,18.9)*mm,vector(71.3,5.2,25.2)*mm);
        makeCylinder(context,id + "camHeadSlot0",vector(67.7,3.5,25)*mm,vector(67.7,3.5,31)*mm,3*mm);
        makeCylinder(context,id + "camHeadSlot1",vector(71.3,3.5,25)*mm,vector(71.3,3.5,31)*mm,3*mm);
        makeBox(context,id + "camHeadSlotMid",vector(67.7,0.5,25)*mm,vector(71.3,6.5,31)*mm);
        cut(context,id + "camShoeMount",body(id + "carriageBridge"),qUnion([
            body(id + "camShoeWell"),body(id + "camLeverRelief"),
            body(id + "camRoofSlot0"),body(id + "camRoofSlot1"),body(id + "camRoofSlotMid"),
            body(id + "camHeadSlot0"),body(id + "camHeadSlot1"),body(id + "camHeadSlotMid")]));
        makeBox(context,id + "camShoe",vector(69,-0.7,9)*mm,vector(73.5,7.7,19)*mm);
        // Forward upper boss stays above roller topZ12.3 by0.9 mm nominally.
        makeBox(context,id + "camShoeBoss",vector(67.5,-0.7,13.2)*mm,vector(69,7.7,19)*mm);
        join(context,id + "joinCamShoe",[body(id + "camShoe"),body(id + "camShoeBoss")]);
        makeCylinder(context,id + "camShoeInsertPilot",vector(70.5,3.5,14.5)*mm,vector(70.5,3.5,19.2)*mm,2.1*mm);
        cut(context,id + "camShoeInsertCut",body(id + "camShoe"),body(id + "camShoeInsertPilot"));
        // Nominal L4 insert entersZ19 and endsZ15. M3x10 underheadZ25
        // endsZ15: full4 mm thread and0.5 mm gap to pilot floorZ14.5.
        makeCylinder(context,id + "camScrew",vector(70.5,3.5,25)*mm,vector(70.5,3.5,28)*mm,2.75*mm);
        makeCylinder(context,id + "camScrewShank",vector(70.5,3.5,15)*mm,vector(70.5,3.5,25.1)*mm,1.5*mm);
        join(context,id + "joinCamScrew",[body(id + "camScrew"),body(id + "camScrewShank")]);
        nameBody(context,body(id + "camScrew"),"H10 M3 x10 vertical cam-shoe clamp - manual setup");
        nameBody(context,body(id + "camShoe"),"P11 PRINT STUDY - guided stepped cam shoe, manually set trim minus preload");
        finishBody(context,body(id + "camShoe"),color(0.88,0.53,0.20));
        const camShift=camTrim-preload;
        if (camShift != 0*mm)
            opTransform(context,id + "configuredManualCamShoe",{
                "bodies":qUnion([body(id + "camScrew"),body(id + "camShoe")]),
                "transform":transform(vector(camShift,0*mm,0*mm)) });
        movingBodies=append(movingBodies,body(id + "camScrew"));
        movingBodies=append(movingBodies,body(id + "camShoe"));

'''
block("replace horizontal cam entirely with top-clamped stepped shoe",
      '        // MANUAL click-cam setup:', '        // Single32 mm central profile', cam)
replace("retain full front guide bearing overlap", 'makeXPrism(context,id + "centralTrack",34*mm,124*mm,',
        'makeXPrism(context,id + "centralTrack",29*mm,124*mm,')
replace("shorten integral stop faces by5 mm", 'vector(35,y+7,29)*mm);', 'vector(30,y+7,29)*mm);')
replace("new stop relation", '        // FaceX35+preload meets P04front65-stroke: stroke+preload<=30.',
        '        // FaceX30+preload meets P04front65-q: q+preload<=35.\n'
        '        // With q=5+u the retained user travel is u<=30-preload.')
replace("rigid return extensions and shifted TPU pads",
        '''                const padY=y+(offset == -8 ? -7.5 : 7.5);
                makeBox(context,id + ("returnPad"~s~t),vector(124,padY-2.25,14)*mm,vector(125.5,padY+2.25,20)*mm);''',
        '''                const padY=y+(offset == -8 ? -7.5 : 7.5);
                // Five-mm rigid extensions establish the closer rest; retain
                // the original1.5 mm TPU pads, rear screws and guide rods.
                makeBox(context,id + ("rearReturnBoss"~s~t),vector(120.5,padY-2.25,14)*mm,vector(125.6,padY+2.25,20)*mm);
                join(context,id + ("rearReturnBossJoin"~s~t),[body(id + ("rearBlock"~s)),body(id + ("rearReturnBoss"~s~t))]);
                makeBox(context,id + ("returnPad"~s~t),vector(119,padY-2.25,14)*mm,vector(120.5,padY+2.25,20)*mm);''')
replace("retainer name", 'PRINT - removable rear retainer - through holes RevC',
        'PRINT STUDY - rear retainer with5 mm rigid return bosses')
replace("spring rest-force comment", '// Ordered pairs: DF2194 initial compression 1..3 mm; DF2185 4..6 mm; travel 30 mm.',
        '// R5 rest compression: DF2194 6..8 mm; DF2185 9..11 mm; user travel30-preload.')
replace("shoe roller motion", 'const rollerX=min(37.4*mm,64*mm-stroke-preload-2.4*mm);',
        'const rollerX=min(37.4*mm,69*mm+camTrim-stroke-preload-2.4*mm);')
replace("shoe operating comment", '        // Cam faceX64-preload-stroke reachesX34 at the integral stop:',
        '        // Shoe faceX69+camTrim-preload-q reachesX34+camTrim at the stop:')
replace("update switch actuation collision query",
        '        auditSolidPair(context,"Adjustable cam / switch actuator",body(id + "camScrew"),actuator,true),',
        '        auditSolidPair(context,"Cam shoe / switch actuator",body(id + "camShoe"),actuator,true),\n'
        '        auditSolidPair(context,"Cam shoe / carriage well",body(id + "camShoe"),carriage,true),\n'
        '        auditSolidPair(context,"Cam clamp / carriage and shoe",body(id + "camScrew"),qUnion([carriage,body(id + "camShoe")]),true),\n'
        '        auditSolidPair(context,"Cam shoe / fixed mechanism",body(id + "camShoe"),qUnion([base,yoke,palm,sleeve,body(id + "switchBody"),sensor]),false),')
replace("hand absolute offset range", 'const stroke = min(30 * millimeter, max(0 * millimeter, displacement));',
        'const stroke = min(35 * millimeter, max(0 * millimeter, displacement));')
replace("explicit motion and trim diagnostics", '"additionalPreload":preload,"actualStroke":stroke,',
        '"additionalPreload":preload,"actualStroke":stroke,\n'
        '            "userTravelFromCloserRest":userTravel,"restOffset":restOffset,"camTrim":camTrim,')
replace("new parameter default", '}, { "previewTravel":0*millimeter,"preloadAdjustment":0*millimeter,',
        '}, { "previewTravel":0*millimeter,"preloadAdjustment":0*millimeter,"camTrim":0*millimeter,')

# User selected81 mm ISO sleeves after the original86 mm checkpoint.
# Recreate that checkpoint exactly before making an auditable ISO-only delta.
PRIOR_R5_SHA = "61885fd717b30eaf1dfc39a1f7f65f017bfc1b4ac077c3e3493399ef3373a9a3"
assert sha256(source.encode()).hexdigest() == PRIOR_R5_SHA
prior_source = source
prior_path = HERE / "fingerworker_flat132_reach_fit_ISO86_61885fd7.fs"
if prior_path.exists():
    assert sha256(prior_path.read_bytes()).hexdigest() == PRIOR_R5_SHA
else:
    prior_path.write_text(prior_source)
iso81_start = len(changes)
replace("ISO81 header formulas", " * Carriage absolute offset q=5+u; retained86 mm ISO sleeves use q=15-p\n * and user-relative approach u=10-p. ISO grip position is unchanged.",
        " * Carriage absolute offset q=5+u; selected81 mm ISO sleeves use q=20-p\n * and user-relative approach u=15-p. Dynamic and ISO grip are5 mm closer.")
replace("ISO81 inherited header sleeve statement", " * has unqualified stiffness/strength. Palm contact geometry, 86 mm sleeve and\n * electronics enclosure are retained. Remove both M4 bolts and lift the palm",
        " * has unqualified stiffness/strength. Palm contact geometry and electronics\n * enclosure are retained; R5 uses81 mm ISO sleeves. Remove both M4 bolts and lift the palm")
replace("ISO81 selector label", '"Isometric: BOTH existing86 mm sleeves; approach8-10 mm from closer rest"',
        '"Isometric: BOTH81 mm sleeves; approach13-15 mm from closer rest"')
replace("ISO81 conditional position only", "        // Retain the actual86 mm sleeves and their original absolute grip.\n        // They seat after u=10-preload, not15-preload from the new rest.\n        const stroke = definition.isometricLock ? 15 * mm - preload : restOffset+definition.previewTravel;",
        "        // Selected81 mm sleeves move ISO grip5 mm closer than R4.\n        // They seat after u=15-preload from the new closer rest.\n        const stroke = definition.isometricLock ? 20 * mm - preload : restOffset+definition.previewTravel;")
replace("ISO81 purchased sleeve label", 'ISOMETRIC steel compression lock sleeve 16 x 8 x 86 mm',
        'ISOMETRIC steel compression lock sleeve 16 x 8 x 81 mm')
iso81_changes = changes[iso81_start:]
restored = source
for item in reversed(iso81_changes):
    assert restored.count(item["new"]) == 1
    restored = restored.replace(item["new"], item["old"], 1)
assert restored == prior_source
assert 'const stroke = definition.isometricLock ? 20 * mm - preload : restOffset+definition.previewTravel;' in source

# No change is allowed in the primary sensor/yoke web or palm geometry.
original = raw.decode()
for start, end, label in [
    ('        // Floating spring yoke:', '        // One M6x1 screw', 'P05 central force web'),
    ('        // Flat132 detachable palm:', '        // Carriage:', 'R3/R4 palm and mounts'),
]:
    assert original.split(start, 1)[1].split(end, 1)[0] == source.split(start, 1)[1].split(end, 1)[0], label
assert 'vector(8.5,y-5,7)*mm' in source and 'vector(25,y+5,29)*mm' in source
assert 'camHeadReliefTool' not in source and 'camThroughTool' not in source and 'camInsertTool' not in source
assert source.count('{') == source.count('}')
OUT.write_text(source)
result = {
    "file": OUT.name, "sha256": sha256(OUT.read_bytes()).hexdigest(), "bytes": len(OUT.read_bytes()),
    "status": "LOCAL_R5_CAD_STUDY_SOURCE_NATIVE_REGEN_AND_VALIDATION_PENDING",
    "baseline_source": str(BASE.relative_to(ROOT)), "baseline_source_sha256": BASE_SHA,
    "rest_offset_mm": 5, "user_travel": "0<=u<=30-preload", "dynamic_absolute_offset": "q=5+u",
    "preload_mm": [0, 2], "camTrim_mm": [-0.8, 0.8], "camTrim_default_mm": 0,
    "manual_shoe_setting": "k=camTrim-preload; actual operator calibration/reset/clamping required",
    "ISO_selected_sleeves_mm": 81, "ISO_absolute_offset": "q=20-preload", "ISO_user_relative_approach": "u=15-preload; ISO grip5mm closer thanR4",
    "prior_R5_source_snapshot": prior_path.name, "prior_R5_source_sha256": PRIOR_R5_SHA,
    "ISO81_changes_from_prior_R5": iso81_changes,
    "ISO81_inverse_replacement_identity": "PASS_EXACT_RESTORATION_TO_61885_SOURCE",
    "ISO81_dynamic_mode_source_delta": "Only conditional isometric stroke15->20 changes coordinates; false branch restOffset+previewTravel, dynamic expressions and defaults unchanged",
    "ISO_changed_purchased_refs": ["H140", "H141"],
    "ISO_hardware": "Two steel sleeves OD16/ID8/length81 replace former length86; both springs removed in ISO mode",
    "expected_device_parts": 53, "expected_total_with_electronics": 106, "expected_print_parts": 15,
    "added_refs": ["P11"], "H10": "M3x10 vertical clamp; no longer horizontal switch-contact screw",
    "expected_geometry_changed_refs": ["P01", "P04", "P05", "P060", "P061", "H10", "P11"],
    "rest_rigid_pose_changed_refs": ["P04", "P070a", "P070b", "P071a", "P071b", "H060", "H061"],
    "preserved": ["132mm width/72mm clear pocket/35mm envelope", "R4 fixed switch housing, tabs and mounting", "P05 primary web and sensor/cassette/steel force interfaces", "R3/R4 palm7mm fit", "rear screw locations and146mm guide rods", "full dynamic28-30mm travel and all dynamic expressions/defaults", "firmware NC failsafe; no firmware edits"],
    "spring_minimum_length_mm": 66, "physical_500N_qualification": "PENDING", "manufacturing_release": False,
    "remaining_requirements": ["Native regeneration and full u/p/camTrim motion/contact/service validation", "Check raised/lipped pocket access recess and guide-bearing extension", "Actual switch lever/bracket and solder/wire fitting", "Actual insert/screw stock and P11 heat-set/clamp durability", "Printed500N force path, return-bumper creep, fatigue and comfort qualification"],
    "changes": changes,
}
(HERE / "source-build.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({k: result[k] for k in ["file", "sha256", "bytes", "status", "expected_total_with_electronics"]}, indent=2))
