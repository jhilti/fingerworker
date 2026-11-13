# R11 – finale Druckprüfung

**Bestanden:** 13 Modelle, drei vollständig geslicte Platten; H2D, Standarddüsen 0,4 mm, PLA, strukturierte PEI-Platte, 100 %.

| Platte | Stücke | Slicerzeit | PLA einschließlich Stützen/Brim |
|---|---:|---:|---:|
| 1 | 1 | 8 h 16 min 26 s | 131.35 g |
| 2 | 11 | 5 h 50 min 42 s | 70.31 g |
| 3 | 1 | 4 h 20 min 33 s | 65.21 g |

Komplett: **18 h 27 min 41 s / 266.87 g**. Der Rahmen ist zu R10 geometrisch identisch und muss nicht erneut gedruckt werden. Mit vorhandenem Rahmen entfallen Platte 1 und 131,35 g. Auf Platte 2 sind P08/P09/P120/P121 neu; die sieben übrigen Stücke können ebenfalls aus dem vorhandenen Passsatz übernommen werden.

Native STEP-Prüfung: vier geänderte Körper stimmen exakt mit unabhängiger CSG überein, 113 übrige BReps unverändert. P01 und P04 sind darunter. Alle 117 nativen Körper sind gültige Volumina. Vier kleine P07 und die separate P10 verschwinden durch Integration.

Das native Bambu-Projekt wurde unabhängig gegen alle 13 Quellmeshes geprüft: richtige Platten 1/11/1, Maßstab 1:1, starre Transformationen, geschlossene Volumina, höchstens 0,0001 mm Vertexabweichung, keine automatischen Meshreparaturen. Originale H2D-Maschinenmakros bleiben unverändert. 101 allgemeine Werkzeugwegprüfungen bestätigen Druckbereich, getrennte Bahnhüllen, erste Schicht, volle Höhe und begrenzte Beschleunigung.

P04 hat auf Platte 3 acht gesondert geprüfte Kontakt-/Führungsregionen ohne Support-, Interface- oder Transitionpfade. Die Fingerzugwand wird als Topfläche und der Muldenboden als Außenwand gedruckt. Die gegenüberliegende Muldenwand bleibt gestützt. Nur die geprüften Bett-Baumstützen übernehmen.

Beide Gehäuseteile haben vollständige Haken und durchgehende Rastarme; Spalte sind frei. P09 hat keine Bridge-Pfade oder Clipstützen. P08 benötigt am USB-Dach und an den außen zugänglichen Endhaken Stützen; der längste Bridge-Pfad beträgt 1,675 mm. Die nominalen Steck-/Entriegelwege wurden zusätzlich an der CAD-Geometrie geprüft.

Beide P12-Schuhe haben die T-förmige Bettanlage, keine Bridge-Pfade und keine Stützen im M2-Fangschlitz. Die Gabel enthält zugängliche Stützen: **vor dem Einbau vollständig axial aus der offenen Gabel entfernen**. Der durchgehende native R4,9-Entnahmezylinder ist materialfrei. Reale Stützentfernung und Passung bestätigt der Druck.

Offizielle Bambu Studio 02.08.02.61; Import und vollständiger Schnitt beenden mit Code 0. Bekannte T1001/T65535/T65279-Parsermeldungen aus den unveränderten Stock-Makros bleiben diagnostisch. Es wurde kein Druckauftrag übertragen; die Lieferdatei enthält keine Gcodes.

Quellhash: `c8ec18f08149553001ccf8173f35fe57eee6a16be0294be2d7f88577f658cf5e`. Onshape-Version: `a6ea6390a313176b40101f6b`. Die Berichte im Ordner validation binden Projekt und internen Slice. Das interne Gcode-Artefakt wird nicht mitgeliefert.

Diese Prüfung betrifft nominale Geometrie und berechnete Werkzeugwege. Rastkraft, PLA-Streuung, wiederholtes Entriegeln, Kriechen, tatsächliche Oberfläche und Festigkeit sind am unbelasteten Muster zu prüfen. Sie erteilt keine Lastfreigabe für gedruckte Stangen/Q01 oder den Funktionsaufbau.
