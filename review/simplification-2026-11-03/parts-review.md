# R12 – vollständige Durchsicht der Druckteile

Stand: 03.11.2026. Ausgangspunkt ist das eingefrorene R11, `review/flat132-click-assembly-2026-11-03/fingerworker_flat132_PLA_click.fs` SHA-256 `c8ec18f08149553001ccf8173f35fe57eee6a16be0294be2d7f88577f658cf5e`, nativer STEP SHA-256 `4c7b412eb5700e6ff8dc985c7ab8182e5acc7003a645ecac3291e88fe455d6e7`. Die nachstehend beschriebene Vereinfachung ist als **R12 in Onshape umgesetzt und nativ geprüft**: sieben Gerätedruckteile, zehn Stücke im federfreien Passpaket und93 native CAD-Körper. Beide Vorspannverstellungen sind entfernt;21 Hardwarekörper entfallen. Die realisierte Konstruktion und die verworfenen Kandidaten sind nachfolgend getrennt beschrieben.

Die finale [native Geometrieprüfung](validation/native-geometry.json) besteht286 Prüfungen: P01, P06 und P08 stimmen exakt mit der erwarteten Geometrie überein;90 weitere Körper bleiben identisch zu R11. [Bewegung und Entriegelung](validation/native-motion.json) bestehen77 Prüfungen; [Sensorservice und Werkzeugzugang](validation/service-native.json) bestehen772 Pfad- und10 Werkzeugprüfungen. Dazu kommen die unabhängigen [28 Frontprüfungen](independent-fixed-front-check.json) und [12 Q01-Prüfungen](fixture/validation.json). Die [finalen Druckmerkmale](../../print/bambu-R12-simplified-2026-11-03/validation/print-feature-check.json) wurden am tatsächlichen Slice kontrolliert. Maßgebliche Dateien, Hashes und Geltungsgrenzen stehen in der [finalen Spezifikation](final-specification.json).

Diese Nachweise betreffen nominelle Geometrie und berechnete Druckwege. Physische PLA-Passung, Rastkraft, Kriechen, Belastbarkeit und Sensorkalibrierung bleiben am realen Muster zu prüfen.

## Ergebnis und sinnvolle Teilzahl

Der deutlichste unnötige Aufwand sitzt in den beiden hinteren Rücklaufanschlägen. **P060, P061, P120 und P121 wurden durch eine einzige abnehmbare hintere Traverse P06 ersetzt**. Das reduziert die tatsächlichen gedruckten Geräteteile von **10 auf 7**. Die beiden unveränderten Stangen-Formhilfen H040/H041 und die neue R12-Passhilfe Q01 werden separat gezählt: Das Passpaket hat **10 statt 13 Stücke**. Optionale S01-Federadapter sind darin weiterhin nicht enthalten.

Zusätzlich wurde P09 als feste Unterseite der P01-Handballenauflage lokal konstruiert und tatsächlich probeweise gesliced. Dieser Kandidat wurde **verworfen**: Dabei liegt Support auf der PCB-Halterfläche mit nur 0,05 mm nominellem Spalt zur Bauteilhülle. Eine von Support befreite Fläche kann diese knappe Passung nicht verlässlich erhalten. Der separate R11-Deckel wird sauber ohne Stützen gedruckt und bleibt deshalb erhalten. Die Reduktion auf sechs Teile wird nicht als ausgelieferte Lösung behauptet.

Die rot markierte tiefe axiale Schraube passt in Form und Lage zum hinteren H26-M4-Einsteller bei X≈120…130, Y=±51, Z=7. Sie ist ein **Rücklauf-/Ruhelagen-Einsteller**; ihre Verstellung verändert auch die Federkompression. Sie ist nicht der zentrale H13-Sensoreinsteller mit Ø22-Daumenrad am anderen Geräteende. Die neue Traverse hat die unverstellte Ruhelage `a=0`, mit Kontaktflächen X=119. Nach bestätigter Erweiterung des Auftrags entfällt auch die zentrale H13-Vorspannverstellung. An ihre Stelle tritt eine breite feste P01-Abstützung für die unveränderte H12-Sensorstütze bei X−12. Die Schaltpunktjustierung P11 bleibt erforderlich.

## Prüfung jedes Druckteils und umgesetzte Entscheidung

