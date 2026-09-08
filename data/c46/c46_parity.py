#!/usr/bin/env python3
"""c46_parity.py -- the ODD block of the Weil quadratic form on the window, and its KATs.

WHY THIS FILE EXISTS
--------------------
data/c42/c42_connes_x.py builds its basis from cosines only:
    phi_0 = 1/sqrt(L);  phi_k = sqrt(2/L) cos(w_k t),  w_k = 2 pi k / L,  k = 1..N
which is complete in the EVEN half of L^2(-L/2, L/2) and spans nothing else. The Weil form is
block-diagonal in the even/odd split (the cross terms give an ODD autocorrelation g, and the
functional kills odd g: g(0)=0, the prime side pairs g(log n)+g(-log n)=0, the archimedean
integrand is odd against an even weight, and h(i/2)+h(-i/2)=0). So

    lambda_window(x) = min( lambda_even(x), lambda_odd(x) )

and every lambda_min this lane has published is the first of the two. Connes lists the evenness
of the minimiser as a REMAINING STEP (sec 6.6) and as an ASSUMPTION (footnote 12). This file
computes the second.

THE ODD BLOCK
-------------
basis  : psi_k = sqrt(2/L) sin(w_k t), k = 1..N, on t in [-L/2, L/2]  (complete in the odd half,
         orthonormal, so g_{jk}(0) = delta_{jk} exactly as in the even block and every
         g(0)-proportional term of the assembly carries over unchanged).
g_{jk} : for 0 <= t <= L, with d = w_j - w_k, e = w_j + w_k, eps = (-1)^{j+k},
         Id = (L-t) if j==k else -eps sin(d t)/d          Ie = -eps sin(e t)/e
         Sd = 0     if j==k else  eps (1-cos(d t))/d      Se =  eps (1-cos(e t))/e
         g_{jk}(t) = nr_j nr_k [ cos(w_k t) (Id - Ie)/2 + sin(w_k t) (Sd + Se)/2 ]
         (the even block's is  nr_j nr_k [ cos(w_k t) (Id + Ie)/2 - sin(w_k t) (Se - Sd)/2 ];
         the sign pattern is the only difference, and it is KAT'd against direct quadrature.)

Everything else -- Gauss-Legendre nodes, pole weight, archimedean weights, the constant, the
prime-power sum -- is a line-for-line copy of c42's build_matrix, and KAT K1 proves it is one by
rebuilding the EVEN block here and differencing it entrywise against c42's own function.

STORAGE (added in c48, 2026-09-08)
----------------------------------
This file used to write `lambda_min = mp.nstr(lam, 60)` out of a dps=150 run, discarding ~90 digits
AT WRITE TIME. c47's published letter (commit c6f6315) named that as a defect of ours and promised
the repair at the storage layer. run_cell and run_block now route every stored number through
data/code/m2_c48_cell_storage.py, which KEEPS the historical narrow prints byte-identical (they are
the same mp.nstr calls) and ADDS the full working-precision value beside each. The frozen c46 JSON
cells in this directory are left exactly as published; the regenerated full-precision ladder lives in
data/c48/, and data/code/m2_c48_nonmovement_check.py byte-compares the two.

usage:
  c46_parity.py kat                                  run K1..K3 (K4 is the expensive one)
  c46_parity.py run PARITY X N DPS GLDEG ITERS       one cell, emits JSON next to itself
  c46_parity.py block PARITY X N DPS GLDEG ITERS K   K smallest Ritz values (simplicity arm)
"""
import sys, os, json, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "c42"))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "code"))
from mpmath import mp, mpf, exp, log, pi, sqrt, euler, cos, sin, cosh
from mpmath.calculus.quadrature import GaussLegendre
import c42_connes_x as c42
import m2_c48_cell_storage as S       # c48: the storage layer; see the STORAGE note in the docstring


# ---------------------------------------------------------------- basis
def make_basis_parity(N, L, parity):
    """even: j = 0..N with w_j = 2 pi j / L (j=0 is the constant).  odd: j = 1..N."""
    if parity == "even":
        om = [2 * pi * j / L for j in range(N + 1)]
        nr = [1 / sqrt(L)] + [sqrt(2 / L) for _ in range(N)]
        idx = list(range(N + 1))
    elif parity == "odd":
        om = [2 * pi * j / L for j in range(1, N + 1)]
        nr = [sqrt(2 / L) for _ in range(N)]
        idx = list(range(1, N + 1))
    else:
        raise ValueError("parity must be even or odd")
    return om, nr, idx


