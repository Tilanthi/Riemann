"""machine2 cycle22 — POST-HOC supplements (labelled: not part of the scored ladder).

(i)  refined crossing delta* on PAIR-A by bisection
(ii) |u_0(1/2+i gamma)| vs gamma -- why PAIR-B cannot fire
(iii) witness power vs height: lam_min(S_Z(0.45),G) for removals across the window
"""
import json
from mpmath import mp
from m2_u_instrument import Basis, load_genomes, load_target
from m2_witness_analysis import gram, lam, mat, zero_pair_K, N

mp.dps = 40
gens = load_genomes("s1/M8"); tgt = load_target("s1/M8")
gam = [mp.mpf(g) for g in json.load(open("/workspace/rh/cycle22/zeros210.json"))]
bases = [Basis(g, degree=8) for g in gens]
half = mp.mpf(1) / 2
G = gram(); K200 = mat(tgt["K_T200"])
up200 = [g for g in gam if g <= 200]


def quad_analytic(delta, g0):
    p = mp.mpc(half + delta, g0); q = mp.mpc(half - delta, g0)
    up = [b.u(p) for b in bases]; uq = [b.u(q) for b in bases]
    M = mp.matrix(N, N)
    for i in range(N):
        for j in range(N):
            M[i, j] = 2 * mp.re(up[i] * mp.conj(uq[j]) + up[j] * mp.conj(uq[i]))
    return M


def lmin(k, delta):
    g1, g2 = up200[k], up200[k + 1]
    g0 = (g1 + g2) / 2
    base = K200 - zero_pair_K(mp.mpc(half, g1)) - zero_pair_K(mp.mpc(half, g2))
    return lam(base + quad_analytic(mp.mpf(delta), g0), G)[0]


print("=== (i) POST-HOC: refined crossing on PAIR-A (k=0) ===")
lo, hi = mp.mpf("0.05"), mp.mpf("0.1")
for _ in range(30):
    mid = (lo + hi) / 2
    if lmin(0, mid) < 0:
        hi = mid
    else:
        lo = mid
print(f"delta* = {mp.nstr((lo+hi)/2, 12)}   (scored ladder rung delta_c = 0.1)")

print("\n=== (ii) |u_0(1/2 + i gamma)| vs height ===")
for g in [mp.mpf(x) for x in ["14.134725", "17.578382", "50", "100", "150", "185.236626"]]:
    v = bases[0].u(mp.mpc(half, g))
    print(f"  gamma={mp.nstr(g,10):>12}   |u_0| = {mp.nstr(abs(v),6)}")

print("\n=== (iii) POST-HOC: witness response vs height, delta=0.45 ===")
print(f"{'k':>4} {'gamma_0':>12} {'lam_min(S_Z(0.45))':>24} {'lam_min(S_Z(0))':>24}")
for k in [0, 1, 2, 5, 10, 20, 40, 70]:
    g0 = (up200[k] + up200[k + 1]) / 2
    a = lmin(k, "0.45"); b = lmin(k, "0")
    print(f"{k:>4} {mp.nstr(g0,8):>12} {mp.nstr(a,10):>24} {mp.nstr(b,10):>24}")
