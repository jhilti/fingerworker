# Flat132 R11 – PLA-Klickmontage

Stand 03.11.2026. PLA ist der Standard. Die vorhandene R10-Grundplatte mit massiver Handballenauflage bleibt unverändert. Die neue Konstruktion vereinfacht Gehäuse und Anschläge; die kontinuierlichen Mechanikeinstellungen bleiben erhalten.

| Änderung | Ergebnis |
|---|---|
| P08 am Rahmen | Zwei lange, zugängliche Rastarme greifen am vorhandenen Rand der Handballenauflage ein. Die zwei M2-Montageschrauben bleiben optional. |
| P09 an P08 | Zwei lange Außenlaschen halten den Deckel. Die drei vorhandenen Deckelschraubstellen bleiben optional. |
| P10 | Kabelkontaktfläche als breite Säule in P09 integriert; separate Leiste und zwei M1,6×3 entfallen. |
| Vier P07 | Kontaktflächen in die beiden größeren P120/P121 integriert; vier Mikroteile und Klebestellen entfallen. |
| P04 Fingerauflage | Gleiche Geometrie, neue Drucklage: vordere Stirnseite unten, schlanke Baumstützen ausschließlich vom Bett. Die Zugfläche wird oben gedruckt. |
| P120/P121 | Zungenoberseite unten; größere zusammenhängende Bettanlage und senkrechter Fangschlitz. |

Der federfreie Passsatz sinkt von **18 auf 13 Stücke**: zehn eigentliche Druckteile, zwei Stangen-Formhilfen und Q01. Schrauben und Muttern sind keine Druckobjekte. Drei getrennte Platten erleichtern Wiederverwendung und Oberflächenkontrolle: Rahmen, übrige Montagekomponenten, Fingerauflage.

Die gesamte Verbindungsmatrix einschließlich der weiterhin erforderlichen mechanischen Sicherungen steht im [Montagereview](ASSEMBLY_JOINT_REVIEW.md). P06-Kappen, verstellbare P12-Schuhe und P11-Schalternocken behalten ihre Schraubsicherung. Ihre vorhandenen Einstell- und Einbauwege erlauben keine einfache zusätzliche Rastung bei unverändertem Rahmen. P05 muss frei auf den Sensor wirken und darf nicht am Rahmen festgeklickt werden.

[Druckpaket](../../print/bambu-R11-PLA-click-2026-11-03/README.md) · [Montage](MONTAGE.md) · [Stücklistenänderungen](BOM_Aenderungen.csv) · [Gehäusedetails](enclosure/README.md) · [Fingerflächenvergleich](../finger-surface-study-2026-11-03/README.md)

Die langen PLA-Arme sind für geringe Auslenkung und lösbare Montage ausgelegt. Die geometrische Blattformel ergibt nominell 0,45 % beziehungsweise 0,405 % Randfaserdehnung. Diese Werte sind ein Konstruktionsvergleich, keine gemessene Werkstoff- oder Dauerfestigkeit. Die fertig gedruckten Clips und Passungen müssen am unbelasteten Muster bestätigt werden. Federn, echte Sensorhalterung und belastete Hardware bleiben für den späteren Funktionsaufbau erforderlich.

Die Quellenentscheidung, Arme lang und in ihrer Biegeebene zu drucken sowie sie im eingerasteten Zustand zu entlasten, folgt den allgemeinen [Formlabs-Hinweisen zu Schnappverbindungen](https://formlabs.com/eu/blog/designing-3d-printed-snap-fit-enclosures/). Konkrete Passungen werden hier aus der eigenen CAD- und Slicerprüfung abgeleitet.

<!-- FINAL_NATIVE -->
## Finaler nativer Stand

[Onshape R11](https://cad.onshape.com/documents/15316cc6370631845af136b2/v/a6ea6390a313176b40101f6b/e/d253eb87b70818ebde8215f0) · Quellhash `c8ec18f08149553001ccf8173f35fe57eee6a16be0294be2d7f88577f658cf5e`.

Die finale Regeneration enthält 117 gültige Körper. Vier geänderte BReps stimmen exakt mit der unabhängigen CSG überein; 113 übrige BReps einschließlich P01 und P04 sind exakt unverändert. [Natives CAD-Protokoll](validation/native-geometry.json). Die neuen Gehäusestocks sind über den vollständigen korrelierten Bewegungsbereich geprüft: 882 konservative Prüfungen ohne Konflikt. [Bewegungsnachweis](enclosure/motion-preflight.json). Die Montage-/Entriegelprüfung des Gehäuses enthält 307 Prüfungen. [Montagenachweis](enclosure/local-enclosure-preflight.json).

Das finale native Bambu-Projekt wurde unabhängig gegen alle 13 Quellmeshes zurückgeprüft und auf drei Platten erfolgreich gesliced. [Prüfberichte und Slicerzeiten](../../print/bambu-R11-PLA-click-2026-11-03/PRINT_QA_NOTES.md). Die berechneten Kontaktregionen von P04 bleiben ohne Stützen; reale Oberfläche, Clips und Stützentfernung sind am Druck zu bestätigen.
