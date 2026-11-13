#!/usr/bin/env python3
"""Exact half-round core/cap source separation proof; native STEP checked separately."""
from pathlib import Path
import json
import numpy as np
import validate_finished as v

manifest_path=v.HERE/'manifest.json'
m=json.loads(manifest_path.read_text());source=Path(m['feature_source'])
expected='d7f476fa34e862e2b0e1b5a5e91fff0f852b9308a589fafd11ce59e01269915a'
actual=v.sha(source);text=source.read_text()
assert actual==expected,'Certificate reviewed only for the frozen R5 source, with unchanged R3/R4 palm source'
requirements=[
    'makeBox(context,id + "palmPad",vector(-37.25,-64,9.5)*mm,vector(-23.25,64,14.5)*mm);',
    'makeBox(context,id + "palmEarLeft",vector(-30,-37,9.5)*mm,vector(-9.5,-26,14.5)*mm);',
    'makeBox(context,id + "palmEarRight",vector(-30,26,9.5)*mm,vector(-9.5,37,14.5)*mm);',
    'makeCylinder(context,id + "palmBolsterCore",vector(-27,-58,19.75)*mm,',
    'vector(-27,58,19.75)*mm,7.75*mm);',
    'makeBox(context,id + "palmCoreForwardHalfTool",vector(-27,-60,0)*mm,vector(0,60,40)*mm);',
    'cut(context,id + "palmCoreHalfCut",body(id + "palmBolsterCore"),body(id + "palmCoreForwardHalfTool"));',
    'makeCylinder(context,id + "sleeveCoreTool",vector(-27,-44,19.75)*mm,vector(-27,44,19.75)*mm,7.75*mm);',
    'makeBox(context,id + "sleeveBottomTool",vector(-50,-45,0)*mm,vector(-18,45,14.6)*mm);',
    'makeBox(context,id + "palmSleeveForwardHalfTool",vector(-27,-45,0)*mm,vector(0,45,40)*mm);',
    'cut(context,id + "openSleeve",body(id + "palmCushion"),qUnion([body(id + "sleeveCoreTool"),body(id + "sleeveBottomTool"),body(id + "palmSleeveForwardHalfTool")]));',
    'const loY=side == -1 ? -43 : 39;',
    'makeBox(context,id + ("palmSleeveReturn"~t),vector(-27,loY,14.6)*mm,',
    'vector(-24.5,loY+4,30)*mm);'
]
assert all(s in text for s in requirements),'Reviewed analytic source datums missing'
parts,_=v.load(m['assembly'],m);core=parts['P02'];cap=parts['P03']
high=core['object'].trim_by_plane([0,0,1],14.600001).to_mesh64()
vertices=np.asarray(high.vert_properties)[:,:3]
radius=np.hypot(vertices[:,0]+27,vertices[:,2]-19.75)
cv=cap['mesh'].vertices;wrist=cv[cv[:,0]<-27.-1e-5];returns=cv[cv[:,0]>-27.+1e-5]
wr=np.hypot(wrist[:,0]+27,wrist[:,2]-19.75)
checks={
    'P02_above_cap_bottom_maximum_vertex_radius_mm':float(radius.max()),
    'P02_above_cap_bottom_maximum_X_mm':float(vertices[:,0].max()),
    'P03_wrist_half_minimum_original_vertex_radius_mm':float(wr.min()),
    'P03_forward_return_vertices_within_declared_band_Y':bool(np.all((np.abs(returns[:,1])>=39.-1e-5)&(np.abs(returns[:,1])<=43.+1e-5))),
    'P03_bounds_mm':cap['mesh'].bounds.tolist(),
    'numeric_vertex_rounding_bound_mm':1e-5,
}
corroborated=(len(wrist)>0 and len(returns)>0 and radius.max()<=7.75+1e-5 and
    vertices[:,0].max()<=-27.+1e-5 and wr.min()>=7.75-1e-5 and
    checks['P03_forward_return_vertices_within_declared_band_Y'] and
    cv[:,2].min()>=14.6-1e-5 and cv[:,0].max()<=-24.5+1e-5 and
    cv[:,1].min()>=-43.-1e-5 and cv[:,1].max()<=43.+1e-5)
assert corroborated,'Native bounds do not corroborate the reviewed half-core/cap source'
report={
    'status':'EXACT_SOURCE_LEVEL_DISJOINTNESS_CERTIFIED',
    'scope':'Reviewed frozen parametric source set containment/plane partition with native mesh corroboration; not the separate exact native STEP Boolean',
    'source_sha256':actual,'manifest_sha256':v.sha(manifest_path),
    'native_parts':{ref:{'member':parts[ref]['member'],'sha256':parts[ref]['sha256']} for ref in ('P02','P03')},
    'axis_mm':{'X':-27.,'Z':19.75,'direction':'Y'},'nominal_shared_radius_mm':7.75,'shared_flat_plane_X_mm':-27.,
    'proof':[
        'All P02 plate/ear/clamp stock is at Z<=14.5. Above that plane, P02 is contained in the radius7.75 cylinder about X-27/Z19.75; convex end fillets and cuts only shrink it.',
        'The complete forward-half tool removes all P02 core material with X>-27. Its Y/Z bounds cover the entire uncut core.',
        'The TPU annular part is cut by the full radius7.75 inner cylinder spanning Y[-44,44], outside the complete cap Y[-43,43] extent. It contains no interior points inside that cylinder.',
        'Both forward-half and bottom tools leave the wrist annulus at X<=-27 and Z>=14.6. The complete remaining wrist half lies within the bottom tool X/Y coverage.',
        'The only subsequently added TPU bodies are two front return boxes at X[-27,-24.5], Y[-43,-39] and[39,43], Z[14.6,30]. Their interiors are separated from the rigid half-core interior by the exact X=-27 plane.',
        'Consequently the plate/ear/clamp stock is separated vertically from all TPU stock by0.1mm. Above it, the annulus excludes the cylinder that contains the rigid core, and the return bands lie on the opposite side of the core flat plane.',
        'No positive-volume core/cap intersection exists in the exact source. Shared curved or planar boundary contact is the intended nominal fit.'
    ],
    'native_corroboration':checks,
    'native_mesh_artifact_intersection_mm3':float((core['object']^cap['object']).volume()),
    'step_roundtrip_status':'CHECK_SEPARATE_VALIDATION_REPORT',
    'retention_scope':'Two return bands provide nominal geometric capture; TPU assembly flex, pull-off force, print tolerance, creep and retention durability are not qualified by this proof.',
    'limitations':['Separately triangulated coincident curved surfaces can have finite chord overlap. Exact native STEP Boolean testing remains separate.',
        'This proves nominal source non-intersection; it does not qualify real printed fit, friction, comfort or strength.']
}
p=v.HERE/'validation.json'
if p.exists():
    r=json.loads(p.read_text())
    if r.get('manifest_sha256')==v.sha(manifest_path) and any(set(x.get('pair',[]))=={'P02','P03'} and x.get('status')=='PASS' for x in r.get('exact_brep_pairs',[])):
        report['step_roundtrip_status']='PASS_FROM_SEPARATE_NATIVE_BREP_REPORT';report['separate_step_roundtrip_report']=str(p)
v.write(v.HERE/'source-fit-certificate.json',report)
print(json.dumps({'status':report['status'],'native_corroboration':checks},indent=2))
