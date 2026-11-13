#!/usr/bin/env python3
"""Compare R13 palm printing to frozen R12; never edits CAD or slicer files."""
from pathlib import Path
import argparse,json,sys,zipfile,xml.etree.ElementTree as ET
from collections import defaultdict,Counter
import numpy as np
from shapely.geometry import box as rect,GeometryCollection
from shapely.ops import unary_union
import check_print_features as paths

HERE=Path(__file__).resolve().parent;STUDY=HERE.parent;ROOT=STUDY.parents[1]
PACK=ROOT/'print/bambu-R13-simple-palm-2026-11-03'
BASELINE=ROOT/'print/bambu-R12-simplified-2026-11-03'
sha=paths.sha

def load_slice(layout_path,slice_path):
    layout=json.loads(layout_path.read_text());row=next(r for r in layout['placements'] if r['ref']=='P01')
    assert np.allclose(row['rotation_3x3'],np.eye(3))
    with zipfile.ZipFile(slice_path) as z:
        cfg=ET.fromstring(z.read('Metadata/model_settings.config'))
        setting=next(o for o in cfg.findall('object') if any(m.get('key')=='name' and m.get('value','').startswith('P01 ') for m in o.findall('metadata')))
        settings={m.get('key'):m.get('value') for m in setting.findall('metadata')}
        info=ET.fromstring(z.read('Metadata/slice_info.config'));plate=info.findall('plate')[0]
        assert len(plate.findall('object'))==1
        label=int(plate.find('object').get('identify_id'))
        parsed=paths.native_paths(paths.parse(z.read('Metadata/plate_1.gcode').decode(),label),row)
        metrics={m.get('key'):m.get('value') for m in plate.findall('metadata')}
    return dict(layout=layout,row=row,settings=settings,metrics=metrics,
        model=[s for s in parsed if s['obj']==label and s['feature'] not in paths.NONMODEL],
        support=[s for s in parsed if s['feature'] in paths.SUPPORT])

def palm_support(items):
    out=[]
    for s in items:
        pp=s['native_points'];lo=pp.min(0);hi=pp.max(0)
        if lo[0]<=-17 and hi[0]>=-48 and lo[1]<=68 and hi[1]>=-68 and -2.1<=hi[2]<=13:
            out.append(s)
    return out

