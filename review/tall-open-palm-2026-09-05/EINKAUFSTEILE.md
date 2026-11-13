# Fingerworker MVP – Einkauf, Fertigung und Montage

CAD-Revision: 4. September 2026. Einkaufsangaben vom 30. August 2026; Preise und Lagerbestand bitte vor der Bestellung nochmals prüfen.

## Offene Mechanik mit gerundeter Handballen-Gegenauflage

- Vierfinger-Griffmulde: **94 × 34 × 20 mm**, Kontaktkante R4, Grundriss-Ecken R8, belastete Wand X137 mm und nominell **12 mm** Wandstärke.
- Die feste Handballenauflage ist jetzt eine querliegende Rundauflage. Ihre weiche Vorderfläche liegt bei **X37 mm**, ihre Krone bei **Z59,5 mm**, auf gleicher Höhe wie der Griffrahmen. Die nominellen X-Datumsabstände bleiben **100/70 mm** bei **30 mm Hub**.
- Runder Kern: Radius **7,75 mm**, Achse X26,75/Z49,25 mm, Länge 116 mm. Er ist mit einer 5-mm-Montageplatte X10..37/Y±64/Z39..44 mm zu einem Bauteil verbunden. Vier M4-Kopfsitze bei Z43 mm bleiben von oben zugänglich.
- Weiche C-förmige Manschette **P13**: Außen-Ø 20,5 mm, Innen-Ø 15,5 mm, Breite 86 mm, nominelle Wandstärke 2,5 mm. Ihre Unterkante liegt bei Z44,1 mm und hält 0,1 mm Abstand zur Montageplatte. Für ein Muster geeignetes Elastomer verwenden; Härte, Halt auf dem Kern und Hautgefühl am Muster abstimmen.
- Untere Gehäusewanne, feste Haube, Sichtfenster, bewegte Haube und zugehörige Befestigungsmerkmale sind entfernt. Das offene Gerät ist ohne Handreferenz **59,5 mm hoch**. Die freiliegende Grundplatte hat R3-Außenkanten.
- Feder-, Führungsstab- und Sensorachse bleiben bei Z25 mm; Führungsabstand 130 mm. Ø17,2-mm-Federkanäle und durchgehende Ø6,6-mm-Stabbohrungen bleiben erhalten.
- Vier Rücklaufanschläge mit Elastomerplättchen 6 × 9,5 × 1 mm definieren die offene Position. Mechanische Endanschläge, Stahlplatten und seitlich einstellbarer Endschalter bleiben im Modell.

Im Feature stehen **Preview displacement** (0–30 mm) und **Show hand reference** zur Verfügung. Für Einzelteilexport: Hub 0 mm, Hand aus. Die optionale Hand zeigt den Handballen vor der gerundeten Gegenauflage; sie ist eine vereinfachte Pose und von der Stückliste ausgeschlossen.

Die Datumsabstände sind keine anthropometrisch validierte Griffweite. Die Mulde und der gerundete Handballenkontakt sollen zunächst am Muster auf Passform und Oberflächengefühl geprüft werden.

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
Die Elektronik bleibt beim ersten mechanischen MVP bewusst extern:
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
- 4 × M4 Messing-Gewindeeinsatz, Außendurchmesser etwa 5,6 mm, Länge 6 mm
- 4 × M4×10 Zylinderkopfschraube für die gerundete Handballen-Gegenauflage
- 2 × M6 Messing-Gewindeeinsatz, Außendurchmesser höchstens 8,4 mm, Länge 8–10 mm
- 2 × M6×25 Einstellschraube plus Kontermutter für die mechanischen Anschläge
- 2 × M2,3×12 Schraube, Scheiben und Muttern für den Omron-Schalter
- 2 × Stahl-Anschlagplatte 8 × 13,5 × 2 mm, Kanten entgratet; angepasste Höhe für den flachen Muldenboden
- 4 × M5-Schraube beziehungsweise Tischklemme zur Befestigung des Geräts

