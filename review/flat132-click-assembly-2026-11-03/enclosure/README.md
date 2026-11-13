# R11 – klickbares Elektronikgehäuse, 03.11.2026

Das lokale CAD-Konzept ersetzt die bisherige Wanne P08 und den Deckel P09. P10 ist kein eigenes Druckteil mehr: Seine bisherige Kabel-Kontaktfläche ist als breite Säule am Deckel ausgebildet. Der bereits gedruckte **R10-Grundrahmen P01 bleibt geometrisch unverändert nutzbar**. PCB, Akku, Stecker und Bedienelemente bleiben an ihren bisherigen Positionen.

Die autoritative Freigabe erfolgt nach Regeneration und Export in Onshape. Die STEP/STL/3MF-Dateien in diesem Unterordner sind lokale CSG-Prüfkandidaten. Für den Benutzerdruck das übergeordnete endgültige R11-Paket verwenden.

## Verbindung und Bedienung

| Verbindung | Ausführung | Zusammenbau | Entriegelung |
|---|---|---|---|
| P08 an vorhandenem P01 | Zwei integrierte lange Blattarme mit hohen Endpfosten; Haken greifen über die flachen Endränder der festen Handballenauflage | Geschlossenes Gehäuse von unten in +Z anheben; Haken spreizen an den Einführschrägen nach außen und rasten oberhalb des Palm-Endrands ein | Beide Endpfosten sanft etwa 0,6 mm in ±Y nach außen spreizen; Gehäuse 20 mm nach unten abnehmen. Gerät dafür von der Tischfläche anheben. Nicht am Deckel ziehen. |
| P09 an P08 | Zwei integrierte lange Seitenarme außen am Handgelenkrand; Gegenlaschen sind an der Wanne | Deckel am ausgebauten Gehäuse geradlinig von oben in −Z aufsetzen und an den beiden Raststellen drücken | Beide Seitenarme am äußeren Handgelenkrand etwa 0,9 mm in −X nach außen spreizen; Deckel 15 mm in +Z abheben. |
| Kabelhalter | Frühere P10-Kontaktfläche als Bestandteil von P09 | Kabel vorher entlang der vorhandenen Führung legen, dann Deckel schließen | Öffnet zusammen mit P09; keine lose Klemmleiste. |

Der Deckel wird **außerhalb des Geräts** geöffnet und geschlossen. Der Abstand seiner normalen Deckelfläche zur festen Handballenauflage bleibt 0,6 mm. Nicht unter der festen Auflage am Deckel hebeln. Beim Abnehmen die Leitungen abstecken bzw. entlasten.

Die drei vorhandenen M1,6×5-Deckelschrauben und die beiden M2-Gehäuseschrauben bleiben optional nutzbar. Die zwei bisherigen M1,6×3-Schrauben für P10 entfallen. Beim verschraubten Aufbau zuerst Schrauben entfernen, dann Rastarme lösen. Die Rastarme sind eine Montage- und Gehäusehalterung; aus ihnen folgt keine Freigabe des Trainingslastpfads.

## Drucklage und erste Passprobe

**PLA ist der Standard.** Die Wanne liegt mit ihrem Boden auf dem Bett, der Deckel mit seiner äußeren Fläche. Die langen Rastarme liegen jeweils in der Druckebene; sie werden beim Einrasten innerhalb dieser Ebene gebogen. Die hohen Wannenpfosten wachsen direkt aus den auf dem Bett liegenden Armen. Es gibt keine frei in der Luft beginnende lange Traverse.

Für P08 bleiben automatische Normalstützen auch auf Modellflächen aktiv, damit die USB-Dachfläche unterstützt wird. Stützen nur an den frei zugänglichen Außenseiten bzw. über das offene Gehäuse entfernen. P09 wurde in dieser Lage ohne Stützen geschnitten; im lokalen Prüfslice entstehen dort **keine Bridge-Pfade**. Die längsten Bridge-getaggten P08-Segmente sind etwa 1,68 mm lang. Es wird kein zweites Material benötigt.

Die zwei kompletten Gehäuseteile eignen sich als robuste erste Passprobe: lokal etwa **61 Minuten und 10,7 g PLA** zusammen mit 3-mm-Außenbrim. Diese Schätzung stammt vom lokalen CSG-Prüfkandidaten, H2D mit 0,4-mm-Düse. Bei zu strammer Passung die Clips nicht mit Kraft überdrücken. Drucktoleranz, Elefantenfuß, PLA-Sorte, Schichthaftung und wiederholte Betätigung müssen am realen Druck geprüft werden. Die vorhandenen Schraubpunkte erlauben auch dann eine Montage.

