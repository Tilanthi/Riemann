import sys, time, itertools
from multiprocessing import Pool
from mpmath import mp, mpc, mpf, fabs
import eval2

DPS = 20
def _init():
    mp.dps = DPS

def modF(args):
    x, y = args
    mp.dps = DPS
    v = eval2.F(mpc(x, y))
    return float(fabs(v))

def dmodF(args):
    x, y = args
    mp.dps = DPS
    h = mpf(10) ** -8
    s = mpc(x, y)
    d = (eval2.F(s + h) - eval2.F(s - h)) / (2 * h)
    return float(fabs(d))

if __name__ == "__main__":
    import numpy as np
    xs = np.linspace(0.52, 1.1843, 12)
    ys = np.linspace(20, 43, 40)
    pts = [(float(x), float(y)) for y in ys for x in xs]
    t0 = time.time()
    with Pool(8, initializer=_init) as p:
        vals = p.map(modF, pts, chunksize=4)
        t1 = time.time()
        ds = p.map(dmodF, pts[::7], chunksize=2)
    t2 = time.time()
    v = np.array(vals).reshape(len(ys), len(xs))
    print("coarse |F| grid %dx%d = %d pts in %.1fs (%.1f ms/eval eff)" % (len(xs), len(ys), len(pts), t1-t0, (t1-t0)/len(pts)*1000))
    print("  min |F| = %.6f at %s" % (v.min(), pts[int(np.argmin(v))]))
    print("  max |F| = %.6f ;  median = %.4f" % (v.max(), np.median(v)))
    print("  |F| < 0.15 at %d of %d pts" % (int((v<0.15).sum()), v.size))
    print("  sampled max |F'| = %.4f over %d pts (%.1fs)" % (max(ds), len(ds), t2-t1))
    lo = np.argsort(np.array(vals))[:12]
    for i in lo:
        print("    small: s=%.4f%+.4fi  |F|=%.6f" % (pts[i][0], pts[i][1], vals[i]))
