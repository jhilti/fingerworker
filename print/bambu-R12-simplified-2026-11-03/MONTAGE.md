# R12 – vereinfachte Klickmontage

Stand 03.11.2026. PLA, Bambu H2D, Standarddüse 0,4 mm. Maßgeblich sind die finalen nativen Dateien und Prüfberichte dieser Revision. Gedruckte Passung und Belastbarkeit sind noch am Muster zu bestätigen.

## Was sich ändert

Die beiden verstellbaren hinteren Kappen samt Anschlagschuhen werden durch **eine abnehmbare Traverse P06** ersetzt. Ihre ebenen vorderen Flächen liegen gemeinsam bei X119; die bisherige hintere Verstellung entfällt. Lange seitliche Rastarme halten die Traverse für den federfreien Passaufbau. Die vier bisherigen M3-Schraubstellen bleiben für die Sicherung des Funktionsaufbaus erhalten.

P01 bekommt die Gegenhalter der Traverse und eine breite feste Sensorabstützung bei X−12. Auch die zentrale Vorspannverstellung entfällt vollständig: H11, H13, H15, H160/H161, H170/H171, H21 und H22 werden entfernt. Die nicht mehr benötigten Taschen für Stellschrauben, Muttern und Scheiben sowie die frühere H15-Servicekerbe werden geschlossen. H12 liegt direkt an der festen Abstützung an; die H18/H19-Sicherung bleibt mit runden statt länglichen Führungslöchern erhalten. P08 verliert zwei unbenutzte Schrauben-Pilotbohrungen des früheren P10-Kabelhalters. P09 bleibt ein separat druckbarer Klickdeckel: Eine Integration in P01 wurde geprüft und wegen Stützspuren an der eng tolerierten PCB-Haltefläche verworfen.

**Neu drucken:** P01, P06 und die R12-Passhilfe Q01. Die alte Q01 passt nicht an die neue feste Sensorabstützung. P08 ist geometrisch vereinfacht; ein vorhandener R11-P08 bleibt kompatibel, da nur zwei unbenutzte Bohrungen gefüllt wurden. P04, P05, P09, P11 sowie H040/H041 können aus dem R11-Satz übernommen werden. P04 verwendet weiterhin die bereits verbesserte R11-Drucklage. Alte P060/P061/P120/P121 und die entfernte Vorspannhardware nicht zusätzlich montieren.

## Federfreier Passaufbau

1. Brims und alle zugänglichen Stützen entfernen. Gleitführung, Stangenaufnahmen, Rastarme und Nockentasche säubern. Teile nicht durch Schrauben in eine klemmende Passung ziehen.
2. Nur die neue Q01 verwenden: den großen Block mit seinem Fuß auf den Boden der Sensortasche (Z2,7) und seiner Rückseite an die feste Sensorabstützung setzen. P05 in Richtung −X über den glatten Ø3-Zapfen schieben, bis es an dessen Schulter anliegt. Die Passhilfe hat keine axiale Verriegelung; den Aufbau abstützen und leicht in Druckrichtung zusammenhalten. Sensorstapel, Federn, Federsitze und Isometriehülsen bleiben dabei vollständig ausgebaut. P05 darf nicht fest mit P01 verbunden werden.
3. P04 von hinten auf die offene zentrale Führung schieben. Beide Stangen-Formhilfen durch die Aufnahmen in die vorderen Stangensockel einsetzen.
4. P06 von hinten auf beide Stangen schieben, also in Richtung −X. Die beiden seitlichen Haken über die Gegenhalter führen und einrasten lassen. Bei strammer PLA-Passung die Enden leicht nach außen führen, statt die Haken zu überdrücken.
5. Beide Haken müssen zurückfedern. Der Griff muss sich vom ebenen hinteren Anschlag frei nach vorne bewegen. Die feste Geometrie lässt 30 mm Nutzweg; kein neuer vorderer Rahmenanschlag darf den Sensorpfad überbrücken.
6. P11 in seine Führung setzen und nach Einbau des echten Schalters mit H10 M3×10 einstellen und klemmen. Die kleine Nocke bleibt separat, um reale Schalter- und Drucktoleranzen auszugleichen.
7. Elektronik und Leitungen in P08 einsetzen, P09 auf die Wanne klicken. Den geschlossenen Einsatz von unten an P01 einsetzen, bis beide äußeren P08-Haken an der festen Auflage einrasten. Die zwei M2-Rahmenschrauben und drei Deckelschraubstellen bleiben bei Bedarf verfügbar.

