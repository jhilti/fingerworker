#!/usr/bin/env python3
"""Read-only R8 P02 cover audit; exact unchanged R7 evidence is retained."""
from pathlib import Path
import argparse,hashlib,json,sys
import numpy as np
HERE=Path(__file__).resolve().parent;STUDY=HERE.parent;PROJECT=STUDY.parents[1]
BASE=PROJECT/'review/flat132-adjustable-rear-2026-10-23'
sys.path.insert(0,str(BASE/'validation'))
import audit_adjustable_rear as r7
b=r7.b;v=r7.v
from OCP.BRepFilletAPI import BRepFilletAPI_MakeFillet
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_EDGE,TopAbs_SOLID,TopAbs_SHELL
from OCP.TopoDS import TopoDS
TOL=1e-6
BAD={'FAIL','INTERFERENCE','UNCHECKED','UNRESOLVED_NEAR_CONTACT'}
def sha(p):return b.sha(p)
def write(p,x):return v.write(p,x)

def certify_source():
    source_path=STUDY/'fingerworker_flat132_palm_cover.fs';baseline_path=BASE/'fingerworker_flat132_adjustable_rear.fs'
    ledger_path=STUDY/'source-build.json';ledger=json.loads(ledger_path.read_text())
    assert sha(baseline_path)=='d42805e8ee10158408099bf7185e49cf9a6eb06c23c327c90c01edfcd04eaddd'
    baseline=baseline_path.read_text();generated=baseline;changes=[]
    assert {x['label'] for x in ledger['changes']}=={'R8 study identity','R8 feature name','P02 only: join flush wrist ledge over complete lid footprint'}
    for row in ledger['changes']:
        count=generated.count(row['old']);assert count==row['count'];generated=generated.replace(row['old'],row['new']);changes.append({'label':row['label'],'replacement_count':count})
    assert generated==source_path.read_text();assert sha(source_path)==ledger['sha256']
    summary_path=BASE/'validation/validation-summary.json';summary=json.loads(summary_path.read_text())
    assert summary['status']=='NOMINAL_GEOMETRY_CHECKS_PASS' and summary['failed_checks']==summary['unresolved_checks']==0
    assert summary['source_sha256']==sha(baseline_path)
    evidence={}
    for name,digest in summary['evidence_files'].items():
        p=BASE/'validation'/name;assert sha(p)==digest,name;evidence[str(p)]=digest
    result={'status':'PASS_EXACT_P02_ONLY_SOURCE_SCOPE','source':str(source_path),'source_sha256':sha(source_path),
      'baseline_source':str(baseline_path),'baseline_source_sha256':sha(baseline_path),'baseline_immutable_version_id':'6dd467818da7364197461627',
      'source_build_sha256':sha(ledger_path),'exact_forward_reconstruction_matches_all_source_bytes':True,
      'replacement_ledger':changes,'changed_ref':'P02','unchanged_domain':'a>=0,p>=0,a+p<=2,u>=0,u+a+p<=30,e in[-0.8,0.8];ISOq20-p',
      'baseline_validation_summary':str(summary_path),'baseline_validation_summary_sha256':sha(summary_path),'baseline_evidence_files_sha256':evidence,
      'reuse_policy':'All R7 body pairs excluding P02 retain exact source/motion definitions. Independent122-body native BRep identity and new P02 construction/coverage/path checks are required; no R7 rear audit is relabeled as newly run.',
      'limitations':['A source reconstruction is not native regeneration or print/strength qualification.']}
    write(HERE/'source-scope-certificate.json',result);return result

def source_ledge():
    def unique_edges(shape):
        ex=TopExp_Explorer(shape,TopAbs_EDGE);edges=[]
        while ex.More():
            edge=TopoDS.Edge(ex.Current())
            if not any(edge.IsSame(prior) for prior in edges):edges.append(edge)
            ex.Next()
        return edges
    stock=b.box([-46.1,-64,9.5],[-33,64,11.5]);f=BRepFilletAPI_MakeFillet(stock)
    for edge in unique_edges(stock):
        bounds=b.bounds(edge)
        if bounds[1,2]-bounds[0,2]>1.9 and np.max(bounds[1,:2]-bounds[0,:2])<1e-6:f.Add(2,edge)
    f.Build();assert f.IsDone();stock=f.Shape();f=BRepFilletAPI_MakeFillet(stock);n=0
    for edge in unique_edges(stock):
        bounds=b.bounds(edge)
        if abs(bounds[0,2]-11.5)<1e-6 and abs(bounds[1,2]-11.5)<1e-6:f.Add(.5,edge);n+=1
    assert n==8,n;f.Build();assert f.IsDone();return f.Shape()

