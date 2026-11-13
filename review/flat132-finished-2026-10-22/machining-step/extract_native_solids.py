"""Package unchanged native solids; no normalization, reshape, healing or scaling."""
from pathlib import Path
import hashlib,json,importlib.metadata
import numpy as np
import trimesh
from OCP.STEPControl import STEPControl_Reader,STEPControl_Writer,STEPControl_AsIs
from OCP.IFSelect import IFSelect_RetDone
from OCP.Interface import Interface_Static
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_SOLID,TopAbs_FACE
from OCP.BRepBndLib import BRepBndLib
from OCP.Bnd import Bnd_Box
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCP.gp import gp_Trsf,gp_Vec
HERE=Path(__file__).resolve().parent;REVIEW=HERE.parent
NATIVE=REVIEW/'native/Flat132_R1_final_AP214.step';SOURCE=REVIEW/'fingerworker_flat132_finished.fs';MESHES=REVIEW/'assembly-mm'
EXPECTED_STEP='6de4383e6423fd1f57bd353d8f42953ecdae841bee1e36b853fb312c679fd7ef'
EXPECTED_SOURCE='041056629440056626b2f2f88a0db216693e48fff178687174478cb1f34227ef'
PARTS={
'H12':('H12_sensor_backing_S355.step','S355 steel, machined planar support, collar and side ears',1),
'H23':('H23_loose_sensor_keeper_stainless.step','Stainless sheet, grade not assigned;0.5mm, cut and deburr',1),
}

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def volume(s):
 p=GProp_GProps();BRepGProp.VolumeProperties_s(s,p);return p.Mass()
def area(s):
 p=GProp_GProps();BRepGProp.SurfaceProperties_s(s,p);return p.Mass()
def bounds(s):
 b=Bnd_Box();BRepBndLib.AddOptimal_s(s,b,False);return np.array([b.CornerMin().Coord(),b.CornerMax().Coord()])
def count(s,t):
 e=TopExp_Explorer(s,t);n=0
 while e.More():n+=1;e.Next()
 return n
def load(p):
 r=STEPControl_Reader();assert r.ReadFile(str(p))==IFSelect_RetDone,p;r.TransferRoots();return r.OneShape()
def xor(a,b):
 ab=BRepAlgoAPI_Cut(a,b);ba=BRepAlgoAPI_Cut(b,a);ab.Build();ba.Build();assert ab.IsDone() and ba.IsDone()
 return [abs(volume(ab.Shape())),abs(volume(ba.Shape()))]
assert sha(NATIVE)==EXPECTED_STEP;assert sha(SOURCE)==EXPECTED_SOURCE
root=load(NATIVE);e=TopExp_Explorer(root,TopAbs_SOLID);solids=[]
while e.More():
 s=e.Current();solids.append({'index':len(solids),'shape':s,'bounds':bounds(s)});e.Next()
assert len(solids)==109,len(solids)
cache={}
def find(ref):
 if ref in cache:return cache[ref]
 m=trimesh.load_mesh(MESHES/(ref+'.stl'));rows=[]
 for item in solids:
  be=float(np.max(np.abs(m.bounds-item['bounds'])))
  if be>.05:continue
  v=volume(item['shape']);ve=abs(v-m.volume)
  if ve<=max(.1,abs(m.volume)*.002):rows.append((item,be,ve))
 assert len(rows)==1,(ref,len(rows));cache[ref]=rows[0];return rows[0]
