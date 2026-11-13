# R11 – Montageverbindungen gegenüber R10

Stand 03.11.2026. Diese Matrix trennt die federfreie Steckmontage von der Sicherung und Krafteinleitung des späteren Funktionsaufbaus. Grundlage ist R10, SHA-256 `5ce830ff2b06cd8d318d3c44dbc1f3385697526a9a679d2a2078f64f81854237`. Sie ist ein Konstruktionsreview; erst die finalen nativen Exporte und ihre Prüfberichte bestätigen den tatsächlich erzeugten Stand.

## Alle 15 bisherigen Druckteile und die Passhilfen

| Teil | Federfreie Montage / R11-Änderung | Funktionale Sicherung / Service |
|---|---|---|
| P01 | Vorhandenes R10-Hauptteil bleibt unverändert; Auflage schon integral. | Vorhandene Sitzflächen und Schraub-/Insertbohrungen bleiben verfügbar. Keine neue Traglastfreigabe. |
| P04 | Zentralführung weiterhin von hinten einschieben. Das ist eine Gleitführung, keine Rastverbindung. Fingeroberfläche durch neue Drucklage verbessern. | Hintere Baugruppe hält den Schlitten im vorgesehenen Bereich. Kein fester vorderer Anschlag darf den Sensorpfad überbrücken. |
| P05 | Weiterhin lose/floating auf Stangen und Q01 bzw. später dem Pusher ausrichten. Nicht an P01 festklicken. | Unter Last muss die Reaktion über Pusher und Sensor laufen. Eine starre Verbindung zum Rahmen würde die Messung verfälschen. |
| P060 | R10-Kappe unverändert, axial von hinten auf die bereits eingelegten Stangen schieben. Eine echte Rahmenrastung wurde nicht hinzugefügt. | Zwei M3×8 und ihre Inserts bleiben für sichere Befestigung vorgesehen. Erst nach Entlastung entfernen. |
| P061 | Spiegelgleiche zweite Kappe wie P060. | Wie P060. |
| P070a | Als separates Mikroteil entfernt; seine alte Kontaktgeometrie wird Bestandteil von P120. | Harte PLA-Anlage statt Dämpfung; Stoß-/Dauerverhalten ist noch zu prüfen. |
| P070b | Wie P070a, zweiter Kontakt in P120. | Wie P070a. |
| P071a | Wie P070a, erster Kontakt in P121. | Wie P070a. |
| P071b | Wie P070a, zweiter Kontakt in P121. | Wie P070a. |
| P08 | Zwei lange integrale Rastarme greifen über die vorhandenen Enden der R10-Auflage; kein neuer Gegenhalter in P01. | Zwei vorhandene M2-Gehäuseschrauben bleiben optional. Seitliche Rastarme lösen, Gehäuse nach unten entnehmen. |
| P09 | Zwei lange Rastlaschen halten den Deckel an neuen Außenfängen von P08. | Drei vorhandene Deckelschraubstellen bleiben optional. Deckel erst am ausgebauten Gehäuse öffnen. |
| P10 | Als separates Mikroteil entfernt; Kabelauflage wird in P09 integriert. | Die Kabel müssen bei abgenommenem Deckel zugänglich bleiben; keine starre Klemmung über die Leitung erzwingen. |
| P11 | Bleibt separat und manuell einstellbar. Die vorhandene Form ist bereits geführt; keine zusätzliche Rastung freigegeben. | M3×10-Klemmung bleibt: die erforderliche Position ist `camTrim − preload`, insgesamt −2,8…+0,8 mm. Einfaches Fusionieren oder ein Festanschlag würde die Schalteinstellung blockieren. |
| P120 | Zwei bisher lose Pads mit dem großen Schuh vereinigt; keine Klebestellen. Die Zunge bleibt in P060 geführt und 0…2 mm verschiebbar. | M2-Fangpin und Mutter bleiben; M4-Einsteller, Reaktionsmutter/-scheibe und Kontermutter erhalten ihre Funktion. |
| P121 | Spiegelgleich zu P120. | Wie P120. |
| H040 / H041 als Druckproxys | Ø6×141 mm, zum federfreien Ausrichten einstecken. | Formhilfen, keine freigegebenen lasttragenden Stangen. Echte Stahlstangen bleiben der bisherige Funktionsstand. |
| Q01 | Großer 12-mm-Vierkant mit Flansch und Ø3-Schaft positioniert den leeren Aufbau. Keine neue axiale Verriegelung. | Nur federfreie Passhilfe. Vor Einbau des Sensor-/Vorspannstapels vollständig entfernen. Nicht als Lastbauteil verwenden. |

