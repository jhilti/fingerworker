# R15 – Änderungsreview der innenliegenden Gurtaufnahme

<!-- RELEASE_STATUS_START -->
**Nominale R15-CAD- und PLA-Druckprüfung bestanden.** Native Geometrie, voller Hub, Sensorservice, Q01-Passung und tatsächliche Druckwege sind an diese Revision gebunden. Reale Passung, Haftung, Komfort und Belastbarkeit bleiben am Ausdruck zu prüfen.
<!-- RELEASE_STATUS_END -->

P01 verliert die vier äußeren R14-Laschen. Neue 27 × 4-mm-Schlitze bei X28/65 und Y±57,5 liegen auf beiden Seiten innerhalb der ursprünglichen 132-mm-Platte. Die Positionen werden gegenüber den bisherigen äußeren Ösen nach innen und axial verschoben, um den vollständigen Griffhub und die Federsitze freizuhalten. Ein nur seitliches Verschieben der R14-Schlitze wäre nicht ausreichend.

| Schnittstelle | R15 |
|---|---|
| Handballenauflage | R14-Form und Lage exakt erhalten |
| P04/P05/P06/P11, Sensorhardware, Stangen und Federn | Native Geometrie unverändert |
| P08/P09 und Servicezugänge | Weiter vorhanden, nicht Teil dieses Drucksatzes |
| Gurte | Zwei echte 25-mm-Bänder, höchstens 2 mm je Lage |
| Schlitze | Vier, 27 × 4 mm, innerhalb P01 |
| Boden | 6 mm; nur die Schlitze schneiden lokal hindurch, keine Gurtvertiefung |
| Verbleibender Steg außen / innen | Nominal 6,5 / 17,5 mm |
| Hauptboden / P01 / maximale Baugruppenbreite | 132 / 132,4 / 135,2 mm |
| Druck | Eine Platte, sechs Teile, alle ohne Brim; benötigte Stützen erhalten |

Die Öffnungen reduzieren lokal den Nettoquerschnitt der Seitenstreifen. Der neue Aufbau wird deshalb nicht als gleich fest wie der ungeschnittene R14-Boden bezeichnet. Im Projekt sind die Schlitzbereiche mit 100 % geradlinigem Infill vorgesehen. Der nominale Geometrie- und Drucknachweis bestätigt weder Zugkraft der Befestigung noch PLA-Kriechen oder Lebensdauer.

Die [Konstruktionsmaße](mechanics/design-specification.json), [native Geometrie](validation/native-geometry.json), [vollständige Bewegung](validation/native-motion.json), [Sensorservice](validation/service-native.json) und [Q01-Passung](validation/fixture-q01-check.json) sind an den finalen R15-Stand gebunden.

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
