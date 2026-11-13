from pathlib import Path
import json,hashlib
import numpy as np
import trimesh as tm
BASE=Path(__file__).resolve().parents[1]/'flat132-palm-cover-2026-10-23'
OUT=Path(__file__).resolve().parent
proposed={'P01':'Zmin','P02':'Xmax','P04':'Xmax','P05':'Zmin','P060':'Zmin','P061':'Zmin','P08':'Zmin','P09':'Zmax','P10':'Zmin','P11':'Zmax','P120':'Xmin','P121':'Xmin',**{r:'Xmin' for r in ['P070a','P070b','P071a','P071b']}}
rows=[]
for path in sorted((BASE/'print-mm').glob('*.stl')):
 mesh=tm.load_mesh(path,process=True);normal=mesh.face_normals;area=mesh.area_faces;b=mesh.bounds
 orientations=[]
 for i,axis in enumerate('XYZ'):
  for sign,label in[(-1,'min'),(1,'max')]:
   level=b[0 if sign<0 else 1,i]
   on=np.all(np.abs(mesh.triangles[:,:,i]-level)<1e-5,axis=1)&(normal[:,i]*sign>.999999)
   contact=float(area[on].sum());down=normal[:,i]*sign>.9
   elevated=down&~on
   orientations.append({'face_on_bed':axis+label,'flat_contact_area_mm2':contact,
     'elevated_downward_near_horizontal_area_mm2':float(area[elevated].sum()),'print_height_mm':float(mesh.extents[i])})
 rows.append({'ref':path.stem,'native_source':str(path.resolve()),'native_stl_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
  'closed_positive':bool(mesh.is_watertight and mesh.is_volume),'bounds_mm':b.tolist(),'volume_mm3':float(mesh.volume),
  'proposed_face_down':proposed[path.stem],'six_face_orientation_metrics':orientations})
result={'status':'GEOMETRIC_ORIENTATION_REVIEW_NOT_SLICING_OR_STRENGTH_QUALIFICATION',
 'source_revision':'R8','source_sha256':'6099df42e341ff9f5c3439709a23107325d10ef922f616bdcda6fa6ef64d41c1',
 'method':'Native STLs read only; near-horizontal triangle area and planar bottom contact. Overhang area is not an unsupported-area or printability certificate.',
 'parts':rows}
(OUT/'qa-orientation-study.json').write_text(json.dumps(result,indent=2)+'\n')
for r in rows:
 selected=next(x for x in r['six_face_orientation_metrics'] if x['face_on_bed']==r['proposed_face_down'])
 print(r['ref'],r['proposed_face_down'],round(selected['flat_contact_area_mm2'],2),'contact',round(selected['print_height_mm'],3),'height')
