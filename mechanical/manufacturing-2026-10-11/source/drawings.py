"""Vector drawings from exported BReps, with finished dimensions and machining notes.
PDFs use explicit view directions; dimension lines reference projected bounding faces.
"""
from pathlib import Path
import io,re,json,hashlib
import cadquery as cq
from OCP.gp import gp_Ax2,gp_Pnt,gp_Dir
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4,landscape
from reportlab.graphics import renderPDF
from svglib.svglib import svg2rlg
import fitz
OUT=Path(__file__).resolve().parents[1]; DRAW=OUT/'drawings'
W,H=landscape(A4)
specs=[
('H02_Pusher','Gefangener Druckstift',1,'C45, Kontaktflaeche poliert',[
 'Kontaktzapfen: D4 -0,02/-0,05; Laenge 1,90 +/-0,02 ab Schulterflaeche A.',
 'Schulter: D8 +/-0,05; Dicke 1,00 +/-0,02. Halteende: M3x0,5-6g, Laenge 6,50.',
 'Gesamtlaenge 9,40 +/-0,05. Gewinde bis Schulter; Freistich max. 0,2 mm.',
 'Kontaktflaeche eben; Ra <=0,8 um; rechtwinklig zur Achse <=0,02 mm.',
 'Kanten 0,1 x45 Grad; Kontaktkante nur leicht brechen. Keine Modellierungszugaben fertigen.',
 'Montage: Schulter am Joch, M3-Vierkantmutter sichert; keine Mutterkraft auf Sensor.']),
('H04_Guide_rod','Fuehrungsstab',2,'Edelstahl 1.4301, geschliffen',[
 'D6 -0,02/-0,05; Laenge 146,0 +/-0,1. Beide Enden 0,3 x45 Grad.',
 'Geradheit <=0,10 mm ueber 146 mm. Laufoberflaeche Ra <=1,6 um.',
 'Kein Gewinde. Nach Ablangen entgraten; beide Staebe gleich lang.']),
('H05_Fixed_spring_seat','Fester Federsitz',2,'Stahl S355',[
 'D22 +/-0,1; Dicke 3,00 +/-0,05; Durchgang D6,60 +0,10/0.',
 'Bohrung konzentrisch zum Aussendurchmesser <=0,10 mm.',
 'Auflageflaechen planparallel <=0,05 mm; Kanten 0,2 x45 Grad.']),
('H06_Moving_spring_seat','Bewegter Federsitz',2,'Stahl S355',[
 'D22 +/-0,1; Dicke 3,00 +/-0,05; Durchgang D8,00 +0,10/0.',
 'Bohrung konzentrisch zum Aussendurchmesser <=0,10 mm.',
 'Auflageflaechen planparallel <=0,05 mm; Kanten 0,2 x45 Grad.']),
('H11_Preload_nut','Vorspannungsmutter',1,'C45',[
 'Grundkoerper 5,00 (X) x12,00 (Y) x12,00 (Z); allgemeine Masse +/-0,1.',
 'Axial M6x1-6H DURCH; Achse mittig Y=0 / Z=18 im Einbaukoordinatensystem.',
 'Radial M3x0,5-6H von Z=24 bis in M6-Bohrung; Achse X=-19 / Y=0.',
 'Radiale Achse 2,00 mm von X=-21; 3,00 mm von X=-16. Position +/-0,05.',
 'Kernloecher D5 / D2,5 sind nur STEP-Darstellung; fertig GEWINDE schneiden.',
 'Gewindeeingaenge 0,2 x45 Grad; keine Grate im kreuzenden M6-Gewinde.']),
('H12_Sensor_cassette','Sensorkassette',1,'C45, geschlichtete Kontaktflaechen',[
 'Hauptkoerper: X=-12..-8; Y=-13,5..+13,5; Z=7,5..28,5 (4 x27 x21).',
 'Ohren: X=-15,2..-11,8; Y=-13,5..-10 und +10..+13,5; Z=7,5..12,5.',
 'Entlastung D15 +0,10/0, Tiefe 1,60 +/-0,05 ab Sensorflaeche X=-8.',
 'Entlastungsachse Y=0 / Z=18; 10,50 mm ab Unterkante Z=7,5.',
 '2x M3x0,5-6H durch Ohren, von beiden Y-Aussenflaechen; X=-13 / Z=10.',
 'Gewindeachsen: 2,20 mm ab Ohr-Ruecken X=-15,2; 2,50 mm ab Unterkante.',
 'Sensorauflage A: X=-8, nur aeusserer Ring; Ra <=1,6 um; Ebenheit <=0,03.',
 'Rueckflaeche X=-12 parallel A <=0,03; restliche Masse +/-0,1; Kanten 0,2.',
 'Monolithisch fraesen; keine lose aufgeklebten Ohren. Keine Auflage in Entlastung.']),
('H13_Preload_adjuster','Vorspannungseinsteller',1,'C45, einteilig gedreht',[
 'Gesamtlaenge 12,00 +/-0,05; Einbau X=-24..-12; Achse Y=0 / Z=18.',
 'Daumenrad D22 +/-0,1; Dicke 2,80 +/-0,05; X=-15,8..-13.',
 'Rueckseitiger Schaft: M6x1-6g, Laenge 8,20 bis Rad; Auslauf max. 0,3.',
 'Vorderer Druckansatz: D6, Laenge 1,00 ab Rad; flache Stirnflaeche A.',
 'A: Ra <=1,6 um; rechtwinklig zur Achse <=0,03 mm; keine Zentrierbohrung.',
 'Radumfang leicht raendeln innerhalb D22; Kanten 0,2 x45 Grad.',
 'Betrieb nur 0..2 Umdrehungen Zusatzvorspannung; Anschlaege im Geraet.']),
('H15_Keeper','Mutter-Halteplatte',1,'S355',[
 'Grundplatte: 2,00 (X) x32,00 (Y) x19,00 (Z); X=-23..-21.',
 'Y=-16..+16 / Z=9..28. Mittelloch D6,40 +0,10/0, Y=0 / Z=18.',
 '2x D3,40 +0,10/0 DURCH; Y=-11/+11, Z=24 (5 mm ab Seiten, 15 mm ab unten).',
 '2x Senkung 90 Grad, D6,00 +0,10/0 ab X=-23; Tiefe nominal 1,30.',
 'Obere Randfreistellung fuer Klemmkopf: D5,80 vertikales Fraeswerkzeug,',
 'Achse X=-19 / Y=0; Z=26..28. Werkzeug liegt 2 mm vor Flaeche X=-21.',
 'Daraus Teilkreisbogen-Ausnehmung in oberer Kante; STEP-Detail verbindlich.',
 'Ebenheit <=0,05; Lochposition +/-0,05; restliche Masse +/-0,1. Entgraten.']),
('H19_Spacer','Retentions-Abstandshuelse',2,'Edelstahl 1.4301',[
 'D4,00 -0,02/-0,05; Durchgang D3,20 +0,05/0; Laenge 4,00 +/-0,03.',
 'Beide Stirnflaechen planparallel <=0,03 mm; Kanten 0,1 x45 Grad.',
 'Dient als Distanzanschlag; Schraube darf gedruckte Fuehrung nicht klemmen.']),
('H22_Brass_pad','Gewindeschonendes Druckstueck',1,'Messing CuZn39Pb3',[
 'D2,50 -0,05/-0,10; Dicke 1,00 +/-0,05. Beide Flaechen eben.',
 'Kanten leicht brechen, keine scharfen Grate; zwischen M3-Schraube und M6-Gewinde.']),
('H14_Isometric_sleeve','Isometriehuelse (optional)',2,'Stahl S355',[
 'D16 +/-0,1; Durchgang D8 +0,10/0; Laenge 86,00 +/-0,05.',
 'Die beiden Huelsen als Paar: Laengenunterschied <=0,05 mm.',
 'Stirnflaechen planparallel <=0,05 mm; Kanten 0,3 x45 Grad.',
 'Nur paarweise statt BEIDER Federn verwenden; keine Feder/Huelsen-Mischung.'])]

