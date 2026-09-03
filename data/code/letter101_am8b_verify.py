"""Independent re-verification of Mac's restored AM-8b evaluator discipline.
NOT a copy of Mac's file (not yet pushed to the shared repo) -- an independently
written implementation of the SAME stated discipline (adaptive termination:
inner m-loop stops once the Bessel argument z=2*pi*D*k*m exceeds ~160 (K-underflow
regime), outer k-loop stops once the k-shell's relative contribution drops below
1e-45), to check it reproduces Mac's four quoted target numbers.
"""
from mpmath import mp, mpf, mpc, pi as mp_pi, sqrt as mp_sqrt, gamma as mp_gamma, zeta, besselk, beta
import time

mp.dps = 30

def zeta2_adaptive(s, D, zcut=160, kshell_reltol=mpf('1e-45'), kmax=200000, mmax=200000):
    """Independently-written adaptive-truncation Bessel-representation evaluator.
    Stopping rules stated to match Mac's restored discipline (not copied code):
      - inner m-loop: stop once z*m > zcut (besselk has entered its underflow regime)
      - outer k-loop: stop once a full k-shell's relative contribution < kshell_reltol
    """
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
    return tot + (4*mp_pi**s/mp_gamma(s))*D**(mpf('0.5') - s)*ssum, k, m


def dirichlet_beta(s):
    s = mpc(s)
    return mpf(4)**(-s) * (zeta(s, mpf('0.25')) - zeta(s, mpf('0.75')))


if __name__ == '__main__':
    print("=== Check 1: D=1 closed form (2*zeta*beta), s=3, 3+5i ===")
    for s0 in [mpc(3,0), mpc(3,5)]:
        val, k, m = zeta2_adaptive(s0, '1.0')
        gt = 2*zeta(s0)*dirichlet_beta(s0)
        reldiff = abs(val-gt)/abs(gt)
        print(f"s={s0}: mine={complex(val):.10e}  ground_truth={complex(gt):.10e}  reldiff={float(reldiff):.3e}  (k={k},m={m})")

    print()
    print("=== Check 2: D=0.001, s=3+0i -> target 1.01734e+18 ===")
    t0=time.time()
    val, k, m = zeta2_adaptive(mpc(3,0), '0.001')
    print(f"mine={float(abs(val)):.6e}  target=1.01734e+18  reldiff={float(abs(abs(val)-1.01734e18)/1.01734e18):.3e}  (k={k},m={m})  [{time.time()-t0:.1f}s]")

    print()
    print("=== Check 3: sigma=1.05, t=5, D=0.02 and D=0.01 -> targets 4.358e+03 / 1.871e+04 ===")
    for D, target in [('0.02', 4.358e3), ('0.01', 1.871e4)]:
        t0=time.time()
        val, k, m = zeta2_adaptive(mpc(mpf('1.05'), 5), D)
        print(f"D={D}: mine={float(abs(val)):.6e}  target={target:.3e}  reldiff={abs(float(abs(val))-target)/target:.3e}  (k={k},m={m})  [{time.time()-t0:.1f}s]")
