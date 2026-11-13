from pathlib import Path
import os,json,shutil,sys
R=Path(__file__).resolve().parent;os.environ['KICAD_CONFIG_HOME']=str(R/'.config')
import pcbnew as p
src=Path(sys.argv[1]);out=Path(sys.argv[2]);b=p.LoadBoard(str(src));layers=[p.F_Cu,p.In2_Cu,p.B_Cu] if b.GetCopperLayerCount()==4 else [p.F_Cu,p.B_Cu];N={n.GetNetname():n for n in b.GetNetInfo().NetsByNetcode().values()};M=p.FromMM
def V(x,y):return p.VECTOR2I(M(x+100),M(y+80))
for row in json.loads((R/'routing/finish-routes.json').read_text()):
 pts=row['points'];net=N[row['net']]
 for a,c in zip(pts,pts[1:]):
  if a[2]!=c[2]:
   pos=V(*a[:2]);existing=any(isinstance(t,p.PCB_VIA) and t.GetNetname()==row['net'] and (t.GetPosition()-pos).EuclideanNorm()<M(.06) for t in b.GetTracks())
   if existing:continue
   v=p.PCB_VIA(b);v.SetPosition(pos);v.SetWidth(M(.6));v.SetDrill(M(.3));v.SetViaType(p.VIATYPE_THROUGH);v.SetLayerPair(p.F_Cu,p.B_Cu);v.SetNet(net);v.SetLocked(True);b.Add(v)
  else:
   t=p.PCB_TRACK(b);t.SetStart(V(*a[:2]));t.SetEnd(V(*c[:2]));t.SetWidth(M(row['width']));t.SetLayer(layers[a[2]]);t.SetNet(net);t.SetLocked(True);b.Add(t)
b.BuildConnectivity();p.SaveBoard(str(out),b);shutil.copyfile(R/'Fingerworker_RevA.kicad_pro',out.with_suffix('.kicad_pro'))
p.ExportSpecctraDSN(b,str(out.with_suffix('.dsn')))
f=out.with_suffix('.dsn');s=f.read_text().replace('119500 -148500  100000 -148500  100000 -80000  119500 -80000\n            119500 -148500','119400 -148400  100100 -148400  100100 -80100  119400 -80100\n            119400 -148400');f.write_text(s)
print(out,len(list(b.GetTracks())))
