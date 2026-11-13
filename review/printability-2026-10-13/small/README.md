# Druckbarkeitsprüfung der kleinen Teile, 13.10.2026

Geprüft: H02, H04, H05, H06, H12, H13 (nur Handrad), H14, H15, H19, H22 und alle vier P07-Puffer. Ausgangspunkt ist das PETG-Paket Rev D mit dem echten Bambu-Studio-Projekt Rev E. Die Prüfung gilt für die Form- und Montagebeurteilung, ohne Federlast. Metallteile bleiben Druck-Anschauungsteile.

Die Geometrie wurde auf geschlossene Volumenkörper, ebene Auflageflächen, hohe Unterseiten, zugängliche Stützen und dünne Wände geprüft. Die Kandidaten wurden mit dem offiziellen Bambu Studio 02.08.02.61, H2D, zwei Standarddüsen 0,4 mm und PETG geslict. `check_gcode.py` wertet tatsächlich extrudierte Geraden und Kreisbögen je Objekt und Feature aus; Fahrbewegungen und Haftungsränder zählen nicht zur direkten Auflage.

## Empfohlene Änderungen

| Teil | Ausrichtung und Einstellungen | Grund / überprüfte Wirkung |
|---|---|---|
| H02 Druckstift | Aktuelle STL um −90° um Y drehen, danach auf Z0 setzen. Ø4-Ende unten, Stiel oben. Normalstützen nur vom Bett, 3-mm-Außenbrim. | Bisher nur 3,40 mm direkte Erstschicht-Bahn auf der Rundung; stehend 22,42 mm. Ebene geometrische Auflage 12,56 mm². Stützen unter der frei erreichbaren Ø8-Schulter, längster Slicer-Brückenabschnitt 4,47 mm. |
| H12 Sensorkassette | Aktuelle STL +90° um Y drehen und auf Z0 setzen. Normalstützen auch auf dem Objekt zulassen, 3-mm-Außenbrim. | Auflage 35,00 → 130,40 mm². Die 531,7-mm²-Unterseite in 3,2 mm Höhe verschwindet. Längster Slicer-Brückenabschnitt 23,675 → 7,316 mm. Die nötigen Stützen liegen in der seitlich offenen, 1,6 mm tiefen Sensorvertiefung und sind von deren offener Seite erreichbar. |
| H19 Abstandshülsen | Vorhandene flache Stirnfläche unten; Arachne beibehalten. 3-mm-Außenbrim, Außenwände 40 mm/s, erste Schicht 20 mm/s. | Wand nur 0,4 mm bei Ø4 / Bohrung Ø3,2; Slicer erzeugt die komplette, durchgehende Einzelwand mit etwa 0,384–0,416 mm Linienbreite. Kleine 4,52-mm²-Auflage benötigt Haftungsrand. Brim vorsichtig von außen entfernen, Bohrung frei halten. |
| H22 Druckstück | Vorhandene flache Scheibenfläche unten; 3-mm-Außenbrim, Außenwände 40 mm/s, erste Schicht 20 mm/s. | Sehr kleines Ø2,5 × 1-mm-Teil, Auflage 4,91 mm². Form wird vollständig geslict; Haftungsrand erleichtert Entnahme. |
| P070a/b, P071a/b | Vorhandene flache Rechteckfläche unten. **Nur an diesen Objekten** Schichthöhe 0,1 mm einstellen; erste Schicht bleibt 0,2 mm. | Quelle 1,5 mm dick; bisherige 0,2-mm-Schichtung endete bei 1,4 mm. Test mit Objekt-Override endet bei exakt Z1,50 mm für alle vier Puffer; zugleich bleibt die 86-mm-Hülse auf derselben Testplatte bei 0,2-mm-Schichten. Kein Bedarf, ganze Platte 6 auf 0,1 mm umzustellen. |

Die globale experimentelle Option `precise_z_height` wird nicht benötigt. Ihr offizieller Hinweis bezeichnet sie als experimentell; der lokal getestete Objekt-Override erfüllt die erforderliche Pufferdicke.

## Beibehaltene Ausrichtungen

| Teil | Befund |
|---|---|
| H04 Führungsstäbe | Liegend beibehalten. Die ebene geometrische Kontaktfläche ist null, die physische 0,2-mm-Erstschicht erzeugt jedoch je Stab 291,25 mm direkte Bahn mit 0,6384-mm-Breite, plus vorhandenen 3-mm-Haftungsrand. Keine Brücken- oder Stützbahnen im realen Rev-E-G-Code. Ein stehender Ø6 × 146-mm-Stab wäre unnötig hoch und schlank. Unterseite nach dem Druck vorsichtig entgraten; Form-/Montageprobe. |
| H05 / H06 Federsitze | Scheibenfläche unten: 345,87 / 329,82 mm² Auflage; keine hohen Deckflächen und keine Slicer-Brücken. Bohrungen laufen vertikal. |
| H13 Handrad | Flache Ringfläche unten: 347,91 mm² Auflage; keine Brücken. Nur Radform; kein gedruckter Schraubenschaft. |
| H14 Isometriehülsen | Axial stehend: 150,77 mm² Ring-Auflage, 86 mm hoch. Keine Überhänge/Brücken, vorhandener 3-mm-Außenbrim ausreichend für diesen schlankeren, aber Ø16-mm-breiten Körper. Bohrung senkrecht/offen. |
| H15 Halteplatte | Bisherige flache Rückseite unten belassen. Keine Brücken. Eine testweise 180°-Drehung vergrößerte zwar den flachen Kontakt, erzeugte aber neue bis 7,022 mm lange Brücken an den Vertiefungen; deshalb verworfen. |
| P07 Puffer | Flach, 27,0 mm² Auflage, keine Brücken. Starres PETG/Pla stellt die Form dar und bietet keine TPU-Rücklaufdämpfung. |

## Nachweise

- `geometry-metrics.json`: Quellhashes, Abmessungen, Kontaktflächen, Unterseiten und Kandidaten.
- `gcode-metrics.json`: Reale Extrusions-Features je Objekt für Rev E, Orientierungsprobe und Probe mit feineren P07-Schichten / Stützen in der H12-Tasche.
- `candidate/`: Rigid gedrehte H02-/H12-STLs und übrige Kontrollteile. **H15 darin ist ein verworfener Drehversuch und wird nicht zur Ausgabe empfohlen.**
- `Small_candidate-verification.gcode.3mf`: Isolierte Orientierungsprobe (14 Typen).
- `Small_finepads-verification.gcode.3mf`: P07 mit objektspezifischem 0,1-mm-Override, H12 mit Stützen auch auf Objekt (14 Typen).
- `review_small.py` / `check_gcode.py`: reproduzierbare Geometrie- und G-Code-Auswertung.

Die genauen Temperaturen folgen dem bestehenden offiziellen H2D-PETG-Profil. Gedruckte H04-/H12-/H05-/H06-Teile sind nicht für die bestellten Federn unter Last freigegeben. Die Prüfung macht Druckanordnung und Entfernen der Stützen konkret; sie ersetzt keine physische Druck- und Passkontrolle.
