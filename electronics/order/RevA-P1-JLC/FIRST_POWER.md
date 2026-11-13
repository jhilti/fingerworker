# Fingerworker A-P1 - Erstinbetriebnahme am Tisch

Diese Prüfungen erfolgen **nach Fertigung**, bevor die Elektronik in die Mechanik eingebaut oder ein Akku geladen wird. Sie sind noch nicht durchgeführt. Schaltplan und `assembly/pad-map.csv` geben Messpunkte an. Keine Last- oder Kraftfreigabe der Mechanik wird daraus abgeleitet.

## 1. Ohne Versorgung

Bestückung, C4/C7=22 uF, Dioden-/IC-Orientierungen und Modulunterseite kontrollieren. Durchgang J1.1–U1.19 und J1.2–U1.20 prüfen. Widerstände aller Versorgungsschienen gegen GND auf Kurzschluss prüfen; Kondensatoraufladung beim Ohmmessen beachten. Akku bleibt abgesteckt. Sensor und Endschalter zunächst abstecken.

## 2. Versorgung und Testfirmware

Zunächst USB über eine geeignete strombegrenzte 5-V-Quelle einspeisen, ohne Akku. Werkseitigen XIAO-Bootloader erhalten. Die Platine wird ohne Applikationsfirmware bestellt; bevor der Messzweig eingeschaltet wird, muss Testfirmware folgende Zustände setzen:

- BOOST_EN und ANALOG_EN LOW, ADC_CS HIGH.
- XIAO P0.13 hochohmig ohne Pull-up/-down für den nominellen 50-mA-Lademodus. P0.14 LOW für den internen Akku-Messteiler. Nicht den P0.13-HIGH-Code aus älteren Wiki-Beispielen verwenden.
- Aufgezeichnete Boardrevision und tatsächlich verwendeten Seeed-Core dokumentieren. Physische Portnamen aus dem Schaltplan verwenden, keine ungeprüften Arduino-Nummern.

V3V3 an U1.12 messen, Ausgang V5A bei deaktiviertem U3 prüfen. BOOST_EN einschalten, zunächst mindestens 10 ms warten. VBOOST soll nominal 5,425 V erreichen. Danach ANALOG_EN einschalten, zunächst mindestens 20 ms warten. V5A soll nominal 5 V erreichen. Bei Überspannung, unerwarteter Erwärmung oder Strombegrenzung abschalten.

## 3. ADC-Rampen und analoge Funktion

Mit Oszilloskop **DVDD und AVDD direkt an U4** bei USB-Kaltstart, Aktivierung des Messzweigs, Standby/Wiederanlauf sowie später Akku-/USB-Wechsel erfassen. Laut ADS1220-Datenblatt müssen beide Rampen monoton und langsamer als 1 V pro 50 us sein. Das interne LDO-Softstart-Verhalten und die XIAO-3,3-V-Regelung sind kein Nachweis für diese Anforderung. Wird sie verletzt, regulären ADC-Betrieb stoppen und eine Schaltungsrevision mit kontrollierter Rampenzeit erstellen. Längeres Warten in Firmware löst eine unzulässige Rampe nicht.

VBOOST-Ripple und V5A-Ripple mit kurzer Massefeder messen, auch unter realer Last und beim BLE-Senden. C5=47 pF ist der bestückte Startwert. Regelreserve des 5-V-LDO und Einschwingzeit prüfen. C4/C7 wurden vergrößert, daher Ein- und Ausschwingzeiten einschließlich Entladung messen.

Sensor spannungslos anschließen. Bei 5 V Erregung beide Sensor-Ausgänge gegen GND messen. Für Gain 8 und maximal 264 mV Differenz aus der ursprünglichen Auslegung muss der Gleichtakt innerhalb etwa 1,256–3,744 V bleiben. TE garantiert im vorliegenden Familienblatt keine feste 2,5-V-Gleichtaktlage. Bei Abweichung Eingangsbereich/Verstärkung neu bewerten, nicht einfach kalibrieren.

SPI Mode 1, 1 MHz, MSB first. ADS1220 RESET, Register 06 84 40 00 schreiben und zurücklesen, START/SYNC. DRDY prüfen, erste Einschwingwerte verwerfen. Rohwert korrekt als vorzeichenbehaftete 24-Bit-Zahl erweitern. Versorgung und Referenz müssen stabil sein, bevor Werte als gültig gelten.

## 4. Endschalter, BLE und Kraftkalibrierung

J3 mit NC/COM verbinden, NO isolieren. ENDSTOP_N ist bei intakter, unbetätigter NC-Schleife HIGH, bei Endlage oder unterbrochener Leitung LOW. Bei abgeschalteter oder hochlaufender Messversorgung ist der Pegel ungültig. Bei LOW Kraftwerte für Leistungs-/Peak-Auswertung sperren; der Hartanschlag kann Handkraft am Sensor vorbeileiten. Rohdaten zur Diagnose erhalten. Nach Rückkehr der Schleife mindestens 10 ms stabil HIGH abwarten. Details und vollständige Wahrheitstabelle: FIRMWARE_CONTRACT.md. Seitentaster, Entprellung, Standby und Wiederaufwachen testen. Im Isometriemodus ist keine Betätigung des Vollhubschalters zu erwarten, LOW bleibt aber ein Fehlerzustand.

Kalibrierung erst in der endgültig montierten Mechanik mit mehreren bekannten Lasten durchführen. Nullpunkt, Nichtlinearität, Hysterese und Reibung dokumentieren. Rohdaten erhalten. BLE-Aussetzer mit Hand am späteren Gerät prüfen. Sensor-Nennlast und ADC-Bereich sind keine zulässige Gerätebelastung.

## 5. Akku zuletzt

Den Originalakku Adafruit 1570 auf richtige Steckerbelegung prüfen: tatsächlicher Pluskontakt muss auf **J1.1**, Minus auf **J1.2** landen. JST-PH legt keine universelle Polarität fest. Bei falscher Belegung ein korrekt konfektioniertes Kabel verwenden; nicht verpolt einstecken.

Erst nach der USB-Prüfung Akku anschließen. Ladestrom am gelieferten XIAO messen, ungefähr 50 mA erwartet. Ladeendspannung, Zellentemperatur, Wechsel USB/Akku und Standby-Strom prüfen. Die Zelle nur im spezifizierten Ladebereich 0–45 °C laden. Der XIAO misst die Zelltemperatur nicht direkt. Ein endgültiger Akkuschwellwert und die Laufzeit folgen aus den Messungen, nicht aus dem Kapazitätsaufdruck.

## Aufzeichnung

Für jedes Muster Serienkennung, Modulrevision, Firmwarestand, Messgerät und Datum festhalten. Messkurven und Werte für die obigen Punkte ablegen. Die Annahmen zur Elektronikaufnahme, insbesondere der zuletzt dokumentierte enge Gehäusespalt, bleiben Teil der separaten mechanischen Überarbeitung.

Quellen: [ADS1220, insbesondere 9.3.2](https://www.ti.com/lit/ds/symlink/ads1220.pdf), [TPS7A20](https://www.ti.com/lit/ds/symlink/tps7a20.pdf), [Seeed-Schaltplan](https://files.seeedstudio.com/wiki/XIAO-BLE/Res/260828_XIAO_nRF52840.pdf), [Zelldatenblatt](https://cdn-shop.adafruit.com/product-files/1570/1570datasheet.pdf).
