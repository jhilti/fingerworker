#!/usr/bin/env python3
"""Check final STEP completeness/validity against every native STL body."""
import json
from pathlib import Path
import numpy as np
from OCP.STEPControl import STEPControl_Reader
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_SOLID,TopAbs_FACE
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepBndLib import BRepBndLib
from OCP.Bnd import Bnd_Box
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
import validate_finished as v

m=json.loads((v.HERE/'manifest.json').read_text());path=Path(m['sensor']['native_assembly_step'])
inputs,ignored=v.load(m['assembly'],m)
reader=STEPControl_Reader();status=str(reader.ReadFile(str(path)))
assert status.endswith('RetDone'),status
transferred=reader.TransferRoots();whole=reader.OneShape()
exp=TopExp_Explorer(whole,TopAbs_SOLID);solids=[];shapes=[]
while exp.More():
    shape=exp.Current();box=Bnd_Box();BRepBndLib.AddOptimal_s(shape,box,False)
    props=GProp_GProps();BRepGProp.VolumeProperties_s(shape,props)
    faces=TopExp_Explorer(shape,TopAbs_FACE);count=0
    while faces.More():count+=1;faces.Next()
    solids.append({'index':len(solids),'valid':bool(BRepCheck_Analyzer(shape).IsValid()),
        'face_count':count,'volume_mm3':float(props.Mass()),
        'bounds_mm':[list(box.CornerMin().Coord()),list(box.CornerMax().Coord())]})
    shapes.append(shape)
    exp.Next()
correspondence={}
for ref,part in sorted(inputs.items()):
    mesh=part['mesh'];candidates=[]
    for item in solids:
        bound_error=float(np.max(np.abs(mesh.bounds-np.array(item['bounds_mm']))))
        volume_error=abs(mesh.volume-item['volume_mm3'])
        if bound_error<=.05 and volume_error<=max(.1,abs(mesh.volume)*.002):
            candidates.append({'solid_index':item['index'],'maximum_bound_error_mm':bound_error,
                'volume_error_mm3':float(volume_error),'native_brep_valid':item['valid']})
    if not candidates:
        bounded=[item for item in solids if np.max(np.abs(mesh.bounds-np.array(item['bounds_mm'])))<=.05]
        if len(bounded)==1:
            item=bounded[0];props=GProp_GProps()
            error=float(BRepGProp.VolumePropertiesGK_s(shapes[item['index']],props,1e-7,True,True,False,False))
            refined=float(props.Mass())
            if error>=0 and np.isfinite(refined) and refined>0:
                item.update(nonadaptive_volume_mm3=item['volume_mm3'],volume_mm3=refined,
                    volume_integration_method='Adaptive Gauss-Kronrod with B-spline knot spans',
                    requested_relative_error=1e-7,estimated_relative_error=error)
                volume_error=abs(mesh.volume-refined)
                if volume_error<=max(.1,abs(mesh.volume)*.002):
                    candidates.append({'solid_index':item['index'],
                        'maximum_bound_error_mm':float(np.max(np.abs(mesh.bounds-np.array(item['bounds_mm'])))),
                        'volume_error_mm3':float(volume_error),'native_brep_valid':item['valid']})
    correspondence[ref]={'native_stl_member':part['member'],'native_stl_sha256':part['sha256'],
        'candidates':candidates,'status':'PASS' if len(candidates)==1 and candidates[0]['native_brep_valid'] else 'UNCHECKED'}
matched=[item['candidates'][0]['solid_index'] for item in correspondence.values() if item['status']=='PASS']
unmatched=[i['index'] for i in solids if i['index'] not in matched]
ambiguous=[r for r,item in correspondence.items() if item['status']!='PASS']
passed=(len(solids)==len(inputs)==109 and len(matched)==len(set(matched))==109 and
        not unmatched and not ambiguous and all(x['valid'] and x['volume_mm3']>0 for x in solids))
report={'status':'PASS' if passed else 'INCOMPLETE_OR_INVALID','scope':'Full native final STEP solid validity, completeness and unique bounds/volume association to all native neutral STL bodies; not every-part exact symmetric difference',
    'source_sha256':m['native_provenance']['feature_source_sha256'],
    'native_provenance':m['native_provenance'],
    'native_step':str(path),'native_step_sha256':v.sha(path),
    'native_stl_archive':m['assembly'],'native_stl_archive_sha256':v.sha(m['assembly']),
    'step_read_status':status,'transferred_roots':transferred,
    'expected_device_solids':56,'expected_electronics_reference_solids':53,
    'native_step_solids':len(solids),'native_stl_parts':len(inputs),
    'valid_positive_solids':sum(x['valid'] and x['volume_mm3']>0 for x in solids),
    'unmatched_step_solid_indices':unmatched,'ambiguous_or_unmatched_stl_refs':ambiguous,
    'solid_inventory':solids,'native_part_correspondence':correspondence,
    'correspondence_criteria':{'all_six_bounds_tolerance_mm':.05,'volume_absolute_tolerance_mm3':.1,'volume_relative_tolerance':.002,
        'meaning':'STL tessellation bounds/volume differ slightly from exact analytic BRep. Unique association is not a general exact geometric identity proof. Genuine sensor exact identity and TPU/core exact Boolean are checked separately.'}}
v.write(v.HERE/'native-step-inventory.json',report)
print(json.dumps({k:report[k] for k in ('status','native_step_solids','native_stl_parts','valid_positive_solids','unmatched_step_solid_indices','ambiguous_or_unmatched_stl_refs')},indent=2))
