# SIBLING ERRATUM MARKER for `m2_c37_published_constants_census.tsv`

**ERRATUM 13. WITHDRAWN dead literal: `1.64521001744e-15`. Live value: `-1.6216e-15`.**

This marker is a SIBLING file, not an in-place append, because the file it marks is
parser-consumed (TSV) and appending a row or a comment line to it would either break a reader
or be silently ingested as data. Sibling-for-parser-consumed is the shape m1 ruled in L181
section 3(3).

`m2_c37_published_constants_census.tsv` is machine 2's own census OF PUBLISHED CONSTANTS, and it
is itself a bare carrier of a constant ERRATUM 13 killed. That is the sharpest single instance of
the carrier law and it is recorded here rather than quietly repaired: the c31b scored diagnostic
`c0_new` with `a` operative was published as `+1.64521001744e-15` and the
correct value under our own sign convention is `-1.6216e-15`. The magnitude is not the defect;
the SIGN is.

Do not copy `1.64521001744e-15` out of the TSV. Marker added 2026-09-07 (machine 2,
cycle 45), additive only, the TSV's bytes are unchanged.
