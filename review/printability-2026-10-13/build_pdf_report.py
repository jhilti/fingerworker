"""Create a concise illustrated printability review from verified Rev F artifacts."""
from pathlib import Path
import json
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate,Paragraph,Table,TableStyle,Image,Spacer,PageBreak,KeepTogether
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
ROOT=Path(__file__).resolve().parents[2];DATA=Path(__file__).resolve().parent
OUT=ROOT/'output/pdf/Fingerworker_Druckbarkeitspruefung_RevF_2026-10-13.pdf'
NATIVE=ROOT/'print/bambu-2026-10-13-RevF'
summary=json.loads((DATA/'printability-summary.json').read_text());validation=json.loads((NATIVE/'validation.json').read_text())
assert json.loads((DATA/'final-toolpath-validation.json').read_text())['status']=='PASS'
assert json.loads((DATA/'final-support-validation.json').read_text())['status']=='PASS'
pdfmetrics.registerFont(TTFont('Arial','/System/Library/Fonts/Supplemental/Arial.ttf'))
pdfmetrics.registerFont(TTFont('ArialBold','/System/Library/Fonts/Supplemental/Arial Bold.ttf'))
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='FWTitle',fontName='ArialBold',fontSize=23,leading=27,textColor=colors.HexColor('#15364b'),spaceAfter=12))
styles.add(ParagraphStyle(name='FWHeading',fontName='ArialBold',fontSize=14,leading=18,textColor=colors.HexColor('#15364b'),spaceBefore=8,spaceAfter=8))
styles.add(ParagraphStyle(name='FWBody',fontName='Arial',fontSize=10,leading=14,textColor=colors.HexColor('#263c4a'),spaceAfter=8))
styles.add(ParagraphStyle(name='FWCell',fontName='Arial',fontSize=8,leading=10.2,textColor=colors.HexColor('#263c4a')))
styles.add(ParagraphStyle(name='FWCellHead',fontName='ArialBold',fontSize=8,leading=10.2,textColor=colors.white))
styles.add(ParagraphStyle(name='FWCaption',fontName='Arial',fontSize=8,leading=10.5,textColor=colors.HexColor('#4e6473'),spaceAfter=6))
def P(s,style='FWBody'):return Paragraph(s,styles[style])
def heading(s):return P(s,'FWHeading')
def footer(c,doc):
    c.saveState();c.setStrokeColor(colors.HexColor('#d5e0e6'));c.line(42,32,A4[0]-42,32)
    c.setFont('Arial',8);c.setFillColor(colors.HexColor('#526879'))
    c.drawString(42,20,'Fingerworker | H2D / PETG / 0,4 mm | Rev F | 13.10.2026')
    c.drawRightString(A4[0]-42,20,f'Seite {doc.page}');c.restoreState()
