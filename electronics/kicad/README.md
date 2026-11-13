# Fingerworker – KiCad, Revision A

11. Oktober 2026. **Geroutetes, editierbares Prototypenprojekt Rev A-P1 für KiCad 10.0.6**, abgeglichen mit `electronics/order/RevA-P1-JLC/source/`. C4 und C7: jeweils **22 µF**, Murata **GRM21BR61E226ME44L**, 25 V, X5R, 0805. Schaltpläne, PCB, lokale Symbolbibliothek und native Pin-/Netzdaten entsprechen dieser eingefrorenen JLC-Quelle. Routing und Bauteilpositionen sind unverändert.

Die separat freigegebenen YAGEO-Ersatzteile für C5/C6/C13 bleiben im JLC-Portal-BOM und in `../order/RevA-P1-JLC/SUBSTITUTIONS.md` dokumentiert; die eingefrorene Quell-BOM enthält deren ursprüngliche Murata-MPNs. Für Portal-Uploads gilt `BOM_JLC_portal.csv`.

Frische ERC-/DRC-Prüfung einschließlich Schaltplanabgleich: keine Fehler, Warnungen oder offenen Verbindungen. Hardwarefunktion und Gehäuseintegration bleiben am Muster zu prüfen. USB-Erkennung der Firmware verwendet jetzt den internen VBUS-Detektor statt des D6-Teilers.

## Öffnen

`Fingerworker_RevA.kicad_pro` in KiCad öffnen; Schaltplan und PCB über den Projektmanager starten. Symbol- und Footprint-Bibliotheken sind lokal enthalten. Unter `preview/` liegen alle vier Schaltplanblätter, beide PCB-Seiten und die lokale Bauraumstudie als SVG/PNG.

## Platine

- **19,5 × 68,5 × 0,8 mm**, vier Kupferlagen, ausschließlich Bestückung oben.
- 48 Footprints, 51 Schaltplansymbole einschließlich externem Sensor, Akku und Endschalter.
- F.Cu: Bauteile, kurze Mess- und Schaltreglerwege. In1.Cu: zusammenhängende Massefläche ohne Signalleiterbahnen. In2.Cu und B.Cu: weitere Verbindungen und ergänzende Masseflächen.
- Der Antennenbereich und der angrenzende Freiraum sind auf **allen vier Kupferlagen** gesperrt. Funkleistung mit Hand und Gehäuse bleibt zu messen.
- Boost-Schaltknoten, Rückstromschleife, ADC-Abblockung und Eingangsfilter wurden gezielt angeordnet und geroutet. Die getrennten Erregungs-Sense-Leitungen enden direkt an J2: Net-Ties 1–5 und 4–6. Physisch bleiben vier Sensoradern; Spannungsabfälle im Sensorkabel werden damit nicht kompensiert.
- 0,15 mm Mindestabstand/-leiterbahnbreite, 0,25 mm Kupfer–Rand, ausschließlich 0,6/0,3-mm-Durchkontaktierungen. Versorgungswege überwiegend 0,4 mm; lokale ADC-Anschlüsse sind schmaler. Den 0,8-mm-Vierlagenaufbau mit dem späteren Fertiger festlegen.
- Die XIAO-Lands haben nominell 0,2925 mm Abstand zum PCB-Rand. Ihre Geometrie entspricht der Herstellerbibliothek.

Vier Lagen erlauben eine eigene Massefläche unter der Messschaltung bei unveränderter Platinenstärke. Die frühere zweilagige Platzierung ist im Arbeitsverzeichnis archiviert.

## Prüfungen

| Prüfung | Ergebnis |
|---|---:|
| Native Schaltplannetze gegen Pin-/Netzdaten | 140 verbundene + 10 explizit unbenutzte Pins, 0 Abweichungen |
| ERC | 0 Fehler / Warnungen |
| DRC inklusive gefüllter Kupferflächen | 0 Fehler / Warnungen |
| Offene Verbindungen | **0** |
| Schaltplan–PCB-Abgleich | 0 Abweichungen |
| Masse-Innenlage | 1 verbundene Fläche, keine Signalleiterbahnen |

Berichte: `reports/verification-summary.json`, `erc-full-review.json`, `drc-full-review.json`, `full-review-netlist.xml`. Keine DRC-Verletzungen als Ausnahmen ausgeblendet. Diese Prüfungen belegen Netztreue und geometrische Regeln, keine gemessene Funktion, Funkleistung oder mechanische Belastbarkeit.

## Einbau

Die lokale FeatureScript-Bauraumstudie verwendet jetzt die tatsächlichen PCB-Positionen und Courtyards. Das Elektronikgehäuse ist nominell **22,5 × 110 × 8,9 mm**, mit 0,5 mm Platinenspiel pro Seite und 0,35 mm Reserve über dem 5,5-mm-JST plus 0,15-mm-Lötzugabe. Die Platine sitzt 0,3 mm über dem Boden; zur festen Handballenplatte bleiben 0,6 mm. Die Gerätehöhe bleibt 30 mm.

