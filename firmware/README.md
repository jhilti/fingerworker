# Fingerworker Rev A Firmware

Für **Seeed Studio XIAO nRF52840 ohne Sense/Plus**, ADS1220 und die vorhandene Rev-A-NC-Endschalterschaltung. Arduino-Core **Seeeduino:nrf52 1.1.13**, Bluefruit; nicht den mbed-Core auswählen.

Implementiert: SPI Mode 1 / 1 MHz, ADS1220-Reset/Registerrücklesung (`06 84 40 00`, 330 SPS), signierte Rohwerte, Kalibrierung mit 2–8 Punkten je Betriebsmodus im internen Flash, separater Tare-Offset, Statusprüfung, 25-Hz-BLE-v3-Telemetrie mit kumulativem Geräte-Peak, geräteseitiger entprellter Gesamtzähler, Akkuspannung, Abschaltung des Analogzweigs und USB-Seriendiagnose.

**Noch nicht auf Hardware getestet oder geflasht.** Kein XIAO wurde am USB-Port gefunden. Der Auslieferungsbuild enthält `HARDWARE_QUALIFIED = false`: echte ADC-Rohwerte und Fehlerstatus werden gesendet; gültige Newton-Werte und Zählung bleiben bis zur Versorgungsqualifikation gesperrt. Kalibrierwerte werden nicht erfunden. Die Build-Dateien sind Bench-Prototypen, keine Hardwarefreigabe.

## Pinbelegung

| XIAO | Signal |
| --- | --- |
| D0 / P0.02 | BOOST_EN |
| D1 / P0.03 | ANALOG_EN |
| D2 / P0.28 | ADC_CS |
| D3 / P0.29 | ADC_DRDY_N |
| D4 / P0.04 | BUTTON_N |
| D5 / P0.05 | ENDSTOP_N; NC geschlossen=HIGH, Endlage/Kabel offen=LOW |
| D6 / P1.11 | USB_PRESENT-Teiler, nur Eingang; Firmware verwendet den internen nRF52840-VBUS-Detektor |
| D8/D9/D10 | SPI SCK/MISO/MOSI |
| PIN_CHARGING_CURRENT / P0.13 | Eingang ohne Pull; 50-mA-Lademodus |
| VBAT_ENABLE / P0.14 | LOW; niemals HIGH treiben |
| PIN_VBAT / P0.31 | interner Batterieteiler |

**Erforderlicher Core-Patch:** Seeed 1.1.13 setzt P0.14 in `initVariant()` vor `setup()` HIGH. `tools/patch_core.py` ändert ausschließlich die lokale Core-Installation unter `/tmp/fingerworker-arduino` auf LOW vor OUTPUT. Ein Build ohne diesen Patch entspricht nicht dem Schaltungsvertrag. Bootloaderverhalten am gelieferten Modul bleibt separat zu prüfen.

## Bauen

`tools/setup.sh` lädt Arduino CLI, den gepinnten Seeed-Core und für Apple Silicon die offizielle Arm-GNU-Toolchain 13.2.Rel1 in temporäre Verzeichnisse. Das ebenfalls Intel-only gelieferte Arduino-ctags wird aus offiziellem Quellcode nativ gebaut; sein internes `__unused__`-Makro wird zur SDK-Kompatibilität umbenannt. Anschließend wird der Core-Patch angewendet. Der DFU-Packager `adafruit-nrfutil 0.5.3.post16` wird in einem temporären Python-Environment installiert. Keine systemweite Installation und keine Rosetta-Installation.

Vom Projektstamm:

```sh
bash firmware/tools/setup.sh
bash firmware/tools/build.sh
bash firmware/tools/build.sh --bench
bash firmware/tools/test.sh
```

Build-Ausgabe: `firmware/build/`; separater Erstinbetriebnahme-Build: `firmware/build-bench/`. Der Bench-Build hält den Analogzweig beim Start und bei USB-Wechsel ausgeschaltet, bis `wake` oder ein langer Tasterdruck den Benutzer-Standby aufhebt. `HARDWARE_QUALIFIED` bleibt in beiden Builds FALSE. Ein `.hex` enthält das Anwendungsimage; Board/Core/SoftDevice müssen zum vorhandenen Seeed-Bootloader passen. **Nicht per Drag-and-drop eine HEX-Datei als UF2 behandeln.** USB-Upload über Arduino CLI verwenden.

