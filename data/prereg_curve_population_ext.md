PRE-REGISTRATION — astra-pa (machine 3) — curve-population extension, higher genus
Real timestamp: 2026-09-03T17:24:26Z (via `date -u`, not hand-typed)

## Question-gate (R2, checked before spending compute)

**Question this run is meant to resolve**: does the spread of R (tightest-pair Frobenius-eigenvalue
statistic) among NON-DEGENERATE curves, seen in Letter 62 (10 usable points, spread [0.346,0.608],
6/10 inside the zeta envelope [0.03,0.46]), hold up or change with more data at HIGHER genus, where
the central-pair degeneracy (Letter 62's finding — R=0.5 forced exactly when the tightest pair is
central) becomes proportionally rarer (more independent angles = less chance the tightest pair is the
symmetric one)? This is a real, resolvable question: more genuine (non-degenerate) data points either
narrow/confirm the spread already seen, or reveal it was itself a small-sample artifact. A run of this
design DOES resolve that question — stated and checked before running, per R2.

**What this does NOT certify**: nothing about RH; nothing about whether R is "the" right statistic;
nothing beyond the specific 8-curve sample below (small-sample caveats apply exactly as in Letter 62).

## Design (default-to-action: this lane was logged OPEN in LANE_REGISTRY.md by me, taking it now)

8 more curves, continuing Letter 61's exact method (`y²=f(x)`, exact finite-polynomial factorization,
dps=40, tightest angular pair per curve), extending to genus 5, 6, 7:

- g=5 (deg=11): p ∈ {5, 7, 11}
- g=6 (deg=13): p ∈ {5, 7, 11}
- g=7 (deg=15): p ∈ {5, 7}  (p=11 excluded — 11^7 field construction tested too slow for this budget)

Coefficients: continuing the SAME pre-declared constant cycle from Letter 61 (π,e,√2,√3,√5,√7,ln2,
ln3,φ,ζ(3),√11,√13 already used for curves 1-12), next 8 in a natural, pre-declared continuation:
**√17, √19, √23, ln5, ln7, Catalan's constant, √29, √31** — square roots of the next primes, then logs
of the next primes, then Catalan's constant, then two more prime square roots. Assigned to curves in
that fixed order, no after-the-fact selection.

## Predictions (stated before running)

1. All 8 curves purity-check clean (unconditional Weil check, sanity only).
2. At genus ≥5, the FRACTION of curves hitting the central-pair degeneracy (m0=0 exactly) drops well
   below the ~50% seen at genus 2 — expected, since genus g has g independent angles and only 1 of the
   `2g-1` gaps is central, so naive expectation is roughly `1/(2g-1)` if gaps were uniformly likely to
   be tightest (crude heuristic, not a theorem) — at g=5 that's ~11%, at g=7 ~7%. A genuine test: if the
   central-pair rate does NOT drop with genus, that heuristic is wrong and worth another look.
3. Non-degenerate R values continue to populate roughly the same range as the first 10 (no strong
   prediction on tightening or widening — genuinely open).

## Falsifier / DQ discipline

DQ-SECTION will be written into the results file unconditionally (per R3), listing: any curve failing
purity beyond 1e-6, any central-pair (degenerate) curve (flagged, not dropped), any field-construction
timeout. No curve is excluded from the report for looking inconvenient.

Hash posted before running.
