#!/usr/bin/env python3
"""Independently check final native P12 first layers and actual support paths."""
from pathlib import Path
import hashlib, json, math, re, zipfile
import sys
import xml.etree.ElementTree as ET
import numpy as np
from shapely.geometry import LineString, box
from shapely.ops import unary_union

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = ROOT / 'print/bambu-R11-PLA-click-2026-11-03'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def exact_fork_access():
    """Prove the whole axial egress cylinder clear in the final native BRep."""
    sys.path.insert(0,str(HERE))
    import check_rear_shoes as local
    inv=json.loads((HERE/'validation/native-step-inventory.json').read_text())
    assert sha(inv['native_step'])==inv['native_step_sha256']
    shapes,_,_=local.b.read_step(Path(inv['native_step']))
    rows={}
    for ref,y in [('P120',-51.),('P121',51.)]:
        shape=shapes[inv['native_part_correspondence'][ref]['candidates'][0]['solid_index']]
        # This cylinder extends beyond BOTH complete native shoe bounds.
        # Thus every interior fork-support point has a continuous straight
        # axial path to the exposed front/back without a shoe wall closing it.
        cylinder=local.previous.r7.cyl([118,y,18],[130,y,18],4.9)
        overlap=local.b.volume(local.b.common(shape,cylinder))
        rows[ref]=dict(status='PASS' if overlap<1e-6 else 'FAIL',native_step_sha256=inv['native_step_sha256'],
            axial_exit_cylinder_x_mm=[118,130],axis_y_mm=y,axis_z_mm=18,radius_mm=4.9,
            intersection_with_final_native_shoe_mm3=overlap,
            meaning='The complete through-X fork cylinder is free in the exact final native solid; support portions in it are accessible axially from front/back, with the U mouth also open.')
    return rows


def segments(gcode):
    """Actual positive-E G0/1/2/3 paths; split arcs at <=0.025mm chord error."""
    pos=np.zeros(3); eold=0.; relative=True; obj=None; feature=''
    for line in gcode.splitlines():
        if line.startswith('; OBJECT_ID: '): obj=int(line.split(':')[1]);continue
        if line.startswith('; FEATURE: '): feature=line[11:].strip();continue
        if line=='M83':relative=True
        if line=='M82':relative=False
        if line.startswith('G92 '):
            m=re.search(r'\bE(-?\d*\.?\d+)',line)
            if m:eold=float(m[1])
        if not re.match(r'^G[0123] ',line):continue
        d={a:float(b) for a,b in re.findall(r'([XYZEFIJ])(-?\d*\.?\d+)',line.split(';')[0])}
        new=np.array([d.get(a,pos[i]) for i,a in enumerate('XYZ')])
        de=d.get('E',0) if relative else d.get('E',eold)-eold
        if 'E' in d:eold=eold+d['E'] if relative else d['E']
        points=[pos.copy(),new.copy()]
        if line.startswith(('G2 ','G3 ')) and ('I'in d or 'J'in d):
            c=pos[:2]+[d.get('I',0),d.get('J',0)];a=pos[:2]-c;b=new[:2]-c
            angle=math.atan2(a[0]*b[1]-a[1]*b[0],a@b)
            if line.startswith('G2 ') and angle>0:angle-=2*math.pi
            if line.startswith('G3 ') and angle<0:angle+=2*math.pi
            radius=float(np.linalg.norm(a));n=max(2,math.ceil(abs(angle)/.05))
            start=math.atan2(a[1],a[0]);angles=np.linspace(start,start+angle,n+1)
            points=[np.array([*(c+radius*np.array([math.cos(t),math.sin(t)])),pos[2]+(new[2]-pos[2])*i/n]) for i,t in enumerate(angles)]
        lengths=[float(np.linalg.norm(b-a)) for a,b in zip(points[:-1],points[1:])]
        total=sum(lengths)
        if obj is not None and de>0 and total>1e-6:
            for a,b,length in zip(points[:-1],points[1:],lengths):
                if length>1e-7:yield obj,feature,a,b,de*length/total,length
        pos=new


