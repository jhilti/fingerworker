#!/usr/bin/env python3
"""Nominal climbing-hand envelope and constant-link-length checks.

Run with Python 3. This samples the reference hand against conservative solids;
it does not replace regenerated Onshape boolean checks or physical fit testing.
The moving enclosure begins at x84 mm (x54 at full stroke), with its roof at
z59.5 mm. Its cavity starts at x80 mm; ignoring that underside relief makes this
surface check conservative. Dimensions are in millimetres.
"""

import math

# Independent numerical envelope check for the hand helper. Conservative deck
# has sharp outer edges and no R4 pocket-mouth relief. Nominal mm dimensions.
fingers=[('index',84,-28,71,43,29,8.5),('middle',87,-8,73,44,27,9),('ring',84,13,72,43,30,8.4),('little',79,31,70,43,33,7.2)]
palms=[((-15,0,65.5),(39,23,12)),((25,0,64),(29,29,14.5)),((58,0,74.5),(45,38,14)),((46,-25,72),(27,17,12))]
thumb=[(47,-30,70),(64,-49,70),(85,-68,69),(101,-71,68)]
thumb_r=[11,9.6,8.2,7.1]
def add(a,b): return tuple(x+y for x,y in zip(a,b))
def sub(a,b): return tuple(x-y for x,y in zip(a,b))
def mul(a,s): return tuple(x*s for x in a)
def norm(a): return math.sqrt(sum(x*x for x in a))
def unit(a): return mul(a,1/norm(a))
def cross(a,b): return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def ellipsoid(c,r):
 for i in range(81):
  lat=math.pi*i/80
  for j in range(96):
   az=2*math.pi*j/96
   yield add(c,(r[0]*math.sin(lat)*math.cos(az),r[1]*math.sin(lat)*math.sin(az),r[2]*math.cos(lat)))
def chain(points,radii):
 for c,r in zip(points,radii): yield from ellipsoid(c,(r,r,r))
 for p,q,r,s in zip(points,points[1:],radii,radii[1:]):
  a=unit(sub(q,p)); length=norm(sub(q,p)); sine=(r-s)/length; cosine=math.sqrt(1-sine*sine)
  bottom=add(p,mul(a,r*sine)); top=add(q,mul(a,s*sine))
  b=unit(cross(a,(0,1,0))); c=cross(a,b)
  for i in range(81):
   t=i/80; center=add(mul(bottom,1-t),mul(top,t)); radius=((1-t)*r+t*s)*cosine
   for j in range(96):
    angle=j*2*math.pi/96
    yield add(center,mul(add(mul(b,math.cos(angle)),mul(c,math.sin(angle))),radius))
def pose(f,stroke):
 name,x,y,z,p,m,r=f; root=(x,y,z); dip=(137.1+r*.8-stroke,y,66); tip=(137.1+r*.74-stroke,y,39.6+r*.74)
 delta=sub(dip,root); distance=norm(delta); along=(p*p-m*m+distance*distance)/(2*distance)
 assert abs(p-m)<distance<p+m, (name,stroke,distance)
 rise=math.sqrt(p*p-along*along); direction=mul(delta,1/distance); up=(-direction[2],0,direction[0]); pip=add(add(root,mul(direction,along)),mul(up,rise))
 points=[root,pip,dip,tip]; radii=[r,r*.9,r*.8,r*.74]
 assert abs(norm(sub(pip,root))-p)<1e-10
 assert abs(norm(sub(dip,pip))-m)<1e-10
 assert abs(tip[0]-radii[-1]-(137-stroke)-.1)<1e-10
 assert abs(tip[2]-radii[-1]-39.5-.1)<1e-10
 return points,radii

def deck_collide(p,stroke):
 x,y,z=p
 if not (125-stroke <= x <= 184-stroke and abs(y)<=62.5 and z<=59.5): return False
 dx=abs(x-(154-stroke))-9; dy=abs(y)-39
 pocket_sdf=math.hypot(max(dx,0),max(dy,0))+min(max(dx,dy),0)-8
 return z<39.5 or pocket_sdf>0

def collide(p,stroke):
 x,y,z=p
 hood = (84-stroke<=x<=198-stroke and abs(y)<=86 and z<59.5
         and not (124.4-stroke<x<184.6-stroke and abs(y)<63.1))
 return deck_collide(p,stroke) or hood

for stroke in [i*.5 for i in range(61)]:
 for f in fingers: pose(f,stroke)
print('Fixed-length inverse kinematics: 61 stroke positions, 0..30 mm in 0.5 mm increments; all feasible.')
fixed=[]
for p,r in palms: fixed.extend(ellipsoid(p,r))
fixed.extend(chain(thumb,thumb_r))
for stroke in (0,15,30):
 checked=0; collisions=[]
 for p in fixed:
  checked+=1
  if collide(p,stroke): collisions.append(('palm/thumb',p))
 for f in fingers:
  points,radii=pose(f,stroke)
  for p in chain(points,radii):
   checked+=1
   if collide(p,stroke): collisions.append((f[0],p))
 assert not collisions, (stroke,collisions[:5],len(collisions))
 print(f'{stroke:2d} mm: {checked:,} sampled hand surface points; no intrusion into conservative deck/pocket and moving hood roof.')
print('Fingertip wall clearance = 0.100 mm; floor clearance = 0.100 mm at every pose.')
print('Heel pad contact: 64 - 14.5 = 49.5 mm. Thumb distal tip underside = 60.9 mm (>59.5 mm deck).')
print('Limits: numerical surface sampling and nominal envelopes; exact regenerated CAD boolean still required.')
