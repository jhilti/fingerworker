#!/usr/bin/env python3
"""Dimensional checks only; not a FeatureScript compiler or solid/strength test."""
from pathlib import Path
import hashlib
import json
import math

root = Path(__file__).resolve().parents[1]
source = (root / 'fingerworker_mvp.fs').read_text()
def close(a, b):
    assert math.isclose(a, b, abs_tol=1e-9), (a, b)

cases = 0
for j in range(21):
    p = j / 10
    # Axial endpoints of the independently translated force stack.
    cassette_back, cassette_front = -12+p, -8+p
    yoke_back = -7+p
    close(cassette_front + 5.45 + .65 + 2.9, 1+p)
    close(yoke_back-cassette_front, 1)
    close((-13+p)-cassette_back, -1)  # wheel clears plate by 1 mm
    assert (-15.8+p)-(-16) >= .2-1e-9  # wheel/fixed wall
    assert min(-16, -12+p)-max(-21, -24+p) >= 5  # nut thread engagement
    assert min(-8,cassette_front)-max(-16.2,cassette_back) >= 2  # guide overlap
    assert (-7+p)-(-8) >= 1  # yoke / fixed guide tips
    for i in range(61):
        x = i / 2
        left = right = 12+p
        moving_seat = 113-x
        length = moving_seat-left
        close(left, right)
        assert 69 <= length <= 101
        compression = 102-length
        close(compression, 1+p+x)
        # Illustrative light coil should not self-intersect axially.
        assert length/25 > 2
        for k, free_length, minimum_length in ((3.307,102,58.59),(3.709,105,56.14)):
            assert length > minimum_length
            force = 2*k*(free_length-length)
            close(force-2*k*(free_length-101+p), 2*k*x)
            assert force > 0
            cases += 1
        assert 65-x >= 35  # retained original hard stop
    locked_travel = 15-p
    sleeve_length = (113-locked_travel)-(12+p)
    close(sleeve_length, 86)
    assert 13 <= locked_travel <= 15
    assert 65-locked_travel-35 >= 15  # no base stop bypass
    assert 60-locked_travel > 31  # switch does not detect isometric hold
    close(121.25-locked_travel, 106.25+p)

for token in ('definition.preloadAdjustment', 'definition.lightSprings',
              'definition.isometricLock', '"synchronizedPreload"',
              '"isoSleeve"~s', '"sensorCassette"', '"nutKeeper"'):
    assert token in source, token
for token in ('6.4 : 6.25', '3.307 : 3.709', '102 : 105', '0X-DF2194', '0X-DF2185'):
    assert token in source, token
# Ensure both seats AND sensor members share the same translation operation.
translation = source.split('opTransform(context,id + "synchronizedPreload",')[1].split('println')[0]
for member in ('springAnchor','fixedSeat0','fixedSeat1','sensorCassette','loadCell',
               'loadCellBoss','loadPusher','loadCellCable','preloadScrew','captureScrew0','captureScrew1','captureSpacer0','captureSpacer1','pusherNut'):
    assert f'body(id + "{member}")' in translation, member
# Physical shoulder-spacer slots permit nominal centers -13..-11 mm.
close((-9-2)-(-15+2),2)
# Flush keeper heads stop at X-23; minimum palm-sleeve X-23.75.
assert -23-(-23.75) >= .75
# Pusher shoulder bears on the printed yoke over a larger annulus.
assert math.pi*(4**2-1.6**2)>42
report = {
    'status': 'PASS: dimensional ledger and source wiring only',
    'dynamic_force_cases': cases,
    'isometric_preload_positions': 21,
    'DF2194_pair_force_N': {'p0':[6.614,205.034], 'p2':[19.842,218.262]},
    'DF2185_pair_force_N': {'p0':[29.672,252.212], 'p2':[44.508,267.048]},
    'spring_installed_length_mm':[69,101],
    'isometric_sleeve_length_mm':86,
    'cad_source_sha256':hashlib.sha256(source.encode()).hexdigest(),
    'scope':'Local dimensional/source checks for ordered springs; fresh Onshape checks are separately bound in enclosure-2026-10-11/cad-validation.json',
    'manufacturing_release':False,
}
(root/'review/device-upgrades-validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
