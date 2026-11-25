# Veröffentlichung und lokale Wiederherstellung

Öffentliches Repository: [jhilti/fingerworker](https://github.com/jhilti/fingerworker). Erster Veröffentlichungsstand: **v0.20.0-prototype**, mechanische Revision **Flat132 R20** vom 13.11.2026.

Die Veröffentlichung stellt Entwicklungsquellen und nachvollziehbare CAD-Prüfungen bereit. Sie ist keine Freigabe für Druck, Lastbetrieb oder klinische Anwendung.

## Entwicklungsstand R31 mit Rev‑E‑Elektronik

Die montierte R31-Federvariante mit Rev‑E‑Platine und den beiden Daumentastern ist im Entwicklungsnotizbuch und in Onshape dokumentiert. [Drehbare R31‑Rev‑E‑Ansicht](https://fingerworker-development-notebook.jonashilti.chatgpt.site/#cad-r31-rev-e) · [Vollständige Baugruppe in Onshape](https://cad.onshape.com/documents/15316cc6370631845af136b2/w/8b79384f95b34ba58197ab08/e/061a7997871e238371c40026)

## Inhalt und Ausnahmen

Im Repository stehen die eigenen CAD-Quellen, Firmware, iOS-App, Elektronikquellen, technische Dokumentation, kompakte Prüfergebnisse und die eigenständige 3D-Ansicht. Technische Quellen und historische Revisionsberichte bleiben erhalten, soweit sie nicht zu Studien mit persönlichen Referenzdaten gehören.

Ausgenommen sind persönliche Bestellungen und Korrespondenz, persönliche Scans und Referenzstudien, lokale Zugangsdaten und Benutzereinstellungen, virtuelle Umgebungen und temporäre Werkzeuge, separat beschaffte Hersteller-PDFs/-CAD sowie alte generierte Spiegelkopien, Cache-Dateien und G-Code. Diese Dateien werden durch die Veröffentlichung nicht aus dem lokalen Arbeitsbestand gelöscht.

Historische Berichte können auf solche lokal vorhandenen Dateien oder auf frühere, hier nicht veröffentlichte Druckpakete verweisen. Diese Links sind Entwicklungsnachweise und kein Versprechen, dass jede historische Datei Bestandteil des öffentlichen Downloads ist. Historische Druckarchive werden gesondert als Archiv gekennzeichnet und gelten nur für ihre damalige Revision. Herstellerunterlagen sind bei Bedarf aus der jeweiligen Originalquelle zu beziehen.

## Native R20-CAD-Dateien

Die nativen CAD-Exporte sind Assets des [Release v0.20.0-prototype](https://github.com/jhilti/fingerworker/releases/tag/v0.20.0-prototype). Das STEP ist zusätzlich im Repository enthalten; das größere STL-ZIP gehört nicht zum automatisch erzeugten GitHub-Quellcode-ZIP.

| Release-Datei | Ursprünglicher Projektpfad |
| --- | --- |
| [Flat132_R20_neutral_final.zip](https://github.com/jhilti/fingerworker/releases/download/v0.20.0-prototype/Flat132_R20_neutral_final.zip) | `review/rear-locating-pegs-2026-11-13/native/Flat132_R20_neutral_final.zip` |
| [Flat132_R20_final_AP214.step](https://github.com/jhilti/fingerworker/releases/download/v0.20.0-prototype/Flat132_R20_final_AP214.step) | `review/rear-locating-pegs-2026-11-13/native/Flat132_R20_final_AP214.step` |

Im Repository-Verzeichnis ausführen, um das aktuelle R20-STL-ZIP an seinem ursprünglichen Pfad wiederherzustellen:

```sh
python3 tools/download_release_assets.py
```

Alternativ den Ordner `review/rear-locating-pegs-2026-11-13/native/` anlegen und den Download unter dem unveränderten Dateinamen dort ablegen. Das STL-ZIP **nicht entpacken oder neu komprimieren**: Die Modellwerkzeuge lesen das Originalarchiv und prüfen dessen SHA-256.

| Datei | Größe | SHA-256 |
| --- | ---: | --- |
| STL-ZIP | 58.580.146 Bytes | `702d1e2194bd5fc3d1d3d6e260b4ac289ffd66ea0702c957cdb15a33745908c5` |
| STEP | 2.498.398 Bytes | `b6ed578e66a00df5cc84b7e03d785c4235fa89457ac45a54cb75295b0806bec2` |

Maßgeblich sind die [unveränderliche Onshape-Version R20](https://cad.onshape.com/documents/15316cc6370631845af136b2/v/0e06e3d98b9ecb574ee41402/e/d253eb87b70818ebde8215f0) und die [lokale Prüfbindung](review/rear-locating-pegs-2026-11-13/final-specification.json). Die Baugruppe enthält 94 Körper einschließlich Referenzhardware. Der Export ist kein Bambu-Druckprojekt.

## Weitere Release-Downloads

| Asset | Inhalt und Status |
| --- | --- |
| [Fingerworker_R20_3D.zip](https://github.com/jhilti/fingerworker/releases/download/v0.20.0-prototype/Fingerworker_R20_3D.zip) | Eigenständige R20-HTML-Ansicht zum Entpacken und Weitergeben |
| [Historical_Bambu_Projects_through_R18.zip](https://github.com/jhilti/fingerworker/releases/download/v0.20.0-prototype/Historical_Bambu_Projects_through_R18.zip) | 24 bestehende 3MF-Dateien bis R18; ausschließlich historische Stände, **kein R20-Druckpaket** |
| [Historical_Mechanical_Drawings_RevA.zip](https://github.com/jhilti/fingerworker/releases/download/v0.20.0-prototype/Historical_Mechanical_Drawings_RevA.zip) | Historische Metallzeichnungen Rev A |
| [Electronics_RevA_Technical_Exports.zip](https://github.com/jhilti/fingerworker/releases/download/v0.20.0-prototype/Electronics_RevA_Technical_Exports.zip) | Technische Elektronikexporte Rev A; dokumentierter Entwicklungsstand, keine Fertigungsfreigabe |

Diese zusätzlichen Archive werden separat heruntergeladen. Der Download-Helfer stellt standardmäßig nur das aktuelle native R20-STL-ZIP wieder her.

## 3D-Ansicht teilen

Die öffentliche interaktive **R20-Ansicht** ist unter **[jhilti.github.io/fingerworker](https://jhilti.github.io/fingerworker/)** erreichbar. Diesen Link zum direkten Betrachten teilen.

[share/Fingerworker_R20_3D.html](share/Fingerworker_R20_3D.html) ist eine eigenständige Datei mit eingebettetem Modell. Herunterladen und in einem Browser öffnen; ein Webserver und eine Onshape-Anmeldung sind dafür nicht erforderlich. GitHub rendert die Datei auf der normalen Repository-Seite nicht als interaktive Website.

[Uebersicht.html](Uebersicht.html) ist die ausführlichere Projektübersicht mit relativen Dokumentverweisen. Sie wird am besten aus einem heruntergeladenen Repository geöffnet. Die Viewer-Bauwerkzeuge liegen unter `overview/model/` und `share/r19-viewer/`; der Verzeichnisname des wiederverwendbaren Share-Builders ist historisch. Aktuelle R20-Metadaten liegen unter `share/r20-viewer/`.

## Revisions- und Montagestatus

R20 ergänzt Positionierzapfen an beiden hinteren Haltern und passende offene Nuten in der Grundplatte. Schraubenloses Zusammenstecken ist ausschließlich für einen **federfreien, unbelasteten Passaufbau** vorgesehen. **Vier M3×8 in den vorgesehenen Inserts müssen vor jeder Federkraft einschließlich der Ruhestellungs-Vorspannung montiert sein.** Der Montageweg ist in [MONTAGE.md](review/rear-locating-pegs-2026-11-13/MONTAGE.md) beschrieben.

Die Druckvorbereitung bleibt auf Nutzerwunsch pausiert. Es gibt kein neues R20-Bambu-Projekt, keinen R20-Slice und keine daraus abgeleitete Druckfreigabe. PLA bleibt der vorgesehene Standard. Frühere Druckstände ersetzen die aktuellen R20-Dateien nicht.

Die nominale CAD-Prüfung bestätigt keine gedruckte Belastbarkeit. Druckpassung, reale Last, Komfort, Elektronik und Kalibrierung müssen am aufgebauten Prototyp geprüft werden; eine klinische Eignung ist nicht validiert.

## Lizenzstand

Für die eigenen Projektdateien wurde noch keine Open-Source-Lizenz gewählt. Deshalb wird keine Lizenzdatei ergänzt und aus der öffentlichen Sichtbarkeit kein allgemeines Nutzungsrecht abgeleitet. Drittbestandteile unterliegen ihren eigenen Bedingungen; die Ausnahmen oben vermeiden eine pauschale Weiterveröffentlichung lokal beschaffter Herstellerunterlagen.
