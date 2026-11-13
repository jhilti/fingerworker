#!/usr/bin/env python3
"""R20 integral rear-block locators, preserving axial blind-socket assembly.
Native R19 is the geometry input. No print setup is performed by this script.
"""
from pathlib import Path
import importlib.util,json,hashlib
import numpy as np
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepPrimAPI import BRepPrimAPI_MakeCone
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeVertex
from OCP.gp import gp_Ax2,gp_Pnt,gp_Dir
from OCP.TopAbs import TopAbs_SOLID,TopAbs_SHELL
HERE=Path(__file__).resolve().parent;STUDY=HERE.parent;ROOT=STUDY.parents[1];BASE=ROOT/'review/thumb-rim-2026-11-13'
s=importlib.util.spec_from_file_location('r20_helpers',BASE/'mechanics/thumb_rim.py');h=importlib.util.module_from_spec(s);s.loader.exec_module(h)
b,m,prior=h.b,h.r17,h.prior
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
BASE_SOURCE=BASE/'fingerworker_R19_thumb_rim.fs';BASE_SHA='0e88e273e2e9bc436b2844a44f04b28fb094593c0af87a2127d792bbb56f016d'
SOURCE=STUDY/'fingerworker_R20_rear_locating_pegs.fs'
CX=123.8;PIN_R=2.5;ROOT_R=.4;SLOT_R=2.7;PIN_BOTTOM=2.5;SLOT_FLOOR=2.2

def load():
 inv=json.loads((BASE/'validation/native-step-inventory.json').read_text());assert sha(inv['native_step'])==inv['native_step_sha256']
 ss,_,_=b.read_step(inv['native_step'])
 return {ref:ss[q['candidates'][0]['solid_index']] for ref,q in inv['native_part_correspondence'].items()},inv

def cone(y,z0,z1,r0,r1):
 return BRepPrimAPI_MakeCone(gp_Ax2(gp_Pnt(CX,y,z0),gp_Dir(0,0,1)),r0,r1,z1-z0).Shape()

def slot_tool(y):
 core=b.fuse(m.r7.cyl([CX,y,2.2],[CX,y,4.8],2.7),b.box([CX,y-2.7,2.2],[130.2,y+2.7,4.8]))
 lead=cone(y,4,4.7,2.7,3.4)
 wedge=m.r7.xprism(CX,130.2,[(y-2.7,4),(y+2.7,4),(y+3.4,4.7),(y-3.4,4.7)])
 return b.fuse(b.fuse(core,lead),wedge)

def add_peg(block,y):
 pin=b.fuse(m.r7.cyl([CX,y,2.9],[CX,y,4.7],2.5),cone(y,2.5,2.9,2.1,2.5))
 joined=b.fuse(block,pin)
 vertex=BRepBuilderAPI_MakeVertex(gp_Pnt(CX,y+2.5,4.5)).Vertex()
 es=[e for e in m.edges(joined) if b.gap(e,vertex)<1e-7]
 assert len(es)==1,('root edge',y,len(es))
 return m.rounded(joined,es,.4)

def expected(old):
 out={};frame=old['P01']
 for y,ref in [(-51,'P06L'),(51,'P06R')]:
  out[ref]=add_peg(old[ref],y);frame=b.cut(frame,slot_tool(y))
 out['P01']=frame
 return out

APPEND='''        // R20: short integral locators, with rear-open blind-bottom slots.
        // Axial assembly is essential because both existing rod sockets are blind.
        // Screwless locating only with springs removed; install four M3 screws
        // before spring preload or any load. These clearance-fit pegs are not latches.
        for (var side in [-1,1])
        {
            const s=side < 0 ? "0" : "1";
            const y=side*51;
            makeCylinder(context,id + ("R20PegCore"~s),vector(123.8,y,2.9)*mm,vector(123.8,y,4.7)*mm,2.5*mm);
            fCone(context,id + ("R20PegTip"~s),{"bottomCenter":vector(123.8,y,2.5)*mm,"topCenter":vector(123.8,y,2.9)*mm,"bottomRadius":2.1*mm,"topRadius":2.5*mm});
            join(context,id + ("R20PegJoin"~s),[body(id + ("rearBlock"~s)),body(id + ("R20PegCore"~s)),body(id + ("R20PegTip"~s))]);
            const rootEdge=qContainsPoint(qOwnedByBody(body(id + ("rearBlock"~s)),EntityType.EDGE),vector(123.8,y+2.5,4.5)*mm);
            if (size(evaluateQuery(context,rootEdge)) != 1)
                throw regenError("R20 locator root must select one circular edge");
            opFillet(context,id + ("R20PegRoot"~s),{"entities":rootEdge,"radius":0.4*mm,"tangentPropagation":false});
            makeCylinder(context,id + ("R20SlotFront"~s),vector(123.8,y,2.2)*mm,vector(123.8,y,4.8)*mm,2.7*mm);
            makeBox(context,id + ("R20SlotEntry"~s),vector(123.8,y-2.7,2.2)*mm,vector(130.2,y+2.7,4.8)*mm);
            fCone(context,id + ("R20SlotLeadFront"~s),{"bottomCenter":vector(123.8,y,4)*mm,"topCenter":vector(123.8,y,4.7)*mm,"bottomRadius":2.7*mm,"topRadius":3.4*mm});
            makeXPrism(context,id + ("R20SlotLeadEntry"~s),123.8*mm,130.2*mm,[vector(y-2.7,4)*mm,vector(y+2.7,4)*mm,vector(y+3.4,4.7)*mm,vector(y-3.4,4.7)*mm]);
            join(context,id + ("R20SlotToolJoin"~s),[body(id + ("R20SlotFront"~s)),body(id + ("R20SlotEntry"~s)),body(id + ("R20SlotLeadFront"~s)),body(id + ("R20SlotLeadEntry"~s) + "body")]);
            cut(context,id + ("R20SlotCut"~s),body(id + "base"),body(id + ("R20SlotFront"~s)));
        }
        nameBody(context,body(id + "rearBlock0"),"P06L PRINT - rear rod block, integral locator, two M3 screws");
        nameBody(context,body(id + "rearBlock1"),"P06R PRINT - rear rod block, integral locator, two M3 screws");
'''

