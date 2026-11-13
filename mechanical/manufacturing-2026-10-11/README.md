# Elektronikaufnahme und Metallteile – Prototyp Rev A

Stand 11.10.2026. Dieser Satz enthält drei neue druckbare Gehäuseteile, elf Metallteil-Zeichnungsblätter und die zugehörigen STEP-Körper. Konstruktion und nominale Einbauprüfung sind abgeschlossen; der erste gefertigte Satz benötigt Passprobe und die bestehende Hardware-Abnahme. Eine Traglast ist damit nicht freigegeben.

![Elektronikwanne im geprüften Onshape-Modell](enclosure-onshape.jpg)

## Dateien

- [Metallzeichnungen, 11 Blätter](drawings/Metallteile_RevA.pdf): Druckstift, Führungsstab, beide Federsitztypen, Vorspannungsmutter, Sensorkassette, Einsteller, Halteplatte, Abstandshülse, Messingdruckstück und optionale Isometriehülse. Material, Menge, Gewinde, Funktionsmaße, Oberflächen und Toleranzen stehen pro Blatt.
- [Elektronikaufnahme, 4 Blätter](drawings/Elektronikaufnahme_RevA.pdf): Wanne, Deckel, Kabelklemme, P02-Bohrbild und Montage.
- [STEP-Einzelteile](step/) und [bestückte Referenzbaugruppe](step/Electronics_assembled.step), in den Einbaukoordinaten des Haupt-CAD.
- [Druck-STLs](stl/), bereits flach und in Druckrichtung ausgerichtet, jeweils ein Teil pro Datei. Je einmal P08, P09, P10 drucken. Der neue P02-STL enthält die Montagepiloten; alternativ vorhandenes P02 nach Bohrbild nacharbeiten. PCB-/Akku-Hüllkörper nicht drucken.
- [Nominale BRep-/Einbauprüfung](validation.json), [gemeinsames Geometrie-Ledger](source/operation-ledger.json), [reproduzierbare Quelle](source/build_models.py).

## Montage und zusätzliche Kaufteile

| Menge | Teil |
|---:|---|
| 2 | M2×6-Zylinder-/Linsenkopfschraube, Kopf maximal Ø4 × 2 mm |
| 2 | M2-Gewindeeinsatz, Länge 4 mm, zum nominalen Ø3,2-Pilot passend |
| 3 | M1,6×5-Senkschraube, 90°, Kopf maximal Ø3 mm, bündig |
| 2 | M1,6×3-Zylinder-/Linsenkopfschraube, Kopf maximal Ø3 × 1,3 mm |
| 1 Zuschnitt | 0,2-mm elektrisch isolierendes Akku-Unterlagepad, 11,5 × 31 mm |
| 1 Zuschnitt | 0,05-mm elektrisch isolierende Folie am PCB-Klemmkorridor |
| nach Bedarf | Weiche isolierende Einlage für Kabelklemme und Kabelausgang |

1. P08/P09/P10 aus PETG drucken: 0,2-mm-Schichten, 0,4-mm-Düse, mindestens drei Wandlinien; schmale Bereiche vollständig füllen. Wanne mit Boden nach unten; Deckel mit flacher Außenseite nach unten; Klemme flach. Keine Stützen im Innenraum. Ø1,25-Piloten nacharbeiten und M1,6×0,35 von Hand schneiden.
2. P02 erhält zwei **Blindlöcher Ø3,2 × 4 mm** von unten, Mittelpunkte **X−26,5 / Y±59 mm**, Eintritt Z9,5, Ende Z13,5. Das entspricht 3,25 mm von der inneren geraden Plattenkante X−23,25 und je 5 mm von den Plattenenden Y±64. Der Haupt-FeatureScript enthält diese Änderung. Bestehendes P02 darf mit Tiefenanschlag und dem Bohrbild nachgearbeitet werden; nicht durchbohren. Pilot an tatsächliches Insertfabrikat anpassen. Der mitgelieferte neue P02-STL enthält die Löcher; der alte Drucksatz vom September enthält sie nicht.
3. PCB auf die Randauflagen setzen, Unterseite Z1,3. Der Halter nutzt keine Platinenbohrungen. Die Deckelrippe greift ausschließlich über dem im gespeicherten Bestückungsledger freien Korridor Y−27…−25; dünne Folie isoliert und schließt den nominalen 0,05-mm-Spalt. Bei überstehender Lötung keinen Deckel erzwingen.
4. Akku auf isolierende 0,2-mm-Unterlage legen. Seiten- und Endführungen lassen Spiel; oberhalb der nominalen Zelle bleiben zur Deckenrippe 1,3 mm. Der Akku wird weder von der Kabelklemme gehalten noch fest verspannt. Bei verändertem Zellmaß/Wölbung keinen Deckel schließen.
5. Sensor-/Schalterleitungen innen getrennt vom Akku führen, unter P10 mit weicher Einlage klemmen und durch den erhöhten seitlichen Schlitz führen. Kabelisolation erhalten; keine Zuglast an PCB-Lötstellen. Die Zugentlastung muss beim realen Kabelbaum auf Halt geprüft werden.
6. Deckel mit den drei bündigen Senkschrauben montieren. Wanne von unten mit M2×6 an P02 anschrauben; nomineller Insert-Gewindeeingriff 3,5 mm. Keine zusätzliche Schraube am Kraftpfad.

