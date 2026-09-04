"""machine 2 (beast-atlas) -- cycle 20 -- INSTRUMENT A: the carrier-axis distance runs.

Lineage: the Gram/normal-equation route is cycle 19's (machine2_cycle19_nb_distance.py), reused
DELIBERATELY for the four anchor carriers so that the anchors are a reproduction on the same
instrument and not a second, differently-broken instrument.  The cycle-20 headline rows are
re-measured by INSTRUMENT B (machine2_cycle20_nb_instrumentB.py), whose independence is in the
code path: full-line tan-substitution quadrature instead of half-line Gauss-Legendre panels with
cos-symmetry, design-matrix QR least squares instead of normal equations, constraint by
elimination instead of a Lagrange multiplier, and a third-party Epstein evaluator (machine 3's
letter133_zeta2_impl.py) instead of our own.

WHAT IS NEW HERE, and it is an identity rather than a model:

    d^2_con  =  d^2_free  +  (a . c_free)^2 / (a^T G^{-1} a),      a_k = 1/k,

the exact decomposition of the pole-constrained minimum into (i) the unconstrained approximation
error and (ii) the PRICE OF KILLING THE POLE.  Cycle 19 reported only d^2_con.  Term (ii) is
identically 0 for a carrier with no pole at s = 1, which is what makes the carrier axis a test.
"""
import json, sys, time
from multiprocessing import Pool
from mpmath import mp, mpf, mpc, pi, sqrt, log, cos, sin, matrix, lu_solve, mpmathify, nstr

sys.path.insert(0, '.')
from machine2_cycle20_carriers import CARRIERS, carrier_eval

DPS_EVAL = 25
DPS_SOLVE = 30
NLIST = [1, 2, 4, 8, 16, 32, 48]


# ------------------------------------------------------------------ weights
def wfun(t, W):
    t2 = t * t
    if W[0] == "W2":
        return 1 / ((mpf(1) / 4 + t2) * (mpf(9) / 4 + t2))
    if W[0] == "SL":                      # sliding weight, mass at t = +-T0, half-width eps
        T0, eps = mpf(W[1]), mpf(W[2])
        A = eps * eps + T0 * T0
        return 1 / ((A - t2) ** 2 + 4 * eps * eps * t2)
    raise ValueError(W)


def Wval(s, W):
    if W[0] == "W2":
        return 1 / (s * (s + 1))
    if W[0] == "SL":
        T0, eps = mpf(W[1]), mpf(W[2])
        return 1 / ((s - (mpf(1) / 2 - eps)) ** 2 + T0 * T0)
    raise ValueError(W)


def norm1_exact(W):
    """(1/2pi) Int_R |W(1/2+it)|^2 dt, closed form."""
    if W[0] == "W2":
        return mpf(1) / 3
    if W[0] == "SL":
        T0, eps = mpf(W[1]), mpf(W[2])
        return 1 / (4 * eps * (eps * eps + T0 * T0))
    raise ValueError(W)


def grid_for(W):
    """Gauss-Legendre panels on [0,T]; panel layout adapted to where |W|^2 lives."""
    import numpy as np
    x, w = np.polynomial.legendre.leggauss(12)
    ts, ws = [], []

    def panels(a, b, npan):
        h = (mpf(b) - mpf(a)) / npan
        for p in range(npan):
            a0 = mpf(a) + p * h
            for xi, wi in zip(x, w):
                ts.append(a0 + h * (mpf(float(xi)) + 1) / 2)
                ws.append(h * mpf(float(wi)) / 2)

    if W[0] == "W2":
        panels(0, 120, 120)                       # cycle-19 grid exactly: unit panels, 1440 nodes
    else:
        T0, eps = float(W[1]), float(W[2])
        Ttail = float(W[3])
        lo, hi = max(0.0, T0 - 20 * eps), T0 + 20 * eps
        if lo > 0:
            panels(0, lo, max(1, int(lo / 2)))    # coarse below the mass
        panels(lo, hi, 80)                        # dense across the mass
        if Ttail > hi:
            panels(hi, Ttail, max(1, int((Ttail - hi) / 5)))
    return ts, ws


# ------------------------------------------------------------------ carrier evaluation (parallel)
_KEY = None


def _init(key):
    global _KEY
    _KEY = key
    mp.dps = DPS_EVAL


def _ev(t):
    mp.dps = DPS_EVAL
    s = mpc(mpf(1) / 2, t)
    v = carrier_eval(_KEY, s)
    return (mp.nstr(mp.re(v), 22), mp.nstr(mp.im(v), 22))


def eval_grid(key, ts, procs=8):
    with Pool(procs, initializer=_init, initargs=(key,)) as pool:
        out = pool.map(_ev, ts, chunksize=4)
    return [mpc(mpf(a), mpf(b)) for a, b in out]


# ------------------------------------------------------------------ Gram + both solves
def gram(Fvals, ts, ws, W, Nmax):
    wt = [wfun(t, W) * w for t, w in zip(ts, ws)]
    absF2 = [abs(f) ** 2 for f in Fvals]
    logs = [log(mpf(k)) for k in range(1, Nmax + 1)]
    G = matrix(Nmax, Nmax)
    cache = {}
    for j in range(1, Nmax + 1):
        for k in range(j, Nmax + 1):
            L = logs[j - 1] - logs[k - 1]
            key = mp.nstr(L, 20)
            if key in cache:
                val = cache[key]
            else:
                acc = mp.zero
                for a, t, q in zip(absF2, ts, wt):
                    acc += a * cos(t * L) * q
                val = acc / pi
                cache[key] = val
            g = val / sqrt(mpf(j) * k)
            G[j - 1, k - 1] = g
            G[k - 1, j - 1] = g
    u = matrix(Nmax, 1)
    for k in range(1, Nmax + 1):
        Lk = logs[k - 1]
        acc = mp.zero
        for f, t, q in zip(Fvals, ts, wt):
            acc += (mp.re(f) * cos(t * Lk) + mp.im(f) * sin(t * Lk)) * q
        u[k - 1] = acc / pi / sqrt(mpf(k))
    # quadrature control: ||1||^2 by the same quadrature vs the closed form
    acc = mp.zero
    for t, q in zip(ts, wt):
        acc += q
    return G, u, acc / pi


