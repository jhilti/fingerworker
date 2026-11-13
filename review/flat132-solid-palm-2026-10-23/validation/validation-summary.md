# R6 solid-palm validation

**NOMINAL_GEOMETRY_CHECKS_PASS**

Source `62fabee79cf36d0e0b6d4cd8430700519dbc529a5ea08f70018b14b0c3f2271f`. Failed checks: 0; unresolved checks: 0.

Native inventory:105 valid STEP solids,52 device bodies plus53 electronics references;14 print bodies. P02 is one filled rigid palm, P03 removed.104 surviving bodies are compared directly with the frozen R5 exact STEP.

The filled half-cylinder is independently rebuilt and fused to the original P02 for exact Boolean comparison. Existing mount regions, electronics pilots, outer contact position,0.6 mm lid gap, dynamic domain and declared service paths are checked. Unchanged R5 pair checks are reused through the exact source scope certificate rather than relabeled as new native checks.

## Limits

- 500 N remains a design target, not a verified printed working-load rating.
- Solid CAD stock removes the hollow sleeve, but does not prescribe slicer infill or qualify material, print orientation, creep/fatigue or comfort.
- Rigid palm contact loses the previous TPU cap compliance; physical comfort remains unqualified.
- The electronics enclosure/lid, USB/button access and existing insert pilots are retained; the previously discussed9 mm cover extension is not included.
- Heat-set insert stock, actual fasteners, purchased switch calibration/total travel, spring fatigue and final hand fit remain physical prototype checks.
- Native export/source association is root-operator declared and hash-bound; this independent script does not regenerate Onshape.
