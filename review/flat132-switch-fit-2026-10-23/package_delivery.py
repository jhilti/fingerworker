#!/usr/bin/env python3
"""Extract unchanged native millimetre STLs; package R4 only after final PASS."""
from pathlib import Path
from hashlib import sha256
import argparse
import json
import re
import zipfile

R = Path(__file__).resolve().parent
ROOT = R.parents[1]
NEUTRAL = R / "native/Flat132_R4_neutral_final.zip"
NEUTRAL_SHA = "4278ba5000a141daa466628d03a2cc08e10267368d6a95dbcdb9546f9ccc63cc"
SOURCE = R / "fingerworker_flat132_switch_fit.fs"
SOURCE_SHA = "b150ff3a76cfaaaaa65ee1ea09e144b7c7d64e45459a925163e56918f48bb3c5"
PRINT_REFS = {"P01", "P02", "P03", "P04", "P05", "P060", "P061", "P070a", "P070b", "P071a", "P071b", "P08", "P09", "P10"}


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def prepare_parts():
    assert digest(SOURCE) == SOURCE_SHA
    assert digest(NEUTRAL) == NEUTRAL_SHA
    mapping = {}
    with zipfile.ZipFile(NEUTRAL) as archive:
        assert len(archive.infolist()) == 105
        assert archive.testzip() is None
        for item in archive.infolist():
            match = re.search(r"(?:^| - )([PH]\d+[ab]?)\b", item.filename)
            if not match:
                continue
            ref = match.group(1)
            assert ref not in mapping, ref
            payload = archive.read(item)
            dest = R / "assembly-mm" / (ref + ".stl")
            dest.parent.mkdir(exist_ok=True)
            dest.write_bytes(payload)
            assert dest.read_bytes() == payload
            mapping[ref] = {"native_member": item.filename, "native_member_sha256": sha256(payload).hexdigest(), "output": str(dest.relative_to(R)), "output_sha256": digest(dest), "bytes": len(payload)}
            if ref in PRINT_REFS:
                printed = R / "print-mm" / (ref + ".stl")
                printed.parent.mkdir(exist_ok=True)
                printed.write_bytes(payload)
                assert printed.read_bytes() == payload
    assert len(mapping) == 52
    assert {ref for ref in mapping if ref.startswith("P")} == PRINT_REFS
    common = {"source_sha256": SOURCE_SHA, "native_zip": str(NEUTRAL.relative_to(R)), "native_zip_sha256": NEUTRAL_SHA, "units": "mm", "orientation": "Original native neutral assembly coordinates; no scaling, recentering, repair, remesh or slicing", "identity": "Every output STL byte-for-byte equals its named original native ZIP member"}
    assembly_manifest = dict(common, count=52, parts=mapping)
    (R / "assembly-mm/part-manifest.json").write_text(json.dumps(assembly_manifest, indent=2) + "\n")
    printed_mapping = {}
    for ref in sorted(PRINT_REFS):
        item = dict(mapping[ref], output="print-mm/" + ref + ".stl")
        printed_mapping[ref] = item
    (R / "print-mm/part-manifest.json").write_text(json.dumps(dict(common, count=14, changed_since_R3=["P01", "P04"], parts=printed_mapping), indent=2) + "\n")
    return mapping


