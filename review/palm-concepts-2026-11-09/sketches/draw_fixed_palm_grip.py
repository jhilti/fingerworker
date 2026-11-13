"""Editable geometric concept sketch. Illustrative geometry; not manufacturing CAD."""
from pathlib import Path
import os
os.environ.setdefault('MPLCONFIGDIR', '/tmp/fingerworker-sketch-mpl')
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import PathPatch, FancyBboxPatch, FancyArrowPatch
from matplotlib.path import Path as MPath
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from mpl_toolkits.mplot3d import proj3d

out = Path(__file__).parent
ink, edge, teal, force = '#273b3c', '#526767', '#a8cfca', '#c17541'
fig = plt.figure(figsize=(16, 11), facecolor='white')
fig.text(.045, .945, 'A GRIP TO PRESS AGAINST', size=29, weight='bold', color=ink)
fig.text(.047, .908, 'Refining option 03  /  fixed palm grip', size=15, color=edge)
ax = fig.add_axes([.015, .255, .68, .63], projection='3d', computed_zorder=False)
ax.set_facecolor('white')

def rounded_rect(hx, hy, r, n=14):
    points = []
    for cx, cy, a in [(hx-r,hy-r,0),(-hx+r,hy-r,90),(-hx+r,-hy+r,180),(hx-r,-hy+r,270)]:
        t = np.deg2rad(np.linspace(a, a+90, n))
        points.extend(zip(cx+r*np.cos(t), cy+r*np.sin(t)))
    return np.asarray(points)

def block(hx, hy, r, z0, z1, color, order):
    p = rounded_rect(hx, hy, r)
    lo = np.c_[p, np.full(len(p),z0)]; hi = np.c_[p, np.full(len(p),z1)]
    faces = [hi, lo[::-1]] + [np.array([lo[i],lo[(i+1)%len(p)],hi[(i+1)%len(p)],hi[i]]) for i in range(len(p))]
    ax.add_collection3d(Poly3DCollection(faces, facecolor=color, edgecolor='none', zorder=order))
    for a in (lo, hi):
        q = np.vstack((a,a[0])); ax.plot(*q.T, color=edge, lw=.7, zorder=order+.1)

block(22, 60, 6, 0, 4, '#e3e9e8', 4)
block(10, 32, 6, 4, 23, '#83aaa6', 21)

# Soft rectangular X/Z section: broad near-vertical face, rounded crown/underside.
# The longitudinal envelope creates generous rounded ends.
def signed_power(a, p):
    return np.sign(a)*np.abs(a)**p
u = np.linspace(-np.pi/2,np.pi/2,160)
v = np.linspace(0,2*np.pi,200)
U,V = np.meshgrid(u,v)
envelope = np.maximum(np.cos(U),0)**.38
x = 14*envelope*signed_power(np.cos(V),.6)
y = 55*np.sin(U)
z = 25+16*envelope*signed_power(np.sin(V),.6)
ax.plot_surface(x,y,z,color=teal,edgecolor='none',rstride=1,cstride=1,shade=True,antialiased=False,zorder=30)
# Sparse surface lines on visible face only, describing the continuous radii.
for vv in (np.pi*.68,np.pi*1.32):
    env = np.maximum(np.cos(u),0)**.38
    ax.plot(14*env*signed_power(np.cos(vv),.6),55*np.sin(u),25+16*env*signed_power(np.sin(vv),.6),
            color=edge,lw=.65,alpha=.55,zorder=31)
ax.set_xlim(-35,35); ax.set_ylim(-68,68); ax.set_zlim(0,49)
ax.set_box_aspect((70,136,49),zoom=1.2)
ax.view_init(elev=22,azim=-135); ax.set_proj_type('ortho'); ax.set_axis_off()
fig.canvas.draw()

def project(point):
    xp,yp,_ = proj3d.proj_transform(*point,ax.get_proj())
    return fig.transFigure.inverted().transform(ax.transData.transform((xp,yp)))

def callout(label, point, at, ha='left'):
    ax.annotate(label,xy=project(point),xycoords=fig.transFigure,xytext=at,textcoords=fig.transFigure,
                ha=ha,va='center',fontsize=14,color=ink,weight='bold',
                arrowprops=dict(arrowstyle='-',color=edge,lw=1,shrinkA=8,shrinkB=3),
                annotation_clip=False,zorder=1000)

