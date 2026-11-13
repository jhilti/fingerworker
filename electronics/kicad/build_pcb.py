#!/usr/bin/env python3
"""Reproducible native PCB placement. No claim of completed routing."""
import os,json,math,random
from pathlib import Path
ROOT=Path(__file__).resolve().parent
os.environ['KICAD_CONFIG_HOME']=str(ROOT/'.config')
import pcbnew as p
M=p.FromMM
def V(x,y):return p.VECTOR2I(M(x),M(y))
project_text=(ROOT/'Fingerworker_RevA.kicad_pro').read_text()
D=json.loads((ROOT/'native_design.json').read_text());parts={x['ref']:x for x in D['parts'] if x['kind']!='external'}
if (ROOT/'Fingerworker_RevA.kicad_pcb').exists() and '--allow-overwrite' not in sys.argv:
 existing=p.LoadBoard(str(ROOT/'Fingerworker_RevA.kicad_pcb'))
 if list(existing.GetTracks()):raise SystemExit('Routed board exists. This legacy placement generator would delete copper; use --allow-overwrite only after making a backup.')
b=p.BOARD();b.GetDesignSettings().SetBoardThickness(M(.8));b.GetDesignSettings().SetCopperLayerCount(2)
# Offset from sheet origin makes coordinates legible in PCB editor.
OX=100;OY=80
nets={n for x in parts.values() for y in x['pins'].values() if (n:=y['net'])}
N={}
for i,n in enumerate(sorted(nets),1):N[n]=p.NETINFO_ITEM(b,n,i);b.Add(N[n])
F={}
for r,x in parts.items():
 name=x['footprint'].split(':')[1];f=p.FootprintLoad(str(ROOT/'Fingerworker.pretty'),name)
 f.SetReference(r);f.SetValue(x['value']);f.SetFPID(p.LIB_ID('Fingerworker',name))
 path=p.KIID_PATH()
 for s in (x['sheetpath']+'/'+x['uuid']).strip('/').split('/'):path.push_back(p.KIID(s))
 f.SetPath(path);f.SetAttributes(p.FP_SMD)
 f.SetField('MPN',x['mpn']);f.GetField('MPN').SetVisible(False)
 f.SetField('Datasheet',x['source']);f.GetField('Datasheet').SetVisible(False)
 for pad in f.Pads():
  n=pad.GetNumber()
  if n in x['pins']:
   pin=x['pins'][n]
   if pin['net']:pad.SetNet(N[pin['net']])
   else:
    name='unconnected-('+r+'-'+pin['name'].replace(' / ','_{slash}_').replace(' ','_')+'-Pad'+n+')'
    if name not in N:N[name]=p.NETINFO_ITEM(b,name,len(N)+1);b.Add(N[name])
    pad.SetNet(N[name])
 # Hide assembly references from soldermask artwork; retain them on F.Fab.
 for t in [f.Reference(),f.Value()]:
  t.SetLayer(p.F_Fab);t.SetTextSize(V(.8,.8));t.SetTextThickness(M(.1))
 f.Value().SetVisible(False);b.Add(f);F[r]=f
# Board edge and documentation graphics.
def line(a,c,layer=p.Edge_Cuts,w=.05):
 s=p.PCB_SHAPE();s.SetShape(p.SHAPE_T_SEGMENT);s.SetStart(V(OX+a[0],OY+a[1]));s.SetEnd(V(OX+c[0],OY+c[1]));s.SetLayer(layer);s.SetWidth(M(w));b.Add(s)
for a,c in [((0,0),(19.5,0)),((19.5,0),(19.5,68.5)),((19.5,68.5),(0,68.5)),((0,68.5),(0,0))]:line(a,c)
def place(r,x,y,a=0):
 f=F[r];f.SetOrientationDegrees(a);f.SetPosition(V(OX+x,OY+y));f.Reference().SetPosition(V(OX+x,OY+y));f.Reference().SetTextAngle(p.EDA_ANGLE(0,p.DEGREES_T));f.BuildCourtyardCaches()
def box(r):
 fp=F[r];c=fp.GetCourtyard(p.F_CrtYd)
 if c.OutlineCount():bb=c.BBox()
 else:bb=fp.GetBoundingBox(False,False)
 return tuple(p.ToMM(k) for k in (bb.GetLeft(),bb.GetTop(),bb.GetRight(),bb.GetBottom()))
def touch(a,c,gap=.12):return a[0]<c[2]+gap and a[2]>c[0]-gap and a[1]<c[3]+gap and a[3]>c[1]-gap
# XIAO stock lands span 18.915 mm. This gives 0.2925 mm copper-edge clearance.
fixed={'U1':(.8325,21.041,0),'L1':(2.55,35.15,0),'D1':(8,34,0),'U2':(6.8,38.2,0),'U3':(15.5,40.4,0),'U4':(10,50,0),'SW2':(3.5,46.5,90),'J1':(11.5,63,0),'J2':(17.8,51.8,0),'J3':(2,63,0)}
for r,(x,y,a) in fixed.items():place(r,x,y,a)
placed=dict(fixed)
# Prioritized local decoupling, signal filters, feedback, then slow control nets.
order=['C12','C14','C13','C3','C4','C6','C7','R3','R4','C5','R7','R8','C8','C9','C10','R9','R10','C11','R11','R12','R13','R14','R15','R16','Q1','C1','R5','R6','R17','R18','C15','R19','R20','R21','C16','R1','R2','C2']
# Desired region per function; all parts are on the top, leaving the underside flat.
target={r:(10,40) for r in order}
for r in ['C12','C13','C14']:target[r]=(14.5,47.5)
for r in ['R7','R8','C8','C9','C10']:target[r]=(15.5,54)
for r in ['R9','R10','C11']:target[r]=(10,55)
for r in ['R11','R12','R13','R14','R15','R16']:target[r]=(8,44)
for r in ['C3','R3','R4','C5','R5']:target[r]=(7,39)
for r in ['C4','C6','C7','R6']:target[r]=(14,37)
for r in ['Q1','R17','R18','C15','R19']:target[r]=(4,58)
for r in ['R20','R21','C16']:target[r]=(4,52)
for r in ['C1','R1','R2','C2']:target[r]=(7,64)
# Reuse reviewed positions unless an explicit repack is requested.
import sys
if (ROOT/'placement.json').exists() and '--repack' not in sys.argv:
 for z in json.loads((ROOT/'placement.json').read_text()):
  r=z['ref']
  if r in fixed: continue
  x,y,a=z['x_mm'],z['y_mm'],z['rotation_deg'];place(r,x,y,a);placed[r]=(x,y,a)
 order=[]
