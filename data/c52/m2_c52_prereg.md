# machine 2 — CYCLE 52 PRE-REGISTRATION: the x-drift of `q_1`, as its own cycle

**Written and pushed BEFORE any registered cell is launched.** The launch time and this commit's
push time are both recorded in `/shared/progress/rh-cycle52.md`; the order is the registration.

Subject is row (a) of my cycle-51 orientation, which I rejected there on cost: *"an honest attack
needs a pre-registered functional family plus an N-control at EACH x."* This is that cycle.

---

## 0. THREE CORRECTIONS TO THE COMMISSION, MADE BEFORE THE DESIGN

**C1 — "a drift that moves with N at any x is an N-artefact at that x" has an EMPTY FIRING WORLD.**
Every `λ_k^N` here is a Rayleigh–Ritz value on a basis nested in N: a variational UPPER bound,
non-increasing in N. So `q_1` moves with N at every x, necessarily, forever. Applied as worded the
rule returns "artefact" at all 12 x by algebra before a single eigenvalue exists, and its clean
verdict can never fire. That is the falsifier-with-an-empty-firing-world defect of my own standing
laws, of the **ALGEBRA** kind. ⇒ **N is registered as a COVARIATE, not as a pass/fail** (P5): the
question that can actually kill the finding is whether the N-sensitivity *grows with x* fast enough
to manufacture the drift.

**C2 — AT FIXED N THE INSTRUMENT IS NOT FIXED ACROSS x, AND IT DEGRADES IN THE DIRECTION OF THE
REPORTED EFFECT.** The basis is `cos/sin(2πjt/L)`, `j ≤ N`, on a window of length `L = log x`; the
resolved frequency ceiling is `ω_max = 2πN/L`. Holding N fixed holds a COUNT fixed while the thing
it resolves changes: over this grid `L` runs 1.386 → 3.136, so resolution falls **2.26×** along the
very axis under study. Direction, measured in c50: `q_1(x=13)` FELL 0.00372 from N=100 to N=180, so
**under-resolution inflates `q_1`**, and larger x is less resolved at fixed N. A fixed-N x-series
therefore carries a built-in bias **of the same sign as the drift it reports**. ⇒ the cycle runs the
fixed-N series **and** an isoresolution series `N_iso(x) = round(100·log x/log 5)` (constant `N/L`,
anchored at the published x=5 cell), and **the difference between the two is the reportable object**
(P4). *(V7: c51's stability-sweep blind spot was found on the NODE detector, which is not used here.
The transferable part is that a sweep over `dps`/`iters`/`gl_degree` cannot see C2, because every
one of those settings shares the same basis truncation — knob-stable and wrong in c51's exact sense.
Bias direction stated above: if present it MANUFACTURES the finding, it does not erase it.)*

**C3 — "significance" and "power" have no statistical meaning here.** Every cell is deterministic;
there is no sampling noise. The error bar is entirely systematic. Power arithmetic below is
**signal-to-systematic**; randomness enters only through LABEL permutation nulls, which test the
ORDERING and never the rate.

---

## 1. OBJECT AND CONVENTIONS (inherited verbatim, not re-derived)

`q_1 = gap_2 / gap_1` of the pooled parity ladder, conventions exactly as c50's prereg §1:
`gap_j = log10 λ_pooled[j+1] − log10 λ_pooled[j]`; pooled = admitted even ∪ odd Ritz values, sorted;
rung admission = relative Ritz residual `< 1e-20`; completeness certificate = pooled rungs at or
below `T = min(λ_even[k], λ_odd[k])`. `q_1` is REPORTED ONLY where the certified prefix is ≥ 3.

- MEASURING instrument: `data/c46/c46_parity.py block`, **unmodified**.
- POOLING instrument: `data/c50/m2_c50_ladder.py` `load_block` + `pool`, **imported unmodified**.
  Re-typing those conventions would create a second definition that can silently diverge from the
  one the published numbers were made with.
- NEW code, all in `m2_c52_qdrift.py` + `m2_c52_grid.py`: the exact zero counter `n(x)`, the per-x
  table, the covariate `S_N(x)`, the two axis discriminators, the isoresolution comparison, three
  rate families, two permutation nulls.

## 2. THE GRID (a rule, printed by `m2_c52_grid.py`, sealed)

- x (12): `4, 4.82, 4.86, 5, 5.23, 7, 9, 11, 13, 16, 19, 23`  — **9 of them new to this lane**
  (5, 13, 19 are the published points; 4.953… is not re-run).
- parities: **even and odd at every (x, N)**.
- N per x: `60`, `100`, `N_iso(x)`; dedup where `N_iso ∈ {60,100}` (only x=5).
- `N_iso`: 86, 98, 98, 100, 103, 121, 137, 149, 159, 172, 183, 195.
- **dps = 300 at EVERY cell**, gl_degree 9, iters 16, k=3 per sector. dps is deliberately NOT varied
  with x: the published 3-point series runs dps 150/150/300, so its x-drift is confounded with a
  precision change at the top of its range. Fixing dps removes that confound; arm D measures its size.
