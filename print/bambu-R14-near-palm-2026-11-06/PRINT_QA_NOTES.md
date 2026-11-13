# R14 – Prüfung der mechanischen Druckplatte

Geprüft wurde der aktuelle Slice mit sechs Teilen. Slicer-Schätzung: **11 h 32 min 24 s / 242.34 g PLA**, einschließlich Stützen und Brims.

Die native Projektprüfung bindet die sechs aktuellen Druckmeshes, Druckausrichtungen und erklärten Einstellungen an das Projekt. Die Werkzeugwegprüfung kontrolliert die tatsächlichen Extrusionswege einschließlich Stützen und Brims, Druckraumgrenzen und Abstände. Detailprüfungen betreffen Fingerkontaktflächen, Führungen, Klickarme, feste Sensorflächen und die Handballen-Unterseite.

- [Native Projektprüfung](validation/native-project-check.json)
- [Druckraum und Werkzeugwege](validation/toolpath-check.json)
- [Bauteil- und Klickmerkmale](validation/print-feature-check.json)
- [Handballenauflage und Stützzugänge](validation/palm-support-check.json)
- [Vier freie Gurtöffnungen und dichte Ösen](validation/strap-slot-check.json)
- [Gurtführung und Bewegungsraum](validation/strap-routing-check.json)
- [P04-Fingeroberfläche](validation/p04-surface-check.json)
- [Slicer-Diagnosen](validation/cli-diagnostics.json)
- [Unabhängige Profilprüfung](validation/independent-profile-review.json)

Die neue P01-Geometrie und der tatsächliche Slice werden gemeinsam geprüft. Die übrigen Teile behalten ihre nativen Funktionen. Die Kontaktflächen, freien Stützzugänge und berechneten Druckwege sind separat geprüft; gleicher Handkomfort oder gleiche Festigkeit werden daraus nicht abgeleitet.

P04 bleibt in der geprüften Stirnseitenlage. Stützen vor der Montage vollständig entfernen. P06 bleibt ohne Stützen. P08/P09 und gedruckte Führungsstangen sind nicht Bestandteil dieses Druckauftrags; vorhandene echte Stangen verwenden.

CAD-Quelle: `9286d5a51880dc79d1e9a07135e8c905f4022a1ed757801b8430f23f51a04829`. Die Berichte mit Präfix `cad-R14-` belegen die aktuelle native Geometrie, Bewegungen und Service dieser R14-Revision. Die neuen Druckberichte sind an das aktuelle Projekt, die Platzierung und den tatsächlichen Slice gebunden.

Das 3MF ist ein editierbares Projekt. Interne Prüfgcodes werden nicht ausgeliefert. Reale Passung, Oberfläche, Rastkraft, Stützentfernung, Festigkeit und Dauerverhalten sind noch nicht gemessen. Q01 bleibt ausschließlich eine federfreie Passhilfe.

[GUI-Prüfstand: bestehendes Nutzerprojekt erhalten](validation/gui-check.json). Kein neuer GUI-Slice-Nachweis; offizielle CLI-Prüfung und tatsächliche Druckwege sind oben dokumentiert.
