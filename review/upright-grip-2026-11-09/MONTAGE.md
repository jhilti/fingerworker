# R16 – Montage des integrierten Handballengriffs

Stand 09.11.2026. **R16-CAD und berechnete PLA-Druckwege geprüft.** Die Nachweise gelten für den unten verlinkten nativen Stand. Handkomfort, sicherer Halt, Druckpassung und Belastbarkeit bleiben am Ausdruck zu prüfen.

## Änderung gegenüber R15

Nur P01 ändert sich. Eine 126 mm breite aufrechte Druckfläche ersetzt die bisherige kurze Rundung. Beide Stangensockel bekommen gerundete Schultern; flache Daumenrückgriffe liegen auf der Handgelenkseite. Der Griff bleibt fest mit dem Rahmen verbunden, P05 bleibt als separates Messjoch frei. Die Höhe bleibt Z33; die 30 mm Griffbewegung und alle Montage-/Servicewege bleiben erhalten. Die alte 3-mm-Stufe auf der Handgelenkseite ist entfernt. Das darunterliegende Elektronikdach bleibt 2 mm dick; Raststellen und Schraubpiloten bleiben erhalten.

P01/P04/P05/P06/P11 und Q01 werden gemeinsam aus PLA gedruckt, ohne Brim. Die vorhandenen echten Stangen verwenden. P08/P09 bleiben für den späteren Elektronikaufbau kompatibel und fehlen absichtlich im mechanischen Drucksatz. Es gibt keine gedruckten Schrauben, Muttern oder neuen kleinen Griffteile.

## Neue Kontaktflächen prüfen

Vor dem Zusammenbau Stützreste unter dem Rahmen und in den vorgesehenen Bohrungen entfernen. Die große aufrechte Palmfläche und die gerundeten Schultern auf gleichmäßige Oberfläche prüfen. Die Daumenrückgriffe sind nur etwa 4 mm tief; ihre schrägen Dächer und die kleinen Randrundungen nicht mit Gewalt aufweiten. Die niedrig liegenden Elektronikraststellen an den Enden bleiben frei.

Federfrei den Handballen gegen die aufrechte Fläche setzen, den Daumen an einer gerundeten Schulter beziehungsweise im Rückgriff anlegen und den Fingergriff vollständig bewegen. Kontakt zu Federn, Messjoch und Sensor vermeiden. Die Rückgriffe sollen das aktive Halten unterstützen; den tatsächlichen Halt am Ausdruck prüfen. Ein entspanntes Loslassen wird durch diese Form nicht gesichert.

## Federfreier Passaufbau

1. Alle zugänglichen Stützen entfernen. Das R16-Projekt druckt alle sechs Teile ohne Brim. Gleitführung, Stangenaufnahmen, Rastarme und Nockentasche säubern. Teile nicht durch Schrauben in eine klemmende Passung ziehen.
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

Der Hauptboden bleibt mit innenliegenden Gurtschlitzen **132 mm breit**; P01 misst einschließlich vorhandener Klickgegenhalter **132,4 mm**. Die vorhandenen hinteren Rastarme ergeben weiterhin **135,2 mm maximale Baugruppenbreite**. Die Verstellung beider hinteren Schrauben und alle dazugehörigen Fangpin-/Kontermutter-Arbeitsschritte entfallen.

## Abnahme am Ausdruck

Federfrei prüfen: leichtgängiger voller Hub, beide Haken rasten und lösen ohne Weißbruch, Stangen lassen sich ohne Zwang einsetzen, P06 bleibt parallel, P08/P09 passen und die Leitungen werden nicht gequetscht. Danach Schalterposition und Sensor kalibrieren. Es gibt weiterhin keine geprüfte 500-N-Freigabe oder Lebensdaueraussage.

<!-- STRAP_ROUTING_START -->
## Befestigung mit zwei Gurten

Die vier gerundeten **27 × 4-mm-Öffnungen liegen in der Grundplatte**, symmetrisch bei **Y±57,5 mm**. Die äußeren R14-Laschen entfallen vollständig. Der Hauptboden bleibt **132 mm breit**; vorhandene Klickgegenhalter ergeben **132,4 mm P01-Außenmaß**. Die zwei Gurtpositionen bei **X28 und X65 mm** liegen **37 mm auseinander**. Sie sind so angeordnet, dass die Bänder die Federsitze und den Griff auch am Ende seines 30-mm-Hubs freilassen.

Der native Bewegungsnachweis ergibt für eine einzelne 2-mm-Gurtlage mindestens **2,26 mm Abstand zu den bewegten Federsitzen** und **3,5 mm zur hinteren Griffbrücke**. Keine doppelte Gurtlage über den Steg legen; die Rückfaltung gehört außerhalb der Platte. Der Abstand der Gurtpositionen sinkt von 75 auf 37 mm. Dadurch nimmt ihre geometrische Abstützung gegen Verdrehen ab; den sicheren Sitz am tatsächlichen Gegenstand beim Passaufbau beurteilen.

Die Schlitze durchtrennen lokal den 6-mm-Boden. Es gibt keine flächige Bodenvertiefung und keine neue dünne Gurtbrücke. Neben jedem Schlitz bleiben nominal **6,5 mm äußerer Steg** und **17,5 mm innerer Restquerschnitt** bis zur vorhandenen Rahmenöffnung. Diese Maße und die lokale massive Füllung sind keine geprüfte Tragfähigkeitsangabe.

Benötigt werden **zwei echte 25-mm-Gurte**, höchstens **2 mm dick** im Durchlass. Die beiden Enden jedes Gurts müssen sich nach außen zurückfalten und sicher am eigenen Gurt befestigen lassen. Die Länge richtet sich nach dem Gegenstand oder Oberschenkelumfang plus beiden Rückfaltungen. Gurte werden nicht gedruckt. Die vier Schlitzbereiche und ihre tragenden Stege werden lokal mit 100 % geradlinigem Infill gedruckt; der übrige P01 bleibt bei 20 % Gyroid. Die Modifikatoren sind Einstellungen im 3MF, keine zusätzlichen Teile.

1. Den langen Gurt unten um den Gegenstand führen. Je ein Ende von unten durch die linke beziehungsweise rechte Öffnung derselben X-Position nach oben stecken.
2. Jedes Ende direkt über den **äußeren Plattensteg** und dann außerhalb der Plattenkante nach unten zurückführen. Die doppelte Lage bleibt außen; im Durchlass liegt nur eine Lage.
3. Beide Enden sicher am eigenen Gurt befestigen. Keine Gurtstrecke quer über Griff oder Federn führen. Den zweiten Gurt an der anderen Position genauso montieren.

![Gurtführung am nativen Schnitt der Grundplatte](evidence/strap-routing.svg)

Die Abbildung zeigt die echte Rahmenkontur; Gurt und Gegenstand sind schematisch. Vor der ersten belasteten Nutzung zunächst federfrei den Sitz, vollen Hub und die sichere Endbefestigung prüfen. Für Demontage und Elektronikservice die Gurte abnehmen. Reale Gurtpassung, Druckfestigkeit, Rutschfestigkeit und Dauerverhalten sind noch zu prüfen.
<!-- STRAP_ROUTING_END -->

[Native Geometrie](validation/native-geometry.json) · [Bewegung](validation/native-motion.json) · [Sensorservice](validation/service-native.json) · [Q01-Passung](validation/fixture-q01-check.json)
