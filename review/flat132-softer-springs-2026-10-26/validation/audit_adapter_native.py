#!/usr/bin/env python3
"""Independent local adapter/spring envelope audit against frozen native R9.

No Onshape edits or regeneration. Continuous affine motion is covered by exact
conservative cylindrical sweeps in each native body's relative coordinate frame.
"""
from pathlib import Path
import hashlib, json, math, sys
import numpy as np

HERE=Path(__file__).resolve().parent
PROJECT=HERE.parents[2]
R9=PROJECT/'review/flat132-palm-bracing-2026-10-25'
sys.path.insert(0,str(R9/'validation'))
import audit_palm_bracing as prior
r7=prior.r7; b=prior.b; v=prior.v
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.TopAbs import TopAbs_SOLID, TopAbs_SHELL

TOL=1e-6
sha=lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
rows=[]
def add(name,ok,**details):
    rows.append(dict(name=name,status='PASS' if ok else 'FAIL',**details))
def ring(x0,x1,y,outer,inner):
    return b.cut(r7.cyl([x0,y,18],[x1,y,18],outer),
                 r7.cyl([x0-.01,y,18],[x1+.01,y,18],inner))
def adapter(y,lo=0.,hi=0.):
    # Each interval is a superset of the corresponding translated tube.
    return b.fuse(ring(12+lo,34+hi,y,8,3.3),
                  ring(34+lo,36+hi,y,5.7,3.3))
def overlap(a,c):
    return 0. if v.separated(b.bounds(a),b.bounds(c)) else b.volume(b.common(a,c))

