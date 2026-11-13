from pathlib import Path
import sys,json,hashlib
from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.collections import List_TopoDS_Shape as TopTools_ListOfShape
import organic_palm as g
HERE=Path(__file__).resolve().parent;V=HERE.parent/'validation'
def get(name):
 inv=json.loads((V/name).read_text());ss,_,_=g.b.read_step(inv['native_step']);return ss[inv['native_part_correspondence']['P01']['candidates'][0]['solid_index']],inv
base,bi=get('foundation-step-inventory.json');new,ni=get('native-step-inventory.json');rows=[]
for direction,a,b in [('foundation_minus_R18',base,new),('R18_minus_foundation',new,base)]:
 for fuzzy in [0,1e-7,1e-6]:
  args=TopTools_ListOfShape();args.Append(a);tools=TopTools_ListOfShape();tools.Append(b)
  op=BRepAlgoAPI_Cut();op.SetArguments(args);op.SetTools(tools);op.SetFuzzyValue(fuzzy);op.Build()
  out=op.Shape() if op.IsDone() else None;row=dict(direction=direction,fuzzy_mm=fuzzy,done=op.IsDone(),valid=bool(out and BRepCheck_Analyzer(out).IsValid()),volume_mm3=g.b.volume(out) if out else None);rows.append(row)
  (HERE/'native-boolean-probe.json').write_text(json.dumps(dict(status='DIAGNOSTIC_ONLY',foundation_step_sha256=bi['native_step_sha256'],R18_step_sha256=ni['native_step_sha256'],results=rows),indent=2)+'\n')
