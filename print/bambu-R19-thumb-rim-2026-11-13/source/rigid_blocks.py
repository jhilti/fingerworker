"""Replace the obsolete crossbar by two native, base-down rear rod blocks.

Called only by build_project after final native P01 has been inserted.  Keeps
all unrelated object meshes, placements and process settings byte-equivalent.
"""
from pathlib import Path
import copy,hashlib,json,uuid,zipfile,xml.etree.ElementTree as E
import numpy as np,trimesh
NS={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'};MN='{'+NS['m']+'}';PN='{http://schemas.microsoft.com/3dmanufacturing/production/2015/06}';RN='{http://schemas.openxmlformats.org/package/2006/relationships}'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
meta=lambda e:{m.get('key'):m.get('value') for m in e.findall('metadata') if m.get('key')}
def replace(seed,layout,native_zip,out,root):
 assert native_zip is not None,'R19 rigid mounts require final native exports; candidate generation is disabled'
 with zipfile.ZipFile(native_zip) as archive:
  members=[n for n in archive.namelist() if n.endswith('.stl')];assert len(members)==94,'Expected final native R19 assembly with94 parts'
  exported={}
  for ref in ('P06L','P06R','P08'):
   selected=[n for n in members if ' - '+ref+' ' in n];assert len(selected)==1,(ref,selected);exported[ref]=(selected[0],archive.read(selected[0]))
 with zipfile.ZipFile(seed) as z:payload={n:z.read(n) for n in z.namelist()}
 model=E.fromstring(payload['3D/3dmodel.model']);cfg=E.fromstring(payload['Metadata/model_settings.config']);rels=E.fromstring(payload['3D/_rels/3dmodel.model.rels'])
 model.set('xmlns:BambuStudio','http://schemas.bambulab.com/package/2021')
 resources=model.find('m:resources',NS);build=model.find('m:build',NS);plate=cfg.find('plate');assemble=cfg.find('assemble')
 old_cfg=next(o for o in cfg.findall('object') if meta(o)['name'].startswith('P06 - '));oid=old_cfg.get('id')
 old_obj=next(o for o in resources.findall('m:object',NS) if o.get('id')==oid);old_item=next(o for o in build if o.get('objectid')==oid)
 old_instance=next(o for o in plate.findall('model_instance') if meta(o)['object_id']==oid)
 old_row=next(r for r in layout['placements'] if r['ref']=='P06');old_asm=[a for a in assemble if a.get('object_id')==oid]
 old_comp=old_obj.find('m:components/m:component',NS);old_mesh_path=old_comp.get(PN+'path').lstrip('/');old_sub=E.fromstring(payload[old_mesh_path])
 cfg.remove(old_cfg);resources.remove(old_obj);build.remove(old_item);plate.remove(old_instance)
 for a in old_asm:assemble.remove(a)
 for r in list(rels):
  if r.get('Target','').lstrip('/')==old_mesh_path:rels.remove(r)
 payload.pop(old_mesh_path)
 layout['placements']=[r for r in layout['placements'] if r['ref']!='P06'];settings=layout['object_settings'].pop('P06');layout['changed_mesh_refs']=['P01','P06L','P06R']
 for ref,obj_id,part_id,xy in [('P06L','16','15',[40,225]),('P06R','18','17',[75,225])]:
  member,data=exported[ref];source=out/'source-mm'/(ref+'.stl');source.write_bytes(data);mesh=trimesh.load(source,force='mesh',process=False)
  vertices,inv=np.unique(mesh.vertices,axis=0,return_inverse=True);faces=inv[mesh.faces];indexed=trimesh.Trimesh(vertices=vertices,faces=faces,process=False)
  assert indexed.is_volume and indexed.is_watertight and indexed.body_count==1,ref
  lo=vertices.min(0);hi=vertices.max(0);size=hi-lo;center=(lo+hi)/2
  assert np.allclose(size,[10,28,23.5],atol=.02),('Unexpected final block envelope',ref,size.tolist())
  trimesh.Trimesh(vertices=vertices-lo,faces=faces,process=False).export(out/'STL-print-oriented'/(ref+'.stl'))
  row=copy.deepcopy(old_row);row.update(ref=ref,source_path=str(source.relative_to(root)),source_sha256=sha(source),source_geometry='NATIVE_R19_ONSHAPE_STL',CAD_source_sha256=layout['CAD_source_sha256'],native_archive_member=member,intent='RIGID REAR ROD BLOCK - TWO M3 SCREWS REQUIRED',orientation='Flat mounting face down; vertical screw holes; retained teardrop rod-socket roof',rotation_3x3=np.eye(3).tolist(),normalization_translation_mm=(-lo).tolist(),plate_xy_mm=xy,size_oriented_mm=size.tolist(),volume_mm3=float(indexed.volume),faces=len(faces),reserved_margin_mm=4,brim_mm=0,reserved_bounds_xy_mm=[xy[0]-4,xy[1]-4,xy[0]+size[0]+4,xy[1]+size[1]+4])
  layout['placements'].append(row);layout['object_settings'][ref]=copy.deepcopy(settings)
  ob=copy.deepcopy(old_cfg);ob.set('id',obj_id)
  for m in ob.findall('metadata'):
   if m.get('key')=='name':m.set('value',ref+' - '+row['intent'])
   if m.get('face_count') is not None:m.set('face_count',str(len(faces)))
  part=ob.find('part');part.set('id',part_id);part.set('uuid',str(uuid.uuid5(uuid.NAMESPACE_URL,'fingerworker-R19-'+ref)))
  for m in part.findall('metadata'):
   k=m.get('key','')
   if k in ('name','source_file'):m.set('value',ref+'.stl')
   if k.startswith('source_offset_'):m.set('value',format(float(size['xyz'.index(k[-1])]/2),'.12g'))
  for stat in part.findall('mesh_stat'):stat.set('face_count',str(len(faces)))
  cfg.append(ob)
  resource=copy.deepcopy(old_obj);resource.set('id',obj_id);resource.set(PN+'UUID',str(uuid.uuid5(uuid.NAMESPACE_URL,'fingerworker-R19-object-'+ref)))
  component=resource.find('m:components/m:component',NS);mesh_path='3D/Objects/object_R19_'+ref+'.model';component.set(PN+'path','/'+mesh_path);component.set('objectid',part_id);component.set(PN+'UUID',str(uuid.uuid5(uuid.NAMESPACE_URL,'fingerworker-R19-component-'+ref)));resources.append(resource)
  sub=copy.deepcopy(old_sub);sub.set('xmlns:BambuStudio','http://schemas.bambulab.com/package/2021');so=sub.find('m:resources/m:object',NS);so.set('id',part_id);so.set(PN+'UUID',str(uuid.uuid5(uuid.NAMESPACE_URL,'fingerworker-R19-mesh-'+ref)));sm=so.find('m:mesh',NS);sm.clear();vv=E.SubElement(sm,MN+'vertices');ff=E.SubElement(sm,MN+'triangles')
  for v in vertices-center:E.SubElement(vv,MN+'vertex',**{k:format(float(n),'.12g') for k,n in zip('xyz',v)})
  for f in faces:E.SubElement(ff,MN+'triangle',**{k:str(int(n)) for k,n in zip(('v1','v2','v3'),f)})
  payload[mesh_path]=E.tostring(sub,encoding='utf-8',xml_declaration=True)
  trans='1 0 0 0 1 0 0 0 1 '+' '.join(format(float(v),'.12g') for v in [xy[0]+size[0]/2,xy[1]+size[1]/2,size[2]/2])
  item=copy.deepcopy(old_item);item.set('objectid',obj_id);item.set('transform',trans);item.set(PN+'UUID',str(uuid.uuid5(uuid.NAMESPACE_URL,'fingerworker-R19-build-'+ref)));build.append(item)
  instance=copy.deepcopy(old_instance)
  for m in instance:
   if m.get('key')=='object_id':m.set('value',obj_id)
   elif m.get('key')=='identify_id':m.set('value','247' if ref=='P06L' else '258')
  plate.append(instance)
  for a in old_asm:
   aa=copy.deepcopy(a);aa.set('object_id',obj_id)
   if aa.get('instance_id') is not None:aa.set('transform',trans)
   assemble.append(aa)
  E.SubElement(rels,RN+'Relationship',Target='/'+mesh_path,Id='rel-R19-'+ref,Type='http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel')
 for m in plate.findall('metadata'):
  if m.get('key')=='plater_name':m.set('value','R19 mechanical kit - 7 objects - PLA')
 for m in model.findall('m:metadata',NS):
  if m.get('name')=='Description':m.text='Seven mechanical objects: P01, P04, P05, P06L, P06R, P11 and unloaded Q01. Rear supports require four existing M3 screws. Electronics P08 excluded.'
 payload['3D/3dmodel.model']=E.tostring(model,encoding='utf-8',xml_declaration=True);payload['Metadata/model_settings.config']=E.tostring(cfg,encoding='utf-8',xml_declaration=True)
 E.register_namespace('',RN[1:-1]);payload['3D/_rels/3dmodel.model.rels']=E.tostring(rels,encoding='utf-8',xml_declaration=True);E.register_namespace('',NS['m'])
 with zipfile.ZipFile(seed,'w',zipfile.ZIP_DEFLATED) as z:
  for name,data in payload.items():z.writestr(name,data)
 for folder in ('source-mm','STL-print-oriented'):(out/folder/'P06.stl').unlink()
 layout.update(object_count=7,changed_native_refs=['P01','P06L','P06R','P08'],retained_mechanical_refs=['P04','P05','P11','Q01'],expected_native_part_count=94,expected_unchanged_native_parts=90,mechanical_hardware='Four existing H30 M3x8 screws are required: two per rear rod block; no snap mounting remains.')
 # P08 is deliberately outside both mechanical projects and their print lists.
 optional=out/'optional-electronics';optional.mkdir(exist_ok=True);member,data=exported['P08'];raw=optional/'P08-native-assembly-mm.stl';raw.write_bytes(data);raw_mesh=trimesh.load(raw,force='mesh',process=False);vv,ii=np.unique(raw_mesh.vertices,axis=0,return_inverse=True);mesh=trimesh.Trimesh(vertices=vv,faces=ii[raw_mesh.faces],process=False);assert mesh.is_volume and mesh.is_watertight and mesh.body_count==1
 lo=mesh.bounds[0].copy();mesh.apply_translation(-lo);oriented=optional/'P08-base-down-mm.stl';mesh.export(oriented)
 (optional/'manifest.json').write_text(json.dumps(dict(status='NATIVE_OPTIONAL_P08_STL_ONLY_NOT_SLICED',CAD_source_sha256=layout['CAD_source_sha256'],native_version=layout['native_R19_version'],native_archive_member=member,source_sha256=sha(raw),oriented_sha256=sha(oriented),rotation_3x3=np.eye(3).tolist(),normalization_translation_mm=(-lo).tolist(),size_mm=mesh.extents.tolist(),included_in_mechanical_projects=False,required_hardware='Two H14 M2x8 screws plus two nominal OD3.2x3mm M2 inserts secure the rigid tray ears; head at most3.8x1.6mm, no washer.',note='Optional electronics tray only; native STL geometry and base-down orientation verified, no ready-to-print slice or time estimate provided.'),indent=2)+'\n')
 (optional/'README.md').write_text('# Optional P08 electronics tray\n\nThis tray is excluded from both mechanical projects. Use it only when installing electronics. P08-base-down-mm.stl is oriented flat-base down at 100% millimeter scale. The tray now has rigid mounting ears, secured with two H14 M2×8 screws and two nominal Ø3.2×3mm M2 inserts in the existing blind pilots. Screw heads at most Ø3.8×1.6mm, no washers in the checked length stack; it no longer clips in.\n\nThis is an optional native STL, not a sliced Bambu project. Review its supports and print settings when needed. Do not import it into the mechanical plate unintentionally.\n')
