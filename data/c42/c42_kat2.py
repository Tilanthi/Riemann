#!/usr/bin/env python3
"""KAT-2: the closed-form basis correlation g_{jk}(t) vs direct numerical quadrature,
   plus KAT-3: F(r) via the sin(rL/2)*G(r) factorisation vs direct quadrature of INT f e^{irt}."""
from mpmath import mp, mpf, log, cos, sin, quad, pi, sqrt
import random
from c42_connes_x import make_basis, g_entry, g_matrix_at, make_G

mp.dps = 40
N, x = 12, 13
L = log(mpf(x))
om, nr = make_basis(N, L)

def phi(j, t):
    return nr[j] * cos(om[j] * t)

random.seed(7)
worst = mpf(0)
print("KAT-2  closed form vs quadrature, x=%s N=%d dps=%d" % (x, N, mp.dps))
for trial in range(14):
    j = random.randint(0, N); k = random.randint(0, N)
    t = mpf(random.random()) * L
    cf = g_entry(j, k, t, N, L, om, nr)
    nu = quad(lambda s: phi(j, s) * phi(k, s + t), [-L/2, L/2 - t])
    d = abs(cf - nu)
    worst = max(worst, d)
    if trial < 4:
        print("  j=%3d k=%3d t=%s : closed=%s quad=%s |d|=%s"
              % (j, k, mp.nstr(t,8), mp.nstr(cf,15), mp.nstr(nu,15), mp.nstr(d,3)))
print("  worst |closed-quad| over 14 random (j,k,t) = %s" % mp.nstr(worst, 5))

# orthonormality at t=0
G0 = g_matrix_at(mpf(0), N, L, om, nr)
err = max(abs(G0[j][k] - (1 if j == k else 0)) for j in range(N+1) for k in range(N+1))
print("  max |g_{jk}(0) - delta_{jk}| = %s   (orthonormality)" % mp.nstr(err, 5))

# matrix form vs entry form
Gt = g_matrix_at(L/3, N, L, om, nr)
err2 = max(abs(Gt[j][k] - g_entry(j, k, L/3, N, L, om, nr)) for j in range(N+1) for k in range(N+1))
print("  max |g_matrix_at - g_entry| at t=L/3 = %s" % mp.nstr(err2, 5))

# KAT-3: Mellin transform factorisation
v = mp.matrix([mpf(random.random()) - mpf("0.5") for _ in range(N+1)])
Gf, dGf = make_G(v, om, nr, L, N)
print("KAT-3  F(r) = sin(rL/2) G(r) vs direct quadrature")
worst3 = mpf(0)
for r in (mpf("3.7"), mpf("14.134725"), mpf("40.1")):
    fac = sin(r*L/2) * Gf(r)
    dq = quad(lambda t: sum(v[j]*phi(j,t) for j in range(N+1)) * cos(r*t), [-L/2, 0, L/2])
    worst3 = max(worst3, abs(fac-dq))
    print("  r=%s  fact=%s quad=%s |d|=%s" % (mp.nstr(r,8), mp.nstr(fac,15), mp.nstr(dq,15), mp.nstr(abs(fac-dq),3)))
# derivative check
h = mpf(10)**(-15)
r0 = mpf("14.1")
print("  dG check: analytic=%s  fd=%s" % (mp.nstr(dGf(r0),12), mp.nstr((Gf(r0+h)-Gf(r0-h))/(2*h),12)))
