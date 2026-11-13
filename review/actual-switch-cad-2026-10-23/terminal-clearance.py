#!/usr/bin/env python3
"""Read-only nominal Omron SS-01GL2 terminal/lug envelope audit.

This creates no production geometry. The switch envelopes come from the
manufacturer's 2D dimensioned drawing; they are not factory CAD solids.
Run with /tmp/fingerworker-sensor-cad-20261022/bin/python.
"""
from __future__ import annotations

from io import BytesIO
import hashlib
import importlib.metadata
import json
from pathlib import Path
import re
import zipfile

import manifold3d as md
import numpy as np
import trimesh as tm

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CAD = ROOT / "review/flat132-palm-fit-2026-10-23"
EPS_MM3 = 1e-7
EXPECTED = {
    "source": (CAD / "fingerworker_flat132_palm_fit.fs", "4665c3ec4e983e478d34c6cfe923b3b60e6c8848f36b7c54b55b1989eaab6326"),
    "drawing": (ROOT / "vendor/omron_ss5gl2/SS_datasheet.pdf", "b7c3cc9e838c1049d58772242b56cd06af3526ac422907769acd892668ba1a09"),
    "neutral": (CAD / "native/Flat132_R3_neutral_final.zip", "0a8d367507744e7dfaaa46a6c1fa46639551293a0ad738d16f87fbebf2eef738"),
    "max": (CAD / "native/Flat132_R3_max28_p2_heavy_final.zip", "e3f4a92aeed099ec3ec5f11ce9a9f0bf948d419329b2672dd663ed449f0b2381"),
    "iso": (CAD / "native/Flat132_R3_isometric13_p2_final.zip", "f4bf05bd31a8929006b5136ed86b8b04c4dc293295bca9daec82a259bf10f921"),
    "step": (CAD / "native/Flat132_R3_final_AP214.step", "bc7f102b5f147d3647ec372ffde1c726087fe64487aa7733c78b3450901da4e3"),
}
TAB_CENTRES_Y = [-15.4, -6.6, 0.7]
TAB_BOUNDS = [np.array([[10.1, y - .25, 7.6], [14., y + .25, 10.8]]) for y in TAB_CENTRES_Y]
LUG_BOUNDS = np.array([[13.6, -17., 6.], [14., 2.8, 12.4]])


def sha(data):
    return hashlib.sha256(data).hexdigest()


def path_record(path):
    raw = path.read_bytes()
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(raw), "bytes": len(raw)}


def box(bounds):
    b = np.asarray(bounds, dtype=float)
    return md.Manifold.cube((b[1] - b[0]).tolist()).translate(b[0].tolist())


def volume(obj):
    value = float(obj.volume())
    if abs(value) < EPS_MM3:
        return 0.0
    return value


def manifold(raw):
    mesh = tm.load(BytesIO(raw), file_type="stl", force="mesh")
    if not mesh.is_watertight or not mesh.is_volume:
        raise ValueError("Source STL is not a closed, consistently oriented positive solid")
    obj = md.Manifold(md.Mesh64(vert_properties=np.asarray(mesh.vertices, np.float64), tri_verts=np.asarray(mesh.faces, np.uint64)))
    if obj.status() != md.Error.NoError:
        raise ValueError(str(obj.status()))
    return obj, mesh


def symmetric_difference_volume(a, b):
    return volume(a - b) + volume(b - a)


def zip_part(archive, ref):
    pattern = re.compile(r"(?<![A-Za-z0-9])" + re.escape(ref) + r"(?=[ _.-]|$)")
    with zipfile.ZipFile(archive) as z:
        names = [n for n in z.namelist() if n.lower().endswith(".stl") and pattern.search(Path(n).stem)]
        if len(names) != 1:
            raise ValueError(f"Expected exactly one {ref} in {archive}: {names}")
        raw = z.read(names[0])
    obj, mesh = manifold(raw)
    return obj, {"member": names[0], "sha256": sha(raw), "bounds_mm": mesh.bounds.tolist(), "triangles": len(mesh.faces)}


