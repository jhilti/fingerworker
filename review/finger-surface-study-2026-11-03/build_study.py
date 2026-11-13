from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
from xml.sax.saxutils import quoteattr
import numpy as np,trimesh as tm,json,hashlib,sys
front_only="--front-only" in sys.argv
STEM="P04_front_down_H2D_04mm_PLA" if front_only else "P04_orientation_study"
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
src=ROOT/'print/bambu-R10-integrated-palm-2026-11-03/source-mm/P04.stl'
source=tm.load_mesh(src)
I=np.eye(3);RY90=np.array([[0,0,1],[0,1,0],[-1,0,0]]);RX90=np.array([[1,0,0],[0,0,-1],[0,1,0]])
variants=[('front_down',RY90.T)] if front_only else [('rear_down',RY90),('front_down',RY90.T),('pocket_up',I),('side_down',RX90)]
model=['<?xml version="1.0" encoding="UTF-8"?>','<model unit="millimeter" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02"><metadata name="Application">BambuStudio-02.08.02.61</metadata><metadata name="BambuStudio:3mfVersion">1</metadata><resources>']
cfg=['<?xml version="1.0" encoding="UTF-8"?><config>'];rows=[]
def meta(k,v):return f'<metadata key={quoteattr(k)} value={quoteattr(str(v))}/>'
for i,(name,R) in enumerate(variants):
 m=source.copy();m.vertices=m.vertices@R.T;minimum=m.bounds[0].copy();m.apply_translation(-minimum);m.export(OUT/f'P04_{name}.stl')
 mid,oid=2*i+1,2*i+2
 model.append(f'<object id="{mid}" type="model"><mesh><vertices>');model.extend(f'<vertex x="{x:.9g}" y="{y:.9g}" z="{z:.9g}"/>' for x,y,z in m.vertices);model.append('</vertices><triangles>');model.extend(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a,b,c in m.faces);model.append(f'</triangles></mesh></object><object id="{oid}" type="model" name="P04_{name}"><components><component objectid="{mid}"/></components></object>')
 opts={'name':f'P04_{name}','extruder':1,'enable_support':1,'support_type':'normal(auto)','support_threshold_angle':30,'support_on_build_plate_only':0,'support_top_z_distance':.25,'brim_type':'outer_only','brim_width':5,'brim_object_gap':.1}
 cfg.append(f'<object id="{oid}">'+''.join(meta(k,v) for k,v in opts.items())+f'<part id="{mid}" subtype="normal_part">'+meta('name',f'P04_{name}.stl')+f'<mesh_stat face_count="{len(m.faces)}" edges_fixed="0" degenerate_facets="0" facets_removed="0" facets_reversed="0" backwards_edges="0"/></part></object>')
 cfg.append('<plate>'+meta('plater_id',i+1)+meta('plater_name',f'P04_{name}')+meta('locked','false')+meta('bed_type','Textured PEI Plate')+meta('print_sequence','by layer')+'<model_instance>'+meta('object_id',oid)+meta('instance_id',0)+meta('identify_id',i+1)+'</model_instance></plate>')
 down=source.face_normals@R.T
 handmask=(source.triangles_center[:,0]>=70)&(source.triangles_center[:,0]<=108)&(abs(source.triangles_center[:,1])<38)&(source.triangles_center[:,2]>8)
 rows.append({'variant':name,'rotation_3x3':R.tolist(),'normalization_translation_mm':(-minimum).tolist(),'extent_mm':m.extents.tolist(),'volume_mm3':m.volume,'bed_contact_area_mm2':float(m.area_faces[(m.triangles[:,:,2].max(axis=1)<1e-5)].sum()),'hand_region_downward_area_mm2':float(source.area_faces[handmask&(down[:,2]<-.5)].sum()),'mesh_watertight':bool(m.is_watertight)})
cfg.append('<assemble/></config>');model.append('</resources><build>')
for i in range(len(variants)):model.append(f'<item objectid="{2*i+2}" transform="1 0 0 0 1 0 0 0 1 {100+420*(i%2)} {80-384*(i//2)} 0" printable="1"/>')
model.append('</build></model>')
with ZipFile(ROOT/'print/bambu-R10-integrated-palm-2026-11-03/Fingerworker_R10_H2D_04mm_PLA_Fit_Test_seed.3mf') as z:extras={n:z.read(n) for n in ['_rels/.rels','[Content_Types].xml','Metadata/project_settings.config']}
with ZipFile(OUT/(STEM+'_seed.3mf'),'w',ZIP_DEFLATED) as z:
 for n,data in {**extras,'3D/3dmodel.model':'\n'.join(model),'Metadata/model_settings.config':'\n'.join(cfg)}.items():z.writestr(n,data)
(OUT/(STEM+'-geometry.json')).write_text(json.dumps({'source':str(src),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'variants':rows},indent=2))
print(json.dumps(rows,indent=2))
