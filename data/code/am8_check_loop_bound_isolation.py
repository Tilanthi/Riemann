from mpmath import mp, mpf, mpc, pi as mp_pi, sqrt as mp_sqrt, gamma as mp_gamma, zeta, besselk

mp.dps = 30

def zeta2_A_variable(s, D, KMAX, MMAX):
    """Same as evaluator A but with adjustable loop bounds, to test convergence."""
    D = mpf(D); s = mpc(s)
    t1 = zeta(2*s)
    t2 = mp_sqrt(mp_pi)*mp_gamma(s - mpf('0.5'))*D**(1 - 2*s)*zeta(2*s - 1)/mp_gamma(s)
    tot = t1 + t2
    nu = s - mpf('0.5')
    ssum = mpf(0)
    for k in range(1, KMAX):
        z = 2*mp_pi*D*k
        inner = mpf(0)
        for m in range(1, MMAX):
            inner += (mpf(m)/k)**nu * besselk(nu, z*m)
        term = inner
        ssum += term
        if abs(term) < mpf('1e-40') and k > 5:
            break
    return tot + (4*mp_pi**s/mp_gamma(s))*D**(mpf('0.5') - s)*ssum

D = mpf('0.001')
s = mpc(3, 0)
for KMAX, MMAX in [(60,60), (60,200), (60,1000), (200,1000), (200,3000)]:
    val = zeta2_A_variable(s, D, KMAX, MMAX)
    print(f"KMAX={KMAX:5d} MMAX={MMAX:5d}: zeta2_A = {val}")
