# R13 – finale Druckprüfung

**Bestanden:** sieben Geräteteile plus drei unbelastete Passhilfen, insgesamt zehn Modelle auf drei vollständig geslicten Platten. H2D, Standarddüsen 0,4 mm, PLA, strukturierte PEI-Platte, Maßstab 100 %.

| Platte | Stücke | Slicerzeit | PLA einschließlich Stützen/Brim |
|---|---:|---:|---:|
| 1 | 1 | 8 h 35 min 15 s | 135.52 g |
| 2 | 8 | 5 h 29 min 35 s | 72.43 g |
| 3 | 1 | 4 h 20 min 33 s | 65.21 g |

Komplett: **18 h 25 min 23 s / 273.16 g**.

P01 hat jetzt eine einfache, durchgehende Handballenauflage. Gegenüber R12 ist nur dieses Geräteteil geändert. Die feste Sensorabstützung, hintere Traverse, Klickmontage sowie das separat zugängliche Elektronikgehäuse bleiben erhalten. Die nominale Feder-Einbaulänge in Ruhe bleibt 96 mm: Gegenüber den freien Längen 102/105 mm sind die bisherigen Federn geometrisch 6/9 mm komprimiert. Der feste Nutzweg beträgt 30 mm; mit 81-mm-Isometriehülsen beträgt der Anfahrweg 15 mm.

Bei vorhandenem R12-Satz muss nur P01 neu gedruckt werden. P04, P05, P06, P08, P09, P11, die beiden Stangen-Formhilfen und die feste R12-Q01 bleiben wiederverwendbar. Die ältere R11-Q01 für eine Muttertasche und die früheren hinteren Kappen/Schuhe gehören nicht in den R13-Aufbau.

Der finale native STEP enthält 93 eindeutig zugeordnete Körper. Die geänderten Körper sind gegen unabhängige CSG geprüft; beibehaltene Körper werden separat auf Geometrieidentität geprüft. Die native Bambu-Datei stimmt mit allen zehn Quellmeshes überein: Plattenverteilung 1/8/1, Maßstab 1:1, starre Transformationen, geschlossene Volumina und keine automatische Meshreparatur. Messungen, Quellen und konkrete Prüfzahlen stehen in den mitgelieferten JSON-Berichten.

Die Werkzeugwegprüfung umfasst die neue Handballenauflage und die Zugänglichkeit ihrer Stützen sowie die beibehaltenen P06-Rastarme, Biegespalte, Stangenbohrungen, P01-Gegenhalter und feste Sensorauflage. Die Sensor-Kontaktfläche und die 45°-Schultern benötigen keine Stützen. Die Traverse wird ohne Stützen gedruckt. Stützen an P01 vollständig entfernen, bevor die Clips montiert werden. Konkrete Kontaktbereiche und Zugänglichkeitsnachweise stehen in palm-support-check.json.

P08/P09 behalten die bewährten langen Klickarme. P09 bleibt separat und ohne Stützen; die Integration seiner PCB-Haltefläche in P01 wurde wegen zusätzlicher Stützspuren verworfen. P08 benötigt am USB-Dach und an den außen zugänglichen Endhaken Stützen. P04 bleibt auf Platte 3 in der geprüften Stirnseitenlage: Die Fingerkontakt-/Führungsregionen sind ohne Support-, Interface- oder Transitionpfade. Die gegenüberliegende Muldenwand bleibt gestützt.

Q01 und die gedruckten Stangen dienen nur der federfreien Passprobe. Für den Funktionsaufbau bleiben Sensor, Stahlstangen, Federsitze und geeignete Sicherungsschrauben vorgesehen. Die vier M3-Traversenschrauben bleiben zur Sicherung verfügbar; PLA-Clips allein sind keine Federlastfreigabe.

Offizielle Bambu Studio 02.08.02.61; Import und vollständiger Slice mit Code 0. Originale H2D-Maschinenmakros bleiben erhalten. Kein Druckauftrag wurde übertragen. Dieses Paket enthält ein editierbares 3MF-Projekt und keine Drucker-Gcodes.

Das CLI-Protokoll enthält je Platte die Meldungen „Invalid T command“ für T1001/T65535/T65279. Anzahl und Wortlaut stimmen mit dem geprüften R12-Lauf und unveränderten offiziellen H2D-Makros überein; es gibt keine neue Warnung oder Fehlermeldung. Diese bestehenden Parsermeldungen sind in cli-diagnostics.json ausdrücklich erfasst. Alle drei Platten wurden vollständig erzeugt und separat geprüft.

Quellhash: `82b7d65708c46cd9d4b6ac271047eac2f638f0222451df99eae0780525edd851`. [Onshape R13](https://cad.onshape.com/documents/15316cc6370631845af136b2/v/18d76d07da0c354cee82580a/e/d253eb87b70818ebde8215f0). Die Berichte in validation binden Projekt, native CAD-Geometrie, Fixture und internen Slice.

Die Prüfungen betreffen nominale Geometrie und berechnete Werkzeugwege. Reale Rastkraft, Passung, Stützentfernung, Oberflächen, Kriechen und Belastbarkeit bleiben am Ausdruck zu prüfen. Eine 500-N- oder Lebensdauerfreigabe ist damit nicht verbunden.