def text(c,x,y,s,size=9):c.setFont('Helvetica',size);c.drawString(x,y,s)
def frame(c,title,num,total,material,quantity):
    c.setStrokeColorRGB(.15,.2,.23); c.setLineWidth(.6); c.rect(24,24,W-48,H-48)
    text(c,38,H-48,'FINGERWORKER | PROTOTYP-ZEICHNUNG | REV A / 11.10.2026',10)
    text(c,38,H-74,title,17)
    c.line(24,74,W-24,74)
    text(c,38,56,f'Werkstoff: {material}   |   Menge: {quantity}',9)
    text(c,38,39,'Masse in mm. Bemaßung hat Vorrang; Ansichten eingepasst. Kein Traglastnachweis.',8)
    text(c,W-125,39,f'Blatt {num}/{total}',8)

def arrow(c,x,y,dx,dy):
    c.line(x,y,x+dx*5-dy*2,y+dy*5+dx*2);c.line(x,y,x+dx*5+dy*2,y+dy*5-dx*2)
def dimh(c,x1,x2,y,top,label):
    c.setLineWidth(.45);c.line(x1,top,x1,y-4);c.line(x2,top,x2,y-4);c.line(x1,y,x2,y)
    arrow(c,x1,y,1,0);arrow(c,x2,y,-1,0);text(c,(x1+x2)/2-14,y+5,label,8)
