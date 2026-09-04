"""machine 2 -- cycle 17 -- E2b: E2 with the (k,m) double sum collapsed onto the divisor sum.

Identity used (exact, no new approximation):
  sum_{k,m>=1} (7k)^{1/2-s} m^{s-1/2} K_{s-1/2}(14 pi m k)
    = sum_{n>=1} [ 7^{1/2-s} n^{s-1/2} sigma_{1-2s}(n) ] K_{s-1/2}(14 pi n),   sigma_a(n)=sum_{d|n} d^a
because the Bessel argument depends on (k,m) only through n = k*m.
This is Chowla-Selberg's own grouping; it is NOT a new evaluator, it is E2 with the terms
that share a Bessel argument added before the Bessel call.  Purpose: E2 spends ~all of its
time inside besselk, and this cuts the number of besselk calls by the divisor multiplicity
(14 calls -> 6 calls at t=118, dps 20).  Verified against E2 term-for-term in fastcheck.py.
"""
from mpmath import mp, mpf, mpc, pi, sqrt, gamma, zeta, besselk, mpmathify

_div_cache = {}
def divisors(n):
    if n in _div_cache: return _div_cache[n]
    d = [k for k in range(1, n+1) if n % k == 0]
    _div_cache[n] = d
    return d

def nmax_needed(s, dps):
    t = abs(float(mp.im(s)))
    cut = 3.141592653589793 * t / 2 + dps * 2.302585092994046 + 20
    return int(cut / (14 * 3.141592653589793))

def F(s, dps_pad=10):
    s = mpmathify(s)
    prec0 = mp.dps
    mp.dps = prec0 + dps_pad
    try:
        half = mpf(1)/2
        nu = s - half
        tot = zeta(2*s) + sqrt(pi)*(gamma(nu)/gamma(s))*mpf(7)**(1-2*s)*zeta(2*s-1)
        pref = 4*pi**s/gamma(s) * mpf(7)**(half-s)
        acc = mp.zero
        for n in range(1, nmax_needed(s, prec0+dps_pad)+1):
            sig = mp.zero
            for d in divisors(n):
                sig += mpf(d)**(1-2*s)
            acc += mpf(n)**nu * sig * besselk(nu, 14*pi*n)
        return +(tot + pref*acc)
    finally:
        mp.dps = prec0
