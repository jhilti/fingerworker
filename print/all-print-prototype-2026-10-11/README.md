> Überholt durch [Rev B, 13.10.2026](../all-print-prototype-2026-10-13-RevB/README.md): Grundplatte 6 mm, freier Einschub, neue P060/P061. Die folgenden Angaben dokumentieren den Vorgänger.

> Offener Montagepunkt: Die digitale Prüfung zeigt beim geraden Einschub auf Betriebshöhe noch eine Kollision mit den festen Sockeln der hinteren Halter (Z5–6 mm). Das Entfernen der Seilaugen beseitigt die gemeldete große Blockade, ist aber noch kein Nachweis eines vollständig freien Montagewegs.

> Revision 13.10.2026: Seilhalter aus P01 entfernt, frischer Onshape-STL. P04 unverändert. Grundplatte 156 × 180 mm. Hintere Halter P060/P061 vor dem Einschieben entfernen. Die restlichen Montagefreiräume sind am Muster zu prüfen.

# Alle Druckteile zur Beurteilung – 11.10.2026

24 unterschiedliche STL-Dateien, insgesamt 29 Teile einschließlich optionaler Isometriehülsen. Millimeter, Maßstab 100 %. Jede Datei enthält ein Exemplar; Stückzahlen stehen in `Druckliste.csv` und `Druckliste.json`. PETG und TPU liegen getrennt.

Enthalten: elf Mechanikdruckteile mit aktuellem Rahmen P01 ohne Seilhalter und neuem P02, drei Gehäuseteile P08/P09/P10 sowie zehn Anschauungsteile aus der Metallkonstruktion. Führungsstäbe, Federsitze, Sensorkassette, Halteplatte, Druckstift, Abstandshülsen, Druckstück und optionale Isometriehülsen sind enthalten. H13 ist ein separates Handrad Ø22 × 2,8 mit Ø6,4-Bohrung, ohne Schraubenschaft und ohne Rändelung.

Schrauben, Muttern, Gewindeeinsätze und Unterlegscheiben sind ausgeschlossen, einschließlich H11-Vorspannungsmutter und H13-Schraubenschaft. Federn, Sensor, Platine und Akku sind Kaufteile. Die H-STLs sind Anschauungsvarianten mit Kernlöchern und glatten Gewindehüllformen, ohne funktionsfähige gedruckte Gewinde. Der Druckstift bleibt als individuelles Formteil mit glattem Anschluss enthalten.

## Bambu Studio

1. ZIP entpacken, tatsächlichen Drucker, Düse und Filament wählen. Die STL-Dateien sind ungeslicte, geräteunabhängige Druckgeometrie.
2. PETG und TPU auf getrennte Druckplatten importieren. Mehrere Dateien als **einzelne Objekte** laden, nicht als gemeinsames mehrteiliges Objekt. Einheit mm, Maßstab 100 %, gespeicherte Orientierung beibehalten und auf Platte setzen.
3. Exemplare nach `Druckliste.csv` duplizieren, automatisch auf mehrere Platten verteilen. P01 benötigt ungefähr 156 × 180 mm; auf kleinen Druckplatten einschließlich Haftungsrand die Platzierung einzeln prüfen. Nicht skalieren.
4. PETG-Startpunkt: 0,4-mm-Düse, 0,2-mm-Schichten, mindestens 4 Wandlinien, 5 Boden-/Deckschichten, 30 % Gyroid. Kleine H-Teile vollständig füllen. Tragende Bereiche von P01/P04/P05 und Einsatzbereiche lokal vollständig füllen. Erhöhte Wandzahl verdickt konstruktiv dünne Gehäusewände nicht.
5. Stützen in der Vorschau prüfen, besonders P02/P04/P05 sowie liegende Stäbe und Druckstift. Nur zugängliche Stützen verwenden; Führungskanäle müssen von den Enden entfernbar bleiben. P08 steht auf dem Boden, P09 auf der flachen Außenfläche mit Rippen nach oben, P10 liegt flach. Kleine Teile/Stäbe bei Bedarf mit Haftungsrand.
6. TPU mit passendem Filamentprofil drucken, etwa 95A als Ausgangspunkt. P03 steht auf einem Ende, vier Puffer liegen flach. Naht von Handkontaktflächen weglegen. Filamentzuführung passend zum tatsächlich verwendeten Drucker und TPU wählen.
7. Jede geslicte Platte vor Druckbeginn auf erste Schicht, Bohrungen, Brücken und Stützenzugang prüfen. H22 ist mit Ø2,5 × 1 mm nur eine winzige Anschauungsprobe.

Gespeicherte Druckrichtungen sind bereits eingestellt. Kunststoffstäbe dienen zur Lage- und groben Passformprüfung. Rundungen/Löcher gegebenenfalls entgraten; Metallfertigungstoleranzen sind keine zugesicherten FDM-Toleranzen.

## Montage und Beurteilung

Zuerst federfrei zusammenlegen und Griff, Bewegungsraum und Einbau beurteilen. Eine verschraubte Montage benötigt weiterhin die ausgeschlossenen Befestigungen. Der Kunststoffsatz besitzt keine bestätigte Belastbarkeit; die bestellten Federpaare erzeugen am vollen Hub nominal bis etwa 267 N. Die gedruckten Metallersatzteile zunächst ohne Federn beurteilen. Für spätere Belastungsversuche geeignete Kraftpfadteile und Prüfung am Muster vorsehen.

## Herkunft und Prüfung

P01 stammt aus dem Live-Export vom 13.10.2026. Unveränderte Mechanikteile stammen aus dem geprüften Export vom 29.09.2026, P02/P08/P09/P10 aus der Gehäuserevision vom 11.10.2026. H-Anschauungsteile stammen aus den zugehörigen STEP-Dateien, mit starrer Drehung und Verschiebung auf Z0. H13 ist eine vereinfachte Handradvariante. Haupt-CAD und Metallfertigungsunterlagen bleiben bestehen.

`validation.json` dokumentiert geschlossene Kanten, nicht entartete Dreiecke, positives Volumen und Bodenlage. `Druckliste.json` enthält Abmessungen, Herkunft und SHA-256. `source/build_pack.py` reproduziert das Paket im vollständigen Projekt mit Python/CadQuery; zum Drucken genügt das ZIP.
