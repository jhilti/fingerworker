# R13 – Review der vereinfachten Handballenauflage

Stand 03.11.2026. R13 verändert ausschließlich den Grundrahmen P01. Die übrigen sechs Gerätedruckteile und alle drei Passhilfen bleiben zum R12-Satz kompatibel. Der vollständige vorherige Review aller Teile bleibt als [R12-Bericht](../simplification-2026-11-03/parts-review.md) erhalten.

**Prüfstand:** Die finale native [Geometrieprüfung](validation/native-geometry.json) besteht alle 98 Prüfungen: P01 stimmt exakt mit der unabhängigen Konstruktion überein, die anderen 92 Körper sind unverändert. [Bewegung und Klickmontage](validation/native-motion.json) bestehen 77 Prüfungen; der unabhängige [Sensorservice](validation/service-native.json) besteht 772 Weg- und 12 Werkzeugprüfungen, einschließlich beider M2-Insertpiloten. Alle drei Platten sind tatsächlich gesliced: [allgemeine Druckpfade](../../print/bambu-R13-simple-palm-2026-11-03/validation/toolpath-check.json), [65 Detailprüfungen](../../print/bambu-R13-simple-palm-2026-11-03/validation/print-feature-check.json), [10 Palm-/Stützprüfungen](../../print/bambu-R13-simple-palm-2026-11-03/validation/palm-support-check.json) und [P04-Oberflächenprüfung](../../print/bambu-R13-simple-palm-2026-11-03/validation/p04-surface-check.json) bestehen gegen dieselbe finale R13-Quelle. Reale Passung, Klickkräfte, Handkomfort und Belastbarkeit wurden nicht geprüft.

## Ergebnis der Formprüfung

Die markierte Handballenregion bestand aus einer schmaleren äußeren Rundung, einer größeren mittleren Kontaktfläche, zwei schmalen Stützrippen, kleinen Rippenfüßen sowie abgestuften Auflage- und Abdeckplatten. Die schmalen Rippen und der zentrale Zwischenraum waren aus älteren Konstruktionsständen mit Wartungszugang zur inzwischen entfernten Vorspannung entstanden.

R13 führt diese Region zu zwei großen, zusammenhängenden Grundformen zusammen:

- Ein zur Hand gerundeter Balken mit **Radius 10,25 mm und 116 mm Breite**. Die bisherige mittlere Kontaktrundung bleibt erhalten und wird gleichmäßig zu beiden Seiten fortgesetzt.
- Eine **breite Verbindung** zum Rahmen, nominell X−27…−17,1, Y−58…+58 und Z9,5…30. Ihre senkrechten Außenecken sind mit Radius 2 mm gerundet. Die früher sichtbaren Rippen und Zwischenräume liegen innerhalb dieser Form. Die neue Unterseite über dem 5,25-mm-Zwischenraum hat zwei 45°-Schrägen statt einer breiten flachen Brücke. Diese Schrägen werden ausschließlich aus der neuen Verbindung ausgeschnitten; altes Rahmenmaterial bleibt erhalten.

Die Vereinfachung entfernt kein bestehendes Rahmenmaterial. Der nominelle Volumenzuwachs beträgt **14.580,03 mm³**. Das ist CAD-Volumen, keine Filamentmenge; Infill und Stützen werden erst im Slice berücksichtigt. Die Anzahl der Druckteile bleibt gleich: **7 Geräteteile, 10 Druckstücke inklusive Passhilfen**. Weitere Fusionen wurden bereits im R12-Review geprüft; die neue Palmform ändert deren Einschränkungen nicht.

## Erhaltene Schnittstellen

| Bereich | Erhaltene Funktion und Grenze |
| --- | --- |
| Handkontakt | Bestehende zentrale Rundung bleibt, seitliche Rundung wird einheitlich. Handkomfort am Ausdruck bestätigen. |
| P08-Rahmenclips | Äußere Rastflächen bei Y±63,6…64 und Z14,5 bleiben unverändert. Die neue breite Verbindung endet bei Y±58. Entriegeln weiterhin etwa 0,6 mm nach außen, Gehäuse 20 mm nach unten. |
| Optionale M2-Sicherung | Beide Insertpiloten bei X−26,5/Y±59 werden **nach** der neuen Vereinigung erneut freigeschnitten. Die breite Verbindung würde sonst die innere Kante dieser Bohrungen teilweise füllen. |
| P09-Klickdeckel | P01-Unterseite bleibt bei Z9,5; P09-Oberseite bei Z8,9. Der nominelle Abstand bleibt **0,6 mm**. Der separate, sauber druckbare Deckel wird weiterverwendet. |
| Leitungen und Elektronik | Unterhalb Z9,5 bleibt die ursprüngliche Geometrie erhalten. Kabelauslass und Gehäuseentnahme werden nicht mit einer neuen Wand geschlossen. Reale Kabelradien und Schlaufen bleiben am Aufbau zu prüfen. |
| Sensorabstützung | Fester Reaktionsanschlag X−12 bleibt identisch. Es wird kein Material in die freie Verbindung P05 → H02 → H01 hinzugefügt. H12 bleibt direkt abgestützt. |
| H18/H19-Service | Seitlicher Schrauben- und Hülsenausbau bleibt frei. Die neue Verbindung endet bei X−17,1, hinter der H18-Kopfzugangshülle mit vorderster negativer Grenze X−15,55. |
| Sensorentnahme | Vollständiger Sensor-/Jochstapel weiterhin zunächst +X 3,2 mm, dann +Z 40 mm herausnehmen. Keine Vorspannbauteile mehr zu lösen. |
| Stangen und Führungen | Funktionale Vorderregion ab X−17 bleibt gleich. Die neue Verbindung endet vor Stangenbohrungen und bewegten Teilen. Voller dynamischer Hub bleibt 30 mm. |
| Hintere Traverse P06 | Gemeinsame feste Anschlagfläche und beide PLA-Rastarme unverändert. Vier M3-Sicherungsstellen bleiben für den Funktionsaufbau vorgesehen. |