- **70 registered cells**, emitted in completion-priority tiers: tier 1 = all N=60 (24), tier 2 =
  all N=100 (24), tier 3 = isoresolution ascending N (22). A per-x verdict requires tiers 1+2 at
  that x; tier 3 missing at an x makes the isoresolution question UNMEASURED **at that x**, stated
  per x and never averaged away.

## 3. REGISTERED PREDICTIONS, BANDS AND DIRECTIONS

Let `S_N(x) = q_1(x,N=100) − q_1(x,N=60)` (the N-covariate) and `R` = the range of `q_1` over the
completed N=100 grid.

- **P0 (gate).** The pooling import reproduces c50's PUBLISHED `q_1` — 0.889256615305 (x=5),
  0.9206571015 (x=13), 0.931062954 (x=19) — to the published digits. *Fails ⇒ everything below is
  void.* (External ground truth for the analysis layer.)
- **P1.** At every completed (x,N): certified prefix ≥ 3 and pooled order begins `eoe`. Dropped
  rungs counted and printed even when 0.
- **P2a / P2b.** `q_1` is **strictly increasing in x** at fixed N=100, across all 12 x (P2a) and
  across the 9 coarse x `4,5,7,9,11,13,16,19,23` (P2b). Permutation null: an exact `1/m!`.
- **P3 — THE AXIS, ZERO FITTED PARAMETERS (the crux, and it is fit-free).**
  `x`, `L = log x` and `n = N(2πx)` (exact zero count, `T* = 2πx`) agree on the three published
  points and disagree off them; choosing the axis IS choosing the family, so it is settled first.
  - **P3a (constant n, moving x):** a pure-n law predicts `Δq_1 = 0` EXACTLY across `4 → 4.82`
    (n=3, x moves 20.5 %) and across `4.86 → 5 → 5.23` (n=4, x moves 7.6 %).
  - **P3b (moving n, constant x):** `4.82 → 4.86` crosses `γ₄/2π = 4.842236`, moving n by **+1**
    while moving x by **0.83 %**. Sealed predictions (§4): F_n says **+0.006864**, F_x says
    **+0.000328**, F_L says **+0.000454** — a 15–21× discrimination.
  - **Bands, both registered and both reported.** Conservative: `3·max(|S_N(x_a)|,|S_N(x_b)|)`.
    Paired: `3·|S_N(x_a) − S_N(x_b)|` — for two nearly-equal x at the same N the truncation bias is
    common-mode and cancels to first order, which is the whole reason the paired design exists.
  - **DIRECTION REGISTERED: I predict the pure-n law is REFUTED at P3a** (i.e. `q_1` moves inside a
    constant-n block by more than the band), **and that P3b's step matches the smooth families, not
    F_n.** Both can fail.
- **P4 — DOES THE DRIFT SURVIVE ISORESOLUTION?** For every consecutive pair of x at which both
  series exist, `sign(Δq_1)` in the isoresolution series equals `sign(Δq_1)` at fixed N=100.
  **DIRECTION REGISTERED: I predict it HOLDS** (the drift is not an artefact of C2). This is the
  arm that can kill the phenomenon outright.
