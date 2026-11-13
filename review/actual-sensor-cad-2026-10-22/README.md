# Actual TE force-sensor CAD — 22 October 2026

This review uses the original TE Connectivity **FX1901-0001-0200-L revision F STEP**, already archived in `vendor/te_fx1901/`. TE's [current product page](https://www.te.com/en/product-FX1901-0001-0200-L.html) lists this revision's STEP customer-view model. The original file is preserved unchanged; the positioned copy is a rigid rotation and translation with no rescaling or reshaping.

- [Original manufacturer STEP](sensor/TE_FX1901_official_original.step)
- [STEP positioned in the 132 mm assembly](sensor/TE_FX1901_actual_apex_aligned_132_mm.step)
- [Interactive sensor and mounting comparison](viewer.html)
- [Exact geometry and collision audit](sensor/sensor-geometry-audit.json)
- [STEP/STL round-trip validation](sensor/export-roundtrip-validation.json)
- [Separate Onshape sensor branch](https://cad.onshape.com/documents/15316cc6370631845af136b2/w/3ee26cf6386f889ca7ae9519/e/d253eb87b70818ebde8215f0)
- [Native integration record](onshape-integration.json)
- [Browser and source verification](qa.json)

In the new Onshape branch, the aligned STEP is imported as one solid and derived into `Fingerworker MVP` at its base origin. A reversible Delete part feature removes the five obsolete H01/H01a/H01b/H01c/H01d proxy bodies in that branch. The mechanism now has 100 parts, including its existing electronics references. The original Rev D and 132 mm V6 workspaces remain preserved; no mount geometry was changed.

The manufacturer's solid includes the short radial four-wire exit. It does not include the complete flexible cable or connector. Their former illustrative envelopes are available in the viewer's old-proxy comparison and are not validated cable-routing CAD.

## Correction to the previous model

The earlier H01 sensor was a simplified cylinder with an incorrect housing size for this STEP model. The older PDF's dimension illustrations are labelled FX1900; they do not justify treating the FX1901 customer-view housing as that smaller cylinder.

| Measured CAD dimension | Old placeholder | Manufacturer STEP |
| --- | ---: | ---: |
| Housing diameter | 19.75 mm | 25.00 mm |
| Placeholder cylinder thickness | 5.45 mm | — |
| Complete contact-apex-to-rear envelope | 6.10 mm, including the 0.65 mm proxy boss | 7.95 mm |
| Rear face after preserving current pusher contact | X −8.00 mm | X −9.85 mm |

The actual central spherical contact apex is at the original model origin. Its surrounding disk is recessed by 0.51 mm. The final placement maps that apex to the existing H02 pusher tip at **X −1.9, Y 0, Z 18 mm**, and points the manufacturer's radial lead toward +Y. The rotation is `[0,0,1; 1,0,0; 0,1,0]`, followed by translation `[-1.9,0,18] mm`.

The earlier disk-aligned intermediate is explicitly superseded; it pushed H02 0.51 mm into the sensor's button. Use only the final files with **`apex_aligned`** in their names.

## Fit result

**The actual sensor does not fit the unchanged 132 mm mount at the preserved pusher datum.** Full-resolution nominal mesh intersections are:

| Unchanged component | Intersection with real sensor |
| --- | ---: |
| H12 backing cassette | 582.55 mm³ |
| P01 frame | 54.10 mm³ |
| P05 floating yoke | 733.72 mm³ |
| H02 pusher | 0.00 mm³ |
| H13 preload adjuster | 0.00 mm³ |

Red solids in the viewer expose those intersections. The default display uses the genuine sensor and hides the five old sensor/cable proxy solids. The old proxies remain available only for comparison. The surrounding mechanism has not been redesigned to remove the conflicts.

Earlier clearance passes for the simplified H01 representation **do not establish clearance for the actual purchased sensor**. This finding reopens the sensor mount, backing support and yoke clearances. The earlier width/motion studies remain historical evidence for their exact input geometry; this reference integration is not a manufacturing release.

The hand layer is optional and initially hidden. Its old placement remains provisional. No hand geometry or mechanism source was changed for this comparison. STEP, STL, placement, source hashes and tessellation details are recorded under `sensor/`; visual display sources are recorded in `viewer-build.json`.