def native_baseline():
    inventory=json.loads((BASE/'validation/native-step-inventory.json').read_text());assert sha(inventory['native_step'])==inventory['native_step_sha256']
    shapes,_,_=b.read_step(Path(inventory['native_step']))
    return {ref:shapes[row['candidates'][0]['solid_index']] for ref,row in inventory['native_part_correspondence'].items()},inventory

def exact_palm_checks(native,old):
    palm=native['P02'];stock=source_ledge();expected=b.fuse(old['P02'],stock);checks=[]
    difference=b.xor_volume(palm,expected)
    checks.append({'name':'Independent R2 plan/R0.5 upper filleted ledge union exact CSG','symmetric_difference_mm3':difference,'status':'PASS' if difference<=TOL else 'FAIL'})
    checks.append({'name':'One connected rigid palm print without enclosed sleeve cavity','solid_count':b.count(palm,TopAbs_SOLID),'shell_count':b.count(palm,TopAbs_SHELL),
       'status':'PASS' if b.count(palm,TopAbs_SOLID)==1 and b.count(palm,TopAbs_SHELL)==1 and BRepCheck_Analyzer(palm).IsValid() else 'FAIL'})
    missing=b.volume(b.cut(old['P02'],palm));checks.append({'name':'All original P02 stock retained','missing_original_material_mm3':missing,'status':'PASS' if missing<=TOL else 'FAIL'})
    high=b.box([-100,-100,11.5001],[10,100,40]);difference=b.xor_volume(b.common(palm,high),b.common(old['P02'],high))
    checks.append({'name':'Curved palm/contact datum unchanged above new low ledge','symmetric_difference_mm3':difference,'curved_tangent_x_mm':-37.25,
       'meaning':'New ledge minX-46.1 is a separate lower feature; it does not redefine the unchanged half-round contact tangent atZ19.75.','status':'PASS' if difference<=TOL else 'FAIL'})
    for name,lo,hi in[
      ('left M4/key',[-24,-38,6],[-9,-25,32]),('right M4/key',[-24,25,6],[-9,38,32]),
      ('left enclosure M2 pilot',[-30,-62,9],[-23,-56,15]),('right enclosure M2 pilot',[-30,56,9],[-23,62,15])]:
        region=b.box(lo,hi);difference=b.xor_volume(b.common(palm,region),b.common(old['P02'],region))
        checks.append({'name':'Unchanged local mount/approach '+name,'symmetric_difference_mm3':difference,'status':'PASS' if difference<=TOL else 'FAIL'})
    # A native horizontal ledge slice and an upper original-plate slice are
    # moved to one elevation. Their union is an exact vertical-coverage witness.
    lower=b.common(palm,b.box([-100,-100,9.6],[10,100,9.7]));upper=b.common(palm,b.box([-100,-100,14],[10,100,14.1]));upper=r7.tr(upper,[0,0,-4.4]);shadow=b.fuse(lower,upper)
    for name,lo,hi in[
      ('Full P09 rectangular lid incl four corners',[-46.1,-55,9.6],[-23.6,55,9.7]),
      ('Full P08 enclosing footprint incl tabs/corners',[-46.1,-62,9.6],[-23.6,62,9.7])]:
        target=b.box(lo,hi);uncovered=b.volume(b.cut(target,shadow));checks.append({'name':name,'uncovered_witness_volume_mm3':uncovered,
          'method':'Complete native slices atZ9.6..9.7 plusZ14..14.1 translated vertically; no sampling or bounding-box-only assertion.',
          'status':'PASS' if uncovered<=TOL else 'FAIL'})
    for ref,expected_gap in [('P09',.6),('E06',2.2),('E08',4.4)]:
        clearance=b.gap(stock,native[ref]);checks.append({'name':'Added ledge to '+ref,'exact_gap_mm':clearance,'expected_gap_mm':expected_gap,
          'status':'PASS' if abs(clearance-expected_gap)<1e-5 else 'FAIL'})
    clearance=b.gap(palm,native['P09']);checks.append({'name':'Complete P02 to P09 lid minimum nominal gap','exact_gap_mm':clearance,'status':'PASS' if abs(clearance-.6)<1e-5 else 'FAIL'})
    physical=lambda table:np.array([np.min([b.bounds(x)[0] for ref,x in table.items() if not ref.startswith(('E','PCB_'))],axis=0),np.max([b.bounds(x)[1] for ref,x in table.items() if not ref.startswith(('E','PCB_'))],axis=0)])
    new_bounds,old_bounds=physical(native),physical(old)
    checks.append({'name':'Physical device envelope unchanged from R7','new_bounds_mm':new_bounds.tolist(),'baseline_bounds_mm':old_bounds.tolist(),
      'depth_width_height_mm':(new_bounds[1]-new_bounds[0]).tolist(),'status':'PASS' if np.max(np.abs(new_bounds-old_bounds))<=1e-6 else 'FAIL'})
    # Existing P02/P08 collars already touch. Only added stock clearance and
    # exact old local mount preservation are new claims.
    for ref,other in sorted(native.items()):
        if ref=='P02':continue
        overlap=0. if v.separated(b.bounds(palm),b.bounds(other)) else b.volume(b.common(palm,other))
        checks.append({'name':'Exact changed-palm native pair','pair':['P02',ref],'intersection_volume_mm3':overlap,'status':'PASS' if overlap<=TOL else 'FAIL'})
    return checks

