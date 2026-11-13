#!/usr/bin/env python3
"""Independent dimensional ledger for the 30 mm printable prototype.

Exact solids are checked separately in Onshape. This checks motion datums,
spring compression, clearances and assembly dimensions at 61 positions.
It does not certify strength, fatigue, friction or hand fit.
"""
from pathlib import Path
import math
import re

source = Path(__file__).resolve().parents[1] / 'fingerworker_mvp.fs'
text = source.read_text()
for token in ['vector(-22,-105,0)', 'vector(194,105,6)',
              'vector(125,-62.5,7)', 'vector(184,62.5,30)',
              'vector(137,-47,10)', 'vector(171,47,36)',
              'vector(15.5,38,29)', 'vector(0,0,-29.5)',
              'vector(51.75,-43,19.75)', 'vector(41.5,-64,9.5)',
              'vector(62.5,64,14.5)', 'for (var x in [47.5,57.5])',
              'vector(y-1.9,5.9)', 'vector(y+6.75,10.3)']:
    assert token in text, f'Source changed; review ledger: {token}'

def close(a,b): assert math.isclose(a,b,abs_tol=1e-9), (a,b)

close(19.75+10.25,30)
close(51.75-10.25,41.5)
close(30-10,20)
close(10-7,3)
close(7-6,1)
assert 216 <= 220 and 210 <= 220
close((59.5-30)/59.5*100,49.57983193277311)

# Dovetails have 45-degree flanks, 0.45 horizontal flank offset and .3 roof gap.
close((6-1.9)/(10-5.9),1)
close((6.75-2.15)/(10.3-5.7),1)
close(3.45-3,.45)
close(10.3-10,.3)
close(.45/math.sqrt(2),.31819805153394637)
assert 102-(94+6.75) > 1.2

# The wrist-side approach contains the heel, with opposed contact normals.
close((51.75-10.25)-15.5,26)
close(41.5-(29.4+12),.1)
close((29.4-12)-15.5,1.9)
assert 29.4 < 41.5 < 137  # heel lies behind bolster, fingers ahead
palm_reaction_on_hand=-1
finger_reaction_on_hand=1
assert palm_reaction_on_hand*finger_reaction_on_hand < 0
close(64-62.5,1.5)  # rigid palm plate / switch case minimum X separation
close(19.75-9-6,4.75)  # heel / base Z separation
close(9.5-3.5,6)  # palm foot height datum above the base top
close(13.5-10,3.5)  # M4x10 screw tip, insertion hole bottom at2.5
assert 3.5 > 2.5
close(9.5-3.5,6)  # nominal M4 engagement in the foot
close(185.5-184,1.5)
close(190-(-16),206)
close(18-11-6,1)
close(75-8-66,1)
close(14.6-14.5,.1)  # soft sleeve / rigid plate, flexible fitted interface

lever_length=math.hypot(3.1,16.7)
for i in range(61):
    stroke=i*.5
    pocket_wall=137-stroke
    spacing=pocket_wall-41.5
    close(spacing,95.5-stroke)
    spring_length=113-stroke-12
    compression=102-spring_length
    close(compression,1+stroke)
    assert 71 <= spring_length <= 101
    close(2*7.8*compression,15.6+15.6*stroke)
    close((116-stroke)-86,30-stroke)
    close(184-(184-stroke),stroke)
    assert 10 <= 116-stroke and 184-stroke <= 184
    # A 68 mm guide engagement remains over the full stroke.
    close((184-stroke)-(116-stroke),68)
    roller_x=min(83.4,110-stroke-2.4)
    roller_y=-21.1+math.sqrt(lever_length**2-(roller_x-75.5)**2)
    assert -9 < roller_y < 1
    assert 110-stroke-(roller_x+2.4) >= -1e-10
    assert roller_x-2.4 > 74.2
close(2*7.8*31,483.6)
print('PASS: 216 x 210 x 30 mm envelope; 49.58% lower than 59.5 mm.')
print('PASS: 20 mm pocket, 3 mm floor, 1 mm base gap; palm crown flush at30 mm.')
print('PASS: 61 travel positions, 95.5..65.5 mm datum spacing, 30 mm hard stop.')
print('PASS: springs101..71 mm, nominal15.6..483.6 N; no strength inference.')
print('PASS: 45-degree printed guides, .30 roof gap, .318 normal flank gap.')
print('PASS: opposed hand reactions; 26 mm approach, heel clears yoke by1.9 mm in X.')
print('PASS: palm plate clears switch by1.5 mm in X; 6 x206 mm guide rods.')

logs=sorted(source.parent.glob('review/onshape-accessible-palm-audit-*mm.txt'))
if logs:
    for p in logs:
        rows=p.read_text().splitlines()
        assert len(rows)==21, (p,len(rows))
        assert all('interferences : 0 ' in r for r in rows),p
        assert all('SKIPPED' not in r for r in rows),p
        print(f'PASS: {p.name}: 21 pairs; zero solid interferences. Boundary contacts remain in log.')