## Lösen und Service

**P06:** Zuerst vollständig entlasten und die vier M3-Schrauben entfernen, soweit eingebaut. Beide seitlichen Haken etwa **0,9 mm nach außen** lösen; die ganze Traverse **mindestens 12 mm nach hinten (+X)** ziehen. Erst anschließend Stangen und Griff herausnehmen. Der neue Querverbinder sitzt hinter dem Ende der zentralen Führung, damit der Einbauweg erhalten bleibt.

**Elektronik:** P08 an den beiden hohen Endhaken etwa **0,6 mm nach außen** lösen, optionale M2-Schrauben entfernen und das geschlossene Gehäuse **20 mm nach unten (−Z)** abnehmen. Kabel dabei führen. P09 erst am ausgebauten Gehäuse öffnen: beide äußeren Deckellaschen **0,9 mm nach außen in −X** lösen und Deckel **15 mm nach oben** abheben.

**Sensor:** Federkraft vollständig beseitigen, Traverse, Stangen und die Federn beziehungsweise Isometriehülsen entfernen. H18/H19 über die seitlichen Zugänge entfernen. Den vollständigen Sensor-/Jochstapel zunächst **3,2 mm zum Griff (+X)**, dann **40 mm nach oben (+Z)** herausnehmen. Sensor, H12, H23 und die H24/H25-Keepersicherung bleiben dabei zusammen. Die entfallene zentrale Einstellschraube, H15-Platte und deren Schrauben/Muttern haben keine Montage- oder Serviceschritte mehr; ein H17-Spezialschlüssel wird nicht mehr benötigt.

**Q01:** Beim federfreien Passaufbau P05 zuerst mindestens 12 mm in Richtung +X vom glatten Zapfen abziehen; Q01 anschließend gerade 40 mm nach oben herausheben. Der Fuß sitzt in der tieferen Sensortasche; deshalb Q01 nicht unten über die umgebende Grundplatte schieben. Q01 vollständig entfernen, bevor der echte Sensorstapel eingesetzt wird.

## Funktionsaufbau und Einstellung

Beide Vorspannverstellungen entfallen. Es gilt fest **`a = p = 0`**, `q = 5 + u` und **`0 ≤ u ≤ 30 mm`**. Die 81-mm-Isometriehülsen haben einen festen Anfahrweg von **15 mm**. P11 behält ausschließlich den Schaltpunktabgleich `camTrim = −0,8…+0,8 mm` für reale Schalter- und Drucktoleranzen.

Die Federn bleiben im eingebauten Ruhezustand auf **96 mm** verkürzt. Ohne einstellbare Vorspannung ist daher weiterhin eine feste Einbaukompression vorhanden: beim leichten DF2194-Paar 6 mm je Feder, beim stärkeren DF2185-Paar 9 mm. Das entspricht rechnerisch etwa 39,7 N beziehungsweise 66,8 N Paarkraft; diese Nennwerte ersetzen keine Messung. Federn beim Ein- und Ausbau kontrolliert entlasten.

Für den Aufbau mit Federn bleiben die vier H30-M3×8-Schrauben und geeignete Inserts zur Sicherung der Traverse vorgesehen. Die PLA-Clips allein sind geometrisch als Montagehilfe geprüft; Federlast, Schläge und wiederholte Belastung sind noch nicht physisch qualifiziert. Der Lastpfad bleibt **P04 → Federn bzw. P05-Endanschläge → P05 → H02 → H01 → H12 → feste P01-Abstützung**. H20 hält den echten Druckstift und bleibt erforderlich. Der feste Rahmen berührt P05 nicht. Sensor, Stahlstangen, Federsitze und die übrige Funktionshardware werden nicht durch die gedruckten Formhilfen ersetzt. Q01 vor Sensoreinbau vollständig entfernen.

Die Grundplatte bleibt 132 mm breit; die äußeren Rastarme der neuen Traverse ergeben **135,2 mm Gesamtbreite**. Die Verstellung beider hinteren Schrauben und alle dazugehörigen Fangpin-/Kontermutter-Arbeitsschritte entfallen.

## Abnahme am Ausdruck

Federfrei prüfen: leichtgängiger voller Hub, beide Haken rasten und lösen ohne Weißbruch, Stangen lassen sich ohne Zwang einsetzen, P06 bleibt parallel, P08/P09 passen und die Leitungen werden nicht gequetscht. Danach Schalterposition und Sensor kalibrieren. Es gibt weiterhin keine geprüfte 500-N-Freigabe oder Lebensdaueraussage.
