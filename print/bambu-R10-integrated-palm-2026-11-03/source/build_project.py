#!/usr/bin/env python3
"""Author a full-scale, editable two-plate R10 H2D fit project.

The integrated P01 is a native Onshape export. All other meshes and their
print transforms/settings are byte-preserved from the verified R9 set.
No scaling, mesh union, remeshing or automated mesh repair occurs here.
"""
from pathlib import Path
from hashlib import sha256
from io import StringIO
from xml.sax.saxutils import escape, quoteattr
import argparse, json, zipfile
import numpy as np
import trimesh as tm

ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parents[1]
PREVIOUS=ROOT/'print/bambu-R9-palm-bracing-2026-10-25'
I=np.eye(3)
RY90=np.array([[0,0,1],[0,1,0],[-1,0,0]])
RX90=np.array([[1,0,0],[0,0,-1],[0,1,0]])
ROTATIONS={'flat':I,'wrist':RY90.T,'side':RX90}
BASE='Fingerworker_R10_H2D_04mm_PLA_Fit_Test'

def sha(path): return sha256(path.read_bytes()).hexdigest()
def meta(k,v): return f'<metadata key={quoteattr(k)} value={quoteattr(str(v))}/>'

def build(source, source_cad, native_version, orientation='flat', candidate=False):
    assert source.is_file() and source_cad.is_file()
    profile=json.loads((OUT/'profiles/project_settings_H2D.json').read_text())
    prior=json.loads((PREVIOUS/'plate-layout.json').read_text())
    cad_sha=sha(source_cad)
    (OUT/'source/fingerworker_R10_integrated_palm.fs').write_bytes(source_cad.read_bytes())
    original=tm.load_mesh(source)
    assert original.is_watertight and original.is_volume and original.body_count==1, 'P01 must be ONE continuous closed mesh'
    R=ROTATIONS[orientation]
    new=dict(ref='P01',source_path=str(source.relative_to(ROOT)),source_sha256=sha(source),
        source_geometry='NATIVE_R10_ONSHAPE_STL',CAD_source_sha256=cad_sha,
        material='PLA',intent='INTEGRATED BASE AND SOLID PALM - UNLOADED FIT STUDY',
        orientation={'flat':'Base floor down; palm supports open toward outer wrist edge',
                     'wrist':'Native Xmin wrist side down; candidate only',
                     'side':'Native Ymin side down; candidate only'}[orientation],
        rotation_3x3=R.tolist(),plate=1,plate_xy_mm=[70,80],brim_mm=5,reserved_margin_mm=6)
    plan=[new]
    if not candidate:
        for previous in prior['placements']:
            if previous['ref'] in ('P01','P02'): continue
            r=previous.copy();r['plate']=2
            r['intent']=r['intent'].replace('R9 rigid printed part','R10 unchanged rigid printed part')
            plan.append(r)
    assert len(plan)==(1 if candidate else 18)
    meshes={};reserved={};settings={};audit=[]
    for r in plan:
        key=r['ref'];src=ROOT/r['source_path'];assert sha(src)==r['source_sha256']
        m=tm.load_mesh(src);before=m.copy();R=np.asarray(r['rotation_3x3'])
        assert np.allclose(R.T@R,I) and abs(np.linalg.det(R)-1)<1e-9
        m.vertices=m.vertices@R.T;minimum=m.bounds[0].copy();m.apply_translation(-minimum)
        assert m.is_watertight and m.is_volume
        assert abs(m.volume-before.volume)<max(.001,before.volume*1e-8)
        assert np.allclose(np.sort(m.extents),np.sort(before.extents),atol=1e-7)
        r.update(normalization_translation_mm=(-minimum).tolist(),size_oriented_mm=m.extents.tolist(),
                 volume_mm3=float(m.volume),faces=len(m.faces),units='mm',scale=1.0)
        x,y=r['plate_xy_mm'];margin=r['reserved_margin_mm']
        b=[x-margin,y-margin,x+m.extents[0]+margin,y+m.extents[1]+margin]
        assert b[0]>=27 and b[1]>=3 and b[2]<=323 and b[3]<=317,(key,b)
        for other,prev in reserved.setdefault(r['plate'],[]):
            assert b[2]+1.5<=prev[0]+1e-5 or prev[2]+1.5<=b[0]+1e-5 or b[3]+1.5<=prev[1]+1e-5 or prev[3]+1.5<=b[1]+1e-5,(key,other)
        reserved[r['plate']].append((key,b));r['reserved_bounds_xy_mm']=b
        meshes[key]=m;audit.append(r)
        copied=OUT/'source-mm'/f'{key}.stl';copied.write_bytes(src.read_bytes())
        if key=='P01':
            opts=dict(brim_type='outer_only',brim_width='5',brim_object_gap='0.1',enable_support='1',
                      support_type='normal(auto)',support_on_build_plate_only='1',
                      support_top_z_distance='0.25',support_threshold_angle='30')
        else: opts=prior['object_settings'][key].copy()
        settings[key]=opts
    ids={key:(2*i+1,2*i+2) for i,key in enumerate(meshes)}
    s=StringIO();s.write('<?xml version="1.0" encoding="UTF-8"?>\n<model unit="millimeter" xml:lang="de-DE" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">\n')
    for name,value in [('Application','BambuStudio-02.08.02.61'),('BambuStudio:3mfVersion','1'),('Title','Fingerworker R10 integrated solid palm'),('Description','Integrated P01; no P02, sleeve, palm M4 hardware. Full-scale unloaded fit project; hard pads and rods are proxies.')]:
        s.write(f'<metadata name={quoteattr(name)}>{escape(value)}</metadata>\n')
    s.write('<resources>\n')
    for key,m in meshes.items():
        mid,oid=ids[key];s.write(f'<object id="{mid}" type="model"><mesh><vertices>\n')
        for x,y,z in m.vertices:s.write(f'<vertex x="{x:.9g}" y="{y:.9g}" z="{z:.9g}"/>\n')
        s.write('</vertices><triangles>\n')
        for a,b,c in m.faces:s.write(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>\n')
        s.write('</triangles></mesh></object>\n')
        s.write(f'<object id="{oid}" type="model" name={quoteattr(key)}><components><component objectid="{mid}" transform="1 0 0 0 1 0 0 0 1 0 0 0"/></components></object>\n')
    s.write('</resources><build>\n')
    for r in audit:
        p=r['plate']-1;x,y=np.asarray(r['plate_xy_mm'])+[(p%3)*420,-(p//3)*384]
        s.write(f'<item objectid="{ids[r["ref"]][1]}" transform="1 0 0 0 1 0 0 0 1 {x:.8g} {y:.8g} 0" printable="1"/>\n')
    s.write('</build></model>\n')
    c=StringIO();c.write('<?xml version="1.0" encoding="UTF-8"?><config>\n')
    for r in audit:
        key=r['ref'];mid,oid=ids[key]
        c.write(f'<object id="{oid}">'+meta('name',key+' - '+r['intent'])+meta('extruder','1'))
        for k,v in settings[key].items():
            if isinstance(profile.get(k),list):v=','.join([str(v)]*len(profile[k]))
            c.write(meta(k,v))
        c.write(f'<part id="{mid}" subtype="normal_part">'+meta('name',key+'.stl')+meta('source_file',key+'.stl')+f'<mesh_stat face_count="{len(meshes[key].faces)}" edges_fixed="0" degenerate_facets="0" facets_removed="0" facets_reversed="0" backwards_edges="0"/></part></object>\n')
    for plate in sorted(reserved):
        name='R10 integrated base + solid palm' if plate==1 else 'R10 remaining 17 unchanged R9 fit objects'
        c.write('<plate>'+meta('plater_id',plate)+meta('plater_name',name)+meta('locked','false')+meta('bed_type','Textured PEI Plate')+meta('print_sequence','by layer'))
        for identify,r in enumerate(audit,1):
            if r['plate']==plate:c.write('<model_instance>'+meta('object_id',ids[r['ref']][1])+meta('instance_id',0)+meta('identify_id',identify)+'</model_instance>')
        c.write('</plate>\n')
    c.write('<assemble/></config>\n')
    rels='<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'
    content='<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/><Default Extension="config" ContentType="application/octet-stream"/></Types>'
    suffix=('-candidate-'+orientation) if candidate else ''
    stem=BASE+suffix;seed=OUT/(stem+'_seed.3mf')
    with zipfile.ZipFile(seed,'w',zipfile.ZIP_DEFLATED) as z:
        for name,data in [('3D/3dmodel.model',s.getvalue()),('Metadata/model_settings.config',c.getvalue()),('Metadata/project_settings.config',json.dumps(profile)),('_rels/.rels',rels),('[Content_Types].xml',content)]:z.writestr(name,data)
    record=dict(status='EDITABLE_SEED_AUTHORED_PENDING_NATIVE_IMPORT_AND_SLICE',CAD_source_path=str(source_cad.relative_to(ROOT)),CAD_source_sha256=cad_sha,native_R10_version=native_version,
                slicer_version='02.08.02.61',printer='H2D',nozzle_mm=.4,material='PLA',bed='Textured PEI Plate',
                plate_count=len(reserved),object_count=len(audit),safe_shared_XY_mm=[[27,3],[323,317]],
                native_machine_macros_modified=False,no_printer_transmission=True,placements=audit,object_settings=settings,
                seed_path=seed.name,seed_sha256=sha(seed),native_project=stem+'.3mf',candidate_orientation=orientation if candidate else None)
    target=OUT/('candidate-'+orientation+'-layout.json' if candidate else 'plate-layout.json')
    target.write_text(json.dumps(record,indent=2)+'\n')
    if not candidate:(OUT/'Druckliste.json').write_text(json.dumps(audit,indent=2)+'\n')
    print(json.dumps({k:record[k] for k in ('status','plate_count','object_count','seed_path','seed_sha256')},indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',required=True,type=Path);p.add_argument('--source-cad',required=True,type=Path);p.add_argument('--version',required=True)
    p.add_argument('--orientation',choices=ROTATIONS,default='flat');p.add_argument('--candidate',action='store_true');a=p.parse_args()
    build(a.source.resolve(),a.source_cad.resolve(),a.version,a.orientation,a.candidate)
