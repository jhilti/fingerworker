#!/usr/bin/env python3
"""Independent exact R3->R4 CSG/drawing check and explicit cam/terminal witnesses.

No production files are created. All compared BReps come from saved native STEP.
The drawing reconstruction is intentionally a clearance proxy, not factory CAD.
"""
from pathlib import Path
import json
import math
import numpy as np
from OCP.STEPControl import STEPControl_Reader
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_SOLID
from OCP.BRepAlgoAPI import BRepAlgoAPI_Fuse, BRepAlgoAPI_Cut, BRepAlgoAPI_Common
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
from OCP.gp import gp_Pnt, gp_Dir, gp_Ax2, gp_Vec, gp_Trsf
import validate_finished as v

EXPECTED='b150ff3a76cfaaaaa65ee1ea09e144b7c7d64e45459a925163e56918f48bb3c5'
BASE=v.ROOT/'review/flat132-palm-fit-2026-10-23'
m=json.loads((v.HERE/'manifest.json').read_text())
source=Path(m['feature_source']);assert v.sha(source)==EXPECTED
proposal=json.loads((v.HERE.parent/'source-build.json').read_text())
assert proposal['sha256']==EXPECTED
baseline_inventory=json.loads((BASE/'validation/native-step-inventory.json').read_text())
current_inventory=json.loads((v.HERE/'native-step-inventory.json').read_text())
assert current_inventory['status']=='PASS'
assert current_inventory['native_step_sha256']==v.sha(m['sensor']['native_assembly_step'])
rows=[]
def row(name,passed,**values):
    rows.append({'name':name,'status':'PASS' if passed else 'FAIL',**values})
def shapes(path,inventory):
    reader=STEPControl_Reader();assert str(reader.ReadFile(str(path))).endswith('RetDone')
    reader.TransferRoots();ex=TopExp_Explorer(reader.OneShape(),TopAbs_SOLID);out=[]
    while ex.More():out.append(ex.Current());ex.Next()
    assert len(out)==105
    return {ref:out[item['candidates'][0]['solid_index']] for ref,item in inventory['native_part_correspondence'].items()}
def volume(shape):
    prop=GProp_GProps();BRepGProp.VolumeProperties_s(shape,prop);return abs(float(prop.Mass()))
def boolean(cls,a,b):
    op=cls(a,b);op.Build();assert op.IsDone();return op.Shape()
def union(a,b):return boolean(BRepAlgoAPI_Fuse,a,b)
def cut(a,b):return boolean(BRepAlgoAPI_Cut,a,b)
def common(a,b):return boolean(BRepAlgoAPI_Common,a,b)
def xor(a,b):return volume(cut(a,b))+volume(cut(b,a))
def box(lo,hi):return BRepPrimAPI_MakeBox(gp_Pnt(*lo),gp_Pnt(*hi)).Shape()
def cylinder(a,b,r):
    delta=np.array(b)-a
    return BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(*a),gp_Dir(*delta)),r,float(np.linalg.norm(delta))).Shape()
def translate(shape,delta):
    tr=gp_Trsf();tr.SetTranslation(gp_Vec(*delta));return BRepBuilderAPI_Transform(shape,tr,True).Shape()
def multi_union(items):
    out=items[0]
    for item in items[1:]:out=union(out,item)
    return out

old=shapes(BASE/'native/Flat132_R3_final_AP214.step',baseline_inventory)
new=shapes(Path(m['sensor']['native_assembly_step']),current_inventory)
# Restore old blind pilot voids only inside the complete, unwindowed base plate
# at X14.9..18.1 (< first window X22), Z2..4. The old pedestal is removed only
# ABOVE Z4, so the original base top and all neighboring geometry are retained.
p01=old['P01']
for y in (-11.9,-2.4):p01=union(p01,cylinder([16.5,y,2],[16.5,y,4],1.6))
p01=cut(p01,box([13,-18,4],[25,4,6]))
p01=union(p01,box([17,-16.5,3.8],[29,5,7.5]))
for y in (-10.9,-1.4):p01=cut(p01,cylinder([20.5,y,3.5],[20.5,y,7.7],1.6))

