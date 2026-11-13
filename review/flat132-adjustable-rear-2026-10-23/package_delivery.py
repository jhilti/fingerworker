#!/usr/bin/env python3
"""Extract raw R7 native millimetre STLs and package only bound nominal PASS evidence."""
from pathlib import Path
from hashlib import sha256
import argparse
import json
import re
import zipfile
R=Path(__file__).resolve().parent
ROOT=R.parents[1]
def digest(path):return sha256(path.read_bytes()).hexdigest()
def specification():return json.loads((R/'final-specification.json').read_text())
def bound_native(spec, filename):
    path=R/'native'/filename; record=spec['native_exports'][filename]
    assert digest(path)==record['sha256'],filename
    assert record['export_source_sha256']==spec['source']['sha256'],filename
    return path,record

def native_members(path,spec):
    result={}
    with zipfile.ZipFile(path) as archive:
        assert archive.testzip() is None
        assert len(archive.infolist())==spec['assembly_set']['full_native_solid_count']
        for item in archive.infolist():
            match=re.search(r'(?:^| - )([PH]\d+[ab]?)\b',item.filename)
            if not match:continue
            ref=match.group(1); assert ref not in result,ref
            assert item.filename.lower().endswith('.stl')
            result[ref]=(item.filename,archive.read(item))
    assert len(result)==spec['assembly_set']['device_STL_count'] and 'P03' not in result
    return result

def prepare_parts():
    spec=specification(); assert digest(R/spec['source']['file'])==spec['source']['sha256']
    neutral,record=bound_native(spec,spec['assembly_set']['source_native_zip'])
    members=native_members(neutral,spec);print_refs=set(spec['print_set']['refs'])
    assert {r for r in members if r.startswith('P')}==print_refs
    mapping={}
    for ref,(member,payload) in sorted(members.items()):
        path=R/'assembly-mm'/(ref+'.stl');path.parent.mkdir(exist_ok=True);path.write_bytes(payload)
        assert path.read_bytes()==payload
        mapping[ref]={'native_member':member,'native_member_sha256':sha256(payload).hexdigest(),'output':str(path.relative_to(R)),'output_sha256':digest(path),'bytes':len(payload)}
        if ref in print_refs:
            printed=R/'print-mm'/(ref+'.stl');printed.parent.mkdir(exist_ok=True);printed.write_bytes(payload)
            assert printed.read_bytes()==payload
    common={'source_sha256':spec['source']['sha256'],'native_zip':str(neutral.relative_to(R)),'native_zip_sha256':record['sha256'],'units':'mm','orientation':'Original native neutral assembly coordinates; no scaling, recentering, repair, remesh or slicing','identity':'Every output STL byte-for-byte equals its named native R7 ZIP member'}
    (R/'assembly-mm/part-manifest.json').write_text(json.dumps(dict(common,count=len(members),parts=mapping),indent=2)+'\n')
    printed={r:dict(mapping[r],output='print-mm/'+r+'.stl') for r in sorted(print_refs)}
    (R/'print-mm/part-manifest.json').write_text(json.dumps(dict(common,count=len(printed),changed_since_R6=spec['print_set']['changed_since_R6'],added_since_R6=spec['print_set']['added_since_R6'],rigid_palm_ref='P02',flexible_refs=spec['print_set']['flexible_refs'],parts=printed),indent=2)+'\n')
    iso,iso_record=bound_native(spec,spec['hardware_set']['source_native_ISO_zip']);sleeves={}
    for ref,(member,payload) in native_members(iso,spec).items():
        if ref not in {'H140','H141'}:continue
        path=R/'hardware-mm'/(ref+'.stl');path.parent.mkdir(exist_ok=True);path.write_bytes(payload)
        assert path.read_bytes()==payload
        sleeves[ref]={'native_member':member,'native_member_sha256':sha256(payload).hexdigest(),'output':str(path.relative_to(R)),'output_sha256':digest(path),'bytes':len(payload)}
    assert set(sleeves)=={'H140','H141'}
    (R/'hardware-mm/part-manifest.json').write_text(json.dumps({'source_sha256':spec['source']['sha256'],'native_zip':str(iso.relative_to(R)),'native_zip_sha256':iso_record['sha256'],'count':2,'units':'mm','material_intent':'Two matching steel ISO sleeves; not print parts','nominal_dimensions_mm':{'outer_diameter':16,'inner_diameter':8,'length':81},'orientation':'Original native ISO coordinates; byte-identical native ZIP members','parts':sleeves},indent=2)+'\n')
    return {'assembly_STLs':len(members),'print_STLs':len(printed),'ISO81_hardware_STLs':2}