def solve_at(G, u, N, n1, has_pole):
    Gs = matrix(N, N)
    for i in range(N):
        for j in range(N):
            Gs[i, j] = G[i, j]
    us = matrix(N, 1)
    for i in range(N):
        us[i] = u[i]
    c_free = lu_solve(Gs, us)
    lin = sum(us[i] * c_free[i] for i in range(N))
    d2_free = n1 - lin                                   # since G c = u  =>  c^T G c = u.c
    a = matrix(N, 1)
    for i in range(N):
        a[i] = mpf(1) / (i + 1)
    Ginv_a = lu_solve(Gs, a)
    aGa = sum(a[i] * Ginv_a[i] for i in range(N))
    ac = sum(a[i] * c_free[i] for i in range(N))
    penalty = ac * ac / aGa
    d2_con = d2_free + penalty
    # independent check of the same constrained value by the cycle-19 KKT route
    M = matrix(N + 1, N + 1)
    rhs = matrix(N + 1, 1)
    for i in range(N):
        for j in range(N):
            M[i, j] = Gs[i, j]
        M[i, N] = a[i]
        M[N, i] = a[i]
        rhs[i] = us[i]
    rhs[N] = mp.zero
    sol = lu_solve(M, rhs)
    c_kkt = matrix(N, 1)
    for i in range(N):
        c_kkt[i] = sol[i]
    quad = mp.zero
    for i in range(N):
        for j in range(N):
            quad += c_kkt[i] * Gs[i, j] * c_kkt[j]
    lin2 = sum(us[i] * c_kkt[i] for i in range(N))
    d2_kkt = n1 - 2 * lin2 + quad
    try:
        import numpy as np
        Gf = np.array([[float(Gs[i, j]) for j in range(N)] for i in range(N)], dtype=float)
        ev = np.linalg.eigvalsh(Gf)
        cond = float(abs(ev).max() / max(abs(ev).min(), 1e-300))
    except Exception:
        cond = float("nan")
    return {"d2_free": d2_free, "d2_con": d2_con if has_pole else d2_free,
            "penalty": penalty, "d2_kkt": d2_kkt, "cond": cond,
            "gprime1": -sum(c_free[i] * log(mpf(i + 1)) / (i + 1) for i in range(N))}


def run(keys, W, tag):
    mp.dps = DPS_SOLVE
    ts, ws = grid_for(W)
    out = {"meta": {"weight": list(W), "nodes": len(ts), "dps_eval": DPS_EVAL,
                    "dps_solve": DPS_SOLVE, "norm1_exact": nstr(norm1_exact(W), 20)}, "runs": []}
    for key in keys:
        t0 = time.time()
        Fv = eval_grid(key, ts)
        mp.dps = DPS_SOLVE
        G, u, n1_quad = gram(Fv, ts, ws, W, max(NLIST))
        n1 = norm1_exact(W)
        has_pole = CARRIERS[key][1]
        rel_quad_err = abs(n1_quad - n1) / n1
        for N in NLIST:
            r = solve_at(G, u, N, n1, has_pole)
            out["runs"].append({
                "carrier": key, "label": CARRIERS[key][0], "pole": has_pole,
                "degree": CARRIERS[key][2], "offline": CARRIERS[key][3], "N": N,
                "d2_con": nstr(r["d2_con"], 12), "d2_free": nstr(r["d2_free"], 12),
                "penalty": nstr(r["penalty"], 12),
                "rel_con": float(r["d2_con"] / n1), "rel_free": float(r["d2_free"] / n1),
                "penalty_share": float(r["penalty"] / r["d2_con"]) if has_pole else 0.0,
                "kkt_check_reldiff": float(abs(r["d2_kkt"] - r["d2_con"]) / abs(r["d2_con"])),
                "cond": r["cond"], "gprime1": nstr(r["gprime1"], 10),
                "quad_norm1_relerr": float(rel_quad_err)})
            print(f"{key:20s} N={N:3d} rel_con={float(r['d2_con']/n1):.6g} "
                  f"rel_free={float(r['d2_free']/n1):.6g} "
                  f"share={out['runs'][-1]['penalty_share']:.4f} cond={r['cond']:.3g}")
        print(f"  [{key} done in {time.time()-t0:.1f}s, quad ||1||^2 rel err {float(rel_quad_err):.3g}]")
        json.dump(out, open(f"machine2_cycle20_{tag}.json", "w"), indent=1)
    return out


if __name__ == "__main__":
    which = sys.argv[1]
    if which == "main":
        run(list(CARRIERS)[:10], ("W2",), "mainW2")
    elif which == "slide":
        T0, eps, Ttail = sys.argv[2], sys.argv[3], sys.argv[4]
        keys = sys.argv[5].split(",")
        run(keys, ("SL", T0, eps, Ttail), f"slide_{keys[0]}_T{T0}_e{eps}_T{Ttail}")
