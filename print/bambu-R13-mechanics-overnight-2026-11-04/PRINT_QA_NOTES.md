# R13 – Prüfung der mechanischen Druckplatte

Geprüft wurde der aktuelle Slice mit sechs Teilen. Slicer-Schätzung: **11 h 13 min 05 s / 232.02 g PLA**, einschließlich Stützen und Brims.

Die native Projektprüfung bindet die sechs R13-Meshes, Druckausrichtungen, individuellen Einstellungen und die neue Profilkonfiguration an das Projekt. Die Werkzeugwegprüfung kontrolliert die tatsächlichen Extrusionswege einschließlich Stützen und Brims, Druckraumgrenzen und Abstände. Detailprüfungen betreffen Fingerkontaktflächen, Führungen, Klickarme, feste Sensorflächen und die Handballen-Unterseite.

- [Native Projektprüfung](validation/native-project-check.json)
- [Druckraum und Werkzeugwege](validation/toolpath-check.json)
- [Bauteil- und Klickmerkmale](validation/print-feature-check.json)
- [Handballenauflage und Stützzugänge](validation/palm-support-check.json)
- [P04-Fingeroberfläche](validation/p04-surface-check.json)
- [Slicer-Diagnosen](validation/cli-diagnostics.json)
- [Unabhängige Profilprüfung](validation/independent-profile-review.json)

20 % Gyroid und geänderte Geschwindigkeiten erzeugen bewusst andere Füllwege als das vollständige R13-Druckprofil. Eine identische Füllwegabdeckung wird deshalb nicht behauptet. Die Geometrie bleibt unverändert; die tatsächlich gedruckten Funktionsbereiche und freien Stützzugänge sind separat geprüft.

P04 bleibt in der geprüften Stirnseitenlage. Stützen vor der Montage vollständig entfernen. P06 bleibt ohne Stützen. P08/P09 und gedruckte Führungsstangen sind nicht Bestandteil dieses Druckauftrags; vorhandene echte Stangen verwenden.

CAD-Quelle: `82b7d65708c46cd9d4b6ac271047eac2f638f0222451df99eae0780525edd851`. Die Berichte mit Präfix `cad-R13-` stammen aus der unveränderten R13-Freigabe vom 03.11.2026 und belegen Geometrie, Bewegungen und Service. Die neuen Druckberichte sind an das aktuelle Projekt, die Platzierung und den tatsächlichen Slice gebunden.

Das 3MF ist ein editierbares Projekt. Interne Prüfgcodes werden nicht ausgeliefert. Reale Passung, Oberfläche, Rastkraft, Stützentfernung, Festigkeit und Dauerverhalten sind noch nicht gemessen. Q01 bleibt ausschließlich eine federfreie Passhilfe.

[Vorschau am verbundenen H2D](validation/connected-gui-check.json)
