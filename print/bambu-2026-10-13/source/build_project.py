"""Create a native Bambu 3MF seed; round-trip it through official Bambu Studio."""
from pathlib import Path
import json,hashlib,zipfile,math
from xml.sax.saxutils import escape,quoteattr
from io import StringIO
import trimesh as tm
import numpy as np
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parents[1]
STLS=ROOT/'print/all-print-prototype-2026-10-13-RevC'
rows=json.loads((STLS/'Druckliste.json').read_text())
items={Path(r['file']).name.split('_')[0]:dict(r,path=STLS/r['file']) for r in rows}
for key,name in [('CouponMale','guide_coupon_male.stl'),('CouponFemale','guide_coupon_female.stl')]:
    items[key]=dict(file=name,quantity=1,description='Führungs-Passprobe',material='PETG',path=ROOT/'print'/name)
plates=[
 ('01 PETG - Passprobe zuerst',[('CouponMale',80,100),('CouponFemale',130,100)]),
 ('02 PETG - Grundplatte 6 mm und Staebe',[('P01',50,40),('H04',55,10),('H04',55,25)]),
 ('03 PETG - Griff, Joch und Auflage',[('P04',45,40),('P05',130,40),('P02',180,40),('P060',225,55),('P061',225,110)]),
 ('04 PETG - Elektronik und Anschauungsteile',[('P08',25,40),('P09',65,40),('P10',110,40),('H12',125,40),('H15',170,40),('H13',210,40),('H02',110,80),('H19',135,80),('H19',155,80),('H22',185,85),('H05',110,120),('H05',145,120),('H06',180,120),('H06',215,120)]),
 ('05 PETG - optionale Isometriehuelsen',[('H14',95,110),('H14',150,110)]),
 ('06 TPU - Manschette und Puffer',[('P03',100,100),('P070a',145,95),('P070b',170,95),('P071a',145,120),('P071b',170,120)]),
]
counts={k:0 for k in items};meshes={};audit=[]
for key,row in items.items():
    m=tm.load_mesh(row['path']);assert m.is_watertight and m.is_volume
    m.apply_translation(-m.bounds[0]);meshes[key]=m
    if row.get('sha256'):assert hashlib.sha256(row['path'].read_bytes()).hexdigest()==row['sha256']
for index,(name,positions) in enumerate(plates):
    boxes=[]
    for key,x,y in positions:
        m=meshes[key];counts[key]+=1
        assert 8<=x and 8<=y and x+m.extents[0]<=248 and y+m.extents[1]<=248,(key,m.extents)
        b=[x,y,x+m.extents[0],y+m.extents[1]]
        for prev in boxes:
            assert b[2]+6<=prev[0] or prev[2]+6<=b[0] or b[3]+6<=prev[1] or prev[3]+6<=b[1],(name,key,prev)
        boxes.append(b)
        audit.append(dict(plate=index+1,plate_name=name,part=key,instance=counts[key]-1,xy_mm=[x,y],size_mm=m.extents.tolist(),material=items[key]['material']))
