#!/usr/bin/env python3
"""Compatibility entry point for the current 30 mm prototype checks."""
from pathlib import Path
import runpy
runpy.run_path(str(Path(__file__).with_name("check_low_profile.py")), run_name="__main__")
