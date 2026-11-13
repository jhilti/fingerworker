# Elektronik-Bauraumprobe unter der Handballenauflage

20. September 2026. Status: Referenzkörper für eine Einbaustudie; keine druckfertige Elektronikaufnahme. Der anschließende Schaltungsentwurf Rev A ist unter [electronics/README.md](electronics/README.md) dokumentiert. Die Referenzkörper wurden dabei nicht verändert.

**Neu aus der Bauteilauswahl:** Der JST-PH-Stecker samt Kabelabgang braucht ein größeres Montagebudget als E04 (vorläufig 10 × 12 × 5,5 mm statt 8 × 6 × 4,5 mm); der seitliche Bedientaster fehlt noch im Modell. Beide müssen mit den tatsächlichen Footprints/Hüllkörpern eingebaut werden. Die unten dokumentierten Kollisionsprüfungen gelten für die bisherige Bauraumstudie, nicht bereits für die vollständige Elektronik Rev A.

Im Onshape-Feature `FingerworkerMVP` gibt es die Option **Show electronics packaging study (not manufacturing)**. Sie ergänzt sieben farbige, mit `REF E…` bezeichnete Körper. Sie gehören nicht in den mechanischen STL-Druckexport. Das bestehende Druckpaket bleibt der Mechanikstand vor dieser optionalen Studie.

## Belegung

| Körper | Aufgabe | Abmessung / Maßstatus |
|---|---|---|
| E00, transparent cyan | Gehäusebauraum unter der festen Auflage | 22 × 110 × 8,5 mm; 1-mm-Wände/-Boden, 0,8-mm-Deckenbudget, USB-Durchbruch; Befestigung noch offen |
| E01, dunkelgrün | Eigene Trägerplatine | Zielgröße19 ×68,5 ×0,8 mm; noch kein geroutetes PCB |
| E02, blau | XIAO nRF52840 | Hersteller-Grundfläche17,8 ×21 mm; 5 mm Bauhöhe als Planungsreserve, kein Hersteller-STEP |
| E03, grün | ADS1220, Filter und 5-V-Versorgung | Gemeinsames Layoutbudget19 ×27,5 ×4 mm; keine zugesicherte Fertigmodulgröße |
| E04, hell | Akku-Steckverbinder | Reserve8 ×6 ×4,5 mm; konkrete Buchse noch festzulegen |
| E05, gelb | Geschützter100-mAh-LiPo | Nominaler Zellkörper11,5 ×31 ×3,8 mm; Kabel nicht als feste Zellabmessung behandelt |
| E06, transparent violett | USB-Steckerzugang von der Seite | Freiraum11 ×20 ×4,9 mm; nur Steckerkopf/Anfahrweg, kein Kabel-Biegeradiusnachweis |

Das Gehäuse liegt bei X−44,1…−22,1 / Y±55 / Z0…8,5. Die unveränderte tragende Auflagenplatte beginnt bei Z9,5. Die Studie hält damit1 mm nominalen Abstand zur Platte; gegenüber der Grundplatte bei X−22 bleiben0,1 mm. Diese kleinen Spalte dienen der räumlichen Machbarkeit und sind keine freigegebene Montagepassung. Befestigung und belastete Durchbiegung brauchen eine eigene Auslegung. Der Akku darf nicht als Anschlag oder Stütze dienen.

Die Platine liegt bei X−42,6…−23,6 / Y−53,5…15 / Z1,5…2,3. Unter dem BLE-Modul ist im späteren PCB ein zum Antennenlayout passender Kupfer-/Bauteilfreiraum vorzusehen. Zwischen dem BLE-Hüllkörper und der übrigen bestückten Zone sind12 mm frei. Dieser Abstand ist eine Platzreserve, keine RF-Freigabe; Hand, Akku, Kupferflächen, Leiterbahnen und nahe Hardware können die Antenne beeinflussen.

Der Akku liegt bei X−39,5…−28 / Y19…50 / Z1,5…5,3. Zum Platinenende sind4 mm frei; seitlich und oberhalb bleibt Raum für Leitung, weiche Lagerung und Zellmaßtoleranzen. Eine kurze Leitung mit Zugentlastung muss noch konstruiert werden. Die beispielhafte Zelle ist eine Größenreferenz; Laufzeit und Strombelastung entscheiden über die endgültige Auswahl.

