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

CONST_ORDER = ['pi','e','sqrt2','sqrt3','sqrt5','sqrt7','ln2','ln3','phi','zeta3','sqrt11','sqrt13']
CONST_VALS = {
    'pi': mp.pi, 'e': mp.e, 'sqrt2': mp.sqrt(2), 'sqrt3': mp.sqrt(3), 'sqrt5': mp.sqrt(5),
    'sqrt7': mp.sqrt(7), 'ln2': mp.log(2), 'ln3': mp.log(3), 'phi': (1+mp.sqrt(5))/2,
    'zeta3': mp.zeta(3), 'sqrt11': mp.sqrt(11), 'sqrt13': mp.sqrt(13)
}

CURVES = [
    (2,7),(2,11),(2,13),(2,17),
    (3,5),(3,11),(3,13),(3,17),
    (4,5),(4,7),(4,11),(4,13),
]

def build_f_coeffs(g, p, const_name):
    deg = 2*g+1
    digits = get_digits(CONST_VALS[const_name], deg+1)
    coeffs = [d % p for d in digits]
    if coeffs[-1] == 0:   # leading coeff (a_deg) must be nonzero mod p
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

def run_curve(f_coeffs, p, g, label):
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
    t0 = time.time()
    for i, (g, p) in enumerate(CURVES):
        const_name = CONST_ORDER[i]
        f_coeffs = build_f_coeffs(g, p, const_name)
        assert np.gcd(2*g+1, p) == 1, f"degeneracy check failed for g={g} p={p}"
        label = f"g={g} p={p} const={const_name} f_coeffs={f_coeffs}"
        tc0 = time.time()
        Ns, alphas, max_dev = run_curve(f_coeffs, p, g, label)
        purity_ok = bool(max_dev < 1e-6)
        meas = measure_R(alphas, p) if purity_ok else None
        dt = time.time()-tc0
        print(f"[{i+1}/12] g={g} p={p} const={const_name}  f={f_coeffs}", flush=True)
        print(f"    Ns={Ns}  purity_dev={max_dev:.2e}  ok={purity_ok}  [{dt:.1f}s]", flush=True)
        if meas:
            print(f"    R={meas['R']:.6f}  q={meas['q']:.6f}  B={meas['B']:.4f}  gap={meas['gap']:.4f}", flush=True)
        results.append(dict(g=g, p=p, const=const_name, f_coeffs=f_coeffs, Ns=Ns,
                             purity_dev=float(max_dev), purity_ok=purity_ok, measure=meas))
        json.dump(results, open('/data/Riemann/results/curve_population.json','w'), indent=1)
    print(f"\nALL DONE, total time {time.time()-t0:.1f}s", flush=True)

    Rs = [r['measure']['R'] for r in results if r['measure']]
    qs = [r['measure']['q'] for r in results if r['measure']]
    print(f"\nR values ({len(Rs)}): {sorted(Rs)}")
    print(f"q values ({len(qs)}): {sorted(qs)}")
    import statistics
    if Rs:
        print(f"R: median={statistics.median(Rs):.4f}  min={min(Rs):.4f}  max={max(Rs):.4f}")
    if qs:
        print(f"q: median={statistics.median(qs):.4f}  min={min(qs):.4f}  max={max(qs):.4f}")
