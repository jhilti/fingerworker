# Passprobenkorrektur Rev E, 13.10.2026

Die weibliche Aufnahme war mit dem Kanal unten exportiert. Ihre Kanaldecke erforderte eine nominal 33,5-mm-Brücke. Jetzt liegt die geschlossene Rückseite auf dem Bett, der Kanal ist oben. Die STL wurde ausschließlich um die Längsachse X um 180° gedreht; Passungsmaße und Volumen bleiben gleich. Der männliche STL ist bytegleich. Die Originale sind unter `original/` eingefroren.

`check_orientation.py` / `orientation-validation.json`: geschlossene Netze, starre Drehung, vollständige 30 × 42 mm Bettauflage, keine erhöhte horizontale Unterseite, 45°-Flanken. Die Korrektur ist im Generator `../make_guide_coupon.py` enthalten.

Das H2D-Projekt Rev E füllt beide Passproben zu 100 %. `slicer-bridge-validation.json` vergleicht die echten G-Code-Pfade: weibliches Objekt 2 hat vorher 134 Bridge-Extrusionssegmente (bis 36,568 mm einschließlich Anschlussbereich), danach null. Alle sechs Platten wurden erneut erfolgreich geslict. Druck- und Montagegeometrie der 30 Geräteteile bleibt unverändert gegenüber Rev D; funktionales CAD bleibt Rev C.

Beim Zusammenstecken die weibliche Probe wieder auf den Kanal nach unten drehen. Diese Probe prüft die nominale Passung. Der große P04-Griff wird im Projekt weiterhin in seiner bestehenden Lage mit Stützen gedruckt; seine Druckunterseite ist damit nicht durch eine gedrehte, stützfreie Passprobe qualifiziert.

Aktuelle Lieferung: `../../print/bambu-2026-10-13-RevE/Fingerworker_RevE_H2D_04mm_PETG.3mf` und `../../print/Fingerworker_H2D_PETG_RevE_2026-10-13.zip`.