# Planar courtyard packing with proximity cost. Routing remains a separate, reviewed operation.
for r in order:
 fp=F[r];best=None
 for a in [0,90,180,270]:
  place(r,0,0,a);bb=box(r);rel=(bb[0]-OX,bb[1]-OY,bb[2]-OX,bb[3]-OY)
  for ix in range(3,77):
   x=ix*.25
   for iy in range(133,272):
    y=iy*.25;ab=(x+rel[0]+OX,y+rel[1]+OY,x+rel[2]+OX,y+rel[3]+OY)
    if ab[0]<OX+.15 or ab[2]>OX+19.35 or ab[1]<OY+32.8 or ab[3]>OY+68.35:continue
    if any(touch(ab,box(z)) for z in placed if z!='U1'):continue
    tx,ty=target[r];cost=(x-tx)**2+(y-ty)**2
    # Prioritize local topology for orientation among equal packing positions.
    connectivity=0
    for pad in fp.Pads():
     net=pad.GetNetname()
     if not net or net in ['GND','V3V3','V5A','VBAT']:continue
     pp=pad.GetPosition();px=p.ToMM(pp.x)-OX+x;py=p.ToMM(pp.y)-OY+y
     ds=[]
     for z in placed:
      for other in F[z].Pads():
       if other.GetNetname()==net:
        op=other.GetPosition();ds.append(math.hypot(px-(p.ToMM(op.x)-OX),py-(p.ToMM(op.y)-OY)))
     if ds:connectivity+=min(ds)
    cost+=.6*connectivity
    if best is None or cost<best[0]:best=(cost,x,y,a)
 if best is None:raise RuntimeError('Cannot place '+r)
 _,x,y,a=best;place(r,x,y,a);placed[r]=(x,y,a)
 print(r,placed[r],flush=True)
# Enforced central RF corridor: actual antenna is on the lower edge of the XIAO.
# Copper-free margin is a conservative study assumption, not a Seeed RF certification.
def keepout(name,rect):
 z=p.ZONE(b);z.SetIsRuleArea(True);z.SetZoneName(name);ls=p.LSET();ls.AddLayer(p.F_Cu);ls.AddLayer(p.B_Cu);z.SetLayerSet(ls)
 z.SetDoNotAllowTracks(True);z.SetDoNotAllowVias(True);z.SetDoNotAllowPads(True);z.SetDoNotAllowZoneFills(True);z.SetDoNotAllowFootprints(False)
 x1,y1,x2,y2=rect;o=z.Outline();o.NewOutline()
 for x,y in [(x1,y1),(x2,y1),(x2,y2),(x1,y2)]:o.Append(M(OX+x),M(OY+y))
 b.Add(z)
keepout('RF antenna underside - no copper', (3.25,18.7,11.5,21.6))
keepout('RF free extension - confirm on hardware',(3.25,21.6,16.25,32.5))
def txt(t,x,y,size=.8,layer=p.F_SilkS,angle=0):
 a=p.PCB_TEXT(b);a.SetText(t);a.SetPosition(V(OX+x,OY+y));a.SetTextSize(V(size,size));a.SetTextThickness(M(.12));a.SetTextAngle(p.EDA_ANGLE(angle,p.DEGREES_T));a.SetLayer(layer);b.Add(a)
txt('FINGERWORKER',9.75,25,1)
txt('REV A / DRAFT',9.75,27,.8)
txt('RF KEEP CLEAR',9.75,29,.8)
# Board documentation, not a production silkscreen assembly legend.
txt('19.5 x 68.5 x 0.8 mm / 2 layers\nPLACEMENT ONLY - NOT ROUTED\nSee reports and README before fabrication',31,13,1.2,p.Dwgs_User)
for r,(x,y,a) in placed.items():F[r].Reference().SetVisible(True)
b.BuildConnectivity();p.SaveBoard(str(ROOT/'Fingerworker_RevA.kicad_pcb'),b)
# pcbnew.SaveBoard can persist defaults from a fresh BOARD; restore intentional project rules.
(ROOT/'Fingerworker_RevA.kicad_pro').write_text(project_text)
# Placement report / reproducible interface to later CAD import.
out=[]
for r,(x,y,a) in placed.items():
 bb=box(r);out.append({'ref':r,'x_mm':x,'y_mm':y,'rotation_deg':a,'courtyard_mm':[round(bb[0]-OX,4),round(bb[1]-OY,4),round(bb[2]-OX,4),round(bb[3]-OY,4)]})
(ROOT/'placement.json').write_text(json.dumps(out,indent=2)+'\n')
print('Saved',len(F),'footprints',len(N),'nets. No tracks yet.')
