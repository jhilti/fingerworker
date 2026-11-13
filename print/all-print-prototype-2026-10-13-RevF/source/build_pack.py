"""Rev F: rigid-only print orientations; nominal assembled device remains unchanged."""
from pathlib import Path
import json,hashlib,csv,shutil
import numpy as np
import trimesh as tm
from scipy.spatial import cKDTree
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parents[1]
BASE=ROOT/'print/all-print-prototype-2026-10-13-RevD'
(OUT/'PETG').mkdir(exist_ok=True)
rotations={'P04':90,'P05':90,'H12':90,'H02':-90}
labels={'P04':'REAR_DOWN','P05':'RIB_DOWN','H12':'SIDE_DOWN','H02':'UPRIGHT'}
notes={
 'P01':'Flache Unterseite unten; 5 mm Außenbrim; zugängliche Stützen nur vom Bett.',
 'P04':'Hintere Stirnseite unten; 5 mm Brim; Stützen auch auf dem Modell, durch Griffmulde und offene Führungsunterseite entfernen.',
 'P05':'Hintere Rippe unten; 5 mm Brim; Stützen nur vom Bett. Führungs- und Druckstiftbohrungen bleiben stützenfrei.',
 'H12':'Seitlich auf flacher Kante; 3 mm Brim; Stützen in offener Sensortasche von deren Vorderseite entfernen.',
 'H02':'Ø4-Kontaktende auf Bett; 3 mm Brim; zugängliche Stützen unter Schulter.',
 'P08':'Wannenboden unten; Stützen auch auf dem Modell unter USB-Ausschnitt, durch offene Wanne entfernen.',
 'P03a':'Senkrecht wie bisher; 8 mm Brim; Wände 60 mm/s, Beschleunigung 1500 mm/s².',
 'P03b':'Senkrecht wie bisher; 8 mm Brim; Wände 60 mm/s, Beschleunigung 1500 mm/s².',
 'P10':'Flach, 2 mm Brim; kleine Wände 40 mm/s, erste Schicht 20 mm/s.',
 'H19':'Aufrecht, Arachne für 0,4-mm-Wand; 3 mm Außenbrim, langsam drucken und vorsichtig abnehmen.',
 'H22':'Flach, 3 mm Außenbrim; winzige Ø2,5-mm-Formprobe, langsam drucken.',
 'P060':'Aufrecht wie bisher, Schraubenlöcher senkrecht; kurze Stablochbrücke 25 mm/s.',
 'P061':'Aufrecht wie bisher, Schraubenlöcher senkrecht; kurze Stablochbrücke 25 mm/s.',
}
rows=[];checks=[]
for row in json.loads((BASE/'Druckliste.json').read_text()):
    key=Path(row['file']).name.split('_')[0];source=BASE/row['file'];before=tm.load_mesh(source)
    assert hashlib.sha256(source.read_bytes()).hexdigest()==row['sha256']
    rotation=np.eye(4)
    if key in rotations:
        sign=1 if rotations[key]>0 else -1
        rotation[:3,:3]=[[0,0,sign],[0,1,0],[-sign,0,0]]
        mesh=before.copy();mesh.apply_transform(rotation);translation=-mesh.bounds[0]
        mesh.apply_translation(translation)
        name=source.stem+'_'+labels[key]+'_RevF.stl';dest=OUT/'PETG'/name;mesh.export(dest)
        full=rotation.copy();full[:3,3]=translation
    else:
        dest=OUT/'PETG'/source.name;shutil.copyfile(source,dest);full=np.eye(4)
    after=tm.load_mesh(dest)
    expected=before.vertices@full[:3,:3].T+full[:3,3]
    error=float(cKDTree(expected).query(after.vertices)[0].max())
    assert error<.0001 and after.is_watertight and after.is_volume
    assert len(before.faces)==len(after.faces) and abs(after.volume-before.volume)<max(.01,before.volume*1e-5)
    assert np.isclose(np.linalg.det(full[:3,:3]),1) and abs(after.bounds[0,2])<.0001
    item=dict(row,file=str(dest.relative_to(OUT)),source=str(source.relative_to(ROOT)),nominal_source=row['source'],
              source_sha256=row['sha256'],sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),
              print_rotation_y_deg=rotations.get(key,0),rigid_transform=full.tolist(),bounds_mm=after.extents.round(4).tolist())
    item['note']=notes.get(key,row['note'])
    if key.startswith('P07'):item['note']='Flach; 0,1-mm-Schichten für tatsächliche 1,50-mm-Dicke. Harte Formprobe ohne elastische Dämpfung.'
    rows.append(item)
    down=after.face_normals[:,2]<-.99999
    bed=down & np.all(after.triangles[:,:,2]<.001,axis=1)
    roof=down & (after.triangles_center[:,2]>.21)
    try:
        section=after.section(plane_origin=[0,0,.1],plane_normal=[0,0,1])
        planar=section.to_2D()[0]
        first_area=sum(p.area for p in planar.polygons_full)
    except Exception:first_area=None
    checks.append(dict(part=key,file=item['file'],closed=True,triangles=len(after.faces),volume_mm3=float(after.volume),
        rigid_roundtrip_error_mm=error,bed_contact_area_mm2=float(after.area_faces[bed].sum()),
        section_at_z0_1_area_mm2=first_area,elevated_downward_horizontal_area_mm2=float(after.area_faces[roof].sum())))
assert len(rows)==25 and sum(r['quantity'] for r in rows)==30
assert len(list((OUT/'PETG').glob('*.stl')))==25
(OUT/'Druckliste.json').write_text(json.dumps(rows,indent=2,ensure_ascii=False)+'\n')
with (OUT/'Druckliste.csv').open('w',newline='') as f:
    w=csv.writer(f,delimiter=';');w.writerow(['Datei','Anzahl','Material','Bezeichnung','Abmessungen mm','Druckhinweis'])
    for r in rows:w.writerow([r['file'],r['quantity'],r['material'],r['description'],' × '.join(map(str,r['bounds_mm'])),r['note']])
(OUT/'validation.json').write_text(json.dumps(dict(status='PASS',unique_parts=25,print_quantity=30,
    nominal_geometry_unchanged=True,rotated_parts=rotations,meshes=checks,
    scope='Closed meshes, rigid orientation only, nominal shape/volume preserved; printability judged with actual slicer/support review'),indent=2)+'\n')
shutil.copyfile(BASE/'source/fingerworker_RevC.fs',OUT/'source/fingerworker_RevC.fs')
shutil.copyfile(BASE/'assembly-validation.json',OUT/'assembly-validation.json')
print('PASS: 25 device meshes, 30 pieces; four rigid orientations changed, nominal geometry preserved')
