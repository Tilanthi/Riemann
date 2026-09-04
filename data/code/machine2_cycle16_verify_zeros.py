"""Localize + certify every zero the extension found; classify sigma0>1 (Davenport-Heilbronn)
vs 1/2 < sigma0 < 1 (off-line strip zero); compute the cycle-11/-15 floor (2 sigma0 - 1)/|s0|^2;
and cross-check each root on E1 (SAME theta ancestor -- declared, not claimed independent)."""
import json, math, sys
from multiprocessing import Pool
import numpy as np
from mpmath import mp, mpc, mpf, findroot, nstr, fabs, re as mre, im as mim
import certify, eval2, epstein_fold as e1

def m(z):
    mp.dps = 25
    return float(fabs(eval2.F(mpc(z[0], z[1]))))

if __name__ == "__main__":
    rows = json.load(open("ext_results.json"))
    boxes = [(r['t_lo'], r['t_hi'], r['zeros']) for r in rows if r['zeros'] not in (0, None)]
    print("boxes with zeros: %s" % boxes)
    roots = []
    with Pool(4, initializer=certify._init, initargs=(25,)) as p:
        for (y0, y1, nz) in boxes:
            pts = [(float(x), float(y)) for x in np.linspace(0.52, 1.1843, 16)
                   for y in np.linspace(y0 - 0.3, y1 + 0.3, 40)]
            vs = p.map(m, pts, chunksize=8)
            idx = np.argsort(vs)[:3]
            seeds = [pts[i] for i in idx]
            mp.dps = 35
            for sd in seeds:
                try:
                    r = findroot(lambda s: eval2.F(s), mpc(str(sd[0]), str(sd[1])), tol=mpf(10) ** -50)
                except Exception:
                    continue
                if not (0.5 < float(mre(r)) < 1.19 and y0 - 0.5 < float(mim(r)) < y1 + 0.5):
                    continue
                if any(abs(complex(r) - complex(q)) < 1e-12 for q in roots):
                    continue
                roots.append(r)
                break
    mp.dps = 40
    print("\n== ZEROS OF zeta2(s,1/7) with Re s >= 0.52, located and cross-checked ==")
    out = []
    for r in sorted(roots, key=lambda z: float(mim(z))):
        s0 = mpc(mre(r), mim(r))
        sig, t = mre(s0), mim(s0)
        res2 = fabs(eval2.F(s0))
        e1.set_cut(60); mp.dps = 60
        res1 = fabs(e1.zeta2(s0, mpf(1) / 7) * mpf(49) ** (-s0))
        mp.dps = 40
        floor = (2 * sig - 1) / (fabs(s0) ** 2)
        cls = "D-H (sigma>1)" if sig > 1 else "off-line strip (1/2<sigma<1)"
        print("  s0 = %s" % nstr(s0, 28))
        print("     sigma0 - 1/2 = %s   |s0| = %s   class = %s" % (nstr(sig - mpf(1)/2, 14), nstr(fabs(s0), 12), cls))
        print("     |F(s0)| on E2 = %s   on E1 (dps 60, SAME theta ancestor) = %s"
              % (nstr(res2, 4), nstr(res1, 4)))
        print("     floor (2*sigma0-1)/|s0|^2 = %s" % nstr(floor, 12))
        out.append(dict(re=str(sig), im=str(t), sigma_minus_half=str(sig - mpf(1)/2), abs_s0=str(fabs(s0)),
                        residual_E2=str(res2), residual_E1_dps60=str(res1), floor=str(floor), cls=cls))
    json.dump(out, open("zeros_verified.json", "w"), indent=1)
    print("\n  denominator: %d boxes flagged, %d roots recovered." % (len(boxes), len(roots)))
