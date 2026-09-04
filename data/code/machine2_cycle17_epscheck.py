"""machine 2 -- cycle 17 -- the eps_eff check m1 asked for (their Delta* is PROPOSED pending it).

CLAIM UNDER TEST (m1, trap #89): our published cycle-15 Delta* is the root of the eps-PERTURBED
map D -> zeta2(1/2+eps, D) at eps = 1e-12 EXACTLY, and r(eps) = r_true + kappa*eps^2 with
kappa = -A_ss/(2 A_D) = -0.377997318614, so m1_true - ours = -kappa*(1e-12)^2 = 3.7799732e-25.

TEST: root-find r(eps) for several eps, fit r(eps) = r0 + kappa*eps^2 + O(eps^4), and compare
  (a) r(1e-12) against our PUBLISHED cycle-15 number  -> is eps_eff really 1e-12?
  (b) r0 against m1's operative Delta*
  (c) fitted kappa against the analytic kappa
Controls: two precisions.  All roots to tol 1e-80.
"""
import json, sys
from mpmath import mp, mpf, findroot, re, nstr, exp, euler, pi, diff
import foldeval

OURS  = mpf('0.14173323966388719139541530708686641')       # cycle 15, published
M1    = mpf('0.141733239663887191395415685084185024')      # m1 cycle-16 reply, "true" root
CF    = None

def r_of_eps(eps, dps):
    mp.dps = dps
    s0 = mpf(1)/2 + mpf(eps)
    return findroot(lambda D: re(foldeval.zeta2(s0, mpf(D))), mpf('0.1417332396638872'),
                    tol=mpf(10)**(-80))

if __name__ == "__main__":
    out = {}
    for dps in (60, 80):
        mp.dps = dps
        CF = exp(euler)/(4*pi)
        rows = []
        for e in ['1e-12','2e-12','4e-12','8e-12','1e-13']:
            r = r_of_eps(e, dps)
            rows.append(dict(eps=e, r=nstr(r, 40)))
            print(dps, e, nstr(r, 40), flush=True)
        # quadratic fit on the first four: r = r0 + kappa eps^2
        import itertools
        e1, r1 = mpf('1e-12'), mpf(rows[0]['r'])
        e2, r2 = mpf('2e-12'), mpf(rows[1]['r'])
        kappa = (r2 - r1)/(e2**2 - e1**2)
        r0 = r1 - kappa*e1**2
        out[dps] = dict(rows=rows, kappa=nstr(kappa, 15), r0=nstr(r0, 40),
                        r0_minus_m1=nstr(r0 - M1, 8), r1_minus_ours=nstr(r1 - OURS, 8),
                        m1_minus_ours=nstr(M1 - OURS, 10), cf=nstr(CF, 40),
                        r0_minus_cf=nstr(r0 - CF, 8))
        print(json.dumps(out[dps], indent=1), flush=True)
    json.dump(out, open('epscheck.json','w'), indent=1)