def prepare_references():
    baseline=ROOT/'review/flat132-solid-palm-2026-10-23'
    copies={
      'reference/baseline/fingerworker_flat132_solid_palm.fs':baseline/'fingerworker_flat132_solid_palm.fs',
      'reference/baseline/R6-PRINT_NOTES.md':baseline/'PRINT_NOTES.md',
      'reference/baseline/R6-final-specification.json':baseline/'final-specification.json',
      'reference/baseline/Flat132_R6_final_AP214.step':baseline/'native/Flat132_R6_final_AP214.step',
      'reference/Omron_SS_datasheet.pdf':ROOT/'vendor/omron_ss5gl2/SS_datasheet.pdf',
      'reference/TE_FX1901_actual_apex_aligned_132_mm.step':ROOT/'review/flat132-palm-fit-2026-10-23/sensor/TE_FX1901_actual_apex_aligned_132_mm.step',
      'reference/spring-tradeoff.json':ROOT/'review/flat132-reach-study-2026-10-23/spring-tradeoff.json',
    }
    # Keep exact evidence with its original directory hierarchy so relative provenance remains readable.
    for path in (baseline/'validation').rglob('*'):
        if path.is_file() and path.suffix in {'.json','.md','.py','.txt'} and '__pycache__' not in path.parts:
            copies['reference/baseline/'+str(path.relative_to(baseline))]=path
    for path in (baseline/'reference').rglob('*'):
        if path.is_file() and path.suffix in {'.json','.md','.fs','.step'}:
            copies['reference/baseline/'+str(path.relative_to(baseline))]=path
    records={}
    for relative,source in copies.items():
        target=R/relative
        if source.is_file():target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(source.read_bytes())
        assert target.is_file(),source
        assert not source.is_file() or target.read_bytes()==source.read_bytes()
        records[relative]={'sha256':digest(target),'bytes':target.stat().st_size,'source_project_path':str(source)}
    assert digest(R/'reference/baseline/fingerworker_flat132_solid_palm.fs')==specification()['baseline']['source_sha256']
    (R/'reference/README.md').write_text('# Frozen reference material\n\nExact R6 baseline, inherited earlier evidence, Omron drawing, genuine TE sensor and spring catalogue record. Historical records do not assign a PASS to changed R7 geometry; the R7 root notes and independent R7 scope certificate govern the revision.\n')
    (R/'reference/reference-manifest.json').write_text(json.dumps({'identity':'Exact reference copies; baseline records are historical only','files':records},indent=2)+'\n')

