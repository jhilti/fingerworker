# R14 – Review der griffnahen Auflage und Gurtaufnahme

<!-- RELEASE_STATUS_START -->
**Nominale R14-CAD- und PLA-Druckprüfung bestanden.** Native Geometrie, voller Hub, Sensorservice, Q01-Passung und der tatsächliche H2D-Slice sind an diese Revision gebunden. Reale Reichweite, Handkomfort, Rastkraft und Belastbarkeit bleiben am Ausdruck zu prüfen.
<!-- RELEASE_STATUS_END -->

## Ziel und Umfang

Die Hand soll auf einer breiten gerundeten Fläche nahe der Sensorwand aufliegen. Der äußere R13-Handballenbalken entfällt. P01 bleibt ein Druckteil; es werden keine neuen Montage- oder Rastteile eingeführt.

Die übrigen gedruckten Funktionen bleiben erhalten: P04 gleitet auf der Führung, P05 überträgt die Messkraft unabhängig vom Rahmen, P06 hält beide Führungsstangen gemeinsam, P11 gleicht den realen Schaltpunkt ab. P08/P09 bleiben abnehmbar, werden im aktuellen mechanischen Sechserpaket jedoch nicht gedruckt.

## Geprüfte Schnittstellen

| Bereich | Nachweisumfang |
|---|---|
| Neue Handballenfläche | Breite glatte Rundung ohne hervorstehende alte Sensorwandkante; Kontaktfläche im Slice frei von Supportkontakt |
| Sensor-Kraftpfad | Feste H12-Reaktionsfläche erhalten; keine starre Verbindung von P01 zu P05 |
| Dynamik und Isometrie | Voller 30-mm-Hub und 15-mm-ISO-Anfahrweg erhalten |
| Sensorservice | H18/H19 seitlich lösbar; Sensorstapel +X3,2 und danach +Z40 entnehmbar |
| Q01 | Unbelastete Sitzflächen, P05-Schulter, 30-mm-Griffbewegung und Entnahme geprüft |
| Elektronik | Dach, äußere Rastflächen und optionale M2-Piloten erhalten; P08/P09-Service zugänglich |
| Hecktraverse | Klickmontage, Entriegelung und vier Sicherungsschrauben unverändert |
| P04-Oberfläche | Bewährte Drucklage; acht kritische Finger-/Führungsbereiche ohne Supportpfade |

## Teilezahl und Wiederverwendung

Vorgesehen sind weiterhin sieben Gerätedruckteile im vollständigen CAD. Das aktuelle Paket enthält fünf davon plus Q01; zwei echte Führungsstangen werden aus dem vorhandenen Bestand verwendet. Nur P01 ändert gegenüber R13 seine Geometrie. Der finale native Export enthält 93 Körper; die 92 Körper außer P01 sind exakt zum R13-Stand erhalten.

## Prüfung am Ausdruck

Der neue Druck klärt zuerst die bevorzugte Handposition und Reichweite. Danach federfrei vollständigen Hub, Leichtgängigkeit, Rastung und Stützentfernung prüfen. Die nominelle CAD-/Slicerprüfung ersetzt keine gemessene Festigkeit, PLA-Kriechprüfung oder Freigabe unter Federlast.

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

## Geprüfte Enddaten

Die [Konstruktionsspezifikation](mechanics/design-specification.json) enthält die finalen Maße der griffnahen Auflage. [Native Geometrie](validation/native-geometry.json), [Bewegung](validation/native-motion.json), [Sensorservice](validation/service-native.json) und [Q01-Passung](validation/fixture-q01-check.json) beziehen sich auf denselben R14-Export. Die Druckberichte gelten für den tatsächlich geslicten Sechsersatz.

<!-- R14_DIMENSIONS_START -->
## Neue Auflage in Zahlen

| Maß | R14 |
|---|---|
| Breite × Tiefe | 76 × 18 mm |
| Scheitel im CAD | X -20 bis -19 mm, Z 33 mm |
| Rundung zum Handgelenk | R 14 mm |
| Rundung zur Sensorseite / an den Enden | R 3 / R 2 mm |
| Neue Unterseite an der Nase | 45° |
| Abstand zur hinteren H12-Sensorebene | 4 mm |

Die frühere äußere Auflage und ihr hoher Verbindungssteg entfallen oberhalb Z14,5. Vier integrale flache Gurtösen werden außen am unteren Rahmen ergänzt. Die ursprüngliche 6-mm-Grundplatte und ihre Führungsquerschnitte bleiben ungeschnitten; funktionale Sensor-, Rast- und Elektronikbereiche bleiben erhalten. Der obere Wandrand und die Enden der Stützrippen werden nur oberhalb Z30 angepasst. Die eigentliche Sensorreaktionsfläche endet bereits bei Z26 und bleibt erhalten. Es kommt keine Verbindung zum beweglichen P05 hinzu.
<!-- R14_DIMENSIONS_END -->
