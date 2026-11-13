# R12 – finale Druckprüfung

**Bestanden:** sieben Geräteteile plus drei unbelastete Passhilfen, insgesamt zehn Modelle auf drei vollständig geslicten Platten. H2D, Standarddüsen 0,4 mm, PLA, strukturierte PEI-Platte, Maßstab 100 %.

| Platte | Stücke | Slicerzeit | PLA einschließlich Stützen/Brim |
|---|---:|---:|---:|
| 1 | 1 | 8 h 20 min 09 s | 133.55 g |
| 2 | 8 | 5 h 29 min 35 s | 72.43 g |
| 3 | 1 | 4 h 20 min 33 s | 65.21 g |

Komplett: **18 h 10 min 17 s / 271.19 g**.

P01 hat eine feste, vom Boden aufsteigende Sensorabstützung und die Gegenhalter der neuen Traverse. P06 ersetzt vier bisherige hintere Druckteile durch ein großes Teil mit langen PLA-Rastarmen. Sowohl hintere Verstellung als auch zentraler H13-Vorspannmechanismus sind entfernt. Dies bedeutet keine unbelasteten Federn: Die nominale Feder-Einbaulänge in Ruhe bleibt 96 mm. Gegenüber den freien Längen 102/105 mm sind die bisherigen Federn bereits 6/9 mm geometrisch komprimiert. Der feste Nutzweg beträgt 30 mm; mit 81-mm-Isometriehülsen beträgt der Anfahrweg15 mm.

Neu benötigt werden P01, P06 und die zum festen Sensordatum passende Q01-Passhilfe. Alte Q01 verwendet die entfernte Muttertasche und passt nicht. Ein vorhandenes R11-P08 bleibt kompatibel; die neue Version füllt lediglich zwei unbenutzte Pilotlöcher. P04, P05, P09, P11 und die beiden Stangen-Formhilfen bleiben wiederverwendbar. Alte P060/P061/P120/P121 und entfernte Verstellhardware gehören nicht in den R12-Aufbau.

Der finale native STEP enthält 93 eindeutig zugeordnete Körper. Die geänderten Körper sind gegen unabhängige CSG geprüft; beibehaltene Körper werden separat auf Geometrieidentität geprüft. Die native Bambu-Datei stimmt mit allen zehn Quellmeshes überein: Plattenverteilung 1/8/1, Maßstab 1:1, starre Transformationen, geschlossene Volumina und keine automatische Meshreparatur. Messungen, Quellen und konkrete Prüfzahlen stehen in den mitgelieferten JSON-Berichten.

Die Werkzeugwegprüfung umfasst P06-Rastarme, freie Biegespalte, offene Stangenbohrungen und deren selbsttragende Dachform, P01-Gegenhalter sowie die feste Sensorauflage. Die Sensor-Kontaktfläche und die 45°-Schultern benötigen keine Stützen; die frühere obere Reaktionsbrücke ist entfernt. Die Traverse wird ohne Stützen gedruckt. Zugängliche Stützen an P01 vollständig entfernen, bevor die Clips montiert werden.

P08/P09 behalten die bewährten langen Klickarme. P09 bleibt separat und ohne Stützen; die Integration seiner PCB-Haltefläche in P01 wurde wegen zusätzlicher Stützspuren verworfen. P08 benötigt am USB-Dach und an den außen zugänglichen Endhaken Stützen. P04 bleibt auf Platte 3 in der geprüften Stirnseitenlage: Die Fingerkontakt-/Führungsregionen sind ohne Support-, Interface- oder Transitionpfade. Die gegenüberliegende Muldenwand bleibt gestützt.

Q01 und die gedruckten Stangen dienen nur der federfreien Passprobe. Für den Funktionsaufbau bleiben Sensor, Stahlstangen, Federsitze und geeignete Sicherungsschrauben vorgesehen. Die vier M3-Traversenschrauben bleiben zur Sicherung verfügbar; PLA-Clips allein sind keine Federlastfreigabe.

Offizielle Bambu Studio 02.08.02.61; Import und vollständiger Slice mit Code 0. Originale H2D-Maschinenmakros bleiben erhalten. Kein Druckauftrag wurde übertragen. Dieses Paket enthält ein editierbares 3MF-Projekt und keine Drucker-Gcodes.

Quellhash: `730cd21ea3aafbe43bf8eb38007b20d9cd0272659430d8a2b3b6245f33f62455`. [Onshape R12](https://cad.onshape.com/documents/15316cc6370631845af136b2/v/a38e831517d6797cbc47077c/e/d253eb87b70818ebde8215f0). Die Berichte in validation binden Projekt, native CAD-Geometrie, Fixture und internen Slice.

Die Prüfungen betreffen nominale Geometrie und berechnete Werkzeugwege. Reale Rastkraft, Passung, Stützentfernung, Oberflächen, Kriechen und Belastbarkeit bleiben am Ausdruck zu prüfen. Eine 500-N- oder Lebensdauerfreigabe ist damit nicht verbunden.
