#!/usr/bin/env python3
"""
c42_weil.py — the Weil explicit formula as an INSTRUMENT, plus its known-answer test.

CONVENTION STRING (carry this with every number produced by this file):
  W(g) = h(i/2)+h(-i/2) - g(0) log(pi) + (1/2pi) INT h(r) Re psi(1/4+ir/2) dr
         - 2 SUM_{n>=2} Lambda(n) n^{-1/2} g(log n)
  h(r) = INT g(t) e^{irt} dt ;  g even, real ;  zeros indexed by gamma with rho = 1/2 + i gamma
  claim under RH:  W(g) = SUM over ALL nontrivial zeros of h(gamma) = 2 SUM_{n>=1} h(gamma_n)

The archimedean integral is rewritten in t-space (exact, no oscillatory quadrature):
  (1/2pi) INT h(r) Re psi(1/4+ir/2) dr
      = -gammaE*g(0) + 2 INT_0^inf [ e^{-2t} g(0) - e^{-t/2} g(t) ] / (1-e^{-2t}) dt
"""
import sys
from mpmath import mp, mpf, exp, log, pi, sqrt, euler, quad, inf, zetazero, mangoldt


def weil_functional(g, dps=None, nmax=None, arch_upper=None):
    """W(g) for an even test function g (callable, mpf->mpf), decaying at infinity."""
    g0 = g(mpf(0))
    # pole terms
    pole = quad(lambda t: g(t) * (exp(t / 2) + exp(-t / 2)), [-arch_upper, 0, arch_upper])
    # archimedean
    def arch_integrand(t):
        if t == 0:
            return mpf(0)
        return (exp(-2 * t) * g0 - exp(-t / 2) * g(t)) / (1 - exp(-2 * t))
    arch = -g0 * log(pi) - euler * g0 + 2 * quad(arch_integrand, [0, 1, arch_upper])
    # prime powers
    s = mpf(0)
    for n in range(2, nmax + 1):
        lam = mangoldt(n)
        if lam == 0:
            continue
        s += lam / sqrt(mpf(n)) * g(log(n))
    prime = -2 * s
    return pole + arch + prime, dict(pole=pole, arch=arch, prime=prime)


def zero_side(h, nzeros):
    tot = mpf(0)
    for n in range(1, nzeros + 1):
        gam = zetazero(n).imag
        tot += 2 * h(gam)
    return tot


if __name__ == "__main__":
    mp.dps = 50
    print("KAT-1: explicit formula, Gaussian test functions. dps=%d" % mp.dps)
    for s_par, nmax, nz, au in ((mpf("0.2"), 4000, 40, 30), (mpf(1), 300000, 40, 40)):
        g = lambda t, s=s_par: exp(-t ** 2 / (2 * s ** 2))
        h = lambda r, s=s_par: s * sqrt(2 * pi) * exp(-(s ** 2) * r ** 2 / 2)
        W, parts = weil_functional(g, nmax=nmax, arch_upper=au)
        Z = zero_side(h, nz)
        print("  s=%s  W=%s" % (s_par, mp.nstr(W, 25)))
        print("         Z=%s   rel.diff=%s" % (mp.nstr(Z, 25), mp.nstr(abs(W - Z) / abs(Z), 5)))
        print("         parts: pole=%s arch=%s prime=%s"
              % (mp.nstr(parts['pole'], 12), mp.nstr(parts['arch'], 12), mp.nstr(parts['prime'], 12)))
