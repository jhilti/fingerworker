#!/usr/bin/env python3
"""Extract exact native R5 millimetre STLs; package only after final bound PASS."""
from pathlib import Path
from hashlib import sha256
import argparse
import json
import re
import zipfile

R = Path(__file__).resolve().parent
ROOT = R.parents[1]
NEUTRAL = R / "native/Flat132_R5_neutral_final.zip"
NEUTRAL_SHA = "2f4a8634c42317d10dfe93a8e113a254ef4d5f05d70b8f6330f23a9f5866e7a5"
ISO81 = R / "native/Flat132_R5_isometric13_p2_81_final.zip"
ISO81_SHA = "e47a1d0dd271184670537dd6d1cc893164ea4e7f4046064a5fd685bc002ffa4d"
SOURCE = R / "fingerworker_flat132_reach_fit.fs"
SOURCE_SHA = "d7f476fa34e862e2b0e1b5a5e91fff0f852b9308a589fafd11ce59e01269915a"
DYNAMIC_EXPORT_SOURCE_SHA = "61885fd717b30eaf1dfc39a1f7f65f017bfc1b4ac077c3e3493399ef3373a9a3"
PRINT_REFS = {"P01", "P02", "P03", "P04", "P05", "P060", "P061", "P070a", "P070b", "P071a", "P071b", "P08", "P09", "P10", "P11"}


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def prepare_references():
    """Preserve report bytes and their original relative Markdown links."""
    copies = {
        "reference/baseline/fingerworker_flat132_switch_fit.fs": ROOT / "review/flat132-switch-fit-2026-10-23/fingerworker_flat132_switch_fit.fs",
        "reference/Omron_SS_datasheet.pdf": ROOT / "vendor/omron_ss5gl2/SS_datasheet.pdf",
        "reference/TE_FX1901_actual_apex_aligned_132_mm.step": ROOT / "review/flat132-palm-fit-2026-10-23/sensor/TE_FX1901_actual_apex_aligned_132_mm.step",
        "reference/procurement/springs/KATALOGFEDERN.md": ROOT / "procurement/springs/KATALOGFEDERN.md",
        "reference/procurement/springs/BESTELLUNG-2026-09-29.md": ROOT / "procurement/springs/BESTELLUNG-2026-09-29.md",
        "reference/review/flat132-reach-fit-2026-10-23/fingerworker_flat132_reach_fit.fs": R / "fingerworker_flat132_reach_fit_ISO86_61885fd7.fs",
        "reference/review/flat132-reach-fit-2026-10-23/source-build.json": R / "source-build.json",
    }
    for stem in ["mechanism-proposal", "reach-clearance", "spring-tradeoff"]:
        for ext in ["md", "json"]:
            relative = "reference/review/flat132-reach-study-2026-10-23/" + stem + "." + ext
            copies[relative] = ROOT / "review/flat132-reach-study-2026-10-23" / (stem + "." + ext)
    records = {}
    for relative, source in copies.items():
        target = R / relative
        if source.is_file():
            payload = source.read_bytes()
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(payload)
            assert target.read_bytes() == payload
        else:
            # An extracted compact package already contains the frozen copies.
            assert target.is_file(), source
        records[relative] = {"sha256": digest(target), "bytes": target.stat().st_size, "source_project_path": str(source)}
    assert digest(R / "reference/baseline/fingerworker_flat132_switch_fit.fs") == "b150ff3a76cfaaaaa65ee1ea09e144b7c7d64e45459a925163e56918f48bb3c5"
    assert digest(R / "reference/review/flat132-reach-fit-2026-10-23/fingerworker_flat132_reach_fit.fs") == DYNAMIC_EXPORT_SOURCE_SHA
    # The unchanged historic procurement ledger links to the full-project
    # DEVICE_UPGRADES history. Supply an explicit navigation note, not a false
    # copy of that much broader project history and its unavailable artifacts.
    navigation = R / "reference/DEVICE_UPGRADES.md"
    navigation.write_text("# Compact-package project-context note\n\nThe original DEVICE_UPGRADES.md is a full-project history and is outside this compact delivery. The exact spring procurement ledger is retained unchanged, including its historic link here. For the selected R5 assembly, use the [current README](../README.md), [print and assembly notes](../PRINT_NOTES.md) and [final specification](../final-specification.json). This navigation note is not a copy of the original project-history document.\n")
    records[str(navigation.relative_to(R))] = {"sha256": digest(navigation), "bytes": navigation.stat().st_size, "identity": "Generated compact-package navigation note; no original project-history copy claimed"}
    (R / "reference/reference-manifest.json").write_text(json.dumps({"identity": "Reference copies preserve original source bytes; original project paths are provenance, not extraction requirements", "historical_studies": "Study reports describe the earlier86mm candidate. Root final specification and selected81mm validation supersede that choice. The mirrored source is the exact61885 checkpoint; its linked source-build record includes the subsequent reversible ISO-only change.", "builder_baseline": "build_reach_fit.py uses the project R4 source when present, otherwise reference/baseline/fingerworker_flat132_switch_fit.fs; SHA must match either way", "files": records}, indent=2) + "\n")


