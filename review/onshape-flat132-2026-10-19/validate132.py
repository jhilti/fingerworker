#!/usr/bin/env python3
"""Independently validate the native 132 mm / 72 mm Onshape study export.

Input must be a complete neutral-pose assembly (0 stroke, 0 preload), not a
print-bed arrangement. The final V5 design retains detachable P02 with a new
keyed two-M4 mount. This script reads CAD and writes only its JSON report.
It establishes geometric packaging evidence, not strength or sensor accuracy.
"""
from pathlib import Path
import argparse
import hashlib
import json
import math
import sys
import time

import numpy as np

D = Path(__file__).resolve().parent
ROOT = D.parents[1]
sys.path.insert(0, str(ROOT / 'review/narrow-design-2026-10-17'))
sys.path.insert(0, str(ROOT / 'review/narrow-feasibility-2026-10-18'))
from validate_narrow import (Auditor, REFS, MOVING, PRELOAD, SPRINGS,
    ARTICULATED, INSERTION_REMOVED, INTENDED, load_inputs, manifold,
    cylinder_x, clean_numbers, aabb_clear)
from validate_study import box, cyl, cyl_z, as_mesh, difference_volume

EXPECTED = set(REFS)
BASELINE_SOURCE_SHA = '43a2dc70e3eed4308534da7772f4b82bf845c97d6f6a53456d0d63aa9552fb33'
VOLUME_TOL = .01


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def input_identity(path):
    if path.is_file():
        return {'archive_sha256': sha(path)}
    return {str(p.relative_to(path)): sha(p) for p in sorted(path.rglob('*.stl'))}


