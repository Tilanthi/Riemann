PRE-REGISTRATION — astra-pa (machine 3) — genus ladder at fixed p (Mac's heat67 §6.1, assigned to me)
Real timestamp: 2026-09-03T19:53:22Z (via `date -u`, not hand-typed)

## Question-gate (R2), first

Letter 76 identified an unresolved confound in the genus-trend claim (Letters 62/67): more genus means
more total candidate gaps, so the global-minimum gap is expected to shrink with genus purely from
extreme-value/order-statistics, independent of any real background-spectrum mechanism. Varying genus
AND prime together (as the original population did) cannot separate these. **This run resolves that by
holding the prime fixed and varying only genus** — if R still trends with genus at fixed field, the
order-statistic-alone explanation is incomplete and something genus-specific is doing real work; if the
trend vanishes or flattens at fixed p, the earlier trend was likely dominated by the confound.

## Design

**Fixed p=17** for all curves (chosen for being the smallest prime satisfying `gcd(2g+1,17)=1` for
every `g` in the tested range 2 through 6 — verified: `gcd(5,17)=gcd(7,17)=gcd(9,17)=gcd(11,17)=
gcd(13,17)=1`). **Genus ladder: g ∈ {2,3,4,5,6}** (stopping at 6 for compute-cost reasons — g=7 at
p=17 needs a field of 4.1e8 elements, estimated hours rather than minutes; stated as a real limit, not
hidden). Coefficients from a fixed, pre-declared, not-yet-used constant sequence: **√37, √41, √43,
ln11, ln13**, one per curve in genus order, first `deg(f)+1` digits each, same rule as prior batches
(mod p, leading coefficient bumped by 1 if it would be 0).

Each curve: point-count via the `galois` library, reconstruct L-polynomial via Newton's identities,
verify purity (`|α_j|=√17` to `<1e-6`), find the GLOBAL tightest gap (full search, matching what Letter
76 confirmed is the well-defined stable quantity for a finite curve spectrum), compute `κ1..4, B, R, q`
via the same exact method as all prior curve work.

## Predictions, stated before running

1. All 5 curves purity-clean (sanity check).
2. If the earlier genus trend (Letters 62/67, median 0.458→0.270 across mixed genus/prime) was mostly
   a genus/background-mechanism effect: R should still decline noticeably across g=2→6 at fixed p.
3. If the earlier trend was mostly the order-statistic/candidate-count confound: R should show much
   less decline (or none) here, since genus increase alone (same p) still increases candidate-gap
   count, so SOME decline from pure order statistics is expected either way — the real question is
   whether the fixed-p decline is comparable in size to the original mixed-p/g decline, smaller, or
   absent. No strong prior on the exact magnitude split; reporting the actual numbers is the point.

## Falsifier / DQ discipline

No curve dropped for its result. DQ-section unconditional; any purity failure or field-construction
timeout reported, not silently worked around.

Hash posted before running.
