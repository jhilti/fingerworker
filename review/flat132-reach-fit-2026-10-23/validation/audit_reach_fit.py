#!/usr/bin/env python3
"""Independent native R5 CSG, preserved shapes, clamp stock and access audit."""
from pathlib import Path
import json,math
import numpy as np
from OCP.STEPControl import STEPControl_Reader
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_SOLID
from OCP.BRepAlgoAPI import BRepAlgoAPI_Fuse,BRepAlgoAPI_Cut,BRepAlgoAPI_Common
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox,BRepPrimAPI_MakeCylinder,BRepPrimAPI_MakePrism
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform,BRepBuilderAPI_MakePolygon,BRepBuilderAPI_MakeFace
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
from OCP.gp import gp_Pnt,gp_Dir,gp_Ax2,gp_Vec,gp_Trsf
import validate_finished as v
EXPECTED='d7f476fa34e862e2b0e1b5a5e91fff0f852b9308a589fafd11ce59e01269915a'
BASE=v.ROOT/'review/flat132-switch-fit-2026-10-23'
m=json.loads((v.HERE/'manifest.json').read_text());assert v.sha(m['feature_source'])==EXPECTED
assert json.loads((v.HERE.parent/'source-build.json').read_text())['sha256']==EXPECTED
ni=json.loads((v.HERE/'native-step-inventory.json').read_text());bi=json.loads((BASE/'validation/native-step-inventory.json').read_text())
assert ni['status']=='PASS' and ni['native_step_sha256']==v.sha(m['sensor']['native_assembly_step'])
rows=[]
def record(name,ok,**details):rows.append(dict(name=name,status='PASS' if ok else 'FAIL',**details))
def shapes(path,inventory):
 r=STEPControl_Reader();assert str(r.ReadFile(str(path))).endswith('RetDone');r.TransferRoots();ex=TopExp_Explorer(r.OneShape(),TopAbs_SOLID);out=[]
 while ex.More():out.append(ex.Current());ex.Next()
 assert len(out)==inventory['native_step_solids']
 return {ref:out[item['candidates'][0]['solid_index']] for ref,item in inventory['native_part_correspondence'].items()}
def volume(shape):
 p=GProp_GProps();BRepGProp.VolumeProperties_s(shape,p);return abs(float(p.Mass()))
def boolean(cls,a,b):
 op=cls(a,b);op.Build();assert op.IsDone();return op.Shape()
def union(a,b):return boolean(BRepAlgoAPI_Fuse,a,b)
def cut(a,b):return boolean(BRepAlgoAPI_Cut,a,b)
def common(a,b):return boolean(BRepAlgoAPI_Common,a,b)
def xor(a,b):return volume(cut(a,b))+volume(cut(b,a))
def box(lo,hi):return BRepPrimAPI_MakeBox(gp_Pnt(*lo),gp_Pnt(*hi)).Shape()
def cylinder(a,b,r):
 d=np.array(b)-a;return BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(*a),gp_Dir(*d)),r,float(np.linalg.norm(d))).Shape()
def translate(shape,xyz):
 t=gp_Trsf();t.SetTranslation(gp_Vec(*xyz));return BRepBuilderAPI_Transform(shape,t,True).Shape()
def multi(shapes):
 a=shapes[0]
 for b in shapes[1:]:a=union(a,b)
 return a
old=shapes(BASE/'native/Flat132_R4_final_AP214.step',bi);new=shapes(Path(m['sensor']['native_assembly_step']),ni)
# Extend only the fixed profile front5mm. Original rail/source end remains124.
w=BRepBuilderAPI_MakePolygon()
for y,z in [(-12.9,3.9),(12.9,3.9),(16,7),(-16,7)]:w.Add(gp_Pnt(29,y,z))
w.Close();extension=BRepPrimAPI_MakePrism(BRepBuilderAPI_MakeFace(w.Wire()).Face(),gp_Vec(5,0,0)).Shape()
p01=union(old['P01'],extension)
# Restore every old horizontal bore only in original intact central deck stock.
old_voids=multi([cylinder([63.8,3.5,11.5],[68,3.5,11.5],2.9),cylinder([67.8,3.5,11.5],[73,3.5,11.5],2.1),cylinder([63,3.5,11.5],[76.5,3.5,11.5],1.7)])
restore=common(old_voids,box([65,-100,-100],[200,100,100]))
a=common(restore,translate(old['P04'],[0,7.5,0]));b=common(restore,translate(old['P04'],[0,-7.5,0]));err=xor(a,b)
record('Opposite intact source-uniform deck sections agree on complete bore restoration',err<=1e-6,symmetric_difference_mm3=err)
p04=union(old['P04'],a)
well=[box([64,-1,8.6],[74.8,8,19]),box([64,-14,8.6],[67.2,8,19])]
for radius,z0,z1 in [(1.7,18.9,25.2),(3.,25.,31.)]:
 well += [cylinder([67.7,3.5,z0],[67.7,3.5,z1],radius),cylinder([71.3,3.5,z0],[71.3,3.5,z1],radius),box([67.7,3.5-radius,z0],[71.3,3.5+radius,z1])]
