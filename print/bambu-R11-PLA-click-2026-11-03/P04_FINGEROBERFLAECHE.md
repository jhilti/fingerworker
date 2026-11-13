# P04: saubere Fingeroberfläche mit PLA

**Platte 3 drucken.** Der Griff steht auf seiner vorderen Stirnseite. Die Fingerzugwand zeigt nach oben, der Muldenboden steht senkrecht. Die separate Platte erhält die geprüfte Baumstützenanordnung.

Voreingestellt: H2D, angenommene Standarddüse 0,4 mm, PLA, Schichthöhe 0,2 mm, 5 mm Außenbrim. Stützen: **Baum automatisch, schlank, nur vom Druckbett**, oberer Z-Abstand 0,25 mm. PLA allein genügt; für diese Verbesserung ist kein zweites Filament nötig.

Die ursprüngliche Drucklage stellte die Fingerzugwand als Unterseite über Stützen her. Die neue Lage vermeidet diese Spuren an der Zugfläche. Normale Stützen überall würden auf dieser Fläche starten und sie wieder beeinträchtigen; die vorbereiteten Bett-Baumstützen erreichen die gegenüberliegende Wand durch die große Öffnung.

Die Kontaktfläche bleibt Teil des vollständigen Griffs. Kein Sleeve, keine kleine Abdeckung und kein zusätzliches Teil. Die Konstruktionsgeometrie, die Führung, P05 und die Montageposition ändern sich durch die Druckrotation nicht.

Nach dem Druck:

1. Brim und äußere Stützen entfernen.
2. Baumstützen durch die große Muldenöffnung herauslösen. Auch die offene Cam-Schuh-Tasche freimachen. Dies vor dem Einsetzen in die Grundplatte erledigen.
3. Führung und beide Stangenbohrungen auf Stützreste prüfen.
4. Den Griff in normaler Montageausrichtung von hinten auf die Grundplatte schieben.

Die gegenüberliegende Muldenwand bleibt gestützt und kann dort Spuren zeigen. Die tatsächliche Oberfläche und die Entfernbarkeit der Stützen bestätigt der nächste Druck. Die neue Baulage verändert die Schichtebene gegenüber der bisherigen Stirnseitenlage nicht; eine Belastungsfreigabe ergibt sich daraus nicht.

Prüfbild: `preview/P04-Stuetzen.png`. Die graue Kontur ist der Mittelschnitt Y0; blaue Stützen sind eine Projektion aus |Y| < 28 mm. Eine Projektion vor der Kontur bedeutet keine Kollision, zum Beispiel beim wirklich ausgeschnittenen Schraubenkopfslot.

Der echte Werkzeugweg wird in `validation/p04-surface-check.json` geprüft. Der wiederverwendbare Prüfer liegt unter `source/check_p04_supports.py`. Er prüft die eigentliche Zugwand, den Boden, die vorderen Rundungen, die seitlichen Muldenradien, die zentrale Führung und die inneren Stangenbohrungen. Physische Oberflächenqualität bleibt eine Eigenschaft des realen Drucks.