Die Hüllmaße stammen aus dem tatsächlichen R11-STEP in Einbaulage, nicht aus alten Zeichnungen. P04 und P11 stehen dabei in der R11-Ruhelage q=5.

| Teil | R11-Hülle / Funktion | Entscheidung und konkrete Vereinfachung |
|---|---|---|
| **P01 Hauptteil** | 175,1 × 132 × 35 mm; 6-mm-Boden, zentrale Gleitführung, vordere Stangenlager, Sensorportal, feste Handballenauflage | Einteilig lassen. Hintere Taschen für M4-Mutter/Scheibe/Stellschraube/Schuh schließen und die Gegenform der neuen lösbaren Traverse ergänzen. Vorne alle Einstellertaschen schließen, feste Sensorabstützung bis X−12 ausbilden, H18/H19-Langlöcher durch runde Führungen ersetzen. Die entfallene H15-Servicekerbe wird geschlossen; Sensor-/Jochservice bleibt über +X3,2 und +Z40 erhalten. Die zusätzliche P09-Deckelfusion wurde wegen ihres tatsächlichen Supportkontakts auf der knappen PCB-Halterfläche verworfen. |
| **P04 Fingergriff** | 59 × 126 × 25 mm; 72-mm-Fingeröffnung, 84-mm-Deck, zentrale weibliche Schwalbenschwanzführung, Federreaktion | Die gerundete Grifföffnung und bestehenden R12-Federsitzfreistellungen erhalten. Die verschiedenen Rundungen sind Komfort- und Kollisionsflächen, keine unnötigen separaten Teile. Keine neue Griffdeckel- oder Sleeve-Trennung. R11-Drucklage mit vorderem X-Ende unten beibehalten; diese verbessert die Fingerflächen bei unveränderter Mechanik. |
| **P05 schwimmendes Joch** | 37 × 126 × 22 mm; verteilt die beiden Federkräfte auf den mittigen Sensorpusher; zwei breite Endanschläge | Eigenständiges Teil lassen. Seine Form ist bereits überwiegend ein breiter Balken mit Sensor-/Leitungsfenster und zwei integrierten Anschlägen. Die Sensorausnehmung, vier Kopf-Freistellungen und der Kabelauslass sind funktional. Vereinfachung zu einem geschlossenen Balken würde reale Hardware überdecken; Fusion mit dem Rahmen würde die Messung überbrücken. |
| **P060 + P061 hintere Kappen** | Je 9 × 28 × 26 mm; hintere Stangenaufnahme, Schuhführung, Verschraubung | Durch eine gemeinsame Traverse ersetzen. Die hohe M2-Fangdachform, M4-Mutterfallen, tiefe Schlüsseltasche und Schuhtaschen entfallen. Weiterhin zwei saubere Ø6,2-Stangensockel und vier optionale M3-Befestigungen erhalten. Die Stangenlänge bleibt 141 mm. |
| **P120 + P121 Anschlagschuhe** | Je 9,6 × 19,5 × 23,2 mm; schmale gegabelte Schieber mit integralen Kontaktpads | Als separate Teile vollständig entfernen. Die vier bisherigen Kontaktflächen werden als breit angebundene feste Flächen der Traverse ausgebildet. Damit entfallen dünne Gabeln, Fangschlitze, Brims und schlecht erreichbare Gabelstützen. |
| **P08 Elektronikwanne** | 23,5 × 131 × 16,2 mm; Akku-/PCB-Aufnahme, USB-Zugang, lange Rahmenclips | Separate herausnehmbare Wanne behalten. Nur die zwei überflüssigen alten P10-Piloten schließen: P10 ist seit R11 bereits integral im Deckel. Lange zugängliche Cliparme sowie optionales M2-Lochbild erhalten. Füllen aller Stufen zu einer einfachen Box würde Elektronik bzw. Leitungsraum belegen. |
| **P09 Elektronikdeckel** | 25 × 110 × 6,75 mm; Deckelfläche, integrierte Kabelauflage, zwei Rastarme | Separat und geometrisch unverändert lassen. Die geprüfte Fusion zu P01 spart zwar ein Teil, bringt jedoch im echten Slice Support auf die knapp tolerierte PCB-Halterfläche. R11 druckt den Deckel ohne Stützen und ohne Brücken mit der Außenfläche auf dem Bett. |
| **P11 Schaltnocke** | 6 × 8,4 × 10 mm, 388,7 mm³; manuell einstellbare Nocke, ein M3-Klemmpunkt | Bleibt das kleinste echte Druckteil. Beibehalten, weil die Funktion nicht nur der entfernte hintere Ruhelagensteller ist. Der reale Schalter hat OP-Toleranz ±0,8 mm; die Nocke gleicht diese und die Druck-/Montagetoleranzen aus. Bei festem p=0 entfällt ausschließlich die frühere zusätzliche p-Korrektur. Kein eigenständiger zusätzlicher Clip oder Mini-Pin. Vergrößern ohne neue Griffhöhlung oder Schalterkollision bringt wenig; ein voll integrierter fixer Nocken verliert die notwendige physische Einstellung. |
| **H040 + H041 Druckproxys** | Je Ø6 × 141 mm; federfreie Montagehilfen | Separat halten, als Formhilfen kennzeichnen. Eine Querbrücke zwischen den langen Stäben würde den axialen Einbau von Federn, P04 und P05 blockieren. Keine gedruckte Schrauben-/Mutternkopie ergänzen. |
| **Q01 Passhilfe** | Großer Vierkant/Flansch mit mittigem Schaft; ersetzt Sensor-/Pusherstapel nur im leeren Passaufbau | Neu konstruieren: Der alte Vierkant kollidiert mit dem nun gefüllten Einstellerportal. Die neue R12-Hilfe steht mit großem Block auf der Grundplatte, liegt bei X−12 an und behält P05-Schulter X1 sowie den glatten Ø3-Zapfen. Ein integraler 45°-Übergang macht die Drucklage ohne Stützen möglich. Separat halten und vor echtem Sensoreinbau entfernen. Fusion mit P05 oder P01 würde späteren Sensorwechsel und/oder den Kraftpfad verhindern. Kein Lastbauteil. |

