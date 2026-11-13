"""Original geometric concept illustration; not an edit of a generated image or CAD."""
from pathlib import Path
import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/fingerworker-sketch-mpl')
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import PathPatch
from matplotlib.path import Path as MPath
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from mpl_toolkits.mplot3d import proj3d

out=Path(__file__).parent
ink='#303637';teal='#a6c9c5';edge='#465354';white='#ffffff'
fig=plt.figure(figsize=(15,10),facecolor=white)
fig.text(.035,.94,'03  WRAP-AROUND GRIP',fontsize=29,fontweight='bold',fontstyle='italic',color=ink)
fig.text(.037,.895,'Isolated grip-form study',fontsize=14,color=edge)
ax=fig.add_axes([.015,.16,.66,.70],projection='3d',computed_zorder=False)
ax.set_facecolor(white)

def rounded_rect(hx,hy,r,n=12):
    pts=[]
    for cx,cy,a in [(hx-r,hy-r,0),(-hx+r,hy-r,90),(-hx+r,-hy+r,180),(hx-r,-hy+r,270)]:
        t=np.deg2rad(np.linspace(a,a+90,n))
        pts.extend(zip(cx+r*np.cos(t),cy+r*np.sin(t)))
    return np.asarray(pts)
def block(hx,hy,r,z0,z1,color):
    p=rounded_rect(hx,hy,r)
    low=np.column_stack((p,np.full(len(p),z0)));hi=np.column_stack((p,np.full(len(p),z1)))
    faces=[hi,low[::-1]]+[np.array([low[i],low[(i+1)%len(p)],hi[(i+1)%len(p)],hi[i]]) for i in range(len(p))]
    ax.add_collection3d(Poly3DCollection(faces,facecolor=color,edgecolor='none',zorder=z1))
    for face in (low,hi):
        q=np.vstack((face,face[0]));ax.plot(q[:,0],q[:,1],q[:,2],color=edge,lw=.7,zorder=z1+.1)

block(21,59,5,0,4,'#d8dfdf')
block(9,32,5,4,21,'#80aaa6')
u=np.linspace(0,np.pi,81);v=np.linspace(0,2*np.pi,121);U,V=np.meshgrid(u,v)
x=17*np.sin(U)*np.cos(V);y=55*np.sin(U)*np.sin(V);z=23+12*np.cos(U)
ax.plot_surface(x,y,z,color=teal,edgecolor='none',rstride=1,cstride=1,antialiased=True,shade=True,zorder=30)
# Sparse contour curves describe the oval form without a dense mesh.
t=np.linspace(0,2*np.pi,220)
ax.plot(17*np.cos(t),55*np.sin(t),np.full_like(t,23),color=edge,lw=.8,alpha=.75,zorder=31)
for vv in [np.pi/2,3*np.pi/2]:
    uu=np.linspace(0,np.pi,160)
    ax.plot(17*np.sin(uu)*np.cos(vv),55*np.sin(uu)*np.sin(vv),23+12*np.cos(uu),color=edge,lw=.7,alpha=.6,zorder=31)
ax.set_xlim(-30,30);ax.set_ylim(-66,66);ax.set_zlim(0,42)
ax.set_box_aspect((60,132,42),zoom=1.22);ax.view_init(elev=24,azim=-40);ax.set_axis_off()
ax.set_proj_type('ortho')
fig.canvas.draw()
def callout(label,point,xytext):
    xp,yp,_=proj3d.proj_transform(*point,ax.get_proj())
    disp=ax.transData.transform((xp,yp));target=fig.transFigure.inverted().transform(disp)
    ax.annotate(label,xy=target,xycoords=fig.transFigure,xytext=xytext,textcoords=fig.transFigure,
                fontsize=16,fontweight='bold',color=ink,ha='left',va='center',
                arrowprops=dict(arrowstyle='-',color=ink,lw=1.1,shrinkA=8,shrinkB=4),annotation_clip=False,zorder=1000)
callout('Broad oval\npalm face',(0,6,35),(.045,.79))
callout('Rounded underside',(0,-45,16.1),(.035,.23))
callout('Open thumb return',(0,-40,9),(.43,.15))

sec=fig.add_axes([.70,.32,.27,.40]);sec.set_aspect('equal');sec.axis('off')
verts=[(-2.2,3.2),(-2.2,4.3),(2.2,4.3),(2.2,3.2),(2.2,2.55),(1.05,2.4),(.85,2.5),(.85,.7),(2.5,.7),(2.5,.3),(-2.5,.3),(-2.5,.7),(-.85,.7),(-.85,2.5),(-1.05,2.4),(-2.2,2.55),(-2.2,3.2),(-2.2,3.2)]
codes=[MPath.MOVETO]+[MPath.CURVE4]*6+[MPath.LINETO]*7+[MPath.CURVE4]*3+[MPath.CLOSEPOLY]
sec.add_patch(PathPatch(MPath(verts,codes),facecolor=teal,edgecolor=edge,lw=1.4,hatch='///'))
sec.set_xlim(-2.8,2.8);sec.set_ylim(0,4.6)
sec.text(0,4.4,'SECTION',fontsize=14,fontweight='bold',color=ink,ha='center')

fig.text(.70,.24,'One continuous printed form',fontsize=13,color=edge)
fig.text(.035,.085,'Open underneath at the outer ends — no closed thumb ring',fontsize=15,color=ink)
fig.text(.035,.04,'SHAPE STUDY — NOT MANUFACTURING CAD',fontsize=12,fontstyle='italic',color=edge)
fig.savefig(out/'03-wraparound-palm-grip.png',dpi=150,facecolor=white)
fig.savefig(out/'03-wraparound-palm-grip.svg',facecolor=white)
print(out/'03-wraparound-palm-grip.png')
