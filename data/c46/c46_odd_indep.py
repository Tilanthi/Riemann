#!/usr/bin/env python3
"""c46_odd_indep.py -- K5: an end-to-end SECOND PATH to the odd block at small N.

K1 proves the c46 assembly IS c42's assembly (max entrywise difference exactly 0), so the odd block
inherits every receipt the even block has earned from m1 and m3. The only genuinely new algebra in
c46 is the closed form for the odd correlation g^odd_{jk}(t). K2/K3 test that closed form pointwise
against quadrature. K5 tests it END TO END: it rebuilds the whole odd matrix with the closed form
REPLACED by direct numerical quadrature of the defining integral, at a small N where that is
affordable, and compares the two smallest eigenvalues.

A pointwise agreement and an eigenvalue agreement are different claims: the second is the one the
cycle's headline rests on, because a smallest eigenvalue of a nearly singular matrix can be moved by
an error that is invisible entrywise.

usage: c46_odd_indep.py [N] [X] [DPS] [GLDEG] [ITERS]     defaults 16 13 60 9 16
"""
import sys, os, time, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "c42"))
from mpmath import mp, mpf, exp, log, pi, sqrt, euler, cosh, sin
from mpmath.calculus.quadrature import GaussLegendre
import c42_connes_x as c42
import c46_parity as c46

N = int(sys.argv[1]) if len(sys.argv) > 1 else 16
X = int(sys.argv[2]) if len(sys.argv) > 2 else 13
DPS = int(sys.argv[3]) if len(sys.argv) > 3 else 60
GLDEG = int(sys.argv[4]) if len(sys.argv) > 4 else 9
ITERS = int(sys.argv[5]) if len(sys.argv) > 5 else 16
PDEG = int(sys.argv[6]) if len(sys.argv) > 6 else 3
mp.dps = DPS


def g_matrix_quad(t, L, om, nr, panel_deg=3):
    """the SAME g_{jk}(t) = INT psi_j(s) psi_k(s+t) ds, by PANELLED Gauss-Legendre quadrature of the
    defining integral, with no closed form anywhere. Two knobs, both declared: the panel count
    4*n+2 (>= 4 panels per shortest half-period of the fastest mode w_n = 2 pi n / L) and the
    per-panel GL degree. K5 varies the degree as its own convergence check."""
    n = len(om)
    G = [[mpf(0)] * n for _ in range(n)]
    a0, b0 = -L / 2, L / 2 - t
    npan = 4 * n + 2
    gl = GaussLegendre(mp)
    for i in range(npan):
        pa = a0 + (b0 - a0) * mpf(i) / npan
        pb = a0 + (b0 - a0) * mpf(i + 1) / npan
        for (s, w) in gl.get_nodes(pa, pb, panel_deg, mp.prec):
            u = [nr[a] * sin(om[a] * s) for a in range(n)]
            v = [nr[b] * sin(om[b] * (s + t)) for b in range(n)]
            for a in range(n):
                wu = w * u[a]
                Ga = G[a]
                for b in range(n):
                    Ga[b] += wu * v[b]
    return G


def build_quad(N, x, gl_degree, PANEL_DEG=3):
    L = log(mpf(x))
    om, nr, idx = c46.make_basis_parity(N, L, "odd")
    n = len(om)
    M = [[mpf(0)] * n for _ in range(n)]
    gl = GaussLegendre(mp)
    nodes = gl.get_nodes(mpf(0), L, gl_degree, mp.prec)
    for (t, w) in nodes:
        G = g_matrix_quad(t, L, om, nr, PANEL_DEG)
        wp = w * 4 * cosh(t / 2)
        den = 1 - exp(-2 * t)
        wa = w * 2 * (-exp(-t / 2)) / den
        wdiag = w * 2 * exp(-2 * t) / den
        wc = wp + wa
        for a in range(n):
            for b in range(a):
                M[a][b] += wc * G[a][b]
            M[a][a] += wc * G[a][a] + wdiag
    cst = -(log(pi) + euler) + 2 * (-log(1 - exp(-2 * L)) / 2)
    for a in range(n):
        M[a][a] += cst
    for (nn, lam) in c42.prime_powers_upto(x):
        t = log(mpf(nn))
        G = g_matrix_quad(t, L, om, nr, PANEL_DEG)
        c = -2 * lam / sqrt(mpf(nn))
        for a in range(n):
            for b in range(a + 1):
                M[a][b] += c * G[a][b]
    for a in range(n):
        for b in range(a + 1, n):
            M[a][b] = M[b][a]
    return M


t0 = time.time()
Mq = build_quad(N, X, GLDEG, PDEG)
t1 = time.time()
Mc, L, pps = c46.build_matrix_parity(N, X, GLDEG, "odd")
worst = max(abs(Mq[i][j] - Mc[i][j]) for i in range(len(Mq)) for j in range(len(Mq)))
scale = max(abs(Mc[i][j]) for i in range(len(Mc)) for j in range(len(Mc)))
lq, _ = c42.smallest_eigenpair(Mq, iters=ITERS, verbose=False)
lc, _ = c42.smallest_eigenpair(Mc, iters=ITERS, verbose=False)
rel = abs(lq - lc) / abs(lc)
agree_sf = int(mp.floor(-mp.log(rel, 10))) if rel > 0 else DPS
out = dict(N=N, x=X, dps=DPS, gl_degree=GLDEG, iters=ITERS, panel_deg=PDEG,
           max_entry_diff=mp.nstr(worst, 8), matrix_scale=mp.nstr(scale, 8),
           lambda_quadrature=mp.nstr(lq, 40), lambda_closed_form=mp.nstr(lc, 40),
           rel_diff=mp.nstr(rel, 8), agreement_sf=agree_sf,
           seconds_quad=t1 - t0, seconds_total=time.time() - t0)
json.dump(out, open(os.path.join(HERE, "c46_K5_indep_N%d_x%d_dps%d_p%d.json" % (N, X, DPS, PDEG)), "w"), indent=1)
print("K5 odd block, quadrature vs closed form, N=%d x=%d dps=%d" % (N, X, DPS))
print("   max entry diff = %s   (matrix scale %s)" % (out["max_entry_diff"], out["matrix_scale"]))
print("   lambda_min quadrature  = %s" % out["lambda_quadrature"])
print("   lambda_min closed form = %s" % out["lambda_closed_form"])
print("   relative difference = %s  -> agree to %d s.f.  [%.1fs]"
      % (out["rel_diff"], agree_sf, out["seconds_total"]))
print("   NOTE: this is an AGREEMENT DEPTH, not a lower bound -- both sides are printed at 40 s.f.,")
print("   wider than the agreement, so the agreement is not censored by either print width.")
