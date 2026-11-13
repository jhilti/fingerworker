# Druckhinweise — kompakte Mittelführung

Revision 20. September 2026. Grundrahmen, Schlitten, Federjoch und Stäbe gehören zur neuen kompakten Ausführung. Vorherige Druckteile nicht als passenden Satz mischen. Gesamtmaß178,25 ×180 ×30 mm; separate Grundplatte156 ×180 mm.

Nur die elf mit `P… PRINT` benannten Körper drucken. `H…` und die optionale Hand sind Referenzgeometrie. Export in Millimetern, 100 %, Hub0 mm und Hand aus.

`print/Fingerworker_30mm_print_pack.zip` enthält die elf STL-Dateien, zwei Passproben und diese Hinweise. Die Geräteteile stammen aus Onshape, Auflösung Fine. Die Netze werden auf geschlossene Kanten und positives Volumen geprüft und starr auf Z0 gesetzt. Manschette und Puffer sind bereits in die unten genannte Orientierung gedreht. Keine Skalierung oder Formkorrektur. Der ursprüngliche Download bleibt als `print/Fingerworker_30mm_Onshape_original.zip` erhalten.

## Führungsprobe zuerst

`guide_coupon_male.stl` und `guide_coupon_female.stl` getrennt mit der flachen Seite nach unten drucken. Die 30 mm langen Proben bilden das neue 32-mm-Mittelprofil ab: 45°-Flanken, 0,30 mm Deckenspiel und 0,45 mm horizontaler Flankenversatz. Die weibliche Probe hat dieselbe 2,7-mm-Deckendicke wie der Muldenboden über der Führung. Im zusammengeschobenen Zustand liegt ihre Unterseite4 mm über der Unterseite der männlichen Probe.

Fäden, Stützmaterial und Elefantenfuß entfernen; von einem Ende zusammenschieben. Leichtgängigkeit und Kipp-/Verdrehspiel beurteilen, dann die Druckkompensation oder CAD-Passung anpassen. Die kurze Probe prüft die Passung; sie ersetzt keine Prüfung des vollen Schlittens unter schiefem Zug.

## Orientierung und Nacharbeit

| Teil | Prototyp-Material / Lage | Hinweise |
|---|---|---|
| Grundrahmen P01 | PETG, breite Unterseite unten | 45°-Profilflanken; zugängliche lokale Stützen für horizontale Stabsockel und Sensorentlastung prüfen. |
| Schlitten P04 | PETG, Unterseite unten, Mulde oben | Führungsdecke spannt33,5 mm, im entlasteten Mittelbereich36 mm. Lokale entnehmbare Stützen oder qualifizierte Brückeneinstellung nötig; Zugang durch die offenen Kanalenden. Ø8-mm-Stabpassagen frei halten. |
| Federjoch P05 | PETG, montierte Unterseite unten | Zugängliche Stützen unter verstärkter Rippe und Sensor-/Kabelausnehmung; Ø6,6-mm-Stablöcher nacharbeiten, Druckfläche zentrisch belassen. |
| Handballenauflage P02 | PETG, flache Platte und Ohren unten | Lokale Stützen unter rundem Kern; M4-Kopfzugänge frei halten. |
| Hintere Halter P060/P061 | PETG, flache Unterseite unten | Kleine horizontale Sacklöcher ggf. stützen und aufØ6,2 nacharbeiten. |
| Manschette P03 | TPU, etwa95A als Startpunkt, auf einem Ende stehend | Naht von Kontaktfläche weg; Härte und Sitz am Muster prüfen. |
| Rücklaufpuffer P07… | TPU, breite4,5 ×6-mm-Fläche unten | 1,5 mm dick; mit dünnem kompatiblem Klebefilm sichern. |

Die Grundplatte braucht156 ×180 mm nutzbare Druckfläche, der Schlitten etwa60 ×174 mm. Beide passen ohne Skalierung auf220 ×220 mm; Platz für Haftungsrand im Slicer prüfen. Das Mittelprofil und die offenen Rahmenfenster müssen frei bleiben.

PETG ist eine praktikable Prototypwahl; Brücken und Stützen erfordern eine passende Einstellung. Siehe [Prusa PETG](https://help.prusa3d.com/article/petg_2059?product=mini) und [Brückendruck](https://help.prusa3d.com/article/poor-bridging_1802?product=mk3-5). Der Werkstoff allein legt keine zulässige Last fest.

Als Startpunkt0,4- oder0,6-mm-Düse,0,2-mm-Schichten und ungefähr3 mm tragende Wandbereiche verwenden. Den 2,7-mm-Boden über dem Führungskanal, Joch, Anschlagblöcke und Gewindeeinsatzbereiche lokal voll drucken. Druckpfade und Stützentfernung im Slicer ansehen. Diese Einstellungen sind kein qualifizierter Fertigungsprozess.

R4-Fingerkante, Muldenübergänge und Nahtstellen glätten. Griff und TPU-Auflage zuerst ohne Federn anfassen und bewegen. Der einstellbare M3-Nocken bestimmt den Klickpunkt unabhängig vom mechanischen Anschlag.

Für Tischmontage dieØ5,5-mm-Piloten nach dem Druck passend zu bündigen Senkschrauben ansenken; Köpfe höchstens bisZ4. Löcher beiX−15/Y±30 undX127/Y±50. Vor allem hinten können hervorstehende Köpfe den Rücklauf behindern.

## Am Muster prüfen

Zuerst ohne Federn den vollständigen30-mm-Hub prüfen, dann mit niedriger Last: Rücklauf, Reibung bei mittigem und einseitigem Fingerzug, Verdrehspiel und Messsignal. Besondere Prüfpunkte sind die einzelne gedruckte Führung, der2,7-mm-Muldenboden, der4-mm-Grundrahmen und die auskragenden Auflagenohren. Die rechnerische Federkraft ist keine experimentell bestätigte Traglast. Den nutzbaren Kraftbereich für den tatsächlichen Druck durch Versuche bestimmen.
