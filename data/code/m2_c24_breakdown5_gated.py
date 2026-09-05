"""cycle24 -- RE-RUN of the breakdown scan for the cell where MY OWN DIAGNOSTIC BROKE.

breakdown.py reported basis 5 first-bad-gamma = 20 at degrees 7,8,9 AND 10 alike.  That is
physically impossible for a resolution threshold (monotone in gamma and in degree), and the
monotonicity violation is what caught it: the composite ground truth at ppw=4 has its own
relative error ~5e-12 on basis 5 near gamma=20, ABOVE the 1e-12 tolerance the scan was applying.
The subject was fine (deg-8 relative error there is 1.15e-19); the INSTRUMENT OF AUDIT was not.

Fix, and it is the general one: never call a departure that is inside the ground truth's own
uncertainty.  Criterion becomes  |u_d - T| > max(TOL*|T|, 8*|T_ppw8 - T_ppw16|).
"""
import sys, json
sys.path.insert(0, "/shared/rh-exchange-repo/Riemann/data/code")
sys.path.insert(0, "/workspace/rh-c24")
from mpmath import mp
import m2_u_instrument as U
from gt_u import u_repo, u_composite

mp.dps = 50
TOL = mp.mpf("1e-12")
gens = U.load_genomes("s1/M8")
out = {}
for i in (5,):
    phi, bumps = U.make_phi(gens[i])
    ivs = U.intervals(bumps)
    for d in (7, 8, 9, 10):
        brk = None
        for g in range(20, 421, 20):
            gg = mp.mpf(g)
            t8, _ = u_composite(phi, ivs, gg, ppw=8, deg=4)
            t16, _ = u_composite(phi, ivs, gg, ppw=16, deg=4)
            unc = 8 * abs(t8 - t16)
            ud = u_repo(phi, ivs, gg, d)
            dep = abs(ud - t16)
            if dep > max(TOL * abs(t16), unc):
                brk = g
                print("   basis %d deg %d gamma %d: dep=%s  tol=%s  gt-unc=%s -> BAD"
                      % (i, d, g, mp.nstr(dep, 4), mp.nstr(TOL*abs(t16), 4), mp.nstr(unc, 4)), flush=True)
                break
        print("basis %d deg=%d first-bad-gamma(gated) = %s" % (i, d, brk), flush=True)
        out["%d_%d" % (i, d)] = brk
json.dump(out, open("/workspace/rh-c24/breakdown5.json", "w"), indent=1)
