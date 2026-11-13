#!/usr/bin/env python3
"""Inspect actual R14 final H2D extrusion paths in native CAD coordinates.

No geometry/project edits. Retained P08/P09 regions derive from the R11
enclosure/check_final_toolpaths.py checker. P06 and P01 catches are new.
"""
from pathlib import Path
import argparse,hashlib,json,math,re,sys,zipfile,xml.etree.ElementTree as ET
from collections import Counter
import numpy as np

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
SUPPORT={'Support','Support interface','Support transition'}
NONMODEL=SUPPORT|{'Brim','Skirt','Custom'}
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def parse(data,single_object=None):
    obj=None;feature='';xyz=np.zeros(3);width=.4;height=.2;speed=0.;relative=True;eold=0.;paths=[]
    for line in data.splitlines():
        if 'start printing object, unique label id:' in line:obj=int(line.split(':')[-1])
        elif line.startswith('; OBJECT_ID: ') and single_object is not None:obj=single_object
        elif 'stop printing object' in line:obj=None
        elif line.startswith('; FEATURE: '):
            feature=line[11:].strip()
            if feature=='Custom':obj=None
        elif line.startswith('; LINE_WIDTH: '):width=float(line.split(':')[1])
        elif line.startswith('; LAYER_HEIGHT: '):height=float(line.split(':')[1])
        elif line.startswith('M83'):relative=True
        elif line.startswith('M82'):relative=False
        elif line.startswith('G92 '):
            v={k:float(n) for k,n in re.findall(r'([XYZE])([-+.\d]+)',line)}
            for i,k in enumerate('XYZ'):xyz[i]=v.get(k,xyz[i])
            eold=v.get('E',eold)
        elif re.match(r'^G[0123] ',line):
            v={k:float(n) for k,n in re.findall(r'([XYZEFIJ])([-+.\d]+)',line.split(';')[0])}
            nxt=np.array([v.get(k,xyz[i]) for i,k in enumerate('XYZ')]);speed=v.get('F',speed)
            de=v.get('E',0) if relative else v.get('E',eold)-eold
            if 'E' in v:eold=eold+v['E'] if relative else v['E']
            points=[xyz.copy(),nxt.copy()];length=float(np.linalg.norm(nxt[:2]-xyz[:2]));arc=None
            if line.startswith(('G2 ','G3 ')):
                center=xyz[:2]+[v.get('I',0),v.get('J',0)];radius=float(np.linalg.norm(xyz[:2]-center))
                a1=math.atan2(*(xyz[:2]-center)[::-1]);a2=math.atan2(*(nxt[:2]-center)[::-1]);ccw=line.startswith('G3 ')
                angle=((a2-a1) if ccw else (a1-a2))%(2*math.pi)
                if angle<1e-10 and np.linalg.norm(nxt[:2]-xyz[:2])<1e-7 and radius>1e-5:angle=2*math.pi
                length=radius*angle
                arc=dict(center=np.array([*center,nxt[2]]),radius=radius,sweep=angle,ccw=ccw)
                for theta in (0,math.pi/2,math.pi,3*math.pi/2):
                    d=((theta-a1) if ccw else (a1-theta))%(2*math.pi)
                    if d<=angle+1e-9:points.append(np.array([center[0]+radius*math.cos(theta),center[1]+radius*math.sin(theta),nxt[2]]))
            if de>1e-8 and length>1e-6 and ('X' in v or 'Y' in v):
                paths.append(dict(obj=obj,feature=feature,a=xyz.copy(),b=nxt.copy(),points=np.array(points),length=length,
                    width=width,height=height,speed_mm_s=speed/60,arc=arc))
            xyz=nxt
    return paths

def native_paths(paths,row):
    R=np.asarray(row['rotation_3x3']);offset=np.asarray(row['normalization_translation_mm'])+[*row['plate_xy_mm'],0]
    result=[]
    for s in paths:
        n=dict(s)
        for k in ('a','b'):n['native_'+k]=R.T@(s[k]-offset)
        n['native_mid']=(n['native_a']+n['native_b'])/2
        n['native_points']=(s['points']-offset)@R
        if s['arc'] is not None:n['native_arc_center']=R.T@(s['arc']['center']-offset)
        result.append(n)
    return result

