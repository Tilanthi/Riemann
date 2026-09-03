#!/usr/bin/env python3
"""machine 2 (BEAST), cycle 13 — every [MACHINE-VERIFIED] item in
machine2-cycle13-kappa-convention-closed-sigmastar-verified-comparison-gate-2026-09-03.md,
in one file, no private state, no network.

  A. kappa permutation null: our ONE-SIDED signed convention vs m1/m3's TWO-SIDED |kappa|.
  B. Davenport-Heilbronn kappa == the classical (sqrt(10-2sqrt5)-2)/(sqrt5-1).
  C. D-H coefficient vector decomposed in the character basis mod 5  ->  c*chi + cbar*chibar,
     zero principal and quadratic components  ->  Saias-Weingartner Thm 4 hypothesis satisfied
     (the vector lies in no single E_{5,psi}), and F entire (m_F = 0).
  D. DFMR II condition (2.6) for D-H: sup|A| = 1+kappa, integral bound sup^2/(2r).
  E. Dirichlet-inverse coefficients b_n of D-H by the general divisor recursion, and the
     empirical exponent log max|B(x)| / log x, which points the WRONG WAY at reachable x.

Run: python3 machine2_cycle13_checks.py          (~7 s, stdlib only)
"""
import cmath
import math
from itertools import permutations

# ---------------------------------------------------------------- A. kappa
CODES = {
    "m1": "CBXXAXXAAB",   # machine1-kappa-codes.md
    "m2": "CBDXAXXAAA",   # machine2-kappa-codes.md (prereg discharge 77e47e3)
    "m3": "BBACCAAAAA",   # letter60-astra-pa-kappa-codes-reveal
}


def kappa(a, b):
    n = len(a)
    p_o = sum(x == y for x, y in zip(a, b)) / n
    cats = set(a) | set(b)
    p_e = sum((a.count(c) / n) * (b.count(c) / n) for c in cats)
    return (p_o - p_e) / (1 - p_e)


def perm_null(a, b, two_sided):
    obs = kappa(a, b)
    seen, ge = set(), 0
    for p in permutations(b):
        if p in seen:
            continue
        seen.add(p)
        k = kappa(a, list(p))
        hit = abs(k) >= abs(obs) - 1e-12 if two_sided else k >= obs - 1e-12
        ge += hit
    return ge, len(seen)


def part_a():
    print("A. kappa permutation nulls (second coder's vector permuted, first fixed,")
    print("   exact enumeration of DISTINCT multiset orderings, no anchors)")
    for x, y in [("m1", "m2"), ("m1", "m3"), ("m2", "m3")]:
        a, b = list(CODES[x]), list(CODES[y])
        k = kappa(a, b)
        g1, n1 = perm_null(a, b, False)
        g2, n2 = perm_null(a, b, True)
        print(f"   {x}-{y}: kappa={k:.6f}  ONE-SIDED signed {g1}/{n1}={g1/n1:.6f}"
              f"   TWO-SIDED |k| {g2}/{n2}={g2/n2:.6f}")


# ------------------------------------------------- B/C/D. the D-H carrier
KAPPA = (math.sqrt(10 - 2 * math.sqrt(5)) - 2) / (math.sqrt(5) - 1)
A_VEC = [1.0, KAPPA, -KAPPA, -1.0, 0.0]          # a_1..a_5, then 5-periodic


def a_of(n):
    return A_VEC[(n - 1) % 5]


