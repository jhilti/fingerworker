# Fingerworker — Einkauf und Montage, flache Revision

CAD-Revision: 20. September 2026, außenliegende Handballenrolle. Diese Liste ersetzt die MGN12-Ausführung. Vorherige Stückliste: `review/tall-open-palm-2026-09-05/EINKAUFSTEILE.md`. Preise und Verfügbarkeit wurden für diese Revision nicht geprüft.

## Gedruckte Teile

| Kennung | Anzahl | Teil |
|---|---:|---|
| P01 | 1 | Grundplatte 216 × 210 × 6 mm mit Führungen, Sensorstütze und Anschlagböcken |
| P02 | 1 | Starre äußere Handballenauflage mit zwei Befestigungslaschen |
| P03 | 1 | TPU-Manschette, 2,5 mm nominelle Wandstärke |
| P04 | 1 | Schlitten mit 20-mm-Klettermulde und seitlichen Federarmen |
| P05 | 1 | Verstärktes schwimmendes Federjoch |
| P060/P061 | 2 | Abnehmbare hintere Stabhalter und Schlitten-Rückhalter |
| P070a/b, P071a/b | 4 | TPU-Rücklaufpuffer, je 1,5 × 4,5 × 6 mm |

MGN12-Schienen, MGN12H-Wagen, hohe Montagewinkel und Abdeckungen entfallen. Führungs-Passprobe und Druckorientierung: `PRINTING.md`.

## Funktionsteile

- **2 × norelem 26000-1608102**: ISO-10243-Druckfeder, außen 16 / innen 8 / freie Länge 102 mm, nominell 7,8 N/mm. [Herstellerfamilie](https://www.norelem.de/en/Product-overview/Systems-and-components-for-machine-and-plant-construction/26000/Springs/c/21221). CAD-Einbaulänge 101 mm, bei 30 mm Hub noch 71 mm. Die lineare Rechnung ergibt zusammen 15,6 bis 483,6 N; das ist keine Belastungsfreigabe der Druckteile.
- **1 × TE FX1901-0001-0200-L**, 200-lbf-Druckkraftsensor, nominell Ø19,75 × 5,45 mm. [Hersteller](https://www.te.com/de/product-FX1901-0001-0200-L.html). Originaldatei: `vendor/te_fx1901/c-fx1901-0001-0200-l-f-3d.stp`. Die Stütze trägt den äußeren Rückenring; die Mitte ist 1,6 mm entlastet. Das Joch hat eine Ø20,4-mm-Ausnehmung und offene Kabelnut.
- **1 × Omron SS-01GL2**, Rollenhebelschalter für Mikrolast. [Herstellerdatenblatt](https://omronfs.omron.com/en_US/ecb/products/pdf/en-ss.pdf). Gehäuse 19,8 × 10,2 × 6,4 mm, Bohrungen Ø2,35 im 9,5-mm-Raster. Flach auf Z6 montiert. Ein einstellbarer M3-Schraubenkopf am Schlitten betätigt die Rolle. Den Klickpunkt am realen Schalter einstellen; die CAD-Hebelbahn ist angenähert.

Kraftmessverstärker, Mikrocontroller und Verkabelung bleiben außerhalb des mechanischen Aufbaus. Vorhandene MGN12-Herstellerdateien sind nur noch Archiv.

## Metallteile und Befestigung

| Anzahl | Teil | CAD-Maß / Verwendung |
|---:|---|---|
| 2 | Glatter Stahl-/Edelstahlstab | Ø6 × **206 mm**, aus längerem Stab ablängen, Enden entgraten |
| 4 | Stahl-Federsitz | Ø22 × 3 mm, Durchgang Ø6,6 mm |
| 1 | Planparalleler Stahl-Druckstift | Ø4 × **2,9 mm**, zwischen Sensorboss und Joch |
| 4 | M4×10 Zylinderkopfschraube | Handballenauflage, Kopfsitz Z13,5, nominell 6 mm Eingriff |
| 4 | M4-Gewindeeinsatz | Länge 6 mm, CAD-Pilot Ø5,2 |
| 4 | M3×8 Zylinderkopfschraube | Hintere Halter, Kopfsitz Z10, nominell 4 mm Eingriff |
| 4 | Kurzer M3-Gewindeeinsatz | Länge 4 mm, CAD-Pilot Ø4,2 |
| 2 | M4×10 Gewindestift mit flachem Ende | Mechanischer Endanschlag bei X86 |
| 2 | M4-Vierkantmutter | Nominell 7 × 7 × 3 mm, offene 7,2-mm-Muttertasche |
| 2 | M2×10 Schraube plus dünne Scheibe | Schalter; Eingriff mit realer Scheibe prüfen |
| 2 | Kurzer M2-Gewindeeinsatz | Länge 3 mm, CAD-Pilot Ø3,2 |
| 1 | M3×12 Zylinderkopfschraube | Klick-Nocken, Kopf Ø5,5 × 3 mm, Frontdatum X110 |
| 1 | M3-Gewindeeinsatz | Länge 4 mm, waagerecht im Nockenarm, CAD-Pilot Ø4,2 |
| nach Bedarf | M5-Schrauben oder Tischklemmen | Vier Ø5,5-mm-Befestigungsbohrungen |

Gewinde und Befestigungsschrauben sind teilweise nur durch ihre Aufnahmen dargestellt. Einsatz-Pilotdurchmesser sind Startmaße und müssen an die gekauften Einsätze angepasst werden. Puffer mit dünnem geeignetem Klebefilm sichern; Halt der weichen C-Manschette am Muster prüfen.

Für die Tischbefestigung bündige Senkschrauben verwenden und die Ø5,5-mm-Pilotbohrungen nach dem Druck passend ansenken. Besonders hinten dürfen Schraubenköpfe nicht über Z6 ragen, sonst behindern sie den Schlittenrücklauf. Alternativ die freie Grundplatte mit Tischklemmen befestigen.

## Montagefolge

1. Führungs-Passprobe drucken. Grundplatte und Schlitten zunächst ohne Federn über den ganzen Hub prüfen und Führungsflächen nacharbeiten.
2. Gewindeeinsätze setzen. Sensor am äußeren Rückenring anlegen, Kabel in die Nut führen, Druckstift zentrieren und Joch davor setzen.
3. Hintere Halter abnehmen. Schlitten von hinten aufschieben. Stäbe, Scheiben und Federn auffädeln; Stäbe in die vorderen Sacklöcher führen.
4. Rücklaufpuffer und hintere Halter montieren. Die Puffer definieren die offene Position, die Halter sichern Stäbe und Schlitten.
5. Handballenauflage und Manschette montieren. M4-Endanschläge einstellen. M3-Klick-Nocken nominell 1 mm vor dem 30-mm-Anschlag einstellen, etwa ±1 mm Einstellbereich.
6. Reibung, Rücklauf und Messsignal am gefertigten Aufbau prüfen, bevor die Federkraft erhöht wird. Die Druckkonstruktion hat noch keine experimentell bestätigte Traglast.

Elektronikvorschlag: siehe `BLUETOOTH.md` (BLE-Controller, Messwandler, Versorgung). Noch nicht im CAD eingebaut. Grundplatte, äußere Handballenauflage und vorgezogenen Griffschlitten gemeinsam aus der neuen Revision drucken. Die vier M4-Befestigungen der Auflage liegen bei X−15, Y−56/−45/+45/+56 mm. Vordere Befestigungslöcher der Grundplatte liegen jetzt bei Y±98 mm; Endanschläge bei Y±94 mm. Der Endschalter sitzt54 mm weiter hinten, seine Schraubengrößen bleiben gleich.
