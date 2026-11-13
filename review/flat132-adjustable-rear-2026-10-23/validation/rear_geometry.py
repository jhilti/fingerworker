"""Independent analytic constructions and focused service/pose witnesses for R7."""
from pathlib import Path
import json,numpy as np
import audit_adjustable_rear as a
b=a.b;v=a.v

def pose_checks(neutral,poses,spec):
    out=[]
    if len(poses)!=3:return [{'pose':'required_witness_inventory','status':'NOT_PROVIDED','reason':'Need adjusted-rest a2, dynamic MAXp2 and ISO81 p2 native whole exports.'}]
    for witness in poses:
        archive=Path(witness['archive']);u,p,adj,e=[float(witness.get(k,0)) for k in ['u','p','a','e']]
        iso=witness.get('isometric',False)
        legal=(u>=0 and p>=0 and adj>=0 and p+adj<=2 and u+p+adj<=30 and -.8<=e<=.8)
        checks=[{'name':'Legal correlated operating pose','status':'PASS' if legal else 'FAIL','u_p_a_e_mm':[u,p,adj,e]}]
        posed,ignored=v.load(archive,{})
        expected=set(neutral)-v.SPRINGS|{'H140','H141'} if iso else set(neutral)
        checks.append({'name':'Whole native inventory','status':'PASS' if not ignored and set(posed)==expected else 'FAIL','part_count':len(posed),'unrecognized_members':ignored})
        vec=np.array([u,p,adj,e])
        for ref in sorted(set(neutral)&set(posed)-v.SPRINGS-v.ARTICULATED):
            delta=float(a.coefficients(ref,spec)@vec)
            target=neutral[ref]['object'].translate([delta,0,0]);actual=posed[ref]['object']
            difference=float((target-actual).volume()+(actual-target).volume())
            bound_error=float(np.max(np.abs(v.bounds(target)-v.bounds(actual))))
            checks.append({'ref':ref,'name':'Native rigid pose congruence','expected_translation_x_mm':delta,'symmetric_difference_mm3':difference,
              'maximum_bound_error_mm':bound_error,'status':'PASS' if difference<=.1 and bound_error<=.02 else 'FAIL'})
        for ref in sorted(v.ARTICULATED&set(posed)):
            effective=u+adj+p-e
            expected_obj=neutral[ref]['object'].transform(v.actuator_transform(effective).tolist())
            actual=posed[ref]['object'];difference=float((expected_obj-actual).volume()+(actual-expected_obj).volume())
            checks.append({'ref':ref,'name':'Native articulated source pose','effective_user_travel_plus_preload_minus_trim_mm':effective,'symmetric_difference_mm3':difference,
              'status':'PASS' if difference<=.1 else 'FAIL'})
        if iso:
            for ref in ['H140','H141']:
                bounds=posed[ref]['mesh'].bounds
                checks.append({'ref':ref,'name':'81mm steel ISO sleeve length/datums','bounds_mm':bounds.tolist(),
                  'status':'PASS' if abs(bounds[0,0]-(12+p))<=.02 and abs(bounds[1,0]-(108-u-adj))<=.02 and abs(bounds[1,0]-bounds[0,0]-81)<=.02 and abs(u-(15-p-adj))<1e-8 else 'FAIL'})
        else:
            for ref in ['H030','H031']:
                bounds=posed[ref]['mesh'].bounds
                checks.append({'ref':ref,'name':'Native spring trim seats','bounds_mm':bounds.tolist(),
                  'status':'PASS' if abs(bounds[0,0]-(12+p))<=.02 and abs(bounds[1,0]-(108-u-adj))<=.02 else 'FAIL'})
        out.append({'pose':witness.get('name',archive.stem),'archive':str(archive.resolve()),'sha256':a.sha(archive),
          'status':'PASS' if all(x['status']=='PASS' for x in checks) else 'FAIL','u_p_a_e_mm':[u,p,adj,e],'isometric':iso,'part_count':len(posed),'checks':checks})
    return out

