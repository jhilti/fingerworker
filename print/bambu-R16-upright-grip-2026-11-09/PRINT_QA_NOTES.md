# R16 – Druckprüfung

Geprüfter nativer Onshape-Stand: `d4421f391a091e249b08aeb1`, FeatureScript SHA-256 `1f492dd841c35a14f488be418e4f4dd8dea8edb63f3d321a492dc2ec3c907ab4`. P01 stammt bytegleich aus dem nativen STL-Archiv; die anderen fünf Druckmeshes sind unverändert. Native CAD-, Hub-, Service- und Q01-Prüfungen sind unter `validation/cad-R16-*` gebunden.

Vollständiger lokaler Slice mit Bambu Studio 2.8.2.61: **10 h 59 min 29 s, 238.18 g**, eine Platte, sechs Teile, keine Pausen, nur PLA. Linke Düse über manuelle Filamentzuordnung beibehalten. Das editierbare 3MF enthält alle Prozess- und Materialwerte des verbundenen R15-Projekts; nur P01, Projektname und die gegen automatische Umzuordnung festgehaltene Düsenwahl ändern sich.

Das finale Projekt wurde zusätzlich in Bambu Studio 2.8.2.61 geöffnet und frisch geslicet: eine Platte, sechs Teile, nur PLA 1 auf der linken Düse, rechts leer. Die GUI bestätigt 10 h 59 min und 238,18 g. Die Datei wurde dabei nicht neu gespeichert; kein Druckauftrag wurde gesendet.

- Meshkoordinaten, Topologie, Transformationen, vier massive Gurtmodifikatoren und alle beibehaltenen Profilwerte geprüft.
- Tatsächliche Extrusionsbahnen auf Druckbettgrenzen und gegenseitigen Abstand geprüft, einschließlich Stützenbreite.
- Keine Brim-/Skirt-Bahnen; zusammenhängende erste Schicht aller sechs Teile gegenüber R15 erhalten.
- Alle vier 25 × 2-mm-Gurtdurchlässe offen; 16 Gurtsteg-Kernbereiche über mindestens 20 Schichten zu mindestens 98 % von nominalen Materialbahnen bedeckt.
- Ganze Stützbahnbreiten und Schichthöhen von Handballenfläche, Krone, Daumenmulden und zentraler Schräge ausgeschlossen. Kleine Stützen unter den äußeren Schulterlippen bleiben außerhalb des Handkontaktbereichs.
- P04-Fingerzugfläche und Muldenboden frei von Stützenkontakt; übrige Gegenwand gezielt gestützt.
- Geschwindigkeiten, Beschleunigungen und Volumenfluss gegen das aktive PLA-Basic-Profil geprüft.

Frisch aus diesen Werkzeugwegen erzeugte Abbildungen: `preview/plate_1.png`, `preview/P01-contact-supports.png`, `preview/P04-Stuetzen.png`. Die zugehörigen Prüfsummen stehen in den Vorschau-Provenienzdateien.

Der offizielle CLI-Lauf beendet sich erfolgreich. Seine unveränderten herstellerspezifischen T1001/T65535/T65279-Parserdiagnosen und Preset-/Düsen-Kompatibilitätswarnungen sind vollständig in `validation/cli-diagnostics.json` dokumentiert und gegen den früheren offiziellen Lauf verglichen; das Log wird nicht als fehlerfrei bezeichnet.

Nominale Geometrie und Druckwege sind geprüft. Haftung, Layerfestigkeit, Dauerlast, Rastzyklen und Handkomfort erfordern den realen Ausdruck. P11 ist klein und ohne Brim; die erste Schicht auf sauberer PEI-Platte beobachten. Q01 nur federfrei verwenden. Kein Druckauftrag wurde gesendet.
