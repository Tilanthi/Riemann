from multiprocessing import Pool
from mpmath import mp, mpc, mpf, findroot, nstr, fabs
import numpy as np, json, certify, eval2

def m(z):
    mp.dps = 25
    return float(fabs(eval2.F(mpc(z[0], z[1]))))

if __name__ == "__main__":
    out = []
    with Pool(4, initializer=certify._init, initargs=(25,)) as p:
        for (y0, y1) in [(43.8, 45.2), (46.8, 48.2)]:
            pts = [(float(x), float(y)) for x in np.linspace(0.52, 1.1843, 18)
                   for y in np.linspace(y0, y1, 50)]
            vs = p.map(m, pts, chunksize=8)
            idx = np.argsort(vs)[:5]
            print("box t[%g,%g]:" % (y0, y1))
            for i in idx: print("   |F|=%.6f at s=%.4f%+.4fi" % (vs[i], pts[i][0], pts[i][1]))
            out.append((pts[idx[0]], vs[idx[0]]))
    mp.dps = 30
    for (x0, y0), v in out:
        try:
            r = findroot(lambda s: eval2.F(s), mpc(str(x0), str(y0)), tol=mpf(10) ** -35)
            print("ROOT s0 = %s ;  |F(s0)| = %s ;  sigma0-1/2 = %s ; sigma0-1 = %s"
                  % (nstr(r, 25), nstr(fabs(eval2.F(r)), 3), nstr(mp.re(r) - mpf(1)/2, 12), nstr(mp.re(r) - 1, 12)))
        except Exception as e:
            print("findroot failed at", x0, y0, e)
