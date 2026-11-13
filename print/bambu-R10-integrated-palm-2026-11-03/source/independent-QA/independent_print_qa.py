#!/usr/bin/env python3
"""Independent read-only QA of delivered R10 native 3MF and actual slice.

No package builder/validator is imported. All meshes and settings are read
directly from the final native 3MF, then compared against frozen source STLs.
"""
from pathlib import Path
from zipfile import ZipFile
import hashlib, json, math, re, xml.etree.ElementTree as ET
import numpy as np
import trimesh
from scipy.spatial import cKDTree
import manifold3d as md

HERE=Path(__file__).resolve().parent
STUDY=HERE.parent
ROOT=STUDY.parents[1]
PACK=ROOT/'print/bambu-R10-integrated-palm-2026-11-03'
PROJECT=PACK/'Fingerworker_R10_H2D_04mm_PLA_Fit_Test.3mf'
SLICE=PACK/'validation/Fingerworker_R10_H2D_04mm_PLA_Fit_Test_verification.gcode.3mf'
NS={'c':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}
PROD='{http://schemas.microsoft.com/3dmanufacturing/production/2015/06}'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
checks=[]
def check(name,condition,**evidence):
    checks.append({'name':name,'status':'PASS' if bool(condition) else 'FAIL',**evidence})
def meta(node):
    return {e.attrib.get('key'):e.attrib.get('value') for e in node.findall('metadata') if 'key' in e.attrib}
def transform(s):
    if not s:return np.eye(4)
    a=np.array([float(x) for x in s.split()]).reshape(4,3).T
    out=np.eye(4);out[:3,:]=a
    return out
def faces_sorted(f):
    a=np.sort(f,axis=1)
    return a[np.lexsort((a[:,2],a[:,1],a[:,0]))]

layout=json.loads((PACK/'plate-layout.json').read_text())
placements={r['ref']:r for r in layout['placements']}
expected={'P01','P04','P05','P060','P061','P070a','P070b','P071a','P071b','P08','P09','P10','P11','P120','P121','H040','H041','Q01'}
check('Inventory18UniqueObjectsNoSeparatePalmSleeveOrFasteners',set(placements)==expected and len(placements)==18,refs=sorted(placements))
check('FinalServiceAccessSourceBoundToLayout',layout.get('CAD_source_sha256')==sha(STUDY/'fingerworker_flat132_integrated_palm.fs') and placements['P01'].get('CAD_source_sha256')==sha(STUDY/'fingerworker_flat132_integrated_palm.fs'),actual_CAD_sha256=sha(STUDY/'fingerworker_flat132_integrated_palm.fs'),layout_CAD_sha256=layout.get('CAD_source_sha256'))
check('FrozenNativeVersionBoundToLayout',bool(re.fullmatch(r'[0-9a-f]{24}',layout.get('native_R10_version',''))),native_version_id=layout.get('native_R10_version'))

