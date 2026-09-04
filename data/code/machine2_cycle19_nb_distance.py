"""machine 2 (beast-atlas) -- cycle 19 BOLD RUNG.

A WEIGHTED NYMAN-BEURLING DISTANCE, AND THE FIRST NUMBER EVER PUT NEXT TO OUR SECTION-4 FLOOR.

THE OBJECT.  For a Dirichlet series F with a_1 = 1, an analytic weight W, and Dirichlet polynomials
g(s) = sum_{k<=N} c_k k^{-s} constrained to kill F's pole at s = 1 (g(1) = 0 when F has a simple
pole there), define

    d_N(F,W)^2  =  min_c  (1/2pi) Int_R | 1 - F(1/2+it) g(1/2+it) |^2 |W(1/2+it)|^2 dt .

W = 1/s and target chi_(0,1) is the classical Nyman-Beurling / Baez-Duarte setting.

THE FLOOR (re-derived here, not quoted).  R := (1 - F g) W is analytic on Pi_{1/2} = {Re s > 1/2}
once the pole is killed, and d_N = ||R||_{H^2(Pi_{1/2})}.  The reproducing kernel of H^2(Pi_{1/2})
is k_{s0}(s) = 1/(s + conj(s0) - 1) with ||k_{s0}||^2 = 1/(2 sigma0 - 1).  If F(s0) = 0 with
sigma0 > 1/2 then R(s0) = W(s0), hence

    d_N^2  >=  (2 sigma0 - 1) |W(s0)|^2      for every N.                    (FLOOR)

WHY THE CLASSICAL WEIGHT W = 1/s IS NOT USABLE HERE, MEASURED NOT ASSUMED.  For the Epstein
carriers |F(1/2+it)|^2 grows, so |F|^2/|s|^2 ~ t^{-3/2} and the tail beyond T falls off only like
T^{-1/2}: at T = 80 the discarded tail is still ~5% of the total.  This is the DFMR mean-square
condition (2.6) biting numerically.  Two faster-decaying weights are therefore used, each with its
own exactly-computable floor:

    W2(s) = 1/(s(s+1))          integrand ~ t^{-7/2}
    W3(s) = 1/(s(s+1)(s+2))     integrand ~ t^{-11/2}

CONTROLS (every numerical claim names its evaluator AND its control):
  C1 SYNTHETIC, floor known in closed form: F_delta(s) = 1 - 2^{1/2+delta-s}, zeros exactly at
     s = 1/2+delta+2*pi*i*n/log 2.  No pole, no constraint.  Calibrates how TIGHT (FLOOR) is.
  C2 ZETA: floor 0 (no known off-line zero); d_N must descend, slowly.
  C3 QUADRATURE: ||1||^2 = (1/2pi) Int |W|^2 dt computed by the same quadrature and compared with
     the exact residue value.
  C4 TWO-GRID / TWO-PRECISION stability on every reported d_N.
  C5 CONDITION NUMBER of the Gram matrix reported beside every d_N (an ill-conditioned solve that
     dips below the floor is an instrument failure, not a falsification -- the diagnostic must be
     printed beside the number, cycle-15 trap #86).
"""
import os, sys, json, math, time
from multiprocessing import Pool
from mpmath import mp, mpf, mpc, pi, sqrt, log, exp, cos, sin, matrix, lu_solve, zeta, mpmathify

DPS = 25


# ----------------------------------------------------------------------------- weights
def wfun(t, kind):
    """|W(1/2+it)|^2 as an mpf."""
    t2 = t * t
    if kind == "W1":
        return 1 / (mpf(1) / 4 + t2)
    if kind == "W2":
        return 1 / ((mpf(1) / 4 + t2) * (mpf(9) / 4 + t2))
    if kind == "W3":
        return 1 / ((mpf(1) / 4 + t2) * (mpf(9) / 4 + t2) * (mpf(25) / 4 + t2))
    raise ValueError(kind)


def Wval(s, kind):
    """W(s) itself (complex)."""
    if kind == "W1":
        return 1 / s
    if kind == "W2":
        return 1 / (s * (s + 1))
    if kind == "W3":
        return 1 / (s * (s + 1) * (s + 2))
    raise ValueError(kind)


def norm1_exact(kind):
    """(1/2pi) Int_R |W|^2 dt in closed form (residues, partial fractions in t^2)."""
    if kind == "W1":
        return mpf(1)
    if kind == "W2":
        return mpf(1) / 3
    if kind == "W3":
        return mpf(1) / 20
    raise ValueError(kind)


def floor_value(s0, kind):
    return (2 * mp.re(s0) - 1) * abs(Wval(s0, kind)) ** 2


# ----------------------------------------------------------------------------- quadrature grid
def gl_panels(T, npan_per_unit=1, nodes=12):
    """Gauss-Legendre nodes/weights on [0,T], panels of width 1/npan_per_unit."""
    from mpmath import polyroots, legendre, diff
    import numpy as np
    x, w = np.polynomial.legendre.leggauss(nodes)
    ts, ws = [], []
    npan = int(T * npan_per_unit)
    h = mpf(1) / npan_per_unit
    for p in range(npan):
        a = p * h
        for xi, wi in zip(x, w):
            ts.append(a + h * (mpf(float(xi)) + 1) / 2)
            ws.append(h * mpf(float(wi)) / 2)
    return ts, ws


