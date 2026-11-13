"""Integration API for the local R12 rear-gate study."""
from pathlib import Path
import importlib.util
_path=Path(__file__).parent/'mechanics/build_rear_gate.py'
_spec=importlib.util.spec_from_file_location('r12_rear_gate_impl',_path)
_impl=importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_impl)
load=_impl.load
expected=_impl.expected
patch_source=_impl.source_patch
geometry=_impl.geometry
restore_frame=_impl.restore_frame
b=_impl.b
r7=_impl.r7
