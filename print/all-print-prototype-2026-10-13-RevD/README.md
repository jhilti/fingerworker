> Historischer Stand: Die vollständige [Druckbarkeitsprüfung Rev F](../bambu-2026-10-13-RevF/README.md) enthält vier verbesserte Drucklagen, zusätzliche zugängliche USB-Stützen, breitere Brims und korrekte Pufferhöhe. Nennformen und Passproben bleiben passend.

> Passprobe: Das H2D-Projekt ist jetzt Rev E; die weibliche Probe liegt mit dem Kanal oben. Die 25 Geräteteil-STLs dieses Rev-D-Satzes bleiben unverändert.

# Fingerworker – vollständiger PETG/PLA-STL-Satz Rev D, 13.10.2026

**Empfohlen: [vorbereitetes H2D-3MF](../bambu-2026-10-13-RevE/Fingerworker_RevE_H2D_04mm_PETG.3mf) in Bambu Studio als Projekt öffnen.** Es enthält 30 Geräteteile und zwei Führungs-Passproben auf sechs vorbereiteten Druckplatten. Schrauben, Muttern, Gewindeeinsätze und Unterlegscheiben sind nicht enthalten. Sensor, Federn, Platine und Akku bleiben Kaufteile.

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

Zuerst Platte 1 drucken, Stützen/Fäden/Elefantenfuß entfernen und die Führungspassung prüfen. Danach die übrigen Platten slicen und die Vorschau auf erste Schicht, freie Bohrungen, Brücken und entfernbares Stützmaterial kontrollieren. Das gelieferte 3MF ist ein bearbeitbares Projekt; der Prüf-G-Code wird nicht als Druckdatei ausgeliefert.

Die originale TPU-Manschette wurde für diesen Satz durch **zwei starre Halbschalen P03a/P03b** ersetzt. Sie passen seitlich um den noch unmontierten P02-Kern und werden für die Beurteilung mit Klebeband gehalten. Die vier harten P07-Formteile zeigen nur den Einbauraum; sie besitzen keine elastische Rücklaufdämpfung. Das funktionale Haupt-CAD behält die elastische Referenzmanschette. Rev D bezeichnet diese separate Druckvariante; Grundplatte und hintere Halter entsprechen dem korrigierten Live-CAD Rev C.

**Montage gemäß [MONTAGE.md](MONTAGE.md), zunächst ohne Federn.** Die gedruckten Stäbe und Metallersatzformen dienen der Beurteilung von Form und Montage. Ihre Kernlöcher/glatten Gewindehüllformen ersetzen keine funktionierenden Gewinde. Das vereinfachte H13-Handrad enthält keinen Schraubenschaft. Für eine verschraubte Montage werden die ausgeschlossenen Kaufbefestigungen benötigt. Mit diesem Anschauungssatz keine Federlastprüfung durchführen.

Die Grundplatte ist 6 statt 4 mm dick; die hinteren Sockel liegen 0,5 mm unter der Griffunterseite. P060/P061 reichen zur tieferen Auflage und haben jetzt durchgehende Schraubenbohrungen. P01/P060/P061 gemeinsam ersetzen; P04 bleibt unverändert.

Prüfung: 25 geschlossene STL-Typen, 30 Geräteteile, zwei Passproben, sechs getrennte Platten; 15 nominale Montagewege mit 235 Stellungen, kontinuierlicher Griff-Einschub und acht Schraubenfreiräume. Bambu Studio 02.08.02.61 hat alle sechs Platten erfolgreich für den H2D geslict. Die Slicer-Schätzung für den vollständigen Satz beträgt etwa **14 h 49 min / 353 g PETG** inklusive Passproben, Stützen und Haftungsrändern. Reale Dauer und Passung hängen vom Druck ab. Nachweise: `validation.json`, `bambu-validation.json`, `assembly-validation.json`, `Druckliste.csv` und `plate-layout.json`.

Dieser STL-Satz enthält 25 Einzeldateien mit Stückzahlen in `Druckliste.csv`/`.json`. Jede STL enthält ein Exemplar, in mm auf Z0; Mengen gemäß Liste duplizieren. Die beiden Passproben liegen im vorbereiteten 3MF. `source/build_pack.py` reproduziert den Satz im vollständigen Repository mit Python/CadQuery. `source/fingerworker_RevC.fs` ist die aktuelle funktionale Onshape-Quelle, `source/build_rigid_palm.py` die separate starre Schalenvariante. `Druckliste.json` enthält Herkunft und SHA-256 jeder STL. P01 stammt aus dem frischen Onshape-Export Rev B (unverändert in Rev C), P060/P061 aus Rev C; P02/P08/P09/P10 aus der Gehäuserevision Rev A vom 11.10.2026. Die übrigen unveränderten Mechaniknetze und harten P07-Formen stammen vom 29.09.2026; H-Formen aus den Rev-A-STEP-Dateien. Frühere Rev-B-/Rev-C-Projekte sind historische Zwischenstände mit der elastischen Manschette; für diesen Erstaufbau ausschließlich den vollständigen Rev-D-Satz verwenden.
