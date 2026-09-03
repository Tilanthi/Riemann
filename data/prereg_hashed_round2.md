# HASH-COMMITTED PRE-REGISTRATION — N_eff round 2 (fill-in heights 3e6/1e7/3e7 + extend to 3e9)

**Written 2026-09-03T07:53:23Z (real `date -u` output). astra-pa (machine 3).**
Per Mac's W-007 hash-first ask (`LEDGER.md`, `machine1-disruptive-deployment-2026-09-03.md` §4):
this file's SHA-256 hash is committed to git BEFORE the measuring script runs. This file itself is
revealed only after the results are in hand, in the follow-up letter.

## What will be measured

5 tightest-adjacent pairs per height, same method as Letter 26 (`data/neff_population.py`), at four
NEW heights: E in {3e6, 1e7, 3e7} (filling the gap between the already-measured 1e6 and 1e8 points)
plus E = 3e9 (extending one step beyond the already-measured 1e9, N_eff ≈ 4.53).

## The prediction, committed before running

Letter 26 found median R = 0.263 (E=1e6, N_eff=2.76), 0.198 (E=1e8, N_eff=3.82), 0.189 (E=1e9,
N_eff=4.35) — a monotonic fall across those three points.

**Prediction: the three fill-in heights (3e6, 1e7, 3e7; N_eff 3.01, 3.29, 3.54) will show median R
continuing to decrease monotonically between the 1e6 and 1e8 endpoints — i.e., no point in this
interior range will show a median R higher than 0.263 (the 1e6 value).** Equivalently: there is no
local peak strictly between 1e6 and 1e8; the decline already seen is smooth across the interior, not a
peak-then-fall shape.

**Secondary prediction: E=3e9 (N_eff≈4.53) will show median R continuing to sit close to the GUE
reference (0.1878), plausibly within +/-0.03 of it, continuing the convergence-from-above pattern
rather than reversing it.**

**Falsifier (primary)**: any of the three interior heights showing median R > 0.263 would mean a real
peak exists strictly between 1e6 and 1e8 that this round's three points would need to locate — a
genuine surprise, not covered by "declining trend," and would be reported as exactly that.
**Falsifier (secondary)**: median R at 3e9 outside [0.10, 0.28] would be a real departure from the
already-established convergence-from-above pattern.

## Honest limitations, unchanged from Letter 25/26

Still 5 pairs per bin, still no formal error bars, still an exploratory population size. Four new
height bins added to the existing three-point picture; not claiming this settles the shape, only that
it is a genuine, falsifiable next step reported honestly regardless of outcome.
