from mpmath import mp, mpf, mpc, pi as mp_pi, sqrt as mp_sqrt, gamma as mp_gamma, zeta, besselk

mp.dps = 30

def zeta2_A(s, D):
    D = mpf(D); s = mpc(s)
    t1 = zeta(2*s)
    t2 = mp_sqrt(mp_pi)*mp_gamma(s - mpf('0.5'))*D**(1 - 2*s)*zeta(2*s - 1)/mp_gamma(s)
    tot = t1 + t2
    nu = s - mpf('0.5')
    ssum = mpf(0)
    for k in range(1, 60):
        z = 2*mp_pi*D*k
        inner = mpf(0)
        for m in range(1, 60):
            inner += (mpf(m)/k)**nu * besselk(nu, z*m)
        term = inner
        ssum += term
        if abs(term) < mpf('1e-40') and k > 5:
            break
    return tot + (4*mp_pi**s/mp_gamma(s))*D**(mpf('0.5') - s)*ssum

def dirichlet_beta(s):
    s = mpc(s)
    return mpf(4)**(-s) * (zeta(s, mpf('0.25')) - zeta(s, mpf('0.75')))

if __name__ == '__main__':
    for s0 in [mpc(3,0), mpc(3,5), mpc(4,20)]:
        zA = zeta2_A(s0, '1.0')
        beta_val = dirichlet_beta(s0)
        gt = 2*zeta(s0)*beta_val
        print(f"s={s0}: A={complex(zA):.10e}  ground_truth(2*zeta*beta)={complex(gt):.10e}  reldiff={float(abs(zA-gt)/abs(gt)):.3e}")
