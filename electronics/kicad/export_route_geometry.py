from pathlib import Path
import os,json,sys
R=Path(__file__).resolve().parent;os.environ['KICAD_CONFIG_HOME']=str(R/'.config')
import pcbnew as p
b=p.LoadBoard(str(Path(sys.argv[1]) if len(sys.argv)>1 else R/'routing/routed.kicad_pcb'))
def xy(v):return [p.ToMM(v.x)-100,p.ToMM(v.y)-80]
def poly(s):return [[xy(s.COutline(i).CPoint(j)) for j in range(s.COutline(i).PointCount())] for i in range(s.OutlineCount())]
layers=[p.F_Cu,p.In2_Cu,p.B_Cu] if b.GetCopperLayerCount()==4 else [p.F_Cu,p.B_Cu]
shapes=[];pads={};holes=[]
for f in b.GetFootprints():
 for d in f.Pads():
  pads[f.GetReference()+':'+d.GetNumber()]={'net':d.GetNetname(),'xy':xy(d.GetPosition())}
  for l in layers:
   if d.IsOnLayer(l):
    for o in poly(d.GetEffectivePolygon(l)):shapes.append({'net':d.GetNetname(),'layer':layers.index(l),'poly':o})
  if d.GetDrillSize().x:holes.append({'xy':xy(d.GetPosition()),'r':p.ToMM(d.GetDrillSize().x)/2})
for t in b.GetTracks():
 if isinstance(t,p.PCB_VIA):
  holes.append({'xy':xy(t.GetPosition()),'r':p.ToMM(t.GetDrill())/2})
  for l in range(len(layers)):shapes.append({'net':t.GetNetname(),'layer':l,'circle':xy(t.GetPosition()),'r':p.ToMM(t.GetWidth(p.F_Cu))/2})
 else:shapes.append({'net':t.GetNetname(),'layer':layers.index(t.GetLayer()),'line':[xy(t.GetStart()),xy(t.GetEnd())],'r':p.ToMM(t.GetWidth())/2})
for z in b.Zones():
 if z.GetIsRuleArea():
  for l in range(len(layers)):
   for o in poly(z.Outline()):shapes.append({'net':'KEEP_OUT','layer':l,'poly':o})
(R/'routing/route-geometry.json').write_text(json.dumps({'shapes':shapes,'pads':pads,'holes':holes,'layers':len(layers)}))
print('Exported',len(shapes),'copper and keepout shapes')