## Warum P06 / P11 jetzt keine zusätzliche Rastung erhalten

P06 muss bei unverändertem R10-Rahmen axial nach −X über die Stangen gelangen. Ein senkrechter Steckzapfen in den vorhandenen M3-Piloten würde diesen Einbauweg sperren. Die vorhandenen Piloten sind blind und bieten keine verlässliche Hinterschneidung; die 0,5-mm-Fußstufe allein reicht für keine robuste PLA-Schnappverbindung. Eine Stangenklemmung könnte nur Reibschluss liefern und wäre keine positive Rahmenrastung. Deshalb bleiben die vier M3-Schrauben ehrlicherweise die sichere Kappenbefestigung.

Auch die M2-Sicherung des verstellbaren Schuhs wird beibehalten. Ein starrer gedruckter Zapfen lässt sich nicht einfach in den geschlossenen Fangschlitz einschieben. Für eine lange federnde Fangzunge konkurrieren im kleinen Kappenraum das mittige M2-Kopflager, die Muttertasche, die M3-Gegenbohrungen und die notwendige Stangenwand. Ein PLA-Arm mit 0,8 mm Biegedicke und mindestens 16 mm wirksamer Länge könnte rechnerisch bei höchstens 1 mm Auslenkung unter 0,5 % nomineller Randfaserdehnung bleiben; Druckrichtung, freie Rückstellung und die unveränderten optionalen Schraubstellen sind dafür aber noch nicht geometrisch nachgewiesen. Dieser Vorschlag wurde nicht in R11 übernommen.

P11 wirkt auf den Mikroschalter, liegt außerhalb des Sensor-Kraftpfades und muss nach Änderungen der Vorspannung manuell verschoben werden. Die M3-Klemmung erhält diese stufenlose Einstellung. Eine größere starre Nase im vorhandenen Schlitz oder eine mit P04 verschmolzene Nocke ist dafür kein gleichwertiger Ersatz.

## Funktionshardware und kleine Teile

| Verbindung / Hardware | Bewertung |
|---|---|
| H03-Federn / H05-H06-Sitze / P04-P05 | Ohne Federn lässt sich der Passaufbau stecken. Beim Funktionsaufbau die echte Federführung und Endsitze beibehalten; eine Rastung ist kein Federkraftnachweis. Große integral gedruckte Sitze wären ein eigener künftiger Last-/Kriechversuch. |
| H02-Pusher / H20-Mutter / P05 | Pusher-Schulter ist die axiale Krafteinleitung; H20 hält den Pusher. Nicht durch einen Rahmenclip ersetzen oder P05 an P01 festlegen. |
| H01-Sensor / H12-Rückplatte | Planare Abstützung und Zentrierung bleiben maßgeblich. Sensor und Stahlrückplatte sind nicht als freigegebene Druckteile deklariert. |
| H23-H25-Sensorkeeper und vier Abstandshülsen | Die Hülsen begrenzen die Verschraubung und halten die Keeper-Lücke. Keine winzigen Druckkopien; die spätere Baugruppe benötigt weiterhin reale, geeignete Teile. Ein neuer großer Druckkäfig wäre separat auf Sensorrandfreiheit zu prüfen. |
| H18-H19-Kassettenfang | Die Abstände verhindern, dass Schrauben die Kassettenführung einklemmen. Die Kassette muss den 0…2-mm-Vorspannweg behalten. Keine feste Rahmenrastung als Ersatz. |
| H11 / H13 / H15-H17-Vorspannung | Gewindeverstellung und innere Reaktion bleiben funktionale Hardware. Die durch R10 eingeführten sensorseitigen Köpfe und der H15-Serviceweg bleiben frei. |
| H21-H22-Vorspannklemmung | Winziges Messing-Druckstück bleibt Kauf-/Metallteil; keine winzige PLA-Reproduktion. Es schützt das Einstellgewinde. |
| H26-H27 / H31-H32-Hintereinstellung | Die beiden M4-Einsteller, Vierkantmuttern, großen Scheiben und Kontermuttern halten die gleiche beidseitige Einstellung. Eine Rastung würde die kontinuierliche Einstellung nicht unverändert ersetzen. |
| H28-H29-Schuhfang | M2-Pin und Mutter bleiben als positive, lösbare Sicherung mit 2 mm Schuhweg. Keine winzigen gedruckten Pin-/Mutterkopien. |
| H30-Kappenbefestigung | Vier M3×8 bleiben funktional; Rahmen/R10 kompatibel. |
| H09-Mikroschalter | Vorhandene M2-Befestigung bleibt. Gehäuse, Hebel und elektrische Anschlüsse sind echte Hardware. |
| PCB, Akku, Kabel, USB | In die vorhandenen Aufnahmen legen; Kabelauflage ist nun im größeren Deckel. Reale Leitungsführung, Zugentlastung und Akkupassung am Muster prüfen. |

