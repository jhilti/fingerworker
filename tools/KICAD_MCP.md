# Seeed KiCad MCP Installation

Installiert am 11.10.2026 aus [Seeed Studio](https://github.com/Seeed-Studio/kicad-mcp-server), Commit `4085d3f98c97b23872cb05605afa8714bb26004a`.

Der globale Codex-MCP-Eintrag `kicad_seeed` startet `/bin/bash tools/run-kicad-mcp.sh` mit absolutem Projektpfad. Registrierung wurde mit `codex mcp get kicad_seeed` bestätigt. Der Server wurde in dieser Sitzung über MCP stdio initialisiert und mit 19 Werkzeugaufrufen geprüft. Eine bereits laufende Codex-Sitzung kann ihre integrierte Werkzeugliste erst beim nächsten Laden aktualisieren; die direkte MCP-Verbindung funktioniert bereits.

## Python und native PCB Daten

`tools/kicad-mcp-env` ist eine eigene Python-3.12-Umgebung. KiCad 10.0.6 enthält hier Python 3.9; dieses kann die aktuellen Seeed-Abhängigkeiten nicht ausführen. KiCad und seine Python-Installation wurden nicht verändert.

`seeed-mcp-launcher.py` lädt den Seeed-Server und ergänzt `get_native_pcb_review`. Diese nur lesende Abfrage startet `native-pcb-review.py` mit KiCads Python. Sie liefert genaue Konturmaße, Tracks, Vias, Padnetze, Masseflächen und geometrische Abstände. Die Platine wird nicht gespeichert. Leiterbahnlängen sind Summen aller Segmente eines Netzes; Abstände sind Luftlinien zwischen Padmitten.

Für PCB-Geometrie auf diesem Rechner `get_native_pcb_review` verwenden. Die ursprünglichen Seeed-PCB-Werkzeuge fallen auf einen Textparser zurück, der bei unserem KiCad-10-Projekt nur 309 statt 464 Segmente und falsche Platinenmaße erfasst. Seine SI-/PI-Heuristiken sind keine elektrische Freigabe. `get_schematic_info` erfasst nur das gewählte Blatt; das Root-Blatt enthält hier keine Bauteile. Die vollständige Netzliste ist für blattübergreifende Verbindungen maßgebend.

## Lokale Fehlerkorrekturen

Die lokale Seeed-Kopie hat Korrekturen in `tools/validation.py` und `tools/netlist.py`:

- ERC liest sowohl `violations` als auch `sheets[].violations`. KiCad 10.0.6 verwendet hier die zweite Form; upstream hätte vorhandene Verstöße übersehen.
- DRC wertet zusätzlich `unconnected_items` und `schematic_parity` aus, wenn der Bericht diese enthält. Die zusätzliche native Prüfung führt DRC ausdrücklich mit `--schematic-parity` aus.
- Die Netzverfolgung rendert die aktuelle Listenstruktur des Parsers korrekt und erhält mehrere Pins desselben Bauteils auf einem Netz, etwa U1-GND-Pins 13/18/20. Upstream brach die Verfolgung ganzer Bauteile mit einem Typfehler ab.

Patch: `kicad-mcp-local-fixes.patch`. Ein Upstream-Update muss diese Korrekturen berücksichtigen. Paketstände: `kicad-mcp-requirements.lock`.

## Erneut prüfen

Vom Projektverzeichnis:

```bash
tools/kicad-mcp-env/bin/python tools/test-kicad-report-parsing.py
tools/kicad-mcp-env/bin/python tools/seeed-review.py
```

Der erste Aufruf prüft gezielt, dass Verstöße in den tatsächlichen KiCad-10-Berichtsstrukturen erkannt werden. Der zweite führt echte MCP-Aufrufe aus und aktualisiert die Rohbelege unter `electronics/kicad/reports/seeed-review-2026-10-11/`. Die separaten JLC-Berichte müssen vor `audit-order-electronics.py` frisch mit KiCad exportiert werden; das Skript prüft deren Pin-/Padnetze, aktuelle PCB-Prüfsumme und BOM-Referenzen. Es führt ERC/DRC nicht selbst erneut aus.
