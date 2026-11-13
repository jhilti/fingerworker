#!/usr/bin/env python3
"""Replace P01 in the frozen connected PLA Basic project; retain other parts.

Never changes source geometry, moves plate XY positions, or sends a printer command.
Candidate mode may omit only exactly zero-area facets and is not release evidence.
"""
from pathlib import Path
import argparse,copy,hashlib,json,shutil,zipfile,xml.etree.ElementTree as E
import numpy as np
import trimesh

OUT=Path(__file__).resolve().parents[1]; ROOT=OUT.parents[1]
OLD=ROOT/'print/bambu-R15-inboard-straps-2026-11-08'
BASELINE=OLD/'Fingerworker_R15_H2D_04mm_PLA_Basic_Print_Ready.3mf'
BASELINE_SHA='b8eeb41a267ef7808fde1a6ee5a036eed1ef9a24f7610044177396576bca23d7'
BASE='Fingerworker_R16_H2D_04mm_PLA_Basic_Print_Ready'
NS={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}
MN='{'+NS['m']+'}'; PN='{http://schemas.microsoft.com/3dmanufacturing/production/2015/06}'
E.register_namespace('',NS['m']);E.register_namespace('p',PN[1:-1])
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
meta=lambda e:{m.get('key'):m.get('value') for m in e.findall('metadata') if m.get('key')}

