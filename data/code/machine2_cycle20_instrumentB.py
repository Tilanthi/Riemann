"""machine 2 (beast-atlas) -- cycle 20 -- INSTRUMENT B.

Independence is in the CODE PATH, not in a second call to the same function:

  (1) QUADRATURE     : Clenshaw-Curtis on [0,120]  (instrument A: 120 Gauss-Legendre unit panels).
  (2) FORMULATION    : weighted real design matrix / residual vector, minimise ||b - A c||_2
                       (instrument A: analytic reduction to a Gram matrix of cosine integrals and
                       the normal equations).
  (3) FACTORISATION  : Householder QR   (instrument A: LU on the normal equations / KKT system).
  (4) CONSTRAINT     : elimination of c_1 via c_1 = -sum_{k>=2} c_k/k
                       (instrument A: a Lagrange multiplier and a bordered system).
  (5) EVALUATOR      : Hurwitz zeta by our own Euler-Maclaurin (instrument A: mpmath's zeta), and
                       for the Epstein carrier machine 3's letter133_zeta2_impl.py, a third-party
                       theta/Poisson-quadrature implementation by a different author -- run at
                       dps = 40 + ceil(0.6822*t) because OUR OWN cycle-16 cancellation law says
                       that split destroys 0.6822*t digits.

Shared, and declared: mpmath's arbitrary-precision arithmetic and its Bernoulli-number table.
Ancestry note (cycle-16 refinement): both Epstein evaluators descend from the Jacobi theta
transformation.  That is a PROVEN IDENTITY, not an approximation, so the receipt that matters here
is implementation-independence, which is what (5) supplies; ancestry-independence is not available
for this object and is not claimed.
"""
import json, sys, time
from multiprocessing import Pool
from mpmath import mp, mpf, mpc, pi, sqrt, log, cos, sin, matrix, mpmathify, nstr, bernoulli

sys.path.insert(0, '.')

T_MAX = 120


# ---------------------------------------------------------------- own Euler-Maclaurin Hurwitz zeta
def hurwitz(s, a, M=80, K=12):
    """zeta(s,a) by Euler-Maclaurin, written out here; not mpmath's zeta()."""
    s = mpc(s)
    a = mpf(a)
    tot = mp.zero
    for n in range(M):
        tot += (n + a) ** (-s)
    Ma = M + a
    tot += Ma ** (1 - s) / (s - 1) + Ma ** (-s) / 2
    poch = s                      # (s)_{2k-1} with 2k-1 = 1 at k=1
    for k in range(1, K + 1):
        tot += bernoulli(2 * k) / mp.factorial(2 * k) * poch * Ma ** (-s - 2 * k + 1)
        poch *= (s + 2 * k - 1) * (s + 2 * k)
    return tot


def kronecker(a, n):
    from machine2_cycle20_carriers import kronecker as kr
    return kr(a, n)


def LfunB(s, D):
    q = abs(D)
    tot = mp.zero
    for aa in range(1, q + 1):
        c = kronecker(D, aa % q if aa % q else q)
        c = kronecker(D, aa)
        if c:
            tot += c * hurwitz(s, mpf(aa) / q)
    return tot * mpf(q) ** (-s)


def zetaB(s):
    return hurwitz(s, 1)


# ---------------------------------------------------------------- carriers, instrument-B routes
def evalB(key, s, dps):
    mp.dps = dps
    if key == "K1_zeta":
        return zetaB(s)
    if key == "K3_epstein_D7":
        try:
            import letter133_zeta2_impl as M3        # machine 3's file, in data/code/
        except ImportError:
            import m3_zeta2_impl as M3               # local copy of the same file
        need = 40 + int(0.6822 * abs(float(mp.im(s)))) + 10
        mp.dps = max(dps, need)
        v = M3.zeta2(s, 7)
        mp.dps = dps
        return +v
    if key == "K7_Lm4_L5":
        return LfunB(s, -4) * LfunB(s, 5)
    if key == "K10_Lm7_L28":
        return LfunB(s, -7) * LfunB(s, 28)
    if key == "K8_epstein_D1":
        return zetaB(s) * LfunB(s, -4)
    if key == "K9_DH":
        from mpmath import sqrt as sq
        k = (sq(10 - 2 * sq(5)) - 2) / (sq(5) - 1)
        a = [mpf(1), k, -k, mpf(-1), mp.zero]
        tot = mp.zero
        for j in range(1, 6):
            if a[j - 1] != 0:
                tot += a[j - 1] * hurwitz(s, mpf(j) / 5)
        return tot * mpf(5) ** (-s)
    raise ValueError(key)


