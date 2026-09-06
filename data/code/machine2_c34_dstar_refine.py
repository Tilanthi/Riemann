"""machine2 CYCLE 34, step 1 -- refine D* and give it its OWN error bar.

c33 measured `D*_true - D*_literal = -3.7685544e-37` from a single dps-70 root find whose
residual was 1.44892e-71.  A single root find cannot report its own error: it prints a
residual, and a residual divided by an unmeasured derivative is not an error bar.  So:

  * root-find  D -> xi_D(1/2)  at dps 70 / 90 / 110 / 130 / 150 (independent Zeta2 objects,
    independent lattice cut-offs -- `cut = (dps+guard) ln 10` changes the number of lattice
    terms, so these are not the same computation at more digits),
  * report the residual AND the measured derivative f'(D*) so residual/|f'| is a real bound,
  * report the SPREAD of the five determinations: that, not any one residual, is the
    error bar on the refined centre.

Certificate = stability under refinement.  A reading is not a certificate.
"""
import sys
import time

import mpmath as mp

sys.path.insert(0, "/workspace/rh/cycle21")
from m2_zeta2_xi import Zeta2  # noqa: E402

LIT = "0.141733239663887191395415685084185024"


def root_at(dps, guard=25):
    with mp.workdps(dps + 25):
        def f(D):
            return Zeta2(D, dps=dps, guard=guard).xi(mp.mpf(1) / 2)
        t0 = time.time()
        # tol is on |f|^2 and the evaluator floors at ~1e-dps, so 2*dps is unreachable
        # by construction; ask for (2*dps - 12), i.e. |f| ~ 1e-(dps-6).
        D = mp.findroot(f, mp.mpf(LIT), tol=mp.mpf(10) ** (-(2 * dps - 12)))
        res = f(D)
        # measured derivative: central difference well inside the trusted range
        h = mp.mpf(10) ** (-(dps // 3))
        fp = (f(D + h) - f(D - h)) / (2 * h)
        return D, res, fp, time.time() - t0


if __name__ == "__main__":
    mp.mp.dps = 200
    lit = mp.mpf(LIT)
    rows = []
    for dps in [70, 90, 110, 130, 150]:
        D, res, fp, wall = root_at(dps)
        rows.append((dps, D, res, fp, wall))
        print(f"dps={dps:4d}  D* = {mp.nstr(D, 60)}")
        print(f"          residual = {mp.nstr(abs(res), 6)}   f'(D*) = {mp.nstr(fp, 12)}"
              f"   residual/|f'| = {mp.nstr(abs(res / fp), 6)}   [{wall:.0f}s]", flush=True)
    print("\n## spread against the dps=150 determination (this is the error bar):")
    ref = rows[-1][1]
    for dps, D, res, fp, wall in rows:
        print(f"   dps={dps:4d}   D*-D*_150 = {mp.nstr(D - ref, 6)}")
    print("\n## against the carried c33/c32 literal:")
    for dps, D, res, fp, wall in rows:
        print(f"   dps={dps:4d}   D*-D*_literal = {mp.nstr(D - lit, 10)}")
    print("\nD*_refined (dps=150 determination, 80 digits):")
    print("  " + mp.nstr(rows[-1][1], 80, strip_zeros=False))
