#!/usr/bin/env python3
"""Replace only P01 with the declared R15 mesh in the verified six-piece project.

No native-release mesh repair, scaling or automatic placement. Local OCC
candidates may omit explicitly recorded zero-area facets. The remaining five
native mesh resources, orientations, object options and positions are retained.
"""
from pathlib import Path
from hashlib import sha256
import argparse,copy,json,shutil,xml.etree.ElementTree as E,zipfile
import numpy as np
import trimesh

OUT=Path(__file__).resolve().parents[1];ROOT=OUT.parents[1]
OLD=ROOT/'print/bambu-R13-mechanics-overnight-2026-11-04'
STUDY=ROOT/'review/inboard-straps-2026-11-08'
BASE='Fingerworker_R15_H2D_04mm_PLA_Inboard_Straps'
NS={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}
PN='{http://schemas.microsoft.com/3dmanufacturing/production/2015/06}'
E.register_namespace('',NS['m']);E.register_namespace('p',PN[1:-1])
meta=lambda e:{m.get('key'):m.get('value') for m in e.findall('metadata') if m.get('key')}
sha=lambda p:sha256(Path(p).read_bytes()).hexdigest()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--source',type=Path,default=STUDY/'print-mm/P01.stl')
    ap.add_argument('--source-cad',type=Path,required=True)
    ap.add_argument('--version',required=True)
    ap.add_argument('--candidate',action='store_true')
    ap.add_argument('--solid-strap-eyes',action='store_true',help='Four local100%% slot-ligament infill masks; native mesh remains unchanged')
    ap.add_argument('--modifier-config',type=Path,default=OUT/'source/strap-print-regions.json')
    args=ap.parse_args();source=args.source.resolve();cad=args.source_cad.resolve()
    for folder in ('profiles','source-mm','STL-print-oriented','preview','runtime','validation','evidence'):(OUT/folder).mkdir(parents=True,exist_ok=True)
    prior=json.loads((OLD/'plate-layout.json').read_text());layout=copy.deepcopy(prior)
    brim_changes={}
    for ref,settings in layout['object_settings'].items():
        brim_changes[ref]={'old_type':settings['brim_type'],'old_width_mm':float(settings['brim_width']),'new_type':'no_brim','new_width_mm':0}
        settings.update(brim_type='no_brim',brim_width='0')
    baseline=OLD/prior['native_project']
    assert sha(baseline)=='6c8d3d766ea78e08310d741d8104fa17f4d0a7ba163688030f10340c743fabe2'
    mesh=trimesh.load(source,force='mesh',process=False)
    # STL repeats vertices by triangle; merge coincident coordinates only to
    # encode a valid indexed mesh. No vertices move and no faces are removed.
    vertices,indices=np.unique(mesh.vertices,axis=0,return_inverse=True)
    faces=indices[mesh.faces]
    candidate_zero_area_facets=0
    candidate_zero_area_facet_vertices=[]
    if args.candidate:
        # OCC's local STL export repeats a vertex in eight inherited base-fillet
        # facets. Only mathematically zero-area facets may be omitted here; the
        # native release path below never removes any source facet.
        keep=np.array([len(set(f))==3 for f in faces])
        candidate_zero_area_facet_vertices=vertices[faces[~keep]].tolist()
        candidate_zero_area_facets=int((~keep).sum());faces=faces[keep]
    mesh=trimesh.Trimesh(vertices=vertices,faces=faces,process=False)
    assert mesh.is_watertight and mesh.is_volume and mesh.body_count==1
    R=np.eye(3);points=mesh.vertices@R.T;lo=points.min(0);hi=points.max(0)
    size=hi-lo;center=(hi+lo)/2;centered=points-center
    row=next(r for r in layout['placements'] if r['ref']=='P01')
    xy=np.array(row['plate_xy_mm']);margin=row['reserved_margin_mm']
    row.update(source_path=str(source.relative_to(ROOT)),source_sha256=sha(source),
        source_geometry='LOCAL_R15_CANDIDATE_STL' if args.candidate else 'NATIVE_R15_ONSHAPE_STL',
        CAD_source_sha256=sha(cad),intent='INTEGRATED NEAR-PALM FRAME WITH INBOARD STRAP SLOTS - PLA ASSEMBLY STUDY',
        orientation='Base floor down; rounded near-palm contact surface upward',
        rotation_3x3=R.tolist(),normalization_translation_mm=(-lo).tolist(),
        size_oriented_mm=size.tolist(),volume_mm3=float(mesh.volume),faces=len(faces),
        reserved_bounds_xy_mm=[*(xy-margin).tolist(),*(xy+size[:2]+margin).tolist()])
    for r in layout['placements']:
        for folder in ('source-mm','STL-print-oriented'):
            if r['ref']!='P01':shutil.copyfile(OLD/folder/(r['ref']+'.stl'),OUT/folder/(r['ref']+'.stl'))
        if r['ref']!='P01':r['source_geometry']='RETAINED_R13_NATIVE_STL' if r['ref']!='Q01' else r['source_geometry']
    shutil.copyfile(source,OUT/'source-mm/P01.stl')
    oriented=trimesh.Trimesh(vertices=points-lo,faces=faces,process=False)
    oriented.export(OUT/'STL-print-oriented/P01.stl')
    shutil.copyfile(cad,OUT/'source'/cad.name)
    process=json.loads((OLD/'profiles/H2D_process.json').read_text())
    process['name']=process['print_settings_id']='Fingerworker R15 inboard straps no brim 0.20mm'
    (OUT/'profiles/H2D_process.json').write_text(json.dumps(process,indent=2)+'\n')
    for name in ('H2D_machine.json','H2D_PLA.json'):shutil.copyfile(OLD/'profiles'/name,OUT/'profiles'/name)
    stem=BASE+('_candidate-flat' if args.candidate else '')
    seed=OUT/(stem+'_seed.3mf')
    with zipfile.ZipFile(baseline) as z:
        extra_resources={}
        model=E.fromstring(z.read('3D/3dmodel.model'));cfg=E.fromstring(z.read('Metadata/model_settings.config'))
        model.set('xmlns:BambuStudio','http://schemas.bambulab.com/package/2021')
        objects={o.get('id'):meta(o)['name'].split(' - ')[0] for o in cfg.findall('object')}
        for object_element in cfg.findall('object'):
            values={m.get('key'):m for m in object_element.findall('metadata') if m.get('key')}
            for key,value in {'brim_type':'no_brim','brim_width':'0'}.items():
                if key in values:values[key].set('value',value)
                else:E.SubElement(object_element,'metadata',key=key,value=value)
        ident=next(i for i,r in objects.items() if r=='P01')
        obj=next(o for o in cfg.findall('object') if o.get('id')==ident)
        resource=next(o for o in model.findall('m:resources/m:object',NS) if o.get('id')==ident)
        component=resource.find('m:components/m:component',NS)
        assert component.get('transform')=='1 0 0 0 1 0 0 0 1 0 0 0'
        mesh_path=component.get(PN+'path').lstrip('/')
        sub=E.fromstring(z.read(mesh_path));sub.set('xmlns:BambuStudio','http://schemas.bambulab.com/package/2021')
        oldmesh=sub.find('m:resources/m:object/m:mesh',NS)
        oldmesh.clear();vv=E.SubElement(oldmesh,'{'+NS['m']+'}vertices');ff=E.SubElement(oldmesh,'{'+NS['m']+'}triangles')
        for v in centered:E.SubElement(vv,'{'+NS['m']+'}vertex',**{k:format(float(n),'.12g') for k,n in zip('xyz',v)})
        for f in faces:E.SubElement(ff,'{'+NS['m']+'}triangle',**{k:str(int(n)) for k,n in zip(('v1','v2','v3'),f)})
        for item in model.findall('m:build/m:item',NS):
            if item.get('objectid')==ident:item.set('transform','1 0 0 0 1 0 0 0 1 '+' '.join(format(float(v),'.12g') for v in [*(xy+size[:2]/2),size[2]/2]))
        for n in obj.findall('metadata'):
            if n.get('key')=='name':n.set('value','P01 - '+row['intent'])
            if n.get('face_count') is not None:n.set('face_count',str(len(faces)))
        for n in obj.findall('part/metadata'):
            if n.get('key','').startswith('source_offset_'):n.set('value',format(float(size['xyz'.index(n.get('key')[-1])]/2),'.12g'))
        for n in obj.findall('part/mesh_stat'):n.set('face_count',str(len(faces)))
        modifiers=[]
        if args.solid_strap_eyes:
            rels=z.read('3D/_rels/3dmodel.model.rels').decode();new_relationships=[]
            regions=json.loads(args.modifier_config.read_text())
            assert regions['revision']=='R15' and len(regions['slots'])==4
            assert regions.get('CAD_source_sha256',sha(cad))==sha(cad)
            for slot in regions['slots']:
                    lower,upper=slot['modifier_bounds_mm']
                    transform=np.eye(4);transform[:3,3]=(np.array(lower)+upper)/2-center
                    mask=trimesh.creation.box(extents=np.array(upper)-lower,transform=transform)
                    mask_id=str(101+len(modifiers));mask_path='3D/Objects/strap_eye_modifier_'+mask_id+'.model'
                    label=f"Inboard slot {slot['name']} - local100% infill"
                    modifiers.append(dict(name=label,native_bounds_mm=[lower,upper],sparse_infill_density='100%',sparse_infill_pattern='zig-zag',purpose='Solid inboard slot bearing ligaments; does not add printed geometry'))
                    mask_model=E.Element('{'+NS['m']+'}model',unit='millimeter')
                    res=E.SubElement(mask_model,'{'+NS['m']+'}resources');mo=E.SubElement(res,'{'+NS['m']+'}object',id=mask_id,type='model')
                    mm=E.SubElement(mo,'{'+NS['m']+'}mesh');mv=E.SubElement(mm,'{'+NS['m']+'}vertices');mf=E.SubElement(mm,'{'+NS['m']+'}triangles')
                    for v in mask.vertices:E.SubElement(mv,'{'+NS['m']+'}vertex',**{k:format(float(n),'.12g') for k,n in zip('xyz',v)})
                    for f in mask.faces:E.SubElement(mf,'{'+NS['m']+'}triangle',**{k:str(int(n)) for k,n in zip(('v1','v2','v3'),f)})
                    extra_resources[mask_path]=E.tostring(mask_model,encoding='utf-8',xml_declaration=True)
                    mc=E.SubElement(resource.find('m:components',NS),'{'+NS['m']+'}component',objectid=mask_id,transform='1 0 0 0 1 0 0 0 1 0 0 0')
                    mc.set(PN+'path','/'+mask_path)
                    part=E.SubElement(obj,'part',id=mask_id,subtype='modifier_part')
                    for k,v in {'name':label,'matrix':'1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1','sparse_infill_density':'100%','sparse_infill_pattern':'zig-zag'}.items():E.SubElement(part,'metadata',key=k,value=v)
                    E.SubElement(part,'mesh_stat',face_count=str(len(mask.faces)),edges_fixed='0',degenerate_facets='0',facets_removed='0',facets_reversed='0',backwards_edges='0')
                    new_relationships.append(f' <Relationship Target="/{mask_path}" Id="rel-r15-strap-slot-{mask_id}" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>\n')
            for n in obj.findall('metadata'):
                if n.get('face_count') is not None:n.set('face_count',str(len(faces)+48))
            # The official importer uses unprefixed relationship tag names.
            # Retain the original default namespace instead of ET's ns0 prefix.
            extra_resources['3D/_rels/3dmodel.model.rels']=rels.replace('</Relationships>',''.join(new_relationships)+'</Relationships>').encode()
        for plate in cfg.findall('plate'):
            for n in plate.findall('metadata'):
                if n.get('key')=='plater_name':n.set('value','R15 inboard straps - 6 pieces - PLA')
        for n in model.findall('m:metadata',NS):
            if n.get('name')=='Title':n.text='Fingerworker R15 inboard-strap mechanical plate'
            if n.get('name')=='Description':n.text='P01 inboard strap slots, no projecting ears; five exact retained R14 parts. H2D0.4 PLA, four walls and20%gyroid; P04 contact orientation and slower P04/P06 surfaces retained. No printer command.'
        settings=json.loads(z.read('Metadata/project_settings.config'))
        settings['print_settings_id']=process['print_settings_id']
        (OUT/'profiles/project_settings_H2D.json').write_text(json.dumps(settings,indent=2)+'\n')
        with zipfile.ZipFile(seed,'w',zipfile.ZIP_DEFLATED) as dest:
            for name in z.namelist():
                if name.startswith('Metadata/') and (name.endswith('.png') or name in ('Metadata/slice_info.config','Metadata/filament_sequence.json')):continue
                if name=='3D/3dmodel.model':data=E.tostring(model,encoding='utf-8',xml_declaration=True)
                elif name==mesh_path:data=E.tostring(sub,encoding='utf-8',xml_declaration=True)
                elif name=='Metadata/model_settings.config':data=E.tostring(cfg,encoding='utf-8',xml_declaration=True)
                elif name=='Metadata/project_settings.config':data=json.dumps(settings,indent=2).encode()
                elif name in extra_resources:data=extra_resources[name]
                else:data=z.read(name)
                dest.writestr(name,data)
            for name,data in extra_resources.items():
                if name not in z.namelist():dest.writestr(name,data)
        layout['baseline_native_mesh_hashes']={name:sha256(z.read(name)).hexdigest() for name in z.namelist() if name.startswith('3D/Objects/')}
    manifest=json.loads((OLD/'profiles/profile-manifest.json').read_text())
    manifest.update(status='PINNED_OFFICIAL_H2D_MACROS_WITH_VERIFIED_R13_PROCESS_REUSED_FOR_R15',
        baseline_native_project=str(baseline.relative_to(ROOT)),baseline_native_project_sha256=sha(baseline),
        process_changes_from_verified_R13='Global process values retained except preset display name. Every object brim removed (no_brim,width0); required supports retained. Four local solid slot-ligament masks are declared in layout.',
        output_profiles={p.name:sha(p) for p in (OUT/'profiles').glob('*.json') if p.name!='profile-manifest.json'})
    (OUT/'profiles/profile-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    for key in ('deadline_local','native_R13_version'):layout.pop(key,None)
    layout.update(status='LOCAL_R15_CANDIDATE_PENDING_SLICE' if args.candidate else 'NATIVE_R15_PENDING_SLICE',
        CAD_source_path=str(cad.relative_to(ROOT)),CAD_source_sha256=sha(cad),native_R15_version=args.version,
        candidate_zero_area_facets_omitted=candidate_zero_area_facets,
        candidate_zero_area_facet_vertices=candidate_zero_area_facet_vertices,
        native_project=stem+'.3mf',seed_path=seed.name,seed_sha256=sha(seed),
        baseline_project=str(baseline.relative_to(ROOT)),baseline_project_sha256=sha(baseline),
        changes='Only P01 geometry replaced by declared R15 source. Other5 meshes, all rotations/XY positions and global process values retained from verified R13 six-piece project. All six object brims removed; required support structures retained and protected speed settings unchanged. Four local100%rectilinear modifiers solidify inboard slot bearing ligaments. Profile display name updated; no deadline assumed.',
        local_density_modifiers=modifiers,modifier_count=len(modifiers),brim_changes=brim_changes,
        strap_print_regions_path=str(args.modifier_config.relative_to(ROOT)),strap_print_regions_sha256=sha(args.modifier_config),
        candidate_orientation='flat' if args.candidate else None,date='2026-11-08')
    layout_path=OUT/('candidate-flat-layout.json' if args.candidate else 'plate-layout.json')
    layout_path.write_text(json.dumps(layout,indent=2)+'\n')
    print(json.dumps({'status':layout['status'],'source_sha256':sha(source),'faces':len(faces),'size_mm':size.tolist(),'seed':str(seed),'seed_sha256':sha(seed)}))

if __name__=='__main__':main()
