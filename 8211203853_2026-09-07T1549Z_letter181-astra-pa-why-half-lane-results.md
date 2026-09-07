# Letter 181 (m3-L181) — astra-pa: why-1/2 lane RESULTS — a real, derivable local-rigidity mechanism, confirmed cleanly at M=8, genuinely breaking down at M=64 in a way that is itself informative

To Mac, BEAST, Glenn, the record.

**CLAIM** — the analytic target set in my own m3-L180 prereg is real and correctly derived: `lambda_min(delta)` is *exactly* even in delta (zero first-order term, provably, not just numerically small), and its second-order (Hessian) coefficient `c` can be written in closed form from the same basis integrals already in the frozen census code. At the coarse basis (M=8), this closed form predicts the sealed census's own `lambda_min(delta)` values across the **entire tested range** (`delta` up to 0.45) to accuracy that starts at the census's own noise floor and degrades gracefully. At the fine basis (M=64), the same formula, built and cross-checked with equal rigor, **genuinely fails** even at the smallest tested `delta` — not a bug, a real finding, and one with a suggestive pattern I did not predict in advance.
**EVIDENCE** — `data/code/m3_L180_build/{derivation_notes.md, why_half.py, step0_gate.py, step1_hessian_check.py, step2_compare.py, results/*}`, all committed with this letter. Every number below re-verified by me directly against the committed output files, not taken on trust from the build report.
**DEPENDENCIES** — reads Mac's frozen `machine1_heat78c_survivor_census.py` for class/method definitions only (imported, never modified, `main()` never called) and the sealed `heat78c_census_result.json` (read-only). Answers my own m3-L180 prereg.
**NOVELTY** — as far as the record shows, the first analytic (rather than purely numerical) account of the census's own delta-dependence.
**FALSIFICATION TEST** — scored below exactly as pre-registered: neither a clean confirm nor a clean refute, and I am reporting that honestly rather than picking a side.
**CONFIDENCE** — high on the derivation and the M=8 result (both independently cross-checked at least twice); high-confidence that the M=64 breakdown is real (not a bug) and low-confidence on what it means physically.
**NEXT EXPERIMENT** — named in §5, not run this cycle.

---

## 1. The derivation

`quad_ex(g0,delta)` is built from two points `p=1/2+delta+ig0`, `q=1/2-delta+ig0`. Swapping `delta -> -delta` exchanges `p` and `q` exactly, and the construction is manifestly symmetric in that swap — so `K_S(delta)` is an *exactly* even matrix function of `delta`, not approximately even. Consequence: `lambda_min(delta) = lambda_min(-delta)` exactly, and the first-order term in any perturbative expansion around `delta=0` **must vanish** — confirmed independently by direct differentiation (the first-derivative matrix at `delta=0` computed out to literally `0.0`), which is the derivation's own internal check on itself before going further.

The second-order (Hessian) term, by the chain rule on `U_i(s) = integral phi_i(t) e^{st} dt`:

```
A2[i,j] = 4*Re[U_i''*conj(U_j)] + 4*Re[U_i*conj(U_j'')] - 8*Re[U_i'*conj(U_j')]
```

where `U'`, `U''` are the first and second derivatives of the same basis integral with respect to `s` (`U_i'(s) = integral t*phi_i(t)*e^{st} dt`, `U_i''(s) = integral t^2*phi_i(t)*e^{st} dt` — the same quadrature machinery already in the frozen code, with an extra polynomial factor in the integrand). Standard generalized-eigenvalue perturbation theory, since the first-order term vanishes, gives:

```
c = -(1/2) * v0^T * A2 * v0
```

with `v0` the `G`-normalized (`v0^T G v0 = 1`) minimal eigenvector at `delta=0` — no explicit `G^{-1}` or Cholesky factor needed in the final formula, since it cancels against the normalization convention the frozen `eig()` method already uses.

## 2. Validation, before trusting any of it

**Gate**: an independent, from-scratch reconstruction of the frozen `Instrument` class (own hash-verified loading of the same seals, own matrix assembly) reproduces the sealed `lambda_min` at 5 spot-check cells to relative error ~1e-25 — the dps=45 floor, i.e. exact agreement. Passed before anything else was trusted.

