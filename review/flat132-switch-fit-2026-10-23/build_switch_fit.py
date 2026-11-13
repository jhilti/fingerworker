#!/usr/bin/env python3
"""Build separate R4 switch-fit source from the immutable R3 palm-fit source."""
from pathlib import Path
from hashlib import sha256
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASELINE = ROOT / "review/flat132-palm-fit-2026-10-23/fingerworker_flat132_palm_fit.fs"
BASELINE_SHA = "4665c3ec4e983e478d34c6cfe923b3b60e6c8848f36b7c54b55b1989eaab6326"
PROPOSAL = ROOT / "review/actual-switch-cad-2026-10-23/switch-fit-proposal.json"
OUTPUT = HERE / "fingerworker_flat132_switch_fit.fs"

data = BASELINE.read_bytes()
assert sha256(data).hexdigest() == BASELINE_SHA, "Frozen R3 source changed"
proposal = json.loads(PROPOSAL.read_text())
assert proposal["preferred_delta_mm"] == [4, 1, 1.5]
assert proposal["local_mesh_check"]["checks_count"] == 62
assert proposal["local_mesh_check"]["positive_volume_conflicts"] == 0
source = data.decode()
changes = []


def replace(label, old, new):
    global source
    count = source.count(old)
    assert count == 1, (label, count)
    source = source.replace(old, new, 1)
    changes.append({"label": label, "count": count, "old": old, "new": new})