rows=[]
for ref,(filename,material,qty) in PARTS.items():
 item,be,ve=find(ref);s=item['shape'];assert BRepCheck_Analyzer(s).IsValid();out=HERE/filename
 writer=STEPControl_Writer();assert Interface_Static.SetCVal_s('write.step.schema','AP214IS');assert Interface_Static.SetCVal_s('write.step.unit','MM')
 assert writer.Transfer(s,STEPControl_AsIs)==IFSelect_RetDone;assert writer.Write(str(out))==IFSelect_RetDone
 new=load(out);newexp=TopExp_Explorer(new,TopAbs_SOLID);assert newexp.More();new=newexp.Current();difference=xor(s,new)
 d=BRepExtrema_DistShapeShape(s,new);d.Perform();assert d.IsDone();minimum_distance=d.Value()
 bb=bounds(new);berr=float(np.max(np.abs(bb-item['bounds'])));verr=abs(volume(s)-volume(new));aerr=abs(area(s)-area(new));valid=bool(BRepCheck_Analyzer(new).IsValid());ns=count(new,TopAbs_SOLID)
 assert berr<1e-6 and verr<1e-7 and aerr<1e-6 and valid and ns==1,(ref,berr,verr,aerr,valid,ns)
 rows.append({'reference':ref,'filename':filename,'sha256':sha(out),'quantity_in_device':qty,'material_or_source_callout':material,'native_step_solid_index':item['index'],'native_stl':str((MESHES/(ref+'.stl')).relative_to(REVIEW)),'native_stl_sha256':sha(MESHES/(ref+'.stl')),'unique_association_bounds_error_mm':be,'unique_association_volume_error_mm3':ve,'native_bounds_mm':item['bounds'].tolist(),'native_volume_mm3':volume(s),'native_area_mm2':area(s),'native_face_count':count(s,TopAbs_FACE),'reimport_valid':valid,'reimport_solid_count':ns,'reimport_face_count':count(new,TopAbs_FACE),'roundtrip_bounds_error_mm':berr,'roundtrip_volume_error_mm3':verr,'roundtrip_area_error_mm2':aerr,'native_minus_reimport_volume_mm3':difference[0],'reimport_minus_native_volume_mm3':difference[1],'minimum_shape_distance_mm':minimum_distance,'boolean_equivalence_status':'PASS_ZERO_DIFFERENCE' if max(difference)<1e-8 else 'INCONCLUSIVE_COINCIDENT_BOOLEAN_RESULT','status':'PASS_UNCHANGED_NATIVE_GEOMETRY' if max(difference)<1e-8 else 'VALID_REIMPORT_IDENTITY_BOOLEAN_INCONCLUSIVE'})
examples=[]
manifest={'status':'VALID_NATIVE_H12_H23_HELPERS_WITH_EXPLICIT_IDENTITY_CHECK_RESULTS','scope':'Exact native solid extraction and STEP roundtrip identity only;no design changes,normalization,healing or scaling. This is prototype CAD, not a manufacturing drawing or load qualification.','feature_source':str(SOURCE.relative_to(REVIEW)),'feature_source_sha256':sha(SOURCE),'primary_full_native_step':str(NATIVE.relative_to(REVIEW)),'primary_full_native_step_sha256':sha(NATIVE),'primary_native_stl_zip':'native/Flat132_R1_neutral_final.zip','primary_native_stl_zip_sha256':sha(REVIEW/'native/Flat132_R1_neutral_final.zip'),'native_assembly_solid_count':len(solids),'units':'mm','coordinate_system':'Unchanged final neutral assembly coordinates, scale1, no reorientation or origin normalization','output_schema':'AP214IS','software':{'cadquery-ocp':importlib.metadata.version('cadquery-ocp'),'numpy':importlib.metadata.version('numpy'),'trimesh':importlib.metadata.version('trimesh')},'tolerances':'No part manufacturing tolerances assigned. Roundtrip validation thresholds are numerical checks only, not machining tolerances.','identity_method':'Unique native solid correspondence to final individual native STL using all6bounds and volume, then direct STEPControl_AsIs transfer of that native solid. Reimported STEP must be1validsolid with matching bounds,volume,area and zero minimum shape distance. Two-way Boolean comparison is recorded explicitly; an inconclusive coincidence result is not reported as zero difference.','parts':rows,'comparison_limitation':'For any INCONCLUSIVE_COINCIDENT_BOOLEAN_RESULT, do not infer a proved zero symmetric difference. The source solid is transferred directly without shape operations; full native assembly STEP remains the geometric authority.'}
(HERE/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'status':manifest['status'],'files':len(rows),'roundtrip_difference_volumes_mm3':[[r['reference'],r['native_minus_reimport_volume_mm3'],r['reimport_minus_native_volume_mm3']] for r in rows]},indent=2))