## Hintere Traverse: zulässige räumliche Anordnung

Die hintere Querbrücke sitzt hinter der zentralen Führung. Die Führung endet bei **X=124**, die hintere P04-Fläche in neuer Ruhelage bei **X=119**. Die Querbrücke bei **X125…129, Z4,5…10** besitzt damit 1 mm Abstand zur Führung und 6 mm zum ruhenden Griff. Die seitlichen Stangen liegen bei Y=±51, Z=18 und enden X=125. Breite, Anschlussflächen, Verrundung, freier Einbauweg und die nach dem Zusammenfügen erneut freigeschnittenen Schraubenlöcher sind im finalen nativen Modell geprüft.

Die Traverse muss **abnehmbar bleiben und axial von hinten montiert werden können**. Erst P04 auf die offene Führung schieben, die Stangen/Joch/Federelemente einsetzen, anschließend die Traverse in Richtung −X auf beide Stangen schieben. Ein nach unten gerichteter fester Zapfen in die blinden M3-Inserts ist mit diesem axialen Pfad nicht kompatibel. Für die federfreie Klickmontage sind zugängliche seitliche Rastarme und passende feste Gegenflächen sinnvoll; vier M3-Schrauben können weiterhin nach Bedarf sichern. Clips dürfen nicht im Griffhub oder an empfindlichen Federflächen liegen.

Die beiden Rücklaufseiten müssen dieselbe Ebene X119 besitzen. Für P04 ist die hintere Fläche bei Fahrt `X119−u`. Der Abstand zu einem festen X119-Anschlag ist folglich `u≥0`; bei u=0 liegt nur Außenkontakt vor. Beim Ziehen verlässt der Griff den hinteren Anschlag. Die vorderen Endanschläge bei X30 bleiben Bestandteil des beweglichen P05 und leiten Kräfte zum Sensor. Es darf kein neuer fester P01-Anschlag an derselben Vollhubposition entstehen.

Durch die neue Traverse entfallen **12 Metallteile**: je zwei H26-Stellschrauben, H27-Vierkantmuttern, H28-M2-Fangpins, H29-M2-Muttern, H31-Reaktionsscheiben und H32-Kontermuttern. Die vier H30-M3-Kappenschrauben können als optionale Sicherung erhalten bleiben. Die vier zugehörigen Inserts sind dann nur für die verschraubte Ausführung nötig. Zusätzlich entfallen durch die bestätigte Entfernung der zentralen Verstellung neun Körper: H11, H13, H15, H160/H161, H170/H171, H21 und H22. H12, H18/H19, H20 und P11/H10 bleiben erforderlich. Insgesamt entfallen 21 Hardwarekörper; mit der Druckteilreduktion verbleiben 93 statt 117 native CAD-Körper.

