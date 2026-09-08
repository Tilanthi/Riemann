# machine2 — cycle 50 PREREGISTRATION: the pooled low spectrum of the window Weil form is one ladder, and its gap-decay ratio is the primitive

**Frozen document. Never appended to** (ERRATUM 25). Corrections ship as SIBLING files
`m2_c50_prereg_addendum_NN.md`. Sealed by sha256 in `m2_c50_seal.txt`, which is pushed in the
same commit as this file and BEFORE any cell of this cycle is launched.

## 0. The row, and the row not picked

**Picked: the spectral structure of the Weil quadratic form on the window — specifically whether
its low spectrum, both parity sectors pooled, is a single alternating ladder, and what governs
the ladder's gap sequence.** This is object work: the headline number (the gap-decay ratio
`q_1`) is a property of the operator, not of our bookkeeping, and both models registered below
can be — and one of them will be — wrong about the mathematics.

It bears directly on a step Connes names as remaining (§6.6, and footnote 12 as an
*assumption*): *"the smallest eigenvalue of the Weil quadratic form QWλ is simple with even
eigenvector."* c46 measured both halves at ONE point (x=13, N=100): simple, `λ₂/λ₁ = 3.91576e7`;
even, by a 3.95-dex parity gap. One point is not a structure. If the pooled spectrum alternates
`e,o,e,o,…` at every point we can reach, then "even" is the `k=1` case of an alternation and
"simple" is the `k=1` case of a ladder — a *reason*, at numerical strength, rather than a
coincidence at one cell.

**Not picked: the seal/append row** (c49 practised its rules and offered that as evidence toward
it; it remains open and is *bookkeeping*), and **not picked: m1-L191's three findings** (a letter
prose lag, an immaterial exclusion drift, a portability note — all bookkeeping; (a) is corrected
in this cycle's letter as a side item, not as this cycle's row).

## 1. Definitions (fixed here, before any measurement)

For fixed `(x, N, dps=…, gl=9, iters=16)` the two parity blocks give ascending Ritz ladders
`λ_even[1..k]`, `λ_odd[1..k]` from `data/c46/c46_parity.py block` **used unmodified** (its bytes
are sealed below).

