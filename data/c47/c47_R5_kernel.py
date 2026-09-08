#!/usr/bin/env python3
"""R5 -- kernel-level comparison of m3's odd basis closed forms against OURS.

R5a : m3.basis_odd.g_odd_closed(j,k,t,L)  vs  our c46_parity.g_matrix_at_parity(...)[a][b]
      at random (j,k,t), t in [0,L]. Pointwise equality at the KERNEL is a stronger statement
      than eigenvalue agreement, and it localises where a common-mode error could still live.
R5b : is g_jk(t) actually EVEN in t for j != k?  m3's code folds t -> |t| "using evenness".
      Answer measured against DIRECT QUADRATURE of the defining integral, not against either
      closed form -- otherwise the fold is being tested by a function that already assumes it.
R5c : does either assembly ever evaluate g at t < 0?  (read off the code, reported as a fact
      about the code, not inferred from R5b.)
"""
import sys, os, random
sys.path.insert(0, "/workspace/rh/c47")                       # m3's build
sys.path.insert(0, "/workspace/rh/c47/mine/data/c46")         # ours
import mpmath as mp
mp.mp.dps = 60

import basis_odd as m3
import c46_parity as ours

x = 13
L = mp.log(mp.mpf(x))
NMAX = 12
om, nr, idx = ours.make_basis_parity(NMAX, L, "odd")

print("L = log(%d) = %s" % (x, mp.nstr(L, 25)))
print("dps =", mp.mp.dps)

# ---------------- R5a
random.seed(4747)
worst = mp.mpf(0); worst_at = None
tested = 0
for _ in range(40):
    t = mp.mpf(random.uniform(0, float(L)))
    G = ours.g_matrix_at_parity(t, L, om, nr, idx, "odd")
    for _ in range(6):
        a = random.randrange(NMAX); b = random.randrange(NMAX)
        j, k = idx[a], idx[b]
        theirs = m3.g_odd_closed(j, k, t, L)
        mine = G[a][b]
        rel = abs(theirs - mine) / max(abs(mine), mp.mpf('1e-80'))
        tested += 1
        if rel > worst:
            worst, worst_at = rel, (j, k, mp.nstr(t, 12))
print("\nR5a  pointwise g_odd: %d comparisons, worst RELATIVE diff = %s at (j,k,t)=%s"
      % (tested, mp.nstr(worst, 6), worst_at))

# also the t=0 orthonormality corner and t exactly at a prime-power log
print("R5a  t = log 2, log 3, ... (the points the prime sum actually uses):")
for n in [2, 3, 4, 5, 7, 8, 9, 11, 13]:
    t = mp.log(mp.mpf(n))
    if t >= L: continue
    G = ours.g_matrix_at_parity(t, L, om, nr, idx, "odd")
    m = mp.mpf(0)
    for a in range(NMAX):
        for b in range(NMAX):
            d = abs(m3.g_odd_closed(idx[a], idx[b], t, L) - G[a][b])
            m = max(m, d)
    print("   n=%2d t=%s  max ABS diff over 12x12 block = %s" % (n, mp.nstr(t, 10), mp.nstr(m, 6)))

# ---------------- R5b : evenness of g_jk in t, judged by direct quadrature
print("\nR5b  is g_jk(t) even in t?  (direct quadrature of the defining integral, no closed form)")
def g_direct(j, k, t, L):
    lo = max(-L/2, -L/2 - t); hi = min(L/2, L/2 - t)
    if lo >= hi: return mp.mpf(0)
    f = lambda s: (mp.sqrt(2/L)*mp.sin(2*mp.pi*j/L*s)) * (mp.sqrt(2/L)*mp.sin(2*mp.pi*k/L*(s+t)))
    return mp.quad(f, [lo, hi])

for (j, k) in [(1, 2), (1, 3), (2, 5), (3, 4)]:
    t = L/3
    gp, gm = g_direct(j, k, t, L), g_direct(j, k, -t, L)
    print("   j=%d k=%d t=L/3: g(+t)=%s g(-t)=%s  |g(+t)-g(-t)|=%s   g(-t) vs g_kj(+t): %s"
          % (j, k, mp.nstr(gp, 12), mp.nstr(gm, 12), mp.nstr(abs(gp-gm), 6),
             mp.nstr(abs(gm - g_direct(k, j, t, L)), 6)))

# and does m3's closed form agree with direct quadrature at NEGATIVE t (what their fold returns)?
print("R5b  m3 closed form at t<0 vs direct quadrature at t<0:")
for (j, k) in [(1, 2), (2, 5)]:
    t = -L/3
    print("   j=%d k=%d: closed(|t| fold)=%s  direct=%s  diff=%s"
          % (j, k, mp.nstr(m3.g_odd_closed(j, k, t, L), 12), mp.nstr(g_direct(j, k, t, L), 12),
             mp.nstr(abs(m3.g_odd_closed(j, k, t, L) - g_direct(j, k, t, L)), 6)))

# ---------------- R5c : do the assemblies ever call g at t<0 ?
print("\nR5c  code fact (read, not inferred):")
print("   ours  : Gauss-Legendre nodes on [0,L] and t=log n for prime powers n<=x  -> t >= 0 always")
print("   m3    : mp.quad over [0,L] and t=log n for n<=x                          -> t >= 0 always")
