#!/usr/bin/env python3
"""Build offline R15 display geometry from immutable native STL ZIP.

These decimated meshes are visualization assets, never manufacturing files.
"""
import base64, gzip, hashlib, io, json, pathlib, re
import numpy as np
import trimesh
from zipfile import ZipFile
from vtkmodules.vtkCommonCore import vtkPoints
from vtkmodules.vtkCommonDataModel import vtkCellArray, vtkPolyData
from vtkmodules.vtkFiltersCore import vtkQuadricDecimation, vtkPolyDataNormals
from vtkmodules.util.numpy_support import numpy_to_vtk, numpy_to_vtkIdTypeArray, vtk_to_numpy

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = pathlib.Path(__file__).resolve().parent
REVIEW = ROOT / 'review/inboard-straps-2026-11-08'
ARCHIVE = REVIEW / 'native/Flat132_R15_neutral_final.zip'
SPEC = json.loads((REVIEW / 'final-specification.json').read_text())
sha = lambda b: hashlib.sha256(b).hexdigest()
raw = ARCHIVE.read_bytes()
assert SPEC['status'].startswith('PASS') and int(SPEC['native_solids'])==93
assert sha(raw) == SPEC['files_sha256'][str(ARCHIVE.relative_to(ROOT))]
z = ZipFile(io.BytesIO(raw))
parts = []
manifest = {
    'revision': 'R15', 'date': '2026-11-08',
    'purpose': 'Display only; no manufacturing geometry or physical collision assertion.',
    'source': str(ARCHIVE.relative_to(ROOT)), 'native_zip_sha256': sha(raw),
    'source_sha256': SPEC['source_sha256'], 'onshape_version': SPEC['onshape_version'],
    'method': 'VTK quadric display decimation, positions rounded to 0.01 mm; native STL coordinates retained.',
    'parts': []
}
for name in sorted(z.namelist()):
    if not name.endswith('.stl'): continue
    blob = z.read(name)
    label = name.removeprefix('Fingerworker MVP - ').removesuffix('.stl')
    ident = ('PCB_' if label.startswith('REF PCB ') else '') + re.match(r'([A-Z]+\d+[a-z]?)', label.removeprefix('REF PCB ').removeprefix('REF ')).group(1)
    group = 'electronics' if label.startswith('REF ') else 'print' if ident.startswith('P') else 'buy' if ident in ('H01','H030','H031','H09','H09a','H09b') else 'metal'
    mesh = trimesh.load(io.BytesIO(blob), file_type='stl', process=True)
    nf = len(mesh.faces)
    budget = 14000 if ident == 'P01' else 11000 if ident == 'P04' else 20000 if ident in ('H030','H031') else 7000 if ident == 'H01' else 3500
    pts = vtkPoints(); pts.SetData(numpy_to_vtk(np.asarray(mesh.vertices, dtype=np.float64), deep=True))
    cells = vtkCellArray(); cells.SetCells(nf, numpy_to_vtkIdTypeArray(np.column_stack((np.full(nf,3,dtype=np.int64), mesh.faces)).astype(np.int64).ravel(), deep=True))
    poly = vtkPolyData(); poly.SetPoints(pts); poly.SetPolys(cells)
    if nf > budget:
        dec = vtkQuadricDecimation(); dec.SetInputData(poly); dec.SetTargetReduction(1 - budget/nf); dec.Update(); poly = dec.GetOutput()
    norm = vtkPolyDataNormals(); norm.SetInputData(poly); norm.SetFeatureAngle(35); norm.SplittingOn(); norm.ConsistencyOn(); norm.AutoOrientNormalsOff(); norm.ComputePointNormalsOn(); norm.Update(); poly = norm.GetOutput()
    verts = np.asarray(vtk_to_numpy(poly.GetPoints().GetData()))
    faces = np.asarray(vtk_to_numpy(poly.GetPolys().GetData())).reshape(-1,4)[:,1:]
    normals = np.asarray(vtk_to_numpy(poly.GetPointData().GetNormals()))
    assert len(verts) < 65536
    # Each body has its own origin to allow 0.01 mm signed-16-bit positions.
    origin = (verts.min(axis=0) + verts.max(axis=0))/2
    qverts = np.rint((verts-origin)*100).astype('<i2')
    qnorm = np.rint(normals*127).clip(-127,127).astype('i1')
    indices = faces.astype('<u2')
    p = {'id': ident,'label': label,'group':group,'origin':origin.round(6).tolist(),'count':len(indices)*3,
         'v':base64.b64encode(qverts.tobytes()).decode(),
         'n':base64.b64encode(qnorm.tobytes()).decode(),
         'f':base64.b64encode(indices.tobytes()).decode()}
    parts.append(p)
    manifest['parts'].append({'id': ident,'group':group,'native_member':name,'native_stl_sha256':sha(blob),'native_triangles':nf,'display_triangles':len(indices),'display_vertices':len(verts),'bounds_mm':mesh.bounds.tolist()})
    print(ident, group, nf, '->', len(indices), flush=True)
assert len(parts) == SPEC['native_solids']
payload = json.dumps(parts,separators=(',',':'),ensure_ascii=False).encode()
packed = gzip.compress(payload,compresslevel=9,mtime=0)
(OUT/'model-data.b64').write_text(base64.b64encode(packed).decode())
manifest['counts'] = {g:sum(p['group']==g for p in parts) for g in ('print','metal','buy','electronics')}
manifest['native_triangle_count'] = sum(p['native_triangles'] for p in manifest['parts'])
manifest['display_triangle_count'] = sum(p['display_triangles'] for p in manifest['parts'])
manifest['data_sha256'] = sha(packed)
manifest['packed_bytes'] = len(packed)
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n')
print('TOTAL',len(parts),manifest['display_triangle_count'],len(packed),flush=True)
