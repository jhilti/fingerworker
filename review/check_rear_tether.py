#!/usr/bin/env python3
"""Validate source-bound Onshape rear-tether captures, never a load release.

The historic 43-group review remains untouched. This validator requires the
eight new cord-enabled configurations and all 45 current source audit labels.
"""
from pathlib import Path
import hashlib
import json
import math
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
CAPTURE = ROOT / "review/onshape-rear-tether.json"
OUTPUT = ROOT / "review/rear-tether-validation.json"
TOLERANCE_MM = 1e-7  # Numerical conversion noise, not manufacturing clearance.
CORD_GAP_LIMITS_MM = {
    "6 mm cord / fixed frame": 1.0,
    "6 mm cord / moving and other parts": 13.0,
}
EXPECTED_CASES = {
    (travel, preload, False)
    for travel in (0, 15, 30)
    for preload in (0, 2)
} | {(15, 0, True), (15, 2, True)}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def number(value, label):
    require(type(value) in (int, float), f"{label}: numeric value required")
    require(math.isfinite(value), f"{label}: finite value required")
    return value


def count(value, label):
    require(type(value) is int and value >= 0,
            f"{label}: nonnegative integer count required")
    return value


def close(actual, expected, label):
    require(abs(number(actual, label) - expected) <= TOLERANCE_MM,
            f"{label}: {actual!r} does not match {expected!r}")


def at_least(actual, expected, label):
    require(number(actual, label) + TOLERANCE_MM >= expected,
            f"{label}: {actual!r} mm is below {expected!r} mm")


def source_identity(source_bytes):
    source = source_bytes.decode("utf-8")
    # CUA hashes JavaScript UTF-16 code units and uses String.length. Match that
    # convention even if later source comments contain non-BMP characters.
    utf16 = source.encode("utf-16-le")
    fnv = 2166136261
    for index in range(0, len(utf16), 2):
        code_unit = utf16[index] | (utf16[index + 1] << 8)
        fnv = ((fnv ^ code_unit) * 16777619) & 0xffffffff
    return source, {
        "cad_source_sha256": hashlib.sha256(source_bytes).hexdigest(),
        "source_fnv1a32": f"{fnv:08x}",
        "source_characters": len(utf16) // 2,
    }


