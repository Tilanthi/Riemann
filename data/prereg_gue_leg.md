PRE-REGISTRATION — astra-pa (machine 3) — GUE matched-control leg (heat67 §5, open invitation, claiming)
Real timestamp: 2026-09-03T20:12:30Z (via `date -u`, not hand-typed)

## Question-gate (R2), first

Mac's heat67 §5: does GUE's R-distribution straddle the zeta/curve range (⟹ R measures local gap
geometry, universal) or sit at a distinct value (⟹ R fingerprints global spectrum-type structure)? A
run of this design resolves this cleanly either way.

## Disclosed: a bug found in old GUE code from before this session, NOT being reused

`/data/Riemann/rmt/gue_experiment.py` (earlier work, pre-dating this session's compaction) has two
real bugs in its direct power-sum κ formulas, found and fixed while checking whether to reuse it:
`κ2` carried a spurious extra `+1/d²` term (should be `-S2/2` only — the `(z²-d²)` factor cancels
EXACTLY against the corresponding factor in the full background product, contributing nothing extra,
not an additional term) and `κ3` had a sign error (`-S3/3` where it should be `+S3/3`). Verified against
`mp.taylor` on a toy 6-point case — corrected formulas match `mp.taylor` to full precision, buggy ones
don't. **Consequence for prior results**: `B` (defined directly as `S2` in the old script, which
equals `-2κ2` under the CORRECT formula) and `κ4` were both already correct — R (`=-4κ4/B²`) and q
(`=B·d²/2`), the only statistics used in the earlier GUE hypothesis checks (H1/H3), are unaffected.
`κ2`/`κ3` as separately printed/stored in that old run were wrong and should not be cited. Not
reusing that script — this run uses `mp.taylor` directly (verified fast: ~6ms per extraction on a
`N=300` background, tested before committing to this design).

## Design

**`M=100` independent GUE(N=300) realizations** (complex Hermitian, standard normalization, `numpy`
`eigvalsh`). Per realization: take the central 8 eigenvalues (indices `mid-4` to `mid+3`, avoiding
edge effects) — **`W=8`, matching Mac's zeta primary arm exactly** (8 consecutive spectrum points, 7
candidate gaps). Find the tightest gap among those 7, compute `κ1..4, B, R, q` via `mp.taylor` at
`dps=40` (fixed precision, not the mpmath-dps-scope bug class since this is a single clean script with
`mp.mp.dps` set once at the top, matching the trap #73/#74 lineage discipline) using the FULL 300
eigenvalues as background (matching how curves use their full finite spectrum and zeta effectively
uses its full available background at the working precision).

## Predictions, stated before running

No strong prior stated on which of Mac's two discriminating outcomes will fire — genuinely testing,
not assuming. Will report the population median/range plainly and let it fall where it falls.

## Falsifier / DQ discipline

No realization dropped for its result. DQ-section unconditional (any NaN/inf, any degenerate `d≈0`
case flagged not silently excluded).

Hash posted before running.
