"""machine2 cycle23 -- DESIGN SCAN for the composition (two-pair) witness family.

Stage 0: re-certify our instrument against m1's exported U0/U1/G_raw/K_T150/K_T200
         (never restate a carried certification without re-running it).
Stage 1: for each candidate second gap k_b (disjoint from gap A = k=0), build the
         count-matched COMPOSED LAUNCH
             L(k_b) = K_T200 - rem(g_0) - rem(g_1) - rem(g_kb) - rem(g_kb+1)
                              + quad_A(0) + quad_B(0)
         (quad(0) = doubled on-line pair at the gap midpoint), take its near-null
         generalized eigenvector v0, and report the FIRST-ORDER SHIFT COEFFICIENTS
             c_X = [v0^T dS_X(delta) v0] / (v0^T G v0) / delta^2 ,
             dS_X(delta) = quad_X(delta) - quad_X(0).
         A near-cancellation configuration needs sign(c_A) != sign(c_B).
No scored value is produced here: the scored object is lam_min of the COMPOSED ladder.
"""
import json, os, sys, time
from mpmath import mp
from m2_u_instrument import Basis, load_genomes, load_target
from m2_witness_analysis import gram, lam, mat, zero_pair_K, N

mp.dps = 40
half = mp.mpf(1) / 2
gens = load_genomes("s1/M8")
tgt = load_target("s1/M8")
gam = [mp.mpf(g) for g in json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "zeros210.json")))]
up200 = [g for g in gam if g <= 200]
t0 = time.time()
bases = [Basis(g, degree=8) for g in gens]
G = gram()
K200 = mat(tgt["K_T200"])
K150 = mat(tgt["K_T150"])
Graw = mat(tgt["G_raw"])
print(f"# build {time.time()-t0:.1f}s  dps={mp.dps}  zeros<=200: {len(up200)}")

# ---------------- Stage 0: certification ----------------
d0 = max(abs(b.u_real(mp.mpf(0)) - mp.mpf(tgt["U0"][i])) for i, b in enumerate(bases))
d1 = max(abs(b.u_real(mp.mpf(1)) - mp.mpf(tgt["U1"][i])) for i, b in enumerate(bases))
dG = max(abs(G[i, j] - Graw[i, j]) for i in range(N) for j in range(N))
Kus = mp.matrix(N, N)
for g in up200:
    Kus += zero_pair_K(mp.mpc(half, g))
dK = max(abs(Kus[i, j] - K200[i, j]) for i in range(N) for j in range(N))
K150us = mp.matrix(N, N)
for g in [x for x in gam if x <= 150]:
    K150us += zero_pair_K(mp.mpc(half, g))
dK150 = max(abs(K150us[i, j] - K150[i, j]) for i in range(N) for j in range(N))
lam0 = lam(K200, G)[0]
print("CERT  max|u_i(0)-U0| = %s   max|u_i(1)-U1| = %s" % (mp.nstr(d0, 4), mp.nstr(d1, 4)))
print("CERT  max|G_ours-G_raw| = %s" % mp.nstr(dG, 4))
print("CERT  max|K200_ours-K_T200| = %s   max|K150_ours-K_T150| = %s" % (mp.nstr(dK, 4), mp.nstr(dK150, 4)))
print("CERT  lam_min(K_T200,G) = %s   (m1 anchor 1.176119142e-5)" % mp.nstr(lam0, 14))
bracket = max(abs(K200[i, j] - K150[i, j]) for i in range(N) for j in range(N))
print("CERT  T200-T150 entrywise bracket = %s" % mp.nstr(bracket, 6))


def quad(delta, g0):
    """analytic zero-side form of the FE-closed quadruple {1/2 +- delta +- i g0}."""
    p = mp.mpc(half + delta, g0); q = mp.mpc(half - delta, g0)
    up = [b.u(p) for b in bases]; uq = [b.u(q) for b in bases]
    M = mp.matrix(N, N)
    for i in range(N):
        for j in range(N):
            M[i, j] = 2 * mp.re(up[i] * mp.conj(uq[j]) + up[j] * mp.conj(uq[i]))
    return M


