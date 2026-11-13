from pathlib import Path
import importlib.util,json
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.TopAbs import TopAbs_SOLID,TopAbs_FACE
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('r',P/'rim_measurements.py');r=importlib.util.module_from_spec(s);s.loader.exec_module(r);b=r.b
old,_,_=r.baseline();rawold,_,_=r.a.a.baseline();ss,inv,_=b.read_step(r.STUDY/'native-probe/Flat132_R19_thumb_rim_probe_AP214.step');frame=ss[next(i for i,q in enumerate(inv) if q['bounds_mm'][0][0]<-40 and q['bounds_mm'][1][0]>120 and q['bounds_mm'][1][1]-q['bounds_mm'][0][1]>130)]
r.a.enable_native_boundary_tolerance();rawbuild=r.a.a.r16;raw=rawbuild.profile(-63,63,rawbuild.RAIL_LINES,rawbuild.RAIL_ARCS,3,[rawbuild.RAIL_MID]);void=b.cut(raw,rawold['P01']);print('VOID',BRepCheck_Analyzer(void).IsValid(),b.volume(void),flush=True)
fs=r.faces(frame);measure=json.loads((P/'rim-probe-check.json').read_text())['rim_measurements'];rows=[]
for sign in [-1,1]:
 pocket=b.common(void,r.a.a.side_box(-30,-24.5,42,60,14,26,sign));ids=set(q['face_zero_index'] for q in measure if q['baseline_point_mm'][1]*sign>0)
 distances=[dict(face_zero_index=i,gap_mm=b.gap(fs[i],pocket),bounds=b.bounds(fs[i]).tolist()) for i in sorted(ids)]
 print('FACEDIST',sign,distances,flush=True)
 roi=r.a.a.side_box(-32,-12,58.7,65.2,21.49,33.2,sign)
 a=b.common(old['P01'],roi);c=b.common(frame,roi);print('CLIPS',sign,BRepCheck_Analyzer(a).IsValid(),b.volume(a),BRepCheck_Analyzer(c).IsValid(),b.volume(c),flush=True)
 inc=b.cut(c,a);rem=b.cut(a,c);print('DELTA',sign,BRepCheck_Analyzer(inc).IsValid(),b.volume(inc),b.count(inc,TopAbs_SOLID),BRepCheck_Analyzer(rem).IsValid(),b.volume(rem),b.bounds(rem).tolist(),flush=True)
 rows.append(dict(sign=sign,distances=distances,old_region_volume=b.volume(a),new_region_volume=b.volume(c),added_valid=BRepCheck_Analyzer(inc).IsValid(),added_volume=b.volume(inc),added_solids=b.count(inc,TopAbs_SOLID),removed_valid=BRepCheck_Analyzer(rem).IsValid(),removed_volume=b.volume(rem),removed_bounds=b.bounds(rem).tolist(),web_removed_to_pocket=b.gap(rem,pocket)))
(P/'scoped-rim-measurements.json').write_text(json.dumps(rows,indent=2)+'\n')
