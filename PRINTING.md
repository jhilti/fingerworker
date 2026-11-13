<!-- CURRENT_FLAT132_R20_START -->
> **13.11.2026 – Flat132 R20: integrierte Positionierzapfen.** P06L/P06R erhalten je einenØ5×2-mm-Unterseitenzapfen; P01 passende hinten offene Sacknuten. So bleibt das axiale Aufschieben auf die Stangen möglich. Schraubenlos nur federfrei und unbelastet positionieren. **Vier M3×8 sind vor Federkraft, auch vor Vorspannung in Ruhestellung, erforderlich.** [Onshape R20](https://cad.onshape.com/documents/15316cc6370631845af136b2/v/0e06e3d98b9ecb574ee41402/e/d253eb87b70818ebde8215f0) · [Native STEP](review/rear-locating-pegs-2026-11-13/native/Flat132_R20_final_AP214.step) · [Review](review/rear-locating-pegs-2026-11-13/README.md) · [Montage](review/rear-locating-pegs-2026-11-13/MONTAGE.md).

> **Druckvorbereitung auf Nutzerwunsch zurückgestellt (PRINT_SETUP_DEFERRED_BY_USER).** Kein neues Bambu-Projekt, kein neuer Slice oder Druckauftrag. Native R20-CAD-Prüfung:94 Körper,91 gegenüberR19 geometrisch unverändert. Frühere Druckpakete enthalten diese neuen Zapfen/Nuten nicht.
<!-- CURRENT_FLAT132_R20_END -->

<!-- CONNECTED_R15_READY_START -->
> **Historischer Stand R15 – für R20 den CAD-Stand oben beachten; Druckvorbereitung zurückgestellt.** Vorbereitungsnachweis vom 08.11.2026: [PLA-Basic-Projekt](print/bambu-R15-inboard-straps-2026-11-08/Fingerworker_R15_H2D_04mm_PLA_Basic_Print_Ready.3mf) · [Print-Ready-Paket](print/bambu-R15-inboard-straps-2026-11-08/Fingerworker_R15_H2D_04mm_PLA_Basic_Print_Ready_Package.zip). Sechs Teile auf einer Platte, alle ohne Brim, erforderliche PLA-Stützen erhalten. Linke 0,4-mm-Standarddüse, Bambu PLA Basic damals aus AMS A3; kein PETG. GUI-Schätzung **10 h 49 min / 233,58 g**. Sendedialog geprüft, **kein Druckauftrag gestartet**. [Nachweise](print/bambu-R15-inboard-straps-2026-11-08/connected-ready-delivery.json). Die damalige Generic-PLA-Variante bleibt als historische Ausgangsdatei erhalten. Die damalige AMS-Zuordnung ist keine Bestätigung für R18.
<!-- CONNECTED_R15_READY_END -->

# Aktueller Drucksatz Rev F - H2D, PETG

[3MF-Projekt](print/bambu-2026-10-13-RevF/Fingerworker_RevF_H2D_04mm_PETG.3mf) · [Komplettpaket](print/Fingerworker_H2D_PETG_RevF_2026-10-13.zip) · [Prüfbericht PDF](output/pdf/Fingerworker_Druckbarkeitspruefung_RevF_2026-10-13.pdf) · [Druckanleitung](print/bambu-2026-10-13-RevF/README.md) · [Montage](print/bambu-2026-10-13-RevF/MONTAGE.md)

Stand 13.10.2026: **25 Geräteteiltypen + zwei Passproben, 32 Exemplare auf sechs Platten**. Komplett PETG; H2D mit 0,4-mm-Standarddüsen angenommen. PLA nach Filamentprofilwechsel und erneutem Slicing möglich. Kein TPU und keine gedruckten Schrauben, Muttern, Inserts oder Scheiben.

Vollständige Druckbarkeitsprüfung: P04/P05 mit hinterer Stirnseite/Rippe unten, H12 seitlich und H02 aufrecht. P08 erhält erreichbare Stützen unter dem USB-Dach, hohe Halbschalen einen 8-mm-Brim, Kleinteile langsame Bahnen. P07 wird einzeln mit 0,10-mm-Schichten bis 1,50 mm gedruckt. Die vier Umorientierungen sind starr und verändern keine Nennmaße oder Montageanschlüsse. Die korrigierten Passproben aus Rev E bleiben unverändert.

Alle 32 Objekte mit direkter Erstschicht und vollständigen Modellbahnen geprüft; alle sechs Platten erfolgreich für den H2D geslict. Reale Bahnen bestätigen maximal 40 mm/s für kleine Teile, 60 mm/s für hohe Schalen/Hülsen und höchstens 1500 mm/s² Modellbeschleunigung. Schätzung **26 h 25 min / 372 g PETG** inklusive Stützen/Brims/Proben. [Prüfung je Teil](review/printability-2026-10-13/PRINTABILITY.md).

Die Grundplatte bleibt 6 mm dick, Seilhalter sind entfernt, hintere Sockel abgesenkt und P060/P061 durchgehend gebohrt. Funktions-CAD bleibt Rev C; aktuelle Drucklage und Einstellungen sind Rev F. **Zunächst federfrei montieren.** Stützen vor Einbau entfernen; P04s neue Lagenrichtung ist für die Formbeurteilung gewählt und ersetzt keine spätere Festigkeitsprüfung. Reale Passung/Haftung/Supportablösung am gedruckten Muster prüfen.

Die folgenden Grundmaße und TPU-Hinweise sind historisch. Für den aktuellen Erstaufbau gelten die oben verlinkten Rev-F-Dateien.

---

# Druckhinweise — kompakte Mittelführung

> Druckzuordnung vom 11.10.2026: [REVISION_STATUS](print/REVISION_STATUS.md). Der mechanische Drucksatz vom 29.09.2026 enthält die Seilaugen; die Federrevision ändert keine Druckteildefinitionen. Die folgenden Grundmaße sind historisch.

> **Aktueller Vollreview vom 21.09.2026:** [FULL_REVIEW.md](FULL_REVIEW.md). Die folgenden historischen Grundmaße bleiben als Kontext erhalten. Aktuelle Sensorhalterung, Befestigungen und Elektroniklage stehen im Vollreview und in DEVICE_UPGRADES.md.

> **Neuer lokaler Entwicklungsstand:** Leichtes Federpaar, gemeinsame Vorspannung und sensorverträgliche Isometrie-Hülsen sind in `fingerworker_mvp.fs` ergänzt. Details und offene Fertigungsfreigabe: [DEVICE_UPGRADES.md](DEVICE_UPGRADES.md). Die folgenden Maße, Stücklisten, Onshape-Prüfungen und Druckpakete beschreiben den vorherigen Stand; sie sind keine Validierung dieser Ergänzungen.

Revision 20. September 2026. Grundrahmen, Schlitten, Federjoch und Stäbe gehören zur neuen kompakten Ausführung. Vorherige Druckteile nicht als passenden Satz mischen. Gesamtmaß178,25 ×180 ×30 mm; separate Grundplatte156 ×180 mm.

Nur die elf mit `P… PRINT` benannten Körper drucken. `H…` und die optionale Hand sind Referenzgeometrie. Export in Millimetern, 100 %, Hub0 mm und Hand aus.

`print/Fingerworker_30mm_print_pack.zip` enthält die elf STL-Dateien, zwei Passproben und diese Hinweise. Die Geräteteile stammen aus Onshape, Auflösung Fine. Die Netze werden auf geschlossene Kanten und positives Volumen geprüft und starr auf Z0 gesetzt. Manschette und Puffer sind bereits in die unten genannte Orientierung gedreht. Keine Skalierung oder Formkorrektur. Der ursprüngliche Download bleibt als `print/Fingerworker_30mm_Onshape_original.zip` erhalten.

## Führungsprobe zuerst

`guide_coupon_male.stl` mit dem Sockel unten und die seit Rev E korrigierte `guide_coupon_female.stl` mit der geschlossenen Rückseite unten (Kanal oben) drucken. Zum Zusammenstecken die weibliche Probe anschließend umdrehen. Die 30 mm langen Proben bilden das neue 32-mm-Mittelprofil ab: 45°-Flanken, 0,30 mm Deckenspiel und 0,45 mm horizontaler Flankenversatz. Die weibliche Probe hat dieselbe 2,7-mm-Deckendicke wie der Muldenboden über der Führung. Im zusammengeschobenen Zustand liegt ihre Unterseite4 mm über der Unterseite der männlichen Probe.

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