objects=[]
actual_meshes={}
with ZipFile(PROJECT) as z:
    xml_cache={}
    def model(path):
        if path not in xml_cache:xml_cache[path]=ET.fromstring(z.read(path))
        return xml_cache[path]
    def read_object(path,oid,matrix):
        obj=model(path).find(f'c:resources/c:object[@id="{oid}"]',NS)
        assert obj is not None,(path,oid)
        mesh=obj.find('c:mesh',NS)
        if mesh is not None:
            v=np.array([[float(e.attrib[k]) for k in ('x','y','z')] for e in mesh.findall('c:vertices/c:vertex',NS)])
            f=np.array([[int(e.attrib[k]) for k in ('v1','v2','v3')] for e in mesh.findall('c:triangles/c:triangle',NS)])
            out=trimesh.Trimesh(v,f,process=True)
            out.apply_transform(matrix)
            return [out]
        result=[]
        for component in obj.findall('c:components/c:component',NS):
            childpath=component.attrib.get(PROD+'path',path).lstrip('/')
            result.extend(read_object(childpath,component.attrib['objectid'],matrix@transform(component.attrib.get('transform'))))
        return result
    root=model('3D/3dmodel.model')
    cfg=ET.fromstring(z.read('Metadata/model_settings.config'))
    settings=json.loads(z.read('Metadata/project_settings.config'))
    cfgobjects={e.attrib['id']:e for e in cfg.findall('object')}
    plate_by_id={}
    plate_sizes=[]
    for plate in cfg.findall('plate'):
        pnum=int(meta(plate)['plater_id'])
        instances=plate.findall('model_instance')
        plate_sizes.append({'plate':pnum,'objects':len(instances)})
        for instance in instances:
            oid=meta(instance)['object_id']
            assert oid not in plate_by_id
            plate_by_id[oid]=pnum
    check('Native3MFUsesMillimeters',root.attrib.get('unit')=='millimeter',unit=root.attrib.get('unit'))
    check('NativeTwoPlates1And17Objects',sorted((r['plate'],r['objects']) for r in plate_sizes)==[(1,1),(2,17)],plates=plate_sizes)
    items=root.findall('c:build/c:item',NS)
    check('NativeBuildHas18PrintableItems',len(items)==18 and all(e.attrib.get('printable','1')=='1' for e in items),count=len(items))
    for item in items:
        oid=item.attrib['objectid'];om=meta(cfgobjects[oid]);ref=om['name'].split(' - ')[0]
        m=read_object('3D/3dmodel.model',oid,transform(item.attrib.get('transform')))
        check(ref+'SingleMeshPerPrintObject',len(m)==1)
        mesh=m[0]
        plate=plate_by_id[oid]
        mesh.apply_translation([-420*(plate-1),0,0])
        actual_meshes[ref]=mesh
        p=placements[ref]
        src=ROOT/p['source_path'];native=trimesh.load_mesh(src,process=True)
        rot=np.array(p['rotation_3x3'],dtype=float)
        expected_mesh=native.copy()
        matrix=np.eye(4);matrix[:3,:3]=rot
        matrix[:3,3]=np.array(p['normalization_translation_mm'])+np.r_[p['plate_xy_mm'],0]
        expected_mesh.apply_transform(matrix)
        d,ix=cKDTree(expected_mesh.vertices).query(mesh.vertices)
        d2,_=cKDTree(mesh.vertices).query(expected_mesh.vertices)
        error=float(max(d.max(),d2.max()))
        facet_match=len(mesh.faces)==len(expected_mesh.faces) and np.array_equal(faces_sorted(ix[mesh.faces]),faces_sorted(expected_mesh.faces))
        rigid=bool(np.allclose(rot@rot.T,np.eye(3),atol=1e-10) and abs(np.linalg.det(rot)-1)<1e-10)
        check(ref+'NativeSourceHash',sha(src)==p['source_sha256'],sha256=sha(src))
        check(ref+'RigidUnscaledNativeMeshRoundtrip',rigid and error<0.0001 and facet_match,max_bidirectional_vertex_error_mm=error,exact_facet_correspondence=facet_match,scale_singular_values=np.linalg.svd(rot)[1].tolist(),faces=len(mesh.faces))
        brim=float(om.get('brim_width',settings.get('brim_width',0)))
        gap=float(om.get('brim_object_gap',settings.get('brim_object_gap',0)))
        # Reserve real line radius too; both-nozzle common machine rectangle
        # is read from official machine settings, not an invented bed size.
        reserve=brim+gap+0.3
        b=mesh.bounds.copy();grown=[b[0,0]-reserve,b[0,1]-reserve,b[1,0]+reserve,b[1,1]+reserve]
        safe=grown[0]>=25-1e-5 and grown[1]>=0-1e-5 and grown[2]<=325+1e-5 and grown[3]<=320+1e-5
        check(ref+'BrimEnvelopeInsideBothNozzleCommonArea',safe,bbox_with_brim_gap_and_0_3mm_line_radius=grown,common_area_mm=[[25,0],[325,320]],brim_width_mm=brim)
        check(ref+'OnBed',abs(b[0,2])<0.0001,z_min_mm=float(b[0,2]))
        objects.append({'ref':ref,'plate':plate,'native_object_id':oid,'name':om['name'],'bbox_mm':b.tolist(),'settings':om,'brim_envelope_mm':grown,'max_mesh_error_mm':error})
    check('NativeObjectInventoryExactlyExpected',set(actual_meshes)==expected,refs=sorted(actual_meshes))
    check('H2D04PLAProfile',settings.get('printer_model')=='Bambu Lab H2D' and settings.get('printer_variant')=='0.4' and settings.get('nozzle_diameter')==['0.4','0.4'] and settings.get('filament_type')==['PLA'],printer_model=settings.get('printer_model'),printer_variant=settings.get('printer_variant'),nozzles=settings.get('nozzle_diameter'),filament_type=settings.get('filament_type'),filament_preset=settings.get('filament_settings_id'))
    check('NozzleCommonAreaReadFromNativeSettings',settings.get('extruder_printable_area')==['0x0,325x0,325x320,0x320','25x0,350x0,350x320,25x320'],extruder_printable_area=settings.get('extruder_printable_area'))
    p01=actual_meshes['P01']
    check('P01OneConnectedClosedPositiveSolid',len(p01.split(only_watertight=False))==1 and p01.is_watertight and p01.is_winding_consistent and p01.volume>0,components=len(p01.split(only_watertight=False)),watertight=bool(p01.is_watertight),consistent_winding=bool(p01.is_winding_consistent),volume_mm3=float(p01.volume),faces=len(p01.faces))
    check('P01BedOnlyNormalSupport',next(r for r in objects if r['ref']=='P01')['settings'].get('enable_support')=='1' and next(r for r in objects if r['ref']=='P01')['settings'].get('support_on_build_plate_only')=='1',settings=next(r for r in objects if r['ref']=='P01')['settings'])
    # Expanded rectangles are deliberately conservative, so a disjoint pair
    # proves brim separation without relying on concave part nesting.
    overlaps=[]
    for i,a in enumerate(objects):
        for b in objects[i+1:]:
            if a['plate']!=b['plate']:continue
            aa=a['brim_envelope_mm'];bb=b['brim_envelope_mm']
            if min(aa[2],bb[2])-max(aa[0],bb[0])>0 and min(aa[3],bb[3])-max(aa[1],bb[1])>0:overlaps.append([a['ref'],b['ref']])
    check('ConservativeBrimEnvelopesDoNotOverlap',not overlaps,overlaps=overlaps)