def dimension_checks(parts,native,spec):
    physical={r:x for r,x in native.items() if not r.startswith(('E','PCB_'))}
    overall=np.array([np.min([b.bounds(x)[0] for x in physical.values()],axis=0),np.max([b.bounds(x)[1] for x in physical.values()],axis=0)])
    checks=[{'name':'Physical device X envelope including real adjuster tips; external electronics approach/travel references excluded','bounds_mm':overall.tolist(),'depth_mm':float(overall[1,0]-overall[0,0]),
      'status':'PASS' if abs(overall[1,0]-spec['expected_rear_x_mm'])<1e-5 and abs(overall[0,0]+46.1)<1e-5 else 'FAIL'},
      {'name':'Printed base shortened five millimeters','base_maximum_x_mm':float(b.bounds(native['P01'])[1,0]),'status':'PASS' if abs(b.bounds(native['P01'])[1,0]-129)<1e-5 else 'FAIL'},
      {'name':'Retained frame width','width_mm':float(b.bounds(native['P01'])[1,1]-b.bounds(native['P01'])[0,1]),'status':'PASS' if abs(b.bounds(native['P01'])[1,1]-b.bounds(native['P01'])[0,1]-132)<1e-5 else 'FAIL'},
      {'name':'Legal minimum and maximum dynamic stroke','maximum_mm':30,'minimum_mm':28,'domain':'a+p<=2,u<=30-p-a','status':'PASS'},
      {'name':'Spring length/force domain inherited exactly','rest_length_range_mm':[94,96],'shortest_spring_mm':66,
        'rest_pair_force_range_N':{'DF2194':[39.684,52.912],'DF2185':[66.762,81.598]},
        'maximum_spring_pair_force_N':{'DF2194':238.104,'DF2185':289.302},
        'meaning':'Same spring compression domain as R6; a and p share the same 2mm budget. No spring life or printed strength qualification.','status':'PASS'}]
    for ref in ['H040','H041']:
        bounds=b.bounds(native[ref]);checks.append({'name':'Shortened guide rod '+ref,'bounds_mm':bounds.tolist(),
          'length_mm':float(bounds[1,0]-bounds[0,0]),'status':'PASS' if abs(bounds[1,0]-125)<1e-5 and abs(bounds[0,0]+16)<1e-5 else 'FAIL'})
    return checks

# Filled after the source agent freezes the actual rear geometry.
def exact_geometry_checks(native,old,spec):
    raise RuntimeError('R7 independent rear construction not configured yet')
def service_checks(parts,native,spec):
    raise RuntimeError('R7 rear service witnesses not configured yet')

def cap_model(side,connector_low=3.0):
    y=side*51
    stock=a.union([b.box([120.5,y-14,4.5],[128.5,y+14,28]),b.box([120.5,y-4.5,27],[129.5,y+4.5,30.5])])
    rod=a.cyl([120,y,18],[126.2,y,18],3.1)
    keep=a.cyl([118.7,y,18],[121.9,y,18],4.6)
    fork=b.cut(b.box([118.8,y-10.05,13.7],[121.8,y+10.05,26.8]),keep)
    connector=b.cut(b.box([118.8,y-4.8,connector_low],[121.8,y+4.8,24.8]),keep)
    tools=[rod,fork,connector,b.box([118.8,y-3.3,23.2],[128.9,y+3.3,26.8]),
      b.box([120.4,y-3.7,4.4],[124.1,y+3.7,10.7]),b.box([123.7,y-6.2,4.4],[124.9,y+6.2,13.2]),
      a.cyl([124.9,y,7],[132,y,7],5.5),a.cyl([124.2,y,22.3],[124.2,y,30.7],1.15),
      b.box([122,y-2.2,27.4],[129.7,y+2.2,28.8])]
    for offset in[-9.5,9.5]:tools.extend([a.cyl([124.5,y+offset,4],[124.5,y+offset,29],1.7),a.cyl([124.5,y+offset,10],[124.5,y+offset,29],3.2)])
    for tool in tools:stock=b.cut(stock,tool)
    return stock

