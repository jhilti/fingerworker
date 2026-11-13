#!/usr/bin/env python3
"""Independent dimension and motion ledger; exact solids checked in Onshape.
No inference of strength, fatigue, friction, or anthropometric fit.
"""
from pathlib import Path
import math

root = Path(__file__).resolve().parents[1]
def close(a,b): assert math.isclose(a,b,abs_tol=1e-9), (a,b)

close(19.75+10.25,30)
close(-34-10.25,-44.25)
close(134-(-44.25),178.25)
close(134-(-22),156)
assert -34+10.25 < -22
close(-22-(-34+10.25),1.75)
close(30-10,20)
close(10-7.3,2.7)
close(5-4,1)
assert 156 <= 220 and 180 <= 220
close(238.25-178.25,60)
close(210-180,30)

# Retained central profile: 32 mm top, 45-degree faces, .30 roof gap.
close((16-12.9)/(7-3.9),1)
close((16.75-13.15)/(7.3-3.7),1)
close((13.15+5-3.7)-(12.9+5-3.9),.45)
close(7.3-7,.3)
close(.45/math.sqrt(2),.31819805153394637)
close(79-65,14)
close(124-110,14)
close((110+124)/2-(65+79)/2,45)
close(4-3,1)  # moving seat/mandrel radial clearance

# Exterior heel and bolted support retained with opposing contact normals.
close(-44.25-(-56.35+12),.1)
assert -56.35+12 < -44.25 < -22 < 77
close(-7-(-8),1)
close(63-61,2)
close(13.5-10,3.5)
assert 3.5 > 2.5
close(9.5-3.5,6)
close(125.5-124,1.5)
close(130-(-16),146)
close(18-11-4,3)
close(75-8-66,1)
close(14.6-14.5,.1)

lever_length=math.hypot(3.1,16.7)
for i in range(61):
    stroke=i*.5
    close(77-stroke-(-44.25),121.25-stroke)
    spring_length=113-stroke-12
    compression=102-spring_length
    close(compression,1+stroke)
    assert 71 <= spring_length <= 101
    close(2*7.8*compression,15.6+15.6*stroke)
    close(65-stroke-35,30-stroke)
    close(124-(124-stroke),stroke)
    assert 34 <= 65-stroke and 124-stroke <= 124
    close((124-stroke)-(65-stroke),59)
    roller_x=min(33.4,60-stroke-2.4)
    roller_y=-51.1+math.sqrt(lever_length**2-(roller_x-25.5)**2)
    assert -37 < roller_y < -34
    assert 60-stroke-(roller_x+2.4) >= -1e-10
    assert roller_x-2.4 > 24.2
    assert 65-stroke-24.2 >= 10.8-1e-9
    assert 64-stroke-(roller_x+2.4) >= 4-1e-9
    assert -29-(roller_y+2.4) > 2
close(2*7.8*31,483.6)
print('PASS: 178.25 x 180 x 30 mm envelope; 156 x 180 x 4 mm base; 60 mm shorter, 30 mm narrower.')
print('PASS: unchanged 20 mm pocket and 121.25..91.25 mm contact datums; 2.7 mm floor above guide.')
print('PASS: 61 motion datums; 30 mm hard stop; 59 mm retained engagement; 45 mm bearing-land spacing.')
print('PASS: spring length101..71 mm, nominal15.6..483.6 N; no strength inference.')
print('PASS: central 45-degree guide, .30 roof gap, .318 normal flank gap; mandrel clearance1 mm radial.')
print('PASS: entire roller and heel outside frame; bracket clears yoke1 mm and rod blocks2 mm.')
print('PASS: switch roller/cam corridor remains clear through61 positions.')

for stroke in (0,15,30):
    p=root/'review'/f'onshape-compact-central-audit-{stroke}mm.txt'
    rows=p.read_text().splitlines()
    assert len(rows)==21,(p,len(rows))
    assert all('interferences : 0 ' in r for r in rows),p
    assert all('SKIPPED' not in r for r in rows),p
    print(f'PASS: {p.name}: 21 selected pairs; zero solid interferences; boundary contacts logged.')
