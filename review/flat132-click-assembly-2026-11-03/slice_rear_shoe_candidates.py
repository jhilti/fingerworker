#!/usr/bin/env python3
"""Small local comparison; never transmits to a printer or edits release files."""
from pathlib import Path
import json, zipfile, subprocess
from io import StringIO
from xml.sax.saxutils import quoteattr
import numpy as np
import trimesh as tm

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
OUT=HERE/'rear-shoe-print-study';OUT.mkdir(exist_ok=True)
PROF=ROOT/'print/bambu-R11-PLA-click-2026-11-03/profiles'
CLI='/tmp/fingerworker-bambu-r8-runtime/BambuStudio.app/Contents/MacOS/BambuStudio'
META=lambda k,v:f'<metadata key={quoteattr(k)} value={quoteattr(str(v))}/>'

def main():
    cfg=json.loads((PROF/'project_settings_H2D.json').read_text())
    mesh=tm.load_mesh(HERE/'local-preflight-meshes/P120.stl')
    matrices={'Xmin':np.array([[0,0,-1],[0,1,0],[1,0,0]]),
              'Zmax':np.diag([1,-1,-1]),
              'Ymin':np.array([[1,0,0],[0,0,-1],[0,1,0]])}
    model=StringIO();model.write('<?xml version="1.0"?><model unit="millimeter" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02"><metadata name="Application">BambuStudio-02.08.02.61</metadata><metadata name="BambuStudio:3mfVersion">1</metadata><resources>')
    xml=StringIO();xml.write('<?xml version="1.0"?><config>')
    rows=[]
    for idx,(name,R) in enumerate(matrices.items()):
        m=mesh.copy();m.vertices=m.vertices@R.T;m.apply_translation(-m.bounds[0])
        mid=2*idx+1;oid=mid+1;x=50+70*idx;y=50
        area=float(m.area_faces[np.max(m.triangles[:,:,2],axis=1)<1e-5].sum())
        rows.append(dict(name=name,rotation_3x3=R.tolist(),bed_contact_area_mm2=area,object_id=oid,xy=[x,y]))
        model.write(f'<object id="{mid}" type="model"><mesh><vertices>')
        for a,b,c in m.vertices:model.write(f'<vertex x="{a:.9g}" y="{b:.9g}" z="{c:.9g}"/>')
        model.write('</vertices><triangles>')
        for a,b,c in m.faces:model.write(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>')
        model.write(f'</triangles></mesh></object><object id="{oid}" type="model" name="{name}"><components><component objectid="{mid}"/></components></object>')
        opts=dict(extruder='1',name=name,brim_type='outer_only',brim_width='4',brim_object_gap='0.1',enable_support='1',support_type='normal(auto)',support_on_build_plate_only='1',support_top_z_distance='0.25',support_threshold_angle='30',outer_wall_speed='40',inner_wall_speed='40',top_surface_speed='40',internal_solid_infill_speed='40',gap_infill_speed='40',sparse_infill_speed='40')
        xml.write(f'<object id="{oid}">')
        for k,v in opts.items():
            if isinstance(cfg.get(k),list):v=','.join([v]*len(cfg[k]))
            xml.write(META(k,v))
        xml.write(f'<part id="{mid}" subtype="normal_part">'+META('name',name+'.stl')+f'<mesh_stat face_count="{len(m.faces)}" edges_fixed="0" degenerate_facets="0" facets_removed="0" facets_reversed="0" backwards_edges="0"/></part></object>')
    model.write('</resources><build>')
    for r in rows:model.write(f'<item objectid="{r["object_id"]}" transform="1 0 0 0 1 0 0 0 1 {r["xy"][0]} {r["xy"][1]} 0" printable="1"/>')
    model.write('</build></model>')
    xml.write('<plate>'+META('plater_id',1)+META('plater_name','Local P12 orientation comparison')+META('bed_type','Textured PEI Plate'))
    for i,r in enumerate(rows):xml.write('<model_instance>'+META('object_id',r['object_id'])+META('instance_id',0)+META('identify_id',i+1)+'</model_instance>')
    xml.write('</plate><assemble/></config>')
    seed=OUT/'candidates_seed.3mf'
    rels='<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'
    content='<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/><Default Extension="config" ContentType="application/octet-stream"/></Types>'
    with zipfile.ZipFile(seed,'w',zipfile.ZIP_DEFLATED) as z:
        for n,d in [('3D/3dmodel.model',model.getvalue()),('Metadata/model_settings.config',xml.getvalue()),('Metadata/project_settings.config',json.dumps(cfg)),('_rels/.rels',rels),('[Content_Types].xml',content)]:z.writestr(n,d)
    native=OUT/'candidates.3mf';sliced=OUT/'candidates_verification.gcode.3mf'
    base=[CLI,'--datadir','/tmp/fingerworker-r11-rear-shoes','--arrange','0','--orient','0','--ensure-on-bed','--debug','2']
    commands=[base+['--load-settings',str(PROF/'H2D_machine.json')+';'+str(PROF/'H2D_process.json'),'--load-filaments',str(PROF/'H2D_PLA.json'),'--export-3mf',str(native),str(seed)],base+['--slice','0','--export-3mf',str(sliced),str(native)]]
    for i,command in enumerate(commands):
        with (OUT/('import.log' if i==0 else 'slice.log')).open('w') as log:
            r=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,cwd=OUT)
        assert r.returncode==0,(i,r.returncode)
    record=dict(status='SUCCESSFULLY_SLICED_LOCAL_CANDIDATES',rows=rows,sliced=str(sliced),scope='Local BRep preflight meshes, not native R11 exports; all supports plate-only normal,0.25mm top gap,4mm outer brim.')
    (OUT/'study.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record,indent=2))

if __name__=='__main__':main()
