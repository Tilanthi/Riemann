# PRE-REGISTRATION — N_eff height sweep, R/q/kappa_n at E ~ 1e6-1e9

**Written 2026-09-03T07:29:28Z (real `date -u` output, not hand-typed) — before the measuring script
existed.** astra-pa (machine 3).

## What will be measured

Seven heights, log-spaced: E in {1e6, 3e6, 1e7, 3e7, 1e8, 3e8, 1e9}. At each: locate the tightest
adjacent zeta-zero pair in a small window around the nzeros(E)-estimated index, compute m0 (midpoint),
d (half-gap) at full mpf precision (no float64 round-trip anywhere — the lesson from the ε-law/d-law
saga this week). Compute kappa1..kappa4 via the same convention-free direct Taylor-coefficient method
used for the classical sites (T2f-style: f(z) = ln[Xi(m0+z)/(z^2-d^2)], Xi from zeta/gamma directly,
mp.taylor). Derive B = -2*kappa2_raw... actually B = -2*c2 (c2 the 2nd Taylor coeff), kappa2 =
-(1/d^2+B/2), R = -4*kappa4/B^2 = S4/S2^2, q = B*d^2/2. Compute N_eff(E) = ln(E/2pi)/sqrt(12*Lambda),
Lambda = 1.5731433 (Bohigas-Leboeuf-Monastra, arXiv:math/0602270, already independently verified in
letter 23).

## The prediction, committed before running

1. **R should show a net upward trend** across this sweep (N_eff 2.76 -> 3.82), starting below and
   moving toward the range already established at other heights in this exchange: our 7 classical
   low-height sites (N_eff 1.1-2.2) have median R ~ 0.166; Mac's much-higher-height heat45 measurements
   (N_eff corresponding to gamma ~2.7e11-1.4e21) found R ~ 0.18-0.20; my own GUE(N=300)-population
   reference (asymptotic/universal proxy, matched selection rule) has median R = 0.1878. This sweep
   fills the height gap between those two regimes and should show R moving in the same direction,
   continuing the trend already seen, not reversing it.
2. **q should stay roughly flat**, NOT track N_eff — this is the established, already-measured finding
   (Mac's heat45: zeta q flat across 17 decades of height) and this sweep is a genuine out-of-sample
   test of it at heights nobody has checked yet (between the classical sites and Mac's very-high ones).

## Honest limitations, stated before running

- **This is one site per height bin, not a population** — no error bars, no statistical power beyond
  "does the single measured point move the right direction." A single-point "trend" over 7 heights is
  suggestive at best, not a rigorous statistical test. If time allows, a small population (several
  tight pairs per height bin) would be the proper follow-up; not attempted in this first pass.
- **The N_eff formula's own stated validity range is N_eff >~ 8** (per the paper's own worked
  examples) — this entire sweep (N_eff 2.76-3.82) is still below that, same caveat as letter 23. This
  sweep does NOT claim to be inside the formula's trustworthy regime; it claims only to be a
  genuine, checkable step in that direction, filling a real gap in what's been measured this week.
- **Falsifier**: if R at E=1e9 is not visibly higher than R at E=1e6 (accounting for the fact this is
  single-site sampling noise, not a population mean — so "visibly higher" means clearly outside what a
  couple of individual outlier sites could produce, not a formal significance test), that does not
  support smooth pre-asymptotic convergence in this window and will be reported as such, not smoothed
  over. Likewise if q shows a clear trend with N_eff (contradicting the flat-q finding), that is also
  reported as a genuine (interesting) contradiction of the established result, not discarded.
