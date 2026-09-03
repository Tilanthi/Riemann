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
    n = len(theta_all)
    out = {}
    for w in range(2, n+1):
        Rs = []
        for start in range(0, n-w+1):
            window = list(range(start, start+w))
            gaps = [(theta_all[window[k+1]]-theta_all[window[k]], window[k], window[k+1]) for k in range(w-1)]
            gaps.sort(key=lambda x: x[0])
            _, i, j = gaps[0]
            R = measure_R_for_pair(theta_all, i, j)
            Rs.append(R)
        out[w] = Rs
    return out

if __name__ == '__main__':
    d = json.load(open('/data/Riemann/results/genus_ladder_fixed_p.json'))
    results = {}
    t0 = time.time()
    for rec in d['results']:
        g, p, Ns = rec['g'], rec['p'], rec['Ns']
        alphas, max_dev = get_alphas(Ns, p, g)
        print(f"g={g} p={p}: purity_dev={max_dev:.2e} (re-verified)", flush=True)
        angles = sorted(float(np.angle(a)) for a in alphas)
        theta_all = [mp.mpf(str(a)) for a in angles]
        n_angles = len(theta_all)  # = 2g
        tc0 = time.time()
        sweep = sliding_window_sweep(theta_all)
        print(f"  sweep done in {time.time()-tc0:.1f}s ({n_angles} angles, up to w={n_angles})", flush=True)
        curve_key = f"g{g}"
        results[curve_key] = {}
        for w, Rs in sweep.items():
            med = statistics.median(Rs)
            k_candidates = w - 1  # number of gaps in this window
            marker = "  <-- FULL SEARCH (Letter-78 value)" if w == n_angles else ""
            print(f"    w={w:2d} (k={k_candidates:2d} candidates)  n_positions={len(Rs)}  median_R={med:.5f}{marker}", flush=True)
            results[curve_key][w] = dict(k_candidates=k_candidates, n_positions=len(Rs), median_R=med, all_R=Rs)
    print(f"\nALL DONE, total {time.time()-t0:.1f}s", flush=True)
    json.dump(results, open('/data/Riemann/results/k_matched_overlay.json','w'), indent=1)
