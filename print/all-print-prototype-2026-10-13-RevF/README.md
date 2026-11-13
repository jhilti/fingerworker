# Fingerworker - H2D-Druckprojekt Rev F, 13.10.2026

**[Vorbereitetes H2D-3MF](../bambu-2026-10-13-RevF/Fingerworker_RevF_H2D_04mm_PETG.3mf) als Projekt öffnen.** Es enthält 30 Geräteteile und zwei Führungs-Passproben auf sechs vorbereiteten Platten. Alle 25 Geräteteiltypen und beide Proben sind auf Drucklage, Bettauflage, Überhänge, Brücken, dünne Bereiche und Stützenzugang geprüft.

Eingestellt: **H2D, Standarddüsen 0,4 mm, PETG, Textured PEI**, 0,20-mm-Schichten, vier Wände, fünf Boden-/Deckschichten, 30 % Gyroid. Individuelle H-Anschauungsteile und Passproben sind vollständig gefüllt. Die vier 1,5-mm-Puffer erhalten einzeln 0,10-mm-Schichten und volle Füllung. Arachne druckt die dünnen Abstandshülsen. Die 0,4-mm-Düsen bleiben die bisherige Standardannahme; mit dem tatsächlich eingebauten Werkzeug abgleichen.

Das Qualitätsprofil nutzt 20 mm/s für die erste Schicht, 60 mm/s Außenwände, 100 mm/s Innenwände und 25 mm/s kurze Brücken. Modellbeschleunigung höchstens 1500 mm/s². Kleine P10/H19/H22/P07-Teile drucken höchstens 40 mm/s, hohe Halbschalen und H14-Hülsen höchstens 60 mm/s. Diese Grenzen sind in den erzeugten Bahnen überprüft. Der vollständige Satz ist laut Slicer etwa **26 h 25 min / 372 g PETG**, einschließlich Stützen, Haftungsrändern und Passproben.

Kein TPU erforderlich. Alle sechs Platten verwenden ein PETG-Filament. Das Filamentprofil auf die tatsächlich verwendete Spule abstimmen. Für PLA ein passendes PLA-H2D-Profil wählen und neu slicen; die hier protokollierte Prüfung verwendet PETG. Das Projekt enthält keine gedruckten Schrauben, Muttern, Inserts oder Scheiben. Federn, Sensor, PCB und Akku bleiben Kaufteile.

## Änderungen gegenüber Rev E

- **P04:** hintere Stirnseite unten. Längsführung und Stabbohrungen werden aufrecht gedruckt; die ursprüngliche breite Führungsdecke entfällt. Stützen auch auf dem Modell, zugänglich durch Griffmulde und offene Führungsunterseite. Brim 5 mm.
- **P05:** hintere Rippe unten. Stützen ausschließlich vom Bett halten die äußeren Schultern, ohne die Druckstift-/Führungsbohrungen zu füllen. Brim 5 mm.
- **H12:** flache Seitenkante unten; größere Auflage und Stützen in der offenen Sensortasche. **H02:** Ø4-Ende unten, zugängliche Schulterstützen. Je 3-mm-Brim.
- **P08:** normale Stützen dürfen auch auf dem Modell beginnen. Unter dem bisher freien USB-Dach sind jetzt echte Stützen einschließlich Kontaktlagen vorhanden.
- **P03a/P03b:** 8-mm-Brim, langsame Wände. Kleine H19/H22/P10 sowie harte P07-Puffer erhalten passende Haftungsränder und langsamere Bahnen.
- **P07:** lokale 0,10-mm-Schichten erzeugen 1,50 mm statt zuvor 1,40 mm Höhe. Der Rest der Platte behält die normalen Schichten.

Die vier Neuausrichtungen sind **starre Drehungen**; Nenngeometrie, Passmaße und CAD-Form sind unverändert. Hintere Halter bleiben in ihrer bewährten aufrechten Drucklage, damit die tiefen Schraubenkopfkanäle senkrecht bleiben. Die Rückseite-unten-Alternative wurde geslict und wegen schwebender Wände verworfen. Auch H15 bleibt in seiner bisherigen Lage.

## Platten und Druck

