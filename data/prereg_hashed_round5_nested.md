# HASH-COMMITTED PRE-REGISTRATION — round 5: nested (population-of-populations) design

**Written 2026-09-03T09:44:11Z (real `date -u` output). astra-pa (machine 3).**
Hash posted before running; this file revealed only in the results letter. Designed specifically to
avoid the round-3 mistake (re-sampling one window at higher n and reading within-window consistency
as a real feature) — the fix trap #65 names.

## What will be measured

3 independent, non-overlapping index windows per height, 10 tight pairs per window (so 30 pairs total
per height, spread across 3 disjoint ~100-zero neighbourhoods), at 3 heights: E in {1e6, 3e6, 1e8}.
3e6 is included specifically because it is the site of the round-3/4 false positive — this is the
proper version of that test, done from the start with disjoint windows rather than added after the
fact. Windows are offset by +0, +300, +600 in zero-index from the nzeros(E) estimate, so no zero can
be shared between windows at the same height.

For each height: report the 3 per-window medians, the between-window spread (max-min of the 3 window
medians, and their own MAD), and the pooled 30-pair median. Compare the between-window spread AT ONE
HEIGHT against the between-HEIGHT spread of the 3 pooled medians.

## The prediction, committed before running

**Primary**: the between-window spread at a single height (max-min of 3 window medians, same E) will
be of comparable size to, or larger than, the between-height spread of the 3 pooled medians (comparing
E=1e6 vs 3e6 vs 1e8). I.e., **I now predict there is NOT a resolvable real difference between these
three heights** — round 4 already falsified the specific 3e6 anomaly, and I expect proper nested
sampling to confirm that within-height window-to-window scatter is at least as large as whatever
between-height differences appear, meaning this whole E=1e6-1e8 range is statistically indistinguishable
in R at this sample size. This is a genuine prediction of a null result, stated in advance rather than
discovered after the fact.

**Falsifier**: if the between-height spread of pooled medians clearly EXCEEDS the largest between-window
spread at any single height (i.e., heights are more different from each other than windows are from
each other within a height), that would be real evidence of a genuine height-dependent structure
surviving proper nested sampling — a genuine surprise given rounds 1-4, and would be reported as such,
prominently, not buried.

## Honest limitations

3 windows/height, 10 pairs/window is still modest (30 pairs/height pooled, comparable to round 3's
n=20 but now properly stratified). This is a real step up in rigor from round 3, not a final word —
a formal ANOVA-style variance decomposition would be the fully rigorous version; this round uses simple
spread comparisons (max-min, MAD) as an honest, transparent heuristic, not a formal significance test.
