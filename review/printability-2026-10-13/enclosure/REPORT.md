# Druckbarkeitsprüfung: Auflage, Halbschalen, Elektronik, hintere Halter

Geprüfter Stand: Rev E, H2D, PETG, 0,4-mm-Düse, 0,20-mm-Schichten. Umfang: acht Bauteiltypen P02, P03a, P03b, P08, P09, P10, P060 und P061. Die übrigen Teile des Satzes werden separat geprüft.

Die vorhandenen Orientierungen dieser acht Typen bleiben erhalten. Die konkrete Schwachstelle ist die bisher nicht unterstützte USB-Öffnung der Elektronikwanne. Für P08 müssen normale Stützen auch auf dem Modell beginnen dürfen. Die hohen Handballenschalen brauchen einen breiteren Brim und geringere Beschleunigung. Die kleine Kabelklemme profitiert von einem kleinen Brim und langsamen Wänden.

| Teil | Orientierung | Feststellung / erforderliche Einstellung |
|---|---|---|
| P02 Auflage | Flache Unterseite auf Bett, Bolster oben | Große Bettauflage 3248 mm²; M4-Bohrungen senkrecht. Vorhandene lokale Stützen beibehalten, Material aus den zwei M2-Blindlöchern unten entfernen. |
| P03a / P03b Halbschalen | Längsachse senkrecht | Kein Support, keine Brücken. 86 mm hoch bei nur rund 20 mm² geometrischer Kontaktfläche pro Schale. Brim 6–8 mm, normale Druckbeschleunigung 1500 mm/s², Außen-/Innenwand höchstens 60 mm/s. |
| P08 Wanne | Boden unten, Öffnung oben | Boden und Hauptwände 1 mm. Montageohren sind bereits unterstützt. USB-Dach bisher echter 13-mm-Spannbereich ohne Stütze. `support_on_build_plate_only=0`; normale automatische Stützen einschließlich Modellkontakt. Stützen vor Einbau aus Öffnungen und unter Ohren entfernen. |
| P09 Deckel | Glatte Außenseite unten, Rippen oben | Richtige Orientierung, kein Support erforderlich. 0,8-mm-Grundhaut entspricht vier Schichten; Erhebungen bauen von dieser Haut auf. |
| P10 Kabelklemme | Platte flach, Bohrungen senkrecht | Kein Support/keine Brücke. Nur 27,6 mm² Kontaktfläche und fünf Schichten Höhe. 2-mm-Brim; Wände 40 mm/s, erste Schicht 20 mm/s, Beschleunigung 1000 mm/s². |
| P060 / P061 Halter | Sockelfläche unten, Schraubenlöcher senkrecht | Beste Abwägung: Schraubenlöcher und tiefe Kopfkanäle bleiben offen nach oben. Ø6,2-mm-Stabsockel seitlich erzeugt kurze Brücken; längster G-Code-Brückenabschnitt 6,466 mm. Brückengeschwindigkeit 25 mm/s; keine schwer zugänglichen Innenstützen einfügen. |

## Nachweise

Alle acht STLs sind geschlossene, positiv orientierte Volumenkörper. Die berechneten Bettflächen, Abmessungen und G-Code-Featurestatistiken stehen in `geometry-and-toolpaths.json`; das reproduzierbare Analyseprogramm ist `analyze.py`.

Für P08 wurde ein separates Projekt mit unveränderter Geometrie und ausschließlich geänderter Supportoption mit dem offiziellen Bambu Studio 02.08.02.61 geslict. Ergebnis: Rückgabecode 0. Im relevanten USB-Dachbereich enthält Rev E null Supportabschnitte, der Kandidat 65, darunter Interfacebahnen bei Z 7,15 und 7,35 mm direkt unter dem Dach. `usb-support-proof.json` enthält die konkreten Koordinaten; `tray_support_verification.gcode.3mf` und `tray_support_slice.log` sind der Nachweis.

Die 0,3-mm-Stoppwände innerhalb P08 sind dünn, werden aber vom Arachne-Slicer tatsächlich gedruckt: durchgehende Bahnen bei Y 48,09 und 117,35 mm auf Z 1,2 / 1,4 / 1,6 / 1,8 / 2,0 mm. Diese Positionierkanten beim Entgraten und Einsetzen schonen. Die 0,6-mm- und 0,8-mm-Führungsleisten sind ebenfalls vom breiteren Hauptboden getragen.

Eine um 90° um Y gedrehte Halterorientierung mit geschlossener Rückseite unten wurde geprüft und verworfen. Sie vergrößert zwar die Bettauflage von 174 auf 564 mm² und senkt die Höhe von 23,5 auf 8 mm, legt aber die langen Ø6,4-mm-Schraubenkopfkanäle waagerecht. Der Slicer erzeugt dann `Floating vertical shell` und deutlich mehr Brücken (bis 11,93 mm Einzelabschnitt, etwa 1,25 m Brückenpfad pro Halter). In der ursprünglichen Orientierung gibt es diese schwebenden Schalen nicht; etwa 0,21 m Brückenpfad und 6,466-mm-Einzelabschnitte sind günstiger. Kandidaten unter `caps_orientation_*` dienen ausschließlich der Prüfung und sollen nicht ausgeliefert werden.

Bei P02 taucht ein Brückenabschnitt von rund 34 mm in den internen Füll-/Decklagen auf. Dieses G-Code-Feature misst den extrudierten Pfad, nicht die tatsächlich frei überspannte Strecke: vorhandene Füllung und umliegende Wände tragen diese Lagen. Das ist nicht der zuvor fehlerhaft orientierte 33,5-mm-Passprobenkanal.

Die Prüfung bewertet Druckgeometrie, Ausrichtung und Slicerbahnen. Tatsächliche Haftung, Maßhaltigkeit und Supportablösung hängen weiterhin von dem vorhandenen Filament und dem gedruckten Ergebnis ab.
