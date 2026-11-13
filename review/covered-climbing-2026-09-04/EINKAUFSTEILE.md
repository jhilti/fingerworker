# Fingerworker MVP – Einkauf, Fertigung und Montage

CAD-Revision: 4. September 2026. Einkaufsangaben vom 30. August 2026; Preise und Lagerbestand bitte vor der Bestellung nochmals prüfen.

## Flache Griffmulde und Bewegungsrevision

- Versenkte Vierfinger-Griffmulde nach dem Prinzip einer Klettergriff-Tasche: nominell **94 mm breit × 34 mm lang × 20 mm tief**, mit R4 an der gerundeten Griffkante und R8 in den Ecken des Grundrisses. Die belastete innere Vorderwand liegt in Ruhestellung bei **X=137 mm**; ihre Wandstärke beträgt nominell 10 mm. Die Mulde ist Teil des tragenden Schlittens.
- 100 mm nominelle lichte Weite zwischen Auflagen-Datum X=37 mm und belasteter Muldenwand in Ruhestellung, 70 mm bei 30 mm Hub. Führungsabstand: 130 mm.
- Oberkante von Griffdeck und bewegter Haube: **Z=59,5 mm**; Muldenboden: **Z=39,5 mm**. Mit der unteren Gehäusekante bei Z=−4 mm beträgt die Gerätehöhe ohne Handreferenz **63,5 mm**, rund **31 % weniger** als die vorherige 92-mm-Revision mit erhöhtem Griff.
- Feder-, Führungsstab- und Sensorachse liegen bei **Z=25 mm**, also 6 mm tiefer als zuvor. Die Federsitze und Durchführungen folgen dieser Achse.
- Auflagefüße bis **Z=39 mm**; abnehmbare Handballenauflage **8 mm dick**, Oberkante **Z=47 mm**. Mit der weichen Kontaktauflage liegt die obere Kontaktfläche bei **Z=49,5 mm**. Zur Sensorwand bleibt 1 mm Abstand; die Füße enden hinten bei X=39 mm, damit der Sensorstecker frei liegt.
- Neue separate Kontaktauflage **P13**, 19 × 86 × 2,5 mm, abgerundete Kanten. Für den Prototyp als weichen Elastomerstreifen fertigen und mit dünner geeigneter Klebeschicht auf der planen Fläche befestigen; Härte und Oberflächengefühl am Muster bestimmen. Die seitlichen Schrauben bleiben erreichbar.
- Zwei Ø17,2-mm-Federkanäle in der Brücke und bis durch deren Rückseite geführte Ø6,6-mm-Stabbohrungen beseitigen die zuvor vorhandenen Materialüberschneidungen.
- Feste und bewegte Haube überlappen nominell schon in Ruhestellung um 9 mm. Die Aussparung der bewegten Haube folgt dem flachen Griffdeck mit 0,6 mm nominellem umlaufendem Abstand. Vier Haubenstützen sitzen bei X=146/188 mm und Y=±72 mm außerhalb der Griffmulde; sie reichen von der Brückenoberseite Z=43 mm bis Z=59,5 mm.
- Vier feste Rücklaufanschläge mit **vier Elastomerplättchen 6 × 9,5 × 1 mm (H22)** definieren die offene Position und dämpfen den Rücklauf. Plättchen vollflächig befestigen; Klebeschicht/Kompression bei der Endmontage berücksichtigen. Die bewegte Haube hat passende untere Freistellungen.
- Endschalter-Befestigung seitlich zugänglich; Schraubenköpfe liegen nicht mehr unter dem Schalterkörper.

Im Feature stehen **Preview displacement** (0–30 mm) und **Show hand reference** zur Verfügung. Für Fertigung und Einzelteilexport: Vorschauhub **0 mm**, Hand **aus**. Die Hand ist eine vereinfachte Griffdarstellung und von der Stückliste ausgeschlossen. Sie ist kein Nachweis für Passform, Kräfte oder eine bestimmte Handgröße.

Der 100/70-mm-Wert bezeichnet die X-Datumsflächen der festen Auflage und der belasteten inneren Muldenwand. Die weiche obere Kontaktfläche und die Handpose definieren keine zusätzliche anthropometrisch validierte Griffweite. Tiefe, Kantenradius und Hautgefühl der Mulde müssen am unbelasteten Muster geprüft werden.

## Einkaufsteile

### Linearführungen

- 2 × **DOLD MGN12R-200**, Schiene 12 × 8 × 200 mm
- 2 × **DOLD MGN12H**, langer Wagen 45,4 × 27 × 13 mm, Gewinderaster 20 × 20 mm
- Produkt Schiene: https://www.dold-mechatronik.de/Linearfuehrung-MGN12R-200mm
- Produkt Wagen: https://www.dold-mechatronik.de/Linearwagen-MGN12H
- Datenblatt: https://www.dold-mechatronik.de/documents/Datenblaetter/Linearfuehrungen/Datenblatt_MGN_MGW_Profilschienenfuehrungen_de.pdf
- Lokale Hersteller-CAD-Dateien: `vendor/dold/MGN12_Rail.step` und `vendor/dold/MGN12H.step`

