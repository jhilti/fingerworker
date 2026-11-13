#!/usr/bin/env python3
"""Deterministic branch-study FeatureScript derivation. Never edits production."""
from pathlib import Path
import hashlib
import json
import struct

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / "fingerworker_mvp.fs"
EXPECTED_SHA256 = "43a2dc70e3eed4308534da7772f4b82bf845c97d6f6a53456d0d63aa9552fb33"
OUT = HERE / "fingerworker_flat132.fs"
rules = []


def change(label, old, new, count=1):
    rules.append({"label": label, "old": old, "new": new, "count": count})


def js_identity(value):
    """FNV-1a over JavaScript UTF-16 code units, using Math.imul semantics."""
    encoded = value.encode("utf-16-le")
    fnv = 2166136261
    for (code_unit,) in struct.iter_unpack("<H", encoded):
        fnv = ((fnv ^ code_unit) * 16777619) & 0xffffffff
    return {"utf16Length": len(encoded) // 2, "fnv1a32": f"{fnv:08x}",
            "sha256Utf8": hashlib.sha256(value.encode("utf-8")).hexdigest()}


change("study header", """ * Revision 2026-10-17 Rev D: 158 mm narrow frame, 92 mm pocket, coordinated 128 mm spring axes; 6 mm base.
 * DEVELOPMENT SOURCE: see DEVICE_UPGRADES.md; old exports are superseded.
 * New geometry requires regeneration and motion verification in Onshape.""", """ * SEPARATE BRANCH STUDY 2026-10-19: flat 132 mm frame, 72 mm clear pocket,
 * 84 mm deck, 102 mm spring-axis spacing, 6 mm base, 32 mm total height.
 * P01/P02 are one integral printed frame and palm support; the existing palm
 * contact geometry, 86 mm sleeve and electronics enclosure are retained.
 * Derived from protected Rev D; this study does not supersede production files.
 * Native regeneration, motion/assembly checks and physical strength validation
 * are required. No tested load capacity or functional equivalence is claimed.""")

# Final integral frame is audited as one rigid body, without self-pairs or
# empty historical P02 queries. Intended contacts retain their original row.
change("remove obsolete separate-palm audit query", '    const palm = body(id + "palmPad");\n', '')
change("keeper forbidden-contact targets", 'auditSolidPair(context,"Keeper hardware / moving stack and palm",keeperHardware,qUnion([body(id + "sensorCassette"),yoke,palm,sleeve]),false)', 'auditSolidPair(context,"Keeper hardware / moving stack and sleeve",keeperHardware,qUnion([body(id + "sensorCassette"),yoke,sleeve]),false)')
change("capture forbidden-contact targets", 'qUnion([palm,sleeve,yoke,carriage,rods,sensor,body(id + "preloadScrew"),keeperHardware])', 'qUnion([sleeve,yoke,carriage,rods,sensor,body(id + "preloadScrew"),keeperHardware])')
change("adjuster moving targets", 'auditSolidPair(context,"Adjustment hardware / yoke carriage palm",qUnion([body(id + "preloadScrew"),\n            body(id + "preloadNut"),body(id + "nutKeeper"),body(id + "sensorCassette")]),qUnion([yoke,carriage,palm]),false)', 'auditSolidPair(context,"Adjustment hardware / yoke carriage sleeve",qUnion([body(id + "preloadScrew"),\n            body(id + "preloadNut"),body(id + "nutKeeper"),body(id + "sensorCassette")]),qUnion([yoke,carriage,sleeve]),false)')
change("remove duplicate preload-frame audit", '        auditSolidPair(context,"Preload screw / palm",body(id + "preloadScrew"),palm,false),\n', '')
change("spring structure final frame", 'qUnion([base,yoke,carriage,rear,rods,palm,sleeve])', 'qUnion([base,yoke,carriage,rear,rods,sleeve])', 2)
change("yoke final frame", 'auditSolidPair(context,"Yoke / base rods and palm",yoke,qUnion([base,rods,palm,sleeve]),false)', 'auditSolidPair(context,"Yoke / integral frame rods and sleeve",yoke,qUnion([base,rods,sleeve]),false)')
change("integral support audit semantics", '''        auditSolidPair(context,"Palm support / base",palm,base,true),
        auditSolidPair(context,"Palm / carriage and switch",qUnion([palm,sleeve]),qUnion([carriage,body(id + "switchBody"),actuator]),false),
        auditSolidPair(context,"Palm sleeve / rigid support",sleeve,palm,true),''', '''        // Palm support is integral with base: no self-pair or missing P02 query.
        auditSolidPair(context,"Palm sleeve / carriage and switch",sleeve,qUnion([carriage,body(id + "switchBody"),actuator]),false),
        auditSolidPair(context,"Switch case and actuator / integral frame",qUnion([body(id + "switchBody"),actuator]),base,true),
        auditSolidPair(context,"Palm sleeve / integral rigid support",sleeve,base,true),''')