def palm_motion_checks(parts):
    source_spec=json.loads((BASE/'validation/rear-spec.json').read_text());domain=r7.vertices();rows=[];palm=parts['P02']['object']
    for target in sorted(set(parts)-{'P02'}-v.SPRINGS-v.ARTICULATED):
        motion=-r7.coefficients(target,source_spec);offsets=domain@motion
        item=v.relative_sweep(palm,parts[target]['object'],float(offsets.min()),float(offsets.max()),.01,.03125)
        rows.append({'pair':['P02',target],'relative_x_coefficients_u_p_a_e':motion.tolist(),**item})
    for target in sorted(v.SPRINGS|v.ARTICULATED):
        # Complete source-derived envelopes; the leftmost spring wire isX12,
        # while the articulated lever pivot envelope beginsX29.05.
        left=12. if target in v.SPRINGS else 29.05
        clearance=left-float(parts['P02']['mesh'].bounds[1,0])
        rows.append({'pair':['P02',target],'status':'CONTINUOUS_CLEARANCE_CERTIFIED' if clearance>0 else 'FAIL',
          'method':'Complete unchanged-source axial envelope separation across exactR7domain','minimum_x_gap_mm':clearance})
    return rows

def service_checks(parts,native):
    old_manifest=json.loads((PROJECT/'review/flat132-reach-fit-2026-10-23/validation/manifest.json').read_text())
    module={'P02','P08','P09','P10'}|{r for r in parts if r.startswith(('E','PCB_'))}
    lift={'name':'Complete palm/case upward release, changed P02 only','moving_refs':['P02'],'fixed_refs':sorted(set(parts)-module-v.SPRINGS-v.ARTICULATED),
      'direction':[0,0,1],'range_mm':[0,40],'initial_translation_mm':[0,0,.001],'preload_mm':2,
      'prerequisites':'Unload/restrain spring energy; set rear advance0/preload2; remove both palm M4 fasteners; move complete P02/case/electronics module together. All unchanged module parts retain original R7 service evidence.'}
    down={'name':'Bench case separation below fixed palm','moving_refs':sorted(module-{'P02','E06','E08'}),'fixed_refs':['P02'],
      'direction':[0,0,-1],'range_mm':[0,20],'initial_translation_mm':[0,0,-.001],
      'prerequisites':'Palm/case unit removed from frame and safely supported; remove two enclosure-to-palm M2 fasteners atX-26.5/Y±59 from below; disconnect/restrain wiring. Lower complete case/electronics from palm.'}
    lid={'name':'P09 lid release only after case detached from palm','moving_refs':['P09'],
      'fixed_refs':sorted((module-{'P02','P09','E06','E08'})),'direction':[0,0,1],'range_mm':[0,15],
      'prerequisites':'Case fully detached from P02; remove all three lid screws. P02 is absent, not an obstacle waived during installed lid opening.'}
    rows=v.service_sweeps(parts,dict(old_manifest,service_sweeps=[lift,down,lid]))
    for row in rows:
        if row['name']=='P09 lid release only after case detached from palm' and row['pair']==['P09','P08']:
            row.update(lid_case_withdrawal(native))
    return rows