def footprints(items):
    grouped=defaultdict(list);clip=rect(-48,-68,-17,68)
    for s in items:
        key=(s['feature'],round(s['native_b'][2],3),round(s['height'],3))
        poly=paths.xy_line(s).buffer(s['width']/2,quad_segs=12).intersection(clip)
        if not poly.is_empty:grouped[key].append(poly)
    return {k:unary_union(v) for k,v in grouped.items()}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--candidate',action='store_true');ap.add_argument('--output',type=Path)
    args=ap.parse_args()
    layout_path=PACK/('candidate-flat-layout.json' if args.candidate else 'plate-layout.json')
    checkpoint=PACK/'checkpoints/local-palm-candidates'
    if args.candidate and not layout_path.exists():layout_path=checkpoint/'candidate-flat-layout.json'
    layout=json.loads(layout_path.read_text())
    slice_path=PACK/'validation'/('candidate-flat' if args.candidate else '')/(Path(layout['native_project']).stem+'_verification.gcode.3mf')
    if args.candidate and not slice_path.exists():slice_path=checkpoint/'validation-candidate-flat'/slice_path.name
    output=args.output or (STUDY/'mechanics/candidate-palm-print-check.json' if args.candidate else PACK/'validation/palm-support-check.json')
    snapshots={str(p):sha(p) for p in (layout_path,slice_path)}
    current=load_slice(layout_path,slice_path)
    old_slice=BASELINE/'validation/Fingerworker_R12_H2D_04mm_PLA_Fit_Test_verification.gcode.3mf'
    baseline=load_slice(BASELINE/'plate-layout.json',old_slice)
    checks=[];metrics={}
    def add(name,ok,**e):checks.append(dict(name=name,status='PASS' if bool(ok) else 'FAIL',**e))
    add('Default automatic bridge direction retained for P01',float(current['settings'].get('bridge_angle','0').split(',')[0])==0,
        actual_bridge_angle=current['settings'].get('bridge_angle','0'))
    support=palm_support(current['support']);old_support=palm_support(baseline['support'])
    new_fp=footprints(support);old_fp=footprints(old_support);extra=[];fine_deltas=[]
    for key,poly in new_fp.items():
        old_poly=old_fp.get(key,GeometryCollection())
        fine_difference=poly.difference(old_poly.buffer(.02))
        if fine_difference.area>1e-7:fine_deltas.append(dict(feature=key[0],top_z_mm=key[1],outside_0_02mm_area_mm2=fine_difference.area,bounds_xy_mm=list(fine_difference.bounds)))
        tolerance=.05 if key[0]=='Support' else .02
        difference=poly.difference(old_poly.buffer(tolerance))
        if difference.area>1e-7:extra.append(dict(feature=key[0],top_z_mm=key[1],height_mm=key[2],new_footprint_area_mm2=difference.area))
    extra_area=sum(r['new_footprint_area_mm2'] for r in extra)
    add('Palm support contacts and structures remain within retained R12 envelopes',extra_area<.01,
        new_outside_area_sum_mm2=extra_area,contact_coordinate_tolerance_mm=.02,bulk_coordinate_tolerance_mm=.05,
        new_support_segments=len(support),baseline_support_segments=len(old_support),new_regions=extra,fine_bulk_deltas=fine_deltas,
        method='Actual bead footprints compared separately by feature, top Z and layer height. Interface/transition contacts use0.02 mm tolerance; bulk roads use0.05 mm (one eighth of nozzle diameter) to account for tessellation and changed road endpoints. Full actual beads also undergo the independent exact added-stock removal sweep below; this comparison does not waive new contacts or new support layers.')
    metrics['support_features']={k:dict(Counter(s['feature'] for s in ss)) for k,ss in [('R13',support),('R12',old_support)]}
    contact=paths.roi(current['support'],[-37.5,-58.2,9.7],[-27,58.2,30.2])
    add('New rounded palm contact rail stays support-free',not contact,support_segments=len(contact))
    for side in (-1,1):
        yy=(-58.1,-38.9) if side<0 else (38.9,58.1)
        # Only the new gap: exclude old palm-plate and rod-block roofs.
        zone=paths.roi(current['model'],[-23.2,yy[0],9.5],[-18.05,yy[1],12.5])
        bridges=[s for s in zone if 'bridge' in s['feature'].lower()]
        spans=paths.free_bridge_spans(bridges,current['model'])
        maximum=max([s['longest_actual_unbacked_centerline_mm'] for s in spans] or [0])
        add('Tent underside closes with short actual bridge side'+str(side),len(zone)>20 and maximum<=1.5,
            model_segments=len(zone),bridge_segments=len(bridges),longest_actual_unbacked_centerline_mm=maximum,layer_evidence=spans)
        center=side*51
        maxima={};evidence={}
        for name,data in [('R12',baseline),('R13',current)]:
            roof=paths.roi(data['model'],[-17.2,center-3.3,20],[-7.8,center+3.3,21.6])
            br=[s for s in roof if 'bridge' in s['feature'].lower()]
            evidence[name]=paths.free_bridge_spans(br,data['model'])
            maxima[name]=max([s['longest_actual_unbacked_centerline_mm'] for s in evidence[name]] or [0])
        add('Functional front rod-socket roof bridge not lengthened side'+str(side),maxima['R13']<=maxima['R12']+.05,
            longest_actual_unbacked_centerline_mm=maxima,layer_evidence=evidence)
    # Preserve the electronics underside and ensure added stock does not obstruct
    # the former wristward removal direction of any actual palm support bead.
    sys.path.insert(0,str(ROOT/'review/flat132-solid-palm-2026-10-23/validation'));import audit_solid_palm as b
    old_inv=json.loads((ROOT/'review/simplification-2026-11-03/validation/native-step-inventory.json').read_text())
    assert sha(old_inv['native_step'])==old_inv['native_step_sha256']
    old_shapes=b.read_step(old_inv['native_step'])[0]
    old_frame=old_shapes[old_inv['native_part_correspondence']['P01']['candidates'][0]['solid_index']]
    if args.candidate:
        frame_path=STUDY/'mechanics/P01_simple_palm.step';frame=b.read_step(frame_path)[0][0]
    else:
        inv=json.loads((HERE/'native-step-inventory.json').read_text());frame_path=Path(inv['native_step'])
        assert sha(frame_path)==inv['native_step_sha256']
        frame=b.read_step(frame_path)[0][inv['native_part_correspondence']['P01']['candidates'][0]['solid_index']]
    added=b.cut(frame,old_frame);removed=b.cut(old_frame,frame);aa=b.bounds(added)
    low=b.box([-60,-70,-3],[0,70,9.4999])
    delta=b.volume(b.common(added,low))+b.volume(b.common(removed,low))
    add('Existing electronics underside below Z9.5 unchanged',delta<1e-6,difference_mm3=delta)
    maximum=0.;worst=None;tested=0
    for s in support:
        pp=s['native_points'];lo=pp.min(0);hi=pp.max(0)
        lo[:2]-=s['width']/2;hi[:2]+=s['width']/2;lo[2]=hi[2]-s['height'];hi[2]+=1e-5;lo[0]=-60
        if np.any(hi<aa[0]) or np.any(lo>aa[1]):continue
        overlap=b.volume(b.common(added,b.box(lo,hi)));tested+=1
        if overlap>maximum:maximum=overlap;worst=dict(lo=lo.tolist(),hi=hi.tolist(),overlap_mm3=overlap)
    add('Added palm stock creates no new wristward support-removal obstruction',maximum<1e-5,
        actual_support_beads=len(support),exact_overlap_candidates=tested,maximum_intersection_mm3=maximum,worst=worst,
        method='Conservative full-bead boxes including arc extrema swept toward X−60 and intersected with added CAD material only; demonstrates no new obstruction relative to R12, not physical break-away force.')
    add('Checked slice and layout stayed unchanged',all(sha(Path(p))==h for p,h in snapshots.items()))
    failures=[c for c in checks if c['status']!='PASS']
    result=dict(status=('PASS_LOCAL_R13_PALM_PRINT_CANDIDATE' if args.candidate else 'PASS_FINAL_R13_PALM_SUPPORTS') if not failures else 'FAIL',
        failed_count=len(failures),failures=failures,checks=checks,metrics=metrics,
        CAD_source_sha256=layout['CAD_source_sha256'],layout_sha256=sha(layout_path),sliced_archive_sha256=sha(slice_path),
        native_step_sha256=sha(frame_path),baseline_native_step_sha256=old_inv['native_step_sha256'],baseline_sliced_archive_sha256=sha(old_slice),validator_sha256=sha(__file__),
        scope='New palm underside bridges, retained front socket bridges, actual support footprint changes and added-CAD obstruction of wristward cleanup.',
        limitations=['No physical surface, PLA fit, fatigue or strength qualification.','Support removal comparison preserves the R12 access assumption; no measured adhesive/break-away force.'])
    output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],checks=len(checks),failures=failures),indent=2))
    return bool(failures)

if __name__=='__main__':raise SystemExit(main())