## Verworfene Zusammenlegungen und deren konkrete Folge

| Idee | Warum sie die Funktionen nicht unverändert erhält |
|---|---|
| P04 + P05 | Die Federn benötigen den relativen Weg zwischen beiden Teilen. Die Fusion sperrt den Hub und verändert den vollständigen Kraftpfad. |
| P05 + P01 | Feder- und Vollhubkraft könnten direkt in den Rahmen statt über H02/H01 laufen; der Kraftsensor wäre umgangen. Auch ein scheinbar harmloser fester „Positionierclip“ im axialen Kraftpfad wäre problematisch. |
| Hintere Traverse + P01 | Der seit langem benötigte offene axiale Einschubweg für P04 und Stangen ginge verloren. Das würde die schon einmal aufgetretene Montageblockade wieder einführen. |
| P11 + P04, Nocke fest | Entfernt die manuelle Feinjustierung des realen Omron-Schalters für reale Schalter- und Drucktoleranzen. Der nominale 1-mm-Schaltvorlauf ist kein Ersatz für reale OP-/Druck-/Montagetoleranzen. |
| P11 entfernen und den realen Schalter „in seinen Löchern schieben“ | Die realen Ø2,35-Montagebohrungen bieten bei M2 nur 0,175 mm radiales Spiel, nicht den erforderlichen ±0,8-mm-Bereich. Verschiebbare Gewindeschienen oder zusätzliche Träger würden neue kleine Teile/Hardware erzeugen. Schaltergehäusebohrungen nicht verändern. |
| P08 + P01 | Elektronikzugang und günstige unabhängige Drucklage entfallen. Die vorhandene Wanne wird nach −Z herausgenommen; starre Fusion würde diesen Zugang schließen. |
| P08 + P09 | Ein dauerhaft geschlossenes Gehäuse ist nicht montierbar. Ein neu eingeführtes PLA-Filmscharnier ist für die bisherigen lösbaren Clips kein nachgewiesener Ersatz. |
| P09 + P01 | Geometrisch einschließlich nachgebesserter H15-Servicekerbe möglich, aber im tatsächlichen Probeslice Support auf der nur 0,05 mm von der PCB-Bauteilhülle entfernten Halterfläche. Der separate Deckel hat diese Druckoberflächen-Einschränkung nicht. Deshalb verworfen. |
| H05/H06-Federsitze direkt in P04/P05 als PLA | Die vier 3-mm-Stahlsitze verteilen die Federendenlast. Drucken/integralieren ist als separater Last-/Kriechversuch möglich, erhält die bislang geplante belastete Funktion aber nicht nachweisgleich. Es reduziert Kauf-/Metallteile, nicht die zehn vorhandenen P-Druckteile. |
| H02/H01-Stapel in P05 integrieren | Sensor ist reale Hardware; mittige definierte Krafteinleitung und freie Sensorränder sind notwendig. Vereinfachung durch breite unkontrollierte Auflage verfälscht die Kraftmessung. |

## Druckbarkeit und Formen

P01 soll auf seiner breiten Unterseite stehen. Den 6-mm-Boden und die beiden abgerundeten Fenster erhalten; eine massive Rechteckplatte würde mehr Material verbrauchen und die Handhabung ohne ersichtlichen Funktionsgewinn verschlechtern. Kleine abgesetzte alte Muttern-/Schuhtaschen hinten sind nach Ausbau der Einsteller tatsächlich überflüssig und dürfen verschwinden. Vorderes Sensorportal und vorhandene breite Handballenstützen erfüllen konkrete Last-/Servicefunktionen.

P04 braucht weiterhin die R11-Drucklage mit vorderem X-Ende auf dem Bett und Support nur an freigegebenen Rückseiten. Der damalige gesamte G-Code prüfte acht Finger-/Führungs-/Bohrungsflächen ohne Supportkontakt. Das ist eine bessere vorhandene Lösung als eine neue Griffteilung oder ein zwingender Materialwechsel. PLA bleibt Standard; PETG als zweite Support-Schnittstelle ist optional und für den vorliegenden Vereinfachungsschritt nicht erforderlich. Werden P04-Flächen doch geändert, gilt der alte Oberflächenbericht nicht automatisch weiter.

