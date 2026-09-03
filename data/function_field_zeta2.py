import galois
import numpy as np
import time
from fractions import Fraction

def count_points(f_coeffs, p, k):
    GF = galois.GF(p**k)
    elems = GF.elements
    f_vals = GF.Zeros(len(elems))
    for c in reversed(f_coeffs):
        f_vals = f_vals * elems + GF(c % p)
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
    print(f"=== {label}: y^2 = poly (deg {len(f_coeffs)-1}) over F_{p}, genus {g} ===")
    Ns = []
    for k in range(1, g+1):
        Nk = count_points(f_coeffs, p, k)
        Ns.append(Nk)
    a = reconstruct_L_poly(Ns, p, g)
    coeffs = [float(x) for x in a]
    full = list(coeffs) + [None]*g
    for i in range(g):
        full[g+1+i] = p**(i+1) * coeffs[g-1-i]
    roots_T = np.roots(list(reversed(full)))
    alphas = 1/roots_T
    max_dev = max(abs(abs(al)-p**0.5) for al in alphas)
    print(f"  N_1..N_{g} = {Ns}")
    print(f"  max |alpha_i| deviation from sqrt(p)={p**0.5:.6f}: {max_dev:.2e}  (RH check: should be ~0)")
    return alphas

if __name__ == '__main__':
    # curve 2: different prime, different polynomial
    run_curve([1,0,1,0,0,1], 13, 2, "curve2 (y^2=x^5+x^2+1, g=2, p=13)")
    run_curve([2,1,0,0,0,0,1], 7, 3, "curve3 (y^2=x^7+x+2, g=3, p=7)")