def dimv(c,x,y1,y2,left,label):
    c.line(left,y1,x-4,y1);c.line(left,y2,x-4,y2);c.line(x,y1,x,y2)
    arrow(c,x,y1,0,1);arrow(c,x,y2,0,-1);text(c,x+5,(y1+y2)/2,label,8)
def view(c,shape,x,y,direction,label,w=225,h=155):
    svg=cq.exporters.svg.getSVG(shape,dict(width=w,height=h,marginLeft=30,marginTop=20,projectionDir=direction,showAxes=False,showHidden=True,strokeWidth=-1))
    path=DRAW/(label.replace(' ','_')+'_temp.svg');path.write_text(svg)
    drawing=svg2rlg(io.BytesIO(svg.encode()))
    # svglib maps SVG pixels to 0.75 PDF points. Restore the requested view box
    # before positioning dimension extension lines from the CAD SVG transform.
    drawing.scale(w/drawing.width,h/drawing.height);drawing.width=w;drawing.height=h
    renderPDF.draw(drawing,c,x,y)
    axis=gp_Ax2(gp_Pnt(),gp_Dir(*direction));u=axis.XDirection();v=axis.YDirection()
    bb=shape.BoundingBox(); corners=[(a,b,d) for a in (bb.xmin,bb.xmax) for b in (bb.ymin,bb.ymax) for d in (bb.zmin,bb.zmax)]
    xx=[a*u.X()+b*u.Y()+d*u.Z() for a,b,d in corners];yy=[a*v.X()+b*v.Y()+d*v.Z() for a,b,d in corners]
    width=max(xx)-min(xx);height=max(yy)-min(yy)
    scale=float(re.search(r'scale\(([0-9.eE+-]+),',svg).group(1))
    left=x+30;top=y+h-20;right=left+width*scale;bottom=top-height*scale
    dimh(c,left,right,bottom-18,bottom,f'{width:.2f}')
    dimv(c,right+12,bottom,top,right,f'{height:.2f}')
    text(c,x+30,y+h+8,label,9)
    return path

c=canvas.Canvas(str(DRAW/'Metallteile_RevA.pdf'),pagesize=(W,H));c.setTitle('Fingerworker - Metallteile Rev A')
tmp=[]
for number,(name,title,q,material,notes) in enumerate(specs,1):
    frame(c,name.split('_')[0]+' - '+title,number,len(specs),material,q)
    shape=cq.importers.importStep(str(OUT/'step'/f'{name}.step')).val()
    for x,dr,label in [(45,(1,0,0),'Blick +X'),(310,(0,1,0),'Blick +Y'),(575,(0,0,1),'Blick +Z')]:tmp.append(view(c,shape,x,290,dr,label))
    text(c,40,262,'FERTIGUNG / DETAILMASSE',10)
    for i,note in enumerate(notes):text(c,40,241-i*17,note,9)
    c.showPage()
c.save()

c=canvas.Canvas(str(DRAW/'Elektronikaufnahme_RevA.pdf'),pagesize=(W,H));c.setTitle('Fingerworker - Elektronikaufnahme Rev A')
pages=[
('P08_Electronics_tray','Elektronikwanne',[
 'Huelle 22,5 x110 x8,1; Wand/Boden 1,0. Montageohren bis Y=+/-62; Oberkante Kragen Z=9,5.',
 '2x Montage D2,2 bei X=-26,5 / Y=+/-59. M2x6 von unten in P02, 2x M2-Einsatz Laenge 4.',
 '3x Deckel-Kernloch D1,25: (-43,2;18), (-43,2;50), (-26,5;50). M1,6x0,35 nachschneiden.',
 '2x Kabelklemme-Kernloch D1,25: X=-26,5 / Y=24 und 31. Ebenfalls M1,6x0,35.',
 'PCB-Unterseite Z=1,3; zwei Randauflagen, Endanschlaege mit 0,2 mm Spiel.',
 'Akkuauflage Z=1,3 plus 0,2 mm Isolierpad; Zelle nominal Z=1,5..5,3.',
 'USB-Oeffnung 13 x5,6; Taster seitlich direkt durch 8 x2,9 mm Zugang betaetigen.',
 'Kabelaustritt 13 x2,2 mm: isolierende Kanteneinlage, Kabel innen klemmen.']),
('P09_Electronics_lid','Abnehmbarer Deckel',[
 'Platte 22,5 x110 x0,8; drei D1,8 Durchgaenge mit 90-Grad-Senkung D3,0.',
 '3x M1,6x5 Senkschraube, Kopf D<=3,0; buendig halten (zur P02 nur 0,6 mm).',
 'PCB-Rippe Y=-27..-25: Fuss Z=2,15; 0,05 mm Isolierfolie am freien PCB-Korridor.',
 'Akku-Deckenrippe Z=6,6; nominal 1,3 mm Luft ueber Zelle; keine Vorspannung.',
 'Deckel mit flacher Aussenseite auf Druckbett, Rippen nach oben.']),
('P10_Wire_clamp','Kabelzugentlastung',[
 '3,2 x10,2 x1,0 mm; 2x D1,8 im Abstand 7,0; X=-26,5 / Y=24 und31.',
 '2x M1,6x3 Zylinder-/Linsenkopfschraube; maximal 1,3 mm Kopfhoehe.',
 'Kabelraum unter Klemme: Z=1,0..3,4, etwa 2,4 mm hoch; weiche isolierte Litzen.',
 'Duennen Silikonstreifen nach Kabelbuendel waehlen; Isolation nicht quetschen.',
 'Akku bleibt getrennt vom Klemmweg und muss mit geoeffnetem Deckel entnehmbar sein.']),
]
for number,(name,title,notes) in enumerate(pages,1):
    frame(c,name[:3]+' - '+title,number,4,'PETG, elektrisch isolierend',1)
    shape=cq.importers.importStep(str(OUT/'step'/f'{name}.step')).val()
    for x,dr,label in [(45,(1,0,0),'Blick +X'),(310,(0,1,0),'Blick +Y'),(575,(0,0,1),'Blick +Z')]:tmp.append(view(c,shape,x,290,dr,label))
    for i,note in enumerate(notes):text(c,40,253-i*18,note,9)
    c.showPage()
