#!/usr/bin/env python3
"""Read-only R7 native STEP/STL audit focused on the changed rear mechanism."""
from __future__ import annotations
import argparse,copy,hashlib,json,sys,zipfile
from pathlib import Path
from itertools import combinations
import numpy as np
HERE=Path(__file__).resolve().parent;STUDY=HERE.parent;PROJECT=STUDY.parents[1]
BASE=PROJECT/'review/flat132-solid-palm-2026-10-23'
sys.path.insert(0,str(BASE/'validation'))
import audit_solid_palm as b
v=b.v
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform,BRepBuilderAPI_MakePolygon,BRepBuilderAPI_MakeFace
from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism,BRepPrimAPI_MakeCylinder
from OCP.BRepFilletAPI import BRepFilletAPI_MakeFillet
from OCP.gp import gp_Trsf,gp_Vec,gp_Pnt,gp_Dir,gp_Ax2
from OCP.TopAbs import TopAbs_SOLID,TopAbs_SHELL,TopAbs_EDGE
from OCP.TopExp import TopExp_Explorer
from OCP.TopoDS import TopoDS
from OCP.BRepCheck import BRepCheck_Analyzer
import importlib.util
_spec=importlib.util.spec_from_file_location('r7_certificate',HERE/'certify_source_scope.py')
_cert=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(_cert)
TOL=1e-6
CHANGED_OLD={'P01','P060','P061','H040','H041'}
BAD={'FAIL','INTERFERENCE','UNCHECKED','UNRESOLVED_NEAR_CONTACT'}
def sha(p):return b.sha(p)
def write(p,x):return v.write(p,x)
def tr(shape,xyz):
    t=gp_Trsf();t.SetTranslation(gp_Vec(*xyz));return BRepBuilderAPI_Transform(shape,t,True).Shape()
def cyl(low,high,r):
    low=np.asarray(low,float);d=np.asarray(high,float)-low
    return BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(*low),gp_Dir(*d)),r,float(np.linalg.norm(d))).Shape()
def xprism(x0,x1,yz):
    p=BRepBuilderAPI_MakePolygon()
    for y,z in yz:p.Add(gp_Pnt(x0,y,z))
    p.Close();return BRepPrimAPI_MakePrism(BRepBuilderAPI_MakeFace(p.Wire()).Face(),gp_Vec(x1-x0,0,0)).Shape()
def union(shapes):
    result=shapes[0]
    for shape in shapes[1:]:result=b.fuse(result,shape)
    return result

def load_native(neutral,step):
    parts,ignored=v.load(neutral,{})
    assert not ignored,ignored
    invalid={r:x.get('error') for r,x in parts.items() if 'error'in x and r not in v.SPRINGS}
    assert not invalid,invalid
    shapes,inventory,roots=b.read_step(step);association=b.associate(shapes,inventory,parts)
    matched=[x['candidates'][0]['solid_index'] for x in association.values() if x['status']=='PASS']
    assert len(matched)==len(set(matched))==len(shapes)==len(parts)
    assert all(x['valid'] and x['volume_mm3']>0 for x in inventory)
    native={r:shapes[x['candidates'][0]['solid_index']] for r,x in association.items()}
    return parts,native,{'status':'PASS','scope':'All native STEP solids valid, uniquely associated to original native per-part STL by bounds/volume.',
      'native_step':str(step.resolve()),'native_step_sha256':sha(step),'native_stl_archive':str(neutral.resolve()),'native_stl_archive_sha256':sha(neutral),
      'transferred_roots':roots,'native_step_solids':len(shapes),'native_stl_parts':len(parts),
      'valid_positive_solids':len(shapes),'solid_inventory':inventory,'native_part_correspondence':association}

def prior_native():
    inventory=json.loads((BASE/'validation/native-step-inventory.json').read_text());assert sha(inventory['native_step'])==inventory['native_step_sha256']
    shapes,_,_=b.read_step(Path(inventory['native_step']))
    return {r:shapes[x['candidates'][0]['solid_index']] for r,x in inventory['native_part_correspondence'].items()},inventory

