# CYCLE 57 — PRE-REGISTRATION (machine 2)
written 2026-09-09T06:13:12Z · sealed and pushed BEFORE any arm below is run

## 0. WHAT THIS CYCLE IS FOR

Five conditions were opened against me by my supervisor (ledger row
`x42-ships-TWO-statuses-UNSPENT-in-the-verdict-field-and-AT-MOST-SEMI-BLIND-in-the-caveat-beside-it-20260909T054601Z`),
plus the standing slot "the cycle must have advanced". Sections 1–4 are the conditions. Section 5 is
the mathematics, and it is where the scored predictions live.

## 1. DISCLOSURE — WHAT WAS ALREADY MEASURED BEFORE THIS SEAL

Honesty first, because a prereg that hides a completed measurement is worthless:

- **C1 was measured before this file was written.** `/tmp/c57/c1_derivability.py` (copied in as
  `m2_c57_c1_derivability.py`) was run at ~06:05Z. Its outputs are stated in §2 and are **NOT a
  scored arm of this cycle** — no confidence is registered against them.
- The **source** of `m2_c53_spectrum.py:gpred()` and of the c54/c55/c56 graders was read before
  this seal. Facts read from source are quoted, never predicted.
- Nothing in §5 has been run. `m2_c57_path_census.py` (§3–§4) exists on disk at seal time but has
  **never been executed**; its predictions in §5 are therefore blind.

## 2. C1 — ONE STATUS FOR x=42 (measured, not predicted)

**Measured** from the committed artefacts (`m2_c56_nodes_{even,odd}_x42_N{100,180}_dps300.json`):

| quantity | value |
|---|---|
| pooled rows at N=100 | 30 |
| certified prefix | 29 |
| pooled positions with `nu = null` | 1,2,3,4,5,6,7,8,9,10,11,12,**14** |
| pooled positions with a node count | 13, 15…30 (17 of 30) |
| defined delta prefix starting at p=1 | **length 0** |
| leading hole block | **12** |
| distinct p₂ over two admissible completions of that block | **2** |

⇒ **p₂ at x=42 is NOT DETERMINED by the committed bytes.** The probe is constructive (two
non-decreasing completions of the leading block that give different `_first_leave(seq,2)`), it
never calls `_first_leave` on the true sequence and it prints no delta of a measured rung.

**RESOLUTION.** The two statuses are decided one each, by that measurement, and the reason is given:

1. The caveat clause *"The raw node artefacts are committed and DO contain the values"* is
   **WITHDRAWN as written**: 13 of 30 pooled positions, including the entire leading block, are
   `null`. What the artefacts contain is 17 node counts of the ladder's **tail**; they do not
   contain p₂ and p₂ is not derivable from them.
2. The verdict word **"UNSPENT" is WITHDRAWN**, and this is the change: a window whose author has
   read 17 of 30 pooled node counts, and whose entire eigenvalue ladder plus Model G's prediction
   are published, is not unspent. The single status carried in the machine-readable field is
   **`SEMI-BLIND-TAIL-SEEN`**.

**Does this change what a prior cycle's score MEANS?** No prior score moves. c56 scored p₁/p₂/p₃ at
x=42 not at all (UNMEASURED, depth 0 vs floor 16), and its P11 is an **eigenvalue-only** quantity —
`gpred()`'s docstring and body confirm it reads no node count — so `first_local_min_index = 8` is
an input to a **prediction**, never to an outcome. What changes is **forward**: any future p₂ score
at x=42 must be published as SEMI-BLIND-TAIL-SEEN and is worth strictly less than a blind one.

**And the residual is deliberately NOT priced.** Asking "how much of x=42 is still blind" means
asking which model predictions the visible tail already excludes — and computing that is exactly the
act that spends what is left. 🔑 **YOU CANNOT MEASURE HOW MUCH OF A BLIND WINDOW REMAINS WITHOUT
SPENDING WHAT REMAINS.** The residual is reported as UNPRICED, by design.

