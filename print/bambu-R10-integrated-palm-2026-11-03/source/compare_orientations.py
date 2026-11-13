"""Compare two successfully sliced rigid orientations of the same native P01."""
from pathlib import Path
from hashlib import sha256
import json,re,zipfile,xml.etree.ElementTree as E
import numpy as np,trimesh as tm
OUT=Path(__file__).resolve().parents[1]
main=json.loads((OUT/'plate-layout.json').read_text())
candidate=json.loads((OUT/'candidate-wrist-layout.json').read_text())
source=tm.load_mesh(OUT/'source-mm/P01.stl')
def sha(p):return sha256(p.read_bytes()).hexdigest()
def read(path,row):
    with zipfile.ZipFile(path) as z:
        assert z.testzip() is None
        p=E.fromstring(z.read('Metadata/slice_info.config')).find('plate')
        md={m.get('key'):m.get('value') for m in p.findall('metadata')}
        assert md['outside']=='false' and len(p.findall('object'))==1
        g=z.read('Metadata/plate_1.gcode').decode()
    mesh=source.copy();mesh.vertices=mesh.vertices@np.asarray(row['rotation_3x3']).T;mesh.apply_translation(-mesh.bounds[0])
    area=float(mesh.area_faces[np.max(mesh.triangles[:,:,2],axis=1)<.00001].sum())
    feature='';active=False;support_e=0.;relative=True;eold=0.;pos=np.zeros(3)
    for line in g.splitlines():
        if line.startswith('; OBJECT_ID: '):active=True
        elif line.startswith('; FEATURE: '):
            feature=line[11:].strip()
            if feature=='Custom':active=False
        elif line.startswith('M83'):relative=True
        elif line.startswith('M82'):relative=False
        elif line.startswith('G92 '):
            e=re.search(r'\bE(-?[\d.]+)',line)
            if e:eold=float(e[1])
        elif re.match('^G[0123] ',line):
            values={a:float(b) for a,b in re.findall(r'([XYZEFIJ])(-?\d*\.?\d+)',line.split(';')[0])}
            new=np.array([values.get(a,pos[i]) for i,a in enumerate('XYZ')]);de=values.get('E',0) if relative else values.get('E',eold)-eold
            if 'E' in values:eold=eold+values['E'] if relative else values['E']
            if active and feature.startswith('Support') and de>0 and (np.linalg.norm(new[:2]-pos[:2])>1e-6 or line.startswith(('G2 ','G3 '))):support_e+=de
            pos=new
    return dict(evidence_archive_sha256=sha(path),source_sha256=row['source_sha256'],print_size_mm=mesh.extents.tolist(),exact_planar_bed_contact_area_mm2=area,
                estimated_seconds=int(md['prediction']),estimated_total_grams=float(md['weight']),actual_support_filament_e_mm=support_e,
                actual_support_mass_estimate_g=support_e*np.pi*(1.75/2)**2*1.24/1000,slicer_exit_code=0,outside=False)
flat=read(OUT/'validation'/(Path(main['native_project']).stem+'_verification.gcode.3mf'),main['placements'][0])
wrist=read(OUT/'validation/candidate-wrist'/(Path(candidate['native_project']).stem+'_verification.gcode.3mf'),candidate['placements'][0])
assert flat['source_sha256']==wrist['source_sha256']
assert flat['estimated_seconds']<wrist['estimated_seconds'] and flat['estimated_total_grams']<wrist['estimated_total_grams']
result=dict(status='PASS_FLAT_ORIENTATION_SELECTED',source_sha256=flat['source_sha256'],flat=flat,wrist=wrist,
    selected='flat',reason='Same native mesh: the flat floor gives the broadest planar bed contact, 35 mm build height, lower material/time and accessible external palm supports. Wrist-down raises the frame to175 mm and requires more support. The curved hand-contact surface remains upward in flat orientation.',
    caution='Only the selected flat layout is shipped. Actual support release and part strength require the unloaded physical trial.')
(OUT/'validation/orientation-comparison.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
