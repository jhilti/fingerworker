#!/usr/bin/env python3
"""Native P01 section with a schematic, clearly labelled strap double-back."""
from pathlib import Path
import hashlib,json,sys
import numpy as np
from shapely.geometry import LineString,box
from shapely.ops import polygonize,unary_union
from OCP.BRepAlgoAPI import BRepAlgoAPI_Section
from OCP.BRepAdaptor import BRepAdaptor_Curve
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_EDGE
from OCP.TopoDS import TopoDS
from OCP.gp import gp_Pln,gp_Pnt,gp_Dir
HERE=Path(__file__).resolve().parent;STUDY=HERE.parent;ROOT=STUDY.parents[1]
sys.path.insert(0,str(ROOT/'review/flat132-solid-palm-2026-10-23/validation'))
import audit_solid_palm as b
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text())
inv=read(STUDY/'validation/native-step-inventory.json');design=read(STUDY/'mechanics/design-specification.json')
native=read(STUDY/'validation/native-integration.json')
assert native['status'].startswith('PASS') and native['source_sha256']==design['source_sha256']
assert inv['native_step_sha256']==native['native_step_sha256']==sha(inv['native_step'])
frame=b.read_step(inv['native_step'])[0][inv['native_part_correspondence']['P01']['candidates'][0]['solid_index']]
cut=BRepAlgoAPI_Section(frame,gp_Pln(gp_Pnt(28,0,0),gp_Dir(1,0,0)),False);cut.Build();assert cut.IsDone()
ex=TopExp_Explorer(cut.Shape(),TopAbs_EDGE);lines=[]
while ex.More():
 c=BRepAdaptor_Curve(TopoDS.Edge(ex.Current()))
 pts=[]
 for t in np.linspace(c.FirstParameter(),c.LastParameter(),201):
  p=c.Value(float(t));pts.append((round(p.Y(),6),round(p.Z(),6)))
 lines.append(LineString(pts));ex.Next()
# Polygonized native section, cropped to the one right-hand inboard slot.
polys=list(polygonize(unary_union(lines)));assert polys
shape=unary_union(polys).intersection(box(46,-3,72,9))
assert shape.area>40 and shape.intersection(box(56.5,-2,58.5,4)).area<1e-6
sx=lambda y:60+(y-46)*12
sy=lambda z:195-z*12
paths=[]
for poly in (list(shape.geoms) if hasattr(shape,'geoms') else [shape]):
 for ring in [poly.exterior]+list(poly.interiors):
  coords=list(ring.coords)
  paths.append('M '+' L '.join(f'{sx(y):.3f},{sy(z):.3f}' for y,z in coords)+' Z')
# The actual frame contour is to scale. Flexible webbing routing is illustrative;
# two25mm ends are attached separately, no band across the top of the mechanism.
svg=f'''<svg xmlns="http://www.w3.org/2000/svg" width="960" height="480" viewBox="0 0 960 480" role="img" aria-labelledby="title desc">
<title id="title">Zwei25-mm-Gurte: Enden um die äußeren Stege zurückführen</title>
<desc id="desc">Querschnitt der rechten P01-Gurtschlitzes bei X28 aus dem nativen R18-CAD. Ein Gurtende kommt von unten, läuft durch die Öffnung nach oben, über den äußeren Steg, außen herunter und wird an sich selbst befestigt. Der lange Gurt läuft unten um den Gegenstand, nicht über den Griff.</desc>
<defs><marker id="arrow" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto"><path d="M0,0 L7,3.5 L0,7 Z" fill="#187f89"/></marker></defs>
<rect width="960" height="480" rx="18" fill="#f3f6f7"/>
<g font-family="Arial,sans-serif" fill="#18353d"><text x="36" y="38" font-size="22" font-weight="700">Zwei Gurte · jedes Ende außen zurückführen</text>
<text x="36" y="64" font-size="14" fill="#526970">Rechter Schlitz in der Grundplatte im Schnitt bei X28 · Rahmenkontur aus dem finalen CAD</text>
<path d="{' '.join(paths)}" fill="#c6d5da" fill-rule="evenodd" stroke="#4f707d" stroke-width="1.5"/>
<path d="M 252,430 L198,290 L198,150 Q198,123 226,123 L302,123 Q324,123 324,147 L324,332 Q324,363 293,374 L269,382" fill="none" stroke="#188b95" stroke-width="20" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M 252,430 L198,290 L198,166 M218,123 L291,123 M324,182 L324,309" fill="none" stroke="#d9f5f3" stroke-width="2.2" marker-end="url(#arrow)"/>
<path d="M249,370 L268,415" stroke="#f0ab42" stroke-width="30" stroke-linecap="round"/>
<path d="M249,370 L268,415" stroke="#8a5d21" stroke-width="1.5" stroke-dasharray="3 4"/>
<path d="M200,449 Q96,405 39,451" fill="none" stroke="#bcc9ca" stroke-width="3" stroke-dasharray="6 5"/>
<text x="36" y="112" font-size="14">innen / Rahmen</text><text x="309" y="101" font-size="14">außen</text>
<text x="63" y="250" font-size="14">27 × 4 mm</text><path d="M136,244 L186,201" stroke="#526970" fill="none"/>
<text x="53" y="281" font-size="13" fill="#526970">Öffnung</text>
<g font-size="17"><text x="470" y="118" font-weight="700">1  Von unten durch die Öffnung</text><text x="470" y="150">Ein25-mm-Gurt, höchstens2 mm dick.</text>
<text x="470" y="201" font-weight="700">2  Über den äußeren Steg</text><text x="470" y="233">Außen nach unten zurückführen.</text>
<text x="470" y="284" font-weight="700">3  Sicher an sich selbst befestigen</text><text x="470" y="316">Beide Enden jedes Gurts müssen rückfaltbar sein.</text><text x="470" y="348">Gurtlänge passend zum Umfang plus Rückfaltungen.</text></g>
<rect x="460" y="378" width="461" height="68" rx="10" fill="#e1eeec"/>
<text x="477" y="405" font-size="16" font-weight="700">Der lange Gurt läuft unten um den Gegenstand.</text>
<text x="477" y="430" font-size="15">Keine Gurtstrecke über Griff oder Bewegungsraum.</text>
<text x="36" y="471" font-size="12" fill="#526970">Gurt und Gegenstand schematisch; Befestigungsart und reale Tragfähigkeit sind am Aufbau zu prüfen.</text></g></svg>'''
svg=svg.replace('Zwei25','Zwei 25').replace('Ein25','Ein 25').replace('höchstens2','höchstens 2')
output=HERE/'strap-routing.svg';output.write_text(svg)
provenance=dict(status='RENDERED_NATIVE_R18_STRAP_ROUTING',source_sha256=design['source_sha256'],native_step_sha256=inv['native_step_sha256'],native_P01_solid_index=inv['native_part_correspondence']['P01']['candidates'][0]['solid_index'],section_x_mm=28,section_crop_yz_mm=[[46,-3],[72,9]],native_section_area_in_crop_mm2=shape.area,image_sha256=sha(output),renderer_sha256=sha(__file__),limitations='Native frame cross-section to scale; flexible strap and object schematic. This is an assembly illustration, not independent strength or collision evidence.')
(HERE/'strap-routing-provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
print(json.dumps(provenance,indent=2))