Das Modell verwendet 130 mm Schienenabstand. Dadurch bleiben an der gedruckten
Brücke rund um die M3-Senkungen mindestens 4,3 mm Material. Die Schienen werden
mit 16 M3-Schrauben in Messing-Gewindeeinsätze der Grundplatte geschraubt; die
Wagen mit acht M3-Schrauben von oben an die Brücke.

### Federn und Führung

- 2 × **norelem 26000-1608102**, ISO 10243, leichte Last
- Außen-Ø 16 mm, Innen-Ø 8 mm, freie Länge 102 mm, Federrate 7,8 N/mm
- Herstellerwerte: 199 N bei 26 mm, 239 N bei 31 mm und höchstens 318 N bei 41 mm Federweg
- Produktfamilie: https://www.norelem.de/en/Product-overview/Systems-and-components-for-machine-and-plant-construction/26000/Springs/c/21221
- Konfigurierbares Hersteller-CAD: https://www.traceparts.com/fr/product/norelem-ressorts-de-compression-helicoidaux-iso-10243?CatalogPath=NORELEM%3A2025_21221&Product=27-05017477-211498
- 2 × geschliffener Edelstahlstab Ø 6 × 126 mm, aus 130-mm-Stäben ablängen
- 4 × gehärtete Federscheibe/Sitzscheibe Ø 22 × 3 mm mit Bohrung mindestens Ø 6,5 mm

Im CAD sind die Federn auf 101 mm vorgespannt. Nach 30 mm Arbeitsweg liefern
beide zusammen rechnerisch 483,6 N, also rund 49,3 kgf. Der Gesamtfederweg von
31 mm entspricht dem vom Hersteller angegebenen mittleren Arbeitspunkt. Die
Führungsstäbe sitzen links in integrierten
6,2-mm-Aufnahmen und laufen durch 6,6-mm-Bohrungen in Anker und Brücke.

Die nominelle lichte Weite zwischen Handballenauflage und belasteter Muldenwand beträgt
damit 100 mm in Ruhestellung und 70 mm am mechanischen Endanschlag.

### Kraftmessung

- 1 × **TE Connectivity FX1901-0001-0200-L**
- Druckkraft-Wägezelle, 0–200 lbf = 0–889,6 N
- Sensorkörper laut Herstellerzeichnung Ø 19,75 mm, 5,45 mm dick
- Produkt/Hersteller-CAD: https://www.te.com/de/product-FX1901-0001-0200-L.html
- RS Schweiz: https://ch.rs-online.com/web/p/dehnungsmessstreifen/2006113
- Lokales Original-STEP: `vendor/te_fx1901/c-fx1901-0001-0200-l-f-3d.stp`
- 1 × Stahl-Pusher Ø 4 mm, planparallel und entgratet

Die Aufnahme trägt die Rückseite nur am äußeren Ring; eine mittige Entlastung
hält die vier rückseitigen Erhebungen frei. Der Pusher belastet ausschließlich
den mittleren Sensorboss. Die Wägezelle nicht einpressen oder am Kabel abstützen.

Für die Auswertung ist ein **NAU7802**-Board geeignet, zum Beispiel SparkFun
Qwiic Scale SEN-15242: https://www.sparkfun.com/sparkfun-qwiic-scale-nau7802.html
Die Elektronik bleibt beim ersten mechanischen MVP bewusst außerhalb der Hülle:
Für dieses Board ist keine verlässliche mechanische Herstellerzeichnung mit
Lochbild verfügbar. Nach Wahl des tatsächlich gekauften Boards folgt ein eigener
kleiner Elektronikträger statt ungesicherter Fantasie-Bohrungen im Hauptteil.

### Endschalter

- 1 × **Omron SS-01GL2**, SPDT, Mikrolast, Rollenhebel, Lötanschlüsse
- 0,49 N maximale Betätigungskraft; mindestens 1,2 mm Nachlauf
- Gehäuse 19,8 × 10,2 × 6,4 mm; 2 × Ø 2,35 mm im Raster 9,5 mm
- Farnell Schweiz, Bestellnummer 1829515: https://ch.farnell.com/en-CH/omron/ss-01gl2/microswitch-spdt-roller-30vdc/dp/1829515
- Herstellerdatenblatt: https://omronfs.omron.com/en_US/ecb/products/pdf/en-ss.pdf

Der gedruckte Winkel ist mit zwei M3-Langlöchern um ±2 mm einstellbar. Schalter
mit M2,3-Schrauben, Unterlegscheiben und 0,23–0,26 Nm montieren. SS-01GL2 ist für
einen Mikrocontroller-Eingang geeigneter als SS-5GL2 mit Leistungskontakten.

### Schrauben, Einsätze und Metallteile

