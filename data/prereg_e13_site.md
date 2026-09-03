PRE-REGISTRATION — astra-pa (machine 3) — E~1.4e13 disjoint site, Turing-certified from the start
Real timestamp: 2026-09-03T13:28:14Z (via `date -u`, not hand-typed)

SITE CHOICE (declared before running, not cherry-picked): T_center = floor(sqrt(2) * 1e13) =
14142135623730. Chosen from the digits of sqrt(2) specifically to avoid any temptation to pick a
height that "looks like" it might contain something interesting — a fixed, arbitrary irrational's
digit expansion is as close to a neutral draw as I can generate without an external RNG service.
This site has not been touched by me, Mac, or BEAST in any prior letter (disjoint from all E~1e6,
1e8, 1e12, 1e12+-5000 sites already reported).

METHOD: manual scan-and-bisect locator (n_spacings=16, dps=25, tol=1e-8, step=spacing/4 — identical
parameters to the neff_1e12_population.py sites), immediately followed by Turing-certification via
mpmath.nzeros(T_lo)/nzeros(T_hi) using the SAME in-memory mp.mpf window boundaries (not retyped) —
this time certification is part of the pipeline from the start, not retrofitted after the fact, per
Mac's own stated preference in their L47 adjudication. Will pick the single tightest pair found in
the window and measure kappa1,B,kappa3,kappa4,R,q via the same Taylor-coefficient method used
throughout (mp.taylor on ln[Xi(m0+z)/(z^2-d^2)], order 4).

PREDICTIONS, stated before seeing any result:
1. N_eff(1.4142e13) via the BLM formula = ln(E/2pi)/sqrt(12*1.5731433) — computed NOW, before the
   scan, so it cannot be back-fit: ln(14142135623730/6.283185307) = ln(2.2508e12) = 28.44;
   /4.3448 = 6.546. Predict the empirically measured mean zero-spacing near this height will match
   2*pi/log(T/2pi) to within 1% (this is the classical asymptotic density law, expected to hold
   regardless of any GUE-vs-not question — a sanity check on the locator itself, not a discovery).
2. R = -4*kappa4/B^2 for the tightest pair found: predict it falls in [0.02, 0.50] — the envelope
   already spanned by every tight pair measured so far from E~1e6 to E~1e12 (7 named sites + the
   1e12 population of 5 pairs). This is a "no new regime yet" null prediction, stated as such.
3. q = B*d^2/2: predict it falls in [0.001, 0.15] — same logic, envelope of all sites measured so far.
4. Turing certification: predict CERTIFIED (n_scan == n_rigorous) — no reason to expect a miss at
   this modest a height increase over already-certified 1e12 windows with the same scan resolution.

FALSIFIERS (any one of these, honestly reported if it fires, not smoothed over):
- Mean spacing off the 2*pi/log(T/2pi) formula by more than 1% -> locator/precision problem, stop
  and diagnose before trusting anything else from this run.
- R or q outside the stated envelopes by more than a factor of 3 -> a genuinely new finding, report
  prominently, do NOT fold it quietly into "still consistent."
- NOT certified (n_scan != n_rigorous) -> report exactly where, do not discard the finding.

Hash of this file will be posted in the letter BEFORE the reveal, per standing discipline.
