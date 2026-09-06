"""machine2 CYCLE 32 -- the WHOLE fold expansion by Taylor coefficients, no ladder, no header.

Extends this cycle's ladder-free determination of `a` to b and a3.  The disputed constants a and
b are HEADER INPUTS to every published r-column in the exchange; a3 is then read off that column.
So an error in a or b propagates into a3 IDENTICALLY on every instrument that uses the same
header -- which is all of them.  This file computes a, b and a3 as Taylor coefficients of one
analytic function, with no header of any kind.

  h(w, e) := xi_D(1/2 + w, D* - e)   is EVEN in w  =>  h(w,e) = G(w^2, e),  G(0,0) = 0.
  Solve G(x, e) = 0 as a power series x(e) = A e + B e^2 + C e^3 + ...,  and u^2 = -x, so
      u^2 = a e + c2 e^2 + a3 e^3 + ...    with a = -A, c2 = -B (= -b), a3 = -C.

  G's coefficients g_{mn} = [x^m e^n] G come from
    * w:  a Cauchy contour integral on |w| = r_w  (exact coefficient extraction, no cancellation)
    * e:  a high-order central finite difference in D (one Zeta2 object per node)

Certificate is STABILITY UNDER REFINEMENT of (r_w, N_w, h_e, dps), not any single reading.
"""
import sys
import time

import mpmath as mp

sys.path.insert(0, "/workspace/rh/cycle21")
from m2_zeta2_xi import Zeta2  # noqa: E402

DSTAR_STR = "0.141733239663887191395415685084185024"
MMAX = 3          # powers of x
NMAX = 3          # powers of e

PUB = {
    "a ": ("2.645521411811662868016126121", "ladder-free derivative value, this cycle"),
    "b ": ("-7.4624528767937415788", "published header literal (m2 c30 runner B)"),
    "a3": ("11.70071732105115376305", "the V2 reference m1-L171 confirms 'to 19 s.f.'"),
}
FIT = {"a ": "2.64552141181166286801613", "b ": "-7.46245287679368626753358",
       "a3": "11.7007173204336676011627"}


def w_coeffs(Z, half, r, N, kmax):
    """Even Taylor coefficients c_k of h(w) = xi(1/2+w) at w=0, by Cauchy on |w|=r."""
    vals = []
    for j in range(N):
        th = 2 * mp.pi * j / N
        vals.append(Z.xi(half + r * mp.e ** (1j * th)))
    out = []
    for k in range(kmax + 1):
        s = mp.mpf(0)
        for j, v in enumerate(vals):
            th = 2 * mp.pi * j / N
            s += v * mp.e ** (-1j * k * th)
        out.append((s / N) / r ** k)
    return out


def fd_weights(n, order_pts):
    """central finite-difference weights for the n-th derivative on symmetric integer nodes."""
    m = order_pts // 2
    nodes = list(range(-m, m + 1))
    A = mp.matrix(len(nodes), len(nodes))
    for i, p in enumerate(nodes):
        for j in range(len(nodes)):
            A[i, j] = mp.mpf(p) ** j
    rhs = mp.matrix(len(nodes), 1)
    rhs[n] = mp.factorial(n)
    w = mp.lu_solve(A.T, rhs)      # solve A^T w = rhs  (Vandermonde transpose)
    return nodes, w


def run(dps, r_w, N_w, hexp_e, npts=9, guard=25):
    mp.mp.dps = dps + 10
    DSTAR = mp.mpf(DSTAR_STR)
    half = mp.mpf(1) / 2
    he = mp.mpf(10) ** (-hexp_e)
    nodes, wts = fd_weights(0, npts)          # placeholder; recomputed per order below

    # w-coefficients at each e node.  e = D* - D  =>  D = D* - e
    kmax = 2 * MMAX
    table = {}
    for p in range(-(npts // 2), npts // 2 + 1):
        e = p * he
        Z = Zeta2(DSTAR - e, dps=dps, guard=guard)
        table[p] = w_coeffs(Z, half, r_w, N_w, kmax)

    # g[m][n] = (1/n!) d^n/de^n  c_{2m}(e)  at e=0
    g = [[None] * (NMAX + 1) for _ in range(MMAX + 1)]
    for m in range(MMAX + 1):
        for n in range(NMAX + 1):
            nodes, wts = fd_weights(n, npts)
            s = mp.mpf(0)
            for idx, p in enumerate(nodes):
                s += wts[idx] * table[p][2 * m]
            g[m][n] = (s / he ** n) / mp.factorial(n)

    # series solve G(x,e)=0
    g00 = g[0][0]
    A = -g[0][1] / g[1][0]
    B = -(g[0][2] + g[1][1] * A + g[2][0] * A ** 2) / g[1][0]
    C = -(g[0][3] + g[1][2] * A + g[1][1] * B + g[2][0] * 2 * A * B
          + g[2][1] * A ** 2 + g[3][0] * A ** 3) / g[1][0]
    return dict(g00=g00, a=-A, c2=-B, a3=-C, g=g)


def main():
    cfgs = [
        (70, "0.03", 20, 12),
        (85, "0.05", 24, 14),
        (100, "0.05", 28, 16),
    ]
    prev = None
    for dps, r, N, he in cfgs:
        t0 = time.time()
        R = run(dps, mp.mpf(r), N, he)
        mp.mp.dps = 60
        print(f"\n### dps={dps} r_w={r} N_w={N} h_e=1e-{he}   [{time.time()-t0:.0f}s]")
        print(f"   G(0,0) = xi(1/2,D*) = {mp.nstr(R['g00'],6)}  (defining residual of D*)")
        print(f"   a  = {mp.nstr(R['a'], 26)}")
        print(f"   b  = {mp.nstr(-R['c2'], 26)}")
        print(f"   a3 = {mp.nstr(R['a3'], 26)}")
        if prev:
            print(f"   refinement deltas:  a {mp.nstr(R['a']-prev['a'],5)}   "
                  f"b {mp.nstr(R['c2']-prev['c2'],5)}   a3 {mp.nstr(R['a3']-prev['a3'],5)}")
        prev = R
    mp.mp.dps = 60
    print("\n=== COMPARISON (finest config) ===")
    got = {"a ": prev["a"], "b ": -prev["c2"], "a3": prev["a3"]}
    for k in ["a ", "b ", "a3"]:
        pub, note = PUB[k]
        print(f"  {k}: derivative = {mp.nstr(got[k], 24)}")
        print(f"      header-free ladder fit (K=8) = {FIT[k]}   diff = "
              f"{mp.nstr(got[k]-mp.mpf(FIT[k]), 6)}")
        print(f"      published {pub:<28s} diff = {mp.nstr(got[k]-mp.mpf(pub), 6)}   [{note}]")


if __name__ == "__main__":
    main()
