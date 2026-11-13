# R13 – Prüfung der gemeinsamen Druckplatte

Geprüft wurde das neue Ein-Platten-Projekt mit allen zehn Teilen, nicht lediglich die Summe der vorherigen Einzelplatten. Die native Projektprüfung bestätigt die richtige H2D-Konfiguration, die zehn Quellmeshes, unveränderte Geometrie und die finale Anordnung. Sämtliche Teile sind im tatsächlichen Slice enthalten.

Slicer-Schätzung: **18 h 15 min 54 s / 273.10 g PLA** einschließlich Stützen und Brims.

Die Werkzeugwegprüfung kontrolliert Druckraumgrenzen und Abstände der tatsächlichen Extrusionswege einschließlich Stützen und Brims. Detailprüfungen decken die Fingerkontaktflächen, Führungen, Klickarme, festen Sensorflächen und die Handballen-Unterseite ab. Konkrete Toleranzen und Einzelwerte stehen in den beigefügten JSON-Berichten.

- [Native Projektprüfung](validation/native-project-check.json)
- [Druckraum und Werkzeugwege](validation/toolpath-check.json)
- [Bauteil- und Klickmerkmale](validation/print-feature-check.json)
- [Handballenauflage und Stützzugänge](validation/palm-support-check.json)
- [P04-Fingeroberfläche](validation/p04-surface-check.json)
- [Slicer-Diagnosen](validation/cli-diagnostics.json)
- [Gedruckte Modellbereiche](validation/model-coverage-check.json)
- [Unabhängige Prüfung der Nahtabweichungen](validation/model-coverage-independent-review.json)
- [Vorschau am verbundenen H2D](validation/connected-gui-check.json)

P04 bleibt in seiner geprüften Stirnseitenlage. Stützen vor der Montage vollständig entfernen. P09 und die hintere Traverse bleiben separat und ohne Stützen. Die neue gemeinsame Anordnung ändert keine Montagefunktion und entfernt keine Funktionshardware.

CAD-Quelle: `82b7d65708c46cd9d4b6ac271047eac2f638f0222451df99eae0780525edd851`. Die Berichte mit Präfix `cad-R13-` stammen aus der unveränderten R13-Freigabe vom 03.11.2026. Sie belegen Geometrie, Bewegungen und Service. Die Ein-Platten-Berichte sind separat an das neue Projekt, die Platzierung und den tatsächlichen Slice gebunden.

Das 3MF ist ein editierbares Projekt. Interne Prüfgcodes werden nicht ausgeliefert. Die Prüfungen bescheinigen nominelle Geometrie und berechnete Werkzeugwege; reale Passung, Oberfläche, Rastkraft, Stützentfernung und Belastbarkeit wurden nicht gemessen.

Der Diagnosebericht erfasst die bekannten Meldungen der unveränderten H2D-Herstellermakros ausdrücklich. Der finale Ein-Platten-Lauf fügt gegenüber der R13-Referenz keine neue Diagnose hinzu und endet mit Code 0.