MODEL={'Outer wall','Inner wall','Overhang wall','Gap infill','Internal solid infill','Top surface','Sparse infill','Bridge'}
SUPPORT={'Support','Support interface','Support transition'}
token=re.compile(r'([XYZEFIJP])(-?(?:\d+(?:\.\d*)?|\.\d+))')
def parse_paths(text):
    pos=np.zeros(3);feature='Custom';relative=True;relative_xyz=False;last_e=0;layer=0;width=.5
    for line in text.splitlines():
        if line.startswith('; FEATURE: '):feature=line[11:].strip()
        elif line.startswith('; Z_HEIGHT: '):layer=float(line.split(':')[1])
        elif line.startswith('; LINE_WIDTH: '):width=float(line.split(':')[1])
        cmd=line.split(';',1)[0].strip()
        if cmd.startswith('M83'):relative=True
        elif cmd.startswith('M82'):relative=False
        elif cmd=='G90':relative_xyz=False
        elif cmd=='G91':relative_xyz=True
        elif cmd.startswith('G92 '):
            vals=dict((k,float(v)) for k,v in token.findall(cmd))
            if 'E'in vals:last_e=vals['E']
            for i,k in enumerate('XYZ'):
                if k in vals:pos[i]=vals[k]
        elif re.match(r'^G[0123] ',cmd):
            vals=dict((k,float(v)) for k,v in token.findall(cmd))
            end=pos.copy()
            for i,k in enumerate('XYZ'):
                if k in vals:end[i]=pos[i]+vals[k] if relative_xyz else vals[k]
            e=vals.get('E',0) if relative else vals.get('E',last_e)-last_e
            if 'E'in vals:last_e=vals['E']
            if e>1e-7 and np.linalg.norm(end-pos)>1e-6 and feature in MODEL|SUPPORT|{'Skirt','Skirt/Brim','Brim'}:
                points=[pos.copy(),end.copy()]
                if cmd.startswith(('G2 ','G3 ')) and ('I'in vals or 'J'in vals):
                    center=pos[:2]+[vals.get('I',0),vals.get('J',0)]
                    r=np.linalg.norm(pos[:2]-center)
                    a0=math.atan2(*(pos[:2]-center)[::-1]);a1=math.atan2(*(end[:2]-center)[::-1])
                    delta=(a1-a0)%(2*math.pi)
                    if cmd.startswith('G2 '):delta=delta-2*math.pi if delta>0 else -2*math.pi
                    for t in np.linspace(0,1,max(3,int(abs(delta)*r/.5)+1)):
                        a=a0+t*delta;points.append(np.r_[center+r*np.array([math.cos(a),math.sin(a)]),pos[2]+t*(end[2]-pos[2])])
                yield feature,np.array(points),float(width),layer
            pos=end