| Platte | Inhalt | Anzahl |
|---|---|---:|
| 1 | Führungs-Passprobe männlich / weiblich | 2 |
| 2 | Grundplatte 6 mm und zwei Führungsstäbe | 3 |
| 3 | Griff, Federjoch, Handballenauflage, hintere Halter | 5 |
| 4 | Elektronikaufnahme und kleine Anschauungsteile | 14 |
| 5 | Zwei optionale Isometriehülsen | 2 |
| 6 | Zwei starre Halbschalen und vier 1,5-mm-Puffer | 6 |
| **Gesamt** | **30 Geräteteile + zwei Passproben** | **32** |

1. Projekt öffnen, tatsächliche Düse/Druckplatte/Filament prüfen. Maßstab 100 %, gespeicherte Lage beibehalten. Keine automatische Neuausrichtung.
2. Die Passproben aus Rev E sind unverändert. Weibliche Probe mit geschlossener Rückseite unten und Kanal oben drucken; zum Zusammenschieben danach umdrehen. Eine bereits brauchbare männliche Probe muss nicht neu gedruckt werden.
3. Vor dem großen Druck die Führungspassung beurteilen. Jede neue Platte in der Vorschau auf erste Schicht, Bohrungen und Stützen prüfen. Brims und unterstützte Bereiche sind im Projekt gesetzt; ihre Flächen passen mit Reserve zwischen die Objekte.
4. Stützen und Brims gemäß [Prüfbericht](Druckbarkeitspruefung_RevF.pdf) beziehungsweise [PRINTABILITY.md](PRINTABILITY.md) entfernen. Erst danach gemäß [MONTAGE.md](MONTAGE.md) federfrei montieren.

Das 3MF ist ein bearbeitbares Projekt; Prüfgcode wird nicht ausgeliefert. Die normalen 0,20-mm-Schichten runden manche Gesamthöhen um etwa 0,10 mm. Die dünnen P07-Puffer verwenden ausdrücklich feinere Schichten. Reale Drucktoleranzen und Haftung am Muster prüfen.

## Gültigkeit und Nachweise

Die Grundplatte bleibt 6 mm dick, ohne Seilhalter, mit abgesenkten hinteren Sockeln. P060/P061 haben durchgehende M3-Bohrungen. P01/P060/P061 gemeinsam als aktuellen Satz verwenden. Die Funktions-CAD-Quelle bleibt Rev C, die geteilten starren Schalen sind die vorhandene Anschauungsvariante. Der neue Drucksatz heißt Rev F.

Die 27 verschiedenen Netze (25 Gerätetypen und zwei Proben) sind geschlossen, quantitativ korrekt und ohne Skalierung importiert. Alle 32 Objekte besitzen direkte Erstschichtbahnen und vollständige Modellbahnen. Alle sechs Platten wurden mit Bambu Studio 02.08.02.61 erfolgreich für den H2D geslict. Die tatsächlichen Bahnen bestätigen Geschwindigkeit, Beschleunigung und Pufferhöhe. Nominale Montage: weiterhin 15 Wege / 235 Stellungen / acht Schraubenfreiräume, da die Geometrie unverändert bleibt.

Der Satz dient der **Form- und Montagebeurteilung ohne Federn**. Gedruckte Stäbe und H-Formen sind keine geprüften Metallersatzteile, ihre glatten Hüllformen/Kernlöcher keine funktionierenden Gewinde. Das vereinfachte H13-Handrad hat keinen Schraubenschaft. Harte Puffer dämpfen nicht wie Elastomer, Schalen werden zur Beurteilung mit Klebeband gehalten. P04s neue Lagenrichtung verlangt vor einer späteren Version unter Federlast eine eigene Festigkeitsentscheidung.

Nachweise: `bambu-validation.json` (natives Projekt/Slicing), `stl-validation.json` (Netze und starre Transformationen), `toolpath-validation.json` (32 reale Objekte, Geschwindigkeiten/Höhen), `support-validation.json` (USB-Stützen), `assembly-validation.json`, `Druckliste.json` (Herkunft und SHA-256) sowie `PRINTABILITY.md` mit einer Entscheidung für jeden Typ.

Einzel-STLs liegen unter `PETG/`; jede enthält ein Exemplar, in mm und in geprüfter Drucklage. Mengen nach `Druckliste.csv` berücksichtigen. `source/build_pack.py` reproduziert die starren Drehungen aus dem vollständigen Vorgängersatz im Repository. Die native 3MF-Prüfung liegt im zugehörigen Bambu-Ordner.
