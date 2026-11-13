<!-- CURRENT_FLAT132_R20_START -->
> **13.11.2026 – Flat132 R20: integrierte Positionierzapfen.** P06L/P06R erhalten je einenØ5×2-mm-Unterseitenzapfen; P01 passende hinten offene Sacknuten. So bleibt das axiale Aufschieben auf die Stangen möglich. Schraubenlos nur federfrei und unbelastet positionieren. **Vier M3×8 sind vor Federkraft, auch vor Vorspannung in Ruhestellung, erforderlich.** [Onshape R20](https://cad.onshape.com/documents/15316cc6370631845af136b2/v/0e06e3d98b9ecb574ee41402/e/d253eb87b70818ebde8215f0) · [Native STEP](review/rear-locating-pegs-2026-11-13/native/Flat132_R20_final_AP214.step) · [Review](review/rear-locating-pegs-2026-11-13/README.md) · [Montage](review/rear-locating-pegs-2026-11-13/MONTAGE.md).

> **Druckvorbereitung auf Nutzerwunsch zurückgestellt (PRINT_SETUP_DEFERRED_BY_USER).** Kein neues Bambu-Projekt, kein neuer Slice oder Druckauftrag. Native R20-CAD-Prüfung:94 Körper,91 gegenüberR19 geometrisch unverändert. Frühere Druckpakete enthalten diese neuen Zapfen/Nuten nicht.
<!-- CURRENT_FLAT132_R20_END -->

<!-- CONNECTED_R15_READY_START -->
> **Historischer Stand R15 – für R20 den CAD-Stand oben beachten; Druckvorbereitung zurückgestellt.** Vorbereitungsnachweis vom 08.11.2026: [PLA-Basic-Projekt](print/bambu-R15-inboard-straps-2026-11-08/Fingerworker_R15_H2D_04mm_PLA_Basic_Print_Ready.3mf) · [Print-Ready-Paket](print/bambu-R15-inboard-straps-2026-11-08/Fingerworker_R15_H2D_04mm_PLA_Basic_Print_Ready_Package.zip). Sechs Teile auf einer Platte, alle ohne Brim, erforderliche PLA-Stützen erhalten. Linke 0,4-mm-Standarddüse, Bambu PLA Basic damals aus AMS A3; kein PETG. GUI-Schätzung **10 h 49 min / 233,58 g**. Sendedialog geprüft, **kein Druckauftrag gestartet**. [Nachweise](print/bambu-R15-inboard-straps-2026-11-08/connected-ready-delivery.json). Die damalige Generic-PLA-Variante bleibt als historische Ausgangsdatei erhalten. Die damalige AMS-Zuordnung ist keine Bestätigung für R18.
<!-- CONNECTED_R15_READY_END -->

# Fingerworker Federn Vorspannung und Isometrie

Stand 11.10.2026. `fingerworker_mvp.fs` verwendet die am 29.09.2026 bestellten Febrotec-Paare. Der vorhandene Parameter `lightSprings` bleibt aus Kompatibilitätsgründen erhalten: TRUE wählt **0X-DF2194**, FALSE **0X-DF2185**. Die früheren 2-N/mm-Ziel- und 7,8-N/mm-norelem-Varianten sind ersetzt. Federn sind nominelle Referenzkörper; die Helix bildet weder geschliffene Enden noch eine Fertigungszeichnung ab.

## Federn

| Variante | OD / ID / freie Länge mm | Rate je Feder N/mm | Paarkraft offen p0 / p2 N | Paarkraft bei 30 mm p0 / p2 N |
| --- | --- | ---: | --- | --- |
| 0X-DF2194 | 14,8 / 10,8 / 102 | 3,307 | 6,614 / 19,842 | 205,034 / 218,262 |
| 0X-DF2185 | 14,5 / 10,5 / 105 | 3,709 | 29,672 / 44,508 | 252,212 / 267,048 |

Beide haben nominal Ø2-mm-Draht. Die Helix-Mittelradien sind 6,4 beziehungsweise 6,25 mm; illustrative Gesamtwindungszahlen 25 beziehungsweise 24 folgen näherungsweise aus der dokumentierten Blocklänge. Die Einbaulänge bleibt `101 − p − x` mm, mit p=0…2 und x=0…30 mm. Kraftberechnung: `2 × k × (L0 − Einbaulänge)`. Die kürzeste Einbaulänge 69 mm liegt oberhalb der dokumentierten Katalog-Prüflängen 58,59 beziehungsweise 56,14 mm. Lauf, Paarabweichung und Ermüdung sind am realen Aufbau zu prüfen; die Zahlen sind keine Gerätetraglast.

Nur gleiche Paare einsetzen. Die 105-mm-Variante beginnt mit 4–6 mm Kompression; der leichtere Satz mit 1–3 mm. Zusätzliche Distanzscheiben sind für die nominelle Geometrie nicht erforderlich. [Beschaffungsnachweis](procurement/springs/KATALOGFEDERN.md).

## Gemeinsame Vorspannung

Der M6×1-Einsteller verschiebt Kassette, Sensor, Druckstift, Joch und beide festen Sitze gemeinsam um 0–2 mm. Eine Umdrehung entspricht 1 mm. Kassettenretention: zwei M3×8-Schrauben mit OD4/ID3,2×4-mm-Stahlhülsen in Langlöchern. Die Schrauben verspannen Stahlteile, nicht die gedruckten Gleitflächen. Die M3×4-Klemmung drückt über ein Messingdruckstück auf das M6-Gewinde. Vor Verstellen lösen; nur unbelastet einstellen und nicht gegen den Verstellanschlag weiterdrehen.

Die Sensor-Hauptstütze ist eine bearbeitete Stahlkassette mit entlasteter Rückenmitte. Halteplatte und captive Stahlmuttern tragen die Einstellmutter. Der Druckstift besitzt eine Ø8-mm-Schulter und ein M3-Halteende mit Vierkantmutter im Joch. Alle aktuellen Kauf-/Sonderteile stehen in [EINKAUFSTEILE.md](EINKAUFSTEILE.md).

Der Sensor selbst muss beim Ausbau beider Federn weiterhin unterstützt werden. Eine Fangsicherung darf keinen parallelen Messkraftweg schaffen. Bedienzugang, Kabelspiel, Gewindeeingriffe und enge nominelle Abstände sind am Muster zu bestätigen.

## Isometrie

Beide Federn durch zwei Stahlhülsen OD16/ID8×86 mm ersetzen. Enden plan und entgratet; Längenpaarung innerhalb 0,05 mm. Niemals Feder/Hülse mischen oder unter Last umbauen.

Kraftweg: Fingerauflage → bewegte Sitze → beide Hülsen → feste Sitze → schwimmendes Joch → Druckstift → Sensor → Kassette/Einsteller → Rahmen. Die Hülsen umgehen den Sensor nicht. Die mittige Führung kann durch Reibung trotzdem Kraft am Sensor vorbeileiten.

Die Sitzposition beträgt 15−p mm Hub, also 15 beziehungsweise 13 mm bei minimaler/maximaler Vorspannung. Ohne Rücklauffedern muss zunächst der freie Weg aufgenommen werden. Der normale Vollhubschalter löst beim isometrischen Halten nicht aus; eine offene NC-Leitung bleibt ein Fehler. Betriebsmodus an USB mit `mode 1` wählen, separate Kalibrierung verwenden; `mode 0` für dynamischen Hub.

## Digitale und physische Prüfung

`review/check_device_upgrades.py` prüft 2562 Federkraft-/Einbaulängenfälle und 21 Isometriepositionen. Ergebnis: [device-upgrades-validation.json](review/device-upgrades-validation.json). Das Skript kompiliert FeatureScript nicht und prüft keine Festigkeit. Der Quelltext vor der Federrevision liegt unter `review/software-2026-10-11/fingerworker_before_springs.fs`.

Die älteren Onshape- und Drucknachweise bleiben datierte Belege. Sie dürfen nicht mit einem neuen Quelltext-Hash als frische Prüfung ausgegeben werden. Aktuelle Live-Regeneration und deren Befunde werden separat unter `review/software-2026-10-11/` dokumentiert. Die elf Druckteildefinitionen sind bei dieser Änderung unverändert; Handpassform, Belastbarkeit, Kabel-/Gehäuseeinbau und elektrische Hardwarequalifikation bleiben offen.