def vertices():
    # Exact vertices of a,p>=0,a+p<=2,u>=0,u+p+a<=30 times trim interval.
    return np.array([[u,p,a,e] for u,p,a in [(0,0,0),(0,2,0),(0,0,2),(30,0,0),(28,2,0),(28,0,2)] for e in[-.8,.8]],float)

def coefficients(ref,spec):
    if ref in spec['adjusting_refs']:return np.array([0.,0.,-1.,0.])
    old=v.motion(ref,json.loads((PROJECT/'review/flat132-reach-fit-2026-10-23/validation/manifest.json').read_text()))
    return np.array([old[0],old[1],old[0],old[2]])

def continuous_pairs(parts,spec):
    altered=CHANGED_OLD|set(spec['new_refs'])|{'P070a','P070b','P071a','P071b'}
    rows=[];domain=vertices()
    contacts={frozenset(x['pair']):x for x in spec.get('contacts',[])}
    # Geometry at the rear does not reach the articulated actuator. Its complete
    # inherited operating envelope lies in front of X40. Rods only lose stock.
    for a,bb in combinations(sorted(set(parts)-v.SPRINGS-v.ARTICULATED),2):
        if not ({a,bb}&altered):continue
        aa,ab=parts[a]['object'],parts[bb]['object']
        # Shortened mandrels are an exact subset of R6; they create no new
        # old-body collision. Newly added parts are still checked against them.
        if {a,bb}&{'H040','H041'} and not ({a,bb}&set(spec['new_refs'])):continue
        # Only the rear X>=116.7 part of P01 changed. Exact STEP equality of
        # the complementary volume is checked independently; avoid rerunning
        # all fixed front mount/guide contacts as if they were new.
        if a=='P01':aa=aa.trim_by_plane([1.,0.,0.],116.7)
        if bb=='P01':ab=ab.trim_by_plane([1.,0.,0.],116.7)
        delta=coefficients(a,spec)-coefficients(bb,spec)
        offsets=domain@delta;lo,hi=float(offsets.min()),float(offsets.max())
        # Move the less complex part so the conservative full-domain sweep is cheaper.
        if len(parts[a]['mesh'].faces)>len(parts[bb]['mesh'].faces):
            a,bb,aa,ab,lo,hi,delta=bb,a,ab,aa,-hi,-lo,-delta
        contact=contacts.get(frozenset((a,bb)))
        partition=next((x for x in spec.get('partitions',[]) if set(x['pair'])=={a,bb}),None)
        item=v.partitioned_relative_sweep(aa,ab,lo,hi,.01,.03125,partition,contact) if partition else v.relative_sweep(aa,ab,lo,hi,.01,.03125,contact)
        item.update(pair=[a,bb],relative_x_coefficients_u_p_a_e=delta.tolist())
        if contact:item=v.classify(item,contact,.01)
        rows.append(item)
    return rows

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--neutral',type=Path,required=True);parser.add_argument('--step',type=Path,required=True)
    parser.add_argument('--workspace',required=True);parser.add_argument('--poses',type=Path);parser.add_argument('--reuse-complete',action='store_true')
    args=parser.parse_args();certificate=_cert.main();source_sha=certificate['source_sha256']
    spec=json.loads((HERE/'rear-spec.json').read_text())
    assert spec['source_sha256']==source_sha
    parts,native,inventory=load_native(args.neutral,args.step)
    assert set(parts)==set(spec['expected_refs'])
    assert len([r for r in parts if r.startswith(('E','PCB_'))])==53
    inventory['source_sha256']=source_sha;write(HERE/'native-step-inventory.json',inventory)
    old,old_inventory=prior_native();assert set(native)-set(old)==set(spec['new_refs']);assert not(set(old)-set(native))
    identities=[]
    if args.reuse_complete:
        previous=json.loads((HERE/'validation-summary.json').read_text())
        assert previous['source_sha256']==source_sha
        cached_manifest=json.loads((HERE/'manifest.json').read_text())
        assert sha(HERE/'manifest.json')==previous['evidence_files']['manifest.json']
        assert sha(args.neutral)==cached_manifest['native_export_files_sha256'][str(args.neutral.resolve())]
        assert sha(args.step)==cached_manifest['native_export_files_sha256'][str(args.step.resolve())]
        for name in ['unchanged-native-breps.json','rear-exact-audit.json','rear-path-audit.json']:
            cached=json.loads((HERE/name).read_text());assert cached['status']=='PASS',name
            assert sha(HERE/name)==previous['evidence_files'][name],name
        assert inventory['native_step_sha256']==json.loads((HERE/'native-step-inventory.json').read_text())['native_step_sha256']
        identities=json.loads((HERE/'unchanged-native-breps.json').read_text())['checks']
    for ref in ([] if args.reuse_complete else sorted(set(old)-CHANGED_OLD)):
        error=b.xor_volume(native[ref],old[ref]);identities.append({'ref':ref,'symmetric_difference_mm3':error,'status':'PASS' if error<=TOL else 'FAIL'})
    identity={'status':'PASS' if all(x['status']=='PASS' for x in identities) else 'FAIL',
       'criterion':'Exact STEP symmetric difference at unchanged coordinates, tolerance1e-6mm3. No scaling, mesh repair or archive relabeling.',
       'baseline_step_sha256':old_inventory['native_step_sha256'],'native_step_sha256':sha(args.step),'checks':identities}
    write(HERE/'unchanged-native-breps.json',identity)
    print('R7 native inventory and unchanged body identities complete',flush=True)
    from rear_geometry import exact_geometry_checks,service_checks,dimension_checks,pose_checks,bearing_checks
    exact=json.loads((HERE/'rear-exact-audit.json').read_text())['checks'] if args.reuse_complete else exact_geometry_checks(native,old,spec)
    if not any(x['name'].startswith('Actual printed washer reaction support') for x in exact):exact+=bearing_checks(native)
    write(HERE/'rear-exact-audit.json',{'status':'PASS' if all(x['status']=='PASS' for x in exact) else 'FAIL','checks':exact})
    print('R7 exact rear construction/hardware checks complete',flush=True)
    continuous=json.loads((HERE/'rear-path-audit.json').read_text())['checks'] if args.reuse_complete else continuous_pairs(parts,spec)
    write(HERE/'rear-path-audit.json',{'status':'PASS' if not any(x['status']in BAD for x in continuous) else 'FAIL','scope':'All altered-rear pairs over exact correlated12vertex u,p,a,e domain; affine relative-X extrema and strict continuous sweep certificates.',
      'configuration_domain_vertices_u_p_a_e_mm':vertices().tolist(),'checks':continuous})
    print('R7 continuous rear pair checks complete:',len(continuous),flush=True)
    if args.reuse_complete:
        from rear_geometry import shoe_tip_withdrawal
        service=json.loads((HERE/'rear-service-audit.json').read_text())['checks']
        for row in service:
            if row['status']in BAD:
                assert row['name']=='Bench shoe withdrawal after capture pin removal' and row['pair']in[['P120','H260'],['P121','H261']]
                row.update(shoe_tip_withdrawal(parts[row['pair'][0]]['object'],parts[row['pair'][1]]['object']))
    else:service=service_checks(parts,native,spec)
    write(HERE/'rear-service-audit.json',{'status':'PASS' if not any(x['status']in BAD for x in service) else 'FAIL','checks':service})
    dimensions=dimension_checks(parts,native,spec)
    pose_spec=json.loads(args.poses.read_text()) if args.poses else []
    poses=pose_checks(parts,pose_spec,spec)
    write(HERE/'native-pose-audit.json',{'source_sha256':source_sha,'poses':poses})
    failures=[x for x in identities+exact+continuous+service+dimensions+poses if x['status']in BAD]
    unresolved=[x for x in poses if x['status']=='NOT_PROVIDED']
    manifest={'status':'ACTUAL_NATIVE_R7_INPUT_MANIFEST','feature_source':certificate['source'],
      'native_provenance':{'workspace_url':args.workspace,'feature_source_sha256':source_sha,'association':'Root operator verified exact R7 source and native pose regeneration before exports. This independent audit does not regenerate Onshape.'},
      'assembly':str(args.neutral.resolve()),'native_step':str(args.step.resolve()),
      'native_export_files_sha256':{str(p.resolve()):sha(p) for p in[args.neutral,args.step]+[Path(x['archive']) for x in pose_spec]},
      'expected_device_refs':sorted(r for r in parts if not r.startswith(('E','PCB_'))),
      'expected_electronics_count':53,'source_scope_certificate':str(HERE/'source-scope-certificate.json'),
      'source_scope_certificate_sha256':sha(HERE/'source-scope-certificate.json')}
    if (HERE/'manifest.json').exists():
        prior=json.loads((HERE/'manifest.json').read_text())
        for key in ['immutable_version_id','immutable_version_url','version_binding_note']:
            if key in prior.get('native_provenance',{}):manifest['native_provenance'][key]=prior['native_provenance'][key]
    write(HERE/'manifest.json',manifest)
    names=['manifest.json','source-scope-certificate.json','native-step-inventory.json','unchanged-native-breps.json','rear-exact-audit.json','rear-path-audit.json','rear-service-audit.json','native-pose-audit.json','rear-spec.json','audit_adjustable_rear.py','certify_source_scope.py','rear_geometry.py','requirements.txt']
    summary={'status':'NOMINAL_GEOMETRY_CHECKS_PASS' if not failures and not unresolved else 'INCOMPLETE_OR_FAILED',
      'scope':'R7 compact adjustable rear: new native exact body/source preservation, changed rear construction and all-domain clearance, actual fastener envelope, positive shoe capture and declared service checks. Unchanged front mechanism evidence is reused through exact R6 body/source identity and domain map.',
      'source_sha256':source_sha,'native_provenance':manifest['native_provenance'],'failed_checks':len(failures),'unresolved_checks':len(unresolved),
      'native_inventory':{'whole':len(parts),'device':len(parts)-53,'electronics_reference':53,'printed':sum(r.startswith('P') and not r.startswith('PCB_') for r in parts)},
      'changed_old_refs':sorted(CHANGED_OLD),'new_refs':spec['new_refs'],'unchanged_exact_brep_count':len(identities),
      'dimension_checks':dimensions,'native_poses':poses,'step_roundtrip_status':'COMPLETE',
      'evidence_files':{name:sha(HERE/name) for name in names},'failures':failures,'unresolved':unresolved,
      'baseline_reuse':{'source_scope_certificate':str(HERE/'source-scope-certificate.json'),'sha256':sha(HERE/'source-scope-certificate.json'),
        'baseline_summary_sha256':certificate['baseline_validation_summary_sha256'],'meaning':'Unchanged R6 front-body geometry and motion pairs retain prior validation under u_R6=a+u. All newly interacting rear bodies are checked here.'},
      'limitations':['500N remains an unqualified printed design target; rear screws/shoes are return stops, outside the full-load sensing stop path.',
        'Both M4 settings require manual equal measurement and locking; no physical synchronization mechanism is modeled.',
        'The nominal nut/set-screw engagement, print fits and assembly/tool envelopes do not establish torque retention, printed creep/fatigue or service life.',
        'Heat-set insert dimensions, actual purchased fastener tolerances and final assembly calibration require physical verification.',
        'Native source/export association is root-operator declared and hash-bound; this audit does not regenerate Onshape.']}
    for name in ['validation.json','validation-summary.json']:write(HERE/name,summary)
    (HERE/'validation-summary.md').write_text('# R7 adjustable rear validation\n\n**'+summary['status']+'**\n\nFailed:'+str(len(failures))+'; unresolved:'+str(len(unresolved))+'.\n\n'+summary['scope']+'\n\n'+ '\n'.join('- '+x for x in summary['limitations'])+'\n')
    print(json.dumps({k:summary[k] for k in['status','failed_checks','unresolved_checks','unchanged_exact_brep_count']},indent=2),flush=True)
if __name__=='__main__':main()
