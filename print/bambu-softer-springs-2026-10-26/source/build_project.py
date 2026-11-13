"""Author a two-instance editable H2D PLA project from the exact S01 prototype STL."""
from pathlib import Path
from hashlib import sha256
from io import StringIO
from xml.sax.saxutils import escape,quoteattr
import json,zipfile,numpy as np,trimesh as tm
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parents[1]
SRC=ROOT/'review/flat132-softer-springs-2026-10-26/print/S01_spring_spacer_22mm.stl'
EXPECTED='be2724e7fbf7a725786b7f9a52ae62f923ff82b8c44994e72d24cef2e4f2addd'
blob=SRC.read_bytes();assert sha256(blob).hexdigest()==EXPECTED
m=tm.load_mesh(SRC);assert m.is_watertight and m.is_volume
parents=list(range(len(m.vertices)))
def find(i):
 while parents[i]!=i:parents[i]=parents[parents[i]];i=parents[i]
 return i
for a,b,c in m.faces:
 for i in [b,c]:parents[find(int(i))]=find(int(a))
assert len({find(int(i)) for i in np.unique(m.faces)})==1
assert np.allclose(m.extents,[16,16,24],atol=.01) and abs(m.bounds[0,2])<.001
shift=-m.bounds[0].copy();m.apply_translation(shift)
(OUT/'source-mm/S01_spring_spacer_22mm.stl').write_bytes(blob)
placements=[[150,152],[184,152]]
s=StringIO();s.write('<?xml version="1.0" encoding="UTF-8"?><model unit="millimeter" xml:lang="en-US" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">')
for name,value in [('Application','BambuStudio-02.08.02.61'),('BambuStudio:3mfVersion','1'),('Title','S01 22mm spring spacers - two PLA prototypes'),('Description','Two full-scale S01 spacers; flat root down, spring pilot up. Prototype, load rating unverified.')]:s.write(f'<metadata name={quoteattr(name)}>{escape(value)}</metadata>')
s.write('<resources><object id="1" type="model"><mesh><vertices>')
for x,y,z in m.vertices:s.write(f'<vertex x="{x:.9g}" y="{y:.9g}" z="{z:.9g}"/>')
s.write('</vertices><triangles>')
for a,b,c in m.faces:s.write(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>')
s.write('</triangles></mesh></object><object id="2" type="model"><components><component objectid="1" transform="1 0 0 0 1 0 0 0 1 0 0 0"/></components></object></resources><build>')
for x,y in placements:s.write(f'<item objectid="2" transform="1 0 0 0 1 0 0 0 1 {x} {y} 0" printable="1"/>')
s.write('</build></model>')
def meta(k,v):return f'<metadata key={quoteattr(k)} value={quoteattr(str(v))}/>'
c=StringIO();c.write('<?xml version="1.0" encoding="UTF-8"?><config><object id="2">')
for k,v in {'name':'S01 -22mm spring spacer - prototype','extruder':'1','enable_support':'0','wall_loops':'4','sparse_infill_density':'100%','brim_type':'no_brim','brim_width':'0'}.items():c.write(meta(k,v))
c.write('<part id="1" subtype="normal_part">'+meta('name',SRC.name)+meta('source_file',SRC.name)+f'<mesh_stat face_count="{len(m.faces)}" edges_fixed="0" degenerate_facets="0" facets_removed="0" facets_reversed="0" backwards_edges="0"/></part></object><plate>')
for k,v in {'plater_id':1,'plater_name':'Two S01 22mm spacers - PLA prototype','locked':'false','bed_type':'Textured PEI Plate','print_sequence':'by layer'}.items():c.write(meta(k,v))
for i in range(2):c.write('<model_instance>'+meta('object_id','2')+meta('instance_id',i)+meta('identify_id',i+1)+'</model_instance>')
c.write('</plate><assemble/></config>')
rels='<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'
content='<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/><Default Extension="config" ContentType="application/octet-stream"/></Types>'
target=OUT/'S01_22mm_spacers_H2D_04mm_PLA_seed.3mf'
with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
 for n,v in [('3D/3dmodel.model',s.getvalue()),('Metadata/model_settings.config',c.getvalue()),('Metadata/project_settings.config',(OUT/'profiles/project_settings_H2D.json').read_text()),('_rels/.rels',rels),('[Content_Types].xml',content)]:z.writestr(n,v)
record={'status':'TWO_INSTANCE_SEED_AUTHORED','source':str(SRC.relative_to(ROOT)),'source_sha256':EXPECTED,'seed_sha256':sha256(target.read_bytes()).hexdigest(),'pieces':2,'unique_meshes':1,'scale':1,'unit':'mm','rotation':'Identity: flat root Z0 down, pilot up','normalization_translation_mm':shift.tolist(),'XY_minima_mm':placements,'size_mm':m.extents.tolist(),'volume_each_mm3':float(m.volume),'faces':len(m.faces),'no_geometry_repair':True,'layer_height_mm':.2,'walls':4,'infill_percent':100,'supports':False,'no_printer_transmission':True}
(OUT/'project-inputs.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record,indent=2))