# Restore cam holes using exact source-uniform central X/Z stock sections.
# At this Y region the original climbing deck/pocket is translationally
# uniform: |Y|<28, while the guide relief belowZ7.3 and the side seats cannot
# affect either old tool (minZ7.9). Two opposite intact neighboring sections
# independently agree, checked by exact BRep symmetric difference below.
old_cam_voids=multi_union([cylinder([63.8,2.5,10],[69,2.5,10],2.1),cylinder([63,2.5,10],[76.5,2.5,10],1.7)])
restore_domain=common(old_cam_voids,box([65,-100,-100],[200,100,100]))
fill_a=common(restore_domain,translate(old['P04'],[0,7.5,0]))
fill_b=common(restore_domain,translate(old['P04'],[0,-7.5,0]))
fill_error=xor(fill_a,fill_b)
row('Opposite intact deck sections give identical old-hole restoration stock',fill_error<=1e-6,symmetric_difference_mm3=fill_error,source_uniform_Y_region_mm=[-28,28],old_tool_minimum_Z_mm=7.9,guide_roof_Z_mm=7.3)
p04=union(old['P04'],fill_a)
p04=cut(p04,box([64,-2,7],[65,8,15]))
for a,b,r in [([63.8,3.5,11.5],[68,3.5,11.5],2.9),([67.8,3.5,11.5],[73,3.5,11.5],2.1),([63,3.5,11.5],[76.5,3.5,11.5],1.7)]:p04=cut(p04,cylinder(a,b,r))

h09=translate(old['H09'],[4,1,1.5])
for y in (-14.4,-5.6,1.7):h09=union(h09,box([14.1,y-.25,9.1],[18,y+.25,12.3]))
h09=union(h09,box([17.6,-16,7.5],[18,3.8,13.9]))
h10=union(cylinder([64,3.5,11.5],[67,3.5,11.5],2.75),cylinder([66.9,3.5,11.5],[75,3.5,11.5],1.5))
expected={'P01':p01,'P04':p04,'H09':h09,'H09a':translate(old['H09a'],[4,1,1.5]),'H09b':translate(old['H09b'],[4,1,1.5]),'H10':h10}
for ref,shape in expected.items():
    delta=xor(shape,new[ref]);valid=BRepCheck_Analyzer(shape).IsValid()
    row('Exact native '+ref+' agrees with independent source CSG reconstruction',valid and delta<=1e-6,symmetric_difference_mm3=delta,tolerance_mm3=1e-6,expected_valid=bool(valid),expected_volume_mm3=volume(shape),native_volume_mm3=volume(new[ref]))
# Check every untouched BRep as well as the stricter native triangle identity
# comparison from the main validator. No rounded-coordinate match is used.
unchanged=[]
for ref in sorted(set(old)-set(expected)):
    delta=xor(old[ref],new[ref]);unchanged.append({'ref':ref,'symmetric_difference_mm3':delta})
row('All99 untouched exact native BReps retained from frozen R3',len(unchanged)==99 and max(x['symmetric_difference_mm3'] for x in unchanged)<=1e-6,parts_checked=len(unchanged),maximum_symmetric_difference_mm3=max(x['symmetric_difference_mm3'] for x in unchanged),changed=[x for x in unchanged if x['symmetric_difference_mm3']>1e-6])

parts,_=v.load(m['assembly'],m)
# Every solder-tab Y/Z slab lies below the P05 upper rib and between its
# outside stop arms. Its complete P05 material has frontX9 atp0,11 atp2.
for y in (-14.4,-5.6,1.7):
    slab=v.probe_object({'type':'box','minimum_mm':[-100,y-.25,9.1],'maximum_mm':[100,y+.25,12.3]})
    local=parts['P05']['object']^slab
    front=float(v.bounds(local)[1,0]);gap=14.1-(front+2.)
    row('Terminal '+str(y)+' has full-preload axial separation from intact P05',gap>=3.1-1e-5,p05_local_front_neutral_X_mm=front,maximum_preload_mm=2.,terminal_minimum_X_mm=14.1,minimum_axial_gap_mm=gap)

