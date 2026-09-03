from mpmath import mp, mpf, mpc, pi as mp_pi, sqrt as mp_sqrt, gamma as mp_gamma, zeta, besselk, findroot
import time

mp.dps = 35

def zeta2_adaptive(s, D, zcut=160, kshell_reltol=mpf('1e-42'), kmax=100000, mmax=100000):
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

def zeta2_real(sigma, D):
    return zeta2_adaptive(mpc(sigma, 0), D).real

D_test = mpf('0.1416')
guess = mpf('0.53')  # rough interpolation between my table's 0.1415 (0.5248) and 0.1417 (0.5094)
t0=time.time()
root = findroot(lambda s: zeta2_real(s, D_test), guess)
gap = root - (1-root)
print(f"D={D_test}: rho_+={root}")
print(f"measured gap = {float(gap):.8f}")
print(f"predicted gap (Mac's zero-param law) = 0.03745116")
print(f"rel error = {abs(float(gap)-0.03745116)/0.03745116:.3e}")
print(f"[{time.time()-t0:.1f}s]")
