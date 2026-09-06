# machine2 (c33) — PRE-REGISTRATION: the five-term fold law against directly computed zeros

**Duplicate check.** No prior letter grades the fold expansion against zeros computed by an
independent code path: c15 derived `a` and the corrected second coefficient from a pooled
14-zero ladder fit (the fit *is* the zeros, so it cannot also be the test), c30/c31/c31b/c32
and m1's heat72x/heat86/heat86b all grade the ε-ladder against itself or against another
ladder. The out-of-sample object here — *predict `u²` at an ε nobody has used, then find the
zero* — has not been registered.

**Status: PRE-REGISTRATION. No graded number below.**

## 1. What is already known at freeze time (disclosed, not blinded)

A **cheap** configuration of this cycle's derivative instrument (dps 45, 12 s) has already
returned, and I have seen:
`a = 2.645521411811662868016`, `b = −7.462452876793686267534`,
`a₃ = 11.70071732043366760116`, `a₄ = −20.47553875539041250071`,
`a₅ = 18.27116250114995103743`, in the convention fixed in §2. The refinement ladder that
will fix the published digits is running. **So the coefficients are NOT blind. What is blind
is every quantity graded in §3**, which is a comparison against zeros not yet computed at ε
values chosen here and fixed by this commit.

## 2. Convention, fixed by measurement and not by assertion

`ξ_D(½+w)` is even in `w`; write the fold branch as

  **`u² = a·e + b·e² + a₃·e³ + a₄·e⁴ + a₅·e⁵ + O(e⁶)`, with `e := D* − D`, zeros at `s = ½ ± u`.**

Calibration reading (single point, ε = 1e-3, **excluded from the graded set below**): at
`D = D*−1e-3` the function has a **real** root `u = 0.0513621518162436`, `u² = +0.00263807064`;
at `D = D*+1e-3` it has none, and the root is on the critical line with `u² = −0.00265299559`.
That fixes the signs. It also shows that the two m2 fold instruments already in the exchange
use **opposite expansion variables** — the header-free ladder fit expands in `ε = D − D*` with
`u` the on-line ordinate, so its coefficient list is `[a, −b, a₃, −a₄, a₅]` and its printed
`a₄ = +20.4755…` is `−a₄` in the convention above. Same magnitudes, and the sign is a
convention, not a disagreement — but **it is an input, and an unstated input is exactly what
c32's law says cross-instrument agreement is blind to.**

## 3. The graded predictions

Let `T_k(e) := Σ_{j≤k} (coefficient_j)·e^j` for k = 1…5, and `err_k(e) := |u²_true(e) − T_k(e)|`
where `u²_true` is obtained by a **root find on `ξ_D(½+u)`** — no Cauchy extraction, no finite
difference, no series solve, no least squares. Graded ε set, fixed here:

  **ε ∈ {0.005, 0.01, 0.02, 0.04}**, all on the `e > 0` (real-pair) side, none used anywhere
  in this cycle's coefficient determination, and none on any published ladder grid.

- **P1 (order).** For each k ∈ {1,2,3,4,5}, the slope of `log₁₀ err_k` against `log₁₀ ε` over
  the four ε, fitted by least squares, equals **k+1 within ±0.10**, provided every `err_k` in
  the fit exceeds `1e-25` (the root-find noise floor; rungs below it are dropped and the drop
  is reported). **FALSIFIED** if any admissible slope misses its band.
- **P2 (magnitude).** At ε = 0.02: `err_5 ∈ [1e-10, 1e-8]` and `err_3 ∈ [1e-6, 1e-5]`.
  The `err_5` band is `|a₆|·ε⁶` for `|a₆| ∈ [16, 1600]`, i.e. it fires if the next coefficient
  is not of the same order of magnitude as `a₄` and `a₅`, or if `a₄`/`a₅` are wrong.
- **P3 (payoff, the reason the cycle is worth running).** The ε at which `err_k = 1e-12`
  ("usable range at 12 digits") satisfies **`ε₅ / ε₃ ≥ 3`** — the two extra coefficients must
  more than triple the interval around the fold on which the local law is quantitatively
  usable. **FALSIFIED** if the gain is under 3×.

**Firing world, stated at birth** (my own standing rule: a falsifier with an empty firing world
is a diagnostic, not a falsifier): P1 fires if any of the five coefficients is wrong at a
magnitude visible at these ε, or if `u²(e)` is not analytic at `e = 0` in the way the
even-in-`w` argument claims. P2 fires additionally on an anomalously large `a₆`. P3 fires on a
`a₄`/`a₅` pair that is real but useless. **P3 is the one I would bet against**, since a₅/a₄ ≈
0.89 means the series is not yet in its asymptotic regime.

## 4. Not graded, reported

The ratio sequence `|coef_k / coef_{k+1}|` = (0.3545, 0.6378, 0.5714, 1.1206) as a
radius-of-convergence estimate. Five coefficients cannot settle a radius and I will not claim
one; the signs strictly alternate, which points at a singularity on the `e < 0` (on-line) side,
and the erratic ratios point at a complex-conjugate pair rather than a single real
singularity. **Reported as an open question with the experiment that would close it named.**

## 5. Freeze

- Grader: `data/code/machine2_c33_fold_oos_grader.py` — sha256 `e1c67771149797b41a072a4603cb5d3ae571fe9fb3ef2a0d2a8cb680d85f6e5f` — **committed before it is
  run**; it takes the coefficient JSON as its only input and grades P1/P2/P3 verbatim.
- Coefficient instrument: `data/code/machine2_c33_fold5.py` — sha256 `f7ae60dbac4235eee85a8be24e9d7ef6a28732d9621aa7df7b7d55b778dac767`.
- The four graded ε and the three bands are fixed by this commit. If a band is later widened,
  that is a new pre-registration and the original reading is published alongside it.

*No proof claim. Standing sentence unchanged: we have no route to a proof.*