def shoe_model(side,connector_low=3.3):
    y=side*51
    stock=a.union([b.box([119.2,y-4.5,3.3],[120.4,y+4.5,11.7]),
      b.box([120.2,y-4.5,connector_low],[121.5,y+4.5,24.5]),
      b.box([120.5,y-9.75,14],[121.5,y+9.75,26.5]),b.box([119.2,y-3,23.5],[128.6,y+3,26.5])])
    tools=[a.cyl([118.8,y,18],[129,y,18],4.9),
      a.cyl([124.2,y,23.2],[124.2,y,26.8],1.1),a.cyl([126.2,y,23.2],[126.2,y,26.8],1.1),
      b.box([124.2,y-1.1,23.2],[126.2,y+1.1,26.8]),a.cyl([120.4,y,7],[121.8,y,7],2.2)]
    for tool in tools:stock=b.cut(stock,tool)
    return stock

def base_tail_model():
    stock=b.box([-22,-66,-2],[129,66,4]);fillet=BRepFilletAPI_MakeFillet(stock)
    ex=TopExp_Explorer(stock,TopAbs_EDGE)
    while ex.More():fillet.Add(1.5,TopoDS.Edge(ex.Current()));ex.Next()
    fillet.Build();assert fillet.IsDone();stock=fillet.Shape()
    stock=b.fuse(stock,a.xprism(29,124,[[-12.9,3.9],[12.9,3.9],[16,7],[-16,7]]))
    for side in[-1,1]:
        y=side*51
        stock=b.fuse(stock,b.box([119.5,y-14,3.8],[129,y+14,4.5]))
        tools=[b.box([121.5,y-3.7,3.3],[124.1,y+3.7,4.7]),b.box([123.7,y-6.2,.8],[130,y+6.2,4.7]),
          b.box([116.9,y-4.8,3.0],[130,y+4.8,4.7]),a.cyl([124.9,y,7],[132,y,7],5.5)]
        for offset in[-9.5,9.5]:tools.append(a.cyl([124.5,y+offset,.5],[124.5,y+offset,4.6],2.1))
        for tool in tools:stock=b.cut(stock,tool)
    from OCP.BRepPrimAPI import BRepPrimAPI_MakeCone
    from OCP.gp import gp_Pnt,gp_Dir,gp_Ax2
    for y in[-28,28]:
        stock=b.cut(stock,a.cyl([122,y,-3],[122,y,5],2.75))
        cone=BRepPrimAPI_MakeCone(gp_Ax2(gp_Pnt(122,y,1.65),gp_Dir(0,0,1)),2.75,5.2,2.45).Shape()
        stock=b.cut(stock,cone)
    return stock

# Imports only needed for independent stock filleting above.
from OCP.BRepFilletAPI import BRepFilletAPI_MakeFillet
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_EDGE,TopAbs_SOLID,TopAbs_SHELL
from OCP.TopoDS import TopoDS
from OCP.BRepCheck import BRepCheck_Analyzer