Die neue feste hintere Traverse entfernt gerade die kompliziertesten kleinen Druckformen: zwei dünne gegabelte Schuhe samt Stützräumen. Ihre Orientierung und beide Cliparme wurden mit dem tatsächlichen finalen nativen STL gesliced; P06 benötigt keine Stützen. Ein zusammenhängender breiter Bettkontakt und in der Druckebene gebogene PLA-Arme sind einem einzelnen aufgestellten dünnen Fanghaken vorzuziehen. P08 behält seine beiden langen Rahmenclips, P09 seine lösbaren Deckelclips.

## Bewegungsregeln, Dokumentation und Software

Beide Vorspannverstellungen entfallen vollständig; **a=p=0** sind feste Konstruktionswerte:

- Weder `rearAdvance` noch `preloadAdjustment` sind Benutzerparameter.
- Absoluter Schlittenversatz `q=5+u`; dynamisch `0≤u≤30 mm`.
- ISO mit beiden 81-mm-Hülsen: `q=20 mm`, Anfahrweg `u=15 mm`.
- P11-Position `k=camTrim` mit `camTrim∈[−0,8,+0,8] mm`.
- Federlänge `L=101−q`; in Ruhe **L=96 mm**. Feste Einbaukompression bleibt erhalten: DF2194 mit102mm freier Länge wird um6mm verkürzt, DF2185 mit105mm um9mm. Rechnerische Paarkräfte sind39,684N bzw.66,762N anhand der dokumentierten Nennraten; keine Messwerte. „Keine Verstellung“ bedeutet nicht „kraftfreie eingebaute Federn“.
- Stahlstangen141mm, ISO-Hülsen81mm, Sensor-/Pusher-/Keeperstapel bleiben geometrisch unverändert.

Die folgenden Änderungsstellen sind im R12-Stand nachgeführt; historische Berichte bleiben unverändert:

| Stelle | Umgesetzte Änderung |
|---|---|
| `fingerworker_mvp.fs` | Beide Verstellparameter und ihre Hardwareerzeugung sind entfernt. Ruhelage, Hub, ISO-Text, Labels und Kollisionsgruppen verwenden feste Werte. |
| Neue R12-Kopie/Release-Spezifikation | 93 native Körper,7 Gerätedruckteile,10 Passstücke,21 entfernte Hardwarekörper und a=p=0 sind in der finalen Spezifikation samt Exporthashes erfasst. R11 bleibt eingefrorene Historie. |
| `README.md`, `PRINTING.md`, `EINKAUFSTEILE.md`, `DEVICE_UPGRADES.md` | Aktuelle R12-Einstiege erklären die ersetzten Teile und die feste Anfangskompression. Ältere R7–R11-Berichte sind ausdrücklich historische Stände. |
| Neue Montage-/Verbindungsmatrix | Die aktuelle Montage beschreibt axialen Traverse-Einbau, Entriegelung, M3-Sicherung, P11-Abgleich, festen Sensorservice und die neue Q01. |
| Bambu-Paketgenerator/Layout/STL-Liste | Die vier alten Heckdruckkörper sind durch P06 ersetzt; P01 und Q01 sind neu. Das Paket enthält zehn Stücke auf drei Platten; Zeiten und Verbrauch stammen aus dem tatsächlichen Slice. |
| Bewegungs-/Kollisionsaudits | Der a=p=0-Bereich, volle Griffhub, Latch-Freigabehüllen und Ein-/Ausbaupfade sind am finalen nativen R12 geprüft. Alte R11-Nachweise sind nicht als neue R12-Prüfungen ausgegeben. |
| `overview/content.json` | Obsolete Einstellerhardware und H17-Werkzeug sind entfernt;24 aktuelle Einkaufs-/Werkzeugpositionen und die R12-Checkliste bleiben. H30 sichert den Lastaufbau. |
| `overview/build_overview.py` | Druckliste, Downloads, Prüfberichte, Filter und Counts verweisen auf R12; die erforderlichen Neudrucke sind P01/P06/Q01. |
| `overview/template.html` + Modellgenerator | Die Übersicht verwendet feste30/15-mm-Werte und93 native R12-Körper. Das frühere R11-Modell und die Vorlagen sind separat archiviert. |

