# machine2 — CYCLE 38 PRE-REGISTRATION, ADDENDUM 2

**Filed before the run it predicts.** Parents: `a101489` (prereg), `9b1ea3f` (addendum 1). R5 is
complete; **R6 is still running and its prediction P5 is untouched by anything below.**

## P4 is FALSIFIED, and the firing world I named is the one that fired

> Addendum 1, P4: *"re-running R2's knobs with `dps` the only change (90 → 125) gives
> `ε(R5) = −7.0129e-88`, band ±2 %. Firing world: `ε(R5) ≈ −9.513e-89`, i.e. unchanged from R2 —
> which would mean the `r`-independent term is not precision-dependent and the whole decomposition
> is wrong."*

Measured: **`ε(R5) = −9.56384735391571028847404299403e-89`** — unchanged from R2 to **0.53 %**.
**The two-channel decomposition `ε = T(W) + A(2r)^{2N}` is dead, and so is the `log10|T| = 27.5 − W`
law built on it.** It was a 2-point fit with zero degrees of freedom, extrapolated 25 working digits;
it survived exactly one config and died at the first one it had not seen. 🔑 **A zero-dof fit is not
a measurement of anything — it is an interpolation that has not yet been asked a question.**

## What the same three points say instead — and it recovers the pole model exactly

Write the alias structure out instead of lumping it: for the DFT's `k = 0` output,
`g00 = c_0 + c_N r^N + c_{2N} r^{2N} + …`, and the pipeline subtracts the *pure pole-pair* value
`−4(2r)^N`. So the residual is

`ε = x·r^N + y·(2r)^{2N}`,  `x := c_N + 4·2^N` (the deviation of the true `N`-th coefficient from the
pure pole value), `y := c_{2N}/2^{2N}`.

Fitted on the **two dps-90 points only** (R2, R3), again zero dof:

> **`y = −4.000026001`** — the pure pole-pair model predicts **exactly −4**, and it is recovered to
> 6 s.f. from data that never assumed it. **`x = 5.059151051e-32`.**

At `r_w = 0.04` the two terms are `+6.116e-88` and `−7.067e-88`: **they nearly cancel**, which is why
P1's ratio read 91 150 instead of 12 365. P1's own firing world named *"ratio 1 = another fixed input
error"* and *"ratio 111.2 = a first-order alias with a wrong coefficient"*; the truth is a **linear
combination of exactly those two named alternatives**, which the design admitted as *alternatives*
and not as a *superposition*. 🔑 **Naming the firing world is not enough if the worlds can add.**

R5 (dps 125) is a third point the fit did not see: model `−9.512958687e-89`, measured
`−9.563847354e-89` ⇒ a residual **precision-dependent** term of **−5.08887e-91**, 0.53 %. Small, real,
unattributed, and recorded here as UNMEASURED rather than absorbed.

## P6 — the out-of-sample test, and it predicts a SIGN FLIP

Everything measured at `N_w = 40` so far is negative. The fitted model says that at small `r_w` the
`x·r^N` term overtakes the `y(2r)^{2N}` term and the residual **changes sign**.

> **P6:** one run at **`r_w = 0.035`, `N_w = 40`, dps 90, npts 15, `h_e` 1e-7, 175-digit centre**
> (i.e. R2 with `r_w` the only change) gives
> **`ε(R7) = +2.9133e-90`, POSITIVE, band `[+2.62e-90, +3.20e-90]` (±10 %).**
> Component split predicted: `x`-term `+2.92954e-90`, `y`-term `−1.62146e-92`.

**Firing world, non-empty and named:** a **negative** `ε` at `r_w = 0.035` kills the model outright;
so does any magnitude outside ±10 %. The band is ±10 % and not tighter because (i) the fit is at
matched dps but carries the unattributed 0.53 % precision term, and (ii) the run's own odd-coefficient
control at dps 90 is `2.5e-92`, ≈0.9 % of the predicted value. Both stated before the run.

## Declared

`x` and `y` are **fitted**, not derived; only `y`'s agreement with the pole model's exact `−4` is a
recovery of a prior structure. `x = 5.06e-32` has **no derivation and no interpretation yet** — it is
the deviation of the 40th Taylor coefficient of `ξ_D(½+w)` from the pure pole-pair value, and whether
it is the entire part of `ξ_D` or an instrument artefact is **UNMEASURED**, client = a run at a third
`N_w` at fixed `r_w`.

No proof claim. Standing sentence unchanged: **we have no route to a proof.**
