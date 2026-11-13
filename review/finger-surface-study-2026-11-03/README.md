# P04: saubere Fingerauflage, PLA allein

Empfohlene Baulage für R11: **vordere Stirnseite auf das Bett**, Muldenboden senkrecht. Bambu-Stützen: **Baum automatisch / schlank / nur vom Druckbett**, 5 mm Außenbrim, oberer Z-Abstand 0,25 mm. H2D, angenommene Standarddüse 0,4 mm, PLA, 0,2 mm Schichten. Geometrie und Montageposition bleiben unverändert; es entsteht kein Zusatzteil.

Das native Einzelprojekt ist `P04_H2D_04mm_PLA_clean_finger_surface.3mf`. Es enthält das Modell und editierbare Einstellungen, keinen vorab zum Drucker gesendeten Auftrag. Bambu Studio 02.08.02.61 hat die Platte erfolgreich gesliced: **4 h 20 min, 65,21 g PLA**, einschließlich Stützen/Brim. Diese Werte sind Slicer-Schätzungen.

## Warum die neue Lage hilft

Die belastete Fingerzugwand ist in CAD X77, im konfigurierten STL wegen der 5-mm-Verschiebung X72. Der Muldenboden liegt Z10. In der bisherigen Lage Xmax unten war die Zugwand eine gestützte Unterseite. Nur die Stirnseite umzudrehen reicht mit normalen automatischen Stützen nicht: Diese starten dann auf der Fingerzugwand und hinterlassen wieder Spuren.

Die geprüften Bett-Baumstützen erreichen die gegenüberliegende Wand durch die offene Mulde. Auf der Fingerzugfläche starten keine Stützen. Die Zugwand endet als Topfläche; Boden und Führung stehen senkrecht. Im echten Werkzeugweg wurden kein Support, kein Interface und kein Übergang in den geprüften Hauptkontaktflächen, der vorderen Rundlippe, der vorderen Bodenrundung, den seitlichen Muldenradien, der zentralen Führung oder den inneren Ø8-Stangenbohrungen gefunden. Die automatische Stützung der gegenüberliegenden, nicht als Zugkontakt gedachten Muldenwand bleibt erforderlich.

`support-path-evidence.png` zeigt echte Supportwege. Die graue Kontur ist der Mittelschnitt Y0; blaue Stützen sind eine Projektion aus |Y| < 28 mm. Projektionen können vor der Kontur liegen, ohne dort Material zu berühren, etwa beim tatsächlich ausgeschnittenen Cam-Schraubenkopfslot.

## Alternativen im Vergleich

| Baulage | Ergebnis |
| --- | --- |
| Bisher: Xmax hinten unten | Zugwand stützpflichtige Unterseite; dort wurden 27 Interface-Segmente und 30 Bridge-Segmente im Kern gefunden. |
| Xmin vorne unten + Normalstützen überall | Zugwand wird Topfläche, aber 39 Interface-Segmente starten darauf. Nicht als Oberflächenlösung freigegeben. |
| **Xmin vorne unten + Bett-Baumstützen** | **Gewählt.** Zugwand, Boden, Lippenkern, Führung und Stangenbohrungen frei von Supportkontakt in den geprüften Werkzeugwegregionen. |
| Mulde nach oben, Original-Z oben | Gute Fingerflächen und für Zug in X günstige Schichtebene; Stützen liegen jedoch in der flachen, untergeschnittenen Führung und den waagrechten Stangenbohrungen. Erschwerte Entfernung und Maßhaltigkeit. |
| Seitenlage | 126 mm Bauhöhe, nur 182 mm² geometrischer Erstkontakt; Stützen in Führung und Bohrungen. Kein Vorteil gegenüber der gewählten Lage. |

## Entfernen und montieren

1. P04 einzeln mit den geprüften Einstellungen drucken. Eine eigene Platte erhält die geprüfte Baumgeometrie und vereinfacht die Sichtkontrolle.
2. Brim und außenliegende Baumstützen vollständig entfernen. Stützen aus der Mulde durch die große Öffnung herauslösen, bevor der Griff montiert wird. Stützen aus der offenen Cam-Schuh-Tasche entfernen.
3. Führung und beide Stangenbohrungen auf Reste prüfen. Die Fingerzugwand und der Boden sollen keine abgerissenen Stützansätze tragen.
4. P04 in unveränderter Konstruktionslage von hinten auf die Grundplatte schieben. P05 bleibt in Form und Montageposition unverändert. Die Druckrotation ist keine Änderung der Montageausrichtung.

PLA genügt für diese Oberflächenverbesserung. Kein zusätzlicher Werkstoff und keine kleinen Abdeckteile nötig. Der Druck muss die reale Oberfläche und Entfernbarkeit noch bestätigen. Die Baulage legt Schichtnormalen weiterhin entlang X; die Studie ersetzt daher keine Belastungsprüfung eines vollständig gedruckten, vorgespannten Geräts.

## Reproduzierbare Nachweise

- `validation.json`: genau geprüfte Supportregionen und echte Extrusionswege.
- `project-validation.json`: native Einstellungen und Mesh-Roundtrip: maximal 0,000004 mm Abweichung.
- `front_tree_bed/result.json`: nativer Slicer-Erfolg, Rückgabecode 0.
- `check_p04_supports.py`: wiederverwendbare Prüfung mit beliebiger Plattenposition und starrem Drucktransform.
- `build_study.py`, `build_support_study.py`, `finalize_study.py`: isolierte Studien; historische Pakete bleiben unverändert.

```sh
/tmp/fingerworker-r10-venv/bin/python check_p04_supports.py \
  --gcode /absoluter/pfad/verification.gcode.3mf --plate 3 \
  --rotation '[[0,0,-1],[0,1,0],[1,0,0]]' \
  --translation '[30,63,-60]' --xy '[100,80]' \
  --output /absoluter/pfad/p04-surface-check.json
```