Firmware- und iOS-Quelltext enthalten **keine Berechnung des mechanischen Hubs aus den entfernten Vorspannparametern** (Quellsuche am 03.11.2026). Firmware misst den Sensorwert und Schalterzustand; eine funktionale Codeänderung ist für die festen Anschläge daher nicht erforderlich. `firmware/README.md` fordert bereits Prüfung der Kraftkalibrierung nach Änderung von Federartikel, Vorspannung oder Gegenlager. Diese Pflicht bleibt. Keine neue Hardwarequalifikation und kein erneuter Build-Erfolg wird aus einer rein mechanischen Änderung abgeleitet.

## Quellen und Nachweisgrenzen

- Native R11-Bauteilzuordnung: `review/flat132-click-assembly-2026-11-03/validation/native-step-inventory.json`.
- Bestehende Gelenk-/Serviceanalyse: `review/flat132-click-assembly-2026-11-03/ASSEMBLY_JOINT_REVIEW.md`.
- Quellbereiche: P01/Handballen 922–1078; P04/P11 1080–1185; Führung/P05 1187–1237; Sensorportal/Kassette 1239–1426; Feder-/Stangensitze/Heck 1448–1617; P05-Endanschläge/Schalter 1620–1688; P08/P09 499–680.
- Ausgangs-Drucknachweise: `print/bambu-R11-PLA-click-2026-11-03/validation/p04-surface-check.json`, `enclosure-toolpath-check.json`, `rear-shoe-toolpath-check.json`.
- Physische Rastkraft, PLA-Toleranzen/Zyklen/Kriechen, reale Schalterkalibrierung und belastete Funktionsprüfung bleiben am Muster nachzuweisen. Dieser Review ist kein 500-N-Belastbarkeitsnachweis.

## Historischer Kandidatennachweis: Traverse vor Änderung der Front

`audit_rear_candidate.py` liest die tatsächlich exportierten lokalen P01-/P06-STEP-Dateien und den eingefrorenen R11-STEP direkt. Der Kandidatengenerator wird dabei nicht ausgeführt. Ergebnis nach Ergänzung des R0,6-Clipwurzelradius: alle Funktions-/Montageprüfungen bestanden, keine beobachtete Festkörperdurchdringung. Nachweis: `independent-rear-candidate-check.json` mit beiden STEP-Hashes.

- P01 und P06 jeweils genau ein gültiger Solid.
- Sitz der Traverse am Rahmen, Griff, Joch, beiden echten Stangen und vier unveränderten M3-Schraubenhüllen ohne Volumenüberschneidung.
- P04 über den ganzen nominellen 30-mm-Hub: 61 exakte Positionen gegenüber P01/P06; ergänzend kontinuierliche Trennung der neuen Geometrie über X-/Y-/Z-Halbräume.
- Entriegelte P06-Traverse: beide Haken 0,9 mm nach außen, anschließend +X12; 49 exakte Positionen gegenüber Rahmen, Griff und beiden echten Stangen. Die vier M3-Schrauben müssen entfernt sein.
- Konservative vollständige Biegehüllen beider Cliparme frei; beide Haken besitzen tatsächlichen positiven axialen Eingriff nach 0,3 mm versuchtem Zurückziehen.
- Montage des Griffs bei entfernter Traverse: 76 exakte Positionen von Ruhelage bis +X75 gegenüber Rahmen und echten Stangen; kein wieder eingeführtes Einschubhindernis.

Der neue Gate-Körper hat eine Hülle X104,8…129, Y±67,6, Z4,5…28. Die äußersten Clips ergeben **135,2 mm Gesamtbreite**, während der bisherige Boden 132 mm breit bleibt. Die beiden zusätzlichen P01-Gegenhalter reichen bis Y±66,2; zum Griff mit Y±63 verbleibt mindestens 1,2 mm seitlicher Abstand. Die nominale Freisetzung des 1,2-mm-Arms bei 18 mm wirksamer Länge und 0,9 mm Auslenkung ergibt elementar 0,5 % Randfaserdehnung. Dies ist ein Rechenansatz, keine gemessene PLA-Zyklus- oder Traglastfreigabe.

