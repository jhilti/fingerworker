#!/usr/bin/env python3
"""Create one full-scale, editable Bambu seed from frozen R8 parts and the Q01 test fixture."""
from pathlib import Path
from hashlib import sha256
from io import StringIO
from xml.sax.saxutils import escape,quoteattr
import json,zipfile
import numpy as np
import trimesh as tm
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parents[1]
R8=ROOT/'review/flat132-palm-cover-2026-10-23'
SOURCE_SHA='6099df42e341ff9f5c3439709a23107325d10ef922f616bdcda6fa6ef64d41c1'
assert sha256((R8/'fingerworker_flat132_palm_cover.fs').read_bytes()).hexdigest()==SOURCE_SHA
I=np.eye(3);RX180=np.diag([1,-1,-1]);RY90=np.array([[0,0,1],[0,1,0],[-1,0,0]]);RYN90=RY90.T;RZ90=np.array([[0,-1,0],[1,0,0],[0,0,1]])
# Positions denote the minimum XY corner of the rigidly oriented model, in millimetres.
plan=[
 ('P01',I,33,9,'Base floor down',5,6),
 ('P02',RY90,199,9,'Native Xmax front-ear plane down; lid-gap face vertical',5,6),
 ('P04',RY90,236.5,9,'Native Xmax rear plane down',5,6),
 ('P05',I,275.5,9,'Native Z up; integral stop undersides on bed',5,6),
 ('P08',RZ90,32,154,'Native Z up; rotated on bed',3,5),
 ('P09',RZ90@RX180,166,152,'Outer lid face down',2,3),
 ('H040',I,30,186.5,'Horizontal native rod axis; rigid shape proxy only',3,3),
 ('H041',I,179,186.5,'Horizontal native rod axis; rigid shape proxy only',3,3),
 ('P060',I,175,203,'Native Z up; no internal supports',3,4),
 ('P061',I,194,203,'Native Z up; no internal supports',3,4),
 ('P120',RYN90,213,203,'Native Xmin shoe front down',3,4),
 ('P121',RYN90,246.2,203,'Native Xmin shoe front down',3,4),
 ('P11',RX180,280,201,'Native Zmax cam-shoe top down; blind pilot bridges without support',2,2),
 ('P10',I,292,201,'Native broad face down',2,2),
 ('P070a',RYN90,280,217.5,'Native Xmin down; rigid PLA thickness proxy',2,2),
 ('P070b',RYN90,292,217.5,'Native Xmin down; rigid PLA thickness proxy',2,2),
 ('P071a',RYN90,280,228,'Native Xmin down; rigid PLA thickness proxy',2,2),
 ('P071b',RYN90,292,228,'Native Xmin down; rigid PLA thickness proxy',2,2),
 ('Q01',I,298,240,'UNLOADED fixture square locator down; supplier print orientation',3,3),
]
assert len(plan)==19
profile=json.loads((OUT/'profiles/project_settings_H2D.json').read_text())
source_manifests=json.loads((R8/'assembly-mm/part-manifest.json').read_text())['parts']
meshes={};items={};audit=[];reserved=[]
for key,R,x,y,orientation,brim,margin in plan:
 assert np.allclose(R.T@R,I) and abs(np.linalg.det(R)-1)<1e-9
 src=R8/('print-mm' if key.startswith('P') else 'assembly-mm')/(key+'.stl')
 if key=='Q01':src=OUT/'fixture/Q01_UNLOADED_TEST_FIXTURE_print-mm.stl'
 blob=src.read_bytes();digest=sha256(blob).hexdigest()
 if key!='Q01':assert digest==source_manifests[key]['output_sha256'],key
 else:assert digest=='4a814328544c999013ab754d2d1c3f9a99e287e034066df127525cfe912a394b'
 m=tm.load_mesh(src);assert m.is_watertight and m.is_volume,(key,'Invalid input mesh')
 original=m.copy();m.vertices=m.vertices@R.T;minimum=m.bounds[0].copy();m.apply_translation(-minimum)
 assert abs(m.volume-original.volume)<max(.001,original.volume*1e-8)
 assert np.allclose(np.sort(m.extents),np.sort(original.extents),atol=1e-7)
 b=[x-margin,y-margin,x+m.extents[0]+margin,y+m.extents[1]+margin]
 assert b[0]>=27-1e-5 and b[1]>=3-1e-5 and b[2]<=323+1e-5 and b[3]<=317+1e-5,(key,b)
 for other,prev in reserved:
  assert b[2]+1.5<=prev[0]+1e-5 or prev[2]+1.5<=b[0]+1e-5 or b[3]+1.5<=prev[1]+1e-5 or prev[3]+1.5<=b[1]+1e-5,(key,other,b,prev)
 reserved.append((key,b));meshes[key]=m
 mock=key.startswith('P07') or key.startswith('H04')
 intent='RIGID PLA SHAPE PROXY - NO LOAD' if mock else 'UNLOADED TEST FIXTURE - NOT A PRODUCTION PART' if key=='Q01' else 'R8 rigid printed part - unloaded fit study'
 row={'ref':key,'source_path':str(src.relative_to(ROOT)),'source_sha256':digest,'source_geometry':'FROZEN_R8_NATIVE_STL' if key!='Q01' else 'SEPARATE_Q01_FIXTURE_PRINT_STL','CAD_source_sha256':SOURCE_SHA if key!='Q01' else None,'material':'PLA','intent':intent,'orientation':orientation,'rotation_3x3':R.tolist(),'normalization_translation_mm':(-minimum).tolist(),'plate_xy_mm':[x,y],'size_oriented_mm':m.extents.tolist(),'brim_mm':brim,'reserved_margin_mm':margin,'reserved_bounds_xy_mm':b,'volume_mm3':float(m.volume),'faces':len(m.faces),'units':'mm','scale':1.0}
 audit.append(row);items[key]=row
 copied=OUT/'source-mm'/(key+'.stl');copied.parent.mkdir(exist_ok=True);copied.write_bytes(blob);assert copied.read_bytes()==blob
