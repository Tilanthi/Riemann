"""machine2 CYCLE 33 -- the fold expansion pushed to a4 and a5 by the DERIVATIVE route.

EXPLOITATION, not a new method: this is c32's ladder-free instrument (`a` from two Taylor
coefficients of one analytic function at one point) carried two orders further.  No header
constant, no eps-ladder, no least squares, no K, no `a_used`.

  h(w,e) := xi_D(1/2 + w, D* - e)   is EVEN in w   =>   h = G(x,e),  x = w^2,  G(0,0)=0
  Solve G(x,e) = 0 as x(e) = A1 e + A2 e^2 + ... + A5 e^5.
  The zero of xi_D sits at s = 1/2 +- w, so u^2 := x  (SIGN FIXED BY MEASUREMENT, see
  m2_c33_validate.py -- c32's script docstring said u^2 = -x and printed a NEGATIVE `a`,
  which is a sign-convention defect in that script; the constants c32 PUBLISHED were the
  positive ones and are unaffected).

  G's coefficients g[m][n] = [x^m e^n] G come from
    * w : exact Cauchy coefficient extraction on |w| = r_w  (no cancellation)
    * e : a high-order central finite difference in D (one Zeta2 object per node)

THREE COST/ACCURACY FACTS USED HERE THAT c32 DID NOT USE
  1. h is EVEN in w and has REAL Taylor coefficients  =>  h(w_{j+N/2}) = h(w_j) and
     h(w_j) = conj(h(w_{N-j})).  Only j = 0 .. N/4 need evaluating: a 4x saving, which
     buys a much larger N_w at the same cost.
  2. xi_D(1/2+w) has simple poles only at w = +-1/2 (the -1/s + 1/(D(s-1)) terms), so the
     Taylor coefficients grow like 2^k and the trapezoid ALIASING error on c_k is ~ (2 r)^N.
     c32 ran (2r)^N = 1e-24 .. 1e-28 -- which is the size of the a3 refinement deltas it
     reported (1.4e-22, -2.2e-22).  ALIASING, not roundoff, was c32's accuracy floor.
  3. FD roundoff ~ eval_eps/h^n and truncation ~ (7h)^(npts-n) (7 ~ 1/radius in D), so
     h ~ 1e-7 is near-optimal for n<=5 at dps 90-110; c32's h=1e-12..1e-16 was far off it.

CERTIFICATE is stability under refinement of (dps, guard, r_w, N_w, npts, h_e), never a
single reading.  Free controls: (i) odd Taylor coefficients must vanish, (ii) imaginary
parts of every g[m][n] must vanish, (iii) G(0,0) = xi_D(1/2, D*) is the defining residual
of the D* literal.
"""
import json
import os
import sys
import time
from multiprocessing import Pool

import mpmath as mp

sys.path.insert(0, "/workspace/rh/cycle21")
from m2_zeta2_xi import Zeta2  # noqa: E402

DSTAR_STR = "0.141733239663887191395415685084185024"
MMAX = 5
NMAX = 5

_CFG = {}


def _init(cfg):
    _CFG.update(cfg)
    mp.mp.dps = cfg["dps"] + 15


