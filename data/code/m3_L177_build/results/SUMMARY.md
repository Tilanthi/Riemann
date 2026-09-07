# m3-L177 build results summary (raw data for parent to write up)

## Gate (all pass)
- basis.py: phihat closed form vs direct quad (max err 1.4e-40), phihat at complex r=i/2 (max err
  5.7e-42), g_jk closed form vs direct quad (max err 4.6e-41), orthonormality g_jk(0)=delta_jk
  (exact, 0.0), symmetry g_jk=g_kj (exact, 0.0). GL(3) quadrature validated exactly against textbook
  values. Prime-power support at x=13: {2,3,4,5,7,8,9,11,13} -- exact match.
- KAT-1-equivalent (Gaussian explicit-formula-vs-zeros, own build, own zero table via mpmath.zetazero):
  arm A (s=0.2): rel diff 2.001e-42 vs zero sum (BEAST's own quoted total W matches mine to their
  displayed precision; component split differs by a pure bookkeeping convention -- see notes).
  arm B (s=1, sharp cancellation): |W| = 2.635e-33 (matches BEAST's own "cancels to 33 places" almost
  exactly, both landing in the same decade).

## P1 -- second-instrument agreement at x=13, N=100, dps=150
  mine:  3.720899741667123935791434766094540694091e-59
  BEAST: 3.72089974166712393579143476609e-59
  relative difference: 1.220321537e-30  (target was >=8 s.f.; got ~30 s.f. -- P1 CONFIRMED, spectacularly)

## Precision cross-check (requested explicitly)
  N=100 at dps=150 vs dps=220: ratio = 1.0 exactly (to displayed precision) -- confirms dps is NOT
  the limiting factor anywhere in the N-sequence below.

## N-sequence at x=13, dps=150 (own build)
  N=100: 3.720899741667123935791434766094540694091e-59
  N=140: 3.191618722904299187775878951533394940265e-59
  N=180: 2.959706807240060045108126519806894301792e-59
  N=220: 2.833656431009356898926062340578180078197e-59

  ratios: N140/N100 = 0.8577545606 (drop 14.22%)  <- matches BEAST's own quoted 0.857755 to 6 s.f.
          N180/N140 = 0.9273372117 (drop 7.266%)
          N220/N180 = 0.9574111949 (drop 4.259%)
  cumulative N220/N100 = 0.7615514063

## P2/P3 -- extrapolation, TWO MODELS TRIED, THEY DISAGREE (honest finding, not smoothed)
  Model A -- geometric (Aitken's Delta-squared, assumes lambda(N) = lambda_inf + C*rho^N):
    from (100,140,180): Linf ratio to N=100 = 0.746820331  (cumulative factor 1.339)
    from (140,180,220): Linf ratio to N=100 = 0.721214543  (cumulative factor 1.387)
    -> BOTH within the pre-registered P2 band [1.15, 1.6]. P2 CONFIRMED under this model.
  Model B -- algebraic (Richardson, assumes lambda(N) = lambda_inf + C/N, using various point pairs):
    ratios to N=100 range from 0.502 (N=100,140 pair) to 0.609 (N=180,220 pair)
    -> cumulative factors 1.64 to 1.99, OUTSIDE the pre-registered band [1.15,1.6] on the high side.
  Diagnostic: successive difference ratios d(180-220)/d(140-180) = 0.544, d(140-180)/d(100-140) =
  0.438 -- NOT constant (would be constant under a pure single-rate geometric model), and INCREASING
  toward 1 as N grows -- suggests the true asymptotic decay is SLOWER than pure geometric, more
  consistent with (or at least not ruled out by) an algebraic/mixed model, though 4 points cannot
  reliably distinguish 2-parameter models from more complex ones.
  P3 (>10% difference from N=100 naive reading): CONFIRMED under EITHER model (both give >>10%).

## Self-caught bugs during the build (report honestly)
  1. First matrix-assembly approach (fixed-panel Gauss-Legendre quadrature per (j,k) pair,
     weil_form.py) did NOT converge with panel count at N=30 -- lambda_min changed by orders of
     magnitude, even SIGN, going from 8 to 16 to 24 panels. Caught by an explicit convergence check
     before trusting any number. Root cause: fixed low-degree panels can't resolve the archimedean
     integral's oscillatory content once basis frequency w_k grows with k.
  2. Restructured to precompute O(N) frequency-indexed integrals (J_sin(w_m) for m=0..N) instead of
     O(N^2) per-pair quadratures, exploiting that g_jk(t) for j!=k decomposes into a combination of
     sin(w_j t) and sin(w_k t) ONLY. Validated new approach against the direct (unsplit) integrand at
     several (j,k) pairs: exact agreement to displayed precision.
  3. Along the way, caught that naively splitting the diagonal (j=k) archimedean piece into separate
     sin/cos "moment" integrals is UNSAFE: the individual cos-type piece is log-DIVERGENT at t=0 even
     though the combined [e^{-2t}delta - e^{-t/2}g_kk(t)]/(1-e^{-2t}) integrand is finite. Caught by
     direct reasoning about the t->0 limit before running a quadrature call that would have returned
     nonsense. Fixed by computing the diagonal piece as ONE combined finite integral per k (still O(N)
     total, not O(N^2)).
  4. KAT-1 gate arm B initially landed 6 orders of magnitude worse than BEAST's own cancellation
     (|W|~8.76e-27 vs their 2.6e-33) -- and crucially the residual was IDENTICAL across dps=50/70/90,
     immediately flagging it as NOT a precision-floor issue. Diagnosed: 8.756508127e-27 matches e^-60
     almost exactly -- the archimedean integral's fixed quadrature cutoff at t=30 (e^{-2*30}) was the
     entire discrepancy, a pure truncation-range bug, not a formula error. Fixed by extending the
     integration range; arm B then landed at 2.635e-33, matching BEAST's own "cancels to 33 places"
     almost exactly.
  5. Own KAT-1 arm A component breakdown (pole/arch split) differs numerically from BEAST's own
     quoted components (mine: pole=-0.137, arch=0.158; theirs: pole=1.008, arch=-0.987) even though
     totals match to ~1e-42 -- traced exactly to a difference of log(pi) between the two pole/arch
     figures, i.e. a pure DISPLAY/bookkeeping convention difference (which bucket the "-g(0)log(pi)"
     term gets folded into), not a mathematical discrepancy. Worth noting as a nice, harmless
     confirmation of genuine independence (even internal bookkeeping conventions differ) alongside the
     matching total.

## Timing
  N=100: ~121s.  N=140: ~251s.  N=180: ~425s (cumulative).  N=220: ~656s (cumulative). dps=220
  cross-check at N=100: ~210s. All well within a single session, no overnight runs needed.

## Code
  data/code/m3_L177_build/{derivation_notes.md, basis.py, weil_form.py (superseded, kept for the bug
  history), weil_form2.py (production), kat1_gate.py}
