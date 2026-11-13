#!/usr/bin/env python3
"""R11 enclosure proposal: exact R10 + literal external snap stocks.

Only files in this directory are written. No browser or main source edits.
The additive parts deliberately leave the user's R10 P01 unchanged.
"""
from pathlib import Path
import hashlib, json, sys
import numpy as np
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeFace, BRepBuilderAPI_Transform
from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism, BRepPrimAPI_MakeCylinder
from OCP.gp import gp_Pnt, gp_Vec, gp_Ax1, gp_Ax2, gp_Dir, gp_Trsf
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.TopAbs import TopAbs_SOLID
from OCP.STEPControl import STEPControl_Writer,STEPControl_AsIs
from OCP.StlAPI import StlAPI_Writer
from OCP.BRepMesh import BRepMesh_IncrementalMesh

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
BASE=ROOT/'review/flat132-integrated-palm-2026-11-03'
sys.path.insert(0,str(ROOT/'review/flat132-solid-palm-2026-10-23/validation'))
import audit_solid_palm as b

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
def union(ss):
    result=ss[0]
    for s in ss[1:]:result=b.fuse(result,s)
    return result
def prism(axis,a,c,points):
    w=BRepBuilderAPI_MakePolygon()
    for u,v in points:w.Add(gp_Pnt(a,u,v) if axis=='X' else gp_Pnt(u,a,v))
    w.Close()
    return BRepPrimAPI_MakePrism(BRepBuilderAPI_MakeFace(w.Wire()).Face(),gp_Vec(c-a,0,0) if axis=='X' else gp_Vec(0,c-a,0)).Shape()
def cylinder(x,y,z0,z1,r):return BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(x,y,z0),gp_Dir(0,0,1)),r,z1-z0).Shape()
def tr(s,xyz):
    t=gp_Trsf();t.SetTranslation(gp_Vec(*xyz));return BRepBuilderAPI_Transform(s,t,True).Shape()
def stock(shape,kind,**spec):return dict(shape=shape,kind=kind,**spec)
def box(lo,hi):return stock(b.box(lo,hi),'box',lo=lo,hi=hi)
def yz(x0,x1,points):return stock(prism('X',x0,x1,points),'Xprism',a=x0,c=x1,points=points)
def xz(y0,y1,points):return stock(prism('Y',y0,y1,points),'Yprism',a=y0,c=y1,points=points)

def stocks():
    tray=[];lid=[]
    # Two integral long arms, with their beams entirely on the print bed.
    # Outward Y flex, existing R10 palm-end edge is the counterfeature.
    for sign in [-1,1]:
        def interval(a,c):return [a,c] if sign>0 else [-c,-a]
        for tag,lo,hi in [
            ('palmRoot',[-46.1,54.6,0],[-45.1,65.5,2.4]),
            ('palmBeam',[-45.5,64.3,0],[-25.6,65.5,2.4]),
            ('palmPost',[-29,64.3,0],[-25.6,65.5,14.9]),
            ('palmLip',[-29,63.6,14.7],[-25.6,65.5,15.5])]:
            lo[1],hi[1]=interval(lo[1],hi[1]);s=box(lo,hi);s.update(tag=tag,side=sign);tray.append(s)
        points=[[63.6*sign,15.5],[64.3*sign,16.2],[65.5*sign,16.2],[65.5*sign,15.45]]
        if sign<0:points.reverse()
        s=yz(-29,-25.6,points);s.update(tag='palmRamp',side=sign);tray.append(s)
        # Explicit concave R0.6 root stock; no topology-dependent fillet.
        yy=interval(63.7,64.35);lo=[-45.15,yy[0],0];hi=[-44.5,yy[1],2.4]
        shape=b.cut(b.box(lo,hi),cylinder(-44.5,63.7*sign,-.1,2.5,.6))
        tray.append(stock(shape,'roundedRoot',tag='palmRootBlend',side=sign,lo=lo,hi=hi,cylinder=[-44.5,63.7*sign,-.1,2.5,.6]))
    # Deckel long side arms are outside the electronics wall, no new hole.
    for k,root0,root1,beam0,free0,free1 in [('0',-52,-48.8,-49.2,-28,-25),('1',16,19.2,18.8,40,43)]:
        s=box([-48.6,root0,8.1],[-45.9,root1,8.9]);s.update(tag='lidRoot'+k);lid.append(s)
        s=box([-48.6,beam0,4.8],[-47.4,free1,8.9]);s.update(tag='lidBeam'+k);lid.append(s)
        points=[[-47.5,4.2],[-47.4,4.2],[-46.3,4.8],[-46.3,5.7],[-47.5,5.7]]
        s=xz(free0,free1,points);s.update(tag='lidHook'+k);lid.append(s)
        s=box([-47.1,free0-.2,5.8],[-46,free1+.2,6.8]);s.update(tag='lidCatch'+k);tray.append(s)
    # The old tiny P10 contact footprint becomes a thick integral lid column.
    s=box([-28.1,22.4,3.4],[-24.9,32.6,8.2]);s.update(tag='integralWireClamp');lid.append(s)
    return tray,lid