def linear_sweep(name, moving, fixed, vector, start, stop, interval=.0625):
    """Continuous finite insertion/removal proof in any translation direction.

    Endpoint interior overlaps fail. Near-contact intervals remain unresolved;
    neither a zero sampled volume nor a coarse sample grid creates a PASS.
    """
    vector = np.asarray(vector, float)
    speed = float(np.linalg.norm(vector))
    mb = np.array(moving.bounding_box()).reshape(2, 3)
    fb = np.array(fixed.bounding_box()).reshape(2, 3)
    row = dict(name=name, parameter_range_mm=[start, stop],
               translation_per_parameter=vector.tolist(), sampled_parameters_mm=[],
               intersections=[], unresolved_intervals=[], certified_intervals=0)
    samples = {}

    def sample(t, search):
        if t not in samples:
            obj = moving.translate((vector * t).tolist())
            vol = float((obj ^ fixed).volume())
            samples[t] = dict(volume_mm3=vol, gap_mm=0., search=0.)
            if vol > VOLUME_TOL:
                row['intersections'].append(dict(parameter_mm=t, volume_mm3=vol))
        result = samples[t]
        if result['volume_mm3'] <= VOLUME_TOL and result['search'] < search:
            result['gap_mm'] = float(moving.translate((vector*t).tolist()).min_gap(fixed, search))
            result['search'] = search
        return result

    def certify(lo, hi):
        ba, bb = mb + vector*lo, mb + vector*hi
        swept = np.stack((np.minimum(ba[0], bb[0]), np.maximum(ba[1], bb[1])))
        if aabb_clear(swept, fb):
            row['certified_intervals'] += 1
            return
        mid, half = (lo+hi)/2, speed*(hi-lo)/2
        result = sample(mid, half+.01)
        if result['volume_mm3'] > VOLUME_TOL:
            return
        if result['gap_mm'] > half+1e-5:
            row['certified_intervals'] += 1
        elif hi-lo <= interval:
            row['unresolved_intervals'].append(dict(parameter_range_mm=[lo,hi],
                midpoint_gap_mm=result['gap_mm'], midpoint_volume_mm3=result['volume_mm3']))
        else:
            certify(lo, mid)
            certify(mid, hi)

    try:
        sample(start, .01)
        sample(stop, .01)
        certify(start, stop)
        row.update(status='INTERFERENCE' if row['intersections'] else
            'UNRESOLVED_NEAR_CONTACT' if row['unresolved_intervals'] else
            'CONTINUOUS_CLEARANCE_CERTIFIED', sampled_parameters_mm=sorted(samples),
            maximum_sampled_volume_mm3=max(x['volume_mm3'] for x in samples.values()))
    except Exception as error:
        row.update(status='UNCHECKED', reason=f'{type(error).__name__}: {error}')
    return row


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('assembly', type=Path, help='Native neutral-pose whole-assembly ZIP or extracted STL directory')
    parser.add_argument('--baseline', type=Path, default=ROOT/'review/narrow-design-2026-10-17/assembly-mm')
    parser.add_argument('--study-source', type=Path)
    parser.add_argument('--provenance', type=Path, help='Optional native-export provenance JSON; copied as evidence, not trusted as geometry')
    parser.add_argument('--exclude-pattern', help='Explicitly exclude duplicated unrelated staging members')
    parser.add_argument('--output', type=Path, default=D/'validation132.json')
    parser.add_argument('--minimum-interval', type=float, default=.0625)
    parser.add_argument('--mount-variant', choices=('v4','v5','v6'), default='v6',
        help='Final V6:6.5 mm foot plane, forward stepped palm bosses, M4X-16 and rear keysX-22..-20')
    args = parser.parse_args()
    mount_z=9.5 if args.mount_variant=='v4' else 6.5
    head_z=13.5 if args.mount_variant=='v4' else 10.5
    key_top=11. if args.mount_variant=='v4' else 8.
    pilot_bottom=2.5 if args.mount_variant=='v4' else .2
    bolt_x=-16. if args.mount_variant=='v6' else -18.
    key_x=(-22.,-20.) if args.mount_variant=='v6' else (-13.5,-10.5)
    began = time.monotonic()
    source = ROOT/'fingerworker_mvp.fs'
    baseline_source_hash = sha(source)
    baseline_identity = input_identity(args.baseline)
    study_identity = input_identity(args.assembly)
    inputs, ignored = load_inputs(args.assembly, args.exclude_pattern)
    original, _ = load_inputs(args.baseline, None)
    audit = Auditor(inputs, VOLUME_TOL, args.minimum_interval)
    base = Auditor(original, VOLUME_TOL, args.minimum_interval)
    groups = ['scalars','preservation','static_pairs','operating_sweeps',
        'insertion_sweeps','spring_envelopes','isometric_cases','support_checks',
        'mount_checks','ligament_checks','access_checks','force_curve_datum_check']
    report = dict(status='RUNNING', study_only=True, units='mm',
        scope='Full-resolution native exported solid geometry; no load, fatigue, tolerance, hand-fit or measurement qualification',
        validator_sha256=sha(Path(__file__)),
        assembly=str(args.assembly.resolve()), assembly_input_identity=study_identity,
        baseline=str(args.baseline.resolve()), baseline_source_sha256=baseline_source_hash,
        expected_baseline_source_sha256=BASELINE_SOURCE_SHA,
        study_source=str(args.study_source.resolve()) if args.study_source else None,
        study_source_sha256=sha(args.study_source) if args.study_source else None,
        native_export_provenance=json.loads(args.provenance.read_text()) if args.provenance else None,
        pose_assumption=dict(stroke_mm=0, preload_mm=0),
        volume_tolerance_mm3=VOLUME_TOL, minimum_adaptive_interval_mm=args.minimum_interval,
        expected_device_part_count=51, device_part_count=len(inputs),
        architecture=args.mount_variant+' detachable palm module, one M4 per side with two positive antirotation keys; original keeper/screw service after module removal',
        palm_mount_config=dict(interface_z_mm=mount_z,head_bearing_z_mm=head_z,
            key_top_z_mm=key_top,pilot_bottom_z_mm=pilot_bottom,bolt_x_mm=bolt_x,key_x_interval_mm=key_x),
        missing_device_refs=sorted(EXPECTED-set(inputs)), unexpected_device_refs=sorted(set(inputs)-EXPECTED),
        ignored_auxiliary_or_alternative_members=ignored,legacy_contacts=[],
        mesh_inventory={}, intended_contacts=[dict(pair=sorted(pair), reason=reason) for pair,reason in INTENDED.items()],
        method='Closed full-resolution Manifold solid intersections; adaptive 1-Lipschitz minimum-gap continuous translation certificates; exact stop-slab witnesses',
        limitations=[
            'A fresh Onshape export must be linked to the compiled branch by separate provenance; this script does not regenerate Onshape.',
            'A geometry PASS does not establish plastic strength, fatigue life, print tolerance, comfort or loaded sensor accuracy.',
            'The ordered spring force curve is retained by axial geometry; rates and free lengths are source data, not a measured calibration.',
            'Switch lever/roller articulation requires native stroke-dependent regeneration and is excluded from fixed-mesh rigid sweeps.',
            'The rear carriage insertion path assumes rear caps, bumpers, rods and springs removed, at zero preload.',
            'The new keyed two-M4 palm joint has unqualified strength and durability; geometry clearance does not establish equality with the original four-M4 joint.',
            'Finite access sweeps describe their exact assumed path/tool envelope; they do not certify every hand tool or assembly sequence.',
            'The provisional 4 mm roof screening target is an idealized geometry target, not an established material-strength limit.'])
    report.update({group:[] for group in groups})
    invalid = dict(audit.invalid)
    for ref, item in sorted(inputs.items()):
        mesh = item['mesh']
        if ref in SPRINGS:
            try:
                manifold(mesh)
            except Exception as error:
                invalid[ref] = str(error)
        report['mesh_inventory'][ref] = dict(member=item['member'], sha256=item['sha256'],
            bounds_mm=mesh.bounds.tolist(), triangles=len(mesh.faces),
            watertight=bool(mesh.is_watertight), is_volume=bool(mesh.is_volume),
            validity=invalid.get(ref,'VALID'), motion_role='MOVING' if ref in MOVING else
                'PRELOAD_TRANSLATED' if ref in PRELOAD else 'ILLUSTRATIVE_SPRING' if ref in SPRINGS else
                'ARTICULATED_PREVIEW' if ref in ARTICULATED else 'FIXED')

    def scalar(name, measured, expected, tolerance=.01):
        report['scalars'].append(dict(name=name, measured_mm=float(measured), expected_mm=expected,
            tolerance_mm=tolerance, status='PASS' if abs(measured-expected)<=tolerance else 'FAIL'))

    def preserve(name, now, before):
        volume = difference_volume(now, before)
        report['preservation'].append(dict(name=name, symmetric_difference_volume_mm3=volume,
            status='PASS' if volume<=VOLUME_TOL else 'FAIL'))

    def compound_pair(name, a, b, intended=False, search=5.):
        volume = float((a^b).volume())
        gap = float(a.min_gap(b, search)) if volume<=VOLUME_TOL else 0.
        return dict(name=name, intersection_volume_mm3=volume, minimum_gap_mm=gap,
            gap_search_cap_mm=search, intended_exterior_contact=intended,
            status='INTERFERENCE' if volume>VOLUME_TOL else
            'INTENDED_CONTACT_CLEAR' if intended else 'CLEAR_WITH_GAP' if gap>1e-4 else 'UNRESOLVED_TANGENCY')

    def section(name, function):
        try:
            function()
        except Exception as error:
            report['scalars'].append(dict(name=name, status='UNCHECKED', reason=f'{type(error).__name__}: {error}'))

    def ray_levels(mesh, point, direction, axis):
        locations, _, _ = mesh.ray.intersects_location([point], [direction], multiple_hits=True)
        return np.sort(np.unique(np.round(locations[:,axis], 7)))

    def finalize(preflight=False):
        rows = [row for group in groups for row in report[group]]
        failed = [row for row in rows if row['status'] in ('FAIL','INTERFERENCE')]
        provisional = [row for row in failed if row.get('criterion_class')=='PROVISIONAL_ANALYTICAL_GEOMETRY_TARGET']
        packaging_failed = [row for row in failed if row not in provisional]
        uncertain = [row for row in rows if row['status'] in ('UNCHECKED','UNRESOLVED_NEAR_CONTACT','UNRESOLVED_TANGENCY')]
        unchanged = (sha(source)==baseline_source_hash and input_identity(args.baseline)==baseline_identity)
        expected_source = baseline_source_hash==BASELINE_SOURCE_SHA
        study_unchanged = input_identity(args.assembly)==study_identity
        if preflight:
            packaging_status = 'INVALID_INPUTS'
        else:
            packaging_status = 'FAIL' if packaging_failed or not unchanged or not expected_source or not study_unchanged else 'PARTIAL' if uncertain else 'PASS'
        overall = 'CONDITIONAL_LIGAMENT_TARGET_NOT_MET' if packaging_status=='PASS' and provisional else 'GEOMETRIC_PACKAGING_PASS' if packaging_status=='PASS' else packaging_status
        report.update(status=overall, geometry_packaging_status=packaging_status,
            structural_qualification='NOT_ESTABLISHED', invalid_solids=invalid,
            invalid_baseline_solids=base.invalid, provisional_ligament_targets_not_met=len(provisional),
            failed_checks=len(failed), failed_packaging_checks=len(packaging_failed),
            unresolved_checks=len(uncertain), baseline_unchanged=unchanged,
            expected_main_baseline_source=expected_source, study_inputs_unchanged=study_unchanged,
            elapsed_seconds=time.monotonic()-began,
            status_counts={status:sum(row['status']==status for row in rows) for status in sorted({row['status'] for row in rows})})
        report['inherited_soft_contact_requires_physical_check']=any(
            row['status']=='INHERITED_NOMINAL_SOFT_PART_CONTACT' for row in report['legacy_contacts'])
        args.output.write_text(json.dumps(clean_numbers(report), indent=2)+'\n')
        print(json.dumps({key:report[key] for key in ('status','device_part_count','failed_checks',
            'failed_packaging_checks','unresolved_checks','provisional_ligament_targets_not_met',
            'baseline_unchanged','expected_main_baseline_source','elapsed_seconds','status_counts')}, indent=2), flush=True)
        print('Saved', args.output, flush=True)

    if invalid or base.invalid or report['missing_device_refs'] or report['unexpected_device_refs'] or len(inputs)!=51:
        report['validation_stopped']='Exactly 51 closed positive device solids and a valid baseline are required before dimensions or motion can be accepted'
        finalize(True)
        return

    def dimensions():
        scalar('Fixed frame total width', inputs['P01']['mesh'].extents[1],132.)
        scalar('P04 outside arm span', inputs['P04']['mesh'].extents[1],126.)
        scalar('P05 outside width', inputs['P05']['mesh'].extents[1],126.)
        scalar('P04 return face X', inputs['P04']['mesh'].bounds[1,0],124.)
        scalar('P05 neutral minimum X', inputs['P05']['mesh'].bounds[0,0],-7.)
        scalar('Fixed steel seat front X', inputs['H050']['mesh'].bounds[0,0],9.)
        scalar('Moving steel seat front X', inputs['H060']['mesh'].bounds[0,0],113.)
        for ref, y in [('H040',-51.),('H041',51.)]:
            bounds=inputs[ref]['mesh'].bounds
            scalar(ref+' rod axis Y',bounds[:,1].mean(),y)
            scalar(ref+' rod axis Z',bounds[:,2].mean(),18.)
            scalar(ref+' rod length',bounds[1,0]-bounds[0,0],146.)
        mesh=inputs['P04']['mesh']
        ys=ray_levels(mesh,[94,-200,20],[0,1,0],1)
        scalar('Pocket inner width at X94/Z20',ys[ys>0].min()-ys[ys<0].max(),72.)
        scalar('Deck outside width at X94/Z20',ys.max()-ys.min(),84.)
        zs=ray_levels(mesh,[94,0,100],[0,0,-1],2)
        scalar('Pocket depth from Z30',30-zs.max(),20.)
        scalar('Floor above guide at X94/Y0',zs[-1]-zs[-2],2.7)
        ys=ray_levels(mesh,[114,-200,18],[0,1,0],1)
        scalar('Negative rear-relief edge Y at X114/Z18',ys.min(),-39.)
        scalar('Positive rear-relief edge Y at X114/Z18',ys.max(),39.)
        scalar('Cam axis Y',inputs['H10']['mesh'].bounds[:,1].mean(),2.5)
        scalar('Connector maximum Y',inputs['H01d']['mesh'].bounds[1,1],38.5)
        all_bounds=np.stack([row['mesh'].bounds for row in inputs.values()])
        scalar('Whole device height',all_bounds[:,1,2].max()-all_bounds[:,0,2].min(),32.,.02)
        # Measure palm plate away from the bridges and rounded plan corners.
        py=ray_levels(inputs['P02']['mesh'],[-34,-200,12],[0,1,0],1)
        scalar('Retained palm plate width at X-34/Z12',py.max()-py.min(),128.)
        scalar('Retained enclosure tray width',inputs['P08']['mesh'].extents[1],124.)
    section('Principal dimensions and cross sections',dimensions)

    def preservations():
        region=manifold(box([-100,-100,-20],[-23.25,100,100]))
        preserve('P02 original palm contact/core/plate/case pilots X<=-23.25',
            audit.objects['P02']^region,base.objects['P02']^region)
        region=manifold(box([34,-17,4.01],[124,17,7.01]))
        preserve('Central fixed guide profile above floor',audit.objects['P01']^region,base.objects['P01']^region)
        region=manifold(box([79,-18,4],[124,18,10]))
        preserve('Carriage guide relief, rear bearing and central floor',audit.objects['P04']^region,base.objects['P04']^region)
        region=manifold(box([-100,-7,-20],[100,7,100]))
        preserve('Yoke centered sensor bore and pusher path |Y|<=7',audit.objects['P05']^region,base.objects['P05']^region)
        shifted={'H030':13,'H031':-13,'H040':13,'H041':-13,
            'H050':13,'H051':-13,'H060':13,'H061':-13,'P060':13,'P061':-13,
            'P070a':13,'P070b':13,'P071a':-13,'P071b':-13,
            'H09':37,'H09a':37,'H09b':37,'H10':37,'H01d':-6}
        for ref in sorted(EXPECTED-{'P01','P02','P04','P05','H01c'}-SPRINGS):
            preserve(ref+' original shape / declared Y relocation',audit.objects[ref],
                base.objects[ref].translate([0,shifted.get(ref,0),0]))
        for ref in sorted(SPRINGS):
            preserve(ref+' indicative neutral coil / declared Y relocation',manifold(inputs[ref]['mesh']),
                manifold(original[ref]['mesh']).translate([0,shifted[ref],0]))
        report['preservation'].append(dict(name='H01c cable reroute',status='DECLARED_CHANGED',
            reason='Cable preview is shortened toward inward-rerouted connector; assembly clearance is checked, real lead slack remains a physical assembly requirement'))
    section('Protected geometry and ordered hardware',preservations)

    def supports_and_mounts():
        for side in (-1,1):
            y=side*51
            old_y=side*64
            support_region=manifold(box([-18,old_y-12,3.8],[-8,old_y+12,28]))
            # Compare actual original native geometry, including its exact
            # hole tessellation, rather than a newly polygonized R3.1 proxy.
            support=(base.objects['P01']^support_region).translate([0,-side*13,0])
            missing=float((support-audit.objects['P01']).volume())
            report['support_checks'].append(dict(name=f'Unchanged 24 mm front rod support side {side}',
                nominal_section_mm=[10,24],plan_area_mm2=240.,baseline_native_support_missing_from_P01_mm3=missing,
                status='PASS' if missing<=VOLUME_TOL else 'FAIL',
                meaning='Nominal material inclusion; does not establish stiffness or strength of the integrated palm/frame'))
            tab=manifold(box([-30,26 if side>0 else -37,9.5],[-9.5,37 if side>0 else -26,14.5]))
            # The M4 hole and key socket are intentional cuts; compare the tab
            # body outside those exact feature neighborhoods, not a solid box.
            hole=cyl_z(bolt_x,side*31.5,mount_z-.01,head_z+.01,2.21)+cyl_z(bolt_x,side*31.5,head_z,31,4.01)
            key_socket=manifold(box([key_x[0]-.26,side*31.5-3.26,mount_z-.21],[key_x[1]+.26,side*31.5+3.26,key_top+.31]))
            tab_check=tab-hole-key_socket
            missing=float((tab_check-audit.objects['P02']).volume())
            report['support_checks'].append(dict(name=f'Detachable 11 mm palm tab side {side}',
                bounds_mm=[[-30,26 if side>0 else -37,9.5],[-9.5,37 if side>0 else -26,14.5]],
                missing_volume_mm3=missing,status='PASS' if missing<=VOLUME_TOL else 'FAIL',
                meaning='Detachable narrower palm tab outside M4/key cuts; no joint strength established'))
            key=manifold(box([key_x[0],side*31.5-3,mount_z+.01],[key_x[1],side*31.5+3,key_top-.01]))
            key_missing=float((key-audit.objects['P01']).volume())
            report['mount_checks'].append(dict(name=f'Positive antirotation key side {side}',
                missing_volume_mm3=key_missing,status='PASS' if key_missing<=VOLUME_TOL else 'FAIL'))
            foot=manifold(box([-23,26 if side>0 else -37,3.8],[-9,37 if side>0 else -26,mount_z]))
            foot=foot-cyl_z(bolt_x,side*31.5,pilot_bottom-.01,mount_z+.01,2.61)
            missing=float((foot-audit.objects['P01']).volume())
            report['support_checks'].append(dict(name=f'Palm mounting foot side {side}',
                nominal_x_interval_mm=[-23,-9],nominal_z_interval_mm=[3.8,mount_z],
                missing_volume_mm3=missing,status='PASS' if missing<=VOLUME_TOL else 'FAIL'))
            foot_z=ray_levels(inputs['P01']['mesh'],[-10,side*36,40],[0,0,-1],2)
            palm_z=ray_levels(inputs['P02']['mesh'],[-10,side*36,40],[0,0,-1],2)
            scalar(f'Foot mating plane side {side}',foot_z.max(),mount_z)
            scalar(f'Palm tab underside side {side}',palm_z.min(),mount_z)
            report['support_checks'].append(compound_pair(f'Actual P02 tab / 24 mm front rod support side {side}',
                audit.objects['P02'],support))
            if args.mount_variant!='v4':
                boss=manifold(box([-23,26 if side>0 else -37,6.5],[-9.5,37 if side>0 else -26,9.6]))
                missing=float(((boss-hole-key_socket)-audit.objects['P02']).volume())
                report['support_checks'].append(dict(name=f'Forward stepped palm boss side {side}',
                    x_interval_mm=[-23,-9.5],z_interval_mm=[6.5,9.6],
                    missing_volume_mm3=missing,status='PASS' if missing<=VOLUME_TOL else 'FAIL',
                    meaning='Lower clamp remains forward of retained case maxX-23.6; upper palm/root is unchanged'))
            cap='P060' if side<0 else 'P061'
            bounds=inputs[cap]['mesh'].bounds
            scalar(cap+' cap width',bounds[1,1]-bounds[0,1],24.)
            scalar(cap+' cap center Y',bounds[:,1].mean(),y)
            scalar(cap+' edge border',66-max(abs(bounds[:,1])),3.)
        # Open blind underside enclosure-palm insert pilots must survive fusion.
        for y in (-59,59):
            probe=cyl_z(-26.5,y,9.51,13.49,1.59)
            volume=float((probe^audit.objects['P02']).volume())
            report['mount_checks'].append(dict(name='Retained underside M2 enclosure-palm pilot',
                x_mm=-26.5,y_mm=y,probe_inside_solid_mm3=volume,
                status='PASS' if volume<=VOLUME_TOL else 'FAIL'))
        for x in (16,127):
            for y in (-28,28):
                bore=cyl_z(x,y,-2.01,4.01,2.74)
                volume=float((bore^audit.objects['P01']).volume())
                report['mount_checks'].append(dict(name='Relocated M5 bench clearance bore',
                    x_mm=x,y_mm=y,probe_inside_solid_mm3=volume,
                    status='PASS' if volume<=VOLUME_TOL else 'FAIL'))
        for side in (-1,1):
            for part,probe,label in [
                ('P01',cyl_z(bolt_x,side*31.5,pilot_bottom+.01,mount_z-.01,2.59),'base M4 insert pilot'),
                ('P02',cyl_z(bolt_x,side*31.5,mount_z+.01,head_z-.01,2.19),'palm M4 through clearance'),
                ('P02',cyl_z(bolt_x,side*31.5,head_z+.01,14.49,3.99),'palm M4 head recess')]:
                volume=float((probe^audit.objects[part]).volume())
                report['mount_checks'].append(dict(name=label,part=part,y_mm=side*31.5,
                    probe_inside_solid_mm3=volume,status='PASS' if volume<=VOLUME_TOL else 'FAIL'))
            bolt=cyl_z(bolt_x,side*31.5,head_z-10,head_z,2)+cyl_z(bolt_x,side*31.5,head_z,head_z+4,3.5)
            driver=cyl_z(bolt_x,side*31.5,head_z+4.001,50,3)
            report['mount_checks'].append(dict(name=f'Conceptual M4x10 palm bolt side {side}',
                conceptual_hardware_only=True,shaft_radius_mm=2.,shaft_z_mm=[head_z-10,head_z],
                head_radius_mm=3.5,head_z_mm=[head_z,head_z+4],nominal_thread_engagement_mm=6.,
                blind_pilot_floor_z_mm=pilot_bottom,nominal_bolt_tip_clearance_mm=head_z-10-pilot_bottom,
                nominal_pilot_floor_wall_mm=pilot_bottom+2,
                nominal_transverse_head_edge_margin_mm=2.,nominal_counterbore_radial_clearance_mm=.5,
                fastener_requirement='M4x10 ISO4762/DIN912 socket head cap screw, nominal head diameter7 mm x4 mm high',
                dimension_sources=[str(ROOT/'EINKAUFSTEILE.md')+':58',
                    str(ROOT/'review/assembly-final-2026-10-13/validation.json')+':1173',
                    'https://nederland.bossard.com/en-us/912000a20040025',
                    'https://www.bossard.com/no-en/-/media/bossard-group/website/documents/technical-resources/en/f-040-en.pdf'],
                status='DIMENSIONS_RECORDED',
                meaning='Explicit standard fastener assumption matching original assembly model, not evidence of a purchased vendor lot. Verify actual head/insert dimensions; screw/insert strength and print tolerances remain unqualified.'))
            bottom_z=ray_levels(inputs['P01']['mesh'],[bolt_x,side*31.5,30],[0,0,-1],2)
            scalar(f'Actual M4 blind pilot floor side {side}',bottom_z.max(),pilot_bottom)
            scalar(f'M4 nominal tip clearance side {side}',head_z-10-bottom_z.max(),
                1. if args.mount_variant=='v4' else .3)
            scalar(f'M4 pilot floor wall side {side}',bottom_z.max()+2,
                4.5 if args.mount_variant=='v4' else 2.2)
            for part in ('P01','P02','P03','H180','H181','H12','H13','H15','H01d','P05','H040','H041'):
                # The shaft intentionally occupies the M4 insert pilot; the
                # modeled pilot R2.6 is an air envelope, not a steel thread.
                report['mount_checks'].append(compound_pair(f'Conceptual M4x10 side {side} / '+part,
                    bolt,audit.objects[part],intended=part in ('P01','P02')))
                report['access_checks'].append(compound_pair(f'Conceptual diameter6 top driver side {side} / '+part,
                    driver,audit.objects[part]))
                # Nominal maximum-head diameter10 mm, 90-degree cone. Exact
                # flat head top is Z4, lower radius2.75 at Z1.75.
                import manifold3d as md
                head=md.Manifold.cylinder(2.25,2.75,5.,128).translate([x,y,1.75])
                volume=float((head^audit.objects['P01']).volume())
                report['mount_checks'].append(dict(name='Flush M5 head envelope / frame',
                    x_mm=x,y_mm=y,intersection_volume_mm3=volume,head_top_z_mm=4.,
                    status='PASS' if volume<=VOLUME_TOL else 'FAIL'))
    section('Detachable keyed palm, case mounts and 24 mm rod supports',supports_and_mounts)

    def rear_ligaments():
        mesh=inputs['P04']['mesh']
        for side in (-1,1):
            levels=ray_levels(mesh,[114,side*41.99,100],[0,0,-1],2)
            if len(levels)!=4:
                raise ValueError(f'Expected four rear-wall levels; got {levels.tolist()} for side {side}')
            roof,bottom=float(levels[3]-levels[2]),float(levels[1]-levels[0])
            approach=[]
            for ay in (41.9,41.99,41.999,41.9999,41.99999):
                zs=ray_levels(mesh,[114,side*ay,100],[0,0,-1],2)
                if len(zs)!=4:
                    raise ValueError('Rear-wall approach did not give four boundaries')
                approach.append(dict(abs_y_mm=ay,retained_top_z_mm=float(zs[-1]),
                    recess_top_z_mm=float(zs[-2]),roof_strip_mm=float(zs[-1]-zs[-2])))
            report['ligament_checks'].append(dict(name=f'Native rear-wall strip side {side}',
                x_mm=114,y_mm=side*41.99,z_intersections_mm=levels.tolist(),roof_strip_mm=roof,
                bottom_strip_mm=bottom,boundary_approach_samples=approach,
                criterion_class='PROVISIONAL_ANALYTICAL_GEOMETRY_TARGET',
                provisional_roof_target_mm=4.,provisional_bottom_target_mm=5.,
                target_source='Screening targets rounded down from flat-deck estimates 4.063/5.063 mm, not user requirements or validated material-strength limits. Actual native fillets are measured.',
                status='PASS' if roof>=4 and bottom>=5 else 'FAIL',
                meaning='Local rays and boundary approach, not a global minimum-ligament search or a strength acceptance'))
            now_probe=cyl(116.001,116.101,side*51,18,11)-cyl(116,116.102,side*51,18,4)
            old_probe=cyl(116.001,116.101,side*64,18,11)-cyl(116,116.102,side*64,18,4)
            now=float((audit.objects['P04']^now_probe).volume())/.1
            before=float((base.objects['P04']^old_probe).volume())/.1
            report['ligament_checks'].append(dict(name=f'Retained X116 seat backing side {side}',
                probe_interval_x_mm=[116.001,116.101],candidate_probe_area_mm2=now,
                baseline_probe_area_mm2=before,status='PASS' if now>=before-.1 else 'FAIL',
                meaning='Volume of a thin annulus probe divided by thickness, not a stress calculation'))
        report['ligament_checks'].append(dict(name='Nominal seat-relief/pocket-tool separation',
            axial_tool_gap_mm=1.,transverse_tool_gap_mm=3.,conservative_diagonal_distance_mm=math.sqrt(10),
            status='PASS',meaning='Source nominal tool bounds X112 vs111 and Y39 vs36; actual lip rounding and remaining wall are separately measured'))
    section('Native rear-seat relief and backing',rear_ligaments)

    # Static reaction path, integrated palm, cable and case checks at both
    # preload extremes. A volume tolerance allows exterior contact, not overlap.
    static_pairs=[('P01','P02'),('P05','P01'),('P05','P02'),('P05','P03'),('P05','H040'),('P05','H041'),
        ('P05','H01'),('P05','H01c'),('P05','H01d'),('P05','P08'),('P05','P09'),('P05','P10')]
    static_pairs += [('P01',ref) for ref in sorted(PRELOAD-{'P05'})]
    static_pairs += [('P01',ref) for ref in ('P08','P09','P10','H15','H160','H161','H170','H171','H21','H22','H09')]
    static_pairs += [('P02',ref) for ref in sorted(PRELOAD|{'H15','H160','H161','H170','H171','H09'})]
    for preload in (0.,2.):
        original_sleeve_overlap=float((base.objects['P02']^base.objects['P03']).volume())
        sleeve_overlap=float((audit.objects['P02']^audit.objects['P03']).volume())
        report['static_pairs'].append(dict(name='Original nominal TPU sleeve/core fit',
            pair=['P02','P03'],preload_mm=preload,intersection_volume_mm3=sleeve_overlap,
            baseline_nominal_fit_mesh_overlap_mm3=original_sleeve_overlap,
            status='INTENDED_BASELINE_TPU_FIT' if sleeve_overlap<=original_sleeve_overlap+VOLUME_TOL else 'INTERFERENCE',
            reason='Core and sleeve share nominal R7.75 contact. Their separately tessellated native meshes overlap slightly; only original fit overlap plus volume tolerance is allowed. Core and sleeve preservation are independently checked.'))
        overlap=float((audit.objects['P03']^audit.objects['H13'].translate([preload,0,0])).volume())
        old_overlap=float((base.objects['P03']^base.objects['H13'].translate([preload,0,0])).volume())
        report['legacy_contacts'].append(dict(pair=['P03','H13'],preload_mm=preload,
            intersection_volume_mm3=overlap,baseline_at_same_preload_volume_mm3=old_overlap,
            status='INHERITED_NOMINAL_SOFT_PART_CONTACT' if overlap>VOLUME_TOL and abs(overlap-old_overlap)<=VOLUME_TOL else
                'NEW_OR_CHANGED_INTERFERENCE' if overlap>VOLUME_TOL else 'CLEAR',
            qualification='NOT_ESTABLISHED',
            meaning='The source retains a soft sleeve/adjuster-shaft-end overlap at zero preload. This is separate from intended sleeve/core fit and is not certified as collision-free. Deformation, adjustment friction and load effects require physical checking; service at2 mm clears it.'))
        for a,b in static_pairs:
            report['static_pairs'].append(dict(preload_mm=preload,
                **audit.pair(a,b,preload if a in PRELOAD else 0.,preload if b in PRELOAD else 0.)))
        for a,b in [('P04','H060'),('P04','H061'),('P04','H10'),('P05','H050'),('P05','H051'),('P05','H02')]:
            report['static_pairs'].append(dict(preload_mm=preload,
                **compound_pair(a+' / '+b+' installed force/fastener contact',
                    audit.objects[a].translate([preload if a in PRELOAD else 0,0,0]),
                    audit.objects[b].translate([preload if b in PRELOAD else 0,0,0]),True)))
    targets=EXPECTED-MOVING-SPRINGS-ARTICULATED
    for preload in (0.,2.):
        for a in sorted(MOVING):
            for b in sorted(targets):
                if frozenset((a,b)) in INTENDED:
                    continue
                row=audit.sweep(a,b,0.,30.,-1.,preload if b in PRELOAD else 0.)
                report['operating_sweeps'].append(dict(preload_mm=preload,**row))
                if row['status']!='CONTINUOUS_CLEARANCE_CERTIFIED':
                    print('OPERATING',preload,a,b,row['status'],flush=True)
    for a in sorted(MOVING):
        for b in sorted(targets-INSERTION_REMOVED):
            if frozenset((a,b)) in INTENDED:
                continue
            row=audit.sweep(a,b,0.,180.,1.,0.,label='Rear insertion with caps bumpers rods springs absent')
            report['insertion_sweeps'].append(row)
            if row['status']!='CONTINUOUS_CLEARANCE_CERTIFIED':
                print('INSERTION',a,b,row['status'],flush=True)

    for preload in (0.,2.):
        for side in (-1,1):
            ref=f'COIL_ENVELOPE_{side}_{preload:g}'
            env=manifold(cylinder_x(12+preload,113,side*51,18,7.4))
            audit.objects[ref]=env
            inputs[ref]=dict(mesh=as_mesh(env))
            for b in ('P04','P01','P02','P03','P05'):
                report['spring_envelopes'].append(dict(preload_mm=preload,side=side,
                    nominal_radius_mm=7.4,continuous_scope='Whole 0..30 via conservative full-length envelope subset argument',
                    **audit.pair(ref,b,0.,preload if b in PRELOAD else 0.)))
            stroke=15-preload
            sleeve=cyl(12+preload,98+preload,side*51,18,8)-cyl(11+preload,99+preload,side*51,18,4)
            for b in sorted(EXPECTED-SPRINGS-ARTICULATED):
                shift=-stroke if b in MOVING else preload if b in PRELOAD else 0.
                intended=b in (('H050','H060') if side<0 else ('H051','H061'))
                report['isometric_cases'].append(dict(preload_mm=preload,stroke_mm=stroke,side=side,
                    **compound_pair('86 mm isometric sleeve / '+b,sleeve,audit.objects[b].translate([shift,0,0]),intended)))

    def access():
        # The case tray has intended exterior contact at the underside palm
        # bosses. Start 0.001 mm below contact after first checking seated volume.
        fixed=audit.objects['P01']
        palm_module=audit.objects['P02']+audit.objects['P03']+audit.objects['P08']+audit.objects['P09']+audit.objects['P10']
        module_targets=EXPECTED-{'P02','P03','P08','P09','P10'}-SPRINGS
        remainder=None
        for ref in sorted(module_targets):
            obj=audit.objects[ref].translate([2 if ref in PRELOAD else 0,0,0])
            remainder=obj if remainder is None else remainder+obj
        # Start just above the exterior seating plane after checking the actual
        # installed pair volumes separately. The source keys have an open-top
        # vertical removal direction; no snap fit is assumed.
        report['access_checks'].append(dict(prerequisites='Release preload lock H21 and advance adjuster to2 mm; safely restrain or remove springs; remove both palm M4s. Case travels attached to palm.',
            service_preload_mm=2.,
            checked_refs=sorted(module_targets),excluded_springs_reason='Spring X>=12 while module X<=-9.5, so their swept X bounds remain disjoint',
            **linear_sweep('P02/P03/P08/P09/P10 complete module upward removal / remaining native assembly',
                palm_module.translate([0,0,.001]),remainder,[0,0,1],0.,40.,args.minimum_interval)))
        for ref in ('P08','P09'):
            report['access_checks'].append(linear_sweep(ref+' downward removal / P01 and P02',
                audit.objects[ref].translate([0,0,-.001]),fixed+audit.objects['P02'],[0,0,-1],0.,30.,args.minimum_interval))
        # A finite 10 mm outward move disengages an M3x8 retention screw.
        # This stays inside the rod-block gap; it is not an unlimited side entry.
        for preload in (0.,2.):
            for side,ref in [(-1,'H180'),(1,'H181')]:
                moving=audit.objects[ref].translate([preload,0,0])
                report['access_checks'].append(dict(preload_mm=preload,
                    **linear_sweep(ref+' finite outward withdrawal / P01',moving,fixed,[0,side,0],0.,10.,args.minimum_interval)))
                # Cylinders along Y, centred on X=-13+preload/Z10.
                import trimesh as tm
                mesh=tm.creation.cylinder(radius=1.5,height=10.,sections=64)
                transform=tm.transformations.rotation_matrix(math.pi/2,[1,0,0])
                transform[:3,3]=[-13+preload,side*25.5,10]
                mesh.apply_transform(transform)
                report['access_checks'].append(dict(preload_mm=preload,
                    assumed_tool='Straight local driver-stub envelope diameter3 x10 mm, from head outerY20.5 to30.5; no handle/hand represented',
                    **compound_pair(ref+' local driver stub / P01',manifold(mesh),fixed)))
        # Access requires the adjustable screw and soft sleeve removed. Check
        # keeper fasteners independently before accepting this claimed path.
        for ref in ('H160','H161'):
            report['access_checks'].append(dict(prerequisites='Complete detachable palm/case module removed; other keeper fastener and preload screw removed',
                **linear_sweep(ref+' full wristward withdrawal / P01',
                    audit.objects[ref],fixed,[-1,0,0],0.,8.,args.minimum_interval)))
        keeper=audit.objects['H15']
        report['access_checks'].append(dict(prerequisites='Detachable palm module, keeper screws H160/H161 and adjuster H13 removed',
            **linear_sweep('Keeper wristward release / P01',keeper,fixed,[-1,0,0],0.,1.4,args.minimum_interval)))
        report['access_checks'].append(dict(prerequisites='Keeper shifted 1.4 mm wristward after palm module, keeper screws and adjuster removed',
            **linear_sweep('Keeper vertical removal after wristward release / P01',
                keeper.translate([-1.4,0,0]),fixed,[0,0,1],0.,35.,args.minimum_interval)))
    section('Finite cassette, keeper and case access paths',access)

    for preload in (0,2):
        for stroke in (0,15,30):
            length=113-stroke-(12+preload)
            report['force_curve_datum_check'].append(dict(preload_mm=preload,stroke_mm=stroke,
                installed_length_mm=length,DF2194_pair_N=2*3.307*(102-length),
                DF2185_pair_N=2*3.709*(105-length),status='PASS' if length==101-preload-stroke else 'FAIL'))
    finalize()


if __name__=='__main__':
    main()
