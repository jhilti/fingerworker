# R18 – Form- und Schnittstellenreview

**Native R18-Geometrie und PLA-Druckwege geprüft.** Der nächste Ausdruck bleibt die praktische Prüfung von Handkomfort, Halt, Passung und Belastbarkeit. **Bambu Studio: Öffnen und visuelle Vorschau warten auf das Entsperren des Mac.**

| Bereich | Umsetzung |
|---|---|
| Handballenauflage | Sieben einfache, gerundete Querschnitte ergeben eine breite, weich gewölbte Auflage; Krone nominal Z34,5 |
| Handlage | Mittlere Wölbung etwa 2 mm zur Handgelenkseite; Kontur bleibt nahe am bisherigen Griff |
| Schulterübergänge | Weicher Übergang in beide bestehende Daumenbereiche; nur die alte obere Krone über Z30 wird lokal neu geformt |
| Seitliche Daumenmulden | Beidseitig am festen P01; nominal 4 mm tief; offene Oberseite, Boden R1,5 und Mundkante R0,4 |
| Vorhandene Rückgriffe | Die flachen handgelenkseitigen Daumenrückgriffe bleiben erhalten |
| Tragende Verbindung | Einteiliger P01-Rahmen; ursprüngliche untere Kraftabstützung bleibt erhalten |
| Stangensockel | Ø6,2-Bohrungen unverändert; äußeres Material wird für die Seitenmulden lokal geformt, verbleibende Wand geprüft |
| Messkraftpfad | P05 bleibt separat; zentraler neuer Körper bleibt hinter X−16; nomineller Sensorgap und Service bleiben erhalten |
| Montage | Klickstellen, Gehäusedach, H18-Werkzeugzugang, 30-mm-Hub und Q01-Entnahme bleiben erhalten |
| Gurte | Vier innenliegende 27×4-mm-Schlitze für zwei echte 25-mm-Gurte unverändert |
| Teilezahl | Keine neuen Teile; nur P01 neu drucken, übrige 92 native Körper unverändert |

Der lokale OCC-Loft und der native Parasolid-Loft verwenden dieselben Querschnittskontrollen. An den sieben Querschnitten beträgt die größte gemessene Abweichung rund 0,00244 mm. Zwischen den Querschnitten unterscheiden sich die interpolierten Flächen: der Stichprobenvergleich der oberen Ansichtsnetze zeigt bis 1,20 mm einschließlich Tessellierungsabweichung. Der visuell geprüfte native Onshape-Export ist maßgeblich. Die native Geometrie wird deshalb unmittelbar auf Funktionsabstände, geschützte Schnittstellen und erlaubte Formänderungen geprüft. Die lokale Vorschau ersetzt diesen Vergleich nicht.

Die geerbte Kopfkommentierung der eingefrorenen FeatureScript-Quelle nennt noch X−29/Z33 für den ursprünglichen R16-Quergriff. Diese Angaben beschreiben das darunterliegende Ausgangsteil vor dem angehängten R18-Loft. Die aktuelle R18-Krone liegt nominal bei Z34,5; die mittlere Wölbung reicht etwa bis X−31. Maßgeblich sind der R18-Abschnitt, die Querschnittskontrollen und der gespeicherte native Export.

Der Kraftpfad bleibt P04 → Federn bzw. P05-Endanschläge → P05 → Druckstift → Sensor → Stahlrückplatte → feste P01-Abstützung → Handballen. Keine feste Griffwölbung darf das Messjoch berühren.

[Native Integrationsprüfung](validation/native-integration.json) · [Versionsbindung](validation/native-release-binding.json) · [Lokaler Vorabcheck](mechanics/preflight.json) · [Druckprüfung](../../print/bambu-R18-organic-palm-2026-11-13/PRINT_QA_NOTES.md)
