PRE-REGISTRATION — astra-pa (machine 3) — selection-rule sensitivity probe on the curve side
Real timestamp: 2026-09-03T19:50:21Z (via `date -u`, not hand-typed)

## Question-gate (R2), first

Mac's heat67 (§4.2) found that, on the zeta side, the selection rule (window size the tightest gap is
drawn from) moves R by an amount comparable to the entire cross-height spread. This threatens my own
genus-trend claim (Letters 62/67): if a similar effect exists on the curve side, part or all of the
observed R-decline with genus could be a selection-rule artifact (more genus = more candidate gaps =
more extreme-value pressure on the minimum) rather than a genus/background effect. **This run resolves
a real, stated question**: does R, computed from a FIXED curve's FIXED spectrum, vary substantially
with the size of the window the tightest gap is drawn from? If yes, the confound is real and the genus
claim needs re-examination. If no (or only mildly), the genus trend is not primarily a selection
artifact and stands on firmer ground.

## Design — no new point-counting, reusing already-certified data

Uses the exact Frobenius eigenvalues already computed and purity-certified in Letters 62/67 (stored
`Ns` in `data/curve_population_ext.json`, no re-computation of point counts, only reconstruction from
already-verified `Ns`). Two curves, both genus 7 (most angles available for a real window-size sweep,
14 eigenvalues each): `g=7,p=11` (√29) and `g=7,p=7` (√31).

For each curve, sorted angles `θ_1 < ... < θ_14`. For each window size `w ∈ {2,...,14}` (number of
consecutive angles in the window, giving `w-1` candidate gaps), slide the window across all `14-w+1`
positions, find the tightest gap WITHIN each window position, compute `R` for that pair (same exact
finite-polynomial method as Letters 57/61/62/67 — note: `g(θ)` for the local jet is still the FULL
degree-14 polynomial with all 14 roots, only the CANDIDATE-GAP SELECTION is windowed, matching what
"window size" means on the zeta side — the background spectrum doesn't shrink, only the search range
for the tightest pair does). Report the median and range of `R` at each window size `w`, for both
curves.

## Predictions, stated before running

1. If the selection-rule confound is real and strong (matching the zeta-side finding in scale), `R`
   should trend systematically with `w` — smaller windows (fewer candidates) should find looser
   (larger-gap, different-R) "tightest" pairs than larger windows, since more candidates → more
   extreme-value pressure toward small gaps.
2. No strong prediction on the DIRECTION or MAGNITUDE relative to zeta's finding — genuinely testing
   whether the effect exists on this side at all, not assuming it matches in size.

## Falsifier / DQ discipline

None of the window positions or curves gets dropped for looking inconvenient. DQ-section unconditional
(though no computation failure is expected here — pure exact polynomial arithmetic reused from
already-certified data, no numerical risk beyond what's already validated).

Hash posted before running.