## Aufspielen

XIAO per USB-Datenkabel verbinden, dann:

```sh
/tmp/fingerworker-arduino/bin/arduino-cli board list --config-file firmware/arduino-cli.yaml
/tmp/fingerworker-arduino/bin/arduino-cli upload --fqbn Seeeduino:nrf52:xiaonRF52840 --port /dev/cu.DEIN_XIAO --input-dir firmware/build-bench --config-file firmware/arduino-cli.yaml --upload-property tools.nrfutil.cmd.macosx=/tmp/fingerworker-arduino/venv/bin/adafruit-nrfutil
```

Der gezeigte Upload verwendet ausdrücklich den Bench-Build für die erste Inbetriebnahme. Nach Qualifikation und Neubau kann `firmware/build` gewählt werden. Den Port durch den tatsächlich erkannten XIAO-Port ersetzen. Bei Bedarf den Board-Reset zweimal drücken, um den Seeed-Bootloader aufzurufen. Ohne angeschlossenes Board ist kein Flash-/Funktionstest möglich. Vor Aufspielen die Erstinbetriebnahme in `../electronics/procurement/FIRST_POWER.md` durchgehen.

## Kalibrieren und qualifizieren

1. Aufbau zuerst elektrisch auf dem Tisch prüfen: gelieferte Boardrevision, SPI/DRDY, 5-V-Rampen gemäß ADS1220-Datenblatt, Referenz/Gleichtakt, Einschwingzeit, USB-Wechsel, Batterieteiler und Akkuabschaltung. `Config.h` enthält ausdrücklich vorläufige Zeit-/Akkuschwellen. Sie sind keine gemessenen Werte. Erst nach diesen Prüfungen die Werte aktualisieren und `HARDWARE_QUALIFIED` setzen, neu bauen/flashen. Der PCB hat keine separate Analog-Rail-Überwachung; ADC-Kommunikation allein beweist keine gültige Versorgung.
2. USB-Serial mit 115200 Baud öffnen. `raw` zeigt ADC-Rohwert, Status und Gerätezähler. Für mehrere bekannte Kräfte am vollständig montierten Gerät Rohwerte aufnehmen, Be-/Entlastung und einseitigen Zug prüfen. Kraftpfad vor dem Hartanschlag verwenden; maximal zulässige Gerätebelastung ist weiter nicht festgelegt.
3. `mode 0` (normal) oder `mode 1` (isometrisch) wählen. Beide benötigen eigene Kalibrierung. Die zwei Speicherplätze erkennen Federartikel, Vorspannung oder Gegenlager nicht automatisch. Nach Änderung dieser mechanischen Konfiguration die Kalibrierung neu prüfen und bei Bedarf ersetzen; Konfiguration im Prüfprotokoll dokumentieren. `cal clear` leert nur die neuen, noch ungespeicherten Punkte. Mit `cal RAW MILLINEWTON` 2–8 reale Punkte hinzufügen: RAW streng aufsteigend; Kraft monoton steigend oder fallend je Sensorpolarität. 1 N = 1000 mN. Keine Beispielwerte als echte Kalibrierung übernehmen.
4. `standby` schaltet den Analogzweig ab. `cal save` prüft die Punkte und schreibt sie mit Version/Checksumme in den internen Flash. Bei unvollständigem Flash-Inhalt nach Stromausfall bleiben Messungen ungültig. `wake` startet den ADC neu und verwirft die ersten acht Messwerte. Es wird nur innerhalb des kalibrierten Rohwertbereichs interpoliert, nicht extrapoliert.
5. `tare` oder kurzer Seitentasterdruck setzt bei gültiger Messung nur den Anzeigeoffset. Absolute Kraft und ADC-Rohwerte bleiben erhalten. Ein langer Druck (1,5 s) schaltet Analog-Standby/Wecken um; BLE und USB bleiben an. Benutzer-Standby bleibt bei Quellenwechsel und Batterieerholung bestehen; eine reine Unterspannungsabschaltung startet erst bei erholter Batterie wieder. Dies ist noch kein optimierter Tiefschlafmodus.

Konfiguration/Kalibrierung erfolgen bewusst am USB-Port. BLE-Telemetrie ist lesbar/notify; eine getrennte Write-Characteristic setzt ausschliesslich den Geräte-Peak für einen neuen App-Messlauf zurück. Keine unbestätigten Kalibrier-/Power-Kommandos aus der App.