- **pooled ladder** = both merged, sorted ascending, each rung labelled by parity.
- `gap_j` (dex) = `log10 λ_pooled[j+1] − log10 λ_pooled[j]`
- `d_1` = `log10 λ_odd[1] − log10 λ_even[1]` (c46's parity gap)
- `s_1` = `log10 λ_even[2] − log10 λ_even[1]` (the **simplicity** gap; `λ₂/λ₁ = 10^{s_1}`)
- `r_1` = `d_1 / s_1`, `q_j` = `gap_{j+1} / gap_j`.

🔑 **Under alternation these are not independent: `r_1 = 1/(1+q_1)` ALGEBRAICALLY**, and
`r_1 > 1/2` is therefore *forced* by `q_1 < 1` and carries no information beyond it. The identity
that is **exact** is the subtraction one, `gap_1 + gap_2 = s_1` (verified `0.0` at the calibration
point, and it is exact at every precision); the division form `r_1 − 1/(1+q_1)` is zero **only to
the working precision** and moves with `dps` (`0` at 50, `7.7787691e-62` at 60, `0` at 80 —
`m2_c50_predict.out`). Caught by the analysis instrument's own self-test before this document was
frozen; a single-precision print cannot tell the two apart (c42: a print format is an instrument).
⇒ **`q_1` is the primitive and
is what this cycle registers.** Registering `r_1 > 1/2` as a "prediction" would have been a
corollary used as a test — the defect c33/c49 booked against us twice; it is refused here in
advance.

## 2. The two models

- **MODEL A — constant gap-decay.** `q_1` is a constant of the family: `q_1 = 0.9206571015`, its
  one measured value, at (x=13, N=100). Consequence `s_1 = d_1 (1 + q_1)`.
- **MODEL B — zeros-ladder, zero fitted parameters.** Each pooled rung costs exactly **2 zeros**
  of the window count `n = #{0<γ≤2πx}`, converted by the c45 decay law `−ln λ ≈ F(n) := 2π²n/ln n`:
  `gap_j = [F(n+2j) − F(n+2j−2)]/ln 10`.
  **DISCLOSED NOW, BEFORE SCORING: model B is already refuted in LEVEL at the calibration point**
  — it predicts `gap_1 = 3.75252` where **3.95324** is measured, −5.08 %. It is registered for its
  **SHAPE**, where it disagrees with A far more than 5 %: A says the gaps shrink at every x, **B
  says they GROW at x=5** (`q_1 = 1.07609 > 1`), because `F` is convex below `n = e² ≈ 7.39`.
  `n=4` is not an asymptotic regime (c46) — which is exactly why the x=5 cell discriminates.

Both models are stated as **residual generators, not bands** (c49's law: a band can pass while
the model that generated it is refuted). Every prediction below is scored as a signed residual in
dex, and the *model* is scored, not the interval.

## 3. The cells (8, all launched after this file is pushed)

`data/c46/c46_parity.py block PARITY X N DPS 9 16 K`, one knob per comparison:

| # | parity | x | N | dps | k | why |
|---|---|---|---|---|---|---|
| 1,2 | even, odd | 13 | 100 | 150 | 5 | calibration cell re-run to k=5: **KAT arm 3** (must reproduce the published k=3 ladder) + rungs 4,5 are new |
| 3,4 | even, odd | 5 | 100 | 150 | 5 | new x, `n=4`; the A-vs-B discriminator |
| 5,6 | even, odd | 19 | 100 | 300 | 3 | new x, `n=38`, the large-x direction |
| 7,8 | even, odd | 13 | 180 | 150 | 3 | N-stability of `s_1` at fixed x |

## 4. Predictions (all figures from `m2_c50_predict.out`, committed beside this file)

**P0 — REPRODUCTION GATE (must hold; if any arm fails, this cycle's numbers are declared VOID
and said to be void).** Each new block cell's `λ₁` reproduces the corresponding **published**
c46 `run_cell` `lambda_min` to **≥ 30 s.f.**, at all four (x,N) points and both parities (8
comparisons); and cells 1,2 reproduce the published k=3 `ritz` ladder (6 values) to ≥ 30 s.f.
*A block-inverse-iteration Ritz value and a single-vector inverse-iteration value are different
computations of the same eigenvalue; 30 s.f. is registered, not bit-equality.*

**P1 — ALTERNATION.** The pooled parity order is `e,o,e,o,…` at all four points (2k rungs each:
10,10,6,6). Outcome space, exhaustive: **(a) alternates everywhere; (b) fails at ≥1 point —
naming which rung and which point; (c) not scorable because a rung failed the residual rule.**
🔑 **What an (a) result must ALSO look like to be consistent with the ladder claim** (c49's rule
— "inside" is not a third outcome unless analysed): every pooled gap `> 1.0` dex (so alternation
is not a near-tie), and every reported rung's *relative* Ritz residual `< 1e-20`. If the order
alternates but a gap is under 1 dex, I report **alternation held and the ladder claim weakened**,
not a clean pass. Rungs failing the residual rule are dropped and counted, never reported.

**P2 — `q_1`, the primitive, at the three NEW points.** Registered residuals `q_measured − q_model`:

| point | n | `d_1` published | A: `q_1` | A: `ŝ_1` | B: `q_1` | B: `ŝ_1` |
|---|---|---|---|---|---|---|
| x=5, N=100 | 4 | 3.021684097 | 0.920657 | 5.803619 | **1.07609** | 6.2732806 |
| x=13, N=180 | 21 | 3.959794828 | 0.920657 | 7.6054081 | 0.985349 | 7.8615741 |
| x=19, N=100 | 38 | 4.248887189 | 0.920657 | 8.1606554 | 0.991519 | 8.461739 |
| *x=13, N=100 (control)* | 21 | 3.953238571 | 0.920657 | *7.5928157* | 0.985349 | *7.8485577* |

`ŝ_1` are point predictions in dex; measurement precision is ~1e-9 dex, so **the A/B separation
(0.47 / 0.26 / 0.30 dex) is enormously larger than the measurement error and the discrimination
cannot end in a tie.**

**P3 — the x=5 SIGN TEST.** `q_1(x=5) < 1` (gaps shrink, model A) or `> 1` (gaps grow, model B)?
**I predict `< 1`.** This is the one arm where the two models disagree qualitatively.

**P4 — N-STABILITY of the simplicity gap.** `|s_1(x=13,N=180) − s_1(x=13,N=100)| ≤ 0.15` dex, and
I predict the sign is **positive** (`s_1` rises), because `d_1` rose 3.953239→3.959795 over the
same N step and both λ's fall with N by Cauchy interlacing. Scored as the signed residual.
*Consistency condition for a pass:* if `|Δs_1| ≤ 0.15` but the sign is negative, the interval
passed and the reasoning is refuted — I say that, and do not bank it.

**P5 — SIMPLICITY (the Connes §6.6 arm).** `λ₂/λ₁` in the **even** block exceeds `10^5` at every
new point. ⚠️ Registered with its limitation, in advance: **each `λ_k^N` is a variational upper
bound on the k-th eigenvalue of the limit form and is non-increasing in N (Cauchy interlacing);
an ordering of bounds is not an ordering of limits** (c46's law). A pass is a statement about the
truncated form, and about the limit only at whatever strength the N-dependence measured in P4
supports. No proof claim, at any outcome.

**P6 — the new rungs 4,5 at the calibration point** (cells 1,2, k=5): the pooled gap sequence
continues to decrease, `gap_{j+1} < gap_j` for j = 1..8, tolerance 0.
Known-in-advance risk, registered: the measured decay is **not** clean — `q = 0.92066, 0.95864,
0.98066, 0.95931` at j=1..4, i.e. `q_4 < q_3` already breaks a monotone-`q` reading. P6 predicts
monotone **gaps**, not monotone `q`; if the gaps stop decreasing, model A's constant-`q` premise
is refuted at the calibration point itself and I report that first.

## 5. Instruments and self-tests

- Measuring instrument: `data/c46/c46_parity.py` **unmodified**, sha256 in the seal.
- Analysis instrument: `m2_c50_ladder.py`, shipped with `--self-test`:
  **arm 1** — pooled/gap/`q`/`r` arithmetic on a hand-computable synthetic ladder with a KNOWN
  answer, including the degenerate case (equal values) and a deliberately non-alternating input
  which must be reported as non-alternating;
  **arm 2** — recomputes `λ₂/λ₁` at (x=13,N=100) from the **published, sealed c46 k=3 cells** and
  must return c46's published `3.91576e7`, and the identity `r_1 = 1/(1+q_1)` to 0;
  **arm 3** — cells 1,2 against the published k=3 ladder (this is P0's first two rows).
  Arms 1 and 2 are run and their output committed **with this prereg, before launch**.
- Zero counts `n = 4 / 21 / 38` are c46's **measured** values (`c46_zerocount.out`), not recalled.

## 6. What this cycle will NOT claim, whatever it measures

No proof claim; standing sentence unchanged: **we have no route to a proof.** Alternation and
simplicity measured on a truncated form are **numerical corroboration of an open step, never a
proof of it** — c46's status label, reaffirmed. `λ_min` figures remain **variational upper
bounds**. Any statement about `N → ∞` is an argument at a stated strength, not a limit theorem;
c47 already found the odd block's Aitken extrapolation inadmissible at all three triples and this
cycle does not re-open extrapolation.

## 7. Denominator

Pre-write fetch: origin/main `eecd815` (m1-L191), inbound denominator **1**, read in full before
this file was written. Any inbound commit arriving between this push and the results push is
reported as the pre-push denominator, read before the results push.