def g_matrix_at_parity(t, L, om, nr, idx, parity):
    """full symmetric matrix [g_{jk}(t)], 0 <= t <= L, in the given parity sector."""
    n = len(om)
    cw = [cos(om[a] * t) for a in range(n)]
    sw = [sin(om[a] * t) for a in range(n)]
    Lt = L - t
    G = [[None] * n for _ in range(n)]
    for a in range(n):
        cj, sj = cw[a], sw[a]
        ja = idx[a]
        for b in range(a + 1):
            ck, sk = cw[b], sw[b]
            jb = idx[b]
            eps = mpf(1) if (ja + jb) % 2 == 0 else mpf(-1)
            sd = sj * ck - cj * sk
            se = sj * ck + cj * sk
            cd = cj * ck + sj * sk
            ce = cj * ck - sj * sk
            d = om[a] - om[b]
            e = om[a] + om[b]
            if ja == jb:
                Id, Sd = Lt, mpf(0)
            else:
                Id, Sd = -eps * sd / d, eps * (1 - cd) / d
            if ja == 0 and jb == 0:
                Ie, Se = Lt, mpf(0)
            else:
                Ie, Se = -eps * se / e, eps * (1 - ce) / e
            if parity == "even":
                v = nr[a] * nr[b] * (ck * ((Id + Ie) / 2) - sk * ((Se - Sd) / 2))
            else:
                v = nr[a] * nr[b] * (ck * ((Id - Ie) / 2) + sk * ((Sd + Se) / 2))
            G[a][b] = v
            G[b][a] = v
    return G


# ---------------------------------------------------------------- the matrix of the form
def build_matrix_parity(N, x, gl_degree, parity, verbose=False):
    """line-for-line the assembly of c42.build_matrix, with the parity-dependent g swapped in.
    KAT K1 differences the parity='even' output against c42.build_matrix entrywise."""
    L = log(mpf(x))
    om, nr, idx = make_basis_parity(N, L, parity)
    n = len(om)
    M = [[mpf(0)] * n for _ in range(n)]

    gl = GaussLegendre(mp)
    nodes = gl.get_nodes(mpf(0), L, gl_degree, mp.prec)

    for (t, w) in nodes:
        G = g_matrix_at_parity(t, L, om, nr, idx, parity)
        wp = w * 4 * cosh(t / 2)
        den = 1 - exp(-2 * t)
        wa = w * 2 * (-exp(-t / 2)) / den
        wdiag = w * 2 * exp(-2 * t) / den
        wc = wp + wa
        for a in range(n):
            Ma, Ga = M[a], G[a]
            for b in range(a):
                Ma[b] += wc * Ga[b]
            Ma[a] += wc * Ga[a] + wdiag

    cst = -(log(pi) + euler) + 2 * (-log(1 - exp(-2 * L)) / 2)
    for a in range(n):
        M[a][a] += cst

    pps = c42.prime_powers_upto(x)
    for (nn, lam) in pps:
        t = log(mpf(nn))
        G = g_matrix_at_parity(t, L, om, nr, idx, parity)
        c = -2 * lam / sqrt(mpf(nn))
        for a in range(n):
            Ma, Ga = M[a], G[a]
            for b in range(a + 1):
                Ma[b] += c * Ga[b]

    for a in range(n):
        for b in range(a + 1, n):
            M[a][b] = M[b][a]
    return M, L, [p for p, _ in pps]


