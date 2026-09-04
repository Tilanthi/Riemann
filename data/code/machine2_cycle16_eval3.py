"""E3 -- the ANCESTRY-CLEAN evaluator (condition 5).

E1 (cycle-15 incomplete-gamma theta split) and E2 (this cycle's Bessel/Chowla-Selberg form)
BOTH descend from the Jacobi theta transformation.  They are ONE ancestor with two names and
their agreement is what a common ancestor predicts, not independent confirmation.

E3 uses no theta transformation, no functional equation and no Bessel function: raw lattice
counting of a_n = #{(j,k): j^2+49k^2=n}/2 plus Abel summation with the ellipse main term.

  F(s) = sum_{n<=N} a_n n^{-s} - A(N) N^{-s} + (pi/14) s N^{1-s}/(s-1) + s int_N^inf E(x) x^{-s-1} dx
  A(x) = sum_{n<=x} a_n = (pi/14) x + E(x),   |E(x)| <= C x^{1/3}   (van der Corput exponent;
  C measured on this very lattice, and the measurement is printed as the bound's denominator)

=> |error| <= |s| C N^{1/3-sigma} / (sigma - 1/3).  Usable for sigma well above 1/3; the bound is
printed with every value so the reader sees the resolution, not just the digits.
"""
import numpy as np, math
from mpmath import mp, mpf, mpc, mpmathify

_cache = {}

def build(N):
    if N in _cache: return _cache[N]
    counts = np.zeros(N + 1, dtype=np.int64)
    kmax = int(math.isqrt(N // 49))
    for k in range(-kmax, kmax + 1):
        rem = N - 49 * k * k
        jmax = int(math.isqrt(rem))
        js = np.arange(-jmax, jmax + 1, dtype=np.int64)
        n = js * js + 49 * k * k
        n = n[n > 0]
        np.add.at(counts, n, 1)
    a = counts / 2.0
    A = np.cumsum(a)
    x = np.arange(0, N + 1, dtype=np.float64)
    E = A - (math.pi / 14) * x
    _cache[N] = (a, A, E)
    return _cache[N]

def C_measured(N):
    a, A, E = build(N)
    x = np.arange(1, N + 1, dtype=np.float64)
    return float(np.max(np.abs(E[1:]) / x ** (1.0 / 3.0)))

def F3(s, N):
    """returns (value, rigorous-modulo-C error bound)."""
    s = mpmathify(s)
    a, A, E = build(N)
    ns = np.arange(1, N + 1, dtype=np.float64)
    nz = np.nonzero(a[1:])[0] + 1
    w = a[nz]
    # sum a_n n^{-s} in float128-free complex128 (values are O(1), no cancellation issue at this
    # precision level -- E3 is a 4-5 digit instrument by construction, see the bound)
    sc = complex(s)
    tot = np.sum(w * np.exp(-sc * np.log(nz.astype(np.float64))))
    tot -= A[N] * math.e ** (0) * complex(np.exp(-sc * math.log(N)))
    tot += complex((math.pi / 14)) * sc * complex(np.exp((1 - sc) * math.log(N))) / (sc - 1)
    C = C_measured(N)
    sig = float(mp.re(s))
    bound = abs(sc) * C * N ** (1.0 / 3.0 - sig) / (sig - 1.0 / 3.0)
    return complex(tot), bound