change("feature branch name", 'annotation { "Feature Type Name" : "FingerworkerMVP", "Feature Name Template" : "Fingerworker 30 mm printable" }', 'annotation { "Feature Type Name" : "FingerworkerFlat132Study", "Feature Name Template" : "Flat132 study 30 mm" }')
change("envelope comment", '// Envelope178.25 x158 x32; base156 x158, floor6 (Z-2 to Z4); pocket20 deep, floor2.7 above guide.', '// Envelope180.1 x132 x32 including enclosure; base156 x132, floor6 (Z-2 to Z4); pocket20 deep, floor2.7 above guide.')
change("base width", 'makeBox(context,id + "base",vector(-22,-79,-2)*mm,vector(134,79,4)*mm);', 'makeBox(context,id + "base",vector(-22,-66,-2)*mm,vector(134,66,4)*mm);')
change("base window negative outer", 'const lowY=side == -1 ? -51 : 27;', 'const lowY=side == -1 ? -38 : 27;')
change("base window positive outer", 'const highY=side == -1 ? -27 : 51;', 'const highY=side == -1 ? -27 : 38;')
change("remove old palm feet", '''        // The roller is entirely outside the wrist end of the frame.
        // Wrist-facing contact X-44.25, crown Z30. Two mounting ears return
        // to the base outside the sensor wall and stop before the moving yoke.
        makeBox(context,id + "palmFootLeft",vector(-21,-50,3.8)*mm,vector(-8,-29,9.5)*mm);
        makeBox(context,id + "palmFootRight",vector(-21,29,3.8)*mm,vector(-8,50,9.5)*mm);
        baseBodies=append(baseBodies,body(id + "palmFootLeft"));
        baseBodies=append(baseBodies,body(id + "palmFootRight"));''', '''        // Flat132: fixed palm and frame form one printed body. Two wristward
        // raised bridges overlap the sensor wall at X[-22,-18.5], |Y|17..24.
        // They clear the enclosure lid Z8.9 by0.6, H15 |Y|16 by1, front rod
        // blocks X-18 by0.5, and capture-head minimum X-15.75 by2.75.
        // Bridge/joint strength remains unqualified; no old four-M4 mount.
        makeBox(context,id + "palmBridgeLeft",vector(-26,-33,9.5)*mm,vector(-18.5,-17,14.5)*mm);
        makeBox(context,id + "palmBridgeRight",vector(-26,17,9.5)*mm,vector(-18.5,33,14.5)*mm);
        baseBodies=append(baseBodies,body(id + "palmBridgeLeft"));
        baseBodies=append(baseBodies,body(id + "palmBridgeRight"));''')
change("remove palm ears", '''        makeBox(context,id + "palmEarLeft",vector(-30,-50,9.5)*mm,vector(-8,-29,14.5)*mm);
        makeBox(context,id + "palmEarRight",vector(-30,29,9.5)*mm,vector(-8,50,14.5)*mm);
''', '')
change("palm join geometry", '''        join(context,id + "palmJoin",[body(id + "palmPad"),body(id + "palmBolsterCore"),
            body(id + "palmEarLeft"),body(id + "palmEarRight")]);''', '''        join(context,id + "palmJoin",[body(id + "palmPad"),body(id + "palmBolsterCore")]);''')
