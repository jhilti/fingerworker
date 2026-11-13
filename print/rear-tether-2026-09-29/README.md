# Entwicklungs-Drucksatz — 29.09.2026

Elf Druckteile aus dem aktuellen Onshape-Modell mit zwei integrierten hinteren Seilaufnahmen für 6-mm-Reepschnur. Nur **P01_base.stl** ist geändert und misst **172 × 180 × 29 mm**; die übrigen zehn STL-Dateien sind anhand ihrer Hashes identisch mit dem Stand vom 21.09.2026.

[Drucksatz als ZIP](../Fingerworker_RearTether_2026-09-29.zip). Die Einzeldateien liegen in `parts/`.

Export: 0 mm Hub, 0 mm Zusatzvorspannung, leichte Federpaarung; Hand-, Elektronik- und Schnurreferenzen ausgeschaltet. Binäre STL in Millimetern, Qualität „Fine“. Metall-, Sensor- und Federteile gehören nicht zu diesem Drucksatz. Die Netze sind ausschließlich starr für den Druck orientiert, nicht skaliert oder repariert.

Alle elf Netze sind geschlossen und haben positives Volumen. Das geometrische Gesamtvolumen beträgt 376,552 cm³, entsprechend 5,98 % mehr als im bisherigen Satz. Der tatsächliche Filamentbedarf hängt von den Einstellungen im Slicer ab. Nachweise: [Drucknetz-Prüfung](../../review/rear-tether-print-validation.json), [CAD-Abstandsprüfung](../../review/rear-tether-validation.json).

**Entwicklungsprototyp ohne Lastfreigabe.** Bei P01 die quer liegenden Seilbohrungen im Slicer prüfen und nach dem Druck auf freien Durchlass sowie glatte, gerundete Kontaktflächen kontrollieren. Die reale Handpassform, Montage und Festigkeit sind noch nicht freigegeben. Zielkraft, Druckmaterial und Druckprozess bleiben festzulegen.

[Seilführung, Kraftweg und offene Belastungsprüfungen](../../REAR_TETHER.md). Die unveränderten mechanischen Umbauten und benötigten Stahlteile sind in [DEVICE_UPGRADES.md](../../DEVICE_UPGRADES.md) beschrieben. Die bisherigen Hinweise zur Druckorientierung und zu Führungsproben stehen in [PRINTING.md](../../PRINTING.md); dessen alte Maß- und Paketangaben sind historische Stände.