# ---------------------------------------------------------------- K smallest Ritz values
def smallest_block(M, k=3, iters=16, verbose=False):
    """block inverse iteration + Rayleigh-Ritz. Returns [(lam_i, residual_i)] ascending.
    The residual is printed beside every value because a Ritz value cannot report its own
    non-convergence, and the iteration count is a knob that does not announce itself."""
    n = len(M)
    A = mp.matrix(M)
    V = mp.matrix(n, k)
    for i in range(n):                       # deterministic, non-degenerate starting block
        for j in range(k):
            V[i, j] = mpf(1) / (1 + ((i * (j + 3) + j) % 7)) + mpf(j + 1) / (n + i + 1)
    def orth(V):
        for j in range(k):
            for i in range(j):
                c = sum(V[r, i] * V[r, j] for r in range(n))
                for r in range(n):
                    V[r, j] -= c * V[r, i]
            nr_ = sqrt(sum(V[r, j] ** 2 for r in range(n)))
            for r in range(n):
                V[r, j] /= nr_
        return V
    V = orth(V)
    lams = None
    for it in range(iters):
        W = mp.matrix(n, k)
        for j in range(k):
            col = mp.lu_solve(A, mp.matrix([V[r, j] for r in range(n)]))
            for r in range(n):
                W[r, j] = col[r]
        V = orth(W)
        B = mp.matrix(k, k)
        AV = A * V
        for i in range(k):
            for j in range(k):
                B[i, j] = sum(V[r, i] * AV[r, j] for r in range(n))
        for i in range(k):
            for j in range(i):
                B[i, j] = B[j, i] = (B[i, j] + B[j, i]) / 2
        E, Q = mp.eigsy(B)
        V = V * Q
        lams = [E[i] for i in range(k)]
        if verbose:
            print("   block-iter %d: %s" % (it, [mp.nstr(l, 8) for l in lams]), flush=True)
    AV = A * V
    out = []
    for j in range(k):
        res = sqrt(sum((AV[r, j] - lams[j] * V[r, j]) ** 2 for r in range(n)))
        out.append((lams[j], res))
    return out


# ---------------------------------------------------------------- KATs
def kat(verbose=True):
    fails = []
    # ---- K1: rebuilt EVEN assembly == c42.build_matrix, entrywise, exactly
    mp.dps = 60
    A, LA, _, _, ppA = c42.build_matrix(12, 13, 9, verbose=False)
    B, LB, ppB = build_matrix_parity(12, 13, 9, "even")
    worst = mpf(0)
    for i in range(len(A)):
        for j in range(len(A)):
            dd = abs(A[i][j] - B[i][j])
            if dd > worst:
                worst = dd
    ok1 = (worst == 0) and (ppA == ppB)
    print("K1 even assembly identical to c42.build_matrix : max|diff| = %s , primes %s  -> %s"
          % (mp.nstr(worst, 5), "same" if ppA == ppB else "DIFFER", "PASS" if ok1 else "FAIL"))
    if not ok1:
        fails.append("K1")

    # ---- K2: odd closed form vs direct quadrature of its own defining integral
    mp.dps = 40
    N, x, = 6, 13
    L = log(mpf(x))
    om, nr, idx = make_basis_parity(N, L, "odd")
    def psi(a, s):
        return nr[a] * sin(om[a] * s) if -L / 2 <= s <= L / 2 else mpf(0)
    worst2 = mpf(0)
    cases = [(0, 0, mpf(0)), (0, 0, L / 3), (2, 2, L / 5), (0, 1, L / 4), (1, 2, L / 7),
             (0, 3, mpf(9) * L / 10), (4, 1, L / 2), (5, 0, mpf(0))]
    for (a, b, t) in cases:
        G = g_matrix_at_parity(t, L, om, nr, idx, "odd")
        num = mp.quad(lambda s: psi(a, s) * psi(b, s + t), [-L / 2, L / 2 - t])
        den = max(abs(num), mpf(1))
        rel = abs(G[a][b] - num) / den
        if rel > worst2:
            worst2 = rel
        # symmetry of the closed form itself
        if abs(G[a][b] - G[b][a]) != 0:
            fails.append("K2-sym")
    ok2 = worst2 < mpf(10) ** (-25)
    print("K2 odd closed form vs quadrature, 8 cases     : max rel err = %s  -> %s"
          % (mp.nstr(worst2, 5), "PASS" if ok2 else "FAIL"))
    if not ok2:
        fails.append("K2")

    # ---- K3: orthonormality at t=0 and support end at t=L
    mp.dps = 60
    L = log(mpf(13))
    om, nr, idx = make_basis_parity(8, L, "odd")
    G0 = g_matrix_at_parity(mpf(0), L, om, nr, idx, "odd")
    GL = g_matrix_at_parity(L, L, om, nr, idx, "odd")
    w0 = max(abs(G0[i][j] - (1 if i == j else 0)) for i in range(len(om)) for j in range(len(om)))
    wL = max(abs(GL[i][j]) for i in range(len(om)) for j in range(len(om)))
    ok3 = (w0 < mpf(10) ** (-40)) and (wL < mpf(10) ** (-40))
    print("K3 odd g(0)=I and g(L)=0                      : %s / %s  -> %s"
          % (mp.nstr(w0, 5), mp.nstr(wL, 5), "PASS" if ok3 else "FAIL"))
    if not ok3:
        fails.append("K3")

    print("KAT RESULT: %d of 3 pass%s" % (3 - len(set(fails)), "" if not fails else "  FAILED: " + ",".join(sorted(set(fails)))))
    return 0 if not fails else 1


