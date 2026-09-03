import mpmath as mp
import json, time, sys

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

def scan_window(T_center, n_spacings, dps=25, tol=mp.mpf('1e-8')):
    old = mp.mp.dps
    mp.mp.dps = dps
    spacing = 2*mp.pi/mp.log(T_center/(2*mp.pi))
    step = spacing/4
    T_lo = T_center - n_spacings*spacing/2
    n_pts = int(n_spacings*spacing/step) + 1
    T_hi = T_lo + n_pts*step

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
    mp.mp.dps = old
    return zeros, T_lo, T_hi, spacing

def measure_kappas(m0, d, dps=30, order=4):
    old = mp.mp.dps
    mp.mp.dps = dps
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
    mp.mp.dps = old
    return dict(kappa1=k1,B=B,kappa3=k3,kappa4=k4,R=R,q=q)

LAMBDA = mp.mpf('1.5731433')
def N_eff(E):
    return mp.log(E/(2*mp.pi)) / mp.sqrt(12*LAMBDA)

if __name__ == '__main__':
    T_center = mp.mpf('14142135623730')   # floor(sqrt(2)*1e13), pre-registered, disjoint site
    n_spacings = 16
    dps = 25

    t0 = time.time()
    zeros, T_lo, T_hi, spacing = scan_window(T_center, n_spacings, dps=dps)
    t1 = time.time()
    n_scan = len(zeros)
    print(f"scan done: T_center={T_center} spacing={float(spacing):.6f} n_scan={n_scan}  [{t1-t0:.1f}s]", flush=True)

    old = mp.mp.dps
    mp.mp.dps = 25
    N_lo = mp.nzeros(T_lo)
    N_hi = mp.nzeros(T_hi)
    mp.mp.dps = old
    n_rigorous = int(N_hi - N_lo)
    t2 = time.time()
    certified = (n_scan == n_rigorous)
    print(f"nzeros: n_rigorous={n_rigorous}  certified={certified}  [{t2-t1:.1f}s]", flush=True)

    # asymptotic spacing law check
    theory_spacing = float(2*mp.pi/mp.log(T_center/(2*mp.pi)))
    if n_scan >= 2:
        emp_spacing = float(zeros[-1]-zeros[0])/(n_scan-1)
    else:
        emp_spacing = None
    print(f"theory_spacing={theory_spacing:.6f}  emp_spacing={emp_spacing}", flush=True)

    # tightest pair
    gaps = [(zeros[i+1]-zeros[i], i) for i in range(len(zeros)-1)]
    gaps.sort(key=lambda x: x[0])
    result = dict(T_center=str(T_center), T_lo=str(T_lo), T_hi=str(T_hi), spacing=str(spacing),
                  n_scan=n_scan, n_rigorous=n_rigorous, certified=certified,
                  theory_spacing=theory_spacing, emp_spacing=emp_spacing,
                  zeros=[str(z) for z in zeros], pairs=[])

    for gap, i in gaps[:3]:
        g1, g2 = zeros[i], zeros[i+1]
        m0 = (g1+g2)/2
        d = (g2-g1)/2
        meas = measure_kappas(m0, d)
        neff = N_eff(m0)
        print(f"pair gap={float(gap):.6f}  m0={m0}  d={float(d):.6f}  N_eff={float(neff):.4f}  "
              f"R={float(meas['R']):.5f}  q={float(meas['q']):.5f}", flush=True)
        result['pairs'].append(dict(m0=str(m0), d=str(d), N_eff=str(neff),
                                     R=str(meas['R']), q=str(meas['q']),
                                     kappa1=str(meas['kappa1']), B=str(meas['B']),
                                     kappa3=str(meas['kappa3']), kappa4=str(meas['kappa4'])))

    json.dump(result, open('/data/Riemann/results/e13_site_prereg.json','w'), indent=1)
    print("DONE total time", time.time()-t0)
