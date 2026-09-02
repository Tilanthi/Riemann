import mpmath as mp
import json, sys, datetime

# =====================================================================
# T2g: kappa5 (and kappa6 as a bonus) at all 7 sites, both normalizations
#      (plain c_n = nth Taylor coeff of ln[Xi/(z^2-d^2)] ; jet a_n = n! c_n)
#
# PRE-REGISTRATION (written before this script is executed, not after):
#   Method: identical convention-free direct Taylor-coefficient extraction
#   used for kappa1..kappa4 in T2f (mp.taylor of ln[Xi(m0+z)/(z^2-d^2)]
#   about z=0, Xi evaluated directly via zeta/Gamma, mpmath dps=50).
#   No zero-table sum, no window, no mirror-term, no index convention.
#   This is a genuinely independent instrument from any zero-sum method
#   Mac or BEAST-AGI might use for kappa5.
#
#   Falsifier / cross-check plan: BEAST-AGI's erratum (machine2_ERRATUM_1)
#   states they will "republish" corrected kappa3 AND kappa5 at all six
#   of their sites once the flip is fully audited. When that lands, my
#   kappa5 values below should be compared to theirs BEFORE either side
#   adjusts anything. Agreement to >=4 sig figs at >=5/6 shared sites
#   would be a 2nd-instrument confirmation exactly like kappa1/B/kappa2
#   already have; disagreement should be reported honestly (as kappa3
#   at Lehmer was, in letter2) not smoothed over.
#
#   No numeric target is being pre-committed here (unlike BEAST's E1-E6
#   experiments) because I have no independently-derived closed-form
#   prediction for kappa5 to test against -- this is a pure measurement,
#   reported as [NUMERIC], not a falsifier test.
# =====================================================================

# Site (m0, d) pairs are loaded from T2f_coefficients.json (the corrected,
# in-place-fixed authority for these numbers -- see letter7 / MEMORY.md for
# the "first buggy midpoint attempt" telescope fix history) rather than
# hand-transcribed, specifically to avoid reintroducing a stale value.
# (Self-caught bug during this script's own development: an earlier draft
# copied the site dict out of T2f_direct_coefficients_all_sites.py's SOURCE
# instead of its JSON output, and that source file still has the old,
# never-updated telescope m0 = 71732.9014623404596 -- about 0.007 off from
# the true midpoint 71732.90855861..., i.e. off by about one d. That
# produced numerically garbage kappa5/kappa6 at the telescope site on the
# first run of this script -- see the ERRATUM note in the letter that
# reports these results. Loading from JSON here fixes it and also fixes
# the stale source file in place for future reuse.)
with open('/data/Riemann/results/T2f_coefficients.json') as fh:
    _t2f = json.load(fh)

mp.mp.dps = 50

sites = {name: (mp.mpf(v['m0']), mp.mpf(v['d'])) for name, v in _t2f.items()}

def make_f(m0, d):
    def f(z, m0=m0, d=d):
        s = mp.mpf('0.5') + 1j*(m0+z)
        Xi_val = mp.mpf('0.5')*s*(s-1)*mp.power(mp.pi, -s/2)*mp.gamma(s/2)*mp.zeta(s)
        return mp.log(Xi_val / (z**2 - d**2))
    return f

import math
results = {}
for name,(m0,d) in sites.items():
    f = make_f(m0,d)
    coeffs = mp.taylor(f, 0, 6)   # need order 6 to have a clean kappa6 too
    c1,c2,c3,c4,c5,c6 = coeffs[1],coeffs[2],coeffs[3],coeffs[4],coeffs[5],coeffs[6]
    B  = -2*c2
    k2 = -(1/d**2 + B/2)
    k1,k3,k4,k5,k6 = c1,c3,c4,c5,c6
    # jet normalization a_n = n! c_n
    a1 = mp.factorial(1)*c1
    a2 = mp.factorial(2)*c2
    a3 = mp.factorial(3)*c3
    a4 = mp.factorial(4)*c4
    a5 = mp.factorial(5)*c5
    a6 = mp.factorial(6)*c6
    results[name] = dict(
        m0=str(m0), d=str(d),
        plain=dict(kappa1=str(k1), B=str(B), kappa2=str(k2), kappa3=str(k3),
                   kappa4=str(k4), kappa5=str(k5), kappa6=str(k6)),
        jet=dict(a1=str(a1), a2=str(a2), a3=str(a3), a4=str(a4), a5=str(a5), a6=str(a6)),
    )
    print(name + ':  m0=' + str(float(m0)) + '  d=' + str(float(d)))
    print('   [plain] kappa5 = ' + str(k5))
    print('   [plain] kappa6 = ' + str(k6))
    print('   [jet]   a5     = ' + str(a5))
    print('   [jet]   a6     = ' + str(a6))
    print()
    sys.stdout.flush()

out = {
    'note': 'T2g kappa5/kappa6 direct Taylor-coefficient measurement, both plain and jet normalization, all 7 sites. See PRE-REGISTRATION comment block in T2g_kappa5_prereg.py for method and cross-check plan (written before execution).',
    'sites': results,
}
json.dump(out, open('/data/Riemann/results/T2g_kappa5_coefficients.json','w'), indent=1)
print('wrote /data/Riemann/results/T2g_kappa5_coefficients.json')
