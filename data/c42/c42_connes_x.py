#!/usr/bin/env python3
"""
c42_connes_x.py — Connes arXiv:2602.04022, letter experiment, recomputed at arbitrary x.

CONVENTION STRING (must be carried with every number this file emits):
  basis      : phi_0 = 1/sqrt(L); phi_k = sqrt(2/L) cos(w_k t), w_k = 2 pi k / L, k=1..N
               on t in [-L/2, L/2], L = log(x)   (t = log u; support of eta_x recentred)
  form       : QW(f,f) = W(g), g(t) = INT f(s) f(s+t) ds, W = the explicit formula of c42_weil.py
               W(g) = h(i/2)+h(-i/2) - g(0) log pi + (1/2pi) INT h(r) Re psi(1/4+ir/2) dr
                      - 2 SUM_{n>=2} Lambda(n) n^{-1/2} g(log n)
  primes     : the sum is FINITE and runs over prime powers n <= x  (support of g is [-L,L])
  minimise   : min over ||f||_{L2(dt)} = 1  ->  smallest eigenpair of the (N+1)x(N+1) matrix M
  approximant: F(r) = INT f(t) e^{irt} dt = Mellin transform of eta_x on the critical line;
               its positive real zeros r_n are compared with gamma_n (zeros of zeta)
  truncation : N = 100 is the letter's own footnote-14 convention ("trigonometric truncation")
  quadrature : fixed Gauss-Legendre, degree given per run, on [0, L]
"""
import sys, time, json
from mpmath import mp, mpf, mpmathify, exp, log, pi, sqrt, euler, cos, sin, cosh, mangoldt
from mpmath.calculus.quadrature import GaussLegendre


# ---------------------------------------------------------------- basis correlations
def make_basis(N, L):
    """returns (omega[j], norm[j]) for j=0..N"""
    om = [2 * pi * j / L for j in range(N + 1)]
    nr = [1 / sqrt(L)] + [sqrt(2 / L) for _ in range(N)]
    return om, nr


def g_entry(j, k, t, N, L, om, nr):
    """g_{jk}(t) = INT phi_j(s) phi_k(s+t) ds, closed form, valid for 0 <= t <= L."""
    d = om[j] - om[k]
    e = om[j] + om[k]
    eps = mpf(1) if (j + k) % 2 == 0 else mpf(-1)
    Id = (L - t) if j == k else -eps * sin(d * t) / d
    Ie = (L - t) if (j == 0 and k == 0) else -eps * sin(e * t) / e
    C = (Id + Ie) / 2
    Sd = mpf(0) if j == k else eps * (1 - cos(d * t)) / d
    Se = mpf(0) if (j == 0 and k == 0) else eps * (1 - cos(e * t)) / e
    S = (Se - Sd) / 2
    return nr[j] * nr[k] * (cos(om[k] * t) * C - sin(om[k] * t) * S)


def g_matrix_at(t, N, L, om, nr):
    """full symmetric matrix [g_{jk}(t)] via angle addition (one trig pair per index)."""
    cw = [cos(om[j] * t) for j in range(N + 1)]
    sw = [sin(om[j] * t) for j in range(N + 1)]
    Lt = L - t
    G = [[None] * (N + 1) for _ in range(N + 1)]
    for j in range(N + 1):
        cj, sj = cw[j], sw[j]
        for k in range(j + 1):
            ck, sk = cw[k], sw[k]
            eps = mpf(1) if (j + k) % 2 == 0 else mpf(-1)
            sd = sj * ck - cj * sk
            se = sj * ck + cj * sk
            cd = cj * ck + sj * sk
            ce = cj * ck - sj * sk
            d = om[j] - om[k]
            e = om[j] + om[k]
            if j == k:
                Id, Sd = Lt, mpf(0)
            else:
                Id, Sd = -eps * sd / d, eps * (1 - cd) / d
            if j == 0 and k == 0:
                Ie, Se = Lt, mpf(0)
            else:
                Ie, Se = -eps * se / e, eps * (1 - ce) / e
            v = nr[j] * nr[k] * (ck * ((Id + Ie) / 2) - sk * ((Se - Sd) / 2))
            G[j][k] = v
            G[k][j] = v
    return G


