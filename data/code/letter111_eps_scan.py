from mpmath import mp, mpf, mpc, pi as mp_pi, sqrt as mp_sqrt, gamma as mp_gamma, zeta, besselk, findroot

def zeta2_adaptive(s, D, zcut=220, kshell_reltol=mpf('1e-65'), kmax=200000, mmax=200000):
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

mp.dps = 50
beast_val = mpf('0.14173323966388719139541530708686641')
mac_val   = mpf('0.14173323966388719139541568508424243')
Dstar_guess = mpf('0.141733239663887191395415')

for eps_exp in [-8, -10, -12, -14, -16, -18]:
    EPS = mpf(10)**eps_exp
    def f_half(D, EPS=EPS):
        D = mpf(D)
        vplus = zeta2_adaptive(mpf('0.5') + EPS, D).real
        vminus = zeta2_adaptive(mpf('0.5') - EPS, D).real
        return (vplus + vminus) / 2
    Dstar = findroot(f_half, Dstar_guess, tol=mpf('1e-42'))
    diff_beast = Dstar - beast_val
    diff_mac = Dstar - mac_val
    print(f"eps=1e{eps_exp}: diff_beast={float(diff_beast):.4e}  diff_mac={float(diff_mac):.4e}")
