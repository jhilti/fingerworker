#!/usr/bin/env python3
"""Extract exact R6 native millimetre STLs; package only final bound PASS evidence."""
from pathlib import Path
from hashlib import sha256
import argparse
import json
import re
import zipfile

R = Path(__file__).resolve().parent
ROOT = R.parents[1]
PRINT_REFS = {"P01", "P02", "P04", "P05", "P060", "P061", "P070a", "P070b", "P071a", "P071b", "P08", "P09", "P10", "P11"}
BASELINE_SHA = "d7f476fa34e862e2b0e1b5a5e91fff0f852b9308a589fafd11ce59e01269915a"


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def specification():
    return json.loads((R / "final-specification.json").read_text())


def bound_native(spec, filename):
    path = R / "native" / filename
    record = spec["native_exports"][filename]
    assert digest(path) == record["sha256"], filename
    assert record["export_source_sha256"] == spec["source"]["sha256"], filename
    return path, record


def native_members(path):
    result = {}
    with zipfile.ZipFile(path) as archive:
        assert archive.testzip() is None
        assert len(archive.infolist()) == 105
        for item in archive.infolist():
            match = re.search(r"(?:^| - )([PH]\d+[ab]?)\b", item.filename)
            if not match:
                continue
            ref = match.group(1)
            assert ref not in result, ref
            assert item.filename.lower().endswith(".stl")
            result[ref] = (item.filename, archive.read(item))
    assert len(result) == 52 and "P03" not in result
    return result


def prepare_parts():
    spec = specification()
    assert digest(R / spec["source"]["file"]) == spec["source"]["sha256"]
    neutral, record = bound_native(spec, "Flat132_R6_neutral_final.zip")
    members = native_members(neutral)
    assert {ref for ref in members if ref.startswith("P")} == PRINT_REFS
    mapping = {}
    for ref, (member, payload) in sorted(members.items()):
        path = R / "assembly-mm" / (ref + ".stl")
        path.parent.mkdir(exist_ok=True)
        path.write_bytes(payload)
        mapping[ref] = {"native_member": member, "native_member_sha256": sha256(payload).hexdigest(), "output": str(path.relative_to(R)), "output_sha256": digest(path), "bytes": len(payload)}
        assert path.read_bytes() == payload
        if ref in PRINT_REFS:
            printed = R / "print-mm" / (ref + ".stl")
            printed.parent.mkdir(exist_ok=True)
            printed.write_bytes(payload)
            assert printed.read_bytes() == payload
    common = {"source_sha256": spec["source"]["sha256"], "native_zip": str(neutral.relative_to(R)), "native_zip_sha256": record["sha256"], "units": "mm", "orientation": "Original native neutral assembly coordinates; no scaling, recentering, repair, remesh or slicing", "identity": "Every output STL byte-for-byte equals its named native R6 ZIP member"}
    (R / "assembly-mm/part-manifest.json").write_text(json.dumps(dict(common, count=52, parts=mapping), indent=2) + "\n")
    printed = {ref: dict(mapping[ref], output="print-mm/" + ref + ".stl") for ref in sorted(PRINT_REFS)}
    (R / "print-mm/part-manifest.json").write_text(json.dumps(dict(common, count=14, changed_since_R5=["P02"], removed_since_R5=["P03"], rigid_palm_ref="P02", flexible_refs=["P070a", "P070b", "P071a", "P071b"], parts=printed), indent=2) + "\n")
    iso, iso_record = bound_native(spec, "Flat132_R6_isometric13_p2_81_final.zip")
    sleeves = {}
    for ref, (member, payload) in native_members(iso).items():
        if ref not in {"H140", "H141"}:
            continue
        path = R / "hardware-mm" / (ref + ".stl")
        path.parent.mkdir(exist_ok=True)
        path.write_bytes(payload)
        assert path.read_bytes() == payload
        sleeves[ref] = {"native_member": member, "native_member_sha256": sha256(payload).hexdigest(), "output": str(path.relative_to(R)), "output_sha256": digest(path), "bytes": len(payload)}
    assert set(sleeves) == {"H140", "H141"}
    (R / "hardware-mm/part-manifest.json").write_text(json.dumps({"source_sha256": spec["source"]["sha256"], "native_zip": str(iso.relative_to(R)), "native_zip_sha256": iso_record["sha256"], "count": 2, "units": "mm", "material_intent": "Two matching steel ISO sleeves; not print parts; unrelated to removed TPU palm sleeve", "nominal_dimensions_mm": {"outer_diameter": 16, "inner_diameter": 8, "length": 81}, "orientation": "Original native ISO13/p2 coordinates; byte-identical native ZIP members", "parts": sleeves}, indent=2) + "\n")
    return {"assembly_STLs": 52, "print_STLs": 14, "ISO81_hardware_STLs": 2}