## Exakte Schuhgeometrie und neuer Druck

`check_rear_shoes.py` stellt für den finalen Prüfer `expected(old)` bereit: `P120 = old P120 ∪ old P070a ∪ old P070b`, entsprechend P121. Die lokal aus dem R10-STEP konstruierte Variante ist für beide Schuhe genau ein gültiger Solid; symmetrische Differenz zur alten Gesamtgeometrie **0 mm³**, Volumenzunahme je Schuh **81 mm³**. Die zur Fusion ergänzten 0,2 mm liegen vollständig im alten Schuhmaterial.

Für jede Einstellung `a ∈ [0,2]` gilt dieselbe gemeinsame Translation. Die Front der integrierten Kontaktflächen bleibt `X = 119 − a`. Die hintere Kontaktfläche des Schlittens ist `124 − (5 + a + u) = 119 − a − u`; damit beträgt der Abstand `u ≥ 0`, mit Außenkontakt genau bei `u = 0`. Es entsteht weder eine neue Interferenz noch ein festgelegter Einstellweg.

Die alte Drucklage „Xmin vorne unten“ wird für die vereinigten Schuhe verworfen: Die neuen Anlageflächen stehen 0,2 mm vor der alten unteren Schuhfront, die dadurch nicht mehr direkt auf dem Bett läge. Der gewählte Kandidat liegt mit **nativer Zmax-Fläche nach unten**, Rotation `diag(1,−1,−1)`. Er besitzt eine zusammenhängende T-förmige Bettanlage von **61,7 mm²**, eine nach oben offene Stangengabel und einen senkrechten Fangschlitz. Lokaler Bambu-Probeslice: **0 Bridge-Segmente, kein Support im Fangschlitz**, ungefähr **0,181 g Support**. Normale automatische Stützen nur vom Bett, 0,25 mm oberer Stützabstand und 4 mm Außenbrim sind vorgesehen. Die Stützen an den äußeren Überständen müssen sauber entfernt werden.

Diese lokalen Schuhmeshes sind ausdrücklich Prüfgeometrie. Das ausgelieferte Paket muss dieselbe Lage auf den finalen nativen R11-STLs verwenden und noch einmal insgesamt gesliced und geprüft werden. PLA-Rastzyklen, reale FDM-Toleranzen und Festigkeit sind erst am Muster nachweisbar.

### Nachprüfung des finalen Gesamtpakets

Der finale Gesamt-Slice wurde anschließend für **beide nativen R11-Schuhe auf Platte 2** geprüft: erste Schicht vollständig in allen vier T-Fußbereichen vorhanden, rund **98,92 % Abdeckung** der mit der tatsächlichen 0,15-mm-Elefantenfußkorrektur erwarteten Anlagefläche, **keine Bridge-Segmente und keine Stützen im M2-Fangschlitz**. Die reale Stangengabel enthält Stützanteile. Im exakten finalen STEP ist der gesamte durchgehende Entnahmeraum **R4,9, X118…130 mm** bei beiden Schuhen materialfrei; die Stützen sind dadurch über die offene Gabel und axial von vorne/hinten erreichbar. **Gabelstützen vor Einbau der Stangen vollständig entfernen**, ebenso die äußeren Stützen an den Überständen. Die Passung nicht durch die Befestigungsschrauben zusammenziehen.

Hashgebundener Nachweis: [rear-shoe-toolpath-check.json](../../print/bambu-R11-PLA-click-2026-11-03/validation/rear-shoe-toolpath-check.json). Er prüft den Gesamt-Slice SHA-256 `269f5d8eb7410609547f56954c892a9a56e0ee8c164138815c58cda523b16a36` gegen die tatsächlichen nativen STL-Dateien und Layouttransformationen. Dies bestätigt die nominelle Geometrie und Werkzeugwege, noch keinen physischen Ausdruck oder eine Festigkeit.
