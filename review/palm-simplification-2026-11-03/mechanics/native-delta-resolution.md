# Initial native delta and geometry correction

The first R13 native export was compared to the independently constructed candidate with a web starting at X−27.1. Both Boolean differences were valid. Native minus expected was zero; expected minus native was 0.001830517884 mm³.

The complete difference was confined to X−27.1000001…−26.9999999, Y±56.6244999, Z29.999512084…30.0000001. This is the thin wedge between the web's horizontal Z30 top and the circular R10.25 palm surface immediately behind its tangent plane at X−27. Its maximum height is less than 0.000489 mm. The native CAD kernel merged this near-tangent boundary while the independent OCC construction retained it.

The geometry was corrected instead of relaxing the comparison tolerance: the web now starts exactly at X−27. Existing R12 palm material already supplies a positive-volume union, so the extra 0.1 mm overlap was unnecessary. This removes the ambiguous wedge by construction.

The same revision replaces the new flat web underside over the old plate/rod-block gap with two 45° slopes. The tool spans X−23.25…−18 with its apex at X−20.625/Z12.125 and passes through Y±58.1. It cuts the newly added web only, before union with R12, so existing functional material remains exact. The optional M2 pilots are recut after the union.

The corrected local candidate passes all 12 geometric checks with zero old material removed and 14,580.033618 mm³ added. The first candidate source and preflight are retained in the `*_before_bridge` files. The corrected native export passed the original strict independent comparison: P01 XOR is exactly 0.0 mm³, all 92 other native bodies are unchanged, and all 98 native audit checks pass. No comparison tolerance was relaxed. The source SHA is `82b7d65708c46cd9d4b6ac271047eac2f638f0222451df99eae0780525edd851`; the native STEP SHA is `34503fabce855c834e2d495a33e8a4c834b651c52cc138e4d2d25ded66348530`.
