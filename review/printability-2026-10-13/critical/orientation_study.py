"""Isolated four-orientation 3MF experiment; no delivery artifacts are modified."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import json, numpy as np, trimesh as tm
from xml.sax.saxutils import escape, quoteattr
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
STLS=ROOT/'print/all-print-prototype-2026-10-13-RevD/PETG'
NS='http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
variants=[('P04_rear_end_on_bed','P04',90),('P04_front_end_on_bed','P04',-90),('P05_rib_side_on_bed','P05',90),('P05_front_side_on_bed','P05',-90)]
parts=[]
for name,key,angle in variants:
    m=tm.load_mesh(next(STLS.glob(key+'_*.stl')))
    m.apply_transform(tm.transformations.rotation_matrix(np.deg2rad(angle),[0,1,0]))
    m.apply_translation(-m.bounds[0]);m.export(OUT/(name+'.stl'))
    parts.append(m)
model=['<?xml version="1.0" encoding="UTF-8"?>',f'<model unit="millimeter" xmlns="{NS}"><metadata name="Application">BambuStudio-02.08.02.61</metadata><metadata name="BambuStudio:3mfVersion">1</metadata><resources>']
cfg=['<?xml version="1.0" encoding="UTF-8"?><config>']
def meta(k,v):return f'<metadata key={quoteattr(k)} value={quoteattr(str(v))}/>'
for i,((name,key,angle),m) in enumerate(zip(variants,parts)):
    mid,oid=2*i+1,2*i+2
    model.append(f'<object id="{mid}" type="model"><mesh><vertices>')
    model.extend(f'<vertex x="{x:.9g}" y="{y:.9g}" z="{z:.9g}"/>' for x,y,z in m.vertices)
    model.append('</vertices><triangles>');model.extend(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a,b,c in m.faces)
    model.append(f'</triangles></mesh></object><object id="{oid}" type="model" name="{name}"><components><component objectid="{mid}"/></components></object>')
    cfg.append(f'<object id="{oid}">'+meta('name',name)+meta('extruder',1)+meta('enable_support',1)+meta('support_type','normal(auto)')+meta('support_threshold_angle',30)+meta('support_on_build_plate_only',0)+meta('support_top_z_distance',.25)+meta('brim_type','outer_only')+meta('brim_width',5)+meta('brim_object_gap',.1)+f'<part id="{mid}" subtype="normal_part">'+meta('name',name+'.stl')+f'<mesh_stat face_count="{len(m.faces)}" edges_fixed="0" degenerate_facets="0" facets_removed="0" facets_reversed="0" backwards_edges="0"/></part></object>')
for i,(name,_,_) in enumerate(variants):
    cfg.append('<plate>'+meta('plater_id',i+1)+meta('plater_name',name)+meta('locked','false')+meta('bed_type','Textured PEI Plate')+meta('print_sequence','by layer')+'<model_instance>'+meta('object_id',2*i+2)+meta('instance_id',0)+meta('identify_id',i+1)+'</model_instance></plate>')
cfg.append('<assemble/></config>')
model.append('</resources><build>')
for i in range(4):model.append(f'<item objectid="{2*i+2}" transform="1 0 0 0 1 0 0 0 1 {50+420*(i%2)} {40-384*(i//2)} 0" printable="1"/>')
model.append('</build></model>')
settings=json.loads((ROOT/'print/bambu-2026-10-13-RevE/profiles/project_settings_H2D.json').read_text())
settings.update(curr_bed_type='Textured PEI Plate',wall_generator='arachne',filament_map=['1'],filament_volume_map=['0'],extruder_nozzle_stats=['Standard#1','Standard#1'])
with ZipFile(ROOT/'print/bambu-2026-10-13-RevE/Fingerworker_RevE_seed.3mf') as z:
    extras={n:z.read(n) for n in ['_rels/.rels','[Content_Types].xml']}
with ZipFile(OUT/'orientation-study.3mf','w',ZIP_DEFLATED) as z:
    for n,data in {**extras,'3D/3dmodel.model':'\n'.join(model),'Metadata/model_settings.config':'\n'.join(cfg),'Metadata/project_settings.config':json.dumps(settings)}.items():z.writestr(n,data)
print('orientation study created: 4 variants')
