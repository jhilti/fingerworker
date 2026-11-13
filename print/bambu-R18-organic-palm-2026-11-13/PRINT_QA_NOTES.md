# R18 – Druckprüfung

Geprüfter nativer Onshape-Stand: `13e353d6762b6cc58530122b`, FeatureScript SHA-256 `345b90327031276f8085e2c225c795946036d7faa4f2ac01b764101b9f4b3dd1`. P01 stammt bytegleich aus dem nativen STL-Archiv; die anderen fünf Druckmeshes sind unverändert. Native CAD-, Hub-, Service- und Q01-Prüfungen sind unter `validation/cad-R18-*` gebunden.

Vollständiger lokaler Slice mit Bambu Studio 2.8.2.61: **11 h 03 min 22 s, 239.38 g**, eine Platte, sechs Teile, keine Pausen, nur PLA. Linke Düse über manuelle Filamentzuordnung beibehalten. Das editierbare 3MF enthält alle Prozess- und Materialwerte des verbundenen R16-Projekts; nur P01 und der Projektname ändern sich. Die manuelle Zuordnung zur linken Düse bleibt unverändert.

Native Onshape-Geometrie und beide vollständigen lokalen Slices sind geprüft. Die abschließende sichtbare Bambu-Studio-Vorschau steht noch aus, weil der Mac gesperrt ist (GUI_PENDING_MAC_LOCKED). Kein Druckauftrag wurde gesendet.

- Meshkoordinaten, Topologie, Transformationen, vier massive Gurtmodifikatoren und alle beibehaltenen Profilwerte geprüft.
- Tatsächliche Extrusionsbahnen auf Druckbettgrenzen und gegenseitigen Abstand geprüft, einschließlich Stützenbreite.
- Keine Brim-/Skirt-Bahnen; zusammenhängende erste Schicht aller sechs Teile gegenüber R16 erhalten.
- Alle vier 25 × 2-mm-Gurtdurchlässe offen; 16 Gurtsteg-Kernbereiche über mindestens 20 Schichten zu mindestens 98 % von nominalen Materialbahnen bedeckt.
- Ganze Stützbahnbreiten und Schichthöhen von Handballenfläche, Krone, Daumenmulden und zentraler Schräge ausgeschlossen. Kleine Stützen unter den äußeren Schulterlippen bleiben außerhalb des Handkontaktbereichs.
- P04-Fingerzugfläche und Muldenboden frei von Stützenkontakt; übrige Gegenwand gezielt gestützt.
- Geschwindigkeiten, Beschleunigungen und Volumenfluss gegen das aktive PLA-Basic-Profil geprüft.

Die geometrische 45°-Wachstumsprüfung markiert kleine innere Schulterübergänge zur Nachprüfung. Die tatsächlichen Druckbahnen haben dort höchstens 1,58 mm Abstand vom nächstliegenden Rand der neuen Bahn zum Material der vorherigen Schicht, entsprechend einem Vorsprung von etwa 2 mm einschließlich der ganzen Bahnbreite; alle betroffenen Bahninseln sind in der vorherigen Lage verankert. Die längeren Bahnen bei Z24,2 liegen am bereits bestehenden 2-mm-Schulterüberstand. Native Schnitte und die vorhandene Geometrie stimmen dort überein. Die ursprüngliche 3-mm-Segmentprüfung bleibt als Prüfanlass dokumentiert und ist keine konstruktive Grenzvorgabe. Diese verdeckten Unterseiten können rauer werden; Ballenfläche, Krone und Daumenmulden bleiben frei von Stützenkontakt.

Frisch aus diesen Werkzeugwegen erzeugte Abbildungen: `preview/plate_1.png`, `preview/P01-contact-supports.png`, `preview/P04-Stuetzen.png` und `preview/P01-shoulder-bridges.png`; die Ersatzvariante hat entsprechende eigene Bilder unter `preview/P01-replacement`. Die zugehörigen Prüfsummen stehen in den Vorschau-Provenienzdateien.

Der offizielle CLI-Lauf beendet sich erfolgreich. Seine unveränderten herstellerspezifischen T1001/T65535/T65279-Parserdiagnosen und Preset-/Düsen-Kompatibilitätswarnungen sind vollständig in `validation/cli-diagnostics.json` dokumentiert und gegen den früheren offiziellen Lauf verglichen; das Log wird nicht als fehlerfrei bezeichnet.

Nominale Geometrie und Druckwege sind geprüft. Haftung, Layerfestigkeit, Dauerlast, Rastzyklen und Handkomfort erfordern den realen Ausdruck. P11 ist klein und ohne Brim; die erste Schicht auf sauberer PEI-Platte beobachten. Q01 nur federfrei verwenden. Kein Druckauftrag wurde gesendet.