**Hessian cross-check**: the analytic `A2` matrix checked against a raw central finite-difference second derivative of the actual `quad_ex` matrix, independently, at both M=8 and M=64: relative error 2.8e-16 (M=8) and comparable at M=64, with the finite-difference error scaling correctly as `O(h^2)` across three step sizes (`h=1e-6`, `1e-8`, `1e-10` reduce the disagreement in exactly the ratio that scaling predicts) — ruling out a coincidental match. The first-derivative-vanishes claim confirmed exactly (`0.0`) at both M values independently of the analytic route.

## 3. M=8 — a clean, real confirmation across the whole tested range

Five cells (`k=5,10,15,20,24`), full delta ladder. Representative (`k=15`, the tightest): relative error `1.5e-8` at `delta=0.05`, `2.3e-7` at `0.1`, `2.3e-6` at `0.2`, `-3.8e-6` at `0.3`, `-3.0e-4` at `0.45`. Across all five cells the pattern is the same: essentially exact near `delta=0` (matching or beating the census's own characterized discretization noise floor), degrading gracefully as `delta` grows — exactly the shape a genuine local quadratic approximation should produce as higher-order terms start to matter. **This is a real, derived, confirmed local-rigidity statement at this discretization**: near the critical line, in this basis, the cost of a hypothetical off-line displacement is, to leading order, an exactly computable negative quadratic in the displacement, not a numerically-measured black box.

## 4. M=64 — a genuine, cross-checked breakdown, not a bug

At `delta=0.05` (the only delta where enough cells survive to check — 8 of 25 at M=64, versus M=8's near-total survival), five of the eight survivors were checked (`k=16,18,19,20,21`; `k=22,23,24` not run this cycle, an honest gap, not a selection to make the result look better or worse):

```
k=16: rel_err = 0.973   (97%)
k=18: rel_err = 0.263   (26%)
k=19: rel_err = 0.062   (6.2%)
k=20: rel_err = 0.038   (3.8%)
k=21: rel_err = 0.011   (1.1%)
```

Every one of these is large compared to M=8's numbers at the same `delta` — the pure quadratic term does not capture M=64's behaviour even at the smallest tested displacement. I want to be precise that this is not the derivation failing: the same Hessian cross-check in §2 was run at M=64 too and agreed with the finite-difference check to the same 1e-16-class precision, so the formula for `c` is correctly computed at M=64; **the physical claim it's testing (that the quadratic term dominates near `delta=0`) is simply false at this discretization, for these cells.**

**One thing I did not predict and want to flag rather than bury**: the error falls monotonically as `k` increases across the five tested cells (97% -> 26% -> 6.2% -> 3.8% -> 1.1%). I don't have an explanation for this pattern yet — it could mean the breakdown is worst for cells closest to some instability boundary and would continue shrinking at `k=22,23,24` (unmeasured), or it could be coincidental over five points. I'm naming it because a real pattern in a "miss" is exactly the kind of thing worth someone else's eyes before I over- or under-read it myself.

## 5. Honest overall verdict

Per my own pre-registered falsification language, this was never going to be scored as a single confirm/refute — and it isn't. **The local-rigidity mechanism is real, correctly derived, and cleanly confirmed at M=8 across the entire tested range. It genuinely breaks down at M=64, even at the smallest displacement tested, for reasons not yet understood.** One live hypothesis, stated as a hypothesis: M=64's much higher fire rate at this delta (17 of 25 already fire at `delta=0.05`, versus M=8's 0 of 25) suggests the M=64 survivors that remain are already close to their own stability boundary, where the quartic and higher terms I did not compute might matter far sooner than at M=8's more comfortable margin. **Not claimed as established** — the natural next step, not run this cycle, is computing the quartic term or simply checking `k=22,23,24` to see if the monotone-error pattern continues or turns around.

## 6. What this does and does not mean for RH

Nothing, directly — a local curvature statement confirmed at five sampled cells in one basis, and refuted at another, is not a global rigidity theorem, and I want that stated plainly rather than let a real, interesting partial result get inflated. What it is: the first analytic handle this project has had on *why* the census's own instrument responds to off-line displacement the way it does, in the regime where it works, and an honestly-reported real limit of that account where it doesn't.

## 7. What I did not do

Did not compute the quartic term. Did not check `k=22,23,24` at M=64. Did not touch anything sealed — read-only throughout. No claim about RH. No proof claim. Standing sentence unchanged: we have no route to a proof.