## Quellen und Annahmen

- [Seeed XIAO nRF52840](https://wiki.seeedstudio.com/XIAO_BLE/): 21 ×17,8 mm, BLE, integrierte LiPo-Ladung. Ohne hohe Stiftleisten verwenden; Einbauhöhe einschließlich Lötung und USB am endgültigen Modell prüfen.
- [Adafruit100-mAh-Zelle,1570](https://www.adafruit.com/product/1570): 11,5 ×31 ×3,8 mm mit Schutzschaltung. Steckerpolarität und Ladestrom an die konkrete Zelle anpassen.
- [TI ADS1220](https://www.ti.com/product/ADS1220): Baustein für die Messplatine; vollständige Filter-, Referenz- und Versorgungsschaltung siehe Arbeitsvorschlag `BLUETOOTH.md`.

## Nächste Entwicklungsstufe

1. Schaltplan Rev A, Pin-/Netzliste und Stückliste sind erstellt. Arbeitsbudget: 10-20 mA aktiv, rechnerisch etwa 4-8 Stunden aus 80 mAh nutzbarer Kapazität. Standby-Ziel unter 100 µA. Ladestrom, Sensor-Gleichtakt, Rampen und Verbrauch müssen am Muster geprüft werden.
2. Reale Bauteile einschließlich Zellschutz, Steckverbinder und USB festlegen, danach das19 ×68,5-mm-PCB routen und tatsächliche 3D-Hüllkörper einsetzen. Hochfrequenz-/Analogbereiche und den Schaltwandler räumlich trennen.
3. Zugentlastung, Antennenfreiraum, isolierte Akkuablage und entnehmbare Aufnahme konstruieren. Die bestehende Handballenhalterung muss Kräfte aufnehmen, ohne die Zelle zu belasten.
4. Elektronik zunächst auf dem Tisch testen: Kalibrierung, BLE-Ausgabe, Endschalter, Rauschen, Stromaufnahme, Laden. Danach Einbau, Handhaltung und Rücklauf am gedruckten Muster prüfen.

Die exakten Onshape-Prüfungen bei0/15/30 mm mit Handreferenz ergeben jeweils28 geprüfte Körperpaare ohne Volumenüberschneidung. Alle sieben neuen Elektronik-Prüfpaare sind CLEAR. Die kleinsten Abstände betragen0,1 mm zwischen Gehäuse und Mechanik,0,4 mm zwischen Komponenten und Gehäuse,4 mm zwischen Akku und bestückter Trägerplatine sowie2,2 mm zwischen USB-Anfahrraum und Mechanik. Die Elektronikstudie hat6,17 mm Abstand zur illustrativen Hand. Berichte: `review/onshape-electronics-audit-*mm.txt`, zusammengefasst in `review/electronics-packaging-validation.json`.

Diese Studie verändert keine tragende Mechanik. Kollisionsprüfung bestätigt ausschließlich nominale Körperabstände; sie ersetzt keine elektrische Funktion, RF-Messung, Wärmeprüfung oder Festigkeitsprüfung. Drei Hubstellungen sind kein kontinuierlicher Kollisionsnachweis. Vor der Fertigung müssen insbesondere die knappen0,1/0,4-mm-Abstände und die belastete Durchbiegung neu ausgelegt werden.


## Native KiCad-Platzierung – 21.09.2026

Die reale Footprint-Platzierung liegt unter `electronics/kicad/`. Sie benötigt **19,5 × 68,5 × 0,8 mm** statt 19 mm Breite. 48 Footprints passen ohne gemeldete Courtyard-/Abstandsverletzung auf die Oberseite. Bei 20 mm CAD-Innenbreite bleiben nur 0,25 mm nominelles Spiel pro Seite. Es sind noch 102 Verbindungen ungeroutet. Der tatsächliche JST-Gegenstecker/Kabelabgang, die Betätigung des Seitentasters und vollständige 3D-Modelle bleiben abzugleichen. **Onshape und die früheren Kollisionsberichte wurden in diesem Schritt nicht verändert.** Dieser PCB-Stand ersetzt keinen vollständigen Gehäuse-Einbaunachweis.
