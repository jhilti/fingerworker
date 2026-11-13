"""Properly rotate the P02-only seed onto its wrist ledge for a scoped support comparison."""
from pathlib import Path
from hashlib import sha256
import json,zipfile,xml.etree.ElementTree as E,numpy as np
OUT=Path(__file__).resolve().parents[1];NS={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}
E.register_namespace('',NS['m'])
source=OUT/'Fingerworker_R9_P02_only_H2D_04mm_PLA_seed.3mf'
with zipfile.ZipFile(source) as z:files={n:z.read(n) for n in z.namelist()}
model=E.fromstring(files['3D/3dmodel.model']);verts=model.findall('m:resources/m:object/m:mesh/m:vertices/m:vertex',NS)
a=np.array([[float(v.get(k)) for k in ['x','y','z']] for v in verts]);R=np.diag([-1,1,-1]);assert np.linalg.det(R)==1
b=a@R.T;b-=b.min(0)
for n,v in zip(verts,b):
 for k,x in zip(['x','y','z'],v):n.set(k,format(x,'.12g'))
files['3D/3dmodel.model']=E.tostring(model,encoding='utf-8',xml_declaration=True)
settings=E.fromstring(files['Metadata/model_settings.config'])
for m in settings.findall('plate/metadata'):
 if m.get('key')=='plater_name':m.set('value','R9 P02 WRIST DOWN - PLA SUPPORT COMPARISON')
files['Metadata/model_settings.config']=E.tostring(settings,encoding='utf-8',xml_declaration=True)
target=OUT/'Fingerworker_R9_P02_wrist_down_H2D_04mm_PLA_seed.3mf'
with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
 for n,v in files.items():z.writestr(n,v)
record={'status':'COMPARISON_SEED_AUTHORED','source_seed_sha256':sha256(source.read_bytes()).hexdigest(),'seed_sha256':sha256(target.read_bytes()).hexdigest(),'orientation':'Native Xmin wrist ledge down; new brace bearing faces upward','additional_print_rotation_3x3':R.tolist(),'source_to_print_rotation_3x3':[[0,0,-1],[0,1,0],[1,0,0]],'scale':1,'bounds_mm':[b.min(0).tolist(),b.max(0).tolist()],'supports':'Same normal buildplate-only, brim5'}
(OUT/'palm-wrist-down-layout.json').write_text(json.dumps(record,indent=2)+'\n');print(target.name)
