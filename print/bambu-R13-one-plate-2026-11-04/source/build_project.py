"""Reposition the exact checked R13 native meshes onto one H2D plate."""
from pathlib import Path
from hashlib import sha256
import copy,json,shutil,xml.etree.ElementTree as E,zipfile

OUT=Path(__file__).resolve().parents[1];ROOT=OUT.parents[1]
OLD=ROOT/'print/bambu-R13-simple-palm-2026-11-03'
BASE='Fingerworker_R13_H2D_04mm_PLA_One_Plate'
NS={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}
E.register_namespace('',NS['m']);E.register_namespace('p','http://schemas.microsoft.com/3dmanufacturing/production/2015/06')
sha=lambda p:sha256(p.read_bytes()).hexdigest()
meta=lambda e:{m.get('key'):m.get('value') for m in e.findall('metadata')}
positions={'P01':[35,22],'P05':[226,22],'P04':[283,22],
 'P08':[35,180],'P09':[195,180],'P06':[40,225],
 'H040':[35,275],'H041':[35,300],'Q01':[210,230],'P11':[255,230]}
margins={'P01':7,'P05':7,'P04':8,'P08':5,'P09':5,'P06':6,'H040':5,'H041':5,'Q01':5,'P11':4}
for folder in ('profiles','source-mm','STL-print-oriented','preview','runtime','validation'):(OUT/folder).mkdir(parents=True,exist_ok=True)
for p in (OLD/'profiles').iterdir():shutil.copyfile(p,OUT/'profiles'/p.name)
prior=json.loads((OLD/'plate-layout.json').read_text());layout=copy.deepcopy(prior)
baseline=OLD/prior['native_project'];records={r['ref']:r for r in prior['placements']}
reserved=[]
for r in layout['placements']:
 key=r['ref'];x,y=positions[key];sx,sy,_=r['size_oriented_mm'];margin=margins[key]
 bounds=[x-margin,y-margin,x+sx+margin,y+sy+margin]
 assert bounds[0]>=27 and bounds[1]>=3 and bounds[2]<=323 and bounds[3]<=317,(key,bounds)
 for other,b in reserved:
  assert bounds[2]+1.5<=b[0] or b[2]+1.5<=bounds[0] or bounds[3]+1.5<=b[1] or b[3]+1.5<=bounds[1],(key,other)
 reserved.append((key,bounds));r.update(plate=1,plate_xy_mm=positions[key],reserved_margin_mm=margin,reserved_bounds_xy_mm=bounds)
 for folder in ('source-mm','STL-print-oriented'):shutil.copyfile(OLD/folder/(key+'.stl'),OUT/folder/(key+'.stl'))
with zipfile.ZipFile(baseline) as z:
 model=E.fromstring(z.read('3D/3dmodel.model'));config=E.fromstring(z.read('Metadata/model_settings.config'))
 model.set('xmlns:BambuStudio','http://schemas.bambulab.com/package/2021')
 objects={o.get('id'):meta(o)['name'].split(' - ')[0] for o in config.findall('object')}
 for item in model.findall('m:build/m:item',NS):
  key=objects[item.get('objectid')];r=records[key];a=[float(v) for v in item.get('transform').split()]
  p=r['plate']-1;origin=[(p%2)*420,-(p//2)*384]
  for i in (0,1):a[9+i]+=positions[key][i]-r['plate_xy_mm'][i]-origin[i]
  item.set('transform',' '.join(format(v,'.12g') for v in a))
 for node in model.findall('m:metadata',NS):
  if node.get('name')=='Title':node.text='Fingerworker R13 - all ten pieces on one H2D plate'
  if node.get('name')=='Description':node.text='One plate, by-layer PLA print. Exact checked R13 meshes and object settings; only XY locations and plate membership changed. Includes three unloaded fit aids.'
  if node.get('name') in ('CreationDate','ModificationDate'):node.text='2026-11-04'
 instances=[copy.deepcopy(i) for p in config.findall('plate') for i in p.findall('model_instance')]
 for p in config.findall('plate'):config.remove(p)
 plate=E.SubElement(config,'plate')
 for k,v in {'plater_id':'1','plater_name':'R13 - all 10 pieces - PLA','locked':'false','bed_type':'Textured PEI Plate','print_sequence':'by layer'}.items():E.SubElement(plate,'metadata',key=k,value=v)
 for i in sorted(instances,key=lambda i:int(meta(i)['identify_id'])):plate.append(i)
 seed=OUT/(BASE+'_seed.3mf')
 with zipfile.ZipFile(seed,'w',zipfile.ZIP_DEFLATED) as dest:
  for name in z.namelist():
   if name.startswith('Metadata/') and (name.endswith('.png') or name in ('Metadata/slice_info.config','Metadata/filament_sequence.json')):continue
   data=E.tostring(model,encoding='utf-8',xml_declaration=True) if name=='3D/3dmodel.model' else E.tostring(config,encoding='utf-8',xml_declaration=True) if name=='Metadata/model_settings.config' else z.read(name)
   dest.writestr(name,data)
  exact_meshes={n:sha256(z.read(n)).hexdigest() for n in z.namelist() if n.startswith('3D/Objects/') and n.endswith('.model')}
layout.update(status='ONE_PLATE_SEED_PENDING_NATIVE_IMPORT_AND_SLICE',date='2026-11-04',plate_count=1,object_count=10,native_project=BASE+'.3mf',seed_path=seed.name,seed_sha256=sha(seed),baseline_project=str(baseline.relative_to(ROOT)),baseline_project_sha256=sha(baseline),baseline_native_mesh_hashes=exact_meshes,changes='XY translations and plate membership only; orientations, source meshes, object settings and profiles retained.',print_sequence='by layer')
(OUT/'plate-layout.json').write_text(json.dumps(layout,indent=2)+'\n')
(OUT/'Druckliste.json').write_text(json.dumps(layout['placements'],indent=2)+'\n')
print(json.dumps({'status':layout['status'],'plate_count':1,'objects':10,'reserved_bounds':reserved},indent=2))