def main():
 p=argparse.ArgumentParser();group=p.add_mutually_exclusive_group(required=True)
 group.add_argument('--source',type=Path);group.add_argument('--native-zip',type=Path);p.add_argument('--source-cad',type=Path,required=True)
 p.add_argument('--version',required=True);p.add_argument('--candidate',action='store_true');a=p.parse_args()
 cad=a.source_cad.resolve();assert sha(BASELINE)==BASELINE_SHA
 for folder in ('profiles','source-mm','STL-print-oriented','preview','runtime','validation'):(OUT/folder).mkdir(exist_ok=True)
 native_zip=None;native_member=None
 if a.native_zip:
  assert not a.candidate
  native_zip=a.native_zip.resolve()
  with zipfile.ZipFile(native_zip) as z:
   names=[n for n in z.namelist() if ' - P01 ' in n and n.endswith('.stl')];assert len(names)==1
   native_member=names[0];source=OUT/'runtime/native-P01.stl';source.write_bytes(z.read(native_member))
 else:source=a.source.resolve()
 layout=copy.deepcopy(json.loads((OLD/'plate-layout.json').read_text()))
 row=next(r for r in layout['placements'] if r['ref']=='P01')
 mesh=trimesh.load(source,force='mesh',process=False)
 vertices,inv=np.unique(mesh.vertices,axis=0,return_inverse=True);faces=inv[mesh.faces]
 omitted=[]
 if a.candidate:
  keep=np.array([len(set(f))==3 for f in faces]);omitted=vertices[faces[~keep]].tolist();faces=faces[keep]
 indexed=trimesh.Trimesh(vertices=vertices,faces=faces,process=False)
 assert indexed.is_volume and indexed.is_watertight and indexed.body_count==1
 lo=vertices.min(0);hi=vertices.max(0);size=hi-lo;center=(hi+lo)/2;xy=np.asarray(row['plate_xy_mm'])
 oldlo=-np.asarray(row['normalization_translation_mm']);oldcenter=oldlo+np.asarray(row['size_oriented_mm'])/2
 old_offset=oldcenter-center
 row.update(source_path=str(source.relative_to(ROOT)),source_sha256=sha(source),source_geometry='LOCAL_R16_CANDIDATE_STL' if a.candidate else 'NATIVE_R16_ONSHAPE_STL',
  CAD_source_sha256=sha(cad),intent='INTEGRATED UPRIGHT PALM GRIP AND ROUNDED THUMB SHOULDERS',
  orientation='Base floor down; upright palm contact is an outer wall',rotation_3x3=np.eye(3).tolist(),normalization_translation_mm=(-lo).tolist(),
  size_oriented_mm=size.tolist(),volume_mm3=float(indexed.volume),faces=len(faces),
  reserved_bounds_xy_mm=[*(xy-row['reserved_margin_mm']).tolist(),*(xy+size[:2]+row['reserved_margin_mm']).tolist()])
 for ref in ('P04','P05','P06','P11','Q01'):
  for folder in ('source-mm','STL-print-oriented'):shutil.copyfile(OLD/folder/(ref+'.stl'),OUT/folder/(ref+'.stl'))
 if source.resolve()!=(OUT/'source-mm/P01.stl').resolve():shutil.copyfile(source,OUT/'source-mm/P01.stl')
 if cad.resolve()!=(OUT/'source'/cad.name).resolve():shutil.copyfile(cad,OUT/'source'/cad.name)
 row['source_path']=str((OUT/'source-mm/P01.stl').relative_to(ROOT))
 trimesh.Trimesh(vertices=vertices-lo,faces=faces,process=False).export(OUT/'STL-print-oriented/P01.stl')
 stem=BASE+('_candidate' if a.candidate else '');seed=OUT/(stem+'_seed.3mf')
 with zipfile.ZipFile(BASELINE) as z:
  model=E.fromstring(z.read('3D/3dmodel.model'));cfg=E.fromstring(z.read('Metadata/model_settings.config'))
  model.set('xmlns:BambuStudio','http://schemas.bambulab.com/package/2021')
  ob=next(o for o in cfg.findall('object') if meta(o)['name'].startswith('P01 - '));ident=ob.get('id')
  res=next(o for o in model.findall('m:resources/m:object',NS) if o.get('id')==ident)
  part=next(p for p in ob.findall('part') if p.get('subtype')=='normal_part')
  comp=next(c for c in res.findall('m:components/m:component',NS) if c.get('objectid')==part.get('id'))
  assert comp.get('transform')=='1 0 0 0 1 0 0 0 1 0 0 0'
  mesh_path=comp.get(PN+'path').lstrip('/')
  sub=E.fromstring(z.read(mesh_path));sub.set('xmlns:BambuStudio','http://schemas.bambulab.com/package/2021')
  mesh_ob=next(o for o in sub.findall('m:resources/m:object',NS) if o.get('id')==part.get('id'))
  smesh=mesh_ob.find('m:mesh',NS);smesh.clear();vv=E.SubElement(smesh,MN+'vertices');ff=E.SubElement(smesh,MN+'triangles')
  for v in vertices-center:E.SubElement(vv,MN+'vertex',**{k:format(float(n),'.12g') for k,n in zip('xyz',v)})
  for f in faces:E.SubElement(ff,MN+'triangle',**{k:str(int(n)) for k,n in zip(('v1','v2','v3'),f)})
  for c in res.findall('m:components/m:component',NS):
   if c is comp:continue
   transform=np.array([float(n) for n in c.get('transform').split()]);transform[9:]+=old_offset
   c.set('transform',' '.join(format(float(n),'.12g') for n in transform))
  build=next(i for i in model.findall('m:build/m:item',NS) if i.get('objectid')==ident)
  build.set('transform','1 0 0 0 1 0 0 0 1 '+' '.join(format(float(n),'.12g') for n in [*(xy+size[:2]/2),size[2]/2]))
  for m in ob.findall('metadata'):
   if m.get('key')=='name':m.set('value','P01 - '+row['intent'])
   if m.get('face_count') is not None:m.set('face_count',str(len(faces)))
  for m in part.findall('metadata'):
   if m.get('key','').startswith('source_offset_'):m.set('value',format(float(size['xyz'.index(m.get('key')[-1])]/2),'.12g'))
  for m in part.findall('mesh_stat'):m.set('face_count',str(len(faces)))
  for plate in cfg.findall('plate'):
   for m in plate.findall('metadata'):
    if m.get('key')=='plater_name':m.set('value','R16 upright palm grip - 6 pieces - PLA')
    if m.get('key')=='filament_map_mode':m.set('value','Manual')
    if m.get('key')=='filament_maps':m.set('value','1 1 1 1 1 1')
  for m in model.findall('m:metadata',NS):
   if m.get('name')=='Title':m.text='Fingerworker R16 upright palm grip'
   elif m.get('name')=='Description':m.text='One-piece P01 upright palm face, rounded rod-socket shoulders and shallow thumb returns. Five retained mechanical pieces, H2D 0.4, PLA Basic, no brim. No printer command.'
   elif m.get('name') in ('CreationDate','ModificationDate'):m.text='2026-11-09'
  settings=json.loads(z.read('Metadata/project_settings.config'));settings['print_settings_id']='Fingerworker R16 upright palm no brim 0.20mm'
  settings['filament_map_mode']='Manual'
  (OUT/'profiles/project_settings_H2D_PLA_Basic.json').write_text(json.dumps(settings,indent=2)+'\n')
  (OUT/'profiles/profile-manifest.json').write_text(json.dumps(dict(status='RETAINED_R15_PROCESS_MATERIAL_SETTINGS',baseline_project_sha256=BASELINE_SHA,declared_changes={'print_settings_id':settings['print_settings_id'],'filament_map_mode':'Manual'},output_profiles={'project_settings_H2D_PLA_Basic.json':sha(OUT/'profiles/project_settings_H2D_PLA_Basic.json')}),indent=2)+'\n')
  with zipfile.ZipFile(seed,'w',zipfile.ZIP_DEFLATED) as dest:
   for name in z.namelist():
    if name.startswith('Metadata/') and (name.endswith('.png') or name in ('Metadata/plate_1.json','Metadata/slice_info.config','Metadata/filament_sequence.json')):continue
    if name=='3D/3dmodel.model':data=E.tostring(model,encoding='utf-8',xml_declaration=True)
    elif name==mesh_path:data=E.tostring(sub,encoding='utf-8',xml_declaration=True)
    elif name=='Metadata/model_settings.config':data=E.tostring(cfg,encoding='utf-8',xml_declaration=True)
    elif name=='Metadata/project_settings.config':data=json.dumps(settings,indent=2).encode()
    else:data=z.read(name)
    dest.writestr(name,data)
 layout.pop('native_R15_version',None);layout['profile_changes']={}
 regions=json.loads((OLD/'source/strap-print-regions.json').read_text());regions.update(revision='R16',CAD_source_sha256=sha(cad),status='RETAINED_R15_STRAP_REGIONS')
 region_path=OUT/'source/strap-print-regions.json';region_path.write_text(json.dumps(regions,indent=2)+'\n')
 layout.update(status='LOCAL_R16_CANDIDATE_PENDING_SLICE' if a.candidate else 'NATIVE_R16_PENDING_SLICE',date='2026-11-09',
  CAD_source_path=str(cad.relative_to(ROOT)),CAD_source_sha256=sha(cad),native_R16_version=a.version,
  native_project=stem+'.3mf',seed_path=seed.name,seed_sha256=sha(seed),baseline_project=str(BASELINE.relative_to(ROOT)),baseline_project_sha256=sha(BASELINE),
  candidate_zero_area_facets_omitted=len(omitted),candidate_zero_area_facet_vertices=omitted,
  strap_print_regions_path=str(region_path.relative_to(ROOT)),strap_print_regions_sha256=sha(region_path),
  changes='Only P01 native geometry replaced. Other five meshes, placements, all process/material settings except preset label retained from connected R15 PLA Basic project. Filament mapping pinned Manual to preserve the existing left nozzle instead of allowing automatic remapping. Four strap infill modifiers retained in native coordinates.',
  mapping_change=dict(previous_mode='Auto For Flush',new_mode='Manual',logical_extruder=1,filament_maps=[1]*6,reason='Prevent automatic nozzle reassignment; retain baseline actual left nozzle',primary_source='https://raw.githubusercontent.com/bambulab/BambuStudio/v02.08.02.61/src/libslic3r/PrintConfig.cpp'),
  native_STL_archive=str(native_zip.relative_to(ROOT)) if native_zip else None,
  native_STL_archive_sha256=sha(native_zip) if native_zip else None,native_P01_member=native_member,
  printer_transmission=False)
 lp=OUT/('candidate-layout.json' if a.candidate else 'plate-layout.json');lp.write_text(json.dumps(layout,indent=2)+'\n')
 print(json.dumps(dict(status=layout['status'],seed=str(seed),layout=str(lp),P01_size_mm=size.tolist(),P01_volume_mm3=float(indexed.volume),source_sha256=sha(source))))

if __name__=='__main__':main()
