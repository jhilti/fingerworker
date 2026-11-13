"""Generate the original 35 ms mono PCM click bundled with the iPhone app."""
import math
from pathlib import Path
import struct
import wave

rate = 44_100
duration = 0.035
frames = []
for index in range(round(rate * duration)):
    t = index / rate
    envelope = min(1, t / 0.001) * math.exp(-t / 0.005) * max(0, 1 - t / duration)
    signal = 0.75 * math.sin(2 * math.pi * 1_800 * t) + 0.25 * math.sin(2 * math.pi * 3_100 * t)
    frames.append(struct.pack('<h', round(0.65 * 32_767 * envelope * signal)))
destination = Path(__file__).parent / 'Fingerworker/Resources/endstop-click.wav'
destination.parent.mkdir(parents=True, exist_ok=True)
with wave.open(str(destination), 'wb') as output:
    output.setparams((1, 2, rate, 0, 'NONE', 'not compressed'))
    output.writeframes(b''.join(frames))
