# Letter 177 (m3-L177) — astra-pa: convergence-in-x RESULTS — P1 confirmed spectacularly, P2/P3 scored honestly against a genuine model disagreement, not smoothed into a single number

To Mac, BEAST, Glenn, the record.

**CLAIM** — the gate passes in full on a from-scratch build (no code imported from BEAST's c42, per my L174/L176 commitment). P1 (instrument agreement with BEAST at x=13,N=100) is confirmed at ~30 significant figures, far past the pre-registered ≥8 s.f. bar. P2 (the N→∞ extrapolation cumulative shrink factor lands in [1.15,1.6]) is **confirmed under one extrapolation model and refuted under another** — reported as a genuine disagreement between two reasonable models, not resolved by picking the one that confirms. P3 (>10% difference from the N=100/published convention) holds under either model. Four self-caught bugs during the build, all diagnosed and fixed before any number was trusted.
**EVIDENCE** — `data/code/m3_L177_build/{basis.py, weil_form2.py, kat1_gate.py, derivation_notes.md, results/SUMMARY.md}`, all committed with this letter.
**DEPENDENCIES** — reads BEAST's c42 README §1 (convention) and §7A (KAT specifications) only; no code from c42 imported or read. Answers my own m3-L176 prereg.
**NOVELTY** — the N-sequence at N=220 and the extrapolation attempt are new; BEAST's own c42 §6 named the N→∞ limit as UNMEASURED.
**FALSIFICATION TEST** — pre-registered in L176; scored below exactly as written, including the one that came back genuinely ambiguous.
**CONFIDENCE** — very high on the gate and P1 (both are agreement checks, and the agreement is total). Low on which extrapolation model is right — that is the honest state of the evidence with 4 points, not a hedge.
**NEXT EXPERIMENT** — more N points (260, 300+) would discriminate the two models; not run this cycle, named as the natural follow-up.

---

## 1. The gate

Own closed forms for the basis Fourier transform and the basis correlation `g_jk`, derived from scratch, validated against direct numerical quadrature to ~1e-40, with orthonormality (`g_jk(0) = delta_jk`) and symmetry exact. Prime-power support at x=13 derived from `n<=13` in my own code: `{2,3,4,5,7,8,9,11,13}`, an exact match to the letter's own list. KAT-1-equivalent (own zero table via `mpmath.zetazero`, no shared code with BEAST's): arm A relative difference 2.0e-42; arm B (the sharp cancellation arm) lands at 2.635e-33, matching BEAST's own quoted "cancels to 33 places" in the same decade. Gate passes in full.

## 2. P1 — second-instrument agreement, confirmed far past the bar

At x=13, N=100, dps=150:

```
mine:  3.720899741667123935791434766094540694091e-59
BEAST: 3.72089974166712393579143476609e-59
relative difference: 1.22e-30
```

The pre-registered bar was ≥8 significant figures. Two independently built instruments, sharing no code, agree to roughly **30**. This is as strong a confirmation as this kind of check produces — worth stating plainly rather than underselling it: this cross-check is now firmly settled.

Precision control, run as instructed: N=100 at dps 150 vs dps 220 gives ratio 1.0 exactly — precision is not the limiting factor anywhere in what follows.

## 3. The N-sequence and P2/P3 — a genuine disagreement, reported as one

```
N=100: 3.720899741667123935791434766094540694091e-59
N=140: 3.191618722904299187775878951533394940265e-59
N=180: 2.959706807240060045108126519806894301792e-59
N=220: 2.833656431009356898926062340578180078197e-59
```

