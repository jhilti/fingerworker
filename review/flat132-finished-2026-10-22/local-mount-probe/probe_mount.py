from pathlib import Path
import trimesh as t, numpy as np, json
R=Path('/Users/jonashilti/Documents/ChatGPT/fingerworker')
OUT=R/'review/flat132-finished-2026-10-22/local-mount-probe';OUT.mkdir(exist_ok=True)
def box(a,b):
 a,b=np.array(a),np.array(b);return t.creation.box(extents=b-a,transform=t.transformations.translation_matrix((a+b)/2))
def cy(a,b,r):
 a,b=np.array(a),np.array(b);v=b-a; m=t.creation.cylinder(radius=r,height=np.linalg.norm(v),sections=160);m.apply_transform(t.geometry.align_vectors([0,0,1],v));m.apply_translation((a+b)/2);return m
def uni(ms):return t.boolean.union(ms,engine='manifold')
def cut(m,ms):return t.boolean.difference([m,*ms],engine='manifold')
def tube(a,b,ro,ri):return cut(cy(a,b,ro),[cy(np.array(a)-.001*(np.array(b)-a),np.array(b)+.001*(np.array(b)-a),ri)])
parts={p.stem:t.load_mesh(p) for p in (R/'review/flat132-hand-fit-2026-10-19/assembly-mm').glob('*.stl')}
for n in ['H01','H01a','H01b','H01c','H01d']:parts.pop(n)
parts['ACTUAL_SENSOR']=t.load_mesh(R/'review/actual-sensor-cad-2026-10-22/sensor/TE_FX1901_actual_apex_aligned_132_mm.stl')
p05cuts=[box([-10.5,-15.3,2.5],[1,15.3,33.5]),box([-10.5,10,12],[-1.4,40,24])]
centres=[(y,z) for y in [-10.5,10.5] for z in [7.5,28.5]]
p05cuts +=[cy([-1.5,y,z],[1.4,y,z],2.6) for y,z in centres]
parts['P05']=cut(parts['P05'],p05cuts)
collar=tube([-9.85,0,18],[-8.65,0,18],13.5,12.75)
collar=cut(collar,[box([-10,10,10.5],[-8.5,29,25.5])]+[cy([-10,y,z],[-8.5,y,z],2.2) for y,z in centres])
H12=uni([box([-12,-15,3],[-9.85,15,33]),collar]+[box([-15.5,-15,4.5],[-9.85,-11.5,11]),box([-15.5,11.5,4.5],[-9.85,15,11])])
H12=cut(H12,[cy([-12.1,y,z],[-9.75,y,z],.85) for y,z in centres]+[cy([-12.8,side*11.9,8.5],[-12.8,side*15.2,8.5],1.55) for side in [-1,1]])
parts['H12']=H12
H23=uni([cy([-1.4,0,18],[-.9,0,18],13.5)]+[box([-1.4,y-4,z-4],[-.9,y+4,z+4]) for y,z in centres])
parts['H23']=cut(H23,[cy([-1.5,0,18],[-.8,0,18],10)]+[cy([-1.5,y,z],[-.8,y,z],1.1) for y,z in centres])
for i,(y,z) in enumerate(centres):
 parts[f'H24{i}']=tube([-9.85,y,z],[-1.4,y,z],2,1.1)
 parts[f'H25{i}']=uni([cy([-12.9,y,z],[-.9,y,z],1),cy([-.9,y,z],[.7,y,z],2)])
for j,side in enumerate([-1,1]):
 parts[f'H18{j}']=uni([cy([-12.8,side*13,8.5],[-12.8,side*21.1,8.5],1.5),cy([-12.8,side*21,8.5],[-12.8,side*24,8.5],2.75)])
 parts[f'H19{j}']=tube([-12.8,side*15,8.5],[-12.8,side*21,8.5],2,1.6)
# Approximate P01 reconstruction from the original native mesh: remove old guides
# above the floor, then reinsert the new guides. Small .2mm joining-face strips
# differ from native regenerated wall, so this is not final manufacturing proof.
P01=cut(parts['P01'],[box([-16.201,-17.001,4],[-7.999,-13.999,29.001]),box([-16.201,13.999,4],[-7.999,17.001,29.001])])
for side in [-1,1]:
 lo=-18.5 if side==-1 else 15.5
 guide=box([-16.2,lo,3.8],[-8,lo+3,29]); slo=-18.7 if side==-1 else 15.3
 tools=[cy([-12.6,side*15.3,8.5],[-12.6,side*18.7,8.5],2.2),cy([-11,side*15.3,8.5],[-11,side*18.7,8.5],2.2),box([-12.6,slo,6.3],[-11,slo+3.4,10.7])]
 if side==1:tools+=[box([-10.2,15.3,12],[-7.8,18.7,24])]
 guide=cut(guide,tools);P01=uni([P01,guide])
parts['P01']=cut(P01,[box([-12.3,-15.3,2.7],[1.4,15.3,4.2])])
for n,m in parts.items():
 if n=='ACTUAL_SENSOR' or n in ['H12','H23','P01','P05'] or n.startswith(('H24','H25','H18','H19')):m.export(OUT/f'{n}.stl')
checks=[]
for a in ['ACTUAL_SENSOR','H12','H23',*[f'H24{i}' for i in range(4)],*[f'H25{i}' for i in range(4)]]:
 for b in parts:
  if b==a:continue
  ma,mb=parts[a],parts[b]
  if np.any(ma.bounds[1]<mb.bounds[0]) or np.any(mb.bounds[1]<ma.bounds[0]):continue
  vol=t.boolean.intersection([ma,mb],engine='manifold').volume
  if vol>1e-5:checks.append({'a':a,'b':b,'mm3':float(vol)})
summary={'scope':'Local approximate primitive/mesh probe only; final native root export required','volumes_mm3':{n:float(m.volume) for n,m in parts.items() if n=='ACTUAL_SENSOR' or n in ['H12','H23','P01','P05'] or n.startswith(('H24','H25','H18','H19'))},'nonzero_intersections':checks}
(OUT/'probe.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
