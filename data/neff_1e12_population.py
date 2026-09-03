import mpmath as mp
import json, time, sys

mp.mp.dps = 30

def my_bisect(f, a, b, tol, max_iter=60):
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

def find_tight_pairs_near(T_center, n_spacings=12, n_pairs=3, tol=mp.mpf('1e-8')):
    spacing = 2*mp.pi/mp.log(T_center/(2*mp.pi))
    step = spacing/4
    T_lo = T_center - n_spacings*spacing/2
    n_pts = int(n_spacings*spacing/step) + 1

    t_prev = T_lo
    z_prev = mp.siegelz(t_prev)
    zeros = []
    for i in range(1, n_pts+1):
        t = T_lo + i*step
        z = mp.siegelz(t)
        if (z_prev > 0) != (z > 0) and z_prev != 0 and z != 0:
            root = my_bisect(mp.siegelz, t_prev, t, tol)
            zeros.append(root)
        t_prev, z_prev = t, z
    gaps = [(zeros[i+1]-zeros[i], i) for i in range(len(zeros)-1)]
    gaps.sort(key=lambda x: x[0])
    chosen = []
    used = set()
    for gap, i in gaps:
        if i in used or (i+1) in used:
            continue
        chosen.append((zeros[i], zeros[i+1]))
        used.add(i); used.add(i+1)
        if len(chosen) >= n_pairs:
            break
    return chosen, spacing

def measure_kappas(m0, d, dps=30, order=4):
    def Xi(z):
        s = mp.mpf('0.5') + 1j*(m0+z)
        return mp.mpf('0.5')*s*(s-1)*mp.power(mp.pi, -s/2)*mp.gamma(s/2)*mp.zeta(s)
    def f(z):
        return mp.log(Xi(z) / (z**2 - d**2))
    c = mp.taylor(f, 0, order)
    k1,k2,k3,k4 = c[1],c[2],c[3],c[4]
    B = -2*k2
    R = -4*k4/B**2
    q = B*d**2/2
    return dict(kappa1=k1,B=B,kappa3=k3,kappa4=k4,R=R,q=q)

LAMBDA = mp.mpf('1.5731433')
def N_eff(E):
    return mp.log(E/(2*mp.pi)) / mp.sqrt(12*LAMBDA)

if __name__ == '__main__':
    # Two more E~1e12-scale windows, DISJOINT in index from letter-40's site (different T_center)
    centers = [mp.mpf('1000000005000'), mp.mpf('999999995000')]
    results = []
    for T_center in centers:
        t0 = time.time()
        pairs, spacing = find_tight_pairs_near(T_center, n_spacings=16, n_pairs=2, tol=mp.mpf('1e-8'))
        for g1, g2 in pairs:
            m0 = (g1+g2)/2
            d = (g2-g1)/2
            meas = measure_kappas(m0, d)
            neff = N_eff(m0)
            print(f"T_center={T_center}  m0={m0}  d={float(d):.6f}  N_eff={float(neff):.4f}  R={float(meas['R']):.5f}  q={float(meas['q']):.5f}  [{time.time()-t0:.1f}s so far]", flush=True)
            results.append(dict(T_center=str(T_center), m0=str(m0), d=str(d), N_eff=str(neff),
                                 R=str(meas['R']), q=str(meas['q']), kappa1=str(meas['kappa1']),
                                 B=str(meas['B']), kappa3=str(meas['kappa3']), kappa4=str(meas['kappa4'])))
        print(f"  window {T_center} done in {time.time()-t0:.1f}s, found {len(pairs)} pairs", flush=True)

    json.dump(results, open('/data/Riemann/results/neff_1e12_population.json','w'), indent=1)
    print("DONE")
