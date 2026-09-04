"""machine 2 (beast-atlas) -- cycle 20 -- the CARRIER AXIS.

Cycle 19 measured a weighted Nyman-Beurling distance on four carriers and left one hole named:
the mechanism setting the ~0.94 stall on the two Epstein carriers is UNIDENTIFIED (reach/sparsity
refuted; "has an off-line zero near the line" excluded by the zeta*(1-2^{0.55-s}) contrast).

This module supplies the carriers of a 2x2x2 design over
      (simple pole at s=1) x (degree) x (off-line zeros present),
each normalised so that a_1 = 1 (d_N^2 is invariant under F -> lambda F, since g -> g/lambda and
the pole constraint a.c = 0 is scale free; normalising only makes the rows readable).

Every carrier is evaluated by mpmath primitives that are NOT the Epstein theta/Poisson evaluator,
so the Epstein rows and the L-function rows have disjoint code paths by construction.

Dirichlet L-functions are built from the Hurwitz zeta:  L(s,chi) = q^{-s} sum_{a=1}^{q} chi(a) zeta(s,a/q),
with chi = the Kronecker symbol (D/.) of a fundamental discriminant D, implemented here from scratch.
"""
from mpmath import mp, mpf, mpc, zeta, sqrt, mpmathify

# ----------------------------------------------------------------- Kronecker symbol (from scratch)
def kronecker(a, n):
    """Kronecker symbol (a/n) for integers a, n.  Written out, not imported."""
    if n == 0:
        return 1 if a in (1, -1) else 0
    sign = 1
    if n < 0:
        n = -n
        if a < 0:
            sign = -sign
    # factor out 2s from n
    e = 0
    while n % 2 == 0:
        n //= 2
        e += 1
    if e:
        if a % 2 == 0:
            return 0
        r = a % 8
        k2 = 1 if r in (1, 7) else -1
        if e % 2 == 1:
            sign *= k2
    # now n odd positive; Jacobi symbol (a/n)
    a = a % n
    result = 1
    while a:
        while a % 2 == 0:
            a //= 2
            if n % 8 in (3, 5):
                result = -result
        a, n = n, a
        if a % 4 == 3 and n % 4 == 3:
            result = -result
        a = a % n
    return sign * result if n == 1 else 0


def chi_coeffs(D):
    """[chi(0..|D|-1)] for the real primitive character mod |D| attached to fundamental disc D."""
    q = abs(D)
    return [kronecker(D, a) for a in range(q)]


def Lfun(s, D):
    """L(s, chi_D) via Hurwitz zeta.  D a fundamental discriminant."""
    q = abs(D)
    ch = chi_coeffs(D)
    tot = mp.zero
    for a in range(1, q + 1):
        c = ch[a % q]
        if c:
            tot += c * zeta(s, mpf(a) / q)
    return tot * mpf(q) ** (-s)


# ----------------------------------------------------------------- Davenport-Heilbronn
def dh_kappa():
    return (sqrt(10 - 2 * sqrt(5)) - 2) / (sqrt(5) - 1)


def DH(s):
    """Davenport-Heilbronn function: a_n 5-periodic (1, k, -k, -1, 0), entire, a_1 = 1."""
    k = dh_kappa()
    a = [mpf(1), k, -k, mpf(-1), mp.zero]
    tot = mp.zero
    for j in range(1, 6):
        if a[j - 1] != 0:
            tot += a[j - 1] * zeta(s, mpf(j) / 5)
    return tot * mpf(5) ** (-s)


