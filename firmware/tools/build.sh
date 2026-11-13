#!/usr/bin/env bash
set -euo pipefail
fw_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
bench_flag=0
output_dir="$fw_root/build"
case "${1:-}" in
  "") ;;
  --bench) bench_flag=1; output_dir="$fw_root/build-bench" ;;
  *) echo "Usage: build.sh [--bench]" >&2; exit 2 ;;
esac
python3 "$fw_root/tools/patch_core.py"
export PATH="/tmp/fingerworker-arduino/bin:$PATH"
arduino-cli compile --fqbn Seeeduino:nrf52:xiaonRF52840 \
    --config-file "$fw_root/arduino-cli.yaml" \
    --output-dir "$output_dir" --build-path /tmp/fingerworker-arduino/build \
    --build-property "compiler.cpp.extra_flags=-DFINGERWORKER_BENCH_START=$bench_flag" \
    --build-property compiler.path=/tmp/fingerworker-arduino/arm-gnu-toolchain-13.2.Rel1-darwin-arm64-arm-none-eabi/bin/ \
    --build-property tools.nrfutil.cmd=/tmp/fingerworker-arduino/venv/bin/adafruit-nrfutil \
    --build-property tools.nrfutil.cmd.macosx=/tmp/fingerworker-arduino/venv/bin/adafruit-nrfutil \
    "$fw_root/Fingerworker"

python3 - "$fw_root" "$output_dir" "$bench_flag" <<'PYBUILD'
import hashlib, json, re, sys
from pathlib import Path
fw, out, bench = Path(sys.argv[1]), Path(sys.argv[2]), bool(int(sys.argv[3]))
qualified = re.search(r'HARDWARE_QUALIFIED\s*=\s*(true|false)', (fw/'Fingerworker/Config.h').read_text()).group(1) == 'true'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
manifest = {"board":"Seeeduino:nrf52:xiaonRF52840", "core":"1.1.13", "bench_start":bench,
 "hardware_qualified":qualified, "protocol":3,
 "source_sha256":{str(p.relative_to(fw)):sha(p) for p in sorted((fw/'Fingerworker').glob('*')) if p.is_file()},
 "output_sha256":{p.name:sha(p) for p in sorted(out.iterdir()) if p.suffix in ('.hex','.zip','.elf','.bin')}}
(out/'SHA256.json').write_text(json.dumps(manifest,indent=2)+'\n')
(out/'BUILD_STATUS.md').write_text('# Fingerworker build status\n\nSuccessful compile/link/DFU packaging for Seeed nRF52 1.1.13. BLE v3, 43 bytes.\n\nBench start: '+str(bench)+'. Hardware qualified: '+str(qualified)+'. Source/output hashes: SHA256.json. No physical upload or qualification is implied.\n')
PYBUILD
