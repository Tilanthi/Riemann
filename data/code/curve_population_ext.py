import galois
import numpy as np
import mpmath as mp
import time, json
from fractions import Fraction

mp.mp.dps = 30

def get_digits(val, n):
    s = mp.nstr(val, 20, strip_zeros=False)
    frac = s.split('.')[1] if '.' in s else s
    return [int(c) for c in frac[:n] if c.isdigit()]

CONST_ORDER = ['sqrt17','sqrt19','sqrt23','ln5','ln7','catalan','sqrt29','sqrt31']
CONST_VALS = {
    'sqrt17': mp.sqrt(17), 'sqrt19': mp.sqrt(19), 'sqrt23': mp.sqrt(23),
    'ln5': mp.log(5), 'ln7': mp.log(7), 'catalan': mp.catalan,
    'sqrt29': mp.sqrt(29), 'sqrt31': mp.sqrt(31)
}

CURVES = [
    (5,5),(5,7),(5,13),   # p=11 replaced with p=13 -- erratum, gcd(11,11)=11 violated the constraint
    (6,5),(6,7),(6,11),
    (7,11),(7,7),   # p=5 replaced with p=11 -- erratum, gcd(15,5)=5 violated the constraint
]

def build_f_coeffs(g, p, const_name):
    deg = 2*g+1
    digits = get_digits(CONST_VALS[const_name], deg+1)
    coeffs = [d % p for d in digits]
    if coeffs[-1] == 0:
        coeffs[-1] = (coeffs[-1] + 1) % p
        if coeffs[-1] == 0:
            coeffs[-1] = 1
    return coeffs

def count_points(f_coeffs, p, k):
    GF = galois.GF(p**k)
    elems = GF.elements
    f_vals = GF.Zeros(len(elems))
    for c in reversed(f_coeffs):
        f_vals = f_vals * elems + GF(int(c) % p)
    ys = GF.elements
    sq = ys**2
    from collections import defaultdict
    sqcount = defaultdict(int)
    for s in sq:
        sqcount[int(s)] += 1
    count = 0
    for v in f_vals:
        vi = int(v)
        if vi == 0:
            count += 1
        else:
            count += sqcount.get(vi, 0)
    deg = len(f_coeffs)-1
    if deg % 2 == 1:
        count += 1
    return count

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

def run_curve(f_coeffs, p, g):
    Ns = []
    for k in range(1, g+1):
        Ns.append(count_points(f_coeffs, p, k))
    a = reconstruct_L_poly(Ns, p, g)
    coeffs = [float(x) for x in a]
    full = list(coeffs) + [None]*g
    for i in range(g):
        full[g+1+i] = p**(i+1) * coeffs[g-1-i]
    roots_T = np.roots(list(reversed(full)))
    alphas = 1/roots_T
    max_dev = max(abs(abs(al)-p**0.5) for al in alphas)
    return Ns, alphas, max_dev

def measure_R(alphas, p):
    angles = sorted(float(np.angle(a)) for a in alphas)
    theta = [mp.mpf(str(a)) for a in angles]
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
    q = B*d**2/2
    return dict(gap=float(gap), d=float(d), m0=float(m0), kappa1=float(k1), B=float(B),
                kappa3=float(k3), kappa4=float(k4), R=float(R), q=float(q))

if __name__ == '__main__':
    results = []
    dq_section = []
    t0 = time.time()
    for i, (g, p) in enumerate(CURVES):
        const_name = CONST_ORDER[i]
        f_coeffs = build_f_coeffs(g, p, const_name)
        assert np.gcd(2*g+1, p) == 1, f"degeneracy check failed for g={g} p={p}"
        tc0 = time.time()
        Ns, alphas, max_dev = run_curve(f_coeffs, p, g)
        purity_ok = bool(max_dev < 1e-6)
        meas = measure_R(alphas, p) if purity_ok else None
        dt = time.time()-tc0
        central = bool(meas and abs(meas['m0']) < 1e-9)
        print(f"[{i+1}/8] g={g} p={p} const={const_name}  f={f_coeffs}", flush=True)
        print(f"    Ns={Ns}  purity_dev={max_dev:.2e}  ok={purity_ok}  central={central}  [{dt:.1f}s]", flush=True)
        if meas:
            print(f"    R={meas['R']:.6f}  q={meas['q']:.6f}  B={meas['B']:.4f}  gap={meas['gap']:.4f}  m0={meas['m0']:.6f}", flush=True)
        if not purity_ok:
            dq_section.append(f"curve {i+1} (g={g},p={p}): purity check FAILED, dev={max_dev:.2e}")
        results.append(dict(g=g, p=p, const=const_name, f_coeffs=f_coeffs, Ns=Ns,
                             purity_dev=float(max_dev), purity_ok=purity_ok, central=central, measure=meas))
        json.dump(dict(results=results, dq_section=dq_section),
                  open('/data/Riemann/results/curve_population_ext.json','w'), indent=1)
    print(f"\nALL DONE, total time {time.time()-t0:.1f}s", flush=True)

    print("\n=== DQ-SECTION (unconditional, per R3) ===")
    if dq_section:
        for d in dq_section:
            print(" -", d)
    else:
        print(" (empty: no purity failures)")
    n_central = sum(1 for r in results if r['central'])
    print(f"\ncentral-pair (degenerate) curves: {n_central}/8")

    Rs_all = [r['measure']['R'] for r in results if r['measure']]
    Rs_nondeg = [r['measure']['R'] for r in results if r['measure'] and not r['central']]
    print(f"\nAll R values ({len(Rs_all)}): {sorted(Rs_all)}")
    print(f"Non-degenerate R values ({len(Rs_nondeg)}): {sorted(Rs_nondeg)}")
    import statistics
    if Rs_nondeg:
        print(f"non-deg R: median={statistics.median(Rs_nondeg):.4f}  min={min(Rs_nondeg):.4f}  max={max(Rs_nondeg):.4f}")
