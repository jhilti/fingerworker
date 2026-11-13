"""Required startup correction for the pinned Seeed core (only this local installation)."""
from pathlib import Path
path = Path('/tmp/fingerworker-arduino/data/packages/Seeeduino/hardware/nrf52/1.1.13/variants/Seeed_XIAO_nRF52840/variant.cpp')
s = path.read_text()
old = '    pinMode(VBAT_ENABLE, OUTPUT);\n    digitalWrite(VBAT_ENABLE, HIGH);'
new = '    digitalWrite(VBAT_ENABLE, LOW);\n    pinMode(VBAT_ENABLE, OUTPUT); // Fingerworker Rev A: never drive P0.14 HIGH'
if old in s:
    path.write_text(s.replace(old, new).replace('// Disable reading of the BAT voltage.', '// Fingerworker: enable battery voltage reading with LOW.'))
elif new not in s:
    raise SystemExit('Unexpected Seeed core: review startup before building')
print('Seeed 1.1.13 battery-divider startup verified LOW')
