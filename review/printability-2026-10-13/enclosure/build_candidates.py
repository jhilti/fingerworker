from pathlib import Path
import zipfile,xml.etree.ElementTree as ET,trimesh as tm
OUT=Path(__file__).resolve().parent; ROOT=OUT.parents[2]
ET.register_namespace('', 'http://schemas.microsoft.com/3dmanufacturing/core/2015/02')
ns={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}
source=ROOT/'print/bambu-2026-10-13-RevE/Fingerworker_RevE_seed.3mf'
with zipfile.ZipFile(source) as z:
 data={name:z.read(name) for name in z.namelist()}
model=ET.fromstring(data['3D/3dmodel.model'])
objs=model.find('m:resources',ns);lookup={a.get('id'):a for a in objs}
for obj in objs:
 k=obj.get('name')
 if k in ['P060','P061']:
  child=obj.find('m:components/m:component',ns).get('objectid');mesh=lookup[child].find('m:mesh',ns)
  for a in list(mesh):mesh.remove(a)
  vs=ET.SubElement(mesh,'{'+ns['m']+'}vertices');ts=ET.SubElement(mesh,'{'+ns['m']+'}triangles')
  m=tm.load_mesh(OUT/(k+'_closed_rear_face_on_bed.stl'))
  for v in m.vertices:ET.SubElement(vs,'{'+ns['m']+'}vertex',{k:f'{v[i]:.9g}' for i,k in enumerate(['x','y','z'])})
  for t in m.faces:ET.SubElement(ts,'{'+ns['m']+'}triangle',{k:str(t[i]) for i,k in enumerate(['v1','v2','v3'])})
data['3D/3dmodel.model']=ET.tostring(model,encoding='utf-8',xml_declaration=True)
with zipfile.ZipFile(OUT/'caps_orientation_candidate.3mf','w',zipfile.ZIP_DEFLATED) as z:
 for name,b in data.items():z.writestr(name,b)
print('Candidate native 3MF ready; other objects and settings retained for direct comparison')
