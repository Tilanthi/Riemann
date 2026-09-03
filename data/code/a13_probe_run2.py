import numpy as np
from scipy import special
import json, time, sys
sys.path.insert(0, '.')
from h_omega_general import prime_sieve, c_omega_array

N_MAX = 100_000_000  # 1e8, covers all x points below

def build_x_points():
    trend = [1e4, 3e4, 1e5, 3e5, 1e6, 3e6, 1e7]
    cluster = list(np.linspace(5e6, 1e7, 8))
    tail = [3e7, 6e7, 1e8]
    return trend, cluster, tail

def g_general_vec(t, omega):
    pref = (4*omega/(2*omega-1)) * (np.pi**omega / special.gamma(omega))
    term1 = t**(omega-1) * special.beta((3-2*omega)/2, omega) * special.betaincc((3-2*omega)/2, omega, t**2)
    term2 = ((2*omega+1)/(4*omega)) * t**(-0.5) * special.beta((5-2*omega)/4, omega) * special.betaincc((5-2*omega)/4, omega, t**2)
    return pref * (term1 - term2)

def h_omega_1_batch_verbose(x_list, c_omega_cache, omega):
    Nmax = len(c_omega_cache)-1
    results = []
    for i, x in enumerate(x_list):
        t0 = time.time()
        N = int(np.floor(x))
        assert N <= Nmax
        n_arr = np.arange(1, N+1, dtype=np.float64)
        t = n_arr / x
        g = g_general_vec(t, omega)
        total = np.sum(c_omega_cache[1:N+1] * g)
        h = total/x
        results.append(h)
        print(f"   [{i+1}/{len(x_list)}] x={x:>12.0f}  h={h: .8e}  sign={'+' if h>0 else ('-' if h<0 else '0')}  "
              f"sqrt(x)*h={np.sqrt(x)*h: .6f}  [{time.time()-t0:.1f}s]", flush=True)
    return results

def run_for_omega(omega, is_prime_cache):
    t0 = time.time()
    c_arr = c_omega_array(N_MAX, omega, is_prime_cache)
    t_c = time.time()-t0
    print(f"omega={omega}: c_arr build {t_c:.1f}s", flush=True)
    trend, cluster, tail = build_x_points()
    all_x = trend + cluster + tail
    t0 = time.time()
    h_vals = h_omega_1_batch_verbose(all_x, c_arr, omega)
    t_eval = time.time()-t0
    results = []
    for x, h in zip(all_x, h_vals):
        results.append(dict(x=float(x), h=float(h), sign='+' if h>0 else ('-' if h<0 else '0'),
                             sqrtx_h=float(np.sqrt(x)*h)))
    print(f"omega={omega}: TOTAL eval {t_eval:.1f}s", flush=True)
    return dict(omega=omega, results=results, band_sizes=dict(trend=len(trend), cluster=len(cluster), tail=len(tail)),
                build_time=t_c, eval_time=t_eval)

if __name__ == '__main__':
    t0 = time.time()
    is_p = prime_sieve(N_MAX)
    print(f"prime sieve N={N_MAX} done in {time.time()-t0:.1f}s, {int(is_p.sum())} primes", flush=True)

    all_results = []
    for omega in [0.1, 0.3, 0.45]:
        r = run_for_omega(omega, is_p)
        all_results.append(r)
        json.dump(all_results, open('/data/Riemann/results/a13_probe.json', 'w'), indent=1)  # save incrementally

    print("ALL DONE, total time", time.time()-t0, flush=True)

    print("\n=== FALSIFIER CHECK ===")
    for r in all_results:
        omega = r['omega']
        n_trend = r['band_sizes']['trend']
        n_cluster = r['band_sizes']['cluster']
        cluster_signs = [pt['sign'] for pt in r['results'][n_trend:n_trend+n_cluster]]
        tail_signs = [pt['sign'] for pt in r['results'][n_trend+n_cluster:]]
        cluster_osc = len(set(cluster_signs)) > 1
        tail_osc = len(set(tail_signs)) > 1
        print(f"omega={omega}: cluster signs={cluster_signs} osc={cluster_osc}  tail signs={tail_signs} osc={tail_osc}")
