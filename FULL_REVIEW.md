# Fingerworker — Vollreview vom 21.09.2026

> Aktueller Software-/CAD-Abgleich vom 11.10.2026: [STATUS](review/software-2026-10-11/STATUS.md). Firmware und App sind implementiert; die Federbeschaffung ist erfolgt. Die folgende Darstellung bleibt ausdrücklich der historische Review vom 21.09.2026.

Dieser Bericht dokumentiert den Stand vom 21.09.2026. Die später ergänzten hinteren Seilaufnahmen und ihre eigenen Nachweise stehen in [REAR_TETHER.md](REAR_TETHER.md).

Der aktuelle Stand wurde in Onshape und im nativen KiCad-Projekt geprüft und überarbeitet. **Mehrere konkrete Konstruktions- und Prüffehler sind behoben. Das Gerät ist weiterhin ein Entwicklungsprototyp, keine vollständig validierte Konstruktion.** Vor allem die tatsächliche Handpassform und die zulässige Belastung sind noch offen. „Alle Fehler beseitigt“ wäre derzeit nicht belegbar.

[Live-Modell in Onshape](https://cad.onshape.com/documents/15316cc6370631845af136b2/w/664d0779b5d992870442f997/e/d253eb87b70818ebde8215f0). Beim Review geöffnet: 15 mm Hub, 0 mm Zusatzvorspannung, leichtes Federpaar, illustrative Hand und Elektronikstudie. Die damaligen STL-Dateien wurden separat bei 0/0 mm ohne Referenzhand/-elektronik exportiert.

## Behoben

| Befund | Änderung | Nachweis / Grenze |
|---|---|---|
| Sensorhalterung hatte keine vollständig ausgeführten tragenden Befestigungen | 2-mm-S355-Halteplatte, 1 mm im Rahmen versenkt, zwei M3×8-Senkschrauben und captive Stahl-Vierkantmuttern | Schraubenköpfe bündig; gefundene Überschneidung mit Handballenmanschette beseitigt. Stahlteile sind Kauf-/Bearbeitungsteile, keine Druckteile. |
| Verstellbare Sensorkassette war bei Entlastung nicht gefangen; Grenzen nur in CAD | Zwei Retentionsschrauben mit Stahl-Abstandshülsen in Langlöchern; nominal 0–2 mm Verstellweg | Schrauben verspannen die Stahlteile, nicht die gedruckten Gleitflächen. Anschläge sind keine Drehmomentbegrenzer. |
| Vorspannung konnte sich verstellen | Versenkte M3-Klemmschraube und Messingdruckstück gegen M6-Einsteller | Vor Verstellen lösen; Haltekraft und Bedienzugang am Muster prüfen. |
| Lose, kleine Druckstiftauflage im Joch | Gefangener Stahl-Druckstift mit Ø8-mm-Schulter und M3-Mutter | Nominale tragende Ringfläche etwa 42,2 mm². Kein Festigkeitsnachweis für das gedruckte Joch. |
| Elektronikgehäuse hatte nur 0,1 mm Abstand zur Mechanik | Gesamte Elektronikstudie um 1,25 mm nach außen versetzt | Aktuelles CAD-Minimum 0,6 mm, Gerätehöhe weiterhin 30 mm. Außenhülle mit Studie 180,1 × 180 × 30 mm. |
| Ein unterbrochener NO-Endschalterdraht blieb unauffällig | Vorhandenen Öffner verwenden: **NC→J3.1, COM→J3.2; NO isolieren**. Signal jetzt **ENDSTOP_N**, aktiv LOW | Schaltplan, Symbolbibliothek, Datenlisten und PCB-Netzname konsistent geändert; Kupfertopologie unverändert. LOW bedeutet Endlage **oder** Leitungsunterbrechung. Hardwaretest/Firmware noch ausstehend. |
| Kraftwert am Hartanschlag konnte als vollständige Handkraft missverstanden werden | Messsperre vor dem Hartanschlag und Status-/Kalibrierregeln spezifiziert | Am Anschlag entsteht ein Kraftweg am Sensor vorbei. [Firmwarevertrag](electronics/FIRMWARE_CONTRACT.md) enthält Logik und Abnahmetests; noch keine implementierte Firmware. |
| Prüfskript benutzte alte ERC-/DRC-Dateien und ignorierte unerwartete Netzlistenpins | Frischer ERC-/DRC-/Netzlistenlauf, vollständiger Pinvergleich einschließlich NC, zusätzlicher PCB-Padvergleich, SHA-256-Bindung | Ein fehlgeschlagener Lauf hinterlässt kein altes PASS. Nur die zwei ausdrücklich bekannten, isolierten JST-Lötanker sind als mechanische Pads ausgenommen. |
| Druckdateien stammten aus dem älteren Aufbau | Elf Teile frisch aus Onshape exportiert und separat als Entwicklungssatz abgelegt | Geschlossene Netze, positives Volumen, keine Skalierung oder Netzreparatur. Alte und neue P01/P05 nicht mischen. |

## Verifikation des aktuellen Stands

- **Onshape:** neun Konfigurationen, jeweils 43 ausgewählte Körperpaargruppen, insgesamt 387 Prüfungen; keine gemeldete Volumenüberschneidung. Leichte Federn: Hub/Vorspannung 0/0, 15/0, 30/0, 0/2, 15/1 und 30/2 mm; bestehendes stärkeres Paar: 30/2; Isometrie: 15/0 und 13/2 mm. Alle 63 Elektronik-Paarprüfungen CLEAR. Beabsichtigte/unklassifizierte Grenzflächenkontakte bleiben ausdrücklich REVIEW.
- **KiCad 10.0.6:** 140 verbundene und 10 explizit unbenutzte Pins geprüft; keine Netz- oder Padabweichung, keine ERC-/DRC-Verletzung, keine offene Verbindung, keine Schaltplan-PCB-Abweichung. 48 Footprints, 4 Lagen, 75 Vias; eigene zusammenhängende Innen-Massefläche ohne Signalleiterbahnen.
- **Maßprüfung:** 2.562 Federkraftfälle und 21 Isometrie-Vorspannungspositionen rechnerisch geprüft. Das ist eine Maß-/Quelltextprüfung, keine physikalische Simulation.
- **Export:** elf geschlossene Druckteilnetze, zusammen 355,319 cm³ geometrisches Volumen; etwa 2,78 % weniger als der vorherige kompakte Drucksatz. Tatsächlicher Materialverbrauch hängt von Druckpfaden und Infill ab.
- Personal hand-fit study omitted from public snapshot; physical ergonomic fit remains to be checked.

Quellgebundene Protokolle: [Onshape](review/onshape-full-review.json), [Elektronik-Einbau](review/electronics-packaging-validation.json), [KiCad](electronics/kicad/reports/verification-summary.json), [Drucknetze](review/full-review-print-validation.json).

## Noch offen — konkrete Gründe gegen eine Freigabe

| Priorität | Problem | Erforderlicher Abschluss |
|---|---|---|
| Hoch | Physical ergonomic fit remains to be checked | Federfreies Passformmuster mit echter Auflageposition prüfen; Daumenfreiraum, verdeckte Kontaktflächen und Griffhaltung am realen Muster bestätigen. |
| Hoch | Keine zulässige Gerätezugkraft und kein qualifizierter Druckprozess | Zielkraft, Material und Drucker festlegen; Muldenboden, Mittelführung, Joch, Rahmen, Palmohren und Befestigungen unter zentralem und einseitigem Zug auslegen/prüfen. Die 200-lbf-Sensorgrenze ist keine Traglastfreigabe. |
| Hoch | Endanschlag kann Handkraft am Sensor vorbeileiten; Führungsreibung verfälscht auch davor | Klickpunkt mit ausreichendem gemessenem Vorlauf einstellen; Messsperre implementieren. Auf-/Abwärtskalibrierung und exzentrische Belastung der kompletten Mechanik prüfen. |
| Hoch | Elektronikgehäuse ist eine Hüllkörperstudie | Tatsächlichen XIAO-Stapel und Akkugegenstecker messen; PCB-/Akkuhalter, Druckknopf, Montagezugang, Kabelradien, Zugentlastung und Zellspiel fertig konstruieren. Die 0,6 mm Abstand gegen Toleranzen und Durchbiegung prüfen. |
| Mittel | Sensorkörper selbst ist beim Ausbau beider Federn weiterhin lose | Sensor beim Wechsel unterstützen; separate unbelastete Fangsicherung auslegen, ohne einen parallelen Messkraftweg zu schaffen. Hauptmutter beim Ausbau von Klemmschraube/Halteplatte sichern. |
| Mittel | Leichtes Federpaar ist ein Beschaffungsziel, kein qualifiziertes Katalogteil | 2 N/mm je Feder, 102 mm freie Länge, erforderliche 33 mm Arbeitskompression, Enden und Paarabweichung vom Hersteller bestätigen. Bestehendes 7,8-N/mm-Paar erreicht bei 30/2 mm rechnerisch 514,8 N und überschreitet den angegebenen S2-Weg; Lebensdauer/Lastfall ungeklärt. |
| Mittel | Elektrische Funktion ist bislang berechnet und geometrisch geprüft | Sensor-Gleichtakt, Versorgungshochlauf, Ripple, Filtereinschwingen, Lade-/Temperaturverhalten, Akkupolarität und BLE mit Hand/Gehäuse am Muster messen; siehe unten. |
| Mittel | Firmware/Bedienung noch nicht gebaut | Firmwarevertrag implementieren und Tests für ADC-Fehler, NC-Schleife, Tare, Peak-Gültigkeit, Zeitstempel, BLE-Paketverlust und Versorgungsausfall bestehen. |

## Elektronikreview: geprüft und noch zu messen

ADS1220-PW-Pinbelegung, Gain 8, differenzieller Eingang, externe ratiometrische Referenz, SPI und Versorgungstopologie sind gegen die Herstellerdaten abgeglichen. Für den angenommenen maximalen Sensorwert von 264 mV bleibt nominaler Messbereich vorhanden; der zulässige Gleichtakt am realen Sensor muss dennoch bestätigt werden. Die vier Sensoradern liefern keine echte entfernte 6-Leiter-Kompensation; die separaten Sense-Leiter enden an J2.

Die aktuelle [ADS1220-Dokumentation](https://www.ti.com/lit/ds/symlink/ads1220.pdf) verlangt monotone AVDD-/DVDD-Rampen langsamer als 1 V pro 50 µs. Beide Rampen messen; ein Softwaredelay nach einem zu schnellen Anstieg behebt die Ursache nicht. Falls verletzt, Versorgung mit kontrollierter Anstiegszeit ergänzen. Boost/LDO müssen außerdem bei Akku-/USB-Wechsel, Funkaktivität und maximaler Brückenlast stabil bleiben. [TPS7A20](https://www.ti.com/lit/ds/symlink/tps7a20.pdf), [TPS61041](https://www.ti.com/lit/ds/symlink/tps61041.pdf).

Der [Omron SS-01GL2](https://omronfs.omron.com/en_US/ecb/products/pdf/en-ss.pdf) stellt COM/NC/NO bereit. Die neue NC-Schleife erkennt Unterbrechungen als Messsperre, unterscheidet sie aber nicht von Endlage und erkennt keinen Kurzschluss gegen Masse. Bei ausgeschalteter V5A ist ENDSTOP_N ungültig.

Akku: reale J1-Polarität vor Anschluss messen. XIAO-Lademodus gemäß [Seeed-Schaltplan](https://files.seeedstudio.com/wiki/XIAO-BLE/Res/260828_XIAO_nRF52840.pdf): P0.13 hochohmig ohne Pull für nominell 50 mA; P0.14 LOW für Batterieteiler. Ladetemperatur und Strom am tatsächlichen Modul/Zellaufbau prüfen; eine konfigurierte Ladestromangabe ersetzt keine Messung.

## Dateien und nächster sinnvoller Schritt

- [KiCad-Projekt](electronics/kicad/Fingerworker_RevA.kicad_pro) — aktuelle bearbeitbare Elektronik.
- [FeatureScript](fingerworker_mvp.fs) — aktueller in Onshape kompilierter Modellquelltext.
- [Entwicklungs-Drucksatz](print/review-2026-09-21/README.md) — elf aktuelle Teile, zunächst für Passform-/Montageprüfung; kein Lastfreigabepaket.
- [Elektronikvorschau](electronics/kicad/preview/mechanical-fit.png).

Der nächste entscheidende Schritt ist das **federfreie Passform-/Montagemuster**, parallel zu einem Elektronik-Tischaufbau. Für die belastete Variante fehlen noch Zielkraft und tatsächlicher Druckwerkstoff/-prozess. Diese offenen Messungen lassen sich nicht durch zusätzliche kollisionsfreie CAD-Bilder ersetzen.
