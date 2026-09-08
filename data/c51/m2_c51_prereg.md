# machine2 — CYCLE 51 PREREGISTRATION: the nodal ladder, registered, and tested at windows that did not produce it

**This file is pushed BEFORE any registered cell is launched.** Its instruments are sealed by
sha256 below; the eight target outputs are proved ABSENT from the repository in the same push.
No proof claim. Standing sentence unchanged: we have no route to a proof.

## 0. Duplicate check and denominators

Fetched before writing: local clone was at `ddf0172`, `origin/main` at **`907221c`** — inbound
denominator **1**, m1-**L192** (m2-c50 adjudicated UPHELD in full at primary; 58 checks, 0 failed;
three bookkeeping findings: the letter's §2 table cell `39.90` against the artefact's `40.0`, the
working-tree layout of `m2_c50_scores.out`, and the on-the-line edit in `ddf0172`). Read in full
before this file was written. Nothing unread behind us.

**Row selection, stated because the delegation required it.** Picked: the **nodal-ladder +2
dislocation** — c50's most-quoted sentence and its only wholly UNREGISTERED arm. Rejected: (a) the
x-drift of `q_1`, which needs ≥5 new x points with an N-control at each and does not fit beside a
registration cycle — a half-powered version would be exactly the "rate fitted to three points" the
delegation warns against; (c) our own kills **C8/C24/C17**, which a repo-wide grep confirms are
**still untested** (last mention anywhere: 2026-09-03, m1's `[UNVERIFIABLE-LOCALLY — not asserted
wrong]`), but which live in the trace-field lane cycle 10 closed as a dead classifier.

## 1. The object, and what c50 actually established

`λ_even(x,N)`, `λ_odd(x,N)`: Ritz ladders of the Weil quadratic form on the window `(−L/2, L/2)`,
`L = ln x`, from the unmodified `data/c46/c46_parity.py`. For a Ritz vector `v` of sector rung `m`,
`ν_s(m)` is the number of interior sign changes of `φ(t) = Σ_a v_a nr_a {cos,sin}(ω_a t)`.

c50 measured, at **x=13, N=100, dps=150 only**:

| sector rung m | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| `ν_even` | 0 | 2 | 4 | 8 | 10 |
| `ν_odd`  | 1 | 3 | 7 | 9 | 15 |

Against the Sturm–Liouville baseline `ν_even^S(m) = 2(m−1)`, `ν_odd^S(m) = 2m−1`, the **defect**
`δ_s(m) = ν_s(m) − ν_s^S(m)` is

    δ_even = (0, 0, 0, 2, 2)        δ_odd = (0, 0, 2, 2, 6)

i.e. pooled: exact for five rungs, `+2` for four, `+6` at the tenth (uncertified) rung.

## 2. A DERIVATION, made before any cell runs, that changes what may be claimed

**THEOREM T.** On a symmetric window an even function has an EVEN number of interior sign changes
and an odd function an ODD number.
*Proof (object).* If `φ(−t) = φ(t)`, the sign pattern is palindromic, so sign changes occur in
`t ↔ −t` pairs and none occurs at `t = 0` (the two sides carry the same sign); the total is even.
If `φ(−t) = −φ(t)` then `φ(0) = 0` and the sign flips across `0`, contributing exactly one, with
the rest again in pairs; the total is odd. ∎
*Proof (instrument).* Every grid used here is `t_i = −L/2 + L(i+1)/(npts+1)`, symmetric about 0 and
containing `t = 0` for odd `npts` (1201, 4001, 12001, 48001 all odd); an odd `φ` is exactly 0 there
and is removed by the significance filter, so the same pairing argument applies to the sampled
sign sequence. **KAT'd** (`m2_c51_kat.py` arm K3): 0 violations in 17 sealed test functions.

**COROLLARY C1, and it is a correction to our own letter.** Let `δ(m)` be the pooled defect. Given
T, `δ(m)` is even for all `m` **iff** `ν(m) ≡ m−1 (mod 2)` **iff** the sector labels alternate
(with rung 1 even, as measured). So c50 §8's "**the dislocation is EVEN, and that is why
alternation survives it … a weaker and more robust mechanism**" is **not weaker and is not a
mechanism**: it is an EQUIVALENT RE-ENCODING of the alternation it claims to explain. Node counts
can corroborate alternation only through their **magnitudes**; their **parities** are forced by the
sector and carry no information about the operator. c50's other nodal sentence — that the node
counter and the completeness certificate independently agree rung 10 is not the 10th — is a
**magnitude** claim (`+6` where certified rungs moved `+1`) and is untouched by C1.

⇒ Consequently **"every dislocation is even" is NOT registered as a prediction** (that would be
c33/c49/c50's defect: a corollary used as a test). It is an INSTRUMENT check: a violation means the
detector is broken, never that the operator surprised us. An ERRATUM against c50 §8 will be filed
with this cycle's letter whatever the cells return.

## 3. The instrument, and the blind spot it measures rather than asserts

`m2_c51_nodes.py` copies c50's `block_with_vectors` and `sample_and_count` **verbatim** (a new file,
never an edit to the registered one) and adds: reference lookup at any `k`; the Ritz residual
computed from our own vectors so the admission rule is applied here by measurement; a REFINE pass
at `npts = 48001, tol = 0`; the minimum detected lobe amplitude; and a KAT.

**The KAT is against sealed integers, and it has already run** (before this prereg, on no cell of
this cycle — it touches no target output): `m2_c51_kat.json`.
- **K1**: `cos(ω_j t)` has exactly `2j` interior sign changes, `sin(ω_j t)` exactly `2j−1`
  (analytic). 12 functions, `j = 1..6`, **12/12 exact at all 9 knob settings**.
- **K3 (Theorem T)**: **0 parity violations**.
- **K2 — the blind spot, MEASURED**: `φ_c(t) = cos(ω_9 t) + c` has exactly **18** interior sign
  changes for every `c < 1` (analytic, sealed), with lobe depth ratio `(1−c)/(1+c)`. Measured:

  | c | depth ratio | 1201 (tol 0 / 1e-8 / 1e-4) | 4001 | 12001 | truth |
  |---|---|---|---|---|---|
  | 0.9 | 5.3e-2 | 18/18/18 | 18/18/18 | 18/18/18 | 18 |
  | 0.99 | 5.0e-3 | 18/18/18 | 18/18/18 | 18/18/18 | 18 |
  | 0.999 | 5.0e-4 | 16/16/16 | 18/18/18 | 18/18/18 | 18 |
  | 0.9999 | 5.0e-5 | 8/8/**0** | 18/18/**0** | 18/18/**0** | 18 |
  | 0.99999 | 5.0e-6 | **0/0/0** | 4/4/0 | 16/16/0 | 18 |

  🔑 **A STABILITY SWEEP CAN BE STABLY WRONG.** At `c = 0.99999` the coarsest grid returns **0 at
  all three tolerances** — "stable across every setting" and wrong by 18. And the significance
  filter c50 introduced to fix the skipped-zeros defect is itself the **first** setting to erase
  real crossings (`tol = 1e-4` loses all 18 at `c = 0.9999`, where `tol = 0` on the same grid keeps
  them). A knob sweep measures reproducibility; only a planted lobe of known depth measures
  resolving power. **Measured frontier: all nine settings are exact down to a lobe depth ratio of
  5.0e-3, and not below.**

## 4. Registered predictions

Scope: only rungs that are **admitted** (c50's rule: relative Ritz residual `< 1e-20`, applied by
measurement inside the instrument) **and knob-stable** are scored; every drop is reported as a
COUNT with its reason, never as a ratio.

- **P0 — GATE (reproduction + portability).** `m2_c51_nodes.py recount` re-counts c50's PUBLISHED
  coefficient arrays with this file's detector: 2 parities × 5 rungs × 9 knobs = **90 integers**,
  which must equal c50's published integers exactly. Threshold **90/90**. Below that the copy is not
  a copy and **nothing else in this cycle is reported**. Also exercised from a fresh clone.
- **P1 — STURM PREFIX at the three new windows** `(x=5,N=100)`, `(x=19,N=100,dps300)`,
  `(x=13,N=180)`: `δ_even(m) = 0` for `m ≤ 3` and `δ_odd(m) = 0` for `m ≤ 2`, over admitted rungs.
  Tolerance **0**. Any nonzero refutes.
- **P2 — Model N's onset is universal.** The first sector rung with `δ ≠ 0` is **even m = 4, odd
  m = 3** at all three new windows and in the deep `k=7` re-run of the calibration window.
  Outcome space, a PARTITION: **HELD** (onset equals the pair) / **REFUTED** (a different index,
  reported with its value) / **CENSORED** (no defect within the admitted rungs — explicitly **not**
  a pass, and it weakens any HELD elsewhere).
- **P3 — the first defect is exactly `+2`** in each sector at every window. Any other value refutes.
- **P4 — the N-control.** At `x=13`, `N=180` (1.8× the basis of the calibration window) the onset
  pair is unchanged. ⚠️ **P4 is NOT independent of P2**: it is P2's `x=13,N=180` conjunct, registered
  separately only because its READING differs (operator vs truncation, not universality in x). It is
  reported once and never counted twice — the c50 law that two registered quantities must have their
  algebra checked before both are registered.
- **P5 — the deep arm.** At `x=13, N=100, k=7` (two sector rungs beyond anything c50 computed), `δ`
  is **non-decreasing in m** in each sector over the admitted rungs. A decrease refutes.
  (`δ` **even** is *not* registered — Theorem T makes it automatic. See §2.)
- **P6 — THE ABSOLUTE REFUTATION TEST of Model N** ("Sturm-exact then a fixed dislocation, uniform
  in x and N"): the complete admitted defect vectors at each new window must equal
  `δ_even = (0,0,0,2,2)` and `δ_odd = (0,0,2,2,6)`, integer for integer, tolerance **0**.
  🔴 **This verdict is reached with no reference to any competing model, and it is the one that
  decides whether Model N is true.** A single mismatch refutes Model N even if Model N wins P8
  outright, and the letter must be readable as "**N won and N is refuted**" without contradiction.
- **P7 — instrument prediction.** At every admitted rung, the REFINE count at `npts = 48001, tol = 0`
  equals the 9-knob consensus, and the minimum detected lobe amplitude ratio exceeds the K2 frontier
  `5.0e-3`. If either fails, the counts sit at or inside the detector's measured blind spot and
  **no object claim may be drawn from them** at that rung.
- **P8 — the comparison, which is NOT a validation.** Three onset models scored on the same cells:
  - **N (index)**: onset `(4,3)` everywhere. 0 free parameters after calibration on `x=13,N=100`.
  - **SCALING (zeros)**: onset `∝ n`, the measured window zero count `n = #{0 < γ ≤ 2πx}` = 4 / 21 /
    38 at x = 5 / 13 / 19 (c46, `NZERO`), calibrated on `x=13`: `onset = max(1, round_half_up(4n/21))`
    even, `max(1, round_half_up(3n/21))` odd ⇒ **(1,1) at x=5**, **(7,5) at x=19** (i.e. even
    predicts *no defect through m=5*), **(4,3) at x=13,N=180**.
  - **THRESHOLD (eigenvalue)**: the defect switches on at a fixed `λ`. Calibrated: `Λ*` lies in
    `(−43.9259, −40.6436)` in `log10 λ` (last exact / first defective pooled rung at the calibration
    window). Rule: `δ = 0` at every rung with `log10 λ ≤ −43.9259`, `δ ≠ 0` at every rung with
    `log10 λ > −40.6436`; a rung strictly inside the interval is **AMBIGUOUS** and is excluded from
    this model's score, declared here rather than at read time.
  P8's tally is reported **in the same sentence as P6's verdict**, never alone.

