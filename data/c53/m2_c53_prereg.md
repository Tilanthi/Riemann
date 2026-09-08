# machine 2 — CYCLE 53 PREREGISTRATION

**Registered before any target cell is launched. Pushed before launch; the launch stamp is in
`data/c53/logs/LAUNCH.txt` and must be LATER than this commit's push.**

Row: **the SECOND dislocation's index** — c51's own named open item (*"OPEN, deliberately
unregistered: the SECOND dislocation's index … Settling it needs k ≥ 8 at x=19 — the cheapest next
question. No guess registered."*).

---

## §1 OBJECT AND CONVENTIONS — INHERITED VERBATIM, NOT RE-DERIVED

From c50/c51, unchanged: the matrix is `c46_parity.build_matrix_parity(N, x, gl, parity)`
(**unmodified, imported**); a sector rung `m` (1-based) has node count `ν` = interior sign changes
of its Ritz/eigen vector, Sturm baseline `ν_even^S = 2(m−1)`, `ν_odd^S = 2m−1`, defect
`δ = ν − ν^S`. Detector knobs: grids `(1201, 4001, 12001)` × tolerances `(0, 1e-8, 1e-4)` = 9
settings, plus the 48001-point refine pass and the minimum detected lobe ratio. **THEOREM T**
(c51): node-count parity is forced by the sector, so it carries no information about the operator
and is an instrument KAT, never a prediction.

**One re-encoding is introduced, and it is declared as a re-encoding, not as a finding.** Under
alternation the pooled ladder's index of even rung `m` is `2m−1` and of odd rung `m` is `2m`, and
then `Δ(p) := ν_p − (p−1)` equals the sector `δ` of that rung **identically**. So the "pooled
defect" is c51's `δ` relabelled. It buys presentation only — one sequence instead of two — and by
c51's ERRATUM 27 law (*a claim that can only be checked on the evidence it explains is not a
mechanism*) nothing is claimed from the relabelling itself.

In that relabelling the published measurements read:

| window | pooled Δ, by index p=1,2,3,… | second dislocation |
|---|---|---|
| x=13, N=100 (c51, k=7 → 14 pooled) | `0 0 0 0 0 2 2 2 2 6 6 6 6 6` | **p₂ = 10** |
| x=13, N=180 (c51, k=5 → 10 pooled) | `0 0 0 0 0 2 2 2 2 6` | **p₂ = 10** |
| x=19, N=100 (c51, k=5 → 10 pooled) | `0 0 0 0 0 2 2 2 2 2` | **p₂ ≥ 11 — OPEN** |

Everything above is published c50/c51 data. **Every model below is calibrated on THAT and on
nothing else; no new cell exists at the time of writing.**

## §2 INSTRUMENT CHANGE, WITH ITS REASON AND ITS COST MEASURED

c50/c51 used block inverse iteration (`k` smallest per sector, 16 iterations). Its top rung is
always its worst: measured relative residuals at the top of each c51 block are 20–50 orders of
magnitude larger than the rung below (x=13 k=7: `1.95e-125` at rung 6 → `1.46e-71` at rung 7;
x=19 k=5: `2.86e-192` at rung 4 → `3.42e-96` at rung 5). Reaching k ≥ 8 that way costs ~16 LU
solves per extra rung and still delivers its deepest rung least converged.

**Cycle 53 solves the same matrix by direct symmetric eigendecomposition (`mpmath.eigsy`), which
returns every rung at once.** Measured pre-registration cost probe, disclosed in §7: at
x=13 N=100 dps150 even, matrix build **167.4 s**, full 101-pair eigendecomposition **19.9 s** —
against **1219.6 s** for c51's 7-rung block cell of the same window.

**The detector is IMPORTED from `data/c51/m2_c51_nodes.py`, not copied.** c51 had to prove its copy
was a copy (the 90/90 P0 gate); this cycle has no copy to prove. The P0 gate still runs, because an
import chain can break where a source file cannot.

⚠️ **The admission rule changes meaning and it is said here, in advance.** c50's rule
(relative residual < 1e-20) tests the **solver**, not the **basis**. For a direct eigensolver it
passes at working precision for essentially every rung, so **its firing world here is almost empty
BY ALGEBRA** — the defect my own standing law names. It is computed and reported anyway, and the
cycle's real truncation control is **the N-control of P6**.

## §3 THE REGISTERED GRID (all cells; nothing outside this list is registered)

**Stage A — `spec` (eigenvalues + vectors, NO node count):** 8 cells, `gl=9`
`{even,odd} × {(x=13, N=100, dps=150), (x=19, N=100, dps=300), (x=13, N=180, dps=150), (x=19, N=180, dps=300)}`

**Stage B — `nodes`, R = 16 rungs per cell:** the same 8 cells.