def binary_stl_bounds(raw):
    count = int.from_bytes(raw[80:84], "little")
    if len(raw) != 84 + 50 * count:
        raise ValueError("Expected native binary STL")
    dtype = np.dtype([("normal", "<f4", 3), ("vertices", "<f4", (3, 3)), ("attr", "<u2")])
    vertices = np.frombuffer(raw, dtype=dtype, offset=84, count=count)["vertices"].reshape(-1, 3)
    return np.array([vertices.min(axis=0), vertices.max(axis=0)], dtype=float)


def broadphase(term_bounds):
    """Independent raw native vertex bounds; only dimensional translation paths.

    Spring/lever shape changes are not being qualified here. Their conservative
    Y or X ranges remain wholly outside this local switch terminal envelope.
    """
    moving = {"P04", "H10", "H060", "H061"}
    preload = set("P05 H050 H051 H12 H01 H02 H13 H180 H181 H190 H191 H20 H23 H240 H241 H242 H243 H250 H251 H252 H253".split())
    rows, candidates = [], []
    for path in sorted((CAD / "assembly-mm").glob("*.stl")):
        raw = path.read_bytes()
        b = binary_stl_bounds(raw)
        sweep = b.copy()
        if path.stem in moving:
            sweep[0, 0] -= 30.0
        if path.stem in preload:
            sweep[1, 0] += 2.0
        candidate = bool(np.all(sweep[1] >= term_bounds[0]) and np.all(term_bounds[1] >= sweep[0]))
        if candidate:
            candidates.append(path.stem)
        rows.append({"reference": path.stem, "sha256": sha(raw), "native_bounds_mm": b.tolist(), "translation_sweep_bounds_mm": sweep.tolist(), "terminal_aabb_candidate": candidate})
    return {"device_solids": len(rows), "candidates": candidates, "source_meshes": rows,
            "limit": "Translation broadphase for terminal envelopes only. Spring/lever shapes remain illustrative, not manufacturer-qualified kinematics; their local bounds are separate from the terminal area."}


