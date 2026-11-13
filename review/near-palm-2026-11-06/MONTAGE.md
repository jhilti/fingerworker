# R14 – integrierte griffnahe Handballenauflage und Gurtaufnahme

Stand 06.11.2026. PLA, Bambu H2D, Standarddüse 0,4 mm. Maßgeblich sind die finalen nativen Dateien und Prüfberichte dieser Revision.

<!-- RELEASE_STATUS_START -->
**Nominale R14-CAD- und PLA-Druckprüfung bestanden.** Native Geometrie, voller Hub, Sensorservice, Q01-Passung und der tatsächliche H2D-Slice sind an diese Revision gebunden. Reale Reichweite, Handkomfort, Rastkraft und Belastbarkeit bleiben am Ausdruck zu prüfen.
<!-- RELEASE_STATUS_END -->

## Was sich gegenüber R13 ändert

P01 erhält eine breite abgerundete Handballenauflage unmittelbar an der Sensorwand. Der bisher außen liegende Handballenbalken entfällt. Die neue Auflage ist mit P01 verbunden: keine separate Auflage, Hülse, Schraube oder kleine Rastteile kommen hinzu.

Die neue Kontaktposition soll die Reichweite zum Fingergriff verkürzen. Die endgültigen Maße und Abstände stehen in der geprüften Konstruktionsspezifikation dieser Revision. Handkomfort und subjektiv passende Reichweite sind erst am neuen Ausdruck zu bestätigen.

**Druckumfang:** P01, P04, P05, P06 und P11 sowie Q01 als unbelastete Sensor-Passhilfe, zusammen sechs Stücke auf einer Platte. Vorhandene echte Führungsstangen verwenden. P08/P09 werden für den aktuellen mechanischen Aufbau nicht gedruckt; die Elektronikmontage bleibt als spätere Funktion vorgesehen. Keine Schrauben, Muttern oder Stangen-Formhilfen drucken.

P04 behält seine Druckausrichtung mit freier Fingerkontaktfläche. Q01 bleibt nur für den federfreien Aufbau bestimmt. Beide Vorspannmechanismen bleiben entfernt; P11 bleibt der separate Schalterfeinabgleich.

## Federfreier Passaufbau

1. Brims und alle zugänglichen Stützen entfernen. Gleitführung, Stangenaufnahmen, Rastarme und Nockentasche säubern. Teile nicht durch Schrauben in eine klemmende Passung ziehen.
2. Nur die R12-kompatible Q01 verwenden: den großen Block mit seinem Fuß auf den Boden der Sensortasche (Z2,7) und seiner Rückseite an die feste Sensorabstützung setzen. P05 in Richtung −X über den glatten Ø3-Zapfen schieben, bis es an dessen Schulter anliegt. Die Passhilfe hat keine axiale Verriegelung; den Aufbau abstützen und leicht in Druckrichtung zusammenhalten. Sensorstapel, Federn, Federsitze und Isometriehülsen bleiben dabei vollständig ausgebaut. P05 darf nicht fest mit P01 verbunden werden.
3. P04 von hinten auf die offene zentrale Führung schieben. Die vorhandenen echten Führungsstangen durch die Aufnahmen in die vorderen Stangensockel einsetzen.
4. P06 von hinten auf beide Stangen schieben, also in Richtung −X. Die beiden seitlichen Haken über die Gegenhalter führen und einrasten lassen. Bei strammer PLA-Passung die Enden leicht nach außen führen, statt die Haken zu überdrücken.
5. Beide Haken müssen zurückfedern. Der Griff muss sich vom ebenen hinteren Anschlag frei nach vorne bewegen. Die feste Geometrie lässt 30 mm Nutzweg; kein neuer vorderer Rahmenanschlag darf den Sensorpfad überbrücken.
6. P11 in seine Führung setzen und nach Einbau des echten Schalters mit H10 M3×10 einstellen und klemmen. Die kleine Nocke bleibt separat, um reale Schalter- und Drucktoleranzen auszugleichen.
7. Späterer Elektronikaufbau, nicht Teil dieses Druckauftrags: Elektronik und Leitungen in P08 einsetzen, P09 auf die Wanne klicken. Den geschlossenen Einsatz von unten an P01 einsetzen, bis beide äußeren P08-Haken an der festen Auflage einrasten. Die zwei M2-Rahmenschrauben und drei Deckelschraubstellen bleiben bei Bedarf verfügbar.

## Lösen und Service

