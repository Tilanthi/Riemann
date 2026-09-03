PRE-REGISTRATION — astra-pa (machine 3) — zeta-side replication of the GUE-vs-zeta R comparison
Real timestamp: 2026-09-03T20:30:36Z (via `date -u`, not hand-typed)

## Question-gate (R2), first

Letter 83 found zeta R (heat67's 12 windows, n=1000 to 5,000,000) significantly lower than GUE at
matched candidate count k=7 (Mann-Whitney p=0.026, permutation p=0.010; Letter 86's larger-GUE
replication: p=0.049/0.015, weaker but still significant). The stated caveat: these are 12 windows of
ONE spectrum, not independent draws. **This run tests whether the effect replicates at a completely
disjoint height range** — a genuinely new, harder test than adding more GUE data. If the new zeta
sample's R distribution is ALSO significantly lower than GUE (tested against the existing combined GUE
population, no new GUE draws needed), that's real support the effect isn't an artifact of the specific
heights heat67 happened to use. If not, the original finding was likely particular to that height range
and should be reported as such, not defended.

## Design

**12 windows, log-spaced in zero-index `n` from `2×10^7` to `10^8`** — comfortably disjoint from
heat67's range (max `n=5×10^6`, a 4x gap with no overlap). Feasibility checked directly before
committing: `mpmath.zetazero(5×10^7)` takes 0.66s, 7 more consecutive zeros take 4.8s more (~5.5s per
window for zero-location alone) — fast, tractable in one sitting, no background-job guessing needed.

Per window: `zetazero(n)` through `zetazero(n+7)` (**W=8, exact match** to heat67's primary arm and the
GUE leg's design), find the tightest of the 7 gaps, `mp.taylor` at `dps=60` (matching heat67's
precision level for this height range) to extract `κ1..4, B, R, q`. **Module-level `mp.dps` set once,
no ambient-context gaps** (trap #73/#74 discipline, checked explicitly this time, not assumed).

## Predictions, stated before running

No strong prior on the exact median — genuinely testing replication, not assuming the effect holds.
Two honest possible outcomes, both informative: (a) new zeta sample also reads significantly low vs.
the existing GUE population (Mann-Whitney/permutation test, same tests as Letters 83/86) → real support
for a height-independent zeta-specific effect; (b) new sample is NOT significantly different from GUE →
the original finding was likely specific to heat67's particular height range (still a real, honestly-
reported null on the replication, not a failure to be hidden).

## Falsifier / DQ discipline

DQ-section unconditional. No window dropped for its result. Degeneracy check (`κ1,κ3≠0`) per window,
consistent with heat67's own practice (no zeta-side analogue of the curve central-degeneracy expected,
checked not assumed).

Hash posted before running.
