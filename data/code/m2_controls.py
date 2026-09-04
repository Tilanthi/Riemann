"""machine2 cycle22 — controls for the N2/N5 witness design.

(a) residue-sum demonstration: for an FE-closed OFF-LINE quadruple the zero-side term of the
    explicit formula is the residue sum of U(s) F'/F(s), which equals the ANALYTIC form S,
    not m1's spec form K.  Checked by an actual contour integral on a model F with exactly
    that zero set.
(b) on-line control ladder: same removal, on-line re-insertion at gamma_0 +- eta.  At
    eta = (g2-g1)/2 the configuration IS the true one, so lam_min must return to
    lam_min(K_T200,G) = +1.176e-5.  Certificate that negativity measures distance from
    zeta's zero set, not off-line-ness.
(c) baseline scan over adjacent zero pairs: the delta=0 baseline is set by the coalescence,
    so the closest available pair minimises it.
(d) noise floor: lam_min shift under a perturbation the size of m3's current identity closure.
"""
import json, random, time
from mpmath import mp
from m2_u_instrument import Basis, load_genomes, load_target
from m2_witness_analysis import gram, lam, mat, zero_pair_K, N

mp.dps = 40
gens = load_genomes("s1/M8")
tgt = load_target("s1/M8")
gam = [mp.mpf(g) for g in json.load(open("/workspace/rh/cycle22/zeros210.json"))]
bases = [Basis(g, degree=8) for g in gens]
half = mp.mpf(1) / 2

G = gram()
K200 = mat(tgt["K_T200"])


def A_analytic(delta, g0):
    p = mp.mpc(half + delta, g0); q = mp.mpc(half - delta, g0)
    up = [b.u(p) for b in bases]; uq = [b.u(q) for b in bases]
    M = mp.matrix(N, N)
    for i in range(N):
        for j in range(N):
            M[i, j] = 2 * mp.re(up[i] * mp.conj(uq[j]) + up[j] * mp.conj(uq[i]))
    return M


def A_spec(delta, g0):
    p = mp.mpc(half + delta, g0); q = mp.mpc(half - delta, g0)
    return zero_pair_K(p) + zero_pair_K(q)


print("=== (a) residue sum over an FE-closed off-line quadruple ===", flush=True)
d = mp.mpf("0.2"); g0 = mp.mpf("17.5")
p = mp.mpc(half + d, g0); q = mp.mpc(half - d, g0)
zs = [p, mp.conj(p), 1 - p, 1 - mp.conj(p)]
print("quadruple:", [mp.nstr(z, 8) for z in zs])
b0 = bases[0]


def E(s):
    r = mp.mpc(1)
    for z in zs:
        r *= (s - z)
    return r


def dE(s):
    tot = mp.mpc(0)
    for k in range(4):
        pr = mp.mpc(1)
        for m in range(4):
            if m != k:
                pr *= (s - zs[m])
        tot += pr
    return tot


def U00(s):
    return b0.u(s) * b0.u(1 - s)          # transform of Phi_00 (symmetric in s<->1-s)


# rectangle contour around all four zeros: Re in [-1,2], Im in [-25,25]
def contour_sum():
    tot = mp.mpc(0)
    corners = [(mp.mpf(-1), mp.mpf(-25)), (mp.mpf(2), mp.mpf(-25)),
               (mp.mpf(2), mp.mpf(25)), (mp.mpf(-1), mp.mpf(25))]
    for k in range(4):
        (x0, y0) = corners[k]; (x1, y1) = corners[(k + 1) % 4]
        f = lambda t: U00(mp.mpc(x0 + (x1 - x0) * t, y0 + (y1 - y0) * t)) * \
            dE(mp.mpc(x0 + (x1 - x0) * t, y0 + (y1 - y0) * t)) / \
            E(mp.mpc(x0 + (x1 - x0) * t, y0 + (y1 - y0) * t)) * \
            mp.mpc(x1 - x0, y1 - y0)
        tot += mp.quad(f, [0, 1])
    return tot / (2 * mp.pi * mp.j)


t0 = time.time()
res = contour_sum()
S = A_analytic(d, g0); K = A_spec(d, g0)
print(f"contour residue sum  U00 over quadruple = {mp.nstr(res, 20)}   ({time.time()-t0:.0f}s)")
print(f"analytic form  S[0][0]                  = {mp.nstr(S[0,0], 20)}")
print(f"m1 spec form   K[0][0]                  = {mp.nstr(K[0,0], 20)}")
print(f"|residue - S| = {mp.nstr(abs(res - S[0,0]),4)}     |residue - K| = {mp.nstr(abs(res - K[0,0]),4)}")

print("\n=== (b) on-line control ladder (same removal, on-line re-insertion) ===", flush=True)
g1, g2 = gam[0], gam[1]
g0 = (g1 + g2) / 2
B_rem = zero_pair_K(mp.mpc(half, g1)) + zero_pair_K(mp.mpc(half, g2))
eta_star = (g2 - g1) / 2
print(f"eta* = {mp.nstr(eta_star,12)} returns the TRUE configuration")
for e in ["0", "0.5", "1", "2", "3", "3.4", str(mp.nstr(eta_star, 20))]:
    ee = mp.mpf(e)
    A = zero_pair_K(mp.mpc(half, g0 + ee)) + zero_pair_K(mp.mpc(half, g0 - ee))
    F = A - B_rem
    l = lam(F, G)[0]
    print(f"eta={e:>22}  lam_min = {mp.nstr(l,12)}")
print(f"reference lam_min(K_T200,G) = {mp.nstr(lam(K200,G)[0],12)}  (F=0 exactly at eta*)")

print("\n=== (c) baseline scan: delta=0 baseline vs which adjacent pair is removed ===", flush=True)
rows = []
for k in range(len(gam) - 1):
    if gam[k + 1] > 200:
        break
    a, b = gam[k], gam[k + 1]
    m = (a + b) / 2
    Br = zero_pair_K(mp.mpc(half, a)) + zero_pair_K(mp.mpc(half, b))
    A0 = A_analytic(mp.mpf(0), m)
    l = lam(A0 - Br, G)[0]
    rows.append((float(b - a), k, float(l)))
rows.sort()
print(f"{'gap':>10} {'k':>4} {'baseline lam_min(delta=0)':>28}")
for r in rows[:5]:
    print(f"{r[0]:10.5f} {r[1]:4d} {r[2]:28.6e}")
print("  ... largest gaps:")
for r in rows[-3:]:
    print(f"{r[0]:10.5f} {r[1]:4d} {r[2]:28.6e}")

print("\n=== (d) noise floor: lam_min shift under |dK| ~ m3's current closure 4.33e-7 ===", flush=True)
random.seed(11)
for scale in ["4.33e-7", "3.34e-8", "1e-9"]:
    sc = mp.mpf(scale)
    shifts = []
    for trial in range(5):
        Ppert = mp.matrix(N, N)
        for i in range(N):
            for j in range(i, N):
                v = sc * mp.mpf(random.uniform(-1, 1))
                Ppert[i, j] = v; Ppert[j, i] = v
        shifts.append(abs(lam(K200 + Ppert, G)[0] - lam(K200, G)[0]))
    print(f"|dK|_max={scale:>10}  median |d lam_min| = {mp.nstr(sorted(shifts)[2],4)}")
