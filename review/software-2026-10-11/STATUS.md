> Nachtrag: [Elektronikaufnahme und Metallzeichnungen Rev A](../../mechanical/manufacturing-2026-10-11/README.md) sind inzwischen erstellt. Die Aussagen zu fehlender Konstruktion/Zeichnung unten beschreiben den vorherigen Reviewstand. Physische Freigaben bleiben offen.

# Fingerworker Änderungen und Prüfstand

11.10.2026. Die ohne Hardware bearbeitbaren Software-, Feder-CAD- und Dokumentationspunkte sind umgesetzt. Firmware und App sind Entwicklungsbuilds; elektrische Qualifikation, Handpassform und Belastbarkeit sind weiterhin nicht freigegeben.

## Firmware

- Geräte-Peak aus jedem frisch eingelesenen gültigen ADC-Sample vor der 25-Hz-BLE-Publikation. Kurze erfasste Spitzen zwischen Notifications und Peaks während Funkverlust bleiben im kumulativen Maximum erhalten.
- BLE v3, 43 Bytes, Peak-valid und Messlaufkennung. App-Aufnahmestart schreibt einen nichtnull Reset-Token; Wiederholung desselben Tokens ist idempotent. Nur bestätigte passende Peaks gehören zum App-Messlauf. Nach Geräte-Neustart beginnt eine neue Epoche; davor nicht übertragene Daten sind verloren.
- Benutzer-Standby von Unterspannungsabschaltung getrennt. USB-Wechsel hebt Benutzer-Standby nicht auf; Unterspannungsabschaltung kann bei Batterieerholung ohne Benutzer-Standby erneut starten.
- Eigener Bench-Build mit ausgeschaltetem Analogzweig bis zu explizitem Wake. Normal- und Bench-Build behalten `HARDWARE_QUALIFIED=false`.
- Serial-Parser auf 16 Zeichen je Loop begrenzt. Loop-Polling bleibt gegenüber blockierenden Operationen begrenzt; keine vollständige 330-SPS-Rohdatenspeicherung oder Hardware-Sicherheitsfunktion.

Normalbuild: `firmware/build/`; erster Tischaufbau: `firmware/build-bench/`. Beide enthalten HEX/DFU-Paket und quell-/ausgabegebundene Hash-Manifeste. Erstinbetriebnahme: [Firmwareanleitung](../../firmware/README.md), [FIRST_POWER](../../electronics/procurement/FIRST_POWER.md).

## iPhone-App

- Geräte-Peak mit Epoche, Retry und Bootwechselprüfung; v1/v2 und Simulation bleiben als empfangene Stichproben gekennzeichnet.
- Automatische Wiederverbindung nach unerwartetem Abbruch; bewusste Trennung/Simulation/Scan beendet Wiederverbindung. Aufnahme bleibt bei Verbindungsabbruch offen und kennzeichnet Unterbrechungen.
- Sitzungsbibliothek mit atomarer JSON-Speicherung ungefähr jede Sekunde bei eintreffenden Paketen sowie bei Stop, Trennung und Background. Nach Neustart auswählbar und als CSV exportierbar. Ein abrupter Prozessabbruch kann Daten seit der letzten Speicherung verlieren; unfertige und unterbrochene Sitzungen bleiben erkennbar.
- Stop wartet maximal eine Sekunde auf den nächsten kumulativen Peak; Timeout markiert die Sitzung unterbrochen.
- Bluetooth-central Background-Modus deklariert. Tatsächliche iOS-Scheduling-/Sperrbildschirmfunktion braucht einen iPhone-Test; Force-quit ist keine fortlaufende Aufzeichnung.
- Charts verbinden keine Sequenzlücken zu einer scheinbar kontinuierlichen Messkurve.

Die App ist im laufenden iPhone-Simulator installiert und gestartet. Eine zusätzliche native UI-Prüfung konnte am gesperrten Mac nicht fortgesetzt werden; keine erfolgreiche UI-/BLE-Abnahme wird daraus behauptet.

## Feder-CAD und Stückliste

