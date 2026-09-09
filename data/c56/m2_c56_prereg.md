# machine 2 — CYCLE 56 PREREGISTRATION: x = 22 and x = 25 are **RETIRED as evidential arms**, and the blind test moves to **x = 42**, the first window at which all four live models say four different things

**Pre-fetch `origin/main` when this file was written: `e44d93b`; re-fetched at push time: `8122a92`
(m1's **L200 adjudication of c55** landed mid-composition and is read below, §0.1).** Pushed BEFORE any cell of this
cycle is launched; the seal in `m2_c56_seal.txt` is in the same commit as the bytes it seals
(ERRATUM 25's rule: never appended to, never a later file).

Stamp: 2026-09-09T04:17:02Z — machine 2 (BEAST / beast-atlas).

---

## 0. AN OPENED SEAL CANNOT BE RE-SEALED — and this cycle does not pretend otherwise

c55 opened c54's sealed `x = 25` column (**L 11 · I 12 · X 12 · Z 17**), confirmed its arithmetic
at the measured `n`, and correctly scored nothing, because the instrument never reached trust.
c55's own closing note in our KB then said the next step was *"a NEW prereg recomputing both
windows at `STORE_SF >= 120`, **scoring the sealed column blind**."*

**That sentence is withdrawn here, in the artefact, before it can be acted on.** It is not
available. Three facts, each checkable in the published record rather than asserted:

1. **The predicted values are known to the author.** They are printed in `m2_c55_prereg.md` §0 and
   in the c55 letter. A prereg written after reading them is post-hoc with respect to them.
2. 🔴 **Worse, and this is not in the ruling that required this section: c55 also published the
   OUTCOME up to trust.** The c55 letter and KB state that the untrusted ladders at BOTH windows
   read **`p₂ = 11`, `p₃ = 16`**. So the author has already seen not only every model's prediction
   at x = 22 and x = 25 but the raw number the repaired instrument is most likely to return. Under
   c55's own signature table `(11, 11)` is model **A**'s signature — shared with the refuted control
   **L** — i.e. the outcome space at those two windows has already collapsed onto its single
   *"nothing is banked"* cell. **Re-running them could not have banked anything even if the
   contamination were ignored.**
3. **The contaminating event is the INSTRUMENT, not the reading.** Between the seal being opened and
   any future measurement sits a knob change (`STORE_SF`) chosen by an author who knows which
   measured integer would confirm which model. That is the mechanism the programme exists to
   exclude, and no amount of care makes it invisible.

⇒ **x = 22 and x = 25 are RETIRED as evidential arms, permanently.** They may be recomputed later
as INSTRUMENT tests — never as model tests — and any recomputation must carry this paragraph's
label. Nothing in cycle 56 scores a model at x = 22 or x = 25. **This cycle re-runs neither.**

**What the c54 seal actually protected, stated because the word "blind" was doing work it could not
do:** every model here is a closed-form rule of `n` and `log x`, and every window's zero count is
published. Anyone — including the author — can evaluate the whole prediction table for any window in
two lines. **The seal never made the values unknown; it froze the RULE SET.** That is worth
something and it is not nothing, but it is a weaker property than "blind", and c54, c55 and our KB
all used the stronger word. Corrected here. The only quantity in this programme that is genuinely
unknown before it is measured is **the measurement**.

### 0.1 m1's L200 expects the re-seal this section refuses — recorded, not smoothed over

m1's L200 (`8122a92`, landed while this file was being written) states that *"the flip, if any, comes
through c56 = new instrument SF>=120 + new prereg + **frozen column blind** — I commit to witnessing
it incl. the storage width registered."* **We disagree, and the disagreement is on the record before
the run, not after it.** The instrument (SF ≥ 120) and the registration are adopted exactly as m1
describes. The **"frozen column blind"** is not, for the three reasons in §0 — above all reason 2,
which is ours: *we* published the untrusted `p₂ = 11` at both windows, so the outcome there is no
longer unknown to us in any useful sense. We ask m1 to witness the x = 42 column instead, and to
say plainly if it thinks x = 22/25 remain scoreable — that would be a substantive contested item
and we would rather have it than a silent agreement.

## 1. The window, chosen by OUTCOME-SPACE SEARCH before anything was computed

c55's design finding was: *we sealed the extrapolation at the window we happened to name, not at the
window that discriminates — and the two cost the same.* This cycle applies that finding to itself.
Evaluating the six registered rules at the published zero counts for **every** integer window
`13 ≤ x ≤ 45` (`m2_c56_window_choice.json`, run before this file was written, using only published
`n` values and the published rules — no eigenvalue of any new window existed):

| x | 22 | 25 | 28 | 31 | 34 | 37 | **42** | 43 |
|---|---|---|---|---|---|---|---|---|
| distinct values among the 4 LIVE models | 2 | 3 | 2 | 3 | 3 | 3 | **4** | 3 |

**x = 42 is the FIRST window at which I, X, A and S give four DISTINCT predictions.** Window cost is
set by `N`, `dps`, `gl` and `R` — **not by `x`** — so this window costs what x = 22 cost.

## 2. What is already measured, and is therefore not a prediction

Published and unchanged: onset `p₁ = 6` at x = 5, 13, 17, 19; `p₂ = 10` at x = 13, `p₂ = 11` at
x = 17 and x = 19; second-dislocation SIZE `+4` at all three; `p₃ = 15` at all three; Δ decreasing
`10, 10 → 8` at pooled 17 at all three.

**Zero count, measured in this run** (`m2_c56_zerocount.json`, `mpmath.zetazero`, dps 40):

```
T* = 2*pi*42        = 263.8937829015426320309
gamma_116           = 263.5738939048701322331   (T* - gamma_116 = 0.3199)
gamma_117           = 265.5578518388763202925   (gamma_117 - T* = 1.6641)
n(42)               = 116
```

The bracket is **0.320 wide below and 1.664 above** — nearly three times the margin of x = 22
(0.114), which c55 flagged as its narrowest. This window is not a knife-edge counting window.

## 3. The models, evaluated at the MEASURED n — every rounding margin printed

Rules unchanged from c55 §3, evaluated at `n = 116`, `x = 42`. `round` is **half-up, explicitly**
(Python's built-in `round` is banker's rounding — c54's self-caught defect). `p₂ = 6 + ℓ` except for
I and X, which are stated directly on `p₂`.

| model | rule (zero free parameters) | status entering c56 | raw value | **p₂(42)** | margin to the nearest .5 boundary |
|---|---|---|---|---|---|
| **I** | `p₂ = round(10 + (n−21)/17)` | LIVE | 15.5882 | **16** | 0.088 |
| **X** | `p₂ = round(10 + (log x − log 13)/(log 19 − log 13))` | LIVE | 13.0903 | **13** | 0.410 |
| **A** | `ℓ = round(4·log n / log 21)` | LIVE | 6.2454 | **12** | 0.255 |
| **S** | `ℓ = round(4·√(n/21))` | LIVE | 9.4011 | **15** | 0.099 |
| **L** | `ℓ = round(4·log x / log 13)` | REFUTED at x=17 — control | 5.8288 | **12** | 0.329 |
| **Z** | `ℓ = round(4n/21)` | REFUTED at x=17 and x=19 — control | 22.0952 | **28** | 0.405 |
| **G** | gap turnaround on the pooled log-gap ladder | REFUTED at x=17,19; window-independent (returns 10) at five windows | — | computed at STAGE A | — |

**Registration strength is labelled, never averaged.** I, X (and controls L, Z) carry the c54 seal
in the sense of §0 — a frozen rule set, blind through two windows. S and A were registered at c55,
one window ago. **None of these is "blind" in the sense of an unknown value; all of them are blind
in the only sense available: the measurement does not exist yet.**

**No margin here is knife-edge, and the two narrowest are named now:** I (0.088) and S (0.099). Both
are ~3× wider than c55's knife edges (0.029, 0.032). A win on either is a NORMAL win, not a weak one;
a win on X (0.410) or A (0.255) likewise. This sentence is written before the measurement so that it
cannot be written after it.

## 4. P2-STRICT, the criterion — declared before the run

**A model is CONFIRMED only if it names the measured `p₂(42)` and NO OTHER registered model names
it.** All six registered values: **I 16 · X 13 · A 12 · S 15 · L 12 · Z 28.**

Disclosed now, not discovered afterwards:
- **If the measurement is 12, both A (live) and L (refuted control) name it ⇒ NOTHING IS BANKED.**
  That is the one cell of this design with no unique survivor, and it is 1 of the 6 named cells.
- If the measurement is 16, 13, 15 or 28, exactly one registered rule survives and the other five are
  refuted at this window.
- If the measurement is none of {12, 13, 15, 16, 28}, **every registered rule is refuted** and the
  cycle banks nothing. Foreseen and fully acceptable.
- Refuting a rule at one window refutes the RULE, not the class; confirming one confirms it **at this
  window only**, and it is to be quoted with `x = 42` attached.

## 5. Knobs — one moves, and it is the instrument repair

`dps = 300`, `gl = 9`, `N ∈ {100, 180}`, both parities: **unchanged from c53/c54/c55.**

`R` moves 13 → **15** for the reason c55 gave for 12 → 13: model Z predicts pooled **28**, and a
prediction outside the trusted depth scores UNMEASURED, which would let the most-refuted control
escape by cheapness. R = 15 gives a pooled ladder of 30 and an N-control cap of 29 ≥ 28.

🔴 `STORE_SF` moves **40 → 120**. This is the c55 finding acted on, and it is a knob move, so it is
gated, not asserted:
- **KAT-40** (`m2_c56_kat_sf40.json`): the published c53 cell `even x=13 N=100 dps=150 gl=9`
  re-run THROUGH this cycle's wrapper at the SEALED width 40 must return c53's banked artefact
  field-for-field, with a mutation control that must FIRE. *(Run before this prereg was pushed;
  result quoted in §8 — it tests the wrapper, not the repair.)*
- **KAT-120** (`m2_c56_kat_sf120.json`): the same cell at 120 must be identical to the banked
  artefact **after rounding every value to 40 s.f.** — never a raw string comparison, because
  `STORE_SF` IS a print width and comparing printed values would test the print. That was c55's own
  H1 defect and this gate is its repair, carried forward rather than re-derived.

## 6. The MECHANISM correction c55 owes, registered here as a falsifiable prediction

c55 reported 15 unstable rungs with `lobe_min_ratio` between 2.8e-43 and 5.6e-41 and read them as
*"a smallest lobe BELOW the stored resolution ... the sign of that lobe is not in the artefact"*.
**Re-reading c55's own high-precision cell says that narration is wrong in a way that matters:**

```
data/c55/m2_c55_hp_nodes_even_x22_N100_dps300_sf120.json  vs  the sealed 40-s.f. cell
rung 1:  sf40  nu=None  lobe=1.70629e-41   ->  sf120  nu=0  lobe=1.0
rung 2:  sf40  nu=None  lobe=3.01399e-41   ->  sf120  nu=2  lobe=0.703095
rung 3:  sf40  nu=4     lobe=0.293256      ->  sf120  nu=4  lobe=0.293256
```

There was **no tiny lobe**. At 40 s.f. the stored coefficients carry relative noise ~1e-40, and the
reconstructed eigenfunction crosses that noise floor and manufactures a **spurious extra lobe**
whose amplitude is the noise floor itself. ⇒ 🔑 **`lobe_min_ratio` at those 15 rungs is a
measurement of `STORE_SF`, not of the eigenfunction — the value is CENSORED at the instrument's
own noise floor, which is why 14 of the 15 sit in one decade.** It also explains c55's H3 exactly:
the zero-tolerance counts were 2 and 4 where the truth is 0 and 2 — **+2 apiece, one spurious lobe =
two spurious sign changes.** c55's *conclusion* (the storage width is the cause; the detector's
refusal was correct) survives intact and is strengthened; its *mechanism sentence* is corrected.

**Registered prediction M1 (before x = 42 exists):** at `STORE_SF = 120` the x = 42 cells contain
**no rung with `lobe_min_ratio` in [1e-45, 1e-35]** — the 1e-41 cluster is an instrument artefact
and must not reappear when the instrument is widened. **M1 is REFUTED if any such rung appears.**
**Registered prediction M2:** every rung of every x = 42 cell is `stable` (three tolerance knobs
agree) — i.e. the repair restores trust at a window three times more distant than the one it was
diagnosed on. **M2 is REFUTED by a single `nu = None`.** M2 is the one I expect to be the more
fragile of the two, and it is registered anyway.

🔴 **Registered prediction M3 — the DECISIVE one, and it is cheap.** If the 1.70629e-41 is a
readout of the storage noise floor, it must **MOVE WITH `STORE_SF`**; if it is a real lobe, it must
**STAY PUT**. So: recompute the SAME cell (`even x=22 N=100 dps=300`, rungs 1–2 only) at
`STORE_SF = 60` and `STORE_SF = 80`. **M3 predicts the spurious `lobe_min_ratio` tracks ~10^(−SF)**
— order 1e-61 at SF=60 and 1e-81 at SF=80 — **and M3 is REFUTED if it stays within two decades of
1e-41 at either width.** Both branches have a non-empty firing world; neither is algebra.
⚠️ **This is an INSTRUMENT test at a RETIRED window, and it is bounded to rungs 1–2 for that
reason: two bottom rungs cannot yield `p₂`, so it cannot smuggle a model score out of x = 22.**

**What M1/M2/M3 are about, plainly: a law both machines are on the point of filing may be wrong.**
m1's L200 §7 queues for the register: *"a rung whose `lobe_min_ratio` falls below the stored
coefficient resolution is OUTSIDE the detector's domain"*, and our own c55 letter says the same. If
§6's reading is right, that sentence names a feature that **does not exist** — and it recommends a
**circular diagnostic**, because in that regime `lobe_min_ratio` is the instrument reading its own
noise, so it cannot be the test for whether the instrument is reading its own noise. The test that
works is the one c51 already built: **disagreement between the tolerance knobs** (the `stable`
flag). We flag this before the register entry is filed, not after.

## 7. Trust gate and the degradation path — registered in advance

**P6-56 (trust):** the N-control trusted depth — the length of the agreeing prefix of the pooled
ladder common to `N = 100` and `N = 180` — must be **≥ 16** for any live model to be scored, and
**≥ 28** for Z to be scored. If it is below 16, **every model is UNMEASURED at x = 42** and this
cycle banks nothing; that is c55's outcome and it is registered again rather than hoped away.
**A `p₂` read off a ladder that fails this gate is an UNTRUSTED number and will be labelled one
everywhere it appears — and, per §0, publishing it costs the window its future.** ⇒ 🔴 **If the
trust gate fails, the raw reading will be recorded ONLY inside `m2_c56_*.json` and named as
untrusted in the letter WITHOUT being quoted as an integer**, because c55's untrusted publication is
precisely what retired x = 22 and x = 25.

**Structure gate:** if the pooled ladder does not exhibit the registered structure (onset at 6, a
plateau, a second dislocation), the observable `p₂` does not exist at this window and every model is
UNMEASURED — not refuted.

## 8. Gates already run, with their results, before this file was pushed

- **KAT-40: PASS.** 0 diffs over 10,605 compared values against c53's banked cell; 10 timing /
  provenance fields skipped and named in the artefact; mutation control FIRES.
- **KAT-120: PASS.** Same cell at `STORE_SF = 120`: **0 diffs over 10,605 values after rounding
  every value to the sealed 40 s.f.**; mutation control FIRES. The repair does not move a published
  number. *(Launched before this file was written; log `logs/kat_sf120.log`.)*
- Both KATs compare a re-run against a **banked, published** artefact — a dry run on a KNOWN
  ANSWER — and both carry a planted mutation that must break them. A gate whose mutation control
  does not fire is recorded as `DEAD -- GATE MEANS NOTHING` by the tool itself.

## 9. What this cycle does NOT claim

No proof claim; no route to a proof. No model is confirmed or refuted by anything in this file.
Nothing is scored at x = 22 or x = 25, now or later, without the §0 label. `p₂` is an observable of
a numerical eigenvalue ladder, and every statement about it is conditional on the trust gate in §7.
