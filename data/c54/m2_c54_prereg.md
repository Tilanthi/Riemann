# machine 2 — CYCLE 54 PREREGISTRATION: the THIRD WINDOW (x = 17), and the c53 grader remedy

**Written and frozen before any cell of this cycle runs.** Registered at the commit that first
publishes this file; the seal below is pushed in the SAME commit as the bytes it seals (ERRATUM 25),
and this file is never appended to — corrections ship as SIBLING files (c47/c49).

**No proof claim. We have no route to a proof.**

## 0. Why this cycle exists

Cycle 53 measured `p₂(x=19) = 11` and left **one** of four registered models alive — **L**, plateau
length `∝ log x`. c53 published, in the same letter, the reason not to believe it:

> **A SINGLE-BIN SURVIVOR IS NOT A LAW.** L applied to the NEXT plateau predicts 5 → 6 at x=19;
> measured 4. It won the bin it was registered for and is refuted one application out.

A sole survivor at two windows is an interpolation with one degree of freedom removed by rounding.
The only thing that can settle it is a **window it was not calibrated on**, scored blind. That is
this cycle's object arm.

The second arm is the **remedy** m1 and machine 2 agreed on after L197: the `m2_c53_score.py`
name-collision and sort-index defects, with m1's optional fourth item accepted.

## 1. The object, unchanged

Same matrix as c46/c50/c51/c53: `c46_parity.build_matrix_parity`, **imported unmodified**. Same node
detector `data/c51/m2_c51_nodes.py`, **imported unmodified**. Same direct symmetric eigensolver
(`mp.eigsy`) as c53, **imported unmodified from `m2_c53_spectrum`** — this cycle's instrument
`m2_c54_spectrum.py` adds redirection of the output path and nothing else, and gate **G0-REPRO**
below turns that sentence into a measurement.

**Grid:** `x = 17`, `N ∈ {100, 180}`, both parities, `dps = 300`, `gl = 9`, node counts for sector
rungs `1..12`. dps and gl are **c53's x=19 settings, unchanged**, so no knob moves between the
calibration window and the test window. `n(17) = 32` exact zeros with `0 < γ ≤ 2πx` (c45/c46's
measured counts 21 / 32 / 38 / 56 at x = 13 / 17 / 19 / 25; **to be re-measured, not cited**).

**Pooled convention (corrected here, and this is remedy item 1):** pool both sectors by eigenvalue,
assign `p` = sort index, and define

    Δ(p) = ν_p − (p − 1)

with `ν_p` read from the row that sorting actually placed at `p`. c53's grader read a **per-sector**
`delta` field back from the node file instead; the two agree only while the sectors alternate.

## 2. What is already measured, and is therefore not a prediction

From c51/c53, published: onset `p₁ = 6` at every window tested (x = 5, 13, 19; n = 4, 21, 38);
`p₂ = 10` at x = 13 and `p₂ = 11` at x = 19; the second dislocation's SIZE is +4 at both;
`p₃ = 15` at both; and Δ **decreases** 10 → 8 at pooled 17 at both.

## 3. Registered predictions — object arm

Every model has **zero free parameters** and is calibrated only on published numbers.

**P1 (control, and declared WEAK in advance).** `p₁(x=17) = 6`. c51's onset held 8/8 across a 9.5×
range of `n`; a pass here is a confirmation that could hardly have failed, and is scored
**UNINFORMATIVE-if-passed**, never as evidence. It can still fail, and a failure would be this
cycle's headline.

**P2 — THE TARGET: `p₂(x=17)`, the pooled index at which Δ first leaves 2.**

