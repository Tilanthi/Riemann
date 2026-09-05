"""machine2 cycle25 -- DESIGN SCAN for a SECOND, INDEPENDENT near-cancellation site.

Cycle 23 named the family (composition of two count-matched FE-closed off-line quadruples with an
EXACTLY-cancelling first-order point) and scored one site:
    gap A = k=0 (14.1347/21.0220), gamma_a = 18.43929670..., delta_a = 0.1
    gap B = k=2 (25.0109/30.4249), gamma_b = 26.36436221..., delta_b = 0.072086352 (cancelling)
Its headline negative -- "the exactly-cancelling point bought nothing over an ordinary opposing
configuration" (additivity defect 9.37% vs 7.13%) -- rests on n = 1 SITE.

This scan builds the second site.  Gap B is moved to a gap NEVER used at nonzero delta (k=4,
32.9350/37.5861); gap A stays k=0 so the leg-A coupling is in the same regime and the comparison is
against a measured baseline rather than against nothing.

SELECTION RULE (cycle-23 standing correction, and the brief's condition 4): the rung is selected by
the sign of the FIRST-ORDER FUNCTIONAL AT THE SELF-CONSISTENT COMPOSED LAUNCH,
    f_X = v0^T [quad_X(delta,g_X) - quad_X(0,g_X)] v0 / (v0^T G v0),
NEVER by the sign of the single-pair lam_min shift (17 of 18 single-pair sites disagree with the
composed-launch functional).  A cancellation site needs sign(f_a) != sign(f_b).

DESIGN DATA ONLY.  Nothing here evaluates lam_min of a composed matrix at nonzero delta on both legs;
the scored object (the ladder's exact lam_min and its additivity defect) is produced by the runner,
after the prediction is committed.
"""
import json, os, sys, time
from mpmath import mp
from m2_u_instrument import Basis, load_genomes, load_target
from m2_witness_analysis import gram, lam, mat, zero_pair_K, N

mp.dps = 40
HERE = os.path.dirname(os.path.abspath(__file__))
half = mp.mpf(1) / 2
gens = load_genomes("s1/M8"); tgt = load_target("s1/M8")
gam = [mp.mpf(g) for g in json.load(open(os.path.join(HERE, "zeros210.json")))]
up200 = [g for g in gam if g <= 200]
t0 = time.time()
bases = [Basis(g, degree=8) for g in gens]
G = gram(); K200 = mat(tgt["K_T200"]); K150 = mat(tgt["K_T150"]); Graw = mat(tgt["G_raw"])

# ---------------- Stage 0: re-certify the instrument (never restate a carried certification) -------
d0 = max(abs(b.u_real(mp.mpf(0)) - mp.mpf(tgt["U0"][i])) for i, b in enumerate(bases))
d1 = max(abs(b.u_real(mp.mpf(1)) - mp.mpf(tgt["U1"][i])) for i, b in enumerate(bases))
dG = max(abs(G[i, j] - Graw[i, j]) for i in range(N) for j in range(N))
Kus = mp.matrix(N, N)
for g in up200:
    Kus += zero_pair_K(mp.mpc(half, g))
dK = max(abs(Kus[i, j] - K200[i, j]) for i in range(N) for j in range(N))
lam0 = lam(K200, G)[0]
print("CERT max|u(0)-U0| %s  max|u(1)-U1| %s  max|G-G_raw| %s  max|K200-K_T200| %s"
      % (mp.nstr(d0, 4), mp.nstr(d1, 4), mp.nstr(dG, 4), mp.nstr(dK, 4)))
print("CERT lam_min(K_T200,G) = %s   (m1 anchor 1.176119142e-5)" % mp.nstr(lam0, 14))


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


def bil(M, v, w):
    s = mp.mpf(0)
    for i in range(N):
        for j in range(N):
            s += v[i] * M[i, j] * w[j]
    return s


