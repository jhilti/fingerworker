from pathlib import Path
import os,json
os.environ['MPLCONFIGDIR']='/tmp/fingerworker-matplotlib-finger'
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import numpy as np,trimesh as tm
from check_p04_supports import segments,read_gcode,SUPPORTS
OUT=Path(__file__).resolve().parents[1];ROOT=OUT.parents[1]
row=next(r for r in json.loads((OUT/'plate-layout.json').read_text())['placements'] if r['ref']=='P04')
R=np.array(row['rotation_3x3']);T=np.array(row['normalization_translation_mm']);O=np.array([*row['plate_xy_mm'],0])
mesh=tm.load_mesh(OUT/'source-mm/P04.stl')
lines=[]
for s in segments(read_gcode(OUT/'validation/Fingerworker_R12_H2D_04mm_PLA_Fit_Test_verification.gcode.3mf',3)):
 if s['feature'] not in SUPPORTS:continue
 p=(s['points']-O-T)@R
 for a,b in zip(p[:-1],p[1:]):
  if max(abs(a[1]),abs(b[1]))<28:lines.append([[a[0],a[2]],[b[0],b[2]]])
fig,ax=plt.subplots(figsize=(11,6),layout='constrained');fig.patch.set_facecolor('white');ax.set_facecolor('#f8fafc')
ax.add_collection(LineCollection(lines,colors='#1689b5',linewidths=.25,alpha=.18))
sec=mesh.section(plane_origin=[0,0,0],plane_normal=[0,1,0])
for ent in sec.entities:
 poly=sec.vertices[ent.points];ax.plot(poly[:,0],poly[:,2],color='#343f4d',lw=1.7)
ax.plot([72,72],[14,26],color='#1b9c63',lw=5,label='Fingerzugfläche: Topfläche, kein Supportkontakt')
ax.plot([77,101],[10,10],color='#dc9d27',lw=4,label='Muldenboden: senkrechte Außenwand, kein Supportkontakt')
ax.axvline(60,color='#596474',lw=1.7,label='Druckbett in dieser Baulage')
ax.annotate('Baumstützen vom Bett\ndurch die offene Mulde',xy=(93,29.5),xytext=(74,40),fontsize=11,arrowprops={'arrowstyle':'->','color':'#1689b5'},color='#096b91')
ax.annotate('Gegenwand wird gestützt',xy=(105,20),xytext=(101,39),fontsize=10,arrowprops={'arrowstyle':'->','color':'#1689b5'})
ax.set(xlim=(56,123),ylim=(-7,46),xlabel='Native X / mm (Druckhöhe = X − 60)',ylabel='Native Z / mm',title='P04: Front unten + Baumstützen nur vom Druckbett\nEchte Bambu-Werkzeugwege: Stützenprojektion |Y| < 28 mm, Kontur Y = 0')
ax.set_aspect('equal');ax.grid(alpha=.15);ax.legend(loc='lower right',fontsize=9,framealpha=.95)
fig.savefig(OUT/'preview/P04-Stuetzen.png',dpi=180);plt.close(fig)
print('Rendered actual toolpaths in native central section')
