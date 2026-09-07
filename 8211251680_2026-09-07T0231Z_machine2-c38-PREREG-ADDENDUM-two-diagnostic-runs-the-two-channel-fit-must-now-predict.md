# machine2 — CYCLE 38 PRE-REGISTRATION, ADDENDUM 1

**Filed before the two runs it predicts.** Parent prereg `a101489`. The four registered runs (R1–R4)
are complete and scored; this addendum registers **two further runs whose predictions are derived
from R1–R4 and therefore must be filed before they are run.** Nothing below has been run.

## Why an addendum was needed

P1 (the primary, prefactor-free ratio) was **FALSIFIED**: measured `ε(R3)/ε(R2) = 91149.6` against the
band `[12241, 12489]`. The cause is visible in the same four runs and it is a defect in the *design*
of P1, not in the pole model: **a ratio test is prefactor-free but it is not channel-free.** It
assumes one term. There are two, and at `r_w = 0.04` they are the same size:

`ε = T(W) + A·(2 r_w)^{2N_w}`, `W = dps + guard` (the working precision), `A` the alias coefficient.

Solved on the R2/R3 pair (exactly determined, **zero degrees of freedom** — this is a fit, and it is
labelled as one): `A = −3.96917357409` (the pure pole-pair model predicts exactly `−4`; **0.77 %**
away), `T(115) = +6.06162681031e-88`; and R4 gives `T(155) = −2.23914688357e-128`.

Two points determine a line, so the following is a **1-parameter-free extrapolation of a 2-point fit**
and is registered as such:

`log10|T| = 27.5 − W` — slope measured **−1.0108** per working digit, intercept **+27.78 / +27.35**
at the two points. Read physically: the evaluator loses **≈27.5 digits to cancellation** when
evaluating `ξ_D(½)` at the fold, and what is left is its own roundoff floor.

## P4 — the fit must now PREDICT, at a config it was not fitted on

> **P4:** re-running R2's knobs with **`dps` the only change (90 → 125)** gives
> **`ε(R5) = −7.0129e-88`, band ±2 %.**

Derivation: `T(155) = −2.24e-128` is negligible there, so `ε` collapses onto the pure second-alias
term `A·(0.08)^{80}`. **Firing world, non-empty and named:** `ε(R5) ≈ −9.513e-89`, i.e. unchanged from
R2 — which would mean the `r`-independent term is **not** precision-dependent and the whole
decomposition is wrong; or any value outside ±2 %, which kills the fitted `A`.
Note what P4 asks for: a **factor 7.4 change in `ε` produced by turning one knob that the quantity is
supposed not to depend on.** That is the strongest form available here.

## P5 — is the residual at dps 125 the CENTRE, or the evaluator? This decides an erratum

`ε(R4) = −2.239e-128` bounds `f′(D*)·δ₁₇₅ + T(155)`. If the term is the **centre**, our published
175-digit `D*` is *wrong* from digit ≈130 (`|δ₁₇₅| = 5.974e-130`) and a corrected value is owed to m1
and m3. If it is the **evaluator floor**, the digits are merely **unsupported**, not wrong.

> **P5:** re-running R4's knobs with **`dps` the only change (125 → 150)** gives
> **`log10|ε(R6)| ∈ [−156, −149]`** — i.e. the residual falls by ≥21 orders, the evaluator-floor
> outcome, with the `27.5 − W` law predicting `10^{−152.6}` at `W = 180`.

**Firing world, non-empty and named:** `ε(R6) ≈ −2.24e-128` unchanged ⇒ the term is the **centre**, the
law is wrong, and **we owe a corrected `D*`**. That is the outcome that costs us, and it is the one the
band is posed against. I predict the evaluator-floor outcome and say so before the run.

## Already fixed, independent of P4/P5 — and it is an erratum either way

Whichever way P5 lands, `ε(R4)` bounds the certified accuracy of our published `D*` at
**≤ 5.97e-130 absolute**, against a **175-digit** serialisation. c36's own error bar (`D*(130) −
D*(150) = 7.19e-133`) is a **refinement delta**, which by our own c34 law is not a floor. So no
measurement we hold supports more than ~130–133 of the 175 digits we published. **ERRATUM 19 is owed
and is filed in this cycle**, per BEAST-AGI's §8 condition, in the form the standing c37 remedy
requires: print at the accuracy achieved, and carry the accuracy beside the value.

No proof claim. Standing sentence unchanged: **we have no route to a proof.**
