#!/usr/bin/env python3
"""Compose the reviewed R11 patches from the frozen native R10 source."""
from pathlib import Path
from hashlib import sha256
import importlib.util, json

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
BASE=ROOT/'review/flat132-integrated-palm-2026-11-03/fingerworker_flat132_integrated_palm.fs'

def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    return mod

raw=BASE.read_bytes()
assert sha256(raw).hexdigest()=='5ce830ff2b06cd8d318d3c44dbc1f3385697526a9a679d2a2078f64f81854237'
rear=module('rear',HERE/'patch_rear_shoes.py')
enclosure=module('enclosure',HERE/'enclosure/build_enclosure.py')
source=enclosure.source_patch(rear.patch_source(raw.decode()))
source=source.replace('''    opBoolean(context, id, { "tools" : qUnion(bodies),
        "operationType" : BooleanOperationType.UNION });''', '''    if (size(evaluateQuery(context,qBodyType(qUnion(bodies),BodyType.SOLID))) < 2)
        throw regenError("R11 union requires two separate solids: " ~ toString(id));
    opBoolean(context, id, { "tools" : qUnion(bodies),
        "operationType" : BooleanOperationType.UNION });''')
source=source.replace('Fingerworker MVP - R10 integral frame and solid palm CAD prototype.',
    'Fingerworker MVP - R11 PLA click assembly CAD prototype.\n * R10 main frame and service access remain unchanged. P08/P09 receive\n * accessible long clips; former P10 wire clamp belongs to P09. Four small\n * P07 lands belong to P120/P121. Other functional retainers remain hardware.')
target=HERE/'fingerworker_flat132_PLA_click.fs'
target.write_text(source)
record=dict(status='SOURCE_COMPOSED_PENDING_NATIVE_REGENERATION',date='2026-11-03',
    baseline_source=str(BASE.relative_to(ROOT)),baseline_sha256=sha256(raw).hexdigest(),
    source_sha256=sha256(target.read_bytes()).hexdigest(),
    changed=['P08','P09','P120','P121'],removed=['P10','P070a','P070b','P071a','P071b'],
    P01_geometry='Unchanged R10 main frame, preserves existing print',
    material='PLA',P04='Geometry unchanged; Xmin-down bed-only slim-tree print orientation')
(HERE/'source-build.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record,indent=2))