def main():
    inv=json.loads((R9/'validation/native-step-inventory.json').read_text())
    step=Path(inv['native_step'])
    assert sha(step)==inv['native_step_sha256']
    solids,_,_=b.read_step(step)
    native={ref:solids[row['candidates'][0]['solid_index']]
            for ref,row in inv['native_part_correspondence'].items()}
    assert len(native)==123
    spec=json.loads((PROJECT/'review/flat132-adjustable-rear-2026-10-23/validation/rear-spec.json').read_text())
    domain=r7.vertices()
    own=np.array([0.,1.,0.,0.])
    start=np.array([0.,1.,0.,0.])
    end=np.array([-1.,0.,-1.,0.])
    old_springs={'H030','H031'}
    spacers={}
    for label,y in [('left',-51.),('right',51.)]:
        s=adapter(y);spacers[label]=s
        add(label+' adapter is one valid positive solid/shell',
            BRepCheck_Analyzer(s).IsValid() and b.volume(s)>0 and
            b.count(s,TopAbs_SOLID)==b.count(s,TopAbs_SHELL)==1,
            volume_mm3=b.volume(s),bounds_mm=b.bounds(s).tolist())
        for ref,target in sorted(native.items()):
            if ref in old_springs:continue
            if ref in v.ARTICULATED:
                # The actuator's conservative full-motion Y envelope remains
                # between -14 and +8; its native geometry is illustrative.
                target=b.box([26,-14,8],[41,8,14])
                target_coefficient=np.zeros(4)
                method='conservative unchanged full articulated actuator envelope'
            else:
                target_coefficient=r7.coefficients(ref,spec)
                method='exact native BRep versus complete conservative relative-X tube sweep'
            offsets=domain@(own-target_coefficient)
            lo,hi=float(offsets.min()),float(offsets.max())
            swept=adapter(y,lo,hi)
            ov=overlap(swept,target)
            gap=b.gap(swept,target)
            intentional=ref==('H050' if y<0 else 'H051')
            add(label+' adapter full dynamic domain versus '+ref,ov<=TOL,
                intersection_upper_bound_mm3=ov,minimum_gap_lower_bound_mm=gap,
                relative_x_range_mm=[lo,hi],method=method,
                intentional_fixed_steel_seat_boundary_contact=intentional)
            # Every real turn lies inside the solid annular spring envelope.
            # Independent endpoint extrema may over-cover correlated poses;
            # therefore zero intersection certifies all intermediate poses.
            x0=34.+float((domain@(start-target_coefficient)).min())
            x1=108.+float((domain@(end-target_coefficient)).max())
            coil=ring(x0,x1,y,8.,6.2)
            cov=overlap(coil,target)
            cg=b.gap(coil,target)
            coil_contact=ref==('H060' if y<0 else 'H061')
            add(label+' nominal new spring envelope full dynamic domain versus '+ref,
                cov<=TOL,intersection_upper_bound_mm3=cov,
                minimum_gap_lower_bound_mm=cg,
                relative_x_cover_mm=[x0,x1],
                method='nominal OD16/ID12.4 full annular envelope, exact native BRep',
                intentional_moving_steel_seat_boundary_contact=coil_contact)
        # Direct new spring/spacer pair, expressed in the spacer frame.
        coil=ring(34,108,y,8,6.2)
        ov=overlap(s,coil)
        add(label+' new spring clears pilot and bears at X34 only',ov<=TOL,
            intersection_mm3=ov,pilot_to_nominal_coil_radial_gap_mm=6.2-5.7,
            shoulder_plane_x_mm=34,body_to_nominal_rod_radial_gap_mm=3.3-3,
            nominal_spring_end_annulus_supported_area_mm2=math.pi*(8**2-6.2**2))
    add('Two adapters remain separated throughout their common motion',
        overlap(spacers['left'],spacers['right'])<=TOL,
        exact_gap_mm=b.gap(spacers['left'],spacers['right']))
    lengths=[]
    for u,p,a,e in domain:
        length=74-a-p-u
        lengths.append(float(length))
        force=2*2.212*(80-length)
        original=2*3.307*(102-(96-a-p-u))
        add('Force and length identity '+str([u,p,a,e]),
            abs(force/original-2.212/3.307)<1e-10 and length>=44-1e-9,
            spring_length_mm=float(length),pair_force_N=float(force),
            force_fraction_of_original=float(force/original))
    add('Full-domain minimum length exceeds manufacturer test length',min(lengths)>34.75,
        minimum_spring_length_mm=min(lengths),manufacturer_test_length_mm=34.75,
        axial_margin_to_test_length_mm=min(lengths)-34.75,
        note='Published L1 is a test length, not an explicit fatigue-life rating.')
    add('Full-domain maximum nominal force below published test force',2.212*36<100.09,
        maximum_force_each_N=2.212*36,published_force_at_test_length_N=100.09)
    failures=[r for r in rows if r['status']!='PASS']
    result=dict(status='NOMINAL_LOCAL_ADAPTER_GEOMETRY_PASS' if not failures else 'FAIL',
        scope='Local exact adapter CSG and conservative continuous nominal new spring envelopes against frozen R9 native BReps. Not native Onshape regeneration or physical testing.',
        native_step=str(step),native_step_sha256=sha(step),
        r9_source_sha256=sha(R9/'fingerworker_flat132_palm_bracing.fs'),
        script_sha256=sha(__file__),
        spring_reference_url='https://www.febrotec.de/de-DE/druckfedern/schraubendruckfedern/0x-rdf2127/',
        configuration_domain_vertices_u_p_a_e_mm=domain.tolist(),
        adapter_spec=dict(body_od_mm=16,bearing_length_mm=22,bore_mm=6.6,
                          pilot_od_mm=11.4,pilot_length_mm=2,overall_length_mm=24),
        excluded_native_refs=sorted(old_springs),
        checks=rows,check_count=len(rows),failed_checks=len(failures),failures=failures,
        limitations=['All dimensions nominal; spring OD/ID and printed hole tolerances require physical fit checks.',
          'New spring envelope uses nominal OD16 and ID12.4, not a manufacturer tolerance or compressed-diameter envelope.',
          'The two adapters are removed together with both springs before fitting the unchanged 81mm isometric sleeves.',
          'Load capacity, fatigue life, print creep and tactile fit are not qualified by geometry.',
          'Published L1=34.75mm is a test length; no explicit dynamic cycle-life qualification is inferred.'])
    (HERE/'adapter-native-audit.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['status','check_count','failed_checks','failures']},indent=2),flush=True)
    assert not failures

if __name__=='__main__':main()
