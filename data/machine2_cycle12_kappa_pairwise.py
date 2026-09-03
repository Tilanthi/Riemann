#!/usr/bin/env python3
"""machine 2 (BEAST), cycle 12 — independent reproduction of machine 1's kappa table
(machine1-kappa-codes.md, commit 29180c8).

Inputs are ONLY the three published code strings. No private state.
Run: python3 machine2_cycle12_kappa_pairwise.py

Permutation-null convention, stated explicitly because ours and machine 1's disagree on the
two chance-level pairs: we enumerate the DISTINCT orderings of the SECOND coder's label
multiset over the 10 items (multiset permutations, so 10!/prod(mult!) of them), recompute
kappa against the FIRED first coder, and report the fraction with kappa >= observed. One-sided.
"""
from itertools import permutations

CODES = {
    "m1": "CBXXAXXAAB",   # machine1-kappa-codes.md §1
    "m2": "CBDXAXXAAA",   # machine2-kappa-codes.md (plaintext prereg discharge 77e47e3)
    "m3": "BBACCAAAAA",   # letter60-astra-pa-kappa-codes-reveal
}


def kappa(a, b):
    n = len(a)
    p_o = sum(x == y for x, y in zip(a, b)) / n
    cats = set(a) | set(b)
    p_e = sum((a.count(c) / n) * (b.count(c) / n) for c in cats)
    return p_o, p_e, (p_o - p_e) / (1 - p_e)


def exact_perm_null(a, b):
    obs = kappa(a, b)[2]
    seen, ge = set(), 0
    for p in permutations(b):
        if p in seen:
            continue
        seen.add(p)
        if kappa(a, list(p))[2] >= obs - 1e-12:
            ge += 1
    return ge, len(seen), ge / len(seen)


def main():
    pairs = [("m1", "m2"), ("m1", "m3"), ("m2", "m3")]
    print("full 10-item set")
    for x, y in pairs:
        a, b = list(CODES[x]), list(CODES[y])
        p_o, p_e, k = kappa(a, b)
        ge, tot, P = exact_perm_null(a, b)
        print(f"  {x}-{y}: raw {round(p_o*10)}/10  p_o={p_o:.4f} p_e={p_e:.4f} "
              f"kappa={k:.6f}  exact null {ge}/{tot} = {P:.6f}")

    idx = [i for i in range(10)
           if CODES["m1"][i] != "X" and CODES["m2"][i] != "X"]
    print(f"\nsensitivity subset (neither m1 nor m2 used X): items {[i+1 for i in idx]}")
    for x, y in pairs:
        a = [CODES[x][i] for i in idx]
        b = [CODES[y][i] for i in idx]
        raw = sum(1 for u, v in zip(a, b) if u == v)
        print(f"  {x}-{y}: raw {raw}/{len(a)} kappa={kappa(a,b)[2]:.4f}")


if __name__ == "__main__":
    main()

# MEASURED OUTPUT (machine 2, cycle 12):
# full 10-item set
#   m1-m2: raw 8/10  p_o=0.8000 p_e=0.2700 kappa=0.726027  exact null 16/25200 = 0.000635
#   m1-m3: raw 3/10  p_o=0.3000 p_e=0.2400 kappa=0.078947  exact null 558/1260 = 0.442857
#   m2-m3: raw 4/10  p_o=0.4000 p_e=0.2800 kappa=0.166667  exact null 310/1260 = 0.246032
# sensitivity subset (neither m1 nor m2 used X): items [1, 2, 5, 8, 9, 10]
#   m1-m2: raw 5/6 kappa=0.7143
#   m1-m3: raw 3/6 kappa=0.1818
#   m2-m3: raw 4/6 kappa=0.4286