def main():
    sources = {}
    for label, (path, expected) in EXPECTED.items():
        record = path_record(path)
        if record["sha256"] != expected:
            raise ValueError(f"Unexpected {label} source hash")
        if path.suffix == ".zip":
            with zipfile.ZipFile(path) as z:
                bad = z.testzip()
                if bad:
                    raise ValueError(f"Archive CRC failure: {bad}")
                record.update(stl_members=sum(n.lower().endswith(".stl") for n in z.namelist()), crc_pass=True)
        sources[label] = record

    solids, native_records = {}, {}
    for ref in ["P05", "P01", "H09"]:
        path = CAD / "assembly-mm" / (ref + ".stl")
        solids[ref], mesh = manifold(path.read_bytes())
        native_records[ref] = {**path_record(path), "bounds_mm": mesh.bounds.tolist(), "triangles": len(mesh.faces), "closed_positive_volume": True}
    tabs = [box(b) for b in TAB_BOUNDS]
    yoke = solids["P05"]

    # Exact continuous rectangular-envelope sweep: relative to neutral P05,
    # p in[0,2] is the stationary terminal box extruded back along X by2mm.
    # Compare intersection with the expected full-web slab to establish that
    # the native yoke has the same plane X9 over every terminal cross-section.
    continuous = []
    for i, b in enumerate(TAB_BOUNDS):
        swept = b.copy()
        swept[0, 0] -= 2
        expected_overlap = swept.copy()
        expected_overlap[1, 0] = 9
        hit = box(swept) ^ yoke
        residual = symmetric_difference_volume(hit, box(expected_overlap))
        if residual > EPS_MM3:
            raise ValueError(f"Analytic web slab not proven for terminal {i + 1}: {residual}")
        continuous.append({"terminal": i + 1, "swept_relative_bounds_mm": swept.tolist(),
                           "exact_native_intersection_bounds_mm": expected_overlap.tolist(),
                           "native_vs_analytic_slab_symmetric_difference_mm3": residual,
                           "full_cross_section_mm2": 1.6,
                           "per_terminal_envelope_overlap_volume_mm3": "1.6 * max(0, preload_mm - 1.1)",
                           "axial_gap_mm": "1.1 - preload_mm"})

    # Numerical witnesses back up the exact continuous rectangular sweep;
    # they are not being substituted for continuous coverage.
    preloads = sorted(set(round(float(p), 10) for p in np.linspace(0, 2, 201)) | {1.1})
    samples = []
    max_error = 0.0
    for p in preloads:
        moved_yoke = yoke.translate([p, 0, 0])
        hits = [volume(t ^ moved_yoke) for t in tabs]
        expected = 1.6 * max(0.0, p - 1.1)
        max_error = max(max_error, *(abs(v - expected) for v in hits))
        samples.append({"preload_mm": p, "gap_or_negative_axial_overlap_mm": round(1.1 - p, 10), "per_terminal_envelope_intersection_mm3": hits, "total_envelope_intersection_mm3": sum(hits)})
    if max_error > EPS_MM3:
        raise ValueError(f"Sample/analytic mismatch: {max_error}")

    stationary_checks = []
    for ref in ["P01", "H09"]:
        for i, t in enumerate(tabs):
            v = volume(t ^ solids[ref])
            stationary_checks.append({"terminal": i + 1, "reference": ref, "intersection_volume_mm3": v, "meaning": "Intentional terminal root/body contact" if ref == "H09" else "No nominal terminal-envelope intrusion into fixed frame"})
            if v > EPS_MM3:
                raise ValueError(f"Unexpected stationary intersection {ref}")

    lug = box(LUG_BOUNDS)
    swept_lug_bounds = LUG_BOUNDS.copy()
    swept_lug_bounds[0, 0] -= 2
    lug_checks = {
        "envelope_bounds_mm": LUG_BOUNDS.tolist(),
        "shape": "Conservative full-length strip; not actual lug profile",
        "conditional_thickness_assumption": "The projecting lug stays inside the dimensioned 6.4mm housing thickness, Z6..12.4. PDF does not independently dimension lug Z/profile; exact factory CAD/measurement still needed.",
        "fixed_P01_positive_intersection_mm3": volume(lug ^ solids["P01"]),
        "fixed_H09_positive_intersection_mm3": volume(lug ^ solids["H09"]),
        "full_preload_relative_sweep_bounds_mm": swept_lug_bounds.tolist(),
        "full_preload_sweep_intersection_with_P05_mm3": volume(box(swept_lug_bounds) ^ yoke),
        "native_support_contact": "Envelope bottom Z6 coincides with P01 pedestal top Z6; this is a nominal support contact, not positive-volume interference.",
        "envelope_minimum_gap_to_P05_mm": {str(p): float(lug.min_gap(yoke.translate([p, 0, 0]), 10)) for p in [0, 1, 2]},
        "status": "CONDITIONAL_NOMINAL_ENVELOPE_CLEAR_OF_P01_AND_P05_FOR_ALL_PRELOADS"
    }
    if max(lug_checks["fixed_P01_positive_intersection_mm3"], lug_checks["fixed_H09_positive_intersection_mm3"], lug_checks["full_preload_sweep_intersection_with_P05_mm3"]) > EPS_MM3:
        raise ValueError("Lug envelope has unexpected positive-volume intersection")

    endpoint_checks = []
    for pose in ["max", "iso"]:
        actual, record = zip_part(EXPECTED[pose][0], "P05")
        difference = symmetric_difference_volume(actual, yoke.translate([2, 0, 0]))
        # Separately exported native STLs can retessellate fillets. This
        # endpoint witness tolerance is explicit and is not the probe zero
        # threshold or an allowance on fabrication clearance.
        if difference > .01:
            raise ValueError(f"Native {pose} P05 is not neutral translated2mm: {difference}")
        hits = [volume(t ^ actual) for t in tabs]
        endpoint_checks.append({"pose": pose, "preload_mm": 2, "native_P05": record, "native_vs_neutral_translated_2mm_symmetric_difference_mm3": difference, "independent_STL_retessellation_witness_tolerance_mm3": .01, "per_terminal_envelope_intersection_mm3": hits})

    region = np.array([np.min(np.array(TAB_BOUNDS)[:, 0], axis=0), np.max(np.array(TAB_BOUNDS)[:, 1], axis=0)])
    bounds_audit = broadphase(region)
    if bounds_audit["device_solids"] != 52 or bounds_audit["candidates"] != ["H09", "P01", "P05"]:
        raise ValueError(f"Unexpected raw-STL broadphase: {bounds_audit['candidates']}")

    result = {
        "status": "NOMINAL_DRAWING_ENVELOPE_INTERFERENCE_FOUND_FACTORY_CAD_PENDING",
        "date": "2026-10-23",
        "scope": "Independent read-only check of previously omitted SS-01GL2 solder-terminal and lower-lug drawing envelopes against frozen R3 native geometry. Does not modify or re-certify the earlier proxy-based report.",
        "sources": sources,
        "script": path_record(Path(__file__).resolve()),
        "tools": {name: importlib.metadata.version(name) for name in ["numpy", "trimesh", "manifold3d"]},
        "method": "Native watertight STL/manifold Boolean; independent raw-STL vertex bounds; exact rectangular probe sweep for all preload values;201 numerical witnesses plus the two native preload2poses. No remeshing, repairs or fabrication geometry edits.",
        "numerical_zero_volume_threshold_mm3": EPS_MM3,
        "manufacturer_drawing": {
            "url": "https://omronfs.omron.com/en_US/ecb/products/pdf/en-ss.pdf",
            "pages": {"solder_tabs": 4, "hinge_roller_and_lower_lug": 6, "mounting": 7},
            "drawing_interpretation_by": "Independent mount_redesign dimension audit, dimension-audit.json; exact dimensions visually checked against manufacturer PDF",
            "dimension_audit": path_record(HERE / "dimension-audit.json"),
            "mapping": "Manufacturer U maps Y=U-17; V maps X=V+14; housing thickness centre Z9.2. Mounting-axis line X16.5; tab tips6.4below that line give X10.1.",
            "terminal_centres_Y_mm": TAB_CENTRES_Y,
            "terminal_envelope_bounds_mm": [b.tolist() for b in TAB_BOUNDS],
            "not_factory_CAD": True,
            "profile_limits": "Rectangular bounding envelopes, not actual terminal solids. Exact tab corner/Ø1.6hole profiles and lug profile are not fully dimensioned. Their absent details cannot be recovered by assigning arbitrary contours.",
        },
        "native_parts": native_records,
        "preload_domain_mm": [0, 2],
        "stroke_domain": "0<=stroke_mm;0<=preload_mm<=2;stroke_mm+preload_mm<=30. Terminals and P05-relative clearance depend on preload only; P05 does not follow stroke.",
        "terminal_clearance": {
            "first_nominal_envelope_contact_preload_mm": 1.1,
            "positive_overlap_preload_interval_mm": {"lower_exclusive": 1.1, "upper_inclusive": 2},
            "preload_0_axial_gap_mm": 1.1,
            "preload_2_axial_overlap_mm": .9,
            "preload_2_per_terminal_envelope_intersection_mm3": [1.44, 1.44, 1.44],
            "preload_2_total_envelope_intersection_mm3": 4.32,
            "interpretation": "Native P05 fills the entire drawing-envelope cross-section at the nominal terminal tip at preload2. The envelope therefore fails the nominal full-preload packaging check.4.32mm³ is box-envelope intersection, not a claim of exact factory metal collision volume. Factory STEP or measurement is still required to resolve precise terminal profiles and routing.",
            "continuous_native_slab_proof": continuous,
            "sample_count": len(samples),
            "maximum_sample_vs_analytic_error_mm3": max_error,
            "samples": samples,
            "fixed_frame_and_body_checks": stationary_checks,
            "native_preload_2_pose_witnesses": endpoint_checks,
        },
        "lower_mount_lug": lug_checks,
        "terminal_broadphase": bounds_audit,
        "remaining_unresolved": [
            "Exact SS-01GL2 manufacturer STEP unavailable to this audit; no surrogate variant was treated as the exact factory part.",
            "Terminal holes/corners, lug Z/profile and actuator mechanism are not fully defined by available drawing; rectangular envelopes do not prove exact physical metal volume.",
            "No dimensional tolerance stack, solder fillets, insulated leads, bend radii or assembly/service wire-routing envelope is included.",
            "Switch operation point, total allowed travel and mount clamping/washer suitability require separate confirmation; this check does not qualify the kinematic proxy or force mode.",
            "Resolve drawing-envelope terminal/P05 clash and rerun actual factory geometry checks before claiming installation works through the complete preload range."
        ],
        "frozen_R3_files_modified": False,
    }
    (HERE / "terminal-clearance.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    make_figure()
    print(json.dumps({"status": result["status"], "preload_2_axial_envelope_overlap_mm": .9, "total_box_envelope_intersection_mm3": 4.32, "full_preload_lug_envelope_intersection_mm3": lug_checks["full_preload_sweep_intersection_with_P05_mm3"], "samples": len(samples), "report_sha256": sha((HERE / "terminal-clearance.json").read_bytes())}, indent=2))


def make_figure():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle

    fig, axes = plt.subplots(1, 2, figsize=(12.5, 6.6), sharey=True)
    for ax, preload in zip(axes, [0, 2]):
        # Local exact yoke web section, Z9.2; no fabrication shape is changed.
        ax.add_patch(Rectangle((-17, -7 + preload), 20, 16, color="#678398", alpha=.8, label="P05 native solid web, Z9.2 section"))
        ax.add_patch(Rectangle((-17, 14), 19.8, 10.2, facecolor="#d1d3d4", edgecolor="#555", label="H09 current housing proxy"))
        for i, y in enumerate(TAB_CENTRES_Y):
            ax.add_patch(Rectangle((y - .25, 10.1), .5, 3.9, facecolor="#eea341", edgecolor="#9b5310", label="Drawing terminal box envelope" if i == 0 else None))
            if preload > 1.1:
                ax.add_patch(Rectangle((y - .25, 10.1), .5, preload - 1.1, facecolor="#be303c", edgecolor="#7c1420", label="Envelope/P05 intersection" if i == 0 else None))
        ax.axhline(9 + preload, color="#345063", ls="--", lw=1)
        ax.axhline(10.1, color="#b46e10", ls=":", lw=1)
        gap = 1.1 - preload
        ax.annotate("", xy=(3.8, 10.1), xytext=(3.8, 9 + preload), arrowprops={"arrowstyle": "<->", "color": "#252525"})
        ax.text(4.1, (10.1 + 9 + preload) / 2, f"{abs(gap):.1f} mm\n" + ("gap" if gap > 0 else "overlap"), va="center", fontsize=10)
        ax.set_title(f"Preload {preload} mm", fontsize=14, fontweight="bold")
        ax.set_xlabel("World Y [mm]")
        ax.set_xlim(-18.5, 7.2)
        ax.set_ylim(6.8, 25.3)
        ax.set_aspect("equal")
        ax.grid(alpha=.18)
    axes[0].set_ylabel("World X [mm] — toward housing / finger grip →")
    handles, labels = axes[1].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=2, bbox_to_anchor=(.5, .095), frameon=False, fontsize=10)
    fig.suptitle("SS-01GL2 omitted-terminal envelope check against native R3 yoke", y=.96, fontsize=16, fontweight="bold")
    fig.text(.5, .035, "Nominal dimensioned drawing envelopes; not factory STEP. Exact metal profiles, tolerances, solder and wiring remain unresolved.\nP05 section checked by native STL Boolean; at preload 2 mm each terminal box intersects by 1.44 mm³ (4.32 mm³ total).", ha="center", va="center", fontsize=10)
    fig.subplots_adjust(left=.08, right=.96, bottom=.24, top=.87, wspace=.12)
    fig.savefig(HERE / "terminal-clearance.png", dpi=180, facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    main()