def validate():
    source, identity = source_identity((ROOT / "fingerworker_mvp.fs").read_bytes())
    capture = json.loads(CAPTURE.read_text())
    require(isinstance(capture, dict), "Final capture must be an object")
    for field, value in identity.items():
        require(capture.get(field) == value,
                f"{field} mismatch: fresh captures of current source required")

    labels = re.findall(r'auditSolidPair\(context,\s*"([^"]+)"', source)
    require(len(labels) == 45 and len(set(labels)) == 45,
            "Current source must contain exactly 45 unique audit groups")
    source_labels = set(labels)
    require(set(CORD_GAP_LIMITS_MM) <= source_labels,
            "Current source is missing a required cord audit group")
    cases = capture.get("cases")
    require(isinstance(cases, list) and len(cases) == 8,
            "Exactly eight completed configurations are required")

    seen = set()
    results = []
    for index, case in enumerate(cases):
        prefix = f"case {index + 1}"
        require(isinstance(case, dict), f"{prefix}: object required")
        travel = number(case.get("travel_mm"), f"{prefix} preview travel")
        preload = number(case.get("preload_mm"), f"{prefix} preload")
        require(type(case.get("isometric")) is bool,
                f"{prefix}: isometric flag must be boolean")
        isometric = case["isometric"]
        key = (travel, preload, isometric)
        require(key in EXPECTED_CASES, f"{prefix}: unexpected configuration {key}")
        require(key not in seen, f"{prefix}: duplicate configuration {key}")
        seen.add(key)
        for flag in ("light", "showHand", "showElectronics", "showCord"):
            require(case.get(flag) is True, f"{prefix}: {flag} must be enabled")
        actual_stroke = 15 - preload if isometric else travel
        close(case.get("actual_stroke_mm"), actual_stroke,
              f"{prefix} actual stroke")
        at_least(case.get("eye_to_carriage_mm"), 2,
                 f"{prefix} eye/carriage clearance")

        rows = case.get("rows")
        require(isinstance(rows, list) and len(rows) == 45,
                f"{prefix}: exactly 45 audit rows required")
        pairs = [row.get("pair") if isinstance(row, dict) else None for row in rows]
        require(all(isinstance(pair, str) for pair in pairs),
                f"{prefix}: every audit row needs a pair label")
        require(len(set(pairs)) == 45 and set(pairs) == source_labels,
                f"{prefix}: duplicate, missing or unexpected audit groups")
        review_pairs = []
        cord_gaps = {}
        for row in rows:
            label = f"{prefix}, {row['pair']}"
            close(row.get("pose_mm"), actual_stroke, f"{label} pose")
            require(count(row.get("interferences"), f"{label} interferences") == 0,
                    f"{label}: solid interference reported")
            contacts = count(row.get("contacts"), f"{label} contacts")
            unclassified = count(row.get("unclassified"), f"{label} unclassified")
            gap = number(row.get("gap_mm"), f"{label} gap")
            require(gap >= -TOLERANCE_MM, f"{label}: negative gap")
            status = row.get("status")
            require(isinstance(status, str) and
                    (status == "CLEAR" or status.startswith("REVIEW")),
                    f"{label}: invalid, failed or skipped status {status!r}")
            if contacts or unclassified:
                require(status.startswith("REVIEW"),
                        f"{label}: contact result must retain REVIEW status")
            if status.startswith("REVIEW"):
                review_pairs.append({
                    "pair": row["pair"], "status": status,
                    "contacts": contacts, "unclassified": unclassified,
                })
            if row["pair"] in CORD_GAP_LIMITS_MM:
                require(status == "CLEAR" and contacts == 0 and unclassified == 0,
                        f"{label}: cord group must be CLEAR without contacts")
                at_least(gap, CORD_GAP_LIMITS_MM[row["pair"]], f"{label} gap")
                cord_gaps[row["pair"]] = gap
        results.append({
            "preview_travel_mm": travel,
            "preload_mm": preload,
            "actual_stroke_mm": actual_stroke,
            "light": True,
            "isometric": isometric,
            "selected_groups": len(rows),
            "solid_interferences": 0,
            "eye_to_carriage_mm": case["eye_to_carriage_mm"],
            "cord_gaps_mm": cord_gaps,
            "contact_review_results": review_pairs,
        })
    require(seen == EXPECTED_CASES, "Incomplete configuration coverage")
    return {
        "status": "PASS",
        "study": "Current-source sampled rear-tether CAD clearance review",
        **identity,
        "source_capture": str(CAPTURE.relative_to(ROOT)),
        "capture_sha256": hashlib.sha256(CAPTURE.read_bytes()).hexdigest(),
        "configuration_count": 8,
        "selected_groups_per_configuration": 45,
        "total_selected_group_checks": 360,
        "solid_interferences": 0,
        "reference_cord_diameter_mm": 6,
        "minimum_eye_to_carriage_mm": min(x["eye_to_carriage_mm"] for x in results),
        "minimum_cord_gaps_mm": {
            pair: min(x["cord_gaps_mm"][pair] for x in results)
            for pair in CORD_GAP_LIMITS_MM
        },
        "configuration_results": results,
        "limitations": [
            "Eight discrete configurations; not a continuous motion sweep or tolerance/deformation analysis.",
            "Reference cord is a nominal 6 mm envelope; actual threading, bend, knots, chafe and mounting routing require a physical check.",
            "Intentional and unclassified contact results retain REVIEW status and are not blanket clearance passes.",
            "Lug/root strength, print material/process and maximum device pull remain unqualified; each eye must be assessed for full device force.",
            "Hard-stop force bypass, guide friction and off-axis loading require complete-device calibration and testing in tether mode.",
            "Illustrative hand/electronics envelopes do not release real hand fit, electronics mounting or electrical behavior.",
        ],
        "manufacturing_release": False,
    }


def main():
    try:
        report = validate()
    except (OSError, ValueError, KeyError, TypeError, UnicodeError) as error:
        # Replace stale success with a diagnostic failure if inputs change or a
        # capture is incomplete. A previous PASS must never survive this run.
        report = {
            "status": "FAIL", "error": str(error),
            "source_capture": str(CAPTURE.relative_to(ROOT)),
            "manufacturing_release": False,
        }
        OUTPUT.write_text(json.dumps(report, indent=2) + "\n")
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    OUTPUT.write_text(json.dumps(report, indent=2) + "\n")
    print("PASS: 8 configurations x 45 groups; zero solid interference; "
          "cord clearance and eye/carriage limits verified. Not a load release.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
