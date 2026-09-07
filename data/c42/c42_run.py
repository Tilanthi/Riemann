#!/usr/bin/env python3
"""c42_run.py — one column of the convergence-in-x table.

usage: c42_run.py X N DPS GLDEG NZEROS [tag]
Emits JSON to c42_x{X}_N{N}_dps{DPS}_g{GLDEG}.json with the full convention string.
"""
import sys, time, json, os
from mpmath import mp, mpf, log, pi, sqrt, sin, cos, mpmathify
from c42_connes_x import build_matrix, smallest_eigenpair, make_G, make_basis

X, N, DPS, GLDEG, NZ = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
TAG = sys.argv[6] if len(sys.argv) > 6 else ""
mp.dps = DPS

import glob as _glob
ZCACHE = "/workspace/rh/cycle42/zeta_zeros_dps%d.json" % DPS


def zeta_zeros(nz):
    for fn in sorted(_glob.glob("/workspace/rh/cycle42/zeta_zeros_dps*.json"),
                     key=lambda f: -int(f.split("dps")[-1].split(".")[0])):
        if int(fn.split("dps")[-1].split(".")[0]) >= DPS:
            d = json.load(open(fn))
            if len(d) >= nz:
                print("   zeta zeros from cache %s" % os.path.basename(fn), flush=True)
                return [mpmathify(s) for s in d[:nz]]
    from mpmath import zetazero
    out = []
    t0 = time.time()
    for n in range(1, nz + 1):
        out.append(zetazero(n).imag)
        if n % 10 == 0:
            print("   zetazero %d  %.1fs" % (n, time.time() - t0), flush=True)
    json.dump([mp.nstr(z, DPS + 5) for z in out], open(ZCACHE, "w"))
    return out


def roots_of_G(Gf, dGf, om, N, rmax):
    """all sign changes of G in the open pole-gaps, refined by Newton."""
    poles = [om[k] for k in range(1, N + 1)]
    edges = [mpf(0)] + poles
    roots = []
    for i in range(len(edges) - 1):
        a, b = edges[i], edges[i + 1]
        if a > rmax:
            break
        gap = b - a
        lo, hi = a + gap / mpf(400), b - gap / mpf(400)
        M = 24
        prev_r = lo
        prev_v = Gf(lo)
        for m in range(1, M + 1):
            r = lo + (hi - lo) * m / M
            v = Gf(r)
            if prev_v == 0:
                roots.append(prev_r)
            elif (prev_v < 0) != (v < 0):
                # bisect then Newton
                x0, x1 = prev_r, r
                for _ in range(60):
                    xm = (x0 + x1) / 2
                    vm = Gf(xm)
                    if (Gf(x0) < 0) != (vm < 0):
                        x1 = xm
                    else:
                        x0 = xm
                xr = (x0 + x1) / 2
                for _ in range(8):
                    xr = xr - Gf(xr) / dGf(xr)
                roots.append(xr)
            prev_r, prev_v = r, v
    return sorted(roots)


t_start = time.time()
print("=== x=%s N=%d dps=%d gldeg=%d %s" % (X, N, DPS, GLDEG, TAG), flush=True)
M, L, om, nr, pps = build_matrix(N, X, GLDEG)
t_build = time.time() - t_start
print("  matrix built %.1fs" % t_build, flush=True)
lam, v = smallest_eigenpair(M)
t_eig = time.time() - t_start - t_build
print("  eigenpair %.1fs  lambda_min=%s" % (t_eig, mp.nstr(lam, 15)), flush=True)

Gf, dGf = make_G(v, om, nr, L, N)
gam = zeta_zeros(NZ)
rmax = gam[-1] * mpf("1.05")
rts = roots_of_G(Gf, dGf, om, N, rmax)
print("  roots of G below %s : %d   (zeta zeros there: %d)"
      % (mp.nstr(rmax, 8), len([r for r in rts if r <= rmax]), NZ), flush=True)

rows = []
for n in range(1, NZ + 1):
    g = gam[n - 1]
    if n - 1 < len(rts):
        rn = rts[n - 1]
        d_idx = abs(rn - g)
    else:
        rn, d_idx = None, None
    # nearest root, independent of index
    nearest_i = min(range(len(rts)), key=lambda i: abs(rts[i] - g)) if rts else None
    near = rts[nearest_i] if nearest_i is not None else None
    rows.append(dict(n=n, gamma=mp.nstr(g, 60),
                     root_by_index=(mp.nstr(rn, 60) if rn is not None else None),
                     diff_by_index=(mp.nstr(d_idx, 8) if d_idx is not None else None),
                     nearest_root=mp.nstr(near, 60) if near is not None else None,
                     diff_nearest=mp.nstr(abs(near - g), 8) if near is not None else None,
                     root_index=nearest_i, offset=(nearest_i - (n - 1)) if nearest_i is not None else None))
    if n <= 6 or n % 10 == 0 or n == NZ:
        print("   n=%2d gamma=%s  d_near=%s  off=%s"
              % (n, mp.nstr(g, 12), rows[-1]['diff_nearest'], rows[-1]['offset']), flush=True)

out = dict(
    convention=("basis phi_0=1/sqrt(L), phi_k=sqrt(2/L)cos(2 pi k t/L), t in [-L/2,L/2], L=log(x); "
                "QW(f,f)=W(g), g=autocorrelation of f, W = explicit formula "
                "h(i/2)+h(-i/2)-g(0)log(pi)+(1/2pi)INT h(r)Re psi(1/4+ir/2)dr-2 SUM Lambda(n)n^{-1/2}g(log n); "
                "prime powers n<=x only; minimise over ||f||_{L2(dt)}=1; "
                "F(r)=INT f e^{irt}dt = Mellin transform of eta_x on the critical line = sin(rL/2)G(r); "
                "approximants = positive real roots of G; quadrature = fixed Gauss-Legendre on [0,L]"),
    x=X, N=N, dps=DPS, gl_degree=GLDEG, prime_powers=pps,
    L=mp.nstr(L, 40), lambda_min=mp.nstr(lam, 30),
    n_roots_below_rmax=len([r for r in rts if r <= rmax]),
    seconds=time.time() - t_start, tag=TAG, rows=rows)
fn = "/workspace/rh/cycle42/c42_x%d_N%d_dps%d_g%d%s.json" % (X, N, DPS, GLDEG, ("_" + TAG if TAG else ""))
json.dump(out, open(fn, "w"), indent=1)
print("  wrote %s  total %.1fs" % (fn, time.time() - t_start), flush=True)