## 5. Cells launched (target outputs, proved absent in this push)

Eight registered cells, `c46_parity.py`'s build and c50's iteration, `GL=9`, `ITERS=16`:

| # | file | window |
|---|---|---|
| 1 | `m2_c51_nodes_even_x5_N100_k5.json` | x=5, N=100, dps=150, k=5 |
| 2 | `m2_c51_nodes_odd_x5_N100_k5.json` | x=5, N=100, dps=150, k=5 |
| 3 | `m2_c51_nodes_even_x19_N100_k5.json` | x=19, N=100, dps=300, k=5 |
| 4 | `m2_c51_nodes_odd_x19_N100_k5.json` | x=19, N=100, dps=300, k=5 |
| 5 | `m2_c51_nodes_even_x13_N180_k5.json` | x=13, N=180, dps=150, k=5 (N-control) |
| 6 | `m2_c51_nodes_odd_x13_N180_k5.json` | x=13, N=180, dps=150, k=5 (N-control) |
| 7 | `m2_c51_nodes_even_x13_N100_k7.json` | x=13, N=100, dps=150, k=7 (deep arm) |
| 8 | `m2_c51_nodes_odd_x13_N100_k7.json` | x=13, N=100, dps=150, k=7 (deep arm) |

plus `m2_c51_p0_recount.json` (P0), `m2_c51_kat.json` (already produced, no cell touched), and the
grader's `m2_c51_scores.{json,out}`.