def source_text():
 assert sha(BASE_SOURCE)==BASE_SHA
 text=BASE_SOURCE.read_text()
 text=text.replace('Fingerworker Flat132 R19 - softly rounded thumb rims and rigid screw mounts.','Fingerworker Flat132 R20 - integral rear locating pegs and open-entry pockets.')
 text=text.replace(' * P01 also omits the obsolete rear latch catches.',' * R20 adds one integral diameter5 x2mm underside peg to each rear block.\n * Two5.4mm wide, rear-open blind-bottom pockets preserve axial assembly.\n * Nominal radial clearance0.2mm, bottom clearance0.3mm; no interference fit.\n * Screwless positioning is only for unloaded, spring-free fitting.\n * Install all four M3 screws before springs/preload or external loading.\n * P01 still omits the obsolete rear latch catches.')
 text=text.replace('The assembly has94 native bodies;90 prior bodies retain their geometry.','The assembly has94 native bodies;91 R19 bodies retain their geometry.')
 text=text.replace('"Flat132 R19 - rounded thumb rims and rigid mounts"','"Flat132 R20 - rear locating pegs and open-entry pockets"')
 anchor='        const integratedFrame=qBodyType(qUnion([body(id + "base"),body(id + "palmPad")]),BodyType.SOLID);'
 assert text.count(anchor)==1;text=text.replace(anchor,APPEND+anchor)
 return text.replace('P01 PRINT - Flat132 organic palm, rounded thumb rims, rigid rear mounts','P01 PRINT - Flat132 organic palm, thumb rims, rear locator pockets')

def run():
 old,inv=load();out=expected(old);rows=[];mesh={}
 def check(name,ok,**data):rows.append(dict(name=name,status='PASS' if ok else 'FAIL',**data))
 for ref,shape in out.items():
  check('One valid solid and shell '+ref,BRepCheck_Analyzer(shape).IsValid() and b.count(shape,TopAbs_SOLID)==b.count(shape,TopAbs_SHELL)==1)
  check('Positive material '+ref,b.volume(shape)>0,volume_mm3=b.volume(shape))
  mesh[ref]=m.export_mesh(shape,HERE/(ref+'_rear_locators'))
 for ref,y in [('P06L',-51),('P06R',51)]:
  inc=b.cut(out[ref],old[ref]);lost=b.cut(old[ref],out[ref]);gap=b.gap(inc,out['P01'])
  check('No original block stock removed '+ref,b.volume(lost)<1e-7,removed_mm3=b.volume(lost))
  check('Peg mating clearance '+ref,gap>=.19,minimum_mm=gap)
  for other,shape in old.items():
   if other in ['P01',ref]:continue
   if np.any(b.bounds(inc)[1]<b.bounds(shape)[0]) or np.any(b.bounds(shape)[1]<b.bounds(inc)[0]):continue
   v=b.volume(b.common(inc,shape));check('Peg seated clearance '+ref+' / '+other,v<1e-7,overlap_mm3=v)
 SOURCE.write_text(source_text())
 report=dict(status='PASS_LOCAL_R20_GEOMETRY' if all(q['status']=='PASS' for q in rows) else 'FAIL',source_sha256=sha(SOURCE),baseline_source_sha256=BASE_SHA,baseline_native_step_sha256=inv['native_step_sha256'],native_body_count=94,changed_bodies=['P01','P06L','P06R'],unchanged_bodies=91,checks=rows,meshes=mesh,print_setup_status='PRINT_SETUP_DEFERRED_BY_USER')
 (STUDY/'local-preflight.json').write_text(json.dumps(report,indent=2)+'\n')
 spec=dict(status='LOCAL_CANDIDATE_NATIVE_PENDING',source=SOURCE.name,source_sha256=sha(SOURCE),dimensions_mm=dict(centers=[[CX,-51,4.5],[CX,51,4.5]],peg_diameter=5,protrusion=2,tip_chamfer=.4,root_radius=.4,slot_width=5.4,slot_floor_z=2.2,slot_mouth_lead_in=.5,side_clearance=.2,bottom_clearance=.3,plate_below_floor_nominal=4.2),assembly='Slide each rear block axially -X onto its rod while the underside peg enters the rear-open slot. Unloaded, spring-free fitting can be positioned without screws; install the four M3 screws before spring preload or external loading.',retention='No positive rearward retention, latch or interference fit. Physical PLA fit remains unqualified.',print_setup_status='PRINT_SETUP_DEFERRED_BY_USER')
 (STUDY/'design-specification.json').write_text(json.dumps(spec,indent=2)+'\n')
 print(json.dumps(dict(status=report['status'],checks=len(rows),source_sha256=sha(SOURCE),failures=[q for q in rows if q['status']=='FAIL']),indent=2))
 assert report['status'].startswith('PASS')

if __name__=='__main__':run()
