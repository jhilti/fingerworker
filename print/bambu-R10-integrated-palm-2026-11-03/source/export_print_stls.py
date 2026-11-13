"""Export exact native meshes using the saved rigid print transforms only."""
from pathlib import Path
from hashlib import sha256
import json,numpy as np,trimesh as tm
OUT=Path(__file__).resolve().parents[1]
layout=json.loads((OUT/'plate-layout.json').read_text());target=OUT/'STL-print-oriented';audit=[]
for r in layout['placements']:
    key=r['ref'];src=OUT/'source-mm'/f'{key}.stl';assert sha256(src.read_bytes()).hexdigest()==r['source_sha256']
    m=tm.load_mesh(src);original=m.copy();m.vertices=m.vertices@np.array(r['rotation_3x3']).T+np.array(r['normalization_translation_mm'])
    suffix='_INTEGRATED_SOLID_PALM' if key=='P01' else '_HARD_PLA_PROXY_NO_LOAD' if key.startswith(('P07','H04')) else '_UNLOADED_TEST_FIXTURE' if key=='Q01' else ''
    p=target/f'{key}{suffix}.stl';m.export(p);check=tm.load_mesh(p)
    assert len(check.faces)==len(original.faces) and check.is_watertight and check.is_volume
    assert np.allclose(check.bounds[0],0,atol=.00001) and np.allclose(check.extents,r['size_oriented_mm'],atol=.00001)
    assert abs(check.volume-original.volume)<max(.01,original.volume*1e-5)
    audit.append(dict(ref=key,file=p.name,sha256=sha256(p.read_bytes()).hexdigest(),source_sha256=r['source_sha256'],rigid_rotation_3x3=r['rotation_3x3'],translation_mm=r['normalization_translation_mm'],scale=1.,unit='mm',bbox_mm=check.bounds.tolist(),faces=len(check.faces),automatic_repairs=0))
(target/'manifest.json').write_text(json.dumps(dict(status='EXACT_SOURCE_RIGID_TRANSFORMS_PASS',objects=len(audit),no_scaling=True,no_remeshing=True,parts=audit),indent=2)+'\n')
print('PASS:',len(audit),'print-oriented full-scale STL files')
