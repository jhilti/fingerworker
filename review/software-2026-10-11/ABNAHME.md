# Fingerworker Abnahme am realen Prototyp

Stand 11.10.2026. Software und digitale CAD-Prüfungen ersetzen diese Messungen nicht. Ein Punkt ist erst abgeschlossen, wenn Ergebnis und Messnachweis am konkreten Muster vorliegen. Keine zulässige Gerätezugkraft oder Messgenauigkeit wird hier als bereits bestätigt angenommen.

## Muster und Konfiguration

Musterkennung: ______  Datum: ______  Prüfer: ______
Drucker/Material/Charge/Wände/Infill/Orientierung: ______
Federartikel und gemessene Paarkennlinien: ______
Vorspannung: ______  Betriebsmodus: ______  Gegenlager/Seilaufbau: ______
PCB-/XIAO-Revision: ______  Firmware-SHA256/Build: ______  Kalibrierpunkte: ______
Vorgesehene maximale Gerätezugkraft: ______ N
Geforderte Messabweichung / Wiederholbarkeit / Drift: ______
Vorgesehene Lastspielzahl und Lastprofil: ______
Messgeräte und deren Unsicherheiten: ______

Die Zielwerte müssen vor dem Last-/Messversuch festgelegt werden. Die nominalen Federendkräfte bis 267,048 N, der Sensorbereich und geschlossene STL-Netze sind keine Freigabe dieser Zielwerte.

## Reihenfolge und Kriterien

| Schritt | Durchführung | Abschlusskriterium | Nachweis |
| --- | --- | --- | --- |
| 1 Handpassform | Federfreies Muster, echte Finger-/Handballenposition, Hub 0–30 mm | Kein störender Kontakt, Daumenraum frei, sichere Auflage und zugängliche Einstellung | Fotos/Notizen ______ |
| 2 Montage | Metallteile, captive Muttern, Druckstift, Einsätze, Feder-/Hülsenwechsel | Vollständiger Eingriff, keine gelösten Halter, kein verspannter Gleitweg; Sensor beim Wechsel unterstützt | Maße/Check ______ |
| 3 Führung/Federn | Beide Artikelpaare, Vorspannung 0/2, mittiger/einseitiger Zug | Rücklauf, kein Klemmen/Ausweichen; minimale Länge ≥69 mm nominal bestätigt | Kennlinien ______ |
| 4 Einbau | Reale Module, Stecker, Kabel und Zellaufnahme | Keine Akkuquetschung, stabile isolierte Halterung, Zugentlastung; Spalte auch bei Verformung frei | Fotos/Maße ______ |
| 5 Elektrik ohne Akku | FIRST_POWER mit Bench-Build, Analog zunächst aus | Bestückung/Polung/Durchgang korrekt, keine Schienenschlüsse | Messprotokoll ______ |
| 6 Versorgung | Oszilloskop DVDD/AVDD/VBOOST/V5A, Kaltstart/Wake/USB-Wechsel, BLE/Brückenlast | ADS1220-Rampen konform, keine Über-/Unterspannung, stabile Referenz und ausreichender PGA-Gleichtakt | Kurven ______ |
| 7 Endlage/Faults | Schalter und jede J3-Ader öffnen, ADC-Ausfall, Einschalten, Standby | Sofortige Messsperre, Freigabe nach stabilem HIGH; Klick unter Last vor beiden Hartanschlägen | Zeitverläufe ______ |
| 8 Mechaniklast | Schrittweise externe Last, mittig/einseitig/schräg, jedes Seilauge einzeln, Wiederholungen | Festgelegtes Lastprofil ohne Schäden/bleibende Verformung; Schnurverschleiss bewertet | Last-/Verformungskurven ______ |
| 9 Kalibrierung | Bekannte Lasten auf/ab, mehrere Punkte, beide Modi und tatsächlich genutzte Aufbauten | Festgelegte Messfehlergrenzen, Drift und Reibung erfüllt; keine Kalibrierung aus Katalogwerten | Rohdaten/Kennlinien ______ |
| 10 BLE/Peak | Echter iPhone-MTU ≥46, Reset-Ack, kurzer Kraftimpuls, Funkverlust, Reconnect, Geräteneustart | Gültige Peaks bis zum ADC-/Sensorzeitlimit erhalten; Fehlerwerte ausgeschlossen; Neustart/Lücken erkennbar | Paket-/Lastprotokoll ______ |
| 11 Bedienung/Speicher | Tare, langes Drücken, USB-Wechsel im Standby, Stop, App-Neustart/CSV | Absolute Kraft bleibt erhalten, Standby bleibt aus, Sessiondaten wieder ladbar | Testexport ______ |
| 12 Background/Laufzeit | Sperrbildschirm, App-Background, Akkuentladung und Standby | Gemessene Aufzeichnungsgrenzen und Laufzeit; kein behaupteter Datenfluss nach Force-quit | Zeit-/Stromprotokoll ______ |
| 13 Laden | Akku zuletzt, gemessene Steckerpolung, Strom/Endspannung/Temperatur | Zellspezifikation eingehalten, Ladestrom/Temperatur dokumentiert | Messwerte ______ |

## Freigabeänderungen

Erst nach elektrischer Prüfung `HARDWARE_QUALIFIED=true` setzen und vorläufige Einschwing-/Akkuschwellen durch gemessene Werte ersetzen. Unzulässige ADC-Rampen verlangen eine Schaltungskorrektur; ein längeres Delay genügt nicht. Erst nach Last- und Kalibrierprüfung einen Gerätearbeitsbereich dokumentieren; gegebenenfalls dann eine absolute Überlastwarnung unabhängig vom Tare implementieren. Softwarewarnungen begrenzen mechanische Last nicht.

## Was bewusst weiter offen bleibt

Reale Handpassform, Passprobe/Fertigungsabnahme der Sondermetallteile nach den inzwischen erstellten Zeichnungen, unbelastete Sensorfangsicherung ohne Lastbypass, Passprobe der inzwischen konstruierten Elektronikaufnahme mit realen Modulmaßen, Lastfreigabe, Sensor-/Versorgungsqualifikation, Kalibrierung, Laufzeit und Fertiger-Engineering-Annahme. Diese Punkte benötigen reale Teile, Messwerte oder Lieferantenbestätigung.