def eig_full(F, Gm):
    L = mp.cholesky(Gm); Li = mp.inverse(L)
    B = Li * F * Li.T
    B = (B + B.T) / 2
    E, V = mp.eigsy(B)
    idx = sorted(range(N), key=lambda i: E[i])
    vals = [E[i] for i in idx]
    vecs = [Li.T * mp.matrix([V[r, i] for r in range(N)]) for i in idx]  # generalized eigvecs
    return vals, vecs


def qform(M, v):
    s = mp.mpf(0)
    for i in range(N):
        for j in range(N):
            s += v[i] * M[i, j] * v[j]
    return s


DELTA_REF = mp.mpf("0.05")
KA = 0
gA1, gA2 = up200[KA], up200[KA + 1]
g0A = (gA1 + gA2) / 2
remA = zero_pair_K(mp.mpc(half, gA1)) + zero_pair_K(mp.mpc(half, gA2))
qA0 = quad(mp.mpf(0), g0A)
dSA = quad(DELTA_REF, g0A) - qA0

cands = [int(x) for x in (sys.argv[1].split(",") if len(sys.argv) > 1 else
                          ["2", "4", "6", "8", "10", "14", "18", "24", "30", "40", "50", "60", "70"])]
print("\n# gap A: k=0  gammas %s %s  midpoint %s" % (mp.nstr(gA1, 8), mp.nstr(gA2, 8), mp.nstr(g0A, 10)))
print("%4s %12s %12s %10s %14s %14s %14s %10s" %
      ("k_b", "gB1", "gB2", "gap", "lam0(launch)", "c_A", "c_B", "ratio"))
rows = {}
for kb in cands:
    gB1, gB2 = up200[kb], up200[kb + 1]
    g0B = (gB1 + gB2) / 2
    remB = zero_pair_K(mp.mpc(half, gB1)) + zero_pair_K(mp.mpc(half, gB2))
    qB0 = quad(mp.mpf(0), g0B)
    L = K200 - remA - remB + qA0 + qB0
    vals, vecs = eig_full(L, G)
    v0 = vecs[0]
    nrm = qform(G, v0)
    dSB = quad(DELTA_REF, g0B) - qB0
    cA = qform(dSA, v0) / nrm / DELTA_REF ** 2
    cB = qform(dSB, v0) / nrm / DELTA_REF ** 2
    ratio = -cA / cB if cB != 0 else mp.inf
    rows[kb] = {"gB1": mp.nstr(gB1, 20), "gB2": mp.nstr(gB2, 20), "g0B": mp.nstr(g0B, 20),
                "lam_launch": mp.nstr(vals[0], 16), "lam1": mp.nstr(vals[1], 12),
                "cA": mp.nstr(cA, 12), "cB": mp.nstr(cB, 12), "ratio": mp.nstr(ratio, 10)}
    print("%4d %12s %12s %10s %14s %14s %14s %10s" %
          (kb, mp.nstr(gB1, 7), mp.nstr(gB2, 7), mp.nstr(gB2 - gB1, 5),
           mp.nstr(vals[0], 8), mp.nstr(cA, 7), mp.nstr(cB, 7), mp.nstr(ratio, 6)), flush=True)

json.dump({"cert": {"u0": mp.nstr(d0, 6), "u1": mp.nstr(d1, 6), "G": mp.nstr(dG, 6),
                    "K200": mp.nstr(dK, 6), "K150": mp.nstr(dK150, 6),
                    "lam_K200": mp.nstr(lam0, 18), "bracket": mp.nstr(bracket, 8)},
           "delta_ref": str(DELTA_REF), "gA1": mp.nstr(gA1, 20), "gA2": mp.nstr(gA2, 20),
           "g0A": mp.nstr(g0A, 20), "scan": rows},
          open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "design_scan.json"), "w"), indent=1)
print("\ndone %.1fs" % (time.time() - t0))
