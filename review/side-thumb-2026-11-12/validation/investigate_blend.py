#!/usr/bin/env python3
"""Read-only candidate reconstruction to isolate failing blend contours."""
from pathlib import Path
import importlib.util,json
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepFilletAPI import BRepFilletAPI_MakeFillet
from OCP.ShapeUpgrade import ShapeUpgrade_UnifySameDomain
HERE=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('candidate',HERE.parent/'mechanics/side_thumb.py');c=importlib.util.module_from_spec(s);s.loader.exec_module(c);b=c.b
old,_=c.load();frame=old['P01'];g=c.stocks()
for q in g['cheeks']:frame=b.fuse(frame,q)
for q in g['tools']:frame=b.cut(frame,q)
assert BRepCheck_Analyzer(frame).IsValid()
edges=c.mouth_edges(frame)
rows=[dict(index=i,bounds=b.bounds(e).tolist(),middle=c.middle(e)) for i,e in enumerate(edges)]
print('EDGES',json.dumps(rows),flush=True)
trials=[]
def trial(name,shape,es,r=.8):
 f=BRepFilletAPI_MakeFillet(shape)
 for e in es:f.Add(r,e)
 f.Build();done=f.IsDone();valid=done and BRepCheck_Analyzer(f.Shape()).IsValid()
 row=dict(name=name,edge_count=len(es),radius=r,done=done,valid=valid,contours=f.NbContours());trials.append(row);print(json.dumps(row),flush=True)
 if valid:c.prior.export(f.Shape(),HERE/('blend-probe-'+name.replace(' ','-')))
 return f.Shape() if valid else None
for i,e in enumerate(edges):
 if b.bounds(e)[1,1]>0:trial('single-'+str(i),frame,[e])
top=[e for e in edges if b.bounds(e)[0,2]>28]
vertical=[e for e in edges if b.bounds(e)[0,2]<=28]
trial('all-top',frame,top)
trial('all-vertical',frame,vertical)
for r in [.6,.4]:trial('all-r'+str(r),frame,edges,r)
u=ShapeUpgrade_UnifySameDomain(frame,True,True,False);u.Build();uf=u.Shape()
if BRepCheck_Analyzer(uf).IsValid():trial('unified',uf,c.mouth_edges(uf))
(HERE/'blend-investigation.json').write_text(json.dumps(dict(generator_sha256=c.sha(HERE.parent/'mechanics/side_thumb.py'),edges=rows,trials=trials),indent=2)+'\n')
