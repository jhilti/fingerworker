# Flat132 R15 – innenliegende Gurtschlitze, ohne Brims

<!-- RELEASE_STATUS_START -->
**Nominale R15-CAD- und PLA-Druckprüfung bestanden.** Native Geometrie, voller Hub, Sensorservice, Q01-Passung und tatsächliche Druckwege sind an diese Revision gebunden. Reale Passung, Haftung, Komfort und Belastbarkeit bleiben am Ausdruck zu prüfen.
<!-- RELEASE_STATUS_END -->

Vier **27 × 4-mm-Gurtschlitze auf beiden Seiten innerhalb der Grundplatte** ersetzen die äußeren R14-Laschen. Der Hauptboden ist 132 mm breit; P01 misst wegen bestehender Klickgegenhalter 132,4 mm; die vorhandenen hinteren Rastarme bestimmen die maximale Baugruppenbreite von 135,2 mm. Die integrierte griffnahe Handballenauflage bleibt unverändert.

**Gegenüber R14 nur P01 neu drucken.** Die übrigen 92 nativen Körper sind unverändert. Der mechanische Drucksatz enthält P01/P04/P05/P06/P11 und Q01 auf einer Platte. Vorhandene echte Stangen verwenden; Elektronikgehäuse und gedruckte Stangen entfallen.

Alle sechs Modelle drucken ohne Brim; erforderliche Stützen bleiben erhalten. Vier Wände, 20 % Gyroid, lokal 100 % an den Gurtstegen; PLA, H2D, 0,4-mm-Standarddüse. Tatsächlicher Slice: **10 h 59 min 19 s / 230.01 g PLA**. P11 bei der ersten Schicht kurz auf Haftung beobachten.

[Onshape R15](https://cad.onshape.com/documents/15316cc6370631845af136b2/v/e8453217d87e9cfdc9a33f65/e/d253eb87b70818ebde8215f0) · [Bambu-Projekt](../../print/bambu-R15-inboard-straps-2026-11-08/Fingerworker_R15_H2D_04mm_PLA_Inboard_Straps.3mf) · [Druckpaket](../../print/bambu-R15-inboard-straps-2026-11-08/Fingerworker_R15_H2D_04mm_PLA_Inboard_Straps_Package.zip) · [Übersicht](../../Uebersicht.html)

[Montage](MONTAGE.md) · [Review](parts-review.md) · [Stückliste](BOM_Aenderungen.csv) · [Maße](mechanics/design-specification.json) · [Finale Spezifikation](final-specification.json)

<!-- STRAP_ROUTING_START -->
## Befestigung mit zwei Gurten

Die vier gerundeten **27 × 4-mm-Öffnungen liegen in der Grundplatte**, symmetrisch bei **Y±57,5 mm**. Die äußeren R14-Laschen entfallen vollständig. Der Hauptboden bleibt **132 mm breit**; vorhandene Klickgegenhalter ergeben **132,4 mm P01-Außenmaß**. Die zwei Gurtpositionen bei **X28 und X65 mm** liegen **37 mm auseinander**. Sie sind so angeordnet, dass die Bänder die Federsitze und den Griff auch am Ende seines 30-mm-Hubs freilassen.

Der native Bewegungsnachweis ergibt für eine einzelne 2-mm-Gurtlage mindestens **2,26 mm Abstand zu den bewegten Federsitzen** und **3,5 mm zur hinteren Griffbrücke**. Keine doppelte Gurtlage über den Steg legen; die Rückfaltung gehört außerhalb der Platte. Der Abstand der Gurtpositionen sinkt von 75 auf 37 mm. Dadurch nimmt ihre geometrische Abstützung gegen Verdrehen ab; den sicheren Sitz am tatsächlichen Gegenstand beim Passaufbau beurteilen.

Die Schlitze durchtrennen lokal den 6-mm-Boden. Es gibt keine flächige Bodenvertiefung und keine neue dünne Gurtbrücke. Neben jedem Schlitz bleiben nominal **6,5 mm äußerer Steg** und **17,5 mm innerer Restquerschnitt** bis zur vorhandenen Rahmenöffnung. Diese Maße und die lokale massive Füllung sind keine geprüfte Tragfähigkeitsangabe.

Benötigt werden **zwei echte 25-mm-Gurte**, höchstens **2 mm dick** im Durchlass. Die beiden Enden jedes Gurts müssen sich nach außen zurückfalten und sicher am eigenen Gurt befestigen lassen. Die Länge richtet sich nach dem Gegenstand oder Oberschenkelumfang plus beiden Rückfaltungen. Gurte werden nicht gedruckt. Die vier Schlitzbereiche und ihre tragenden Stege werden lokal mit 100 % geradlinigem Infill gedruckt; der übrige P01 bleibt bei 20 % Gyroid. Die Modifikatoren sind Einstellungen im 3MF, keine zusätzlichen Teile.

1. Den langen Gurt unten um den Gegenstand führen. Je ein Ende von unten durch die linke beziehungsweise rechte Öffnung derselben X-Position nach oben stecken.
2. Jedes Ende direkt über den **äußeren Plattensteg** und dann außerhalb der Plattenkante nach unten zurückführen. Die doppelte Lage bleibt außen; im Durchlass liegt nur eine Lage.
3. Beide Enden sicher am eigenen Gurt befestigen. Keine Gurtstrecke quer über Griff oder Federn führen. Den zweiten Gurt an der anderen Position genauso montieren.

![Gurtführung am nativen Schnitt der Grundplatte](evidence/strap-routing.svg)

Die Abbildung zeigt die echte Rahmenkontur; Gurt und Gegenstand sind schematisch. Vor der ersten belasteten Nutzung zunächst federfrei den Sitz, vollen Hub und die sichere Endbefestigung prüfen. Für Demontage und Elektronikservice die Gurte abnehmen. Reale Gurtpassung, Druckfestigkeit, Rutschfestigkeit und Dauerverhalten sind noch zu prüfen.
<!-- STRAP_ROUTING_END -->

Q01 nur federfrei einsetzen und vor Sensor-/Federeinbau entfernen. Clips dienen der Montage; die vorgesehenen Sicherungsschrauben bleiben für Federlast erforderlich. Kein Druckauftrag wurde gestartet.