def roi(paths,lo,hi):
    lo=np.asarray(lo);hi=np.asarray(hi)
    return [s for s in paths if np.all(s['native_mid']>=lo) and np.all(s['native_mid']<=hi)]

def xy_path_distance(s,point):
    """Exact line/circular-arc centerline distance in native XY (no tilt)."""
    point=np.asarray(point);a=s['native_a'][:2];c=s['native_b'][:2]
    if s['arc'] is None:
        d=c-a;u=np.clip(np.dot(point-a,d)/max(np.dot(d,d),1e-20),0,1)
        return float(np.linalg.norm(point-(a+u*d)))
    center=s['native_arc_center'][:2];arc=s['arc'];start=math.atan2(*(a-center)[::-1])
    theta=math.atan2(*(point-center)[::-1]);sweep=((theta-start) if arc['ccw'] else (start-theta))%(2*math.pi)
    if sweep<=arc['sweep']+1e-9:return abs(float(np.linalg.norm(point-center))-arc['radius'])
    return min(float(np.linalg.norm(point-a)),float(np.linalg.norm(point-c)))

def xy_line(s):
    from shapely.geometry import LineString
    if s['arc'] is None:return LineString([s['native_a'][:2],s['native_b'][:2]])
    arc=s['arc'];center=s['native_arc_center'][:2]
    start=math.atan2(*(s['native_a'][:2]-center)[::-1]);sign=1 if arc['ccw'] else -1
    angles=start+sign*np.linspace(0,arc['sweep'],max(2,math.ceil(s['length']/.05)+1))
    points=center+arc['radius']*np.column_stack([np.cos(angles),np.sin(angles)])
    return LineString(points)

