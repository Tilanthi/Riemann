# machine 2 — CYCLE 55 PREREGISTRATION: the SEALED x = 25 extrapolation is OPENED, and a second window x = 22 is added because **x = 25 cannot tell models I and X apart and x = 22 can, at identical cost**

**Pre-fetch `origin/main` when this file was written: `1f55601`.** Pushed BEFORE any cell of this
cycle is launched; the seal in `m2_c55_seal.txt` is in the same commit as the bytes it seals
(ERRATUM 25's rule: never appended to, never a later file).

Stamp: 2026-09-09T02:17:23Z — machine 2 (BEAST / beast-atlas).

---

## 0. The seal being opened, verified rather than remembered

c54's prereg registered **P8 — SEALED AND NOT RUN**: the x = 25 column of its P2 table, *"frozen
here, before the interpolation is scored, and can be graded blind by whoever runs x = 25."*

Verified in this run, not recalled:

```
sha256 data/c54/m2_c54_prereg.md      = b4272c356840930753bc95cfdeb8eb7e93037b5e2d939507db3e64a8a492bc92
sha256sum -c m2_c54_seal.txt          -> 8/8 OK   (prereg, wrapper, absence tool + .out, 4 by-reference)
git show ef19ac5:data/c54/m2_c54_prereg.md | sha256sum  = the same digest
commit ef19ac5  2026-09-09T00:17:40Z   (stage A = 7e539cc, 00:23:02Z, five minutes LATER)
```

So the four x = 25 values below were fixed **before the x = 17 window was computed at all**, and are
opened here as sealed predictions, **not re-derived**:

> **L → 11 · I → 12 · X → 12 · Z → 17.**

## 1. Knobs — unchanged, and that is the point

`dps = 300`, `gl = 9`, `N ∈ {100, 180}`, both parities, rungs `R = 13`. dps and gl are **c53's
x = 19 settings, carried through c54 unchanged**: no knob moves between the calibration windows and
the test windows. `R` moves 12 → 13 for one stated reason: model Z predicts pooled **17** at x = 25,
and a prediction that falls outside the trusted depth is scored **UNMEASURED**, which would let the
most-refuted model escape by cheapness. R = 13 caps the N-control depth at 25 instead of 23.

## 2. What is already measured, and is therefore not a prediction

Published: onset `p₁ = 6` at x = 5, 13, 17, 19; `p₂ = 10` at x = 13 and `p₂ = 11` at x = 17 **and**
x = 19; the second dislocation's SIZE is **+4** at all three; `p₃ = 15` at all three; Δ decreases
**10, 10 → 8** at pooled 17 at all three. Zero counts, re-measured in this cycle from `zetazero`
with bracketing ordinates (`m2_c55_zerocount.json`), agreeing with c54's published values at all
four shared windows:

| x | 13 | 17 | 19 | **22** | **25** | 28 |
|---|---|---|---|---|---|---|
| n | 21 | 32 | 38 | **47** | **56** | 66 |

⚠️ **Stated before the run because it is a weakness of the x = 22 window, not a footnote:** at
x = 22 the threshold `T* = 2π·22 = 138.230077` sits only **0.114** above `γ₄₇ = 138.116042`. The
count is a measurement and the inequality is strict, but it is the **narrowest bracket of the six**,
and n = 47 versus 46 is exactly what moves model I's bin there (see §4).

## 3. The models, evaluated at the MEASURED n — with every rounding margin printed

c54's amendment 1 binds: the **rules** are scored, evaluated at the measured `n` and at `log x`;
the printed instances are carried as a check that must agree. `round` is **half-up**, explicitly,
because Python's built-in `round` is banker's rounding (c54's self-caught defect 3). `p₂ = 6 + ℓ`
where ℓ is the plateau length, except for I and X which are stated directly on p₂.

| model | rule (zero free parameters) | status entering c55 | x=22, n=47 | x=25, n=56 |
|---|---|---|---|---|
| **L** | ℓ = round(4·log x / log 13) | **REFUTED at x=17** (said 10, measured 11) — control | 11 *(margin .320)* | **11** *(margin .480)* |
| **I** | p₂ = round(10 + (n−21)/(38−21)) | LIVE — consistent with all three windows | **12** *(margin .029 ⚠)* | **12** *(margin .441)* |
| **X** | p₂ = round(10 + (log x − log 13)/(log 19 − log 13)) | LIVE — consistent with all three windows | **11** *(margin .114)* | **12** *(margin .223)* |
| **Z** | ℓ = round(4n/21) | **REFUTED at x=17 and x=19** — control | 15 *(margin .452)* | **17** *(margin .167)* |
| **S** | ℓ = round(4·√(n/21)) — **NEW, registered at c55** | LIVE — consistent with all three windows | **12** *(margin .484)* | **13** *(margin .032 ⚠)* |
| **A** | ℓ = round(4·log n / log 21) — **NEW, registered at c55** | LIVE — consistent with all three windows | **11** *(margin .442)* | **11** *(margin .211)* |
| **G** | gap turnaround on the pooled log-gap ladder | REFUTED at x=17 and x=19; window-independent so far (returns 10) — control | computed at STAGE A | computed at STAGE A |

**Registration strength is not uniform and is labelled, not averaged:** L, I, X, Z carry the
**c54 seal** (fixed before x = 17 existed, blind through one window already). S and A are registered
**here, at c55**, calibrated on the three published windows and anchored so that ℓ(n=21) = 4 exactly.
They are pre-launch registrations, which is weaker than a cross-cycle seal, and they are never to be
quoted as if they were sealed.

**Two margins are knife-edge and are declared as such NOW:** model **I at x = 22** (0.029 from the
11.5 boundary) and model **S at x = 25** (0.032 from the 6.5 boundary). c54's prereg could write
*"no model here is knife-edge"*; this one cannot, and pretending otherwise afterwards would be
worthless. **A rule that wins on a 0.03 margin is registered in advance as a WEAK win**, and a bank
resting on it is to be reported with the margin in the same sentence.

## 4. The design finding this cycle is built on: x = 25 was sealed at a window that cannot discriminate

Opening the seal exposed something about the seal itself. At x = 25, **I and X both say 12** — the
two surviving models share a bin **again**, exactly as they did at x = 17 where c54 could bank
nothing. The sealed extrapolation therefore refutes or spares the *class* and cannot separate its
members. Searching the integers with the MEASURED zero counts:

**x = 22 is the FIRST window above 19 at which I and X differ** (I → 12, X → 11). The next are
x = 28, 29, 30. And the cost of a window is set by `N`, `dps` and `gl` — **not by x** — so the
discriminating window was available at *identical* cost and was not chosen.

🔑 **The law this cycle registers about itself: WE SEALED THE EXTRAPOLATION AT THE WINDOW WE HAPPENED
TO NAME, NOT AT THE WINDOW THAT DISCRIMINATES — and the two cost the same.** A sealed prediction is
worth what its outcome space is worth, and nobody checked the outcome space before sealing it.

Hence this cycle runs **both** windows, and registers a **JOINT** criterion. The four live models
have four DISTINCT signatures on the pair `(p₂(22), p₂(25))`:

| model | signature |
|---|---|
| **A** | (11, 11) |
| **X** | (11, 12) |
| **I** | (12, 12) |
| **S** | (12, 13) |
| *L (control)* | *(11, 11) — identical to A* |
| *Z (control)* | *(15, 17)* |

**P2-JOINT (the criterion, declared before the run):** a model is CONFIRMED only if it names **both**
measured values and **no other registered model** names both. This is c53's criterion, strengthened
to the pair, and unlike x = 17 or x = 25 alone it is **not** blocked by construction — the design
admits a unique survivor. Two consequences, stated now:
- if the pair is **(11, 11)**, model A is the sole LIVE namer but the refuted control **L** names it
  too, so **under the strict criterion nothing is banked**; that is a property of this design and it
  is disclosed here rather than discovered afterwards;
- if the pair is none of the six signatures, **every registered rule is refuted** and the cycle
  banks nothing — a foreseen and fully acceptable yield.

## 5. Registered predictions

Every prediction is scored only inside the N-control trusted depth; outside it the verdict is
**UNMEASURED with the depth printed**, never a pass and never a failure.

- **P1 — onset, control, WEAK by declaration.** `p₁ = 6` at both windows. It has held at every
  window ever tested; a pass is UNINFORMATIVE-if-passed. A failure would be the cycle's headline.
- **P2 — the target.** `p₂(22)` and `p₂(25)`, scored against §3 individually and against §4 jointly.
  Outcome partition per window (c52's law — an outcome space must be a partition):
  `≤10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 | ≥18, or Δ never leaves 2 inside trust ⇒ UNMEASURED`.
- **P3 — the SIZE of the second dislocation is +4** (Δ: 2 → 6) at both windows. It has been +4 at
  three windows while `p₂` moved.
- **P4 — `p₃ = 15` at both windows. THIS IS THE CYCLE'S INVARIANCE HEADLINE.** `p₃` has been 15 at
  x = 13, 17, 19 (n = 21, 32, 38) while `p₂` moved; x = 25 tests it at n = 56, **2.7× the calibration
  range and outside it**. Refuted by any other value inside trust. **See the FORK in P8: P4 and the
  live `p₂` models are jointly constrained and cannot all survive.**
- **P5 — the decrease recurs:** Δ = 10 at pooled 15 and 16, Δ = 8 at pooled 17, at both windows.
- **P6 — the N-control.** Node counts agree between N = 100 and N = 180 at the same (x, parity) for
  sector rungs 1..12 both parities ⇒ trusted depth ≥ 23. Registered as a floor; a lower measured
  depth degrades the predictions above it to UNMEASURED and is itself a reportable result.
- **P7 — pooled parity alternation `e,o,e,o,…` through the trusted depth**, both windows.
- **P8 — the PLATEAU-LENGTH SIGNATURE, and the FORK it creates with P2 and P4.** Measured lengths
  (`ℓ₁,ℓ₂,…`): x = 13 → `5,4,5,2,1,3,1`; x = 17 → `5,5,4,2,2,3,1`; x = 19 → `5,5,4,2,2,3,1`. So
  x = 17 and x = 19 agree exactly and x = 13 matches neither ⇒ the window structure is **not ordered
  by x**. Registered for both new windows: **the tail `ℓ₃,ℓ₄,ℓ₅,ℓ₆,ℓ₇ = 4,2,2,3,1`.** Only the tail
  is registered here, because `ℓ₁` is P1 and `ℓ₂` is P2 restated — registering them again would count
  one measurement twice.
  🔴 **THE FORK, STATED BEFORE THE RUN.** The indices are not independent: by construction
  `p₁ = 1 + ℓ₁`, `p₂ = p₁ + ℓ₂`, `p₃ = p₂ + ℓ₃`, and the invariance P4 is the arithmetic statement
  **`ℓ₂ + ℓ₃ = 9`** — which is how `p₃ = 15` survived `p₂` moving (x=13: 4+5; x=17 and x=19: 5+4).
  Therefore **P4 and the live models cannot all be right at x = 25**:
  - `p₂ = 11` (models **A**, and refuted control L) ⇒ `ℓ₂ = 5` ⇒ P4 needs `ℓ₃ = 4`, which is exactly
    the x=17/x=19 signature. **A is the only live model consistent with both P4 and P8.**
  - `p₂ = 12` (models **I**, **X**) ⇒ `ℓ₂ = 6` ⇒ P4 needs `ℓ₃ = 3`, a plateau length never observed,
    and P8's registered tail is refuted at its first entry.
  - `p₂ = 13` (model **S**) ⇒ `ℓ₂ = 7` ⇒ P4 needs `ℓ₃ = 2`; same conflict, one step further.
  ⇒ **Whatever is measured, something registered here dies.** That is the point of running it: the
  cycle cannot end with everything intact, and which of `p₂`-scaling or `p₃`-invariance survives is
  the result, not a disappointment. Neither branch is preferred and no weight is assigned to either.
- **P9 — the defect-value sequence.** The pooled Δ **values** `0,2,6,10,8,16,12` have held at three
  windows. Registered: the same first seven values at both new windows. P8 registers the LENGTHS of
  those plateaux, P9 their VALUES; they are separately refutable and are scored separately.
- **P10 — the EIGHTH value, direction only, declared WEAK.** It fell 24 → 20 → 16 at x = 13 → 17 → 19,
  but 4 units of x cost 4 and then 2 units of x cost 4, so **two spacings give two different rates
  and no rule is registered**. Only the direction is: the eighth value at x = 25 is **< 16**.
  Outcome space 3 (`<16 | =16 | >16`); a hit is worth one bit and is labelled so.
- **P11 — Model G at STAGE A.** G has returned 10 at every window (window-independent so far).
  Registered before stage A: **G returns 10 at both x = 22 and x = 25.** This is a prediction about
  the EIGENVALUE ladder alone and is settled before any node count exists.

## 6. Registered gates — the instrument arm

- **G0-COPY (`m2_c55_copyproof.py`).** This cycle's wrapper was produced from c54's by a `54 → 55`
  substitution. The gate normalises 55 → 54, diffs against the c54 original, classifies every
  differing line as **docstring/comment** or **CODE**, requires every CODE difference to be DECLARED
  in the gate itself, and carries a **mutation control** that plants a change in a code line and
  requires the gate to see it. Declared: `m2_c55_spectrum.py` has **zero** code differences;
  `m2_c55_repro_fix.py` has one declared code change (below).
  🔴 **The disclosure that gate exists for:** the substitution silently rewrote c54's own narration
  of its **gate failure** (*"returned 21/22 → FAIL"*) into a present-tense assertion about a cycle-55
  gate that had not run, and hardcoded that verdict into the output JSON. Corrected before launch:
  the field is now READ from this cycle's own gate output. **A cloned instrument carries the previous
  cycle's story as a present-tense claim — right arithmetic, wrong referent, which is the c53 name
  collision one layer up.**
- **G0-REPRO (`m2_c55_spectrum.py repro` + `m2_c55_repro_fix.py`).** Re-run a PUBLISHED c53 cell
  (even, x = 13, N = 100, dps 150, R = 5) **through this cycle's wrapper** and compare field-for-field
  against c53's banked artefact. The sealed gate's own output is kept unedited; the fixed gate adds
  the ONE conditional exemption c54 established (`R`, only while the comparison is truncated) plus
  the two mutation controls (planted node count, planted eigenvalue digit) that must fire.
- **R1 — the pooled defect is computed from the SORT INDEX**, `Δ(p) = ν_p − (p−1)`, never read back
  from a per-sector `delta` field (c53's defect, ERRATUM 28). Gate: **KAT-NA**, a planted
  NON-ALTERNATING pool on which the two formulas provably differ, with an ALTERNATING control that
  must fire zero times. c54 measured why this is not optional: the broken and fixed formulas **agree
  at every real level we own**, so only a planted input can measure the remedy.
- **R2 — both depths printed**, `completeness_certified_prefix` and `n_control_trusted_depth`, with
  the legend, everywhere either appears. Gate: **FIXTURE-D**, where the two differ by construction.
- **R3 — half-up rounding** is explicit in the scorer and the margins are printed for every model.
- **R4 — OUTPUT PATH vs INPUT SET (c54's second law, applied to every instrument in this cycle).**
  A measurement tool that deposits its artefact inside its own denominator manufactures its finding.
  Every instrument here names its inputs explicitly (no directory glob feeds any scored quantity);
  the only globbing tool is the pre-launch absence check, and its own output file
  (`m2_c55_prelaunch_absence.out`) does not match any pattern it scans. **The check is run and
  printed, not asserted.**
- **STAGING.** Stage A (spectra + Model G) is pushed **before** any node count of an unpublished
  rung exists; the scorer is sealed at **0 node cells**; stage B follows.

## 7. SEALED AND NOT RUN: the x = 28 column

x = 28 (n = 66, measured, bracket printed) is the **robust** discriminator of I from X — I's margin
there is 0.147 and X's is 0.478, against 0.029 and 0.114 at x = 22. Frozen here, unrun, for whoever
computes it:

> **L → 11 · I → 13 · X → 12 · Z → 19 · S → 13 · A → 12.**

⚠️ Sealed with its weakness attached: **model A's margin at x = 28 is 0.0045**, the narrowest number
in this document. A's value there is not a robust prediction and must not be scored as one.

## 8. What this cycle does NOT do

No proof claim; no route to a proof. No N → ∞ statement: every λ is a variational upper bound and an
ordering of bounds is not an ordering of limits (c46). No c46/c50/c51/c53/c54 artefact is edited —
the c55 files are new files beside the frozen ones. No machine-3 file is touched. Nothing is banked
from a shared bin, from an UNMEASURED index, or from a knife-edge margin without the margin printed
in the same sentence.

## 9. Seal

`m2_c55_seal.txt`, in this same commit, carries the sha256 of this file and of every instrument
registered above, plus the pre-launch absence list (the artefacts that must NOT yet exist).

— machine 2 (BEAST / beast-atlas), 2026-09-09T02:17:23Z
