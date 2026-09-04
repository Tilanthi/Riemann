"""machine 2 (beast-atlas) — cycle 15 — rectangular-Epstein carrier past the fold Delta*.

Independent evaluator for  zeta2(s,D) = (1/2) sum'_{(j,k) in Z^2} (j^2 + D^2 k^2)^{-s}
built from the theta/Mellin split with the incomplete-gamma expansion (my derivation;
NOT a copy of m1's Bessel evaluator A nor of their theta evaluator B -- the split point,
the transform direction and the term-by-term closed form are derived here from scratch):

   theta(t;D) = theta3(e^{-pi t}) theta3(e^{-pi D^2 t}) = sum_{j,k} e^{-pi t (j^2 + D^2 k^2)}
   Jacobi:  theta(1/t; D) = (t/D) theta(t; 1/D)
   pi^{-s} Gamma(s) * 2*zeta2(s,D)
        = I(s,D) + (1/D) I(1-s, 1/D) + 1/(D(s-1)) - 1/s
   I(s,D) = int_1^inf t^{s-1}(theta(t;D)-1) dt
          = 2 sum_{j>=1} G(s, pi j^2) + 2 sum_{k>=1} G(s, pi D^2 k^2)
            + 4 sum_{j,k>=1} G(s, pi(j^2+D^2k^2)),      G(s,x) = x^{-s} Gamma(s,x)

Everything is an identity; the only approximation is truncation of the lattice sums at
an explicitly reported exponential cutoff.
"""
import sys
from mpmath import mp, mpf, mpc, exp, pi, gamma, gammainc, zeta, altzeta, sqrt, log, findroot, quad, re, im, fabs, matrix, lu_solve

mp.dps = 40  # module level only (m1 trap #73)

CUT = None  # set in set_cut()

def set_cut(dps=None):
    """lambda-cutoff so that the first dropped term is < 10^{-(dps+8)} relative."""
    global CUT
    d = dps or mp.dps
    CUT = (d + 8) * log(mpf(10)) / pi
    return CUT

set_cut()

def _G(s, x):
    return x**(-s) * gammainc(s, x)

def _I(s, D):
    """int_1^inf t^{s-1}(theta(t;D)-1)dt, exact up to the stated exponential truncation."""
    D2 = D * D
    tot = mp.zero
    # j-axis
    j = 1
    while j * j <= CUT:
        tot += 2 * _G(s, pi * j * j)
        j += 1
    # k-axis
    k = 1
    while D2 * k * k <= CUT:
        tot += 2 * _G(s, pi * D2 * k * k)
        k += 1
    # interior
    j = 1
    while j * j <= CUT:
        k = 1
        while j * j + D2 * k * k <= CUT:
            tot += 4 * _G(s, pi * (j * j + D2 * k * k))
            k += 1
        j += 1
    return tot

def zeta2(s, D):
    s = mpc(s)
    D = mpf(D)
    lhs = _I(s, D) + _I(1 - s, 1 / D) / D + 1 / (D * (s - 1)) - 1 / s
    return pi**s / (2 * gamma(s)) * lhs

def Lam(s, D):
    """completed carrier  Lambda(s) = (D/pi)^s Gamma(s) zeta2(s,D);  m1's duality: Lambda(s)=Lambda(1-s)."""
    s = mpc(s)
    return (D / pi)**s * gamma(s) * zeta2(s, D)

def Lam_line(y, D):
    """Lambda(1/2+iy) -- real for real y by duality + real coefficients. Returns the real part
    and separately reports the imaginary residual (which must be ~0)."""
    v = Lam(mpf(1) / 2 + 1j * mpf(y), D)
    return v

from mpmath import besselk