KA = int(sys.argv[1]) if len(sys.argv) > 1 else 0
KB = int(sys.argv[2]) if len(sys.argv) > 2 else 4
GA1, GA2 = up200[KA], up200[KA + 1]
GB1, GB2 = up200[KB], up200[KB + 1]
assert len({GA1, GA2, GB1, GB2}) == 4, "legs must remove disjoint ordinates"
remA = zero_pair_K(mp.mpc(half, GA1)) + zero_pair_K(mp.mpc(half, GA2))
remB = zero_pair_K(mp.mpc(half, GB1)) + zero_pair_K(mp.mpc(half, GB2))
D = mp.mpf("0.1")
NA = NB = 9
print("\n# gap A k=%d [%s, %s]   gap B k=%d [%s, %s]"
      % (KA, mp.nstr(GA1, 12), mp.nstr(GA2, 12), KB, mp.nstr(GB1, 12), mp.nstr(GB2, 12)))
qA0c, qAdc, qB0c, qBdc = {}, {}, {}, {}
for m in range(1, NA):
    g = GA1 + (GA2 - GA1) * m / mp.mpf(NA - 1)
    qA0c[m] = quad(mp.mpf(0), g); qAdc[m] = quad(D, g)
for m in range(1, NB):
    g = GB1 + (GB2 - GB1) * m / mp.mpf(NB - 1)
    qB0c[m] = quad(mp.mpf(0), g); qBdc[m] = quad(D, g)
print("# quadruple cache %.1fs ; entry = (sign f_a)(sign f_b) at the self-consistent composed launch"
      % (time.time() - t0))

res, opp = {}, []
print("%3s " % "a\\b" + "".join("%14d" % m for m in range(1, NB)))
for ma in range(1, NA):
    line = "%3d " % ma
    for mb in range(1, NB):
        L = K200 - remA - remB + qA0c[ma] + qB0c[mb]
        vals, vecs = eig_full(L, G)
        v0 = vecs[0]; nrm = bil(G, v0, v0)
        fa = bil(qAdc[ma] - qA0c[ma], v0, v0) / nrm
        fb = bil(qBdc[mb] - qB0c[mb], v0, v0) / nrm
        tag = ("+" if fa > 0 else "-") + ("+" if fb > 0 else "-")
        if (fa > 0) != (fb > 0):
            opp.append((ma, mb, mp.nstr(fa, 8), mp.nstr(fb, 8), mp.nstr(abs(fa / fb), 6)))
        res["%d,%d" % (ma, mb)] = {"lam0": mp.nstr(vals[0], 14), "gap": mp.nstr(vals[1] - vals[0], 8),
                                   "f_a": mp.nstr(fa, 12), "f_b": mp.nstr(fb, 12), "tag": tag}
        line += "%14s" % (tag + mp.nstr(abs(fa / fb), 3))
    print(line, flush=True)

print("\n# OPPOSITE-SIGN (cancellation-admitting) configurations: %d of %d" % (len(opp), (NA - 1) * (NB - 1)))
for ma, mb, fa, fb, r in opp:
    print("   a=%d b=%d  f_a=%s  f_b=%s  |f_a/f_b|=%s" % (ma, mb, fa, fb, r))
json.dump({"cert": {"u0": mp.nstr(d0, 6), "u1": mp.nstr(d1, 6), "G": mp.nstr(dG, 6),
                    "K200": mp.nstr(dK, 6), "lam_K200": mp.nstr(lam0, 18)},
           "kA": KA, "kB": KB, "delta_probe": str(D),
           "gapA": [mp.nstr(GA1, 25), mp.nstr(GA2, 25)], "gapB": [mp.nstr(GB1, 25), mp.nstr(GB2, 25)],
           "grid": res, "opposite": opp},
          open(os.path.join(HERE, "c25_design_scan_k%d_%d.json" % (KA, KB)), "w"), indent=1)
print("done %.1fs" % (time.time() - t0))
