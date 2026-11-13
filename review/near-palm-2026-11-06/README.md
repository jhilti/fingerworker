# Flat132 R14 – griffnahe Handballenauflage und Gurtaufnahme

<!-- RELEASE_STATUS_START -->
**Nominale R14-CAD- und PLA-Druckprüfung bestanden.** Native Geometrie, voller Hub, Sensorservice, Q01-Passung und der tatsächliche H2D-Slice sind an diese Revision gebunden. Reale Reichweite, Handkomfort, Rastkraft und Belastbarkeit bleiben am Ausdruck zu prüfen.
<!-- RELEASE_STATUS_END -->

Die neue breite Rundung sitzt direkt an der Sensorwand und gehört zum einteiligen Rahmen P01. Der äußere R13-Handballenbalken entfällt. Die Hand kann damit näher am Fingergriff aufliegen, ohne ein zusätzliches Druckteil oder eine Schraubverbindung. Vier gerundete Öffnungen in integralen äußeren Ösen schaffen zwei Befestigungspositionen für echte 25-mm-Gurte; Gesamtbreite 156 mm. Die ursprüngliche Grundplatte bleibt ungeschnitten. Die bevorzugte Reichweite und der Handkomfort werden am neuen Ausdruck beurteilt.

**Gegenüber R13 nur P01 neu drucken.** P04, P05, P06, P08, P09, P11 und Q01 bleiben geometrisch kompatibel. Die vollständige native Baugruppe enthält 93 Körper, davon sieben Gerätedruckteile; 92 Körper außer P01 sind exakt unverändert.

Der aktuelle mechanische Drucksatz enthält **sechs Stücke auf einer Platte**: P01, P04, P05, P06, P11 und die federfreie Sensor-Passhilfe Q01. Vorhandene echte Führungsstangen verwenden. Elektronikwanne, Deckel und gedruckte Stangen werden diesmal weggelassen. Es kommen keine kleinen Montageteile hinzu.

[Onshape R14](https://cad.onshape.com/documents/15316cc6370631845af136b2/v/05c07284f9a5edf33d05f680/e/d253eb87b70818ebde8215f0) · [Bambu-Projekt](../../print/bambu-R14-near-palm-2026-11-06/Fingerworker_R14_H2D_04mm_PLA_Near_Palm.3mf) · [Druckpaket](../../print/bambu-R14-near-palm-2026-11-06/Fingerworker_R14_H2D_04mm_PLA_Near_Palm_Package.zip) · [HTML-Übersicht](../../Uebersicht.html)

[Montage](MONTAGE.md) · [Änderungsreview](parts-review.md) · [Stücklistenänderungen](BOM_Aenderungen.csv) · [Konstruktionsmaße](mechanics/design-specification.json) · [Finale Spezifikation](final-specification.json)

Sensor-Kraftpfad, voller 30-mm-Hub, 15-mm-ISO-Anfahrweg, Rastfunktionen, Elektronikzugänge und Sensorservice sind nominal geprüft. Beide Vorspannverstellungen bleiben entfernt. Q01 bleibt eine unbelastete Passhilfe und wird vor Sensor-/Federeinbau entfernt.

H2D / PLA / 0,4-mm-Standarddüse, vier Wände und 20 % Gyroid; die vier Gurtösen samt kurzem Wurzelbereich sind lokal mit 100 % gefüllt. Die vier Modifikatoren im 3MF sind keine zusätzlichen Druckteile. Das 3MF als Projekt öffnen, damit die individuellen Einstellungen und Stützen erhalten bleiben. Tatsächlicher Slice: **11 h 32 min 24 s / 242.34 g PLA** einschließlich Stützen und Brims. P04 behält seine bewährte Lage mit freien Fingerkontaktflächen.

<!-- STRAP_ROUTING_START -->
## Befestigung mit zwei Gurten

Vier integrale, flache Ösen liegen außen an P01: je zwei bei **X5 und X80 mm**, also **75 mm auseinander**. Die gerundeten Öffnungen sind **27 × 4 mm** groß und liegen bei Y±69,5. Der Rahmen ist einschließlich Ösen **156 mm breit**; die ursprüngliche 132-mm-Grundplatte und ihre Führung werden dafür nicht durchtrennt.

Benötigt werden **zwei echte 25-mm-Gurte**, höchstens **2 mm dick** im Durchlass. Beide Enden jedes Gurts müssen sich zurückfalten und sicher an sich selbst befestigen lassen, etwa mit dafür geeignetem selbsthaftendem Gurtband. Die passende Länge richtet sich nach dem Gegenstand beziehungsweise Oberschenkelumfang und dem Platz für beide Rückfaltungen. Gurte gehören nicht zum Druckpaket. Die vier Ösen und ihre kurzen Übergänge zur Platte werden lokal mit 100 % geradlinigem Infill gedruckt; der restliche P01 bleibt bei 20 % Gyroid. Die vier Modifikatoren sind Einstellungen im 3MF und keine zusätzlichen Bauteile.

1. Den langen Gurt unten um den runden Gegenstand führen. Je ein Ende von unten durch die linke beziehungsweise rechte Öffnung derselben X-Position nach oben stecken.
2. Jedes Ende über den **äußeren Steg** falten und **außen nach unten** zurückführen. Die doppelte Lage gehört außerhalb der Öffnung; dort berücksichtigt die nominale Freiraumprüfung bis zu 4 mm.
3. Beide Enden sicher am eigenen Gurt befestigen. Es läuft **kein Gurt über den Griff oder quer durch den oberen Bewegungsraum**. Den zweiten Gurt an der anderen X-Position genauso montieren.

![Gurtführung am nativen Querschnitt einer äußeren Öse](evidence/strap-routing.svg)

Die Abbildung zeigt die reale Rahmenkontur einer rechten Öse; Gurtverlauf und Gegenstand sind schematisch. Vor Benutzung am federfreien Aufbau Sitz, vollen Hub, sichere Endbefestigung und freien Zugang zu den Rastarmen prüfen. Gedruckte Tragfähigkeit, Gurtzug und Dauerhaltbarkeit sind noch nicht gemessen. Für Demontage und Elektronikservice die Gurte abnehmen.
<!-- STRAP_ROUTING_END -->

Reale Passung, neue Handposition, Stützentfernung, PLA-Kriechen und Belastbarkeit sind am Ausdruck zu prüfen. Clips dienen der federfreien Montage; für Federlast bleiben die vorgesehenen Sicherungsschrauben erforderlich. Es wurde kein Druckauftrag gesendet.
