"""
m3-L169 part 2 -- the pre-registered blind tests: G(0,0) aliasing law + the "a" coefficient,
using the validated xi_D instrument from m3_L169_xiD_core.py.

CORRECTED IN m3-L170 (self-caught bug, distinct from the L169 lattice-cutoff bug): the ORIGINAL
version of this file built `Dstar = mp.mpf('0.1417...')` once at the top of main(), BEFORE
`mp.mp.dps` had been raised from its ambient default (15). Passing that already-created mpf object
into circle_average_power()/f_half() and re-wrapping it with `mp.mpf(Dstar)` does NOT recover the
lost digits -- an mpf object copied at higher dps stays truncated to however many digits it had when
it was first constructed. The result: every "dps=50" or "dps=60" computation downstream was silently
working with a D* good to only ~15 significant digits, not the ~50-60 intended. This was invisible
until the G(0,0) test failed to show the expected exponential shrinkage between N_w=16 and N_w=24 (it
plateaued at ~4.8e-16 regardless of N_w or even dps, which is the fingerprint of a fixed absolute
input error, not a genuine roundoff/precision-insufficiency issue). Fixed here by ALWAYS constructing
Dstar from the raw string, freshly, AFTER `mp.mp.dps` is set in the scope that needs it -- never by
copying a pre-existing mpf across a dps change.
"""
import sys, time
sys.path.insert(0, '.')
from m3_L169_xiD_core import xiD
import mpmath as mp

DSTAR_STR = '0.141733239663887191395415685084185023623144561955016655942867'


def circle_average_power(dstar_str, r_w, N_w, power, dps):
    """(1/N_w) * sum_k xi_D*(1/2 + r_w*omega^k) * (r_w*omega^k)^(-power), omega=exp(2pi i/N_w).

    dstar_str: the D* value as a STRING (not a pre-built mpf) -- see module docstring for why
    this matters. Constructed into an mpf only after mp.mp.dps is set to the target precision.
    """
    mp.mp.dps = dps
    Dstar = mp.mpf(dstar_str)
    total = mp.mpc(0)
    for k in range(N_w):
        theta = 2 * mp.pi * k / N_w
        w = r_w * mp.e**(mp.mpc(0, theta))
        val = xiD(mp.mpf('0.5') + w, Dstar)
        total += val * w**(-power)
    return total / N_w


def a_coefficient(dstar_str, r_w, N_w_a, dps, h_e_str):
    """g[1][0] (circle-average, power=2) and g[0][1] (4th-order central diff in D at D*),
    both built strictly after dps is raised, from the D* string, matching the docstring fix."""
    mp.mp.dps = dps
    Dstar = mp.mpf(dstar_str)
    h_e = mp.mpf(h_e_str)

    g10 = circle_average_power(dstar_str, r_w, N_w_a, 2, dps)

    mp.mp.dps = dps  # circle_average_power leaves dps set, but be explicit

    def f_half(D):
        return xiD(mp.mpf('0.5'), D).real

    fm2 = f_half(Dstar - 2 * h_e)
    fm1 = f_half(Dstar - h_e)
    fp1 = f_half(Dstar + h_e)
    fp2 = f_half(Dstar + 2 * h_e)
    g01 = (-fp2 + 8 * fp1 - 8 * fm1 + fm2) / (12 * h_e)

    return g10, g01


def main():
    t0 = time.time()

    print("=== G(0,0) aliasing test (corrected: Dstar built after dps is set) ===", flush=True)
    r_w = mp.mpf('0.04')
    for N_w in (4, 8, 16, 24):
        t1 = time.time()
        g00 = circle_average_power(DSTAR_STR, r_w, N_w, 0, dps=50)
        law = -4 * (2 * r_w) ** N_w
        ratio = g00.real / law
        print(f"N_w={N_w}: G(0,0) = {g00}  law -4*(2r_w)^Nw = {law}  ratio = {ratio}  "
              f"[{time.time()-t1:.1f}s]", flush=True)

    print(f"\n[{time.time()-t0:.1f}s] === 'a' coefficient ===", flush=True)
    g10, g01 = a_coefficient(DSTAR_STR, r_w, N_w_a=24, dps=60, h_e_str='1e-15')
    print(f"g[1][0] (coeff of w^2) = {g10}", flush=True)
    print(f"g[0][1] (d/dD xi_D(1/2) at D*), 4th-order central diff, h_e=1e-15 = {g01}", flush=True)

    mp.mp.dps = 60
    a_val = g01 / g10.real
    ref = mp.mpf('2.645521411811662868016126121')
    print(f"\na = g[0][1]/g[1][0] = {a_val}", flush=True)
    print(f"operative reference a = {ref}", flush=True)
    print("rel diff =", abs(a_val - ref) / ref, flush=True)

    print(f"\n[{time.time()-t0:.1f}s] done")


if __name__ == '__main__':
    main()
