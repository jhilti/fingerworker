from pathlib import Path
import importlib.util,json
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.TopAbs import TopAbs_SOLID,TopAbs_FACE
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('r',P/'rim_measurements.py');r=importlib.util.module_from_spec(s);s.loader.exec_module(r);b=r.b
old,_,_=r.baseline();ss,inv,_=b.read_step(r.STUDY/'native-probe/Flat132_R19_thumb_rim_probe_AP214.step');frame=ss[next(i for i,q in enumerate(inv) if q['bounds_mm'][0][0]<-40 and q['bounds_mm'][1][0]>120 and q['bounds_mm'][1][1]-q['bounds_mm'][0][1]>130)];r.a.enable_native_boundary_tolerance()
rois={'lower_frame':([-50,-70,-5],[140,70,21.49]),'central_palm_and_sensor':([-50,-58.7,-5],[140,58.7,40]),'front_of_rims':([-12,-70,21.49],[140,70,40]),'wristward_of_rims':([-50,-70,21.49],[-32,70,40]),'above_rims':([-50,-70,33.2],[140,70,40])}
rows=[]
for name,(lo,hi) in rois.items():
 roi=b.box(lo,hi);a=b.common(old['P01'],roi);c=b.common(frame,roi);inc=b.cut(c,a);rem=b.cut(a,c)
 row=dict(name=name,old_valid=BRepCheck_Analyzer(a).IsValid(),new_valid=BRepCheck_Analyzer(c).IsValid(),added_valid=BRepCheck_Analyzer(inc).IsValid(),removed_valid=BRepCheck_Analyzer(rem).IsValid(),added_solids=b.count(inc,TopAbs_SOLID),removed_solids=b.count(rem,TopAbs_SOLID),added_faces=b.count(inc,TopAbs_FACE),removed_faces=b.count(rem,TopAbs_FACE),added_volume=b.volume(inc),removed_volume=b.volume(rem));rows.append(row);print(row,flush=True)
(P/'protected-rim-measurements.json').write_text(json.dumps(rows,indent=2)+'\n')
