import mpmath as mp
import json, time, sys

mp.mp.dps = 40

LAMBDA = mp.mpf('1.5731433')  # gamma0^2 + 2*gamma1 + c0, verified in letter 23
def N_eff(E):
    return mp.log(E/(2*mp.pi)) / mp.sqrt(12*LAMBDA)

def find_tight_pair(E, window=10):
    """Locate the tightest adjacent zero pair in a window around the nzeros(E)-estimated index."""
    n_est = int(mp.nzeros(E))
    idx0 = max(1, n_est - window)
    gammas = {}
    for n in range(idx0, n_est + window + 1):
        gammas[n] = mp.zetazero(n).imag
    best = None
    for n in range(idx0, n_est + window):
        gap = gammas[n+1] - gammas[n]
        if best is None or gap < best[0]:
            best = (gap, n, n+1)
    gap, n1, n2 = best
    g1, g2 = gammas[n1], gammas[n2]
    m0 = (g1+g2)/2
    d = (g2-g1)/2
    return dict(n_est=n_est, n1=n1, n2=n2, gamma1=g1, gamma2=g2, m0=m0, d=d)

def make_Xi(m0):
    def Xi(z):
        s = mp.mpf('0.5') + 1j*(m0+z)
        return mp.mpf('0.5')*s*(s-1)*mp.power(mp.pi, -s/2)*mp.gamma(s/2)*mp.zeta(s)
    return Xi

def measure_kappas(m0, d, dps=40, order=4):
    old_dps = mp.mp.dps
    mp.mp.dps = dps
    Xi = make_Xi(m0)
    def f(z):
        return mp.log(Xi(z) / (z**2 - d**2))
    c = mp.taylor(f, 0, order)
    mp.mp.dps = old_dps
    k1, k2, k3, k4 = c[1], c[2], c[3], c[4]
    B = -2*k2
    kappa2 = -(1/d**2 + B/2)
    R = -4*k4/B**2
    q = B*d**2/2
    return dict(kappa1=k1, B=B, kappa2=kappa2, kappa3=k3, kappa4=k4, R=R, q=q)

heights = [mp.mpf('1e6'), mp.mpf('3e6'), mp.mpf('1e7'), mp.mpf('3e7'),
           mp.mpf('1e8'), mp.mpf('3e8'), mp.mpf('1e9')]

results = []
for E in heights:
    t0 = time.time()
    pair = find_tight_pair(E, window=10)
    m0, d = pair['m0'], pair['d']
    meas40 = measure_kappas(m0, d, dps=40)
    meas60 = measure_kappas(m0, d, dps=60)  # stability check
    neff = N_eff(E)
    dt = time.time()-t0
    row = dict(
        E=str(E), N_eff=str(neff),
        n1=pair['n1'], n2=pair['n2'], m0=str(m0), d=str(d),
        kappa1_dps40=str(meas40['kappa1']), kappa1_dps60=str(meas60['kappa1']),
        B_dps40=str(meas40['B']), B_dps60=str(meas60['B']),
        kappa2_dps40=str(meas40['kappa2']), kappa2_dps60=str(meas60['kappa2']),
        kappa3_dps40=str(meas40['kappa3']), kappa3_dps60=str(meas60['kappa3']),
        kappa4_dps40=str(meas40['kappa4']), kappa4_dps60=str(meas60['kappa4']),
        R_dps40=str(meas40['R']), R_dps60=str(meas60['R']),
        q_dps40=str(meas40['q']), q_dps60=str(meas60['q']),
        wall_s=dt,
    )
    dps_stable = abs(meas40['R']-meas60['R']) < mp.mpf('1e-6')*abs(meas40['R']) if meas40['R']!=0 else True
    row['dps_stable_R'] = dps_stable
    results.append(row)
    print(f"E={float(E):.0e}  N_eff={float(neff):.4f}  d={float(d):.6g}  R={float(meas40['R']):.6f}  q={float(meas40['q']):.6f}  dps_stable={dps_stable}  ({dt:.1f}s)")
    sys.stdout.flush()

json.dump(results, open('/data/Riemann/results/neff_sweep.json','w'), indent=1)
print('DONE')