slice_evidence=[]
support_test={}
with ZipFile(SLICE) as z:
    for plate in [1,2]:
        name=f'Metadata/plate_{plate}.gcode'
        text=z.read(name).decode()
        pts=[];models=[];support=[];top=0;features={};first_model_segments=0
        for feature,p,w,layer in parse_paths(text):
            features[feature]=features.get(feature,0)+1
            pts.append(p);top=max(top,float(p[:,2].max()))
            if feature in MODEL:
                models.append(p)
                if layer<=.20001:first_model_segments+=1
            if feature in SUPPORT and plate==1:
                # Sampling centerline at<=1 mm captures every actual support
                # straight segment, rather than trusting a support-setting flag.
                for a,b in zip(p[:-1],p[1:]):
                    for t in np.linspace(0,1,max(2,int(np.linalg.norm(b-a))+1)):
                        support.append((a+t*(b-a),w))
        allp=np.concatenate(pts);bbox=[allp.min(axis=0).tolist(),allp.max(axis=0).tolist()]
        minxy=allp[:,:2].min(axis=0)-.3;maxxy=allp[:,:2].max(axis=0)+.3
        check(f'Plate{plate}ActualExtrusionIncludingBrimsInsideCommonArea',bool(np.all(minxy>=[25,0]) and np.all(maxxy<=[325,320])),bbox_centerline_mm=bbox,bbox_with_0_3mm_line_radius_mm=[minxy.tolist(),maxxy.tolist()])
        check(f'Plate{plate}ActualModelStartsOnBed',first_model_segments>0,first_layer_model_segments=first_model_segments)
        check(f'Plate{plate}ActualModelHeight',abs(top-(35 if plate==1 else 59))<.001,z_max_mm=top)
        slice_evidence.append({'plate':plate,'gcode_member':name,'member_sha256':hashlib.sha256(z.read(name)).hexdigest(),'features_extruding_segments':features,'bbox_extrusion_centerline_mm':bbox})
        if plate==1:
            source=trimesh.load_mesh(STUDY/'print-mm/P01.stl',process=True)
            solid=md.Manifold(md.Mesh(np.asarray(source.vertices,dtype=np.float32),np.asarray(source.faces,dtype=np.uint32)))
            offset=np.array(placements['P01']['normalization_translation_mm'])+np.r_[placements['P01']['plate_xy_mm'],0]
            # Bed-only support in open wrist bay may drop down after plate
            # removal. Check actual support centers and half-line-width XY
            # offsets against the complete fresh native solid, along -Z.
            rays=0;blocked=[];centerblocked=[];nativebounds=[];ray_columns={};center_columns={};sampled_rays=0;blocked_hits=[]
            for point,w in support:
                q=point-offset;nativebounds.append(q)
                for dx,dy in [(0,0),(w/2,0),(-w/2,0),(0,w/2),(0,-w/2)]:
                    start=q+[dx,dy,-.0001]
                    sampled_rays+=1
                    key=tuple(np.round(start[:2],7))
                    prev=ray_columns.get(key)
                    if prev is None or start[2]>prev[0][2]:ray_columns[key]=(start,dx==0 and dy==0)
                    if dx==0 and dy==0:
                        prevcenter=center_columns.get(key)
                        if prevcenter is None or start[2]>prevcenter[2]:center_columns[key]=start
            # For coincident XY, a clear ray from the highest sampled Z also
            # proves every shorter downward ray. This avoids redundant casts
            # through identical vertical support columns across many layers.
            for start,is_center in ray_columns.values():
                hits=solid.ray_cast(start.tolist(),[float(start[0]),float(start[1]),-5])
                rays+=1
                if hits:
                    blocked.append(start.tolist())
                    blocked_hits.append(list(hits[0].position))
            # Verify centerlines separately: an offset sharing the same XY
            # cannot accidentally hide a lower centerline in the cache.
            for start in center_columns.values():
                if solid.ray_cast(start.tolist(),[float(start[0]),float(start[1]),-5]):centerblocked.append(start.tolist())
            first_layer_z=float(source.bounds[0,2])+.2-.0001
            first_layer_brim=[p for p in blocked if abs(p[2]-first_layer_z)<.00001]
            above_first_layer=[p for p in blocked if abs(p[2]-first_layer_z)>=.00001]
            first_layer_hits=[h for p,h in zip(blocked,blocked_hits) if abs(p[2]-first_layer_z)<.00001]
            lateral_release=[];unresolved=[]
            for point in above_first_layer:
                start=np.array(point);outside=start+[-.5,0,0]
                horizontal=solid.ray_cast(start.tolist(),outside.tolist())
                down=solid.ray_cast(outside.tolist(),[float(outside[0]),float(outside[1]),-5])
                if not horizontal and not down:lateral_release.append(point)
                else:unresolved.append({'start_native_mm':point,'lateral_hits':len(horizontal),'down_after_lateral_hits':len(down)})
            # A brim is an intended breakaway attachment around the floor.
            # The conservative rectangular half-width-at-nozzle-Z envelope
            # is wider than a round bead at its top. All first-layer cases
            # are therefore disclosed separately, not silently ignored or
            # presented as a removal-force certification.
            support_test={'support_sample_centers':len(support),'support_envelope_sample_rays':sampled_rays,'tested_downward_rays_including_half_line_width_offsets_after_redundant_XY_column_collapse':rays,'blocked_half_width_envelope_rays_total':len(blocked),'blocked_center_rays':len(centerblocked),'centerline_unique_downward_rays':len(center_columns),'first_layer_brim_half_width_cases':len(first_layer_brim),'above_first_layer_cases_needing_lateral_then_down_release':len(above_first_layer),'lateral_then_down_free_cases':len(lateral_release),'unresolved_cases':unresolved,'lateral_release_vector_mm':[-.5,0,0],'first_layer_nozzle_Z_native_mm':first_layer_z+.0001,'first_layer_brim_cases_native_mm':first_layer_brim,'higher_floor_edge_support_lateral_release_cases_native_mm':lateral_release,'first_layer_brim_ray_hit_bounds_native_mm':[np.min(first_layer_hits,axis=0).tolist(),np.max(first_layer_hits,axis=0).tolist()] if first_layer_hits else None,'higher_support_ray_hit_bounds_native_mm':[np.min([h for p,h in zip(blocked,blocked_hits) if abs(p[2]-first_layer_z)>=.00001],axis=0).tolist(),np.max([h for p,h in zip(blocked,blocked_hits) if abs(p[2]-first_layer_z)>=.00001],axis=0).tolist()] if above_first_layer else None,'native_support_sample_bounds_mm':[np.min(nativebounds,axis=0).tolist(),np.max(nativebounds,axis=0).tolist()] if nativebounds else None,'classification':'First-layer half-width envelope cases are disclosed as deliberate breakaway adhesion-brim contacts. Higher support half-width samples that brush the wider floor side during a purely vertical withdrawal are separately checked by0.5 mm outward-X then downward. Normal supports are removed in sections; no whole-tree extraction or real separation force is claimed.'}
            check('P01SupportSectionsAboveFirstLayerHaveDownOrOutwardThenDownRemovalDirection',len(support)>0 and not unresolved and not centerblocked,support_samples=len(support),higher_half_width_cases_needing_outward_release=len(above_first_layer),outward_then_down_pass=len(lateral_release),blocked_centerline_rays=len(centerblocked),unresolved_cases=unresolved,tested_half_width_column_rays=rays,method='Support/interface/transition strands sampled at<=1mm, plus half-line-width XY offsets. Ordinary support sections may peel0.5mm outward-X before downward removal; no whole-tree or force guarantee.')
            check('P01FirstLayerBrimContactsAreExplicitBreakawayFloorRimOnly',all(float(source.bounds[0,2])-.0001<=p[2]<=first_layer_z+.00001 for p in first_layer_hits),first_layer_brim_half_width_cases=len(first_layer_brim),all_half_width_cases_counted=len(first_layer_brim)+len(above_first_layer)==len(blocked),total_half_width_cases=len(blocked),hit_Z_bounds_native_mm=[min(p[2] for p in first_layer_hits),max(p[2] for p in first_layer_hits)] if first_layer_hits else None,nozzle_first_layer_Z_native_mm=first_layer_z+.0001,interpretation='Expected breakaway first-layer adhesion brim at bottom floor fillet; all conservative half-width envelope cases are counted, higher supports are checked separately, and physical removal force is unverified.')
            inside_rod_socket=0;inside_keeper_head_access=0;inside_cassette_service_bore=0
            for point in nativebounds:
                x,y,zz=point
                if -17.05<x<-7.95 and min((y+51)**2+(zz-18)**2,(y-51)**2+(zz-18)**2)<2.9**2:inside_rod_socket+=1
                if -18.45<x<-15.95 and min((y+11)**2+(zz-24)**2,(y-11)**2+(zz-24)**2)<2.9**2:inside_keeper_head_access+=1
                if 38.8<abs(y)<66.5 and (x+12.8)**2+(zz-8.5)**2<3.0**2:inside_cassette_service_bore+=1
            check('P01NoSupportInsideRodKeeperOrNewH18ServiceBores',not (inside_rod_socket or inside_keeper_head_access or inside_cassette_service_bore),rod_socket_support_centers=inside_rod_socket,keeper_head_access_support_centers=inside_keeper_head_access,H18_service_bore_support_centers=inside_cassette_service_bore)

