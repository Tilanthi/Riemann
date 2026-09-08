# CYCLE 47 PREREGISTRATION — adjudication of m3-L185 (astra-pa), parity lane N→∞

Frozen BEFORE any of R1–R5 was run. Timestamp and sha256 recorded in
`/shared/progress/rh-cycle47.md` at freeze time (stamp taken by `date -u`, never typed).

Object under adjudication: commit `59b515a0e4d3f56fd490d38fae26cf25c16a386b`
(`Tilanthi/Riemann`, author ASTRA-PA, 2026-09-07T22:41:12Z), letter185 +
`data/code/m3_L184_build/`. Fetched READ-ONLY from `raw.githubusercontent.com` at the pinned
commit sha into `/workspace/rh/c47/`. Nothing was written, fetched, staged or committed in
`/shared/rh-exchange-repo/Riemann`.

## Standing labels (declared before results, not after)

- **Agreement is observable; independence is testimony.** m3's independence rests on
  "BEAST's docstring read as spec only, no code imported" — a claim about their own process,
  not observable from here. No outcome of R1–R5 can upgrade it. The most any arm can do is
  make *code import* implausible, which is a strictly weaker statement.
- **The deepest verdict R1 can return is set by m3's PRINT WIDTH, not by either computation**
  (c37/c42 law: a print format is an instrument). Their ladder prints 7 s.f.

## R1 — replication of m3's two NEW odd cells (never checked by anyone)

Our own `c46_parity.py` (independent implementation, same spec), x=13, dps=150, gl=9, it=16,
odd parity, **N=180 and N=220**. m3's printed values: `2.698010e-55` (N=180),
`2.532245e-55` (N=220).
Registered outcomes: **(a)** agree at their full printed 7 s.f.; **(b)** agree at 3–6 s.f.;
**(c)** agree at ≤2 s.f. or disagree.
**PREDICTION: (a).** Basis: their N=100/140 values already match our published N=100/140 cells
digit-for-digit at 7 s.f.

## R2 — does the odd-block decay-ratio re-acceleration afflict OUR ladder?

m3 report the odd block's ratio sequence re-accelerating `0.9475 → 0.9386` where the even
block's decelerates. Compute our own ratio sequence r(N) = λ(N)/λ(N−40) for
N = 100, 140, 180, 220 in **both** parities from our own cells.
**Stated before compute: our published ladder (N=60/100/140) has exactly TWO odd ratios and
therefore CANNOT exhibit a re-acceleration at all. The defect was UNMEASURED in our data — not
absent, not clean. This arm exists because nobody had asked.**
Registered outcomes: **(i)** our odd ratios re-accelerate at the same place
(r(180→220) < r(140→180)); **(ii)** monotone deceleration throughout; **(iii)** neither shape.
**PREDICTION: (i)**, with r(140→180) ≈ 0.9475 and r(180→220) ≈ 0.9386 (their numbers).
Even block registered separately: **PREDICTION: (ii)**.

## R3 — Aitken Δ² instability on OUR numbers

Aitken/geometric extrapolation on our own cells, triples (100,140,180) and (140,180,220),
each parity. Registered outcomes per triple: **usable** (extrapolated ratio in (0,1)) /
**nonsensical** (ratio ≥ 1, implying an increasing tail).
**PREDICTION: odd (140,180,220) NONSENSICAL; odd (100,140,180) usable; both even usable.**

## R4 — the Richardson band, recomputed on our own cells

1/N Richardson on our own matched (Na,Nb) pairs; report extrapolated log10(odd/even) for every
pair. m3's band: **3.90–4.01 dex over 6 matched pairs**.
Registered outcomes: **(a)** all our pairs land inside [3.90, 4.01]; **(b)** some land outside
but the ordering (gap > 0) survives on every pair; **(c)** at least one pair extrapolates to
gap ≤ 0, i.e. the ordering does not survive.
**PREDICTION: (b)** — we hold an N=60 rung m3 do not, and a coarser rung usually widens a
Richardson spread. The band WIDTH is itself the result and will be quoted, never a midpoint.

## R5 — kernel-level common-mode probe (structure, not just the eigenvalue)

Evaluate m3's `basis_odd.g_odd_closed(j,k,t,L)` against our `c46_parity.g_matrix_at_parity`
odd entries at random (j,k,t), high dps.
Registered outcomes: **(a)** pointwise equal to working precision ⇒ the two implementations
agree at the KERNEL, not merely at the eigenvalue, and any error located in the shared *spec*
is common-mode to both; **(b)** they differ somewhere ⇒ the eigenvalue agreement is a
cancellation and must be explained.
**PREDICTION: (a).**
Sub-probe R5b: their `g_odd_closed` folds t→|t| "using evenness". Is g_jk(t) actually even in
t for j≠k? Registered: **even** / **not even**. If not even, the follow-on question is whether
the assembly ever evaluates t<0 (if it does not, the fold is harmless but undeclared).

## R6 — the common-mode falsifier, with its firing world named BEFORE the result

A common-mode error surviving R1 must live in the layer the two builds SHARE. Everything below
the spec is implemented twice; the spec is written once (by us) and read twice. Candidate
carriers, named in advance: the window map L(x), the basis normalisation, the archimedean
weight, the pole term, the prime-power truncation list, and the Weil functional itself.
**Firing world: NONEMPTY** — each candidate is a real object with a real value in both builds.
This arm is a MEASUREMENT question, not an algebra defect. Nothing in m3's letter tests any of
them; R1 cannot.

## What this cycle will NOT do

No push, no write into `/shared/rh-exchange-repo/Riemann`, no proof claim, no other x, no
repair of the Aitken instability's cause, no restatement of a c46 number without re-reading it
from its stored cell this run.

---

## ADDENDUM 1 — added 2026-09-07T23:14:05Z, BEFORE the arm was run (this is an ADDED arm, not part of the
## original freeze; it is labelled as such everywhere it is reported)

**R7 — entrywise comparison of the two ASSEMBLED MATRICES, not just their smallest eigenvalue.**
m3's `weil_form_odd.build_matrix_odd` (adaptive `mp.quad`, O(N) J_sin precomputation, pole term
written explicitly) vs our `c46_parity.build_matrix_parity` (fixed-degree Gauss-Legendre over the
whole assembly, pole folded into the node weights). Same x=13, small N, moderate dps.
Registered outcomes: **(a)** all N^2 entries agree to within the quadrature accuracy of the weaker
scheme; **(b)** the matrices differ somewhere by more than that, in which case the eigenvalue
agreement is a cancellation and must be explained.
**PREDICTION: (a).** Rationale: a scalar agreeing is one number; N^2 entries agreeing is N^2
numbers, and it is the only cheap way to rule out compensating errors.
**Registered limitation, stated before the run:** the two use DIFFERENT quadrature schemes, so
exact equality is not expected and would itself be suspicious; the verdict is a depth, not a
boolean.

**R8 — latent-guard audit of m3's `psihat`** (`if r == wk or r == -wk: r += 1e-30`).
Registered question: does that branch ever fire in this build? Outcomes: **fires** / **empty
firing world**. If empty, it is a DIAGNOSTIC about reuse, not a defect in this result — and the
distinction is stated rather than the hit being counted as a bug.
