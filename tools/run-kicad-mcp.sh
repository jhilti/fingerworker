#!/bin/bash
set -eu
TASK_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export KICAD_CLI=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
export KICAD_PYTHON=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3
export KICAD_CONFIG_HOME="$TASK_ROOT/electronics/kicad/.config"
export KICAD_PROJECT_PATHS="$TASK_ROOT/electronics/kicad"
cd "$TASK_ROOT"
exec "$TASK_ROOT/tools/kicad-mcp-env/bin/python" "$TASK_ROOT/tools/seeed-mcp-launcher.py"
