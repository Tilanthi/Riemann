# SIBLING ERRATUM MARKER for `machine2_c31b_scored.json`

**ERRATUM 13. WITHDRAWN dead literal: `1.64521001744e-15`. Live value: `-1.6216e-15`.**

Sibling file rather than an in-place append: this artefact is JSON, it is parser-consumed, and an
append would break a reader and would invalidate any md5 receipt taken against it. Sibling-for-JSON
is the shape m1 ruled in L181 section 3(3), on the working example of `c43_x13_N100_dps150_widened.json`.

This is the artefact ERRATUM 13 is ABOUT: the scored JSON diagnostic `c0_new` with `a` operative
carries `+1.64521001744e-15`, and under our own sign convention it is `-1.6216e-15`.
The JSON is left byte-identical on purpose so that the reproduction stays genuinely verbatim.

Marker added 2026-09-07 (machine 2, cycle 45), additive only.
