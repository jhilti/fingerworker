#!/usr/bin/env python3
"""Derive a one-object P01 replacement from the exact final six-object project."""
from pathlib import Path
import argparse,copy,hashlib,json,zipfile,xml.etree.ElementTree as E
OUT=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
NS={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'};MN='{'+NS['m']+'}';PN='{http://schemas.microsoft.com/3dmanufacturing/production/2015/06}'
E.register_namespace('',NS['m']);E.register_namespace('p',PN[1:-1])
meta=lambda e:{m.get('key'):m.get('value') for m in e.findall('metadata')}
parser=argparse.ArgumentParser();parser.add_argument('--candidate',action='store_true');args=parser.parse_args()
layout=copy.deepcopy(json.loads((OUT/('candidate-layout.json' if args.candidate else 'plate-layout.json')).read_text()))
assert layout['status'].startswith('LOCAL_')==args.candidate
full=OUT/layout['native_project'];stem='Fingerworker_R17_P01_Replacement'+('_LOCAL_TEST_CANDIDATE' if args.candidate else '')+'_H2D_04mm_PLA_Basic';seed=OUT/(stem+'_seed.3mf')
with zipfile.ZipFile(full) as z:
 model=E.fromstring(z.read('3D/3dmodel.model'));cfg=E.fromstring(z.read('Metadata/model_settings.config'))
 model.set('xmlns:BambuStudio','http://schemas.bambulab.com/package/2021')
 keep=next(o for o in cfg.findall('object') if meta(o)['name'].startswith('P01 - '));ident=keep.get('id')
 for o in list(cfg.findall('object')):
  if o is not keep:cfg.remove(o)
 for p in cfg.findall('plate'):
  for n in list(p.findall('model_instance')):
   if meta(n)['object_id']!=ident:p.remove(n)
  for n in p.findall('metadata'):
   if n.get('key')=='plater_name':n.set('value','R17 P01 replacement only - PLA')
 for n in list(cfg.find('assemble')):
  if n.get('object_id')!=ident:cfg.find('assemble').remove(n)
 resources=model.find('m:resources',NS);build=model.find('m:build',NS)
 for item in list(build):
  if item.get('objectid')!=ident:build.remove(item)
 for ob in list(resources.findall('m:object',NS)):
  if ob.get('id')!=ident:resources.remove(ob)
 retained_paths={c.get(PN+'path').lstrip('/') for c in resources.findall('m:object/m:components/m:component',NS)}
 rels=E.fromstring(z.read('3D/_rels/3dmodel.model.rels'))
 for r in list(rels):
  if r.get('Target','').lstrip('/') not in retained_paths:rels.remove(r)
 # Bambu's relationship reader expects the unprefixed element names emitted
 # by its own exporter. Preserve this document's default namespace separately.
 E.register_namespace('','http://schemas.openxmlformats.org/package/2006/relationships')
 rels_bytes=E.tostring(rels,encoding='utf-8',xml_declaration=True)
 E.register_namespace('',NS['m'])
 for n in model.findall('m:metadata',NS):
  if n.get('name')=='Title':n.text='Fingerworker R17 - P01 replacement only'+(' - LOCAL TEST CANDIDATE' if args.candidate else '')
  elif n.get('name')=='Description':n.text='Only the revised P01 frame. Same native mesh, pose, PLA Basic process and four dense strap modifiers as the six-part R17 project.'
 with zipfile.ZipFile(seed,'w',zipfile.ZIP_DEFLATED) as dst:
  for name in z.namelist():
   if name.startswith('3D/Objects/') and name not in retained_paths:continue
   if name.startswith('Metadata/') and (name.endswith('.png') or name in ('Metadata/slice_info.config','Metadata/filament_sequence.json','Metadata/plate_1.json')):continue
   if name=='3D/3dmodel.model':data=E.tostring(model,encoding='utf-8',xml_declaration=True)
   elif name=='Metadata/model_settings.config':data=E.tostring(cfg,encoding='utf-8',xml_declaration=True)
   elif name=='3D/_rels/3dmodel.model.rels':data=rels_bytes
   else:data=z.read(name)
   dst.writestr(name,data)
layout.update(status='LOCAL_R17_P01_REPLACEMENT_CANDIDATE_PENDING_SLICE' if args.candidate else 'NATIVE_R17_P01_REPLACEMENT_PENDING_SLICE',native_project=stem+'.3mf',seed_path=seed.name,seed_sha256=sha(seed),parent_six_part_project=full.name,parent_six_part_project_sha256=sha(full),variant='P01 replacement only',candidate=args.candidate)
layout['placements']=[r for r in layout['placements'] if r['ref']=='P01'];layout['object_settings']={'P01':layout['object_settings']['P01']}
(OUT/('replacement-candidate-layout.json' if args.candidate else 'replacement-layout.json')).write_text(json.dumps(layout,indent=2)+'\n')
print(json.dumps(dict(status=layout['status'],seed=seed.name,parent_sha256=sha(full),objects=1,modifiers=layout['modifier_count'])))
