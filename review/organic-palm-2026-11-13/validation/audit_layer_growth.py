#!/usr/bin/env python3
"""Quantify new palm-bolster overhangs by horizontal mesh sections.

This is an isolated geometric screening of new upper stock. The native sliced
paths remain authoritative for extrusion, support placement and adhesion.
"""
from pathlib import Path
import argparse,hashlib,json,math
import numpy as np
import trimesh
from shapely import affinity
from shapely.geometry import box,GeometryCollection
from shapely.ops import unary_union
HERE=Path(__file__).resolve().parent;STUDY=HERE.parent;ROOT=STUDY.parents[1]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def horizontal(mesh,z):
    sec=mesh.section(plane_origin=[0,0,z],plane_normal=[0,0,1])
    if sec is None:return GeometryCollection()
    path,to3d=sec.to_2D()
    assert path.is_closed,'Open horizontal section'
    polys=list(path.polygons_full)
    assert all(p.is_valid for p in polys),'Invalid horizontal polygon'
    transform=[to3d[0,0],to3d[0,1],to3d[1,0],to3d[1,1],to3d[0,3],to3d[1,3]]
    return unary_union([affinity.affine_transform(p,transform) for p in polys])

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--mesh',type=Path,required=True);ap.add_argument('--source',type=Path,required=True);ap.add_argument('--source-sha',required=True);ap.add_argument('--native',action='store_true');args=ap.parse_args()
    assert sha(args.source)==args.source_sha
    base=ROOT/'review/side-thumb-2026-11-12/mechanics/P01_side_thumb.stl'
    assert sha(base)=='013f0e2d9d8fd8849594e4621b9ddfb632524e9178a7caf8028073159d97551a'
    mesh=trimesh.load(args.mesh,force='mesh');old=trimesh.load(base,force='mesh')
    assert mesh.is_watertight and old.is_watertight
    # Includes both wrist and sensor-facing contour growth of the declared
    # bolster. The subtraction excludes unchanged legacy shelves elsewhere.
    roi=box(-34,-60.5,-7.9,60.5)
    dz=.1;eps=.000013;slack=.025;rows=[]
    heights=np.arange(16.4,math.ceil(float(mesh.bounds[1,2])*10)/10+.001,dz)+eps
    prev=horizontal(mesh,float(heights[0]))
    for z in heights[1:]:
        current=horizontal(mesh,float(z));baseline=horizontal(old,float(z))
        added=current.difference(baseline).intersection(roi)
        unsupported=added.difference(prev.buffer(dz+slack,quad_segs=16))
        rows.append(dict(z_mm=float(z),new_bulge_section_area_mm2=float(added.area),outside_45deg_envelope_area_mm2=float(unsupported.area)))
        prev=current
    maximum=max(q['outside_45deg_envelope_area_mm2'] for q in rows)
    report=dict(status='PASS_GEOMETRIC_LAYER_GROWTH' if maximum<.01 else 'REVIEW_GEOMETRIC_LAYER_GROWTH',source_sha256=args.source_sha,mesh_sha256=sha(args.mesh),baseline_mesh_sha256=sha(base),validator_sha256=sha(__file__),native_mesh=bool(args.native),horizontal_increment_mm=dz,mesh_tolerance_slack_mm=slack,allowed_outward_growth_mm_per_mm_z=1,section_area_threshold_mm2=.01,maximum_outside_envelope_area_mm2=maximum,roi_xy_mm=[[-34,-60.5],[-7.9,60.5]],checks=rows,scope='Sampled mesh-section screening of new upper palm stock only. Finite section spacing and mesh tolerance are explicit; actual native G-code support/overhang review remains required.')
    assert sha(args.source)==args.source_sha
    out=HERE/('native-layer-growth.json' if args.native else 'local-layer-growth.json');out.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='checks'},indent=2))
if __name__=='__main__':main()