def prepare_references():
    copies = {
        "reference/baseline/fingerworker_flat132_reach_fit.fs": ROOT / "review/flat132-reach-fit-2026-10-23/fingerworker_flat132_reach_fit.fs",
        "reference/baseline/R5-PRINT_NOTES.md": ROOT / "review/flat132-reach-fit-2026-10-23/PRINT_NOTES.md",
        "reference/baseline/R5-final-specification.json": ROOT / "review/flat132-reach-fit-2026-10-23/final-specification.json",
        "reference/baseline/Flat132_R5_final_AP214.step": ROOT / "review/flat132-reach-fit-2026-10-23/native/Flat132_R5_final_AP214.step",
        "reference/Omron_SS_datasheet.pdf": ROOT / "vendor/omron_ss5gl2/SS_datasheet.pdf",
        "reference/TE_FX1901_actual_apex_aligned_132_mm.step": ROOT / "review/flat132-palm-fit-2026-10-23/sensor/TE_FX1901_actual_apex_aligned_132_mm.step",
        "reference/spring-tradeoff.json": ROOT / "review/flat132-reach-study-2026-10-23/spring-tradeoff.json",
        "reference/baseline/validation/validation-summary.md": ROOT / "review/flat132-reach-fit-2026-10-23/validation/validation-summary.md",
    }
    records = {}
    certificate_path = R / "validation/source-scope-certificate.json"
    if certificate_path.is_file():
        certificate = json.loads(certificate_path.read_text())
        for original, expected in certificate["baseline_evidence_files_sha256"].items():
            source = Path(original)
            relative = "reference/baseline/validation/" + source.name
            assert digest(source if source.is_file() else R / relative) == expected
            copies[relative] = source
        source = Path(certificate["baseline_validation_summary"])
        relative = "reference/baseline/validation/validation-summary.json"
        assert digest(source if source.is_file() else R / relative) == certificate["baseline_validation_summary_sha256"]
        copies[relative] = source
    for relative, source in copies.items():
        target = R / relative
        if source.is_file():
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(source.read_bytes())
            assert target.read_bytes() == source.read_bytes()
        assert target.is_file(), source
        records[relative] = {"sha256": digest(target), "bytes": target.stat().st_size, "source_project_path": str(source)}
    assert digest(R / "reference/baseline/fingerworker_flat132_reach_fit.fs") == BASELINE_SHA
    (R / "reference/README.md").write_text("# Frozen reference material\n\nThese exact copies document the R5 baseline, Omron drawing and actual TE sensor source. R5 notes and specification are historical; the R6 root notes override the palm construction, remove P03 and retain only four P07 flexible pads. R5 relative links refer to its original project folder. No R5 nominal PASS is assigned to the R6 geometry.\n")
    (R / "reference/reference-manifest.json").write_text(json.dumps({"identity": "Exact source copies; R5 records are historical baseline only", "files": records}, indent=2) + "\n")


