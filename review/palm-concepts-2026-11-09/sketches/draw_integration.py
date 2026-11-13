"""Dimension-informed integration schematic; no manufacturing geometry is changed."""
from pathlib import Path
import os, json, hashlib
os.environ.setdefault('MPLCONFIGDIR','/tmp/fingerworker-sketch-mpl')
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, PathPatch
from matplotlib.path import Path as MP

out=Path(__file__).parent
ink='#273b3c'; grey='#617071'; teal='#99c9c0'; dark='#408e82'; tan='#e9d5b7'; orange='#b67546'
fig=plt.figure(figsize=(16,10),facecolor='white')
fig.text(.045,.945,'INTEGRATE THE GRIP INTO THE FRAME',size=26,weight='bold',color=ink)
fig.text(.047,.905,'One continuous P01 part  /  retain the close reach and the existing mechanism',size=14,color=grey)

def rounded(ax,x,y,w,h,r,fc,ec=grey,lw=1,z=1):
    p=FancyBboxPatch((x,y),w,h,boxstyle=f'round,pad=0,rounding_size={r}',facecolor=fc,edgecolor=ec,lw=lw,zorder=z)
    ax.add_patch(p);return p
def label(ax,text,xy,pos,ha='left',color=ink):
    ax.annotate(text,xy=xy,xytext=pos,ha=ha,va='center',size=12,color=color,
                arrowprops=dict(arrowstyle='-',color=grey,lw=1,shrinkA=5,shrinkB=3),zorder=20)

ax=fig.add_axes([.03,.22,.62,.63]);ax.set_aspect('equal');ax.axis('off')
rounded(ax,-46,-66,175,132,3,'#f0f3f2',lw=1)
# Current interfaces, simplified but placed in their R15 coordinates.
for y in [-51,51]:
    rounded(ax,-18,y-12,10,24,1,'#b6c0be',z=3)
    ax.plot([-16,125],[y,y],color='#8c9ca0',lw=4,zorder=2)
    xx=np.linspace(12,108,500)
    ax.plot(xx,y+5*np.sin((xx-12)*2*np.pi/4),color='#9faeb0',lw=.8,zorder=2)
    for x in [28,65]:rounded(ax,x-13.5,np.sign(y)*57.5-2,27,4,2,'white',z=2)
rounded(ax,-7,-63,16,126,2,'#d2d8d6',z=4)
rounded(ax,-12,-15,12,30,1,'#b0b9b8',z=5)
rounded(ax,47,-37,64,74,6,tan,z=4)
rounded(ax,57,-27,43,54,6,'#f9f5ee',z=5)
rounded(ax,119,-64,10,128,1,'#d7dddb',z=3)
# New visual envelope: central rail and rounded fixed shoulders.
verts=[(-29,-54),(-29,-62),(-24,-64),(-18,-63),(-8,-61),(-8,-46),(-16,-40),
       (-16,40),(-8,46),(-8,61),(-18,63),(-24,64),(-29,62),(-29,54),(-29,-54)]
codes=[MP.MOVETO]+[MP.CURVE4]*6+[MP.LINETO]+[MP.CURVE4]*6+[MP.CLOSEPOLY]
ax.add_patch(PathPatch(MP(verts,codes),facecolor=teal,edgecolor=dark,lw=1.8,zorder=8))
for y in [-51,51]:
    # Hidden rod socket outline demonstrates retained structural core.
    ax.add_patch(Rectangle((-18,y-12),10,24,fill=False,edgecolor=grey,lw=1,ls='--',zorder=9))
    # Wrist-side scallop indicator, not a dimensioned cut.
    t=np.linspace(-np.pi/2,np.pi/2,50)
    ax.plot(-29+2.8*np.cos(t),y+4.8*np.sin(t),color=dark,lw=2,zorder=10)
ax.annotate('',xy=(-30,0),xytext=(-54,0),arrowprops=dict(arrowstyle='-|>',color=orange,lw=2.5),zorder=20)
ax.text(-56,6,'Palm',color=orange,size=12,ha='right')
ax.annotate('',xy=(112,0),xytext=(136,0),arrowprops=dict(arrowstyle='-|>',color=orange,lw=2.5),zorder=20)
ax.text(137,6,'Fingers',color=orange,size=12,ha='left')
label(ax,'Rounded shoulders blend\nover the fixed rod sockets',(-17,54),(-59,88))
label(ax,'Sensor + floating yoke\nremain separate',(-2,4),(36,88))
label(ax,'Shallow thumb return\non the wrist side',(-27,-51),(-61,-90))
label(ax,'Existing sliding grip\nand 30 mm travel',(78,-36),(57,-91))
ax.text(-46,72,'TOP VIEW — SIMPLIFIED ASSEMBLY',size=10,color=grey)
ax.set_xlim(-68,151);ax.set_ylim(-106,103)