**P06:** Zuerst vollständig entlasten und die vier M3-Schrauben entfernen, soweit eingebaut. Beide seitlichen Haken etwa **0,9 mm nach außen** lösen; die ganze Traverse **mindestens 12 mm nach hinten (+X)** ziehen. Erst anschließend Stangen und Griff herausnehmen. Der Querverbinder sitzt hinter dem Ende der zentralen Führung, damit der Einbauweg erhalten bleibt.

**Elektronik:** P08 an den beiden hohen Endhaken etwa **0,6 mm nach außen** lösen, optionale M2-Schrauben entfernen und das geschlossene Gehäuse **20 mm nach unten (−Z)** abnehmen. Kabel dabei führen. P09 erst am ausgebauten Gehäuse öffnen: beide äußeren Deckellaschen **0,9 mm nach außen in −X** lösen und Deckel **15 mm nach oben** abheben.

**Sensor:** Federkraft vollständig beseitigen, Traverse, Stangen und die Federn beziehungsweise Isometriehülsen entfernen. H18/H19 über die seitlichen Zugänge entfernen. Den vollständigen Sensor-/Jochstapel zunächst **3,2 mm zum Griff (+X)**, dann **40 mm nach oben (+Z)** herausnehmen. Sensor, H12, H23 und die H24/H25-Keepersicherung bleiben dabei zusammen. Die entfallene zentrale Einstellschraube, H15-Platte und deren Schrauben/Muttern haben keine Montage- oder Serviceschritte mehr; ein H17-Spezialschlüssel wird nicht mehr benötigt.

**Q01:** Beim federfreien Passaufbau P05 zuerst mindestens 12 mm in Richtung +X vom glatten Zapfen abziehen; Q01 anschließend gerade 40 mm nach oben herausheben. Der Fuß sitzt in der tieferen Sensortasche; deshalb Q01 nicht unten über die umgebende Grundplatte schieben. Q01 vollständig entfernen, bevor der echte Sensorstapel eingesetzt wird.

## Funktionsaufbau und Einstellung

Beide Vorspannverstellungen entfallen. Es gilt fest **`a = p = 0`**, `q = 5 + u` und **`0 ≤ u ≤ 30 mm`**. Die 81-mm-Isometriehülsen haben einen festen Anfahrweg von **15 mm**. P11 behält ausschließlich den Schaltpunktabgleich `camTrim = −0,8…+0,8 mm` für reale Schalter- und Drucktoleranzen.

Die Federn bleiben im eingebauten Ruhezustand auf **96 mm** verkürzt. Ohne einstellbare Vorspannung ist daher weiterhin eine feste Einbaukompression vorhanden: beim leichten DF2194-Paar 6 mm je Feder, beim stärkeren DF2185-Paar 9 mm. Das entspricht rechnerisch etwa 39,7 N beziehungsweise 66,8 N Paarkraft; diese Nennwerte ersetzen keine Messung. Federn beim Ein- und Ausbau kontrolliert entlasten.

Für den Aufbau mit Federn bleiben die vier H30-M3×8-Schrauben und geeignete Inserts zur Sicherung der Traverse vorgesehen. Die PLA-Clips allein sind geometrisch als Montagehilfe geprüft; Federlast, Schläge und wiederholte Belastung sind noch nicht physisch qualifiziert. Der Lastpfad bleibt **P04 → Federn bzw. P05-Endanschläge → P05 → H02 → H01 → H12 → feste P01-Abstützung**. H20 hält den echten Druckstift und bleibt erforderlich. Der feste Rahmen berührt P05 nicht. Sensor, Stahlstangen, Federsitze und die übrige Funktionshardware werden nicht durch die gedruckten Formhilfen ersetzt. Q01 vor Sensoreinbau vollständig entfernen.

Die Grundplatte bleibt 132 mm breit; die neuen äußeren Gurtösen ergeben **156 mm Gesamtbreite**. Die hinteren Rastarme liegen innerhalb dieser Breite. Die Verstellung beider hinteren Schrauben und alle dazugehörigen Fangpin-/Kontermutter-Arbeitsschritte entfallen.

## Abnahme am Ausdruck

Federfrei prüfen: leichtgängiger voller Hub, beide Haken rasten und lösen ohne Weißbruch, Stangen lassen sich ohne Zwang einsetzen, P06 bleibt parallel, P08/P09 passen und die Leitungen werden nicht gequetscht. Danach Schalterposition und Sensor kalibrieren. Es gibt weiterhin keine geprüfte 500-N-Freigabe oder Lebensdaueraussage.

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
