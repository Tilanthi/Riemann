from mpmath import mp, mpf, mpc, pi as mp_pi, sqrt as mp_sqrt, gamma as mp_gamma, zeta, besselk
import time

mp.dps = 20   # lower precision, just need to see the trend quickly

def zeta2_A_variable(s, D, KMAX, MMAX):
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
        if abs(term) < mpf('1e-25') and k > 5:
            break
    return tot + (4*mp_pi**s/mp_gamma(s))*D**(mpf('0.5') - s)*ssum

Ds = ['0.02', '0.01', '0.005', '0.002', '0.001']
sig = mpf('1.05')
t = 5
print(f"{'D':>8} {'orig(60,60)':>16} {'relaxed(150,600)':>18} {'rel_error':>12}")
for D in Ds:
    s = mpc(sig, t)
    t0=time.time()
    v_orig = zeta2_A_variable(s, D, 60, 60)
    v_relax = zeta2_A_variable(s, D, 150, 600)
    dt = time.time()-t0
    relerr = abs(v_orig - v_relax) / abs(v_relax) if abs(v_relax)>0 else mpf(0)
    print(f"{D:>8} {float(abs(v_orig)):>16.6e} {float(abs(v_relax)):>18.6e} {float(relerr):>12.3e}  [{dt:.1f}s]", flush=True)
