# Fingerworker Rev A — verbindliche Schnittstelle nach Vollreview

Stand 21.09.2026. Dies ist die Implementierungs- und Prüfvorgabe. Firmware und passende iPhone-App sind seit 11.10.2026 implementiert und kompiliert: [Firmware/Build/Kalibrierung](../firmware/README.md), [BLE-Protokoll v3](../ios/BLE_PROTOCOL.md). Noch kein Hardwaretest oder Flashen am Muster. Alte NO-/END_ACTIVE-Beschreibungen sind überholt.

## Endlage und unterbrochene Leitung

Omron SS-01GL2: **NC → J3.1, COM → J3.2/GND; NO isolieren**. PCB-Topologie unverändert. Das GPIO-Netz heißt jetzt **ENDSTOP_N** (XIAO D5 / P0.05). R17 stellt etwa 1,064 mA Kontaktstrom bei geschlossener NC-Schleife bereit.

| Zustand bei stabiler V5A | NC-Schleife | ENDSTOP_N | Interpretation |
|---|---|---|---|
| Vor dem Endanschlag, Leitung intakt | geschlossen | HIGH | Endlage nicht aktiv |
| Schalter betätigt | offen | LOW | Endlage oder Leitungsunterbrechung |
| J3-Kabel unterbrochen | offen | LOW | Endlage oder Leitungsunterbrechung |
| V5A aus / Hochlauf / unbekannt | beliebig | nicht verwenden | Messung ungültig |

Die Schaltung unterscheidet Kabelbruch und Endlage nicht. Ein Kurzschluss der Kontaktleitung gegen Masse wird nicht erkannt. Sie ist kein zertifizierter Sicherheitskanal. Die reale Verdrahtung und beide Schaltzustände vor Inbetriebnahme prüfen.

Bei LOW sofort `ENDSTOP_OR_OPEN` setzen und Kraftwerte als ungültig für Leistungs-/Peak-Auswertung kennzeichnen; Freigabe erst nach mindestens 10 ms stabil HIGH und erfüllten übrigen Messbedingungen. Entprellzeit am realen Schalter prüfen. Rohdaten weiter für Diagnose übertragen, nicht als gültige Newton-Werte darstellen.

## Warum der Endanschlag Messwerte ungültig macht

Im freien Hub läuft die Kraft über Federn/Joch/Sensor; Führungsreibung bleibt ein Fehleranteil. Wenn der Schlitten auf den M4-Hartanschlag trifft, entsteht zusätzlich der Weg **Schlitten → Anschlag → Rahmen**. Diese zusätzliche Handkraft misst der Sensor nicht vollständig. Der Klickpunkt soll deshalb vor dem Hartanschlag liegen und die nachfolgende Messung sperren. Den Nocken im Muster so einstellen, dass er einschließlich Toleranzen und Verformung vor beiden Anschlägen schaltet. Der nominelle 1-mm-Vorlauf ist noch kein bestätigtes Toleranzbudget.

Isometrie verwendet die beiden Stahlhülsen und erreicht den normalen Endschalter nicht. Messung darf in diesem Modus nicht auf einen Endlagenimpuls warten; eine LOW-Meldung bleibt trotzdem ein Fehlerzustand.

## Messzustand, Kalibrierung und BLE

USB-Versorgung wird seit 11.10.2026 über `nrf_power_usbregstatus_vbusdet_get(NRF_POWER)` erkannt, unabhängig von USB-Enumeration. Der Rev-A-Teiler an D6 bleibt als Eingang bestehen; sein HIGH-Pegel ist über den USB-Spannungsbereich nicht garantiert. Bei jedem Quellenwechsel werden die Analogschienen abgeschaltet und die Batteriespannung frisch geprüft, bevor sie erneut eingeschaltet werden. USB erlaubt Betrieb ohne Akku. Ohne USB gelten 3400 mV Abschaltschwelle und 3550 mV Erholungsschwelle; Startup und Quellenwechsel beginnen mit einer frischen Bewertung bei 3400 mV. Die Schwellen sind am Muster zu prüfen.