def build_package():
    spec=specification();report_path=R/'validation/validation.json';report=json.loads(report_path.read_text())
    assert report['status']=='NOMINAL_GEOMETRY_CHECKS_PASS' and report['failed_checks']==report['unresolved_checks']==0
    assert spec['status']=='CAD_PROTOTYPE_NOMINAL_GEOMETRY_CHECKS_PASS'
    assert spec['validation']['binding_status']=='FINAL_BOUND'
    assert digest(report_path)==spec['validation']['report_sha256']
    assert digest(R/'validation/validation-summary.json')==spec['validation']['summary_sha256']
    source_sha=spec['source']['sha256']; assert digest(R/spec['source']['file'])==source_sha
    certificate=json.loads((R/'validation/source-scope-certificate.json').read_text())
    assert digest(R/'source-build.json')==certificate['source_build_sha256']
    assert digest(R/'hardware-dimension-evidence.json')==spec['hardware_dimension_evidence_sha256']
    assert digest(R/'portable-build-check.json')==spec['portable_build_check_sha256']
    portable=json.loads((R/'portable-build-check.json').read_text())
    assert portable['status']=='PASS' and portable['source_sha256']==source_sha
    assert digest(R/spec['source']['builder'])==portable['builder_sha256']
    assert report['native_provenance']['feature_source_sha256']==source_sha
    assert report['native_provenance']['immutable_version_id']==spec['onshape']['immutable_version_id']
    build=json.loads((R/'onshape-build.json').read_text())
    assert build['immutable_version_id']==spec['onshape']['immutable_version_id']
    assert build['immutable_source_readback_sha256']==source_sha
    for name in spec['native_exports']:bound_native(spec,name)
    assert not spec.get('proof_files_pending')
    assert set(spec['required_proof_files']).issubset(spec['proof_files'])
    for name,expected in spec['proof_files'].items():assert digest(R/name)==expected,name
    for name,expected in spec['validation'].get('evidence_files',{}).items():assert digest(R/name)==expected,name
    counts=prepare_parts();prepare_references()
    primary=['README.md','PRINT_NOTES.md','finalization-notes.md','final-specification.json',spec['source']['file'],spec['source']['builder'],'source-build.json','hardware-dimension-evidence.json','portable-build-check.json','onshape-build.json','package_delivery.py',spec['assembly_set']['source_native_step']]
    entries={name:R/name for name in primary}
    for sub in ['print-mm','assembly-mm','hardware-mm','reference','validation','proof']:
        for path in (R/sub).rglob('*'):
            if path.is_file() and '__pycache__' not in path.parts and path.suffix.lower()!='.zip' and not path.name.startswith(('provisional-','diagnostic-')):entries[str(path.relative_to(R))]=path
    assert all(p.is_file() for p in entries.values())
    for sub,count in [('print-mm',counts['print_STLs']),('assembly-mm',counts['assembly_STLs']),('hardware-mm',2)]:
        assert len([n for n in entries if n.startswith(sub+'/') and n.endswith('.stl')])==count
    assert not any(Path(n).name=='P03.stl' for n in entries)
    manifest={'revision':'Flat132 R7 compact screw-adjustable rear','source_sha256':source_sha,'neutral_native_zip_sha256':spec['native_exports'][spec['assembly_set']['source_native_zip']]['sha256'],'native_step_sha256':spec['native_exports'][Path(spec['assembly_set']['source_native_step']).name]['sha256'],'nominal_validation':'PASS','physical_500N_qualification':'PENDING',**counts,'steel_ISO_sleeves_mm':81,'immutable_version_id':spec['onshape']['immutable_version_id'],'large_native_pose_ZIPs':'Hash-bound project validation inputs omitted from compact package','files':{name:digest(path) for name,path in sorted(entries.items())}}
    delivery=R/'deliverables';delivery.mkdir(exist_ok=True);manifest_path=delivery/'package-manifest.json';manifest_path.write_text(json.dumps(manifest,indent=2)+'\n');package=R/spec['package']
    with zipfile.ZipFile(package,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
        for name,path in sorted(entries.items()):archive.write(path,name)
        archive.write(manifest_path,'package-manifest.json')
    with zipfile.ZipFile(package) as archive:
        assert archive.testzip() is None
        for name,expected in manifest['files'].items():assert sha256(archive.read(name)).hexdigest()==expected,name
    check=dict(path=str(package.relative_to(R)),sha256=digest(package),bytes=package.stat().st_size,members=len(entries)+1,crc_check='PASS',member_sha256_checks='PASS',**counts)
    (delivery/'delivery-check.json').write_text(json.dumps(check,indent=2)+'\n');return check
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--prepare-only',action='store_true');args=parser.parse_args()
    if args.prepare_only:
        counts=prepare_parts();prepare_references();print(json.dumps(dict(status='NATIVE_PART_FILES_PREPARED',**counts),indent=2))
    else:print(json.dumps(build_package(),indent=2))