Every cell self-tests against the published block cell for its window at the largest available `k`
and refuses to report if the agreement is below **30 s.f.** ⚠️ That depth is **CEILING-LIMITED by
the published cells' print width (40 s.f.)** and is stated as a ceiling, never as an accuracy
(c37/c47).

## 6. Seal

sha256 of the instruments, fixed before launch:

```
INSTRUMENT_SHA256_BEGIN
109a6e3a8dcc82b49850baa906ec38864e85e52b0714e0a30e396096173c6581  m2_c51_nodes.py
6e8661d96275176fb8063f6e563b2062c9e0dcbcbcb67b9c00daf984e538c137  m2_c51_score.py
6b647506cdc798dc21113602357ec5555922815af24335260dc25239cef51c85  m2_c51_seal_verify.sh
INSTRUMENT_SHA256_END
```

The mapper that verifies this block is `m2_c51_seal_verify.sh`, **shipped in this same push**
(c50's prereg named a mapper and omitted it; c49: a seal whose objects are unpublished is a seal
nobody can produce). `m2_c51_seal_verify.sh --absence` re-proves the eight target outputs absent.

Pre-launch absence of the eight target outputs is proved in the same push by
`m2_c51_prelaunch_absence.out` (a repository-wide search for each filename, run at the pre-push
HEAD).

## 7. What this cycle does not claim

Every `λ_k^N` is a variational upper bound, non-increasing in N; an ordering of bounds is not an
ordering of limits (c46), and a node count of a Ritz vector is a property of the truncated form.
Nothing here is a statement about the limiting operator unless the N-control says so, and the
N-control moves one knob at one window. No proof claim. Standing sentence unchanged: we have no
route to a proof.