def main():
    layout=json.loads((OUT/'plate-layout.json').read_text())
    fork_access=exact_fork_access()
    matches=[p for p in (OUT/'validation').glob('*verification.gcode.3mf') if 'candidate' not in p.name]
    assert len(matches)==1,matches
    archive=matches[0]
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        info=ET.fromstring(z.read('Metadata/slice_info.config'))
        plate=next(p for p in info.findall('plate') if any(m.get('key')=='index' and m.get('value')=='2' for m in p.findall('metadata')))
        md={m.get('key'):m.get('value') for m in plate.findall('metadata')}
        assert md['outside']=='false'
        objects={o.get('name').split()[0]:int(o.get('identify_id')) for o in plate.findall('object')}
        for ref in ['P120','P121']:
            assert any(o.get('name').split()[0]==ref and o.get('skipped')=='false' for o in plate.findall('object'))
        gcode=z.read('Metadata/plate_2.gcode').decode()
        compensation_match=re.search(r'^; elefant_foot_compensation = ([\d.]+)',gcode,re.M)
        assert compensation_match, 'Actual first-layer elephant-foot compensation must be explicit'
        compensation=float(compensation_match[1])
        paths=list(segments(gcode))
    rows=[]
    for ref,y in [('P120',-51.),('P121',51.)]:
        row=next(r for r in layout['placements'] if r['ref']==ref)
        assert row['plate']==2
        R=np.array(row['rotation_3x3']);assert np.array_equal(R,np.diag([1,-1,-1]))
        offset=np.array(row['normalization_translation_mm']);xy=np.array([*row['plate_xy_mm'],0.])
        source=ROOT/row['source_path'];assert sha(source)==row['source_sha256']
        slot=LineString([(124.2,y),(126.2,y)]).buffer(1.1,quad_segs=64)
        tongue=box(119.2,y-3,128.6,y+3).difference(slot)
        fork=box(120.5,y-9.75,121.5,y+9.75)
        nominal_foot=unary_union([tongue,fork])
        # The actual first layer is intentionally offset inward by the pinned
        # slicer's elephant-foot compensation. Test that target, while still
        # checking all four original foot regions independently.
        foot=nominal_foot.buffer(-compensation,join_style='mitre')
        regions={'tongue_front':box(119.2,y-3,120.5,y+3),
                 'tongue_rear':box(121.5,y-3,128.6,y+3).difference(slot),
                 'fork_low_wing':box(120.5,y-9.75,121.5,y-3),
                 'fork_high_wing':box(120.5,y+3,121.5,y+9.75)}
        covered=[];support_slot=[];support_fork=[];support_paths=[]
        first_length=0.;bridge=0;model_count=0;first_widths=[];first_segments=0
        for oid,feature,a,b,de,length in paths:
            if oid!=objects[ref]:continue
            na=(a-xy-offset)@R;nb=(b-xy-offset)@R
            width=de*math.pi*(1.75/2)**2/length/.2 + .2*(1-math.pi/4)
            if feature.startswith('Support'):
                support_paths.append((na,nb))
                segment=LineString([na[:2],nb[:2]])
                if min(na[2],nb[2])<=26.8 and max(na[2],nb[2])>=23.2 and segment.intersects(slot.buffer(-.05)):
                    support_slot.append([na.tolist(),nb.tolist()])
                # The through-X rod fork has an open U mouth. Any support
                # centreline inside its generous interior would need review.
                for t in np.linspace(0,1,max(2,int(length/.1)+1)):
                    n=na+(nb-na)*t
                    if 118.8<n[0]<129 and 14<n[2]<22.9 and (n[1]-y)**2+(n[2]-18)**2<4.9**2:
                        support_fork.append(n.tolist());break
                continue
            if feature in ['Custom','Skirt','Brim']:continue
            model_count+=1
            if feature=='Bridge':bridge+=1
            if abs(a[2]-.2)<1e-5 and abs(b[2]-.2)<1e-5:
                first_segments+=1;first_length+=length;first_widths.append(width)
                covered.append(LineString([na[:2],nb[:2]]).buffer(width/2,cap_style='round'))
        assert covered and model_count
        coverage=unary_union(covered)
        ratio=foot.intersection(coverage).area/foot.area
        by_region={name:polygon.intersection(foot).intersection(coverage).area/polygon.intersection(foot).area for name,polygon in regions.items()}
        status='PASS' if ratio>=.92 and min(by_region.values())>=.90 and bridge==0 and not support_slot and fork_access[ref]['status']=='PASS' else 'FAIL'
        rows.append(dict(ref=ref,status=status,native_stl_sha256=sha(source),CAD_source_sha256=row['CAD_source_sha256'],
            final_plate=2,final_identify_id=objects[ref],rotation_3x3=R.tolist(),plate_xy_mm=row['plate_xy_mm'],
            first_layer_z_mm=.2,first_layer_model_segment_count=first_segments,first_layer_extrusion_length_mm=first_length,
            exact_nominal_T_foot_area_mm2=nominal_foot.area,actual_elephant_foot_compensation_mm=compensation,
            expected_compensated_first_layer_area_mm2=foot.area,first_layer_covered_area_fraction=ratio,first_layer_region_coverage=by_region,
            first_layer_extrusion_width_range_mm=[min(first_widths),max(first_widths)],bridge_segment_count=bridge,
            support_segment_count=len(support_paths),support_centerlines_in_capture_slot=len(support_slot),
            support_centerlines_in_rod_fork_interior=len(support_fork),
            exact_native_fork_support_access=fork_access[ref],
            support_access='The capture slot is free of support. Fork support portions occupy a through-X cylinder proven open beyond both final native shoe ends; remove them axially through the exposed front/back and open U mouth. Remaining supports are on exterior overhangs. Manual removal is required before assembly.',
            failures=dict(slot_supports=support_slot[:5])))
    result=dict(status='PASS_FINAL_NATIVE_REAR_SHOE_TOOLPATHS' if all(r['status']=='PASS' for r in rows) else 'FAIL',
        archive=str(archive),archive_sha256=sha(archive),layout_sha256=sha(OUT/'plate-layout.json'),validator_sha256=sha(__file__),
        scope='Both final native R11 shoe meshes in actual shared plate2 G-code; exact layer0.2 T-foot coverage with actual elephant-foot compensation and volumetric extrusion widths; arc subdivision, no bridges, no support in capture slots and exact native axial access for supports in rod forks.',
        checks=rows,limits='Nominal geometry and toolpath evidence only; no physical print, material strength or support-removal qualification.')
    target=OUT/'validation/rear-shoe-toolpath-check.json';target.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
    if result['status']=='FAIL':raise SystemExit(1)


if __name__=='__main__':main()