- `measurement_valid = rails_valid && adc_ready && calibration_valid && !ENDSTOP_OR_OPEN && !adc_timeout && !adc_saturated`. Versorgungshochlauf vorher hardwareseitig qualifizieren; ein Zeitdelay beweist keine zulässige Rampe.
- Startup: P0.13 hochohmig ohne Pull (50-mA-Lademodus), P0.14 LOW (Batterieteiler), BOOST_EN HIGH, danach ANALOG_EN HIGH; RESET/WREG/RREG/START für ADS1220. Register `06 84 40 00`, SPI Mode 1, Startwert 1 MHz, 330 SPS. Rücklese- und DRDY-Timeoutfehler sperren Daten.
- RAW-Signal und kalibrierte absolute Kraft erhalten. Benutzer-Tare nur als separaten Offset auf den Anzeigewert anwenden; Überlastschwelle niemals mittarieren. Zulässige Gerätebelastung ist noch nicht festgelegt.
- Im montierten Gerät mehrere Lastpunkte auf- und absteigend sowie mittigen/einseitigen Zug kalibrieren. Hysterese, Führungshaftreibung, Vorspannungswechsel und Hülsenmodus getrennt bewerten. Sensor-Nennkennwert allein genügt nicht.
- BLE-Datensatz: Sequenznummer, monotoner Gerätezeitstempel, signed 24-bit Rohwert korrekt auf 32 bit erweitert, kalibrierte Kraft, Benutzer-Tare, ENDSTOP_OR_OPEN, Batteriespannung, Betriebsmodus und Statusbits. Paketverlust erkennbar lassen; keine alten Werte als neue Messung wiederholen.
- Status mindestens: RAILS_UNQUALIFIED, ADC_NOT_READY, ADC_TIMEOUT, ADC_SATURATED, CALIBRATION_MISSING, ENDSTOP_OR_OPEN, BATTERY_LOW. Anzeige nur bei valid=true; bei Fehlern Diagnosegrund zeigen.
- Reale Versorgungsschwellen, Einschwingzeit, zulässige Kraft und BLE-UUIDs erst mit validierter Hardware festlegen. Der bisherige 25-Hz-Anzeigewert ist von der 330-SPS-Erfassung zu trennen.

## Peak und Standby seit 11.10.2026

Der Firmware-Peak entsteht aus jedem frisch eingelesenen gültigen ADC-Sample vor der 25-Hz-Publikation. BLE v3 überträgt Peak, separates Peak-valid und bestätigte Epoche. Ein später ungültiger aktueller Kraftwert löscht einen vorher gültigen Peak nicht. App-Aufnahmestart setzt ausschliesslich den Peak per Epochentoken zurück; derselbe Token darf den laufenden Peak bei Wiederholung nicht löschen. Nach Bootwechsel startet ein neuer Peak-Lauf. Vor der Bestätigung liegende Werte sind nicht Teil des neuen geräteseitigen Messlaufs.

Benutzer-Standby bleibt bei USB-Wechsel erhalten. Unterspannung bleibt ein eigener Abschaltgrund und darf nur bei erfüllter Batterieerholung und fehlendem Benutzer-Standby automatisch aufgehoben werden. `build.sh --bench` erzeugt einen gesonderten Build, der zunächst im Benutzer-Standby bleibt. Hardwarequalifikation wird dadurch nicht erteilt.

## Abnahmetests

1. V5A aus, Einschalten, Ausschalten und USB-Wechsel: nie fälschlich gültige Kraft/Endlagenwerte.
2. Betätigung und Abziehen jeweils einer J3-Ader: LOW und Messsperre; Rückkehr erst nach stabiler Schleife.
3. Messungen vor dem Klick und am Hartanschlag: Peak-Auswertung endet vor Lastbypass; Rohdaten sind weiter diagnostizierbar.
4. ADC-Timeout, falsche Registerrücklesung und ungültige Kalibrierung: eindeutiger Fehler statt plausibler Nullen.
5. Tare unter Vorspannung darf absolute Rohkraft und spätere absolute Lastgrenze nicht verändern.
6. BLE-Abbruch, Wiederverbindung und Paketverlust: keine doppelten/alten Stichproben ohne erkennbare Zeit-/Sequenzinformation.

7. Kurzer gültiger Kraftimpuls zwischen zwei BLE-Publikationen: Geräte-Peak enthält ihn. BLE-Paketverlust/Wiederverbindung und idempotenter Peak-Reset dürfen ihn nicht löschen; Fault-/Endlagensamples dürfen ihn nicht erhöhen.
8. Benutzer-Standby mit USB-Ein/Aus und Batterieerholung: Analog bleibt aus. Bench-Kaltstart bleibt aus; explizites Wake startet nur bei ausreichender Quelle.
9. App-Sitzung aufnehmen, stoppen, App neu starten und CSV exportieren; gespeicherte Peak-Epoche, Boot-ID, Rohwerte und Zähler müssen erhalten bleiben. Sperrbildschirm/Background-BLE am echten iPhone prüfen.
