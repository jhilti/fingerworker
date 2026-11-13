#!/usr/bin/env python3
"""Derive a single-piece P02 reprint seed from the full nineteen-piece R9 seed."""
from pathlib import Path
import zipfile,json,xml.etree.ElementTree as E
from hashlib import sha256
OUT=Path(__file__).resolve().parents[1]
NS={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}
CORE=NS['m'];E.register_namespace('',CORE)
seed=OUT/'Fingerworker_R9_H2D_04mm_PLA_FIT_seed.3mf'
layout=json.loads((OUT/'plate-layout.json').read_text())
palm=next(r for r in layout['placements'] if r['ref']=='P02')
with zipfile.ZipFile(seed) as z:files={n:z.read(n) for n in z.namelist()}
model=E.fromstring(files['3D/3dmodel.model']);resources=model.find('m:resources',NS);build=model.find('m:build',NS)
settings=E.fromstring(files['Metadata/model_settings.config'])
objs=settings.findall('object')
palm_obj=next(o for o in objs if any(n.get('key')=='name' and n.get('value','').startswith('P02 - ') for n in o.findall('metadata')))
oid=palm_obj.get('id');mid=palm_obj.find('part').get('id')
for o in list(resources):
 if o.get('id') not in {oid,mid}:resources.remove(o)
for item in list(build):
 if item.get('objectid')!=oid:build.remove(item)
xy=[(350-palm['size_oriented_mm'][0])/2,(320-palm['size_oriented_mm'][1])/2]
build[0].set('transform','1 0 0 0 1 0 0 0 1 '+str(xy[0])+' '+str(xy[1])+' 0')
for o in objs:
 if o!=palm_obj:settings.remove(o)
plate=settings.find('plate')
for m in plate.findall('metadata'):
 if m.get('key')=='plater_name':m.set('value','R9 P02 WRIST DOWN - PLA - UNLOADED FIT')
for i in plate.findall('model_instance'):
 if not any(m.get('key')=='object_id' and m.get('value')==oid for m in i.findall('metadata')):plate.remove(i)
for i in plate.findall('model_instance'):
 for m in i.findall('metadata'):
  if m.get('key')=='identify_id':m.set('value','1')
files['3D/3dmodel.model']=E.tostring(model,encoding='utf-8',xml_declaration=True)
files['Metadata/model_settings.config']=E.tostring(settings,encoding='utf-8',xml_declaration=True)
target=OUT/'Fingerworker_R9_P02_wrist_down_H2D_04mm_PLA_seed.3mf'
with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
 for n,v in files.items():z.writestr(n,v)
(OUT/'palm-only-layout.json').write_text(json.dumps({'scope':'P02 only reprint convenience; same exact mesh/settings as full R9 project','ref':'P02','source_sha256':palm['source_sha256'],'main_seed_sha256':sha256(seed.read_bytes()).hexdigest(),'seed_sha256':sha256(target.read_bytes()).hexdigest(),'plate_xy_mm':xy,'size_oriented_mm':palm['size_oriented_mm'],'settings':layout['object_settings']['P02'],'scale':1},indent=2)+'\n')
print(target.name)