def build_package():
    spec = specification()
    report_path = R / "validation/validation.json"
    report = json.loads(report_path.read_text())
    assert report["status"] == "NOMINAL_GEOMETRY_CHECKS_PASS"
    assert report["failed_checks"] == report["unresolved_checks"] == 0
    assert spec["status"] == "CAD_PROTOTYPE_NOMINAL_GEOMETRY_CHECKS_PASS"
    assert spec["validation"]["binding_status"] == "FINAL_BOUND"
    assert digest(report_path) == spec["validation"]["report_sha256"]
    assert digest(R / "validation/validation-summary.json") == spec["validation"]["summary_sha256"]
    source_sha = spec["source"]["sha256"]
    assert digest(R / spec["source"]["file"]) == source_sha
    provenance = report["native_provenance"]
    assert provenance["feature_source_sha256"] == source_sha
    assert provenance["immutable_version_id"] == spec["onshape"]["immutable_version_id"]
    build = json.loads((R / "onshape-build.json").read_text())
    assert build["immutable_version_id"] == spec["onshape"]["immutable_version_id"]
    assert build["immutable_source_readback_sha256"] == source_sha
    for name, record in spec["native_exports"].items():
        bound_native(spec, name)
    assert not spec.get("proof_files_pending"), spec.get("proof_files_pending")
    assert {"proof/onshape-R6-immutable-neutral.png", "proof/R6-solid-palm-round.png", "proof/R6-solid-palm-flat-back.png"}.issubset(spec["proof_files"])
    for name, expected in spec["proof_files"].items():
        assert digest(R / name) == expected, name
    for name, expected in spec["validation"].get("evidence_files", {}).items():
        assert digest(R / name) == expected, name
    prepare_parts()
    prepare_references()
    primary = ["README.md", "PRINT_NOTES.md", "finalization-notes.md", "final-specification.json", spec["source"]["file"], spec["source"]["builder"], "source-build.json", "onshape-build.json", "package_delivery.py", "native/Flat132_R6_final_AP214.step"]
    entries = {name: R / name for name in primary}
    for sub in ["print-mm", "assembly-mm", "hardware-mm", "reference", "validation", "proof"]:
        for path in (R / sub).rglob("*"):
            if path.is_file() and "__pycache__" not in path.parts and path.suffix.lower() != ".zip" and not path.name.startswith(("provisional-", "diagnostic-")):
                entries[str(path.relative_to(R))] = path
    assert all(p.is_file() for p in entries.values())
    assert len([n for n in entries if n.startswith("print-mm/") and n.endswith(".stl")]) == 14
    assert len([n for n in entries if n.startswith("assembly-mm/") and n.endswith(".stl")]) == 52
    assert len([n for n in entries if n.startswith("hardware-mm/") and n.endswith(".stl")]) == 2
    assert not any(Path(n).name == "P03.stl" for n in entries)
    manifest = {"revision": "Flat132 R6 single rigid printed palm", "source_sha256": source_sha, "neutral_native_zip_sha256": spec["native_exports"]["Flat132_R6_neutral_final.zip"]["sha256"], "native_step_sha256": spec["native_exports"]["Flat132_R6_final_AP214.step"]["sha256"], "nominal_validation": "PASS", "physical_500N_qualification": "PENDING", "print_STLs": 14, "assembly_STLs": 52, "palm": "One rigid P02 block; P03 removed", "flexible_print_refs": ["P070a", "P070b", "P071a", "P071b"], "steel_ISO_sleeves_mm": 81, "immutable_version_id": spec["onshape"]["immutable_version_id"], "large_native_pose_ZIPs": "Hash-bound project validation inputs omitted from compact package", "files": {name: digest(path) for name, path in sorted(entries.items())}}
    delivery = R / "deliverables"
    delivery.mkdir(exist_ok=True)
    manifest_path = delivery / "package-manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    package = R / spec["package"]
    with zipfile.ZipFile(package, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, path in sorted(entries.items()):
            archive.write(path, name)
        archive.write(manifest_path, "package-manifest.json")
    with zipfile.ZipFile(package) as archive:
        assert archive.testzip() is None
        for name, expected in manifest["files"].items():
            assert sha256(archive.read(name)).hexdigest() == expected, name
    check = dict(path=str(package.relative_to(R)), sha256=digest(package), bytes=package.stat().st_size, members=len(entries) + 1, crc_check="PASS", member_sha256_checks="PASS", print_STLs=14, device_assembly_STLs=52, ISO81_hardware_STLs=2)
    (delivery / "delivery-check.json").write_text(json.dumps(check, indent=2) + "\n")
    return check


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare-only", action="store_true")
    args = parser.parse_args()
    if args.prepare_only:
        counts = prepare_parts()
        prepare_references()
        print(json.dumps(dict(status="NATIVE_PART_FILES_PREPARED", **counts), indent=2))
    else:
        print(json.dumps(build_package(), indent=2))
