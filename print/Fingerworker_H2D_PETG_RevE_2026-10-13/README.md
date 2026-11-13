# Fingerworker – H2D-Druckprojekt Rev E, 13.10.2026

**`Fingerworker_RevE_H2D_04mm_PETG.3mf` in Bambu Studio als Projekt öffnen.** Es enthält 30 Geräteteile und zwei Führungs-Passproben auf sechs vorbereiteten Druckplatten. Schrauben, Muttern, Gewindeeinsätze und Unterlegscheiben sind nicht enthalten. Sensor, Federn, Platine und Akku bleiben Kaufteile.

Eingestellt sind **Bambu Lab H2D, Standarddüsen 0,4 mm, PETG, Textured PEI Plate**, 0,20-mm-Schichten, vier Wandlinien, fünf Boden-/Deckschichten und 30 % Gyroid. Die individuellen H-Anschauungsteile erhalten 100 % Füllung. Zugängliche Stützen und Haftungsränder sind an den benötigten Objekten eingestellt. Arachne berücksichtigt die dünnen Abstandshülsen. Die Düsengröße ist als Standardannahme gewählt; die tatsächlichen Düsen und Druckplatte vor dem Druck abgleichen.

Alle Platten verwenden **ein PETG-Filament**. Das Projekt benötigt kein TPU. Für PLA in Bambu Studio das Filament durch ein zum vorhandenen PLA passendes H2D-Profil ersetzen und neu slicen; Temperaturen und Geschwindigkeit stammen dann aus diesem Profil. Auch bei PETG das Profil auf das tatsächliche Filament abstimmen. Keine Skalierung und keine automatische Neuausrichtung nötig.

| Platte | Inhalt | Anzahl |
|---|---|---:|
| 1 | Führungs-Passprobe männlich/weiblich – zuerst drucken | 2 |
| 2 | Grundplatte 6 mm, zwei Führungsstäbe | 3 |
| 3 | Griff, Federjoch, Handballenauflage, zwei hintere Halter | 5 |
| 4 | Elektronikaufnahme und kleine Anschauungsteile | 14 |
| 5 | Zwei optionale Isometriehülsen | 2 |
| 6 | Zwei starre Handballenschalen und vier harte Rücklaufpuffer | 6 |
| **Gesamt** | **30 Geräteteile + 2 Passproben** | **32** |

**Korrektur Rev E:** Die weibliche Passprobe ist um 180° gedreht: geschlossene Rückseite auf dem Druckbett, Führungskanal nach oben. Die frühere Lage erzeugte eine 33,5-mm-Brücke über dem Kanal. Geometrie und Passungsmaße sind unverändert; die männliche Probe bleibt wie bisher. Beide Passproben benötigen hier keine Stützen und werden mit 100 % Füllung gedruckt, damit auch im Probenboden keine langen Druckpfade über spärlicher Füllung nötig sind. Zum Zusammenstecken die weibliche Probe nach dem Druck umdrehen, sodass der Kanal nach unten über dem männlichen Profil liegt. Eine vorhandene männliche Probe muss nicht neu gedruckt werden.

Zuerst Platte 1 drucken, Stützen/Fäden/Elefantenfuß entfernen und die Führungspassung prüfen. Danach die übrigen Platten slicen und die Vorschau auf erste Schicht, freie Bohrungen, Brücken und entfernbares Stützmaterial kontrollieren. Das gelieferte 3MF ist ein bearbeitbares Projekt; der Prüf-G-Code wird nicht als Druckdatei ausgeliefert.

Die originale TPU-Manschette wurde für diesen Satz durch **zwei starre Halbschalen P03a/P03b** ersetzt. Sie passen seitlich um den noch unmontierten P02-Kern und werden für die Beurteilung mit Klebeband gehalten. Die vier harten P07-Formteile zeigen nur den Einbauraum; sie besitzen keine elastische Rücklaufdämpfung. Das funktionale Haupt-CAD behält die elastische Referenzmanschette. Rev D bezeichnet diese separate Druckvariante; Grundplatte und hintere Halter entsprechen dem korrigierten Live-CAD Rev C.

**Montage gemäß [MONTAGE.md](MONTAGE.md), zunächst ohne Federn.** Die gedruckten Stäbe und Metallersatzformen dienen der Beurteilung von Form und Montage. Ihre Kernlöcher/glatten Gewindehüllformen ersetzen keine funktionierenden Gewinde. Das vereinfachte H13-Handrad enthält keinen Schraubenschaft. Für eine verschraubte Montage werden die ausgeschlossenen Kaufbefestigungen benötigt. Mit diesem Anschauungssatz keine Federlastprüfung durchführen.

Die Grundplatte ist 6 statt 4 mm dick; die hinteren Sockel liegen 0,5 mm unter der Griffunterseite. P060/P061 reichen zur tieferen Auflage und haben jetzt durchgehende Schraubenbohrungen. P01/P060/P061 gemeinsam ersetzen; P04 bleibt unverändert.

Prüfung: 25 geschlossene STL-Typen, 30 Geräteteile, zwei Passproben, sechs getrennte Platten; 15 nominale Montagewege mit 235 Stellungen, kontinuierlicher Griff-Einschub und acht Schraubenfreiräume. Bambu Studio 02.08.02.61 hat alle sechs Platten erfolgreich für den H2D geslict. Die Slicer-Schätzung für den vollständigen Satz beträgt etwa **15 h 04 min / 356 g PETG** inklusive Passproben, Stützen und Haftungsrändern. Reale Dauer und Passung hängen vom Druck ab. Nachweise: `validation.json`, `assembly-validation.json`, `Druckliste.csv` und `plate-layout.json` sowie `coupon-orientation-validation.json`.

Die Geräteteil-STLs liegen unter `PETG/`, Stückzahlen und Herkunft in `Druckliste.csv`/`.json`. Die beiden korrigierten Passproben sind separat enthalten. Jede STL enthält ein Exemplar. `Plattenvorschau.png` zeigt die sechs vorbereiteten Platten. `Onshape_RevC.png` zeigt den unveränderten aktuellen Funktions-CAD-Stand. Die Quellgeneratoren liegen im Fingerworker-Projekt. Rev E korrigiert die Orientierung der weiblichen Passprobe und setzt die Passproben auf 100 % Füllung; alle 30 Geräteteile und deren Druckeinstellungen entsprechen Rev D. Frühere Rev-B-/Rev-C-Projekte sind historische Zwischenstände mit der elastischen Manschette; für diesen Erstaufbau ausschließlich den vollständigen Rev-E-Projektstand verwenden.
