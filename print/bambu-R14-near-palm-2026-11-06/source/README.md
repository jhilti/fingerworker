# R14-Druckprojekt reproduzieren

`build_project.py` ersetzt P01 durch die freigegebene native R14-STL. P04, P05,
P06, P11 und Q01, ihre Drucklagen sowie die geprüften PLA-Prozesswerte stammen
aus dem eingefrorenen R13-Projekt mit sechs Teilen. Der Prozessname wird auf R14
aktualisiert; Maschinenmakros und Materialgrenzen bleiben identisch.

Die Pfade in diesen Skripten beziehen sich auf das vollständige Projektarchiv im
Fingerworker-Arbeitsverzeichnis. Sie sind keine Befehle zum Starten eines Druckers.

1. `build_project.py --source-cad <R14-FeatureScript> --version <Onshape-Version> --solid-strap-eyes`
2. `run_slicer.py import`, danach `run_slicer.py slice` mit der festgelegten
   offiziellen Bambu-Studio-CLI.
3. `validate_project.py`, `audit_toolpaths.py`, `check_print_features.py`,
   `check_palm_supports.py`, `check_one_plate_p04.py` und
   `check_cli_diagnostics.py` prüfen das tatsächliche neue Ergebnis.
   `check_strap_slots.py` prüft die offenen Gurtkanäle und die lokale Füllung;
   `check_strap_routing.py` prüft die endlichen Gurtumschläge gegen die bewegten Teile.
4. `render_support_evidence.py` erstellt die P04-Abbildung aus den zugeordneten
   Stützbahnen des neuen Slices.

Jeder abschließende Bericht bindet die geprüften Dateien über SHA-256. Die native
STL wird weder repariert noch skaliert. Ein ausdrücklich markierter lokaler
OCC-Kandidat darf ausschließlich mathematisch flächenlose Dreiecke verwerfen;
diese Ausnahme gilt nicht für die endgültige native Datei.

Vier reine Parameterkörper unter P01 setzen die Gurtösen samt kurzem
Grundplattenanschluss auf 100% geradlinige Füllung. Sie sind keine zusätzlichen Druckteile
und erscheinen nicht als druckbare STL-Dateien. Das 3MF speichert sie als
`modifier_part` mit teilbezogener `sparse_infill_density`, wie im
[Bambu-3MF-Exporter](https://github.com/bambulab/BambuStudio/blob/master/src/libslic3r/Format/bbs_3mf.cpp)
und in der [Typzuordnung](https://github.com/bambulab/BambuStudio/blob/master/src/libslic3r/Model.cpp)
definiert. Der offizielle lokale Import und die ausgegebenen Bahnen prüfen die
Unterstützung durch die tatsächlich verwendete Version.

Der sparse-Infill-Wert für die im Dialog als „Rectilinear“ bezeichnete Füllung
heißt im [offiziellen Konfigurationsschema](https://github.com/bambulab/BambuStudio/blob/master/src/libslic3r/PrintConfig.cpp)
`zig-zag`. Der Import muss diesen Wert und die vier lokalen 100%-Werte erhalten.
Zusätzlich prüft jede innere Schicht die tatsächlichen Extrusionsbahnen in den
tragenden Außenstegen und Anschlüssen. Die reine Angabe „100%“ reicht als Nachweis
nicht aus.

Die Prüfungen bestätigen digitale Geometrie, Drucklage und Werkzeugwege. Sie
ersetzen keine gedruckte Pass-, Festigkeits- oder Ermüdungsprüfung.
