#!/usr/bin/env python3
"""Static source/metadata checks; browser rendering is reviewed separately."""
from pathlib import Path
from hashlib import sha256
import ast,json,math,subprocess,tempfile
D=Path(__file__).resolve().parent;P=D.parent
hash_file=lambda p:sha256(p.read_bytes()).hexdigest()
c=json.loads((D/'poses-input.json').read_text());b=json.loads((D/'viewer-build.json').read_text());html=(D/'viewer.html').read_text()
assert hash_file(P/c['feature_source'])==c['source_sha256']==b['source_sha256']
assert hash_file(D/'viewer.html')==b['viewer_sha256']
assert '<script src=' not in html.lower() and '<link rel="stylesheet" href=' not in html.lower()
assert 'data-view="rear"' in html and 'data-view="cover"' in html and 'a+p ≤ 2 mm' in html
assert b['package_ready']==bool(c.get('prototype_package',{}).get('sha256'))
assert len(b['poses'])==len([p for p in c['poses'] if p['sha256']])
summary=[]
for pose in b['poses']:
    assert len(pose['rows'])==c['native_device_parts']+1
    assert len({r['ref'] for r in pose['rows']})==len(pose['rows'])
    assert hash_file(P/pose['archive'])==pose['sha256']
    assert pose['native_export_source_sha256']==b['source_sha256']
    assert pose['preload_mm']+pose['rear_adjust_mm']<=2
    assert pose['stroke_mm']+pose['preload_mm']+pose['rear_adjust_mm']<=30
    assert abs(pose['actual_carriage_shift_mm']-(5+pose['rear_adjust_mm']+pose['stroke_mm']))<1e-6
    assert all(math.isfinite(x) for row in pose['device_bounds_mm'] for x in row)
    dimensions=[pose['device_bounds_mm'][1][k]-pose['device_bounds_mm'][0][k] for k in range(3)]
    assert abs(dimensions[1]-132)<.001 and abs(dimensions[2]-35)<.001
    if pose['id']=='neutral':assert abs(dimensions[0]-176.5)<.001
    if pose['id']=='adjusted_rest':assert abs(dimensions[0]-175.6)<.001
    refs={r['ref'] for r in pose['rows']};assert 'P03' not in refs and {'P02','P120','P121','H260','H261','H320','H321'}.issubset(refs)
    summary.append({'id':pose['id'],'device_parts':len(pose['rows'])-1,'native_XYZ_span_mm':dimensions,'native_source_sha256':pose['native_export_source_sha256']})
tree=ast.parse((D/'build_viewer.py').read_text());template=next(ast.literal_eval(s.value) for s in tree.body if isinstance(s,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='TEMPLATE' for t in s.targets))
logic=template.split('<script>__PLOTLY__</script><script>',1)[1].split('</script>',1)[0].replace('__DATA__','[]').replace('__META__','{}')
with tempfile.NamedTemporaryFile(suffix='.js',mode='w') as temp:
    temp.write(logic);temp.flush();subprocess.run(['/Users/jonashilti/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node','--check',temp.name],check=True)
result={'status':'PASS_STATIC_SOURCE_BOUND_VIEWER_CHECKS','scope':'Source/native/archive metadata and domain, actual native dimension readouts, required rear controls, offline embedding and JavaScript syntax; browser visual review is separate','viewer_sha256':b['viewer_sha256'],'source_sha256':b['source_sha256'],'native_poses':summary,'nominal_geometry_state':b['review_state'],'package_ready':b['package_ready']}
(D/'viewer-static-validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
