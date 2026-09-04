"""machine 2 (beast-atlas) -- cycle 19 -- Epstein evaluator, D-general form of cycle-16's E2.

F_D(s) = zeta2(s, D) = (1/2) sum'_{(j,k) in Z^2} (j^2 + D^2 k^2)^{-s}
       = sum_{n>=1} a_n n^{-s}   (Re s > 1) whenever D^2 is a positive integer,
         a_n = (1/2)#{(j,k): j^2 + D^2 k^2 = n},  a_1 = 1.

Chowla-Selberg / k-direction Poisson form (identical algebra to cycle 16's eval2.py with the
literal 7 replaced by D; the cycle-16 lesson that the SCALING must be applied first is honoured
by choosing D >= 1, so the Bessel argument 2*pi*D*m*k is large and no digits are lost):

  F_D(s) = zeta(2s)
         + sqrt(pi) (Gamma(s-1/2)/Gamma(s)) D^{1-2s} zeta(2s-1)
         + (4 pi^s / Gamma(s)) sum_{k>=1} (D k)^{1/2-s} sum_{m>=1} m^{s-1/2} K_{s-1/2}(2 pi D m k)

The prefactor 4 pi^s/Gamma(s) is huge (~e^{+pi t/2}) and K_{s-1/2} is tiny (~e^{-pi t/2}); they are
multiplied, never subtracted, so relative precision survives with height (cycle-16 finding: the E1
theta-split loses 0.6822*t digits and returned pure noise at t=43 and dps=20).

CARRIERS OF THIS CYCLE
  D = 7        -> Delta = 1/7      = 0.142857...  ABOVE Delta*  (fold pair on the critical line)
  D = sqrt(50) -> Delta = 1/sqrt50 = 0.141421...  BELOW Delta*  (fold pair REAL, i.e. off-line)
Both have a_1 = 1 and Delta = 1/sqrt(q), q integer, so both are in the ordinary-Dirichlet-series
transfer class (cycle-15 membership rule).
"""
from mpmath import mp, mpf, mpc, pi, sqrt, gamma, zeta, besselk, mpmathify

_pairs_cache = {}


def _pairs(cut, D):
    key = (round(float(cut), 6), float(D))
    if key in _pairs_cache:
        return _pairs_cache[key]
    out = []
    twopiD = 2 * 3.141592653589793 * float(D)
    kmax = int(cut / twopiD) + 1
    for k in range(1, kmax + 1):
        m = 1
        while twopiD * m * k <= cut:
            out.append((k, m))
            m += 1
    _pairs_cache[key] = out
    return out


def bessel_terms_used(s, D, digits):
    t = abs(float(mp.im(s)))
    cut = 3.141592653589793 * t / 2 + digits * 2.302585092994046 + 20
    return _pairs(cut, D)


def F(s, D, dps_pad=10):
    """F_D(s) = zeta2(s, D) at the current mp.dps."""
    s = mpmathify(s)
    D = mpmathify(D)
    prec0 = mp.dps
    mp.dps = prec0 + dps_pad
    try:
        half = mpf(1) / 2
        tot = zeta(2 * s) + sqrt(pi) * (gamma(s - half) / gamma(s)) * D ** (1 - 2 * s) * zeta(2 * s - 1)
        pref = 4 * pi ** s / gamma(s)
        acc = mp.zero
        for (k, m) in bessel_terms_used(s, D, prec0 + dps_pad):
            acc += (D * k) ** (half - s) * mpf(m) ** (s - half) * besselk(s - half, 2 * pi * D * m * k)
        tot += pref * acc
        return +tot
    finally:
        mp.dps = prec0


def residue_at_1(D):
    """Res_{s=1} F_D(s) = pi/(2D)   (area of the fundamental domain is D)."""
    return pi / (2 * mpmathify(D))
