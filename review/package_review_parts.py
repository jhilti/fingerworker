#!/usr/bin/env python3
"""Package Onshape's eleven STL exports, orienting each part for printing.

Rigid rotations/translations only; units remain millimetres, no scaling or
mesh repair. Validate closed edges, positive volume, dimensions and file count.
"""
from pathlib import Path
from collections import Counter
import struct, zipfile, hashlib, json, shutil

root=Path(__file__).resolve().parents[1]
source=root/'review/full-review-2026-09-21/Onshape_open_all_parts.zip'
out=root/'print'/'review-2026-09-21'/'parts';out.mkdir(parents=True,exist_ok=True)
names={'P01':'base','P02':'palm_bolster','P03':'palm_sleeve_TPU',
       'P04':'climbing_carriage','P05':'floating_yoke',
       'P060':'rear_retainer_left','P061':'rear_retainer_right',
       'P070a':'return_pad_left_a_TPU','P070b':'return_pad_left_b_TPU',
       'P071a':'return_pad_right_a_TPU','P071b':'return_pad_right_b_TPU'}
def rotate(v,key):
    x,y,z=v
    if key=='P03': return (x,-z,y)  # sleeve axis stands vertical
    if key.startswith('P07'): return (-z,y,x)  # 1.5 mm pad thickness vertical
    return v

report={'source':'Onshape, compact central guide and exterior wrist-side palm, 21 September 2026; final 0 mm pose, preload 0 mm, light springs, hand/electronics off; binary STL, millimetres, Fine',
        'source_zip_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
        'cad_source_sha256':hashlib.sha256((root/'fingerworker_mvp.fs').read_bytes()).hexdigest(),
        'parts':[]}
with zipfile.ZipFile(source) as archive:
    files=[n for n in archive.namelist() if n.split(' - ')[1].split()[0] in names];assert len(files)==11
    for filename in files:
        assert filename.endswith('.stl') and '/' not in filename
        key=filename.split(' - ')[1].split()[0];assert key in names
        data=archive.read(filename)
        count=struct.unpack_from('<I',data,80)[0];assert len(data)==84+50*count
        triangles=[];normals=[]
        for i in range(count):
            vals=struct.unpack_from('<12fH',data,84+50*i)
            normals.append(rotate(vals[:3],key))
            triangles.append([rotate(vals[j:j+3],key) for j in (3,6,9)])
        mins=tuple(min(v[i] for t in triangles for v in t) for i in range(3))
        maxs=tuple(max(v[i] for t in triangles for v in t) for i in range(3))
        triangles=[[tuple(v[i]-mins[i] for i in range(3)) for v in t] for t in triangles]
        edges=Counter()
        volume=0
        for tri in triangles:
            points=[tuple(round(x,5) for x in p) for p in tri]
            for a,b in zip(points,points[1:]+points[:1]):
                if a!=b: edges[tuple(sorted((a,b)))]+=1
            a,b,c=tri
            volume+=(a[0]*(b[1]*c[2]-b[2]*c[1])+a[1]*(b[2]*c[0]-b[0]*c[2])+a[2]*(b[0]*c[1]-b[1]*c[0]))/6
        bad_edges=sum(v!=2 for v in edges.values())
        assert bad_edges==0,(key,bad_edges)
        assert volume>0,(key,volume)
        size=tuple(maxs[i]-mins[i] for i in range(3))
        if key=='P01':
            assert all(abs(a-b)<.01 for a,b in zip(size,(156,180,29))),size
        if key=='P04':
            assert all(abs(a-b)<.01 for a,b in zip(size,(60,174,25))),size
        assert max(size[:2])<=220
        binary=bytearray(b'Fingerworker printable part; mm; rigid orientation only'.ljust(80,b'\0'))
        binary.extend(struct.pack('<I',count))
        for normal,tri in zip(normals,triangles):
            binary.extend(struct.pack('<12fH',*normal,*tri[0],*tri[1],*tri[2],0))
        target=out/f'{key}_{names[key]}.stl';target.write_bytes(binary)
        report['parts'].append({'file':target.name,'triangles':count,
            'size_mm':[round(x,3) for x in size],'volume_mm3':round(volume,3),
            'nonmanifold_edges_at_1e-5mm':bad_edges,
            'sha256':hashlib.sha256(binary).hexdigest()})
        print(f'{target.name}: closed mesh; {count} facets; '+ ' x '.join(f'{x:.2f}' for x in size)+' mm')

previous=json.loads((root/'review'/'low-profile-print-validation.json').read_text())
old_volume=sum(p['volume_mm3'] for p in previous['parts'])
new_volume=sum(p['volume_mm3'] for p in report['parts'])
report['material_comparison']={'previous_solid_volume_cm3':round(old_volume/1000,3),
    'current_solid_volume_cm3':round(new_volume/1000,3),
    'reduction_percent':round((1-new_volume/old_volume)*100,2),
    'meaning':'Geometric volume of eleven printable solids; actual filament depends on infill, walls and supports.'}
print(report['material_comparison'])
report['manufacturing_release']=False
report['limitations']=['Development meshes only. Real-hand fit, force rating and assembly tests remain open.','No geometry repair/scaling; rigid print orientation only. Metal parts excluded.']
(root/'review/full-review-print-validation.json').write_text(json.dumps(report,indent=2)+'\n')
print('Fresh development part set saved to',out)
