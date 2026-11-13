"""Build an unsliced, printer-independent Bambu Studio STL assessment pack."""
from pathlib import Path
import json, shutil, hashlib, struct, collections, csv, zipfile
import cadquery as cq

ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parents[1]
FAB=ROOT/'mechanical/manufacturing-2026-10-11'
rows=[]
def register(path,qty,description,origin,note):
    rows.append(dict(file=str(path.relative_to(OUT)),quantity=qty,description=description,
                     material='TPU 95A' if 'TPU' in path.name else 'PETG',source=origin,note=note))
for material in ['PETG','TPU']:(OUT/material).mkdir(exist_ok=True)
for src in sorted((ROOT/'print/rear-tether-2026-09-29/parts').glob('*.stl')):
    if src.name.startswith(('P01','P02','P060','P061')):continue
    dest=OUT/('TPU' if 'TPU' in src.name else 'PETG')/src.name
    shutil.copyfile(src,dest)
    register(dest,1,src.stem,str(src.relative_to(ROOT)),'Vorhandene geprüfte Druckorientierung; siehe Druckanleitung.')
for name,desc in [('P01_base_6mm_AssemblyClear_RevB_2026-10-13','Grundplatte 6 mm, freier Einschub'),('P060_rear_retainer_left_RevC_2026-10-13','Hinterer Halter links, tiefere Auflage'),('P061_rear_retainer_right_RevC_2026-10-13','Hinterer Halter rechts, tiefere Auflage')]:
    src=ROOT/('print/assembly-clear-2026-10-13/parts' if name.startswith('P01') else 'print/assembly-final-2026-10-13/parts')/(name+'.stl')
    dest=OUT/'PETG'/src.name;shutil.copyfile(src,dest)
    register(dest,1,desc,str(src.relative_to(ROOT)),'Live-Onshape 13.10.2026, Halter RevC; P01/P060/P061 gemeinsam ersetzen.')
for src in sorted((FAB/'stl').glob('*.stl')):
    dest=OUT/'PETG'/src.name;shutil.copyfile(src,dest)
    register(dest,1,src.stem,str(src.relative_to(ROOT)),'Aktuelle Gehäuserevision inklusive P02-Montagepiloten.')
specs={
 'H02_Pusher':(1,'Druckstift, Anschauung ohne Gewindefunktion',False),
 'H04_Guide_rod':(2,'Führungsstab Ø6 × 146, Anschauung',False),
 'H05_Fixed_spring_seat':(2,'Fester Federsitz',True),
 'H06_Moving_spring_seat':(2,'Beweglicher Federsitz',True),
 'H12_Sensor_cassette':(1,'Sensorkassette',True),
 'H15_Keeper':(1,'Halteplatte',True),
 'H19_Spacer':(2,'Abstandshülse',True),
 'H22_Brass_pad':(1,'Druckstück Ø2,5 × 1, Anschauung',True),
 'H14_Isometric_sleeve':(2,'Optionale Isometriehülse',True),
}
for name,(qty,description,vertical) in specs.items():
    src=FAB/'step'/f'{name}.step'
    s=cq.importers.importStep(str(src)).val()
    assert s.isValid() and len(s.Solids())==1
    if vertical:s=s.rotate((0,0,0),(0,1,0),-90)
    bb=s.BoundingBox();s=s.translate((-bb.xmin,-bb.ymin,-bb.zmin))
    dest=OUT/'PETG'/f'{name}_PRINT_MOCKUP.stl'
    cq.exporters.export(s,str(dest),tolerance=.015,angularTolerance=.06)
    register(dest,qty,description,str(src.relative_to(ROOT)),
             'Metall-Nennform; Kernlöcher/glatte Gewindehüllform, keine gedruckten Gewinde. '
             +('Flache Stirn-/Rückfläche unten; Stützen bei Bedarf.' if vertical else 'Liegend; lokale Stützen unter Rundung/Schulter und Haftungsrand.'))
# The threaded H11 nut and H13 screw shaft are deliberately not included.
# Only the wheel envelope is useful for visual assessment without printing screws.
s=cq.Solid.makeCylinder(11,2.8).cut(cq.Solid.makeCylinder(3.2,2.8))
dest=OUT/'PETG/H13_Handwheel_ONLY_PRINT_MOCKUP.stl'
cq.exporters.export(s,str(dest),tolerance=.015,angularTolerance=.06)
register(dest,1,'Handrad Ø22 × 2,8, Bohrung Ø6,4; ohne Schraubenschaft',
         'H13 nominal wheel envelope; separate assessment variant',
         'Flach drucken; glatte Anschauungsform ohne Rändelung. Kein funktionsfähiger Gewindeeinsteller.')

checks=[]
for row in rows:
    p=OUT/row['file'];raw=p.read_bytes();n=struct.unpack_from('<I',raw,80)[0]
    assert len(raw)==84+50*n,p
    edges=collections.Counter();volume=0;pts=[]
    for i in range(n):
        v=struct.unpack_from('<12fH',raw,84+50*i)
        tri=[tuple(round(x,5) for x in v[j:j+3]) for j in [3,6,9]]
        assert len(set(tri))==3,p
        for a,b in zip(tri,tri[1:]+tri[:1]):edges[tuple(sorted((a,b)))]+=1
        a,b,c=tri
        volume+=(a[0]*(b[1]*c[2]-b[2]*c[1])+a[1]*(b[2]*c[0]-b[0]*c[2])+a[2]*(b[0]*c[1]-b[1]*c[0]))/6
        pts.extend(tri)
    assert all(v==2 for v in edges.values()) and volume>0,p
    lo=[min(v[i] for v in pts) for i in range(3)]
    hi=[max(v[i] for v in pts) for i in range(3)]
    assert abs(lo[2])<.001,(p,lo)
    row['bounds_mm']=[round(hi[i]-lo[i],3) for i in range(3)]
    row['sha256']=hashlib.sha256(raw).hexdigest()
    checks.append(dict(file=row['file'],closed=True,volume_mm3=volume,triangles=n,bounds_mm=row['bounds_mm']))
assert len(list((OUT/'PETG').glob('*.stl')))+len(list((OUT/'TPU').glob('*.stl')))==len(rows), 'Unexpected stale STL in print pack'
assert len(rows)==24 and sum(r['quantity'] for r in rows)==29
(OUT/'Druckliste.json').write_text(json.dumps(rows,indent=2,ensure_ascii=False)+'\n')
with (OUT/'Druckliste.csv').open('w',newline='') as f:
    w=csv.writer(f,delimiter=';');w.writerow(['Datei','Anzahl','Material','Bezeichnung','Abmessungen mm','Hinweis'])
    for r in rows:w.writerow([r['file'],r['quantity'],r['material'],r['description'],' × '.join(map(str,r['bounds_mm'])),r['note']])
(OUT/'validation.json').write_text(json.dumps(dict(status='PASS',unique_parts=len(rows),print_quantity=29,
    scope='Closed positive-volume meshes, floor orientation, quantities and provenance; no physical load qualification',meshes=checks),indent=2)+'\n')
archive=ROOT/'print/Fingerworker_Alle_Druckteile_Bambu_RevC_2026-10-13.zip'
shutil.copyfile(ROOT/'review/assembly-clear-2026-10-13/validation.json',OUT/'assembly-validation.json')
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
    for p in sorted(OUT.rglob('*')):
        if p.is_file():z.write(p,Path('Fingerworker_Alle_Druckteile')/p.relative_to(OUT))
with zipfile.ZipFile(archive) as z:assert z.testzip() is None
print(f'PASS: {len(rows)} unique STLs, 29 printed pieces; archive {archive}')
