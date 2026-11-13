# R10 – Druckprüfung

**Bestanden:** 18 native Meshes, zwei vollständig geslicte Platten. H2D · 0,4 mm · PLA · strukturierte PEI-Platte · 100 %.

Slicer-Schätzung einschließlich Stützen und Brims: **17 h 56 min / 266 g PLA**. Nur das neue P01 auf Platte 1: **8 h 16 min / 131 g PLA**. Vorhandene R9-Restteile können weiterverwendet werden.

P01 bleibt bodenflach; die Stützen unter dem äußeren Handballenüberhang sind über die Handgelenkseite/Unterseite erreichbar. Die zentrale Serviceausnehmung bleibt von unten offen. Ein erfolgreicher Vergleichsslice mit Handgelenkseite unten benötigt 9 h 20 min / 154 g und erzeugt 175 mm Bauhöhe bei nur 186 mm² ebener Bettauflage. Die ausgelieferte flache Lage benötigt 8 h 16 min / 131 g, bleibt 35 mm hoch und hat rund 17104 mm² ebene Bettauflage. Der alternative Kandidat wird nicht mitgeliefert.

Die restlichen 17 Stücke übernehmen die unveränderten R9-Quellmeshes, Drucklagen und individuellen Einstellungen. Alle Objekte besitzen tatsächliche Extrusionsbahnen ab der ersten Schicht und erreichen ihre Höhe; die vier P07-Dummies enden bei exakt 1,50 mm.

Die 3MF-Rückprüfung bestätigt Maßstab 1:1, geschlossene Volumen, starre Transformationen, maximal 0,0001 mm Vertexabweichung und keine automatischen Meshreparaturen. Tatsächliche Modell-/Stütz-/Brimbahnen bleiben im gemeinsam nutzbaren H2D-Bettbereich; die Bahnhüllen der Teile auf Platte 2 überschneiden sich nicht. Lokalisiertes Stützmaterial wurde unter Palm, USB-Dach, Fingerraum, Joch und hinteren Schuhverbindern geprüft; die geschlossenen hinteren Zungenführungen enthalten keine eingeschlossenen Stützen.

Offizielle Bambu Studio 02.08.02.61, originale H2D-Maschinenmakros unverändert. Die bekannten lokalen Parserdiagnosen T1001/T65535/T65279 aus diesen Makros verhindern die beiden erfolgreichen Slices nicht. Es wurde kein Druckauftrag übertragen. Das Lieferprojekt enthält keine Gcode-Datei.

CAD-Quellhash: `5ce830ff2b06cd8d318d3c44dbc1f3385697526a9a679d2a2078f64f81854237`. Native Onshape-Version: `1d91807cca19866934a439eb`. Die einzelnen Prüfberichte binden Quellhash, Projekt und internes Slice-Artefakt.

Die Prüfung bewertet Geometrie und Werkzeugwege. Die reale Entfernung der Stützen, Passung und Festigkeit sind am unbelasteten Druckteil zu bestätigen. Infill ist keine Festigkeitsfreigabe; Q01, die gedruckten Stangen und harten Pads ersetzen die belasteten Funktionsteile nicht.
