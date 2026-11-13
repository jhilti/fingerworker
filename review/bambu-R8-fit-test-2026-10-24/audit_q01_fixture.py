#!/usr/bin/env python3
"""Independent exact Q01 unloaded fixture and installation audit against frozen R8."""
from pathlib import Path
import sys,json,hashlib
import numpy as np
import trimesh
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[1]
R8=ROOT/'review/flat132-palm-cover-2026-10-23'; QDIR=ROOT/'print/bambu-R8-fit-test-2026-10-24/fixture'
sys.path.insert(0,str(ROOT/'review/flat132-adjustable-rear-2026-10-23/validation'))
import audit_adjustable_rear as r7
b=r7.b;v=r7.v
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.TopAbs import TopAbs_SOLID,TopAbs_SHELL
TOL=1e-6
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def q_shape(lo=0.,hi=0.):
    # Axial sweep of independently specified primitives, not imported builder output.
    pieces=[b.box([-20.5+lo,-6,12],[-16+hi,6,24])]
    for x0,x1,rad in [(-16,-14,9),(-14.01,.1,2.8),(0,1,4),(.9,7.5,1.5)]:
        pieces.append(r7.cyl([x0+lo,0,18],[x1+hi,0,18],rad))
    return r7.union(pieces)
def main():
    manifest=json.loads((QDIR/'manifest.json').read_text()); checks=[]
    def add(name,passed,**evidence): checks.append(dict(name=name,status='PASS' if passed else 'FAIL',**evidence))
    for name,row in manifest['files'].items():add('Fixture file hash '+name,sha(QDIR/name)==row['sha256'],sha256=sha(QDIR/name))
    add('Fixture builder hash',sha(QDIR/manifest['source'])==manifest['source_sha256'],sha256=sha(QDIR/manifest['source']))
    inv=json.loads((R8/'validation/native-step-inventory.json').read_text()); assert sha(Path(inv['native_step']))==inv['native_step_sha256']
    shapes,_,_=b.read_step(Path(inv['native_step']));native={ref:shapes[row['candidates'][0]['solid_index']] for ref,row in inv['native_part_correspondence'].items()}
    qs,_,_=b.read_step(QDIR/'Q01_UNLOADED_TEST_FIXTURE_assembly-mm.step');assert len(qs)==1;q=qs[0]
    diff=b.xor_volume(q,q_shape());add('Independent literal CSG equals Q01 STEP',diff<TOL,symmetric_difference_mm3=diff)
    add('One valid positive connected fixture',BRepCheck_Analyzer(q).IsValid() and b.count(q,TopAbs_SOLID)==1 and b.count(q,TopAbs_SHELL)==1 and b.volume(q)>0,solids=b.count(q,TopAbs_SOLID),shells=b.count(q,TopAbs_SHELL),volume_mm3=b.volume(q))
    mat=np.asarray(manifest['assembly_to_print_matrix']);add('Fixture print transform rigid orientation and scale1',np.allclose(mat[:3,:3].T@mat[:3,:3],np.eye(3)) and abs(np.linalg.det(mat[:3,:3])-1)<1e-10,determinant=float(np.linalg.det(mat[:3,:3])))
    assembly=trimesh.load(QDIR/'Q01_UNLOADED_TEST_FIXTURE_assembly-mm.stl',force='mesh');pr=trimesh.load(QDIR/'Q01_UNLOADED_TEST_FIXTURE_print-mm.stl',force='mesh');assembly.apply_transform(mat)
    # Binary STL reload may reorder welded vertices; compare both transformed vertex sets.
    def nearest_max(a,bb): return max(float(np.sqrt(np.sum((a[i:i+128,None,:]-bb[None,:,:])**2,axis=2).min(axis=1)).max()) for i in range(0,len(a),128))
    err=max(nearest_max(assembly.vertices,pr.vertices),nearest_max(pr.vertices,assembly.vertices));add('Print STL rigidly identical to assembly STL',err<3e-6 and len(assembly.faces)==len(pr.faces) and assembly.is_watertight and pr.is_watertight and abs(assembly.volume-pr.volume)<.001,max_bidirectional_vertex_error_mm=err,facet_count=len(pr.faces))
    selected=sorted([p.stem for p in (R8/'print-mm').glob('*.stl')]+['H040','H041'])
    for ref in selected:
        ov=b.volume(b.common(q,native[ref]));gap=b.gap(q,native[ref]);add('Unloaded fixture versus selected native '+ref,ov<TOL,intersection_mm3=ov,gap_mm=gap)
    for ref in ['P01','P05']:
        gap=b.gap(q,native[ref]);add('Intended datum contact '+ref,gap<1e-6,exact_gap_mm=gap)
    # Native receiving stock in thin witness bands immediately behind the two reaction faces.
    flange_witness=r7.cyl([-16.001,0,18],[-16,0,18],9);face_witness=r7.cyl([1,0,18],[1.001,0,18],4)
    areas={ref:b.volume(b.common(w,native[ref]))/.001 for ref,w in [('P01',flange_witness),('P05',face_witness)]}
    add('Portal and yoke datum faces have positive bearing area',all(x>0 for x in areas.values()),nominal_contact_area_mm2=areas,axial_datum_spacing_mm=17)
    swept=q_shape(0,10)
    # The p0 yoke is deliberately absent while the square locator is inserted from +X.
    for ref in set(selected)-{'P05'}:
        ov=b.volume(b.common(swept,native[ref]));add('Continuous fixture insertion +X10 to seated0 versus '+ref,ov<TOL,intersection_mm3=ov,translation_range_mm=[0,10],method='Exact union of axially extended original primitives')
    # Relative Q01 sweep -10..0 proves P05 can move +10..0 over tail with Q01 seated.
    ov=b.volume(b.common(q_shape(-10,0),native['P05']));add('Continuous P05 installation from +X10 over seated tail',ov<TOL,intersection_mm3=ov,method='Exact opposite axial sweep of fixture primitives')
    # Carriage and cam are far forward of Q01 throughout the complete a+u interval0..30.
    motion=[]
    for ref in ['P04','P11']:
        low=b.bounds(native[ref])[0,0]-30;clear=low-b.bounds(q)[1,0];motion.append({'ref':ref,'minimum_x_bound_mm':float(low),'q01_max_x_mm':float(b.bounds(q)[1,0]),'minimum_axial_clearance_mm':float(clear)})
    add('Full p0 carriage motion a0..2/u0..30-a clears fixture',all(r['minimum_axial_clearance_mm']>0 for r in motion),domain='p0,a>=0,a<=2,u>=0,u+a<=30',motion_evidence=motion)
    # All rear adjuster bodies move between -2 and0 and remain far beyond the fixture.
    rear=['P120','P121','P070a','P070b','P071a','P071b'];rear_gap=min(b.bounds(native[r])[0,0]-2-b.bounds(q)[1,0] for r in rear)
    add('Rear adjustment full0..2 clears fixture',rear_gap>0,minimum_axial_clearance_mm=float(rear_gap))
    result={'status':'PASS_UNLOADED_NOMINAL_FIXTURE_ASSEMBLY' if all(c['status']=='PASS' for c in checks) else 'FAIL','scope':'Q01 only: exact R8 static interface, selected print bodies, rod proxies, continuous insertion and p0 unloaded motion. Inherited R8 geometry is not rerun.','frozen_source_sha256':sha(R8/'fingerworker_flat132_palm_cover.fs'),'native_immutable_version_id':'6965afcca3af7c58ef3ac73f','native_step_sha256':inv['native_step_sha256'],'fixture_source_sha256':sha(QDIR/manifest['source']),'fixture_manifest_sha256':sha(QDIR/'manifest.json'),'checks':checks,'failed_checks':sum(c['status']=='FAIL' for c in checks),'axial_retention':'None: square locator and plain tail locate radially; keep assembly supported and gently seated, p0 only.','excluded_real_hardware':'Sensor, pusher, pusher nut, steel cassette, preload nut/keeper/adjuster/lock, cassette retention hardware, springs and isometric sleeves.','physical_limitations':['Unloaded hand fit/motion only; no squeeze, force, preload, calibration or strength qualification.','PLA rod/pad proxies are shape/fit substitutes only.','Support cleanup and print dimensional fits must be measured; printed .1/.2mm radial/flat clearances are not printer capability guarantees.']}
    (HERE/'qa-q01-fixture.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:result[k] for k in ['status','failed_checks']},indent=2));print('Checks',len(checks),'contactareas',areas)
    assert result['failed_checks']==0
if __name__=='__main__':main()