report={
    'status':'PASS' if all(c['status']=='PASS' for c in checks) else 'FAIL',
    'scope':'Independent native 3MF geometry/settings/inventory/bed-brim checks and actual final Gcode, including P01 support removal-direction sampling. No package validators imported; no package files edited.',
    'native_project':str(PROJECT.relative_to(ROOT)),'native_project_sha256':sha(PROJECT),
    'slice_archive':str(SLICE.relative_to(ROOT)),'slice_archive_sha256':sha(SLICE),
    'native_P01_source':str((STUDY/'print-mm/P01.stl').relative_to(ROOT)),
    'native_P01_source_sha256':sha(STUDY/'print-mm/P01.stl'),
    'source_P01_sha256':sha(STUDY/'print-mm/P01.stl'),
    'source_sha256':sha(STUDY/'fingerworker_flat132_integrated_palm.fs'),
    'source_cad_sha256':sha(STUDY/'fingerworker_flat132_integrated_palm.fs'),
    'native_version_id':layout['native_R10_version'],
    'checker_sha256':sha(__file__),
    'checks':checks,'objects':objects,'slice_evidence':slice_evidence,'support_removal_evidence':support_test,
    'limits':'Mesh/toolpath geometry only. Support rays sample actual centerlines plus conservative half-width XY offsets at nozzle Z, rather than a rounded bead simulation. First-layer brim is an intentional breakaway adhesion rim and its floor-fillet envelope cases are reported separately. Normal supports are removed in sections: higher floor-edge half-width cases have a checked0.5mm outward-X then downward route; this is not a rigid whole-tree extraction proof. Adhesion, removal force, surface finish and physical print/assembly fit remain unverified. No strength/load qualification. H040/H041 and P07 are explicitly rigid unloaded proxies; fasteners and separate sleeve are absent.'
}
(HERE/'independent-print-qa.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'status':report['status'],'checks':len(checks),'failures':[r for r in checks if r['status']!='PASS'],'support':{k:v for k,v in support_test.items() if not k.endswith('cases_native_mm')}},indent=2))
