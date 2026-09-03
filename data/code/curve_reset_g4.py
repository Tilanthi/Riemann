import galois
import numpy as np
import time
from fractions import Fraction

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
        count += 1   # point at infinity for odd degree
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
    print(f"=== {label}: y^2 = poly (deg {len(f_coeffs)-1}) over F_{p}, genus {g} ===", flush=True)
    assert (len(f_coeffs)-1) % 2 == 1, "need odd degree for this simple point-at-infinity handling"
    assert np.gcd(len(f_coeffs)-1, p) == 1, "need gcd(deg,p)=1 to avoid the degeneracy found earlier"
    Ns = []
    t0=time.time()
    for k in range(1, g+1):
        Nk = count_points(f_coeffs, p, k)
        Ns.append(Nk)
        print(f"  N_{k} = {Nk}  [{time.time()-t0:.1f}s]", flush=True)
    a = reconstruct_L_poly(Ns, p, g)
    coeffs = [float(x) for x in a]
    full = list(coeffs) + [None]*g
    for i in range(g):
        full[g+1+i] = p**(i+1) * coeffs[g-1-i]
    roots_T = np.roots(list(reversed(full)))
    alphas = 1/roots_T
    max_dev = max(abs(abs(al)-p**0.5) for al in alphas)
    print(f"  max |alpha_i| deviation from sqrt(p)={p**0.5:.6f}: {max_dev:.2e}  (RH/purity check: should be ~0)", flush=True)
    return alphas

if __name__ == '__main__':
    # genus-4 curve, degree-9 poly, coefficients from digits of pi (arbitrary/non-cherry-picked),
    # p=11 chosen with gcd(9,11)=1 to avoid the earlier-found degeneracy
    pi_digits = [3,1,4,1,5,9,2,6,5,3]  # 10 coeffs for degree-9 poly (a0..a9)
    alphas = run_curve(pi_digits, 11, 4, "curve4 (y^2 = pi-digit-coeff deg-9 poly, g=4, p=11)")
    print("alphas:", alphas)
    angles = sorted(np.angle(a) for a in alphas)
    print("sorted angles (rad):", angles)