def lid_case_withdrawal(native):
    # Complete conservative native-BRep cover, independently checked rather
    # than relying on tiny float32 STL rim-plane deviations. Filling the three
    # screw holes is conservative. Seven convex rectangular stocks cover every
    # P09 material point; each full translated union is one taller exact box.
    covers=[([-46.1,-53.9,8.1],[-23.6,53.9,8.9]),
      ([-46.1,-55,8.1],[-29.1,-53.9,8.9]),([-46.1,53.9,8.1],[-29.1,55,8.9]),
      ([-23.9,-55,8.1],[-23.6,-53.9,8.9]),([-23.9,53.9,8.1],[-23.6,55,8.9]),
      ([-44.6,-27,2.15],[-25.1,-25,8.2]),([-41.5,36,6.6],[-29.5,39,8.2])]
    cover=r7.union([b.box(lo,hi) for lo,hi in covers]);missing=b.volume(b.cut(native['P09'],cover));rows=[]
    for lo,hi in covers:
        end=list(hi);end[2]+=15;swept=b.box(lo,end);overlap=b.volume(b.common(swept,native['P08']))
        rows.append({'neutral_cover_bounds_mm':[lo,hi],'complete_sweep_bounds_mm':[lo,end],
          'complete_swept_envelope_intersection_upper_bound_mm3':overlap,'status':'PASS' if overlap<=TOL else 'FAIL'})
    passed=missing<=TOL and all(x['status']=='PASS' for x in rows)
    return {'status':'COMPLETE_NATIVE_BREP_CONVEX_COVER_CONTINUOUS_CLEARANCE_CERTIFIED' if passed else 'FAIL',
      'method':'Independent7-box conservative cover of the complete actual native STEP lid, with all source screw holes filled. Complete0..15mm vertical union of each convex stock is one exact box. Every swept box is intersected with native P08. This proves all translations, including initial rim tangency, without sampled-contact or STL-quantization waivers.',
      'native_lid_uncovered_material_mm3':missing,'kernel_volume_tolerance_mm3':TOL,'certificates':rows,
      'complete_sweep_intersection_volume_upper_bound_mm3':sum(x['complete_swept_envelope_intersection_upper_bound_mm3'] for x in rows),
      'relative_x_range_mm':[0,15]}