change("keeper plate service notch", '''        // Electronics enclosure M2 insert pilots in underside of fixed palm.
''', '''        // Service notch clears the keeper plate's wristward disengagement.
        // Retained core ends at X-26.25; this notch starts at X-24.4, clear1.85.
        // Bridge inner |Y|17 remains0.7 beyond the notch |Y|16.3.
        makeBox(context,id + "keeperPalmServiceTool",vector(-24.4,-16.3,9.4)*mm,
            vector(-23.0,16.3,14.6)*mm);
        cut(context,id + "keeperPalmServiceCut",body(id + "palmPad"),
            body(id + "keeperPalmServiceTool"));
        // Electronics enclosure M2 insert pilots in underside of fixed palm.
''')
change("remove four-M4 mounts", '''        var insertTools=[];
        var palmTools=[];
        var n=0;
        for (var x in [-15])
        {
            for (var y in [-45,-34,34,45])
            {
                makeCylinder(context,id + ("palmInsert"~n),vector(x,y,2.5)*mm,vector(x,y,10.5)*mm,2.6*mm);
                insertTools=append(insertTools,body(id + ("palmInsert"~n)));
                makeCylinder(context,id + ("palmHole"~n),vector(x,y,8.5)*mm,vector(x,y,31)*mm,2.2*mm);
                palmTools=append(palmTools,body(id + ("palmHole"~n)));
                makeCylinder(context,id + ("palmHead"~n),vector(x,y,13.5)*mm,vector(x,y,31)*mm,4*mm);
                palmTools=append(palmTools,body(id + ("palmHead"~n)));
                n+=1;
            }
        }
        cut(context,id + "palmMountHoles",body(id + "palmPad"),qUnion(palmTools));''', '''        var insertTools=[];
        var n=0;
        // P01/P02 are united below after all fixed frame elements exist.''')
change("temporary palm name", 'nameBody(context,body(id + "palmPad"),"P02 PRINT - rounded palm bolster");', 'nameBody(context,body(id + "palmPad"),"P02 STUDY intermediate palm - united into P01");')
change("rear bridge width", 'makeBox(context,id + "carriageBridge",vector(116,-76,5)*mm,vector(124,76,24)*mm);', 'makeBox(context,id + "carriageBridge",vector(116,-63,5)*mm,vector(124,63,24)*mm);')
change("arm negative outer/positive inner", 'const loY = side == -1 ? -76 : 53;', 'const loY = side == -1 ? -63 : 40;')
change("arm negative inner/positive outer", 'const hiY = side == -1 ? -53 : 76;', 'const hiY = side == -1 ? -40 : 63;')
change("central click cam", 'makeBox(context,id + "switchCam",vector(64,-39,7)*mm,vector(78,-29,15)*mm);', 'makeBox(context,id + "switchCam",vector(64,-2,7)*mm,vector(78,8,15)*mm);')
change("deck width", 'makeBox(context,id + "climbingDeck",vector(65,-52,5)*mm,vector(124,52,30)*mm);', 'makeBox(context,id + "climbingDeck",vector(65,-42,5)*mm,vector(124,42,30)*mm);')
change("pocket width", 'makeBox(context,id + "pocketTool",vector(77,-46,10)*mm,vector(111,46,36)*mm);', 'makeBox(context,id + "pocketTool",vector(77,-36,10)*mm,vector(111,36,36)*mm);')
change("local moving-seat clearance", '''        movingBodies=append(movingBodies,body(id + "carriageBridge"));
        nameBody(context,body(id + "carriageBridge"),"P04 PRINT - RevD 92 mm clear climbing pocket and narrow central slider");''', '''        // R12 clearance lies entirely behind pocket X111. Steel seat OD22
        // occupies X113..116; retain its X116 planar reaction datum.
        for (var side in [-1,1])
        {
            const t=side == -1 ? "0" : "1";
            makeCylinder(context,id + ("movingSeatRelief"~t),
                vector(112,side*51,18)*mm,vector(116,side*51,18)*mm,12*mm);
            cut(context,id + ("movingSeatReliefCut"~t),body(id + "carriageBridge"),
                body(id + ("movingSeatRelief"~t)));
        }
        movingBodies=append(movingBodies,body(id + "carriageBridge"));
        nameBody(context,body(id + "carriageBridge"),"P04 PRINT STUDY - Flat132 72 mm clear pocket, R12 seat reliefs");''')
