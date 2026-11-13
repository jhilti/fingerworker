#!/usr/bin/env bash
set -euo pipefail
fw_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
build_root=/tmp/fingerworker-arduino
mkdir -p "$build_root/bin"
if [[ "$(uname -s)" != Darwin || "$(uname -m)" != arm64 ]]; then
    echo 'This setup script targets macOS Apple Silicon; use the documented Seeed core with a native compiler on other hosts.' >&2
    exit 1
fi
if [[ ! -x "$build_root/bin/arduino-cli" ]]; then
    curl -fL https://downloads.arduino.cc/arduino-cli/arduino-cli_latest_macOS_ARM64.tar.gz -o "$build_root/arduino-cli.tar.gz"
    tar -xzf "$build_root/arduino-cli.tar.gz" -C "$build_root/bin" arduino-cli
fi
"$build_root/bin/arduino-cli" core update-index --config-file "$fw_root/arduino-cli.yaml"
"$build_root/bin/arduino-cli" core install Seeeduino:nrf52@1.1.13 --config-file "$fw_root/arduino-cli.yaml"
arm_dir="$build_root/arm-gnu-toolchain-13.2.Rel1-darwin-arm64-arm-none-eabi"
if [[ ! -x "$arm_dir/bin/arm-none-eabi-g++" ]]; then
    curl -fL https://developer.arm.com/-/media/Files/downloads/gnu/13.2.rel1/binrel/arm-gnu-toolchain-13.2.rel1-darwin-arm64-arm-none-eabi.tar.xz -o "$build_root/arm.tar.xz"
    echo "39c44f8af42695b7b871df42e346c09fee670ea8dfc11f17083e296ea2b0d279  $build_root/arm.tar.xz" | shasum -a 256 -c -
    tar -xJf "$build_root/arm.tar.xz" -C "$build_root"
fi
if [[ ! -x "$build_root/ctags-5.8-arduino11/ctags" ]]; then
    curl -fL https://github.com/arduino/ctags/archive/refs/tags/5.8-arduino11.tar.gz -o "$build_root/ctags.tar.gz"
    tar -xzf "$build_root/ctags.tar.gz" -C "$build_root"
    python3 - "$build_root/ctags-5.8-arduino11" <<'PY'
from pathlib import Path
import sys
for p in Path(sys.argv[1]).glob('*.[ch]'):
    p.write_bytes(p.read_bytes().replace(b'__unused__', b'CTAGS_UNUSED'))
PY
    (cd "$build_root/ctags-5.8-arduino11"; ./configure; make -j4)
fi
cp "$build_root/ctags-5.8-arduino11/ctags" "$build_root/data/packages/builtin/tools/ctags/5.8-arduino11/ctags"
python3 - "$build_root/bin/python" <<'PYTHON'
from pathlib import Path
import sys
p=Path(sys.argv[1])
if p.is_symlink(): p.unlink()
p.write_text('#!/bin/sh\nexec /usr/bin/python3 "$@"\n')
p.chmod(0o755)
PYTHON
python3 "$fw_root/tools/patch_core.py"

if [[ ! -x "$build_root/venv/bin/adafruit-nrfutil" ]]; then
    python3 -m venv "$build_root/venv"
    "$build_root/venv/bin/python" -m pip install --disable-pip-version-check --no-cache-dir adafruit-nrfutil==0.5.3.post16
fi