def load():
    inv=json.loads((BASE/'validation/native-step-inventory.json').read_text())
    assert sha(inv['native_step'])==inv['native_step_sha256']
    ss,_,_=b.read_step(inv['native_step'])
    return {r:ss[x['candidates'][0]['solid_index']] for r,x in inv['native_part_correspondence'].items()},inv

def expected(old):
    ts,ls=stocks()
    return {'P08':union([old['P08']]+[s['shape'] for s in ts]),'P09':union([old['P09']]+[s['shape'] for s in ls])}

def source_patch(source):
    # Stable existing anchors; no P01 or reference electronics change.
    ts,ls=stocks()
    def command(s,prefix):
        tag='R11'+prefix+s['tag']+(('L' if s['side']<0 else 'R') if 'side' in s else '')
        def vec(v):return 'vector('+','.join(f'{x:g}' for x in v)+')*mm'
        if s['kind']=='box':line=f'    makeBox(context,id + "{tag}",{vec(s["lo"])},{vec(s["hi"])});'
        elif s['kind'] in ('Xprism','Yprism'):
            fn='make'+s['kind'][0]+'Prism';points=','.join(vec(p) for p in s['points'])
            line=f'    {fn}(context,id + "{tag}",{s["a"]:g}*mm,{s["c"]:g}*mm,[{points}]);'
        else:
            x,y,z0,z1,r=s['cylinder']
            line=f'    makeBox(context,id + "{tag}",{vec(s["lo"])},{vec(s["hi"])});\n'
            line+=f'    makeCylinder(context,id + "{tag}Tool",{vec([x,y,z0])},{vec([x,y,z1])},{r:g}*mm);\n'
            line+=f'    cut(context,id + "{tag}Round",body(id + "{tag}"),body(id + "{tag}Tool"));'
        actual_id=f'id + "{tag}" + "body"' if s['kind'] in ('Xprism','Yprism') else f'id + "{tag}"'
        return line+f'\n    join(context,id + "{tag}Join",[body(id + "P0{8 if prefix=="Tray" else 9}_Electronics_{"tray" if prefix=="Tray" else "lid"}"),body({actual_id})]);'
    traycode='\n    // R11 additive outside clips; existing R10 P01 remains reusable.\n'+'\n'.join(command(s,'Tray') for s in ts)+'\n'
    anchor='    nameBody(context,body(id + "P08_Electronics_tray"),"P08 PRINT - Electronics tray");'
    assert source.count(anchor)==1
    source=source.replace(anchor,traycode+anchor.replace('P08 PRINT - Electronics tray','P08 PRINT - Snap electronics tray, optional M2 mount'))
    start=source.index('    nameBody(context,body(id + "P09_Electronics_lid"),"P09 PRINT - Electronics lid");')
    end=source.index('\n}\n// END GENERATED ENCLOSURE REV A',start)
    code='    // R11 lid-integral P10 clamp: same contact footprint, no loose tiny bar.\n'+'\n'.join(command(s,'Lid') for s in ls)+'''\n    nameBody(context,body(id + "P09_Electronics_lid"),"P09 PRINT - Snap lid with integral wire clamp");
    finishBody(context,body(id + "P09_Electronics_lid"),color(0.15,0.65,0.78));
    return qUnion([body(id + "P08_Electronics_tray"),body(id + "P09_Electronics_lid")]);'''
    return source[:start]+code+source[end:]

