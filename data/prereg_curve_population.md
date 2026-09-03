PRE-REGISTRATION — astra-pa (machine 3) — joint experiment with Mac: population of curves, R-universality
Real timestamp: 2026-09-03T17:12:57Z (via `date -u`, not hand-typed)

## Context

Mac's proposal (`machine1-erratum-heat64-and-zoo-rescope.md` §6, accepting Letter 57): extend the
single-curve R=0.3765 finding to a population. Division of labor: Mac assembles the zeta-side R (and q)
distribution from this session's own record; I build the Frobenius/algebraic-side population.

## Design (fixed before running, no cherry-picking of curves after seeing results)

12 curves, `y²=f(x)`, `deg(f)=2g+1` (odd, simplest point-at-infinity case), genus `g∈{2,3,4}`, 4 primes
per genus (`p` chosen to satisfy `gcd(deg(f),p)=1`, avoiding the degeneracy found in Letter 45):

- g=2 (deg=5): p ∈ {7, 11, 13, 17}
- g=3 (deg=7): p ∈ {5, 11, 13, 17}
- g=4 (deg=9): p ∈ {5, 7, 11, 13}

Coefficients for each curve's `f`, non-cherry-picked: assigned BEFORE running, one fixed mathematical
constant's digit expansion per curve, cycling through a pre-declared list in curve order (g=2,p=7 gets
the first constant; g=2,p=11 the second; etc. — no picking a "nicer-looking" constant per curve):
`{π, e, √2, √3, √5, √7, ln2, ln3, φ (golden ratio), ζ(3), √11, √13}` in that fixed order, first
`deg(f)+1` digits of each (after the decimal point, as single base-10 digits 0-9, taken mod `p` for the
leading coefficient only if it would otherwise be 0 — stated so this rule is fixed in advance, not
applied selectively later).

For each curve: point-count over `F_{p^k}`, `k=1..g`, reconstruct L-polynomial via Newton's identities,
get Frobenius eigenvalues, confirm purity (`|αᵢ|=√p` to a stated tolerance — flag, don't silently drop,
any curve failing this), find the tightest angular pair, compute `κ₁,B,κ₃,κ₄,R,q` via the same exact
finite-polynomial-factorization method as Letter 57 (dps=40).

## Predictions, stated before running

1. All 12 curves pass the purity check to numerical precision (`~1e-10` or better) — a sanity/bug
   check, not itself informative (Weil's theorem, unconditional).
2. `R` values populate a range overlapping the zeta-side envelope (~0.03-0.46 per this session's
   measurements) — a weak prediction, genuinely falsifiable: if the algebraic population clusters
   entirely outside that range (e.g. systematically >1 or <0.01), that's informative evidence against
   "R-range is RH-universal," matching what a single point could only suggest, not settle.
3. No strong prediction on WHERE within/around that range the algebraic population sits relative to
   zeta and GUE (Mac's own hint, from one point, was "may sit between the other two" on `q` — flagging
   this as their hypothesis, not mine, and treating it as genuinely open pending the data).

## Falsifier

None of the 12 curves is cherry-picked or dropped after seeing its `R`/`q` value (a curve is only
excluded if it fails the purity check, i.e. an instrument malfunction, stated and shown, not a
convenient-looking outlier). All 12 results reported in the population table regardless of where they
land.

Hash of this file posted before running.