for tool in well:p04=cut(p04,tool)
p04=translate(p04,[-5,0,0])
p05=old['P05']
for side in (-1,1):p05=cut(p05,box([30,side*24-7,7],[35,side*24+7,29]))
expected={'P01':p01,'P04':p04,'P05':p05}
for side,ref in [(-1,'P060'),(1,'P061')]:
 shape=old[ref]
 for sign in (-1,1):
  y=side*51+sign*7.5;shape=union(shape,box([120.5,y-2.25,14],[125.6,y+2.25,20]))
 expected[ref]=shape
shoe=union(box([69,-.7,9],[73.5,7.7,19]),box([67.5,-.7,13.2],[69,7.7,19]))
shoe=cut(shoe,cylinder([70.5,3.5,14.5],[70.5,3.5,19.2],2.1));expected['P11']=translate(shoe,[-5,0,0])
expected['H10']=translate(union(cylinder([70.5,3.5,25],[70.5,3.5,28],2.75),cylinder([70.5,3.5,15],[70.5,3.5,25.1],1.5)),[-5,0,0])
for ref,shape in expected.items():
 err=xor(shape,new[ref]);valid=BRepCheck_Analyzer(shape).IsValid()
 record('Exact native '+ref+' matches independent R4-to-R5 source CSG',valid and err<=1e-6,symmetric_difference_mm3=err,tolerance_mm3=1e-6,expected_valid=bool(valid),expected_volume_mm3=volume(shape),native_volume_mm3=volume(new[ref]))
shifted={'H060','H061','P070a','P070b','P071a','P071b'}
changed_old=set(expected)-{'P11'}|{'H030','H031'}
unchanged=[]
for ref in sorted(set(old)-changed_old):
 shift=[-5.,0.,0.] if ref in shifted else [0.,0.,0.]
 err=xor(translate(old[ref],shift),new[ref]);unchanged.append(dict(ref=ref,expected_rigid_translation_mm=shift,symmetric_difference_mm3=err))
record('All97 otherwise-preserved exact BReps retain shape and only six declared5mm rigid shifts',len(unchanged)==97 and max(x['symmetric_difference_mm3'] for x in unchanged)<=1e-6,parts_checked=len(unchanged),maximum_symmetric_difference_mm3=max(x['symmetric_difference_mm3'] for x in unchanged),failed=[x for x in unchanged if x['symmetric_difference_mm3']>1e-6])
# Every section normal to the indicative spring path is a radius1 disk centered
# on a radius6.4/6.25 helix. Its radial occupancy lies inside5.25..7.4 regardless
# of section rotation. End trimming restricts X to the exact seat planes.
text=Path(m['feature_source']).read_text();base_text=(BASE/'fingerworker_flat132_switch_fit.fs').read_text()
helper=lambda s:s.split('function makeCompressionSpring(',1)[1].split('/**',1)[0]
record('Indicative spring helper geometry unchanged, only installed span differs',helper(text)==helper(base_text),new_open_installed_length_p0_p2_mm=[96.,94.],new_minimum_dynamic_length_mm=66.,meaning='Helix is illustrative; manufacturer operating-length and physical fatigue remain separate checks')
parts,_=v.load(m['assembly'],m)
# Rigorous lower bound to nominal under-head support: both disk lobes outside
# the infinite inner-slot strip are present for EVERY e-p in[-2.8,.8].
R=2.75;r=1.7;reach=math.sqrt(R*R-r*r)
area=math.pi*R*R-2*(r*reach+R*R*math.asin(r/R))
x0=62.7-reach;x1=66.3+reach
support=[]
for y0,y1 in [(.75,1.8),(5.2,6.25)]:
 stock=box([x0,y0,24.99],[x1,y1,24.9999]);missing=volume(cut(stock,new['P04']));support.append(dict(bounds_mm=[[x0,y0,24.99],[x1,y1,24.9999]],missing_stock_mm3=missing))
