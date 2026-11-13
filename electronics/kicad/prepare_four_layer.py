from pathlib import Path
import os,shutil
R=Path(__file__).resolve().parent;os.environ['KICAD_CONFIG_HOME']=str(R/'.config')
import pcbnew as p
b=p.LoadBoard(str(R/'routing/critical.kicad_pcb'));b.GetDesignSettings().SetCopperLayerCount(4);b.GetDesignSettings().SetBoardThickness(p.FromMM(.8))
b.SetLayerType(p.In1_Cu,p.LT_POWER)
for z in b.Zones():
 if z.GetIsRuleArea():
  ls=p.LSET();[ls.AddLayer(l) for l in [p.F_Cu,p.In1_Cu,p.In2_Cu,p.B_Cu]];z.SetLayerSet(ls)
out=R/'routing/critical-4L.kicad_pcb';p.SaveBoard(str(out),b);shutil.copyfile(R/'Fingerworker_RevA.kicad_pro',out.with_suffix('.kicad_pro'))
p.ExportSpecctraDSN(b,str(out.with_suffix('.dsn')))
f=out.with_suffix('.dsn');s=f.read_text();s=s.replace('119500 -148500  100000 -148500  100000 -80000  119500 -80000\n            119500 -148500','119400 -148400  100100 -148400  100100 -80100  119400 -80100\n            119400 -148400');s=s.replace('    (keepout ""','    (plane GND (polygon In1.Cu 0 100250 -80250 119250 -80250 119250 -148250 100250 -148250 100250 -80250))\n    (keepout ""',1)
f.write_text(s);print('four layer board exported')
