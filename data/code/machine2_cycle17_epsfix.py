"""machine 2 -- cycle 17 -- eps_eff comparison numbers, recomputed at high precision.
(The first pass built the reference constants at import time, when mp.dps was still 15, so its
r1_minus_ours / m1_minus_ours fields are garbage -- a precision-context bug in the REPORTING,
not in the roots.  Roots are re-read from epscheck.json unchanged.)"""
import json
from mpmath import mp, mpf, nstr, exp, euler, pi
mp.dps = 60
OURS = mpf('0.14173323966388719139541530708686641')      # cycle 15 published (35 sig digits)
M1   = mpf('0.141733239663887191395415685084185024')     # m1 cycle-16 "true" root
d = json.load(open('epscheck.json'))['60']
r = {row['eps']: mpf(row['r']) for row in d['rows']}
r0 = mpf(d['r0']); kap = mpf(d['kappa']); CF = exp(euler)/(4*pi)
pred13 = r0 + kap*mpf('1e-13')**2
out = dict(
  r_at_1e12                = nstr(r['1e-12'], 40),
  ours_published           = nstr(OURS, 36),
  r_1e12_minus_ours        = nstr(r['1e-12'] - OURS, 6),
  digits_r1e12_vs_ours     = nstr(-mp.log10(abs(r['1e-12']-OURS)/abs(OURS)), 5),
  r0_extrapolated          = nstr(r0, 40),
  m1_operative             = nstr(M1, 36),
  r0_minus_m1              = nstr(r0 - M1, 6),
  digits_r0_vs_m1          = nstr(-mp.log10(abs(r0-M1)/abs(M1)), 5),
  kappa_fitted             = nstr(kap, 15),
  kappa_m1_analytic        = "-0.377997318614",
  m1_minus_ours            = nstr(M1 - OURS, 8),
  minus_kappa_eps2         = nstr(-kap*mpf('1e-12')**2, 8),
  ratio                    = nstr((M1-OURS)/(-kap*mpf('1e-12')**2), 12),
  OUT_OF_SAMPLE_1e13_pred  = nstr(pred13, 40),
  OUT_OF_SAMPLE_1e13_meas  = nstr(r['1e-13'], 40),
  OUT_OF_SAMPLE_rel_err    = nstr(abs(pred13-r['1e-13'])/abs(r['1e-13']), 6),
  r0_minus_egamma_over_4pi = nstr(r0 - CF, 8),
  digits_r0_vs_closedform  = nstr(-mp.log10(abs(r0-CF)/abs(CF)), 6),
)
print(json.dumps(out, indent=1)); json.dump(out, open('epsfix.json','w'), indent=1)
