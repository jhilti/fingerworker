# A-P1 component selection and electrical review

All purchased PCBA items are assigned exact MPNs in `parts.json` and `assembly/BOM.csv`. Source links are recorded per row; the referenced Murata and YAGEO specification PDFs were retrieved on 2026-09-21 and are retained under `electronics/procurement/datasheets/` in the workspace. This is a prototype engineering selection. Supplier stock and final quoted prices are not reserved.

## Ceramic capacitor bias review

The manufacturer's characteristic plots are typical curves, not guaranteed minimum-capacitance curves. Reading a plot does not establish a production lower bound. We use rounded conservative readings for prototype margin screening, then require supply/ripple measurements on the first article. A separate 10% ageing allowance below is an engineering allowance, not a manufacturer life-test guarantee.

| References | Selected MPN | Bias point | Conservative typical-curve reading | Screening after tolerance, temperature and ageing allowance |
|---|---|---:|---:|---:|
| C1/C3 | GRM21BR61E106KA73L, 10 uF / 25 V X5R | 3.3 V | at least about 7.5 uF | 7.5 × 0.90 × 0.85 × 0.90 = 5.16 uF |
| C4 | GRM21BR61E226ME44L, 22 uF / 25 V X5R | 5.5 V | at least about 9.0 uF | 9.0 × 0.80 × 0.85 × 0.90 = 5.51 uF |
| C7 | same 22-uF part | 5.0 V | at least about 9.0 uF | 5.51 uF using the same conservative screen |

This supports the original 4.7-uF reservoir target at C1/C3/C4 and exceeds the intended 1-uF effective target at C7 with the selected parts. The rejected 10-uF part at 5.5 V has only roughly 5 uF before allowances; it has inadequate margin there. C4/C7 have therefore been increased, without changing the 0805 footprint or routing. Maximum 22-uF part height is 1.45 mm. Recheck the final enclosure against this height as part of its separate release.

TPS7A20 Rev H recommended operating conditions allow up to 200 uF effective output capacitance. Its actual stability minimum is 0.47 uF; the project uses a more conservative 1-uF design target. C7=22 uF is within that range. C6 remains the local 1-uF input bypass; C4 is additional capacitance on the same VBOOST net. Increased reservoirs can change startup/inrush and discharge time, so measurements remain in FIRST_POWER.md.

Sources for the plotted estimates:

- [Murata GRM21BR61E106KA73 characteristics, page 2, manufacturer document mirrored by Octopart](https://datasheet.octopart.com/GRM21BR61E106KA73K-Murata-datasheet-138744870.pdf), document dated 2020-01-25. Current rating/package checked against [Murata reference specification](https://search.murata.co.jp/Ceramy/image/img/A01X/G101/ENG/GRM21BR61E106KA73-01A.pdf).
- [Murata GRM21BR61E226ME44 electrical characteristics, manufacturer document hosted by TI](https://e2e.ti.com/cfs-file/__key/communityserver-discussions-components-files/196/GRM21BR61E226ME44_5F00_EC_5F00_22uF_5F00_0805.pdf), dated 12/2020. Current rating/package checked against [Murata reference specification](https://search.murata.co.jp/Ceramy/image/img/A01X/G101/ENG/GRM21BR61E226ME44-01A.pdf).
- [TI TPS7A20 Rev H](https://www.ti.com/lit/ds/symlink/tps7a20.pdf), recommended operating conditions and input/output capacitor guidance.

Other capacitors retain their original nominal values. C5 and C9/C10 use C0G, not X7R replacements. Their nominal values and 50-V rating are fixed by MPN. C8 is differential with small normal DC voltage; C6/C13 and 100-nF bypass parts use X7R with 16-V rating. The prototype supply/filter measurements cover the complete assembly.

## Resistances and regulator headroom

R3=680 kohm and R4=200 kohm use 0.1%, 25 ppm/K thin-film parts. R7/R8 use identical 1-kohm 0.1% parts. Standard pulls and series resistors use 1%, 0.1-W YAGEO RC0603 parts. Exact part specification sheets are available directly from the YAGEO links in the BOM. R7/R8 individual tolerances imply up to about 0.2% pair mismatch at reference temperature; no matched tracking beyond the published individual part specifications is assumed.

VBOOST nominal: 1.233 × (1 + 680/200) = 5.4252 V. Component tolerance, reference limits and ripple must leave adequate 5-V LDO headroom and stay below its 6-V operating maximum. First-article measurement under BLE and bridge load is required. The original converter, LDO, ADC and bridge topology is retained for this first prototype.

## Release scope

No real board, battery connector or force sensor was available for measurement. Those facts are explicitly separated from manufacturing-data checks. Physical harness polarity is an acceptance check before connecting BT1, not a claimed completed measurement. Supplier-confirmed module assembly and stock are quotation steps. ADC power ramp, bridge common-mode, regulator stability, charge behavior, RF and calibration are first-article engineering tests. This package releases a prototype manufacturing attempt; it does not label the device electrically validated or ready for series production.
