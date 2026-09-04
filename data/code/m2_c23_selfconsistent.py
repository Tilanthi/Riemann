"""machine2 cycle23 -- SELF-CONSISTENT search for a near-cancellation configuration.

For each candidate (gamma_a in gap A grid) x (gamma_b in gap B grid) the COMPOSED LAUNCH
    L = K_T200 - rem_A - rem_B + quad_A(0,g_a) + quad_B(0,g_b)
is rebuilt, its near-null generalized eigenvector v0 recomputed, and BOTH first-order
functionals evaluated at that v0:
    f_X(delta) = v0^T [quad_X(delta,g_X) - quad_X(0,g_X)] v0 / (v0^T G v0)
m1-L148's near-cancellation rung needs sign(f_a) != sign(f_b).  Reported at delta=0.1
for both legs (f scales ~ delta^2, so the SIGN is delta-independent to leading order).
Design data only: no composed lam_min at nonzero delta is evaluated.
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


GA1, GA2 = up200[0], up200[1]
GB1, GB2 = up200[2], up200[3]
remA = zero_pair_K(mp.mpc(half, GA1)) + zero_pair_K(mp.mpc(half, GA2))
remB = zero_pair_K(mp.mpc(half, GB1)) + zero_pair_K(mp.mpc(half, GB2))
D = mp.mpf("0.1")
qA0c, qAdc, qB0c, qBdc = {}, {}, {}, {}
NA, NB = 9, 9
for m in range(NA):
    g = GA1 + (GA2 - GA1) * m / mp.mpf(NA - 1)
    qA0c[m] = quad(mp.mpf(0), g); qAdc[m] = quad(D, g)
for m in range(NB):
    g = GB1 + (GB2 - GB1) * m / mp.mpf(NB - 1)
    qB0c[m] = quad(mp.mpf(0), g); qBdc[m] = quad(D, g)
print("# quadruple cache built %.1fs" % (time.time() - t0))
print("# rows = gamma_a index (gap A), cols = gamma_b index (gap B)")
print("# entry = sign pattern of (f_a, f_b) at delta=0.1 at the SELF-CONSISTENT composed launch")

res = {}
npos = 0
hdr = "%3s " % "a\\b" + "".join("%12d" % m for m in range(NB))
print(hdr)
for ma in range(NA):
    line = "%3d " % ma
    row = []
    for mb in range(NB):
        L = K200 - remA - remB + qA0c[ma] + qB0c[mb]
        vals, vecs = eig_full(L, G)
        v0 = vecs[0]
        fa = bil(qAdc[ma] - qA0c[ma], v0, v0)
        fb = bil(qBdc[mb] - qB0c[mb], v0, v0)
        if fb > 0 or fa > 0:
            npos += 1
        row.append({"lam0": mp.nstr(vals[0], 12), "gap": mp.nstr(vals[1] - vals[0], 8),
                    "fa": mp.nstr(fa, 12), "fb": mp.nstr(fb, 12)})
        tag = ("+" if fa > 0 else "-") + ("+" if fb > 0 else "-")
        line += "%12s" % (tag + " " + mp.nstr(fb, 3))
    res[ma] = row
    print(line, flush=True)
print("\n# configurations with at least one POSITIVE first-order functional: %d of %d" % (npos, NA * NB))
json.dump(res, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "selfconsistent.json"), "w"), indent=1)
print("done %.1fs" % (time.time() - t0))
