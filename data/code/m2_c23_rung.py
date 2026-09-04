"""machine2 cycle23 -- FINAL DESIGN of the near-cancellation rung, configuration (a=5,b=2).

gamma_a = grid point 5 of gap A (k=0)  = 18.439296721...   [one of m1's nine ordinates]
gamma_b = grid point 2 of gap B (k=2)  = 26.364362216...   [fresh site, unused gap]

Design data only.  Nothing here evaluates lam_min of the composed matrix at nonzero delta.
Outputs: the self-consistent composed launch, its spectrum, the first-order functionals,
the delta_b that cancels the delta_a=0.1 leg, the second-order self and CROSS terms, and
the T=200 truncation budget measured on THIS launch from the 123 zeros 200<gamma<=400.
"""
import json, os, time
from mpmath import mp
from m2_u_instrument import Basis, load_genomes, load_target
from m2_witness_analysis import gram, lam, mat, zero_pair_K, N

mp.dps = 40
half = mp.mpf(1) / 2
gens = load_genomes("s1/M8"); tgt = load_target("s1/M8")
gam = [mp.mpf(g) for g in json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "zeros210.json")))]
up200 = [g for g in gam if g <= 200]
tail = [mp.mpf(g) for g in json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "tailzeros.json")))]
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
g_a = GA1 + (GA2 - GA1) * 5 / mp.mpf(8)
g_b = GB1 + (GB2 - GB1) * 2 / mp.mpf(8)
remA = zero_pair_K(mp.mpc(half, GA1)) + zero_pair_K(mp.mpc(half, GA2))
remB = zero_pair_K(mp.mpc(half, GB1)) + zero_pair_K(mp.mpc(half, GB2))
qA0, qB0 = quad(mp.mpf(0), g_a), quad(mp.mpf(0), g_b)
L = K200 - remA - remB + qA0 + qB0
vals, vecs = eig_full(L, G); v0 = vecs[0]
print("gamma_a = %s" % mp.nstr(g_a, 25))
print("gamma_b = %s" % mp.nstr(g_b, 25))
print("removed on-line ordinates: %s %s %s %s" % (mp.nstr(GA1,20), mp.nstr(GA2,20), mp.nstr(GB1,20), mp.nstr(GB2,20)))
print("composed launch lam_min = %s" % mp.nstr(vals[0], 20))
print("full spectrum: %s" % [mp.nstr(x, 8) for x in vals])
print("spectral gap lam1-lam0 = %s" % mp.nstr(vals[1] - vals[0], 12))

DA = mp.mpf("0.1")
Pa = quad(DA, g_a) - qA0
fa = bil(Pa, v0, v0)
print("\nleg A at delta_a = %s : f_a = %s" % (DA, mp.nstr(fa, 18)))
def gfun(d):
    return bil(quad(d, g_b) - qB0, v0, v0) + fa
lo, hi = mp.mpf("0.01"), mp.mpf("0.3")
glo, ghi = gfun(lo), gfun(hi)
print("bracket: g(%s)=%s  g(%s)=%s" % (lo, mp.nstr(glo,6), hi, mp.nstr(ghi,6)))
for it in range(80):
    mid = (lo + hi) / 2; gm = gfun(mid)
    if (gm > 0) == (glo > 0): lo, glo = mid, gm
    else: hi, ghi = mid, gm
    if hi - lo < mp.mpf("1e-28"): break
d_b = (lo + hi) / 2
Pb = quad(d_b, g_b) - qB0
fb = bil(Pb, v0, v0)
print("delta_b (cancelling) = %s   [%d bisections]" % (mp.nstr(d_b, 25), it))
print("f_b = %s ;  f_a+f_b = %s  (depth %s of |f_a|)" %
      (mp.nstr(fb, 18), mp.nstr(fa + fb, 8), mp.nstr(abs(fa+fb)/abs(fa), 6)))

sa = sb = X = mp.mpf(0)
for k in range(1, N):
    A = bil(Pa, v0, vecs[k]); B_ = bil(Pb, v0, vecs[k]); den = vals[0] - vals[k]
    sa += A*A/den; sb += B_*B_/den; X += 2*A*B_/den
print("\nsecond order: self_a = %s  self_b = %s  CROSS X = %s" %
      (mp.nstr(sa, 12), mp.nstr(sb, 12), mp.nstr(X, 14)))
print("  |X| / |f_a| = %s ;  |X| / |f_a+f_b| = %s" % (mp.nstr(abs(X/fa), 8), mp.nstr(abs(X/(fa+fb)), 8)))
print("  |self_a+self_b| = %s ;  |X|/|self sum| = %s" % (mp.nstr(abs(sa+sb),10), mp.nstr(abs(X/(sa+sb)),8)))

dK = mp.matrix(N, N)
for g in tail:
    dK += zero_pair_K(mp.mpc(half, g))
dmax = max(abs(dK[i,j]) for i in range(N) for j in range(N))
dlam1 = bil(dK, v0, v0)
lam_tail = eig_full(L + dK, G)[0][0]
print("\nT-truncation budget from the 123 zeros 200<gamma<=400 (deg 8 nodes):")
print("  |dK|_max = %s   v0^T dK v0 = %s   exact d lam_min = %s" %
      (mp.nstr(dmax, 8), mp.nstr(dlam1, 8), mp.nstr(lam_tail - vals[0], 8)))
print("  |X| / B_tail = %s" % mp.nstr(abs(X)/abs(lam_tail - vals[0]), 8))

json.dump({"g_a": mp.nstr(g_a,25), "g_b": mp.nstr(g_b,25),
           "removed": [mp.nstr(x,25) for x in (GA1,GA2,GB1,GB2)],
           "delta_a": str(DA), "delta_b": mp.nstr(d_b,25),
           "launch_lam": mp.nstr(vals[0],20), "spectrum": [mp.nstr(x,14) for x in vals],
           "f_a": mp.nstr(fa,18), "f_b": mp.nstr(fb,18), "f_sum": mp.nstr(fa+fb,12),
           "self_a": mp.nstr(sa,14), "self_b": mp.nstr(sb,14), "cross": mp.nstr(X,16),
           "B_tail_dlam": mp.nstr(lam_tail-vals[0],10), "B_tail_dKmax": mp.nstr(dmax,10)},
          open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "rung_design.json"), "w"), indent=1)
print("\ndone %.1fs" % (time.time()-t0))
