import mpmath as mp
import numpy as np
import json, time

mp.mp.dps = 40

N_MAT = 300
M_REALIZATIONS = 100
W = 8

def one_realization(seed):
    rng = np.random.default_rng(seed)
    A = rng.normal(size=(N_MAT, N_MAT)) + 1j * rng.normal(size=(N_MAT, N_MAT))
    H = (A + A.conj().T) / 2.0
    eigs = np.sort(np.linalg.eigvalsh(H).real)

    mid = N_MAT // 2
    window = eigs[mid-4: mid+4]  # W=8
    gaps = np.diff(window)
    j = int(np.argmin(gaps))
    global_j = mid - 4 + j
    lam1, lam2 = eigs[global_j], eigs[global_j+1]
    if lam2 - lam1 < 1e-12:
        return dict(seed=seed, dq="degenerate d~0, excluded from stats but reported")

    eigs_mp = [mp.mpf(str(e)) for e in eigs]
    g1, g2 = eigs_mp[global_j], eigs_mp[global_j+1]
    d = (g2-g1)/2
    m0 = (g1+g2)/2

    def g_poly(t):
        val = mp.mpf(1)
        for e in eigs_mp:
            val *= (t-e)
        return val
    def f(z):
        return mp.log(g_poly(m0+z)/(z**2-d**2))
    c = mp.taylor(f, 0, 4)
    k1,k2,k3,k4 = c[1],c[2],c[3],c[4]
    B = -2*k2
    R = -4*k4/B**2
    q = B*d**2/2
    return dict(seed=seed, d=float(d), m0=float(m0), kappa1=float(k1), B=float(B),
                kappa3=float(k3), kappa4=float(k4), R=float(R), q=float(q))

if __name__ == '__main__':
    t0 = time.time()
    results = []
    dq_section = []
    for seed in range(M_REALIZATIONS):
        r = one_realization(seed)
        if 'dq' in r:
            dq_section.append(f"seed={seed}: {r['dq']}")
        results.append(r)
    dt = time.time()-t0
    print(f"M={M_REALIZATIONS} realizations, N={N_MAT}, W={W}, wall={dt:.1f}s", flush=True)

    json.dump(dict(results=results, dq_section=dq_section, N=N_MAT, M=M_REALIZATIONS, W=W),
              open('/data/Riemann/results/gue_leg.json', 'w'), indent=1)

    print("\n=== DQ-SECTION (unconditional, per R3) ===")
    print(" (empty: no degenerate cases)" if not dq_section else "\n".join(f" - {x}" for x in dq_section))

    Rs = [r['R'] for r in results if 'R' in r]
    qs = [r['q'] for r in results if 'R' in r]
    import statistics
    print(f"\nR: n={len(Rs)}  median={statistics.median(Rs):.5f}  mean={statistics.mean(Rs):.5f}  "
          f"min={min(Rs):.5f}  max={max(Rs):.5f}  stdev={statistics.stdev(Rs):.5f}")
    print(f"q: n={len(qs)}  median={statistics.median(qs):.5f}  mean={statistics.mean(qs):.5f}  "
          f"min={min(qs):.5f}  max={max(qs):.5f}")