callout('Broad, upright\npalm contact',(-14,-5,25),(.045,.79))
callout('Softly rounded\nthumb-contact ends',(0,-52,30),(.49,.795))
callout('Open underside\nat both ends',(-8,-43,10),(.43,.30))
callout('Solid central support\ninto the fixed frame',(-10,20,9),(.045,.32))

# Explicit force arrow enters the palm-facing side, parallel to sliding travel.
start,end = project((-44,-3,25)),project((-15,-3,25))
arrow = FancyArrowPatch(start,end,transform=fig.transFigure,arrowstyle='-|>',mutation_scale=21,
                       lw=3,color=force,zorder=2000)
fig.add_artist(arrow)
fig.text(start[0]-.018,start[1]-.038,'PRESS',size=13,color=force,weight='bold')

# Side profile: tall contact face rather than an upward-facing shelf.
sec = fig.add_axes([.715,.43,.25,.39]); sec.set_aspect('equal'); sec.axis('off')
verts=[(-14,19),(-14,34),(-14,40),(-9,42),(0,42),
       (9,42),(14,40),(14,34),(14,19),(14,12),(10,10),(9,10),
       (9,4),(22,4),(22,0),(-22,0),(-22,4),(-9,4),(-9,10),
       (-10,10),(-14,12),(-14,19),(-14,19)]
codes=[MPath.MOVETO,MPath.LINETO]+[MPath.CURVE4]*6+[MPath.LINETO]+[MPath.CURVE4]*3+[MPath.LINETO]*7+[MPath.CURVE4]*3+[MPath.CLOSEPOLY]
sec.add_patch(PathPatch(MPath(verts,codes),facecolor=teal,edgecolor=edge,lw=1.4,hatch='///'))
sec.annotate('',xy=(-14,25),xytext=(-40,25),arrowprops=dict(arrowstyle='-|>',lw=3,color=force,mutation_scale=20))
sec.text(-40,31,'Palm\npressure',size=12,color=force,weight='bold',ha='left')
sec.set_xlim(-43,26); sec.set_ylim(-4,50)
fig.text(.72,.84,'SIDE PROFILE',size=14,color=ink,weight='bold')
fig.text(.72,.805,'Along the sliding direction',size=12,color=edge)
fig.text(.72,.40,'A tall face takes the pressure.\nThe rounded crown eases contact.',size=13,color=edge,linespacing=1.5)

# Context strip shows the opposing loads without implying a changed mechanism.
ctx=fig.add_axes([.045,.105,.91,.135]);ctx.set_xlim(0,100);ctx.set_ylim(0,15);ctx.axis('off')
ctx.plot([15,86],[3,3],lw=4,color='#cbd5d3',solid_capstyle='round')
ctx.add_patch(FancyBboxPatch((22,3),7,9,boxstyle='round,pad=0,rounding_size=2',facecolor=teal,edgecolor=edge,lw=1.2))
ctx.add_patch(FancyBboxPatch((70,3),7,9,boxstyle='round,pad=0,rounding_size=2',facecolor='#eee5d8',edgecolor=edge,lw=1.2))
ctx.annotate('',xy=(21,8),xytext=(7,8),arrowprops=dict(arrowstyle='-|>',color=force,lw=2.5,mutation_scale=18))
ctx.annotate('',xy=(78,8),xytext=(92,8),arrowprops=dict(arrowstyle='-|>',color=force,lw=2.5,mutation_scale=18))
ctx.text(7,12,'Palm pushes',size=12,color=force,weight='bold')
ctx.text(92,12,'Fingers pull',size=12,color=force,weight='bold',ha='right')
ctx.text(25.5,-.5,'FIXED PALM GRIP',size=11,color=ink,ha='center',va='top')
ctx.text(73.5,-.5,'SLIDING FINGER GRIP',size=11,color=ink,ha='center',va='top')
ctx.text(49,7,'Opposing contact surfaces',size=12,color=edge,ha='center')
fig.text(.045,.045,'CONCEPT SKETCH  /  One continuous grip form. Geometry and hand fit still to be developed.',size=11,color=edge)
fig.savefig(out/'04-fixed-palm-grip.png',dpi=150,facecolor='white')
fig.savefig(out/'04-fixed-palm-grip.svg',facecolor='white')
print(out/'04-fixed-palm-grip.png')
