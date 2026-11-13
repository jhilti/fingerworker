# Spring tradeoff for a closer palm/finger reach

Additional permanent compression of **3–10 mm is nominally inside the recorded spring operating-length envelopes**, even if the complete current 30−p mm travel is retained. That does not establish cycle life or a new device load rating. Keeping the present closed endpoint instead consumes the same amount of usable stroke. The mounting, switch timing and stop geometry determine which interpretation is achievable.

## Verified baseline and source limits

The R4 source gives `L = 101 − p − s` mm, with `0 ≤ p ≤ 2` and `s + p ≤ 30`. The present minimum spring length is therefore **71 mm** at both endpoints (s30/p0 and s28/p2). The historical procurement table’s 69 mm case belongs to the earlier independent 30 mm stroke plus2 mm preload assumption and is outside the current legal domain.

Both ordered pairs contain two identical steel compression springs. The nominal calculation is `F_pair = 2 × k × (L0 − L)`, assuming direct1:1 motion and ignoring rate/free-length tolerances and friction.

| Spring | Free L0 | Rate each | L1 operating boundary | Approximate block Lc | Evidence |
|---|---:|---:|---:|---:|---|
| 0X-DF2194, lighter |102 mm|3.307 N/mm|58.59 mm|50 mm|Fresh official product data; F1=143.56 N each|
| 0X-DF2185, stronger |105 mm|3.709 N/mm|56.14 mm|48 mm|Fresh official product data; F1=181.22 N each|

Both sets of values are freshly verified by direct read-only retrieval of the official [DF2194](https://www.febrotec.de/de-DE/druckfedern/schraubendruckfedern/0x-df2194/) and [DF2185](https://www.febrotec.de/de-DE/druckfedern/schraubendruckfedern/0x-df2185/) product pages on23 October2026. They agree with the [dated procurement ledger](../../procurement/springs/KATALOGFEDERN.md). Both pages explicitly describe Lc as approximate block length. The JSON preserves product-spec excerpts and HTML hashes; no older original spring datasheet was present locally.

Febrotec’s [official selection tool](https://www.febrotec.de/federnrechner/druckfeder-auswahl.html) makes L1 the shortest permissible operating length. It does not qualify fatigue, buckling, setting or installed guidance. Block length Lc is a geometric endpoint, not a permissible operating target. The [manufacturer help](https://www.febrotec.de/de-DE/faq/schraubendruckfedern) also distinguishes static and dynamic limits.

## More starting force

All forces below are for the **pair**, in N. The two starting-force numbers correspond to adjustment p0/p2. Extra compression a increases force at the same incremental stroke by6.614a N for the lighter pair and7.418a N for the stronger pair.

| Extra a | Open length p0/p2 | Lighter starting force p0/p2 | Stronger starting force p0/p2 |
|---:|---:|---:|---:|
|0 mm|101/99 mm|6.61/19.84 N|29.67/44.51 N|
|3 mm|98/96 mm|26.46/39.68 N|51.93/66.76 N|
|5 mm|96/94 mm|39.68/52.91 N|66.76/81.60 N|
|7 mm|94/92 mm|52.91/66.14 N|81.60/96.43 N|
|10 mm|91/89 mm|72.75/85.98 N|103.85/118.69 N|

For example,5 mm raises starting resistance to about4.05–5.40 kgf for the lighter pair and6.81–8.32 kgf for the stronger pair. It raises force without changing the spring rate.

## A: preserve the existing closed endpoint

If the existing carriage simply starts a mm inward, the remaining travel is `30 − p − a`. The final spring length stays71 mm and pair end force stays **205.03 N lighter /252.21 N stronger**. The preload adjustment still changes starting force and available stroke, while the existing endpoint force remains constant.

| Extra a | Remaining travel p0/p2 | End length |
|---:|---:|---:|
|0 mm|30/28 mm|71 mm|
|3 mm|27/25 mm|71 mm|
|5 mm|25/23 mm|71 mm|
|7 mm|23/21 mm|71 mm|
|10 mm|20/18 mm|71 mm|

This interpretation reduces function if the original28–30 mm stroke is required. It must not be described as a full-stroke design.

## B: preserve the complete30−p mm travel

If the stop/end pose is redesigned to maintain full travel after the shorter rest span, `L_min = 71 − a`. End force rises; the reserve to L1 falls by a. These end values are the same at p0/s30 and p2/s28.

| Extra a | Minimum length | Lighter end force | Stronger end force | Reserve to L1 lighter/stronger | Reserve to block lighter/stronger |
|---:|---:|---:|---:|---:|---:|
|0 mm|71 mm|205.03 N|252.21 N|12.41/14.86 mm|21.00/23.00 mm|
|3 mm|68 mm|224.88 N|274.47 N|9.41/11.86 mm|18.00/20.00 mm|
|5 mm|66 mm|238.10 N|289.30 N|7.41/9.86 mm|16.00/18.00 mm|
|7 mm|64 mm|251.33 N|304.14 N|5.41/7.86 mm|14.00/16.00 mm|
|10 mm|61 mm|271.17 N|326.39 N|2.41/4.86 mm|11.00/13.00 mm|

At10 mm, the nominal minimum length61 mm remains2.41 mm above the lighter L1 and4.86 mm above the stronger L1; the corresponding block clearances are11/13 mm. L1, not coil bind, is the tighter catalogue limit. These are nominal geometric reserves, without allowance for unknown spring/device tolerances.

## Spring-only travel ceilings

At an already shortened rest span, the nominal catalogue ceiling is `s_catalog = 101 − a − p − L1`. This is an operating-length limit, **not a fatigue-qualified safe-stroke rating**. A functioning redesign must obey both this ceiling and its actual mechanical stop domain.

| Extra a | Lighter ceiling p0/p2 | Stronger ceiling p0/p2 |
|---:|---:|---:|
|0 mm|42.41/40.41 mm|44.86/42.86 mm|
|3 mm|39.41/37.41 mm|41.86/39.86 mm|
|5 mm|37.41/35.41 mm|39.86/37.86 mm|
|7 mm|35.41/33.41 mm|37.86/35.86 mm|
|10 mm|32.41/30.41 mm|34.86/32.86 mm|

For retained full travel, the zero-reserve algebraic shortening limits are12.41 mm lighter and14.86 mm stronger. These are not recommended design allowances or guaranteed safe values. A validated limit needs actual length/rate tolerances and the required fatigue duty.

## Integration constraints

Springs alone do not establish feasibility. A shifted carriage/end pose changes cam timing and approach to the fixed SS-01GL2/pedestal; shortened printed P05 stop arms must keep the load through the sensor. The R4 switch/body/tab clearances and central guide would need a new complete motion audit. No CAD was changed for this calculation.

Current isometric mode replaces springs with 86 mm steel sleeves. Keeping the same incremental isometric setting `s=15−p` after shortening by a requires lock span `86−a` mm: 81 mm for a=5, 79 mm for a=7, and 76 mm for a=10. Keeping the existing 86 mm sleeves instead moves the incremental setting to `15−p−a`. Either choice needs coordinated assembly/service validation. The existing 500 N target remains physically unqualified.

Source and exact unrounded values are recorded in [spring-tradeoff.json](spring-tradeoff.json).
