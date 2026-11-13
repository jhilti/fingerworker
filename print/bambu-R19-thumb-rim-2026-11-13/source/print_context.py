"""Paths for full-plate, local-candidate or three-part replacement validation runs."""
from pathlib import Path
import json,sys
OUT=Path(__file__).resolve().parents[1];ROOT=OUT.parents[1]
REPLACEMENT='--replacement' in sys.argv;CANDIDATE='--candidate' in sys.argv
LAYOUT_PATH=OUT/('replacement-candidate-layout.json' if REPLACEMENT and CANDIDATE else 'replacement-layout.json' if REPLACEMENT else 'candidate-layout.json' if CANDIDATE else 'plate-layout.json')
LAYOUT=json.loads(LAYOUT_PATH.read_text())
V=OUT/'validation'/('candidate/replacement' if REPLACEMENT and CANDIDATE else 'replacement' if REPLACEMENT else 'candidate' if CANDIDATE else '')
PREVIEW=OUT/'preview'/('candidate/replacement' if REPLACEMENT and CANDIDATE else 'replacement' if REPLACEMENT else '')
PROJECT=OUT/LAYOUT['native_project'];SLICED=V/(PROJECT.stem+'_verification.gcode.3mf')
V.mkdir(parents=True,exist_ok=True);PREVIEW.mkdir(parents=True,exist_ok=True)
