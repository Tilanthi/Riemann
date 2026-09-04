"""machine2 cycle23 -- where does the first-order coefficient c(gamma_0) change SIGN?

Design question: m1-L148 offers a "near-cancellation" composition family, which requires
two first-order shifts of OPPOSITE sign.  The midpoint scan (m2_c23_design.py) found
c_B < 0 at every low gap and c_B > 0 only at heights where |c_B| ~ 1e-10..1e-12, i.e.
10^6..10^8 times too small to cancel c_A ~ -7.2e-4 at any delta inside the Taylor range.
So the cancellation, if it exists, must come from the POSITION OF THE INSERTED QUADRUPLE
INSIDE ITS GAP, not from the choice of gap.  This scans that.

c(g0; k) = [v0^T (quad_k(delta,g0) - quad_k(0,g0)) v0] / (v0^T G v0) / delta^2
with v0 the near-null generalized eigenvector of the composed launch (both quadruples at
their gap midpoints).  Also reports the single-pair lam_min at delta=0.1, which
reproduces m1's published nine-ordinate sweep for gap A.
"""
import json, os, sys, time
from mpmath import mp
from m2_u_instrument import Basis, load_genomes, load_target
from m2_witness_analysis import gram, lam, mat, zero_pair_K, N

mp.dps = 40
half = mp.mpf(1) / 2
gens = load_genomes("s1/M8"); tgt = load_target("s1/M8")
gam = [mp.mpf(g) for g in json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "zeros210.json")))]
up200 = [g for g in gam if g <= 200]
t0 = time.time()
bases = [Basis(g, degree=8) for g in gens]
G = gram(); K200 = mat(tgt["K_T200"])
print(f"# build {time.time()-t0:.1f}s")


def quad(delta, g0):
    p = mp.mpc(half + delta, g0); q = mp.mpc(half - delta, g0)
    up = [b.u(p) for b in bases]; uq = [b.u(q) for b in bases]
    M = mp.matrix(N, N)
    for i in range(N):
        for j in range(N):
            M[i, j] = 2 * mp.re(up[i] * mp.conj(uq[j]) + up[j] * mp.conj(uq[i]))
    return M


def eig_full(F, Gm):
    L = mp.cholesky(Gm); Li = mp.inverse(L)
    B = Li * F * Li.T; B = (B + B.T) / 2
    E, V = mp.eigsy(B)
    idx = sorted(range(N), key=lambda i: E[i])
    return [E[i] for i in idx], [Li.T * mp.matrix([V[r, i] for r in range(N)]) for i in idx]


def qform(M, v):
    s = mp.mpf(0)
    for i in range(N):
        for j in range(N):
            s += v[i] * M[i, j] * v[j]
    return s


KA, KB = 0, 2
gA1, gA2 = up200[KA], up200[KA + 1]
gB1, gB2 = up200[KB], up200[KB + 1]
g0A, g0B = (gA1 + gA2) / 2, (gB1 + gB2) / 2
remA = zero_pair_K(mp.mpc(half, gA1)) + zero_pair_K(mp.mpc(half, gA2))
remB = zero_pair_K(mp.mpc(half, gB1)) + zero_pair_K(mp.mpc(half, gB2))
LAUNCH = K200 - remA - remB + quad(mp.mpf(0), g0A) + quad(mp.mpf(0), g0B)
vals, vecs = eig_full(LAUNCH, G)
v0 = vecs[0]; nrm = qform(G, v0)
print("# composed launch (both quadruples at gap midpoints): lam0 = %s  lam1 = %s" %
      (mp.nstr(vals[0], 14), mp.nstr(vals[1], 10)))
print("# spectral gap lam1-lam0 = %s" % mp.nstr(vals[1] - vals[0], 10))

D = mp.mpf("0.05")
out = {}
for tag, (k, g1, g2) in (("A", (KA, gA1, gA2)), ("B", (KB, gB1, gB2))):
    rem = remA if tag == "A" else remB
    print("\n### gap %s  k=%d  [%s, %s]  width %s" %
          (tag, k, mp.nstr(g1, 9), mp.nstr(g2, 9), mp.nstr(g2 - g1, 6)))
    print("%12s %16s %20s %8s" % ("gamma_0", "c(g0)", "lam_min single @0.1", "fires"))
    rows = []
    for m in range(9):
        g0 = g1 + (g2 - g1) * m / mp.mpf(8)
        q0 = quad(mp.mpf(0), g0)
        c = qform(quad(D, g0) - q0, v0) / nrm / D ** 2
        lsingle = lam(K200 - rem + quad(mp.mpf("0.1"), g0), G)[0]
        rows.append({"g0": mp.nstr(g0, 20), "c": mp.nstr(c, 12), "lam_single_0.1": mp.nstr(lsingle, 14)})
        print("%12s %16s %20s %8s" % (mp.nstr(g0, 9), mp.nstr(c, 9), mp.nstr(lsingle, 10),
                                      "YES" if lsingle < 0 else "no"), flush=True)
    out[tag] = rows

json.dump({"launch_lam": [mp.nstr(x, 16) for x in vals], "delta_ref": str(D), "sweeps": out},
          open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "sweep_c.json"), "w"), indent=1)
print("\ndone %.1fs" % (time.time() - t0))
