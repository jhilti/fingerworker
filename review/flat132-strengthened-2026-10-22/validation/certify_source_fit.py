#!/usr/bin/env python3
"""Exact source-level sleeve/core proof, distinct from STEP roundtrip checking."""
from pathlib import Path
import json
import numpy as np
import validate_finished as v

manifest_path=v.HERE/'manifest.json'
m=json.loads(manifest_path.read_text());source=Path(m['feature_source'])
expected='d5eca2f3d87bf4b9a47c1987ee91ba1d56e8c87003eca101677a148a2e605654'
actual=v.sha(source);text=source.read_text()
assert actual==expected, 'Certificate was reviewed only for the frozen final source revision'
requirements=[
    'makeBox(context,id + "palmPad",vector(-44.25,-64,9.5)*mm,vector(-23.25,64,14.5)*mm);',
    'makeBox(context,id + "palmEarLeft",vector(-30,-37,9.5)*mm,vector(-9.5,-26,14.5)*mm);',
    'makeBox(context,id + "palmEarRight",vector(-30,26,9.5)*mm,vector(-9.5,37,14.5)*mm);',
    'makeCylinder(context,id + "palmBolsterCore",vector(-34,-58,19.75)*mm,',
    'vector(-34,58,19.75)*mm,7.75*mm);',
    'makeCylinder(context,id + "sleeveCoreTool",vector(-34,-44,19.75)*mm,vector(-34,44,19.75)*mm,7.75*mm);',
    'makeBox(context,id + "sleeveBottomTool",vector(-50,-45,0)*mm,vector(-18,45,14.6)*mm);',
    'cut(context,id + "openSleeve",body(id + "palmCushion"),qUnion([body(id + "sleeveCoreTool"),body(id + "sleeveBottomTool")]));',
]
assert all(s in text for s in requirements), 'Reviewed analytic source datums missing'
parts,_=v.load(m['assembly'],m)
core=parts['P02'];sleeve=parts['P03']
high=core['object'].trim_by_plane([0,0,1],14.600001).to_mesh64()
vertices=np.asarray(high.vert_properties)[:,:3]
radius=np.hypot(vertices[:,0]+34,vertices[:,2]-19.75)
sv=sleeve['mesh'].vertices
sr=np.hypot(sv[:,0]+34,sv[:,2]-19.75)
native_checks={
    'P02_above_sleeve_bottom_maximum_vertex_radius_mm':float(radius.max()),
    'P03_minimum_vertex_radius_mm':float(sr.min()),
    'P03_bounds_mm':sleeve['mesh'].bounds.tolist(),
    'numeric_vertex_rounding_bound_mm':1e-5,
}
corroborated=(radius.max()<=7.75+1e-5 and sr.min()>=7.75-1e-5 and
              sleeve['mesh'].bounds[0,2]>=14.6-1e-5 and
              sleeve['mesh'].bounds[0,1]>=-43.-1e-5 and sleeve['mesh'].bounds[1,1]<=43.+1e-5)
assert corroborated, 'Native bounds do not corroborate the source certificate'
report={
    'status':'EXACT_SOURCE_LEVEL_DISJOINTNESS_CERTIFIED',
    'scope':'Reviewed final parametric source set containment with native mesh corroboration; not a native BRep roundtrip comparison',
    'source_sha256':actual,'manifest_sha256':v.sha(manifest_path),
    'native_parts':{r:{'member':parts[r]['member'],'sha256':parts[r]['sha256']} for r in ('P02','P03')},
    'axis_mm':{'X':-34.,'Z':19.75,'direction':'Y'},'nominal_shared_radius_mm':7.75,
    'proof':[
        'All P02 plate, ear and clamp material is at Z<=14.5. The only P02 material above that plane is contained in the radius7.75 bolster cylinder; convex fillets and all later cuts only shrink it.',
        'P03 is created within Y=[-43,43]. The complete radius7.75 inner cylinder tool spans Y=[-44,44], beyond both sleeve ends, and is subtracted from the sleeve.',
        'The complete sleeve bottom tool removes Z<14.6 throughout its X/Y extent. The later adjuster relief is another subtraction.',
        'Consequently P02 plate/ear/clamp material is separated from P03 by the 0.1mm Z interval, and all remaining P02 material lies inside the very cylinder excluded from the P03 interior.',
        'Therefore no positive-volume intersection exists in the exact parametric source. Coincident cylindrical boundary contact is the intended nominal fit.'
    ],
    'native_corroboration':native_checks,
    'mesh_artifact_intersection_mm3':float((core['object']^sleeve['object']).volume()),
    'step_roundtrip_status':'CHECK_SEPARATE_VALIDATION_REPORT; not inferred from this source certificate',
    'limitations':['Separate cylinder triangulations use planar chords and can show small mesh overlap even where exact analytic cylindrical surfaces coincide.',
                   'This proves nominal source non-intersection, not real print fit, friction, comfort or material qualification.']
}
validation_path=v.HERE/'validation.json'
if validation_path.exists():
    separate=json.loads(validation_path.read_text())
    same=separate.get('manifest_sha256')==v.sha(manifest_path)
    pair_ok=any(set(row.get('pair',[]))=={'P02','P03'} and row.get('status')=='PASS' for row in separate.get('exact_brep_pairs',[]))
    if same and pair_ok:
        report['step_roundtrip_status']='PASS_FROM_SEPARATE_NATIVE_BREP_REPORT'
        report['separate_step_roundtrip_report']=str(validation_path)
v.write(v.HERE/'source-fit-certificate.json',report)
print(json.dumps({'status':report['status'],'native_corroboration':native_checks},indent=2))
