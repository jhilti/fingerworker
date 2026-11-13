# R19 – Konstruktionsreview

**Native R19-Geometrie geprüft. Druckvorbereitung auf deinen Wunsch zurückgestellt.** Es gibt noch kein freigegebenes R19-Bambu-Projekt, keinen neuen Slice und keinen gestarteten Druckauftrag.

| Bereich | Umsetzung |
|---|---|
| P01 Daumenrand | Beidseitig variable Rundung; obenR2, HandgelenkseiteR1, untere LippeR0,4 |
| Verbleibender Steg | Native Mindestabstände2,432/2,433mm zum bestehenden Rückgriff; vorher3,090mm |
| Unterlippe | Alle58 unabhängigen Boden-/Lippenquerschnitte bleiben identisch |
| Organische Handballenauflage | R18-Loft und Kontaktlage unverändert; KroneZ34,5 und mittlere Wölbung etwaX−31 |
| P06L/P06R | Zwei massive getrennte Stangenblöcke, je zwei erforderliche M3×8; Brücke und Schnapparme entfernt |
| P01 Heckgegenhalter | Nicht mehr benötigte Rastnocken entfernt; ursprünglicher gerundeter Boden wieder frei |
| P08 optional | Hohe Schnappclips durch feste Schraubohren ersetzt; zwei erforderliche M2×8 in bestehenden M2-Inserts |
| P09 | Separater Klickdeckel mit Kabelhalter unverändert |
| Kraftpfad/Service | P05 separat; Stangenbohrungen, Sensorzugang,30-mm-Hub und Q01-Entnahme geprüft |
| Gurte | Vier innenliegende27×4-mm-Schlitze für zwei25-mm-Gurte erhalten |
| Teilezahl |94 native Körper;90 bisherige Körper geometrisch unverändert. P06 wird durch zwei Körper ersetzt |
| Druckstatus | PRINT_SETUP_DEFERRED_BY_USER – keine R19-Slice- oder Bambu-Freigabe |

Die größere Rundung entsteht an den ursprünglichen Muldenkanten vor dem unveränderten organischen Loft. Der native Onshape-Export ist maßgeblich. Die fehlgeschlagenen lokalen Defeaturing-Versuche sind nur Diagnosehistorie und keine Fertigungsgeometrie. Die variable Rundung schützt die dünne Unterlippe vor einer pauschalen großen Abrundung.

[Native Integration:81 Prüfungen](validation/native-integration.json) · [Native Randmessung](validation/native-rim-check.json) · [Versionsbindung](validation/native-release-binding.json) · [Massive Halter: lokaler Check](latches/design-specification.json)
