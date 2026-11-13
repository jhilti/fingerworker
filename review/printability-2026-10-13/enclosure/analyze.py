from pathlib import Path
import trimesh as tm,numpy as np,json,zipfile,re
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
PARTS=ROOT/'print/all-print-prototype-2026-10-13-RevD/PETG'
keys=['P02','P03a','P03b','P08','P09','P10','P060','P061']
report={}
for k in keys:
 p=next(PARTS.glob(k+'_*.stl'));m=tm.load_mesh(p);m.apply_translation(-m.bounds[0]);a=m.area_faces;n=m.face_normals;c=m.triangles_center
 variants={'current':m}
 if k in ['P060','P061']:
  alt=m.copy();alt.apply_transform(tm.transformations.rotation_matrix(np.pi/2,[0,1,0]));alt.apply_translation(-alt.bounds[0]);variants['closed_rear_face_on_bed']=alt
 for v,mesh in variants.items():
  a=mesh.area_faces;n=mesh.face_normals;c=mesh.triangles_center
  report.setdefault(k,{})[v]=dict(size_mm=mesh.extents.tolist(),volume_mm3=mesh.volume,bed_contact_geometric_mm2=float(a[(n[:,2]<-.999)&(c[:,2]<.002)].sum()),downward_faces_above_first_layer_mm2=float(a[(n[:,2]<-.5)&(c[:,2]>.21)].sum()),watertight=mesh.is_watertight)
  if v!='current':mesh.export(OUT/(k+'_'+v+'.stl'))

labels={8:'P02',9:'P060',10:'P061',11:'P08',12:'P09',13:'P10',27:'P03a',28:'P03b'}
segments={k:[] for k in keys}
with zipfile.ZipFile(ROOT/'review/coupon-orientation-2026-10-13/H2D-RevE-verification.gcode.3mf') as z:
 for plate in [3,4,6]:
  x=y=zz=0.;obj=None;feature=None;width=None;height=None;f=0
  for line in z.read(f'Metadata/plate_{plate}.gcode').decode().splitlines():
   if 'start printing object, unique label id:' in line:obj=int(line.split(':')[-1])
   elif 'stop printing object' in line:obj=None
   elif line.startswith('; FEATURE: '):feature=line[11:]
   elif line.startswith('; LINE_WIDTH: '):width=float(line[14:])
   elif line.startswith('; LAYER_HEIGHT: '):height=float(line[16:])
   elif line.startswith('G92 '):
    vals={k:float(v) for k,v in re.findall(r'([XYZ])([+\-\.\d]+)',line)}
    x=vals.get('X',x);y=vals.get('Y',y);zz=vals.get('Z',zz)
   elif re.match(r'^G[0123] ',line):
    vals={k:float(v) for k,v in re.findall(r'([XYZEF])([+\-\.\d]+)',line)}
    nx=vals.get('X',x);ny=vals.get('Y',y);nz=vals.get('Z',zz);f=vals.get('F',f);e=vals.get('E',0)
    if obj in labels and e>0 and ('X' in vals or 'Y' in vals):
     segments[labels[obj]].append(dict(feature=feature,xy_len_mm=float(np.hypot(nx-x,ny-y)),z=nz,e=e,width=width,speed_mm_s=f/60))
    x,y,zz=nx,ny,nz
for k,ss in segments.items():
 features={}
 for s in ss:
  a=features.setdefault(s['feature'],dict(segments=0,max_segment_mm=0,xy_path_mm=0,e_mm=0,min_z_mm=999,max_z_mm=0,max_speed_mm_s=0))
  a['segments']+=1;a['max_segment_mm']=max(a['max_segment_mm'],s['xy_len_mm']);a['xy_path_mm']+=s['xy_len_mm'];a['e_mm']+=s['e'];a['min_z_mm']=min(a['min_z_mm'],s['z']);a['max_z_mm']=max(a['max_z_mm'],s['z']);a['max_speed_mm_s']=max(a['max_speed_mm_s'],s['speed_mm_s'])
 report[k]['current']['slicer_features']=features
(OUT/'geometry-and-toolpaths.json').write_text(json.dumps(report,indent=2)+'\n')
for k,v in report.items():
 print(k, {mode:{key:round(n,2) if isinstance(n,float) else n for key,n in metrics.items() if key!='slicer_features'} for mode,metrics in v.items()})
 print(' bridges/support:',{f:a for f,a in v['current']['slicer_features'].items() if 'bridge' in f.lower() or 'support' in f.lower()})
