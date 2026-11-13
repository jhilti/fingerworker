#!/usr/bin/env python3
"""Local draft flat-print preflight; never sends anything to the printer."""
from pathlib import Path
from io import StringIO
from xml.sax.saxutils import escape,quoteattr
import json,zipfile,subprocess,hashlib
import trimesh as tm
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
BASE=ROOT/'print/bambu-R10-integrated-palm-2026-11-03'
profile=json.loads((BASE/'profiles/project_settings_H2D.json').read_text())
prior=json.loads((BASE/'plate-layout.json').read_text())
meta=lambda k,v:f'<metadata key={quoteattr(k)} value={quoteattr(str(v))}/>'
rows=[];meshes={};settings={}
for k,xy in [('P08',[80,80]),('P09',[130,90])]:
 m=tm.load_mesh(HERE/(k+'_print.stl'));assert m.is_volume and m.body_count==1
 meshes[k]=m;settings[k]=prior['object_settings'][k].copy()
 settings[k].update(brim_type='outer_only',brim_width='3',brim_object_gap='0.1',outer_wall_speed='40',inner_wall_speed='60',gap_infill_speed='40')
 if k=='P08':settings[k].update(enable_support='1',support_type='normal(auto)',support_on_build_plate_only='0')
 else:settings[k]['enable_support']='0'
 rows.append(dict(ref=k,xy=xy,extents_mm=m.extents.tolist(),volume_mm3=float(m.volume),bed_area_mm2=float(m.area_faces[(m.face_normals[:,2]<-.999)&(m.triangles_center[:,2]<.001)].sum())))
s=StringIO();s.write('<?xml version="1.0" encoding="UTF-8"?><model unit="millimeter" xml:lang="de-DE" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">')
for name,value in [('Application','BambuStudio-02.08.02.61'),('BambuStudio:3mfVersion','1'),('Title','R11 enclosure local printability preflight')]:s.write(f'<metadata name={quoteattr(name)}>{escape(value)}</metadata>')
s.write('<resources>')
for i,(k,m) in enumerate(meshes.items()):
 mid,oid=2*i+1,2*i+2;s.write(f'<object id="{mid}" type="model"><mesh><vertices>')
 for x,y,z in m.vertices:s.write(f'<vertex x="{x:.9g}" y="{y:.9g}" z="{z:.9g}"/>')
 s.write('</vertices><triangles>')
 for a,b,c in m.faces:s.write(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>')
 s.write(f'</triangles></mesh></object><object id="{oid}" type="model" name="{k}"><components><component objectid="{mid}" transform="1 0 0 0 1 0 0 0 1 0 0 0"/></components></object>')
s.write('</resources><build>')
for i,r in enumerate(rows):s.write(f'<item objectid="{2*i+2}" transform="1 0 0 0 1 0 0 0 1 {r["xy"][0]} {r["xy"][1]} 0" printable="1"/>')
s.write('</build></model>')
c=StringIO();c.write('<?xml version="1.0"?><config>')
for i,r in enumerate(rows):
 k=r['ref'];mid,oid=2*i+1,2*i+2;c.write(f'<object id="{oid}">'+meta('name',k+' R11 local preflight')+meta('extruder','1'))
 for key,val in settings[k].items():
  if isinstance(profile.get(key),list):val=','.join([str(val)]*len(profile[key]))
  c.write(meta(key,val))
 c.write(f'<part id="{mid}" subtype="normal_part">'+meta('name',k+'.stl')+f'<mesh_stat face_count="{len(meshes[k].faces)}" edges_fixed="0" degenerate_facets="0" facets_removed="0" facets_reversed="0" backwards_edges="0"/></part></object>')
c.write('<plate>'+meta('plater_id',1)+meta('plater_name','R11 enclosure local preflight')+meta('locked','false')+meta('bed_type','Textured PEI Plate')+meta('print_sequence','by layer'))
for i,r in enumerate(rows):c.write('<model_instance>'+meta('object_id',2*i+2)+meta('instance_id',0)+meta('identify_id',i+1)+'</model_instance>')
c.write('</plate><assemble/></config>')
rels='<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'
content='<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/><Default Extension="config" ContentType="application/octet-stream"/></Types>'
seed=HERE/'enclosure_seed.3mf';native=HERE/'enclosure_preflight.3mf';sliced=HERE/'enclosure_preflight_verification.gcode.3mf'
with zipfile.ZipFile(seed,'w',zipfile.ZIP_DEFLATED) as z:
 for n,data in [('3D/3dmodel.model',s.getvalue()),('Metadata/model_settings.config',c.getvalue()),('Metadata/project_settings.config',json.dumps(profile)),('_rels/.rels',rels),('[Content_Types].xml',content)]:z.writestr(n,data)
common=['/tmp/fingerworker-bambu-r8-runtime/BambuStudio.app/Contents/MacOS/BambuStudio','--datadir','/tmp/fingerworker-bambu-r11-enclosure-data','--arrange','0','--orient','0','--ensure-on-bed','--debug','2']
commands=[common+['--load-settings',str(BASE/'profiles/H2D_machine.json')+';'+str(BASE/'profiles/H2D_process.json'),'--load-filaments',str(BASE/'profiles/H2D_PLA.json'),'--outputdir',str(HERE),'--export-3mf',native.name,str(seed)],common+['--slice','0','--outputdir',str(HERE),'--export-3mf',sliced.name,str(native)]]
results=[]
for i,cmd in enumerate(commands):
 with (HERE/f'slicer-{i}.log').open('w') as f:r=subprocess.run(cmd,cwd=HERE,stdout=f,stderr=subprocess.STDOUT)
 results.append(dict(exit_code=r.returncode,command=cmd));assert r.returncode==0
report=dict(status='SLICED_LOCAL_PROPOSAL',objects=rows,commands=results,native_sha256=hashlib.sha256(native.read_bytes()).hexdigest(),sliced_sha256=hashlib.sha256(sliced.read_bytes()).hexdigest(),note='Local CSG candidate, not authoritative native Onshape geometry; inspect final R11 native exports separately.')
(HERE/'slice-summary.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