**Grenze der lokalen STEP-Identitätsprüfung:** OCC erzeugte beim Vergleich des nochmals serialisierten lokalen P01 mit dem originalen R11-STEP ungültige Boolean-Ergebnisse an deckungsgleichen gekrümmten Flächen. Ein `IsDone`-Resultat allein war hier kein brauchbarer Volumennachweis. Die sinnlosen Differenzvolumina wurden nicht als Materialverlust interpretiert und nicht als bestanden ausgegeben. Der unabhängige Bericht kennzeichnet diese Identität deshalb ausdrücklich als `INDETERMINATE`. Die gesonderte Prüfung der frischen Geometrie im Speicher bestätigt dagegen gültig `old−new=0 mm³` und 688,199868 mm³ ausschließlich hinten hinzugefügtes Material in X108,2…129; siehe `mechanics/in-memory-frame-scope.json`. Die endgültige native Onshape-Identität wurde gegen die frische Erwartungsgeometrie geprüft und besteht; der nochmals serialisierte lokale P01 wurde dafür nicht als Referenz verwendet. Die bestandenen Montageprüfungen und ihre Geltungsgrenzen bleiben davon getrennt.

## Feste Sensorabstützung und erneuerte Q01

Die finale Front entfernt die zentrale Stellmechanik vollständig. Der feste Stützstock reicht von X−16,2 bis−12, steigt vom BodenZ3,8 auf und hat ein einfaches YZ-Profil: unten Y±9 bisZ9,5, zwei45°-Schultern bisY±11/Z11,5, dann bisZ26. Der spätere Sensor-Taschenschnitt entfernt noch den unteren18×0,4mm-Streifen. Die tatsächliche native Kontaktfläche an H12 beträgt deshalb454,4mm². Das vermeidet eine frei schwebende Stufe beim Druck. Die vier H25-Schraubspitzen und die H12-Seitenohren bleiben außerhalb dieser Fläche; H18/H19 lassen sich durch die runden R2,2-Führungen seitlich entfernen.

P05 beginnt beiX−7; die feste zentrale Stütze endet beiX−12. Dieser5mm-Abstand verhindert eine direkte starre Verbindung zum Joch. Der Kraftpfad bleibt P04 → Federn bzw. P05-Endanschläge → P05 → H02 → H01 → H12 → feste P01-Abstützung. P05 wird weder festgeclipst noch an P01 verschraubt. Die Kontaktfläche verbessert die nominelle Abstützung; Traglast, Kriechen und Sensorgenauigkeit bleiben physisch zu qualifizieren.

Die neue Q01 ist eine einteilige12×22,3×19,5mm-Passhilfe in Drucklage, mit großer12×22,3mm-Reaktionsfläche auf dem Bett. Ihr Fuß setzt auf der tatsächlichen Sensor-Taschenfläche Z2,7 auf, ihre Rückfläche liegt anX−12; SchulterX1 und Ø3-Zapfen bleiben zum unveränderten P05 passend. Ein45°-Kegel ersetzt die früher gestützte Schulterunterseite. Der alte Vierkant, der alte Flansch und deren Stützbereiche entfallen. Die Formhilfe darf nur ohne Sensorstapel, Federn, Federsitze und Isometriehülsen verwendet werden. Generator, genaue Maße und gesonderte geometrische Nachweise liegen unter `fixture/`; der finale native Fitnachweis ist separat hashgebunden.

Die unabhängigen Prüfskripte lesen exportierte STEP-Körper, nicht den Frontgenerator: `independent-fixed-front-check.json` dokumentiert28 nominale Prüfungen am nativen P01 einschließlich454,4mm² H12-Reaktionsfläche, getrenntem Sensor-Kraftpfad und vollständigem Sensor-/Jochservice. `fixture/validation.json` prüft die neue Q01 separat:249,6mm² Reaktionskontakt,48mm² Taschenbodenkontakt,42,223mm² P05-Schulterkontakt,30mm Griffhub, P05-Abziehen und Q01-Herausheben. Der tatsächliche Taschenboden liegt beiZ2,7; deshalb wird Q01 nach dem Abziehen von P05 gerade nach oben entnommen. Die Berichte enthalten ihre Eingabehashes und gelten nur für diese Geometrie.
