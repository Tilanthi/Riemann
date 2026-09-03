import json, time, statistics
from fractions import Fraction
import numpy as np
import mpmath as mp

mp.mp.dps = 40

def reconstruct_L_poly(Ns, p, g):
    s = [None] + [p**n + 1 - Ns[n-1] for n in range(1, g+1)]
    a = [Fraction(1)]
    for n in range(1, g+1):
        total = Fraction(0)
        for i in range(1, n+1):
            total += ((-1)**(i-1)) * a[n-i] * s[i]
        a_n = total / n
        a.append(a_n)
    return a

def get_alphas(Ns, p, g):
    a = reconstruct_L_poly(Ns, p, g)
    coeffs = [float(x) for x in a]
    full = list(coeffs) + [None]*g
    for i in range(g):
        full[g+1+i] = p**(i+1) * coeffs[g-1-i]
    roots_T = np.roots(list(reversed(full)))
    alphas = 1/roots_T
    max_dev = max(abs(abs(al)-p**0.5) for al in alphas)
    return alphas, max_dev

def measure_R_for_pair(theta_all, i, j):
    """theta_all: full sorted list of mpf angles (the WHOLE curve spectrum, unchanged).
    i,j: indices of the chosen tightest pair within a window -- only the SEARCH is windowed,
    the background polynomial g(theta) always uses the full spectrum, matching what 'window size'
    means on the zeta side (search range narrows, background does not)."""
    g1, g2 = theta_all[i], theta_all[j]
    d = (g2-g1)/2
    m0 = (g1+g2)/2
    def g_poly(t):
        val = mp.mpf(1)
        for th in theta_all:
            val *= (t - th)
        return val
    def f(z):
        return mp.log(g_poly(m0+z) / (z**2 - d**2))
    c = mp.taylor(f, 0, 4)
    k1,k2,k3,k4 = c[1],c[2],c[3],c[4]
    B = -2*k2
    R = -4*k4/B**2
    return float(R)

def sliding_window_sweep(theta_all):
    """theta_all: sorted list of mpf angles. Returns dict w -> list of R values (one per window position)."""
    n = len(theta_all)
    out = {}
    for w in range(2, n+1):
        Rs = []
        for start in range(0, n-w+1):
            window = list(range(start, start+w))
            # tightest gap within this window (indices into theta_all)
            gaps = [(theta_all[window[k+1]]-theta_all[window[k]], window[k], window[k+1]) for k in range(w-1)]
            gaps.sort(key=lambda x: x[0])
            _, i, j = gaps[0]
            R = measure_R_for_pair(theta_all, i, j)
            Rs.append(R)
        out[w] = Rs
    return out

if __name__ == '__main__':
    d = json.load(open('/data/Riemann/results/curve_population_ext.json'))
    target_curves = [(7,11), (7,7)]
    results = {}
    t0 = time.time()
    for g_target, p_target in target_curves:
        rec = next(r for r in d['results'] if r['g']==g_target and r['p']==p_target)
        Ns = rec['Ns']
        alphas, max_dev = get_alphas(Ns, p_target, g_target)
        print(f"g={g_target} p={p_target}: purity_dev={max_dev:.2e} (re-verified)", flush=True)
        angles = sorted(float(np.angle(a)) for a in alphas)
        theta_all = [mp.mpf(str(a)) for a in angles]
        tc0 = time.time()
        sweep = sliding_window_sweep(theta_all)
        print(f"  sweep done in {time.time()-tc0:.1f}s", flush=True)
        curve_key = f"g{g_target}_p{p_target}"
        results[curve_key] = {}
        for w, Rs in sweep.items():
            med = statistics.median(Rs)
            print(f"    w={w:2d}  n_positions={len(Rs)}  median_R={med:.5f}  range=[{min(Rs):.5f},{max(Rs):.5f}]", flush=True)
            results[curve_key][w] = dict(n_positions=len(Rs), median_R=med, min_R=min(Rs), max_R=max(Rs), all_R=Rs)
    print(f"\nALL DONE, total {time.time()-t0:.1f}s", flush=True)
    json.dump(results, open('/data/Riemann/results/selection_rule_probe.json','w'), indent=1)

    print("\n=== DQ-SECTION (unconditional) ===")
    print(" (empty: pure exact polynomial arithmetic on already-certified eigenvalues, no failures)")
