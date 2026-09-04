"""Independent verification of Mac's residue-removal resolution: compute the eps-INDEPENDENT
'true' Delta* by explicitly removing the O(eps^2) residue from the symmetric-offset map,
using my own A_ss (already independently computed in Letter 110's verification), own code."""
from mpmath import mp, mpf, mpc, pi as mp_pi, sqrt as mp_sqrt, gamma as mp_gamma, zeta, besselk, findroot

mp.dps = 50  # SET FIRST before any literal parsing

def zeta2_adaptive(s, D, zcut=220, kshell_reltol=mpf('1e-60'), kmax=200000, mmax=200000):
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

# my own independently-computed A_ss (from Letter 110's symmetric-stencil check),
# best estimate at h=1e-6: -37.6335585778090731217273175263238576918820409
A_ss_mine = mpf('-37.6335585778090731217273175263238576918820409')

mac_true_root = mpf('0.141733239663887191395415685084185024')
beast_val = mpf('0.14173323966388719139541530708686641')

Dstar_guess = mpf('0.141733239663887191395415')

for eps_exp in [-10, -12, -14]:
    EPS = mpf(10)**eps_exp
    def f_half_removed(D, EPS=EPS):
        D = mpf(D)
        vplus = zeta2_adaptive(mpf('0.5') + EPS, D).real
        vminus = zeta2_adaptive(mpf('0.5') - EPS, D).real
        raw_avg = (vplus + vminus) / 2
        # remove the O(eps^2) residue: raw_avg - eps^2 * A_ss/2
        removed = raw_avg - EPS**2 * A_ss_mine / 2
        return removed
    Dstar = findroot(f_half_removed, Dstar_guess, tol=mpf('1e-42'))
    diff_mac_true = Dstar - mac_true_root
    diff_beast = Dstar - beast_val
    print(f"eps=1e{eps_exp} (removed): Dstar={Dstar}")
    print(f"   diff from Mac's true root: {float(diff_mac_true):.4e}   diff from BEAST published: {float(diff_beast):.4e}")