def part_bcd():
    print("\nB. D-H constant")
    print(f"   (sqrt(10-2sqrt5)-2)/(sqrt5-1) = {KAPPA!r}")
    print(f"   m1's FE-derived value 0.2840790438404123  ->  |diff| = "
          f"{abs(KAPPA - 0.2840790438404123):.3e}")

    print("\nC. character decomposition mod 5 (generator 2, chi(2)=i)")
    idx = {1: 0, 2: 1, 4: 2, 3: 3}
    for k in range(4):
        chi = [0j] * 5
        for n, e in idx.items():
            chi[n - 1] = cmath.exp(2j * math.pi * k * e / 4)
        c = sum(A_VEC[n] * chi[n].conjugate() for n in range(5)) / 4
        name = ["principal", "chi (order 4)", "quadratic", "chi-bar"][k]
        print(f"   component on chi^{k} ({name:>13}): {c.real:+.12f}{c.imag:+.12f}j")
    print("   => two distinct PRIMITIVE characters, zero principal component")
    print("   => lies in no single E_{5,psi}: Saias-Weingartner Thm 4 applies")
    print("   => no principal component: F entire, m_F = 0")

    print("\nD. DFMR II condition (2.6): psi(u) = -A(u) for u>1, A bounded")
    pref, s = [], 0.0
    for v in A_VEC:
        s += v
        pref.append(s)
    print(f"   A(u) over one period: {[round(x, 6) for x in pref]}")
    print(f"   sup|A| = {max(abs(x) for x in pref)!r}   1+kappa = {1 + KAPPA!r}")
    print("   int_1^inf |A|^2 t^{-1-2r} dt <= sup(A)^2/(2r) < inf for every r>0")


# ------------------------------------------------ E. Dirichlet inverse b_n
def part_e(N=1000000):
    print(f"\nE. Dirichlet-inverse coefficients b_n of D-H, n <= {N}")
    b = [0.0] * (N + 1)
    b[1] = 1.0
    for n in range(1, N + 1):
        bn = b[n]
        if bn == 0.0:
            continue
        d = 2
        while n * d <= N:
            ad = a_of(d)
            if ad != 0.0:
                b[n * d] -= ad * bn
            d += 1

    def conv(m):
        return sum(a_of(d) * b[m // d] for d in range(1, m + 1) if m % d == 0)

    print("   identity a*b = delta, n=1..12:",
          [round(conv(m), 12) for m in range(1, 13)])
    print(f"   {'x':>9} {'max|B(y)|, y<=x':>18} {'log max|B| / log x':>20}")
    S, mx = 0.0, 0.0
    marks = {10 ** k for k in range(1, 7)}
    for n in range(1, N + 1):
        S += b[n]
        mx = max(mx, abs(S))
        if n in marks:
            print(f"   {n:>9} {mx:>18.4f} {math.log(mx)/math.log(n):>20.4f}")
    print("   TRUE limsup of that column is sigma_c >= sigma* > 1 (Titchmarsh Ch.10;")
    print("   Saias-Weingartner arXiv:0807.0783). The finite-x estimate points the WRONG WAY.")


if __name__ == "__main__":
    part_a()
    part_bcd()
    part_e()

# ============================ MEASURED OUTPUT (machine 2, cycle 13) ============================
# A. kappa permutation nulls (second coder's vector permuted, first fixed,
#    exact enumeration of DISTINCT multiset orderings, no anchors)
#    m1-m2: kappa=0.726027  ONE-SIDED signed 16/25200=0.000635   TWO-SIDED |k| 16/25200=0.000635
#    m1-m3: kappa=0.078947  ONE-SIDED signed 558/1260=0.442857   TWO-SIDED |k| 831/1260=0.659524
#    m2-m3: kappa=0.166667  ONE-SIDED signed 310/1260=0.246032   TWO-SIDED |k| 436/1260=0.346032
#
# B. D-H constant
#    (sqrt(10-2sqrt5)-2)/(sqrt5-1) = 0.28407904384041227
#    m1's FE-derived value 0.2840790438404123  ->  |diff| = 5.551e-17   (= 1 ulp at this magnitude)
#
# C. character decomposition mod 5 (generator 2, chi(2)=i)
#    component on chi^0 (    principal): +0.000000000000+0.000000000000j
#    component on chi^1 (chi (order 4)): +0.500000000000-0.142039521920j
#    component on chi^2 (    quadratic): +0.000000000000-0.000000000000j
#    component on chi^3 (      chi-bar): +0.500000000000+0.142039521920j
#
# D. sup|A| = 1.2840790438404124   1+kappa = 1.2840790438404124
#
# E. identity a*b = delta, n=1..12: [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
#           x    max|B(y)|, y<=x   log max|B| / log x
#          10             2.0807               0.3182
#         100             4.1679               0.3100
#        1000            19.5999               0.4308
#       10000            76.3184               0.4707
#      100000           587.1237               0.5537
#     1000000          2954.1582               0.5784