frame(c,'Montage / P02-Bohrbild / Druck',4,4,'P02 bestehend + PETG-Neuteile',1)
text(c,40,485,'P02 von UNTEN: zwei neue Insert-Sitze D3,2, Tiefe 4,0 ab Z=9,5.',12)
text(c,40,461,'Mittelpunkte X=-26,5 / Y=-59 und +59; 118,0 mm Achsabstand. Nicht durchbohren.',11)
text(c,40,439,'X: 3,25 mm ab innerer gerader Plattenkante X=-23,25; Y: je 5,00 mm ab Plattenenden.',10)
text(c,40,419,'Pilot an reales M2-Insert anpassen. Montage M2x6; Gewindeeingriff 3,5 mm.',10)
# Full scale one-axis mounting template, dimensioned (print 100%, verify scale bar).
cx=420; cy=335; mm=72/25.4
c.setLineWidth(.6);c.rect(cx-12*mm,cy-5*mm,24*mm,10*mm)
for xx in [cx-59*mm,cx+59*mm]:c.circle(xx,cy,1.6*mm);c.line(xx-8,cy,xx+8,cy);c.line(xx,cy-8,xx,cy+8)
dimh(c,cx-59*mm,cx+59*mm,cy-30,cy,'118,00 mm')
text(c,40,276,'Bohrschablone 1:1 fuer Y-Achse; X-Lage an P02-Unterseite separat anzeichnen.',9)
for i,s in enumerate([
 'Druck: PETG, 0,2 mm Schichten, 0,4 mm Duese, mindestens 3 Wandlinien; kleine Teile voll fuellen.',
 'Wanne Boden unten; Deckel Aussenflaeche unten; Klemme flach. Keine Stuetzen im Innenraum.',
 'Bohrungen nacharbeiten; Gewinde von Hand schneiden. Gehaeuse ist kein lasttragendes Teil.',
 'USB, Taster, Kabelisolation und Akku-Spiel am gelieferten Satz kontrollieren; nicht erzwingen.',
 'PCB-Klemmfolie nur im unbestueckten Korridor; Zelle weder kleben noch fest verspannen.',
 'Die Platine und der belastete Mechanismus bleiben unveraendert; nur P02 erhaelt zwei Blindloecher.'
]):text(c,40,251-i*19,s,9)
c.line(600,104,600+20*mm,104);c.line(600,100,600,108);c.line(600+20*mm,100,600+20*mm,108);text(c,600,115,'Kontrollmass 20 mm',8)
c.showPage();c.save()
for p in set(tmp):p.unlink(missing_ok=True)
# Render every page for visual QA; retain thumbnails in review directory.
review=OUT.parents[1]/'review/enclosure-2026-10-11';review.mkdir(parents=True,exist_ok=True)
for filename in ['Metallteile_RevA','Elektronikaufnahme_RevA']:
    doc=fitz.open(DRAW/(filename+'.pdf'))
    for i,page in enumerate(doc):page.get_pixmap(matrix=fitz.Matrix(1.2,1.2)).save(review/f'{filename}-{i+1:02}.png')
    print(filename,len(doc),'pages rendered')