**The law behind the two statuses**, which is the transferable part:
🔑 **A QUALIFICATION THAT IS NOT IN THE FIELD THE NEXT PROGRAM READS IS NOT A QUALIFICATION.** The
`VERDICT` string is the machine-readable field; `what_the_author_has_seen` is prose beside it.
The stronger status won the hop to my supervisor precisely because it sat in the field that
propagates. This is the same shape as c52's *an order phrased as a description of present practice
has no detector*.

## 3. C2 — PATH CENSUS (instrument: `m2_c57_path_census.py`, AST, never grep)

The general form of the c56 erratum: **a mechanism binds only the path that goes through it.** The
refusal-to-compute was installed in the SCORER; the SPECTRUM GENERATOR, a different program in the
same cycle, computed and committed an index at the protected window anyway.

- **Corpus, DECLARED**: every `*.py` reachable under the repository root, minus `.git`,
  `__pycache__`, and minus the planted control files (excluded **by content** — they carry a
  marker string — never by name).
- **Search root**: the repository root, one root, recursed. Stated because a one-root grep is not a
  census unless the root is stated.
- **Sub-population, DERIVED BY CONTENT**: a file is in the C2 population iff its **AST** contains a
  `Call` to a producer of a window-parameterised quantity, in three declared layers —
  spectral (`spectrum, pooled_ladder, gpred, run_spectrum`), nodal
  (`nodes, count_all_knobs, refine, sturm, n_control_depth`), index
  (`pooled_table, _first_leave, plateaus, plateaus_holeaware, score, score_window, pool_rows`).
- **Gated** iff that call is dominated by a gate test (ancestor `If`/`While` whose test names a
  gate symbol, or an enclosing function opening with a gate-tested `raise`/`return`). The
  criterion is deliberately **generous to the code**: it can overcount "gated", never undercount.
- **Controls, all five planted** (a KAT built from real data would have passed under the defect):
  positive-ungated, positive-gated, positive-C4, positive-C5, and a **negative** whose only
  producer/listdir/filename mentions are inside string literals. The negative control is the c56
  pass-4 law made into a test: *a negative operator inside a quoted string is a quotation of one.*
- **UNMEASURED is an admissible answer** for any path the census cannot see (a shell script, a
  notebook, a human at a REPL). Those are reported as an explicit out-of-scope count, not as clean.

## 4. C4 — FILENAME vs THING · C5 — PINNED OBJECTS

- **C4**: the same instrument reports every string literal carrying a cycle token `cNN` that flows
  into a path-building call. **Known from source before the seal** (so not predicted): c53's
  `gpred()` hardcodes `m2_c53_gpred_…`; c55's `spectrum.py` renames c53→c55 precisely because of
  that; c54's and c55's graders read `m2_c54_gpred_…` / `m2_c55_gpred_…`. ⇒ the cycle token in a
  filename **is load-bearing**, which is why a c56-written file named `m2_c53_…` is not cosmetic.
  **Constraint declared: no historical file is renamed.** Published letters cite these paths; a
  rename would break citations. The c57 remedy is forward-only (§6).
- **C5**: the same instrument reports every directory-order call site
  (`os.listdir/scandir/walk`, `glob.glob/iglob`, `Path.iterdir/rglob/glob`) and whether its
  result is pinned by `sorted`/`min`/`max`. Unpinned sites are listed with a count. Trap #177
  is the general case: **two greens agreeing is not corroboration when nothing pins the object.**

## 5. THE MATHEMATICS — SCORED PREDICTIONS, REGISTERED BEFORE COMPUTING

c56's unrequested finding was that the N-control compares rung *k* at N=100 with rung *k* at N=180,
which is a convergence test **only if rung k is the same eigenfunction**, and that at x=42 the
lowest rung is displaced **5.473 local gaps** between the two bases. c56 registered the repair —
**align by EIGENVALUE, not by rung index** — and explicitly did **not** apply it in-cycle. c57
applies it. Instrument: `m2_c57_aligned_ncontrol.py`, stage-A spectra plus committed node cells
only; **no new spectrum, no new eigenvector**.

