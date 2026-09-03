import numpy as np
import mpmath as mp
import json, time, statistics

mp.mp.dps = 30

def measure_R(theta_all):
    theta_all = sorted(theta_all)
    theta = [mp.mpf(str(t)) for t in theta_all]
    gaps = [(theta[i+1]-theta[i], i) for i in range(len(theta)-1)]
    gaps.sort(key=lambda x: x[0])
    gap, i = gaps[0]
    g1, g2 = theta[i], theta[i+1]
    d = (g2-g1)/2
    m0 = (g1+g2)/2
    def g_poly(t):
        val = mp.mpf(1)
        for th in theta:
            val *= (t - th)
        return val
    def f(z):
        return mp.log(g_poly(m0+z) / (z**2 - d**2))
    c = mp.taylor(f, 0, 4)
    k1,k2,k3,k4 = c[1],c[2],c[3],c[4]
    B = -2*k2
    R = -4*k4/B**2
    return float(R)

def cue_sample(n, rng):
    Z = (rng.normal(size=(n,n)) + 1j*rng.normal(size=(n,n))) / np.sqrt(2)
    Q, R_ = np.linalg.qr(Z)
    d_ = np.diagonal(R_)
    ph = d_ / np.abs(d_)
    Q = Q * ph
    eigvals = np.linalg.eigvals(Q)
    return np.angle(eigvals)

def cue_null_for_n(n_angles, M, seed):
    rng = np.random.default_rng(seed)
    Rs = []
    for _ in range(M):
        angles = cue_sample(n_angles, rng)
        Rs.append(measure_R(angles))
    return Rs

if __name__ == '__main__':
    mac_null = json.load(open('/data/Riemann/results/m1_genus_null_overlay.json'))
    null_by_g = {row['g']: dict(E_b2=row['E_b2'], se_b2=row['se_b2']) for row in mac_null['rows']}
    print("Reusing Mac's CUE null (M=400) for g=2..6, matched n_angles=2g:", flush=True)
    for g in sorted(null_by_g):
        print(f"  g={g}: E_b2={null_by_g[g]['E_b2']:.5f} se={null_by_g[g]['se_b2']:.5f}", flush=True)

    t0 = time.time()
    Rs7 = cue_null_for_n(14, M=200, seed=99887766)
    E7, SE7 = statistics.mean(Rs7), statistics.stdev(Rs7)/len(Rs7)**0.5
    null_by_g[7] = dict(E_b2=E7, se_b2=SE7)
    print(f"g=7 (n=14, M=200, own run): E={E7:.5f} SE={SE7:.5f}  [{time.time()-t0:.1f}s]", flush=True)

    d1 = json.load(open('/data/Riemann/results/curve_population.json'))
    d2 = json.load(open('/data/Riemann/results/curve_population_ext.json'))
    all_curves = d1 + d2['results']

    rows = []
    for r in all_curves:
        if not r['measure']:
            continue
        g = r['g']; p = r['p']; R = r['measure']['R']
        is_central = (abs(R - 0.5) < 1e-6) or r.get('central', False)
        entry = dict(g=g, p=p, R=R, central=is_central)
        if not is_central:
            null = null_by_g[g]
            z = (R - null['E_b2']) / (null['se_b2'] * (400**0.5 if g<=6 else 200**0.5))
            entry['null_E'] = null['E_b2']
            entry['null_se'] = null['se_b2']
            entry['z'] = z
            entry['ratio'] = R / null['E_b2']
        rows.append(entry)
        print(f"g={g} p={p} R={R:.4f} central={is_central}" +
              (f"  null_E={entry.get('null_E',0):.4f}  z={entry.get('z',0):+.2f}  ratio={entry.get('ratio',0):.3f}" if not is_central else ""),
              flush=True)

    nondeg = [r for r in rows if not r['central']]
    g24 = [r for r in nondeg if r['g'] <= 4]
    g57 = [r for r in nondeg if r['g'] >= 5]

    print("\n=== SUMMARY: raw R vs null-normalized ratio (R/E_null), by population ===")
    print(f"genus 2-4 (n={len(g24)}): raw median={statistics.median(r['R'] for r in g24):.4f}  "
          f"ratio median={statistics.median(r['ratio'] for r in g24):.4f}  "
          f"z median={statistics.median(r['z'] for r in g24):.3f}")
    print(f"genus 5-7 (n={len(g57)}): raw median={statistics.median(r['R'] for r in g57):.4f}  "
          f"ratio median={statistics.median(r['ratio'] for r in g57):.4f}  "
          f"z median={statistics.median(r['z'] for r in g57):.3f}")

    json.dump(dict(rows=rows, null_by_g=null_by_g), open('/data/Riemann/results/curve_matched_k_null.json','w'), indent=1)