def table(rows,widths,header=True):
    t=Table(rows,colWidths=widths,repeatRows=1 if header else 0,hAlign='LEFT')
    cmds=[('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),('LINEBELOW',(0,0),(-1,-1),.4,colors.HexColor('#d7e3e9'))]
    if header:cmds+=[('BACKGROUND',(0,0),(-1,0),colors.HexColor('#15364b')),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#f1f5f7')])]
    t.setStyle(TableStyle(cmds));return t
story=[P('Druckbarkeitsprüfung','FWTitle'),P('Rev F - kompletter Form- und Montageprototyp'),P('25 Geräteteiltypen + 2 Passproben | 32 Exemplare | 6 Druckplatten','FWCaption')]
minutes=validation['estimated_total_seconds']//60;grams=validation['estimated_total_grams']
statrows=[[P('DRUCKER / MATERIAL','FWCellHead'),P('PRÜFUNG','FWCellHead'),P('SLICER-SCHÄTZUNG','FWCellHead')],
          [P('H2D, Standarddüsen 0,4 mm<br/>PETG, Textured PEI','FWCell'),P('Alle 32 Objekte mit echten Bahnen<br/>Alle 6 Platten erfolgreich','FWCell'),P(f'{minutes//60} h {minutes%60:02d} min / {grams:.0f} g<br/>inkl. Stützen, Brims und Passproben','FWCell')]]
story += [table(statrows,[170,171,170]),Spacer(1,9),heading('Die wesentlichen Korrekturen')]
for text in [
 'P04-Griff und P05-Federjoch: Rückseite aufs Bett. Führung und Stabbohrungen werden aufrecht gedruckt; Stützen berühren die Passflächen weniger.',
 'H12-Sensorkassette seitlich, H02-Druckstift aufrecht. P08-USB-Dach jetzt mit zugänglichen Stützen unterlegt.',
 'Hohe Schalen mit 8-mm-Brim. Kleine Teile mit maximal 40 mm/s; Schalen/Hülsen mit maximal 60 mm/s. Modellbeschleunigung höchstens 1500 mm/s².',
 'Vier P07-Formpuffer: nur diese Objekte mit 0,1-mm-Schichten. Reale Druckpfade enden bei Z1,50 mm statt zuvor 1,40 mm.'
]:story.append(P('• '+text))
story += [Image(str(NATIVE/'preview/alle-sechs-platten.png'),width=511,height=368),P('Native Bambu-Studio-Vorschauen der endgültigen sechs Platten. Die Nennform der Teile bleibt erhalten; vier STLs sind ausschließlich starr gedreht.','FWCaption'),
          P('Die Prüfung gilt für den <b>federfreien Erstaufbau</b>. Sie belegt Geometrie, Ausrichtung, erreichbare Stützen und die erzeugten Bahnen. Reale Haftung, Passung und Supportablösung müssen am gedruckten Muster bestätigt werden.','FWCaption'),PageBreak()]
story += [heading('Stützen entfernen und Passflächen schonen'),P('Die neue Orientierung ist in den STLs und im 3MF bereits gespeichert. Nicht automatisch neu ausrichten. Stützen und Brims vollständig entfernen, bevor der Griff eingeschoben wird.')]
images=[Image(str(DATA/'critical/orientation-1.png'),width=242,height=242),Image(str(DATA/'critical/orientation-3.png'),width=242,height=242)]
t=Table([images,[P('<b>P04: hintere Stirnseite unten.</b><br/>Bohrungen und Längsführung laufen aufrecht. Die breite ursprüngliche Kanaldecke entfällt.','FWCaption'),P('<b>P05: hintere Rippe unten.</b><br/>Nur Bettstützen: beide Schultern unterstützt, Druckstift- und Führungsbohrungen stützenfrei.','FWCaption')]],colWidths=[255.5,255.5]);t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),3),('RIGHTPADDING',(0,0),(-1,-1),9)]));story += [t,Spacer(1,6)]
cleanup=[
 ('P04-Griff','Stützen durch die große seitliche Griffmulde lösen. Kleine Stützen an den Querabsätzen der Führung durch deren offene Unterseite entnehmen. Die langen Gleitseiten und senkrechten Bohrungen benötigen keine Innenstützen.'),
 ('P05-Federjoch','Die beiden äußeren Schulterstützen abnehmen. Die seitlich offene 5,7-mm-Muttertasche wird kurz überbrückt. Keine Stützen aus der Druckstiftbohrung bohren: das gewählte Bettstützen-Profil hält diese frei.'),
 ('P08-Elektronikwanne','Stützen unter Montageohren und USB-Dach entfernen. Der USB-Bereich hat jetzt 65 echte Supportbahnen einschließlich Kontaktlagen. Zugang über offene Wanne/Port; dünne 0,3-mm-PCB-Stoppkanten schonen.'),
 ('H12 / H02','H12-Stützen aus der seitlich offenen, nur 1,6 mm tiefen Sensortasche abnehmen. H02-Schulterstützen liegen außen frei erreichbar. Diese H-Teile besitzen keine funktionsfähigen gedruckten Gewinde.'),
 ('Brims und Kleinteile','H19 und H22 mit dem Haftungsrand von der abgekühlten Platte nehmen, dann den Rand vorsichtig von außen abtrennen. Ringbohrungen frei halten. Die Halbschalen mit breitem Brim abnehmen und erst außerhalb des Geräts an P02 anlegen.')]
