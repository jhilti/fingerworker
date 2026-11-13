> 13.10.2026: Die Seilaugen wurden auf Nutzerwunsch aus dem aktuellen Live-CAD entfernt, da sie die Montage des Schlittens blockieren. Diese Dokumentation und die September-Exporte sind historische Stände; nicht erneut für den aktuellen Druck verwenden.

# Hintere Seilaufnahmen — Entwicklungsstand 29.09.2026

> Standabgleich 11.10.2026: Federreferenzen im CAD auf die bestellten Febrotec-Paare geändert. Die folgenden acht CAD-Konfigurationen belegen weiterhin den Quellstand vom 29.09.; neue Prüfungen stehen unter [STATUS](review/software-2026-10-11/STATUS.md).

Der feste Rahmen **P01** erhält zwei integrierte Aufnahmen für die bestätigte **6-mm-Reepschnur**. Damit kann der Rahmen an einem äußeren Gegenlager befestigt werden, während die Finger an der beweglichen Auflage ziehen. Die Handballenauflage bleibt für den bisherigen Betrieb verfügbar.

## Geometrie

- Zwei Augen hinten am festen Rahmen, symmetrisch bei Y = ±34 mm, jeweils 20 mm breit.
- Querbohrung Ø8,5 mm bei X = 140 mm / Z = 18 mm; die Zugabe dient dem Einfädeln einer 6-mm-Schnur.
- Bohrungsmündungen mit R1,5 mm, Außenprofil mit R2 mm gerundet.
- P01 wächst von 156 auf **172 × 180 × 29 mm**. Die gesamte Mechanik misst nun **194,25 × 180 × 30 mm**; die Gesamthöhe bleibt 30 mm. Die beiden lokalen Augen ersetzen keine durchgehende zusätzliche Platte.
- Die vorhandenen Befestigungsbohrungen bleiben erhalten. Die erhöhte Geometrie beginnt bei X = 126 mm, hinter dem offenen Schlittenende X = 124 mm.

Die aktuelle Quelle wurde in Onshape regeneriert und für den neuen Drucksatz exportiert. Die Prüfungen vom 21.09.2026 bleiben dem damaligen Stand ohne Seilaugen zugeordnet.

![Onshape-Modell mit hinteren Seilaugen und 6-mm-Schnurreferenz](review/rear-tether-2026-09-29/Onshape_rear_tether.jpg)

Ansicht bei 15 mm Hub und 0 mm Zusatzvorspannung; Hand- und Elektronikreferenzen ausgeblendet.

## Abgeschlossene digitale Prüfung

Mit der leichten Federpaarung wurden acht Konfigurationen geprüft: 0/15/30 mm dynamischer Hub jeweils mit 0/2 mm Vorspannung sowie der isometrische Aufbau mit 0/2 mm Vorspannung. Hand-, Elektronik- und Schnurreferenzen waren dabei eingeblendet. **360 Gruppenprüfungen ergaben keine Volumenüberlagerung**. Bestehende beabsichtigte beziehungsweise nicht klassifizierte Kontakte behalten den Status „REVIEW“.

Der kleinste Abstand zwischen Seilaugen und Schlitten beträgt **2 mm**. Die vereinfachte 6-mm-Schnurreferenz hält mindestens **1 mm** zum festen Rahmen und **13 mm** zu den übrigen Teilen. Dies sind acht einzelne CAD-Stellungen, keine kontinuierliche Bewegungs-, Toleranz- oder Verformungsprüfung. Die illustrative Handreferenz belegt keine reale Handpassform.

Nachweise: [CAD-Prüfbericht](review/rear-tether-validation.json), [aufgezeichnete Onshape-Ergebnisse](review/onshape-rear-tether.json).