def prepare_hardware():
    assert digest(ISO81) == ISO81_SHA
    parts = {}
    with zipfile.ZipFile(ISO81) as archive:
        assert len(archive.infolist()) == 106 and archive.testzip() is None
        for item in archive.infolist():
            match = re.search(r"(?:^| - )(H14[01])\b", item.filename)
            if not match:
                continue
            ref = match.group(1)
            assert ref not in parts
            payload = archive.read(item)
            path = R / "hardware-mm" / (ref + ".stl")
            path.parent.mkdir(exist_ok=True)
            path.write_bytes(payload)
            assert path.read_bytes() == payload
            parts[ref] = {"native_member": item.filename, "native_member_sha256": sha256(payload).hexdigest(), "output": str(path.relative_to(R)), "output_sha256": digest(path), "bytes": len(payload)}
    assert set(parts) == {"H140", "H141"}
    manifest = {"source_sha256": SOURCE_SHA, "native_zip": str(ISO81.relative_to(R)), "native_zip_sha256": ISO81_SHA, "count": 2, "units": "mm", "material_intent": "Steel; two matching sleeves; not print parts", "nominal_dimensions_mm": {"outer_diameter": 16, "inner_diameter": 8, "length": 81}, "native_pose": {"user_travel_mm": 13, "absolute_carriage_shift_mm": 18, "preload_mm": 2, "cam_trim_mm": 0, "mode": "ISO81"}, "orientation": "Original native ISO81 assembly coordinates; no scaling, recentering, repair or remesh", "identity": "Every output STL byte-for-byte equals its named native ISO81 ZIP member", "parts": parts}
    (R / "hardware-mm/part-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return parts


def prepare_parts():
    assert digest(SOURCE) == SOURCE_SHA
    assert digest(NEUTRAL) == NEUTRAL_SHA
    assert digest(R / "fingerworker_flat132_reach_fit_ISO86_61885fd7.fs") == DYNAMIC_EXPORT_SOURCE_SHA
    mapping = {}
    with zipfile.ZipFile(NEUTRAL) as archive:
        assert len(archive.infolist()) == 106
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
    assert len(mapping) == 53
    assert {ref for ref in mapping if ref.startswith("P")} == PRINT_REFS
    spec = json.loads((R / "final-specification.json").read_text())
    common = {"source_sha256": SOURCE_SHA, "native_export_source_sha256": DYNAMIC_EXPORT_SOURCE_SHA, "source_association": "Original dynamic export belongs to61885 source. Selected81mm source has identical dynamic expressions; see final independent mode-conditioned certificate.", "dynamic_source_equivalence_status": spec["validation"]["dynamic_source_equivalence_status"], "native_zip": str(NEUTRAL.relative_to(R)), "native_zip_sha256": NEUTRAL_SHA, "units": "mm", "orientation": "Original native neutral assembly coordinates; no scaling, recentering, repair, remesh or slicing", "identity": "Every output STL byte-for-byte equals its named original native ZIP member"}
    (R / "assembly-mm/part-manifest.json").write_text(json.dumps(dict(common, count=53, parts=mapping), indent=2) + "\n")
    printed_mapping = {ref: dict(mapping[ref], output="print-mm/" + ref + ".stl") for ref in sorted(PRINT_REFS)}
    print_manifest = dict(common, count=15, changed_since_R4=["P01", "P04", "P05", "P060", "P061"], added_since_R4=["P11"], repositioned_same_shape=["P070a", "P070b", "P071a", "P071b"], parts=printed_mapping)
    (R / "print-mm/part-manifest.json").write_text(json.dumps(print_manifest, indent=2) + "\n")
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
    provenance = report["manifest"]["native_provenance"]
    assert provenance["immutable_version_id"] == spec["onshape"]["immutable_version_id"]
    assert provenance["feature_source_sha256"] == SOURCE_SHA
    native_build = json.loads((R / "onshape-build.json").read_text())
    assert native_build["immutable_version_id"] == spec["onshape"]["immutable_version_id"]
    assert native_build["immutable_source_readback_sha256"] == SOURCE_SHA
    assert spec["validation"]["binding_status"] == "FINAL_BOUND"
    assert spec["validation"]["dynamic_source_equivalence_status"] == "PASS"
    assert spec["validation"]["report_sha256"] == digest(report_path)
    assert spec["validation"]["summary_sha256"] == digest(R / "validation/validation-summary.json")
    step = R / "native/Flat132_R5_final_AP214.step"
    assert digest(step) == spec["native_exports"][step.name]["sha256"]
    for name, record in spec["native_exports"].items():
        assert digest(R / "native" / name) == record["sha256"], name
    assert spec.get("proof_files"), "Final visual proof has not been bound"
    assert not spec.get("proof_files_pending"), "Final visual proof is incomplete"
    assert {"proof/onshape-R5-immutable-neutral.png", "proof/R5-reach-comparison.png", "proof/R5-cam-max-preload.png"}.issubset(spec["proof_files"])
    for name, expected in spec["proof_files"].items():
        assert digest(R / name) == expected, name
    for name, expected in spec["validation"].get("evidence_files", {}).items():
        assert digest(R / name) == expected, name
    prepare_parts()
    prepare_hardware()
    prepare_references()
    primary = ["README.md", "PRINT_NOTES.md", "finalization-notes.md", "final-specification.json", "fingerworker_flat132_reach_fit.fs", "fingerworker_flat132_reach_fit_ISO86_61885fd7.fs", "build_reach_fit.py", "source-build.json", "onshape-build.json", "package_delivery.py", "native/Flat132_R5_final_AP214.step"]
    entries = {name: R / name for name in primary}
    for sub in ["print-mm", "assembly-mm", "hardware-mm", "reference", "validation", "proof"]:
        for path in (R / sub).rglob("*"):
            if (path.is_file() and "__pycache__" not in path.parts
                    and not path.name.startswith("provisional-")
                    and not path.name.startswith("diagnostic-")
                    and "sign-in-required" not in path.name
                    and path.suffix.lower() != ".zip"):
                entries[str(path.relative_to(R))] = path
    assert all(path.is_file() for path in entries.values())
    assert len([n for n in entries if n.startswith("print-mm/") and n.endswith(".stl")]) == 15
    assert len([n for n in entries if n.startswith("assembly-mm/") and n.endswith(".stl")]) == 53
    assert len([n for n in entries if n.startswith("hardware-mm/") and n.endswith(".stl")]) == 2
    manifest = {"revision": "Flat132 R5 closer dynamic and ISO grip", "purpose": "CAD prototype with15 print STLs and53 device assembly STLs; unsliced original native millimetre coordinates", "source_sha256": SOURCE_SHA, "neutral_native_export_source_sha256": DYNAMIC_EXPORT_SOURCE_SHA, "dynamic_source_equivalence": "PASS_MODE_CONDITIONED_CERTIFICATE_IN_VALIDATION", "neutral_native_zip_sha256": NEUTRAL_SHA, "native_step_sha256": digest(step), "nominal_validation": "PASS", "physical_500N_qualification": "PENDING", "switch_geometry": "Manufacturer DRAWING clearance reference; no factory switch STEP", "ISO_sleeves_mm": 81, "cam_setup": "Manual shoe setting camTrim-preload; physical calibration required", "immutable_version_id": spec["onshape"]["immutable_version_id"], "large_native_pose_ZIPs": "Validation input archives remain in project/native and are omitted from this compact delivery; report hashes bind them", "files": {name: digest(path) for name, path in sorted(entries.items())}}
    delivery = R / "deliverables"
    delivery.mkdir(exist_ok=True)
    manifest_path = delivery / "package-manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    package = delivery / "Flat132_R5_Closer_Grip.zip"
    with zipfile.ZipFile(package, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, path in sorted(entries.items()):
            archive.write(path, name)
        archive.write(manifest_path, "package-manifest.json")
    with zipfile.ZipFile(package) as archive:
        assert archive.testzip() is None
        for name, expected in manifest["files"].items():
            assert sha256(archive.read(name)).hexdigest() == expected, name
    record = {"path": str(package.relative_to(R)), "sha256": digest(package), "bytes": package.stat().st_size, "members": len(entries) + 1, "crc_check": "PASS", "member_sha256_checks": "PASS", "print_STLs": 15, "device_assembly_STLs": 53, "ISO81_hardware_STLs": 2}
    (delivery / "delivery-check.json").write_text(json.dumps(record, indent=2) + "\n")
    return record


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare-only", action="store_true", help="Copy unchanged native STLs and write identity manifests; no delivery ZIP")
    args = parser.parse_args()
    if args.prepare_only:
        prepare_parts()
        prepare_hardware()
        prepare_references()
        print(json.dumps({"status": "NATIVE_PART_FILES_PREPARED_FINAL_VALIDATION_PENDING", "assembly_STLs": 53, "print_STLs": 15, "ISO81_hardware_STLs": 2, "native_zip_sha256": NEUTRAL_SHA}, indent=2))
    else:
        print(json.dumps(build_package(), indent=2))
