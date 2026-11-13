#!/usr/bin/env python3
"""Write watertight STL fit coupons matching the CAD dovetail cross-sections.
Millimetres. The female bottom sits at Z4 over the male at Z0 in an assembled
test; print separately, both flat bottoms down. No source CAD export required.
"""
from pathlib import Path
import math
import struct
from collections import Counter

out=Path(__file__).resolve().parents[1]/'print'
out.mkdir(exist_ok=True)

def cross(a,b,c): return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
def triangulate(p):
    indices=list(range(len(p))); result=[]
    while len(indices)>3:
        for k,b in enumerate(indices):
            a,c=indices[k-1],indices[(k+1)%len(indices)]
            if cross(p[a],p[b],p[c])<=1e-10: continue
            def inside(v):
                return all(cross(p[i],p[j],p[v])>=-1e-10 for i,j in [(a,b),(b,c),(c,a)])
            if any(inside(v) for v in indices if v not in (a,b,c)): continue
            result.append((a,b,c));indices.pop(k);break
        else: raise ValueError('Cannot triangulate polygon')
    return result+[tuple(indices)]

def write_prism(name,points):
    vertices=[(x,y,z) for x in (0.,30.) for y,z in points]
    n=len(points); end=triangulate(points)
    triangles=[tuple(reversed(t)) for t in end]+[tuple(i+n for i in t) for t in end]
    for i in range(n):
        j=(i+1)%n
        triangles.extend([(i,j,j+n),(i,j+n,i+n)])
    edges=Counter(tuple(sorted((t[i],t[(i+1)%3]))) for t in triangles for i in range(3))
    assert all(c==2 for c in edges.values())
    volume=0; data=bytearray(b'Fingerworker 30 mm guide fit coupon'.ljust(80,b'\0'))
    data.extend(struct.pack('<I',len(triangles)))
    for t in triangles:
        a,b,c=(vertices[i] for i in t)
        u=tuple(b[i]-a[i] for i in range(3));v=tuple(c[i]-a[i] for i in range(3))
        normal=(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0])
        length=math.sqrt(sum(x*x for x in normal)); assert length>0
        normal=tuple(x/length for x in normal)
        volume+=(a[0]*(b[1]*c[2]-b[2]*c[1])+a[1]*(b[2]*c[0]-b[0]*c[2])+a[2]*(b[0]*c[1]-b[1]*c[0]))/6
        data.extend(struct.pack('<12fH',*normal,*a,*b,*c,0))
    assert volume>0
    path=out/name;path.write_bytes(data)
    print(f'{path.name}: watertight, {len(triangles)} triangles, volume{volume:.1f} mm3')

write_prism('guide_coupon_male.stl',[(-21,0),(21,0),(21,3),(13,3),(16,6),(-16,6),(-13,3),(-21,3)])
write_prism('guide_coupon_female.stl',[(-21,0),(-14.45,0),(-16.75,2.3),(16.75,2.3),(14.45,0),(21,0),(21,5),(-21,5)])