## Mit der App verbinden

Auf einem echten iPhone App starten, Bluetooth erlauben und **Find device** → **Fingerworker** wählen. Der Simulator verwendet automatisch Simulation; für echte BLE-Hardware das iPhone verwenden. Telemetrie-UUIDs, 43-Byte-v3-Paket und Statusbits stehen in `../ios/BLE_PROTOCOL.md`.

**Repetitions · device** übernimmt den Gesamtzähler des Geräts. Paketverlust oder BLE-Abbruch verliert keine im laufenden Gerät gezählten Wiederholungen. Nach einem Geräte-Neustart zeigt die App einen neuen Zählerlauf. Reset/Record in der App setzt deren Anzeige zurück, nicht den Gerätezähler. CSV enthält beide Zählerstände und die Boot-Kennung.

Kabelbruch und Schalterbetätigung sind weiterhin elektrisch identisch. Der Firmwarezähler kann einen Kabelbruch als eine Wiederholung zählen; dauernd LOW zählt nur einmal. Im Isometrie-Modus wird nicht gezählt. Versorgung und ADC müssen qualifiziert/bereit sein; Kalibrierung ist für reine Schalterzählung nicht notwendig.

## Geräte-Peak

Jeder frisch eingelesene ADC-Wert aktualisiert bei Status ZERO den maximalen Anzeigewert (absolute Kraft minus damaliger Tare). Die 25-Hz-Telemetrie sendet diesen kumulativen Peak zusätzlich zum letzten Sample; Funkverlust löscht ihn nicht. Die App startet mit einem nichtnull Epochentoken einen eigenen Peak-Lauf und akzeptiert nur dessen bestätigte Werte. Wiederholung desselben Tokens ist idempotent. Ein Geräte-Neustart verliert den alten Peak; ein späterer Fault behält einen zuvor gültig erfassten historischen Peak. Peak-Beginn liegt bei geräteseitiger Bestätigung, nicht rückwirkend beim App-Tap. Loop-Polling erfasst keine Werte während blockierender Firmwarearbeit; der Serial-Parser bearbeitet maximal 16 Zeichen pro Schleife.

## Verifikation und offene Hardwaretests

Hosttests prüfen Vorzeichenerweiterung, Entprellung, LOW bei Start, gehaltenen Schalter, Fault-/Isometrie-Sperre, Timer-/Zählerüberlauf, Endlagen-Messsperre und Kalibrierung. Von echtem C++-Encoder erzeugte v2-/v3-Binärpakete werden vom Swift-Decoder gelesen; Apptests prüfen Paketverlust, erneute Verbindung, Displayreset und Geräteneustart. Zusätzliche Tests prüfen kurze Spitzen zwischen BLE-Paketen, Fault-Ausschluss, negative Tare-Anzeige, Epochwechsel, Standby-Policy und persistente App-Sitzungen. Der iOS-Simulator-SDK-Build wird separat geprüft.

Vor echter Benutzung sind sämtliche Abnahmetests aus `../electronics/FIRMWARE_CONTRACT.md` am Muster erforderlich, insbesondere Versorgung/USB-Wechsel, Kabelziehen, ADC-Ausfall, Endschalter vor Hartanschlag, Kalibrierung und BLE-Abbruch. Loop-Polling ersetzt keine Hardware-Sicherheitsfunktion; lang blockierende Diagnoseschritte können kurze Schalterereignisse verpassen. Flash-Schreiben ist deshalb nur im Standby erlaubt. Batterie-Minimum und Versorgung werden erst mit Hardwaretests freigegeben. Kein vollständiger 330-SPS-Rohdatenspeicher, keine Firmware-Updates per BLE, keine bewertete Überlastgrenze, keine garantierte Batterielaufzeit.

Herstellergrundlagen: [Seeed Board/Core](https://wiki.seeedstudio.com/XIAO_BLE/), [Seeed Variant](https://github.com/Seeed-Studio/Adafruit_nRF52_Arduino/tree/master/variants/Seeed_XIAO_nRF52840), [ADS1220-Datenblatt](https://www.ti.com/lit/ds/symlink/ads1220.pdf), [Arm Toolchain](https://developer.arm.com/Tools%20and%20Software/GNU%20Toolchain). Projektvorgabe: `../electronics/FIRMWARE_CONTRACT.md`.
