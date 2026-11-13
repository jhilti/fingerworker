#!/usr/bin/env python3
"""Build the R6 one-piece rigid palm prototype from frozen R5 ISO81 source."""
from hashlib import sha256
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROJECT_BASE = ROOT / "review/flat132-reach-fit-2026-10-23/fingerworker_flat132_reach_fit.fs"
BUNDLED_BASE = HERE / "reference/baseline/fingerworker_flat132_reach_fit.fs"
BASE = PROJECT_BASE if PROJECT_BASE.is_file() else BUNDLED_BASE
BASE_SHA = "d7f476fa34e862e2b0e1b5a5e91fff0f852b9308a589fafd11ce59e01269915a"
OUT = HERE / "fingerworker_flat132_solid_palm.fs"
raw = BASE.read_bytes()
assert sha256(raw).hexdigest() == BASE_SHA, "Frozen R5 baseline changed"
source = raw.decode()
changes = []


def replace(label, old, new, expected=1):
    global source
    count = source.count(old)
    assert count == expected, (label, count, expected)
    source = source.replace(old, new)
    changes.append({"label": label, "count": count, "old": old, "new": new})


replace("R6 study identification",
        " * Fingerworker MVP - R5 reach-fit CAD STUDY; load rating unverified.",
        " * Fingerworker MVP - R6 solid-palm CAD prototype; load rating unverified.\n"
        " * R6: former P03 palm contact stock is solid and joined into rigid P02.\n"
        " * No separate palm sleeve, core bore, bottom interface gap or retaining tabs.\n"
        " * Wrist-facing outer contact curve, palm mounts and electronics are retained.\n"
        " * Four P07 TPU return bumpers remain separate and unchanged.\n"
        " * Inherited R5 motion and selected81 mm ISO sleeves are retained.")
replace("R6 feature name",
        '"Feature Name Template" : "Flat132 R5 reach study - 5 mm closer and full travel"',
        '"Feature Name Template" : "Flat132 R6 - one-piece printable palm block"')

start = source.index('        makeCylinder(context,id + "palmCushion",')
end = source.index('        // Carriage: two outside spring arms', start)
replace("replace separate hollow palm cap with joined solid contact stock", source[start:end],
        '''        // R6 one-piece rigid palm block. Preserve the former cap's outer
        // wrist-facing half-round and rounded ends, but omit its core bore and
        // bottom cut. Solid stock joins the original core and plate, including
        // the old0.1 mm plate-to-cap split; there is no internal sleeve seam.
        // Former front retaining returns are unnecessary without a loose cap.
        makeCylinder(context,id + "palmContactStock",vector(-27,-43,19.75)*mm,
            vector(-27,43,19.75)*mm,10.25*mm);
        opFillet(context,id + "palmContactEnds",{
            "entities":qCreatedBy(id + "palmContactStock",EntityType.EDGE),
            "radius":1.2*mm,"tangentPropagation":true });
        makeBox(context,id + "palmContactForwardHalfTool",vector(-27,-45,0)*mm,
            vector(0,45,40)*mm);
        cut(context,id + "palmContactHalfCut",body(id + "palmContactStock"),
            body(id + "palmContactForwardHalfTool"));
        join(context,id + "palmSolidBlockJoin",
            [body(id + "palmPad"),body(id + "palmContactStock")]);
        nameBody(context,body(id + "palmPad"),
            "P02 PRINT STUDY - one-piece rigid half-round palm block, retained keyed mounts");

''')

# P03 no longer exists. Every native collision query now uses the complete P02.
replace("remove obsolete sleeve body query", '    const sleeve = body(id + "palmCushion");\n', '')
replace("merged palm collision groups", 'palm,sleeve', 'palm', expected=7)
replace("direct merged palm collision query", 'qUnion([palm])', 'palm', expected=1)
replace("remove obsolete palm-to-sleeve contact audit",
        '        auditSolidPair(context,"Palm sleeve / rigid support",sleeve,palm,true),\n', '')
replace("hand now contacts rigid palm block",
        '        auditSolidPair(context,"Hand / palm sleeve",hand,sleeve,true),',
        '        auditSolidPair(context,"Hand / rigid palm block",hand,palm,true),')
replace("hand exclusion follows merged palm",
        'qSubtraction(device,qUnion([hand,carriage,sleeve]))',
        'qSubtraction(device,qUnion([hand,carriage,palm]))')
replace("remove separate soft cap appearance",
        '        finishBody(context,body(id + "palmCushion"),color(0.15,0.20,0.17));\n', '')
replace("appearance comment reflects rigid contact",
        '        // Neutral green frame, warm tan climbing surface, dark soft contact.',
        '        // Neutral green frame and one-piece rigid palm; warm tan climbing surface.')

assert 'palmCushion' not in source
assert 'palmSleeveReturn' not in source
assert 'sleeveCoreTool' not in source
assert 'sleeveBottomTool' not in source
assert 'const sleeve' not in source
assert source.count('"P02 PRINT STUDY') == 1
assert '"P03 ' not in source
out = source.encode()
OUT.write_bytes(out)
manifest = {
    "file": OUT.name,
    "sha256": sha256(out).hexdigest(),
    "bytes": len(out),
    "status": "LOCAL_R6_SOURCE_NATIVE_REGEN_AND_VALIDATION_PENDING",
    "baseline_source": "review/flat132-reach-fit-2026-10-23/fingerworker_flat132_reach_fit.fs",
    "baseline_source_sha256": BASE_SHA,
    "expected_native_body_count_with_electronics": 105,
    "expected_device_body_count": 52,
    "expected_print_part_count": 14,
    "geometry_change_ledger": [
        "P02 gains solid former P03 outer half-cylinder: axis X−27/Z19.75, Y−43…43, radius10.25 mm, end fillet1.2 mm; flat back X−27.",
        "Omit former P03 R7.75 core-bore and Z14.6 bottom subtraction; fill sleeve/core stock and old0.1 mm split down into unchanged plate.",
        "Union solid contact stock into the original rigid P02; one connected CAD solid, no separate P03 or internal cap seam.",
        "Remove two obsolete front retaining tabs X−27…−24.5, Y−43…−39/+39…+43, Z14.6…30.",
        "Existing R7.75 core Y−58…58, plate, feet, keys, all palm mounting bores and enclosure insert pilots remain unchanged.",
        "Wrist-facing contact X−37.25 and original outer R10.25 contact curve remain unchanged; electronics-cover extension is not included.",
        "P07 return pads, R5 motion/source domain, 132 mm frame, 72 mm clear finger pocket and81 mm steel ISO sleeves unchanged."
    ],
    "qualification": "Solid CAD stock does not prescribe slicer infill or qualify material, comfort, print process, strength or500 N capacity.",
    "changes": changes,
}
(HERE / "source-build.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
print(json.dumps({k: manifest[k] for k in ["file", "sha256", "bytes", "status"]}))
