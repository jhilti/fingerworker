"""Validate native Bambu import, geometry, quantities and real H2D slicing output."""
from pathlib import Path
from collections import Counter
import json,zipfile,re,hashlib,xml.etree.ElementTree as ET
import numpy as np
import trimesh as tm
from scipy.spatial import cKDTree
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parents[1]
PACK=ROOT/'print/all-print-prototype-2026-10-13-RevD'
NATIVE=OUT/'Fingerworker_RevE_H2D_04mm_PETG.3mf'
SLICED=ROOT/'review/coupon-orientation-2026-10-13/H2D-RevE-verification.gcode.3mf'
NS={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}
def metadata(node):return {n.get('key'):n.get('value') for n in node.findall('metadata') if n.get('key')}
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
rows=json.loads((PACK/'Druckliste.json').read_text())
inputs={Path(r['file']).name:PACK/r['file'] for r in rows}
inputs.update({n:ROOT/'print'/n for n in ['guide_coupon_male.stl','guide_coupon_female.stl']})
with zipfile.ZipFile(NATIVE) as z:
    assert z.testzip() is None
    assert not any(n.endswith('.gcode') for n in z.namelist()),'Deliver an editable project'
    cfg=json.loads(z.read('Metadata/project_settings.config'))
    assert cfg['printer_model']=='Bambu Lab H2D' and cfg['nozzle_diameter']==['0.4','0.4']
    assert cfg['filament_type']==['PETG'] and cfg['filament_map']==['1']
    assert cfg['extruder_nozzle_stats']==['Standard#1','Standard#1']
    settings=ET.fromstring(z.read('Metadata/model_settings.config'))
    objects={o.get('id'):o for o in settings.findall('object')};assert len(objects)==27
    plates=settings.findall('plate');assert len(plates)==6
    meshes={}
    for name in z.namelist():
        if name.startswith('3D/Objects/') and name.endswith('.model'):
            doc=ET.fromstring(z.read(name))
            for o in doc.findall('m:resources/m:object',NS):
                mesh=o.find('m:mesh',NS)
                vertices=np.array([[float(v.get(k)) for k in ['x','y','z']] for v in mesh.findall('m:vertices/m:vertex',NS)])
                faces=np.array([[int(f.get(k)) for k in ['v1','v2','v3']] for f in mesh.findall('m:triangles/m:triangle',NS)])
                meshes[o.get('id')]=tm.Trimesh(vertices=vertices,faces=faces)
    assert len(meshes)==27
    geometry=[]
    for oid,obj in objects.items():
        meta=metadata(obj);assert meta['extruder']=='1'
        if meta['name'].startswith('Coupon'):assert meta['sparse_infill_density']=='100%'
        part=obj.find('part');filename=metadata(part)['source_file']
        source=tm.load_mesh(inputs[filename]);native=meshes[part.get('id')]
        assert native.is_watertight and native.is_volume and len(native.faces)==len(source.faces)
        a=native.vertices-native.bounds[0];b=source.vertices-source.bounds[0]
        distance=cKDTree(b).query(a)[0].max()
        assert len(a)==len(b) and distance<.0001,(filename,distance)
        assert np.allclose(native.extents,source.extents,atol=.0001)
        assert abs(native.volume-source.volume)<max(.01,source.volume*1e-5)
        geometry.append(dict(file=filename,source_sha256=sha(inputs[filename]),mesh_roundtrip_max_error_mm=float(distance)))
    quantities=Counter();instances_per_plate=[]
    for p in plates:
        instances=p.findall('model_instance');instances_per_plate.append(len(instances))
        for i in instances:
            obj=objects[metadata(i)['object_id']];name=metadata(obj.find('part'))['source_file'];quantities[name]+=1
    assert instances_per_plate==[2,3,5,14,2,6]
    assert all(quantities[Path(r['file']).name]==r['quantity'] for r in rows)
    assert quantities['guide_coupon_male.stl']==quantities['guide_coupon_female.stl']==1
    # Check Bambu's centering transforms preserve each authored placement and Z0.
    model=ET.fromstring(z.read('3D/3dmodel.model'))
    wrappers={o.get('id'):o for o in model.findall('m:resources/m:object',NS)}
    actual=[]
    for item in model.findall('m:build/m:item',NS):
        oid=item.get('objectid');component=wrappers[oid].find('m:components/m:component',NS)
        def translation(node):
            a=np.array([float(v) for v in node.get('transform').split()]);assert np.allclose(a[:9],np.eye(3).ravel());return a[9:]
        bbox=meshes[component.get('objectid')].bounds+translation(component)+translation(item)
        assert abs(bbox[0,2])<.0001
        key=metadata(objects[oid])['name'].split(' - ')[0]
        actual.append((key,*bbox[0,:2]))
    expected=[]
    for r in json.loads((OUT/'plate-layout.json').read_text())['placements']:
        i=r['plate']-1;x,y=r['xy_mm'];expected.append((r['part'],x+(i%3)*420,y-(i//3)*384))
    assert len(actual)==len(expected)==32
    for (ka,*a),(kb,*b) in zip(sorted(actual),sorted(expected)):
        assert ka==kb and np.allclose(a,b,atol=.0001),(ka,a,kb,b)
    (OUT/'preview').mkdir(exist_ok=True)
    for i in range(1,7):(OUT/'preview'/f'plate_{i}.png').write_bytes(z.read(f'Metadata/plate_{i}.png'))
log=(ROOT/'review/coupon-orientation-2026-10-13/bambu-H2D-RevE-slice.log').read_text()
returns=re.findall(r'Slicer_Info_Report: plate_id=(\d+), return_code=(\d+)',log)
assert returns==[(str(i),'0') for i in range(6)]
slices=[]
with zipfile.ZipFile(SLICED) as z:
    info=ET.fromstring(z.read('Metadata/slice_info.config'))
    for i,p in enumerate(info.findall('plate'),1):
        meta=metadata(p);assert meta['outside']=='false'
        objects=p.findall('object');assert len(objects)==instances_per_plate[i-1]
        assert all(o.get('skipped')=='false' for o in objects)
        assert all(f.get('type')=='PETG' for f in p.findall('filament'))
        data=z.read(f'Metadata/plate_{i}.gcode').decode()
        labels=set(re.findall(r'; start printing object, unique label id: (\d+)',data))
        assert len(labels)==len(objects)
        slices.append(dict(plate=i,objects_with_toolpaths=len(labels),outside=False,return_code=0,
                           estimated_seconds=int(meta['prediction']),estimated_grams=float(meta['weight'])))
assert len(slices)==6
report=dict(status='PASS',native_project=NATIVE.name,native_sha256=sha(NATIVE),slicer='Bambu Studio 02.08.02.61',
            printer='H2D',nozzle_mm=.4,materials=['PETG'],device_types=25,device_pieces=30,fit_coupons=2,
            plates=6,instances_per_plate=instances_per_plate,mesh_roundtrip=geometry,slices=slices,
            coupon_infill='100%',coupon_orientation='Female channel up; closed back on bed; male unchanged',
            coupon_bridge_validation='slicer-bridge-validation.json',
            estimated_total_seconds=sum(p['estimated_seconds'] for p in slices),estimated_total_grams=sum(p['estimated_grams'] for p in slices),
            assembly_validation_sha256=sha(ROOT/'review/assembly-final-2026-10-13/validation.json'),
            scope='Native import/export, unchanged closed mesh geometry, quantities, placements, all objects sliced; no physical load qualification',
            cli_diagnostics='Stock H2D macros emit Invalid T1001/T65535/T65279 parser diagnostics. All six plate exit codes are zero. Stock macros are preserved.')
(OUT/'validation.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
print('PASS: native H2D/PETG project, 27 unchanged meshes / 32 instances / 6 successfully sliced plates')
