# R15 – Prüfung der mechanischen Druckplatte

Geprüft wurde der aktuelle Slice mit sechs Teilen. Slicer-Schätzung: **10 h 59 min 19 s / 230.01 g PLA**, einschließlich der erforderlichen Stützen; ohne Modellbrims.

Die native Projektprüfung bindet die sechs aktuellen Druckmeshes, Druckausrichtungen und erklärten Einstellungen an das Projekt. Die Werkzeugwegprüfung kontrolliert die tatsächlichen Extrusionswege einschließlich der erforderlichen Stützen; ohne Modellbrims, Druckraumgrenzen und Abstände; der aktuelle Slice enthält keine Modellbrims. Detailprüfungen betreffen Fingerkontaktflächen, Führungen, Klickarme, feste Sensorflächen und die Handballen-Unterseite.

- [Native Projektprüfung](validation/native-project-check.json)
- [Druckraum und Werkzeugwege](validation/toolpath-check.json)
- [Bauteil- und Klickmerkmale](validation/print-feature-check.json)
- [Handballenauflage und Stützzugänge](validation/palm-support-check.json)
- [Vier freie Gurtöffnungen und dichte Ösen](validation/strap-slot-check.json)
- [Gurtführung und Bewegungsraum](validation/strap-routing-check.json)
- [P04-Fingeroberfläche](validation/p04-surface-check.json)
- [Alle sechs Modelle ohne Brim](validation/no-brim-check.json)
- [Slicer-Diagnosen](validation/cli-diagnostics.json)
- [Unabhängige Profilprüfung](validation/independent-profile-review.json)

Die neue P01-Geometrie und der tatsächliche Slice werden gemeinsam geprüft. Gegenüber R14 ändern sich nur P01, die lokalen Füllbereiche und die ausdrücklich entfernten Brims aller sechs Teile. Die übrigen Teile behalten ihre nativen Funktionen. Die Kontaktflächen, freien Stützzugänge und berechneten Druckwege sind separat geprüft; gleicher Handkomfort oder gleiche Festigkeit werden daraus nicht abgeleitet.

P04 bleibt in der geprüften Stirnseitenlage. Stützen vor der Montage vollständig entfernen. P06 bleibt ohne Stützen. P08/P09 und gedruckte Führungsstangen sind nicht Bestandteil dieses Druckauftrags; vorhandene echte Stangen verwenden.

CAD-Quelle: `97e2010cc17d06eb8648cf278b9aae2fd85b6e909bd657b9b216f3b37748665f`. Die Berichte mit Präfix `cad-R15-` belegen die aktuelle native Geometrie, Bewegungen und Service dieser R15-Revision. Die neuen Druckberichte sind an das aktuelle Projekt, die Platzierung und den tatsächlichen Slice gebunden.

Das 3MF ist ein editierbares Projekt. Interne Prüfgcodes werden nicht ausgeliefert. Erstschichthaftung ohne Brims ist am realen Drucker zu bestätigen. Reale Passung, Oberfläche, Rastkraft, Stützentfernung, Festigkeit und Dauerverhalten sind noch nicht gemessen. Q01 bleibt ausschließlich eine federfreie Passhilfe.

[GUI-Import und Plattenanordnung bestätigt](validation/gui-check.json). Die GUI-Slice-Vorschau blieb wegen der aktiven AMS-Filamentzuordnung offen. Die aktuelle Schätzung und tatsächlichen Druckwege wurden mit der offiziellen CLI vollständig geprüft. Kein Druckauftrag wurde gestartet.
