"""Route remaining signals against conservative copper envelopes; native KiCad DRC remains authoritative."""
from pathlib import Path
import json,math,heapq,time
import numpy as np
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parent;g=json.loads((R/'routing/route-geometry.json').read_text());shapes=g['shapes'];pads=g['pads']
S=.05;W=391;H=1371;L=g['layers']

def mask(net,r):
 imgs=[Image.new('L',(W,H)) for _ in range(L)];draw=[ImageDraw.Draw(x) for x in imgs]
 def point(a):return tuple(round(x/S) for x in a)
 def circle(d,c,r):
  x,y=[t/S for t in c];rr=r/S;d.ellipse((x-rr,y-rr,x+rr,y+rr),fill=255)
 for v in shapes:
  if v['net']==net:continue
  d=draw[v['layer']];margin=r+.155
  if 'poly' in v:
   q=[point(x) for x in v['poly']];d.polygon(q,fill=255);d.line(q+[q[0]],fill=255,width=math.ceil(2*margin/S),joint='curve')
   for c in v['poly']:circle(d,c,margin)
  elif 'circle' in v:circle(d,v['circle'],v['r']+margin)
  else:
   rr=v['r']+margin;d.line([point(x) for x in v['line']],fill=255,width=math.ceil(2*rr/S))
   for c in v['line']:circle(d,c,rr)
 for d in draw:
  rr=math.ceil((r+.275)/S);d.rectangle((0,0,rr-1,H-1),fill=255);d.rectangle((W-rr,0,W-1,H-1),fill=255);d.rectangle((0,0,W-1,rr-1),fill=255);d.rectangle((0,H-rr,W-1,H-1),fill=255)
 return np.array([np.asarray(x)>0 for x in imgs])

def solve(net,a,z,width=.15):
 blocked=mask(net,width/2);vb=mask(net,.30);vblock=np.logical_or.reduce(vb)
 # Vias may not overlap other drills, including drills on their own net.
 for h in g['holes']:
  x,y=[round(t/S) for t in h['xy']];rr=math.ceil((h['r']+.15+.25)/S)
  for yy in range(max(0,y-rr),min(H,y+rr+1)):
   dx=int(math.sqrt(max(0,rr*rr-(yy-y)**2)));vblock[yy,max(0,x-dx):min(W,x+dx+1)]=True
 existing_vias={(round(t['circle'][1]/S),round(t['circle'][0]/S)) for t in shapes if t['net']==net and 'circle' in t}
 for y,x in existing_vias:vblock[y,x]=False
 start=(a[2],round(a[1]/S),round(a[0]/S));end=(z[2],round(z[1]/S),round(z[0]/S))
 print(net,start,end,'blocked',blocked[start],blocked[end],flush=True)
 assert not blocked[start] and not blocked[end]
 def heuristic(n):
  dx=abs(n[2]-end[2]);dy=abs(n[1]-end[1]);return max(dx,dy)+(2**.5-1)*min(dx,dy)+(90 if n[0]!=end[0] else 0)
 dist=np.full((L,H,W),np.inf,dtype=np.float32);dist[start]=0;prev={};q=[(heuristic(start),0,start)];count=0
 dirs=[(dy,dx,2**.5 if dy and dx else 1) for dy in [-1,0,1] for dx in [-1,0,1] if dx or dy]
 while q:
  _,d,n=heapq.heappop(q)
  if d>dist[n]+.001:continue
  if n==end:break
  l,y,x=n;count+=1
  for dy,dx,cost in dirs:
   yy=y+dy;xx=x+dx
   if not(0<=yy<H and 0<=xx<W) or blocked[l,yy,xx]:continue
   if dx and dy and (blocked[l,y,xx] or blocked[l,yy,x]):continue
   nn=(l,yy,xx);nd=d+cost
   if nd+.001<dist[nn]:dist[nn]=nd;prev[nn]=n;heapq.heappush(q,(nd+heuristic(nn),nd,nn))
  if not vblock[y,x]:
   for ll in range(L):
    if ll==l:continue
    nn=(ll,y,x);nd=d+90
    if nd+.001<dist[nn]:dist[nn]=nd;prev[nn]=n;heapq.heappush(q,(nd+heuristic(nn),nd,nn))
 else:
  Image.fromarray(np.uint8(blocked[0])*255).resize((W*2,H*2)).save(str(R/'routing/mask-F.png'))
  Image.fromarray(np.uint8(vblock)*255).resize((W*2,H*2)).save(str(R/'routing/mask-via.png'))
  raise RuntimeError('No route '+net+' expanded '+str(count))
 path=[end]
 while path[-1]!=start:path.append(prev[path[-1]])
 path.reverse();pts=[]
 for i,n in enumerate(path):
  if i==0 or i==len(path)-1 or tuple(n[j]-path[i-1][j] for j in range(3))!=tuple(path[i+1][j]-n[j] for j in range(3)):pts.append([n[2]*S,n[1]*S,n[0]])
 pts[0]=a;pts[-1]=z
 for p1,p2 in zip(pts,pts[1:]):
  if p1[2]!=p2[2]:
   for l in range(L):shapes.append({'net':net,'layer':l,'circle':p1[:2],'r':.3})
   g['holes'].append({'xy':p1[:2],'r':.15})
  else:shapes.append({'net':net,'layer':p1[2],'line':[p1[:2],p2[:2]],'r':width/2})
 print('routed',net,'segments',len(pts)-1,'expanded',count,flush=True);return {'net':net,'points':pts,'width':width}

def p(k):return pads[k]['xy']+[0]
plans=[('EXC_SENSE_P',[5.7,53.35,2],[18.85,46.1,2],.15),('REF_N',p('R10:2'),p('C11:2'),.15),('V3V3',p('C3:1'),p('U1:12'),.4)]
results=[]
for net,a,z,width in plans:
 results.append(solve(net,a,z,width));(R/'routing/finish-routes.json').write_text(json.dumps(results,indent=2))
