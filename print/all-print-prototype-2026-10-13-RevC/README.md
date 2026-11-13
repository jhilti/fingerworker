> Historisch: Dieser Zwischenstand ist durch den [Rev-D-Satz für H2D, PETG/PLA](../bambu-2026-10-13-RevD/README.md) ersetzt. Rev C behebt die Halterbohrungen, Rev D ergänzt die starren geteilten Handballenschalen. Für den aktuellen Erstaufbau den vollständigen Rev-D-Satz verwenden.

# Alle Druckteile zur Beurteilung – Rev B, 13.10.2026

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

**Gegenüber dem bisherigen Satz P01, P060 und P061 ersetzen. P04 bleibt unverändert.** P01 besitzt jetzt eine 6-mm-Grundplatte (vorher 4 mm); das zusätzliche Material liegt unterhalb der bisherigen Unterseite. Die Funktionshöhe oben bleibt gleich. Die hinteren festen Sockel enden bei Z4,5; unter dem Griff bei Z5 verbleiben nominal 0,5 mm Spiel. P060/P061 reichen bis zur tieferen Auflage. Rodachse Z18 und Schraubenkopfauflage Z10 bleiben erhalten. Die vier M3-Einsatzpiloten sind nominal Ø4,2 × 4 mm tief, mit 2,5 mm verbleibendem Boden; das reale Einsatzfabrikat weiterhin passend prüfen.

Montagereihenfolge:

1. P060/P061 abnehmen; Führungsstäbe, Federn, Isometriehülsen und Anschlagschrauben noch nicht einsetzen. Die festen Sockel bleiben an P01.
2. Führung und Griffkanal entgraten und Stützen entfernen. P04 von hinten gerade auf die Mittelführung schieben, ohne Anheben oder Verbiegen. Montage bis zur offenen Betriebsstellung, dann federfrei den 30-mm-Hub prüfen.
3. Erst danach Führungsstäbe und übrige Mechanikteile montieren; P060/P061 zuletzt auf die abgesenkten Sockel setzen und befestigen. Die bisherigen Halter passen nicht zur neuen Sockelhöhe.

Zuerst federfrei Griff, Bewegungsraum und Einbau beurteilen. Eine verschraubte Montage benötigt weiterhin die ausgeschlossenen Befestigungen. Der Kunststoffsatz besitzt keine bestätigte Belastbarkeit; die bestellten Federpaare erzeugen am vollen Hub nominal bis etwa 267 N. Die gedruckten Metallersatzteile zunächst ohne Federn beurteilen. Für spätere Belastungsversuche geeignete Kraftpfadteile und Prüfung am Muster vorsehen.

## Herkunft und Prüfung

P01/P060/P061 stammen aus frischen Live-Onshape-Exporten der Rev B vom 13.10.2026. Unveränderte Mechanikteile stammen aus dem geprüften Export vom 29.09.2026, P02/P08/P09/P10 aus der Gehäuserevision vom 11.10.2026. H-Anschauungsteile stammen aus den zugehörigen STEP-Dateien, mit starrer Drehung und Verschiebung auf Z0. H13 ist eine vereinfachte Handradvariante. Haupt-CAD und Metallfertigungsunterlagen bleiben bestehen.

`validation.json` dokumentiert geschlossene Kanten, nicht entartete Dreiecke, positives Volumen und Bodenlage. `Druckliste.json` enthält Abmessungen, Herkunft und SHA-256. `source/build_pack.py` reproduziert das Paket im vollständigen Projekt mit Python/CadQuery; zum Drucken genügt das ZIP.

Die Montageprüfung in `assembly-validation.json` umfasst 362 Einschubstellungen und das kontinuierliche überstrichene Volumen zwischen 0 und 180 mm rückwärtigem Versatz. Kein Volumeneingriff zwischen P01 und P04; aufgesetzte Halter passen ohne Volumenüberlagerung. Fenster und Tischbefestigungsbohrungen bleiben durchgehend offen. Diese nominale Prüfung ersetzt die Passprobe am tatsächlichen Druck nicht.

Der finale Live-Onshape-Stand ist als `source/fingerworker_RevB.fs` enthalten; `Onshape_RevB.png` zeigt die gespeicherte Grundplatte. Drei Betriebsstellungen 0/15/30 mm mit leichter Federpaarung und 0 mm Vorspannung wurden zusätzlich in Onshape geprüft: keine Volumeninterferenzen in 129 Gruppenprüfungen; Handreferenz aus, beabsichtigte Kontakte unverändert.