replace(
    "identify new drawing-based R4 candidate",
    " * Fingerworker MVP - reviewed development prototype; load rating unverified.",
    " * Fingerworker MVP - R4 switch-fit drawing-based prototype; load rating unverified.\n"
    " * R4 2026-10-23: SS-01GL2 manufacturer DRAWING clearance reference.\n"
    " * Main body, three solder-tab boxes and a conservative lower-lug strip\n"
    " * share H09. Lever motion remains approximate; no factory STEP claim.\n"
    " * Switch moves +4 X / +1 Y / +1.5 Z mm; manual cam is M3x8.\n"
    " * Preserve the R3 palm fit and the R2 sensor-force path and travel limits.\n"
    " * Native regeneration and full validation are required before release.",
)
replace(
    "remove obsolete one-mm projecting cam nub",
    'makeBox(context,id + "switchCam",vector(64,-2,7)*mm,vector(78,8,15)*mm);',
    'makeBox(context,id + "switchCam",vector(65,-2,7)*mm,vector(78,8,15)*mm);',
)
replace(
    "update historical stop-flare clearance comment for shifted switch",
    "            // Inner flare starts0.5 mm ahead of the fixed switchcaseX24.2.",
    "            // R2 flare X24.7 is retained; the shifted R4 case overlaps in X\n"
    "            // and clears the negative stop by1 mm in Y (case-16, stop-17).",
)
replace(
    "coordinated recessed M3x8 cam and guide-preserving insert pocket",
    '''        // MANUAL click-cam setup: after changing preload, back out the M3x12
        // screw by the same axial distance as that preload. This model shows
        // the required configured position X60-preload; there is no automatic
        // physical coupling. Check switch operation and re-lock before use.
        makeCylinder(context,id + "camScrew",vector(60,2.5,10)*mm,vector(63,2.5,10)*mm,2.75*mm);
        makeCylinder(context,id + "camScrewShank",vector(62.9,2.5,10)*mm,vector(75,2.5,10)*mm,1.5*mm);
        join(context,id + "joinCamScrew",[body(id + "camScrew"),body(id + "camScrewShank")]);
        makeCylinder(context,id + "camInsertTool",vector(63.8,2.5,10)*mm,vector(69,2.5,10)*mm,2.1*mm);
        makeCylinder(context,id + "camThroughTool",vector(63,2.5,10)*mm,vector(76.5,2.5,10)*mm,1.7*mm);
        cut(context,id + "camMount",body(id + "carriageBridge"),qUnion([body(id + "camInsertTool"),body(id + "camThroughTool")]));
        movingBodies=append(movingBodies,body(id + "camScrew"));
        nameBody(context,body(id + "camScrew"),"H10 M3 x12 manual click cam - reset by preload amount");''',
    '''        // MANUAL click-cam setup: after changing preload, back out the M3x8
        // screw by the same axial distance as that preload. This model shows
        // the required configured position X64-preload; there is no automatic
        // physical coupling. Check switch operation and re-lock before use.
        // The shifted switch and cam retain one-mm NOMINAL trip lead only.
        // OP tolerance and actual total travel require physical calibration.
        makeCylinder(context,id + "camScrew",vector(64,3.5,11.5)*mm,vector(67,3.5,11.5)*mm,2.75*mm);
        makeCylinder(context,id + "camScrewShank",vector(66.9,3.5,11.5)*mm,vector(75,3.5,11.5)*mm,1.5*mm);
        join(context,id + "joinCamScrew",[body(id + "camScrew"),body(id + "camScrewShank")]);
        // Diameter5.8 head recess leaves1.3 mm above female guide roofZ7.3.
        // Nominal L4 M3 insert is flush atX68 and endsX72; pilot endsX73.
        // Pilot fit and the setting lock remain dependent on actual hardware.
        makeCylinder(context,id + "camHeadReliefTool",vector(63.8,3.5,11.5)*mm,vector(68,3.5,11.5)*mm,2.9*mm);
        makeCylinder(context,id + "camInsertTool",vector(67.8,3.5,11.5)*mm,vector(73,3.5,11.5)*mm,2.1*mm);
        makeCylinder(context,id + "camThroughTool",vector(63,3.5,11.5)*mm,vector(76.5,3.5,11.5)*mm,1.7*mm);
        cut(context,id + "camMount",body(id + "carriageBridge"),qUnion([body(id + "camHeadReliefTool"),body(id + "camInsertTool"),body(id + "camThroughTool")]));
        movingBodies=append(movingBodies,body(id + "camScrew"));
        nameBody(context,body(id + "camScrew"),"H10 M3 x8 recessed manual click cam - reset by preload amount");''',
)
replace(
    "drawing-based switch, supported pedestal, tabs, lug and approximate motion",
    '''        // SS-01GL2 laid on its broad face: only 6.4 mm above the base. Actual
        // case and mounting dimensions; hinge is an illustrative approximation.
        // The manually reset cam preserves the original one-mm trip margin:
        // cam faceX60-preload-stroke reachesX30 at the integral stop.
        makeBox(context,id + "switchPedestal",vector(13,-18,3.8)*mm,vector(25,4,6)*mm);
        baseBodies=append(baseBodies,body(id + "switchPedestal"));
        makeBox(context,id + "switchBody",vector(14,-17,6)*mm,vector(24.2,2.8,12.4)*mm);
        for (var y in [-11.9,-2.4])
        {
            const s=y == -11.9 ? "0" : "1";
            makeCylinder(context,id + ("switchMountHole"~s),vector(16.5,y,5)*mm,vector(16.5,y,13)*mm,1.175*mm);
            cut(context,id + ("switchDrill"~s),body(id + "switchBody"),body(id + ("switchMountHole"~s)));
            makeCylinder(context,id + ("switchInsert"~s),vector(16.5,y,2)*mm,vector(16.5,y,6.2)*mm,1.6*mm);
            insertTools=append(insertTools,body(id + ("switchInsert"~s)));
        }
        const leverLength=sqrt(3.1*3.1+16.7*16.7)*mm;
        const rollerX=min(33.4*mm,60*mm-stroke-preload-2.4*mm);
        const rollerY=-14.1*mm+sqrt(leverLength*leverLength-(rollerX-25.5*mm)*(rollerX-25.5*mm));
        makeCylinder(context,id + "switchLever",vector(25.5,-14.1,9.2)*mm,
            vector(rollerX,rollerY,9.2*mm),0.45*mm);
        makeCylinder(context,id + "switchRoller",vector(rollerX,rollerY,7.6*mm),
            vector(rollerX,rollerY,10.8*mm),2.4*mm);
        nameBody(context,body(id + "switchBody"),"H09 Omron SS-01GL2 - flat mounting");
        nameBody(context,body(id + "switchLever"),"H09a Switch lever preview");
        nameBody(context,body(id + "switchRoller"),"H09b Switch roller preview");''',
    '''        // SS-01GL2 manufacturer DRAWING reference: no factory STEP claim.
        // Omron B032-E1 pages4/6: major body19.8 x10.2 x6.4, two9.5-spaced
        // mounts, three solder tabs and0.4 mm lower-lug projection.
        // Exact terminal holes/corners and lug width/profile are unspecified;
        // use solid tab boxes and a conservative full-housing-width lug strip.
        // The strip assumes the lug stays within the stated6.4 mm thickness.
        // Shift +4 X / +1 Y / +1.5 Z clears the intact P05 force web.
        // Extend the pedestal upward from the base; do not lift its bottom.
        // Trim Ymin to-16.5 for0.5 mm stop gap and0.5 mm body support margin.
        makeBox(context,id + "switchPedestal",vector(17,-16.5,3.8)*mm,vector(29,5,7.5)*mm);
        baseBodies=append(baseBodies,body(id + "switchPedestal"));
        makeBox(context,id + "switchBody",vector(18,-16,7.5)*mm,vector(28.2,3.8,13.9)*mm);
        var switchReferenceBodies=[body(id + "switchBody")];
        var terminalIndex=0;
        for (var terminalY in [-14.4,-5.6,1.7])
        {
            makeBox(context,id + ("switchTerminalEnvelope"~terminalIndex),
                vector(14.1,terminalY-0.25,9.1)*mm,vector(18,terminalY+0.25,12.3)*mm);
            switchReferenceBodies=append(switchReferenceBodies,
                body(id + ("switchTerminalEnvelope"~terminalIndex)));
            terminalIndex+=1;
        }
        makeBox(context,id + "switchLugEnvelope",vector(17.6,-16,7.5)*mm,vector(18,3.8,13.9)*mm);
        switchReferenceBodies=append(switchReferenceBodies,body(id + "switchLugEnvelope"));
        join(context,id + "joinSwitchDrawingReference",switchReferenceBodies);
        for (var y in [-10.9,-1.4])
        {
            const s=y == -10.9 ? "0" : "1";
            makeCylinder(context,id + ("switchMountHole"~s),vector(20.5,y,6.5)*mm,vector(20.5,y,14.5)*mm,1.175*mm);
            cut(context,id + ("switchDrill"~s),body(id + "switchBody"),body(id + ("switchMountHole"~s)));
            // Four-mm blind pilot fromZ7.5; nominal L3 M2 insert endsZ4.5.
            // M2x10/washer engagement is unchanged; match actual insert stock.
            makeCylinder(context,id + ("switchInsert"~s),vector(20.5,y,3.5)*mm,vector(20.5,y,7.7)*mm,1.6*mm);
            insertTools=append(insertTools,body(id + ("switchInsert"~s)));
        }
        // Illustrative fixed-length motion, not the real formed0.3 mm lever.
        // Manufacturer OP14.5 +/-0.8 is measured from mount lineX20.5.
        // Cam faceX64-preload-stroke reachesX34 at the integral stop:
        // one-mm nominal trip lead only; calibrate and check actual overtravel.
        const leverLength=sqrt(3.1*3.1+16.7*16.7)*mm;
        const rollerX=min(37.4*mm,64*mm-stroke-preload-2.4*mm);
        const rollerY=-13.1*mm+sqrt(leverLength*leverLength-(rollerX-29.5*mm)*(rollerX-29.5*mm));
        makeCylinder(context,id + "switchLever",vector(29.5,-13.1,10.7)*mm,
            vector(rollerX,rollerY,10.7*mm),0.45*mm);
        makeCylinder(context,id + "switchRoller",vector(rollerX,rollerY,9.1*mm),
            vector(rollerX,rollerY,12.3*mm),2.4*mm);
        nameBody(context,body(id + "switchBody"),"H09 Omron SS-01GL2 DRAWING REF - solder tabs and conservative lug envelope");
        nameBody(context,body(id + "switchLever"),"H09a SS-01GL2 approximate lever motion - drawing reference");
        nameBody(context,body(id + "switchRoller"),"H09b SS-01GL2 nominal roller - approximate motion");''',
)

