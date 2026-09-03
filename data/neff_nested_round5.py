import mpmath as mp
import json, time, sys

mp.mp.dps = 40

LAMBDA = mp.mpf('1.5731433')
def N_eff(E):
    return mp.log(E/(2*mp.pi)) / mp.sqrt(12*LAMBDA)

def find_tight_pairs_offset(E, offset, window=50, n_pairs=10):
    n_est = int(mp.nzeros(E)) + offset
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

def median(xs):
    s = sorted(xs); n=len(s)
    return s[n//2] if n%2==1 else (s[n//2-1]+s[n//2])/2

heights = [mp.mpf('1e6'), mp.mpf('3e6'), mp.mpf('1e8')]
WINDOW_OFFSETS = [0, 300, 600]
N_PAIRS = 10

all_results = {}
for E in heights:
    window_medians = []
    all_pairs_pooled = []
    window_data = []
    for woff in WINDOW_OFFSETS:
        t0=time.time()
        pairs = find_tight_pairs_offset(E, woff, window=50, n_pairs=N_PAIRS)
        rows=[]
        for p in pairs:
            m0=(p['gamma1']+p['gamma2'])/2
            d=(p['gamma2']-p['gamma1'])/2
            meas = measure_kappas(m0,d,dps=40)
            rows.append(dict(n1=p['n1'],n2=p['n2'],m0=str(m0),d=str(d),
                              R=str(meas['R']), q=str(meas['q'])))
        dt=time.time()-t0
        Rs = [float(r['R']) for r in rows]
        med = median(Rs)
        window_medians.append(med)
        all_pairs_pooled.extend(Rs)
        window_data.append(dict(offset=woff, rows=rows, median_R=med, wall_s=dt))
        print(f"E={float(E):.0e} window_offset={woff}  n={len(rows)}  median R={med:.5f} (range {min(Rs):.4f}-{max(Rs):.4f})  [{dt:.1f}s]")
        sys.stdout.flush()
    pooled_median = median(all_pairs_pooled)
    within_height_spread = max(window_medians) - min(window_medians)
    print(f"  E={float(E):.0e} N_eff={float(N_eff(E)):.4f}  window medians={[round(m,5) for m in window_medians]}  pooled(n=30) median={pooled_median:.5f}  within-height spread={within_height_spread:.5f}")
    sys.stdout.flush()
    all_results[str(E)] = dict(N_eff=str(N_eff(E)), window_medians=window_medians,
                                pooled_median=pooled_median, within_height_spread=within_height_spread,
                                windows=window_data)

# between-height spread of pooled medians
pooled_meds = [all_results[str(E)]['pooled_median'] for E in heights]
between_height_spread = max(pooled_meds) - min(pooled_meds)
print(f"\nPooled medians by height: {[round(m,5) for m in pooled_meds]}")
print(f"Between-height spread: {between_height_spread:.5f}")
print(f"Within-height spreads: {[round(all_results[str(E)]['within_height_spread'],5) for E in heights]}")

all_results['summary'] = dict(pooled_medians=pooled_meds, between_height_spread=between_height_spread)
json.dump(all_results, open('/data/Riemann/results/neff_nested_round5.json','w'), indent=1)
print('DONE')