for title,text in cleanup:story += [P('<b>'+title+'</b> - '+text)]
story += [P('Die unveränderten nominalen Montagewege bleiben gültig. Die endgültigen Druckkörper sind geschlossen; eine Rücktransformation bestätigt die unveränderten Schnittstellen. Die neue Lagenrichtung von P04 ist für die Formbeurteilung gewählt. Eine spätere Version unter Federlast benötigt eine eigene Festigkeitsentscheidung.','FWCaption'),PageBreak()]
def matrix(rows):
    vals=[[P(k,'FWCellHead') for k in ['Teil','Stk','Drucklage','Stützen / Haftung','Prüfung / Nacharbeit']]]
    for r in rows:
        label={'CouponMale':'Probe<br/>männlich','CouponFemale':'Probe<br/>weiblich'}.get(r['part'],r['part'])
        vals.append([P('<b>'+label+'</b>','FWCell'),P(str(r['quantity']),'FWCell'),P(r['orientation'],'FWCell'),P(r['support'],'FWCell'),P(r['note'],'FWCell')])
    return table(vals,[48,26,107,112,218])
story += [heading('Prüfung je Teil - Mechanik und Gehäuse'),P('Jede STL enthält ein Exemplar. Stückzahlen sind bereits im 3MF berücksichtigt. „Bett“ bedeutet, dass die Stützen ausschließlich vom Druckbett starten.','FWCaption'),matrix(summary['decisions'][:15]),PageBreak()]
story += [heading('Prüfung je Teil - Anschauungsteile und Proben'),matrix(summary['decisions'][15:]),Spacer(1,8),
          P('<b>Qualitätsprofil:</b> 0,20-mm-Schichten, 4 Wände, 5 Boden-/Deckschichten, 30 % Gyroid. H-Anschauungsteile und Passproben voll gefüllt. Erste Schicht 20 mm/s; kurze Brücken 25 mm/s. P07 lokal 0,10 mm. Die unverändert dimensionierten Passproben aus Rev E bleiben passend.','FWCaption'),
          P('<b>Grenzen:</b> 0,20-mm-Schichtung kann Gesamthöhen um etwa 0,10 mm runden. H-Teile bleiben Anschauungsformen. Harte PETG/PLA-Puffer dämpfen nicht wie Elastomer. Schrauben, Muttern, Inserts, Sensor, Federn und Elektronik werden nicht gedruckt.','FWCaption'),
          P('<b>Bewertungsgrundlage:</b> Geschlossene Quellnetze, vergleichende Orientierungsstudien, die wirklichen Stützbahnen und der offizielle H2D-Slicer. Bridge-Tags umfassen auch Bahnen über innerer Füllung oder Support; ihre Länge ist nicht gleich einer freien Luftspannweite. Allgemeine Konstruktionsprinzipien: <link href="https://help.prusa3d.com/article/modeling-with-3d-printing-in-mind_164135" color="#226b90"><u>Prusa - Modeling with 3D printing in mind</u></link>.','FWCaption'),
          P('<b>Prüfnachweise im Paket:</b> validation.json, stl-validation.json, toolpath-validation.json, support-validation.json und PRINTABILITY.md. Das 3MF ist ein editierbares Projekt; Prüf-G-Code wird nicht ausgeliefert.','FWCaption')]
doc=SimpleDocTemplate(str(OUT),pagesize=A4,leftMargin=42,rightMargin=42,topMargin=38,bottomMargin=44,title='Fingerworker Druckbarkeitsprüfung Rev F',author='Fingerworker')
doc.build(story,onFirstPage=footer,onLaterPages=footer)
print(OUT)
