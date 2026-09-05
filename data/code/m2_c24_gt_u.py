"""cycle24 Object A/V5 -- EXTERNAL GROUND TRUTH for u_i(1/2+i gamma).

Three independent discretisations of the SAME integral:
  (1) the repo instrument: single-panel Gauss-Legendre, mpmath degree d, 3*2^(d-1) nodes/subinterval
  (2) COMPOSITE Gauss-Legendre: each subinterval cut into panels of width <= lambda/4 where
      lambda = 2*pi/gamma is the oscillation wavelength, 20-node GL per panel.  Different scheme.
  (3) mpmath adaptive quad (tanh-sinh / GL with its own error control) on each subinterval,
      run at higher dps -- spot checks only, it is slow.
Certificate is agreement of (2) with (3) and stability of (2) under panel refinement,
never a single reading (our own cycle-17 law).
"""
import sys, os, json, time
sys.path.insert(0, "/shared/rh-exchange-repo/Riemann/data/code")
from mpmath import mp
import m2_u_instrument as U

mp.dps = 50
half = mp.mpf(1) / 2

# --- affine-mapped GL nodes: compute the [-1,1] rule ONCE per degree ---
from mpmath.calculus.quadrature import GaussLegendre
_gl = GaussLegendre(mp)
_ref = {}
def ref_nodes(deg):
    if deg not in _ref:
        raw = _gl.get_nodes(mp.mpf(-1), mp.mpf(1), deg, mp.prec)
        _ref[deg] = raw[0] if isinstance(raw[0], list) else raw
    return _ref[deg]

def panel_nodes(a, b, deg):
    r = ref_nodes(deg)
    c = (a + b) / 2; h = (b - a) / 2
    return [(c + h * x, h * w) for (x, w) in r]

def u_repo(phi, ivs, gamma, deg):
    """scheme (1): the repo instrument, one GL panel per subinterval."""
    rho = mp.mpc(half, gamma)
    tot = mp.mpc(0)
    for (a, b) in ivs:
        for (x, w) in panel_nodes(a, b, deg):
            v = phi(x)
            if v != 0:
                tot += w * v * mp.exp(rho * x)
    return tot

def u_composite(phi, ivs, gamma, ppw=4, deg=4):
    """scheme (2): composite GL, panel width <= wavelength/ppw, 3*2^(deg-1) nodes/panel."""
    rho = mp.mpc(half, gamma)
    lam = 2 * mp.pi / gamma if gamma > 0 else mp.inf
    hmax = lam / ppw
    tot = mp.mpc(0)
    npan = 0
    for (a, b) in ivs:
        n = int(mp.ceil((b - a) / hmax)) if hmax < (b - a) else 1
        n = max(n, 1)
        step = (b - a) / n
        for k in range(n):
            aa = a + k * step; bb = aa + step
            npan += 1
            for (x, w) in panel_nodes(aa, bb, deg):
                v = phi(x)
                if v != 0:
                    tot += w * v * mp.exp(rho * x)
    return tot, npan

def u_adaptive(phi, ivs, gamma, dps=60):
    """scheme (3): mpmath adaptive quad, its own error control."""
    old = mp.dps
    mp.dps = dps
    rho = mp.mpc(half, gamma)
    tot = mp.mpc(0)
    for (a, b) in ivs:
        tot += mp.quad(lambda x: phi(x) * mp.exp(rho * x), [a, b], maxdegree=12)
    mp.dps = old
    return tot


if __name__ == "__main__":
    gens = U.load_genomes("s1/M8")
    which = [int(x) for x in (sys.argv[1].split(",") if len(sys.argv) > 1 else ["0"])]
    gammas = [mp.mpf(g) for g in (sys.argv[2].split(",") if len(sys.argv) > 2
                                  else "14,50,100,150,200,250,300,350,400".split(","))]
    out = {}
    for i in which:
        phi, bumps = U.make_phi(gens[i])
        ivs = U.intervals(bumps)
        hmax = max(float(b - a) for a, b in ivs)
        print(f"=== basis {i}: {len(ivs)} subintervals, hmax={hmax:.4f}", flush=True)
        print(f"{'gamma':>7} {'|u| TRUE (comp)':>20} {'|u| deg8':>20} {'|u| deg10':>20} "
              f"{'relerr d8':>12} {'relerr d10':>12} {'panels':>8}", flush=True)
        rows = []
        for g in gammas:
            t0 = time.time()
            ut, npan = u_composite(phi, ivs, g, ppw=4, deg=4)
            ut2, _ = u_composite(phi, ivs, g, ppw=8, deg=4)   # refinement check
            u8 = u_repo(phi, ivs, g, 8)
            u10 = u_repo(phi, ivs, g, 10)
            ref = abs(ut)
            selfc = abs(ut - ut2) / ref if ref != 0 else mp.inf
            e8 = abs(u8 - ut) / ref
            e10 = abs(u10 - ut) / ref
            print(f"{mp.nstr(g,6):>7} {mp.nstr(ref,10):>20} {mp.nstr(abs(u8),10):>20} "
                  f"{mp.nstr(abs(u10),10):>20} {mp.nstr(e8,4):>12} {mp.nstr(e10,4):>12} "
                  f"{npan:>8}  [selfconv {mp.nstr(selfc,3)}] {time.time()-t0:.1f}s", flush=True)
            rows.append({"gamma": mp.nstr(g, 10), "u_true": mp.nstr(ref, 12),
                         "u_d8": mp.nstr(abs(u8), 12), "u_d10": mp.nstr(abs(u10), 12),
                         "relerr_d8": mp.nstr(e8, 6), "relerr_d10": mp.nstr(e10, 6),
                         "selfconv": mp.nstr(selfc, 4), "panels": npan})
        out[str(i)] = {"hmax": hmax, "nivs": len(ivs), "rows": rows}
    json.dump(out, open(f"machine2_cycle24_gt_basis_{'_'.join(map(str,which))}.json", "w"), indent=1)