**Tier 2 — independent solver, c51's instrument BYTE-IDENTICAL (sha256 published in `m2_c53_seal.txt`,
filename changed only so it cannot shadow the import), `k=12`:** 4 cells,
`{even,odd} × {(x=13, N=100, dps=150), (x=19, N=100, dps=300)}`. Its outputs land in `data/c53/`
under c51's filename pattern with `_k12`; `data/c51/` is not written to.

**THE TWO-STAGE SPLIT IS THE PRE-REGISTRATION MECHANISM.** Stage A writes no node count. The stage-A
ladders and **Model G's numeric prediction derived from them** are pushed to `origin/main` BEFORE
stage B or tier 2 is launched, so G's value is on record before any new node count exists.

## §4 REGISTERED PREDICTIONS

Every one states, per cycle 49's finding, **what a result inside the range would have to look like
for the reasoning to be confirmed** — agreement that cannot fail is scored UNINFORMATIVE, not PASS.

**G0 — P0 gate.** The imported detector recounts **all eight** published `m2_c51_nodes_*.json` cells
from their published 40-s.f. coefficients and returns c51's published integers at all 9 knob
settings. Tolerance 0. (c51's own gate covered c50's two cells; this covers all of c51's.)

**G1 — eigenvalue cross-determination.** For each stage-A cell with a published block reference, the
eigsy ladder agrees with the published Ritz values to **≥ 30 s.f.**, ceiling-limited by the
published print width (c37/c43: an agreement depth reads the narrower party's print). Depths are
reported per rung with their ceiling.

**G2 — δ cross-determination, and this one can refute c51.** At every rung c51 published in a window
this grid covers (x=13 N=100 rungs 1–7; x=13 N=180 rungs 1–5; x=19 N=100 rungs 1–5), the eigsy δ
equals c51's published δ. Tolerance 0.
*Confirmation criterion:* rungs 1–3 are separated from their neighbours by orders of magnitude and
**any** solver gets them, so agreement there is not evidence about the solvers. The informative
rungs are the **top rung of each c51 block** (residuals `1.46e-71`, `2.71e-66`, `8.16e-84`,
`8.61e-76`, `3.42e-96`, `8.47e-91`), where the block method is furthest from converged. If
agreement holds only below those, G2 is **UNINFORMATIVE**, not a pass. **Any disagreement anywhere
is this cycle's headline and means one of the two published integer sets is wrong.**

**P1 — THE TARGET: `p₂` at x=19**, the pooled index at which Δ first leaves the value 2.
Registered models, each with **zero free parameters**, all calibrated on the published table in §1:

| model | rule | prediction at x=19 |
|---|---|---|
| **C** — constant plateau | plateau length is a window-independent 4 | **p₂ = 10 — DEAD ON ARRIVAL**, c51 measured Δ=2 at p=10 |
| **L** — window-length scaling | plateau length `∝ log x`: `round(4·log19/log13)=5` | **p₂ = 11** |
| **Z** — zero-count scaling | plateau length `∝ n`: `round(4·38/21)=7` | **p₂ = 13** |
| **G** — gap turnaround | `p₂ = 1 + M`, where `M` is the first strict local **maximum** of the pooled log-gap sequence that follows its first strict local **minimum** | **computed at stage A and pushed before stage B** |

Model G's rule is checked on the calibration window in this document: at x=13 the pooled log-gaps
are `3.95, 3.64, 3.49, 3.42, 3.28, 3.03, 2.83, 2.90, 2.91, 2.60, 2.38, 2.49, 2.42`; the first strict
local minimum is at gap index 7 and the first strict local maximum after it at 9, giving
**p₂ = 10 = the measured value**. That is a **zero-degree-of-freedom interpolation, not a
measurement** (c38's law), and it is registered as such. At x=19 the same sequence begins
`4.249, 3.956, 3.800, 3.721, 3.602, 3.399, 3.202, 3.222, 3.284` — the first strict local minimum is
again at index 7, and whether a local maximum follows is exactly what the deep rungs decide.
🔴 **G is refutable at STAGE A ALONE**: if the rule returns `p₂ ≤ 10` it contradicts an already
published measurement and dies before a single new node is counted.

*Outcome partition (declared so the space is a partition, c52's law):* `p₂ ∈ {11, 12, …, 20}` or
`p₂ > 20` or `no dislocation inside the trusted range`. **The number of surviving models is
registered as a COUNT, not as "at most one".** *Confirmation criterion:* a model counts as
CONFIRMED only if it names the occupied bin **and** no other registered model names the same bin.
Two models in the winning bin ⇒ **no discrimination**, neither is banked. (Known in advance: L and
Z occupy different bins; G's bin is unknown at the time of writing.)

**P2 — the SIZE of the second dislocation at x=19 is +4** (Δ: 2 → 6), i.e. the increment is
window-independent even though c51 proved the *position* is not. Refuted by any other increment.
*Confirmation criterion:* this only says something if a second dislocation occurs inside the
trusted range; if none does, P2 is UNMEASURED, not held.

**P3 — the THIRD dislocation at x=13.** Per sector, the first dislocation hides 1 level and the
second hides 2 (even: ν=6 then 12 and 14; odd: ν=5 then 11 and 13). Both of the following fit those
two jumps exactly and disagree about the next:
- **Model A (arithmetic):** the j-th dislocation hides j levels ⇒ increments +2, +4, **+6** ⇒ Δ: 2 → 6 → **12**.
- **Model D (doubling):** hides 1, 2, 4 ⇒ increments +2, +4, **+8** ⇒ Δ: 2 → 6 → **14**.
*Confirmation criterion:* if no third jump occurs inside the trusted range at x=13, **both are
UNMEASURED** — not "held". Exactly one bin of `{+2, +4, +6, +8, other, none-in-range}` is occupied.

**P4 — no recovery.** Δ is non-decreasing across the whole trusted range, at both windows, both
parities, both N; equivalently no eigenfunction in the trusted range has ν ∈ {5, 6}, and none at
x=13 has ν ∈ {11, 12, 13, 14}. Firing world **non-empty by measurement**: if the dislocation is a
level-ordering inversion rather than an absence, the hidden node counts reappear at deeper rungs and
this fails. *Confirmation criterion:* informative only over rungs deeper than c51 reached (sector
rung ≥ 8 at x=13, ≥ 6 at x=19); if the trusted range does not extend past those, P4 is **inherited,
not tested**.

**P5 — control with a known answer.** Δ = 0 for pooled p ≤ 5 and Δ(6) = 2, at both windows and both
N. This is c51's P2 re-measured through an independent eigensolver. A failure here is an instrument
failure, not a finding about the operator.

**P6 — the truncation control (this cycle's real admission rule).** A rung is TRUSTED iff its ν
agrees between N=100 and N=180 at the same (x, parity). Registered prediction: **the trusted depth
is at least 12 pooled levels at both windows.** Refuted if ν disagrees below pooled index 12.
*Confirmation criterion:* the N-control must be run at the same depth R=16 for it to have any
chance of firing; a trusted depth that merely equals the depth computed is not a measurement of the
truncation, and will be reported as a floor.

**P7 — the detector runs out before the basis does.** Deeper rungs have shallower lobes, and c51
measured this detector's blind-spot frontier at a lobe-depth ratio of **5.0e-3** (its most-quoted
rung, the ν=15 at x=13, sat at `0.005694` = 1.14× the frontier). Registered prediction: **at least
one rung inside the new deep range (sector rung 8–16) has a minimum detected lobe ratio BELOW
5.0e-3.** If so, verdicts are restricted to rungs above the frontier and **that restriction is a
result, not a caveat**. If no rung falls below, the frontier is not binding at this depth and P7 is
refuted — which would be good news reported as a refutation of my own expectation.

## §5 WHAT THIS CYCLE WILL NOT CLAIM

No proof claim, and **no route to a proof is in hand — in those words.** Nothing here is a statement
about the limiting operator: every eigenvalue is a variational upper bound on a truncated basis, no
`N → ∞` extrapolation is performed, and **an ordering of bounds is not an ordering of limits**
(c46). No corrected observable is authored mid-cycle (c52's V4). Windows are x=13 and x=19 only;
x=5's deep rungs are inadmissible under c50's residual rule and are not revisited.

## §6 SEAL

`m2_c53_seal.txt` carries sha256 of: this prereg, `m2_c53_spectrum.py`, the byte-identical copy of
c51's block instrument, and the two files they import that must not move
(`data/c51/m2_c51_nodes.py`, `data/c46/c46_parity.py`). **The mapper that verifies the seal ships in
the same push** (`m2_c53_seal_verify.sh`) — c50 named a mapper and omitted it; c51 fixed that; this
cycle inherits the fix. A pre-launch absence proof for every registered output name is committed
with this prereg.

## §7 PRE-REGISTRATION PROBES, DISCLOSED

1. **Timing probe on random symmetric matrices** (no window, no operator): `eigsy` on 26×26 and
   51×51 at dps 150/300. No target information.
2. **Cost probe at x=13, N=100, dps=150, even** (`/tmp/probe_build.py`): it built the published
   matrix, ran the full eigendecomposition, and printed **the eight smallest log₁₀λ**. Seven of
   those eight are published c51 values; **the eighth, `−16.807854261857`, is an unpublished
   eigenvalue that I saw before writing this prereg, and I say so.** It cannot have informed Model
   G, which needs the **pooled** ladder (both sectors) — the odd sector was not computed — and it
   is an eigenvalue, not a node count: **no node count of any unpublished rung existed anywhere at
   the time this prereg was written.**
3. **KAT** (`m2_c53_spectrum.py kat`, run before this prereg, output committed with it): planted
   spectra spanning 90 orders of magnitude, recovered at relative error `2.4e-212` (dps300) and
   `5.8e-63` (dps150), eigenvector relative residuals `9.2e-212` / `6.8e-62`. 0 fails. This is the
   dry run on a known answer for the one component c50/c51 never had to check.
4. **P0 recount** launched before this prereg and touching no target output.
