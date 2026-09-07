# data/c43 — BEAST machine2, cycle 43: adjudication of m3-L177

Entry point for the letter
`BEAST-c43-adjudication-m3-L177-P1-uncensored-to-45sf-lambda-inf-is-POSITIVE-and-a-model-free-floor.md`.
Everything here reruns in well under 4 minutes total on one core; `c43_widen.py` is 185 s of it and is
the only piece that rebuilds a matrix.

| file | what it establishes | letter § |
|---|---|---|
| `p1_width.py` | P1 and the N=140 rel diffs re-derived; the print-width censoring interval quantified | §1, §2 |
| `c43_widen.py` | reruns **our own** c42 x=13,N=100,dps=150,GL9 cell and prints λ_min at widths 30/45/60/100. w30 reproduces the published literal exactly (control); w45 is character-identical to m3's dps-220 crosscheck | §2.1 |
| `nesting_kat.py` | **known-answer test** that `M(N=12)` is exactly the leading block of `M(N=20)` (max entry difference `0.0`) ⇒ Cauchy interlacing ⇒ `λ_min(N)` non-increasing | §3 |
| `zero_limit.py` | tests whether `λ_∞ = 0` is admissible (it is not, in any family tried); derives the model-free floor `factor ≥ 1.31310899` | §3 |
| `extrap.py` | the three extrapolation families scored out-of-sample; implied `λ_∞` per family and per anchor pair | §4 |
| `sensitivity.py` | cumulative factor vs the power-law shape parameter `p`, anchored uniformly on (180,220) | §4 |
| `kat_check.py` | KAT-1 arm A/B cross-instrument agreements and the `log π` bookkeeping identity, all against our §7A literals | §6, §7 |

`*.out` are the committed outputs of the corresponding `*.py`.

## Inputs and their provenance

- The four λ values at N = 100/140/180/220 are **m3's**, read from
  `data/code/m3_L177_build/results/{x13_N100_output.txt, x13_Nextrap_output.txt, SUMMARY.md}`.
  Nothing here recomputes a cell in m3's lane.
- `c43_widen.py` imports `c42_connes_x` from BEAST's own c42 build. It is a strict subset of
  `c42_run.py`: identical `build_matrix` / `smallest_eigenpair` path, zero-comparison diagnostics
  skipped (they do not touch `lambda_min`). The w30 line is the control proving the path is the same.

## Declared limitations

- §4's span ≈[1.313, 1.64] is a **span over refuted model families**, not a confidence interval.
  The true asymptotic form is in none of them.
- Digits 46–60 of the reading form in §2.1 are `[UNMEASURED]`: 45 is the externally corroborated width.
- The registration in §5 rests on **two** values of `p_eff`. Two values give a direction, never a rate.
  Declared WEAK at birth.

No proof claim. Standing sentence unchanged: we have no route to a proof.
