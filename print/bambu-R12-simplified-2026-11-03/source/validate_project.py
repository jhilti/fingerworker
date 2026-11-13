"""Bind editable native meshes, rigid placements and both actual slices to R12."""
from pathlib import Path
from hashlib import sha256
import json,zipfile,xml.etree.ElementTree as E
import numpy as np,trimesh as tm
from scipy.spatial import cKDTree
OUT=Path(__file__).resolve().parents[1];ROOT=OUT.parents[1]
NS={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}
def meta(n):return {i.get('key'):i.get('value') for i in n.findall('metadata') if i.get('key')}
def sha(p):return sha256(p.read_bytes()).hexdigest()
def translation(n):
    a=np.array([float(x) for x in n.get('transform').split()]);assert np.allclose(a[:9],np.eye(3).ravel());return a[9:]
layout=json.loads((OUT/'plate-layout.json').read_text());expected={r['ref']:r for r in layout['placements']}
NATIVE=OUT/layout['native_project'];SLICED=OUT/'validation'/(NATIVE.stem+'_verification.gcode.3mf')
macros=json.loads((OUT/'profiles/profile-manifest.json').read_text())['machine_macro_hashes']
audit=[]
with zipfile.ZipFile(NATIVE) as z:
    assert z.testzip() is None and not any(n.endswith('.gcode') for n in z.namelist())
    cfg=json.loads(z.read('Metadata/project_settings.config'))
    assert cfg['printer_model']=='Bambu Lab H2D' and cfg['nozzle_diameter']==['0.4','0.4']
    assert cfg['filament_type']==['PLA'] and cfg['filament_map']==['1']
    assert cfg['extruder_nozzle_stats']==['Standard#1','Standard#1'] and cfg['curr_bed_type']=='Textured PEI Plate'
    for k,h in macros.items():assert sha256(json.dumps(cfg[k],sort_keys=True).encode()).hexdigest()==h,k
    settings=E.fromstring(z.read('Metadata/model_settings.config'));objects={o.get('id'):o for o in settings.findall('object')}
    assert len(objects)==10
    plates=settings.findall('plate');assert len(plates)==3
    assert [len(p.findall('model_instance')) for p in plates]==[1,8,1]
    refplate={}
    for i,p in enumerate(plates,1):
        for instance in p.findall('model_instance'):refplate[meta(instance)['object_id']]=i
    meshes={}
    for name in z.namelist():
        if name.startswith('3D/Objects/') and name.endswith('.model'):
            d=E.fromstring(z.read(name))
            for o in d.findall('m:resources/m:object',NS):
                m=o.find('m:mesh',NS);v=np.array([[float(v.get(k)) for k in 'xyz'] for v in m.findall('m:vertices/m:vertex',NS)])
                f=np.array([[int(f.get(k)) for k in ('v1','v2','v3')] for f in m.findall('m:triangles/m:triangle',NS)])
                meshes[o.get('id')]=tm.Trimesh(vertices=v,faces=f)
    assert len(meshes)==10
    model=E.fromstring(z.read('3D/3dmodel.model'));wrappers={o.get('id'):o for o in model.findall('m:resources/m:object',NS)}
    build=model.findall('m:build/m:item',NS);assert len(build)==10
    for item in build:
        oid=item.get('objectid');obj=objects[oid];md=meta(obj);key=md['name'].split(' - ')[0];r=expected[key]
        assert md['extruder']=='1' and refplate[oid]==r['plate']
        for k,v in layout['object_settings'][key].items():assert all(x==v for x in md[k].split(',')),(key,k)
        part=obj.find('part');source=tm.load_mesh(ROOT/r['source_path']);native=meshes[part.get('id')]
        assert sha(ROOT/r['source_path'])==r['source_sha256']==sha(OUT/'source-mm'/f'{key}.stl')
        R=np.array(r['rotation_3x3']);assert np.isclose(np.linalg.det(R),1)
        rotated=source.vertices@R.T+np.array(r['normalization_translation_mm'])
        a=native.vertices-native.bounds[0];b=rotated-rotated.min(0)
        err=max(cKDTree(a).query(b)[0].max(),cKDTree(b).query(a)[0].max());assert err<.0001,(key,err)
        assert len(native.faces)==r['faces'] and native.is_watertight and native.is_volume
        if key=='P01':assert native.body_count==source.body_count==1, 'Integrated palm must remain one connected closed mesh'
        assert np.allclose(native.extents,r['size_oriented_mm'],atol=.0001)
        assert abs(native.volume-source.volume)<max(.01,source.volume*1e-5)
        comp=wrappers[oid].find('m:components/m:component',NS)
        p=r['plate']-1;origin=np.array([(p%2)*420,-(p//2)*384,0])
        bbox=native.bounds+translation(comp)+translation(item)-origin
        assert np.allclose(bbox[0],[*r['plate_xy_mm'],0],atol=.0001),(key,bbox)
        assert bbox[0,0]>=27 and bbox[1,0]<=323 and bbox[0,1]>=3 and bbox[1,1]<=317
        stats=part.find('mesh_stat');assert all(int(stats.get(k,'0'))==0 for k in ('edges_fixed','degenerate_facets','facets_removed','facets_reversed','backwards_edges'))
        audit.append(dict(ref=key,plate=r['plate'],source_sha256=r['source_sha256'],mesh_roundtrip_max_error_mm=float(err),bbox_plate_mm=bbox.tolist(),faces=len(native.faces),automatic_repairs=0))
    for name in z.namelist():
        if name.startswith('Metadata/plate_') and name.endswith('.png'):(OUT/'preview'/Path(name).name).write_bytes(z.read(name))
with zipfile.ZipFile(SLICED) as z:
    assert z.testzip() is None
    info=E.fromstring(z.read('Metadata/slice_info.config'));plates=info.findall('plate');assert len(plates)==3
    estimates=[]
    for i,p in enumerate(plates,1):
        md=meta(p);assert md['outside']=='false'
        objects=p.findall('object');assert len(objects)==([1,8,1][i-1])
        assert all(o.get('skipped')=='false' for o in objects)
        assert [f.get('type') for f in p.findall('filament')]==['PLA']
        estimates.append(dict(plate=i,seconds=int(md['prediction']),grams=float(md['weight']),objects=len(objects)))
        assert len(z.read(f'Metadata/plate_{i}.gcode'))>1000
    with zipfile.ZipFile(NATIVE) as n:
        for name in n.namelist():
            if name.startswith('3D/Objects/') and name.endswith('.model'):assert n.read(name)==z.read(name),name
result=dict(status='NATIVE_PROJECT_AND_ALL_THREE_SLICES_PASS',native_project=NATIVE.name,native_sha256=sha(NATIVE),sliced_internal_evidence_sha256=sha(SLICED),
    CAD_source_sha256=layout['CAD_source_sha256'],native_R12_version=layout['native_R12_version'],plate_count=3,object_count=10,estimates=estimates,
    estimated_seconds=sum(x['seconds'] for x in estimates),estimated_grams=sum(x['grams'] for x in estimates),
    mesh_roundtrip=audit,stock_macros_modified=False,machine_macro_hashes=macros,no_printer_transmission=True,
    scope='Mesh identity/rigid placements and three complete slices. Physical fit, support removal and strength require the unloaded print trial.')
(OUT/'validation/native-project-check.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:result[k] for k in ('status','object_count','estimated_seconds','estimated_grams')},indent=2))
