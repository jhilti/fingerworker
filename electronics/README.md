# Fingerworker Elektronik - Revision A

20. September 2026. **Pin-genauer Schaltungsentwurf für einen Tischprototyp**, noch keine bestellfertige Platine. Der Entwurf enthält Versorgung, Filter, Referenz, ADC, BLE-Modul, Bedienung und Endschalter. Die tragende Mechanik bleibt unverändert. Den neueren Routing- und Bauraumstand beschreibt der nächste Absatz.

## Dateien

**Stand vom 21.09.2026:** Das native KiCad-10-Projekt unter `kicad/` ist vollständig geroutet: **19,5 × 68,5 × 0,8 mm, vier Kupferlagen, 48 Footprints**. ERC, DRC und Schaltplan–PCB-Abgleich bestehen mit **0 Fehlern/Warnungen und 0 offenen Verbindungen**. Die Sense-Leitungen werden über getrennte Netze bis zu den Sensor-Lötpads geführt. Der aktuelle EDA- und Freigabestatus steht in `kicad/README.md`. Die FeatureScript-Bauraumstudie ist in Onshape übernommen und bei 0/15/30 mm Hub mit Handmodell geprüft: keine Volumenüberschneidung in den 43 ausgewählten Körperpaaren. Der bisherige 0,1-mm-Mindestspalt ist auf nominal 0,6 mm vergrößert; Drucktoleranz und Verformung bleiben zu prüfen.

- `../output/pdf/Fingerworker_Elektronik_RevA.pdf`: historischer fünfseitiger Netzlabel-Schaltplan vom ursprünglichen Schaltungsentwurf; aktuelle Net-Ties und Layout stehen im nativen KiCad-Projekt. Gleiche Netznamen bedeuten eine elektrische Verbindung, auch zwischen Seiten.
- `design.json`: vollständige Bauteil- und Pin-/Netzliste als editierbare Datenquelle des Exports.
- `bom.csv`: Stückliste mit Referenzen, Herstellerteilen oder definierten Passiv-Spezifikationen.
- `connections.csv`, `connectivity.xml`: vollständige elektrische Verbindungen; XML ist ein eigenes Austauschformat, kein behaupteter KiCad-Import.
- `validation.json`: reproduzierbare Rechen- und Konsistenzprüfungen.
- `build_design.py`: Autorquelle; erzeugt die genannten Dateien aus einer gemeinsamen Bauteilliste. Python mit ReportLab genügt.
- `vendor/`: die bei der Recherche heruntergeladenen Herstellerunterlagen; TE liegt weiter unter `../vendor/te_fx1901/`.

Der PDF-Plan ist kein Screenshot einer CAD-Anwendung. Er wurde aus den expliziten Pin-/Netzdaten erzeugt. Für diesen früheren PDF-Export wurden noch keine EDA-Prüfungen durchgeführt. Inzwischen liegen ERC und eine DRC der Platzierung im nativen KiCad-Projekt vor; SPICE-Simulation und Hardwaremessungen stehen weiterhin aus.

## Festgelegte Hauptbauteile

| Ref. | Auswahl | Zweck |
|---|---|---|
| U1 | Seeed Studio XIAO nRF52840, 102010448, ohne Sense/Plus und ohne Stiftleisten | BLE, USB, SPI, Ladefunktion |
| U2 | TI TPS61041DBVR | 3,3 V auf nominal 5,425 V anheben |
| U3 | TI TPS7A2050PDBVR | Geregelte 5 V für Brücke/ADC; Abschaltung mit Ausgangsentladung |
| U4 | TI ADS1220IPWR, **TSSOP-16** | Differenzieller ADC; Pinbelegung gilt ausdrücklich für PW, nicht QFN |
| L1 | Coilcraft XFL3012-103MEC, 10 µH | Flache, geschirmte Boost-Drossel |
| D1 | onsemi MBR0520LT1G | Boost-Schottkydiode, Kathode an VBOOST |
| Q1 | Nexperia 2N7002,215 | Endschalter von 5-V-Kontaktkreis auf 3,3-V-Logik umsetzen |
| SW2 | Panasonic EVQPUC02K, seitlicher Taster, 4,7 × 4,5 × 1,65 mm | Wecken, Tarieren, Standby |
| J1 | JST S2B-PH-SM4-TB(LF)(SN) | Akku steckbar; Originalkabel verwenden |
| BT1 | Adafruit 1570, geschützter 100-mAh-LiPo | Größenreferenz und Prototypakku |
| H1 / SW1 | Vorhandene TE FX1901-0001-0200-L / Omron SS-01GL2 | Sensorik bleibt erhalten |