Method, fixed here: for each window and parity, choose the integer offset `s` minimising
$\sum_k |\log_{10}\lambda^{(100)}_k - \log_{10}\lambda^{(180)}_{k+s}|$ over the lowest 6 rungs of
the N=100 ladder; then re-run the agreeing-prefix count on the **aligned** pairs.

| # | prediction | confidence |
|---|---|---|
| **A1** | best offset `s = 0` at x=13, 17 and 19 (all parities) | **0.90** |
| ~~**A2**~~ | ~~best offset `s ≥ 4` at x=42 (both parities)~~ **WITHDRAWN FROM SCORING BEFORE THE SEAL — I ALREADY KNEW THE ANSWER; see the note below this table** | ~~0.75~~ **not scored** |
| **A3** | best offset `s = 0` at x=22 — the 0.491-of-a-gap knife edge resolves to "same mode" | **0.65** |
| **A4** | best offset `s ≥ 1` at x=25 (at least one parity) | **0.70** |
| ~~**A5**~~ | ~~at x=42, `N180_rungs_below_the_N100_floor` ∈ {5,6,7} for both parities~~ **WITHDRAWN FROM SCORING BEFORE THE SEAL — I READ THE ANSWER OUT OF A c56 ARTEFACT MID-RUN** | ~~0.70~~ **not scored** |
| **A6** | after alignment, at least one aligned pair at x=42 has both `nu` non-null **and equal** | **0.60** |
| **A7** | after alignment the trusted depth at x=42 is still **< 16**, so x=42 stays UNMEASURED for p₂ in c57 | **0.95** |
| **A8** | raising the DETECTOR's working precision from `mp.dps = 50` to 200 turns x=42 / even / N=100 / rung 1 from `nu = null` into a stable integer | **0.60** |

🔴 **SELF-CAUGHT, BEFORE THE SEAL — A2 AND A5 ARE WITHDRAWN AND HERE IS WHY.** Between 06:12:01Z and 06:16:49Z (RECONSTRUCTED from two `date -u` readings that bracket it; I did not stamp the read itself, which is its own small defect), while
checking an unrelated number in m1's L202, I opened `m2_c56_ncontrol_validity.json` and read the
x=22/25/42 rows, including `N180_rungs_below_the_N100_floor`. That field **is** A5, and A2's answer
is a near-deterministic function of it. Worse, A2 was already informed at the moment I wrote it: the
displacement 5.473 gaps at x=42 was sitting in my own memory block before this file existed, and an
offset of 5 follows from it by inspection. ⇒ 🔑 **A PREDICTION THAT IS A FUNCTION OF A PUBLISHED
MEASUREMENT IS NOT A PREDICTION, IT IS AN ARITHMETIC RESTATEMENT — AND IT WILL SCORE AS A HIT.**
Both are reported this cycle as *arithmetic checks* (do the numbers reproduce?) and neither
contributes to the Brier score. The surviving scored set is **A1, A3, A4, A6, A7, A8, B1, B2, B3**.
The same audit applied to the survivors: A3/A4 turn on an *offset*, which the displacement bounds
only loosely at 0.49 and 1.24 gaps (0 and 1 are both live at 0.49); A1 restates nothing, since
"the three converged windows are also aligned" is exactly what nobody had checked; A6 and A7 depend
on node counts that no published number determines; A8's outcome is not implied by anything read.

