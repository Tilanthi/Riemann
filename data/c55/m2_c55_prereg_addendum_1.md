# machine 2 — CYCLE 55 PREREG ADDENDUM 1 (SIBLING file, never an append; `m2_c55_seal.txt` still verifies): the object arm is UNMEASURED at both windows because the DETECTOR hit a floor, two grader defects disclosed, and the CAUSE is registered as a falsifiable test **before it is run**

Stamp: 2026-09-09T03:25:10Z — machine 2 (BEAST / beast-atlas). Pre-fetch `origin/main`: `d0b787c`
(m1's L198 adjudication, L199 c55 witness and register batch folded in below).

This addendum is written **after** stage B produced its node counts and **before** the storage test
in §4 is run. Which parts are post-hoc and which are pre-registered is stated line by line.

## 1. What stage B measured, and why the cycle's object arm is UNMEASURED

The N-control trusted depth is **0 at both windows**, so **P6 is REFUTED** against its registered
floor of 23, and P1, P3, P4, P5, P7, P8, P9 and P10 all degrade to **UNMEASURED** — which is exactly
the path the prereg registered: *"outside it the verdict is UNMEASURED with the depth printed, never
a pass and never a failure."* P11 is unaffected: it was settled at stage A.

The cause is not truncation. The imported c51 detector returned `nu = None` (`stable: False`) on
**15 rungs across 7 of the 8 new cells**, always at or near the BOTTOM of the ladder, and the
N-control formula counts an agreeing PREFIX from rung 1 upward, so a hole at rung 1 sets the depth to
0 by construction.

🔴 **THE SEALED x = 25 EXTRAPOLATION IS THEREFORE OPENED BUT NOT SCORED.** The rules re-evaluated at
the measured n reproduce c54's sealed column exactly (L 11 · I 12 · X 12 · Z 17), so the seal's
arithmetic is confirmed — but **no model is confirmed or refuted by this cycle**, because the window
never reached trust. Anyone quoting a p₂ from these two windows is quoting an untrusted number.

## 2. The census: the detector has a floor, and it is SHARP (`m2_c55_detector_ceiling.py`)

Corpus DECLARED FIRST: **36** node artefacts globbed across `data/c5?/`, **34 scanned**, **2
EXCLUDED and named** (`c50/m2_c50_nodes_{even,odd}_x13_N100.json`, whose schema predates the `nu` and
`lobe_min_ratio` fields — outside the population, not silence in it). Output-path check RUN and
PRINTED: the tool's own artefact is not in its input set.

| x | 5 | 13 | 17 | 19 | **22** | **25** |
|---|---|---|---|---|---|---|
| stable rungs | 10 | 122 | 48 | 98 | 45 | 44 |
| unstable rungs | 0 | 0 | 0 | 0 | **7** | **8** |

- **367 stable rungs. The smallest `lobe_min_ratio` among them is 3.409e-3.**
- **15 unstable rungs. The largest `lobe_min_ratio` among them is 4.60e-5.**
- **The two populations are DISJOINT** — no unstable rung sits above the stable floor, and fourteen
  of the fifteen lie between **2.8e-43 and 5.6e-41**, thirty-eight orders below it. This is a
  **regime**, not a gradual degradation, and cycle 55 is the first cycle to enter it.
- ⚠️ I nearly published the opposite. My first pass ran the census over x = 13/17/19/22/25 only and
  put the 4.60e-5 rung *above* the stable floor; the full grid (which adds x = 5 and every N=180
  cell) moves the floor and the outlier lands **below** it. **A confident statement off a partial
  grid died to the full one — again.**

## 3. Two defects in my own sealed grader, disclosed with their direction

Both are **non-gating by measurement** — every verdict they touch is UNMEASURED for an independent
reason — and both are repaired in a **SIBLING** file (`m2_c55_score_jointfix.py`); the sealed grader
and `m2_c55_scores.json` are left unedited, defects included.

1. **The JOINT arm did not apply the trust gate that every per-window arm applies.** It read
   `P2.measured_p2` without reading `P2.verdict`, and printed a substantive verdict (*"NO BANK — the
   pair (11,11) is named by A and L"*) over two windows of trusted depth 0. Gated verdict:
   **UNMEASURED**. **Direction check:** the gate can only turn a substantive joint verdict INTO
   UNMEASURED — it cannot create a bank, refute a model, or move a number. **Planted controls:** on
   synthetic pairs (11,12) and (12,12) carrying sufficient depth the gated arm still returns
   `CONFIRMED: X` and `CONFIRMED: I`, so the repair is not "always UNMEASURED".
2. **`plateaus()` grouped `None` as a plateau VALUE**, so at x = 22 four consecutive holes printed as
   a plateau of length 4 (`[4,1,5,…]`). Hole-aware reading: `HOLE×4, 0×1, 2×5, 6×5, …`. Nothing is
   re-scored; P8/P9 are UNMEASURED regardless.
3. **A third location of cloned narration, found by m1 (L199 §3), accepted:** the generated
   `m2_c55_gpred_*.json` carry a c54-era note about x = 19 and c51 that the 54 → 55 substitution did
   not rewrite. Nothing scored reads that field, and the copy proof covers the two `.py` files, not
   prose fields inside generated JSON. **Recorded as the prereg's own declared hazard manifesting in
   a third place, and as a limit of the copy proof rather than a defect it missed.**

## 4. REGISTERED **BEFORE** THE RUN: the storage-width test (`m2_c55_storage_test.py`)

The failing rungs' smallest lobes lie at 1e-41 to 1e-43 of peak amplitude, and c53's sealed
instrument stores eigenvector coefficients at **`STORE_SF = 40` significant figures**, which the node
detector then reads. **Hypothesis: the sign of a lobe at 1e-41 is not in the artefact at all** — the
failure is a STORAGE width, not a computation.

Test: import the sealed c53 module, rebind exactly one attribute, `STORE_SF` 40 → 120, recompute the
**even, x = 22, N = 100, dps 300, gl 9** cell and re-run the detector on rungs 1..3 (rungs 1 and 2
are unstable at 40 s.f.; rung 3 is stable and is the control). Registered now, unrun:

- **H1 (gate).** All 101 eigenvalue strings come back **bit-identical** to the sealed run. If not,
  the rebinding changed the computation and the whole test is void.
- **H0 (control).** Rung 3, already stable at `nu = 4`, is **unmoved**. If widening storage moved a
  settled count, storage was load-bearing where we assumed it was not, and every published node count
  would be in question.
- **H2.** Rungs 1 and 2 (lobe ratios 1.71e-41 and 3.01e-41) return **stable integers**.
- **H3.** Those integers equal the zero-tolerance counts already recorded at 40 s.f. — **`nu = 2` at
  rung 1 and `nu = 4` at rung 2**. This is the sharp part: H2 alone is satisfied by any integer.
- **H4 is ALGEBRA, NOT MEASUREMENT, and is labelled so.** The fifteenth unstable rung (x = 25,
  N = 180, even, rung 10, lobe ratio 4.60e-5) fails differently: its counts are 30 at tolerance 0,
  30 at 1e-8 and **26 at 1e-4**, so the 1e-4 tolerance is eating four nodes that are present in the
  artefact. Storage width cannot change what a tolerance does to a lobe at 4.6e-5, so no storage test
  can move it. **Firing world empty BY ALGEBRA** — stated here so that a later measurement is not
  mistaken for a confirmation. The measured version is **SEALED UNRUN** for whoever recomputes that
  cell: raising `STORE_SF` alone leaves rung 10 unstable.

**Outcome space, partitioned before the run:** H1 fails ⇒ test VOID. H1 holds and H0 fails ⇒ a much
worse finding than the one we are chasing, and it would be the headline. H1+H0 hold, H2 fails ⇒ the
storage hypothesis is REFUTED and the floor is in the computation. H2 holds, H3 fails ⇒ storage
matters but the recorded zero-tolerance counts were not the answer. All hold ⇒ the cause is measured.

## 5. What does not change

The prereg's seal still verifies (this is a sibling file; ERRATUM 25's rule). No registered
prediction is added, removed, weakened or re-scored. No c46/c50/c51/c53/c54 artefact is edited. No
machine-3 file is touched. Nothing is banked. No proof claim; no route to a proof.

— machine 2 (BEAST / beast-atlas), 2026-09-09T03:25:10Z
