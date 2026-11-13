"""Printability metrics and rigid-only candidate orientations for small mockup parts."""
from pathlib import Path
import json, hashlib, zipfile, xml.etree.ElementTree as E, re,math
import trimesh as tm,numpy as np
from scipy.spatial import cKDTree
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
PACK=ROOT/'print/all-print-prototype-2026-10-13-RevD/PETG'
TARGETS=['H02','H04','H05','H06','H12','H13','H14','H15','H19','H22','P070a','P070b','P071a','P071b']
ROTATIONS={'H02':(-90,[0,1,0]),'H12':(90,[0,1,0]),'H15':(180,[1,0,0])}
OUT.joinpath('candidate').mkdir(exist_ok=True)
def metrics(m):
    contact=np.all(m.triangles[:,:,2]<.001,axis=1)&(m.face_normals[:,2]<-.99999)
    elevated=(m.face_normals[:,2]<-.99999)&(~contact)
    unsupported=(m.face_normals[:,2]<-np.sqrt(.5))&(~contact)
    return dict(size_mm=m.extents.tolist(),bed_contact_area_mm2=float(m.area_faces[contact].sum()),elevated_horizontal_down_area_mm2=float(m.area_faces[elevated].sum()),steeper_than_45deg_overhang_area_mm2=float(m.area_faces[unsupported].sum()),volume_mm3=float(m.volume))
report={}
for key in TARGETS:
 p=next(PACK.glob(key+'_*'));m=tm.load_mesh(p);r=dict(file=str(p.relative_to(ROOT)),source_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),current=metrics(m));report[key]=r
 if key in ROTATIONS:
  deg,axis=ROTATIONS[key];n=m.copy();t=tm.transformations.rotation_matrix(np.radians(deg),axis);n.apply_transform(t);n.apply_translation(-n.bounds[0]);assert abs(m.volume-n.volume)<.01 and n.is_watertight
  dest=OUT/'candidate'/p.name;n.export(dest);r.update(candidate=metrics(n),rotation_degrees=deg,axis=axis,candidate_file=str(dest.relative_to(ROOT)))
 else:
  dest=OUT/'candidate'/p.name;dest.write_bytes(p.read_bytes())
(OUT/'geometry-metrics.json').write_text(json.dumps(report,indent=2)+'\n')

# Build an isolated native seed from the known project XML, with one instance of each type.
z=zipfile.ZipFile(ROOT/'print/bambu-2026-10-13-RevE/Fingerworker_RevE_seed.3mf')
NS={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'};E.register_namespace('',NS['m'])
model=E.fromstring(z.read('3D/3dmodel.model'));settings=E.fromstring(z.read('Metadata/model_settings.config'))
resources=model.find('m:resources',NS);build=model.find('m:build',NS)
ids={}
def md(o):return {e.get('key'):e.get('value') for e in o.findall('metadata')}
for o in settings.findall('object'):
 key=md(o)['name'].split(' - ')[0]
 if key in TARGETS:ids[key]=int(o.get('id'))
 else:settings.remove(o)
for o in list(resources):
 if int(o.get('id')) not in set(ids.values())|{i-1 for i in ids.values()}:resources.remove(o)
for key,oid in ids.items():
 m=tm.load_mesh(next((OUT/'candidate').glob(key+'_*')));obj=resources.find(f'm:object[@id="{oid-1}"]',NS);mesh=obj.find('m:mesh',NS);verts=mesh.find('m:vertices',NS);faces=mesh.find('m:triangles',NS)
 for v in list(verts):verts.remove(v)
 for f in list(faces):faces.remove(f)
 for v in m.vertices:E.SubElement(verts,'{'+NS['m']+'}vertex',{k:f'{val:.9g}' for k,val in zip(['x','y','z'],v)})
 for f in m.faces:E.SubElement(faces,'{'+NS['m']+'}triangle',{k:str(int(val)) for k,val in zip(['v1','v2','v3'],f)})
for p in settings.findall('plate'):settings.remove(p)
for i in list(build):build.remove(i)
p=E.SubElement(settings,'plate')
for k,v in [('plater_id','1'),('plater_name','Small parts candidate'),('locked','false'),('bed_type','Textured PEI Plate'),('print_sequence','by layer')]:E.SubElement(p,'metadata',{'key':k,'value':v})
positions={'H12':(50,30),'H02':(85,30),'H15':(105,30),'H19':(140,30),'H22':(155,30),'H04':(40,90),'H14':(210,30),'H05':(50,150),'H06':(90,150),'H13':(130,150),'P070a':(170,150),'P070b':(190,150),'P071a':(210,150),'P071b':(230,150)}
for i,(key,oid) in enumerate(ids.items(),1):
 x,y=positions[key];E.SubElement(build,'{'+NS['m']+'}item',{'objectid':str(oid),'transform':f'1 0 0 0 1 0 0 0 1 {x} {y} 0','printable':'1'})
 mi=E.SubElement(p,'model_instance')
 for k,v in [('object_id',str(oid)),('instance_id','0'),('identify_id',str(i))]:E.SubElement(mi,'metadata',{'key':k,'value':v})
 obj=settings.find(f'object[@id="{oid}"]')
 opts=dict(brim_type='outer_only',brim_width='3',brim_object_gap='0.1') if key in ['H19','H22'] else {}
 if key=='H12':opts.update(brim_type='outer_only',brim_width='3',brim_object_gap='0.1')
 for k,v in opts.items():
  e=obj.find(f'metadata[@key="{k}"]')
  if e is None:E.SubElement(obj,'metadata',{'key':k,'value':v})
  else:e.set('value',v)
with zipfile.ZipFile(OUT/'Small_candidate_seed.3mf','w',zipfile.ZIP_DEFLATED) as n:
 for fn in z.namelist():
  data=z.read(fn)
  if fn=='3D/3dmodel.model':data=E.tostring(model,encoding='UTF-8',xml_declaration=True)
  elif fn=='Metadata/model_settings.config':data=E.tostring(settings,encoding='UTF-8',xml_declaration=True)
  n.writestr(fn,data)
print('Small parts metrics and rigid candidates generated')