ids={key:(2*i+1,2*i+2) for i,key in enumerate(meshes)}
s=StringIO();s.write('<?xml version="1.0" encoding="UTF-8"?>\n<model unit="millimeter" xml:lang="en-US" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">\n')
for name,value in [('Application','BambuStudio-02.08.02.61'),('BambuStudio:3mfVersion','1'),('Title','Fingerworker R8 - one plate unloaded fit test'),('Description','19 full-scale PLA objects. Four hard return-pad proxies and two rod proxies are not functional replacements; Q01 is unloaded test fixture only.')]:s.write(f'<metadata name={quoteattr(name)}>{escape(value)}</metadata>\n')
s.write('<resources>\n')
for key,m in meshes.items():
 mid,oid=ids[key];s.write(f'<object id="{mid}" type="model"><mesh><vertices>\n')
 for x,y,z in m.vertices:s.write(f'<vertex x="{x:.9g}" y="{y:.9g}" z="{z:.9g}"/>\n')
 s.write('</vertices><triangles>\n')
 for a,b,c in m.faces:s.write(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>\n')
 s.write('</triangles></mesh></object>\n');s.write(f'<object id="{oid}" type="model" name={quoteattr(key)}><components><component objectid="{mid}" transform="1 0 0 0 1 0 0 0 1 0 0 0"/></components></object>\n')
s.write('</resources><build>\n')
for row in audit:
 x,y=row['plate_xy_mm'];s.write(f'<item objectid="{ids[row["ref"]][1]}" transform="1 0 0 0 1 0 0 0 1 {x:.8g} {y:.8g} 0" printable="1"/>\n')
s.write('</build></model>\n')
def meta(k,v):return f'<metadata key={quoteattr(k)} value={quoteattr(str(v))}/>'
c=StringIO();c.write('<?xml version="1.0" encoding="UTF-8"?><config>\n')
settings_rows={}
for key,row in items.items():
 mid,oid=ids[key];c.write(f'<object id="{oid}">');c.write(meta('name',key+' - '+row['intent'])+meta('extruder','1'))
 opts={'brim_type':'outer_only','brim_width':str(row['brim_mm']),'brim_object_gap':'0.1','enable_support':'0'}
 if key in ['P01','P02','P04','P05','P060','P061','P08','P120','P121','H040','H041','Q01']:
  opts.update(enable_support='1',support_type='normal(auto)',support_on_build_plate_only='1',support_top_z_distance='0.25',support_threshold_angle='30')
 if key in ['P04','P08','Q01']:opts['support_on_build_plate_only']='0'
 if key.startswith('P07') or key in ['P11','Q01','H040','H041']:opts['sparse_infill_density']='100%'
 if key.startswith('P07') or key=='P11':opts['layer_height']='0.1'
 if key.startswith('P07') or key in ['P10','P11','P060','P061','P120','P121','Q01']:
  opts.update(outer_wall_speed='40',inner_wall_speed='40',top_surface_speed='40',internal_solid_infill_speed='40',gap_infill_speed='40',sparse_infill_speed='40')
 if key in ['H040','H041']:opts.update(outer_wall_speed='60',inner_wall_speed='60',top_surface_speed='60',internal_solid_infill_speed='60',gap_infill_speed='60',sparse_infill_speed='60')
 settings_rows[key]=opts.copy()
 for k,v in opts.items():
  if isinstance(profile.get(k),list):v=','.join([str(v)]*len(profile[k]))
  c.write(meta(k,v))
 c.write(f'<part id="{mid}" subtype="normal_part">'+meta('name',key+'.stl')+meta('source_file',key+'.stl')+f'<mesh_stat face_count="{len(meshes[key].faces)}" edges_fixed="0" degenerate_facets="0" facets_removed="0" facets_reversed="0" backwards_edges="0"/></part></object>\n')
c.write('<plate>'+meta('plater_id',1)+meta('plater_name','R8 FIT ONLY - 19 PLA objects - UNLOADED')+meta('locked','false')+meta('bed_type','Textured PEI Plate')+meta('print_sequence','by layer'))
for identify,row in enumerate(audit,1):c.write('<model_instance>'+meta('object_id',ids[row['ref']][1])+meta('instance_id',0)+meta('identify_id',identify)+'</model_instance>')
c.write('</plate><assemble/></config>\n')
rels='<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'
content='<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/><Default Extension="config" ContentType="application/octet-stream"/></Types>'
seed=OUT/'Fingerworker_R8_H2D_04mm_PLA_FIT_seed.3mf'
with zipfile.ZipFile(seed,'w',zipfile.ZIP_DEFLATED) as z:
 for name,data in [('3D/3dmodel.model',s.getvalue()),('Metadata/model_settings.config',c.getvalue()),('Metadata/project_settings.config',json.dumps(profile)),('_rels/.rels',rels),('[Content_Types].xml',content)]:z.writestr(name,data)
record={'status':'FULL_SCALE_ONE_PLATE_SEED_AUTHORED_PENDING_NATIVE_IMPORT_AND_SLICE','CAD_source_sha256':SOURCE_SHA,'native_R8_version':'6965afcca3af7c58ef3ac73f','slicer_version':'02.08.02.61','printer':'H2D','nozzle_mm':0.4,'material':'PLA','bed':'Textured PEI Plate','plate_count':1,'object_count':19,'rigid_device_P_parts':12,'rigid_pad_proxies':4,'rigid_rod_proxies':2,'unloaded_fixture_count':1,'safe_shared_XY_mm':[[27,3],[323,317]],'native_machine_macros_modified':False,'no_printer_transmission':True,'placements':audit,'object_settings':settings_rows,'seed_path':seed.name,'seed_sha256':sha256(seed.read_bytes()).hexdigest()}
(OUT/'plate-layout.json').write_text(json.dumps(record,indent=2)+'\n');(OUT/'Druckliste.json').write_text(json.dumps(audit,indent=2)+'\n');print(json.dumps({k:record[k] for k in ['status','plate_count','object_count','seed_path','seed_sha256']},indent=2))
