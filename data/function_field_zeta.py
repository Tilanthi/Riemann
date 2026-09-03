import galois
import numpy as np
import time
from fractions import Fraction

def count_points(f_coeffs, p, k):
    """Count affine+infinity points of y^2=f(x) over GF(p^k), f_coeffs low-to-high degree."""
    GF = galois.GF(p**k)
    elems = GF.elements
    # f(x) evaluation via Horner, vectorized over all elements
    f_vals = GF.Zeros(len(elems))
    for c in reversed(f_coeffs):
        f_vals = f_vals * elems + GF(c % p)
    # squares: y^2 for y in GF -> build square set with multiplicity count
    ys = GF.elements
    sq = ys**2
    # count, for each value v, how many y give y^2=v
    # use dict keyed by int representation
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
        count += 1  # one point at infinity for odd-degree hyperelliptic model
    return count

def reconstruct_L_poly(Ns, p, g):
    """Given N_1..N_g (point counts over F_{p^1}..F_{p^g}), reconstruct L(T) coefficients
    (degree 2g) via the standard curve zeta function recursion:
    Z(T) = exp(sum N_n T^n/n) = L(T) / [(1-T)(1-pT)]
    We compute power sums s_n = p^n+1-N_n = sum of Frobenius eigenvalues^n (n=1..g),
    then get elementary symmetric functions e_1..e_g of the FULL 2g eigenvalues using the
    functional equation pairing (eigenvalues come in pairs multiplying to p), which lets us
    get all 2g power sums from the first g via s_{2g-n} relations... 
    Simpler + standard approach: use the direct recursive formula for the numerator
    coefficients a_1..a_g of L(T)=1+a_1 T+...+a_g T^g + (functional eqn mirrors rest),
    via Newton's identity: n*a_n = a_{n-1}*s_1 - a_{n-2}*s_2 + ... +/- s_n  (sign pattern),
    equivalently the standard: a_n determined from s_1..s_n by Newton-Girard with a_0=1.
    """
    s = [None] + [p**n + 1 - Ns[n-1] for n in range(1, g+1)]  # s[1..g]
    a = [Fraction(1)]  # a[0]=1
    for n in range(1, g+1):
        total = Fraction(0)
        for i in range(1, n+1):
            total += ((-1)**(i-1)) * a[n-i] * s[i]
        a_n = total / n
        a.append(a_n)
    return a  # a[0..g], L(T) = sum a_n T^n for n=0..g, then mirrored by functional equation

if __name__ == '__main__':
    p = 11
    g = 3
    f_coeffs = [1, 1, 0, 0, 0, 0, 0, 1]  # 1 + x + x^7  (degree 7, genus 3)
    print(f"Curve: y^2 = x^7 + x + 1 over F_{p}, genus {g}")
    Ns = []
    for k in range(1, g+1):
        t0=time.time()
        Nk = count_points(f_coeffs, p, k)
        dt = time.time()-t0
        print(f"  N_{k} = #C(F_{{{p}^{k}}}) = {Nk}   [{dt:.2f}s]")
        Ns.append(Nk)
    a = reconstruct_L_poly(Ns, p, g)
    print("L-polynomial coefficients a_0..a_g:", a)
    # full L(T) = a_0 + a_1 T + ... + a_g T^g + p*a_{g-1} T^{g+1} + ... + p^g*a_0 T^{2g}
    # (functional equation: a_{2g-i} = p^{g-i} a_i)
    full = list(a) + [None]*(g)
    for i in range(g):
        full[g+1+i] = p**(i+1) * a[g-1-i]
    print("Full L(T) coeffs (deg 0..2g):", full)