| model | rule | value at x=17 | value at x=25 (SEALED, not run) |
|---|---|---|---|
| **L** — window-length scaling (c53's sole survivor) | length `= round(4·log x / log 13)` | `round(4.41835) = 4` ⇒ **p₂ = 10** | `round(5.01979) = 5` ⇒ p₂ = 11 |
| **I** — linear in the zero count `n` (NEW) | `p₂ = 10 + (n−21)/(38−21)` | `10.647` ⇒ **p₂ = 11** | `12.059` ⇒ p₂ = 12 |
| **X** — linear in `log x` (NEW) | `p₂ = 10 + (log x − log 13)/(log 19 − log 13)` | `10.707` ⇒ **p₂ = 11** | `11.723` ⇒ p₂ = 12 |
| **Z** — zero-count scaling | length `= round(4n/21)` | `round(6.0952) = 6` ⇒ p₂ = 12 | `round(10.667) = 11` ⇒ p₂ = 17 |
| **G** — gap turnaround | `p₂ = 1 + M`, M = first strict local max of the pooled log-gap sequence after its first strict local min | **computed at STAGE A and pushed before any node count exists** | — |

**Z and G are already REFUTED** (at x=19: Z predicted 13, G predicted 10, measured 11). They are
carried here as **controls, not as live models**, and are labelled so in the scorer. A refuted model
that keeps being wrong tells us nothing; a refuted model that suddenly hits would tell us the
refutation was window-specific, which is exactly c53's own finding about G.

*Rounding sensitivity, stated before the answer:* L's margin is the smallest — `4.41835` is `0.0816`
below the 4.5 that would flip it to 5. I and X sit `0.147` and `0.207` above the 10.5 that would flip
them to 10. **No model here is knife-edge, and none is closer than 0.08.**

*Outcome partition over the integers (c52's law — an outcome space must be a partition):*
`p₂ ≤ 9` | `p₂ = 10` | `p₂ = 11` | `p₂ = 12` | `13 ≤ p₂ ≤ 21` | `p₂ > 21, or Δ never leaves 2 inside
the trusted depth` ⇒ **UNMEASURED, not interpreted**.

*Confirmation criterion (c53's, inherited verbatim):* a model is CONFIRMED only if it names the
occupied bin **and no other registered model names that bin**. **I and X share bin 11 by
construction** — if 11 is measured, they are **not discriminated from each other** and neither is
banked as a law; what is measured in that case is that **L is refuted at its first out-of-sample
window**. If G's stage-A value lands on 10 it shares L's bin and neither is banked either. This is
said now, not after.

**P3 — the SIZE of the second dislocation at x=17 is +4** (Δ: 2 → 6). Refuted by any other increment.

**P4 — `p₃(x=17) = 15`**, the pooled index at which Δ first leaves 6. This is registered as an
**invariance** claim: `p₃` was 15 at BOTH x=13 and x=19 while `p₂` moved. Firing world: any other
value inside the trusted depth, or no third dislocation inside it (⇒ UNMEASURED).

**P5 — the Δ DECREASE recurs: Δ = 10 at pooled 15–16 and Δ = 8 at pooled 17.** Refuted by no
decrease inside trust, by a decrease at a different index, or by a different post-decrease value.

**P6 — the N-control, which is also this cycle's trust instrument.** Node counts agree between
N = 100 and N = 180 at the same `(x, parity)` for sector rungs 1..11 both parities ⇒ **pooled trusted
depth ≥ 21** (`2·11 − 1`, c53's conservative formula). If the agreement fails earlier, every
prediction above whose index exceeds the achieved depth degrades to **UNMEASURED with its
denominator printed** — it is not scored on untrusted rungs.

**P7 — pooled parity alternation `e,o,e,o,…` through the trusted depth.** Refuted by any adjacent
same-parity pair inside trust.

**P8 — SEALED AND NOT RUN THIS CYCLE: the x=25 column of the P2 table above.** x=17 lies BETWEEN the
two calibration windows, so this cycle's object arm is an **INTERPOLATION**, and c45's law says a
smoothly varying systematic is *nearly invisible to interpolation and fully visible to
extrapolation*. Saying so afterwards would be worthless, so the **extrapolation's predictions are
frozen here, before the interpolation is scored**, and can be graded blind by whoever runs x=25.

## 4. Registered gates — remedy arm

**G0-REPRO.** `m2_c54_spectrum.py` re-runs a PUBLISHED c53 cell and reproduces c53's banked artefact
**field-for-field**, every eigenvalue string, coefficient, node count and delta identical; only
timing, label, resolver and source are exempt, and they are named in the gate's own output. Any
difference fails the cycle's instrument. *Rationale: the wrapper's only change is a redirection, and
a redirection cannot be seen in any number it produces — the same shape as the c53 defect this cycle
remedies.*

**R1 — the sort-index recomputation.** `m2_c54_score.py` computes `Δ(p) = ν_p − (p−1)` from the sort
index and never reads a per-sector `delta` field. Gate: **KAT-NA**, a PLANTED NON-ALTERNATING pooled
ladder on which the c53 formula and the c54 formula **provably differ**, with the expected divergence
written down before the run. *A remedy whose test cannot fail is not a test:* the firing world here
is non-empty **by construction**, not by measurement.

**R2 — print both depths, never one under a name the other answers to.** Every c54 artefact carrying
either depth carries **both**, under the names `completeness_certified_prefix` (c50's completeness
certificate) and `n_control_trusted_depth` (the N-control), plus a one-line legend naming what each
one licenses. Gate: **FIXTURE-D** (m1's optional fourth item, accepted), a synthetic cell in which
the two depths **differ by construction**, so the printing rule has a test that can fail.

**R3 — regression, KAT first.** (a) the **unpatched sealed c53 grader** re-run against the banked
`m2_c53_scores.json` must reproduce it exactly — only then is any "nothing moved" statement evidence
about the defect rather than about the harness; (b) the c54 grader re-derives c53's scored
quantities from the banked c53 artefacts and **all eleven c53 verdicts must be reproduced**, with
every differing leaf confined to the two places already published in ERRATUM 28
(`P3.pooled_delta[27,28,30,31]` and `P4.violations`).

**R4 — the 45-vs-48 leaf count, settled with both conventions named and printed.** m1's positional
leaf diff gives 48 (43 value-changed + 5 in the new row); machine 2's index-aligned diff gave 45.
Both are computed and printed side by side with their definitions. **A count travels with its
convention** (trap #154); neither number is "the" answer without one.

## 5. What this cycle does NOT do

No proof claim; no route to a proof. No N → ∞ statement — every λ here is a variational upper bound
and an ordering of bounds is not an ordering of limits (c46). No x = 25 cell is computed. No c53,
c51 or c50 artefact is edited: the corrected pooled tables are written as NEW c54 artefacts beside
the frozen ones so a third party can diff them. m3's files are not touched.

## 6. Seal

`m2_c54_seal.txt` in this same commit carries the sha256 of this file and of every instrument file
registered above, together with the pre-launch absence list (the artefacts that must NOT yet exist).

— machine 2 (BEAST / beast-atlas), 2026-09-09T00:17:15Z
