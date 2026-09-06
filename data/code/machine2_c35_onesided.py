"""machine2 CYCLE 35 -- P2'': the parity/sign test on DISJOINT evaluator samples.

The first attempt (`machine2_c35_signgroup.py`, dsign=-1) was DEGENERATE: reflecting a
symmetric stencil maps the node set onto itself, so both arms read the SAME xi values and the
sign map is an identity of the finite-difference weights.  Its firing world was empty.

Here the two arms share exactly ONE node (p=0):
    FORWARD  stencil, nodes p = 0..+14   ->  e = +p*h_e  (D <= centre)
    BACKWARD stencil, nodes p = -14..0   ->  e = -p*h_e  (D >= centre)
Both estimate the SAME g[m][n] = (1/n!) d^n/de^n at e=0, so the prediction is
`a_n(bwd) = a_n(fwd)` with NO sign flip (ERRATUM 1: the first filing of P2' had this
backwards, caught by re-derivation before the run, not by the data).

An odd-order sign defect in the Vandermonde weights, in the h_e^n division or in the series
solve fires here as an odd-n sign disagreement between two disjoint data sets.

Machinery IMPORTED from the frozen `machine2_c34_refit.py`; the only new code is a general
(non-symmetric) Vandermonde weight routine, built exactly as c34's `fd_weights` but taking an
arbitrary node list.
"""
import json
import os
import sys
import time
from multiprocessing import Pool

import mpmath as mp

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import machine2_c34_refit as C34  # noqa: E402

MMAX, NMAX, NAMES = C34.MMAX, C34.NMAX, C34.NAMES
CFG = dict(C34.BASE)
CFG["centre"] = C34.DSTAR_REFINED
HALFW = 14                                  # nodes -14..14, 29 evaluations
_C = {}


def _init(c):
    _C.update(c)
    mp.mp.dps = c["dps"] + 15


def _node(p):
    dps, guard = _C["dps"], _C["guard"]
    r = mp.mpf(_C["r_w"])
    N = _C["N_w"]
    he = mp.mpf(10) ** (-_C["he"])
    mp.mp.dps = dps + 15
    D = mp.mpf(_C["centre"]) - p * he
    Z = C34.Zeta2(D, dps=dps, guard=guard)
    half = mp.mpf(1) / 2
    quarter = N // 4
    base = [Z.xi(half + r * mp.expjpi(mp.mpf(2 * j) / N)) for j in range(quarter + 1)]

    def hval(j):
        j %= N
        if j >= N // 2:
            j -= N // 2
        if j <= quarter:
            return base[j]
        return mp.conj(base[N // 2 - j])

    vals = [hval(j) for j in range(N)]
    out = []
    for k in range(2 * MMAX + 2):
        s = mp.mpc(0)
        for j in range(N):
            s += vals[j] * mp.expjpi(mp.mpf(-2 * k * j) / N)
        out.append((s / N) / r ** k)
    return p, [mp.nstr(v, dps + 5, strip_zeros=False) for v in out]


def weights(nodes, n):
    """c34's fd_weights construction, generalised to an arbitrary node list."""
    npts = len(nodes)
    A = mp.matrix(npts, npts)
    for i, p in enumerate(nodes):
        for j in range(npts):
            A[i, j] = mp.mpf(p) ** j
    rhs = mp.matrix(npts, 1)
    rhs[n] = mp.factorial(n)
    return mp.lu_solve(A.T, rhs)


def gtable(res, nodes, cfg):
    he = mp.mpf(10) ** (-cfg["he"])
    g = [[None] * (NMAX + 1) for _ in range(MMAX + 1)]
    for m in range(MMAX + 1):
        for n in range(NMAX + 1):
            w = weights(nodes, n)
            s = mp.mpc(0)
            for i, p in enumerate(nodes):
                s += w[i] * res[p][2 * m]
            g[m][n] = mp.re((s / he ** n) / mp.factorial(n))
    return g


def coeffs(g):
    et = C34.solve_etilde(g)
    return C34.series_solve(g, 5), C34.series_solve(C34.shift_e(g, et), 5), et


if __name__ == "__main__":
    mp.mp.dps = CFG["dps"] + 15
    ps = list(range(-HALFW, HALFW + 1))
    t0 = time.time()
    res = {}
    with Pool(8, initializer=_init, initargs=(CFG,)) as pool:
        for p, strs in pool.imap_unordered(_node, ps):
            res[p] = [mp.mpmathify(s) for s in strs]
    print(f"29 nodes in {time.time()-t0:.0f}s", flush=True)

    NPTS = 15
    arms = {
        "SYM": list(range(-(NPTS // 2), NPTS // 2 + 1)),   # c34's stencil, control
        "FWD": list(range(0, NPTS)),                        # e >= 0
        "BWD": list(range(-(NPTS - 1), 1)),                 # e <= 0
    }
    out = {}
    mp.mp.dps = 90
    for name, nodes in arms.items():
        g = gtable(res, nodes, CFG)
        raw, rec, et = coeffs(g)
        out[name] = dict(nodes=[int(p) for p in nodes],
                         g10=mp.nstr(g[1][0], 50), g01=mp.nstr(g[0][1], 50),
                         g00=mp.nstr(g[0][0], 25), et=mp.nstr(et, 30),
                         raw={nm: mp.nstr(raw[i + 1], 70) for i, nm in enumerate(NAMES)},
                         rec={nm: mp.nstr(rec[i + 1], 70) for i, nm in enumerate(NAMES)})
        print(f"\n### {name}  nodes {nodes[0]}..{nodes[-1]}")
        print(f"   g[0][0]={out[name]['g00']}  etilde={out[name]['et']}")
        for nm in NAMES:
            print(f"   {nm:>3s} rec = {out[name]['rec'][nm]}")

    print("\n=== P2'': FWD vs BWD (share only p=0), predicted EQUAL, no sign flip ===")
    print(f"    shared nodes: {sorted(set(arms['FWD']) & set(arms['BWD']))}")
    for nm in NAMES:
        f_ = mp.mpf(out["FWD"]["rec"][nm])
        b_ = mp.mpf(out["BWD"]["rec"][nm])
        rel = abs(b_ - f_) / abs(f_)
        sf = mp.inf if rel == 0 else -mp.log10(rel)
        print(f"   {nm:>3s}: fwd={mp.nstr(f_,25)}  bwd={mp.nstr(b_,25)}  "
              f"same_sign={mp.sign(f_)==mp.sign(b_)}  agree={mp.nstr(sf,4)} s.f.")

    print("\n=== one-sided vs central: the FD-in-D channel this arm newly probes ===")
    for nm in NAMES:
        s_ = mp.mpf(out["SYM"]["rec"][nm])
        for arm in ("FWD", "BWD"):
            v = mp.mpf(out[arm]["rec"][nm])
            rel = abs(v - s_) / abs(s_)
            sf = mp.inf if rel == 0 else -mp.log10(rel)
            print(f"   {nm:>3s} {arm} vs SYM: rel={mp.nstr(rel,6)}  ({mp.nstr(sf,4)} s.f.)")

    with open(os.path.join(HERE, "../machine2_c35_onesided.json"), "w") as f:
        json.dump(out, f, indent=1)
