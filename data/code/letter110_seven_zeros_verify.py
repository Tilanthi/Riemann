"""Independent (own from-scratch, adaptive-truncation) check of BEAST's best and lowest
off-line zeros of zeta2(s,1/7), using the scaling-identity trick (evaluate at D=7 where
the Bessel series converges fast, since zeta2(s,1/7)=49^s * zeta2(s,7))."""
from mpmath import mp, mpf, mpc, pi as mp_pi, sqrt as mp_sqrt, gamma as mp_gamma, zeta, besselk
import time

mp.dps = 40

def zeta2_adaptive(s, D, zcut=200, kshell_reltol=mpf('1e-50'), kmax=200000, mmax=200000):
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

def F_via_scaling(s, Delta_inv_target=mpf(7)):
    # zeta2(s, 1/7) = 49^s * zeta2(s, 7)
    s = mpc(s)
    return (Delta_inv_target**2)**s * zeta2_adaptive(s, Delta_inv_target)

zeros_to_check = {
    "best (t=47.30)": mpc(mpf('0.7159014103823531018264718067'), mpf('47.29775881721048753252892984')),
    "lowest (t=44.41)": mpc(mpf('0.5246770865109702460561581364'), mpf('44.41100379785915585775068919')),
}

for name, s0 in zeros_to_check.items():
    t0 = time.time()
    val = F_via_scaling(s0)
    dt = time.time()-t0
    print(f"{name}: F(s0) = {complex(val):.6e}  |F| = {float(abs(val)):.6e}   [{dt:.1f}s]")

# Try the five zeros Mac's instrument couldn't confirm (death line above t~84)
more_zeros = {
    "t=84.47": mpc(mpf('0.6046656812518528366431236261'), mpf('84.46688428178119162005426882')),
    "t=91.06": mpc(mpf('0.6310301952784749425929755304'), mpf('91.06135680391329435771957746')),
    "t=92.40": mpc(mpf('0.6608607494128433009276473937'), mpf('92.40067261379804243385567371')),
    "t=98.62": mpc(mpf('0.6852853131833004632846554526'), mpf('98.61599811620170433773193031')),
    "t=110.28": mpc(mpf('0.6203387601752353028098032884'), mpf('110.2778479937533731781573067')),
}
print()
print("=== Zeros Mac's instrument could NOT confirm (t>84 death line) ===")
for name, s0 in more_zeros.items():
    t0 = time.time()
    val = F_via_scaling(s0)
    dt = time.time()-t0
    print(f"{name}: |F(s0)| = {float(abs(val)):.6e}   [{dt:.1f}s]")

# Sanity/bug check: evaluate at a nearby NON-zero point, should NOT be tiny
print()
print("=== Sanity check: nearby non-zero points (should NOT be ~1e-25) ===")
for name, s0 in {"near best +0.01": zeros_to_check["best (t=47.30)"] + mpf('0.01'),
                  "near t=110 +0.01": more_zeros["t=110.28"] + mpf('0.01')}.items():
    val = F_via_scaling(s0)
    print(f"{name}: |F| = {float(abs(val)):.6e}")