change("cam screw head center", 'vector(60,-34.5,10)*mm,vector(63,-34.5,10)*mm', 'vector(60,2.5,10)*mm,vector(63,2.5,10)*mm')
change("cam screw shank center", 'vector(62.9,-34.5,10)*mm,vector(75,-34.5,10)*mm', 'vector(62.9,2.5,10)*mm,vector(75,2.5,10)*mm')
change("cam insert center", 'vector(63.8,-34.5,10)*mm,vector(69,-34.5,10)*mm', 'vector(63.8,2.5,10)*mm,vector(69,2.5,10)*mm')
change("blind cam bore center and end", 'vector(63,-34.5,10)*mm,vector(79,-34.5,10)*mm', 'vector(63,2.5,10)*mm,vector(76.5,2.5,10)*mm')
change("yoke span", 'makeBox(context,id + "springAnchor",vector(-7,-76,7)*mm,vector(9,76,29)*mm);', 'makeBox(context,id + "springAnchor",vector(-7,-63,7)*mm,vector(9,63,29)*mm);')
change("yoke cable relief", 'vector(-1.5,46,21.5)*mm', 'vector(-1.5,40,21.5)*mm')
change("yoke name", '"P05 PRINT - RevD narrow reinforced floating spring yoke"', '"P05 PRINT STUDY - Flat132 reinforced floating spring yoke"')
change("sensor cable route", 'vector(-5.25,39,18)*mm', 'vector(-5.25,33,18)*mm')
change("sensor connector route", 'vector(-8.25,36.5,15)*mm,vector(-2.25,44.5,21)*mm', 'vector(-8.25,30.5,15)*mm,vector(-2.25,38.5,21)*mm')
change("spring rod support axes", 'const y = side*64;', 'const y = side*51;')
change("switch pedestal center shift", 'vector(13,-55,3.8)*mm,vector(25,-33,6)*mm', 'vector(13,-18,3.8)*mm,vector(25,4,6)*mm')
change("switch case center shift", 'vector(14,-54,6)*mm,vector(24.2,-34.2,12.4)*mm', 'vector(14,-17,6)*mm,vector(24.2,2.8,12.4)*mm')
change("switch mount axes shift", 'for (var y in [-48.9,-39.4])', 'for (var y in [-11.9,-2.4])')
change("switch mount suffix shift", 'const s=y == -48.9 ? "0" : "1";', 'const s=y == -11.9 ? "0" : "1";')
change("switch roller hinge shift", 'const rollerY=-51.1*mm+', 'const rollerY=-14.1*mm+')
change("switch lever hinge shift", 'vector(25.5,-51.1,9.2)*mm', 'vector(25.5,-14.1,9.2)*mm')
change("integral palm union", '        join(context,id + "integrateBase",baseBodies);', '''        join(context,id + "integrateBase",baseBodies);
        join(context,id + "integratePalm",[body(id + "base"),body(id + "palmPad")]);''')
change("front bench mount X", 'for (var x in [20,127])', 'for (var x in [16,127])')
change("bench mount Y", 'for (var y in [-10,10])', 'for (var y in [-28,28])')
change("bench common coordinates", 'x < 100 ? y : y*3.9', 'y', 4)
change("integral frame name", '"P01 PRINT - RevD 156 x 158 narrow fixed frame - 6 mm floor, clear rear insertion"', '"P01-P02 PRINT STUDY - Flat132 integral fixed frame and palm support, 6 mm floor"')
change("remove obsolete palm finish query", '        finishBody(context,body(id + "palmPad"),color(0.27,0.32,0.28));\n', '')