Für Service zuerst die beiden M2-Schrauben von unten lösen und die Wanne abnehmen; erst dann sind die Deckelschrauben von oben zugänglich.

USB ist von hinten zugänglich. Der seitliche Panasonic-Taster wird direkt durch die Gehäuseöffnung mit Fingernagel oder stumpfem Stift betätigt; ein ungeprüfter separater Betätigungsstößel ist nicht erforderlich. Kein metallischer oder scharfer Stift auf die Platine drücken.

## Zeichnungsregeln

Alle Maße in mm, Ansichten ausdrücklich mit Blickrichtung gekennzeichnet und zum Blatt eingepasst; ausschließlich das Bohrbild auf Blatt 4 der Elektronikzeichnung ist 1:1. Vor Verwendung der Schablone das 20-mm-Kontrollmaß prüfen. Fertigungsmaße und Gewindeangaben auf dem Blatt haben Vorrang vor glatten STEP-Gewindehüllkörpern. H11/H12-STEP zeigt Kernlöcher, H02/H13 Außengewinde als volle Zylinder. Auf dem Papier steht das fertig zu schneidende Gewinde.

H12 wird einteilig gefräst; die Ohren sind Teil des Körpers. H15 enthält die Teilkreis-Freistellung für den Klemmkopf, die bei bloßem Rechteckzuschnitt fehlen würde. H02 besitzt eine fertige 1,90-mm-Kontaktlänge ab Schulter und keine CAD-Überlappungszugabe.

Standard-Schrauben, Vierkantmuttern und Gewindeeinsätze bleiben Kaufteile aus der [Gesamtstückliste](../../EINKAUFSTEILE.md). Die Material- und Toleranzangaben definieren den Prototypsatz, ersetzen jedoch keine Belastungsqualifikation.

## Nachweise und Reproduktion

Lokales CadQuery-Modell: 14 gültige Einzelkörper; zusätzlich ein gültiger P02-Körper aus dem Live-Onshape-STEP mit geprüften Pilotlöchern und verbleibendem Dach. drei Gehäuse-Paarprüfungen und 156 Vergleiche gegen gespeicherte Komponenten-, PCB-, Akku-, Stecker- und USB-Hüllkörper ohne positive Volumenüberschneidung. Frische Onshape-Prüfung: [14 Konfigurationen und 630 Gruppenprüfungen](../../review/enclosure-2026-10-11/cad-validation.json) ohne Volumeninterferenzen; 194 Kontaktbefunde bleiben REVIEW. Gehäuseauflagen und Schraubverbindungen haben beabsichtigte Kontakte. Hüllkörper sind konservative Nennmaße; Passprobe, realer Kabelweg und Funk-/Temperaturprüfung bleiben am Muster erforderlich.

Mit Python 3.12, CadQuery 2.8.0, ReportLab 5.0.1, svglib 2.3.0 und PyMuPDF 1.28.2:

```bash
python source/build_models.py
python source/integrate_featurescript.py
python source/drawings.py
```

P02 ist separat aus dem geprüften Live-Onshape-Modell exportiert; `p02-export-validation.json` prüft seine beiden Blindlöcher und das verbleibende Dach. Die Python-Buildquelle erzeugt P08/P09/P10 und die elf Metallteile. Nach Änderungen an P02 muss der Onshape-Export erneut erstellt werden.

Build-Quelle und Operation-Ledger erzeugen beide Gehäusefassungen (CadQuery und FeatureScript); Zeichnungen lesen die exportierten STEP-Körper. KiCad, Gerber und eingefrorene Bestellunterlagen sind unverändert.
