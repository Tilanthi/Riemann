import numpy as np
import time, json
from mpmath import mp, mpf, mpc, pi as mp_pi, sqrt as mp_sqrt, gamma as mp_gamma, zeta as mp_zeta, besselk

mp.dps = 30

def zeta2_A(s, D):
    """Mac's evaluator A (Bessel representation), copied verbatim from heat68c.py."""
    D = mpf(D); s = mpc(s)
    t1 = mp_zeta(2*s)
    t2 = mp_sqrt(mp_pi)*mp_gamma(s - mpf('0.5'))*D**(1 - 2*s)*mp_zeta(2*s - 1)/mp_gamma(s)
    tot = t1 + t2
    nu = s - mpf('0.5')
    ssum = mpf(0)
    for k in range(1, 60):
        z = 2*mp_pi*D*k
        inner = mpf(0)
        for m in range(1, 60):
            inner += (mpf(m)/k)**nu * besselk(nu, z*m)
        term = inner
        ssum += term
        if abs(term) < mpf('1e-40') and k > 5:
            break
    return tot + (4*mp_pi**s/mp_gamma(s))*D**(mpf('0.5') - s)*ssum


def zeta2_direct_np(sigma, t, D, J, K):
    """Independent evaluator: brute force direct lattice sum in float64 (numpy),
    Re(s)>1 only. zeta2(s,D) = (1/2) sum'_{(j,k)!=(0,0)} (j^2+D^2 k^2)^{-s}."""
    j = np.arange(-J, J+1, dtype=np.float64)
    k = np.arange(-K, K+1, dtype=np.float64)
    JJ, KK = np.meshgrid(j, k, indexing='ij')
    base = JJ**2 + (D**2) * KK**2
    mask = base > 0
    base = base[mask]
    logbase = np.log(base)
    s = complex(sigma, t)
    # (base)^(-s) = exp(-s * log(base))
    vals = np.exp(-s * logbase)
    return 0.5 * np.sum(vals)


def adaptive_direct(sigma, t, D, J0=500, K0=None, max_doublings=6, reltol=1e-9):
    if K0 is None:
        K0 = max(500, int(min(200000, 30.0/D)))
    J, K = J0, K0
    prev = None
    for i in range(max_doublings):
        val = zeta2_direct_np(sigma, t, D, J, K)
        if prev is not None:
            rel = abs(val - prev) / abs(val)
            if rel < reltol:
                return val, J, K, rel
        prev = val
        J *= 2
        K = min(K*2, 4_000_000)
    return val, J, K, None


if __name__ == '__main__':
    Ds = ['0.02', '0.01', '0.005', '0.002', '0.001']
    sigmas = [3.0, 4.0]
    ts = [5, 20]
    print(f"{'D':>8} {'sigma':>6} {'t':>4} {'|A|':>14} {'|direct|':>14} {'reldiff':>12} {'conv_rel':>10} {'J':>7} {'K':>7}")
    results = []
    for D in Ds:
        Dv = float(D)
        for sigma in sigmas:
            for t in ts:
                s = mpc(sigma, t)
                t0 = time.time()
                zA = zeta2_A(s, D)
                val, J, K, conv = adaptive_direct(sigma, t, Dv)
                dt = time.time() - t0
                zA_c = complex(zA)
                reldiff = abs(zA_c - val) / abs(zA_c)
                print(f"{D:>8} {sigma:>6.1f} {t:>4d} {abs(zA_c):>14.6e} {abs(val):>14.6e} {reldiff:>12.3e} {str(conv):>10} {J:>7} {K:>7}  [{dt:.1f}s]", flush=True)
                results.append(dict(D=D, sigma=sigma, t=t, zA_abs=abs(zA_c), direct_abs=abs(val),
                                     reldiff=reldiff, conv_rel=conv, J=J, K=K, elapsed_s=dt))
    json.dump(results, open('/tmp/am8check/results.json', 'w'), indent=1)
    print("done")