# V4 replaces the integral-palm concept: it traps the keeper screws against
# the retained palm core. Keep the real separate-body native audit queries.
omit_v4 = {
    "remove obsolete separate-palm audit query", "keeper forbidden-contact targets",
    "capture forbidden-contact targets", "adjuster moving targets",
    "remove duplicate preload-frame audit", "spring structure final frame",
    "yoke final frame", "integral support audit semantics", "palm join geometry",
    "keeper plate service notch", "integral palm union", "remove obsolete palm finish query",
}
rules = [rule for rule in rules if rule["label"] not in omit_v4]
overrides_v4 = {
    "study header": """ * SEPARATE BRANCH STUDY 2026-10-19: flat 132 mm frame, 72 mm clear pocket,
 * 84 mm deck, 102 mm spring-axis spacing, 6 mm base, 32 mm total height.
 * P02 is detachable on two M4 bolts and positive locating keys. This NEW joint
 * has unqualified stiffness/strength. Palm contact geometry, 86 mm sleeve and
 * electronics enclosure are retained. Remove both M4 bolts and lift the palm
 * and case module vertically before keeper/cassette assembly or service.
 * Lower forward clamps provide0.75 mm nominal capture-head withdrawal gap.
 * Derived from protected Rev D; this study does not supersede production files.
 * Native regeneration, motion/assembly checks and physical strength validation
 * are required. No tested load capacity or functional equivalence is claimed.""",
    "remove old palm feet": """        // Flat132 detachable palm: two narrow feet remain outside sensor wall
        // |Y|24 and inside rod blocks |Y|39, with2 mm nominal gaps each side.
        // Positive keys supplement two M4 bolts; joint strength is unqualified.
        // Case front X-23.6 clears foot wrist edge X-23 by0.6 mm.
        makeBox(context,id + "palmFootLeft",vector(-23,-37,3.8)*mm,vector(-9,-26,6.5)*mm);
        makeBox(context,id + "palmFootRight",vector(-23,26,3.8)*mm,vector(-9,37,6.5)*mm);
        baseBodies=append(baseBodies,body(id + "palmFootLeft"));
        baseBodies=append(baseBodies,body(id + "palmFootRight"));
        for (var side in [-1,1])
        {
            const s=side == -1 ? "0" : "1";
            const y=side*31.5;
            makeBox(context,id + ("palmKey"~s),vector(-22,y-3,6.3)*mm,
                vector(-20,y+3,8)*mm);
            baseBodies=append(baseBodies,body(id + ("palmKey"~s)));
        }""",
    "remove palm ears": """        makeBox(context,id + "palmEarLeft",vector(-30,-37,9.5)*mm,vector(-9.5,-26,14.5)*mm);
        makeBox(context,id + "palmEarRight",vector(-30,26,9.5)*mm,vector(-9.5,37,14.5)*mm);
        // Only the forward clamp drops belowZ9.5, retaining0.6 mm case gap
        // atX-23. The original upper root stays above the unchanged case.
        makeBox(context,id + "palmClampDropLeft",vector(-23,-37,6.5)*mm,vector(-9.5,-26,9.6)*mm);
        makeBox(context,id + "palmClampDropRight",vector(-23,26,6.5)*mm,vector(-9.5,37,9.6)*mm);
        join(context,id + "palmEarDropJoinLeft",[body(id + "palmEarLeft"),body(id + "palmClampDropLeft")]);
        join(context,id + "palmEarDropJoinRight",[body(id + "palmEarRight"),body(id + "palmClampDropRight")]);
""",
    "remove four-M4 mounts": """        var insertTools=[];
        var palmTools=[];
        var n=0;
        // Two M4 bolts are retained from the existing hardware set. Each wing
        // has one locating key with0.25 mm side and0.3 mm roof clearance.
        // Tab front X-9.5 clears connector X-8.25 by1.25 mm for vertical lift.
        for (var side in [-1,1])
        {
            const s=side == -1 ? "0" : "1";
            const y=side*31.5;
            makeBox(context,id + ("palmKeySlot"~s),vector(-22.25,y-3.25,6.4)*mm,
                vector(-19.75,y+3.25,8.3)*mm);
            cut(context,id + ("palmKeySlotCut"~s),body(id + "palmPad"),
                body(id + ("palmKeySlot"~s)));
        }
        for (var x in [-16])
        {
            for (var y in [-31.5,31.5])
            {
                // Six-mm inserts install flushZ6.5 and endZ0.5, leaving
                // Pilot floorZ0.2 leaves2.2 mm bottom wall above baseZ-2.
                // M4x10 fromZ10.5 ends0.5, with0.3 mm nominal tip clearance.
                makeCylinder(context,id + ("palmInsert"~n),vector(x,y,0.2)*mm,vector(x,y,7.5)*mm,2.6*mm);
                insertTools=append(insertTools,body(id + ("palmInsert"~n)));
                makeCylinder(context,id + ("palmHole"~n),vector(x,y,5.5)*mm,vector(x,y,31)*mm,2.2*mm);
                palmTools=append(palmTools,body(id + ("palmHole"~n)));
                makeCylinder(context,id + ("palmHead"~n),vector(x,y,10.5)*mm,vector(x,y,31)*mm,4*mm);
                palmTools=append(palmTools,body(id + ("palmHead"~n)));
                n+=1;
            }
        }
        cut(context,id + "palmMountHoles",body(id + "palmPad"),qUnion(palmTools));""",
    "temporary palm name": 'nameBody(context,body(id + "palmPad"),"P02 PRINT STUDY - detachable keyed palm bolster, two M4 mounts");',
    "integral frame name": '"P01 PRINT STUDY - Flat132 fixed frame, keyed detachable palm feet, 6 mm floor"',
}
for rule in rules:
    if rule["label"] in overrides_v4:
        rule["new"] = overrides_v4[rule["label"]]