sec=fig.add_axes([.69,.44,.27,.40]);sec.set_aspect('equal');sec.axis('off')
# Existing fixed roof and central support (section omits other planes).
sec.add_patch(Rectangle((-46.1,9.5),22.85,5,facecolor='#e2e8e5',edgecolor=grey,lw=.8))
sec.add_patch(Rectangle((-22.75,3.8),6.75,25.7,facecolor='#c6d2cd',edgecolor=grey,lw=.8))
# Proposed profile retains crown Z33; new outer face replaces the arc.
vv=[(-29,14.4),(-29,28),(-29,31),(-27,33),(-24,33),(-21,33),
    (-18,33),(-16,31),(-16,28),(-16,14.4),(-29,14.4)]
cc=[MP.MOVETO,MP.LINETO]+[MP.CURVE4]*3+[MP.LINETO]+[MP.CURVE4]*3+[MP.LINETO,MP.CLOSEPOLY]
sec.add_patch(PathPatch(MP(vv,cc),facecolor=teal,edgecolor=dark,lw=1.8,zorder=3))
# True R15 wrist arc at the center section.
ang=np.linspace(np.pi,np.pi/2,100)
sec.plot(-20+14*np.cos(ang),19+14*np.sin(ang),color=grey,lw=1.3,ls='--',zorder=5)
sec.plot([-34,-34],[14.4,19],color=grey,lw=1.3,ls='--',zorder=5)
sec.plot([-16,-16],[12,43],color='#acb5b1',lw=1,ls=':',zorder=6)
sec.annotate('',xy=(-29,25),xytext=(-42,25),arrowprops=dict(arrowstyle='-|>',color=orange,lw=2.3))
sec.annotate('Keep the current\n33 mm crown first',xy=(-22,33),xytext=(-45,40),size=10,color=ink,va='top',
             arrowprops=dict(arrowstyle='-',lw=.8,color=grey))
sec.text(-45,1,'Retain the roof and structural root',size=9,color=grey,ha='left',va='bottom')
sec.text(-11,23,'Sensor\nside',size=11,color=grey,ha='left')
sec.set_xlim(-47,0);sec.set_ylim(0,49)
fig.text(.69,.85,'CENTRAL PROFILE',size=14,weight='bold',color=ink)
fig.text(.69,.81,'Dashed: current R15 contact',size=11,color=grey)
fig.text(.69,.405,'Upright face, broad root',size=16,weight='bold',color=ink)
fig.text(.69,.375,'Reshape before adding height.\nKeep new central stock behind\nthe existing sensor-side limit.',size=12,color=grey,linespacing=1.5,va='top')

fig.text(.047,.135,'PRINT AS ONE FRAME',size=12,weight='bold',color=dark)
fig.text(.047,.098,'Base down • PLA • sloped thumb returns • no added clips or small parts',size=13,color=ink)
fig.text(.047,.045,'INTEGRATION STUDY — proposed contours are schematic; no new CAD, fit or strength validation.',size=11,color=grey)
fig.savefig(out/'05-integration-layout.png',dpi=150,facecolor='white')
fig.savefig(out/'05-integration-layout.svg',facecolor='white')

root=out.parents[2]
sources=['fingerworker_mvp.fs','review/inboard-straps-2026-11-08/validation/native-motion.json',
         'review/near-palm-2026-11-06/mechanics/design-specification.json']
data={'purpose':'Concept integration review, not a release','changes_proposed':['Reshape only P01','Upright central contact backed by existing fixed wall','Rounded shoulders retaining rod sockets','Shallow wristward thumb returns with sloped undersides'],
      'first_profile_candidate':{'crown_z_mm':33,'wrist_face_x_mm':-29,'central_added_stock_max_x_mm':-16,'status':'Illustrative starting profile, no human-fit or native CAD validation'},
      'retained':['P05 floating yoke and sensor load path','Steel rod sockets and lateral service access','30mm slider stroke','Sensor +3.2mm X then +40mm Z removal','Electronics roof and attachment interfaces','Inboard strap slots'],
      'limitations':['No guarantee of hands-free retention; thumb must still grip','Only existing R15 is geometrically validated','One-plate layout and print time need re-slicing after CAD changes'],
      'sources':{s:hashlib.sha256((root/s).read_bytes()).hexdigest() for s in sources}}
(out/'integration-review.json').write_text(json.dumps(data,indent=2)+'\n')
print(out/'05-integration-layout.png')
