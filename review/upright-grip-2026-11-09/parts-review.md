# R16 – Konstruktions- und Schnittstellenreview

**R16-CAD und berechnete PLA-Druckwege geprüft.** Die Nachweise gelten für den unten verlinkten nativen Stand. Handkomfort, sicherer Halt, Druckpassung und Belastbarkeit bleiben am Ausdruck zu prüfen.

| Bereich | Umsetzung |
|---|---|
| P01-Handballenfläche | Aufrechte Handgelenkseite bei X−29; obere Höhe weiterhin Z33; Quergriff 126 mm |
| Daumenkontakt | Gerundete Schultern über beiden vorhandenen Stangensockeln; 130 mm Gesamtbreite |
| Daumenrückgriffe | Beidseitig Y±51; etwa 4 mm tief; 45°-Dach; Mundkanten R0,8 |
| Kontakt-Rundungen | Handballenkante R5; Sensorseite R3; Quergriffenden R3; Schulteroberseiten R4, Schulterenden R2 |
| Tragende Verbindung | Breite vorhandene Abstützung; kein freistehender schmaler Stiel |
| Alte Stufe hinter dem Griff | Nur X−40…−29, Z11,5…14,5 entfernt; durchgängiges 2-mm-Elektronikdach und alle Raststellen bleiben |
| Stangensockel | Ursprüngliches Material und Ø6,2-Bohrungen vollständig erhalten |
| Sensorpfad | P05 bleibt vom festen Rahmen getrennt; feste Reaktion und Führung unter Z30 bleiben erhalten |
| Service | H18-Zugänge, Sensorentnahme +X3,2/+Z40, Elektronikrastung und Entnahmewege erhalten |
| Gurtaufnahme | Vier unveränderte 27×4-mm-Schlitze für zwei echte 25-mm-Gurte |
| Druckumfang | Kein zusätzliches Teil; P01 neu, übrige fünf Stücke im Druckpaket geometrisch unverändert |

Die gerundeten Schultern überdecken die zuvor scharfkantigen Sockeloberseiten. Die neue Griffgeometrie liegt hinter dem bewegten Mechanismus. Ein tiefer umlaufender Untergriff wurde nicht umgesetzt: dafür müssten Stangensockel oder Elektronikdach ausgeschnitten werden. Stattdessen bilden zwei flache, von der Handgelenkseite zugängliche Rückgriffe eine Haltekante.

Der Kraftpfad bleibt **P04 → Federn bzw. P05-Endanschläge → P05 → Druckstift → Sensor → Stahlrückplatte → feste P01-Abstützung → Handballen**. Keine neue feste Fläche darf das bewegliche Messjoch berühren. Die CAD-Prüfung bestätigt diese nominale Trennung; sie ist keine Belastungsprüfung des PLA-Teils.

Die Grundfläche bleibt unverändert. P01 liegt beim Druck mit dem Boden auf dem Bett. Die Handballenfläche ist eine Außenwand, die Daumenrückgriffe haben schräge Dächer. Der finale Slice und die Kontaktflächenprüfung sind im [Druckpaket](../../print/bambu-R16-upright-grip-2026-11-09/Fingerworker_R16_H2D_04mm_PLA_Basic_Print_Ready_Package.zip) enthalten. Druckparameter und Stützen können die reale Oberfläche beeinflussen; der nächste Ausdruck bleibt die Komfort- und Montageprobe.

[Native Geometrie](validation/native-geometry.json) · [Bewegung](validation/native-motion.json) · [Service](validation/service-native.json) · [Q01](validation/fixture-q01-check.json) · [Lokaler Vorabcheck](mechanics/preflight.json)