_KEY = None
_DPS = 30


def _init(key, dps):
    global _KEY, _DPS
    _KEY, _DPS = key, dps


def _ev(t):
    mp.dps = _DPS
    v = evalB(_KEY, mpc(mpf(1) / 2, mpf(t)), _DPS)
    mp.dps = _DPS
    return (mp.nstr(mp.re(v), 22), mp.nstr(mp.im(v), 22))


# ---------------------------------------------------------------- Clenshaw-Curtis nodes on [0,T]
def cc_panel(M, A, B):
    """Clenshaw-Curtis on [A,B]: nodes x_j = cos(pi j/M), weights by the standard formula."""
    ts, ws = [], []
    for j in range(M + 1):
        th = pi * j / M
        x = mp.cos(th)
        w = mp.zero
        for k in range(0, M // 2 + 1):
            bk = 1 if (k == 0 or k == M // 2) else 2
            if 2 * k == 0:
                continue
            w += mpf(bk) / (1 - 4 * mpf(k) ** 2) * mp.cos(2 * k * th)
        cj = 1 if (j == 0 or j == M) else 2
        w = cj * (1 + w) / M
        ts.append(mpf(A) + (mpf(B) - mpf(A)) * (1 - x) / 2)
        ws.append((mpf(B) - mpf(A)) * w / 2)
    return ts, ws


def cc_nodes(M, intervals):
    ts, ws = [], []
    for (A, B) in intervals:
        a, b = cc_panel(M, A, B)
        ts += a
        ws += b
    return ts, ws


def wfunB(t, W):
    t2 = t * t
    if W[0] == "W2":
        return 1 / ((mpf(1) / 4 + t2) * (mpf(9) / 4 + t2))
    if W[0] == "SL":
        T0, eps = mpf(W[1]), mpf(W[2])
        A = eps * eps + T0 * T0
        return 1 / ((A - t2) ** 2 + 4 * eps * eps * t2)
    raise ValueError(W)


def norm1B(W):
    if W[0] == "W2":
        return mpf(1) / 3
    T0, eps = mpf(W[1]), mpf(W[2])
    return 1 / (4 * eps * (eps * eps + T0 * T0))


def householder_ls(A, b, m, n):
    """Least squares by Householder QR, written out here (instrument A uses mpmath's LU on the
    normal equations; mpmath's own qr_solve is deliberately NOT used either).  Returns ||r||^2."""
    Aw = [[A[i, j] for j in range(n)] for i in range(m)]
    bw = [b[i] for i in range(m)]
    for j in range(n):
        nrm = mp.sqrt(sum(Aw[i][j] ** 2 for i in range(j, m)))
        if nrm == 0:
            continue
        alpha = -nrm if Aw[j][j] >= 0 else nrm
        v = [mp.zero] * m
        v[j] = Aw[j][j] - alpha
        for i in range(j + 1, m):
            v[i] = Aw[i][j]
        vtv = sum(v[i] ** 2 for i in range(j, m))
        if vtv == 0:
            continue
        for k in range(j, n):
            vt = sum(v[i] * Aw[i][k] for i in range(j, m))
            f = 2 * vt / vtv
            for i in range(j, m):
                Aw[i][k] -= f * v[i]
        vt = sum(v[i] * bw[i] for i in range(j, m))
        f = 2 * vt / vtv
        for i in range(j, m):
            bw[i] -= f * v[i]
    return sum(bw[i] ** 2 for i in range(n, m))


def run_B(key, W, N, M, has_pole, dps=30, procs=8, Fcache=None, intervals=None):
    """Return d2_con by the design-matrix/QR/elimination route."""
    mp.dps = dps
    ts, ws = cc_nodes(M, intervals or [(0, T_MAX)])
    if Fcache is None:
        with Pool(procs, initializer=_init, initargs=(key, dps)) as pool:
            out = pool.map(_ev, [float(t) for t in ts], chunksize=1)
        Fv = [mpc(mpf(a), mpf(b)) for a, b in out]
    else:
        Fv = Fcache
    mp.dps = dps
    # objective:  (1/2pi) Int_R |1-Fg|^2 |W|^2 dt = (1/pi) Int_0^inf ... (real coefficients)
    # rows: for each node, sqrt(2*w_q*|W|^2/(2pi)) times (Re, Im) of (1 - F g)
    rows_re, rows_im, b_re, b_im = [], [], [], []
    for t, w, F in zip(ts, ws, Fv):
        al = sqrt(2 * w * wfunB(t, W) / (2 * pi))
        rr, ri = [], []
        for k in range(1, N + 1):
            kk = mpf(k) ** (-mpf(1) / 2)
            lg = t * log(mpf(k))
            z = F * kk * mpc(cos(lg), -sin(lg))
            rr.append(al * mp.re(z))
            ri.append(al * mp.im(z))
        rows_re.append(rr)
        rows_im.append(ri)
        b_re.append(al)
        b_im.append(mp.zero)
    nrow = 2 * len(ts)
    if has_pole:
        ncol = N - 1                      # c_1 eliminated: c_1 = -sum_{k>=2} c_k/k
        A = matrix(nrow, ncol)
        b = matrix(nrow, 1)
        for i, (rr, ri, br, bi) in enumerate(zip(rows_re, rows_im, b_re, b_im)):
            for k in range(2, N + 1):
                A[2 * i, k - 2] = rr[k - 1] - rr[0] / k
                A[2 * i + 1, k - 2] = ri[k - 1] - ri[0] / k
            b[2 * i] = br
            b[2 * i + 1] = bi
    else:
        ncol = N
        A = matrix(nrow, ncol)
        b = matrix(nrow, 1)
        for i, (rr, ri, br, bi) in enumerate(zip(rows_re, rows_im, b_re, b_im)):
            for k in range(1, N + 1):
                A[2 * i, k - 1] = rr[k - 1]
                A[2 * i + 1, k - 1] = ri[k - 1]
            b[2 * i] = br
            b[2 * i + 1] = bi
    d2 = householder_ls(A, b, nrow, ncol)
    return d2, Fv


if __name__ == "__main__":
    # argv: key  Wspec  Mlist  tag
    #   Wspec = "W2"  |  "SL:T0:eps:Ttail"
    key = sys.argv[1]
    wspec = sys.argv[2].split(":")
    if wspec[0] == "W2":
        W = ("W2",)
        intervals = [(0, 120)]
    else:
        T0, eps, Tt = float(wspec[1]), float(wspec[2]), float(wspec[3])
        W = ("SL", wspec[1], wspec[2], wspec[3])
        lo, hi = max(0.0, T0 - 20 * eps), T0 + 20 * eps
        intervals = ([(0, lo)] if lo > 0 else []) + [(lo, hi), (hi, Tt)]
    from machine2_cycle20_carriers import CARRIERS
    has_pole = CARRIERS[key][1]
    n1 = norm1B(W)
    out = []
    for M in [int(x) for x in sys.argv[3].split(",")]:
        Fc = None
        for N in [16, 32, 48]:
            t0 = time.time()
            d2, Fc = run_B(key, W, N, M, has_pole, Fcache=Fc, intervals=intervals)
            row = {"carrier": key, "weight": list(W), "M_per_panel": M,
                   "panels": [list(map(float, iv)) for iv in intervals], "N": N,
                   "d2": nstr(d2, 12), "rel": float(d2 / n1), "secs": round(time.time() - t0, 1)}
            print(row, flush=True)
            out.append(row)
        json.dump(out, open(f"machine2_cycle20_instrumentB_{sys.argv[4]}.json", "w"), indent=1)