Lokaler Quelltext und Live-Onshape-FeatureScript verwenden **0X-DF2194** (Parameter TRUE) und **0X-DF2185** (FALSE). Freie Länge, Rate, Draht-/Außen-/Innendurchmesser, Körpernamen und nominale Kraftausgabe sind angepasst. Wicklungen bleiben illustrative Referenzen, keine Fertigungsvorgabe. Die elf Druckteildefinitionen sind unverändert; [Quelltextdiff](cad-spring-changes.diff).

Frisch in Onshape kompiliert und regeneriert: beide Paare bei 0/15/30 mm Hub, jeweils 0/2 mm Zusatzvorspannung, sowie Isometrie bei 0/2 mm. Hand-, Elektronik- und Seilreferenzen eingeblendet. **14 Konfigurationen, 630 Gruppenprüfungen, keine Volumenüberlagerung.** 166 Kontaktbefunde behalten REVIEW; sie wurden nicht pauschal zu CLEAR umetikettiert. Die illustrative Hand bleibt kein realer Passformnachweis.

- [Quellgebundene CAD-Auswertung](cad-validation.json)
- [Aufgezeichnete Onshape-Ausgaben](onshape-ordered-springs.json)
- [Lokale 2562 Kraft-/Einbaulängenfälle und 21 Isometriepositionen](../device-upgrades-validation.json)
- [Konsolidierte aktuelle Stückliste](../../EINKAUFSTEILE.md)
- [Federkennwerte und Umbau](../../DEVICE_UPGRADES.md)

Die älteren Onshape-/STL-Nachweise bleiben ihren ursprünglichen Quellen und Daten zugeordnet. Der mechanische Druckexport vom 29.09.2026 bleibt verwendbarer Entwicklungsstand; es wurde kein neuer Druckexport behauptet.

## Bestellunterlagen

Gerber, Platinenquellen, Original-BOM/CPL und ursprüngliche Bestell-ZIP sind unverändert. Die historische JLC-Hashliste passt bei 72 von 73 Dateien; das README enthält spätere Portalnotizen und wurde auf den aktuellen dokumentierten Checkout-/Softwarestand korrigiert. Der historische Manifeststand bleibt erhalten; [aktueller Hashabgleich](frozen-jlc-check.json) enthält die jetzigen Hashes und die reine Dokumentationsabweichung. Keine Bestellung oder Zahlung ausgeführt.

## Verifikation

- C++-Logiktests mit Address-/Undefined-Sanitizern: PASS.
- C++→Swift v2/v3-Decoding und Peak-Epoche, Retry-Idempotenz, verlorene Pakete, Boot-/Zählerwechsel: PASS innerhalb der getesteten Logikmodelle.
- Atomare Sitzungsspeicherung, Wiederladen, Aktualisierung und CSV: PASS.
- Normal- und Bench-Firmware compile/link/DFU: PASS; aktuelle Quellen und Paket-Hashes stimmen mit beiden Manifesten überein.
- iOS-Simulator-SDK-Build: PASS; generiertes Info.plist enthält `bluetooth-central`.
- 14 Onshape-Konfigurationen / 630 Gruppen und lokale Federmaßrechnung: PASS in ihrem ausgewiesenen Umfang.
- Native KiCad-ERC/DRC/Pin-/Padprüfung: PASS; Elektronikdesign in dieser Änderung unverändert.

Build-/Testprotokolle und aktuelle Eingangs-Hashes stehen neben diesem Bericht. Die bereits bekannten newlib/nosys-Linkerwarnungen bleiben dokumentiert; sie verhindern den Build nicht und sind kein Hardwarefunktionsnachweis.

## Offen am realen Muster

[ABNAHME.md](ABNAHME.md) enthält die konkrete Reihenfolge und Protokollfelder für Handpassform, Montage/Sondermetallteile, Sensorfangsicherung, fertige Elektronikaufnahme, Federlauf und Lebensdauer, Zielkraft/Druckprozess, Belastung, Versorgung, Endschalter-Vorlauf, Kalibrierung, Funk, Akku/Laden und Laufzeit. Werkstatt-/Gehäusefreigaben benötigen reale Passungen und Komponentenmaße. Die Hardwarequalifikation bleibt bis zu diesen Messungen gesperrt.
