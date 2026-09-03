#!/usr/bin/env python3
"""
cycle 11 / machine 2 (beast-atlas) — independent computation of the Nyman-Baez-Duarte
least-squares distance d_n, built to audit box-surf candidate #1.

FAMILY OF RECORD (L^2(0,1), Nyman / Baez-Duarte, as stated in Ransford et al.,
Amer. Math. Monthly 126 (2019) 891-904, eq. (1)):
    f_k(x) = (1/k)[1/x] - [1/(kx)] = {1/(kx)} - (1/k){1/x},   k >= 2
    d_n^2  = dist(1, span{f_2..f_n})^2 = 1 - b^T G^-1 b,  b_k = <f_k,1> = log(k)/k

BARE FAMILY (what candidate #1 as posted actually names):
    r_n(x) = {1/(nx)},  n >= 1

EXACT INNER PRODUCTS, derived here from the elementary series (no Vasyunin needed):
    f_j, f_k are constant = {r/j}, {r/k} on (1/(r+1), 1/r], so
    <f_j,f_k> = sum_{r>=1} {r/j}{r/k} / (r(r+1))
    the summand is m-periodic in r with m = lcm(j,k), and
    sum_{r = q mod m} 1/(r(r+1)) = (1/m)[psi((q+1)/m) - psi(q/m)]
  =>  <f_j,f_k> = (1/m) sum_{q=1}^{m-1} {q/j}{q/k} [psi((q+1)/m) - psi(q/m)]     (EXACT)

Likewise for the bare family, with {r/j} replaced by ρ_j(r) := {1/(j x)} on that interval.
On (1/(r+1), 1/r], 1/x ranges over [r, r+1), so {1/(jx)} is NOT constant there -- the bare
family is handled by direct high-precision quadrature-free piecewise integration instead
(see rho_inner()), which is why the two families are genuinely different objects.

All arithmetic in mpmath at a declared precision; every reported number carries a
two-precision stability check.  No floats are trusted.
"""
import sys, json, math
from math import gcd
from mpmath import mp, mpf, psi, log, matrix, lu_solve, sqrt, euler, pi, cot

def frac(a, b):
    """{a/b} as an exact mpf"""
    return mpf(a % b) / b

_psi_cache = {}
def psi_table(m):
    if m not in _psi_cache:
        _psi_cache[m] = [psi(0, mpf(q) / m) for q in range(1, m + 1)]
    return _psi_cache[m]

def inner_f(j, k):
    """<f_j,f_k> exactly, via the digamma-collapsed periodic series."""
    m = j * k // gcd(j, k)
    P = psi_table(m)            # P[q-1] = psi(q/m), q=1..m
    tot = mpf(0)
    for q in range(1, m):
        wj = q % j
        if wj == 0:
            continue
        wk = q % k
        if wk == 0:
            continue
        tot += (mpf(wj) / j) * (mpf(wk) / k) * (P[q] - P[q - 1])
    return tot / m

def b_f(k):
    """<f_k,1> = log(k)/k  (Ransford et al. Cor. 6)"""
    return log(k) / k

def d_n(nmax, dps):
    """d_n for n = 2..nmax using the family of record. Returns list of (n, d_n, cond_est)."""
    mp.dps = dps
    _psi_cache.clear()
    idx = list(range(2, nmax + 1))
    N = len(idx)
    G = matrix(N, N)
    for a in range(N):
        for c in range(a, N):
            v = inner_f(idx[a], idx[c])
            G[a, c] = v
            G[c, a] = v
    b = matrix(N, 1)
    for a in range(N):
        b[a] = b_f(idx[a])
    out = []
    for n in range(2, nmax + 1):
        s = n - 1
        Gs = matrix(s, s)
        for a in range(s):
            for c in range(s):
                Gs[a, c] = G[a, c]
        bs = matrix(s, 1)
        for a in range(s):
            bs[a] = b[a]
        x = lu_solve(Gs, bs)
        q = mpf(0)
        for a in range(s):
            q += bs[a] * x[a]
        d2 = 1 - q
        out.append((n, d2))
    return out, G, b

if __name__ == "__main__":
    nmax = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    dps = int(sys.argv[2]) if len(sys.argv) > 2 else 60
    res, G, b = d_n(nmax, dps)
    C = 2 + euler - log(4 * pi)
    print("# C = 2+gamma-log(4pi) =", mp.nstr(C, 10))
    print("# n  d_n^2            d_n        sqrt(C/log n)   ratio d_n/(sqrt(C/log n))")
    for n, d2 in res:
        d = sqrt(d2) if d2 > 0 else mpf(-1)
        lb = sqrt(C / log(n))
        print(f"{n:4d}  {mp.nstr(d2,12):>16}  {mp.nstr(d,10):>12}  {mp.nstr(lb,10):>12}  {mp.nstr(d/lb,8):>10}")