def build_package():
    report_path = R / "validation/validation.json"
    report = json.loads(report_path.read_text())
    assert report.get("status") == "NOMINAL_GEOMETRY_CHECKS_PASS", report.get("status")
    assert report.get("failed_checks") == 0
    assert report.get("unresolved_checks") == 0
    spec = json.loads((R / "final-specification.json").read_text())
    assert spec["status"] == "CAD_PROTOTYPE_NOMINAL_GEOMETRY_CHECKS_PASS"
    assert spec["onshape"].get("immutable_version_id"), "Final immutable version is not bound"
    assert spec["source"]["sha256"] == SOURCE_SHA
    assert spec["validation"]["binding_status"] == "FINAL_BOUND"
    assert spec["validation"]["report_sha256"] == digest(report_path)
    assert spec["validation"]["summary_sha256"] == digest(R / "validation/validation-summary.json")
    step = R / "native/Flat132_R4_final_AP214.step"
    assert digest(step) == spec["native_exports"][step.name]["sha256"]
    for name, record in spec["native_exports"].items():
        assert digest(R / "native" / name) == record["sha256"], name
    prepare_parts()
    primary = ["README.md", "PRINT_NOTES.md", "finalization-notes.md", "final-specification.json", "fingerworker_flat132_switch_fit.fs", "build_switch_fit.py", "source-build.json", "onshape-build.json", "package_delivery.py", "native/Flat132_R4_final_AP214.step"]
    entries = {name: R / name for name in primary}
    for sub in ["print-mm", "assembly-mm", "validation", "proof"]:
        for path in (R / sub).rglob("*"):
            if (path.is_file() and "__pycache__" not in path.parts
                    and not path.name.startswith("provisional-")
                    and "sign-in-required" not in path.name):
                entries[str(path.relative_to(R))] = path
    entries["reference/Omron_SS_datasheet.pdf"] = ROOT / "vendor/omron_ss5gl2/SS_datasheet.pdf"
    sensor = ROOT / "review/flat132-palm-fit-2026-10-23/sensor/TE_FX1901_actual_apex_aligned_132_mm.step"
    if sensor.is_file():
        entries["reference/TE_FX1901_actual_apex_aligned_132_mm.step"] = sensor
    assert all(path.is_file() for path in entries.values())
    assert len([n for n in entries if n.startswith("print-mm/") and n.endswith(".stl")]) == 14
    assert len([n for n in entries if n.startswith("assembly-mm/") and n.endswith(".stl")]) == 52
    manifest = {"revision": "Flat132 R4 switch fit", "purpose": "CAD prototype with14 print STLs and52 device assembly STLs; unsliced original native millimetre coordinates", "source_sha256": SOURCE_SHA, "neutral_native_zip_sha256": NEUTRAL_SHA, "native_step_sha256": digest(step), "nominal_validation": "PASS", "physical_500N_qualification": "PENDING", "switch_geometry": "Manufacturer DRAWING clearance reference; no factory switch STEP", "immutable_version_id": spec["onshape"]["immutable_version_id"], "files": {name: digest(path) for name, path in sorted(entries.items())}}
    delivery = R / "deliverables"
    delivery.mkdir(exist_ok=True)
    manifest_path = delivery / "package-manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    package = delivery / "Flat132_R4_Switch_Fit.zip"
    with zipfile.ZipFile(package, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, path in sorted(entries.items()):
            archive.write(path, name)
        archive.write(manifest_path, "package-manifest.json")
    with zipfile.ZipFile(package) as archive:
        assert archive.testzip() is None
        for name, expected in manifest["files"].items():
            assert sha256(archive.read(name)).hexdigest() == expected, name
    record = {"path": str(package.relative_to(R)), "sha256": digest(package), "bytes": package.stat().st_size, "members": len(entries) + 1, "crc_check": "PASS", "member_sha256_checks": "PASS", "print_STLs": 14, "device_assembly_STLs": 52}
    (delivery / "delivery-check.json").write_text(json.dumps(record, indent=2) + "\n")
    return record


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare-only", action="store_true", help="Copy unchanged native STLs and write identity manifests; no delivery ZIP")
    args = parser.parse_args()
    if args.prepare_only:
        prepare_parts()
        print(json.dumps({"status": "NATIVE_PART_FILES_PREPARED_FINAL_VALIDATION_PENDING", "assembly_STLs": 52, "print_STLs": 14, "native_zip_sha256": NEUTRAL_SHA}, indent=2))
    else:
        print(json.dumps(build_package(), indent=2))