record('Head-bearing disk lobes have continuous nominal roof support over full calibration/preload range',all(x['missing_stock_mm3']<=1e-6 for x in support),guaranteed_source_area_lower_bound_mm2=area,all_setting_lobe_stock_bounds=support,axis_X_range_in_neutral_carriage_frame_mm=[62.7,66.3],qualification='Geometric area only; clamp torque/insert and print strength unqualified')
# Nominal vertical driver shaft only, at unloaded user rest over all p/e.
tool=v.probe_object(dict(type='cylinder_z',x_mm=65.5,y_mm=3.5,start_z_mm=28.01,end_z_mm=50.,radius_mm=2.))
vertices=np.array([[0,p,e] for p in (0.,2.) for e in (-.8,.8)])
tool_motion=np.array([0.,-1.,1.]);tool_rows=[]
for ref,item in sorted(parts.items()):
 if ref in v.SPRINGS:continue
 coefficients=tool_motion-v.motion(ref,m);range_=vertices@coefficients
 result=v.relative_sweep(tool,item['object'],float(range_.min()),float(range_.max()),m['volume_tolerance_mm3'],m['minimum_interval_mm'])
 tool_rows.append(dict(ref=ref,**result))
bad=[r for r in tool_rows if r['status'] in ('INTERFERENCE','UNCHECKED','UNRESOLVED_NEAR_CONTACT')]
record('Diameter4 vertical driver-shank corridor clears all104 non-coil obstacles over full p/e at user rest',not bad,pairs_checked=len(tool_rows),failed=bad,source_corridor=dict(axis_X_mm=65.5,Y_mm=3.5,Z_range_mm=[28.01,50.],diameter_mm=4.),qualification='Partial shaft only; head socket, actual hand-tool handle and physical access unqualified')
record('Nominal M3x10 covers L4 vertical insert with0.5mm pilot-floor reserve',15>=14.5 and min(25,19)-max(15,15)==4.,under_head_Z_mm=25.,nominal_shaft_tip_Z_mm=15.,nominal_insert_Z_range_mm=[15.,19.],nominal_engagement_mm=4.,pilot_floor_Z_mm=14.5,pilot_floor_gap_mm=.5,qualification='Actual hardware/insert stock and thread/clamp durability unqualified')
record('Front and rear14mm guide-bearing lands remain inside extended fixed rail at all user travel',29.<=65.-35. and 124.-5.<=124.,fixed_rail_X_mm=[29.,124.],front_land_extreme_X_mm=[[60.,74.],[30.,44.]],rear_land_extreme_X_mm=[[105.,119.],[75.,89.]],nominal_each_land_length_mm=14.,qualification='Source geometry overlap, not wear/friction/side-load qualification')
report={'status':'PASS' if all(r['status']=='PASS' for r in rows) else 'FAIL','scope':'Independent exact native source CSG and retained-shape check, clamp-support lower bound, driver corridor and source guide/insert witnesses; no printed load rating or factory switch mechanism claim',
 'auditor_sha256':v.sha(Path(__file__)),'source_sha256':EXPECTED,'manifest_sha256':v.sha(v.HERE/'manifest.json'),'native_step_sha256':v.sha(m['sensor']['native_assembly_step']),'baseline_step_sha256':v.sha(BASE/'native/Flat132_R4_final_AP214.step'),'native_provenance':m['native_provenance'],
 'rows':rows,'unchanged_brep_comparison':unchanged,'tool_corridor_pairs':tool_rows,
 'limitations':['500N remains physically unqualified; new return-boss joints, stop face, shoe and clamp need printed prototype checks.','SS-01GL2 remains a conservative manufacturer-drawing body/terminal/lug reference and approximate fixed-length actuator; geometry trim range does not qualify actual OP tolerance or total travel.','Actual inserts, screw/head/socket, solder/wire bending, setting lock, fatigue, guide friction, creep and comfort are unqualified.','The selected81mm sleeves move isometric grip5mm closer than R4; user-relative approach is13..15mm.','The shoe pilot has nominal0.9mm front/rear X ligaments and1.3mm lower boss bridge; insert installation and clamp durability remain unqualified.']}
v.write(v.HERE/'reach-fit-audit.json',report)
print(json.dumps({'status':report['status'],'checks':len(rows),'failed':[r for r in rows if r['status']=='FAIL']},indent=2));assert report['status']=='PASS'