## Geometrische Eckdaten und Prüfung

| Merkmal | P08 / P01 | P09 / P08 |
|---|---:|---:|
| Konservativ angesetzte wirksame Blattlänge | 15,5 mm | 20,0 mm |
| Blattdicke in Biegerichtung | 1,2 mm | 1,2 mm |
| Auslenkung an der Spitze zum Freigeben | 0,6 mm nach außen | 0,9 mm nach außen |
| Nominelle Randfaserdehnung, ε = 1,5·t·δ/L² | 0,45 % | 0,405 % |
| Nominales vertikales Spiel | 0,2 mm | 0,1 mm |
| Nomineller seitlicher Hakeneingriff | 0,4 mm | 0,8 mm |

Die einfache Blattformel ist ein Auslegungsvergleich. Sie berücksichtigt weder Kerbwirkung noch Schichtfehler, Pfostentorsion, Materialstreuung, Temperatur oder Ermüdung und liefert keine reale Festigkeitsfreigabe. Die Haken liegen außen und sind gezielt entriegelbar; eine Prüfung erfolgt mit unbelastetem Gerät.

P08 bleibt innerhalb der bestehenden Gerätebreite von 132 mm; die neutralen Endpfosten reichen bis Y±65,5. Nur beim Entriegeln können sie kurz bis etwa Y±66,1 reichen. Die neuen P09-Seitenarme erweitern den Gehäusegrundriss am Handgelenk um 2,5 mm von X−46,1 auf X−48,6. Die gedruckte P01-Grundplatte braucht dafür keine Änderung.

`local-enclosure-preflight.json`: **307 Prüfungen PASS**, einschließlich genau eines gültigen Solids je Teil, keiner neu eingeführten Überschneidung mit allen R10-Fremdteilen, freiem vollständigem 20-mm-Montageweg des geschlossenen Moduls, freiem 15-mm-Deckelweg mit integriertem Kabelhalter sowie positivem Halteeingriff beider Hakenpaare. Die Freigabewege enthalten gespreizte Haken; die elastische Verformung ist geometrisch idealisiert. Die Biegearme sind zusätzlich durch ganze Hüllboxen über den Montageweg auf freien Raum geprüft.

`motion-preflight.json`: **882 Prüfungen PASS** der 21 neuen additiven Gehäuseprimitive gegen 42 bewegte bzw. optionale R10-Zielkörper. Die vollständige korrelierte Domäne u≥0, p≥0, a≥0, p+a≤2, u+p+a≤30 und e±0,8 wird über ihre 12 Eckpunkte exakt extremisiert. Ganze in X gesweepte konservative Ziel-Hüllboxen enthalten alle Zwischenstellungen; gegen jede neue Primitive werden exakte OCP-Schnitt und Abstand geprüft. Der kleinste konservative Restabstand beträgt **9,35 mm**. Federn, beweglicher Schalter, ISO-Hülsen und S01-Adapter nutzen vollständige Quellhüllen. Diese Bewegungsaussage ist nicht aus einzelnen Hubpositionen interpoliert. Die native R11-BRep-Identität zur beschriebenen CSG bleibt eine getrennte Voraussetzung.

`toolpath-preflight.json`: **PASS** am tatsächlichen lokalen H2D-PLA-Prüfslice. Beide Teile beginnen auf dem Bett, beide Wannenhaken werden bis Z16,2 gedruckt, beide Deckelarme samt Haken sind vorhanden, und die USB-Dachfläche bleibt gestützt. Die offiziellen H2D-Makros blieben unverändert. Ihre bekannten Parserdiagnosen T1001/T65535/T65279 treten auf; Import und Schnitt beenden beide mit Code 0. Es erfolgt keine Übertragung an einen Drucker.

## Weiterverwendung durch das übergeordnete R11-Build

`build_enclosure.py` stellt `source_patch(source)` für den FeatureScript-Quelltext und `expected(old)` für unabhängiges natives BRep-Auditing bereit. `enclosure-spec.json` beschreibt alle additiven Primitive. Die Funktion ändert ausschließlich den Elektronikgehäuseblock, entfernt die P10-Source-ID und verwendet für die vorhandenen Prism-Helfer deren tatsächliche `...body`-Extrusions-ID. Die anderen Geometrieblöcke einschließlich P01 bleiben unverändert.
