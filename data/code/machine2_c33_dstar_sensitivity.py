"""machine2 CYCLE 33 -- D* is an INPUT to the derivative route.  Measure what it costs.

c32's law: enumerate what the instruments SHARE and state what the agreement is blind to.
The derivative route and the header-free ladder fit share exactly two things: the Zeta2
evaluator and the D* literal.  This file measures the second one.

(1) Re-derive D* itself by an independent path -- a 1-D root find of D -> xi_D(1/2, D) --
    and report the difference from the carried literal.
(2) Measure d(coefficient)/dD* by a central difference of the whole cfg-A pipeline at
    D* +- delta, so the induced error in a, b, a3, a4, a5 is a measured number, not a hope.
"""
import os
import sys
import time

import mpmath as mp

sys.path.insert(0, "/workspace/rh/cycle21")
sys.path.insert(0, "/workspace/rh/cycle33")
from m2_zeta2_xi import Zeta2  # noqa: E402
import m2_c33_fold5 as F  # noqa: E402
from multiprocessing import Pool  # noqa: E402

LIT = "0.141733239663887191395415685084185024"
NAMES = F.NAMES


def refind_dstar(dps=70, guard=25):
    """Independent determination of D*: root of D -> xi_D(1/2)."""
    with mp.workdps(dps + 20):
        def f(D):
            return Zeta2(D, dps=dps, guard=guard).xi(mp.mpf(1) / 2)
        D = mp.findroot(f, mp.mpf(LIT), tol=mp.mpf(10) ** (-2 * dps))
        return D, f(D)


def coeffs_at(dstar, cfg):
    F.DSTAR_STR = mp.nstr(dstar, 60, strip_zeros=False)
    os.environ["C33_DSTAR"] = F.DSTAR_STR
    with Pool(8, initializer=_init2, initargs=(cfg, F.DSTAR_STR)) as pool:
        R = F.run(cfg, pool)
    return R["x"]


def _init2(cfg, ds):
    F.DSTAR_STR = ds
    F._init(cfg)


if __name__ == "__main__":
    mp.mp.dps = 80
    t0 = time.time()
    D, res = refind_dstar()
    lit = mp.mpf(LIT)
    print("## (1) D* re-derived by an independent 1-D root find")
    print("   D*_rootfind = " + mp.nstr(D, 45))
    print("   D*_literal  = " + mp.nstr(lit, 45))
    print("   difference  = " + mp.nstr(D - lit, 8) + "     |xi(1/2,D*)| at the root = "
          + mp.nstr(abs(res), 6) + f"   [{time.time()-t0:.0f}s]")

    cfg = dict(label="S", dps=90, guard=25, r_w="0.04", N_w=40, npts=15, he=7)
    delta = mp.mpf(10) ** (-25)
    print("\n## (2) d(coefficient)/dD* by central difference of the whole pipeline, "
          f"delta = {mp.nstr(delta,3)}")
    xp = coeffs_at(lit + delta, cfg)
    xm = coeffs_at(lit - delta, cfg)
    x0 = coeffs_at(lit, cfg)
    err_lit = D - lit
    for i, nm in enumerate(NAMES):
        d = (xp[i + 1] - xm[i + 1]) / (2 * delta)
        print(f"   d{nm:>2s}/dD* = {mp.nstr(d, 12):>22s}    "
              f"induced error from the literal = {mp.nstr(d * err_lit, 6)}")
    print("\n   value at the literal (cfg S):")
    for i, nm in enumerate(NAMES):
        print(f"     {nm:>2s} = {mp.nstr(x0[i+1], 30)}")