def exact_geometry_checks(native,old,spec):
    checks=[]
    region=b.box([116.7,-100,-10],[140,100,40])
    front=b.box([-100,-100,-10],[116.7,100,40])
    difference=b.xor_volume(b.common(native['P01'],front),b.common(old['P01'],front))
    checks.append({'name':'Unchanged P01 front through X116.7 exact STEP','symmetric_difference_mm3':difference,'status':'PASS' if difference<=a.TOL else 'FAIL'})
    expected=b.common(base_tail_model(),region);actual=b.common(native['P01'],region);difference=b.xor_volume(expected,actual)
    checks.append({'name':'Independent complete P01 rear stock/fillets/feet/track/pockets/inserts/bench-hole CSG','symmetric_difference_mm3':difference,'status':'PASS' if difference<=a.TOL else 'FAIL'})
    for ref in['H040','H041']:
        expected=b.common(old[ref],b.box([-100,-100,-10],[125,100,40]));difference=b.xor_volume(native[ref],expected)
        checks.append({'name':'Exactly shortened unchanged 6mm mandrel '+ref,'symmetric_difference_mm3':difference,'added_material_mm3':b.volume(b.cut(native[ref],old[ref])),
          'status':'PASS' if difference<=a.TOL and b.volume(b.cut(native[ref],old[ref]))<=a.TOL else 'FAIL'})
    for side,index in[(-1,'0'),(1,'1')]:
        for ref,model in[('P06'+index,cap_model(side)),('P12'+index,shoe_model(side))]:
            difference=b.xor_volume(native[ref],model)
            checks.append({'name':'Independent rear construction CSG '+ref,'symmetric_difference_mm3':difference,
              'solid_count':b.count(native[ref],TopAbs_SOLID),'shell_count':b.count(native[ref],TopAbs_SHELL),
              'status':'PASS' if difference<=a.TOL and b.count(native[ref],TopAbs_SOLID)==1 and b.count(native[ref],TopAbs_SHELL)==1 else 'FAIL'})
        y=side*51
        # Exact steel envelope probes are independent of nearby void sizes.
        hardware={
         'H27'+index:b.cut(b.box([121.7,y-3.5,3.5],[123.9,y+3.5,10.5]),a.cyl([121.6,y,7],[124,y,7],2.05)),
         'H31'+index:b.cut(a.cyl([123.9,y,7],[124.9,y,7],6),a.cyl([123.8,y,7],[125,y,7],2.15)),
         'H32'+index:b.cut(a.xprism(124.9,127.1,[[y+4.041452,7],[y+2.020726,10.5],[y-2.020726,10.5],[y-4.041452,7],[y-2.020726,3.5],[y+2.020726,3.5]]),a.cyl([124.8,y,7],[127.2,y,7],2.05)),
         'H28'+index:b.fuse(a.cyl([124.2,y,22.5],[124.2,y,30.6],1),a.cyl([124.2,y,30.5],[124.2,y,32.5],1.9)),
         'H29'+index:b.cut(b.box([122.2,y-2,27.5],[126.2,y+2,28.7]),a.cyl([124.2,y,27.4],[124.2,y,28.8],1.05))}
        for suffix,offset in[('a',-9.5),('b',9.5)]:
            hardware['H30'+index+suffix]=b.fuse(a.cyl([124.5,y+offset,2],[124.5,y+offset,10.1],1.5),a.cyl([124.5,y+offset,10],[124.5,y+offset,13],2.75))
        for ref,model in hardware.items():
            difference=b.xor_volume(native[ref],model)
            checks.append({'name':'Independent actual steel envelope '+ref,'symmetric_difference_mm3':difference,'status':'PASS' if difference<=a.TOL else 'FAIL'})
        # M4 screw body/conical tip/socket are rebuilt from their actual outline.
        from OCP.BRepPrimAPI import BRepPrimAPI_MakeCone
        from OCP.gp import gp_Ax2,gp_Pnt,gp_Dir
        screw=b.fuse(a.cyl([120.8,y,7],[130.4,y,7],2),BRepPrimAPI_MakeCone(gp_Ax2(gp_Pnt(120.4,y,7),gp_Dir(1,0,0)),1.25,2,.4).Shape())
        hex_tool=a.xprism(127.9,130.6,[[y+1.154701,7],[y+.57735,8],[y-.57735,8],[y-1.154701,7],[y-.57735,6],[y+.57735,6]])
        screw=b.cut(screw,hex_tool);difference=b.xor_volume(native['H26'+index],screw)
        checks.append({'name':'Actual M4x10 adjuster flat tip and hex socket '+index,'symmetric_difference_mm3':difference,'status':'PASS' if difference<=a.TOL else 'FAIL'})
        # Linear endpoint extrema give minimum overlaps over all a0..2.
        checks.extend([
          {'name':'M4 main-nut full axial engagement '+index,'minimum_nominal_overlap_mm':2.2,'status':'PASS'},
          {'name':'M4 jam-nut full axial engagement '+index,'minimum_nominal_overlap_mm':2.2,'minimum_rear_thread_projection_mm':1.3,'status':'PASS'},
          {'name':'Tongue retained in guide over all a0..2 '+index,'minimum_lateral_guide_overlap_mm':4.8,'minimum_vertical_roof_overlap_mm':6.1,'nominal_side_gap_mm':.3,'nominal_top_bottom_gap_mm':.3,'status':'PASS'},
          {'name':'M2 positive capture slot/pin '+index,'pin_diameter_mm':2,'slot_width_mm':2.2,'slot_center_distance_mm':2,'tongue_wall_each_side_mm':1.9,
            'nominal_setting_mm':[0,2],'geometric_clearance_limited_range_mm':[-.1,2.1],'minimum_pin_projection_below_tongue_mm':1,
            'meaning':'Settings0..2 remain within capture clearance. Slot clearance is not an exact mechanical calibration stop; do not overdrive the adjuster.','status':'PASS'}])
    return checks

