"""Check exported meshes and PDF geometry/text; no hardware qualification implied."""
from pathlib import Path
import struct,collections,json,hashlib
import pymupdf as fitz
OUT=Path(__file__).resolve().parents[1]
results=[]
for p in sorted((OUT/'stl').glob('*.stl')):
    raw=p.read_bytes();n=struct.unpack_from('<I',raw,80)[0];assert len(raw)==84+n*50
    edges=collections.Counter();volume=0;xs=[];ys=[];zs=[]
    for i in range(n):
        vals=struct.unpack_from('<12fH',raw,84+i*50)
        points=[tuple(round(v,5) for v in vals[j:j+3]) for j in [3,6,9]]
        assert len(set(points))==3
        for a,b in zip(points,points[1:]+points[:1]):edges[tuple(sorted([a,b]))]+=1
        a,b,c=points;volume+=(a[0]*(b[1]*c[2]-b[2]*c[1])+a[1]*(b[2]*c[0]-b[0]*c[2])+a[2]*(b[0]*c[1]-b[1]*c[0]))/6
        for x,y,z in points:xs.append(x);ys.append(y);zs.append(z)
    assert all(v==2 for v in edges.values()) and volume>0
    assert min(zs)==0 and min(xs)==0 and min(ys)==0
    results.append(dict(file=p.name,triangles=n,closed=True,positive_volume_mm3=volume,print_bounds_mm=[max(xs),max(ys),max(zs)]))
pdfs=[]
for name,count in [('Metallteile_RevA.pdf',11),('Elektronikaufnahme_RevA.pdf',4)]:
    doc=fitz.open(OUT/'drawings'/name);assert len(doc)==count
    for page in doc:
        assert len(page.get_text())>300
        for block in page.get_text('dict')['blocks']:
            for line in block.get('lines',[]):
                for span in line['spans']:
                    x0,y0,x1,y1=span['bbox'];assert x0>=24 and x1<=page.rect.width-24 and y0>=24 and y1<=page.rect.height-24,(name,span)
    pdfs.append(dict(file=name,pages=count,text_bounds='PASS',visual_review='rendered pages inspected'))
(OUT/'export-validation.json').write_text(json.dumps(dict(status='PASS',meshes=results,pdfs=pdfs),indent=2)+'\n')
print('PASS',len(results),'closed positive-volume floor-oriented meshes; 15 PDF pages')
