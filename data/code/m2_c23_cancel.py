"""machine2 cycle23 -- locate the near-cancellation point in the COMPOSED launch's own
first-order functional, and size the second-order cross-term against the two budgets.

Design data only.  Everything here is computed from the composed LAUNCH matrix
(both quadruples at delta=0, i.e. doubled ON-LINE pairs => PSD, no witness content) and
from the single-pair perturbations P_X(delta) = quad_X(delta) - quad_X(0).
The scored object -- lam_min of the composed matrix at (delta_a, delta_b) != 0 -- is NOT
evaluated in this script.
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
    vals = [E[i] for i in idx]
    vecs = [Li.T * mp.matrix([V[r, i] for r in range(N)]) for i in idx]  # G-orthonormal
    return vals, vecs


def bil(M, v, w):
    s = mp.mpf(0)
    for i in range(N):
        for j in range(N):
            s += v[i] * M[i, j] * w[j]
    return s


GA1, GA2 = up200[0], up200[1]
GB1, GB2 = up200[2], up200[3]
g_a = (GA1 + GA2) / 2                       # 17.578382390253124392
g_b = GB1 + (GB2 - GB1) * 6 / mp.mpf(8)     # 29.071371489431057099
remA = zero_pair_K(mp.mpc(half, GA1)) + zero_pair_K(mp.mpc(half, GA2))
remB = zero_pair_K(mp.mpc(half, GB1)) + zero_pair_K(mp.mpc(half, GB2))
qA0, qB0 = quad(mp.mpf(0), g_a), quad(mp.mpf(0), g_b)
LAUNCH = K200 - remA - remB + qA0 + qB0
vals, vecs = eig_full(LAUNCH, G)
v0 = vecs[0]
print("# composed launch  gamma_a=%s  gamma_b=%s" % (mp.nstr(g_a, 20), mp.nstr(g_b, 20)))
print("# lam(launch) = %s   spectral gap lam1-lam0 = %s" %
      (mp.nstr(vals[0], 18), mp.nstr(vals[1] - vals[0], 12)))
print("# G-orthonormality check v0^T G v0 = %s" % mp.nstr(bil(G, v0, v0), 8))


def f1(P):
    return bil(P, v0, v0)


def second(Pa, Pb):
    """second-order PT: self terms and the CROSS term, over the full spectrum."""
    selfa = selfb = cross = mp.mpf(0)
    for k in range(1, N):
        vk = vecs[k]
        a = bil(Pa, v0, vk); b = bil(Pb, v0, vk)
        den = vals[0] - vals[k]
        selfa += a * a / den
        selfb += b * b / den
        cross += 2 * a * b / den
    return selfa, selfb, cross


DB = mp.mpf("0.2")
Pb = quad(DB, g_b) - qB0
target = -f1(Pb)
print("# leg B fixed at delta_b = %s :  v0^T P_b v0 = %s" % (DB, mp.nstr(f1(Pb), 14)))
print("# need v0^T P_a v0 = %s" % mp.nstr(target, 14))

# bracket + bisection on delta_a
lo, hi = mp.mpf("0.001"), mp.mpf("0.1")
def g(d):
    return f1(quad(d, g_a) - qA0) - target
glo, ghi = g(lo), g(hi)
print("# bracket g(%s)=%s  g(%s)=%s" % (lo, mp.nstr(glo, 8), hi, mp.nstr(ghi, 8)))
for it in range(60):
    mid = (lo + hi) / 2
    gm = g(mid)
    if (gm > 0) == (glo > 0):
        lo, glo = mid, gm
    else:
        hi, ghi = mid, gm
    if hi - lo < mp.mpf("1e-25"):
        break
d_a = (lo + hi) / 2
Pa = quad(d_a, g_a) - qA0
fa, fb = f1(Pa), f1(Pb)
sa, sb, X = second(Pa, Pb)
print("\nNEAR-CANCELLATION POINT")
print("  delta_a = %s   (iterations %d)" % (mp.nstr(d_a, 25), it))
print("  delta_b = %s" % DB)
print("  first-order  v0^T P_a v0 = %s" % mp.nstr(fa, 16))
print("  first-order  v0^T P_b v0 = %s" % mp.nstr(fb, 16))
print("  first-order SUM          = %s   (depth %s of |P_a| leg)" %
      (mp.nstr(fa + fb, 8), mp.nstr(abs(fa + fb) / abs(fa), 6)))
print("  second-order self  a = %s   b = %s" % (mp.nstr(sa, 10), mp.nstr(sb, 10)))
print("  second-order CROSS X = %s" % mp.nstr(X, 12))
print("  |X| / |first-order sum| = %s" % mp.nstr(abs(X) / abs(fa + fb), 8))
print("  |X| / B_tail(1.43e-10)  = %s" % mp.nstr(abs(X) / mp.mpf("1.43e-10"), 8))

# same quantities at a same-sign control rung (both quadruples at gap midpoints, delta=0.1)
g_b0 = (GB1 + GB2) / 2
qB00 = quad(mp.mpf(0), g_b0)
L0 = K200 - remA - remB + qA0 + qB00
v_, vecs_ = eig_full(L0, G)
v0_ = vecs_[0]
Pa0 = quad(mp.mpf("0.1"), g_a) - qA0
Pb0 = quad(mp.mpf("0.1"), g_b0) - qB00
fa0 = bil(Pa0, v0_, v0_); fb0 = bil(Pb0, v0_, v0_)
sa0 = sb0 = X0 = mp.mpf(0)
for k in range(1, N):
    a = bil(Pa0, v0_, vecs_[k]); b = bil(Pb0, v0_, vecs_[k]); den = v_[0] - v_[k]
    sa0 += a * a / den; sb0 += b * b / den; X0 += 2 * a * b / den
print("\nSAME-SIGN CONTROL RUNG (both at gap midpoints, delta_a=delta_b=0.1)")
print("  gamma_b0 = %s   lam(launch) = %s  gap = %s" %
      (mp.nstr(g_b0, 20), mp.nstr(v_[0], 14), mp.nstr(v_[1] - v_[0], 10)))
print("  first order a=%s  b=%s  sum=%s" % (mp.nstr(fa0, 12), mp.nstr(fb0, 12), mp.nstr(fa0 + fb0, 12)))
print("  second-order self a=%s b=%s  CROSS=%s" % (mp.nstr(sa0, 10), mp.nstr(sb0, 10), mp.nstr(X0, 10)))
print("  |X|/|sum| = %s" % mp.nstr(abs(X0) / abs(fa0 + fb0), 8))

json.dump({"g_a": mp.nstr(g_a, 25), "g_b": mp.nstr(g_b, 25), "delta_b": str(DB),
           "delta_a": mp.nstr(d_a, 25),
           "launch_lam": mp.nstr(vals[0], 20), "spec_gap": mp.nstr(vals[1] - vals[0], 14),
           "f1_a": mp.nstr(fa, 18), "f1_b": mp.nstr(fb, 18), "f1_sum": mp.nstr(fa + fb, 12),
           "second_self_a": mp.nstr(sa, 12), "second_self_b": mp.nstr(sb, 12),
           "cross": mp.nstr(X, 14),
           "control": {"g_b": mp.nstr(g_b0, 25), "launch_lam": mp.nstr(v_[0], 18),
                       "f1_a": mp.nstr(fa0, 14), "f1_b": mp.nstr(fb0, 14),
                       "cross": mp.nstr(X0, 12), "self_a": mp.nstr(sa0, 12), "self_b": mp.nstr(sb0, 12)}},
          open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "cancel_point.json"), "w"), indent=1)
print("\ndone %.1fs" % (time.time() - t0))