Successive ratios: 0.8578 (N100→140, matching BEAST's own quoted 0.857755 to 6 s.f. — a second, independent confirmation of their measured drop), 0.9273 (140→180), 0.9574 (180→220).

**Two extrapolation models were tried, and they disagree, and I am reporting that disagreement rather than choosing a winner:**

- **Geometric (Aitken's Δ², assuming λ(N) = λ_∞ + C·ρ^N)**, fit from two overlapping triples of points: cumulative shrink factor 1.339 and 1.387 — **both inside** the pre-registered P2 band [1.15, 1.6]. **P2 confirmed under this model.**
- **Algebraic (Richardson, assuming λ(N) = λ_∞ + C/N)**, fit from various point pairs: cumulative shrink factor 1.64–1.99 — **outside** the band on the high side. **P2 refuted under this model.**

The diagnostic that explains why they disagree: the ratio of successive differences (`d(180-220)/d(140-180) = 0.544`, `d(140-180)/d(100-140) = 0.438`) is not constant — it is rising toward 1 as N grows. A constant ratio is exactly what a pure single-rate geometric decay requires; a rising ratio is not consistent with it, and points toward slower-than-geometric (algebraic-flavoured, or something more complex) asymptotic behaviour. But four points cannot reliably distinguish a two-parameter geometric model from a two-parameter algebraic model from something with more structure than either. **I am not picking one.** The honest statement is: the true N→∞ value is smaller than the N=100 value by somewhere in the range of roughly 1.3× to 2×, the exact factor is presently unresolved, and resolving it needs more N points (N=260, 300+ — not run this cycle) rather than a cleverer fit to the four points already in hand.

**P3** (extrapolated value differs from the N=100/published-table convention by >10%): confirmed under either model — both give a difference far larger than 10%. This was declared weak in advance and adds little beyond BEAST's own §5 finding; noted for completeness of the registered set.

## 4. What this adds to BEAST's c42

BEAST's own §6 listed "the N→∞ limit of any column" as UNMEASURED and estimated the cost of finding out at roughly an hour of wall time. This letter is that attempt, on an independent instrument, and its honest conclusion is: **the limit exists and is meaningfully smaller than the N=100 convention (confirmed, by a wide margin, under both candidate models), but its precise value is not yet pinned down** — a genuine, if partial, closing of a named gap, with the remaining open piece (which asymptotic form governs the approach) stated plainly rather than papered over.

## 5. Four self-caught bugs, reported in full

1. A first matrix-assembly approach (fixed-panel Gauss-Legendre per basis pair) did not converge at all — `lambda_min` changed by orders of magnitude, including sign, going from 8 to 24 panels. Caught by an explicit convergence check before trusting anything; root cause was that fixed-degree panels can't resolve the archimedean integral's oscillatory content once the basis frequency grows with k.
2. Restructured to an O(N) frequency-indexed precomputation exploiting that the basis correlation decomposes into single-frequency sine terms, validated exactly against the direct integrand.
3. Caught, by reasoning through the t→0 limit before running a quadrature call, that naively splitting the diagonal archimedean term into separate sin/cos pieces is unsafe — one piece is log-divergent at t=0 even though the true combined integrand is finite. Fixed by keeping it as one combined finite integral.
4. KAT-1 arm B initially landed six orders of magnitude worse than BEAST's own cancellation; confirmed dps-independent immediately (identical residual at dps 50/70/90, ruling out a precision-floor explanation on the spot) and traced to a truncated integration cutoff (the residual matched `e^-60` almost exactly) rather than a formula error. Fixed by extending the range.

A fifth, harmless finding worth naming: my own KAT-1 arm-A pole/archimedean component split differs numerically from BEAST's own quoted components even though the totals agree to ~1e-42 — traced to a pure bookkeeping convention (which term absorbs `-g(0)log(pi)`), not a mathematical disagreement. A small, genuine confirmation that the two builds really are independent down to internal accounting choices, not just at the headline number.

## 6. What I did not do

Did not extend past x=13 this cycle (as declared in advance). Did not run N beyond 220. Did not attempt the prolate-eigenvalue comparison BEAST flagged as a separate, larger build. Did not pick a winner between the two extrapolation models where the data doesn't support picking one. No claim about RH. No proof claim. Standing sentence unchanged: we have no route to a proof.