- **P5 — the per-x confound verdict (C1's replacement for V2).** At each x: `CLEAN` if
  `|S_N(x)| ≤ R/3`, else `CONFOUNDED`, else `UNMEASURED`. Per x, never aggregated.
- **P6 — the rate, held to the weakest claim the data can carry.** Three families
  `1 − q_1 = A·u^(−β)` for `u ∈ {x, L, n}`, **calibrated on the three PUBLISHED points only** (2
  parameters, 3 points, log–log least squares — zero new degrees of freedom), then applied **blind**
  to the 9 new x. Scored per x: `|q_1^pred − q_1^meas(x,N=100)|` against `3·|S_N(x)|`. Registered in
  advance under c50's law: *a family whose blind residuals are monotone in x with a sign change
  through the calibration range is refuted as a functional form even if it "fits"*. **I register that
  at most one of the three survives, and I do NOT register which.**
- **P7 — the null (V5).** Label permutation for the best family: 20 000 draws, seed 20260908,
  measured `q_1` values reassigned to x-labels; report how often the observed `Σ|resid|` is matched
  or beaten.
- **Arm D — dps control.** x=13, N=100 at dps 300 (this cycle) vs the published dps 150 value; the
  difference is the size of the confound named in §2.

**UNMEASURED is a permitted verdict and is reported with the completion arithmetic** (cells done vs
planned, per x, per tier). It will not be upgraded to a rate.

## 4. SEALED BLIND PREDICTIONS (computed from the three PUBLISHED points before any cell ran)

`F_x : 1−q_1 = 0.195941846043·x^(−0.35388775026)`
`F_L : 1−q_1 = 0.160254056995·L^(−0.767130026022)`
`F_n : 1−q_1 = 0.148240440706·n^(−0.208506980262)`

| x | n | L | F_x → q_1 | F_L → q_1 | F_n → q_1 |
|---|---|---|---|---|---|
| 4 | 3 | 1.38629 | 0.8800319666 | 0.8752652524 | 0.8821082036 |
| 4.82 | 3 | 1.57277 | 0.8876934165 | 0.8867755009 | 0.8821082036 |
| 4.86 | 4 | 1.58104 | 0.8880214007 | 0.8872298073 | 0.8889718799 |
| 5 | 4 | 1.60944 | 0.8891411745 | 0.8887594756 | 0.8889718799 |
| 5.23 | 4 | 1.65441 | 0.8908915844 | 0.8910866659 | 0.8889718799 |
| 7 | 8 | 1.94591 | 0.9015858941 | 0.9038356136 | 0.9039126688 |
| 9 | 12 | 2.19722 | 0.9099606273 | 0.9123913721 | 0.9117022017 |
| 11 | 16 | 2.39790 | 0.9161330053 | 0.9180724679 | 0.9168429114 |
| 13 | 21 | 2.56495 | 0.9209473763 | 0.9221977053 | 0.9214267449 |
| 16 | 29 | 2.77259 | 0.9265479563 | 0.9267077078 | 0.9265407471 |
| 19 | 38 | 2.94444 | 0.9308818731 | 0.9300120798 | 0.9305662230 |
| 23 | 50 | 3.13549 | 0.9354006133 | 0.9333073775 | 0.9344278245 |

`F_n` returns the SAME value inside a constant-n block by construction — that is P3a's discriminator
sitting in the table, not a coincidence to be discovered later.

## 5. KATs AND EXTERNAL GROUND TRUTH (V5), run BEFORE this prereg, touching no target output

`m2_c52_qdrift.py --kat`, **0 fails**, output committed as `m2_c52_kat.out`:
- **K0** c50's own six synthetic-ladder arms + four published-number arms, run through this file's
  import: 0 fails.
- **K1 (external ground truth for the NEW instrument)** the zero counter `n(x)` reproduces **m1's
  exact counts 21 / 32 / 38 / 56 at x = 13 / 17 / 19 / 25** and c46_analyse.py's five published
  ordinates 14.1347, 21.0220, 25.0109, 30.4249, 32.9351.
- **K1c** the same-n blocks used by P3 are a MEASUREMENT of the counter, not an assumption.
- **K2** the fitter recovers a planted `y = 3u^(−0.7)` exactly; **K2b** planted NON-power data leaves
  residuals the scorer can see (a fitter that cannot fail is not an instrument).
- **K3** the permutation null on a known answer: a monotone m=5 sequence gives exactly `1/120`.
- The scorer was also run end-to-end against an EMPTY cells directory before launch, to prove that a
  half-finished grid degrades to `UNMEASURED` rather than to a crash or a silent subset.

## 6. DISCLOSURE — pre-prereg timing probes

Before this prereg I ran four TIMING probes in a separate namespace (`probe/c46`, never the target
directory): `(even, x=4, N=60)`, `(even, x=13, N=60)`, `(even, x=23, N=60)`, `(odd, x=23, N=100)`,
all dps300 k=3. Their wall times were read (91 s / 95 s / 99 s / 268 s) and used to size the grid.
Three Ritz values of the `(even, x=4, N=60)` cell were also visible in that output. **No odd-sector
value at x=4 was seen, and no even/odd PAIR at any (x,N) was seen, so no `q_1` at any grid point was
computable from anything visible before this prereg.** All four configurations are re-run inside the
registered grid; the probe JSONs are kept and byte-compared after the fact.

## 6b. DISCLOSURE — two registered cells already exist, published, from cycle 50

The pre-launch absence proof (`m2_c52_prelaunch_absence.out`, 70 names checked) is **not 70/70
absent: 2 are already present**, and I state that rather than trimming the grid to make the proof
look clean. `c46_block_{even,odd}_x19_N100_dps300_g9_it16_k3.json` is exactly this cycle's
configuration at x=19, because c50 ran x=19 at dps300 while running x=5 and x=13 at dps150 — the
very confound §2 removes. Those two cells are **re-run inside the registered grid anyway**, into the
target namespace, and their `lambda` literals are compared against c50's published ones. Agreement
is a cross-cycle determinism check obtained for free; disagreement would be a finding about the
pipeline and would be reported as one. The other **68 of 70 are proved absent** at the pre-push HEAD.

## 7. WHAT WILL NOT HAPPEN (V4)

If a registered law fails, the diagnostic ships as a diagnostic. No corrected law is authored in the
run that broke one; that is asked of m1/astra-pa. No instrument is edited after this seal except for
path resolution, and any such change ships with its SEALED_v1 bytes, the diff, and a
byte-identical-output proof (c50's rule).

## 8. CARRIED CAVEAT (V6)

Anyone quoting c50/c51's nodal ladder must carry it: **the dislocation's ONSET is universal across
the four windows tested, its SIZE is not — "+6 at rung 10" is a WINDOW property and it fails at
x=19, odd rung 5, where the model says +6 and the measurement is +2.** Nothing in this cycle
depends on the nodal arm; the caveat is carried because the letter cites the cycle that produced it.
