"""machine 2 (beast-atlas) -- cycle 16 -- STABLE evaluator E2 for the VOID wedge.

F(s) := 49^{-s} zeta2(s, 1/7) = zeta2(s, 7) = (1/2) sum'_{(j,k)} (j^2 + 49 k^2)^{-s}
      = sum_{n>=1} a_n n^{-s}   (sigma > 1),   a_n = #{(j,k): j^2+49k^2 = n}/2,  a_1 = 1.

Zeros of zeta2(s,1/7) == zeros of F, since 49^s never vanishes.

WHY A NEW EVALUATOR (this is the cycle-16 finding, not a preference):
cycle 15's E1 (incomplete-gamma theta split) computes pi^{-s}Gamma(s)*2*zeta2 as a sum of
terms of size O(1/|s|), while |Gamma(s)| ~ e^{-pi t/2}.  At t = 43 that is
e^{-67.5} ~ 10^{-29}: THIRTY digits of cancellation.  E1 at dps 20 returns NOISE there.
The cycle-15 stage-7 box (Re[0.52,2] x Im[20,43], dps 20) is exactly that regime.

E2 is the k-direction Poisson/Bessel form (Chowla-Selberg shape) applied AFTER the
scaling identity zeta2(s,D) = D^{-2s} zeta2(s, 1/D), so the Bessel argument is 14*pi*m*k
(large) rather than 2*pi*m*k/7 (small):

  F(s) = zeta(2s)
       + sqrt(pi) * (Gamma(s-1/2)/Gamma(s)) * 7^{1-2s} * zeta(2s-1)
       + (4 pi^s / Gamma(s)) * sum_{k>=1} (7k)^{1/2-s} sum_{m>=1} m^{s-1/2} K_{s-1/2}(14 pi m k)

The two large/small factors (4 pi^s/Gamma(s) ~ 1e20 at t=30, K ~ 1e-20) are each computed at
full RELATIVE precision and multiplied -- there is no subtraction of nearly equal numbers,
so E2 loses no digits with height.

ANCESTRY NOTE (cycle-16 verification condition 5): E1 and E2 are NOT independent.  Both
descend from the Jacobi theta transformation theta(1/t) = ... .  They are one ancestor with
two names and their agreement is what a common ancestor predicts.  The ancestry-clean check
is E3 (lattice counting + partial summation, no theta, no functional equation) in eval3.py.
"""
from mpmath import mp, mpf, mpc, pi, sqrt, gamma, zeta, besselk, exp, log, mpmathify

__all__ = ["F", "Fp", "bessel_terms_used"]

_bessel_pairs_cache = {}


def _pairs(cut):
    """(k, m) pairs with 14*pi*m*k <= cut, ordered."""
    key = float(cut)
    if key in _bessel_pairs_cache:
        return _bessel_pairs_cache[key]
    out = []
    kmax = int(cut / (14 * 3.141592653589793)) + 1
    for k in range(1, kmax + 1):
        m = 1
        while 14 * 3.141592653589793 * m * k <= cut:
            out.append((k, m))
            m += 1
    _bessel_pairs_cache[key] = out
    return out


def bessel_terms_used(s, extra_digits=None):
    d = extra_digits if extra_digits is not None else mp.dps
    t = abs(float(mp.im(s)))
    # need 14 pi m k >= pi t /2 (to beat the 1/Gamma(s) growth) + d*ln10 (for d digits)
    cut = 3.141592653589793 * t / 2 + d * 2.302585092994046 + 20
    return _pairs(cut)


def F(s, dps_pad=10):
    """F(s) = zeta2(s,7).  Returns an mpf/mpc at current mp.dps."""
    s = mpmathify(s)
    prec0 = mp.dps
    mp.dps = prec0 + dps_pad
    try:
        half = mpf(1) / 2
        tot = zeta(2 * s) + sqrt(pi) * (gamma(s - half) / gamma(s)) * mpf(7) ** (1 - 2 * s) * zeta(2 * s - 1)
        pref = 4 * pi ** s / gamma(s)
        acc = mp.zero
        for (k, m) in bessel_terms_used(s, prec0 + dps_pad):
            acc += (mpf(7) * k) ** (half - s) * mpf(m) ** (s - half) * besselk(s - half, 14 * pi * m * k)
        tot += pref * acc
        return +tot
    finally:
        mp.dps = prec0


def Fp(s, h=None):
    """F'(s) by a symmetric complex-step-free central difference at working precision."""
    s = mpmathify(s)
    if h is None:
        h = mpf(10) ** (-(mp.dps // 3))
    return (F(s + h) - F(s - h)) / (2 * h)