Der Akku wurde innerhalb der Studie um 3 mm verschoben; hinten bleibt 1 mm. Gegenstecker/Leitungsansatz und Seitentaster haben eigene Hüllkörper und Zugangsöffnungen. 51 Komponenten-/PCB-/Akku-Hüllkörper passen nominal in den reservierten Innenraum. Darstellung: `preview/mechanical-fit.svg`; Maße und Grenzen: `reports/mechanical-fit-local.json`.

**In Onshape aktualisiert und geprüft:** Bei 0/15/30 mm Hub mit Handmodell jeweils 43 ausgewählte Körperpaare ohne Volumenüberschneidung; alle sieben Elektronik-Prüfpaare CLEAR. Der kleinste Gehäuse-/Mechanikabstand ist von 0,1 auf **0,6 mm** vergrößert; Drucktoleranzen und belastete Verformung bleiben zu prüfen. Die Elektronik bleibt mindestens 4,70 mm vom Handmodell entfernt. Aktuelle Berichte liegen unter `../../review/` im Arbeitsverzeichnis und im neuen Vollreview-Paket. Die früheren Berichte gelten nur für die alte Studie. Die neue lokale Studie ist kein druckfertiges Gehäuse; XIAO-Höhe, Gegenstecker und Tasterbetätigung enthalten Planungsreserven. Die KiCad-3D-Bibliotheken sind für U1/J1/L1 unvollständig; eine 3D-Ansicht allein ist kein Einbaunachweis.

## Endschalter nach Vollreview

**NC statt NO:** NC an J3.1, COM an J3.2; NO isolieren. `ENDSTOP_N` (D5/P0.05) ist LOW bei Endlage oder unterbrochener Leitung. Bei V5A aus ungültig. Die Kupferführung ist unverändert; Schaltplan, Bibliothek, Netznamen und Verbindungsliste sind aktualisiert. Kraftwerte am Hartanschlag sind wegen Lastbypass nicht vollständig; Firmware muss sie entsprechend sperren. Siehe `../FIRMWARE_CONTRACT.md` (im neuen Paket unter `electronics/`).

## Vor Bestellung

1. Vorhandenen Akku-Kabelbaum messen: J1 ist hier **1 = VBAT, 2 = GND**; tatsächliche Steckerpolarität bestätigen.
2. Konkrete Passiv-MPNs und effektive MLCC-Kapazitäten festlegen. Lieferbares Vierlagen-Stackup und Fertigungstoleranzen bestätigen.
3. Sensor-Gleichtakt, Boost-Ripple, monotone ADC-Versorgungsrampen, Ladestrom/Temperatur und Kalibrierung am Tischaufbau prüfen. Die offenen elektrischen Punkte aus `../README.md` bleiben relevant.
4. 0,6-mm-Gehäuse-/Mechanikspalt gegen Drucktoleranzen und Verformung prüfen. Tatsächlichen Modulstapel, Gegenstecker/Kabelbiegung, Akkuhalterung, Zugentlastung und Befestigung auslegen. Anschließend die Kollisionsprüfung wiederholen.

Gerber-/Bohr-/Bestückungsdaten sind noch nicht freigegeben. Die PCB-Datei enthält alle gerouteten Daten für den weiteren Review.

## Quellen und Bearbeitung

- Herstellergeometrie: [Seeed XIAO](https://wiki.seeedstudio.com/XIAO_BLE/), [JST PH, SMT side entry 5,5 mm](https://www.jst-mfg.com/product/pdf/eng/ePH.pdf), [Coilcraft XFL3012](https://www.coilcraft.com/en-us/products/power/shielded-inductors/molded-inductor/xfl/xfl3012/). Weitere elektrische Quellen stehen in `../README.md`.
- KiCad-Standard-Footprints 10.0.6 sowie lokale Herstellerkopien. XIAO-Kupfergeometrie unverändert; dekorative Umrisse auf F.Fab. J2 enthält die beiden zusätzlichen internen Sense-Net-Ties.
- Das native Projekt ist der bearbeitbare Lieferstand. Entwicklungsskripte im Arbeitsverzeichnis erzeugen Zwischenstände und können Dateien überschreiben. `build_pcb.py` erzeugt nur die historische Platzierung; es verweigert jetzt das Überschreiben einer gerouteten Platine ohne ausdrückliches Flag. Auch `build_kicad.py` verweigert das ungefragte Überschreiben der geprüften Schaltpläne und Bibliotheken.
- `verify_project.py` führt ERC, DRC und Netzlistenexport frisch aus. Es prüft alle vorgesehenen Pins einschließlich NC sowie die PCB-Padnetze; zusätzliche Pins werden nicht mehr stillschweigend herausgefiltert. Eingaben und Berichte sind per SHA-256 gebunden. Ein fehlgeschlagener Lauf hinterlässt kein altes PASS-Ergebnis. `update_packaging.py` erzeugt die lokale Hüllkörperstudie; `review_packaging.py` prüft deren nominelle Innenraummaße. Die separate Onshape-Prüfung ist an den übertragenen FeatureScript-Quellstand gebunden; Änderungen benötigen neue Prüfungen.
