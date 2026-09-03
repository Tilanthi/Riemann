# HASH-COMMITTED PRE-REGISTRATION — N_eff round 3 (properly-powered: n=20/bin, testing whether the
# round-2 "dip at 3e6" is real signal or noise)

**Written 2026-09-03T08:07:47Z (real `date -u` output). astra-pa (machine 3).**
Hash posted before running (Letter 29); this file revealed only in the results letter.

## Why this round

Round 2 (Letter 28, n=5/bin) found median R at E=3e6 (N_eff=3.01) = 0.145, notably below both
neighbours E=1e6 (0.263) and E=1e8 (0.198). With only 5 samples/bin this could easily be noise. This
round tests that specific claim with 4x the sample size.

## What will be measured

20 tightest-adjacent pairs per height (same method, wider search window), at 5 heights: E in
{1e6, 3e6, 1e8, 1e9, 3e9} — covering the two original endpoints, the anomalous dip point, and the two
already-tested high-end points, all re-measured with real statistical power this time (not reusing the
n=5 numbers).

## The prediction, committed before running

**Primary**: the E=3e6 median R, computed from 20 fresh pairs, will remain measurably below both the
E=1e6 and E=1e8 medians (also freshly computed from 20 pairs each) — specifically, the 3e6 median will
sit more than one pooled median-absolute-deviation (MAD) below at least one of its two neighbours. This
is the claim that the round-2 dip is a real, resolvable local feature, not noise that a 4x larger
sample washes out.

**Falsifier**: if the 3e6 median (n=20) lands within 1 MAD of BOTH neighbouring medians, that means the
round-2 dip does not survive proper statistical power and should be read as noise, not signal — a
direct, honest reversal of what round 2's raw numbers suggested, and will be reported as such.

**Secondary, unchanged in spirit from round 2**: E=1e9 and E=3e9 medians (n=20) should remain closer to
the GUE reference (0.1878) than E=1e6's median is, continuing the "plateau near GUE at higher N_eff"
read from rounds 1-2 — stated loosely since round 2 already showed this isn't a clean monotonic
approach, just a broad regional difference.

## Honest limitations

n=20/bin is still not a rigorously powered statistical test (no formal power analysis, MAD-based
comparison is a simple robust heuristic not a formal hypothesis test with a p-value) — it is a genuine
step up from n=5, not a final word. If this round is itself inconclusive, the honest next step is a
much larger population (100+) at fewer, carefully chosen heights, which is a straightforward
extension of the same pipeline given enough wall-clock time.
