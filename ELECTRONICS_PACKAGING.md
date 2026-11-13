<!-- CURRENT_FLAT132_R11_START -->
> **03.11.2026 – aktueller Flat132 R11, PLA als Standard:** Elektronikwanne P08 klickt an den vorhandenen R10-Rahmen; P09 klickt an P08. P10 und vier P07 entfallen durch Integration in Deckel und Führungsschuhe. **P01 bleibt geometrisch unverändert – vorhandenen R10-Druck weiterverwenden.** P04 bleibt geometrisch gleich und wird für saubere Fingerflächen mit vorderer Stirnseite unten und schlanken Baumstützen nur vom Bett gedruckt. P06, verstellbare P12-Schuhe und P11 behalten ihre Funktionsschrauben. [CAD/Review](review/flat132-click-assembly-2026-11-03/README.md) · [Verbindungsmatrix](review/flat132-click-assembly-2026-11-03/ASSEMBLY_JOINT_REVIEW.md) · [Montage](review/flat132-click-assembly-2026-11-03/MONTAGE.md) · [Stücklistenänderungen](review/flat132-click-assembly-2026-11-03/BOM_Aenderungen.csv) · [Onshape R11](https://cad.onshape.com/documents/15316cc6370631845af136b2/v/a6ea6390a313176b40101f6b/e/d253eb87b70818ebde8215f0).
>
> [Bambu H2D / 0,4 mm / PLA – 3MF](print/bambu-R11-PLA-click-2026-11-03/Fingerworker_R11_H2D_04mm_PLA_Fit_Test.3mf) · [Druckpaket ZIP](print/bambu-R11-PLA-click-2026-11-03/Fingerworker_R11_H2D_04mm_PLA_Fit_Test_Package.zip). **13 Druckstücke auf drei Platten:** Rahmen / elf Montage- und Passstücke / Fingergriff. Keine Schrauben oder Muttern drucken. Fünf kleine Druckteile weniger als R10; ein PLA-Filament genügt. Alle drei Platten sind gesliced und geprüft. Federfreier Passsatz mit Stangen-Formhilfen und Q01; reale Passung und Festigkeit sind noch am Muster zu prüfen. Die folgenden älteren Revisionsangaben bleiben historische Stände.
<!-- CURRENT_FLAT132_R11_END -->

# Elektronik unter der Handballenauflage

> Neue Konstruktion 11.10.2026: [Elektronikaufnahme Rev A mit STL, STEP, Zeichnungen und Montage](mechanical/manufacturing-2026-10-11/README.md) ersetzt die unten beschriebene Bauraumstudie. P02 erhält zwei Blindloch-Inserts; Wanne, Deckel und Kabelklemme sind konstruiert. Die folgenden Einbauprüfungen beschreiben den historischen Stand vom 21.09.2026.

21. September 2026. Das **vierlagige KiCad-PCB ist vollständig geroutet** und besteht ERC, DRC sowie Schaltplanabgleich ohne offene Verbindungen. Die optionale FeatureScript-Einbaustudie ist auf die tatsächliche Platzierung angepasst und **in Onshape übernommen und regeneriert**. Bei 0, 15 und 30 mm Hub wurden mit Handmodell jeweils 43 ausgewählte Körperpaare geprüft: keine Volumenüberschneidung, alle sieben Elektronik-Prüfpaare CLEAR. Das ist eine nominelle Einbaustudie, noch kein druckfertiges Gehäuse.

## Aktuelles Bauraumbudget

| Teil / Abstand | Nomineller Wert |
|---|---:|
| PCB, Bestückung nur oben | 19,5 × 68,5 × 0,8 mm |
| Elektronikgehäuse | 22,5 × 110 × 8,9 mm |
| Gehäuse-Innenraum | 20,5 × 108 × 7,1 mm |
| Platinenspiel pro Seite | 0,5 mm |
| Unterseite PCB zum Boden | 0,3 mm |
| JST-Höhe laut Hersteller | 5,5 mm |
| Zusätzliche Lötzugabe | 0,15 mm |
| JST zur Decke inklusive Lötzugabe | 0,35 mm |
| Gehäuse zur festen Auflagenplatte | 0,6 mm |
| Gehäuse zur gesamten Mechanik, Minimum aus Onshape | **0,6 mm — nominell; Drucktoleranz prüfen** |
| Elektronik zum Handmodell, Minimum aus Onshape | 4,70 mm |
| Akku zur hinteren Innenwand | 1 mm |
| Gegenstecker-/Leitungsreserve zum Akku | 1,3 mm |

Die Bauteilhüllkörper verwenden die KiCad-Courtyards und konservative Höhen. Für XIAO sind weiterhin 5 mm ab PCB-Oberseite reserviert; das ist kein bestätigtes Hersteller-STEP. Für die Passiv-/Halbleiterkörper gelten 1,65 mm einschließlich Lötreserve, für den Taster 2,5 mm. Der JST ist im [Herstellerblatt, SMT side entry](https://www.jst-mfg.com/product/pdf/eng/ePH.pdf) mit 5,5 mm spezifiziert.

Die Platine liegt bei X−44,6…−25,1 / Y−53,5…15 / Z1,3…2,1 mm. Das Gehäuse liegt bei X−46,1…−23,6 / Y±55 / Z0…8,9 mm. Es ist gegenüber dem bisherigen Budget 0,5 mm breiter und 0,4 mm höher; die gesamte Gerätehöhe bleibt 30 mm. Die komplette Elektronikstudie wurde im Vollreview um 1,25 mm nach außen versetzt. Mit der Studie beträgt die Außenhülle 180,1 × 180 × 30 mm; USB-Ansteckraum ist kein Teil des Gerätemaßes. Die Befestigungen der Mechanik wurden separat überarbeitet.

Der Akku liegt jetzt bei X−41,25…−29,75 / Y22…53 / Z1,5…5,3 mm. Die Verschiebung um 3 mm schafft Platz für den größeren Stecker. Dessen Gegenstück und erster Leitungsabschnitt erhalten eine zusätzliche 8 × 6 × 5,3-mm-Reserve vor der Zelle. Die 6-mm-Verlängerung ist eine Montageannahme; die tatsächliche gesteckte Länge und Kabelbiegung am Kabelbaum messen. Die Zelle braucht eine isolierte, entnehmbare Halterung, ohne als Stütze oder Anschlag zu wirken.

Die Studie ergänzt eine seitliche Tasteröffnung mit Betätigungshüllkörper und eine erhöhte Kabelöffnung zur Mechanik. Betätigung, Kabelweg und Zugentlastung sind noch keine fertigen Druckteile. Die Hüllkörper gehören nicht in den STL-Export der mechanischen Druckteile.

## Prüfung und Grenzen

Der lokale Maßabgleich bestätigt **51 Komponenten-/Platinenträger-/Akku-Hüllkörper innerhalb des reservierten Gehäuse-Innenraums**. Er prüft achsenparallele Nennmaße. Die Aussparungen und externen USB-/Taster-Zugänge sind nicht Gegenstand dieses Einschlussnachweises. Visualisierung: `electronics/kicad/preview/mechanical-fit.svg`; maschinenlesbar: `electronics/kicad/reports/mechanical-fit-local.json`.

Die frischen Onshape-Ausgaben stehen in `review/onshape-full-review.json`, die Prüfung in `review/electronics-packaging-validation.json`. Der Prüfer bindet sie per Quelltext-Fingerprint und SHA-256 an den tatsächlich übertragenen FeatureScript-Stand. 103 Körper waren aktiviert: Mechanik, Hand und 54 Elektronik-Referenzkörper. Die aktuelle Prüfung umfasst zusätzlich Vorspannungs-Endlagen, eine Zwischenstellung, das bestehende stärkere Federpaar und Isometrie. Eine kontinuierliche Hubprüfung oder Belastungsrechnung ist damit nicht ersetzt. Mechanische Nullspalt-Kontakte sind weiterhin als REVIEW dokumentiert. Die älteren Berichte unter `review/electronics-old-study-2026-09-21/` bleiben ausschließlich Nachweise der alten Studie.

Der bisherige 0,1-mm-Engpass ist im CAD auf **0,6 mm** vergrößert. Diesen Spalt mit Drucktoleranzen sowie belasteter Verformung abgleichen. Konkrete Modul-/Gegensteckermaße, Kabelradien, Akku-Spiel und Befestigung prüfen. Dann die Aufnahme druckfertig konstruieren. Funkleistung, Versorgungshochlauf, Kalibrierung und Ladefunktion werden am Elektronikmuster geprüft.
