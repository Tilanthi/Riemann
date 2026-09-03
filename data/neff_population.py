import mpmath as mp
import json, time, sys

mp.mp.dps = 40

LAMBDA = mp.mpf('1.5731433')
def N_eff(E):
    return mp.log(E/(2*mp.pi)) / mp.sqrt(12*LAMBDA)

def find_tight_pairs(E, window=30, n_pairs=5):
    """Locate the n_pairs tightest DISJOINT adjacent zero pairs in a window around nzeros(E)."""
    n_est = int(mp.nzeros(E))
    idx0 = max(1, n_est - window)
    gammas = {}
    for n in range(idx0, n_est + window + 1):
        gammas[n] = mp.zetazero(n).imag
    gaps = []
    for n in range(idx0, n_est + window):
        gaps.append((gammas[n+1]-gammas[n], n, n+1))
    gaps.sort(key=lambda x: x[0])
    chosen = []
    used = set()
    for gap, n1, n2 in gaps:
        if n1 in used or n2 in used:
            continue
        chosen.append((gap, n1, n2))
        used.add(n1); used.add(n2)
        # also block immediate neighbours so pairs are locally well-separated from each other
        used.add(n1-1); used.add(n2+1)
        if len(chosen) >= n_pairs:
            break
    return [dict(n1=n1, n2=n2, gamma1=gammas[n1], gamma2=gammas[n2]) for gap,n1,n2 in chosen]

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
    k1,k2,k3,k4 = c[1],c[2],c[3],c[4]
    B = -2*k2
    R = -4*k4/B**2
    q = B*d**2/2
    return dict(kappa1=k1,B=B,kappa3=k3,kappa4=k4,R=R,q=q)

heights = [mp.mpf('1e6'), mp.mpf('1e8'), mp.mpf('1e9')]
N_PAIRS = 5

all_results = {}
for E in heights:
    t0=time.time()
    pairs = find_tight_pairs(E, window=30, n_pairs=N_PAIRS)
    rows=[]
    for p in pairs:
        m0=(p['gamma1']+p['gamma2'])/2
        d=(p['gamma2']-p['gamma1'])/2
        meas = measure_kappas(m0,d,dps=40)
        rows.append(dict(n1=p['n1'],n2=p['n2'],m0=str(m0),d=str(d),
                          R=str(meas['R']), q=str(meas['q']), B=str(meas['B'])))
    dt=time.time()-t0
    Rs=[float(r['R']) for r in rows]
    qs=[float(r['q']) for r in rows]
    Rs_sorted=sorted(Rs); qs_sorted=sorted(qs)
    med_R = Rs_sorted[len(Rs_sorted)//2]
    med_q = qs_sorted[len(qs_sorted)//2]
    print(f"E={float(E):.0e} N_eff={float(N_eff(E)):.4f}  median R={med_R:.5f} (range {min(Rs):.4f}-{max(Rs):.4f})  median q={med_q:.5f} (range {min(qs):.4f}-{max(qs):.4f})  [{dt:.1f}s]")
    sys.stdout.flush()
    all_results[str(E)] = dict(N_eff=str(N_eff(E)), rows=rows, median_R=med_R, median_q=med_q, wall_s=dt)

json.dump(all_results, open('/data/Riemann/results/neff_population.json','w'), indent=1)
print('DONE')
