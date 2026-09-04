"""machine 2 -- cycle 17 -- general-Delta Epstein evaluator (E2b generalised).

zeta2(s,Delta) = (1/2) sum'_{j,k} (j^2 + Delta^2 k^2)^{-s}
Scaling identity (exact): zeta2(s,D) = D^{-2s} zeta2(s,1/D).  We always evaluate at E = max(D,1/D)
so the Bessel arguments 2 pi E n are as LARGE as possible (this is cycle 16's E2 lesson).
  zeta2(s,E) = zeta(2s) + sqrt(pi) Gamma(s-1/2) E^{1-2s} zeta(2s-1)/Gamma(s)
             + (4 pi^s/Gamma(s)) E^{1/2-s} sum_n n^{s-1/2} sigma_{1-2s}(n) K_{s-1/2}(2 pi E n)
"""
from mpmath import mp, mpf, mpc, pi, sqrt, gamma, zeta, besselk, mpmathify, log
_dc = {}
def divisors(n):
    if n not in _dc: _dc[n] = [k for k in range(1, n+1) if n % k == 0]
    return _dc[n]

def zeta2(s, D, pad=12):
    s = mpmathify(s); D = mpf(D)
    prec0 = mp.dps; mp.dps = prec0 + pad
    try:
        flip = D < 1
        E = 1/D if flip else D
        half = mpf(1)/2; nu = s - half
        t = abs(mp.im(s))
        cut = pi*t/2 + (prec0+pad)*log(mpf(10)) + 25
        nmax = int(cut/(2*pi*E)) + 2
        acc = mp.zero
        for n in range(1, nmax+1):
            sig = mp.zero
            for d in divisors(n): sig += mpf(d)**(1-2*s)
            acc += mpf(n)**nu * sig * besselk(nu, 2*pi*E*n)
        val = (zeta(2*s) + sqrt(pi)*gamma(nu)*E**(1-2*s)*zeta(2*s-1)/gamma(s)
               + 4*pi**s*E**(half-s)*acc/gamma(s))
        if flip: val = D**(-2*s) * val
        return +val
    finally:
        mp.dps = prec0
