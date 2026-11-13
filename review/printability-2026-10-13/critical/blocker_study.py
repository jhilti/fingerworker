"""Local P05 support blocker over the side-open pusher nuttrap and blind bore."""
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import xml.etree.ElementTree as E
import trimesh as tm
OUT=Path(__file__).resolve().parent
NS='http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
E.register_namespace('',NS)
q=lambda n:f'{{{NS}}}{n}'
with ZipFile(OUT/'orientation-study.3mf') as z:data={n:z.read(n) for n in z.namelist()}
model=E.fromstring(data['3D/3dmodel.model']);cfg=E.fromstring(data['Metadata/model_settings.config'])
block=tm.creation.box(extents=[14,6.6,8.1]);block.apply_translation([15,87,11.15])
o=E.SubElement(model.find(q('resources')),q('object'),{'id':'9','type':'model'})
mesh=E.SubElement(o,q('mesh'));verts=E.SubElement(mesh,q('vertices'));tri=E.SubElement(mesh,q('triangles'))
for x,y,z in block.vertices:E.SubElement(verts,q('vertex'),{'x':str(x),'y':str(y),'z':str(z)})
for a,b,c in block.faces:E.SubElement(tri,q('triangle'),{'v1':str(a),'v2':str(b),'v3':str(c)})
holder=next(x for x in model.find(q('resources')).findall(q('object')) if x.attrib['id']=='6')
E.SubElement(holder.find(q('components')),q('component'),{'objectid':'9'})
c=next(x for x in cfg.findall('object') if x.attrib['id']=='6')
part=E.SubElement(c,'part',{'id':'9','subtype':'support_blocker'})
E.SubElement(part,'metadata',{'key':'name','value':'Pusher bore and nuttrap support blocker'})
E.SubElement(part,'mesh_stat',{'face_count':str(len(block.faces)),'edges_fixed':'0','degenerate_facets':'0','facets_removed':'0','facets_reversed':'0','backwards_edges':'0'})
data['3D/3dmodel.model']=E.tostring(model,encoding='utf-8',xml_declaration=True)
data['Metadata/model_settings.config']=E.tostring(cfg,encoding='utf-8',xml_declaration=True)
with ZipFile(OUT/'orientation-study-blocker.3mf','w',ZIP_DEFLATED) as z:
 for n,b in data.items():z.writestr(n,b)
print('P05 blocker local bounding box:',block.bounds.tolist())