Die Schraubenlängen sind auf die modellierten Kopfauflagen und Sacklochböden
abgestimmt: M3×8 an den Schienen ergibt nominell 5 mm Eingriff und 1,5 mm
Abstand zum Sacklochboden; M4×10 an der Handballenauflage 6 mm Eingriff und
1 mm Bodenabstand. Die M4-Kopfsitze bleiben bei Z43 mm; die Werkzeugschächte
reichen durch den runden Kern nach oben. Eingesetzte Gewindeeinsätze, tatsächliche
Schraubenlängen und Kopfgeometrie vor dem Anziehen am montierten Muster prüfen.
Die acht M3×10-Wagenschrauben bleiben über die seitlichen und inneren
Werkzeugöffnungen erreichbar.

## Druckempfehlung

- Lasttragende Teile: **PA-CF** bevorzugt; für erste Versuche PETG oder ASA.
- Kein PLA für wiederholte 500-N-Tests, warme Umgebung oder dauerhafte Federvorspannung.
- Düse 0,6 mm, mindestens 5 Außenwände, 6 obere/untere Schichten, 35–45 % Gyroid.
- Grundplatte flach drucken. Den Schlitten mit der Griffmulde nach oben ausrichten; die durchgehende Muldenwand leitet die Last direkt in die Brücke. Lokale Freistellungen für Anschläge, Federkanäle und Senkungen im Slicer prüfen und bei Bedarf mit entfernbaren Stützen versehen. Eine andere Druckorientierung erst anhand des Lastpfads und eines Musters festlegen. Die gerundete Gegenauflage mit der planen Montageplatte auf das Bett legen; die separate weiche Manschette und ihre Passung am Muster prüfen.
- Griffmulde und R4-Kante sorgfältig entgraten und glätten; keine scharfkantigen Schichtwechsel oder freiliegenden Fasern auf der Hautkontaktfläche belassen. Oberflächengefühl zuerst ohne Federn prüfen.
- Gewindeeinsätze erst nach dem vollständigen Abkühlen setzen und an Probeteilen kalibrieren.
- Führungsbohrungen nach dem Druck mit 6,2 beziehungsweise 6,6 mm aufreiben.
- Schienenauflagen leicht planschleifen; beide Schienen erst lose ausrichten, Wagen bewegen und dann kreuzweise anziehen.

## Sichere Erstinbetriebnahme

1. Ohne Federn prüfen, ob beide Wagen über den kompletten Weg frei laufen; insbesondere Federkanäle, durchgehende Stabbohrungen, Handballen-Gegenauflage und Rücklaufanschläge prüfen.
2. Endanschläge zunächst auf 10 mm Weg einstellen und den Schalter etwa 1 mm davor auslösen lassen.
3. Nur eine Feder montieren und Kraftmessung sowie freien Rücklauf prüfen.
4. Zweite Feder montieren und in 50-N-Schritten bis höchstens 500 N testen.
5. Nach jedem Schritt Grundplatte, Schlitten, Gewindeeinsätze und Anschlagplatten auf Risse oder Wandern prüfen.

Diese offene Revision ist ein mechanischer Prototyp. CAD-Prüfungen ersetzen
keine Messung von Halt, Reibung und Dauerfestigkeit am gefertigten Aufbau.

### Schalterlage der flachen Revision

Der Schalterkörper sitzt bei X=94 mm und Z=12 mm. Eine lokale Aussparung im
Montagefuß lässt Gehäuse und Hebelwurzel frei; die beiden seitlichen
Befestigungsschrauben behalten die volle Fußdicke. Die nominelle
Betätigungsposition liegt 1 mm vor dem 30-mm-Hartanschlag. Maßgeblich ist
die Bohrungsmittellinie als OP-Bezug im Omron-Datenblatt, nicht die
Gehäuseunterkante. Die Hebelbewegung im CAD ist eine schematische
Kontaktvorschau mit angenähertem Gelenk; den tatsächlichen Klickpunkt
am eingebauten Schalter über die Langlöcher einstellen.
