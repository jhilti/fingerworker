#!/usr/bin/env bash
set -euo pipefail
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
clang++ -std=c++11 -Wall -Wextra -Werror -fsanitize=undefined,address \
    "$repo_root/firmware/tests/logic_test.cpp" -o /tmp/fingerworker-firmware-tests
/tmp/fingerworker-firmware-tests
swiftc -module-cache-path /tmp/fingerworker-swift-cache \
 "$repo_root/ios/Fingerworker/Measurement.swift" "$repo_root/ios/Fingerworker/Training.swift" "$repo_root/ios/Fingerworker/TrainingLog.swift" \
    "$repo_root/ios/Tests/main.swift" \
    -o /tmp/fingerworker-packet-tests
/tmp/fingerworker-packet-tests