- 18 × M3 Messing-Gewindeeinsatz, Außendurchmesser etwa 4,6 mm, Länge 5–6 mm
- 16 × M3×8 Zylinderkopfschraube für die beiden Schienen
- 8 × M3×10 Zylinderkopfschraube für die beiden MGN12H-Wagen
- 2 × M3×8 Schraube für den einstellbaren Schalterwinkel
- 12 × M4 Messing-Gewindeeinsatz, Außendurchmesser etwa 5,6 mm, Länge 6 mm
- 4 × M4×10 Zylinderkopfschraube für die 8-mm-Handballenauflage
- 4 × M4×10 Schraube plus Scheibe für die feste Haube
- 4 × M4×18 Zylinderkopfschraube für die bewegte Haube
- 2 × M6 Messing-Gewindeeinsatz, Außendurchmesser höchstens 8,4 mm, Länge 8–10 mm
- 2 × M6×25 Einstellschraube plus Kontermutter für die mechanischen Anschläge
- 2 × M2,3×12 Schraube, Scheiben und Muttern für den Omron-Schalter
- 2 × Stahl-Anschlagplatte 8 × 13,5 × 2 mm, Kanten entgratet; angepasste Höhe für den flachen Muldenboden
- 4 × M5-Schraube beziehungsweise Tischklemme zur Befestigung des Geräts
- 1 × klares PETG- oder Polycarbonat-Fenster 45 × 92 × 1,5 mm

Die Schraubenlängen sind auf die modellierten Kopfauflagen und Sacklochböden
abgestimmt: M3×8 an den Schienen ergibt nominell 5 mm Eingriff und 1,5 mm
Abstand zum Sacklochboden; M4×10 an der Handballenauflage 6 mm Eingriff und
1 mm Bodenabstand. An der bewegten Haube liegt die Kopfauflage bei Z=55,5 mm:
M4×18 ergibt 5,5 mm Eingriff und 1 mm Bodenabstand. M4×20 würde dort am
modellierten Sacklochboden anstehen. Eingesetzte Gewindeeinsätze, tatsächliche
Schraubenlängen und Kopfgeometrie vor dem Anziehen am montierten Muster prüfen.
Die acht M3×10-Wagenschrauben bleiben über die seitlichen und inneren
Werkzeugöffnungen erreichbar.

## Druckempfehlung

- Lasttragende Teile: **PA-CF** bevorzugt; für erste Versuche PETG oder ASA.
- Kein PLA für wiederholte 500-N-Tests, warme Umgebung oder dauerhafte Federvorspannung.
- Düse 0,6 mm, mindestens 5 Außenwände, 6 obere/untere Schichten, 35–45 % Gyroid.
- Grundplatte flach drucken. Den Schlitten mit der Griffmulde nach oben ausrichten; die durchgehende Muldenwand leitet die Last direkt in die Brücke. Lokale Freistellungen für Anschläge, Federkanäle und Senkungen im Slicer prüfen und bei Bedarf mit entfernbaren Stützen versehen. Eine andere Druckorientierung erst anhand des Lastpfads und eines Musters festlegen. Hauben mit offener Seite auf das Bett; Innenstützen und Überhänge im Slicer kontrollieren.
- Griffmulde und R4-Kante sorgfältig entgraten und glätten; keine scharfkantigen Schichtwechsel oder freiliegenden Fasern auf der Hautkontaktfläche belassen. Oberflächengefühl zuerst ohne Federn prüfen.
- Gewindeeinsätze erst nach dem vollständigen Abkühlen setzen und an Probeteilen kalibrieren.
- Führungsbohrungen nach dem Druck mit 6,2 beziehungsweise 6,6 mm aufreiben.
- Schienenauflagen leicht planschleifen; beide Schienen erst lose ausrichten, Wagen bewegen und dann kreuzweise anziehen.

## Sichere Erstinbetriebnahme

1. Ohne Federn prüfen, ob beide Wagen über den kompletten Weg frei laufen; insbesondere Federkanäle, durchgehende Stabbohrungen, Haubenüberlappung und Rücklaufanschläge prüfen.
2. Endanschläge zunächst auf 10 mm Weg einstellen und den Schalter etwa 1 mm davor auslösen lassen.
3. Nur eine Feder montieren und Kraftmessung sowie freien Rücklauf prüfen.
4. Zweite Feder montieren und in 50-N-Schritten bis höchstens 500 N testen.
5. Nach jedem Schritt Grundplatte, Schlitten, Gewindeeinsätze und Anschlagplatten auf Risse oder Wandern prüfen.

Das MVP ist ein Prototyp, keine geprüfte Trainings- oder Medizinmaschine. Vor
Belastung am Menschen muss der Aufbau am Tisch fixiert und mit einer Schutzhaube
betrieben werden.

### Schalterlage der flachen Revision

Der Schalterkörper sitzt bei X=94 mm und Z=12 mm. Eine lokale Aussparung im
Montagefuß lässt Gehäuse und Hebelwurzel frei; die beiden seitlichen
Befestigungsschrauben behalten die volle Fußdicke. Die nominelle
Betätigungsposition liegt 1 mm vor dem 30-mm-Hartanschlag. Maßgeblich ist
die Bohrungsmittellinie als OP-Bezug im Omron-Datenblatt, nicht die
Gehäuseunterkante. Die Hebelbewegung im CAD ist eine schematische
Kontaktvorschau mit angenähertem Gelenk; den tatsächlichen Klickpunkt
am eingebauten Schalter über die Langlöcher einstellen.