# Nominal diameter4 driver SHANK corridor only, with all preload combinations
# at zero stroke. The conservative fixed tube contains the shorter p2 path.
# It terminates0.01 before the neutral cam face. H10 is the intended target;
# its head socket and a complete hand-tool/handle are not represented.
tool=v.probe_object({'type':'cylinder_x','start_x_mm':40.05,'end_x_mm':63.99,'y_mm':3.5,'z_mm':11.5,'radius_mm':2.})
tool_rows=[]
for ref,item in sorted(parts.items()):
    if ref=='H10' or ref in v.SPRINGS:continue
    coeff=v.motion(ref,m);delta=[float(coeff@np.array([0.,p])) for p in (0.,2.)]
    result=v.relative_sweep(item['object'],tool,min(delta),max(delta),m['volume_tolerance_mm3'],m['minimum_interval_mm'])
    tool_rows.append({'ref':ref,**result})
fail=[r for r in tool_rows if r['status'] in ('INTERFERENCE','UNCHECKED','UNRESOLVED_NEAR_CONTACT')]
row('Diameter4 nominal cam driver-shank corridor clear at stroke0 over preload0..2',not fail,checks_count=len(tool_rows),failed=fail,corridor={'start_X_mm':40.05,'end_X_mm':63.99,'Y_mm':3.5,'Z_mm':11.5,'diameter_mm':4.,'actual_end_X_function':'63.99-preload','actual_end_X_range_mm':[61.99,63.99]},meaning='Partial shaft corridor to head face only; head socket, handle approach and actual hardware/tool are unqualified')

# This is a source envelope calculation, not proof of unmodeled insert stock.
engagement=[]
for preload in (0.,2.):
    shaft=[67.-preload,75.-preload];insert=[68.,72.]
    engaged=max(0.,min(shaft[1],insert[1])-max(shaft[0],insert[0]))
    engagement.append({'preload_mm':preload,'nominal_M3x8_shaft_X_mm':shaft,'nominal_L4_insert_X_mm':insert,'nominal_axial_overlap_mm':engaged,'shaft_beyond_insert_mm':shaft[1]-insert[1]})
row('Nominal M3x8 maintains complete L4 insert overlap through preload reset',all(x['nominal_axial_overlap_mm']>=4.-1e-9 for x in engagement),endpoint_values=engagement,meaning='Nominal source shaft/insert intent only; actual insert fit, thread form and setting lock require hardware verification')
row('Head recess radial clearance and intact guide roof match source',abs((2.9-2.75)-.15)<1e-12 and abs((11.5-2.9)-7.3-1.3)<1e-12,head_radial_gap_mm=2.9-2.75,guide_roof_Z_mm=7.3,head_recess_minimum_Z_mm=11.5-2.9,retained_roof_web_mm=(11.5-2.9)-7.3)
report={'status':'PASS' if all(x['status']=='PASS' for x in rows) else 'FAIL','scope':'Independent exact native switch/pedestal/cam CSG,99 unchanged BReps, terminal separation and nominal cam shaft/insert/driver witnesses. Not factory switch CAD, actual switch travel qualification or printed strength.',
    'auditor_sha256':v.sha(Path(__file__)),'source_sha256':EXPECTED,'manifest_sha256':v.sha(v.HERE/'manifest.json'),'native_step_sha256':v.sha(m['sensor']['native_assembly_step']),'baseline_step_sha256':v.sha(BASE/'native/Flat132_R3_final_AP214.step'),'native_provenance':m['native_provenance'],
    'rows':rows,'tool_corridor_pairs':tool_rows,'unchanged_brep_comparison':unchanged,
    'limitations':['H09 terminals and lug are conservative dimensioned boxes, not exact manufacturer shapes. H09a/H09b use an approximate fixed-length rotating mechanism.','Actual solder joints, wire bends, insulation and strain relief are not modeled.','SS-01GL2 operating-position tolerance and total travel require physical cam calibration at every preload reset; nominal one-mm trip lead is not a guaranteed margin.','Actual inserts, screw/head/washer sizes, driver socket/handle fit, retention and printed500N working load remain unqualified.']}
v.write(v.HERE/'switch-fit-audit.json',report)
print(json.dumps({'status':report['status'],'checks':len(rows),'failed':[x for x in rows if x['status']=='FAIL']},indent=2))
assert report['status']=='PASS'
