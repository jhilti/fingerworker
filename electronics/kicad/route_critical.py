#!/usr/bin/env python3
"""Explicit critical copper: compact switcher loop, ADC decoupling and bridge filters."""
import os,json,re
from pathlib import Path
R=Path(__file__).resolve().parent;os.environ['KICAD_CONFIG_HOME']=str(R/'.config')
import pcbnew as p
M=p.FromMM
def V(x,y):return p.VECTOR2I(M(x+100),M(y+80))
b=p.LoadBoard(str(R/'routing/prepared.kicad_pcb'))
F={f.GetReference():f for f in b.GetFootprints()}
for item in F['D1'].GraphicalItems():
 if item.GetLayer()==p.F_SilkS:item.SetLayer(p.F_Fab)
N={n.GetNetname():n for n in b.GetNetInfo().NetsByNetcode().values()}
def pad(r,n):return next(x for x in F[r].Pads() if x.GetNumber()==str(n))
def P(r,n):
 q=pad(r,n).GetPosition();return (p.ToMM(q.x)-100,p.ToMM(q.y)-80)
def wire(net,points,width=.2,layer=p.F_Cu):
 for a,c in zip(points,points[1:]):
  if a==c:continue
  t=p.PCB_TRACK(b);t.SetStart(V(*a));t.SetEnd(V(*c));t.SetWidth(M(width));t.SetLayer(layer);t.SetNet(N[net]);t.SetLocked(True);b.Add(t)
def via(net,x,y):
 v=p.PCB_VIA(b);v.SetPosition(V(x,y));v.SetWidth(M(.6));v.SetDrill(M(.3));v.SetViaType(p.VIATYPE_THROUGH);v.SetLayerPair(p.F_Cu,p.B_Cu);v.SetNet(N[net]);v.SetLocked(True);b.Add(v)
def gv(r,n,point):wire('GND',[P(r,n),point],.3);via('GND',*point)
# Power stage; SW stays on F.Cu with a compact path. Feedback stays to its right.
wire('BOOST_SW',[P('L1',2),(4.3,36.235),(4.3,39.3375),P('U2',1)],.4)
wire('BOOST_SW',[P('D1',2),(4.3,39.3375)],.4)
wire('V3V3',[P('C3',1),P('U2',5)],.4)
wire('V3V3',[P('L1',1),(1.735,33.3),(4.45,33.3),P('C3',1)],.4)
wire('VBOOST',[P('D1',1),(.75,41.45),P('C4',1)],.4)
wire('GND',[P('U2',2),(6.8,40.6),(5.4,42),P('C4',2)],.5)
gv('U2',2,(6.8,40.2));gv('C4',2,(3.2,42.85));gv('C3',2,(7.75,33.6))
wire('BOOST_FB',[P('U2',3),(8.7,39.3375),P('R3',2)],.2)
wire('BOOST_FB',[P('R3',2),P('R4',1)],.2)
wire('BOOST_FB',[P('R3',2),(9.55,38.775),P('C5',2)],.2)
wire('VBOOST',[P('R3',1),(9.55,37.225),P('C5',1)],.25)
gv('R4',2,(9.0,43.0))
# LDO bypass and local ground returns.
wire('V5A',[P('C7',1),P('U3',5)],.4)
wire('VBOOST',[P('C6',1),(14.55,42.425),P('U3',1)],.4)
gv('U3',2,(15.5,42.35));gv('C7',2,(17.3,37.05));gv('C6',2,(16.2,45.0))
# ADC rail decoupling and tied CLK/AGND/DGND pins.
wire('V5A',[P('U4',12),(14.45,49.325),(14.85,49.725),P('C12',1)],.25)
wire('V3V3',[P('U4',13),(13.8,48.675),(14.4,48.075),P('C14',1)],.25)
wire('GND',[P('U4',3),P('U4',4),P('U4',5)],.25)
gv('U4',4,(6.4,48.675));gv('C12',2,(15.0,52.0));gv('C14',2,(15.6,45.9));gv('C13',2,(12.5,45.3))
# Differential inputs. Preserve the two fine-pitch escapes and nearby RC loop.
wire('AIN_P',[P('U4',11),(14.3,49.975),(14.3,52.675),P('R7',2)],.15)
wire('AIN_P',[P('R7',2),(13.75,53.225),P('C8',1)],.2)
wire('AIN_N',[P('U4',10),(13.95,50.625),(13.95,51.7),(11.375,51.7),(11.375,54.775),P('C8',2)],.15)
wire('AIN_N',[P('C8',2),(13.75,54.775),P('R8',2)],.2)
# One short back-side crossing connects the positive common-mode capacitor.
wire('AIN_P',[P('C8',1),(12.25,52.45)],.2);via('AIN_P',12.25,52.45)
wire('AIN_P',[P('C9',1),(10.5,52.45)],.2);via('AIN_P',10.5,52.45)
wire('AIN_P',[(12.25,52.45),(10.5,52.45)],.2,p.B_Cu)
wire('AIN_N',[P('C10',1),(8.75,51.9)],.2);via('AIN_N',8.75,51.9)
wire('AIN_N',[(8.75,51.9),(9.85,53.0),(10.375,53.0),(11.375,54.0)],.2,p.B_Cu)
via('AIN_N',11.375,54.0)
# Via intersects the locked AIN_N vertical trace at x=11.375.
gv('C9',2,(10.5,55.55));gv('C10',2,(8.75,55.55))
wire('REF_N',[P('U4',8),(7,51.4125),P('C11',2)],.2)
wire('REF_P',[P('U4',9),(11.875,51.275),(11.5,50.9)],.2);via('REF_P',11.5,50.9)
wire('REF_P',[P('C11',1),(6.2,54.8)],.2);via('REF_P',6.2,54.8)
# Sense lines keep separate nets; J2 net ties are their only power-net joins.
wire('EXC_SENSE_P',[P('J2',5),(18.6,46.85),(18.85,46.6),(18.85,46.1)],.15);via('EXC_SENSE_P',18.85,46.1)
wire('EXC_SENSE_N',[P('J2',6),(18.2,56.75),(18.6,57.15)],.15);via('EXC_SENSE_N',18.6,57.15)
# Reserve escapes for the fine-pitch and long signals before global routing.
for net,r,n,point in [
 ('EXC_SENSE_P','R9',1,(5.7,53.35)),
 ('ADC_DRDY_N','U4',14,(11.5,48.025)),
 ('ADC_DRDY_N','U1',4,(3.5,10.541)),
 ('SPI_SCK_MCU','R11',1,(7.1,45.9)),
 ('SPI_SCK_MCU','U1',9,(16.2,15.621)),
 ('ANALOG_EN','U1',2,(3.8,5.461)),
 ('ADC_CS_MCU','U1',3,(3.5,8.001)),
 ('ADC_CS_MCU','R13',1,(16,59))]:
 wire(net,[P(r,n),point],.15);via(net,*point)
# Add local ground fanouts on every remaining grounded component. Router connects these and the plane later.
b.BuildConnectivity();out=R/'routing/critical.kicad_pcb';p.SaveBoard(str(out),b)
p.ExportSpecctraDSN(b,str(R/'routing/critical.dsn'))
# Route against a 0.1-mm inset boundary. Freerouting adds the normal 0.15-mm clearance.
f=R/'routing/critical.dsn';s=f.read_text();s=s.replace('119500 -148500  100000 -148500  100000 -80000  119500 -80000\n            119500 -148500','119400 -148400  100100 -148400  100100 -80100  119400 -80100\n            119400 -148400');f.write_text(s)
print('Wrote',out,len(list(b.GetTracks())),'locked track/via objects')