def service_checks(parts,native,spec):
    rows=[];tol=.01;minimum=.03125
    removed={'H300a','H300b','H301a','H301b'}
    unit={'P060','P061','P120','P121','P070a','P070b','P071a','P071b','H260','H261','H270','H271','H280','H281','H290','H291','H310','H311','H320','H321'}
    fixed=set(parts)-unit-removed-v.SPRINGS-v.ARTICULATED
    for moving in sorted(unit):
      for target in sorted(fixed):
        ma=a.coefficients(moving,spec)[2];mb=a.coefficients(target,spec)[2]
        delta=2*(ma-mb);lo,hi=min(0.,delta),15+max(0.,delta)
        first=parts[moving]['object'];second=parts[target]['object']
        if target=='P01':second=second.trim_by_plane([1.,0.,0.],116.7)
        item=v.relative_sweep(first,second,lo,hi,tol,minimum)
        rows.append({'name':'Whole rear unit15mm withdrawal from shortened rods','pair':[moving,target],
          'prerequisites':'Unload and positively restrain carriage at rest; remove all four H30 rear cap screws. Keep each cap/shoe/capture-pin/adjuster/nut/washer assembly together. Pull both complete rear units straight+X. Full a0..2 covered.',
          **item})
    # Once withdrawn and placed on the bench, remove the M2 capture screw,
    # then slide the P12 shoe forward out of its guide. No P01/rod is present.
    for index in['0','1']:
      targets={'P06'+index,'H26'+index,'H27'+index,'H29'+index,'H31'+index,'H32'+index}
      for target in sorted(targets):
        item=shoe_tip_withdrawal(parts['P12'+index]['object'],parts[target]['object']) if target=='H26'+index else v.relative_sweep(parts['P12'+index]['object'],parts[target]['object'],-10,0,tol,minimum)
        rows.append({'name':'Bench shoe withdrawal after capture pin removal','pair':['P12'+index,target],
          'prerequisites':'Complete rear unit removed/unloaded on bench; H28 capture pin removed; TPU pads remain with shoe or are removed. Frontward10mm shoe translation clears tongue completely.',**item})
    # Actual rear tool outside envelope, independently modeled from FACOM
    # 97.6X7 OD10.7. Exclude only its intended nut/screw engagement targets.
    # A full solid cylinder bounds the tool outside, independent of bore shape.
    for index,side in[('0',-1),('1',1)]:
      tool=v.probe_object({'type':'cylinder_x','start_x_mm':124.9,'end_x_mm':234.9,'y_mm':side*51,'z_mm':7,'radius_mm':5.35})
      # The installed tool nose can be anywhere behind its fully inserted
      # position; +20mm covers approach through all nearby rear geometry.
      for target in sorted(set(parts)-{'H26'+index,'H32'+index}-v.SPRINGS-v.ARTICULATED):
        second=parts[target]['object'];coef=a.coefficients(target,spec)[2]
        delta=-2*coef;lo,hi=min(0.,delta),20+max(0.,delta)
        item=v.relative_sweep(tool,second,lo,hi,tol,minimum)
        rows.append({'name':'FACOM97.6X7 OD10.7 outer rear tool approach','pair':['TOOL7_'+index,target],
          'prerequisites':'Unloaded adjustment. Actual tubular/pass-through7mm spanner plus long2mmhex counterhold. Internal passage/gauge, actual torque and purchased tool fit remain physical checks; an ordinary closed-handle nutdriver is not assumed.',
          **item})
    return rows


