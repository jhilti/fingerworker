"""Check a rigid-only turn of the female coupon: full back on bed, no channel roof bridge."""
from pathlib import Path
import json,hashlib
import numpy as np
import trimesh as tm
from scipy.spatial import cKDTree
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
old=tm.load_mesh(OUT/'original/guide_coupon_female.stl')
new=tm.load_mesh(ROOT/'print/guide_coupon_female.stl')
expected=old.vertices*np.array([1,-1,-1])+[0,0,5]
assert cKDTree(expected).query(new.vertices)[0].max()<.000001
assert np.isclose(old.volume,new.volume) and new.is_watertight and new.is_volume
assert np.allclose(old.extents,new.extents)
assert (ROOT/'print/guide_coupon_male.stl').read_bytes()==(OUT/'original/guide_coupon_male.stl').read_bytes()
horizontal_down=new.face_normals[:,2]<-.99999
heights=new.triangles_center[horizontal_down,2]
assert np.allclose(heights,0),heights
area=new.area_faces[horizontal_down].sum();assert np.isclose(area,30*42)
slope_normals=new.face_normals[(new.face_normals[:,2]<-1e-5)&(~horizontal_down)]
assert np.allclose(np.abs(slope_normals[:,2]),1/np.sqrt(2),atol=1e-6)
report=dict(status='PASS',change='Rigid 180 degree rotation about longitudinal X axis; closed back on bed and channel up',
    dimensions_unchanged_mm=new.extents.tolist(),volume_unchanged_mm3=float(new.volume),bed_contact_area_mm2=float(area),
    elevated_horizontal_downward_faces=0,inward_flank_angle_degrees=45,old_channel_bridge_span_mm=33.5,
    male_unchanged=True,female_sha256=hashlib.sha256((ROOT/'print/guide_coupon_female.stl').read_bytes()).hexdigest(),
    generator_sha256=hashlib.sha256((ROOT/'review/make_guide_coupon.py').read_bytes()).hexdigest(),
    limitation='This orientation checks nominal fit without a channel-roof bridge; it does not reproduce the large P04 bridge/underside print process.')
(OUT/'orientation-validation.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS: female rigidly turned over, 1260 mm² bed contact, no elevated horizontal ceiling; male unchanged')
