"""
m3-L171 part D -- refine D* far beyond the L169 root-find, via a single high-precision Newton step
from the existing (dps-60, ~61 s.f. verified) root, using g[0][0] (residual) and g[0][1] (local
derivative) computed at dps=150. This is numerically the SAME operation as BEAST's "self-recentring"
trick (the g[0][.] column determines its own offset for free) -- one Newton step from an already
good approximation should roughly double the number of correct digits (61 -> ~120), which is more
than enough to test agreement with BEAST's own dps-150 D* at the ~1e-77 level they asked about.
"""
import sys, time
sys.path.insert(0, '.')
import mpmath as mp
from m3_L169_xiD_core import xiD

DSTAR_OLD = '0.141733239663887191395415685084185023623144561955016655942867'
BEAST_DSTAR_STR = '0.14173323966388719139541568508418502362314456195501665594286660394665904218970743'


def f(D, dps):
    mp.mp.dps = dps
    return xiD(mp.mpf('0.5'), D).real


def main():
    dps = 150
    mp.mp.dps = dps
    t0 = time.time()
    D_old = mp.mpf(DSTAR_OLD)

    f0 = f(D_old, dps)
    print(f"f(D_old) = xi_D_old(1/2) at dps={dps}: {f0}", flush=True)
    print(f"[{time.time()-t0:.1f}s]", flush=True)

    # 5-point central difference for f'(D_old), h chosen to balance truncation vs roundoff at dps=150
    h = mp.mpf('1e-30')
    fp2 = f(D_old + 2 * h, dps)
    fp1 = f(D_old + h, dps)
    fm1 = f(D_old - h, dps)
    fm2 = f(D_old - 2 * h, dps)
    fprime = (-fp2 + 8 * fp1 - 8 * fm1 + fm2) / (12 * h)
    print(f"f'(D_old) (5-pt central, h={h}) = {fprime}", flush=True)
    print(f"[{time.time()-t0:.1f}s]", flush=True)

    correction = -f0 / fprime
    D_new = D_old + correction
    print(f"\nNewton correction = {correction}", flush=True)
    print(f"D_new (refined, dps={dps}) = {D_new}", flush=True)

    # verify: residual at D_new should be MUCH smaller than at D_old
    f_new = f(D_new, dps)
    print(f"\nf(D_new) residual check = {f_new}   (should be tiny vs f(D_old)={f0})", flush=True)

    BEAST_DSTAR = mp.mpf(BEAST_DSTAR_STR)  # constructed AFTER dps=150 is set -- bug-2 discipline
    rel_diff = abs(D_new - BEAST_DSTAR) / BEAST_DSTAR
    print(f"\nBEAST's published D* (dps-150, 83 s.f.) = {BEAST_DSTAR}")
    print(f"my refined D*                            = {D_new}")
    print(f"relative difference = {rel_diff}")
    print(f"\n[{time.time()-t0:.1f}s] done")


if __name__ == '__main__':
    main()
