#!/usr/bin/env python3
"""Restore the exact R20 native STL archive used by the model build tools.

Uses only Python's standard library. Existing files with a different hash are
never overwritten. This downloads CAD; it does not prepare or start printing.
"""
import argparse
import hashlib
import os
import tempfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RELATIVE_PATH = Path("review/rear-locating-pegs-2026-11-13/native/Flat132_R20_neutral_final.zip")
URL = "https://github.com/jhilti/fingerworker/releases/download/v0.20.0-prototype/Flat132_R20_neutral_final.zip"
SHA256 = "702d1e2194bd5fc3d1d3d6e260b4ac289ffd66ea0702c957cdb15a33745908c5"
SIZE = 58580146


def digest(path):
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--destination", type=Path, help="Optional alternative file destination")
    args = parser.parse_args()
    target = args.destination or ROOT / RELATIVE_PATH
    if target.exists():
        if target.stat().st_size == SIZE and digest(target) == SHA256:
            print(f"Verified existing R20 archive: {target}")
            return
        raise SystemExit(f"Refusing to overwrite a different file: {target}")
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=target.parent, prefix=".r20-download-", delete=False) as stream:
            temporary = Path(stream.name)
            request = urllib.request.Request(URL, headers={"User-Agent": "fingerworker-release-downloader"})
            with urllib.request.urlopen(request, timeout=60) as response:
                total = 0
                for block in iter(lambda: response.read(1024 * 1024), b""):
                    total += len(block)
                    if total > SIZE:
                        raise ValueError("Download exceeds the expected archive size")
                    stream.write(block)
        if temporary.stat().st_size != SIZE or digest(temporary) != SHA256:
            raise ValueError("Download failed the R20 size/SHA-256 check")
        # Exclusive creation also protects against another process creating the
        # destination while this download was running.
        os.link(temporary, target)
        print(f"Downloaded and verified R20 archive: {target}")
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