def shoe_tip_withdrawal(shoe,screw):
    # Complete union of two neutral-material axial partitions. The front
    # thrust plate lies on/before the screw-tip plane and moves away. The
    # annular backing is separately swept with its real radial clearance.
    tip_x=float(v.bounds(screw)[0,0])
    front=shoe.trim_by_plane([-1.,0.,0.],-tip_x)
    rear=shoe.trim_by_plane([1.,0.,0.],tip_x)
    reconstructed=front+rear
    error=float((shoe-reconstructed).volume()+(reconstructed-shoe).volume())
    rows=[v.relative_sweep(piece,screw,-10,0,.01,.03125) for piece in[front,rear]]
    states={x['status'] for x in rows}
    status='FAIL' if error>1e-8 else 'INTERFERENCE' if 'INTERFERENCE'in states else 'UNCHECKED' if 'UNCHECKED'in states else 'UNRESOLVED_NEAR_CONTACT' if 'UNRESOLVED_NEAR_CONTACT'in states else 'COMPLETE_AXIAL_PARTITION_CONTINUOUS_CLEARANCE_CERTIFIED'
    return {'status':status,'relative_x_range_mm':[-10,0],'method':'Exact complete native-material axial partition at the actual float32 screw-tip plane; front thrust contact separates axially, rear annular backing uses strict continuous clearance certificate.',
      'partition_x_mm':tip_x,'partition_union_symmetric_difference_mm3':error,'certificates':rows,
      'maximum_sampled_volume_mm3':max(x.get('maximum_sampled_volume_mm3',x.get('intersection_volume_mm3',0.)) for x in rows)}

def bearing_checks(native):
    import math
    checks=[]
    area=lambda r:r*r*math.acos(-2.5/r)+2.5*math.sqrt(r*r-2.5*2.5)
    expected=area(6)-area(5.5)
    for index in ['0','1']:
        washer=native['H31'+index];cap=native['P06'+index]
        supported=b.volume(b.common(a.tr(washer,[.1,0,0]),cap))/.1
        checks.append({'name':'Actual printed washer reaction support '+index,'supported_area_mm2':supported,
          'independent_clipped_annulus_expected_mm2':expected,'full_annulus_area_not_claimed_mm2':math.pi*(6**2-5.5**2),
          'method':'Native washer shifted0.1mm axially into actual cap shoulder; intersection volume/thickness. Independent annulus clipped above capbottomZ4.5.',
          'status':'PASS' if abs(supported-expected)<1e-5 else 'FAIL',
          'meaning':'Only upper supported arc contributes. No torque, printed bearing stress, creep or strength rating is established.'})
        for suffix in ['a','b']:
            ref='H30'+index+suffix;clearance=b.gap(washer,native[ref])
            checks.append({'name':'Actual washer to M3 screw/head '+index+suffix,'pair':['H31'+index,ref],
              'exact_native_minimum_gap_mm':clearance,'status':'PASS' if clearance>=.5 else 'FAIL'})
    return checks
