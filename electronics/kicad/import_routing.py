#!/usr/bin/env python3
"""Import the local router result, retaining the source project and adding GND planes."""
from pathlib import Path
import os,sys,shutil
R=Path(__file__).resolve().parent;os.environ['KICAD_CONFIG_HOME']=str(R/'.config')
import pcbnew as p
src=Path(sys.argv[2]) if len(sys.argv)>2 else R/'routing/critical.kicad_pcb';ses=Path(sys.argv[1]) if len(sys.argv)>1 else R/'routing/routed-no-fanout.ses'
out=R/'routing/routed.kicad_pcb';b=p.LoadBoard(str(src))
assert p.ImportSpecctraSES(b,str(ses)),'Session import failed'
N={n.GetNetname():n for n in b.GetNetInfo().NetsByNetcode().values()}
M=p.FromMM
for layer in ([p.F_Cu,p.In1_Cu,p.In2_Cu,p.B_Cu] if b.GetCopperLayerCount()==4 else [p.F_Cu,p.B_Cu]):
 z=p.ZONE(b);z.SetLayer(layer);z.SetNet(N['GND']);z.SetZoneName('GND top' if layer==p.F_Cu else 'GND return plane')
 z.SetLocalClearance(M(.2));z.SetMinThickness(M(.2));z.SetThermalReliefGap(M(.25));z.SetThermalReliefSpokeWidth(M(.25));z.SetPadConnection(p.ZONE_CONNECTION_FULL)
 poly=z.Outline();poly.NewOutline()
 for x,y in [(100.25,80.25),(119.25,80.25),(119.25,148.25),(100.25,148.25)]:poly.Append(M(x),M(y))
 b.Add(z)
b.BuildConnectivity();p.SaveBoard(str(out),b)
shutil.copyfile(R/'Fingerworker_RevA.kicad_pro',out.with_suffix('.kicad_pro'))
print(out,len(list(b.GetTracks())),'track/via objects')
