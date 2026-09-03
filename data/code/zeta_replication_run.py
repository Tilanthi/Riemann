import mpmath as mp
import json, time
import numpy as np

mp.mp.dps = 60  # module-level, set once, matching trap #73/#74 discipline

def measure_window(n_start):
    """W=8: zetazero(n_start) through zetazero(n_start+7), tightest of 7 gaps, exact mp.taylor."""
    t0 = time.time()
    zeros = [mp.zetazero(n_start + i) for i in range(8)]
    ordinates = [mp.im(z) for z in zeros]
    assert all(ordinates[i] < ordinates[i+1] for i in range(7)), "not strictly increasing"
    t_zeros = time.time() - t0

    gaps = [(ordinates[i+1] - ordinates[i], i) for i in range(7)]
    gaps.sort(key=lambda x: x[0])
    gap, i = gaps[0]
    g1, g2 = ordinates[i], ordinates[i+1]
    d = (g2 - g1) / 2
    m0 = (g1 + g2) / 2

    def Xi(z):
        s = mp.mpf('0.5') + 1j * (m0 + z)
        return mp.mpf('0.5') * s * (s - 1) * mp.power(mp.pi, -s / 2) * mp.gamma(s / 2) * mp.zeta(s)
    def f(z):
        return mp.log(Xi(z) / (z**2 - d**2))
    c = mp.taylor(f, 0, 4)
    k1, k2, k3, k4 = c[1], c[2], c[3], c[4]
    B = -2 * k2
    R = -4 * k4 / B**2
    q = B * d**2 / 2
    t_total = time.time() - t0

    return dict(n_start=n_start, m0=float(m0), d=float(d), gap=float(gap),
                kappa1=float(k1), B=float(B), kappa3=float(k3), kappa4=float(k4),
                R=float(R), q=float(q), t_zeros=t_zeros, t_total=t_total,
                degenerate=bool(abs(float(k1)) < 1e-8 or abs(float(k3)) < 1e-8))

if __name__ == '__main__':
    n_starts = [int(round(x)) for x in np.geomspace(2e7, 1e8, 12)]
    results = []
    dq_section = []
    t0 = time.time()
    for i, n_start in enumerate(n_starts):
        r = measure_window(n_start)
        print(f"[{i+1}/12] n_start={n_start}  R={r['R']:.6f}  q={r['q']:.6f}  gap={r['gap']:.6f}  "
              f"degenerate={r['degenerate']}  [{r['t_total']:.1f}s]", flush=True)
        if r['degenerate']:
            dq_section.append(f"n_start={n_start}: kappa1 or kappa3 near zero, flagged")
        results.append(r)
        json.dump(dict(results=results, dq_section=dq_section), open('/data/Riemann/results/zeta_replication.json', 'w'), indent=1)
    print(f"\nALL DONE, total {time.time()-t0:.1f}s", flush=True)

    print("\n=== DQ-SECTION (unconditional, per R3) ===")
    print(" (empty: no degenerate windows)" if not dq_section else "\n".join(f" - {x}" for x in dq_section))

    Rs = [r['R'] for r in results]
    import statistics
    print(f"\nR: n={len(Rs)}  median={statistics.median(Rs):.5f}  mean={statistics.mean(Rs):.5f}  "
          f"min={min(Rs):.5f}  max={max(Rs):.5f}")
