# R6 one-piece printed palm viewer

Run `python3 build_viewer.py` after the three hash-bound R6 native pose ZIPs and neutral STEP are supplied. The viewer displays native geometry at exact exported poses, without interpolated motion. P02 is one rigid printed block; P03 is absent. Four P07 return bumpers remain flexible. The unchanged previous hand scan is an approximate reference.

Serve the parent directory on port 8774, then open http://127.0.0.1:8774/viewer/viewer.html. The nominal PASS banner is gated on the final source-bound validation report. Physical strength and comfort remain unqualified.

Existing local geometry runtime: `/tmp/fingerworker-sensor-cad-20261022/bin/python` supplies numpy, trimesh and the optional spring display decimator. This absolute runtime is a workstation convenience, not a packaged dependency.