def _node(p):
    """Even Taylor coefficients c_0..c_{2*MMAX} of h(w) = xi_D(1/2+w, D*-p*h_e) at w=0."""
    dps, guard = _CFG["dps"], _CFG["guard"]
    r = mp.mpf(_CFG["r_w"])
    N = _CFG["N_w"]
    he = mp.mpf(10) ** (-_CFG["he"])
    mp.mp.dps = dps + 15
    D = mp.mpf(DSTAR_STR) - p * he
    Z = Zeta2(D, dps=dps, guard=guard)
    half = mp.mpf(1) / 2
    quarter = N // 4
    base = [Z.xi(half + r * mp.expjpi(mp.mpf(2 * j) / N)) for j in range(quarter + 1)]

    def hval(j):
        j %= N
        if j >= N // 2:            # evenness: h(w + pi) = h(w)
            j -= N // 2
        if j <= quarter:
            return base[j]
        return mp.conj(base[N // 2 - j])   # reality: h(w_j) = conj(h(w_{N-j}))

    vals = [hval(j) for j in range(N)]
    out = []
    for k in range(2 * MMAX + 2):          # +2 so an ODD coefficient is a free control
        s = mp.mpc(0)
        for j in range(N):
            s += vals[j] * mp.expjpi(mp.mpf(-2 * k * j) / N)
        out.append((s / N) / r ** k)
    return p, [mp.nstr(v, dps + 5, strip_zeros=False) for v in out], mp.nstr(D, dps + 5)


def fd_weights(n, npts):
    m = npts // 2
    nodes = list(range(-m, m + 1))
    A = mp.matrix(npts, npts)
    for i, p in enumerate(nodes):
        for j in range(npts):
            A[i, j] = mp.mpf(p) ** j
    rhs = mp.matrix(npts, 1)
    rhs[n] = mp.factorial(n)
    return nodes, mp.lu_solve(A.T, rhs)


# ---------- truncated power-series helpers (in e, order K) ----------
def pmul(u, v, K):
    out = [mp.mpf(0)] * (K + 1)
    for i, ui in enumerate(u):
        if ui == 0:
            continue
        for j, vj in enumerate(v):
            if i + j > K:
                break
            out[i + j] += ui * vj
    return out


def series_solve(g, K):
    """x(e) with x(0)=0 solving sum_{m,n} g[m][n] x^m e^n = 0, by fixed point on g[1][0]."""
    x = [mp.mpf(0)] * (K + 1)
    for _ in range(K + 3):
        # R = G(x, e)
        R = [mp.mpf(0)] * (K + 1)
        xp = [mp.mpf(0)] * (K + 1)
        xp[0] = mp.mpf(1)
        for m in range(MMAX + 1):
            for n in range(min(NMAX, K) + 1):
                gm = g[m][n]
                if gm == 0:
                    continue
                for i, c in enumerate(xp):
                    if i + n > K:
                        break
                    R[i + n] += gm * c
            xp = pmul(xp, x, K)
        x = [x[i] - R[i] / g[1][0] for i in range(K + 1)]
        x[0] = mp.mpf(0)
    return x


def run(cfg, pool):
    dps = cfg["dps"]
    npts = cfg["npts"]
    mp.mp.dps = dps + 15
    ps = list(range(-(npts // 2), npts // 2 + 1))
    t0 = time.time()
    res = dict()
    for p, strs, Dstr in pool.imap_unordered(_node, ps):
        res[p] = [mp.mpmathify(s) for s in strs]
    wall = time.time() - t0

    he = mp.mpf(10) ** (-cfg["he"])
    g = [[None] * (NMAX + 1) for _ in range(MMAX + 1)]
    odd_ctl = mp.mpf(0)
    im_ctl = mp.mpf(0)
    for m in range(MMAX + 1):
        for n in range(NMAX + 1):
            nodes, wts = fd_weights(n, npts)
            s = mp.mpc(0)
            for idx, p in enumerate(nodes):
                s += wts[idx] * res[p][2 * m]
            val = (s / he ** n) / mp.factorial(n)
            im_ctl = max(im_ctl, abs(mp.im(val)) / (abs(val) + mp.mpf(10) ** (-dps)))
            g[m][n] = mp.re(val)
    for p in ps:                       # odd coefficients must vanish
        for k in [1, 3, 5, 7, 9, 11]:
            odd_ctl = max(odd_ctl, abs(res[p][k]) / (abs(res[p][0]) + 1))

    x = series_solve(g, 5)
    return dict(cfg=cfg, wall=wall, g=g, x=x, g00=g[0][0],
                odd_ctl=odd_ctl, im_ctl=im_ctl)


CFGS = [
    dict(label="A", dps=90, guard=25, r_w="0.04", N_w=40, npts=15, he=7),
    dict(label="B", dps=110, guard=30, r_w="0.04", N_w=64, npts=15, he=7),
    dict(label="C", dps=110, guard=30, r_w="0.05", N_w=64, npts=17, he=8),
    dict(label="D", dps=125, guard=30, r_w="0.045", N_w=72, npts=17, he=7),
]

NAMES = ["a", "b", "a3", "a4", "a5"]

if __name__ == "__main__":
    only = sys.argv[1:] if len(sys.argv) > 1 else None
    prev = None
    dump = []
    for cfg in CFGS:
        if only and cfg["label"] not in only:
            continue
        with Pool(8, initializer=_init, initargs=(cfg,)) as pool:
            R = run(cfg, pool)
        mp.mp.dps = 60
        print(f"\n### cfg {cfg['label']}: dps={cfg['dps']} guard={cfg['guard']} "
              f"r_w={cfg['r_w']} N_w={cfg['N_w']} npts={cfg['npts']} h_e=1e-{cfg['he']}"
              f"   [{R['wall']:.0f}s]", flush=True)
        print(f"   controls: max|odd c_k|/|c_0| = {mp.nstr(R['odd_ctl'],4)}   "
              f"max|Im g|/|g| = {mp.nstr(R['im_ctl'],4)}")
        print(f"   G(0,0) = xi_D(1/2,D*) = {mp.nstr(R['g00'],6)}   (residual of the D* literal)")
        for i, nm in enumerate(NAMES):
            v = R["x"][i + 1]
            line = f"   {nm:>3s} = {mp.nstr(v, 30)}"
            if prev is not None:
                line += f"    d(prev) = {mp.nstr(v - prev['x'][i+1], 5)}"
            print(line)
        dump.append(dict(label=cfg["label"], cfg=cfg, wall=R["wall"],
                         odd_ctl=mp.nstr(R["odd_ctl"], 6), im_ctl=mp.nstr(R["im_ctl"], 6),
                         g00=mp.nstr(R["g00"], 8),
                         coeffs={nm: mp.nstr(R["x"][i + 1], 40) for i, nm in enumerate(NAMES)}))
        prev = R
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "c33_fold5.json"), "w") as f:
            json.dump(dump, f, indent=1)
