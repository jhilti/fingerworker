"""Package a released native display model in one offline HTML file.

Later revisions require explicit inputs. This script does not create CAD,
change manufacturing files, or set up printing.
"""
import argparse
import base64
import gzip
import hashlib
import html as html_lib
import json
import re
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DEFAULT_HIGHLIGHTS = [
    {"title": "Shaped for the hand", "text": "Organic palm support with rounded thumb recesses on both sides."},
    {"title": "Solid, separate supports", "text": "Two rear rod blocks with screw fastening replace the fragile latch bridge."},
    {"title": "Flexible mounting", "text": "Slots within the base accommodate two 25 mm straps."},
]
sha = lambda data: hashlib.sha256(data).hexdigest()


class ResourceAudit(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []
        self.external = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.append(attrs["id"])
        for key in ("href", "src", "action"):
            value = attrs.get(key)
            if value and not value.startswith(("data:", "#")):
                self.external.append({"tag": tag, "attribute": key, "value": value})


def static_check(document, viewer):
    audit = ResourceAudit()
    audit.feed(document)
    required = {"fw3d", "loading", "loading-title", "loading-detail", "model-status", "model-data", "interaction-help"}
    checks = {
        "required_ids_present": required.issubset(audit.ids),
        "unique_ids": len(audit.ids) == len(set(audit.ids)),
        "no_external_resource_references": not audit.external,
        "no_unresolved_placeholders": re.search(r"@@[A-Z_]+@@", document) is None,
        "no_local_file_or_preview_urls": re.search(r"/Users/|file://|localhost|127\.0\.0\.1", document) is None,
        "no_network_api_calls": re.search(r"\b(?:fetch|WebSocket|XMLHttpRequest|sendBeacon)\s*\(", viewer) is None,
        "embedded_fallback": 'src="data:image/png;base64,' in document,
        "touch_controls_present": "touch-action:none" in document and "const pointers=new Map()" in viewer,
    }
    if not all(checks.values()):
        raise ValueError(f"Static viewer checks failed: {checks}")
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--revision", default="R19", help="Native released revision, e.g. R19")
    parser.add_argument("--manifest", type=Path, help="Display geometry manifest.json")
    parser.add_argument("--model", type=Path, help="Gzip/base64 display model payload")
    parser.add_argument("--fallback", type=Path, help="Native assembly PNG preview")
    parser.add_argument("--highlights", type=Path, help='JSON array of three or four {"title": "…", "text": "…"} objects; text is HTML-escaped')
    parser.add_argument("--date", dest="display_date", help="Display date YYYY-MM-DD; defaults to manifest date")
    parser.add_argument("--output", type=Path, help="HTML destination; default share/Fingerworker_<revision>_3D.html")
    parser.add_argument("--report", type=Path, help="Build/static-check manifest destination")
    parser.add_argument("--overwrite", action="store_true", help="Allow replacement of existing HTML, ZIP and report")
    parser.add_argument("--check-only", action="store_true", help="Validate and report to stdout without writing artifacts")
    args = parser.parse_args()
    if not re.fullmatch(r"R[1-9]\d*", args.revision):
        parser.error("--revision must be R followed by a positive integer")
    if args.revision != "R19" and not all((args.manifest, args.model, args.fallback)):
        parser.error("Later revisions require explicit --manifest, --model and --fallback inputs")
    manifest_path = args.manifest or ROOT / "overview/model/manifest.json"
    model_path = args.model or ROOT / "overview/model/model-data.b64"
    fallback_path = args.fallback or ROOT / "review/thumb-rim-2026-11-13/evidence/assembly-final-native.png"
    manifest = json.loads(manifest_path.read_text())
    if manifest.get("revision") != args.revision or manifest.get("binding_status") != f"BOUND_TO_RELEASED_{args.revision}":
        raise ValueError("Model manifest is not bound to the requested released native revision")
    if args.revision == "R19" and manifest.get("onshape_version") != "21323818480a2406fe14f51f":
        raise ValueError("R19 must remain bound to its frozen native version")
    if not re.fullmatch(r"[0-9a-f]{24}", manifest.get("onshape_version", "")):
        raise ValueError("A native immutable Onshape version is required")
    native_path = Path(manifest["source"])
    if not native_path.is_absolute():
        native_path = ROOT / native_path
    if sha(native_path.read_bytes()) != manifest["native_zip_sha256"]:
        raise ValueError("Native ZIP does not match the display model manifest")
    if not re.fullmatch(r"[0-9a-f]{64}", manifest.get("source_sha256", "")):
        raise ValueError("Native CAD source binding is missing")
    model = model_path.read_text().strip()
    packed = base64.b64decode(model, validate=True)
    if sha(packed) != manifest["data_sha256"]:
        raise ValueError("Display model payload hash does not match its manifest")
    objects = json.loads(gzip.decompress(packed))
    if not objects or len(objects) != len({part["id"] for part in objects}):
        raise ValueError("Display bodies must have unique identifiers")
    if {(p["id"], p["group"]) for p in objects} != {(p["id"], p["group"]) for p in manifest["parts"]}:
        raise ValueError("Display bodies do not match the native-bound manifest")
    counts = {group: sum(p["group"] == group for p in objects) for group in ("print", "metal", "buy", "electronics")}
    if counts != manifest["counts"] or sum(counts.values()) != len(objects):
        raise ValueError("Display group counts do not match the manifest")
    preview = fallback_path.read_bytes()
    if not preview.startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValueError("--fallback must be a PNG image")
    highlights = json.loads(args.highlights.read_text()) if args.highlights else DEFAULT_HIGHLIGHTS
    if not isinstance(highlights, list) or len(highlights) not in (3, 4) or any(not isinstance(p, dict) or not all(isinstance(p.get(k), str) and p[k].strip() for k in ("title", "text")) for p in highlights):
        raise ValueError("--highlights must contain three or four title/text objects")
    day = date.fromisoformat(args.display_date or manifest["date"])
    month = ("JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC")[day.month - 1]
    display_date = f"{day.day:02d} {month} {day.year}"
    highlight_html = "".join(f'<div class="detail"><strong>{html_lib.escape(p["title"])}</strong><p>{html_lib.escape(p["text"])}</p></div>' for p in highlights)
    viewer = (HERE / "viewer.js").read_text()
    viewer = viewer.replace("plastic:'8 printed components'", f"plastic:'{counts['print']} printed components'")
    document = (HERE / "template.html").read_text()
    replacements = {"REVISION": args.revision, "DISPLAY_DATE": display_date, "HIGHLIGHTS": highlight_html, "FALLBACK": base64.b64encode(preview).decode(), "MODEL": model, "VIEWER": viewer}
    for key, value in replacements.items():
        document = document.replace(f"@@{key}@@", value)
    checks = static_check(document, viewer)
    output = args.output or ROOT / f"share/Fingerworker_{args.revision}_3D.html"
    report_path = args.report or output.with_name(output.stem + "_manifest.json")
    zip_path = output.with_suffix(".zip")
    report = {
        "revision": args.revision, "objects": len(objects), "groups": counts,
        "source_payload_sha256": manifest["data_sha256"],
        "source_sha256": manifest["source_sha256"], "native_zip_sha256": manifest["native_zip_sha256"],
        "onshape_version": manifest["onshape_version"], "fallback_sha256": sha(preview),
        "html_bytes": len(document.encode()), "html_sha256": sha(document.encode()),
        "self_contained": True, "printing_setup_changed": False,
        "static_checks": checks, "check_only": args.check_only,
    }
    if not args.check_only:
        if not args.overwrite and any(p.exists() for p in (output, zip_path, report_path)):
            raise FileExistsError("Output already exists; choose a new --output or explicitly use --overwrite")
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(document)
        with ZipFile(zip_path, "w", ZIP_DEFLATED, compresslevel=9) as archive:
            archive.write(output, output.name)
        report["zip_bytes"] = zip_path.stat().st_size
        report["zip_sha256"] = sha(zip_path.read_bytes())
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
