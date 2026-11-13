# Fingerworker Elektronik Review

11.10.2026. Der KiCad-Arbeitsstand und der JLC-Lieferstand bestehen die frischen elektrischen, geometrischen und Pin-/Padnetz-Prüfungen. Der Review zeigt jedoch eine fehlende HIGH-Pegelreserve der USB-Erkennung und unterschiedliche Kondensatorwerte zwischen Arbeits- und Lieferstand. Die Versorgung und Sensorfunktion bleiben am Muster zu qualifizieren. Eine elektrische Betriebsfreigabe folgt aus diesem Review nicht.

## Korrekturen nach dem Review — 11.10.2026

Die beiden P2-Befunde unten sind im Arbeitsstand behoben: USB-Erkennung über den internen nRF52840-VBUS-Detektor statt D6; sofortige Batterieprüfung bei Quellenwechsel. KiCad-Schaltpläne, PCB, Symbolbibliothek und native Pin-/Netzdaten sind bytegleich mit der eingefrorenen JLC-Quelle A-P1. C4/C7 sind jeweils 22 µF, GRM21BR61E226ME44L. Der native Vorher-/Nachher-Abgleich bestätigt unveränderte Positionen, Padnetze, Leiterbahnen, Vias und Kupferflächen. Freigegebene Portalersatzteile für C5/C6/C13 bleiben separat im Portal-BOM dokumentiert.

Frische ERC/DRC einschließlich Netzabgleich: 0 Fehler/Warnungen, 0 offene Verbindungen, 140 verbundene und 10 unbenutzte Pins korrekt. Firmware-Build/DFU-Paket erfolgreich: 116488 Byte Flash, 14668 Byte statisches RAM. C++-Tests mit Sanitizern und Swift-Pakettests bestehen. Das JLC-Paket blieb unverändert. Noch kein Flashen oder physischer USB-/Versorgungstest. Nachweis: `kicad/reports/usb-kicad-sync-2026-10-11.json`, `kicad/reports/verification-summary.json`, `../firmware/build/BUILD_STATUS.md`.

Die folgenden Befunde und Hashes dokumentieren den ursprünglichen Review vor diesen Korrekturen.

## Geprüfte Stände und Ergebnisse

| Prüfung | KiCad Arbeitsstand | JLC Lieferstand A P1 |
| --- | --- | --- |
| Native ERC | 0 Verstöße | 0 Verstöße |
| Native DRC einschließlich Schaltplanabgleich | 0 Verstöße | 0 Verstöße |
| Offene Verbindungen | 0 | 0 |
| Strenger Netzlistenabgleich | 140 verbundene und 10 unbenutzte Pins, 0 Abweichungen | gleich |
| PCB Padnetze | 0 Abweichungen | 0 Abweichungen |
| Kontur und Aufbau | 19,5 × 68,5 × 0,8 mm, 4 Kupferlagen | gleich |
| Geometrie | 48 Footprints, 464 Leiterbahnsegmente, 75 Vias | gleich |
| Portal BOM | keine Lieferantenzuordnung in diesem Stand | 26 Gruppen, 46 Bestückungsreferenzen; vollständig gegenüber PCB ohne J2/J3-Lötanschlüsse |

Die JLC-Quellen liegen unter `order/RevA-P1-JLC/source/`; die gewählten Teile in `upload/BOM_JLC_portal.csv`. Die PCB-Positionen und Padnetze beider Stände stimmen überein. C4/C7 unterscheiden sich im Wert. Portalrotationen und Lieferantenannahme wurden anhand der gespeicherten Unterlagen bewertet; kein neuer Portalzugriff und keine Bestellung erfolgten.

## USB Erkennung mit zu geringer Pegelreserve