# ----------------------------------------------------------------------------- carriers
_CARRIER = None


def _init(carrier):
    global _CARRIER
    _CARRIER = carrier
    mp.dps = DPS


def _evalF(t):
    mp.dps = DPS
    s = mpc(mpf(1) / 2, t)
    kind, param = _CARRIER
    if kind == "epstein":
        from eval_epstein import F as EF
        v = EF(s, mpmathify(param))
    elif kind == "zeta":
        v = zeta(s)
    elif kind == "zeta_times_synth":
        d = mpmathify(param)
        v = zeta(s) * (1 - mpf(2) ** (mpf(1) / 2 + d - s))
    elif kind == "synth":
        d = mpmathify(param)
        v = 1 - mpf(2) ** (mpf(1) / 2 + d - s)
    elif kind == "synthsig":
        sz = mpmathify(param)
        v = 1 - mpf(2) ** (sz - s)
    else:
        raise ValueError(kind)
    return (mp.nstr(mp.re(v), 22), mp.nstr(mp.im(v), 22))


def eval_grid(carrier, ts, procs=8):
    with Pool(procs, initializer=_init, initargs=(carrier,)) as pool:
        out = pool.map(_evalF, ts, chunksize=4)
    return [mpc(mpf(a), mpf(b)) for a, b in out]


# ----------------------------------------------------------------------------- the solve
def dN(Fvals, ts, ws, kind, N, has_pole):
    """Return (d_N^2, cond, c) for the family {k^{-s}}_{k=1..N}."""
    wt = [wfun(t, kind) * w for t, w in zip(ts, ws)]
    absF2 = [abs(f) ** 2 for f in Fvals]
    logs = [log(mpf(k)) for k in range(1, N + 1)]

    # G_{jk} = (jk)^{-1/2} (1/pi) Int_0^inf |F|^2 cos(t log(j/k)) w dt
    G = matrix(N, N)
    cache = {}
    for j in range(1, N + 1):
        for k in range(j, N + 1):
            L = logs[j - 1] - logs[k - 1]
            key = mp.nstr(L, 20)
            if key in cache:
                val = cache[key]
            else:
                acc = mp.zero
                for a, t, wq in zip(absF2, ts, wt):
                    acc += a * cos(t * L) * wq
                val = acc / pi
                cache[key] = val
            g = val / sqrt(mpf(j) * k)
            G[j - 1, k - 1] = g
            G[k - 1, j - 1] = g

    # u_k = <F k^{-s}, 1> = k^{-1/2} (1/pi) Re Int_0^inf F(1/2+it) k^{-it} w dt
    u = matrix(N, 1)
    for k in range(1, N + 1):
        Lk = logs[k - 1]
        acc = mp.zero
        for f, t, wq in zip(Fvals, ts, wt):
            acc += (mp.re(f) * cos(t * Lk) + mp.im(f) * sin(t * Lk)) * wq
        u[k - 1] = acc / pi / sqrt(mpf(k))

    n1 = norm1_exact(kind)

    if has_pole:
        # constraint a^T c = 0 with a_k = 1/k  (g(1) = 0 kills the simple pole of F at s=1)
        M = matrix(N + 1, N + 1)
        rhs = matrix(N + 1, 1)
        for i in range(N):
            for j in range(N):
                M[i, j] = G[i, j]
            M[i, N] = mpf(1) / (i + 1)
            M[N, i] = mpf(1) / (i + 1)
            rhs[i] = u[i]
        rhs[N] = mp.zero
        sol = lu_solve(M, rhs)
        c = matrix(N, 1)
        for i in range(N):
            c[i] = sol[i]
    else:
        c = lu_solve(G, u)

    # d^2 = ||1||^2 - 2 u.c + c^T G c
    quad = mp.zero
    for i in range(N):
        for j in range(N):
            quad += c[i] * G[i, j] * c[j]
    lin = mp.zero
    for i in range(N):
        lin += u[i] * c[i]
    d2 = n1 - 2 * lin + quad

    # condition number (2-norm) of G via mpmath eigenvalues of the symmetric matrix
    try:
        import numpy as np
        Gf = np.array([[float(G[i, j]) for j in range(N)] for i in range(N)], dtype=float)
        ev = np.linalg.eigvalsh(Gf)
        cond = float(abs(ev).max() / max(abs(ev).min(), 1e-300))
    except Exception:
        cond = float("nan")
    return d2, cond, c, G, u, n1


def _evalF_extra(t):
    """extra carriers used by the cycle-19 mechanism test (kept beside _evalF deliberately)."""
    mp.dps = DPS
    s = mpc(mpf(1) / 2, t)
    kind, param = _CARRIER
    if kind == "zeta_times_synth":
        d = mpmathify(param)
        return zeta(s) * (1 - mpf(2) ** (mpf(1) / 2 + d - s))
    raise ValueError(kind)
