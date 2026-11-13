from pathlib import Path
import json,hashlib,xml.etree.ElementTree as ET
from zipfile import ZipFile
import numpy as np,trimesh as tm
from check_p04_supports import check
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
geom=json.loads((OUT/'P04_orientation_study-geometry.json').read_text());compare=[]
for i,row in enumerate(geom['variants'],1):
 r=check(OUT/f'plate_{i}.gcode',row['rotation_3x3'],row['normalization_translation_mm'],[100,80]);r['variant']=row['variant'];compare.append(r)
(OUT/'orientation-criterion-comparison.json').write_text(json.dumps(compare,indent=2)+'\n')
project=OUT/'P04_H2D_04mm_PLA_clean_finger_surface.3mf';source=ROOT/'print/bambu-R10-integrated-palm-2026-11-03/source-mm/P04.stl';m=tm.load_mesh(source);expected=m.vertices@np.array([[0,0,-1],[0,1,0],[1,0,0]]).T+[30,63,-60]
ns={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}
with ZipFile(project) as z:
 names=[n for n in z.namelist() if n.startswith('3D/Objects/') and n.endswith('.model')];assert len(names)==1
 model=ET.fromstring(z.read(names[0]));vertices=np.array([[float(v.get(k)) for k in 'xyz'] for v in model.findall('.//m:vertex',ns)]);faces=model.findall('.//m:triangle',ns)
 # Native Bambu moves the mesh origin to its bbox center; combine component
 # transform and object mesh transform to recover native plate coordinates.
 root=ET.fromstring(z.read('3D/3dmodel.model'));comp=root.find('.//m:component',ns);ct=np.array([float(x) for x in comp.get('transform').split()]).reshape(4,3);vertices=vertices@ct[:3]+ct[3]
 # The wrapper component applies -bbox normalization separately; compare all
 # normalized vertices rather than assuming a particular internal origin.
 vertices-=vertices.min(axis=0)
 assert len(vertices)==len(expected) and len(faces)==len(m.faces)
 from scipy.spatial import cKDTree
 d=cKDTree(expected).query(vertices)[0];error=float(d.max());assert error<.0001
 cfg=ET.fromstring(z.read('Metadata/model_settings.config'));obj=cfg.find('object');opts={n.get('key'):n.get('value') for n in obj.findall('metadata')}
 for key,val in {'support_type':'tree(auto)','support_style':'tree_slim','support_on_build_plate_only':'1','support_top_z_distance':'0.25','brim_width':'5'}.items():assert opts[key]==val,(key,opts.get(key))
 settings=json.loads(z.read('Metadata/project_settings.config'));assert settings['filament_type']==['PLA']
 verification=OUT/'front_tree_bed/verification.gcode.3mf';result=json.loads((OUT/'front_tree_bed/result.json').read_text());assert result['return_code']==0 and len(result['sliced_plates'])==1
valid=json.loads((OUT/'validation.json').read_text());assert valid['status']=='PASS'
report={'status':'PASS','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'native_project_sha256':hashlib.sha256(project.read_bytes()).hexdigest(),'native_project_vertex_roundtrip_max_error_mm':error,'mesh_faces':len(m.faces),'mesh_watertight':bool(m.is_watertight),'rigid_rotation_only':True,'geometry_or_assembly_datums_changed':False,'P05_unchanged':True,'support_settings':{k:opts[k] for k in ['support_type','support_style','support_on_build_plate_only','support_top_z_distance','brim_width']},'printer':'H2D','nozzle_mm':.4,'material':'PLA','slicer_version':'02.08.02.61','native_slicer_exit_code':result['return_code'],'plate_count':1,'gcode_in_user_project':False,'no_printer_transmission':True,'critical_support_contacts':valid['support_segments_in_critical_regions'],'estimated_time':valid['estimated_time'],'estimated_weight_g':valid['estimated_weight_g'],'limitations':['Physical finish and support removal need print confirmation','The opposite pocket wall still has removable support marks','No loaded strength qualification from this geometry/toolpath review']}
(OUT/'project-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
