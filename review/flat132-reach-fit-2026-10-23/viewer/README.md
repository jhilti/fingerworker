# R5 reach-fit viewer

This viewer consumes supplied, hash-bound native configurations. It does not generate or interpolate poses or edit fabrication geometry. R4 remains frozen separately.

User stroke `u` and actual carriage displacement differ: **actual =5+u**. The legal dynamic domain remains `u≥0`, `0≤preload≤2`, `u+preload≤30 mm`. The R5 finger-wall datum is `72−u`, giving `109.25−u mm` spacing from the unchanged palm contact at X−37.25. R4 spacing at the same relative stroke was `114.25−u mm`.

The user selected **81 mm isometric sleeves**. At preload2 the relative user setting is13 mm and actual displacement18 mm. The formulas are user setting15−preload and actual displacement20−preload. The earlier86 mm checkpoint remains separate and is superseded for this configuration. Never label actual displacement as user stroke.

The R5 cam uses a stepped P11 printed shoe and vertical H10 M3x10 clamp. The shoe is manually calibrated by `e` and reset by `e−preload`; the available trim is±0.8 mm. The Omron SS-01GL2 remains a manufacturer-drawing reference with conservative terminal/lug envelopes and illustrative actuator motion. The TE force sensor remains genuine manufacturer STEP geometry. Nominal CAD clearance never establishes actual switch travel, lock retention, wiring, printed strength or a 500 N rating.

`poses-input.json` binds the final FeatureScript, native archives, STEP, immutable version, validation report and delivery package. Keep `review-state.json` pending until final validation is supplied. The builder requires a matching final report/source/STEP before showing nominal green. A local CSG study cannot receive native-regeneration PASS.

Run `build_viewer.py` with `/tmp/fingerworker-sensor-cad-20261022/bin/python`, then `check_viewer.py`. Only the indicative spring meshes may use a lighter display representation. The optional hand is the unchanged local raw scan with its earlier approximate registration; it is not physical fit evidence. Browser QA is a separate step from source/JavaScript checks.

The reach comparison uses analytic R4/R5 finger-wall markers at the same relative user stroke. It does not introduce a second transformed fabrication model. The top-cam preset frames the supplied shoe/clamp positions for each exact configuration.