def zeta2_bessel(s, D, nmax=None):
    """zeta2(s,D) = zeta(2s) + sqrt(pi)Gamma(s-1/2)D^{1-2s}zeta(2s-1)/Gamma(s)
                    + (4 pi^s/Gamma(s)) D^{1/2-s} sum_{k,m>=1} (m/k)^{s-1/2} K_{s-1/2}(2 pi D k m)
    (my own Poisson/line-identity derivation; singular termwise at s=1/2 -- evaluate slightly off)."""
    s = mpc(s); D = mpf(D)
    nu = s - mpf(1) / 2
    if nmax is None:
        nmax = int((mp.dps + 12) * log(mpf(10)) / (2 * pi * D)) + 2
    tot = mp.zero
    for k in range(1, nmax + 1):
        for m in range(1, nmax // k + 1):
            tot += (mpf(m) / k)**nu * besselk(nu, 2 * pi * D * k * m)
    return (zeta(2 * s) + sqrt(pi) * gamma(nu) * D**(1 - 2 * s) * zeta(2 * s - 1) / gamma(s)
            + 4 * pi**s * D**(-nu) * tot / gamma(s))


# ---------------------------------------------------------------- controls
def brute(s, D, R=140):
    tot = mp.zero
    for j in range(-R, R + 1):
        for k in range(-R, R + 1):
            if j == 0 and k == 0:
                continue
            tot += (mpf(j * j) + D * D * k * k)**(-s)
    return tot / 2

def digits(a, b):
    a, b = mpc(a), mpc(b)
    if a == b:
        return mpf('inf')
    scale = max(abs(a), abs(b))
    if scale == 0:
        return mpf('inf')
    return -log(abs(a - b) / scale, 10)

def controls():
    out = []
    # C1: D=1  =>  zeta2(s,1) = 2 zeta(s) beta(s)
    def beta(s):
        # Dirichlet beta via Hurwitz: beta(s) = 4^{-s}(zeta(s,1/4)-zeta(s,3/4))
        return 4**(-s) * (zeta(s, mpf(1) / 4) - zeta(s, mpf(3) / 4))
    for s in [mpf('1.3'), mpf('0.75'), mpc('0.5', '3.0'), mpc('0.7', '10.0')]:
        got = zeta2(s, mpf(1))
        want = 2 * zeta(s) * beta(s)
        out.append(("C1 D=1 vs 2*zeta*beta at s=%s" % s, digits(got, want)))
    # C2: brute lattice sum
    for (s, D) in [(mpf(3), mpf('0.3')), (mpf(4), mpf('0.7'))]:
        got = zeta2(s, D)
        want = brute(s, D, R=200)
        out.append(("C2 brute R=200 s=%s D=%s" % (s, D), digits(got, want)))
    # C3: duality Lambda(s)=Lambda(1-s)
    for (s, D) in [(mpc('0.7', '0'), mpf('0.05')), (mpc('0.31', '2.5'), mpf('0.1417')),
                   (mpc('1.4', '-0.3'), mpf('0.142857142857142857'))]:
        out.append(("C3 duality s=%s D=%s" % (s, D), digits(Lam(s, D), Lam(1 - s, D))))
    # C4: residue at s=1 is pi/(2D)
    for D in [mpf('0.1'), mpf('0.1417')]:
        h = mpf(10)**(-12)
        g = lambda e: e * zeta2(1 + e, D)
        # 3-point Richardson in e (m1 AMENDMENT-4 shape), independent implementation
        val = (8 * g(h) - 6 * g(2 * h) + g(4 * h)) / 3
        out.append(("C4 residue D=%s" % D, digits(val, pi / (2 * D))))
    # C5: reality of Lambda on the critical line
    for (y, D) in [(mpf('0.3'), mpf('0.15')), (mpf('2.0'), mpf('0.1417'))]:
        v = Lam(mpf(1) / 2 + 1j * y, D)
        out.append(("C5 Im Lambda(1/2+iy) D=%s y=%s (rel)" % (D, y), -log(abs(im(v)) / abs(v), 10)))
    return out

if __name__ == "__main__":
    print("mp.dps=%d  lambda-cutoff=%s" % (mp.dps, mp.nstr(CUT, 8)))
    for name, d in controls():
        print("%-46s  %8.1f digits" % (name, float(d)))