def free_bridge_spans(bridges,model):
    """Bridge-tagged segments include supported anchors; measure actual air gap."""
    from shapely.ops import unary_union
    results=[]
    for z in sorted({round(s['native_b'][2],5) for s in bridges}):
        current=[s for s in bridges if abs(s['native_b'][2]-z)<1e-4]
        points=np.concatenate([s['native_points'] for s in current]);lo=points[:,:2].min(0)-.6;hi=points[:,:2].max(0)+.6
        height=max(s['height'] for s in current)
        prior=[s for s in model if abs(s['native_b'][2]-(z-height))<.002
            and np.all(s['native_points'][:,:2].max(0)>=lo) and np.all(s['native_points'][:,:2].min(0)<=hi)]
        footprint=unary_union([xy_line(s).buffer(s['width']/2,quad_segs=12) for s in prior])
        maximum=0.
        for s in current:
            unsupported=xy_line(s).difference(footprint)
            lengths=[g.length for g in unsupported.geoms] if hasattr(unsupported,'geoms') else [unsupported.length]
            maximum=max(maximum,max(lengths,default=0.))
        results.append(dict(native_top_z_mm=z,prior_layer_model_segments=len(prior),longest_actual_unbacked_centerline_mm=maximum))
    return results

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--pack',type=Path,default=HERE.parent)
    ap.add_argument('--layout',type=Path);ap.add_argument('--slice',type=Path);ap.add_argument('--output',type=Path)
    ap.add_argument('--native-inventory',type=Path,default=ROOT/'review/near-palm-2026-11-06/validation/native-step-inventory.json')
    args=ap.parse_args();pack=args.pack.resolve();layout_path=args.layout or pack/'plate-layout.json'
    layout=json.loads(layout_path.read_text());plan={r['ref']:r for r in layout['placements']}
    sliced=args.slice or pack/'validation'/(Path(layout['native_project']).stem+'_verification.gcode.3mf')
    target=args.output or pack/'validation/print-feature-check.json'
    starting_layout_sha=sha(layout_path);starting_slice_sha=sha(sliced)
    checks=[];metrics={};transformed={};labels={};actual_settings={}
    def add(name,ok,**detail):checks.append(dict(name=name,status='PASS' if ok else 'FAIL',**detail))
    with zipfile.ZipFile(sliced) as z:
        project_settings=json.loads(z.read('Metadata/project_settings.config'))
        info=ET.fromstring(z.read('Metadata/slice_info.config'))
        config=ET.fromstring(z.read('Metadata/model_settings.config'))
        for ob in config.findall('object'):
            md={m.get('key'):m.get('value') for m in ob.findall('metadata')};name=md.get('name','').split(' - ')[0]
            actual_settings[name]=md
        platepaths={}
        for plate in info.findall('plate'):
            md={m.get('key'):m.get('value') for m in plate.findall('metadata')};p=int(md['index'])
            objects=plate.findall('object');single=int(objects[0].get('identify_id')) if len(objects)==1 else None
            platepaths[p]=parse(z.read(f'Metadata/plate_{p}.gcode').decode(),single)
            for ob in objects:
                for ref in ('P01','P06','Q01'):
                    if ob.get('name','').startswith(ref+' '):labels[ref]=(p,int(ob.get('identify_id')))
    for ref in ('P01','P06','Q01'):
        row=plan[ref];plate,label=labels[ref];assert plate==row['plate']
        paths=native_paths([s for s in platepaths[plate] if s['obj']==label],row);transformed[ref]=paths
        model=[s for s in paths if s['obj']==label and s['feature'] not in NONMODEL]
        supports=[s for s in paths if s['feature'] in SUPPORT]
        first=[s for s in model if s['b'][2]<=.201]
        bridges=[s for s in model if 'bridge' in s['feature'].lower()]
        mm=dict(plate=plate,label_id=label,model_segments=len(model),first_layer_path_mm=sum(s['length'] for s in first),
            maximum_print_z_mm=max(s['b'][2] for s in model),bridge_segments=len(bridges),
            longest_bridge_mm=max([s['length'] for s in bridges] or [0]),native_stl_sha256=row['source_sha256'])
        metrics[ref]=mm
        add(ref+' present from first layer',mm['first_layer_path_mm']>10,**mm)
        add(ref+' full native mesh height printed',abs(mm['maximum_print_z_mm']-row['size_oriented_mm'][2])<=.201,
            expected_print_height_mm=row['size_oriented_mm'][2],actual_print_height_mm=mm['maximum_print_z_mm'])
        if ref=='P06':
            gate_support=roi(supports,[104.4,-68,4.25],[129.4,68,28.3])
            add('P06 support disabled in actual project',str(actual_settings[ref].get('enable_support'))=='0',actual_enable_support=actual_settings[ref].get('enable_support'))
            add('P06 no actual support in gate or clip envelope',not gate_support,support_segments=len(gate_support))
            for side in (-1,1):
                lo,hi=([66.3,67.7] if side>0 else [-67.7,-66.3])
                beam=roi(model,[108.2,lo,4.4],[125.8,hi,7.6]);bed=[s for s in beam if s['b'][2]<=.201]
                xx=[s[k][0] for s in bed for k in ('native_a','native_b')]
                span=max(xx)-min(xx) if xx else 0
                add('P06 long clip beam lies fully on bed side'+str(side),span>16 and sum(s['length'] for s in bed)>30,
                    native_first_layer_X_span_mm=span,first_layer_beam_path_mm=sum(s['length'] for s in bed))
                yy=([65.5,66.7] if side>0 else [-66.7,-65.5])
                hook=roi(model,[104.7,yy[0],4.4],[108.1,yy[1],7.6])
                top=max([s['native_b'][2] for s in hook] or [-999])
                add('P06 hook complete side'+str(side),len(hook)>20 and top>=7.35,model_segments=len(hook),native_top_z_mm=top)
                yy=([65.2,66.2] if side>0 else [-66.2,-65.2])
                free=roi(model,[110.7,yy[0],4.4],[125.6,yy[1],7.4])
                add('P06 free flexure gap printed open side'+str(side),not free,unexpected_model_segments=len(free))
                center=side*51
                bore=roi(model,[119.3,center-2.9,15.1],[125.8,center+2.9,20.9])
                inside=[s for s in bore if (s['native_mid'][1]-center)**2+(s['native_mid'][2]-18)**2<2.85**2]
                add('P06 functional round rod passage stays empty side'+str(side),not inside,unexpected_model_centerlines_in_R2_85_mm=len(inside))
                roof=roi(model,[119.2,center-2.4,20.05],[125.8,center+2.4,22.55])
                roofbridge=[s for s in roof if 'bridge' in s['feature'].lower()]
                maxbridge=max([s['length'] for s in roofbridge] or [0])
                spans=free_bridge_spans(roofbridge,model)
                maxfree=max([s['longest_actual_unbacked_centerline_mm'] for s in spans] or [0])
                add('P06 teardrop roof has no long unsupported span side'+str(side),bool(roof) and maxfree<=1.0,
                    roof_model_segments=len(roof),roof_bridge_segments=len(roofbridge),longest_bridge_tagged_path_mm=maxbridge,
                    longest_actual_unbacked_centerline_mm=maxfree,layer_evidence=spans,
                    method='Subtract prior-layer actual model extrusion footprints from bridge centerlines; tagged paths include their supported anchors.')
                for offset in (-9.5,9.5):
                    axis=[124.5,center+offset]
                    lower=[s for s in model if 4.55<=s['native_b'][2]<=27.95 and xy_path_distance(s,axis)<1.45]
                    upper=[s for s in model if 10.05<s['native_b'][2]-s['height']/2 and s['native_b'][2]<=27.95 and xy_path_distance(s,axis)<2.95]
                    add('P06 optional M3 bore open in actual paths Y'+str(center+offset),not lower and not upper,
                        unexpected_lower_R1_45_centerlines=len(lower),unexpected_upper_R2_95_centerlines=len(upper),
                        method='Full shaft remains clear throughout height; head cavity evaluated above its Z10 datum using actual layer midpoint, excluding the straddling transition layer.')
            bridge=roi(first,[125.0,-30,4.4],[129.1,30,4.8])
            yy=[s[k][1] for s in bridge for k in ('native_a','native_b')]
            span=max(yy)-min(yy) if yy else 0
            add('P06 transverse bridge connected to bed',span>=55,first_layer_native_Y_span_mm=span)
        elif ref=='P01':
            # Fixed front support replaces the complete central preload stack.
            # Its contact face is vertical; the lower pillar grows from the
            # base, with two45-degree widening shoulders and no ceiling above.
            pillar=roi(model,[-16.05,-8.9,4.1],[-11.95,8.9,9.4])
            add('P01 fixed sensor support grows continuously from base',len(pillar)>30,model_segments=len(pillar))
            face=roi(model,[-12.3,-8.5,4.5],[-11.7,8.5,25.9])
            heights=sorted({round(s['native_b'][2],4) for s in face})
            add('P01 fixed support vertical contact face present',len(face)>50 and bool(heights) and min(heights)<5 and max(heights)>25.5,
                model_segments=len(face),contact_face_height_range_mm=[min(heights),max(heights)] if heights else None)
            contactsupport=roi(supports,[-12.35,-8.7,4.3],[-11.6,8.7,26.1])
            add('P01 fixed sensor contact face support-free',not contactsupport,support_segments=len(contactsupport))
            for side in (-1,1):
                yy=([8.9,11.1] if side>0 else [-11.1,-8.9])
                shoulder=roi(model,[-16.1,yy[0],9.5],[-11.9,yy[1],11.6])
                shouldersupport=roi(supports,[-16.1,yy[0],9.3],[-11.6,yy[1],11.6])
                add('P01 fixed support45-degree shoulder side'+str(side),len(shoulder)>5 and not shouldersupport,
                    model_segments=len(shoulder),support_segments=len(shouldersupport))
            roof=roi(model,[-15.7,-20.0,30.1],[-12.6,20.0,32.9])
            roofsupport=roi(supports,[-15.7,-20.0,26.2],[-12.3,20.0,30.1])
            add('P01 obsolete front reaction roof absent',not roof,unexpected_model_segments=len(roof))
            add('P01 no roof support trapped above fixed sensor pad',not roofsupport,support_segments=len(roofsupport))
            for side in (-1,1):
                yy=([64.0,66.5] if side>0 else [-66.5,-64.0])
                catch=roi(model,[108.05,yy[0],3],[110.65,yy[1],7.9])
                top=max([s['native_b'][2] for s in catch] or [-999])
                add('P01 rear latch catch full height side'+str(side),len(catch)>10 and top>=7.65,
                    model_segments=len(catch),native_top_z_mm=top)
                support=roi(supports,[107.8,yy[0]-.3,-2.1],[110.9,yy[1]+.3,3.2])
                metrics.setdefault('P01_catch_support',[]).append(dict(side=side,support_segments=len(support),
                    interface_segments=sum(s['feature']=='Support interface' for s in support),
                    chord_or_arc_path_mm=sum(s['length'] for s in support),
                    nominal_access='Exterior side of base; remove outwards in signed Y. No enclosed catch cavity.'))
                blocked=roi(supports,[108.15,yy[0],4.1],[110.55,yy[1],7.75])
                add('P01 latch catch engagement face support-free side'+str(side),not blocked,support_segments_on_catch_face=len(blocked))
        elif ref=='P08':
            add('P08 no long unsupported bridge path',mm['longest_bridge_mm']<4,longest_actual_bridge_tagged_segment_mm=mm['longest_bridge_mm'])
            for side in (-1,1):
                lo,hi=([64.1,65.7] if side>0 else [-65.7,-64.1])
                post=roi(model,[-29.2,lo,-.1],[-25.4,hi,16.4]);top=max([s['native_b'][2] for s in post] or [-999])
                add('P08 retained high palm hook side'+str(side),top>=16.15 and len(post)>100,native_top_z_mm=top,segments=len(post))
                beam=roi(first,[-43.8,lo,-.1],[-30,hi,2.5]);xx=[s[k][0] for s in beam for k in ('native_a','native_b')]
                span=max(xx)-min(xx) if xx else 0
                add('P08 retained long beam bed connection side'+str(side),sum(s['length'] for s in beam)>25 and span>13,
                    first_layer_path_mm=sum(s['length'] for s in beam),native_X_span_mm=span)
                lo,hi=([55.4,63.7] if side>0 else [-63.7,-55.4])
                free=roi(model,[-43.5,lo,-.1],[-30,hi,2.5])
                add('P08 retained open clip gap side'+str(side),not free,unexpected_model_segments=len(free))
            usb=roi(supports,[-42,-55.3,6.5],[-28.5,-53.4,7.6])
            add('P08 USB roof has accessible support',len(usb)>5,support_segments=len(usb),access='Open tray above and13mm USB aperture outside.')
        elif ref=='P09':
            add('P09 retained support-free lid',str(actual_settings[ref].get('enable_support'))=='0' and mm['bridge_segments']==0,
                actual_enable_support=actual_settings[ref].get('enable_support'),bridge_segments=mm['bridge_segments'])
            for name,beam0,free0,free1 in [('negative',-49.2,-28,-25),('positive',18.8,40,43)]:
                beam=roi(first,[-48.8,beam0-.1,4.6],[-47.2,free1+.1,9.1])
                hook=roi(model,[-47.65,free0-.1,4.0],[-46.1,free1+.1,5.9])
                add('P09 retained flat leaf and hook '+name,len(beam)>5 and len(hook)>10,first_layer_arm_segments=len(beam),hook_segments=len(hook))
            for name,y0,y1 in [('negative',-47,-30),('positive',22,38)]:
                gap=roi(model,[-47.05,y0,4.6],[-46.35,y1,9.1])
                add('P09 retained free leaf gap '+name,not gap,unexpected_model_segments=len(gap))
            clip_support=roi(supports,[-49,-54,4],[-46.2,45,9.1])
            add('P09 clips need no support cleanup',not clip_support,support_segments=len(clip_support))
            clamp=roi(model,[-28.3,22.2,3.2],[-24.7,32.8,8.3])
            add('P09 retained integral cable clamp',len(clamp)>50,model_segments=len(clamp))
        elif ref=='Q01':
            # The layout uses assembly coordinates plus an explicit rotation.
            # Inspect the independently documented print frame from its manifest.
            manifest_path=ROOT/row['fixture_manifest_path'];manifest=json.loads(manifest_path.read_text())
            add('Q01 layout binds current fixture manifest',sha(manifest_path)==row['fixture_manifest_sha256'],
                manifest_sha256=sha(manifest_path),expected_sha256=row['fixture_manifest_sha256'])
            matrix=np.asarray(manifest['assembly_to_print_matrix']);rot=matrix[:3,:3];shift=matrix[:3,3]
            def fixture_frame(items):
                result=[]
                for s in items:
                    n=dict(s)
                    for k in ('native_a','native_b','native_mid'):n[k]=rot@s[k]+shift
                    n['native_points']=s['native_points']@rot.T+shift
                    result.append(n)
                return result
            model=fixture_frame(model);supports=fixture_frame(supports);first=fixture_frame(first)
            bounds=np.asarray(manifest['print_bounds_mm']);dims=bounds[1]-bounds[0]
            fixture_support=roi(supports,bounds[0]-.3,bounds[1]+.3)
            add('Q01 current fixed-datum fixture support-free',str(actual_settings[ref].get('enable_support'))=='0' and not fixture_support,
                actual_enable_support=actual_settings[ref].get('enable_support'),support_segments=len(fixture_support))
            add('Q01 tapered shoulder avoids bridge paths',mm['bridge_segments']==0,bridge_segments=mm['bridge_segments'])
            points=np.array([s[k] for s in first for k in ('native_a','native_b')])
            span=points.max(0)-points.min(0) if len(points) else np.zeros(3)
            edge_lo=np.array([s['native_points'][:,:2].min(0)-s['width']/2 for s in first])
            edge_hi=np.array([s['native_points'][:,:2].max(0)+s['width']/2 for s in first])
            printed_span=edge_hi.max(0)-edge_lo.min(0) if len(first) else np.zeros(2)
            foot_comp=float(actual_settings[ref].get('elefant_foot_compensation',project_settings['elefant_foot_compensation']))
            expected_foot=dims[:2]-2*foot_comp
            add('Q01 broad reaction face lies on bed',bool(len(points)) and np.all(abs(printed_span-expected_foot)<=.05),
                first_layer_centerline_XY_span_mm=span[:2].tolist(),first_layer_extrusion_XY_span_mm=printed_span.tolist(),
                reaction_face_XY_dimensions_mm=dims[:2].tolist(),actual_elefant_foot_compensation_mm=foot_comp,
                expected_compensated_first_layer_XY_mm=expected_foot.tolist())
            axis=rot@np.array([manifest['parameters']['pusher_shoulder']['x_mm'][1],*manifest['parameters']['axis_y_z_mm']])+shift
            radius=manifest['parameters']['pusher_shoulder']['radius_mm']
            shoulder=roi(model,axis- [radius+.1,radius+.1,.25],axis+[radius+.1,radius+.1,.1])
            top=[s for s in shoulder if s['feature']=='Top surface']
            add('Q01 P05 bearing shoulder faces upward',len(top)>2,top_surface_segments=len(top))
    # Optional exact native collision check for the complete outward prism of
    # each catch-support bead bounding box. This is conservative: arc extrema
    # are included. It tests clearance, not adhesive strength or break-away force.
    if args.native_inventory.is_file():
        inv=json.loads(args.native_inventory.read_text())
        sys.path.insert(0,str(ROOT/'review/flat132-solid-palm-2026-10-23/validation'))
        import audit_solid_palm as b
        from OCP.BRepCheck import BRepCheck_Analyzer
        def checked_volume(shape):
            assert BRepCheck_Analyzer(shape).IsValid(),'Invalid native CAD Boolean result'
            return b.volume(shape)
        assert sha(inv['native_step'])==inv['native_step_sha256']
        solids,_,_=b.read_step(inv['native_step']);frame=solids[inv['native_part_correspondence']['P01']['candidates'][0]['solid_index']]
        gate=solids[inv['native_part_correspondence']['P06']['candidates'][0]['solid_index']]
        from OCP.BRepPrimAPI import BRepPrimAPI_MakeCylinder
        from OCP.gp import gp_Ax2,gp_Pnt,gp_Dir
        for y in (-60.5,-41.5,41.5,60.5):
            overlaps=[]
            for z0,z1,radius in ((4.45,10.05,1.65),(10.05,28.05,3.15)):
                tool=BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(124.5,y,z0),gp_Dir(0,0,1)),radius,z1-z0).Shape()
                overlaps.append(checked_volume(b.common(gate,tool)))
            add('P06 native optional M3 hole clear through final united bridge Y'+str(y),max(overlaps)<1e-6,
                lower_and_upper_clearance_overlap_mm3=overlaps)
        samples=[]
        row=plan['P01'];R=np.asarray(row['rotation_3x3']);assert np.allclose(R,np.eye(3))
        for side in (-1,1):
            yy=([63.7,66.8] if side>0 else [-66.8,-63.7])
            ss=roi([s for s in transformed['P01'] if s['feature'] in SUPPORT],[107.8,yy[0],-2.1],[110.9,yy[1],3.2])
            maxov=0.;worst=None
            for s in ss:
                pts=s['native_points'];lo=pts.min(0);hi=pts.max(0)
                lo[:2]-=s['width']/2;hi[:2]+=s['width']/2
                # Extrusion line is an obround, so box is deliberately larger.
                lo[2]=hi[2]-s['height'];hi[2]+=1e-5
                if side>0:hi[1]=90
                else:lo[1]=-90
                ov=checked_volume(b.common(frame,b.box(lo,hi)))
                if ov>maxov:maxov=ov;worst=dict(lo=lo.tolist(),hi=hi.tolist(),overlap_mm3=ov)
            add('P01 complete conservative catch-support outward removal side'+str(side),maxov<1e-5,
                tested_support_segments=len(ss),maximum_intersection_upper_bound_mm3=maxov,worst=worst,
                scope='All actual local support bead AABBs including arc extrema, swept outwards to Y±90; only nominal collision accessibility, no break-away force claim.')
        native_sha=inv['native_step_sha256']
    else:
        native_sha=None
        add('Native P01 STEP available for support removal envelope check',False,missing_file=str(args.native_inventory))
    add('Inspected layout and slice stable throughout validation',
        starting_layout_sha==sha(layout_path) and starting_slice_sha==sha(sliced),
        starting_layout_sha256=starting_layout_sha,starting_slice_sha256=starting_slice_sha)
    failures=[c for c in checks if c['status']!='PASS']
    result=dict(status='PASS_R14_PRINT_FEATURES' if not failures else 'FAIL',date='2026-11-06',revision='R14',
        checks=checks,failed_count=len(failures),failures=failures,metrics=metrics,
        sliced_archive_sha256=starting_slice_sha,layout_sha256=starting_layout_sha,CAD_source_sha256=layout['CAD_source_sha256'],
        native_step_sha256=native_sha,validator_sha256=sha(Path(__file__)),
        scope='Actual final H2D0.4 PLA paths for fixed front support, rear gate/clips, rear frame catches, Q01 fixture. Electronics housing/lid and printed rods are omitted.',
        limitations=['No physical PLA fit, fatigue, strength or support-removal-force qualification.',
            'Feature-presence ROIs use segment midpoints; model watertightness and exact native CAD identity belong to separate validators.',
            'Native support clearance uses complete conservative bead boxes and can reject otherwise-clear rounded paths; a positive conservative overlap must be investigated, not silently waived.'])
    target.parent.mkdir(parents=True,exist_ok=True);target.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],checks=len(checks),failures=failures,metrics=metrics),indent=2))
    return bool(failures)

if __name__=='__main__':raise SystemExit(main())
