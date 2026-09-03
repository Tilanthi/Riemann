import mpmath as mp
import time

mp.mp.dps = 30   # SET BEFORE parsing any high-precision constants -- this is the fix

g1_approx = mp.mpf('14142135623731.13763022274')
g2_approx = mp.mpf('14142135623731.23545079008')
print('sanity: g1_approx as parsed =', mp.nstr(g1_approx, 25))
print('sanity: g2_approx as parsed =', mp.nstr(g2_approx, 25))

def my_bisect(f, a, b, tol, max_iter=200):
    fa = f(a)
    for _ in range(max_iter):
        mid = (a+b)/2
        fm = f(mid)
        if abs(b-a) < tol:
            return mid
        if (fa > 0) == (fm > 0):
            a, fa = mid, fm
        else:
            b = mid
    return (a+b)/2

def relocate(approx, tol, dps):
    old = mp.mp.dps
    mp.mp.dps = dps
    eps = mp.mpf('2e-6')
    lo, hi = approx-eps, approx+eps
    zlo, zhi = mp.siegelz(lo), mp.siegelz(hi)
    ok = (zlo>0) != (zhi>0)
    if not ok:
        mp.mp.dps = old
        raise SystemExit(f"bracket does not straddle at tol={tol}: z(lo)={zlo} z(hi)={zhi}  approx={mp.nstr(approx,20)}")
    root = my_bisect(mp.siegelz, lo, hi, tol)
    mp.mp.dps = old
    return root

def measure(g1, g2, dps):
    old = mp.mp.dps
    mp.mp.dps = dps
    m0 = (g1+g2)/2
    d = (g2-g1)/2
    def Xi(z):
        s = mp.mpf('0.5') + 1j*(m0+z)
        return mp.mpf('0.5')*s*(s-1)*mp.power(mp.pi, -s/2)*mp.gamma(s/2)*mp.zeta(s)
    def f(z):
        return mp.log(Xi(z) / (z**2 - d**2))
    c = mp.taylor(f, 0, 4)
    k1,k2,k3,k4 = c[1],c[2],c[3],c[4]
    B = -2*k2
    R = -4*k4/B**2
    q = B*d**2/2
    mp.mp.dps = old
    return k1,B,k4,R,q,m0,d

for tol_exp in [8, 12, 16, 20]:
    tol = mp.mpf(10)**(-tol_exp)
    dps = max(30, tol_exp+15)
    t0=time.time()
    g1 = relocate(g1_approx, tol, dps)
    g2 = relocate(g2_approx, tol, dps)
    k1,B,k4,R,q,m0,d = measure(g1, g2, dps)
    print(f"tol=1e-{tol_exp:<3d} dps={dps:3d}  d={mp.nstr(d,12)}  kappa4={mp.nstr(k4,10)}  B={mp.nstr(B,10)}  R={mp.nstr(R,10)}  q={mp.nstr(q,10)}  [{time.time()-t0:.1f}s]", flush=True)
