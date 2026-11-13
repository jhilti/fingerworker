#!/usr/bin/env python3
"""Compose the continuous palm from the frozen R12 source."""
from pathlib import Path
import hashlib,importlib.util,json
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
BASE=ROOT/'review/simplification-2026-11-03/fingerworker_R12_simplified.fs'
s=importlib.util.spec_from_file_location('r13_palm',HERE/'mechanics/simple_palm.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(BASE)=='730cd21ea3aafbe43bf8eb38007b20d9cd0272659430d8a2b3b6245f33f62455'
source=m.patch_source(BASE.read_text())
source=source.replace('Fingerworker Flat132 R12 - simplified PLA click assembly.','Fingerworker Flat132 R13 - continuous rounded palm support.\n * One constant-radius palm rail and a broad web absorb old steps and ribs.\n * R12 electronics underside, click catches, sensor and rod interfaces remain.\n * Only P01 changes; the other92 native bodies and all functions are retained.')
source=source.replace('"Flat132 R12 - simplified click assembly"','"Flat132 R13 - continuous palm support"')
source=source.replace('        // One M6x1 screw translates the complete sensor support, cell, pusher\n        // and yoke. Both seats therefore advance equally, without bypassing\n        // the sensor. Hardware below is nominal/unthreaded CAD envelope only.\n','        // Fixed sensor reaction with no preload adjustment.\n')
source=source.replace('"R10 construction region - solid palm and braces, fused into P01 at feature end"','"Palm construction region, fused into the continuous P01 support at feature end"')
source=source.replace('// Main wall is6.75 mm deep; new upper bridge remains inside35 mm height.','// Fixed wall is6.75 mm deep; sensor-side protection remains within35 mm height.')
out=HERE/'fingerworker_R13_simple_palm.fs';out.write_text(source)
report={'status':'SOURCE_COMPOSED_PENDING_NATIVE_REGENERATION','baseline_source_sha256':sha(BASE),'source_sha256':sha(out),'changed':['P01'],'new':[],'removed':[],'device_prints':7,'fit_pieces':10,'native_solids':93,'new_prints_required':['P01']}
(HERE/'source-build.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