Passive sind in der BOM bewusst über Wert, Toleranz, Bauform, Spannungsfestigkeit und gegebenenfalls effektive Kapazität spezifiziert. Das sind vollständige elektrische Anforderungen, aber noch keine durchgängig lieferantenbezogene Bestellliste. Exakte MLCC-Teilenummern und DC-Bias-Kurven werden beim Footprint-/Beschaffungsabgleich fixiert. Bestand und Preise sind nicht zugesichert; TI zeigte für den TPS7A2050PDBVR beim Abruf keinen Direktbestand. Distributoren oder ein elektrisch/ mechanisch geprüfter Ersatz müssen vor Bestellung geprüft werden.

## USB, Akku und Abschaltung

Der geprüfte [Seeed-Schaltplan v1.2](https://files.seeedstudio.com/wiki/XIAO-BLE/Res/260828_XIAO_nRF52840.pdf) enthält bereits eine USB/Akku-Auswahl vor dem 3,3-V-Regler. Der zusätzliche Messzweig wird daher aus **V3V3**, nicht direkt aus VBAT gespeist. Bei USB-Versorgung bleibt die externe Messlast vom Batterie-Ladeausgang getrennt. Das ist ein Schaltungsbefund, noch kein Ladetest am gelieferten Modul.

P0.13 bleibt hochohmiger Eingang ohne Pull-up/-down für nominal 50 mA Ladestrom. Nicht den widersprüchlichen HIGH-Beispielcode der Wiki übernehmen. P0.14 früh als LOW-Ausgang setzen; der interne Batterieteiler liegt an P0.31. P0.14 nicht HIGH treiben. Die konkrete Boardrevision, Ladehöhe und Abschaltung am tatsächlichen Modul kontrollieren. Das Modul verwendet am TS-Eingang einen Festwiderstand und erfasst keine Zelltemperatur. Der Akku ist laut verlinktem Zellblatt im Bereich 0-45 °C zu laden.

U2 allein isoliert seine Versorgung bei EN=LOW nicht: Ein Gleichstrompfad über Drossel und Diode bleibt bestehen. **U3** übernimmt die Abschaltung der Brücke und entlädt V5A. Der BLE-Controller bleibt für den Seitentaster im sparsamen Standby versorgt. Zum vollständigen Trennen wird der Akku abgesteckt; ein zusätzlicher harter Geräteschalter ist in Rev A nicht vorgesehen. USB kann das Modul unabhängig davon speisen.

## Signalqualität und Messbereich

Der TE-Datenblattwert für die 200-lbf-Variante führt bei 5 V auf maximal 264 mV einschließlich des positiven Offset-Grenzwerts. Gain 8 ergibt einen ADC-Codebereich von ±625 mV. Wegen des PGA-Ausgangshubs sind bei genau mittigem Gleichtakt praktisch maximal ±575 mV zulässig. Für das erwartete 264-mV-Signal liegt das zulässige Gleichtaktfenster bei 1,256-3,744 V. Ein symmetrischer Brückenausgang um 2,5 V wäre geeignet; **TE garantiert diesen Gleichtaktwert im verwendeten Familienblatt nicht ausdrücklich**, deshalb beide Ausgänge am realen Sensor messen.

R7/R8 bilden mit C8-C10 und dem Sensor-Ausgangswiderstand einen Vorfilter mit ungefähr 73-90 Hz Grenzfrequenz. Das unterdrückt Störungen, ist aber kein vollständiger steiler Antialiasfilter. Die spätere Anzeige soll zusätzlich digital gefiltert werden. Die externe Referenz wird am gleichen PCB-Anschlusspunkt wie die Brückenerregung abgegriffen. Vier Sensoradern erlauben keine separate Fernmessung der Erregung direkt an der Brücke; kurze Leitungen und Kalibrierung der kompletten Montage bleiben nötig.

Endschalter: **NC an J3.1, COM an GND; NO offen isolieren.** R17 liefert nominal 1,064 mA bei geschlossener NC-Schleife. Q1 setzt auf 3,3 V um. Das umbenannte Signal `ENDSTOP_N` ist LOW bei Endlage **oder unterbrochener Leitung**, HIGH im normalen unbetätigten Zustand. Bei V5A aus/Hochlauf ist der Pegel ungültig. Kurzschluss gegen GND wird nicht erkannt. Kraftauswertung am Hartanschlag sperren, weil dort ein Teil der Handkraft den Sensor umgeht. Vollständige Wahrheitstabelle und Firmware-Prüfvorgaben: [FIRMWARE_CONTRACT.md](FIRMWARE_CONTRACT.md).

## Firmware-Vertrag

Die PDF-Pins bezeichnen physische XIAO-Pads/Portnamen. Nicht ungeprüft numerische Arduino-Pinindizes einsetzen; die Seeed-Cores unterscheiden sich.

1. Beim Start beide EN-Ausgänge LOW, CS HIGH, SPI Mode 1 / 1 MHz / MSB first; P0.13 hochohmig ohne Pull, P0.14 LOW. LEDs und nicht verwendeten Flash-Zugriff für Standby berücksichtigen.
2. BOOST_EN HIGH, mindestens 10 ms als vorläufige Wartezeit; ANALOG_EN HIGH. Nochmals Versorgung und Filter einschwingen lassen (20 ms Startwert). Spannungsanstiege messen: Die aktuelle ADS1220-Dokumentation fordert monotone Rampen langsamer als 1 V je 50 µs. Falls der Aufbau dies nicht einhält, Versorgung mit kontrollierter Anstiegszeit ergänzen; bloßes Warten nach einem zu schnellen Anstieg ersetzt diese Bedingung nicht.
3. ADS1220 RESET; Register `06 84 40 00` schreiben und zurücklesen; START/SYNC. Das bedeutet AIN0-AIN1, Gain 8, 330 SPS normal/continuous, REF0 extern, IDAC und Burnout aus. Ersten gültigen DRDY abwarten; Einschwingmessungen verwerfen. Bei Register- oder Timeoutfehler keine scheinbar gültigen Kraftwerte senden.
4. Rohwert als vorzeichenbehafteten 24-Bit-Wert erweitern. Newton aus gespeicherter Mehrpunktkalibrierung der montierten Mechanik bestimmen; Nullpunkt inklusive Federvorspannung. Sensor-Nennkraft ist keine zulässige Belastungsangabe für die gedruckte Mechanik.
5. Datensätze: Sequenznummer, Gerätetimestamp, Rohwert, Newton, entprellte Endlage, Batteriespannung, Statusbits. BLE-Paketformat und Service-UUIDs werden mit der Firmware festgelegt. 25-Hz-Anzeige ist unabhängig von der Erfassung mit 330 SPS.
6. Standby: ADC POWERDOWN, CS HIGH, ANALOG_EN LOW, BOOST_EN LOW. Taster loslassen abwarten, LOW-Wakeup konfigurieren, Funk und unnötige Peripherie ausschalten. Bei Versorgung unter dem in der Erprobung festgelegten Batterieschwellenwert Messung beenden; nicht auf die Schutzschaltung als normale Abschaltung warten.

Stand 11.10.2026: [Firmware](../firmware/README.md) für den XIAO nRF52840 und [iPhone-App](../ios/README.md) implementiert und kompiliert. BLE v3 überträgt den geräteseitigen Zähler und den kumulativen Peak mit Messlaufkennung. Benutzer-Standby bleibt bei USB-Wechsel erhalten; ein gesonderter Bench-Build startet mit ausgeschaltetem Analogzweig. Hardwaretest, Flashen, Versorgungsqualifikation und Kalibrierung stehen noch aus.

## Verbrauch und Bauraum

Arbeitsbudget: **10-20 mA am Akku** einschließlich MCU/BLE und Wandlungsverlusten. Mit angesetzten 80 mAh nutzbarer Kapazität entspricht dies **etwa 4-8 Stunden aktiv**. Das ist eine Planungsrechnung, keine Messung oder zugesicherte Laufzeit. Die Brücke allein benötigt bei 5 V rechnerisch 1,39-2,08 mA. Standby-Ziel für das ganze Gerät: unter 100 µA. Für das Laden mit 50 mA sind 2 Stunden nur die ideale CC-Untergrenze für 100 mAh; die CV-Phase verlängert die Zeit.

Das PCB misst jetzt 19,5 × 68,5 × 0,8 mm und ist auf vier Kupferlagen vollständig geroutet. Boost, ADC und Antenne liegen in getrennten Bereichen; In1.Cu bildet die durchgehende Massefläche. Lokale Hüllkörper verwenden die tatsächliche Footprint-Platzierung, siehe `../ELECTRONICS_PACKAGING.md`.

**Aktualisierte Bauraumprobe:** Der 5,5-mm-JST einschließlich Lötzugabe, Gegensteckerreserve und Seitentaster ist nun in der lokalen Hüllkörperstudie berücksichtigt. Das Gehäusebudget beträgt 22,5 × 110 × 8,9 mm. Neue, quellengebundene Onshape-Prüfungen bei 0/15/30 mm liegen in `../review/onshape-full-review.json` vor. Alle sieben Elektronik-Prüfpaare sind CLEAR; der Mindestspalt zur Mechanik beträgt nominell 0,6 mm. Befestigung, Kabelbiegeradien und tatsächliche Modulhöhe bleiben offen.

## Vor Bestellung abzuarbeiten

- J1: Pin 1 ist im Entwurf Plus. Gegen den tatsächlichen Akku-Kabelbaum messen. Die physischen XIAO-/JST-/SW2-Pads sind zugeordnet; die Polarität des gelieferten Akkusteckers muss noch bestätigt werden.
- Brücken-Gleichtakt, Filtereinschwingen, LDO-Reserve und Schaltregler-Ripple prüfen. C5=47 pF ist ein begründeter Startwert, kein am Muster optimierter Wert.
- Echte Modulhöhe, Antennenbereich ohne Kupfer/Leitungen, Steckerzugang, Kabelradien und Akku-Montagespiel im Onshape-Modell ersetzen/prüfen.
- Native EDA-/Routingprüfungen und die Onshape-Nennmaßprüfung bei 0/15/30 mm sind abgeschlossen. Den vergrößerten Gehäusespalt und den Einbau mit echten Bauhöhen, Drucktoleranzen und Verformung prüfen.
- Elektronik auf dem Tisch betreiben, dann mit der Mechanik kalibrieren; Lade-/Temperaturtest und Verhalten beim USB-Wechsel. Erst anschließend druckbare Aufnahme anpassen.

## Herstellerquellen

- [Seeed Modul und Dokumentation](https://wiki.seeedstudio.com/XIAO_BLE/), [geprüfter Schaltplan](https://files.seeedstudio.com/wiki/XIAO-BLE/Res/260828_XIAO_nRF52840.pdf)
- [TI ADS1220](https://www.ti.com/lit/ds/symlink/ads1220.pdf), [TPS61041](https://www.ti.com/lit/ds/symlink/tps61041.pdf), [TPS7A20](https://www.ti.com/lit/ds/symlink/tps7a20.pdf)
- [TE FX1901](https://www.te.com/commerce/DocumentDelivery/DDEController?Action=srchrtrv&DocFormat=pdf&DocLang=English&DocNm=FX19&DocType=Data+Sheet&PartCntxt=FX1901-0001-0200-L), lokale Kopie unter `vendor/te_fx1901` im Projektstamm
- [Omron SS](https://omronfs.omron.com/en_US/ecb/products/pdf/en-ss.pdf), [Panasonic EVQPUC02K](https://industry.panasonic.com/global/en/products/control/switch/light-touch/number/evqpuc02k)
- [Nexperia 2N7002](https://assets.nexperia.com/documents/data-sheet/2N7002.pdf), [onsemi MBR0520](https://www.onsemi.com/pdf/datasheet/mbr0520lt1-d.pdf), [Coilcraft XFL3012](https://www.coilcraft.com/getmedia/f76a3c9b-4fff-4397-8028-ef8e043eb200/xfl3012.pdf)
- [JST PH](https://www.jst-mfg.com/product/pdf/eng/ePH.pdf), [Adafruit Akku 1570](https://www.adafruit.com/product/1570), [verlinktes PKCELL-Zellblatt](https://cdn-shop.adafruit.com/product-files/1570/1570datasheet.pdf)
