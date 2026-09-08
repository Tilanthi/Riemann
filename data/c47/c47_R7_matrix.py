#!/usr/bin/env python3
"""R7 (ADDED arm, addendum 1) -- entrywise comparison of the two ASSEMBLED odd matrices.

m3 : weil_form_odd.build_matrix_odd  -- adaptive mp.quad, O(N) J_sin table, explicit pole term
us : c46_parity.build_matrix_parity  -- fixed-degree Gauss-Legendre over the whole assembly

Different quadrature schemes, so the verdict is an agreement DEPTH, not a boolean.
R8 : count how many times m3's psihat resonance guard (r == +-w_k -> r += 1e-30) fires.
"""
import sys
sys.path.insert(0, "/workspace/rh/c47")
sys.path.insert(0, "/workspace/rh/c47/mine/data/c46")
import mpmath as mp

import basis_odd as m3b
# ---- R8 instrumentation: wrap their psihat and count guard hits
_guard_hits = {"n": 0, "calls": 0}
_orig_psihat = m3b.psihat
def _counting_psihat(k, r, L):
    _guard_hits["calls"] += 1
    if r == m3b.w(k, L) or r == -m3b.w(k, L):
        _guard_hits["n"] += 1
    return _orig_psihat(k, r, L)
m3b.psihat = _counting_psihat

import weil_form_odd as m3w
m3w.psihat = _counting_psihat
import c46_parity as ours

X = 13
N = int(sys.argv[1]) if len(sys.argv) > 1 else 12
DPS = int(sys.argv[2]) if len(sys.argv) > 2 else 60
GL = int(sys.argv[3]) if len(sys.argv) > 3 else 9

mp.mp.dps = DPS
L = mp.log(mp.mpf(X))
print("R7  x=%d N=%d dps=%d  (ours gl_degree=%d, m3 adaptive mp.quad)" % (X, N, DPS, GL))

Mm = m3w.build_matrix_odd(X, N, L, DPS, log=False)
mp.mp.dps = DPS
Mo, Lo, pps = ours.build_matrix_parity(N, X, GL, "odd")
print("   our prime powers:", pps, " m3 prime powers:", m3w.prime_powers_upto(X))
print("   our L =", mp.nstr(Lo, 25), "  m3 L =", mp.nstr(L, 25))

worst_rel = mp.mpf(0); worst_abs = mp.mpf(0); at = None
scale = max(abs(Mo[i][j]) for i in range(N) for j in range(N))
for i in range(N):
    for j in range(N):
        d = abs(Mm[i][j] - Mo[i][j])
        r = d / max(abs(Mo[i][j]), mp.mpf('1e-90'))
        if d > worst_abs:
            worst_abs = d; at = (i + 1, j + 1)
        worst_rel = max(worst_rel, r)
print("   entries compared: %d" % (N * N))
print("   matrix scale max|M_ij| = %s" % mp.nstr(scale, 8))
print("   worst ABSOLUTE diff = %s at (j,k)=%s" % (mp.nstr(worst_abs, 8), at))
print("   worst RELATIVE diff = %s" % mp.nstr(worst_rel, 8))
print("   worst diff / matrix scale = %s" % mp.nstr(worst_abs / scale, 8))

lam_m3, _ = ours.c42.smallest_eigenpair(Mm, iters=16, verbose=False)
lam_us, _ = ours.c42.smallest_eigenpair(Mo, iters=16, verbose=False)
print("   lambda_min from m3 matrix = %s" % mp.nstr(lam_m3, 30))
print("   lambda_min from our matrix= %s" % mp.nstr(lam_us, 30))
print("   relative difference of the two lambda_min = %s"
      % mp.nstr(abs(lam_m3 - lam_us) / abs(lam_us), 6))
print("R8  m3 psihat calls=%d, resonance-guard firings=%d  -> %s"
      % (_guard_hits["calls"], _guard_hits["n"],
         "EMPTY FIRING WORLD in this build" if _guard_hits["n"] == 0 else "GUARD FIRED"))