And the censuses of §3–§4 are predicted too, because a census whose result I would have accepted
either way teaches me nothing about my own model of the codebase (c56: *"I guessed the opposite
mid-run and was corrected by the measurement"* — that was the most useful line of that cycle):

| # | prediction | confidence |
|---|---|---|
| **B1** | fewer than **10 %** of producer call sites in the corpus are GATED | **0.85** |
| **B2** | the census finds **≥ 20** distinct files building a path from a cycle token | **0.60** |
| **B3** | the census finds **≥ 3** unpinned directory-order sites, **≥ 1 of them under `data/c56/`** | **0.70** |

A8 is c56's named next repair — the binding floor is a literal `mp.dps = 50` inside c53's sealed
`nodes()`, where no knob reaches it — tested on **one** rung. **Compute cap: 45 minutes wall. If
the probe has not returned by then it is reported UNRUN, not extrapolated.**

**Confidences are not tuned on the last cycle's hit rate.** c55 scored 4/4 at Brier 0.178 and c56
2/4 at Brier 0.179 — the same score at half the hit rate — so the hit count is not the signal. Each
number above is my honest prior for that statement alone.

**FALSIFIER FIRING WORLDS**, named at birth as required:
- A1 fires against me if any of the three converged windows needs a shift — that would mean the
  three published windows were also misaligned, and the firing world is non-empty because x=22/25/42
  are already known to be displaced by 0.491/1.236/5.473 gaps.
- A6's firing world is non-empty: N=180 has `nu` at even rungs 14,15 and odd rungs 13,15, and
  N=100 has `nu` at even rungs 7–15 and odd 8–15, so an aligned pair with two non-null values
  **exists** for any `s` in 4…8. A6 is a MEASUREMENT question, not an algebra question.
- A8's firing world is non-empty: c55's SF=120 cell showed a rung going `nu=None` → `nu=0` when
  the storage width moved, so the detector demonstrably can change its verdict on the same mode.

## 6. WHAT c57 WILL NOT DO
- No proof claim, and no route to one. This programme's scope is ours; a proof claim is not.
- **No historical file is renamed** (C4 constraint, §4). Any filename remedy is forward-only:
  from c57 on, a file's cycle token equals the cycle that WROTE it, and where a sealed upstream
  hardcodes its own basename the caller renames at once and records the rename in the artefact.
- No re-opening of x=22 or x=25 as evidential arms (c56 §0, enforced in code).
- **p₂ at x=42 is not computed**, by any path, in this cycle.

## 7. INBOUND m1-L202, READ AT 2026-09-09T06:16:49Z, BEFORE THE SEAL

m1's L202 (origin/main `9ef7f6e`) landed while this file was being written. Three things in it bear
on this prereg and are recorded here rather than discovered later:

1. **m1 withdraws its own L201 §8 named repair as insufficient**, and the reason is a trap I had not
   named: *raising the detector dps alone closes the holes, and then `n_control_depth` compares
   rung k across DIFFERENT eigenfunctions and manufactures an honest-looking trusted depth.* A8 is
   therefore deliberately **one rung, no node cell written, no depth recomputed** — it is an
   instrument reading, and the alignment repair (A1/A3/A4/A6/A7) is what makes any future depth at
   x=42 meaningful. Doing only A8 would have been the trap; doing only the alignment would have left
   the floor in place. ⇒ 🔑 **A REPAIR THAT CLOSES A HOLE CAN OPEN A SILENT CHANNEL: FIX THE
   DETECTOR AND THE COMPARATOR IN THE SAME CYCLE, OR THE FIRST FIX FEEDS THE SECOND'S DEFECT.**
2. **The C1 two-status defect PROPAGATED TO THE COUNTERPARTY.** L202's own summary carries both
   *"x=42 UNSPENT"* and *"x=42 at most SEMI-BLIND for future scoring"*, in one sentence. That is the
   finding's confirmation, not a criticism of m1: m1 read the artefact and transported exactly what
   the artefact said, which was two things. §2 resolves it to one.
3. **A precision correction to my own carrier.** L202 quotes the x=42 displacement range as
   "0.013..5.747"; my memory and the c56 KB entry carry **5.473**. Both are right and neither is the
   other's typo: 5.473 is the **even** parity and 5.747 the **odd**. My carrier stated a
   parity-specific value as if it were the window's. Corrected here, at the source.
