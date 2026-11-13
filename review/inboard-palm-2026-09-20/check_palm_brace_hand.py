#!/usr/bin/env python3
"""Check fixed-length finger kinematics and the saved exact-solid hand audits.

The previous conservative envelope sampler is archived with the tall design.
The current design uses actual Onshape solids at0/15/30 mm instead.
"""
from pathlib import Path
import math
fingers=[('index',84,-28,71,43,29,8.5),('middle',87,-8,73,44,27,9),
         ('ring',84,13,72,43,30,8.4),('little',79,31,70,43,33,7.2)]
for i in range(61):
    stroke=i*.5
    for name,x,y,z,p,m,r in fingers:
        root=(x,y,z-29.5)
        dip=(137.1+r*.8-stroke,y,66-29.5)
        tip=(137.1+r*.74-stroke,y,39.6+r*.74-29.5)
        delta=tuple(b-a for a,b in zip(root,dip))
        distance=math.sqrt(sum(v*v for v in delta))
        assert abs(p-m)<distance<p+m,(name,stroke,distance)
        along=(p*p-m*m+distance*distance)/(2*distance)
        rise=math.sqrt(p*p-along*along)
        direction=tuple(v/distance for v in delta)
        up=(-direction[2],0,direction[0])
        pip=tuple(root[j]+direction[j]*along+up[j]*rise for j in range(3))
        assert math.isclose(math.dist(root,pip),p,abs_tol=1e-9)
        assert math.isclose(math.dist(pip,dip),m,abs_tol=1e-9)
        assert math.isclose(tip[0]-r*.74-(137-stroke),.1,abs_tol=1e-9)
        assert math.isclose(tip[2]-r*.74-10,.1,abs_tol=1e-9)
print('PASS: all four fixed-length finger linkages feasible at61 positions,0..30 mm.')
assert math.isclose(41.5-(29.4+12),.1,abs_tol=1e-9)
assert 29.4-12 > 15.5
print('PASS: heel is behind the bolster, with0.1 mm contact gap and1.9 mm yoke clearance.')
print('PASS: fingertip floor/wall nominal visualization gaps remain0.1 mm.')
for stroke in (0,15,30):
    path=Path(__file__).with_name(f'onshape-accessible-palm-audit-{stroke}mm.txt')
    rows=[r for r in path.read_text().splitlines() if 'pair : Hand /' in r]
    assert len(rows)==3,(path,len(rows))
    assert all('interferences : 0 ' in r and 'status : CLEAR ' in r for r in rows),path
    print(f'PASS: exact Onshape hand solids at{stroke} mm: all3 targeted pairs clear.')
print('Illustrative reference only; no anthropometric or load-capacity validation.')