**P2, bestätigtes Auslegungsproblem:** R1=100 kΩ und R2=100 kΩ teilen VBUS_USB auf XIAO D6/P1.11. Bei 1-%-Widerständen liegt der kleinste Teilerfaktor bei 0,495. Bei 4,4 V entstehen daher nur 2,178 V. Für ein garantiertes HIGH fordert der nRF52840 0,7 × VDD, bei 3,3 V also 2,31 V. Der aktuelle Teiler garantiert HIGH erst ab etwa 4,67 V, noch ohne Versorgungstoleranz und Eingangsstrom. Zulässige USB-Konstellationen können niedrigere Spannungen liefern. Das ist eine fehlende Garantie, kein Nachweis, dass jedes Muster bei 4,4 V LOW liest. [Nordic GPIO-Spezifikation und Herstellerbestätigung](https://devzone.nordicsemi.com/f/nordic-q-a/111050/nrf52840-vih-max-voltage-is-vdd), [USB-IF Drop/Droop, Tabelle 2](https://www.usb.org/sites/default/files/USB20_32_BC12_Drop_Droop_1_4_1.pdf).

Die Firmware liest D6 bei Start und Quellenwechsel. Ohne Akku kann eine falsche USB-Erkennung den Analogstart verhindern; bei USB/Akku-Wechsel kann sie die falsche Quelle melden. Für die nächste Änderung vorzugsweise die interne nRF52840-VBUS-Erkennung verwenden. Der vorhandene Seeed-Core enthält `nrf_power_usbregstatus_vbusdet_get(NRF_POWER)`, und der geprüfte XIAO-Schaltplan verbindet MCU-VBUS mit USB-VBUS. Diese Firmwareänderung benötigt keine neue Leiterbahn. Alternativ den Teiler nach maximaler VDD-, VBUS-, Widerstands- und Eingangsleckstromtoleranz neu auslegen. Ein-/Ausstecken und abgesenkte USB-Spannung am Muster prüfen. [Nordic POWER HAL](https://docs.nordicsemi.com/r/bundle/nrf5_sdk_v17.0.2/page/group_nrf_power_hal.html?contentId=zmjc2pVcngwON~qaNNfXbg).

## Kondensatorwerte im Arbeitsstand sind überholt

**P2, bestätigte Standabweichung:** Der Arbeitsstand unter `kicad/` enthält C4=10 µF und C7=4,7 µF, einschließlich `native_design.json`, Schaltplan und PCB. Der JLC-Lieferstand enthält beide mit 22 µF, Murata GRM21BR61E226ME44L. Die Erhöhung ist im bisherigen Komponentenreview begründet und im Portal-BOM enthalten. Damit ist die JLC-BOM an dieser Stelle konsistent; ein neuer Export aus dem Arbeitsstand würde jedoch alte Werte wieder einführen.

Arbeitsstand, Datenquelle und zugehörige Dokumentation vor dem nächsten Export auf den freigegebenen Lieferstand abgleichen. Die Schaltung wurde in diesem Review nicht geändert. Die bisherigen DC-Bias-Abschätzungen sind typische Kurven mit Engineering-Reserve, keine garantierten Kapazitätsuntergrenzen.

## Versorgung und ADC am Muster qualifizieren

**Bereits bekannter Abnahmepunkt:** Monotone ADC-Versorgungsrampen langsamer als 1 V je 50 µs sind weiterhin zu messen, bei USB-Kaltstart, Analog-Einschalten, Standby und Quellenwechsel. Weder die 10-/20-ms-Firmwarewartezeiten noch ein erfolgreicher Registerzugriff beweisen eine geeignete Rampe. Bei Verletzung muss die Versorgung korrigiert werden. `HARDWARE_QUALIFIED=false` sperrt derzeit gültige Kraftwerte. [ADS1220, Abschnitt 9.3.2](https://www.ti.com/lit/ds/symlink/ads1220.pdf).

VBOOST ist nominal 5,425 V; für 5-V-Regelung verbleiben nominal 425 mV. Ripple, Lastwechsel und Einschaltstrom mit C4/C7=22 µF können diese Reserve verändern. VBOOST und V5A gleichzeitig unter Sensorlast und BLE-Aktivität messen. Der LDO erlaubt 0,47–200 µF effektive Ausgangskapazität; C7=22 µF nominal ist daher kein pauschaler Stabilitätsverstoß. [TPS7A20, Betriebsbedingungen und Abschnitt 7.1](https://www.ti.com/lit/ds/symlink/tps7a20.pdf).

## Sensorweg und Layout

Die ratiometrische Referenz wird an J2 über getrennte Sense-Netze abgegriffen. Bei vier externen Sensoradern bleiben Kabelspannungsabfälle zur Brücke unkompensiert. Der 200-lbf-Sensor kann rechnerisch bis 264 mV einschließlich positivem Offset liefern: 5 V × (37,8 + 15) mV/V. Gain 8 bietet ausreichend Differenzbereich; der Sensor-Gleichtakt muss trotzdem gemessen werden. Das bestehende nominelle Fenster 1,256–3,744 V folgt aus PGA-Grenzen bei 5-V-AVDD und 264-mV-Differenz. [TE FX1901, Seite 2](https://www.te.com/commerce/DocumentDelivery/DDEController?Action=srchrtrv&DocFormat=pdf&DocLang=English&DocNm=FX19&DocType=Data+Sheet&PartCntxt=FX1901-0001-0200-L), [ADS1220 PGA](https://www.ti.com/lit/ds/symlink/ads1220.pdf).

Die native Geometrie bestätigt eine gefüllte, zusammenhängende In1.Cu-Massefläche ohne Signalleiterbahnen und Antennen-Kupfersperren auf allen vier Lagen. BOOST_SW liegt vollständig auf F.Cu, 0,4 mm breit, ohne Vias; die Summe seiner Segmente beträgt 5,77 mm. Die ADC-100-nF-Abblockung liegt 2,17 beziehungsweise 2,22 mm zwischen Versorgungs-Padmitten; die nächsten Massevias der Kondensatoren sind 0,73 beziehungsweise 0,87 mm entfernt. Das sind kompakte geometrische Wege, keine gemessene Rauschuntergrenze.

AIN_P/AIN_N und die Referenz wechseln teilweise die Lage. Für eine spätere Layoutrevision sollten deren Schleifen und Massebezug weiter verkürzt werden. Eine 0,396-mm-Längendifferenz der kurzen SIG-Leitungen ist bei dieser niederfrequenten Brückenmessung allein kein belastbarer Fehler. Messrauschen, Gleichtakteinkopplung und BLE-/Boost-Störung am Aufbau sind aussagekräftiger als Seeeds pauschale Differenzpaarwarnung.

## Ersatzteile und Fertigung

C5 YAGEO CC0603JRNPO9BN470 erhält 47 pF, C0G, 50 V, ±5 % und 0603. C6/C13 CC0603KRX7R7BB105 erhalten 1 µF, X7R, 16 V, ±10 % und 0603. Nominalwerte und Bauform passen; dies beweist keine identische DC-Bias-Kurve. C6 wird durch C4, C13 durch C7 und C12 ergänzt. Der 47-pF-Boost-Feedforward-Wert bleibt unter realer Last zu überprüfen. [YAGEO C5](https://www.yageogroup.com/download/specsheet/CC0603JRNPO9BN470), [YAGEO C6/C13](https://www.yageogroup.com/download/specsheet/CC0603KRX7R7BB105), [TPS61041 Feedforward](https://www.ti.com/lit/ds/symlink/tps61041.pdf).

**Vor Produktion beim Fertiger klären:** Via-Mittelpunkte liegen in U4-Pad 4 und U1-Pad 12; Filled-and-Capped ist für diesen Stand ausdrücklich erforderlich. Die unterseitigen XIAO-Batteriekontakte 19/20 müssen tatsächlich verlötet und elektrisch geprüft werden. Die Portalnotizen enthalten beide Anforderungen, eine Engineering-Annahme ist nicht dokumentiert. Tatsächliche Akkupolarität, Ladestrom und Temperatur bleiben Abnahmepunkte vor Akkuanschluss beziehungsweise Laden.

Der NC-Endschalter ist pinweise richtig angebunden: Unterbrechung oder Endlage führen bei aktiver V5A zu ENDSTOP_N=LOW. Bei ausgeschalteter V5A ist das Signal ungültig; der Firmware-Gate berücksichtigt diese Qualifikation. Ein Kurzschluss der NC-Schleife gegen GND wird durch diese Topologie nicht erkannt.

## Installation und Belege

Seeed ist als `kicad_seeed` global in Codex registriert. 19 echte MCP-Aufrufe wurden ausgeführt. Ein nativer PCB-Lesezugriff ergänzt den Textparser; dessen falsche Maße und unvollständige Segmentzählung wurden nicht als Reviewbelege verwendet. Die lokale ERC-Auswertung wurde für `sheets[].violations` korrigiert; DRC berücksichtigt zusätzlich offene Verbindungen und vorhandene Paritätsbefunde. Die Netzverfolgung wurde an die aktuelle Listenstruktur des Parsers angepasst; mehrere GND-Pins eines Bauteils bleiben erhalten. Die gezielten Parser- und Netzverfolgungsprüfungen bestehen.

Installationsdetails: [KICAD_MCP.md](../tools/KICAD_MCP.md). Rohaufrufe und native Befunde: `kicad/reports/seeed-review-2026-10-11/`. Der Arbeitsstand ist über `kicad/reports/verification-summary.json`, der Lieferstand über `order/parity-and-bom.json` in diesem Reviewordner per SHA-256 gebunden. Design-, Firmware-, Gerber-, BOM- und CPL-Dateien wurden im Review nicht geändert.

Als nächste Schritte zuerst die USB-Erkennung korrigieren und die CAD-Stände abgleichen, danach Lieferantenbestätigung und die bereits definierte Erstinbetriebnahme abarbeiten. Die Softwareprüfungen liefern keinen Ersatz für diese Messungen.
