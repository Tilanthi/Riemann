"""machine 2 -- cycle 17 -- fast general-D Epstein evaluator for the FOLD region (eps_eff check).

zeta2(s,D) = D^{-2s} zeta2(s,1/D)      [scaling identity, exact]
and for E = 1/D > 1 (Chowla-Selberg / Poisson in the k-direction, divisor-grouped):
  zeta2(s,E) = zeta(2s) + sqrt(pi) Gamma(s-1/2) E^{1-2s} zeta(2s-1)/Gamma(s)
             + (4 pi^s/Gamma(s)) E^{1/2-s} sum_{n>=1} n^{s-1/2} sigma_{1-2s}(n) K_{s-1/2}(2 pi E n)
This is cycle 16's E2 with the (k,m) pairs grouped by n=km, generalised from E=7 to any E.
WHY: cycle 15's stage4 evaluated the Bessel sum at D ~ 0.1417 DIRECTLY (argument 2 pi D k m,
small) and needed ~900 Bessel calls per point; after the scaling identity the argument is
2 pi n / D ~ 44 n and 3-4 calls suffice.  Same function, same identity, ~200x cheaper.

NB the s -> 1/2 cancellation is REAL and is the whole point of the eps: zeta(2s) ~ 1/(2 eps)
and Gamma(s-1/2) ~ 1/eps individually blow up and cancel.  Digits lost ~ log10(1/eps).
Run at dps >= 60 for eps = 1e-12.
"""
from mpmath import mp, mpf, mpc, pi, sqrt, gamma, zeta, besselk, mpmathify, log

_dc = {}
def divisors(n):
    if n not in _dc: _dc[n] = [k for k in range(1, n+1) if n % k == 0]
    return _dc[n]

def zeta2(s, D, pad=15):
    s = mpmathify(s); D = mpf(D)
    prec0 = mp.dps
    mp.dps = prec0 + pad
    try:
        E = 1/D
        half = mpf(1)/2
        nu = s - half
        nmax = int(((prec0+pad)*log(mpf(10)) + 25)/(2*pi*E)) + 2
        acc = mp.zero
        for n in range(1, nmax+1):
            sig = mp.zero
            for d in divisors(n):
                sig += mpf(d)**(1-2*s)
            acc += mpf(n)**nu * sig * besselk(nu, 2*pi*E*n)
        val = (zeta(2*s) + sqrt(pi)*gamma(nu)*E**(1-2*s)*zeta(2*s-1)/gamma(s)
               + 4*pi**s*E**(half-s)*acc/gamma(s))
        return +(D**(-2*s) * val)
    finally:
        mp.dps = prec0
