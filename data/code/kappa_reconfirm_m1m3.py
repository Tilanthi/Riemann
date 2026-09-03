from itertools import permutations

# m1 (Mac, fixed reference) — from machine1-kappa-codes.md
mac = {1:'C',2:'B',3:'X',4:'X',5:'A',6:'X',7:'X',8:'A',9:'A',10:'B'}
# m3 (mine, second coder — permuted) — from machine3-kappa-codes.md
mine = {1:'B',2:'B',3:'A',4:'C',5:'C',6:'A',7:'A',8:'A',9:'A',10:'A'}

items = list(range(1, 11))
mac_vec = [mac[i] for i in items]
mine_vec = [mine[i] for i in items]

def cohen_kappa(v1, v2):
    n = len(v1)
    cats = sorted(set(v1) | set(v2))
    po = sum(1 for a, b in zip(v1, v2) if a == b) / n
    m1_marg = {c: sum(1 for x in v1 if x == c) / n for c in cats}
    m2_marg = {c: sum(1 for x in v2 if x == c) / n for c in cats}
    pe = sum(m1_marg[c] * m2_marg[c] for c in cats)
    if pe == 1.0:
        return 1.0, po, pe
    kappa = (po - pe) / (1 - pe)
    return kappa, po, pe

k_obs, po, pe = cohen_kappa(mac_vec, mine_vec)
print(f"po={po:.4f} pe={pe:.4f} kappa_obs={k_obs:.4f}")
agree = [i for i in items if mac[i] == mine[i]]
print("agree on items:", agree, f"({len(agree)}/10)")

# exact enumeration: permute the SECOND coder's vector (mine), distinct relabelings
distinct_perms = set(permutations(mine_vec))
N = len(distinct_perms)
count = 0
for p in distinct_perms:
    k, _, _ = cohen_kappa(mac_vec, list(p))
    if abs(k) >= abs(k_obs) - 1e-12:
        count += 1
P = count / N
print(f"N distinct relabelings = {N}")
print(f"two-sided exact permutation P = {count}/{N} = {P:.4f}")
