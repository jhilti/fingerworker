#!/usr/bin/env python3
"""Refine placement for local power loops and ADC inputs, then export native DSN.
Routed copper is generated separately; archived initial placement stays intact.
"""
import os,json,math,itertools
from pathlib import Path
ROOT=Path(__file__).resolve().parent
os.environ['KICAD_CONFIG_HOME']=str(ROOT/'.config')
import pcbnew as p
M=p.FromMM;OX=100;OY=80
def V(x,y):return p.VECTOR2I(M(x),M(y))
b=p.LoadBoard(str(ROOT/'archive/placement-2026-09-21/Fingerworker_RevA.kicad_pcb'));project=(ROOT/'Fingerworker_RevA.kicad_pro').read_text()
# Replace J2 with the footprint containing the two internal Kelvin net ties.
old=next(f for f in b.GetFootprints() if f.GetReference()=='J2')
new=p.FootprintLoad(str(ROOT/'Fingerworker.pretty'),'SolderWire_4x2mm_P2.54')
new.SetReference('J2');new.SetValue(old.GetValue());new.SetPath(old.GetPath());new.SetFPID(old.GetFPID());new.SetAttributes(p.FP_SMD)
new.SetField('MPN',old.GetFieldText('MPN'));new.GetField('MPN').SetVisible(False);new.SetField('Datasheet',old.GetFieldText('Datasheet'));new.GetField('Datasheet').SetVisible(False)
new.Reference().SetLayer(p.F_Fab);new.Value().SetVisible(False);b.Remove(old);b.Add(new)
F={f.GetReference():f for f in b.GetFootprints()}
for name in ['EXC_SENSE_P','EXC_SENSE_N']:
 b.Add(p.NETINFO_ITEM(b,name,b.GetNetCount()+1))
source=json.loads((ROOT/'native_design.json').read_text())
for x in source['parts']:
 if x['ref'] not in F:continue
 for pad in F[x['ref']].Pads():
  n=pad.GetNumber()
  if n in x['pins'] and x['pins'][n]['net']:pad.SetNet(b.FindNet(x['pins'][n]['net']))
def place(r,x,y,a):
 f=F[r];f.SetOrientationDegrees(a);f.SetPosition(V(OX+x,OY+y));f.BuildCourtyardCaches();f.Reference().SetPosition(V(OX+x,OY+y))
def bbox(r):
 c=F[r].GetCourtyard(p.F_CrtYd);bb=c.BBox() if c.OutlineCount() else F[r].GetBoundingBox(False,False)
 return tuple(p.ToMM(i)-o for i,o in zip([bb.GetLeft(),bb.GetTop(),bb.GetRight(),bb.GetBottom()],[OX,OY,OX,OY]))
def overlap(a,c,g=.10):return a[0]<c[2]+g and a[2]>c[0]-g and a[1]<c[3]+g and a[3]>c[1]-g
fixed={'U1':(.8325,21.041,0), 'U2':(6.8,38.2,90),'L1':(2.75,35.7,0),'D1':(2.4,39.6,0),'C3':(6.8,34.7,0),'C4':(2.25,42,0),'R3':(9.5,38,270),'R4':(9.5,41.5,270),'C5':(11.25,38,270),
'U3':(15.5,40.4,90),'C7':(15.5,37.05,0),'C6':(15.5,44.15,270),
'U4':(10,49,0),'C14':(15,47.3,90),'C12':(15,50.5,270),'C13':(11.5,44.5,0),
'SW2':(3.5,47.9,90),'J1':(11.5,63,0),'J2':(17.8,51.8,0),'J3':(2,63,0),'R13':(17.8,58.25,0),
'C8':(12.25,54,270),'R7':(14.8,53,180),'R8':(14.8,55,180),'C9':(10.5,54,270),'C10':(8.75,54,270),'C11':(7,54,90),'R9':(4.5,54,180),'R10':(4.5,55.75,180)}
for r,t in fixed.items():place(r,*t)
boxes={r:bbox(r) for r in fixed if r!='U1'}
clashes=[(a,c) for a,c in itertools.combinations(boxes,2) if overlap(boxes[a],boxes[c],.08)]
if clashes:raise RuntimeError(clashes)
placed=dict(fixed)
# Reserve the front copper return path between C4 and the switcher ground.
boxes['_power_return']=(4.0,40.5,8.5,42.5)
prev={z['ref']:(z['x_mm'],z['y_mm'],z['rotation_deg']) for z in json.loads((ROOT/'archive/placement-2026-09-21/placement.json').read_text())}
targets={'C1':(10,34),'R5':(8,36),'R6':(18,41),'Q1':(4,59),'R17':(2,59),'R18':(5,61),'C15':(2,56),'R19':(2,54),'R20':(5,52),'R21':(4,52),'C16':(5,52),'R1':(17,64),'R2':(17,66.5),'C2':(17,61),'R11':(7,44),'R12':(9,44),'R13':(12,42),'R14':(10,46),'R15':(7,42),'R16':(12,41)}
order=sorted(set(F)-set(fixed),key=lambda r:({'C1':0,'Q1':1}.get(r,2),r))
for r in order:
 best=None;tx,ty=targets.get(r,prev[r][:2])
 for a in [0,90,180,270]:
  place(r,0,0,a);rx1,ry1,rx2,ry2=bbox(r)
  for xi in range(3,77):
   x=xi*.25
   if x+rx1<.15 or x+rx2>19.35:continue
   for yi in range(133,272):
    y=yi*.25;bb=(x+rx1,y+ry1,x+rx2,y+ry2)
    if bb[1]<32.8 or bb[3]>68.35:continue
    if any(overlap(bb,k) for k in boxes.values()):continue
    cost=(x-tx)**2+(y-ty)**2 +(.01 if a else 0)
    if best is None or cost<best[0]:best=(cost,x,y,a,bb)
 if best is None:
  print('DEBUG',r,(rx1,ry1,rx2,ry2),boxes,placed);raise RuntimeError('No place: '+r)
 _,x,y,a,bb=best;place(r,x,y,a);placed[r]=(x,y,a);boxes[r]=bb
# Keep draft scope prominent in the native board.
for t in b.GetDrawings():
 if isinstance(t,p.PCB_TEXT) and 'PLACEMENT ONLY' in t.GetText():t.SetText('19.5 x 68.5 x 0.8 mm / 2 layers\nROUTING PROTOTYPE - NOT RELEASED\nSee reports and README before fabrication')
b.BuildConnectivity();out=ROOT/'routing';out.mkdir(exist_ok=True)
p.SaveBoard(str(out/'prepared.kicad_pcb'),b)
(ROOT/'Fingerworker_RevA.kicad_pro').write_text(project)
# Export uses the named project's rules, loaded into the BOARD by LoadBoard.
# Explicitly set track minimums and edge clearance on this working board.
b.GetDesignSettings().m_CopperEdgeClearance=M(.25)
print('DSN:',p.ExportSpecctraDSN(b,str(out/'prepared.dsn')))
outlist=[{'ref':r,'x_mm':x,'y_mm':y,'rotation_deg':a,'courtyard_mm':[round(t,4) for t in bbox(r)]} for r,(x,y,a) in placed.items()]
(ROOT/'routing/placement-routing.json').write_text(json.dumps(outlist,indent=2)+'\n')
print('Placed',len(F),'footprints with no courtyard overlaps.')
print(json.dumps({r:placed[r] for r in order},indent=2))