change("central switch frame audit", '        auditSolidPair(context,"Switch actuator / case",actuator,body(id + "switchBody"),false),', '''        auditSolidPair(context,"Switch actuator / case",actuator,body(id + "switchBody"),false),
        auditSolidPair(context,"Switch case and actuator / fixed frame",qUnion([body(id + "switchBody"),actuator]),base,true),''')


def main():
    raw = SOURCE.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != EXPECTED_SHA256:
        raise RuntimeError(f"Protected source changed: {digest}")
    original = raw.decode("utf-8")
    derived = original
    for rule in rules:
        found = derived.count(rule["old"])
        if found != rule["count"]:
            raise RuntimeError(f"{rule['label']}: expected {rule['count']} occurrence(s), found {found}")
        derived = derived.replace(rule["old"], rule["new"])
    assert 'const palm = body(id + "palmPad")' in derived
    assert '"Palm support / base"' in derived
    assert 'integratePalm' not in derived and 'keeperPalmServiceTool' not in derived
    assert 'const loY = side == -1 ? -63 : 40;' in derived
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == EXPECTED_SHA256
    # Preserve the already compiled first source as evidence, never as final.
    v1_hash = "df19decc227d4c05311336dd599d7c8fb2365de3cd8e3d8d1d55aacb1ce48d21"
    v2_hash = "09c117bc88351235400f6d255ec85ed94c0568446fd9a272c09f9954ccd0c6ff"
    v3_hash = "3c37cdc6dfa9dd98d9edc4b814bbb0b8948652067602bc950e9dd0c53091d885"
    v4_hash = "ebe75d94a8c2fbbf860971f8fd0671e0afa7641cbd2ba9e90de4ca81970818b8"
    v5_hash = "71adae92d90575c4fc854d0b3b1abe24682050f013b1ddcf5f7d63a0364c4b86"
    archive = HERE / "fingerworker_flat132_v1.fs"
    if OUT.exists() and hashlib.sha256(OUT.read_bytes()).hexdigest() == v1_hash:
        if archive.exists() and hashlib.sha256(archive.read_bytes()).hexdigest() != v1_hash:
            raise RuntimeError("Refuse to replace nonmatching v1 evidence")
        archive.write_bytes(OUT.read_bytes())
    if OUT.exists() and hashlib.sha256(OUT.read_bytes()).hexdigest() == v2_hash:
        archive_v2 = HERE / "fingerworker_flat132_v2.fs"
        if archive_v2.exists() and hashlib.sha256(archive_v2.read_bytes()).hexdigest() != v2_hash:
            raise RuntimeError("Refuse to replace nonmatching v2 evidence")
        archive_v2.write_bytes(OUT.read_bytes())
    if OUT.exists() and hashlib.sha256(OUT.read_bytes()).hexdigest() == v3_hash:
        archive_v3 = HERE / "fingerworker_flat132_v3.fs"
        if archive_v3.exists() and hashlib.sha256(archive_v3.read_bytes()).hexdigest() != v3_hash:
            raise RuntimeError("Refuse to replace nonmatching v3 evidence")
        archive_v3.write_bytes(OUT.read_bytes())
    if OUT.exists() and hashlib.sha256(OUT.read_bytes()).hexdigest() == v4_hash:
        archive_v4 = HERE / "fingerworker_flat132_v4.fs"
        if archive_v4.exists() and hashlib.sha256(archive_v4.read_bytes()).hexdigest() != v4_hash:
            raise RuntimeError("Refuse to replace nonmatching v4 evidence")
        archive_v4.write_bytes(OUT.read_bytes())
    if OUT.exists() and hashlib.sha256(OUT.read_bytes()).hexdigest() == v5_hash:
        archive_v5 = HERE / "fingerworker_flat132_v5.fs"
        if archive_v5.exists() and hashlib.sha256(archive_v5.read_bytes()).hexdigest() != v5_hash:
            raise RuntimeError("Refuse to replace nonmatching v5 evidence")
        archive_v5.write_bytes(OUT.read_bytes())
    OUT.write_text(derived, encoding="utf-8")
    patch = {"schema": "fingerworker.exact-text-replacements.v1", "studySourceRevision": 6,
             "supersededV1Sha256Utf8": v1_hash, "source": str(SOURCE),
             "supersededV2Sha256Utf8": v2_hash,
             "supersededV3Sha256Utf8": v3_hash,
             "supersededV4Sha256Utf8": v4_hash,
             "supersededV5Sha256Utf8": v5_hash,
             "target": str(OUT), "sourceIdentity": js_identity(original),
             "targetIdentity": js_identity(derived),
             "javascriptIdentity": "let h=2166136261;for(let i=0;i<s.length;i++)h=Math.imul(h^s.charCodeAt(i),16777619)>>>0;({utf16Length:s.length,fnv1a32:h.toString(16).padStart(8,'0')})",
             "rules": rules, "status": "LOCAL SOURCE ONLY - requires native Onshape regeneration and validation",
             "expectedNominalAssemblyPartsWithoutElectronicsReferencesOrHand": 51,
             "palmMount": {"type": "detachable P02 with two M4 bolts and positive keys", "separateP02": True,
                           "footX": [-23,-9], "absY": [26,37], "footZ": [3.8,6.5],
                           "wingX": [-30,-9.5], "wingZ": [9.5,14.5],
                           "wingForwardDropX": [-23,-9.5], "wingForwardDropZ": [6.5,9.6],
                           "boltCenters": [[-16,-31.5],[-16,31.5]],
                           "keyX": [-22,-20], "keyAbsY": [28.5,34.5], "keyZ": [6.3,8],
                           "slotSideClearance": 0.25, "slotRoofClearance": 0.3,
                           "insertLength": 6, "insertInstalledZ": [0.5,6.5],
                           "insertPilotZ": [0.2,7.5], "baseBottomWall": 2.2,
                           "boltM4Length": 10, "boltUnderHeadZ": 10.5, "boltTipZ": 0.5,
                           "boltTipNominalAxialClearance": 0.3,
                           "captureHeadWithdrawNominalVerticalGap": 0.75,
                           "assemblySequence": "Set synchronized preload to 2 mm before palm removal so the rear M6 shaft clears the palm plate. Remove both M4 bolts, lift the palm and case module vertically, then service keeper or cassette.",
                           "strengthValidated": False},
             "camBore": {"axisY": 2.5, "axisZ": 10, "endX": 76.5, "screwEndX": 75,
                         "nominalRemainingWallToPocketFrontMm": 0.5},
             "benchM5": {"front": [[16,-28],[16,28]], "rear": [[127,-28],[127,28]],
                         "requiresFlush90DegreeHeadMaxDiameterMm": 10},
             "unchanged": ["palm contact geometry", "86 mm TPU sleeve", "electronics enclosure and PCB", "22 mm spring seats", "24 mm rod supports", "6 mm rods", "ordered spring pair", "30 mm travel", "0..2 mm preload", "86 mm isometric lock mode", "central guide", "sensor load path"],
             "unqualified": ["native regeneration", "solid collision/assembly checks", "load capacity", "two-M4 keyed palm joint stiffness and fatigue", "revised switch and cable assembly access", "printability"]}
    (HERE / "source-replacements.json").write_text(json.dumps(patch, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(OUT), "rules": len(rules), "sourceIdentity": patch["sourceIdentity"], "targetIdentity": patch["targetIdentity"]}, indent=2))


if __name__ == "__main__":
    main()