# Preserve high-value geometry source exactly; only the stale R2 stop comment changes.
def without_comment_lines(block):
    return "\n".join(line for line in block.splitlines()
                     if not line.lstrip().startswith("//"))


for start, end, label, comments_changed in [
    ('        // Floating spring yoke:', '        // One M6x1 screw', 'P05 central force web', False),
    ('        // Broad integral PRINTED sensing stops', '        // SS-01GL2', 'P05 integral stops', True),
    ('        // Flat132 detachable palm:', '        // Carriage:', 'R3 palm and mounts', False),
]:
    a = data.decode().split(start, 1)[1].split(end, 1)[0]
    b = source.split(start, 1)[1].split(end, 1)[0]
    if comments_changed:
        a, b = without_comment_lines(a), without_comment_lines(b)
    assert a == b, label
assert source.count('nameBody(context,body(id + "switchBody")') == 1
assert source.count('nameBody(context,body(id + "switchLever")') == 1
assert source.count('nameBody(context,body(id + "switchRoller")') == 1
assert 'const maxDynamicTravel = 30 * mm - preload;' in source
assert 'const stroke = definition.isometricLock ? 15 * mm - preload : definition.previewTravel;' in source

OUTPUT.write_text(source)
result = {
    "file": OUTPUT.name,
    "bytes": len(OUTPUT.read_bytes()),
    "sha256": sha256(OUTPUT.read_bytes()).hexdigest(),
    "baseline_source": str(BASELINE.relative_to(ROOT)),
    "baseline_source_sha256": BASELINE_SHA,
    "proposal": str(PROPOSAL.relative_to(ROOT)),
    "proposal_sha256": sha256(PROPOSAL.read_bytes()).hexdigest(),
    "status": "DRAWING_BASED_SOURCE_CANDIDATE_NATIVE_REGEN_AND_VALIDATION_PENDING",
    "manufacturer_geometry_status": "No factory STEP. H09 is a joined manufacturer-drawing clearance reference; exact terminal/lug profiles are not claimed. H09a/H09b motion remains approximate.",
    "expected_device_parts": 52,
    "expected_total_with_electronics": 105,
    "expected_modified_parts": ["P01", "P04", "H09", "H09a", "H09b", "H10"],
    "switch_body_inventory": ["H09", "H09a", "H09b"],
    "source_preservation_assertions": ["P05 central force web byte-identical", "P05 integral sensing stops exact comment-stripped source identical; stale clearance comment updated", "R3 palm and mounting source byte-identical", "30-preload dynamic and15-preload isometric travel retained"],
    "preliminary_local_mesh_checks": {"count": 62, "positive_volume_conflicts": 0, "scope": "Prior local source-equivalent contact-region study; not native R4 or full-assembly validation"},
    "hardware_delta": "H10 M3x12 -> M3x8, same nominal diameter5.5 x3 head; other screw/washer/insert intent retained pending stock matching",
    "clearances_nominal_mm": {"terminal_to_P05_at_preload2": 3.1, "switch_body_to_negative_stop": 1.0, "pedestal_to_negative_stop": 0.5, "cam_head_radial": 0.15, "head_recess_to_female_guide_roof": 1.3},
    "qualifications": ["Native regeneration and whole-assembly/motion/service checks required", "Actual insert and screw/head/washer dimensions required", "Solder/wire bend/insulation and strain relief remain unqualified", "Switch OP tolerance, total travel, manual cam reset and setting lock require physical checks", "NC fail-safe and firmware behavior unchanged; CAD does not enable force display", "500 N target remains physically unqualified"],
    "changes": changes,
}
(HERE / "source-build.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({k: result[k] for k in ["file", "bytes", "sha256", "status", "expected_total_with_electronics"]}, indent=2))