# ----------------------------------------------------------------- binary-form Dirichlet coefficients
def form_coeffs(a, b, c, nmax):
    """a_n = (1/2) #{(x,y) in Z^2 : a x^2 + b x y + c y^2 = n}, for n <= nmax  (disc b^2-4ac < 0)."""
    out = [0] * (nmax + 1)
    import math
    disc = b * b - 4 * a * c
    assert disc < 0
    ylim = int(math.isqrt(int(4 * a * nmax // (-disc)))) + 2
    for y in range(-ylim, ylim + 1):
        # a x^2 + b x y + c y^2 = n  ->  solve for x range
        # a(x + by/(2a))^2 + (|disc|/(4a)) y^2 = n
        rem = nmax - (-disc) * y * y / (4.0 * a)
        if rem < 0:
            continue
        x0 = -b * y / (2.0 * a)
        w = math.sqrt(rem / a)
        for x in range(int(math.floor(x0 - w)) - 1, int(math.ceil(x0 + w)) + 2):
            n = a * x * x + b * x * y + c * y * y
            if 1 <= n <= nmax:
                out[n] += 1
    return [mpf(v) / 2 for v in out]


def dirichlet_coeffs_of(fun_coeffs_list, weights, nmax):
    out = [mp.zero] * (nmax + 1)
    for w, cs in zip(weights, fun_coeffs_list):
        for n in range(1, nmax + 1):
            out[n] += w * cs[n]
    return out


def convolve_coeffs(A, B, nmax):
    out = [mp.zero] * (nmax + 1)
    for i in range(1, nmax + 1):
        if A[i] == 0:
            continue
        for j in range(1, nmax // i + 1):
            out[i * j] += A[i] * B[j]
    return out


def char_coeffs(D, nmax):
    ch = chi_coeffs(D)
    q = abs(D)
    return [mp.zero] + [mpf(ch[n % q]) for n in range(1, nmax + 1)]


# ----------------------------------------------------------------- the carrier table
# key -> (label, has_pole, degree, offline_zeros_known, evaluator)
def carrier_eval(key, s):
    from eval_epstein import F as EF
    if key == "K1_zeta":
        return zeta(s)
    if key == "K2_zeta_synth":
        return zeta(s) * (1 - mpf(2) ** (mpf(1) / 2 + mpf('0.05') - s))
    if key == "K3_epstein_D7":
        return EF(s, 7)
    if key == "K4_epstein_Dsqrt50":
        return EF(s, sqrt(50))
    if key == "K5_Lm4":
        return Lfun(s, -4)
    if key == "K6_zeta_L5":
        return zeta(s) * Lfun(s, 5)
    if key == "K7_Lm4_L5":
        return Lfun(s, -4) * Lfun(s, 5)
    if key == "K8_epstein_D1":
        return zeta(s) * Lfun(s, -4)      # = (1/2) sum' (j^2+k^2)^{-s} / 2, a_1 = 1
    if key == "K9_DH":
        return DH(s)
    if key == "K10_Lm7_L28":
        return Lfun(s, -7) * Lfun(s, 28)
    if key == "K11_form_disc23":
        raise NotImplementedError("K11 is killed by Gate A (a_1 = 0) before any evaluation")
    if key == "K12_zeta_squared":
        return zeta(s) ** 2
    raise ValueError(key)


CARRIERS = {
    # key                : (label, has_pole, degree, offline_zeros, note)
    "K1_zeta":            ("zeta(s)", True, 1, "no", "cycle-19 anchor"),
    "K2_zeta_synth":      ("zeta(s)(1-2^{0.55-s})", True, 1, "yes (sigma=0.55)", "cycle-19 anchor"),
    "K3_epstein_D7":      ("Epstein Delta=1/7 (D=7)", True, 2, "yes (7 known, sigma in (1/2,1))", "cycle-19 anchor"),
    "K4_epstein_Dsqrt50": ("Epstein Delta=1/sqrt50", True, 2, "yes (fold pair real)", "cycle-19 anchor"),
    "K5_Lm4":             ("L(s,chi_{-4})", False, 1, "no", "NEW"),
    "K6_zeta_L5":         ("zeta(s)L(s,chi_5) = zeta_{Q(sqrt5)}", True, 2, "no", "NEW"),
    "K7_Lm4_L5":          ("L(s,chi_{-4})L(s,chi_5)", False, 2, "no", "NEW  * separator"),
    "K8_epstein_D1":      ("Epstein Delta=1 = zeta(s)L(s,chi_{-4})", True, 2, "no", "NEW"),
    "K9_DH":              ("Davenport-Heilbronn (1,k,-k,-1,0)", False, 1, "yes, incl. sigma>1", "NEW"),
    "K10_Lm7_L28":        ("L(s,chi_{-7})L(s,chi_{28}) = genus difference, disc -196", False, 2, "no", "NEW  * separator"),
    # K11/K12 are deliberate GATE POSITIVE CONTROLS: a gate that has never killed anything is in
    # the same position as a falsifier that cannot fire (cycle-19 D2).  They are expected kills.
    "K11_form_disc23":    ("Epstein zeta of the non-principal form (2,1,3), disc -23", False, 2, "unknown", "gate control, expect KILL by Gate A"),
    "K12_zeta_squared":   ("zeta(s)^2", True, 2, "no", "gate control, expect KILL by Gate P (double pole)"),
}


def residue_at_1(key):
    """Residue of the carrier at s=1 (0 if entire there).  Used only as a reported diagnostic."""
    from mpmath import pi
    if key == "K1_zeta":
        return mpf(1)
    if key == "K2_zeta_synth":
        return 1 - mpf(2) ** (mpf('-0.45'))
    if key == "K3_epstein_D7":
        return pi / 14
    if key == "K4_epstein_Dsqrt50":
        return pi / (2 * sqrt(50))
    if key == "K6_zeta_L5":
        return Lfun(mpf(1), 5)
    if key == "K8_epstein_D1":
        return Lfun(mpf(1), -4)
    return mp.zero