## Unabhängige lokale Gegenprüfung

Die erste exportierte Kandidaten-STEP wurde getrennt vom Geometriegenerator gegen die tatsächlichen R12-Komponenten geprüft. Alle geprüften Booleans waren gültig und hatten kein Überschneidungsvolumen: P05, P08, P09, Sensor H01, Druckstift H02, Stütze H12, beide H18-Schrauben, beide H19-Hülsen, beide Stangen sowie PCB-, MCU- und Akkuhüllen. Die beabsichtigten P08- und H12-Anlagen bleiben Kontaktflächen.

Nominelle Mindestabstände: P05 zum Rahmen **0,5 mm**, P09 **0,6 mm**, H01 **0,5 mm**, H18 **0,45 mm**, H19 **0,2 mm**, Stangen **0,1 mm**. Beide M2-Pilotinnenräume und beide oberen Clip-Entriegelungskorridore sind frei. Die anschließende Druckrevision verkürzt die neue Verbindung um 0,1 mm und ersetzt ihre flache Unterseite durch 45°-Schrägen. Sie entfernt ausschließlich neues Material und verändert keine der genannten Schnittstellen. Der anschließende native Exportvergleich und der vollständige Servicecheck bestätigen die finale Geometrie; Nachweise sind oben verlinkt.

Die eigene lokale [Geometrieprüfung](mechanics/preflight.json) prüft zusätzlich Materialerhalt, unveränderte Elektronik-Unterseite, beide Rastauflagen, Sensor-Vorderregion und die seitlichen Zugänge. Die abschließenden Nachweise sind in der [finalen Spezifikation](final-specification.json) mit Dateihashes gebunden.

## Druck und Weiterverwendung

Nur **P01** muss beim Wechsel von R12 neu gedruckt werden. P04, P05, P06, P08, P09, P11, Q01 und die beiden Stangen-Formhilfen bleiben nutzbar. Das vollständige Projekt enthält weiterhin drei Platten; Platte 1 enthält nur den neuen Rahmen.

P01 bleibt mit seinem breiten Boden auf der Druckplatte. Die neue Verbindung wächst über den bisherigen Zwischenraum auf 45°-Schrägen zusammen. Eine globale Änderung der Brückenrichtung wurde verworfen, weil sie die vorhandenen Stangenbohrungen verschlechterte. Die bewährte automatische Brückenrichtung bleibt erhalten. Im finalen Slice schließen die neuen Schrägen mit nur **0,460 beziehungsweise 0,450 mm frei gespannter Druckbahn**. Die bestehenden Dächer der vorderen Stangenbohrungen bleiben bei **2,188 mm**. Die neue Handkontakt-Rundung hat keine Stützpfade. Stützkontaktflächen bleiben innerhalb der R12-Konturen (0,02 mm numerische Vergleichstoleranz); die übrigen Stützbahnen innerhalb 0,05 mm. Der vollständige konservative Stütz-Entnahmeraum zur Handseite schneidet das hinzugefügte Material mit **0,0 mm³**. Das bestätigt freie geometrische Zugänglichkeit, keine gemessene Ablösekraft. Elektronikfreiraum und Klickflächen dürfen beim Entfernen der Stützen nicht beschädigt werden. Die gerundete Handkontaktfläche liegt außen zugänglich. P04 behält die R11-Drucklage, bei der keine Stützen auf den geprüften Fingerkontaktflächen liegen.

PLA bleibt Standard. Es werden weiterhin keine Schrauben, Muttern oder winzigen Sicherungsstifte gedruckt. Gedruckte Stangen und Q01 sind nur für den federfreien Passaufbau vorgesehen. Die Funktionshardware sowie die feste konstruktive Federkompression bleiben unverändert; beide Vorspannverstellungen bleiben entfernt.

## Grenzen der weiteren Vereinfachung

Eine durchgehende Wand bis zur Grundplatte würde Elektronik und Kabelservice verschließen. Eine Verbreiterung bis zu den äußeren Gehäusehaken würde ihre Rastflächen und Entriegelung behindern. Ein Vorrücken in die Sensorregion könnte den Messkraftpfad überbrücken oder die H18/H19-Zugänge sperren. Deshalb endet die einfache obere Form gezielt an diesen funktionalen Grenzen.

P09 bleibt separat: Die in R12 geprüfte Fusion erzeugte Stützen an der PCB-Haltefläche mit nur 0,05 mm nominellem Spalt. P05 bleibt beweglich und vom Rahmen getrennt; eine starre Verbindung würde die Kraftmessung umgehen. P11 bleibt für den Schaltpunktabgleich ±0,8 mm separat. Diese Trennstellen sichern konkrete Funktionen und sind keine verbleibenden dekorativen Kleinteile.

Montage siehe [MONTAGE.md](MONTAGE.md), Änderungsliste siehe [BOM_Aenderungen.csv](BOM_Aenderungen.csv).
