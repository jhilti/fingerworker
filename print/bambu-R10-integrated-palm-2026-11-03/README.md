# Fingerworker R10 – integrierte Handballenauflage

Öffne **Fingerworker_R10_H2D_04mm_PLA_Fit_Test.3mf** in Bambu Studio. Das Projekt enthält **18 Teile auf zwei Platten**, in Millimetern und bei 100 % Maßstab.

Sind die übrigen R9-Teile bereits gedruckt, genügt **Platte 1** als Ersatz für die bisher getrennten P01/P02. Platte 2 dient dem vollständigen Neudruck.

- **Platte 1:** P01, Grundkörper und Handballenauflage als ein durchgängiges Druckteil. Die bisherige P02-Auflage, Sleeves und ihre zwei M4-Befestigungen entfallen.
- **Platte 2:** 17 übrige Teile in den geprüften R9-Drucklagen. Enthalten sind vier harte P07-Pad-Dummies, zwei gedruckte Führungsstangen-Dummies und Q01 für die unbelastete Passprobe. Schrauben, Muttern und Inserts werden nicht gedruckt.

Voreingestellt sind **Bambu H2D, 0,4-mm-Düse, Generic PLA, strukturierte PEI-Platte**, 0,20-mm-Schichten, vier Wände und 30 % Gyroid. Dünne P07-Dummies und P11 verwenden 0,10-mm-Schichten; ausgewählte kleine Teile sind voll gefüllt. Die gespeicherten Lagen und individuellen Stützeinstellungen beibehalten. Für PETG in Bambu Studio das tatsächliche Filamentprofil wählen und erneut slicen.

P01 liegt mit seiner ebenen Bodenfläche auf dem Bett. Stützen unter dem Handballenbereich abschnittweise über die offene Unterseite und die äußere Handgelenkseite lösen. Am gerundeten Grundplattenrand zunächst nach außen zum Handgelenk lösen, dann nach unten abnehmen. Stützreste an Führungen und Servicezugang sorgfältig beseitigen, ohne Passflächen abzuschleifen. Die zwei seitlichen H18-Werkzeugkanäle sind mit kurzen Bohrungsbrücken und ohne eingeschlossene Stützen vorbereitet. Die Handballenauflage wird nach dem Druck nicht mehr angeschraubt oder überzogen.

Die aktuelle Druckzeit, Materialmenge und Prüfbindung stehen in [PRINT_QA_NOTES.md](PRINT_QA_NOTES.md); die Montage in [FIT_TEST_README.md](FIT_TEST_README.md). Das native Projekt bleibt editierbar und enthält keine vorbereiteten Druckaufträge. Es wurde lokal geslict; kein Auftrag wurde an den Drucker geschickt.

[MONTAGE.md](MONTAGE.md) beschreibt außerdem den späteren inneren Service bei festem Handballenbereich, einschließlich der revidierten H15-/H16-Befestigung und der neuen H18-Zugänge. [BOM_Aenderungen.csv](BOM_Aenderungen.csv) listet die entfallenen Palm-Befestigungen und die übernommenen Teile auf.

**STL-print-oriented/** enthält die 18 Einzel-STLs in Drucklage. **source-mm/** bewahrt die exakten nativen Eingangsmeshes; sie stehen in Montagekoordinaten. **profiles/** und **source/** enthalten Profile und Reproduktionsskripte; die Skripte verwenden die eingefrorenen CAD-Quellen im Repository. Die 3MF-Datei selbst ist vollständig und benötigt keine externen STL-Dateien.

Die Passprobe erfolgt ohne Federn und ohne Sensor-/Vorspannstapel. Q01 und gedruckte Führungsstangen dienen nur dem unterstützten, unbelasteten Handversuch. Physische Passung, erfolgreiche Stützentfernung und Festigkeit sind erst am Druckteil zu bestätigen.