def main():
    old,inv=load();new=expected(old);ts,ls=stocks();rows=[]
    def add(name,ok,**e):rows.append(dict(name=name,status='PASS' if ok else 'FAIL',**e))
    for r,s in new.items():
        add(r+' valid single solid',bool(BRepCheck_Analyzer(s).IsValid()) and b.count(s,TopAbs_SOLID)==1,volume_mm3=b.volume(s),solid_count=b.count(s,TopAbs_SOLID),bounds_mm=b.bounds(s).tolist())
        writer=STEPControl_Writer();writer.Transfer(s,STEPControl_AsIs);writer.Write(str(HERE/(r+'_proposal.step')))
        def stl(shape,path):
            mesh=BRepMesh_IncrementalMesh(shape,.025,False,.1,True);mesh.Perform()
            writer=StlAPI_Writer();writer.ASCIIMode=False;assert writer.Write(shape,str(path))
        stl(s,HERE/(r+'_assembly.stl'))
        m=s
        if r=='P09':
            rot=gp_Trsf();rot.SetRotation(gp_Ax1(gp_Pnt(0,0,0),gp_Dir(1,0,0)),np.pi);m=BRepBuilderAPI_Transform(m,rot,True).Shape()
        m=tr(m,-b.bounds(m)[0]);stl(m,HERE/(r+'_print.stl'))
    # Additive geometry never enters PCB, battery, switch button or USB space.
    for r,s in new.items():
        for ref,other in old.items():
            if ref in ['P08','P09','P10']:continue
            vol=0 if np.any(b.bounds(s)[1]<b.bounds(other)[0]) or np.any(b.bounds(other)[1]<b.bounds(s)[0]) else b.volume(b.common(s,other))
            # Original parts include seated screw bodies and expected support contacts.
            prior=0 if np.any(b.bounds(old[r])[1]<b.bounds(other)[0]) or np.any(b.bounds(other)[1]<b.bounds(old[r])[0]) else b.volume(b.common(old[r],other))
            add(r+' no new seated interference '+ref,vol-prior<1e-6,new_overlap_mm3=vol-prior)
    add('New P08 and P09 have no solid overlap',b.volume(b.common(new['P08'],new['P09']))<1e-6,intersection_mm3=b.volume(b.common(new['P08'],new['P09'])))
    add('Main lid skin retains0.6mm P01 gap',abs(b.gap(old['P01'],old['P09'])-.6)<1e-5,gap_mm=b.gap(old['P01'],old['P09']))
    # Flexed geometric release witness: isolate each added hook/post, shift out.
    # Elastic strain is an elementary tip-deflection estimate, no material rating.
    strains=[dict(connection='P08 / existing P01 palm end',effective_length_mm=15.5,thickness_mm=1.2,max_tip_deflection_mm=.6,nominal_outer_fibre_strain=1.5*1.2*.6/(15.5**2)),dict(connection='P09 / new P08 outside catch',effective_length_mm=20.0,thickness_mm=1.2,max_tip_deflection_mm=.9,nominal_outer_fibre_strain=1.5*1.2*.9/(20.0**2))]
    for a in strains:add(a['connection']+' nominal strain <=0.5%',a['nominal_outer_fibre_strain']<=.005,**a)
    palm=old['P01']
    flexed_posts=[]
    for sign in [-1,1]:
        group=[s['shape'] for s in ts if s.get('side')==sign and s['tag'] in ['palmPost','palmLip','palmRamp']]
        hook=tr(union(group),[0,sign*.6,0])
        flexed_posts.append(hook)
        maxov=0
        for dz in np.linspace(-20,0,81):maxov=max(maxov,b.volume(b.common(tr(hook,[0,0,float(dz)]),palm)))
        add('P08 flexed insertion/release ±Y0.6 thenZ side'+str(sign),maxov<1e-6,maximum_sampled_overlap_mm3=maxov,sampled_poses=81,closed_hook_gap_mm=b.gap(union(group),palm))
        retained_overlap=b.volume(b.common(tr(union(group),[0,0,-.3]),palm))
        add('P08 seated hook positively retains before0.3mm withdrawal side'+str(sign),retained_overlap>0,restraining_intersection_mm3=retained_overlap,nominal_axial_lash_mm=.2,nominal_lateral_hook_overlap_mm=.4)
    # FULL closed enclosure, including both root plates and beams. The beam
    # deflection itself stays within the broad Y interval64.3..66.1, Z0..2.4;
    # that entire box is outside the unchanged P01, so its shape is immaterial
    # to collision clearance. Posts are at their conservative fully open tips.
    flexed_case=union([old['P08'],new['P09']]+[s['shape'] for s in ts if s['tag'] not in ['palmPost','palmLip','palmRamp']]+flexed_posts)
    maxov=0
    for dz in np.linspace(-20,0,81):maxov=max(maxov,b.volume(b.common(tr(flexed_case,[0,0,float(dz)]),palm)))
    add('Complete CLOSED P08/P09 module with open palm hooks has20mm vertical assembly path',maxov<1e-6,maximum_sampled_overlap_mm3=maxov,sampled_poses=81,includes='R10 P08, complete R11 P09, all added root/beam/catch geometry, both spread hook/post assemblies')
    for sign in [-1,1]:
        lo,hi=([64.3,66.1] if sign>0 else [-66.1,-64.3])
        conservative=b.box([-45.5,lo,-20],[-25.6,hi,2.4])
        ov=b.volume(b.common(conservative,palm))
        add('Continuous whole bending-beam assembly envelope side'+str(sign),ov<1e-6,intersection_upper_bound_mm3=ov)
    # Lid flexed ends slide past their catch bosses. Other lid geometry has
    # unchanged direct +Z service route, checked against every electronics part.
    stationary={r:s for r,s in old.items() if r.startswith(('E','PCB_')) and r not in ['E06','E08']}
    stationary['P08']=new['P08']
    movingcore=union([old['P09']]+[s['shape'] for s in ls if s['tag']=='integralWireClamp'])
    for ref,target in stationary.items():
        maxov=0
        for dz in np.linspace(.001,15,31):maxov=max(maxov,b.volume(b.common(tr(movingcore,[0,0,float(dz)]),target)))
        add('P09 rigid core/clamp vertical service '+ref,maxov<1e-6,max_sampled_interference_mm3=maxov,sampled_poses=31)
    for k in ['0','1']:
        arm=union([s['shape'] for s in ls if s['tag'] in ['lidBeam'+k,'lidHook'+k]])
        arm=tr(arm,[-.9,0,0]);maxov=0
        for dz in np.linspace(0,15,61):maxov=max(maxov,b.volume(b.common(tr(arm,[0,0,float(dz)]),new['P08'])))
        add('P09 side arm outsideX0.9 vertical release '+k,maxov<1e-6,maximum_sampled_overlap_mm3=maxov,sampled_poses=61)
        seated=union([s['shape'] for s in ls if s['tag']=='lidHook'+k]);retained=b.volume(b.common(tr(seated,[0,0,.2]),new['P08']))
        add('P09 hook positively retains before0.2mm withdrawal '+k,retained>0,restraining_intersection_mm3=retained,nominal_axial_lash_mm=.1,nominal_lateral_hook_overlap_mm=.8)
    spec=dict(revision='R11',date='2026-11-03',baseline_source_sha256=sha(BASE/'fingerworker_flat132_integrated_palm.fs'),unchanged_P01=True,removed_refs=['P10'],changed_refs=['P08','P09'],tray_stocks=[{k:v for k,v in s.items() if k!='shape'} for s in ts],lid_stocks=[{k:v for k,v in s.items() if k!='shape'} for s in ls],nominal_strain_estimates=strains,scope='Local OCP literal design preflight, not a native Onshape export or material qualification.')
    write(HERE/'enclosure-spec.json',spec)
    out=dict(status='PASS' if all(x['status']=='PASS' for x in rows) else 'FAIL',source_baseline=inv['native_step'],baseline_native_sha256=inv['native_step_sha256'],checks=rows,failed=[x for x in rows if x['status']=='FAIL'],strain_model='epsilon=1.5*t*delta/L^2 for elementary cantilever; no stress concentration, print defect, anisotropy, fatigue or strength claim.')
    write(HERE/'local-enclosure-preflight.json',out)
    src=(BASE/'fingerworker_flat132_integrated_palm.fs').read_text();patched=source_patch(src)
    (HERE/'fingerworker_R11_enclosure_patch_preview.fs').write_text(patched)
    print(json.dumps(dict(status=out['status'],checks=len(rows),failed=out['failed'],strains=strains),indent=2))

if __name__=='__main__':main()
