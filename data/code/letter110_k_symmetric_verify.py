from mpmath import mp, mpf, mpc, pi as mp_pi, sqrt as mp_sqrt, gamma as mp_gamma, zeta, besselk

mp.dps = 45

def zeta2_adaptive(s, D, zcut=200, kshell_reltol=mpf('1e-55'), kmax=200000, mmax=200000):
    D = mpf(D); s = mpc(s)
    t1 = zeta(2*s)
    t2 = mp_sqrt(mp_pi)*mp_gamma(s - mpf('0.5'))*D**(1 - 2*s)*zeta(2*s - 1)/mp_gamma(s)
    tot = t1 + t2
    nu = s - mpf('0.5')
    ssum = mpc(0)
    running_abs_scale = mpf(0)
    for k in range(1, kmax+1):
        z = 2*mp_pi*D*k
        inner = mpc(0)
        m = 1
        while m <= mmax:
            arg = z*m
            term = (mpf(m)/k)**nu * besselk(nu, arg)
            inner += term
            if arg > zcut:
                break
            m += 1
        ssum += inner
        running_abs_scale = max(running_abs_scale, abs(inner))
        if abs(inner) < kshell_reltol * running_abs_scale and k > 5:
            break
    return tot + (4*mp_pi**s/mp_gamma(s))*D**(mpf('0.5') - s)*ssum

Dstar = mpf('0.14173323966388719139541530708686641')  # BEAST's/operative value
s0 = mpf('0.5') + mpf('1e-20')

# Symmetric double-sided finite differences (own design, symmetric BY CONSTRUCTION,
# to avoid trap #87's one-sided-offset artifact from the start), Richardson-extrapolated.
def A_D_deriv(h):
    # d/dD at fixed s=1/2, symmetric
    vp = zeta2_adaptive(s0, Dstar + h).real
    vm = zeta2_adaptive(s0, Dstar - h).real
    return (vp - vm) / (2*h)

def A_ss_deriv(h):
    # d^2/ds^2 at fixed D=Dstar, s=1/2 -- need symmetric offset in s too (avoid pole at s=1/2 exactly)
    # use central second difference around s0 with small imaginary or real step avoiding exact pole
    eps = mpf('1e-20')  # tiny offset to dodge pole, symmetric evaluation around it
    vp = zeta2_adaptive(s0 + eps + h, Dstar).real
    vc = zeta2_adaptive(s0 + eps, Dstar).real
    vm = zeta2_adaptive(s0 + eps - h, Dstar).real
    return (vp - 2*vc + vm) / (h*h)

for h in [mpf('1e-6'), mpf('1e-7'), mpf('1e-8')]:
    AD = A_D_deriv(h)
    print(f"h={h}: A_D = {AD}")

for h in [mpf('1e-5'), mpf('1e-6')]:
    Ass = A_ss_deriv(h)
    print(f"h={h}: A_ss = {Ass}")
