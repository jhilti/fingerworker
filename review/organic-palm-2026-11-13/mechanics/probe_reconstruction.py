from pathlib import Path
import json
from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut,BRepAlgoAPI_Fuse,BRepAlgoAPI_Common
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.collections import List_TopoDS_Shape
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
import organic_palm as g
H=Path(__file__).resolve().parent;V=H.parent/'validation'
def get(name):
 inv=json.loads((V/name).read_text());ss,_,_=g.b.read_step(inv['native_step']);return ss[inv['native_part_correspondence']['P01']['candidates'][0]['solid_index']],inv
base,bi=get('foundation-step-inventory.json');new,ni=get('native-step-inventory.json');rows=[]
def op(kind,a,b):
 args=List_TopoDS_Shape();args.Append(a);tools=List_TopoDS_Shape();tools.Append(b);q=kind();q.SetArguments(args);q.SetTools(tools);q.SetFuzzyValue(1e-6);q.Build();assert q.IsDone();s=q.Shape();assert BRepCheck_Analyzer(s).IsValid();return s
def measure(name,shape):
 p=GProp_GProps();err=BRepGProp.VolumePropertiesGK_s(shape,p,1e-10,True,True,False,False,False)
 row=dict(name=name,valid=BRepCheck_Analyzer(shape).IsValid(),volume_default_mm3=g.b.volume(shape),volume_GK_spans_mm3=p.Mass(),relative_error_estimate=err);rows.append(row)
 (H/'native-reconstruction-probe.json').write_text(json.dumps(dict(status='DIAGNOSTIC_ONLY',fuzzy_mm=1e-6,native_step_sha256=ni['native_step_sha256'],foundation_step_sha256=bi['native_step_sha256'],results=rows),indent=2)+'\n')
added=op(BRepAlgoAPI_Cut,new,base);removed=op(BRepAlgoAPI_Cut,base,new)
measure('added',added);measure('removed',removed)
kept=op(BRepAlgoAPI_Cut,base,removed);rebuilt=op(BRepAlgoAPI_Fuse,kept,added)
measure('reconstructed',rebuilt)
measure('native_minus_reconstruction',op(BRepAlgoAPI_Cut,new,rebuilt))
measure('reconstruction_minus_native',op(BRepAlgoAPI_Cut,rebuilt,new))
measure('added_intersects_foundation',op(BRepAlgoAPI_Common,added,base))
measure('removed_intersects_native',op(BRepAlgoAPI_Common,removed,new))