Der [neue Drucksatz](print/rear-tether-2026-09-29/README.md) enthält elf geschlossene Netze mit positivem Volumen. Nur P01 ist geändert; die übrigen zehn STL-Dateien sind anhand ihrer Hashes identisch mit dem Stand vom 21.09.2026. Der Export erfolgte bei 0 mm Hub, 0 mm Vorspannung und ausgeblendeten Hand-, Elektronik- und Schnurreferenzen. Das geometrische Gesamtvolumen der Druckteile beträgt **376,552 cm³**, gegenüber 355,319 cm³ zuvor: **+5,98 %**. Der tatsächliche Filamentbedarf hängt von Wänden, Füllung und Stützmaterial ab.

Download: [Fingerworker_RearTether_2026-09-29.zip](print/Fingerworker_RearTether_2026-09-29.zip). [Netz-Prüfbericht](review/rear-tether-print-validation.json). Digitale Prüfung und Export sind abgeschlossen; Montage- und Belastungstests am gedruckten Prototyp bleiben offen.

## Einfädeln und Benutzung

Die Schnur mit einem freien Ende durch beide Aufnahmen führen beziehungsweise je eine Schnur durch jedes Auge. Die zum Baum laufenden Stränge müssen auf der Rückseite des Geräts bleiben und den Rahmen gleichmäßig nach hinten ziehen. Knoten und lose Enden gehören außerhalb des gesamten Bewegungsbereichs von Schlitten, Federn und Endschalter. Eine breite Bandschlinge am Baum kann als Gegenlager dienen; ihre Verbindung zur Reepschnur muss zum tatsächlichen Aufbau passen.

Beide Augen verwenden und möglichst gerade in Zugrichtung belasten. Stark schräge Stränge erhöhen die Schnurkräfte; ungleiche Längen und Reibung können ein Auge deutlich stärker belasten. Deshalb muss **jedes Auge für die volle vorgesehene Gerätezugkraft geprüft werden**, nicht lediglich für die Hälfte. Auch seitliches Kippen und Verdrehen sind im Belastungsversuch zu prüfen.

In Onshape zeigt **„Show 6 mm rear cord routing (reference only)“** einen vereinfachten Schnurverlauf. Diese Körper sind Referenzen und gehören nicht in den Druckexport. Sie bilden keine Knoten und keine verformbare echte Schnur ab.

## Kraftmessung

Der vorgesehene Kraftweg lautet:

**Fingerauflage P04 → Federn beziehungsweise isometrische Sperre → P05/Druckstift → Kraftsensor → fester Rahmen P01 → hintere Seilaufnahmen.**

Die Aufnahmen sitzen am festen Rahmen hinter dem Sensor. Die Schnur darf nicht am Schlitten, an P05, an den Führungsstangen oder an den abnehmbaren hinteren Haltern befestigt werden. Solche Befestigungen können den Messweg verändern oder umgehen.

Bei erreichtem mechanischem Endanschlag kann Kraft am Sensor vorbeilaufen; die Kraftdaten bleiben dann gemäß Firmwarevertrag ungültig. Vor Messungen im Seilaufbau neu nullen und die Anzeige mit einer bekannten äußeren Zuglast prüfen. Dass Führungsreibung und eine schräg eingeleitete Last die Abweichung verändern können, ist eine mechanische Schlussfolgerung; die Größe dieser Abweichung ist bisher nicht gemessen.

## Druck und noch offene Freigabe

P01 als ein zusammenhängendes Teil drucken. Die quer liegenden Bohrungen erfordern eine Prüfung der Überhänge im Slicer. Nach dem Druck tatsächlichen Durchlass, Rundungen und Innenflächen kontrollieren: Die Schnur muss frei einfädelbar sein und darf weder an Graten noch an rauen Übergängen scheuern. Nacharbeit darf die tragenden Stege nicht unnötig schwächen.

Die maximale Zugkraft, das Druckmaterial und der Druckprozess sind noch nicht festgelegt. Die Augen haben daher **keine Lastfreigabe**. Erforderlich sind Versuche am tatsächlich gedruckten P01 mit der verwendeten Schnur, einschließlich einseitiger Belastung, wiederholtem Zug, schräger Last und Kontrolle auf Risse sowie Schnurverschleiß. Die CAD-Kollisionsprüfung ersetzt diese Belastungsprüfung nicht.