# ---------------------------------------------------------------- drivers
def _ritz_cell(l, r):
    """c48 STORAGE FIX: same narrow prints as before, plus the full working-precision value."""
    d = {}
    d.update(S.store_number(l, "lam", (("", 40),)))
    d.update(S.store_number(mp.log(abs(l), 10), "log10", (("", 20),)))
    d.update(S.store_number(r, "residual", (("", 10),)))
    return d


def run_cell(parity, X, N, DPS, GLDEG, ITERS):
    mp.dps = DPS                       # dps FIRST, before any mpmath value is created
    t0 = time.time()
    M, L, pps = build_matrix_parity(N, X, GLDEG, parity)
    t_build = time.time() - t0
    lam, v = c42.smallest_eigenpair(M, iters=ITERS, verbose=False)
    A = mp.matrix(M)
    Av = A * v
    res = sqrt(sum((Av[i] - lam * v[i]) ** 2 for i in range(len(M))))
    out = dict(parity=parity, x=X, N=N, dim=len(M), dps=DPS, gl_degree=GLDEG, iters=ITERS,
               prime_powers=pps)
    # c48 STORAGE FIX. The four narrow prints below are the SAME CALLS this file has always made --
    # mp.nstr(L,40) / mp.nstr(lam,60) / mp.nstr(lam,30) / mp.nstr(res,10) / mp.nstr(log10,20) -- so no
    # string this lane has published can move; store_number adds the full working-precision value
    # beside each one instead of discarding it at write time.
    out.update(S.store_number(L, "L", (("", 40),)))
    out.update(S.store_number(lam, "lambda_min", (("", 60), ("_30", 30))))
    out.update(S.store_number(res, "residual", (("", 10),)))
    out.update(S.store_number(mp.log(lam, 10), "log10", (("", 20),)))
    out["seconds_build"] = t_build
    out["seconds_total"] = time.time() - t0
    fn = os.path.join(HERE, "c46_%s_x%s_N%d_dps%d_g%d_it%d.json"
                      % (parity, str(X).replace(".", "p"), N, DPS, GLDEG, ITERS))
    json.dump(out, open(fn, "w"), indent=1)
    print("%s x=%s N=%d dps=%d g=%d it=%d dim=%d  lambda=%s  log10=%s  res=%s  %.1fs"
          % (parity, X, N, DPS, GLDEG, ITERS, len(M), out["lambda_min_30"], out["log10"],
             out["residual"], out["seconds_total"]), flush=True)


def run_block(parity, X, N, DPS, GLDEG, ITERS, K):
    mp.dps = DPS
    t0 = time.time()
    M, L, pps = build_matrix_parity(N, X, GLDEG, parity)
    t_build = time.time() - t0
    pairs = smallest_block(M, k=K, iters=ITERS, verbose=True)
    out = dict(parity=parity, x=X, N=N, dim=len(M), dps=DPS, gl_degree=GLDEG, iters=ITERS, k=K,
               L=mp.nstr(L, 40),
               ritz=[_ritz_cell(l, r) for (l, r) in pairs],
               seconds_build=t_build, seconds_total=time.time() - t0)
    fn = os.path.join(HERE, "c46_block_%s_x%s_N%d_dps%d_g%d_it%d_k%d.json"
                      % (parity, str(X).replace(".", "p"), N, DPS, GLDEG, ITERS, K))
    json.dump(out, open(fn, "w"), indent=1)
    for i, r in enumerate(out["ritz"]):
        print("  ritz[%d] lam=%s  log10=%s  res=%s" % (i, r["lam"], r["log10"], r["residual"]), flush=True)
    print("block %s x=%s N=%d k=%d  %.1fs" % (parity, X, N, K, out["seconds_total"]), flush=True)


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "kat":
        sys.exit(kat())
    elif cmd == "run":
        p = sys.argv[2]
        X = float(sys.argv[3]) if "." in sys.argv[3] else int(sys.argv[3])
        run_cell(p, X, *[int(a) for a in sys.argv[4:8]])
    elif cmd == "block":
        p = sys.argv[2]
        X = float(sys.argv[3]) if "." in sys.argv[3] else int(sys.argv[3])
        run_block(p, X, *[int(a) for a in sys.argv[4:9]])
    else:
        raise SystemExit(__doc__)