# ---------------------------------------------------------------- the matrix of the form
def prime_powers_upto(x):
    out = []
    n = 2
    while n <= x:
        lam = mangoldt(n)
        if lam != 0:
            out.append((n, lam))
        n += 1
    return out


def build_matrix(N, x, gl_degree, verbose=True):
    L = log(mpf(x))
    om, nr = make_basis(N, L)
    n = N + 1
    M = [[mpf(0)] * n for _ in range(n)]

    gl = GaussLegendre(mp)
    nodes = gl.get_nodes(mpf(0), L, gl_degree, mp.prec)
    if verbose:
        print("  GL nodes on [0,L]: %d" % len(nodes), flush=True)

    t0 = time.time()
    for idx, (t, w) in enumerate(nodes):
        G = g_matrix_at(t, N, L, om, nr)
        wp = w * 4 * cosh(t / 2)                       # pole term weight (g even -> 4*INT_0^L)
        den = 1 - exp(-2 * t)
        wa = w * 2 * (-exp(-t / 2)) / den              # archimedean, g-dependent part
        wdiag = w * 2 * exp(-2 * t) / den              # archimedean, g(0)=delta_{jk} part
        wc = wp + wa
        for j in range(n):
            Mj, Gj = M[j], G[j]
            for k in range(j):
                Mj[k] += wc * Gj[k]
            Mj[j] += wc * Gj[j] + wdiag   # combined: each piece alone has a 1/t pole at 0
        if verbose and idx % 50 == 0:
            print("    node %d/%d  %.1fs" % (idx, len(nodes), time.time() - t0), flush=True)

    # archimedean constants and the [L,inf) tail (g vanishes there, only the g(0) part survives)
    cst = -(log(pi) + euler) + 2 * (-log(1 - exp(-2 * L)) / 2)
    for j in range(n):
        M[j][j] += cst

    # prime powers
    pps = prime_powers_upto(x)
    if verbose:
        print("  prime powers <= %s : %s" % (x, [p for p, _ in pps]), flush=True)
    for (nn, lam) in pps:
        t = log(mpf(nn))
        G = g_matrix_at(t, N, L, om, nr)
        c = -2 * lam / sqrt(mpf(nn))
        for j in range(n):
            Mj, Gj = M[j], G[j]
            for k in range(j + 1):
                Mj[k] += c * Gj[k]

    for j in range(n):
        for k in range(j + 1, n):
            M[j][k] = M[k][j]
    return M, L, om, nr, [p for p, _ in pps]


# ---------------------------------------------------------------- smallest eigenpair
def smallest_eigenpair(M, iters=4, verbose=True):
    n = len(M)
    A = mp.matrix(M)
    v = mp.matrix([mpf(1) / sqrt(n)] * n)
    lam = None
    for it in range(iters):
        w = mp.lu_solve(A, v)
        nrm = sqrt(sum(wi ** 2 for wi in w))
        v = w / nrm
        Av = A * v
        lam = sum(v[i] * Av[i] for i in range(n))
        res = sqrt(sum((Av[i] - lam * v[i]) ** 2 for i in range(n)))
        if verbose:
            print("    inv-iter %d: lam=%s res=%s" % (it, mp.nstr(lam, 8), mp.nstr(res, 5)), flush=True)
    return lam, v


# ---------------------------------------------------------------- the Mellin transform
def make_G(v, om, nr, L, N):
    """F(r) = sin(rL/2) * G(r); returns G and G'."""
    coef = [nr[k] * v[k] * (mpf(1) if k % 2 == 0 else mpf(-1)) for k in range(N + 1)]

    def Gf(r):
        s = 2 * coef[0] / r
        for k in range(1, N + 1):
            s += coef[k] * 2 * r / (r * r - om[k] ** 2)
        return s

    def dGf(r):
        s = -2 * coef[0] / (r * r)
        for k in range(1, N + 1):
            w2 = om[k] ** 2
            s += -2 * coef[k] * (r * r + w2) / (r * r - w2) ** 2
        return s
    return Gf, dGf
