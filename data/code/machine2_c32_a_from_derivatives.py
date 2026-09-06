"""machine2 CYCLE 32 -- LADDER-FREE determination of the fold constant `a`.

WHY THIS INSTRUMENT EXISTS
--------------------------
m1's heat72x/heat86b lineage and m2's own c30/c31 lineage determine `a` the SAME WAY: solve
u(eps) on a ladder, form r = (u^2 - a_used*eps + b*eps^2)/eps^3 with a DISPUTED constant in
the header, and read the eps^-2 coefficient of r.  That is ONE METHOD run on two evaluators.
Their agreement is evidence about the evaluators, not about the method.

Here `a` NEVER APPEARS AS AN INPUT.  No ladder, no eps grid, no r column, no least squares,
no fit basis, no b, no K.  Two Taylor coefficients of one analytic function at one point:

  xi_D(1/2+w) is EVEN in w (self-duality xi(s)=xi(1-s))  =>  xi_D(1/2+w) = F(w^2, D).
  At the fold F(0, D*) = 0 (that IS the definition of D*).
  F_x * x + F_D * (D - D*) + ... = 0,  and zeros sit at s = 1/2 + i u  =>  x = w^2 = -u^2
  =>  u^2 = (F_D/F_x) * (D* - D) = a * eps,     eps := D* - D
  =>  a = F_D / F_x.

Stencils are 4th order and written out here (no library differentiator: mpmath's mp.diff
silently returns 0.0 against this evaluator because Zeta2 clamps working precision with
`workdps`, which discards mp.diff's internal precision boost -- recorded as a live gotcha).
"""
import sys
import time

import mpmath as mp

sys.path.insert(0, "/workspace/rh/cycle21")
from m2_zeta2_xi import Zeta2  # noqa: E402

# The three-machine operative D*, identical literal to my own c30 runner (DECLARED SHARED INPUT).
DSTAR_STR = "0.141733239663887191395415685084185024"

# Candidate values of `a`.  USED ONLY FOR COMPARISON AT THE END, never as input.
REFS = [
    ("retired 16 s.f.", "2.645521411811663"),
    ("#120 19 s.f.   ", "2.645521411811664489"),
    ("m1 band-A 22sf ", "2.645521411811662855605"),
    ("operative 17sf ", "2.6455214118116629"),
]


def run(dps, hexp_w, hexp_D, guard=25):
    mp.mp.dps = dps + 10
    DSTAR = mp.mpf(DSTAR_STR)
    half = mp.mpf(1) / 2
    hw = mp.mpf(10) ** (-hexp_w)
    hD = mp.mpf(10) ** (-hexp_D)

    Z0 = Zeta2(DSTAR, dps=dps, guard=guard)
    f0 = Z0.xi(half)
    f1 = Z0.xi(half + hw)
    f2 = Z0.xi(half + 2 * hw)
    fm1 = Z0.xi(half - hw)          # evenness control
    A = f1 - f0
    B = f2 - f0
    Fx = (16 * A - B) / (12 * hw ** 2)          # 4th-order, uses evenness (f(-w)=f(w))
    even_resid = abs(f1 - fm1) / (abs(f1) + abs(f0) + mp.mpf(10) ** (-dps))

    def g(D):
        return Zeta2(D, dps=dps, guard=guard).xi(half)

    gp2, gp1, gm1, gm2 = g(DSTAR + 2 * hD), g(DSTAR + hD), g(DSTAR - hD), g(DSTAR - 2 * hD)
    FD = (-gp2 + 8 * gp1 - 8 * gm1 + gm2) / (12 * hD)   # 4th-order central

    return dict(dps=dps, hexp_w=hexp_w, hexp_D=hexp_D, f0=f0, Fx=Fx, FD=FD,
                a=FD / Fx, even_resid=even_resid)


def main():
    configs = [
        (60, 10, 12),
        (80, 14, 16),
        (100, 18, 20),
        (110, 20, 22),
    ]
    rows = []
    for dps, hw, hD in configs:
        t0 = time.time()
        r = run(dps, hw, hD)
        r["secs"] = time.time() - t0
        rows.append(r)
        mp.mp.dps = 60
        print(f"dps={dps:4d} h_w=1e-{hw:<3d} h_D=1e-{hD:<3d}  "
              f"xi(1/2,D*)={mp.nstr(r['f0'],6):>14s}  even={mp.nstr(r['even_resid'],3):>10s}")
        print(f"          F_x = {mp.nstr(r['Fx'], 32)}")
        print(f"          F_D = {mp.nstr(r['FD'], 32)}")
        print(f"          a   = {mp.nstr(r['a'], 32)}      [{r['secs']:.1f}s]")
    print()
    print("=== STABILITY UNDER REFINEMENT (the certificate, not any single reading) ===")
    for i in range(1, len(rows)):
        mp.mp.dps = 60
        d = rows[i]["a"] - rows[i - 1]["a"]
        print(f"  a(cfg{i+1}) - a(cfg{i}) = {mp.nstr(d, 8)}")
    print()
    mp.mp.dps = 60
    a = rows[-1]["a"]
    print(f"=== LADDER-FREE a (finest config) ===\n  a = {mp.nstr(a, 30)}")
    print()
    for name, s in REFS:
        print(f"  a - [{name} {s:<24s}] = {mp.nstr(a - mp.mpf(s), 8)}")


if __name__ == "__main__":
    main()