def pose_checks(neutral,poses):
    rows=[]
    if len(poses)!=3:return [{'status':'NOT_PROVIDED','name':'All3additionalnativewholeposewitnessesrequired'}]
    mapping={'adjusted_rest_a2':'Flat132_R7_adjusted_rest_a2_final.zip','maximum28_p2':'Flat132_R7_max28_p2_heavy_final.zip','isometric13_p2_81':'Flat132_R7_isometric13_p2_81_final.zip'}
    palm_sha=v.canonical_triangle_sha256(neutral['P02']['mesh'])
    for pose in poses:
        archive=Path(pose['archive']);posed,ignored=v.load(archive,{});old_path=BASE/'native'/mapping[pose['name']];prior,ignored_old=v.load(old_path,{})
        checks=[]
        for ref in sorted(posed):
            first=v.canonical_triangle_sha256(posed[ref]['mesh']);second=palm_sha if ref=='P02' else v.canonical_triangle_sha256(prior[ref]['mesh'])
            checks.append({'ref':ref,'native_triangle_sha256':first,'expected_triangle_sha256':second,'status':'PASS' if first==second else 'FAIL'})
        rows.append({'pose':pose['name'],'archive':str(archive.resolve()),'sha256':sha(archive),'baseline_native_pose_sha256':sha(old_path),
          'status':'PASS' if not ignored and not ignored_old and set(posed)==set(prior) and len(posed)==123 and all(x['status']=='PASS' for x in checks) else 'FAIL',
          'scope':'Changed fixed P02 matches native R8 neutral; all122 other complete native posed bodies match equivalent frozen R7 pose exactly, ignoring only triangle/vertex order. No archive renaming/relabeling.','checks':checks})
    return rows

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--neutral',type=Path,required=True);parser.add_argument('--step',type=Path,required=True)
    parser.add_argument('--workspace',required=True);parser.add_argument('--poses',type=Path);parser.add_argument('--reuse-complete',action='store_true');args=parser.parse_args()
    certificate=certify_source();source_sha=certificate['source_sha256'];parts,native,inventory=r7.load_native(args.neutral,args.step)
    assert len(parts)==123 and sum(r.startswith(('E','PCB_')) for r in parts)==53
    old,old_inventory=native_baseline();assert set(native)==set(old)
    inventory['source_sha256']=source_sha;write(HERE/'native-step-inventory.json',inventory)
    prior={}
    if args.reuse_complete:
        summary=json.loads((HERE/'validation-summary.json').read_text());assert summary['source_sha256']==source_sha
        for fn in ['unchanged-native-breps.json','palm-exact-audit.json','palm-path-audit.json','palm-service-audit.json']:
            assert sha(HERE/fn)==summary['evidence_files'][fn];prior[fn]=json.loads((HERE/fn).read_text())
            if fn=='palm-service-audit.json' and prior[fn]['status']!='PASS':
                for row in prior[fn]['checks']:
                    if row['status']in BAD:
                        assert row['name']=='P09 lid release only after case detached from palm' and row['pair']==['P09','P08']
                        row.update(lid_case_withdrawal(native))
                prior[fn]['status']='PASS' if not any(row['status']in BAD for row in prior[fn]['checks']) else 'FAIL'
            assert prior[fn]['status']=='PASS',fn
        m=json.loads((HERE/'manifest.json').read_text());assert sha(args.neutral)==m['native_export_files_sha256'][str(args.neutral.resolve())] and sha(args.step)==m['native_export_files_sha256'][str(args.step.resolve())]
    identity=prior.get('unchanged-native-breps.json',{}).get('checks',[])
    if not args.reuse_complete:
        for ref in sorted(set(native)-{'P02'}):
            difference=b.xor_volume(native[ref],old[ref]);identity.append({'ref':ref,'symmetric_difference_mm3':difference,'status':'PASS' if difference<=TOL else 'FAIL'})
    write(HERE/'unchanged-native-breps.json',{'status':'PASS' if all(x['status']=='PASS' for x in identity) else 'FAIL','native_step_sha256':sha(args.step),'baseline_step_sha256':old_inventory['native_step_sha256'],
      'criterion':'Exact native STEP Boolean symmetric difference, threshold1e-6mm3; no geometry correction, scaling or translation.','checks':identity})
    print('R8 native123valid;122unchangedBRepidentitiescomplete',flush=True)
    exact=prior.get('palm-exact-audit.json',{}).get('checks') if args.reuse_complete else exact_palm_checks(native,old)
    write(HERE/'palm-exact-audit.json',{'status':'PASS' if all(x['status']=='PASS' for x in exact) else 'FAIL','source_sha256':source_sha,'native_step_sha256':sha(args.step),'checks':exact})
    print('R8 independentP02CSG,coverage,exactpairscomplete',flush=True)
    motion=prior.get('palm-path-audit.json',{}).get('checks') if args.reuse_complete else palm_motion_checks(parts)
    write(HERE/'palm-path-audit.json',{'status':'PASS' if not any(x['status']in BAD for x in motion) else 'FAIL','source_sha256':source_sha,
      'scope':'Only changedP02 versus full unchanged R7 mechanism over12verticesofcorrelatedu,p,a,e domain; strict continuous affine-X certificates, plus complete spring/articulated envelope separation.','checks':motion})
    service=prior.get('palm-service-audit.json',{}).get('checks') if args.reuse_complete else service_checks(parts,native)
    write(HERE/'palm-service-audit.json',{'status':'PASS' if not any(x['status']in BAD for x in service) else 'FAIL','source_sha256':source_sha,'checks':service})
    print('R8 changedP02full-domainanddeclaredservicecheckscomplete',flush=True)
    poses_spec=json.loads(args.poses.read_text()) if args.poses else [];poses=pose_checks(parts,poses_spec)
    write(HERE/'native-pose-audit.json',{'source_sha256':source_sha,'poses':poses})
    failures=[x for x in identity+exact+motion+service+poses if x['status']in BAD];unresolved=[x for x in poses if x['status']=='NOT_PROVIDED']
    manifest={'status':'ACTUAL_NATIVE_R8_INPUT_MANIFEST','feature_source':certificate['source'],
      'native_provenance':{'workspace_url':args.workspace,'feature_source_sha256':source_sha,'association':'Root operator verified exact R8 source/native regeneration and poses before export; this independent script does not regenerate Onshape.'},
      'assembly':str(args.neutral.resolve()),'native_step':str(args.step.resolve()),'native_export_files_sha256':{str(p.resolve()):sha(p) for p in[args.neutral,args.step]+[Path(x['archive']) for x in poses_spec]},
      'expected_device_refs':sorted(r for r in parts if not r.startswith(('E','PCB_'))),'expected_electronics_count':53,
      'source_scope_certificate':str(HERE/'source-scope-certificate.json'),'source_scope_certificate_sha256':sha(HERE/'source-scope-certificate.json')}
    if (HERE/'manifest.json').exists():
        before=json.loads((HERE/'manifest.json').read_text())
        for key in ['immutable_version_id','immutable_version_url','version_binding_note']:
            if key in before.get('native_provenance',{}):manifest['native_provenance'][key]=before['native_provenance'][key]
    write(HERE/'manifest.json',manifest)
    names=['manifest.json','source-scope-certificate.json','native-step-inventory.json','unchanged-native-breps.json','palm-exact-audit.json','palm-path-audit.json','palm-service-audit.json','native-pose-audit.json','audit_palm_cover.py','requirements.txt']
    summary={'status':'NOMINAL_GEOMETRY_CHECKS_PASS' if not failures and not unresolved else 'INCOMPLETE_OR_FAILED','source_sha256':source_sha,'native_provenance':manifest['native_provenance'],
      'scope':'R8 P02-only palm electronics cover: exact native122-body/source preservation, independent single-body ledge construction, complete electronics footprint coverage, lid/port gaps and focused full-domain/module/case/lid service checks. Prior unchanged R7 rear/motion evidence is retained under exact identity; not rerun or relabeled.',
      'failed_checks':len(failures),'unresolved_checks':len(unresolved),'native_inventory':{'whole':123,'device':70,'electronics_reference':53,'printed':16},'changed_ref':'P02','unchanged_exact_brep_count':122,
      'step_roundtrip_status':'COMPLETE','palm_checks':[x for x in exact if x['name']!='Exact changed-palm native pair'],
      'native_poses':poses,'evidence_files':{name:sha(HERE/name) for name in names},'failures':failures,'unresolved':unresolved,
      'baseline_reuse':{'source_scope_certificate':str(HERE/'source-scope-certificate.json'),'sha256':sha(HERE/'source-scope-certificate.json'),'baseline_summary_sha256':certificate['baseline_validation_summary_sha256']},
      'limitations':['500N remains an unqualified printed design target; no new load rating is inferred from nominal geometry.',
       'P02 remains a separate rigid palm cover; P09 remains a separate lid. Detach the case from the removed palm/case unit before opening P09.',
       '0.6mm is specifically P02-to-P09 nominal gap; existing P08 mounting collar contact is unchanged and not a clearance claim.',
       'Actual heat-set insert stock, fastening/USB/tool tolerances, print creep/durability and comfort remain physical checks.',
       'The hand scan is approximate. No fit, pinch-safe human envelope or comfort qualification is inferred.',
       'The new ledge has the requested case footprint; its 2mm nominal stock and rounding are not slicer infill, water/dust sealing or strength qualification.',
       'Native source/export association is operator-declared and hash-bound; this audit does not regenerate Onshape.']}
    for name in ['validation.json','validation-summary.json']:write(HERE/name,summary)
    (HERE/'validation-summary.md').write_text('# R8 palm-cover validation\n\n**'+summary['status']+'**\n\nFailed:'+str(len(failures))+'; unresolved:'+str(len(unresolved))+'.\n\n'+summary['scope']+'\n\n'+'\n'.join('- '+x for x in summary['limitations'])+'\n')
    print(json.dumps({k:summary[k] for k in['status','failed_checks','unresolved_checks','unchanged_exact_brep_count']},indent=2),flush=True)
if __name__=='__main__':main()
