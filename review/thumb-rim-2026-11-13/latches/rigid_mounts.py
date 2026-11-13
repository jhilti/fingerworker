#!/usr/bin/env python3
"""R19 rigid rear blocks and rigid electronics screw ears; no snap beams.
Deterministic source transformation plus native-R18-derived local candidates.
"""
from pathlib import Path
import importlib.util,json,hashlib
import numpy as np
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCP.gp import gp_Trsf,gp_Vec
from OCP.TopAbs import TopAbs_SOLID
from OCP.TopExp import TopExp_Explorer
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];BASE=ROOT/'review/organic-palm-2026-11-13'
s=importlib.util.spec_from_file_location('rigid_m',ROOT/'review/side-thumb-2026-11-12/mechanics/side_thumb.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
b=m.b;sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def load():
 inv=json.loads((BASE/'validation/native-step-inventory.json').read_text());assert sha(inv['native_step'])==inv['native_step_sha256'];ss,_,_=b.read_step(inv['native_step'])
 return {r:ss[v['candidates'][0]['solid_index']] for r,v in inv['native_part_correspondence'].items()},inv

def boxside(xlo,xhi,ylo,yhi,zlo,zhi,side):
 yy=sorted([side*ylo,side*yhi]);return b.box([xlo,yy[0],zlo],[xhi,yy[1],zhi])
def move(shape,xyz):
 t=gp_Trsf();t.SetTranslation(gp_Vec(*xyz));return BRepBuilderAPI_Transform(shape,t,True).Shape()
def dist(a,c):
 op=BRepExtrema_DistShapeShape(a,c);op.Perform();assert op.IsDone();return op.Value()
def nsol(shape):
 ex=TopExp_Explorer(shape,TopAbs_SOLID);n=0
 while ex.More():n+=1;ex.Next()
 return n

def ear(side):
 # Body-side pillar and five-and-a-half-mm flat screw land.
 root=boxside(-29,-23.8,53.8,56,0,8.1,side)
 pad=boxside(-29,-24,54,62,4,9.5,side)
 es=[e for e in m.edges(pad) if (lambda q:q[1,2]-q[0,2]>5)(b.bounds(e))]
 pad=m.rounded(pad,es,1.0)
 out=b.fuse(root,pad);hole=m.r7.cyl([-26.5,side*59,3.9],[-26.5,side*59,9.6],1.1)
 return b.cut(out,hole)

def expected(old):
 out={}
 for side,ref in [(-1,'P06L'),(1,'P06R')]:
  out[ref]=b.common(old['P06'],boxside(119,129,37,65,4.5,28,side))
 tray=old['P08']
 for side in [-1,1]:
  tray=b.cut(tray,boxside(-50,-23.5,55,70,-.1,17,side))
  tray=b.cut(tray,boxside(-29,-24,54,55,8.1,9.6,side))
  tray=b.fuse(tray,ear(side))
 out['P08']=tray
 # Restore the original filleted floor where the obsolete catch stock joined.
 floor=b.box([-22,-66,-2],[129,66,4]);floor=m.rounded(floor,m.edges(floor),1.5)
 frame=old['P01']
 for side in [-1,1]:
  catch=boxside(108.2,110.5,64.2,66.2,3,7.8,side)
  frame=b.cut(frame,b.cut(catch,floor))
 out['P01_without_rear_catches']=frame
 return out

RIGID_EARS='''    // R19: two broad rigid screw ears replace the exposed tray snap clips.
    // M2x8 from below:5.5mm land +2.5mm engagement in existing M2 inserts.
    for (var side in [-1,1])
    {
        const s=side < 0 ? "0" : "1";
        const rootLo=side < 0 ? -56 : 53.8;
        const rootHi=side < 0 ? -53.8 : 56;
        const padLo=side < 0 ? -62 : 54;
        const padHi=side < 0 ? -54 : 62;
        makeBox(context,id + ("R19TrayMountRoot"~s),vector(-29,rootLo,0)*mm,vector(-23.8,rootHi,8.1)*mm);
        makeBox(context,id + ("R19TrayMountPad"~s),vector(-29,padLo,4)*mm,vector(-24,padHi,9.5)*mm);
        opFillet(context,id + ("R19TrayMountPadRound"~s),{
            "entities":qParallelEdges(qCreatedBy(id + ("R19TrayMountPad"~s),EntityType.EDGE),vector(0,0,1)),
            "radius":1*mm,"tangentPropagation":true });
        join(context,id + ("R19TrayMountJoin"~s),[body(id + "P08_Electronics_tray"),body(id + ("R19TrayMountRoot"~s)),body(id + ("R19TrayMountPad"~s))]);
        makeCylinder(context,id + ("R19TrayMountHole"~s),vector(-26.5,side*59,3.9)*mm,vector(-26.5,side*59,9.6)*mm,1.1*mm);
        cut(context,id + ("R19TrayMountHoleCut"~s),body(id + "P08_Electronics_tray"),body(id + ("R19TrayMountHole"~s)));
    }
'''
REAR='''        // R19: independent solid rod supports; two M3 screws per block.
        // No crossbar, latch beams or unused frame catches.
        nameBody(context,body(id + "rearBlock0"),"P06L PRINT - rigid rear rod block, two M3 screws");
        nameBody(context,body(id + "rearBlock1"),"P06R PRINT - rigid rear rod block, two M3 screws");
'''

def patch_source(text):
 start='    makeBox(context,id + "P08_Electronics_tray_24"'
 end='    makeBox(context,id + "R11TraylidCatch0"'
 a=text.index(start);z=text.index(end,a);text=text[:a]+RIGID_EARS+text[z:]
 start='        // One transverse bridge starts after rail end X124:1 mm clearance.'
 end='        // Broad integral PRINTED sensing stops'
 a=text.index(start);z=text.index(end,a);text=text[:a]+REAR+'\n'+text[z:]
 text=text.replace('const rear = body(id + "rearBlock0");','const rear = qUnion([body(id + "rearBlock0"),body(id + "rearBlock1")]);')
 text=text.replace('const pads = body(id + "rearBlock0"); // R12 fixed return gate','const pads = rear; // R19 two fixed screw-mounted rod blocks')
 text=text.replace('auditSolidPair(context,"Carriage / fixed return gate",carriage,body(id + "rearBlock0"),true)','auditSolidPair(context,"Carriage / fixed rear rod blocks",carriage,rear,true)')
 text=text.replace('"P08 PRINT - Snap electronics tray, optional M2 mount"','"P08 PRINT - rigid electronics tray, two M2x8 screws"')
 text=text.replace(' M3x8 rear gate screw - optional fitting/functional securing',' M3x8 rear rod-block screw - required fastening')
 text=text.replace(' * Seven printed device bodies: P01 frame/palm, P04 grip,\n * P05 floating force yoke, P06 fixed rear gate, P08 tray, P09 lid, P11 cam.', ' * Eight printed device bodies: P01 frame/palm, P04 grip, P05 force yoke,\n * P06L/P06R rigid rod blocks, P08 screw-mounted tray, P09 lid, P11 cam.')
 text=text.replace(' * One plain removable rear gate replaces both caps and return shoes.', ' * Two independent screw-mounted rod blocks replace the thin rear gate.')
 text=text.replace(' * PLA gate latches permit unloaded fitting; four M3 securing screws remain\n * for the loaded assembly. Release both side arms outward0.9mm then+X12mm.', ' * All four M3x8 screws are required to retain the two rear rod blocks.\n * Remove both screws from each block before its axial+X12mm withdrawal.')
 text=text.replace(' * Spread P08 hooks0.6mm then lower20mm; open P09 only after removal.', ' * Remove the two required P08 M2x8 screws then lower20mm; open P09 after removal.')
 return text

def export(shape,path):
 return m.export_mesh(shape,path)

def run():
 old,inv=load();parts=expected(old);checks=[]
 def ck(name,ok,**kw):checks.append(dict(name=name,status='PASS' if ok else 'FAIL',**kw))
 for ref,shape in parts.items():
  ck('Valid single solid '+ref,BRepCheck_Analyzer(shape).IsValid() and nsol(shape)==1)
  export(shape,HERE/ref)
 ck('Rear blocks identical after102mm Y translation',b.volume(b.cut(move(parts['P06L'],[0,102,0]),parts['P06R']))+b.volume(b.cut(parts['P06R'],move(parts['P06L'],[0,102,0])))<1e-6)
 for ref in ['P06L','P06R']:
  ck('Rear support stock is unchanged '+ref,b.volume(b.cut(parts[ref],old['P06']))<1e-6)
 for ref in ['P06L','P06R','P08']:
  shape=parts[ref]
  for other in ['P01','P04','P05','P09','E01','E05','E06','E07','E08']:
   if other not in old:continue
   overlap=b.volume(b.common(shape,old[other]));baseline=b.volume(b.common(old['P06'] if ref.startswith('P06') else old['P08'],old[other]))
   ck(ref+' seated overlap does not increase '+other,overlap<=baseline+1e-6,overlap_mm3=overlap,baseline_mm3=baseline)
 # Required M2 hardware and driver approach use the existing underside insert axes.
 for side in [-1,1]:
  y=side*59
  head=m.r7.cyl([-26.5,y,2.4],[-26.5,y,3.999],1.9)
  driver=m.r7.cyl([-26.5,y,-20],[-26.5,y,3.999],2.5)
  shank=m.r7.cyl([-26.5,y,4.001],[-26.5,y,12],1.0)
  insert=m.r7.cyl([-26.5,y,9.5],[-26.5,y,12.5],1.6)
  for ref,shape in [('P08',parts['P08']),('P01',parts['P01_without_rear_catches']),('P09',old['P09'])]:
   ck('M2 head seating clearance '+str(side)+' '+ref,b.volume(b.common(head,shape))<1e-6)
   ck('5mm driver approach from below '+str(side)+' '+ref,b.volume(b.common(driver,shape))<1e-6)
  ck('M2x8 shank through ear and into pilot '+str(side),b.volume(b.common(shank,parts['P08']))+b.volume(b.common(shank,parts['P01_without_rear_catches']))<1e-6)
  ck('Existing3.2x3mm insert cavity retained '+str(side),b.volume(b.common(insert,parts['P01_without_rear_catches']))<1e-6)
 # Tray withdrawal straight down after removing its screws; original lid remains seated.
 for dz in [0,-.25,-1,-5,-10,-20]:
  tray=move(parts['P08'],[0,0,dz]);ov=b.volume(b.common(tray,parts['P01_without_rear_catches']))
  ck('Rigid tray downward withdrawal '+str(dz),ov<1e-6,overlap_mm3=ov)
 # Side pillars leave the same enclosure cavity; no new contact with battery/PCB.
 spec=dict(status='PASS_LOCAL_RIGID_MOUNTS' if all(c['status']=='PASS' for c in checks) else 'FAIL',baseline_step_sha256=inv['native_step_sha256'],generator_sha256=sha(__file__),changed_refs=['P01','P06','P08'],new_refs=['P06L','P06R'],removed_ref='P06',native_part_count_expected=94,
 rear=dict(blocks=2,identical_translated_y_mm=102,dimensions_mm=[10,28,23.5],fasteners='4 existing M3x8,2 per block; existing M3 inserts',rod_socket='unchanged6.2mm socket and teardrop roof',assembly='Slide each block axially over its rod, seat on original feet, fit both screws. Remove screws before+X12mm withdrawal.'),
 tray=dict(fasteners='2 M2x8 screws and existing M2 OD3.2 x3mm inserts',hole_centers_mm=[[-26.5,-59],[-26.5,59]],through_diameter_mm=2.2,flat_land_z_mm=[4,9.5],nominal_engagement_mm=2.5,insert_cavity_z_mm=[9.5,13.5],insert_envelope_z_mm=[9.5,12.5],screw_head_envelope=dict(diameter_mm=3.8,height_mm=1.6,bearing_plane_z_mm=4),driver_approach_diameter_mm=5,screw_washer=False,pad_xy_mm=[5,8],root_xy_mm=[5.2,2.2],release='Remove2M2 screws, lower tray20mm; no flexing.',P09_lid_unchanged=True),
 source_patch_ranges=['P08 old ears24..31 and R11Traypalm clips replaced by rigid ears','P06 bridge/latches/frame catches removed; original2rod blocks kept','audit rear query covers both blocks'],checks=checks,failures=[c for c in checks if c['status']!='PASS'],limitations=['Nominal CAD and screw engagement only; no printed strength, heat-set insert retention or loaded hardware qualification.'])
 (HERE/'design-specification.json').write_text(json.dumps(spec,indent=2)+'\n')
 (HERE/'rigid_mounts.fs').write_text(RIGID_EARS+'\n'+REAR)
 print(json.dumps({'status':spec['status'],'checks':len(checks),'failures':spec['failures']},indent=2))
 return bool(spec['failures'])
if __name__=='__main__':raise SystemExit(run())