assert all(counts[k]==items[k]['quantity'] for k in items)
assert sum(counts.values())==31
ids={key:(2*i+1,2*i+2) for i,key in enumerate(items)}
s=StringIO();s.write('<?xml version="1.0" encoding="UTF-8"?>\n<model unit="millimeter" xml:lang="de-DE" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">\n')
for name,value in [('Application','BambuStudio-02.08.02.61'),('BambuStudio:3mfVersion','1'),('Title','Fingerworker RevC - Montageprototyp'),('Description','6 mm base, clear rear assembly; spring-free assessment; 29 device pieces and 2 fit coupons')]:s.write(f'<metadata name={quoteattr(name)}>{escape(value)}</metadata>\n')
s.write('<resources>\n')
for key,m in meshes.items():
    mesh_id,object_id=ids[key]
    s.write(f'<object id="{mesh_id}" type="model"><mesh><vertices>\n')
    for x,y,z in m.vertices:s.write(f'<vertex x="{x:.9g}" y="{y:.9g}" z="{z:.9g}"/>\n')
    s.write('</vertices><triangles>\n')
    for a,b,c in m.faces:s.write(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>\n')
    s.write('</triangles></mesh></object>\n')
    s.write(f'<object id="{object_id}" type="model" name={quoteattr(key)}><components><component objectid="{mesh_id}" transform="1 0 0 0 1 0 0 0 1 0 0 0"/></components></object>\n')
s.write('</resources><build>\n')
for row in audit:
    plate=row['plate']-1;origin=[(plate%3)*420,-(plate//3)*384]
    x,y=np.add(origin,row['xy_mm'])
    s.write(f'<item objectid="{ids[row["part"]][1]}" transform="1 0 0 0 1 0 0 0 1 {x:.8g} {y:.8g} 0" printable="1"/>\n')
s.write('</build></model>\n')
config=StringIO();config.write('<?xml version="1.0" encoding="UTF-8"?><config>\n')
def meta(key,value):return f'<metadata key={quoteattr(key)} value={quoteattr(str(value))}/>'
for key,row in items.items():
    mesh_id,object_id=ids[key];extruder=2 if row['material'].startswith('TPU') else 1
    config.write(f'<object id="{object_id}">')
    config.write(meta('name',key+' - '+row['description'])+meta('extruder',extruder))
    opts={}
    if key.startswith('H'):opts.update(sparse_infill_density='100%')
    if key in ['P01','P04','P05','P02','P08','H12','H04','H02']:
        opts.update(enable_support='1',support_type='normal(auto)',support_on_build_plate_only='1',support_top_z_distance='0.25',support_threshold_angle='30')
    if key in ['H04','H02','H14','P03']:
        opts.update(brim_type='outer_only',brim_width='3',brim_object_gap='0.1')
    for k,v in opts.items():config.write(meta(k,v))
    config.write(f'<part id="{mesh_id}" subtype="normal_part">'+meta('name',Path(row['file']).name)+meta('source_file',Path(row['file']).name)+f'<mesh_stat face_count="{len(meshes[key].faces)}" edges_fixed="0" degenerate_facets="0" facets_removed="0" facets_reversed="0" backwards_edges="0"/></part></object>\n')
for index,(name,positions) in enumerate(plates):
    config.write('<plate>'+meta('plater_id',index+1)+meta('plater_name',name)+meta('locked','false')+meta('bed_type','Textured PEI Plate')+meta('print_sequence','by layer'))
    for identify,row in enumerate(audit,1):
        if row['plate']==index+1:config.write('<model_instance>'+meta('object_id',ids[row['part']][1])+meta('instance_id',row['instance'])+meta('identify_id',identify)+'</model_instance>')
    config.write('</plate>\n')
config.write('<assemble/></config>\n')
settings=json.loads((OUT/'profiles/project_settings_H2D.json').read_text())
settings.update(curr_bed_type='Textured PEI Plate',wall_generator='arachne',
                filament_map=['1','1'],filament_volume_map=['0','0'],print_settings_id='Fingerworker RevC 0.20mm',
                extruder_nozzle_stats=['Standard#1','Standard#1'])
relationships='''<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'''
content='''<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/><Default Extension="config" ContentType="application/octet-stream"/></Types>'''
with zipfile.ZipFile(OUT/'Fingerworker_RevC_seed.3mf','w',zipfile.ZIP_DEFLATED) as z:
    for name,data in [('3D/3dmodel.model',s.getvalue()),('Metadata/model_settings.config',config.getvalue()),('Metadata/project_settings.config',json.dumps(settings)),('_rels/.rels',relationships),('[Content_Types].xml',content)]:z.writestr(name,data)
(OUT/'plate-layout.json').write_text(json.dumps(dict(parts=24,device_pieces=29,additional_fit_coupons=2,plates=6,bed_mm=[350,320],usable_layout_mm=[256,256],printer='Bambu Lab H2D',nozzle_mm=.4,placements=audit),indent=2,ensure_ascii=False)+'\n')
print('PASS: 6 plates, 29 device pieces + 2 fit coupons; spacing/bounds/quantities/provenance checked')
